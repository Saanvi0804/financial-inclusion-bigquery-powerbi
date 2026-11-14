-- BigQuery Staging: stg_repayments.sql
-- Handles deduplication, explicit PAISE to INR standardisation, and quarantine logging (ISSUE-02, ISSUE-04, ISSUE-05, ISSUE-09)

-- 1. Quarantine Duplicate Transactions (ISSUE-02)
INSERT INTO `fin_staging.stg_quarantined_records` (quarantine_id, batch_run_id, quarantined_at, source_table, record_identifier, reason_code, raw_payload)
SELECT 
    GENERATE_UUID(),
    CONCAT('BATCH_STG_', FORMAT_TIMESTAMP('%Y%m%d%H%M%S', CURRENT_TIMESTAMP())),
    CURRENT_TIMESTAMP(),
    'raw_repayments',
    transaction_id,
    'DUPLICATE_TXN_ID',
    CONCAT('transaction_id=', transaction_id, ', loan_id=', loan_id, ', amount=', CAST(payment_amount AS STRING))
FROM (
    SELECT transaction_id, loan_id, payment_amount,
           ROW_NUMBER() OVER (PARTITION BY transaction_id ORDER BY payment_date) AS rn
    FROM `fin_raw.raw_repayments`
)
WHERE rn > 1;

-- 2. Quarantine Negative Payment Amounts (ISSUE-05)
INSERT INTO `fin_staging.stg_quarantined_records` (quarantine_id, batch_run_id, quarantined_at, source_table, record_identifier, reason_code, raw_payload)
SELECT 
    GENERATE_UUID(),
    CONCAT('BATCH_STG_', FORMAT_TIMESTAMP('%Y%m%d%H%M%S', CURRENT_TIMESTAMP())),
    CURRENT_TIMESTAMP(),
    'raw_repayments',
    transaction_id,
    'NEGATIVE_PAYMENT_AMOUNT',
    CONCAT('transaction_id=', transaction_id, ', amount=', CAST(payment_amount AS STRING))
FROM `fin_raw.raw_repayments`
WHERE payment_amount < 0;

-- 3. Quarantine Payments Preceding Loan Disbursement (ISSUE-09)
INSERT INTO `fin_staging.stg_quarantined_records` (quarantine_id, batch_run_id, quarantined_at, source_table, record_identifier, reason_code, raw_payload)
SELECT 
    GENERATE_UUID(),
    CONCAT('BATCH_STG_', FORMAT_TIMESTAMP('%Y%m%d%H%M%S', CURRENT_TIMESTAMP())),
    CURRENT_TIMESTAMP(),
    'raw_repayments',
    r.transaction_id,
    'PAYMENT_BEFORE_DISBURSEMENT',
    CONCAT('pay_date=', CAST(r.payment_date AS STRING), ', disb_date=', CAST(l.disbursement_date AS STRING))
FROM `fin_raw.raw_repayments` r
JOIN `fin_staging.stg_loans` l ON r.loan_id = l.loan_id
WHERE r.payment_date < l.disbursement_date;

-- 4. Create Clean Staging Repayments Table
CREATE OR REPLACE TABLE `fin_staging.stg_repayments` AS
WITH deduplicated_txns AS (
    SELECT 
        TRIM(r.transaction_id) AS transaction_id,
        TRIM(r.loan_id) AS loan_id,
        CAST(r.payment_date AS DATE) AS payment_date,
        -- Unit Standardisation: Convert explicit PAISE to INR (/ 100.0) exactly once; INR remains unchanged
        CASE 
            WHEN UPPER(TRIM(r.amount_unit)) = 'PAISE' THEN ROUND(CAST(r.payment_amount AS NUMERIC) / NUMERIC '100.0', 2)
            ELSE ROUND(CAST(r.payment_amount AS NUMERIC), 2)
        END AS payment_amount,
        TRIM(r.payment_channel) AS payment_channel,
        CAST(r.payment_amount AS NUMERIC) AS raw_payment_amount,
        TRIM(r.amount_unit) AS raw_amount_unit,
        'INR' AS amount_unit,
        l.disbursement_date,
        ROW_NUMBER() OVER (PARTITION BY r.transaction_id ORDER BY r.payment_date) AS rn
    FROM `fin_raw.raw_repayments` r
    LEFT JOIN `fin_staging.stg_loans` l ON r.loan_id = l.loan_id
    WHERE r.payment_amount >= 0 -- Exclude negative amounts
)
SELECT 
    transaction_id,
    loan_id,
    payment_date,
    payment_amount,
    payment_channel,
    raw_payment_amount,
    raw_amount_unit,
    amount_unit
FROM deduplicated_txns
WHERE rn = 1
  AND (disbursement_date IS NULL OR payment_date >= disbursement_date); -- Exclude pre-disbursement payments
