import duckdb

con = duckdb.connect('data/warehouse/financial_inclusion_bigquery.duckdb', read_only=True)

def test_aggregation(cohort_filter=None, product_filter=None, mob_filter=None):
    where_clauses = ['1=1']
    if cohort_filter:
        if isinstance(cohort_filter, list):
            cohorts = ", ".join([f"'{c}'" for c in cohort_filter])
            where_clauses.append(f"cohort_month IN ({cohorts})")
        else:
            where_clauses.append(f"cohort_month = '{cohort_filter}'")
    if product_filter:
        where_clauses.append(f"(product_name = '{product_filter}' OR product_id = '{product_filter}')")
    if mob_filter:
        where_clauses.append(f"month_on_book = {mob_filter}")
    
    where_sql = " AND ".join(where_clauses)
    
    # Correct calculation: max valid MOB for each (cohort_month, product_id)
    sql_correct = f"""
        WITH filtered AS (
            SELECT * FROM fin_analytics.kpi_vintage_curves WHERE {where_sql}
        ),
        latest_mob AS (
            SELECT cohort_month, product_id, MAX(month_on_book) as max_mob
            FROM filtered
            GROUP BY cohort_month, product_id
        )
        SELECT 
            CAST(SUM(v.cumulative_amount_paid) AS DOUBLE) as cum_paid,
            CAST(SUM(v.cumulative_scheduled_due) AS DOUBLE) as cum_due,
            CAST(SUM(v.cumulative_amount_paid) / SUM(v.cumulative_scheduled_due) * 100.0 AS DOUBLE) as rep_rate
        FROM latest_mob m
        JOIN filtered v
          ON m.cohort_month = v.cohort_month 
         AND m.product_id = v.product_id 
         AND m.max_mob = v.month_on_book
    """
    # Original naive calculation: SUM of cumulative columns across all rows
    sql_original = f"""
        SELECT 
            CAST(SUM(cumulative_amount_paid) AS DOUBLE) as cum_paid,
            CAST(SUM(cumulative_scheduled_due) AS DOUBLE) as cum_due,
            CAST(SUM(cumulative_amount_paid) / SUM(cumulative_scheduled_due) * 100.0 AS DOUBLE) as rep_rate
        FROM fin_analytics.kpi_vintage_curves
        WHERE {where_sql}
    """
    corr = con.execute(sql_correct).fetchone()
    orig = con.execute(sql_original).fetchone()
    return orig, corr

print("="*70)
print("--- 1. NO FILTERS (OVERALL) ---")
orig, corr = test_aggregation()
print(f"Original Naive: Paid=INR {orig[0]:,.2f}, Due=INR {orig[1]:,.2f}, Rate={orig[2]:.4f}%")
print(f"Correct Latest: Paid=INR {corr[0]:,.2f}, Due=INR {corr[1]:,.2f}, Rate={corr[2]:.4f}%")

print("\n--- 2. SINGLE COHORT (2023-01) ---")
orig, corr = test_aggregation(cohort_filter="2023-01")
print(f"Original Naive: Paid=INR {orig[0]:,.2f}, Due=INR {orig[1]:,.2f}, Rate={orig[2]:.4f}%")
print(f"Correct Latest: Paid=INR {corr[0]:,.2f}, Due=INR {corr[1]:,.2f}, Rate={corr[2]:.4f}%")

print("\n--- 3. MULTIPLE COHORTS (2023-01, 2023-02, 2023-03) ---")
orig, corr = test_aggregation(cohort_filter=["2023-01", "2023-02", "2023-03"])
print(f"Original Naive: Paid=INR {orig[0]:,.2f}, Due=INR {orig[1]:,.2f}, Rate={orig[2]:.4f}%")
print(f"Correct Latest: Paid=INR {corr[0]:,.2f}, Due=INR {corr[1]:,.2f}, Rate={corr[2]:.4f}%")

print("\n--- 4. PRODUCT FILTER (PRD_MFI) ---")
orig, corr = test_aggregation(product_filter="PRD_MFI")
print(f"Original Naive: Paid=INR {orig[0]:,.2f}, Due=INR {orig[1]:,.2f}, Rate={orig[2]:.4f}%")
print(f"Correct Latest: Paid=INR {corr[0]:,.2f}, Due=INR {corr[1]:,.2f}, Rate={corr[2]:.4f}%")

print("\n--- 5. SPECIFIC MOB (MOB=6) ---")
orig, corr = test_aggregation(mob_filter=6)
print(f"Original Naive: Paid=INR {orig[0]:,.2f}, Due=INR {orig[1]:,.2f}, Rate={orig[2]:.4f}%")
print(f"Correct Latest: Paid=INR {corr[0]:,.2f}, Due=INR {corr[1]:,.2f}, Rate={corr[2]:.4f}%")
print("="*70)
