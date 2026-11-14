-- BigQuery Dimension: dim_state.sql
-- Geographic dimension modeling Indian states and economic regions

CREATE OR REPLACE TABLE `fin_warehouse.dim_state` AS
WITH state_raw AS (
    SELECT 'ST_MH' AS state_id, 'Maharashtra' AS state_name, 'West' AS region UNION ALL
    SELECT 'ST_TN', 'Tamil Nadu', 'South' UNION ALL
    SELECT 'ST_UP', 'Uttar Pradesh', 'North' UNION ALL
    SELECT 'ST_KA', 'Karnataka', 'South' UNION ALL
    SELECT 'ST_BR', 'Bihar', 'East' UNION ALL
    SELECT 'ST_OD', 'Odisha', 'East' UNION ALL
    SELECT 'ST_RJ', 'Rajasthan', 'North' UNION ALL
    SELECT 'ST_MP', 'Madhya Pradesh', 'Central' UNION ALL
    SELECT 'ST_WB', 'West Bengal', 'East' UNION ALL
    SELECT 'ST_GJ', 'Gujarat', 'West'
)
SELECT 
    ROW_NUMBER() OVER (ORDER BY state_id) AS state_key,
    state_id,
    state_name,
    region
FROM state_raw
UNION ALL
-- Fallback entry for unmapped or missing states
SELECT -1, 'UNKNOWN_STATE', 'Unknown State', 'Unknown';
