"""
End-to-End BigQuery Transformation Pipeline Orchestrator.

Orchestrates:
1. BigQuery Environment Initialization (Cloud BigQuery or Local Engine)
2. Staging Layer Execution (Cleaning, Deduplication, Quarantine Logging)
3. Dimensional Layer Execution (Surrogate Keys, Role-playing Date, Fallbacks)
4. Fact Layer Execution (Transactions, Waterfall Allocations, Monthly Snapshots)
5. Analytical KPI Layer Execution (Portfolio Health, Collection Efficiency, Vintage, Digital)
6. Enterprise Multi-Layer Financial Reconciliation & Audit Logging
"""

import os
import sys
import logging
import re
import time
import duckdb

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("PipelineOrchestrator")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQL_DIR = os.path.join(BASE_DIR, "sql")
LOCAL_DB_PATH = os.path.join(BASE_DIR, "data", "warehouse", "financial_inclusion_bigquery.duckdb")

def init_local_engine(con):
    """Initializes BigQuery macro compatibility layer in DuckDB."""
    con.execute("""
        CREATE MACRO IF NOT EXISTS FORMAT_TIMESTAMP(fmt, ts) AS strftime(ts, fmt);
        CREATE MACRO IF NOT EXISTS FORMAT_DATE(fmt, dt) AS strftime(dt, fmt);
        CREATE MACRO IF NOT EXISTS SAFE_DIVIDE(a, b) AS (a / NULLIF(b, 0));
        CREATE MACRO IF NOT EXISTS GENERATE_UUID() AS uuid();
    """)

def bq_to_duckdb(sql: str) -> str:
    """Adapts BigQuery Standard SQL statements for local execution while preserving exact semantics."""
    s = re.sub(r'OPTIONS\s*\([^)]*\)', '', sql, flags=re.IGNORECASE)
    # Remove table-level PARTITION BY (which comes after table definition, not inside OVER)
    s = re.sub(r'\)\s*PARTITION BY\s+[^\n;]+', ')', s, flags=re.IGNORECASE)
    s = re.sub(r'CLUSTER BY\s+[^\n;]+', '', s, flags=re.IGNORECASE)
    s = s.replace('`', '')
    # Convert BigQuery NUMERIC 'x.xx' literal to x.xx
    s = re.sub(r"NUMERIC\s*'([^']+)'", r"\1", s, flags=re.IGNORECASE)
    s = re.sub(r'GENERATE_DATE_ARRAY\s*\(', 'generate_series(', s, flags=re.IGNORECASE)
    s = re.sub(r'LAST_DAY\s*\(\s*([^,\)]+)\s*,\s*MONTH\s*\)', r'last_day(\1)', s, flags=re.IGNORECASE)
    # CURRENT_TIMESTAMP() in BigQuery -> current_timestamp in DuckDB
    s = re.sub(r'CURRENT_TIMESTAMP\(\)', 'current_timestamp', s, flags=re.IGNORECASE)
    # DATE_DIFF(d1, d2, DAY) in BigQuery -> date_diff('day', d2, d1) in DuckDB
    s = re.sub(r'DATE_DIFF\s*\(\s*([^,]+)\s*,\s*([^,]+)\s*,\s*DAY\s*\)', r"date_diff('day', \2, \1)", s, flags=re.IGNORECASE)
    return s

def execute_sql_file(con, file_path: str):
    rel_path = os.path.relpath(file_path, BASE_DIR)
    logger.info("Executing SQL model: %s", rel_path)
    with open(file_path, "r", encoding="utf-8") as f:
        raw_sql = f.read()

    # Strip single line comments so semicolons in comments do not split statements
    clean_lines = []
    for line in raw_sql.splitlines():
        idx = line.find('--')
        if idx != -1:
            line = line[:idx]
        clean_lines.append(line)
    clean_sql = "\n".join(clean_lines)

    # Split on semicolons that terminate statements
    statements = [stmt.strip() for stmt in clean_sql.split(";") if stmt.strip()]
    for stmt in statements:
        adapted_sql = bq_to_duckdb(stmt)
        if adapted_sql.strip():
            con.execute(adapted_sql)

