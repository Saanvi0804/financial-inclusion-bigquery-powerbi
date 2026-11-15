import duckdb
import pandas as pd

con = duckdb.connect("data/warehouse/financial_inclusion_bigquery.duckdb", read_only=True)

print("="*80)
print("1. INVESTIGATE KPI_DIGITAL_COLLECTIONS: MONTHLY VS CUMULATIVE")
print("="*80)

# Check columns and values
df_dc = con.execute("""
    SELECT year_month, 
           SUM(upi_value) as upi, 
           SUM(bank_transfer_value) as bank, 
           SUM(cash_collection_value) as cash, 
           SUM(total_collection_value) as tot
    FROM fin_analytics.kpi_digital_collections 
    GROUP BY year_month 
    ORDER BY year_month 
    LIMIT 6
""").fetchdf()
print("kpi_digital_collections by month:")
print(df_dc.to_string())

# Check total sum across all months vs sum of fact_payment
tot_dc_val = con.execute("SELECT SUM(total_collection_value) FROM fin_analytics.kpi_digital_collections").fetchone()[0]
tot_pay_val = con.execute("SELECT SUM(payment_amount) FROM fin_warehouse.fact_payment").fetchone()[0]
print(f"Total Digital KPI Collections Value: INR {tot_dc_val:,.2f}")
print(f"Total Fact Payment Amount:          INR {tot_pay_val:,.2f}")
print(f"Difference:                         INR {abs(tot_dc_val - tot_pay_val):,.2f}")

print("\n" + "="*80)
print("2. INVESTIGATE KPI_VINTAGE_CURVES: GRAIN, MOB AND CUMULATIVE VALUES")
print("="*80)

# Check columns of kpi_vintage_curves
cols = con.execute("DESCRIBE fin_analytics.kpi_vintage_curves").fetchall()
print("kpi_vintage_curves columns:", [c[0] for c in cols])

# Check 2023-01 cohort progression
df_vc_202301 = con.execute("""
    SELECT cohort_month, month_on_book, total_cohort_loans, cohort_disbursed_principal,
           cumulative_scheduled_due, cumulative_amount_paid, cumulative_repayment_pct
    FROM fin_analytics.kpi_vintage_curves
    WHERE cohort_month = '2023-01'
    ORDER BY month_on_book
""").fetchdf()
print("kpi_vintage_curves for cohort 2023-01 across MOB 1 to 24:")
print(df_vc_202301.to_string())

# Sum of all rows in kpi_vintage_curves
df_vc_sums = con.execute("""
    SELECT 
        COUNT(*) as total_rows,
        COUNT(DISTINCT cohort_month) as num_cohorts,
        SUM(cohort_disbursed_principal) as naive_sum_disbursed,
        SUM(cumulative_scheduled_due) as naive_sum_sched_due,
        SUM(cumulative_amount_paid) as naive_sum_paid
    FROM fin_analytics.kpi_vintage_curves
""").fetchdf()
print("\nNaive SUM across ALL rows of kpi_vintage_curves:")
print(df_vc_sums.to_string())

# Correct distinct cohort disbursed principal and latest MOB values
df_vc_latest_mob = con.execute("""
    WITH latest_mob_per_cohort AS (
        SELECT cohort_month, 
               MAX(month_on_book) as max_mob
        FROM fin_analytics.kpi_vintage_curves
        GROUP BY cohort_month
    ),
    cohort_latest_values AS (
        SELECT v.cohort_month,
               v.month_on_book,
               v.total_cohort_loans,
               v.cohort_disbursed_principal,
               v.cumulative_scheduled_due,
               v.cumulative_amount_paid,
               v.cumulative_repayment_pct
        FROM fin_analytics.kpi_vintage_curves v
        JOIN latest_mob_per_cohort l
          ON v.cohort_month = l.cohort_month AND v.month_on_book = l.max_mob
    )
    SELECT 
        COUNT(*) as cohorts_count,
        SUM(cohort_disbursed_principal) as total_cohort_disbursed,
        SUM(cumulative_scheduled_due) as latest_cumulative_scheduled_due,
        SUM(cumulative_amount_paid) as latest_cumulative_amount_paid,
        ROUND(SUM(cumulative_amount_paid) / SUM(cumulative_scheduled_due) * 100, 4) as weighted_latest_repayment_pct
    FROM cohort_latest_values
""").fetchdf()
print("\nCORRECT Evaluation (Aggregating each cohort at its latest Month-on-Book):")
print(df_vc_latest_mob.to_string())

# Check total disbursed principal in dim_loan for comparison
tot_loan_disb = con.execute("SELECT SUM(principal_amount) FROM fin_warehouse.dim_loan").fetchone()[0]
print(f"\nTotal Disbursed Principal in dim_loan: INR {tot_loan_disb:,.2f}")
