# Power BI DAX Measure Catalog (46 Measures)
## Financial Inclusion Analytics Warehouse

**Semantic Model:** [model.bim](file:///C:/Users/Saanvi%20Shetty/Desktop/projects/financial-inclusion-bigquery-powerbi/powerbi/Financial_Inclusion_Analytics.SemanticModel/model.bim)  
**DAX Script File:** [dax_measures.dax](file:///C:/Users/Saanvi%20Shetty/Desktop/projects/financial-inclusion-bigquery-powerbi/powerbi/dax_measures.dax)  
**Measure Container Table:** `_Measures` (Disconnected DAX Calculation Table)  

---

## 1. Domain Group 1 — Portfolio Health & Risk Measures (11 Measures)

These measures evaluate loan portfolio scale, active accounts, outstanding principal exposure, and risk migration across Days Past Due (DPD) ageing buckets using point-in-time monthly snapshots.

| # | Measure Name | Format String | Underlying Fact Table | Date Relationship | DAX Formula Summary |
|:---:|:---|:---:|:---|:---:|:---|
| **1** | `Active Loans Count` | `#,##0` | `fact_loan_monthly` | `USERELATIONSHIP` (Snapshot Date) | `CALCULATE(DISTINCTCOUNT(fact_loan_monthly[loan_key]), fact_loan_monthly[outstanding_principal] > 0)` evaluated at max snapshot date |
| **2** | `Total Outstanding Principal` | `₹ #,##0.00` | `fact_loan_monthly` | `USERELATIONSHIP` (Snapshot Date) | `CALCULATE(SUM(fact_loan_monthly[outstanding_principal]))` evaluated at max snapshot date |
| **3** | `Outstanding Principal (INR Cr)` | `₹ #,##0.00 Cr` | `fact_loan_monthly` | Active Default | `DIVIDE([Total Outstanding Principal], 10000000, 0)` |
| **4** | `PAR 30 Principal` | `₹ #,##0.00` | `fact_loan_monthly` | `USERELATIONSHIP` (Snapshot Date) | `CALCULATE(SUM(fact_loan_monthly[outstanding_principal]), fact_loan_monthly[days_past_due] > 30)` |
| **5** | `PAR 30 %` | `0.00%` | `fact_loan_monthly` | Active Default | `DIVIDE([PAR 30 Principal], [Total Outstanding Principal], 0)` |
| **6** | `PAR 90 Principal` | `₹ #,##0.00` | `fact_loan_monthly` | `USERELATIONSHIP` (Snapshot Date) | `CALCULATE(SUM(fact_loan_monthly[outstanding_principal]), fact_loan_monthly[days_past_due] > 90)` |
| **7** | `PAR 90 %` | `0.00%` | `fact_loan_monthly` | Active Default | `DIVIDE([PAR 90 Principal], [Total Outstanding Principal], 0)` |
| **8** | `Current Principal` | `₹ #,##0.00` | `fact_loan_monthly` | `USERELATIONSHIP` (Snapshot Date) | `CALCULATE(SUM(fact_loan_monthly[outstanding_principal]), fact_loan_monthly[days_past_due] = 0)` |
| **9** | `Delinquency DPD 1-30` | `₹ #,##0.00` | `fact_loan_monthly` | `USERELATIONSHIP` (Snapshot Date) | `CALCULATE(SUM(fact_loan_monthly[outstanding_principal]), fact_loan_monthly[days_past_due] >= 1, fact_loan_monthly[days_past_due] <= 30)` |
| **10** | `Delinquency DPD 31-60` | `₹ #,##0.00` | `fact_loan_monthly` | `USERELATIONSHIP` (Snapshot Date) | `CALCULATE(SUM(fact_loan_monthly[outstanding_principal]), fact_loan_monthly[days_past_due] >= 31, fact_loan_monthly[days_past_due] <= 60)` |
| **11** | `Delinquency DPD 61-90` | `₹ #,##0.00` | `fact_loan_monthly` | `USERELATIONSHIP` (Snapshot Date) | `CALCULATE(SUM(fact_loan_monthly[outstanding_principal]), fact_loan_monthly[days_past_due] >= 61, fact_loan_monthly[days_past_due] <= 90)` |

---

## 2. Domain Group 2 — Collection Efficiency & Billing Measures (7 Measures)

These measures track monthly contractual demand against realized cash collections across current period billing, arrears recovery, and advance prepayments.

| # | Measure Name | Format String | Source Table | Date Relationship | DAX Formula Summary |
|:---:|:---|:---:|:---|:---:|:---|
| **12** | `Scheduled Billing Due` | `₹ #,##0.00` | `kpi_collection_efficiency` | Active (`month_date_key`) | `SUM(kpi_collection_efficiency[scheduled_amount_due])` |
| **13** | `Current Period Collected` | `₹ #,##0.00` | `kpi_collection_efficiency` | Active (`month_date_key`) | `SUM(kpi_collection_efficiency[current_period_collected])` |
| **14** | `Arrears Collected` | `₹ #,##0.00` | `kpi_collection_efficiency` | Active (`month_date_key`) | `SUM(kpi_collection_efficiency[arrears_collected])` |
| **15** | `Advance Collected` | `₹ #,##0.00` | `kpi_collection_efficiency` | Active (`month_date_key`) | `SUM(kpi_collection_efficiency[advance_collected])` |
| **16** | `Total Cash Collected` | `₹ #,##0.00` | `kpi_collection_efficiency` | Active (`month_date_key`) | `SUM(kpi_collection_efficiency[total_amount_collected])` |
| **17** | `Current Period Collection Efficiency %` | `0.00%` | `kpi_collection_efficiency` | Active Default | `DIVIDE([Current Period Collected], [Scheduled Billing Due], 0)` |
| **18** | `Total Collection Ratio %` | `0.00%` | `kpi_collection_efficiency` | Active Default | `DIVIDE([Total Cash Collected], [Scheduled Billing Due], 0)` |

---

## 3. Domain Group 3 — Digital Collections & Channel Transformation (10 Measures)

These measures quantify the strategic displacement of cash by UPI and net banking digital payment rails.

| # | Measure Name | Format String | Source Table | Date Relationship | DAX Formula Summary |
|:---:|:---|:---:|:---|:---:|:---|
| **19** | `Total Collections Value` | `₹ #,##0.00` | `kpi_digital_collections` | Active (`month_date_key`) | `SUM(kpi_digital_collections[total_collection_value])` |
| **20** | `Digital Collections Value` | `₹ #,##0.00` | `kpi_digital_collections` | Active (`month_date_key`) | `SUM(kpi_digital_collections[digital_collection_value])` |
| **21** | `Cash Collections Value` | `₹ #,##0.00` | `kpi_digital_collections` | Active (`month_date_key`) | `SUM(kpi_digital_collections[cash_collection_value])` |
| **22** | `UPI Value` | `₹ #,##0.00` | `kpi_digital_collections` | Active (`month_date_key`) | `SUM(kpi_digital_collections[upi_value])` |
| **23** | `Bank Transfer Value` | `₹ #,##0.00` | `kpi_digital_collections` | Active (`month_date_key`) | `SUM(kpi_digital_collections[bank_transfer_value])` |
| **24** | `Digital Value Share %` | `0.00%` | `kpi_digital_collections` | Active Default | `DIVIDE([Digital Collections Value], [Total Collections Value], 0)` |
| **25** | `Digital Count Share %` | `0.00%` | `kpi_digital_collections` | Active Default | `DIVIDE(SUM(kpi_digital_collections[digital_transaction_count]), SUM(kpi_digital_collections[total_transaction_count]), 0)` |
| **38** | `Digital Transactions Count` | `#,##0` | `kpi_digital_collections` | Active (`month_date_key`) | `SUM(kpi_digital_collections[digital_transaction_count])` |
| **39** | `Average Digital Payment Amount` | `₹ #,##0.00` | `kpi_digital_collections` | Active Default | `DIVIDE([Digital Collections Value], [Digital Transactions Count], 0)` |
| **44** | `Digital Collection MoM Growth %` | `0.00%` | `kpi_digital_collections` | Active Default | `AVERAGE(kpi_digital_collections[mom_digital_value_growth_pct])` |
| **45** | `Digital Collection YoY Growth %` | `0.00%` | `kpi_digital_collections` | Active Default | `AVERAGE(kpi_digital_collections[yoy_digital_value_growth_pct])` |

---

## 4. Domain Group 4 — Repayment Vintage Curves (3 Measures)

These measures track the cumulative recovery velocity of loan disbursement vintages across months on book (MOB 1 to 24).

| # | Measure Name | Format String | Source Table | Date Relationship | DAX Formula Summary |
|:---:|:---|:---:|:---|:---:|:---|
| **26** | `Cumulative Scheduled Due (Vintage)` | `₹ #,##0.00` | `kpi_vintage_curves` | Active (`cohort_date_key`) | `SUMX(SUMMARIZE(kpi_vintage_curves, [cohort_month], [product_id]), CALCULATE(SUM(kpi_vintage_curves[cumulative_scheduled_due]), kpi_vintage_curves[month_on_book] = CALCULATE(MAX(kpi_vintage_curves[month_on_book]))))` |
| **27** | `Cumulative Amount Paid (Vintage)` | `₹ #,##0.00` | `kpi_vintage_curves` | Active (`cohort_date_key`) | `SUMX(SUMMARIZE(kpi_vintage_curves, [cohort_month], [product_id]), CALCULATE(SUM(kpi_vintage_curves[cumulative_amount_paid]), kpi_vintage_curves[month_on_book] = CALCULATE(MAX(kpi_vintage_curves[month_on_book]))))` |
| **28** | `Vintage Repayment Rate %` | `0.00%` | `kpi_vintage_curves` | Active Default | `DIVIDE([Cumulative Amount Paid (Vintage)], [Cumulative Scheduled Due (Vintage)], 0)` |

---

## 5. Domain Group 5 — Data Quality & Quarantine Firewall (8 Measures)

These measures quantify ingestion pipeline throughput, clean vs quarantined record counts, anomaly distributions, and overall firewall pass rates.

| # | Measure Name | Format String | Source Table | Relationship Scope | DAX Formula Summary |
|:---:|:---|:---:|:---|:---:|:---|
| **29** | `Total Quarantined Records` | `#,##0` | `stg_quarantined_records` | Disconnected | `COUNTROWS(stg_quarantined_records)` |
| **30** | `Negative Amount Anomalies` | `#,##0` | `stg_quarantined_records` | Disconnected | `CALCULATE(COUNTROWS(stg_quarantined_records), stg_quarantined_records[reason_code] = "NEGATIVE_PAYMENT_AMOUNT")` |
| **31** | `Pre-dated Payment Anomalies` | `#,##0` | `stg_quarantined_records` | Disconnected | `CALCULATE(COUNTROWS(stg_quarantined_records), stg_quarantined_records[reason_code] = "PAYMENT_PREDATES_DISBURSEMENT")` |
| **32** | `Excess Payment Anomalies` | `#,##0` | `stg_quarantined_records` | Disconnected | `CALCULATE(COUNTROWS(stg_quarantined_records), stg_quarantined_records[reason_code] = "EXCESS_INSTALMENT_PAYMENT")` |
| **40** | `Total Clean Records` | `#,##0` | `fact_payment` | Fact Table | `COUNTROWS(fact_payment)` (533,147 verified records) |
| **41** | `Total Raw Records` | `#,##0` | Combined | Disconnected | `[Total Clean Records] + [Total Quarantined Records]` (534,828 payloads) |
| **42** | `Data Quality Pass Rate %` | `0.00%` | Combined | Disconnected | `DIVIDE([Total Clean Records], [Total Raw Records], 0)` (99.69% pass rate) |
| **43** | `Issue Categories Count` | `#,##0` | `stg_quarantined_records` | Disconnected | `DISTINCTCOUNT(stg_quarantined_records[reason_code])` (8 anomaly codes) |

---

## 6. Domain Group 6 — Origination & Loan Master Measures (6 Measures)

These measures evaluate loan contract origination parameters using inactive disbursement date links activated via `USERELATIONSHIP`.

| # | Measure Name | Format String | Source Table | Date Relationship | DAX Formula Summary |
|:---:|:---|:---:|:---|:---:|:---|
| **33** | `Loans Disbursed Count` | `#,##0` | `dim_loan` | `USERELATIONSHIP` (Disbursement Date) | `CALCULATE(DISTINCTCOUNT(dim_loan[loan_key]))` |
| **34** | `Total Disbursed Principal` | `₹ #,##0.00` | `dim_loan` | `USERELATIONSHIP` (Disbursement Date) | `CALCULATE(SUM(dim_loan[principal_amount]))` |
| **35** | `Disbursed Principal (INR Cr)` | `₹ #,##0.00 Cr` | `dim_loan` | Active Default | `DIVIDE([Total Disbursed Principal], 10000000, 0)` |
| **36** | `Payments by Loan Disbursement Date` | `₹ #,##0.00` | `fact_payment` | `USERELATIONSHIP` (Disbursement Date) | `CALCULATE(SUM(fact_payment[payment_amount]))` |
| **37** | `Allocations by Cash Payment Date` | `₹ #,##0.00` | `fact_instalment_allocation` | `USERELATIONSHIP` (Payment Date) | `CALCULATE(SUM(fact_instalment_allocation[allocated_amount]))` |
| **46** | `Total Loans Count` | `#,##0` | `dim_loan` | Dimension Master | `CALCULATE(DISTINCTCOUNT(dim_loan[loan_id]), dim_loan[loan_key] > 0)` (52,000 accounts) |

---

## 7. Measure Integrity & Verification Summary

All 46 measures have been reconciled against the underlying warehouse CSV extracts:
- Zero divide-by-zero errors (all divisions guarded via `DIVIDE(..., ..., 0)`).
- Zero orphan measure definitions (every measure resides cleanly in `_Measures`).
- Every measure referenced in [report.json](file:///C:/Users/Saanvi%20Shetty/Desktop/projects/financial-inclusion-bigquery-powerbi/powerbi/Financial_Inclusion_Analytics.Report/report.json) strictly resolves to [model.bim](file:///C:/Users/Saanvi%20Shetty/Desktop/projects/financial-inclusion-bigquery-powerbi/powerbi/Financial_Inclusion_Analytics.SemanticModel/model.bim).
