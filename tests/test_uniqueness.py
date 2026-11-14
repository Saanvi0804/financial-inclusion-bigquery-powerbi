"""
Primary Key and Uniqueness Tests across Raw, Staging, and Dimensional Layers.
Verifies that duplicate records in raw data are correctly detected and that
warehouse dimensions and fact tables enforce strict primary key uniqueness.
"""

import pytest

def test_raw_loans_seeded_duplicates_detected(db_con):
    """Detects deliberately seeded duplicate loans in raw layer (Issue 1)."""
    dup_cnt = db_con.execute("""
        SELECT COUNT(*) FROM (
            SELECT loan_id, COUNT(*) 
            FROM fin_raw.raw_loans 
            GROUP BY loan_id 
            HAVING COUNT(*) > 1
        )
    """).fetchone()[0]
    assert dup_cnt == 200, f"Expected 200 duplicate loan keys in raw data, found {dup_cnt}"

def test_raw_repayments_seeded_duplicates_detected(db_con):
    """Detects deliberately seeded duplicate payment transactions in raw layer (Issue 2)."""
    dup_cnt = db_con.execute("""
        SELECT COUNT(*) FROM (
            SELECT transaction_id, COUNT(*) 
            FROM fin_raw.raw_repayments 
            GROUP BY transaction_id 
            HAVING COUNT(*) > 1
        )
    """).fetchone()[0]
    assert dup_cnt in (398, 400), f"Expected ~400 duplicate transactions in raw, found {dup_cnt}"

def test_warehouse_dim_loan_unique_ids(db_con):
    """Warehouse dim_loan must have strictly unique loan IDs (excluding fallback row)."""
    dup_cnt = db_con.execute("""
        SELECT COUNT(*) FROM (
            SELECT loan_id, COUNT(*) 
            FROM fin_warehouse.dim_loan 
            WHERE loan_key > 0 
            GROUP BY loan_id 
            HAVING COUNT(*) > 1
        )
    """).fetchone()[0]
    assert dup_cnt == 0, f"Found {dup_cnt} duplicate loan_ids in fin_warehouse.dim_loan"

def test_warehouse_dim_loan_unique_surrogate_keys(db_con):
    """Warehouse dim_loan must have unique surrogate loan_key values."""
    dup_cnt = db_con.execute("""
        SELECT COUNT(*) FROM (
            SELECT loan_key, COUNT(*) 
            FROM fin_warehouse.dim_loan 
            GROUP BY loan_key 
            HAVING COUNT(*) > 1
        )
    """).fetchone()[0]
    assert dup_cnt == 0, f"Found {dup_cnt} duplicate loan_key values in dim_loan"

def test_warehouse_dim_branch_unique_keys(db_con):
    """Warehouse dim_branch must have strictly unique branch_id and branch_key."""
    dup_id = db_con.execute("""
        SELECT COUNT(*) FROM (
            SELECT branch_id, COUNT(*) 
            FROM fin_warehouse.dim_branch 
            WHERE branch_key > 0 
            GROUP BY branch_id 
            HAVING COUNT(*) > 1
        )
    """).fetchone()[0]
    dup_key = db_con.execute("""
        SELECT COUNT(*) FROM (
            SELECT branch_key, COUNT(*) 
            FROM fin_warehouse.dim_branch 
            GROUP BY branch_key 
            HAVING COUNT(*) > 1
        )
    """).fetchone()[0]
    assert dup_id == 0, f"Found {dup_id} duplicate branch_ids in dim_branch"
    assert dup_key == 0, f"Found {dup_key} duplicate branch_keys in dim_branch"

def test_warehouse_dim_state_unique_keys(db_con):
    """Warehouse dim_state must have strictly unique state_id and state_key."""
    dup_id = db_con.execute("""
        SELECT COUNT(*) FROM (
            SELECT state_id, COUNT(*) 
            FROM fin_warehouse.dim_state 
            WHERE state_key > 0 
            GROUP BY state_id 
            HAVING COUNT(*) > 1
        )
    """).fetchone()[0]
    dup_key = db_con.execute("""
        SELECT COUNT(*) FROM (
            SELECT state_key, COUNT(*) 
            FROM fin_warehouse.dim_state 
            GROUP BY state_key 
            HAVING COUNT(*) > 1
        )
    """).fetchone()[0]
    assert dup_id == 0, f"Found {dup_id} duplicate state_ids in dim_state"
    assert dup_key == 0, f"Found {dup_key} duplicate state_keys in dim_state"

