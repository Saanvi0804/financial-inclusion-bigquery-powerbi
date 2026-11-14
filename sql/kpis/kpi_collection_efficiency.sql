-- BigQuery KPI Model: kpi_collection_efficiency.sql
-- Calculates periodic collection efficiency across states, branches, and products
-- Disaggregates current-period scheduled billing, past arrears recovery, and total cash collections

CREATE OR REPLACE TABLE `fin_analytics.kpi_collection_efficiency` AS
WITH monthly_billing AS (
    SELECT 
        FORMAT_DATE('%Y-%m', i.due_date) AS year_month,
        s.state_name,
        b.branch_name,
        p.product_name,
        ROUND(SUM(i.amount_due), 2) AS scheduled_amount_due
    FROM `fin_staging.stg_instalments` i
    JOIN `fin_staging.stg_loans` l ON i.loan_id = l.loan_id
    LEFT JOIN `fin_warehouse.dim_branch` b ON l.branch_id = b.branch_id
    LEFT JOIN `fin_warehouse.dim_state` s ON l.state_id = s.state_id
    LEFT JOIN `fin_warehouse.dim_product` p ON l.product_id = p.product_id
    WHERE i.due_date >= DATE '2023-01-01' AND i.due_date <= DATE '2024-12-31'
    GROUP BY 1, 2, 3, 4
),
monthly_allocations AS (
    SELECT 
        FORMAT_DATE('%Y-%m', a.payment_date) AS year_month,
        s.state_name,
        b.branch_name,
        p.product_name,
        -- Current-month billing collected (instalment due in current month and paid in current month)
        ROUND(SUM(CASE WHEN FORMAT_DATE('%Y-%m', a.due_date) = FORMAT_DATE('%Y-%m', a.payment_date) THEN a.allocated_amount ELSE NUMERIC '0.0' END), 2) AS current_period_collected,
        -- Arrears collected (instalment due prior to payment month)
        ROUND(SUM(CASE WHEN FORMAT_DATE('%Y-%m', a.due_date) < FORMAT_DATE('%Y-%m', a.payment_date) THEN a.allocated_amount ELSE NUMERIC '0.0' END), 2) AS arrears_collected,
        -- Advance collections (instalment due after payment month)
        ROUND(SUM(CASE WHEN FORMAT_DATE('%Y-%m', a.due_date) > FORMAT_DATE('%Y-%m', a.payment_date) THEN a.allocated_amount ELSE NUMERIC '0.0' END), 2) AS advance_collected,
        -- Total cash collected via allocations
        ROUND(SUM(a.allocated_amount), 2) AS total_cash_collected
    FROM `fin_staging.stg_instalment_allocation` a
    JOIN `fin_staging.stg_loans` l ON a.loan_id = l.loan_id
    LEFT JOIN `fin_warehouse.dim_branch` b ON l.branch_id = b.branch_id
    LEFT JOIN `fin_warehouse.dim_state` s ON l.state_id = s.state_id
    LEFT JOIN `fin_warehouse.dim_product` p ON l.product_id = p.product_id
    GROUP BY 1, 2, 3, 4
)
SELECT 
    COALESCE(mb.year_month, ma.year_month) AS year_month,
    COALESCE(mb.state_name, ma.state_name) AS state_name,
    COALESCE(mb.branch_name, ma.branch_name) AS branch_name,
    COALESCE(mb.product_name, ma.product_name) AS product_name,
    COALESCE(mb.scheduled_amount_due, NUMERIC '0.00') AS scheduled_amount_due,
    COALESCE(ma.current_period_collected, NUMERIC '0.00') AS current_period_collected,
    COALESCE(ma.arrears_collected, NUMERIC '0.00') AS arrears_collected,
    COALESCE(ma.advance_collected, NUMERIC '0.00') AS advance_collected,
    COALESCE(ma.total_cash_collected, NUMERIC '0.00') AS total_amount_collected,
    -- Current-period efficiency: (Current-month billing collected / Current-month scheduled billing due) * 100
    ROUND(
        SAFE_DIVIDE(COALESCE(ma.current_period_collected, NUMERIC '0.00') * NUMERIC '100.0', 
                    COALESCE(mb.scheduled_amount_due, NUMERIC '0.00')), 
        2
    ) AS current_period_efficiency_pct,
    -- Total collection ratio: (Total cash collected / Current-month scheduled billing due) * 100
    ROUND(
        SAFE_DIVIDE(COALESCE(ma.total_cash_collected, NUMERIC '0.00') * NUMERIC '100.0', 
                    COALESCE(mb.scheduled_amount_due, NUMERIC '0.00')), 
        2
    ) AS total_collection_ratio_pct,
    -- Standard collection efficiency alias
    ROUND(
        SAFE_DIVIDE(COALESCE(ma.total_cash_collected, NUMERIC '0.00') * NUMERIC '100.0', 
                    COALESCE(mb.scheduled_amount_due, NUMERIC '0.00')), 
        2
    ) AS collection_efficiency_pct
FROM monthly_billing mb
FULL OUTER JOIN monthly_allocations ma
    ON mb.year_month = ma.year_month
   AND mb.state_name = ma.state_name
   AND mb.branch_name = ma.branch_name
   AND mb.product_name = ma.product_name;
