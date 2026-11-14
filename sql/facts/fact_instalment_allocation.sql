-- BigQuery Fact Table: fact_instalment_allocation.sql
-- Grain: One row per allocation of an inbound transaction against a scheduled instalment
-- Enables atomic cash conservation and principal-interest reconciliation

CREATE OR REPLACE TABLE `fin_warehouse.fact_instalment_allocation` AS
SELECT 
    ROW_NUMBER() OVER (ORDER BY a.payment_date, a.transaction_id, a.instalment_number) AS allocation_key,
    a.transaction_id,
    a.instalment_id,
    COALESCE(dl.loan_key, -1) AS loan_key,
    a.payment_date,
    CAST(FORMAT_DATE('%Y%m%d', a.payment_date) AS INT64) AS payment_date_key,
    a.due_date,
    CAST(FORMAT_DATE('%Y%m%d', a.due_date) AS INT64) AS due_date_key,
    COALESCE(db.branch_key, -1) AS branch_key,
    COALESCE(ds.state_key, -1) AS state_key,
    COALESCE(dp.product_key, -1) AS product_key,
    COALESCE(dbs.borrower_segment_key, -1) AS borrower_segment_key,
    a.instalment_number,
    a.allocated_amount,
    a.allocated_principal,
    a.allocated_interest,
    a.payment_channel
FROM `fin_staging.stg_instalment_allocation` a
JOIN `fin_staging.stg_loans` l ON a.loan_id = l.loan_id
LEFT JOIN `fin_warehouse.dim_loan` dl ON l.loan_id = dl.loan_id
LEFT JOIN `fin_warehouse.dim_branch` db ON l.branch_id = db.branch_id
LEFT JOIN `fin_warehouse.dim_state` ds ON l.state_id = ds.state_id
LEFT JOIN `fin_warehouse.dim_product` dp ON l.product_id = dp.product_id
LEFT JOIN `fin_staging.stg_borrowers` b ON l.borrower_id = b.borrower_id
LEFT JOIN `fin_warehouse.dim_borrower_segment` dbs 
    ON b.borrower_segment = dbs.borrower_segment
   AND b.income_band = dbs.income_band
   AND b.location_type = dbs.location_type
   AND b.occupation_category = dbs.occupation_category;
