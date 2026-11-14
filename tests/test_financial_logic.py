"""
Financial Business Logic and Amortisation Engine Tests.
Verifies reducing-balance amortisation, FIFO payment waterfall, snapshot-specific
DPD calculation, historical payment cut-off, and referential integrity.
"""

import pytest

def test_referential_integrity_loan_to_branch(db_con):
    """Every loan in dim_loan must map to a valid branch dimension entry."""
    orphan_cnt = db_con.execute("""
        SELECT COUNT(*) 
        FROM fin_warehouse.dim_loan dl
        LEFT JOIN fin_warehouse.dim_branch db ON dl.branch_id = db.branch_id
        WHERE dl.loan_key > 0 AND db.branch_key IS NULL
    """).fetchone()[0]
    assert orphan_cnt == 0, f"Found {orphan_cnt} loans not mapped to branch dimension"

def test_referential_integrity_loan_to_product(db_con):
    """Every loan in dim_loan must map to a valid product dimension entry."""
    orphan_cnt = db_con.execute("""
        SELECT COUNT(*) 
        FROM fin_warehouse.dim_loan dl
        LEFT JOIN fin_warehouse.dim_product dp ON dl.product_id = dp.product_id
        WHERE dl.loan_key > 0 AND dp.product_key IS NULL
    """).fetchone()[0]
    assert orphan_cnt == 0, f"Found {orphan_cnt} loans not mapped to product dimension"

def test_referential_integrity_loan_to_state(db_con):
    """Every loan in dim_loan must map to a valid state dimension entry."""
    orphan_cnt = db_con.execute("""
        SELECT COUNT(*) 
        FROM fin_warehouse.dim_loan dl
        LEFT JOIN fin_warehouse.dim_state ds ON dl.state_id = ds.state_id
        WHERE dl.loan_key > 0 AND ds.state_key IS NULL
    """).fetchone()[0]
    assert orphan_cnt == 0, f"Found {orphan_cnt} loans not mapped to state dimension"

def test_referential_integrity_loan_to_segment(db_con):
    """Every loan monthly snapshot must map to a valid borrower segment dimension entry."""
    orphan_cnt = db_con.execute("""
        SELECT COUNT(*) 
        FROM fin_warehouse.fact_loan_monthly f
        LEFT JOIN fin_warehouse.dim_borrower_segment dbs ON f.borrower_segment_key = dbs.borrower_segment_key
        WHERE dbs.borrower_segment_key IS NULL
    """).fetchone()[0]
    assert orphan_cnt == 0, f"Found {orphan_cnt} snapshots not mapped to segment dimension"

def test_fifo_waterfall_allocation_order(db_con):
    """Verifies FIFO sequential waterfall allocation: prior instalments satisfied before subsequent ones."""
    out_of_order = db_con.execute("""
        WITH inst_paid AS (
            SELECT 
                loan_id,
                instalment_number,
                SUM(allocated_amount) as total_alloc
            FROM fin_staging.stg_instalment_allocation
            GROUP BY loan_id, instalment_number
        ),
        checks AS (
            SELECT 
                i.loan_id,
                i.instalment_number,
                i.amount_due,
                COALESCE(p.total_alloc, 0.0) as alloc,
                LEAD(p.total_alloc) OVER (PARTITION BY i.loan_id ORDER BY i.instalment_number) as next_alloc
            FROM fin_staging.stg_instalments i
            LEFT JOIN inst_paid p ON i.loan_id = p.loan_id AND i.instalment_number = p.instalment_number
        )
        SELECT COUNT(*)
        FROM checks
        WHERE next_alloc > 0 AND (amount_due - alloc) > 0.05
    """).fetchone()[0]
    assert out_of_order == 0, f"Found {out_of_order} instalments with out-of-order FIFO allocations"

def test_reducing_balance_amortisation_components(db_con):
    """Allocated principal and interest components must sum exactly to total allocated amount."""
    component_diff = db_con.execute("""
        SELECT COUNT(*) 
        FROM fin_warehouse.fact_instalment_allocation
        WHERE ABS(allocated_amount - (allocated_principal + allocated_interest)) > 0.02
    """).fetchone()[0]
    assert component_diff == 0, f"Found {component_diff} allocations where principal + interest != total allocated"

def test_partial_payments_handling(db_con):
    """Validates that loans with partial payments properly allocate cash without exceeding payment amount."""
    over_allocated = db_con.execute("""
        SELECT COUNT(*) 
        FROM (
            SELECT r.transaction_id, r.payment_amount, SUM(a.allocated_amount) as total_alloc
            FROM fin_staging.stg_repayments r
            JOIN fin_staging.stg_instalment_allocation a ON r.transaction_id = a.transaction_id
            GROUP BY r.transaction_id, r.payment_amount
            HAVING SUM(a.allocated_amount) > r.payment_amount + 0.01
        )
    """).fetchone()[0]
    assert over_allocated == 0, f"Found {over_allocated} transactions over-allocated across instalments"

