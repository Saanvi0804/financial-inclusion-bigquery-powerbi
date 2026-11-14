-- BigQuery KPI Model: kpi_vintage_curves.sql
-- Tracks cumulative repayment performance of loan origination cohorts across months-on-book (MOB 1 to 24)

CREATE OR REPLACE TABLE `fin_analytics.kpi_vintage_curves` AS
WITH cohort_instalments AS (
    SELECT 
        FORMAT_DATE('%Y-%m', l.disbursement_date) AS cohort_month,
        CAST(FORMAT_DATE('%Y%m01', l.disbursement_date) AS INT64) AS cohort_date_key,
        p.product_id,
        p.product_name,
        p.category AS product_category,
        i.instalment_number AS month_on_book,
        COUNT(DISTINCT l.loan_id) AS total_cohort_loans,
        SUM(i.amount_due) AS scheduled_due_mob,
        SUM(i.amount_paid) AS amount_paid_mob
    FROM `fin_staging.stg_instalments` i
    JOIN `fin_staging.stg_loans` l ON i.loan_id = l.loan_id
    LEFT JOIN `fin_warehouse.dim_product` p ON l.product_id = p.product_id
    WHERE i.due_date <= DATE '2024-12-31' -- Observed data window
    GROUP BY 1, 2, 3, 4, 5, 6
),
cumulative_vintages AS (
    SELECT 
        cohort_month,
        cohort_date_key,
        product_id,
        product_name,
        product_category,
        month_on_book,
        total_cohort_loans,
        scheduled_due_mob,
        amount_paid_mob,
        SUM(scheduled_due_mob) OVER (
            PARTITION BY cohort_month, product_id 
            ORDER BY month_on_book
        ) AS cumulative_scheduled_due,
        SUM(amount_paid_mob) OVER (
            PARTITION BY cohort_month, product_id 
            ORDER BY month_on_book
        ) AS cumulative_amount_paid
    FROM cohort_instalments
)
SELECT 
    cohort_month,
    cohort_date_key,
    product_id,
    product_name,
    product_category,
    month_on_book,
    total_cohort_loans,
    scheduled_due_mob,
    amount_paid_mob,
    cumulative_scheduled_due,
    cumulative_amount_paid,
    ROUND(
        SAFE_DIVIDE(cumulative_amount_paid * NUMERIC '100.0', cumulative_scheduled_due), 
        2
    ) AS vintage_repayment_rate_pct
FROM cumulative_vintages
ORDER BY cohort_month, product_id, month_on_book;
