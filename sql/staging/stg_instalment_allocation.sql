-- BigQuery Staging: stg_instalment_allocation.sql
-- Implements chronological FIFO waterfall instalment allocation between repayments and scheduled instalments
-- Maps transactions sequentially to scheduled instalments per loan, preserving payment dates and partial amounts

CREATE OR REPLACE TABLE `fin_staging.stg_instalment_allocation` AS
WITH cum_instalments AS (
    SELECT 
        loan_id,
        instalment_id,
        instalment_number,
        due_date,
        amount_due,
        principal_component,
        interest_component,
        COALESCE(SUM(amount_due) OVER (
            PARTITION BY loan_id 
            ORDER BY instalment_number 
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ), NUMERIC '0.0') AS prev_cum_due,
        SUM(amount_due) OVER (
            PARTITION BY loan_id 
            ORDER BY instalment_number 
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cum_due
    FROM `fin_staging.stg_instalments`
),
cum_payments AS (
    SELECT 
        loan_id,
        transaction_id,
        payment_date,
        payment_amount,
        payment_channel,
        COALESCE(SUM(payment_amount) OVER (
            PARTITION BY loan_id 
            ORDER BY payment_date, transaction_id 
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ), NUMERIC '0.0') AS prev_cum_pay,
        SUM(payment_amount) OVER (
            PARTITION BY loan_id 
            ORDER BY payment_date, transaction_id 
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cum_pay
    FROM `fin_staging.stg_repayments`
)
SELECT 
    p.transaction_id,
    i.instalment_id,
    p.loan_id,
    i.instalment_number,
    i.due_date,
    p.payment_date,
    p.payment_channel,
    ROUND(LEAST(p.cum_pay, i.cum_due) - GREATEST(p.prev_cum_pay, i.prev_cum_due), 2) AS allocated_amount,
    ROUND((LEAST(p.cum_pay, i.cum_due) - GREATEST(p.prev_cum_pay, i.prev_cum_due)) * SAFE_DIVIDE(i.principal_component, i.amount_due), 2) AS allocated_principal,
    ROUND((LEAST(p.cum_pay, i.cum_due) - GREATEST(p.prev_cum_pay, i.prev_cum_due)) - 
          ROUND((LEAST(p.cum_pay, i.cum_due) - GREATEST(p.prev_cum_pay, i.prev_cum_due)) * SAFE_DIVIDE(i.principal_component, i.amount_due), 2), 2) AS allocated_interest
FROM cum_payments p
JOIN cum_instalments i 
    ON p.loan_id = i.loan_id
   AND GREATEST(p.prev_cum_pay, i.prev_cum_due) < LEAST(p.cum_pay, i.cum_due);
