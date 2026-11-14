-- BigQuery Dimension: dim_branch.sql
-- Physical branch office dimension with surrogate keys and fallback for unassigned loans

CREATE OR REPLACE TABLE `fin_warehouse.dim_branch` AS
WITH branches AS (
    SELECT 
        branch_id,
        branch_name,
        state_id,
        location_type
    FROM `fin_staging.stg_branches`
)
SELECT 
    ROW_NUMBER() OVER (ORDER BY branch_id) AS branch_key,
    branch_id,
    branch_name,
    state_id,
    location_type
FROM branches
UNION ALL
-- Fallback entry for loans with missing or unassigned branch IDs (ISSUE-06)
SELECT -1, 'UNKNOWN_BRANCH', 'Unassigned Branch Office', 'UNKNOWN_STATE', 'Unknown';
