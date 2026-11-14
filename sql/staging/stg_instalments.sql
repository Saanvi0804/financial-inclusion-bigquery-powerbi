-- BigQuery Staging: stg_instalments.sql
-- Corrects payment overages, retains lineage of corrupted DPD, and standardises schedule balances (ISSUE-08, ISSUE-10)

-- 1. Quarantine / Audit Excess Payments (ISSUE-08)
INSERT INTO `fin_staging.stg_quarantined_records` (quarantine_id, batch_run_id, quarantined_at, source_table, record_identifier, reason_code, raw_payload)
SELECT 
    GENERATE_UUID(),
    CONCAT('BATCH_STG_', FORMAT_TIMESTAMP('%Y%m%d%H%M%S', CURRENT_TIMESTAMP())),
    CURRENT_TIMESTAMP(),
    'raw_instalments',
    instalment_id,
    'EXCESS_INSTALMENT_PAYMENT',
    CONCAT('due=', CAST(amount_due AS STRING), ', paid=', CAST(amount_paid AS STRING))
FROM `fin_raw.raw_instalments`
WHERE amount_paid > (amount_due * NUMERIC '2.0');

-- 2. Audit Corrupted Zero DPD Records (ISSUE-10)
INSERT INTO `fin_staging.stg_quarantined_records` (quarantine_id, batch_run_id, quarantined_at, source_table, record_identifier, reason_code, raw_payload)
SELECT 
    GENERATE_UUID(),
    CONCAT('BATCH_STG_', FORMAT_TIMESTAMP('%Y%m%d%H%M%S', CURRENT_TIMESTAMP())),
    CURRENT_TIMESTAMP(),
    'raw_instalments',
    instalment_id,
    'CORRUPTED_ZERO_DPD',
    CONCAT('due_date=', CAST(due_date AS STRING), ', original_dpd=', CAST(days_past_due AS STRING))
FROM `fin_raw.raw_instalments`
WHERE due_date <= DATE '2024-10-31'
  AND amount_paid = 0
  AND days_past_due = 0;

-- 3. Create Clean Staging Instalments Table
CREATE OR REPLACE TABLE `fin_staging.stg_instalments` AS
WITH cleaned_instalments AS (
    SELECT 
        TRIM(instalment_id) AS instalment_id,
        TRIM(loan_id) AS loan_id,
        CAST(due_date AS DATE) AS due_date,
        CAST(instalment_number AS INT64) AS instalment_number,
        CAST(opening_principal AS NUMERIC) AS opening_principal,
        CAST(amount_due AS NUMERIC) AS amount_due,
        CAST(principal_component AS NUMERIC) AS principal_component,
        CAST(interest_component AS NUMERIC) AS interest_component,
        CAST(closing_principal AS NUMERIC) AS closing_principal,
        -- Cap excess instalment payment at scheduled amount
        LEAST(CAST(amount_paid AS NUMERIC), CAST(amount_due AS NUMERIC)) AS amount_paid,
        -- Retain raw DPD for audit lineage; historical point-in-time DPD is dynamically evaluated per reporting snapshot in warehouse.fact_loan_monthly
        CAST(days_past_due AS INT64) AS days_past_due,
        -- Outstanding instalment amount
        GREATEST(NUMERIC '0.0', CAST(amount_due AS NUMERIC) - LEAST(CAST(amount_paid AS NUMERIC), CAST(amount_due AS NUMERIC))) AS outstanding_instalment_amount
    FROM `fin_raw.raw_instalments`
)
SELECT * FROM cleaned_instalments;
