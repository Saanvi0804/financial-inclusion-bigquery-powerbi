-- BigQuery Fact Table: fact_payment.sql
-- Grain: One row per valid repayment transaction
-- Captures inbound cash flow events mapped to dimension surrogate keys

CREATE OR REPLACE TABLE `fin_warehouse.fact_payment` AS
SELECT 
    ROW_NUMBER() OVER (ORDER BY r.payment_date, r.transaction_id) AS payment_key,
    r.transaction_id,
    COALESCE(dl.loan_key, -1) AS loan_key,
    r.payment_date,
    CAST(FORMAT_DATE('%Y%m%d', r.payment_date) AS INT64) AS payment_date_key,
    COALESCE(db.branch_key, -1) AS branch_key,
    COALESCE(ds.state_key, -1) AS state_key,
    COALESCE(dp.product_key, -1) AS product_key,
    COALESCE(dbs.borrower_segment_key, -1) AS borrower_segment_key,
    r.payment_amount,
    r.payment_channel,
    r.raw_payment_amount,
    r.raw_amount_unit
FROM `fin_staging.stg_repayments` r
JOIN `fin_staging.stg_loans` l ON r.loan_id = l.loan_id
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
