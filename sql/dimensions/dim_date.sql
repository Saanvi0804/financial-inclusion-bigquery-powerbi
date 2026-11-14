-- BigQuery Dimension: dim_date.sql
-- Unified role-playing calendar dimension covering 2022 through 2026 with Indian Financial Year conventions

CREATE OR REPLACE TABLE `fin_warehouse.dim_date` AS
WITH date_series AS (
    SELECT d AS full_date
    FROM UNNEST(GENERATE_DATE_ARRAY(DATE '2022-01-01', DATE '2026-12-31', INTERVAL 1 DAY)) AS d
)
SELECT 
    CAST(FORMAT_DATE('%Y%m%d', full_date) AS INT64) AS date_key,
    full_date,
    EXTRACT(DAY FROM full_date) AS day_of_month,
    EXTRACT(MONTH FROM full_date) AS month_number,
    FORMAT_DATE('%B', full_date) AS month_name,
    FORMAT_DATE('%Y-%m', full_date) AS year_month,
    EXTRACT(QUARTER FROM full_date) AS quarter_number,
    CONCAT('Q', CAST(EXTRACT(QUARTER FROM full_date) AS STRING)) AS quarter_name,
    EXTRACT(YEAR FROM full_date) AS calendar_year,
    -- Indian Financial Year (April 1 to March 31)
    CASE 
        WHEN EXTRACT(MONTH FROM full_date) >= 4 
        THEN CONCAT('FY ', CAST(EXTRACT(YEAR FROM full_date) AS STRING), '-', SUBSTR(CAST(EXTRACT(YEAR FROM full_date) + 1 AS STRING), 3, 2))
        ELSE CONCAT('FY ', CAST(EXTRACT(YEAR FROM full_date) - 1 AS STRING), '-', SUBSTR(CAST(EXTRACT(YEAR FROM full_date) AS STRING), 3, 2))
    END AS financial_year,
    -- Indian Financial Quarter
    CASE 
        WHEN EXTRACT(MONTH FROM full_date) IN (4, 5, 6) THEN 'Q1 (Apr-Jun)'
        WHEN EXTRACT(MONTH FROM full_date) IN (7, 8, 9) THEN 'Q2 (Jul-Sep)'
        WHEN EXTRACT(MONTH FROM full_date) IN (10, 11, 12) THEN 'Q3 (Oct-Dec)'
        ELSE 'Q4 (Jan-Mar)'
    END AS financial_quarter,
    -- Weekend flag (Sunday=1, Saturday=7 in BigQuery DAYOFWEEK)
    EXTRACT(DAYOFWEEK FROM full_date) IN (1, 7) AS is_weekend,
    -- Month-end close flag
    full_date = LAST_DAY(full_date, MONTH) AS is_month_end
FROM date_series;