def run_transformations(db_path: str = LOCAL_DB_PATH):
    logger.info("Starting BigQuery Transformation Pipeline on database: %s", db_path)
    con = duckdb.connect(db_path)
    init_local_engine(con)

    # 1. Reset Staging Quarantine Table for Idempotent Execution
    con.execute("CREATE SCHEMA IF NOT EXISTS fin_staging;")
    con.execute("CREATE TABLE IF NOT EXISTS fin_staging.stg_quarantined_records (quarantine_id VARCHAR, batch_run_id VARCHAR, quarantined_at TIMESTAMP, source_table VARCHAR, record_identifier VARCHAR, reason_code VARCHAR, raw_payload VARCHAR);")
    con.execute("DELETE FROM fin_staging.stg_quarantined_records;")

    # 2. Staging Layer Execution
    staging_order = [
        "stg_quarantined_records.sql",
        "stg_branches.sql",
        "stg_borrowers.sql",
        "stg_loans.sql",
        "stg_repayments.sql",
        "stg_instalments.sql",
        "stg_instalment_allocation.sql",
    ]
    logger.info("--- Executing Staging Layer Models (fin_staging.*) ---")
    for file_name in staging_order:
        execute_sql_file(con, os.path.join(SQL_DIR, "staging", file_name))
        tbl = file_name.replace(".sql", "")
        cnt = con.execute(f"SELECT COUNT(*) FROM fin_staging.{tbl}").fetchone()[0]
        logger.info("  -> fin_staging.%s populated (%d records)", tbl, cnt)

    # 3. Dimension Layer Execution
    dimension_order = [
        "dim_date.sql",
        "dim_state.sql",
        "dim_branch.sql",
        "dim_product.sql",
        "dim_borrower_segment.sql",
        "dim_loan.sql",
    ]
    logger.info("--- Executing Dimensional Layer Models (fin_warehouse.dim_*) ---")
    for file_name in dimension_order:
        execute_sql_file(con, os.path.join(SQL_DIR, "dimensions", file_name))
        tbl = file_name.replace(".sql", "")
        cnt = con.execute(f"SELECT COUNT(*) FROM fin_warehouse.{tbl}").fetchone()[0]
        logger.info("  -> fin_warehouse.%s populated (%d records)", tbl, cnt)

    # 4. Fact Layer Execution
    fact_order = [
        "fact_payment.sql",
        "fact_instalment_allocation.sql",
        "fact_loan_monthly.sql",
    ]
    logger.info("--- Executing Fact Layer Models (fin_warehouse.fact_*) ---")
    for file_name in fact_order:
        execute_sql_file(con, os.path.join(SQL_DIR, "facts", file_name))
        tbl = file_name.replace(".sql", "")
        cnt = con.execute(f"SELECT COUNT(*) FROM fin_warehouse.{tbl}").fetchone()[0]
        logger.info("  -> fin_warehouse.%s populated (%d records)", tbl, cnt)

    # 5. Analytical KPI Models Execution
    kpi_order = [
        "kpi_portfolio_health.sql",
        "kpi_collection_efficiency.sql",
        "kpi_vintage_curves.sql",
        "kpi_digital_collections.sql",
    ]
    logger.info("--- Executing Analytical KPI Models (fin_analytics.kpi_*) ---")
    for file_name in kpi_order:
        execute_sql_file(con, os.path.join(SQL_DIR, "kpis", file_name))
        tbl = file_name.replace(".sql", "")
        cnt = con.execute(f"SELECT COUNT(*) FROM fin_analytics.{tbl}").fetchone()[0]
        logger.info("  -> fin_analytics.%s populated (%d records)", tbl, cnt)

    # 6. Multi-Layer Financial Reconciliation
    logger.info("--- Executing Comprehensive Financial & Count Reconciliations ---")

    # Loan Reconciliation
    raw_loans_cnt = con.execute("SELECT COUNT(*) FROM fin_raw.raw_loans").fetchone()[0]
    stg_loans_cnt = con.execute("SELECT COUNT(*) FROM fin_staging.stg_loans").fetchone()[0]
    dim_loans_cnt = con.execute("SELECT COUNT(*) - 1 FROM fin_warehouse.dim_loan").fetchone()[0] # Exclude fallback
    loan_quarantine_cnt = con.execute("SELECT COUNT(*) FROM fin_staging.stg_quarantined_records WHERE source_table = 'raw_loans'").fetchone()[0]

    logger.info("Loan Ledger Reconciliation:")
    logger.info("  Raw Loans Ingested: %d", raw_loans_cnt)
    logger.info("  Staging Clean Loans: %d", stg_loans_cnt)
    logger.info("  Dimension Loans (excluding fallback): %d", dim_loans_cnt)
    logger.info("  Loan Quarantine Audit Entries: %d", loan_quarantine_cnt)
    assert raw_loans_cnt == 52200 and stg_loans_cnt == 52000 and dim_loans_cnt == 52000, "Loan reconciliation count invariant failed!"

    # Payment Reconciliation with Granular Exclusion Accounting
    raw_repay_stats = con.execute("""
        SELECT 
            COUNT(*),
            ROUND(SUM(CASE WHEN UPPER(TRIM(amount_unit)) = 'PAISE' THEN ROUND(payment_amount / 100.0, 2) ELSE ROUND(payment_amount, 2) END), 2)
        FROM fin_raw.raw_repayments
    """).fetchone()
    raw_repay_cnt, raw_repay_gross_amt = raw_repay_stats[0], raw_repay_stats[1]

    neg_excl = con.execute("SELECT COUNT(*), ROUND(SUM(payment_amount), 2) FROM fin_raw.raw_repayments WHERE payment_amount < 0").fetchone()
    dup_excl = con.execute("""
        WITH ranked AS (
            SELECT transaction_id, payment_amount, amount_unit,
                   ROW_NUMBER() OVER (PARTITION BY transaction_id ORDER BY payment_date) as rn
            FROM fin_raw.raw_repayments WHERE payment_amount >= 0
        )
        SELECT COUNT(*), ROUND(SUM(CASE WHEN UPPER(TRIM(amount_unit)) = 'PAISE' THEN ROUND(payment_amount / 100.0, 2) ELSE ROUND(payment_amount, 2) END), 2)
        FROM ranked WHERE rn > 1
    """).fetchone()

    pre_excl = con.execute("""
        WITH dedup AS (
            SELECT r.transaction_id, r.loan_id, r.payment_date, r.payment_amount, r.amount_unit,
                   ROW_NUMBER() OVER (PARTITION BY r.transaction_id ORDER BY r.payment_date) as rn
            FROM fin_raw.raw_repayments r WHERE r.payment_amount >= 0
        )
        SELECT COUNT(*), ROUND(SUM(CASE WHEN UPPER(TRIM(r.amount_unit)) = 'PAISE' THEN ROUND(r.payment_amount / 100.0, 2) ELSE ROUND(r.payment_amount, 2) END), 2)
        FROM dedup r
        JOIN fin_staging.stg_loans l ON r.loan_id = l.loan_id
        WHERE r.rn = 1 AND CAST(r.payment_date AS DATE) < l.disbursement_date
    """).fetchone()

    clean_raw_stats = con.execute("""
        WITH dedup AS (
            SELECT r.transaction_id, r.loan_id, r.payment_date, r.payment_amount, r.amount_unit,
                   ROW_NUMBER() OVER (PARTITION BY r.transaction_id ORDER BY r.payment_date) as rn
            FROM fin_raw.raw_repayments r WHERE r.payment_amount >= 0
        )
        SELECT COUNT(*), ROUND(SUM(CASE WHEN UPPER(TRIM(r.amount_unit)) = 'PAISE' THEN ROUND(r.payment_amount / 100.0, 2) ELSE ROUND(r.payment_amount, 2) END), 2)
        FROM dedup r
        JOIN fin_staging.stg_loans l ON r.loan_id = l.loan_id
        WHERE r.rn = 1 AND CAST(r.payment_date AS DATE) >= l.disbursement_date
    """).fetchone()
    clean_raw_cnt, clean_raw_amt = clean_raw_stats[0], clean_raw_stats[1]

    stg_repay_cnt = con.execute("SELECT COUNT(*) FROM fin_staging.stg_repayments").fetchone()[0]
    stg_repay_amt = con.execute("SELECT ROUND(SUM(payment_amount), 2) FROM fin_staging.stg_repayments").fetchone()[0]
    fact_pay_cnt = con.execute("SELECT COUNT(*) FROM fin_warehouse.fact_payment").fetchone()[0]
    fact_pay_amt = con.execute("SELECT ROUND(SUM(payment_amount), 2) FROM fin_warehouse.fact_payment").fetchone()[0]

    logger.info("Payment Ledger Reconciliation:")
    logger.info("  Unfiltered Raw Repayments: %d records | Gross: ₹%.2f", raw_repay_cnt, raw_repay_gross_amt)
    logger.info("  Excluded Anomalies:")
    logger.info("    - Negative Amounts (ISSUE-05): %d records | Amount: ₹%.2f", neg_excl[0], neg_excl[1])
    logger.info("    - Duplicate Transactions (ISSUE-02): %d records | Amount: ₹%.2f", dup_excl[0], dup_excl[1])
    logger.info("    - Pre-Disbursement Payments (ISSUE-09): %d records | Amount: ₹%.2f", pre_excl[0], pre_excl[1])
    logger.info("  Clean Normalised Raw Repayments: %d records | Total: ₹%.2f", clean_raw_cnt, clean_raw_amt)
    logger.info("  Staging Layer Repayments: %d records | Total: ₹%.2f", stg_repay_cnt, stg_repay_amt)
    logger.info("  Warehouse Fact Payment: %d records | Total: ₹%.2f", fact_pay_cnt, fact_pay_amt)

    cnt_diff = clean_raw_cnt - fact_pay_cnt
    amt_diff = round(abs(clean_raw_amt - fact_pay_amt), 2)
    logger.info("  Reconciliation Variance: Count Diff = %d | Amount Diff = ₹%.2f", cnt_diff, amt_diff)
    assert cnt_diff == 0 and amt_diff == 0.00, f"Payment reconciliation failed! Count Diff={cnt_diff}, Amt Diff={amt_diff}"

    con.close()
    logger.info("BigQuery Data Warehouse transformation pipeline executed and reconciled successfully!")

if __name__ == "__main__":
    t0 = time.time()
    run_transformations()
    logger.info("Total pipeline run duration: %.2f seconds", time.time() - t0)
