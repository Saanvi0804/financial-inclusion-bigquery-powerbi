-- BigQuery Staging: stg_borrowers.sql
-- Cleanses, deduplicates, and validates borrower demographic attributes

CREATE OR REPLACE TABLE `fin_staging.stg_borrowers` AS
WITH deduplicated AS (
    SELECT 
        TRIM(borrower_id) AS borrower_id,
        TRIM(borrower_segment) AS borrower_segment,
        TRIM(income_band) AS income_band,
        TRIM(location_type) AS location_type,
        TRIM(occupation_category) AS occupation_category,
        ROW_NUMBER() OVER (PARTITION BY borrower_id ORDER BY borrower_id) AS rn
    FROM `fin_raw.raw_borrowers`
    WHERE borrower_id IS NOT NULL AND TRIM(borrower_id) != ''
)
SELECT 
    borrower_id,
    borrower_segment,
    income_band,
    location_type,
    occupation_category
FROM deduplicated
WHERE rn = 1;
