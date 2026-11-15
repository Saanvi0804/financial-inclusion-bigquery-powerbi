-- BigQuery KPI Model: kpi_portfolio_health.sql
-- Portfolio at Risk (PAR30, PAR90) and delinquency breakdown across dimensions

CREATE OR REPLACE TABLE `fin_analytics.kpi_portfolio_health` AS
SELECT 
    d.year_month,
    f.snapshot_date,
    f.snapshot_date_key,
    s.state_id,
    s.state_name,
    s.region,
    b.branch_id,
    b.branch_name,
    b.location_type AS branch_location_type,
    p.product_id,
    p.product_name,
    p.category AS product_category,
    bs.borrower_segment,
    COUNT(DISTINCT CASE WHEN f.outstanding_principal > 0 THEN f.loan_id END) AS total_active_loans,
    COUNT(DISTINCT f.loan_id) AS total_cumulative_loans,
    SUM(f.outstanding_principal) AS total_outstanding_principal,
    -- Delinquency bucket balances
    SUM(CASE WHEN f.days_past_due = 0 THEN f.outstanding_principal ELSE NUMERIC '0.0' END) AS principal_current,
    SUM(CASE WHEN f.days_past_due BETWEEN 1 AND 30 THEN f.outstanding_principal ELSE NUMERIC '0.0' END) AS principal_dpd_1_30,
    SUM(CASE WHEN f.days_past_due BETWEEN 31 AND 60 THEN f.outstanding_principal ELSE NUMERIC '0.0' END) AS principal_dpd_31_60,
    SUM(CASE WHEN f.days_past_due BETWEEN 61 AND 90 THEN f.outstanding_principal ELSE NUMERIC '0.0' END) AS principal_dpd_61_90,
    SUM(CASE WHEN f.days_past_due > 90 THEN f.outstanding_principal ELSE NUMERIC '0.0' END) AS principal_dpd_90_plus,
    -- PAR30 & PAR90 Balance
    SUM(CASE WHEN f.days_past_due > 30 THEN f.outstanding_principal ELSE NUMERIC '0.0' END) AS par30_principal,
    SUM(CASE WHEN f.days_past_due > 90 THEN f.outstanding_principal ELSE NUMERIC '0.0' END) AS par90_principal,
    -- PAR Rates (%)
    COALESCE(
        ROUND(
            SAFE_DIVIDE(SUM(CASE WHEN f.days_past_due > 30 THEN f.outstanding_principal ELSE NUMERIC '0.0' END) * NUMERIC '100.0', 
                        SUM(f.outstanding_principal)), 
            4
        ),
        NUMERIC '0.0'
    ) AS par30_pct,
    COALESCE(
        ROUND(
            SAFE_DIVIDE(SUM(CASE WHEN f.days_past_due > 90 THEN f.outstanding_principal ELSE NUMERIC '0.0' END) * NUMERIC '100.0', 
                        SUM(f.outstanding_principal)), 
            4
        ),
        NUMERIC '0.0'
    ) AS par90_pct
FROM `fin_warehouse.fact_loan_monthly` f
JOIN `fin_warehouse.dim_date` d ON f.snapshot_date_key = d.date_key
JOIN `fin_warehouse.dim_state` s ON f.state_key = s.state_key
JOIN `fin_warehouse.dim_branch` b ON f.branch_key = b.branch_key
JOIN `fin_warehouse.dim_product` p ON f.product_key = p.product_key
JOIN `fin_warehouse.dim_borrower_segment` bs ON f.borrower_segment_key = bs.borrower_segment_key
GROUP BY 
    d.year_month, f.snapshot_date, f.snapshot_date_key,
    s.state_id, s.state_name, s.region,
    b.branch_id, b.branch_name, b.location_type,
    p.product_id, p.product_name, p.category, bs.borrower_segment;