def test_snapshot_payment_cutoff(db_con):
    """Payments made after snapshot date must strictly have zero effect on earlier snapshot balances."""
    leakage = db_con.execute("""
        WITH jan_snapshot AS (
            SELECT loan_id, amount_paid, outstanding_principal
            FROM fin_warehouse.fact_loan_monthly
            WHERE snapshot_date_key = 20240131
        ),
        payments_after_jan AS (
            SELECT loan_id, SUM(allocated_amount) as post_jan_pay
            FROM fin_staging.stg_instalment_allocation
            WHERE payment_date > DATE '2024-01-31'
            GROUP BY loan_id
        ),
        payments_up_to_jan AS (
            SELECT loan_id, COALESCE(SUM(allocated_amount), 0.0) as jan_pay
            FROM fin_staging.stg_instalment_allocation
            WHERE payment_date <= DATE '2024-01-31'
            GROUP BY loan_id
        )
        SELECT COUNT(*)
        FROM jan_snapshot j
        JOIN payments_after_jan paj ON j.loan_id = paj.loan_id
        LEFT JOIN payments_up_to_jan puj ON j.loan_id = puj.loan_id
        WHERE j.amount_paid > (COALESCE(puj.jan_pay, 0.0) + 0.05)
    """).fetchone()[0]
    assert leakage == 0, f"Found {leakage} snapshots contaminated by future payments"

def test_snapshot_future_instalments_excluded(db_con):
    """DPD calculation must strictly exclude future instalments whose due date is after snapshot date."""
    violations = db_con.execute("""
        WITH snap_dues AS (
            SELECT 
                f.loan_id,
                f.snapshot_date_key,
                d.full_date as snap_date,
                f.days_past_due,
                SUM(CASE WHEN i.amount_due - COALESCE(a.alloc, 0.0) > 0.01 THEN 1 ELSE 0 END) as overdue_past_count
            FROM fin_warehouse.fact_loan_monthly f
            JOIN fin_warehouse.dim_date d ON f.snapshot_date_key = d.date_key
            JOIN fin_staging.stg_instalments i ON f.loan_id = i.loan_id AND i.due_date <= d.full_date
            LEFT JOIN (
                SELECT instalment_id, SUM(allocated_amount) as alloc
                FROM fin_staging.stg_instalment_allocation
                WHERE payment_date <= DATE '2024-12-31'
                GROUP BY instalment_id
            ) a ON i.instalment_id = a.instalment_id
            WHERE f.snapshot_date_key = 20241231
            GROUP BY f.loan_id, f.snapshot_date_key, d.full_date, f.days_past_due
        )
        SELECT COUNT(*) 
        FROM snap_dues
        WHERE overdue_past_count = 0 AND days_past_due > 0
    """).fetchone()[0]
    assert violations == 0, f"Found {violations} loans flagged overdue despite no overdue past instalments"

def test_residual_penny_balance_rule(db_con):
    """Institutional definition: 1-paisa residual rounding differences (< 0.01) do not trigger > 30 DPD."""
    penny_violations = db_con.execute("""
        WITH snap_due AS (
            SELECT 
                f.loan_id,
                f.snapshot_date_key,
                f.days_past_due,
                ROUND(SUM(i.amount_due - i.amount_paid), 2) as residual_balance
            FROM fin_warehouse.fact_loan_monthly f
            JOIN fin_warehouse.dim_date d ON f.snapshot_date_key = d.date_key
            JOIN fin_staging.stg_instalments i ON f.loan_id = i.loan_id AND i.due_date <= d.full_date
            WHERE f.snapshot_date_key = 20241231
            GROUP BY f.loan_id, f.snapshot_date_key, f.days_past_due
            HAVING residual_balance <= 0.01 AND residual_balance > 0
        )
        SELECT COUNT(*) 
        FROM snap_due
        WHERE days_past_due > 30
    """).fetchone()[0]
    assert penny_violations == 0, f"Found {penny_violations} loans flagged > 30 DPD from <= 1-paisa residual balance"

def test_unallocated_cash_is_non_negative(db_con):
    """Transaction unallocated cash must be strictly non-negative (payments >= allocated)."""
    violations = db_con.execute("""
        SELECT COUNT(*) 
        FROM (
            SELECT r.transaction_id, r.payment_amount, COALESCE(SUM(a.allocated_amount), 0.0) as alloc 
            FROM fin_staging.stg_repayments r 
            LEFT JOIN fin_staging.stg_instalment_allocation a ON r.transaction_id = a.transaction_id 
            GROUP BY r.transaction_id, r.payment_amount 
            HAVING r.payment_amount - alloc < -0.01
        )
    """).fetchone()[0]
    assert violations == 0, f"Found {violations} transactions where allocated exceeds payment"

def test_dpd_matches_schedule(db_con):
    """Dynamic snapshot DPD in fact_loan_monthly accurately reflects arrears for overdue unpaid loans."""
    bad_dpd = db_con.execute("""
        WITH unpaid_prior_instalments AS (
            SELECT 
                ls.loan_id,
                ls.snapshot_date_key
            FROM fin_warehouse.fact_loan_monthly ls
            JOIN fin_warehouse.dim_date d ON ls.snapshot_date_key = d.date_key
            JOIN fin_staging.stg_instalments i ON ls.loan_id = i.loan_id AND i.due_date < d.full_date
            LEFT JOIN fin_staging.stg_instalment_allocation a ON i.instalment_id = a.instalment_id AND a.payment_date <= d.full_date
            GROUP BY ls.loan_id, ls.snapshot_date_key, i.instalment_id, i.amount_due
            HAVING (i.amount_due - COALESCE(SUM(a.allocated_amount), 0.0)) > 0.01
        )
        SELECT COUNT(*) 
        FROM unpaid_prior_instalments up
        JOIN fin_warehouse.fact_loan_monthly f ON up.loan_id = f.loan_id AND up.snapshot_date_key = f.snapshot_date_key
        WHERE f.days_past_due = 0
    """).fetchone()[0]
    assert bad_dpd == 0, f"Found {bad_dpd} snapshots with prior overdue instalments having 0 DPD"
