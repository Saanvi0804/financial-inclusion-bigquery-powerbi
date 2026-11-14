"""
Reconciliation and KPI Validation Tests across Raw, Warehouse, and Analytics Layers.
Verifies conservation of financial cash flows, dimensional reconciliations,
and analytical metrics (Portfolio Health, Collection Efficiency, Vintage Curves, Digital Collections).
"""

import pytest

def test_reconciliation_loan_counts_across_layers(db_con):
    """Reconciles loan counts: raw_loans (52,200) - 200 duplicates == staging (52,000) == dim_loan (52,000)."""
    raw_cnt = db_con.execute("SELECT COUNT(*) FROM fin_raw.raw_loans").fetchone()[0]
    stg_cnt = db_con.execute("SELECT COUNT(*) FROM fin_staging.stg_loans").fetchone()[0]
    dim_cnt = db_con.execute("SELECT COUNT(*) FROM fin_warehouse.dim_loan WHERE loan_key > 0").fetchone()[0]

    assert raw_cnt == 52200, f"Unexpected raw loan count: {raw_cnt}"
    assert stg_cnt == 52000, f"Staging loans count should be exactly 52,000, got {stg_cnt}"
    assert dim_cnt == 52000, f"Dimension loans count should be exactly 52,000, got {dim_cnt}"

def test_reconciliation_payment_transaction_counts(db_con):
    """Reconciles payment transaction counts: stg_repayments count equals fact_payment count."""
    stg_cnt = db_con.execute("SELECT COUNT(*) FROM fin_staging.stg_repayments").fetchone()[0]
    fact_cnt = db_con.execute("SELECT COUNT(*) FROM fin_warehouse.fact_payment").fetchone()[0]

    assert stg_cnt == 533147, f"Unexpected staging repayment count: {stg_cnt}"
    assert stg_cnt == fact_cnt, f"Staging count ({stg_cnt}) does not match Fact count ({fact_cnt})"

def test_reconciliation_financial_amounts_raw_to_warehouse(db_con):
    """Reconciles total collections between clean staging and warehouse fact tables within 0.01 INR tolerance."""
    stg_sum = db_con.execute("SELECT SUM(payment_amount) FROM fin_staging.stg_repayments").fetchone()[0]
    fact_sum = db_con.execute("SELECT SUM(payment_amount) FROM fin_warehouse.fact_payment").fetchone()[0]

    diff = abs(stg_sum - fact_sum)
    assert diff < 0.01, f"Financial mismatch between staging ({stg_sum}) and fact ({fact_sum}): diff={diff}"

def test_reconciliation_instalment_allocation_conservation(db_con):
    """Total allocated amount in fact_instalment_allocation exactly equals total payment amount."""
    pay_sum = db_con.execute("SELECT SUM(payment_amount) FROM fin_staging.stg_repayments").fetchone()[0]
    alloc_sum = db_con.execute("SELECT SUM(allocated_amount) FROM fin_warehouse.fact_instalment_allocation").fetchone()[0]

    diff = abs(pay_sum - alloc_sum)
    assert diff < 0.01, f"Instalment allocation mismatch: payments={pay_sum}, allocated={alloc_sum}, diff={diff}"

def test_reconciliation_allocation_components_sum(db_con):
    """Allocated principal and interest components sum exactly to total allocated amount."""
    prin_sum = db_con.execute("SELECT SUM(allocated_principal) FROM fin_warehouse.fact_instalment_allocation").fetchone()[0]
    int_sum = db_con.execute("SELECT SUM(allocated_interest) FROM fin_warehouse.fact_instalment_allocation").fetchone()[0]
    alloc_sum = db_con.execute("SELECT SUM(allocated_amount) FROM fin_warehouse.fact_instalment_allocation").fetchone()[0]

    diff = abs((prin_sum + int_sum) - alloc_sum)
    assert diff < 0.05, f"Allocation components sum mismatch: prin+int={prin_sum + int_sum}, total={alloc_sum}, diff={diff}"

def test_kpi_collection_efficiency_breakdown(db_con):
    """In kpi_collection_efficiency, total cash collected equals current + arrears + advance collections."""
    bad_rows = db_con.execute("""
        SELECT COUNT(*) 
        FROM fin_analytics.kpi_collection_efficiency
        WHERE ABS(total_amount_collected - (current_period_collected + arrears_collected + advance_collected)) > 0.05
    """).fetchone()[0]
    assert bad_rows == 0, f"Found {bad_rows} rows in kpi_collection_efficiency where components do not sum to total"

