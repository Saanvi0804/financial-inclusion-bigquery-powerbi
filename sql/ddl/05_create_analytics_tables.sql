-- BigQuery DDL: 05_create_analytics_tables.sql
-- Pre-aggregated analytical KPI models for Portfolio Health, Collection Efficiency, Vintage Curves, and Digital Adoption

CREATE TABLE IF NOT EXISTS `fin_analytics.kpi_portfolio_health` (
    year_month STRING OPTIONS(description="Reporting calendar period (YYYY-MM)"),
    snapshot_date DATE OPTIONS(description="Month-end snapshot date"),
    snapshot_date_key INT64 OPTIONS(description="FK to dim_date"),
    state_id STRING OPTIONS(description="FK to dim_state (e.g. ST_MH)"),
    state_name STRING OPTIONS(description="State name"),
    region STRING OPTIONS(description="Indian geographic region"),
    branch_id STRING OPTIONS(description="FK to dim_branch (e.g. BR001)"),
    branch_name STRING OPTIONS(description="Branch office name"),
    branch_location_type STRING OPTIONS(description="Urban, Semi-Urban, Rural"),
    product_id STRING OPTIONS(description="FK to dim_product (e.g. PRD_MFI)"),
    product_name STRING OPTIONS(description="Loan product name"),
    product_category STRING OPTIONS(description="Microfinance, Agri, MSME, Personal, Education"),
    borrower_segment STRING OPTIONS(description="Borrower demographic category"),
    total_active_loans INT64 OPTIONS(description="Count of loans with positive outstanding principal"),
    total_cumulative_loans INT64 OPTIONS(description="Total loans originated on or before snapshot"),
    total_outstanding_principal NUMERIC(14, 2) OPTIONS(description="Total portfolio outstanding principal balance in INR"),
    principal_current NUMERIC(14, 2) OPTIONS(description="Outstanding principal on performing loans (DPD = 0)"),
    principal_dpd_1_30 NUMERIC(14, 2) OPTIONS(description="Outstanding principal in 1-30 DPD bucket"),
    principal_dpd_31_60 NUMERIC(14, 2) OPTIONS(description="Outstanding principal in 31-60 DPD bucket"),
    principal_dpd_61_90 NUMERIC(14, 2) OPTIONS(description="Outstanding principal in 61-90 DPD bucket"),
    principal_dpd_90_plus NUMERIC(14, 2) OPTIONS(description="Outstanding principal in > 90 DPD bucket (NPA)"),
    par30_principal NUMERIC(14, 2) OPTIONS(description="Portfolio at Risk > 30 Days principal balance"),
    par90_principal NUMERIC(14, 2) OPTIONS(description="Portfolio at Risk > 90 Days principal balance (NPA)"),
    par30_pct NUMERIC(7, 4) OPTIONS(description="PAR30 ratio percentage: (PAR30 Principal / Total Outstanding Principal) * 100"),
    par90_pct NUMERIC(7, 4) OPTIONS(description="PAR90 ratio percentage: (PAR90 Principal / Total Outstanding Principal) * 100")
)
CLUSTER BY year_month, state_id, product_id;

CREATE TABLE IF NOT EXISTS `fin_analytics.kpi_collection_efficiency` (
    year_month STRING OPTIONS(description="Reporting billing month (YYYY-MM)"),
    month_date_key INT64 OPTIONS(description="FK to dim_date for month start (YYYYMM01)"),
    state_id STRING OPTIONS(description="FK to dim_state"),
    state_name STRING OPTIONS(description="State name"),
    branch_id STRING OPTIONS(description="FK to dim_branch"),
    branch_name STRING OPTIONS(description="Branch office name"),
    product_id STRING OPTIONS(description="FK to dim_product"),
    product_name STRING OPTIONS(description="Loan product name"),
    scheduled_amount_due NUMERIC(14, 2) OPTIONS(description="Contractual billing due in current month"),
    current_period_collected NUMERIC(14, 2) OPTIONS(description="Cash collected against current-month billing"),
    arrears_collected NUMERIC(14, 2) OPTIONS(description="Cash collected against overdue arrears (due_date < current_month)"),
    advance_collected NUMERIC(14, 2) OPTIONS(description="Cash collected in advance against future instalments (due_date > current_month)"),
    total_amount_collected NUMERIC(14, 2) OPTIONS(description="Total gross cash collections in month"),
    current_period_efficiency_pct NUMERIC(7, 2) OPTIONS(description="Current-period scheduled efficiency percentage (bounded [0, 100])"),
    total_collection_ratio_pct NUMERIC(7, 2) OPTIONS(description="Total cash collection ratio (can exceed 100% on recovery drives)"),
    collection_efficiency_pct NUMERIC(7, 2) OPTIONS(description="Standard collection efficiency percentage")
)
CLUSTER BY year_month, branch_id;

