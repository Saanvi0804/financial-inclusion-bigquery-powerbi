-- BigQuery Dimension: dim_product.sql
-- Loan product catalogue dimension with contractual interest rate and tenure bounds

CREATE OR REPLACE TABLE `fin_warehouse.dim_product` AS
WITH product_definitions AS (
    SELECT 'PRD_MFI' AS product_id, 'Joint Liability Group Microfinance Loan' AS product_name, 'Microfinance' AS category, NUMERIC '18.0' AS min_rate, NUMERIC '24.0' AS max_rate, 12 AS min_tenure, 24 AS max_tenure UNION ALL
    SELECT 'PRD_AGR', 'Kisan Agri Crop & Dairy Loan', 'Agriculture', NUMERIC '12.0', NUMERIC '16.0', 12, 18 UNION ALL
    SELECT 'PRD_SMB', 'MSME Small Enterprise Working Capital', 'MSME', NUMERIC '16.0', NUMERIC '22.0', 18, 36 UNION ALL
    SELECT 'PRD_PER', 'Emergency & Consumption Personal Loan', 'Personal', NUMERIC '20.0', NUMERIC '26.0', 12, 24 UNION ALL
    SELECT 'PRD_EDU', 'Vocational Skill & Higher Education Loan', 'Education', NUMERIC '11.0', NUMERIC '15.0', 18, 36
)
SELECT 
    ROW_NUMBER() OVER (ORDER BY product_id) AS product_key,
    product_id,
    product_name,
    category,
    min_rate,
    max_rate,
    min_tenure,
    max_tenure
FROM product_definitions
UNION ALL
-- Fallback entry for loans with invalid or unrecognised product codes (ISSUE-07)
SELECT -1, 'UNKNOWN_PRODUCT', 'Unrecognised Loan Product', 'Other', NUMERIC '0.0', NUMERIC '0.0', 0, 0;
