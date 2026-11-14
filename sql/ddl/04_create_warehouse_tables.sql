-- BigQuery DDL: 04_create_warehouse_tables.sql
-- Dimensional Star Schema definitions (6 Dimensions, 3 Fact tables)

-- 1. Dimensions
CREATE TABLE IF NOT EXISTS `fin_warehouse.dim_date` (
    date_key INT64 OPTIONS(description="Date surrogate key in YYYYMMDD format"),
    full_date DATE OPTIONS(description="Calendar date"),
    day_of_month INT64,
    month_number INT64,
    month_name STRING,
    year_month STRING,
    quarter_number INT64,
    quarter_name STRING,
    calendar_year INT64,
    financial_year STRING OPTIONS(description="Indian Financial Year (e.g. FY 2023-24, April-March)"),
    financial_quarter STRING OPTIONS(description="Indian Financial Quarter (Q1: Apr-Jun, Q2: Jul-Sep, etc.)"),
    is_weekend BOOL,
    is_month_end BOOL
)
PARTITION BY full_date
CLUSTER BY date_key;

CREATE TABLE IF NOT EXISTS `fin_warehouse.dim_state` (
    state_key INT64 OPTIONS(description="Surrogate primary key"),
    state_id STRING OPTIONS(description="Natural state identifier"),
    state_name STRING OPTIONS(description="Full state name"),
    region STRING OPTIONS(description="Geographic region of India (North, South, East, West, Central)")
)
CLUSTER BY state_key;

CREATE TABLE IF NOT EXISTS `fin_warehouse.dim_branch` (
    branch_key INT64 OPTIONS(description="Surrogate primary key (includes -1 fallback for UNKNOWN_BRANCH)"),
    branch_id STRING OPTIONS(description="Natural branch code"),
    branch_name STRING OPTIONS(description="Branch office name"),
    state_id STRING,
    location_type STRING OPTIONS(description="Location category (Urban, Semi-Urban, Rural)")
)
CLUSTER BY branch_key;

CREATE TABLE IF NOT EXISTS `fin_warehouse.dim_product` (
    product_key INT64 OPTIONS(description="Surrogate primary key (includes -1 fallback for UNKNOWN_PRODUCT)"),
    product_id STRING OPTIONS(description="Natural product code"),
    product_name STRING OPTIONS(description="Descriptive product title"),
    category STRING OPTIONS(description="Product family (Microfinance, Agriculture, MSME, Personal, Education)"),
    min_rate NUMERIC(5, 2),
    max_rate NUMERIC(5, 2),
    min_tenure INT64,
    max_tenure INT64
)
CLUSTER BY product_key;

CREATE TABLE IF NOT EXISTS `fin_warehouse.dim_borrower_segment` (
    borrower_segment_key INT64 OPTIONS(description="Surrogate primary key (includes -1 fallback)"),
    borrower_segment STRING OPTIONS(description="Socio-economic borrower segment"),
    income_band STRING OPTIONS(description="Household income tier"),
    location_type STRING OPTIONS(description="Urban, Semi-Urban, Rural"),
    occupation_category STRING OPTIONS(description="Occupational group")
)
CLUSTER BY borrower_segment_key;

CREATE TABLE IF NOT EXISTS `fin_warehouse.dim_loan` (
    loan_key INT64 OPTIONS(description="Surrogate primary key (includes -1 fallback)"),
    loan_id STRING OPTIONS(description="Unique business loan ID"),
    borrower_id STRING,
    branch_id STRING,
    state_id STRING,
    product_id STRING,
    disbursement_date DATE,
    disbursement_date_key INT64,
    principal_amount NUMERIC(12, 2),
    annual_interest_rate NUMERIC(5, 2),
    tenure_months INT64,
    loan_status STRING
)
CLUSTER BY product_id, branch_id;