CREATE TABLE IF NOT EXISTS `fin_analytics.kpi_vintage_curves` (
    cohort_month STRING OPTIONS(description="Origination disbursement month (YYYY-MM)"),
    cohort_date_key INT64 OPTIONS(description="FK to dim_date for cohort month start (YYYYMM01)"),
    product_id STRING OPTIONS(description="FK to dim_product"),
    product_name STRING OPTIONS(description="Loan product name"),
    product_category STRING OPTIONS(description="Product category"),
    month_on_book INT64 OPTIONS(description="Tenure seasoning index (MOB 1, 2, ..., 24)"),
    total_cohort_loans INT64 OPTIONS(description="Original number of loans disbursed in cohort"),
    scheduled_due_mob NUMERIC(14, 2) OPTIONS(description="Contractual dues falling in specific MOB"),
    amount_paid_mob NUMERIC(14, 2) OPTIONS(description="Actual cash collected in specific MOB"),
    cumulative_scheduled_due NUMERIC(14, 2) OPTIONS(description="Cumulative scheduled contractual dues through MOB"),
    cumulative_amount_paid NUMERIC(14, 2) OPTIONS(description="Cumulative cash collections through MOB"),
    vintage_repayment_rate_pct NUMERIC(7, 2) OPTIONS(description="Cumulative collection percentage: (Cum Paid / Cum Due) * 100")
)
CLUSTER BY cohort_month, product_id;

CREATE TABLE IF NOT EXISTS `fin_analytics.kpi_digital_collections` (
    year_month STRING OPTIONS(description="Calendar transaction month (YYYY-MM)"),
    month_date_key INT64 OPTIONS(description="FK to dim_date for month start (YYYYMM01)"),
    state_id STRING OPTIONS(description="FK to dim_state"),
    state_name STRING OPTIONS(description="State name"),
    total_collection_value NUMERIC(14, 2) OPTIONS(description="Total collection volume across all channels in INR"),
    total_transaction_count INT64 OPTIONS(description="Total count of repayment transactions"),
    digital_collection_value NUMERIC(14, 2) OPTIONS(description="Collections via UPI and Bank Transfer"),
    digital_transaction_count INT64 OPTIONS(description="Count of UPI and Bank Transfer transactions"),
    cash_collection_value NUMERIC(14, 2) OPTIONS(description="Collections via physical cash"),
    cash_transaction_count INT64 OPTIONS(description="Count of cash transactions"),
    upi_value NUMERIC(14, 2) OPTIONS(description="UPI volume"),
    upi_count INT64 OPTIONS(description="UPI transaction count"),
    bank_transfer_value NUMERIC(14, 2) OPTIONS(description="Bank transfer volume"),
    bank_transfer_count INT64 OPTIONS(description="Bank transfer transaction count"),
    avg_ticket_upi NUMERIC(10, 2) OPTIONS(description="Average ticket size for UPI transactions"),
    avg_ticket_bank_transfer NUMERIC(10, 2) OPTIONS(description="Average ticket size for Bank Transfers"),
    avg_ticket_cash NUMERIC(10, 2) OPTIONS(description="Average ticket size for Cash transactions"),
    avg_ticket_overall NUMERIC(10, 2) OPTIONS(description="Average ticket size across all channels"),
    digital_value_share_pct NUMERIC(7, 2) OPTIONS(description="Share of total value processed digitally: (Digital Value / Total Value) * 100"),
    digital_count_share_pct NUMERIC(7, 2) OPTIONS(description="Share of total transactions processed digitally"),
    prev_month_digital_value_share NUMERIC(7, 2) OPTIONS(description="Prior month digital value share"),
    mom_digital_value_share_pts NUMERIC(7, 2) OPTIONS(description="Month-on-Month percentage point change"),
    mom_digital_value_growth_pct NUMERIC(7, 2) OPTIONS(description="Month-on-Month relative growth rate"),
    prev_year_digital_value_share NUMERIC(7, 2) OPTIONS(description="Prior year digital value share"),
    yoy_digital_value_share_pts NUMERIC(7, 2) OPTIONS(description="Year-on-Year percentage point change"),
    yoy_digital_value_growth_pct NUMERIC(7, 2) OPTIONS(description="Year-on-Year relative growth rate")
)
CLUSTER BY year_month, state_id;
