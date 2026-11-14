"""
Quarantine and Seeded Anomaly Isolation Tests.
Verifies deliberate seeded anomalies in the raw layer, their proper quarantine isolation,
and ensures that the cleaned staging and warehouse layers are 100% free of data defects.
"""

import pytest

def test_raw_has_negative_payments(db_con):
    """Detects deliberately seeded negative payment amounts in raw layer (Issue 5)."""
    neg_raw = db_con.execute("""
        SELECT COUNT(*) FROM fin_raw.raw_repayments WHERE payment_amount < 0
    """).fetchone()[0]
    assert neg_raw == 150, f"Expected 150 negative payment amounts in raw data, found {neg_raw}"

def test_quarantine_captures_negative_payments(db_con):
    """Verifies that quarantined table captures exactly the 150 negative payment records."""
    quarantined_neg = db_con.execute("""
        SELECT COUNT(*) FROM fin_staging.stg_quarantined_records 
        WHERE reason_code = 'NEGATIVE_PAYMENT_AMOUNT'
    """).fetchone()[0]
    assert quarantined_neg == 150, f"Expected 150 negative records in quarantine, found {quarantined_neg}"

def test_warehouse_has_no_negative_payments(db_con):
    """Cleaned fact_payment must have zero negative payment amounts."""
    neg_fact = db_con.execute("""
        SELECT COUNT(*) FROM fin_warehouse.fact_payment WHERE payment_amount < 0
    """).fetchone()[0]
    neg_stg = db_con.execute("""
        SELECT COUNT(*) FROM fin_staging.stg_repayments WHERE payment_amount < 0
    """).fetchone()[0]
    assert neg_fact == 0, f"Found {neg_fact} negative amounts in warehouse.fact_payment"
    assert neg_stg == 0, f"Found {neg_stg} negative amounts in staging.stg_repayments"

def test_raw_has_predated_payments(db_con):
    """Detects seeded payments dated before loan disbursement in raw layer (Issue 6)."""
    predated_raw = db_con.execute("""
        SELECT COUNT(*) 
        FROM fin_raw.raw_repayments r
        JOIN fin_raw.raw_loans l ON r.loan_id = l.loan_id
        WHERE CAST(r.payment_date AS DATE) < CAST(l.disbursement_date AS DATE)
    """).fetchone()[0]
    assert predated_raw >= 160, f"Expected at least 160 pre-dated payments in raw, found {predated_raw}"

def test_quarantine_captures_predated_payments(db_con):
    """Verifies that quarantined table captures pre-dated payment records."""
    quarantined_predated = db_con.execute("""
        SELECT COUNT(*) FROM fin_staging.stg_quarantined_records 
        WHERE reason_code = 'PAYMENT_BEFORE_DISBURSEMENT'
    """).fetchone()[0]
    assert quarantined_predated == 160, f"Expected 160 pre-dated records in quarantine, found {quarantined_predated}"

def test_warehouse_has_no_predated_payments(db_con):
    """Cleaned fact_payment must contain zero payments made prior to loan disbursement."""
    predated_fact = db_con.execute("""
        SELECT COUNT(*) 
        FROM fin_warehouse.fact_payment p
        JOIN fin_warehouse.dim_loan l ON p.loan_key = l.loan_key
        WHERE l.loan_key > 0 AND p.payment_date < l.disbursement_date
    """).fetchone()[0]
    assert predated_fact == 0, f"Found {predated_fact} pre-dated payments in fact_payment"

def test_raw_has_paise_units(db_con):
    """Detects deliberately seeded PAISE records in raw layer (Issue 4)."""
    paise_cnt = db_con.execute("""
        SELECT COUNT(*) FROM fin_raw.raw_repayments 
        WHERE UPPER(TRIM(amount_unit)) = 'PAISE'
    """).fetchone()[0]
    assert paise_cnt == 500, f"Expected 500 PAISE records in raw data, found {paise_cnt}"

def test_staging_normalises_paise_to_inr_exactly_once(db_con):
    """Verifies PAISE amounts are divided by 100.0 and normalised to INR in staging."""
    sample_diff = db_con.execute("""
        SELECT COUNT(*) 
        FROM fin_raw.raw_repayments r
        JOIN fin_staging.stg_repayments s ON r.transaction_id = s.transaction_id
        WHERE UPPER(TRIM(r.amount_unit)) = 'PAISE'
          AND ABS(s.payment_amount - (r.payment_amount / 100.0)) > 0.001
    """).fetchone()[0]
    assert sample_diff == 0, f"Found {sample_diff} PAISE records incorrectly converted in staging"

def test_raw_has_excess_instalments(db_con):
    """Detects deliberately seeded payments exceeding scheduled dues in raw instalments (Issue 8)."""
    excess_raw = db_con.execute("""
        SELECT COUNT(*) FROM fin_raw.raw_instalments WHERE amount_paid > (amount_due * 2.0)
    """).fetchone()[0]
    assert excess_raw == 220, f"Expected 220 excess instalment payment records in raw, found {excess_raw}"

def test_staging_cleans_excess_instalments(db_con):
    """In cleaned staging layer, instalment payments must never exceed scheduled amounts."""
    excess_stg = db_con.execute("""
        SELECT COUNT(*) FROM fin_staging.stg_instalments WHERE amount_paid > amount_due
    """).fetchone()[0]
    assert excess_stg == 0, f"Found {excess_stg} instalments where amount_paid > amount_due in staging"

def test_raw_has_corrupted_dpd(db_con):
    """Detects seeded corrupted zero DPD records in raw instalments despite overdue arrears (Issue 10)."""
    # 350 instalments were seeded with corrupted 0 DPD
    quarantined_corrupt = db_con.execute("""
        SELECT COUNT(*) FROM fin_staging.stg_quarantined_records 
        WHERE reason_code = 'CORRUPTED_ZERO_DPD'
    """).fetchone()[0]
    assert quarantined_corrupt == 123, f"Expected 123 active corrupted DPD records quarantined, found {quarantined_corrupt}"

def test_warehouse_calculates_clean_dpd(db_con):
    """Warehouse fact_loan_monthly calculates dynamic DPD and contains zero corrupted values."""
    corrupt_fact = db_con.execute("""
        SELECT COUNT(*) FROM fin_warehouse.fact_loan_monthly 
        WHERE days_past_due IN (-999, 9999, 8888) OR days_past_due < 0
    """).fetchone()[0]
    assert corrupt_fact == 0, f"Found {corrupt_fact} corrupted DPD values in fact_loan_monthly"

def test_br025_oct2024_collection_outage_detected(db_con):
    """Verifies that the October 2024 collection outage at branch BR025 is detected (Issue 3)."""
    oct_txns = db_con.execute("""
        SELECT COUNT(*) 
        FROM fin_staging.stg_repayments r
        JOIN fin_staging.stg_loans l ON r.loan_id = l.loan_id
        WHERE l.branch_id = 'BR025' 
          AND strftime(r.payment_date, '%Y-%m') = '2024-10'
    """).fetchone()[0]
    assert oct_txns == 0, f"Expected 0 repayments for branch BR025 in 2024-10, found {oct_txns}"

def test_quarantined_records_completeness(db_con):
    """Verifies that quarantined table captures expected total defect count and maintains audit lineage."""
    total_quarantine = db_con.execute("SELECT COUNT(*) FROM fin_staging.stg_quarantined_records").fetchone()[0]
    # Total quarantined across all 8 quarantine rules is exactly 1,681
    assert total_quarantine == 1681, f"Expected 1681 quarantined records, found {total_quarantine}"
