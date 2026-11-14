"""
Export Power BI Curated Data Extracts.
Exports dimension, fact, and KPI tables from the warehouse into optimised CSV/Parquet files
ready for immediate import into Power BI Desktop or DirectQuery connectivity.
"""

import os
import duckdb
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ExportPowerBI")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "warehouse", "financial_inclusion_bigquery.duckdb")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "powerbi_extracts")

def export_tables():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    con = duckdb.connect(DB_PATH, read_only=True)
    
    tables_to_export = [
        # Dimensions
        ("fin_warehouse.dim_date", "dim_date.csv"),
        ("fin_warehouse.dim_state", "dim_state.csv"),
        ("fin_warehouse.dim_branch", "dim_branch.csv"),
        ("fin_warehouse.dim_product", "dim_product.csv"),
        ("fin_warehouse.dim_borrower_segment", "dim_borrower_segment.csv"),
        ("fin_warehouse.dim_loan", "dim_loan.csv"),
        # Facts (Summary & Monthly)
        ("fin_warehouse.fact_loan_monthly", "fact_loan_monthly.csv"),
        # Pre-calculated KPI Aggregations (for instant Power BI responsiveness)
        ("fin_analytics.kpi_portfolio_health", "kpi_portfolio_health.csv"),
        ("fin_analytics.kpi_collection_efficiency", "kpi_collection_efficiency.csv"),
        ("fin_analytics.kpi_vintage_curves", "kpi_vintage_curves.csv"),
        ("fin_analytics.kpi_digital_collections", "kpi_digital_collections.csv"),
        # Data Quality & Quarantine Monitoring
        ("fin_staging.stg_quarantined_records", "stg_quarantined_records.csv")
    ]
    
    logger.info("Exporting warehouse tables for Power BI...")
    for table_name, file_name in tables_to_export:
        dest_path = os.path.join(OUTPUT_DIR, file_name).replace("\\", "/")
        query = f"COPY (SELECT * FROM {table_name}) TO '{dest_path}' (HEADER, DELIMITER ',')"
        con.execute(query)
        cnt = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        logger.info(f"  Exported {table_name} ({cnt:,} rows) -> {file_name}")
        
    con.close()
    logger.info(f"All Power BI extracts successfully generated in: {OUTPUT_DIR}")

if __name__ == "__main__":
    export_tables()
