-- BigQuery DDL: 03_create_staging_tables.sql
-- Staging and governance quarantine schema definitions

CREATE TABLE IF NOT EXISTS `fin_staging.stg_quarantined_records` (
    quarantine_id STRING OPTIONS(description="Unique quarantine event ID"),
    batch_run_id STRING OPTIONS(description="ETL batch run execution ID"),
    quarantined_at TIMESTAMP OPTIONS(description="Timestamp when record was quarantined"),
    source_table STRING OPTIONS(description="Raw source table name"),
    record_identifier STRING OPTIONS(description="Primary business identifier (loan_id, transaction_id, etc.)"),
    reason_code STRING OPTIONS(description="Explicit anomaly classification code (e.g. DUPLICATE_LOAN_ID, NEGATIVE_PAYMENT_AMOUNT)"),
    raw_payload STRING OPTIONS(description="Full serialization of anomalous record attributes for audit lineage")
)
CLUSTER BY source_table, reason_code;

CREATE TABLE IF NOT EXISTS `fin_staging.stg_loans` (
    loan_id STRING,
    borrower_id STRING,
    branch_id STRING,
    state_id STRING,
    product_id STRING,
    disbursement_date DATE,
    principal_amount NUMERIC(12, 2),
    annual_interest_rate NUMERIC(5, 2),
    tenure_months INT64,
    loan_status STRING
)
CLUSTER BY product_id, branch_id;

CREATE TABLE IF NOT EXISTS `fin_staging.stg_borrowers` (
    borrower_id STRING,
    borrower_segment STRING,
    income_band STRING,
    location_type STRING,
    occupation_category STRING
)
CLUSTER BY borrower_segment;

CREATE TABLE IF NOT EXISTS `fin_staging.stg_branches` (
    branch_id STRING,
    branch_name STRING,
    state_id STRING,
    location_type STRING
)
CLUSTER BY state_id;

CREATE TABLE IF NOT EXISTS `fin_staging.stg_repayments` (
    transaction_id STRING,
    loan_id STRING,
    payment_date DATE,
    payment_amount NUMERIC(12, 2),
    payment_channel STRING,
    raw_payment_amount NUMERIC(12, 2),
    raw_amount_unit STRING,
    amount_unit STRING
)
PARTITION BY payment_date
CLUSTER BY loan_id;

CREATE TABLE IF NOT EXISTS `fin_staging.stg_instalments` (
    instalment_id STRING,
    loan_id STRING,
    due_date DATE,
    instalment_number INT64,
    opening_principal NUMERIC(12, 2),
    amount_due NUMERIC(12, 2),
    principal_component NUMERIC(12, 2),
    interest_component NUMERIC(12, 2),
    closing_principal NUMERIC(12, 2),
    amount_paid NUMERIC(12, 2),
    days_past_due INT64,
    outstanding_instalment_amount NUMERIC(12, 2)
)
PARTITION BY due_date
CLUSTER BY loan_id;

CREATE TABLE IF NOT EXISTS `fin_staging.stg_instalment_allocation` (
    transaction_id STRING,
    instalment_id STRING,
    loan_id STRING,
    instalment_number INT64,
    due_date DATE,
    payment_date DATE,
    payment_channel STRING,
    allocated_amount NUMERIC(12, 2),
    allocated_principal NUMERIC(12, 2),
    allocated_interest NUMERIC(12, 2)
)
PARTITION BY payment_date
CLUSTER BY loan_id, instalment_id;
