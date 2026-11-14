"""
Completeness and Validity Tests across Warehouse Layers.
Ensures zero nulls in required business and surrogate keys, positive loan values,
valid enum domain values, and chronological date boundaries.
"""

import pytest

def test_completeness_no_null_loan_ids(db_con):
    """No null or empty loan IDs in warehouse.dim_loan (excluding fallback)."""
    null_cnt = db_con.execute("""
        SELECT COUNT(*) 
        FROM fin_warehouse.dim_loan 
        WHERE loan_key > 0 AND (loan_id IS NULL OR TRIM(loan_id) = '')
    """).fetchone()[0]
    assert null_cnt == 0, f"Found {null_cnt} null loan IDs in dim_loan"

def test_completeness_no_null_transaction_ids(db_con):
    """No null or empty transaction IDs in warehouse.fact_payment."""
    null_cnt = db_con.execute("""
        SELECT COUNT(*) 
        FROM fin_warehouse.fact_payment 
        WHERE transaction_id IS NULL OR TRIM(transaction_id) = ''
    """).fetchone()[0]
    assert null_cnt == 0, f"Found {null_cnt} null transaction IDs in fact_payment"

def test_completeness_no_missing_financial_fields(db_con):
    """Required financial metrics in fact tables must not be null."""
    null_fact_pay = db_con.execute("""
        SELECT COUNT(*) FROM fin_warehouse.fact_payment WHERE payment_amount IS NULL
    """).fetchone()[0]
    null_fact_loan = db_con.execute("""
        SELECT COUNT(*) FROM fin_warehouse.fact_loan_monthly 
        WHERE outstanding_principal IS NULL OR amount_due IS NULL OR amount_paid IS NULL
    """).fetchone()[0]
    assert null_fact_pay == 0, f"Found {null_fact_pay} null payment amounts in fact_payment"
    assert null_fact_loan == 0, f"Found {null_fact_loan} null values in monthly loan facts"

def test_completeness_no_null_foreign_keys_fact_payment(db_con):
    """Foreign keys in fact_payment must not be null (must map to valid key or -1 fallback)."""
    null_fk = db_con.execute("""
        SELECT COUNT(*) 
        FROM fin_warehouse.fact_payment 
        WHERE loan_key IS NULL OR payment_date_key IS NULL OR branch_key IS NULL 
           OR state_key IS NULL OR product_key IS NULL OR borrower_segment_key IS NULL
    """).fetchone()[0]
    assert null_fk == 0, f"Found {null_fk} null foreign keys in fact_payment"

def test_completeness_no_null_foreign_keys_fact_loan_monthly(db_con):
    """Foreign keys in fact_loan_monthly must not be null."""
    null_fk = db_con.execute("""
        SELECT COUNT(*) 
        FROM fin_warehouse.fact_loan_monthly 
        WHERE loan_key IS NULL OR snapshot_date_key IS NULL OR branch_key IS NULL 
           OR state_key IS NULL OR product_key IS NULL OR borrower_segment_key IS NULL
    """).fetchone()[0]
    assert null_fk == 0, f"Found {null_fk} null foreign keys in fact_loan_monthly"

def test_validity_loan_principal_positive(db_con):
    """Loan principal amounts must be strictly positive."""
    invalid_prin = db_con.execute("""
        SELECT COUNT(*) 
        FROM fin_warehouse.dim_loan 
        WHERE loan_key > 0 AND principal_amount <= 0
    """).fetchone()[0]
    assert invalid_prin == 0, f"Found {invalid_prin} non-positive principal amounts in dim_loan"

def test_validity_loan_tenure_range(db_con):
    """Loan tenures must be valid positive durations (12 to 36 months)."""
    invalid_tenure = db_con.execute("""
        SELECT COUNT(*) 
        FROM fin_warehouse.dim_loan 
        WHERE loan_key > 0 AND (tenure_months < 12 OR tenure_months > 36)
    """).fetchone()[0]
    assert invalid_tenure == 0, f"Found {invalid_tenure} invalid tenure values in dim_loan"

def test_validity_interest_rate_range(db_con):
    """Annual interest rates must be within valid portfolio underwriting bounds (10% to 36%)."""
    invalid_rates = db_con.execute("""
        SELECT COUNT(*) 
        FROM fin_warehouse.dim_loan 
        WHERE loan_key > 0 AND (annual_interest_rate < 10.0 OR annual_interest_rate > 36.0)
    """).fetchone()[0]
    assert invalid_rates == 0, f"Found {invalid_rates} invalid annual_interest_rate values in dim_loan"

def test_validity_payment_channels(db_con):
    """Repayment channels in fact_payment must be valid recognized channels ('Cash', 'UPI', 'Bank_Transfer')."""
    invalid_channels = db_con.execute("""
        SELECT COUNT(*) 
        FROM fin_warehouse.fact_payment 
        WHERE payment_channel NOT IN ('Cash', 'UPI', 'Bank_Transfer', 'Bank Transfer')
    """).fetchone()[0]
    assert invalid_channels == 0, f"Found {invalid_channels} invalid payment channels in fact_payment"

def test_validity_loan_status_values(db_con):
    """Loan status values in dim_loan must belong to approved financial lifecycle states."""
    invalid_status = db_con.execute("""
        SELECT COUNT(*) 
        FROM fin_warehouse.dim_loan 
        WHERE loan_key > 0 AND loan_status NOT IN ('Active', 'Closed', 'Defaulted', 'Written-Off')
    """).fetchone()[0]
    assert invalid_status == 0, f"Found {invalid_status} invalid loan statuses in dim_loan"

def test_validity_date_chronology(db_con):
    """Instalment due dates must be on or after loan disbursement date."""
    invalid_dates = db_con.execute("""
        SELECT COUNT(*) 
        FROM fin_staging.stg_instalments i
        JOIN fin_warehouse.dim_loan l ON i.loan_id = l.loan_id
        WHERE l.loan_key > 0 AND i.due_date < l.disbursement_date
    """).fetchone()[0]
    assert invalid_dates == 0, f"Found {invalid_dates} instalments scheduled before loan disbursement"

def test_validity_dpd_non_negative(db_con):
    """Days past due (DPD) in monthly snapshots must be strictly non-negative."""
    neg_dpd = db_con.execute("""
        SELECT COUNT(*) 
        FROM fin_warehouse.fact_loan_monthly 
        WHERE days_past_due < 0
    """).fetchone()[0]
    assert neg_dpd == 0, f"Found {neg_dpd} negative DPD values in fact_loan_monthly"

def test_validity_outstanding_principal_non_negative(db_con):
    """Outstanding principal in monthly snapshots must be strictly non-negative."""
    neg_prin = db_con.execute("""
        SELECT COUNT(*) 
        FROM fin_warehouse.fact_loan_monthly 
        WHERE outstanding_principal < 0
    """).fetchone()[0]
    assert neg_prin == 0, f"Found {neg_prin} negative outstanding principal values"