def test_warehouse_dim_product_unique_keys(db_con):
    """Warehouse dim_product must have strictly unique product_id and product_key."""
    dup_id = db_con.execute("""
        SELECT COUNT(*) FROM (
            SELECT product_id, COUNT(*) 
            FROM fin_warehouse.dim_product 
            WHERE product_key > 0 
            GROUP BY product_id 
            HAVING COUNT(*) > 1
        )
    """).fetchone()[0]
    dup_key = db_con.execute("""
        SELECT COUNT(*) FROM (
            SELECT product_key, COUNT(*) 
            FROM fin_warehouse.dim_product 
            GROUP BY product_key 
            HAVING COUNT(*) > 1
        )
    """).fetchone()[0]
    assert dup_id == 0, f"Found {dup_id} duplicate product_ids in dim_product"
    assert dup_key == 0, f"Found {dup_key} duplicate product_keys in dim_product"

def test_warehouse_dim_borrower_segment_unique_keys(db_con):
    """Warehouse dim_borrower_segment must have strictly unique borrower_segment_key values."""
    dup_key = db_con.execute("""
        SELECT COUNT(*) FROM (
            SELECT borrower_segment_key, COUNT(*) 
            FROM fin_warehouse.dim_borrower_segment 
            GROUP BY borrower_segment_key 
            HAVING COUNT(*) > 1
        )
    """).fetchone()[0]
    assert dup_key == 0, f"Found {dup_key} duplicate borrower_segment_keys in dim_borrower_segment"

def test_warehouse_dim_date_unique_keys(db_con):
    """Warehouse dim_date must have unique date_key and full_date values."""
    dup_id = db_con.execute("""
        SELECT COUNT(*) FROM (
            SELECT full_date, COUNT(*) 
            FROM fin_warehouse.dim_date 
            GROUP BY full_date 
            HAVING COUNT(*) > 1
        )
    """).fetchone()[0]
    dup_key = db_con.execute("""
        SELECT COUNT(*) FROM (
            SELECT date_key, COUNT(*) 
            FROM fin_warehouse.dim_date 
            GROUP BY date_key 
            HAVING COUNT(*) > 1
        )
    """).fetchone()[0]
    assert dup_id == 0, f"Found {dup_id} duplicate full_date values in dim_date"
    assert dup_key == 0, f"Found {dup_key} duplicate date_keys in dim_date"

def test_warehouse_fact_payment_unique_transactions(db_con):
    """Warehouse fact_payment must have strictly unique transaction IDs."""
    dup_cnt = db_con.execute("""
        SELECT COUNT(*) FROM (
            SELECT transaction_id, COUNT(*) 
            FROM fin_warehouse.fact_payment 
            GROUP BY transaction_id 
            HAVING COUNT(*) > 1
        )
    """).fetchone()[0]
    assert dup_cnt == 0, f"Found {dup_cnt} duplicate transactions in fin_warehouse.fact_payment"

def test_warehouse_fact_loan_monthly_grain_uniqueness(db_con):
    """Grain check: exactly one row per loan per month-end snapshot in fact_loan_monthly."""
    dup_cnt = db_con.execute("""
        SELECT COUNT(*) FROM (
            SELECT loan_id, snapshot_date_key, COUNT(*) 
            FROM fin_warehouse.fact_loan_monthly 
            GROUP BY loan_id, snapshot_date_key 
            HAVING COUNT(*) > 1
        )
    """).fetchone()[0]
    assert dup_cnt == 0, f"Found {dup_cnt} duplicate loan monthly snapshots"

def test_staging_loans_uniqueness(db_con):
    """Cleaned staging layer stg_loans must have deduplicated exactly 52,000 unique loans."""
    cnt = db_con.execute("SELECT COUNT(*), COUNT(DISTINCT loan_id) FROM fin_staging.stg_loans").fetchone()
    assert cnt[0] == 52000, f"Expected 52,000 loans in staging, got {cnt[0]}"
    assert cnt[0] == cnt[1], f"Staging loans has non-unique loan_ids: total={cnt[0]}, distinct={cnt[1]}"

def test_staging_repayments_uniqueness(db_con):
    """Cleaned staging layer stg_repayments must have unique transaction IDs."""
    cnt = db_con.execute("SELECT COUNT(*), COUNT(DISTINCT transaction_id) FROM fin_staging.stg_repayments").fetchone()
    assert cnt[0] == cnt[1], f"Staging repayments has duplicate transactions: total={cnt[0]}, distinct={cnt[1]}"
