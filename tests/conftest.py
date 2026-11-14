"""
Pytest configuration and database fixtures for BigQuery analytical warehouse testing.
"""

import os
import pytest
import duckdb

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "warehouse", "financial_inclusion_bigquery.duckdb")

@pytest.fixture(scope="session")
def db_con():
    """Session-scoped read-only connection to the analytical warehouse database."""
    if not os.path.exists(DB_PATH):
        pytest.fail(f"Warehouse database file not found at: {DB_PATH}")
    con = duckdb.connect(DB_PATH, read_only=True)
    yield con
    con.close()
