-- BigQuery KPI Model: kpi_digital_collections.sql
-- Computes cash vs digital transition, channel splits, ticket sizes, and MoM / YoY growth rates

CREATE OR REPLACE TABLE `fin_analytics.kpi_digital_collections` AS
WITH channel_txns AS (
    SELECT 
        d.year_month,
        CAST(FORMAT_DATE('%Y%m01', d.full_date) AS INT64) AS month_date_key,
        COALESCE(s.state_id, 'ALL') AS state_id,
        COALESCE(s.state_name, 'All States') AS state_name,
        f.payment_channel,
        COUNT(*) AS txn_count,
        SUM(f.payment_amount) AS total_amount
    FROM `fin_warehouse.fact_payment` f
    JOIN `fin_warehouse.dim_date` d ON f.payment_date_key = d.date_key
    JOIN `fin_warehouse.dim_state` s ON f.state_key = s.state_key
    GROUP BY d.year_month, month_date_key, s.state_id, s.state_name, f.payment_channel
),
state_monthly_totals AS (
    SELECT 
        year_month,
        month_date_key,
        state_id,
        state_name,
        -- Total Collections
        SUM(total_amount) AS total_collection_value,
        SUM(txn_count) AS total_transaction_count,
        -- Digital Collections (UPI + Bank Transfer)
        SUM(CASE WHEN payment_channel IN ('UPI', 'Bank Transfer') THEN total_amount ELSE NUMERIC '0.0' END) AS digital_collection_value,
        SUM(CASE WHEN payment_channel IN ('UPI', 'Bank Transfer') THEN txn_count ELSE 0 END) AS digital_transaction_count,
        -- Non-Digital Collections (Cash)
        SUM(CASE WHEN payment_channel = 'Cash' THEN total_amount ELSE NUMERIC '0.0' END) AS cash_collection_value,
        SUM(CASE WHEN payment_channel = 'Cash' THEN txn_count ELSE 0 END) AS cash_transaction_count,
        -- Specific Channel Breakdown
        SUM(CASE WHEN payment_channel = 'UPI' THEN total_amount ELSE NUMERIC '0.0' END) AS upi_value,
        SUM(CASE WHEN payment_channel = 'UPI' THEN txn_count ELSE 0 END) AS upi_count,
        SUM(CASE WHEN payment_channel = 'Bank Transfer' THEN total_amount ELSE NUMERIC '0.0' END) AS bank_transfer_value,
        SUM(CASE WHEN payment_channel = 'Bank Transfer' THEN txn_count ELSE 0 END) AS bank_transfer_count,
        -- Average Ticket Sizes
        COALESCE(ROUND(SAFE_DIVIDE(SUM(CASE WHEN payment_channel = 'UPI' THEN total_amount ELSE NUMERIC '0.0' END), 
                          SUM(CASE WHEN payment_channel = 'UPI' THEN txn_count ELSE 0 END)), 2), NUMERIC '0.00') AS avg_ticket_upi,
        COALESCE(ROUND(SAFE_DIVIDE(SUM(CASE WHEN payment_channel = 'Bank Transfer' THEN total_amount ELSE NUMERIC '0.0' END), 
                          SUM(CASE WHEN payment_channel = 'Bank Transfer' THEN txn_count ELSE 0 END)), 2), NUMERIC '0.00') AS avg_ticket_bank_transfer,
        COALESCE(ROUND(SAFE_DIVIDE(SUM(CASE WHEN payment_channel = 'Cash' THEN total_amount ELSE NUMERIC '0.0' END), 
                          SUM(CASE WHEN payment_channel = 'Cash' THEN txn_count ELSE 0 END)), 2), NUMERIC '0.00') AS avg_ticket_cash,
        COALESCE(ROUND(SAFE_DIVIDE(SUM(total_amount), SUM(txn_count)), 2), NUMERIC '0.00') AS avg_ticket_overall
    FROM channel_txns
    GROUP BY year_month, month_date_key, state_id, state_name
),
shares_computed AS (
    SELECT 
        *,
        COALESCE(ROUND(SAFE_DIVIDE(digital_collection_value * NUMERIC '100.0', total_collection_value), 2), NUMERIC '0.00') AS digital_value_share_pct,
        COALESCE(ROUND(SAFE_DIVIDE(digital_transaction_count * NUMERIC '100.0', total_transaction_count), 2), NUMERIC '0.00') AS digital_count_share_pct
    FROM state_monthly_totals
)
SELECT 
    sc.*,
    -- Month-on-Month (MoM) Changes
    COALESCE(LAG(digital_value_share_pct, 1) OVER (PARTITION BY state_id ORDER BY year_month), NUMERIC '0.00') AS prev_month_digital_value_share,
    COALESCE(ROUND(
        digital_value_share_pct - LAG(digital_value_share_pct, 1) OVER (PARTITION BY state_id ORDER BY year_month), 
        2
    ), NUMERIC '0.00') AS mom_digital_value_share_pts,
    COALESCE(ROUND(
        SAFE_DIVIDE((digital_value_share_pct - LAG(digital_value_share_pct, 1) OVER (PARTITION BY state_id ORDER BY year_month)) * NUMERIC '100.0',
                    LAG(digital_value_share_pct, 1) OVER (PARTITION BY state_id ORDER BY year_month)),
        2
    ), NUMERIC '0.00') AS mom_digital_value_growth_pct,
    -- Year-on-Year (YoY) Changes
    COALESCE(LAG(digital_value_share_pct, 12) OVER (PARTITION BY state_id ORDER BY year_month), NUMERIC '0.00') AS prev_year_digital_value_share,
    COALESCE(ROUND(
        digital_value_share_pct - LAG(digital_value_share_pct, 12) OVER (PARTITION BY state_id ORDER BY year_month), 
        2
    ), NUMERIC '0.00') AS yoy_digital_value_share_pts,
    COALESCE(ROUND(
        SAFE_DIVIDE((digital_value_share_pct - LAG(digital_value_share_pct, 12) OVER (PARTITION BY state_id ORDER BY year_month)) * NUMERIC '100.0',
                    LAG(digital_value_share_pct, 12) OVER (PARTITION BY state_id ORDER BY year_month)),
        2
    ), NUMERIC '0.00') AS yoy_digital_value_growth_pct
FROM shares_computed sc
ORDER BY year_month, state_id;