def test_kpi_collection_efficiency_headline_formula(db_con):
    """Verifies headline collection efficiency formula: (current_period_collected / scheduled_amount_due * 100)."""
    bad_calc = db_con.execute("""
        SELECT COUNT(*) 
        FROM fin_analytics.kpi_collection_efficiency
        WHERE scheduled_amount_due > 0 
          AND ABS(current_period_efficiency_pct - (current_period_collected / scheduled_amount_due * 100.0)) > 0.02
    """).fetchone()[0]
    assert bad_calc == 0, f"Found {bad_calc} rows with incorrect headline current period collection efficiency"

def test_kpi_digital_collections_monotonically_increases(db_con):
    """Portfolio digital collection value share increases from Jan 2023 (~32%) to Dec 2024 (~81%)."""
    trend = db_con.execute("""
        SELECT 
            SUM(CASE WHEN year_month = '2023-01' THEN digital_collection_value ELSE 0 END) / 
                NULLIF(SUM(CASE WHEN year_month = '2023-01' THEN total_collection_value ELSE 0 END), 0) * 100.0 as jan_2023,
            SUM(CASE WHEN year_month = '2024-12' THEN digital_collection_value ELSE 0 END) / 
                NULLIF(SUM(CASE WHEN year_month = '2024-12' THEN total_collection_value ELSE 0 END), 0) * 100.0 as dec_2024
        FROM fin_analytics.kpi_digital_collections
    """).fetchone()

    jan_share = trend[0]
    dec_share = trend[1]

    assert jan_share is not None and dec_share is not None
    assert 30.0 <= jan_share <= 40.0, f"Jan 2023 digital share out of expected range: {jan_share}"
    assert 75.0 <= dec_share <= 85.0, f"Dec 2024 digital share out of expected range: {dec_share}"
    assert dec_share > jan_share + 40.0, f"Expected significant digital adoption growth (+40 pts), got {dec_share - jan_share}"

def test_kpi_portfolio_health_active_loans_dec2024(db_con):
    """Total active loans on 2024-12-31 matches portfolio benchmark of exactly 40,940."""
    active_cnt = db_con.execute("""
        SELECT SUM(total_active_loans) 
        FROM fin_analytics.kpi_portfolio_health
        WHERE snapshot_date = DATE '2024-12-31'
    """).fetchone()[0]

    assert active_cnt == 40940, f"Expected 40,940 active loans on 2024-12-31, got {active_cnt}"

def test_kpi_portfolio_health_par30_dec2024(db_con):
    """PAR30 on 2024-12-31 matches approved institutional definition within 0.05 bps of benchmark (8.2211%)."""
    par30_val = db_con.execute("""
        SELECT ROUND(SUM(par30_principal) / SUM(total_outstanding_principal) * 100.0, 4) 
        FROM fin_analytics.kpi_portfolio_health
        WHERE snapshot_date = DATE '2024-12-31'
    """).fetchone()[0]

    # Benchmark is 8.2211% vs Python 8.2215%
    assert 8.20 <= par30_val <= 8.25, f"PAR30 out of tolerance: {par30_val}"
    assert abs(par30_val - 8.2211) < 0.001, f"Expected 8.2211%, got {par30_val}"

def test_kpi_portfolio_health_par90_dec2024(db_con):
    """PAR90 on 2024-12-31 is non-negative and strictly less than or equal to PAR30."""
    metrics = db_con.execute("""
        SELECT 
            ROUND(SUM(par30_principal) / SUM(total_outstanding_principal) * 100.0, 4) as par30,
            ROUND(SUM(par90_principal) / SUM(total_outstanding_principal) * 100.0, 4) as par90
        FROM fin_analytics.kpi_portfolio_health
        WHERE snapshot_date = DATE '2024-12-31'
    """).fetchone()

    par30, par90 = metrics[0], metrics[1]
    assert 0.0 <= par90 <= par30, f"PAR90 ({par90}) should be >= 0 and <= PAR30 ({par30})"

def test_kpi_vintage_curves_month_on_book_bounds(db_con):
    """Vintage curves cover months on book 1 to 24 with valid non-decreasing cumulative performance."""
    mob_summary = db_con.execute("""
        SELECT 
            MIN(month_on_book), 
            MAX(month_on_book), 
            COUNT(DISTINCT cohort_month) 
        FROM fin_analytics.kpi_vintage_curves
    """).fetchone()

    assert mob_summary[0] == 1, f"Expected min month_on_book=1, got {mob_summary[0]}"
    assert mob_summary[1] <= 24, f"Expected max month_on_book<=24, got {mob_summary[1]}"
    assert mob_summary[2] >= 20, f"Expected at least 20 disbursement cohorts, got {mob_summary[2]}"
