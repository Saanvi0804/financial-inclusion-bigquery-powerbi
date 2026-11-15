# Power BI Dashboard Implementation Guide
## Financial Inclusion Analytics Warehouse

**Power BI Project:** [Financial_Inclusion_Analytics.pbip](file:///C:/Users/Saanvi%20Shetty/Desktop/projects/financial-inclusion-bigquery-powerbi/powerbi/Financial_Inclusion_Analytics.pbip)  
**Report Definition:** [report.json](file:///C:/Users/Saanvi%20Shetty/Desktop/projects/financial-inclusion-bigquery-powerbi/powerbi/Financial_Inclusion_Analytics.Report/report.json)  
**Semantic Model:** [model.bim](file:///C:/Users/Saanvi%20Shetty/Desktop/projects/financial-inclusion-bigquery-powerbi/powerbi/Financial_Inclusion_Analytics.SemanticModel/model.bim)  
**DAX Measures File:** [dax_measures.dax](file:///C:/Users/Saanvi%20Shetty/Desktop/projects/financial-inclusion-bigquery-powerbi/powerbi/dax_measures.dax)  
**Author:** Candidate Take-Home Submission  

---

## 1. Executive Summary & Design System

The **Financial Inclusion Analytics Dashboard** is an enterprise-grade, five-page interactive business intelligence solution built directly on top of the validated **Fact Constellation (Galaxy Schema)** semantic model. It provides microfinance executive leadership, portfolio risk managers, operations directors, and data governance officers with deep, real-time transparency into loan portfolio health, collection efficiency, cohort repayment dynamics, digital payment channel adoption, and ingestion firewall surveillance.

### Professional Theme & Typography
- **Canvas Resolution**: Standard 16:9 widescreen ($1280 \times 720$ pixels).
- **Grid Layout Architecture**:
  - **Row 1 ($y = 12, h = 38$)**: Full-width Executive Title Header Banner ($x=16, w=1248$).
  - **Row 2 ($y = 54, h = 48$)**: Dedicated Top Filter Bar with spacious Dropdown Slicers ($w = 300\text{px}$ to $616\text{px}$).
  - **Row 3 ($y = 106, h = 80$)**: Executive KPI Callout Cards ($w = 164\text{px}$ to $300\text{px}$).
  - **Rows 4 & 5 ($y = 190 \text{ to } 708, h = 518$)**: Analytical Canvas (balanced 2-column or 2-row grid).
- **Typography**: Clean corporate sans-serif hierarchy (Titles: 14pt Bold `#0F172A`, Subtitles: 10pt `#64748B`, Callouts: 20pt Bold).
- **Restrained Color Palette**:
  - **Portfolio Health & Neutral State**: Corporate Navy (`#0F172A`), Slate Blue (`#1E40AF`), Cobalt (`#2563EB`).
  - **Risk & Delinquency (DPD / PAR)**: Amber Warning (`#D97706`), Red Alert (`#DC2626`).
  - **Cash Collections & Efficiency**: Emerald Green (`#059669`), Teal (`#0D9488`).
  - **Digital Payment Rails**: Indigo UPI (`#4F46E5`), Sky Blue Net Banking (`#0284C7`), Violet Advance (`#7C3AED`).

---

## 2. Phase 2B Root Cause Diagnoses & Architectural Solutions

### A. Resolution of Page 1 Blank KPI Cards & State Matrix
* **Identified Symptom**: `Active Loans Count`, `Total Outstanding Principal`, `PAR 30 %`, `PAR 90 %` evaluated to `BLANK()`, and the state-wise table appeared empty.
* **Root Cause Analysis**: The calendar dimension `dim_date` extends from `2022-01-01` to `2026-12-31` (a standard 5-year calendar dimension). In the default unfiltered report context, `MAX(dim_date[date_key])` evaluated to `20261231`. However, historical snapshot data in `fact_loan_monthly` spans from `2023-01-31` to `2024-12-31`. Because `snapshot_date_key = 20261231` contained zero rows, all snapshot DAX measures returned `BLANK()`, and Power BI's pivot table pruned all 11 state rows because every measure was blank.
* **Architectural Fix**: Refactored all 8 snapshot measures in `model.bim` and `dax_measures.dax` to dynamically resolve the maximum available snapshot date within the active filter context:
  ```dax
  VAR MaxSnapshotDate = 
      CALCULATE(
          MAX(fact_loan_monthly[snapshot_date_key]),
          USERELATIONSHIP(fact_loan_monthly[snapshot_date_key], dim_date[date_key])
      )
  RETURN
      IF(
          ISBLANK(MaxSnapshotDate),
          BLANK(),
          CALCULATE(
              DISTINCTCOUNT(fact_loan_monthly[loan_key]),
              fact_loan_monthly[snapshot_date_key] = MaxSnapshotDate,
              fact_loan_monthly[outstanding_principal] > 0,
              USERELATIONSHIP(fact_loan_monthly[snapshot_date_key], dim_date[date_key])
          )
      )
  ```
* **Validation Outcome**:
  - In default context, `MaxSnapshotDate` evaluates to `20241231`.
  - `Active Loans Count` displays **40,940**.
  - `Total Outstanding Principal` displays **₹203.71 Cr** (₹153.28 Cr when filtered by core active parameters).
  - `PAR 30 %` displays **8.22%**, `PAR 90 %` displays **4.79%**.
  - State matrix immediately populates all 11 states (Maharashtra: 4,658 loans, ₹23.05 Cr; Rajasthan: 4,669 loans, ₹23.21 Cr; Bihar: 4,538 loans, ₹22.42 Cr, etc.).

### B. Resolution of Slicer Cramping Across All Pages
* **Identified Symptom**: Slicers were crammed into a single 45px tall row beside the title, displaying only 1 clipped row with small scrollbars.
* **Architectural Fix**: 
  1. Separated the Executive Title banner into its own dedicated row ($y = 12, h = 38, w = 1248$).
  2. Placed slicers into a dedicated top filter bar ($y = 54, h = 48$) with wide container footprints ($w = 300\text{px}$ to $616\text{px}$).
  3. Added `"data": [{"properties": {"mode": {"expr": {"Literal": {"Value": "'Dropdown'"}}}}}]` to every slicer visual configuration.
  4. Enabled dropdown search capabilities across all dimensional textual slicers.

### C. Resolution of Page 2 Whitespace & Layout Balancing
* **Identified Symptom**: Page 2 exhibited empty whitespace on the left while content was concentrated on the right.
* **Root Cause Analysis**: The combo chart (`lineClusteredColumnComboChart`) used non-standard projection names (`ColumnValues` and `LineValues`). Power BI Desktop requires role names `Y` (for column values) and `Y2` (for line values). Because the roles did not match, the entire 710px chart rendered blank, leaving only the right pivot table visible.
* **Architectural Fix**: 
  1. Updated `build_combo_chart` to bind columns to role `Y` and line efficiency to role `Y2`.
  2. Balanced the layout into a clean two-column grid: Monthly Combo Chart ($x=16, w=680, h=518$) on the left, and Branch Performance Matrix ($x=708, w=556, h=518$) on the right, completely eliminating unused margins.

### D. Page 4 Monthly Trend Sharp Drop (Data Validation Finding)
* **Identified Symptom**: The monthly collection volume chart displayed a steep drop at the end of the trend.
* **Empirical Forensic Validation**:
  - The warehouse covers core operating years **2023–2024** (24 full calendar months).
  - October 2024 exhibits the known regional collection outage (BR025) which was successfully caught and quarantined.
  - November 2024 had 29,539 digital transactions (₹16.88 Cr total collections).
  - December 2024 had 29,900 digital transactions (₹16.64 Cr total collections).
  - In `kpi_collection_efficiency`, `scheduled_amount_due = 0.00` for 2025 because all loans were originated in 2023–2024 and scheduled billing ended on 2024-12-31.
  - Payments recorded in `fact_payment` for January 2025 (1,778 transactions, ₹78.28 Lakhs) and February 2025 (149 transactions, ₹7.48 Lakhs) represent late trailing arrears received during a 10-day stub period ending on **2025-02-10**.
  - **Conclusion**: The sharp drop is **not a data defect or DAX error**, but an empirical trailing partial-period phenomenon reflecting the cutoff date of the synthetic dataset.
  - **Dashboard Solution**: Added subtitle clarity identifying 2023–2024 as the core operating horizon, and ensured slicers allow isolated analysis of full operational years.

---

## 3. Page-by-Page Implementation & Visual Specifications

### Page 1 — Portfolio Health & Risk Exposure
* **Purpose**: Executive command center tracking active portfolio scale, outstanding principal exposure, and credit risk migration across DPD ageing buckets.
* **Canvas Coordinates**: $1280 \times 720$ pixels.

#### Slicers (Row 2: $y = 54, h = 48$)
1. **Calendar Year** ($w = 300\text{px}$): Slices by year (`dim_date.calendar_year`).
2. **State Geography** ($w = 300\text{px}$): Slices by state (`dim_state.state_name`).
3. **Operational Branch** ($w = 300\text{px}$): Slices by branch (`dim_branch.branch_name`).
4. **Credit Product** ($w = 300\text{px}$): Slices by loan product (`dim_product.product_name`).

#### KPI Summary Cards (Row 3: $y = 106, h = 80$)
1. **Total Portfolio Loans**: `_Measures.Total Loans Count` (52,000 accounts).
2. **Active Loans**: `_Measures.Active Loans Count` (40,940 accounts as of Dec 2024).
3. **Total Disbursed (₹ Cr)**: `_Measures.Disbursed Principal (INR Cr)` (Cumulative origination capital).
4. **Outstanding Principal (₹ Cr)**: `_Measures.Outstanding Principal (INR Cr)` (Active book balance).
5. **PAR 30 Rate**: `_Measures.PAR 30 %` (8.22% portfolio at risk > 30 days).
6. **PAR 90 Rate (NPL)**: `_Measures.PAR 90 %` (4.79% non-performing loan threshold).

#### Analytical Visualizations (Rows 4 & 5)
1. **Monthly Portfolio Outstanding & PAR 30 Balance Progression** (`lineChart`, $x=16, y=190, w=616, h=252$):
   - *X-Axis*: `dim_date.year_month` (full 24-month progression).
   - *Y-Axis*: `_Measures.Total Outstanding Principal`, `_Measures.PAR 30 Principal`.
2. **Monthly Delinquency Aging Profile by DPD Buckets** (`clusteredColumnChart`, $x=648, y=190, w=616, h=252$):
   - *X-Axis*: `dim_date.year_month`.
   - *Y-Axis*: `Current Principal`, `Delinquency DPD 1-30`, `Delinquency DPD 31-60`, `Delinquency DPD 61-90`, `PAR 90 Principal`.
3. **Outstanding Principal Exposure by Product Category** (`pieChart`, $x=16, y=446, w=460, h=262$):
   - *Category*: `dim_product.product_name`.
   - *Values*: `_Measures.Total Outstanding Principal`.
4. **State-wise Portfolio Risk & Outstanding Balance Breakdown** (`pivotTable`, $x=488, y=446, w=776, h=262$):
   - *Rows*: `dim_state.state_name`.
   - *Values*: `Active Loans Count`, `Outstanding Principal (INR Cr)`, `PAR 30 %`, `PAR 90 %`.

---

### Page 2 — Collection Efficiency & Billing
* **Purpose**: Evaluates repayment cash flow performance, comparing contractual scheduled billing against actual realized cash across current dues, arrears recovery, and advance prepayments.

#### Slicers (Row 2: $y = 54, h = 48$)
1. **Billing Month** ($w = 300\text{px}$): `kpi_collection_efficiency.year_month`
2. **State Geography** ($w = 300\text{px}$): `dim_state.state_name`
3. **Operational Branch** ($w = 300\text{px}$): `dim_branch.branch_name`
4. **Credit Product** ($w = 300\text{px}$): `dim_product.product_name`

#### KPI Summary Cards (Row 3: $y = 106, h = 80$)
1. **Scheduled Billing Due**: `_Measures.Scheduled Billing Due`
2. **Total Cash Collected**: `_Measures.Total Cash Collected`
3. **Current Dues Collected**: `_Measures.Current Period Collected`
4. **Prior Arrears Recovered**: `_Measures.Arrears Collected`
5. **Advance Prepayments**: `_Measures.Advance Collected`
6. **Headline Current Efficiency %**: `_Measures.Current Period Collection Efficiency %`

#### Analytical Visualizations (Row 4: $y = 190, h = 518$)
1. **Monthly Scheduled Billing Dues vs Cash Recovered & Efficiency Ratio** (`lineClusteredColumnComboChart`, $x=16, w=680, h=518$):
   - *Category*: `kpi_collection_efficiency.year_month`
   - *Column Values (Y)*: `Scheduled Billing Due`, `Total Cash Collected`
   - *Line Values (Y2)*: `Current Period Collection Efficiency %`
2. **Operational Branch Collection & Arrears Performance Matrix** (`pivotTable`, $x=708, w=556, h=518$):
   - *Rows*: `dim_branch.branch_name`
   - *Values*: `Scheduled Billing Due`, `Current Dues Collected`, `Arrears Collected`, `Headline Current Efficiency %`

---

### Page 3 — Repayment Vintage Curves
* **Purpose**: Actuarial cohort analysis tracking cumulative repayment velocity across disbursement cohorts over months on book (MOB 1 to 24).

#### Slicers (Row 2: $y = 54, h = 48$)
1. **Credit Product** ($w = 616\text{px}$): `dim_product.product_name`
2. **Disbursement Cohort Month** ($w = 616\text{px}$): `kpi_vintage_curves.cohort_month`

#### KPI Summary Cards (Row 3: $y = 106, h = 80$)
1. **Cohort Disbursed Principal**: `_Measures.Total Disbursed Principal`
2. **Cumulative Cash Repaid**: `_Measures.Cumulative Amount Paid (Vintage)`
3. **Cumulative Scheduled Dues**: `_Measures.Cumulative Scheduled Due (Vintage)`
4. **Portfolio Vintage Repayment Rate %**: `_Measures.Vintage Repayment Rate %`

#### Analytical Visualizations
1. **Repayment Vintage Curve by Month-on-Book** (`lineChart`, $x=16, y=190, w=1248, h=252$):
   - *X-Axis*: `kpi_vintage_curves.month_on_book` (1 to 24)
   - *Series / Legend*: `kpi_vintage_curves.cohort_month`
   - *Y-Axis*: `_Measures.Vintage Repayment Rate %`
2. **Cohort Repayment Performance Matrix** (`pivotTable`, $x=16, y=446, w=1248, h=262$):
   - *Rows*: `kpi_vintage_curves.cohort_month`
   - *Columns*: `kpi_vintage_curves.month_on_book`
   - *Values*: `_Measures.Vintage Repayment Rate %`

---

### Page 4 — Digital Collections Growth & Transformation
* **Purpose**: Tracks cashless migration and payment channel adoption across UPI, net banking, and field cash.

#### Slicers (Row 2: $y = 54, h = 48$)
1. **State Geography** ($w = 405\text{px}$): `dim_state.state_name`
2. **Reporting Month** ($w = 405\text{px}$): `kpi_digital_collections.year_month`
3. **Payment Channel Mode** ($w = 406\text{px}$): `fact_payment.payment_channel`

#### KPI Summary Cards (Row 3: $y = 106, h = 80$)
1. **Digital Value**: `_Measures.Digital Collections Value`
2. **Digital Txns**: `_Measures.Digital Transactions Count`
3. **Digital Value %**: `_Measures.Digital Value Share %`
4. **Digital Txn %**: `_Measures.Digital Count Share %`
5. **UPI Collections**: `_Measures.UPI Value`
6. **Net Banking / NEFT**: `_Measures.Bank Transfer Value`
7. **Avg Digital Ticket**: `_Measures.Average Digital Payment Amount`

#### Analytical Visualizations (Row 4: $y = 190, h = 518$)
1. **Monthly Cash vs UPI vs Bank Transfer Volume Distribution** (`stackedAreaChart`, $x=16, w=680, h=518$):
   - *Category*: `kpi_digital_collections.year_month`
   - *Values*: `UPI Value`, `Bank Transfer Value`, `Cash Collections Value`
2. **State-wise Digital Adoption & Channel Volume Breakdown** (`pivotTable`, $x=708, w=556, h=518$):
   - *Rows*: `dim_state.state_name`
   - *Values*: `Total Collections Value`, `Digital Collections Value`, `Digital Value Share %`, `Digital Count Share %`

---

### Page 5 — Data Quality & Quarantine Firewall
* **Purpose**: Surveillance over data ingestion, documenting rejected records and tracking pipeline integrity.

#### Slicers (Row 2: $y = 54, h = 48$)
1. **Source Table** ($w = 616\text{px}$): `stg_quarantined_records.source_table`
2. **Anomaly Reason Code** ($w = 616\text{px}$): `stg_quarantined_records.reason_code`

#### KPI Summary Cards (Row 3: $y = 106, h = 80$)
1. **Raw Ingested Records**: `_Measures.Total Raw Records` (534,828 records)
2. **Clean Verified Records**: `_Measures.Total Clean Records` (533,147 fact rows)
3. **Quarantined Anomalies**: `_Measures.Total Quarantined Records` (1,681 records)
4. **Pipeline Pass Rate %**: `_Measures.Data Quality Pass Rate %` (99.69%)
5. **Anomaly Root Causes**: `_Measures.Issue Categories Count` (8 categories)

#### Analytical Visualizations (Row 4: $y = 190, h = 518$)
1. **Distribution of Quarantined Anomalies by Reason Code** (`pieChart`, $x=16, w=480, h=518$):
   - *Category*: `stg_quarantined_records.reason_code`
   - *Values*: `_Measures.Total Quarantined Records`
2. **Forensic Audit Trail of Quarantined Payloads** (`tableEx`, $x=508, w=756, h=518$):
   - *Columns*: `quarantine_id`, `batch_run_id`, `source_table`, `reason_code`, `record_identifier`, `quarantined_at`
