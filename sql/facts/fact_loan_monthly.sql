-- BigQuery Fact Table: fact_loan_monthly.sql
-- Grain: Exactly one row per loan per month-end reporting snapshot
-- Calculates point-in-time DPD, overdue arrears, and reducing-balance outstanding principal

CREATE OR REPLACE TABLE `fin_warehouse.fact_loan_monthly` AS
WITH month_ends AS (
    SELECT DISTINCT full_date AS snapshot_date, date_key AS snapshot_date_key
    FROM `fin_warehouse.dim_date`
    WHERE is_month_end = TRUE
      AND full_date >= DATE '2023-01-01'
      AND full_date <= DATE '2024-12-31'
),
-- Eligible loans as of each month-end (disbursed on or before snapshot date)
loan_snapshots AS (
    SELECT 
        l.loan_id,
        l.borrower_id,
        l.branch_id,
        l.state_id,
        l.product_id,
        l.principal_amount,
        l.tenure_months,
        l.disbursement_date,
        me.snapshot_date,
        me.snapshot_date_key
    FROM `fin_staging.stg_loans` l
    CROSS JOIN month_ends me
    WHERE l.disbursement_date <= me.snapshot_date
),
-- Payments allocated up to snapshot date for each scheduled instalment
instalment_snapshot_perf AS (
    SELECT 
        ls.loan_id,
        ls.snapshot_date,
        i.instalment_id,
        i.instalment_number,
        i.due_date,
        i.amount_due,
        i.principal_component,
        COALESCE(SUM(CASE WHEN a.payment_date <= ls.snapshot_date THEN a.allocated_amount ELSE NUMERIC '0.0' END), NUMERIC '0.0') AS paid_amt,
        COALESCE(SUM(CASE WHEN a.payment_date <= ls.snapshot_date THEN a.allocated_principal ELSE NUMERIC '0.0' END), NUMERIC '0.0') AS paid_prin
    FROM loan_snapshots ls
    JOIN `fin_staging.stg_instalments` i 
        ON ls.loan_id = i.loan_id 
       AND i.due_date <= ls.snapshot_date
    LEFT JOIN `fin_staging.stg_instalment_allocation` a 
        ON i.instalment_id = a.instalment_id
    GROUP BY 
        ls.loan_id, ls.snapshot_date, i.instalment_id, i.instalment_number, 
        i.due_date, i.amount_due, i.principal_component
),
-- Total principal repaid on or before snapshot date across all instalments (including advances)
loan_snapshot_principal AS (
    SELECT 
        ls.loan_id,
        ls.snapshot_date,
        COALESCE(SUM(a.allocated_principal), NUMERIC '0.0') AS total_principal_repaid
    FROM loan_snapshots ls
    LEFT JOIN `fin_staging.stg_instalment_allocation` a 
        ON ls.loan_id = a.loan_id 
       AND a.payment_date <= ls.snapshot_date
    GROUP BY ls.loan_id, ls.snapshot_date
),
loan_snapshot_aggs AS (
    SELECT 
        loan_id,
        snapshot_date,
        COUNT(instalment_id) AS instalments_due,
        COUNT(CASE WHEN (amount_due - paid_amt) <= NUMERIC '0.01' THEN 1 END) AS instalments_paid,
        ROUND(SUM(amount_due), 2) AS amount_due,
        ROUND(SUM(paid_amt), 2) AS amount_paid,
        ROUND(SUM(GREATEST(NUMERIC '0.0', amount_due - paid_amt)), 2) AS overdue_amount,
        -- Exact NUMERIC tolerance eliminates floating point 1-paisa artifacts
        MAX(CASE WHEN ROUND(amount_due - paid_amt, 2) > NUMERIC '0.01' THEN DATE_DIFF(snapshot_date, due_date, DAY) ELSE 0 END) AS days_past_due
    FROM instalment_snapshot_perf
    GROUP BY loan_id, snapshot_date
)
SELECT 
    ROW_NUMBER() OVER (ORDER BY ls.snapshot_date, ls.loan_id) AS snapshot_key,
    ls.loan_id,
    COALESCE(dl.loan_key, -1) AS loan_key,
    ls.snapshot_date,
    ls.snapshot_date_key,
    COALESCE(db.branch_key, -1) AS branch_key,
    COALESCE(ds.state_key, -1) AS state_key,
    COALESCE(dp.product_key, -1) AS product_key,
    COALESCE(dbs.borrower_segment_key, -1) AS borrower_segment_key,
    -- Reducing balance outstanding principal
    GREATEST(NUMERIC '0.00', ROUND(ls.principal_amount - COALESCE(lsp.total_principal_repaid, NUMERIC '0.0'), 2)) AS outstanding_principal,
    COALESCE(lsa.instalments_due, 0) AS instalments_due,
    COALESCE(lsa.instalments_paid, 0) AS instalments_paid,
    COALESCE(lsa.amount_due, NUMERIC '0.00') AS amount_due,
    COALESCE(lsa.amount_paid, NUMERIC '0.00') AS amount_paid,
    COALESCE(lsa.days_past_due, 0) AS days_past_due,
    COALESCE(lsa.overdue_amount, NUMERIC '0.00') AS overdue_amount
FROM loan_snapshots ls
LEFT JOIN loan_snapshot_aggs lsa 
    ON ls.loan_id = lsa.loan_id 
   AND ls.snapshot_date = lsa.snapshot_date
LEFT JOIN loan_snapshot_principal lsp 
    ON ls.loan_id = lsp.loan_id 
   AND ls.snapshot_date = lsp.snapshot_date
LEFT JOIN `fin_warehouse.dim_loan` dl ON ls.loan_id = dl.loan_id
LEFT JOIN `fin_warehouse.dim_branch` db ON ls.branch_id = db.branch_id
LEFT JOIN `fin_warehouse.dim_state` ds ON ls.state_id = ds.state_id
LEFT JOIN `fin_warehouse.dim_product` dp ON ls.product_id = dp.product_id
LEFT JOIN `fin_staging.stg_borrowers` b ON ls.borrower_id = b.borrower_id
LEFT JOIN `fin_warehouse.dim_borrower_segment` dbs 
    ON b.borrower_segment = dbs.borrower_segment
   AND b.income_band = dbs.income_band
   AND b.location_type = dbs.location_type
   AND b.occupation_category = dbs.occupation_category;