-- 2. Fact Tables
CREATE TABLE IF NOT EXISTS `fin_warehouse.fact_payment` (
    payment_key INT64 OPTIONS(description="Surrogate payment event key"),
    transaction_id STRING OPTIONS(description="Natural transaction identifier"),
    loan_key INT64 OPTIONS(description="FK to dim_loan"),
    payment_date DATE OPTIONS(description="Event payment date"),
    payment_date_key INT64 OPTIONS(description="FK to dim_date"),
    branch_key INT64 OPTIONS(description="FK to dim_branch"),
    state_key INT64 OPTIONS(description="FK to dim_state"),
    product_key INT64 OPTIONS(description="FK to dim_product"),
    borrower_segment_key INT64 OPTIONS(description="FK to dim_borrower_segment"),
    payment_amount NUMERIC(12, 2) OPTIONS(description="Validated cash payment amount in INR"),
    payment_channel STRING OPTIONS(description="Repayment instrument: UPI, Bank Transfer, Cash"),
    raw_payment_amount NUMERIC(12, 2) OPTIONS(description="Lineage: original raw amount before normalisation"),
    raw_amount_unit STRING OPTIONS(description="Lineage: original raw unit ('INR' or 'PAISE')")
)
PARTITION BY payment_date
CLUSTER BY loan_key, branch_key;

CREATE TABLE IF NOT EXISTS `fin_warehouse.fact_instalment_allocation` (
    allocation_key INT64 OPTIONS(description="Surrogate allocation line-item key"),
    transaction_id STRING OPTIONS(description="Natural transaction identifier"),
    instalment_id STRING OPTIONS(description="Natural instalment identifier"),
    loan_key INT64 OPTIONS(description="FK to dim_loan"),
    payment_date DATE OPTIONS(description="Date payment cash was received"),
    payment_date_key INT64 OPTIONS(description="FK to dim_date (payment)"),
    due_date DATE OPTIONS(description="Contractual scheduled due date"),
    due_date_key INT64 OPTIONS(description="FK to dim_date (due)"),
    branch_key INT64 OPTIONS(description="FK to dim_branch"),
    state_key INT64 OPTIONS(description="FK to dim_state"),
    product_key INT64 OPTIONS(description="FK to dim_product"),
    borrower_segment_key INT64 OPTIONS(description="FK to dim_borrower_segment"),
    instalment_number INT64 OPTIONS(description="Instalment sequence on book"),
    allocated_amount NUMERIC(12, 2) OPTIONS(description="Portion of payment cash allocated to instalment"),
    allocated_principal NUMERIC(12, 2) OPTIONS(description="Proportional principal portion"),
    allocated_interest NUMERIC(12, 2) OPTIONS(description="Proportional interest portion"),
    payment_channel STRING OPTIONS(description="Payment channel")
)
PARTITION BY payment_date
CLUSTER BY loan_key, instalment_id;

CREATE TABLE IF NOT EXISTS `fin_warehouse.fact_loan_monthly` (
    snapshot_key INT64 OPTIONS(description="Surrogate monthly snapshot key"),
    loan_id STRING OPTIONS(description="Business loan ID"),
    loan_key INT64 OPTIONS(description="FK to dim_loan"),
    snapshot_date DATE OPTIONS(description="Month-end snapshot reporting date"),
    snapshot_date_key INT64 OPTIONS(description="FK to dim_date"),
    branch_key INT64 OPTIONS(description="FK to dim_branch"),
    state_key INT64 OPTIONS(description="FK to dim_state"),
    product_key INT64 OPTIONS(description="FK to dim_product"),
    borrower_segment_key INT64 OPTIONS(description="FK to dim_borrower_segment"),
    outstanding_principal NUMERIC(12, 2) OPTIONS(description="True reducing-balance principal outstanding as of snapshot"),
    instalments_due INT64 OPTIONS(description="Total instalments due on or before snapshot"),
    instalments_paid INT64 OPTIONS(description="Instalments fully satisfied on or before snapshot"),
    amount_due NUMERIC(12, 2) OPTIONS(description="Cumulative contractual billing due on or before snapshot"),
    amount_paid NUMERIC(12, 2) OPTIONS(description="Cumulative cash allocated on or before snapshot"),
    days_past_due INT64 OPTIONS(description="Snapshot-specific maximum DPD for overdue instalments (> 0.01 tolerance)"),
    overdue_amount NUMERIC(12, 2) OPTIONS(description="Total overdue arrears as of snapshot")
)
PARTITION BY snapshot_date
CLUSTER BY branch_key, product_key;
