-- BigQuery DDL: 02_create_raw_tables.sql
-- Raw landing tables preserving immutable source feed, raw amount units, and ingestion audit metadata

CREATE TABLE IF NOT EXISTS `fin_raw.raw_loans` (
    loan_id STRING OPTIONS(description="Alphanumeric unique loan identifier (contains intentional duplicates)"),
    borrower_id STRING OPTIONS(description="Borrower identifier referencing raw_borrowers"),
    branch_id STRING OPTIONS(description="Branch identifier (contains blanks for ISSUE-06)"),
    state_id STRING OPTIONS(description="State identifier code"),
    product_id STRING OPTIONS(description="Loan product catalogue identifier (contains invalid PRD_INVALID for ISSUE-07)"),
    disbursement_date DATE OPTIONS(description="Loan origination / disbursement date"),
    principal_amount NUMERIC(12, 2) OPTIONS(description="Contractual principal amount disbursed"),
    annual_interest_rate NUMERIC(5, 2) OPTIONS(description="Nominal contractual annual interest rate percentage"),
    tenure_months INT64 OPTIONS(description="Contractual loan duration in months"),
    loan_status STRING OPTIONS(description="Terminal operational status (Active, Closed, Defaulted)"),
    ingestion_timestamp TIMESTAMP OPTIONS(description="Timestamp when record was ingested into BigQuery raw layer")
)
CLUSTER BY product_id, state_id;

CREATE TABLE IF NOT EXISTS `fin_raw.raw_borrowers` (
    borrower_id STRING OPTIONS(description="Unique borrower identifier"),
    borrower_segment STRING OPTIONS(description="Borrower demographic and socio-economic category"),
    income_band STRING OPTIONS(description="Annual household income tier"),
    location_type STRING OPTIONS(description="Geographic demographic type (Rural, Semi-Urban, Urban)"),
    occupation_category STRING OPTIONS(description="Primary livelihood / occupational archetype"),
    ingestion_timestamp TIMESTAMP OPTIONS(description="Timestamp when record was ingested")
)
CLUSTER BY borrower_segment;

CREATE TABLE IF NOT EXISTS `fin_raw.raw_branches` (
    branch_id STRING OPTIONS(description="Unique physical branch identifier"),
    branch_name STRING OPTIONS(description="Official operational branch office name"),
    state_id STRING OPTIONS(description="State identifier where branch is physically located"),
    location_type STRING OPTIONS(description="Location category (Urban, Semi-Urban, Rural)"),
    ingestion_timestamp TIMESTAMP OPTIONS(description="Timestamp when record was ingested")
)
CLUSTER BY state_id;

CREATE TABLE IF NOT EXISTS `fin_raw.raw_repayments` (
    transaction_id STRING OPTIONS(description="Unique inbound payment transaction identifier (contains duplicates)"),
    loan_id STRING OPTIONS(description="Associated loan identifier"),
    payment_date DATE OPTIONS(description="Date transaction was executed / credited"),
    payment_amount NUMERIC(12, 2) OPTIONS(description="Raw payment amount as received (contains negative values & paise)"),
    payment_channel STRING OPTIONS(description="Repayment instrument / channel (UPI, Bank Transfer, Cash)"),
    amount_unit STRING OPTIONS(description="Explicit denomination unit indicator ('INR' vs 'PAISE')"),
    ingestion_timestamp TIMESTAMP OPTIONS(description="Timestamp when record was ingested")
)
PARTITION BY payment_date
CLUSTER BY loan_id;

CREATE TABLE IF NOT EXISTS `fin_raw.raw_instalments` (
    instalment_id STRING OPTIONS(description="Unique contractual instalment schedule identifier"),
    loan_id STRING OPTIONS(description="Associated loan identifier"),
    due_date DATE OPTIONS(description="Contractual due date of instalment"),
    instalment_number INT64 OPTIONS(description="Sequential month sequence on book (1, 2, ..., tenure)"),
    opening_principal NUMERIC(12, 2) OPTIONS(description="Contractual opening balance before instalment"),
    amount_due NUMERIC(12, 2) OPTIONS(description="Total contractual monthly instalment amount (EMI)"),
    principal_component NUMERIC(12, 2) OPTIONS(description="Contractual principal amortization portion"),
    interest_component NUMERIC(12, 2) OPTIONS(description="Contractual interest portion"),
    closing_principal NUMERIC(12, 2) OPTIONS(description="Expected contractual principal after instalment"),
    amount_paid NUMERIC(12, 2) OPTIONS(description="Reported amount paid (contains excess amounts up to 2.8x)"),
    days_past_due INT64 OPTIONS(description="Raw reported DPD (contains corrupted zero DPD on arrears)"),
    outstanding_instalment_amount NUMERIC(12, 2) OPTIONS(description="Raw reported remaining due amount"),
    ingestion_timestamp TIMESTAMP OPTIONS(description="Timestamp when record was ingested")
)
PARTITION BY due_date
CLUSTER BY loan_id;

CREATE TABLE IF NOT EXISTS `fin_raw.raw_ingestion_audit_log` (
    audit_id STRING OPTIONS(description="Unique ingestion audit UUID"),
    batch_run_id STRING OPTIONS(description="Batch identifier for idempotent loading"),
    source_file STRING OPTIONS(description="Source file name"),
    target_table STRING OPTIONS(description="Target BigQuery raw table"),
    records_loaded INT64 OPTIONS(description="Total rows inserted"),
    ingestion_timestamp TIMESTAMP OPTIONS(description="Execution timestamp"),
    status STRING OPTIONS(description="Ingestion status (SUCCESS, FAILED)")
)
PARTITION BY DATE(ingestion_timestamp);
