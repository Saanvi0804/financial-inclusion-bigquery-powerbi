-- BigQuery Dimension: dim_borrower_segment.sql
-- Borrower socio-economic, income, and occupational demographic archetype dimension

CREATE OR REPLACE TABLE `fin_warehouse.dim_borrower_segment` AS
WITH segments AS (
    SELECT DISTINCT
        borrower_segment,
        income_band,
        location_type,
        occupation_category
    FROM `fin_staging.stg_borrowers`
)
SELECT 
    ROW_NUMBER() OVER (ORDER BY borrower_segment, income_band, location_type, occupation_category) AS borrower_segment_key,
    borrower_segment,
    income_band,
    location_type,
    occupation_category
FROM segments
UNION ALL
-- Fallback entry for unmapped borrower demographics
SELECT -1, 'Unknown Segment', 'Unknown Income', 'Unknown', 'Unknown';
