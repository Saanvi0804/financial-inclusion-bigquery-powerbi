import json
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bim_path = os.path.join(PROJECT_ROOT, "powerbi", "Financial_Inclusion_Analytics.SemanticModel", "model.bim")

with open(bim_path, "r", encoding="utf-8") as f:
    bim = json.load(f)

measure_updates = {
    "Active Loans Count": "VAR MaxSnapshotDate = CALCULATE(MAX(fact_loan_monthly[snapshot_date_key]), USERELATIONSHIP(fact_loan_monthly[snapshot_date_key], dim_date[date_key])) RETURN IF(ISBLANK(MaxSnapshotDate), BLANK(), CALCULATE(DISTINCTCOUNT(fact_loan_monthly[loan_key]), fact_loan_monthly[snapshot_date_key] = MaxSnapshotDate, fact_loan_monthly[outstanding_principal] > 0, USERELATIONSHIP(fact_loan_monthly[snapshot_date_key], dim_date[date_key])))",
    "Total Outstanding Principal": "VAR MaxSnapshotDate = CALCULATE(MAX(fact_loan_monthly[snapshot_date_key]), USERELATIONSHIP(fact_loan_monthly[snapshot_date_key], dim_date[date_key])) RETURN IF(ISBLANK(MaxSnapshotDate), BLANK(), CALCULATE(SUM(fact_loan_monthly[outstanding_principal]), fact_loan_monthly[snapshot_date_key] = MaxSnapshotDate, USERELATIONSHIP(fact_loan_monthly[snapshot_date_key], dim_date[date_key])))",
    "PAR 30 Principal": "VAR MaxSnapshotDate = CALCULATE(MAX(fact_loan_monthly[snapshot_date_key]), USERELATIONSHIP(fact_loan_monthly[snapshot_date_key], dim_date[date_key])) RETURN IF(ISBLANK(MaxSnapshotDate), BLANK(), CALCULATE(SUM(fact_loan_monthly[outstanding_principal]), fact_loan_monthly[snapshot_date_key] = MaxSnapshotDate, fact_loan_monthly[days_past_due] > 30, USERELATIONSHIP(fact_loan_monthly[snapshot_date_key], dim_date[date_key])))",
    "PAR 90 Principal": "VAR MaxSnapshotDate = CALCULATE(MAX(fact_loan_monthly[snapshot_date_key]), USERELATIONSHIP(fact_loan_monthly[snapshot_date_key], dim_date[date_key])) RETURN IF(ISBLANK(MaxSnapshotDate), BLANK(), CALCULATE(SUM(fact_loan_monthly[outstanding_principal]), fact_loan_monthly[snapshot_date_key] = MaxSnapshotDate, fact_loan_monthly[days_past_due] > 90, USERELATIONSHIP(fact_loan_monthly[snapshot_date_key], dim_date[date_key])))",
    "Current Principal": "VAR MaxSnapshotDate = CALCULATE(MAX(fact_loan_monthly[snapshot_date_key]), USERELATIONSHIP(fact_loan_monthly[snapshot_date_key], dim_date[date_key])) RETURN IF(ISBLANK(MaxSnapshotDate), BLANK(), CALCULATE(SUM(fact_loan_monthly[outstanding_principal]), fact_loan_monthly[snapshot_date_key] = MaxSnapshotDate, fact_loan_monthly[days_past_due] = 0, USERELATIONSHIP(fact_loan_monthly[snapshot_date_key], dim_date[date_key])))",
    "Delinquency DPD 1-30": "VAR MaxSnapshotDate = CALCULATE(MAX(fact_loan_monthly[snapshot_date_key]), USERELATIONSHIP(fact_loan_monthly[snapshot_date_key], dim_date[date_key])) RETURN IF(ISBLANK(MaxSnapshotDate), BLANK(), CALCULATE(SUM(fact_loan_monthly[outstanding_principal]), fact_loan_monthly[snapshot_date_key] = MaxSnapshotDate, fact_loan_monthly[days_past_due] >= 1, fact_loan_monthly[days_past_due] <= 30, USERELATIONSHIP(fact_loan_monthly[snapshot_date_key], dim_date[date_key])))",
    "Delinquency DPD 31-60": "VAR MaxSnapshotDate = CALCULATE(MAX(fact_loan_monthly[snapshot_date_key]), USERELATIONSHIP(fact_loan_monthly[snapshot_date_key], dim_date[date_key])) RETURN IF(ISBLANK(MaxSnapshotDate), BLANK(), CALCULATE(SUM(fact_loan_monthly[outstanding_principal]), fact_loan_monthly[snapshot_date_key] = MaxSnapshotDate, fact_loan_monthly[days_past_due] >= 31, fact_loan_monthly[days_past_due] <= 60, USERELATIONSHIP(fact_loan_monthly[snapshot_date_key], dim_date[date_key])))",
    "Delinquency DPD 61-90": "VAR MaxSnapshotDate = CALCULATE(MAX(fact_loan_monthly[snapshot_date_key]), USERELATIONSHIP(fact_loan_monthly[snapshot_date_key], dim_date[date_key])) RETURN IF(ISBLANK(MaxSnapshotDate), BLANK(), CALCULATE(SUM(fact_loan_monthly[outstanding_principal]), fact_loan_monthly[snapshot_date_key] = MaxSnapshotDate, fact_loan_monthly[days_past_due] >= 61, fact_loan_monthly[days_past_due] <= 90, USERELATIONSHIP(fact_loan_monthly[snapshot_date_key], dim_date[date_key])))"
}

m_table = [t for t in bim["model"]["tables"] if t["name"] == "_Measures"][0]
updated_count = 0
for m in m_table["measures"]:
    if m["name"] in measure_updates:
        m["expression"] = measure_updates[m["name"]]
        updated_count += 1
        print(f"Updated {m['name']}")

assert updated_count == 8, f"Expected 8 updates, got {updated_count}"

with open(bim_path, "w", encoding="utf-8") as f:
    json.dump(bim, f, indent=2)

print("Successfully updated model.bim with 8 corrected snapshot DAX measures!")
