-- BigQuery Staging: stg_loans.sql
-- Cleanses, deduplicates, and standardizes loan applications
-- Audits anomalies into stg_quarantined_records (ISSUE-01, ISSUE-06, ISSUE-07)

-- 1. Quarantine Duplicate Loans (ISSUE-01)
INSERT INTO `fin_staging.stg_quarantined_records` (quarantine_id, batch_run_id, quarantined_at, source_table, record_identifier, reason_code, raw_payload)
SELECT 
    GENERATE_UUID(),
    CONCAT('BATCH_STG_', FORMAT_TIMESTAMP('%Y%m%d%H%M%S', CURRENT_TIMESTAMP())),
    CURRENT_TIMESTAMP(),
    'raw_loans',
    loan_id,
    'DUPLICATE_LOAN_ID',
    CONCAT('loan_id=', loan_id, ', borrower_id=', borrower_id, ', principal=', CAST(principal_amount AS STRING))
FROM (
    SELECT loan_id, borrower_id, principal_amount,
           ROW_NUMBER() OVER (PARTITION BY loan_id ORDER BY disbursement_date) AS rn
    FROM `fin_raw.raw_loans`
)
WHERE rn > 1;

-- 2. Quarantine Invalid Product Loans (ISSUE-07)
INSERT INTO `fin_staging.stg_quarantined_records` (quarantine_id, batch_run_id, quarantined_at, source_table, record_identifier, reason_code, raw_payload)
SELECT 
    GENERATE_UUID(),
    CONCAT('BATCH_STG_', FORMAT_TIMESTAMP('%Y%m%d%H%M%S', CURRENT_TIMESTAMP())),
    CURRENT_TIMESTAMP(),
    'raw_loans',
    loan_id,
    'INVALID_PRODUCT_KEY',
    CONCAT('product_id=', COALESCE(product_id, 'NULL'), ', principal=', CAST(principal_amount AS STRING))
FROM `fin_raw.raw_loans`
WHERE product_id NOT IN ('PRD_MFI', 'PRD_AGR', 'PRD_SMB', 'PRD_PER', 'PRD_EDU');

-- 3. Quarantine Missing Branch Loans (ISSUE-06)
INSERT INTO `fin_staging.stg_quarantined_records` (quarantine_id, batch_run_id, quarantined_at, source_table, record_identifier, reason_code, raw_payload)
SELECT 
    GENERATE_UUID(),
    CONCAT('BATCH_STG_', FORMAT_TIMESTAMP('%Y%m%d%H%M%S', CURRENT_TIMESTAMP())),
    CURRENT_TIMESTAMP(),
    'raw_loans',
    loan_id,
    'MISSING_BRANCH_ID',
    CONCAT('loan_id=', loan_id, ', branch_id is blank')
FROM `fin_raw.raw_loans`
WHERE branch_id IS NULL OR TRIM(branch_id) = '';

-- 4. Create Clean Staging Loans Table
CREATE OR REPLACE TABLE `fin_staging.stg_loans` AS
WITH ranked_loans AS (
    SELECT 
        TRIM(loan_id) AS loan_id,
        TRIM(borrower_id) AS borrower_id,
        CASE 
            WHEN branch_id IS NULL OR TRIM(branch_id) = '' THEN 'UNKNOWN_BRANCH'
            ELSE TRIM(branch_id)
        END AS branch_id,
        TRIM(state_id) AS state_id,
        CASE 
            WHEN product_id IN ('PRD_MFI', 'PRD_AGR', 'PRD_SMB', 'PRD_PER', 'PRD_EDU') THEN TRIM(product_id)
            ELSE 'UNKNOWN_PRODUCT'
        END AS product_id,
        CAST(disbursement_date AS DATE) AS disbursement_date,
        CAST(principal_amount AS NUMERIC) AS principal_amount,
        CAST(annual_interest_rate AS NUMERIC) AS annual_interest_rate,
        CAST(tenure_months AS INT64) AS tenure_months,
        TRIM(loan_status) AS loan_status,
        ROW_NUMBER() OVER (PARTITION BY loan_id ORDER BY disbursement_date) AS rn
    FROM `fin_raw.raw_loans`
)
SELECT 
    loan_id,
    borrower_id,
    branch_id,
    state_id,
    product_id,
    disbursement_date,
    principal_amount,
    annual_interest_rate,
    tenure_months,
    loan_status
FROM ranked_loans
WHERE rn = 1;
