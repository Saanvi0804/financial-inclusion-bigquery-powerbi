-- BigQuery Staging: stg_branches.sql
-- Cleanses, deduplicates, and standardizes branch attributes

CREATE OR REPLACE TABLE `fin_staging.stg_branches` AS
SELECT DISTINCT
    TRIM(branch_id) AS branch_id,
    TRIM(branch_name) AS branch_name,
    TRIM(state_id) AS state_id,
    TRIM(location_type) AS location_type
FROM `fin_raw.raw_branches`
WHERE branch_id IS NOT NULL AND TRIM(branch_id) != '';
