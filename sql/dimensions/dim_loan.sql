-- BigQuery Dimension: dim_loan.sql
-- Static loan origination dimension isolating disbursement attributes from transaction events

CREATE OR REPLACE TABLE `fin_warehouse.dim_loan` AS
WITH loans AS (
    SELECT 
        l.loan_id,
        l.borrower_id,
        l.branch_id,
        l.state_id,
        l.product_id,
        l.disbursement_date,
        CAST(FORMAT_DATE('%Y%m%d', l.disbursement_date) AS INT64) AS disbursement_date_key,
        l.principal_amount,
        l.annual_interest_rate,
        l.tenure_months,
        l.loan_status
    FROM `fin_staging.stg_loans` l
)
SELECT 
    ROW_NUMBER() OVER (ORDER BY loan_id) AS loan_key,
    loan_id,
    borrower_id,
    branch_id,
    state_id,
    product_id,
    disbursement_date,
    disbursement_date_key,
    principal_amount,
    annual_interest_rate,
    tenure_months,
    loan_status
FROM loans
UNION ALL
-- Fallback entry for unmapped loans
SELECT -1, 'UNKNOWN_LOAN', 'UNKNOWN_BORROWER', 'UNKNOWN_BRANCH', 'UNKNOWN_STATE', 'UNKNOWN_PRODUCT', 
       DATE '1970-01-01', 19700101, NUMERIC '0.00', NUMERIC '0.00', 0, 'Unknown';
