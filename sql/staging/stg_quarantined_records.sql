-- BigQuery Staging: stg_quarantined_records.sql
-- Initializes and captures quarantined anomaly records with reason codes and full payloads

CREATE TABLE IF NOT EXISTS `fin_staging.stg_quarantined_records` (
    quarantine_id STRING,
    batch_run_id STRING,
    quarantined_at TIMESTAMP,
    source_table STRING,
    record_identifier STRING,
    reason_code STRING,
    raw_payload STRING
);
