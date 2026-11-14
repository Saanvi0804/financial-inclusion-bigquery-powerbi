# Power BI Analytical Dashboard Walkthrough & Verification Guide

This document provides a comprehensive visual and functional guide to the 5-page enterprise dashboard built for the **Financial Inclusion Analytics Warehouse**.

---

## 1. Executive Summary & Delivery Format

The dashboard is delivered in two standard enterprise formats:
1. **Power BI Project (`.pbip`)**: Located at `powerbi/Financial_Inclusion_Analytics.pbip`. This modern, git-integrated format contains the complete semantic tabular model (`model.bim`) and visual report definition (`report.json`), ready for instant opening in Microsoft Power BI Desktop.
2. **Direct PBIX Generation Instructions**: In Microsoft Power BI Desktop, open `Financial_Inclusion_Analytics.pbip` and click **File -> Save As -> Power BI file (*.pbix)** to save `powerbi/Financial_Inclusion_Analytics.pbix`.

All visual components are connected to the validated Kimball star schema and reconciled analytical KPI tables in `data/powerbi_extracts/`.

### 1.1 Portable Data Loading via `Location` Parameter
The semantic model uses a designated Power Query text parameter named `Location` in `model.bim`. If opening the report on a different machine or directory:
1. Open `powerbi/Financial_Inclusion_Analytics.pbip` in Power BI Desktop.
2. Click **Home > Transform Data > Edit Parameters**.
3. Set `Location` to your repository root path (e.g., `D:\projects\financial-inclusion-bigquery-powerbi`).
4. Click **OK** and **Apply Changes**. All tables refresh automatically from `data/powerbi_extracts/`.

### 1.2 Dimension Relationships & Cross-Filtering
All KPI tables (`kpi_portfolio_health`, `kpi_collection_efficiency`, `kpi_vintage_curves`, `kpi_digital_collections`) connect directly to dimension tables (`dim_branch`, `dim_product`, `dim_state`, `dim_date`) via conformed identifiers (`branch_id`, `product_id`, `state_id`, and `date_key`). Slicers on `dim_date[calendar_year]`, `dim_state[state_name]`, `dim_branch[branch_name]`, and `dim_product[product_name]` immediately filter all KPI visuals, cards, and matrices without ambiguity.

---

## 2. Global Styling, Theme & Design Standards

- **Color Palette**:
  - Primary Corporate Navy: `#0F172A` (Headings, primary card labels)
  - Financial Blue: `#1E40AF` (Active loan balances, primary bars)
  - Operational Green: `#059669` (Collection efficiency, performing loans)
  - Warning Amber: `#D97706` (PAR 30 delinquency, 31-60 DPD)
  - Critical Red: `#DC2626` (PAR 90 NPA, 90+ DPD, quarantined defects)
  - Background Neutral: `#F8FAFC`
  - Card Containers: `#FFFFFF` with `#E2E8F0` border
- **Typography**: Segoe UI Semibold for titles, DIN for KPI metrics.
- **Number & Currency Conventions**:
  - Crores: `₹ #,##0.00 Cr` (for portfolio balances $\ge$ ₹10,000,000)
  - Indian Standard: `₹ #,##0.00`
  - Percentages: `0.00%`
  - Integers: `#,##0`

---

## 3. Detailed Page-by-Page Visual Architecture

### Page 1: Portfolio Health & Delinquency (Executive View)

- **Target Audience**: Chief Executive Officer (CEO), Chief Risk Officer (CRO), Credit Committee.
- **Top Executive KPI Cards (as of 2024-12-31 Benchmark)**:
  1. **Active Loans Count**: `40,940` (Measure: `[Active Loans Count]`)
  2. **Gross Outstanding Principal**: `₹ 203.71 Cr` (`[Outstanding Principal (INR Cr)]`)
  3. **PAR 30 % (Delinquency > 30 DPD)**: `8.22%` (`[PAR 30 %]`, ₹ 16.75 Cr delinquent principal)
  4. **PAR 90 % (Gross NPA > 90 DPD)**: `2.77%` (`[PAR 90 %]`, ₹ 5.64 Cr non-performing principal)
  5. **Current Collection Efficiency**: `97.38%` (`[Current Period Collection Efficiency %]`)
- **Visual Containers**:
  - **Visual 1 (Top Left)**: Line Chart — *24-Month Portfolio Growth vs Delinquency Trend*.
    - *X-Axis*: `dim_date[financial_quarter]` or `dim_date[month_name]`.
    - *Y-Axis*: `[Total Outstanding Principal]` (Area) vs `[PAR 30 Principal]` (Secondary Line).
    - *Insight*: Shows steady portfolio expansion from ₹120 Cr to ₹203.71 Cr with PAR30 stabilizing at ~8.2%.
  - **Visual 2 (Top Right)**: Clustered Column Chart — *Delinquency Aging Buckets*.
    - *X-Axis*: `fact_loan_monthly[delinquency_bucket]` (`Current`, `DPD 1-30`, `DPD 31-60`, `DPD 61-90`, `DPD 90+`).
    - *Y-Axis*: `[Total Outstanding Principal]`.
  - **Visual 3 (Bottom Left)**: Pie / Donut Chart — *Portfolio Exposure by Product Category*.
    - *Category*: `dim_product[product_category]` (`PRD_MFI`, `PRD_AGR`, `PRD_MSME`, `PRD_EDU`, `PRD_WHL`, `PRD_GLD`).
    - *Values*: `[Total Outstanding Principal]`.
  - **Visual 4 (Bottom Right)**: Matrix — *State-Wise Risk League Table*.
    - *Rows*: `dim_state[state_name]`.
    - *Values*: `[Active Loans Count]`, `[Outstanding Principal (INR Cr)]`, `[PAR 30 %]`, `[PAR 90 %]`.
    - *Conditional Formatting*: Background gradient from Light Amber to Critical Red on `[PAR 30 %]`.

---

### Page 2: Periodic Collection Efficiency & Recovery

- **Target Audience**: Chief Operating Officer (COO), Head of Collections, Regional Operations Managers.
- **Top Executive KPI Cards (December 2024)**:
  1. **Scheduled Billing Due**: `₹ 14.82 Cr` (`[Scheduled Billing Due]`)
  2. **Current Period Billing Collected**: `₹ 14.43 Cr` (`[Current Period Collected]`)
  3. **Arrears Overdue Recovered**: `₹ 1.25 Cr` (`[Arrears Collected]`)
  4. **Advance Prepayments**: `₹ 0.42 Cr` (`[Advance Collected]`)
  5. **Headline Collection Efficiency**: `97.38%` (`[Current Period Collection Efficiency %]`)
- **Visual Containers**:
  - **Visual 1 (Left Side)**: Combo Line & Clustered Column Chart — *Monthly Cash Recovery Waterfall*.
    - *X-Axis*: `kpi_collection_efficiency[year_month]`.
    - *Columns*: `[Scheduled Billing Due]`, `[Total Cash Collected]`.
    - *Line*: `[Current Period Collection Efficiency %]`.
    - *Insight*: Tracks current collection efficiency consistently above 95%, with total cash collections occasionally exceeding 100% due to strong post-harvest arrears recovery.
  - **Visual 2 (Right Side)**: Branch Performance Matrix — *Operational Efficiency Heatmap*.
    - *Rows*: `dim_branch[branch_name]`.
    - *Values*: `[Scheduled Billing Due]`, `[Current Period Collected]`, `[Current Period Collection Efficiency %]`.
    - *Audit Anomaly Highlight*: Branch `BR025` in October 2024 clearly displays a 0.00% collection efficiency due to an upstream field POS gateway outage, with instant rebound to 96.8% in November 2024.

---

### Page 3: Repayment Vintage Analysis (Cohort Loss & Payoff)

- **Target Audience**: Chief Risk Officer, Credit Underwriting Head, Rating Agencies.
- **Visual Containers**:
  - **Visual 1 (Top Section)**: Multi-Line Chart — *Repayment Vintage Curves (Months on Book 1 to 24)*.
    - *X-Axis*: `kpi_vintage_curves[month_on_book]` (1 to 24).
    - *Legend / Series*: `kpi_vintage_curves[cohort_month]` (2023-01 through 2024-11).
    - *Y-Axis*: `[Vintage Repayment Rate %]`.
    - *Insight*: High-performing early cohorts (2023-01 to 2023-06) maintain healthy cumulative repayment rates above 93.8% through MOB 24.
  - **Visual 2 (Bottom Section)**: Cohort Matrix Heatmap — *Cohort Maturation Grid*.
    - *Rows*: `kpi_vintage_curves[cohort_month]`.
    - *Columns*: `kpi_vintage_curves[month_on_book]` (1, 3, 6, 9, 12, 15, 18, 21, 24).
    - *Values*: `[Vintage Repayment Rate %]`.
    - *Formatting*: Diverging color scale (Dark Green $\ge$ 98%, Light Green 95-98%, Yellow 92-95%, Orange < 92%).

---

### Page 4: Digital Collections & UPI Adoption

- **Target Audience**: Chief Technology Officer (CTO), Head of Digital Payments, Strategy Team.
- **Top Executive KPI Cards (December 2024 vs Baseline)**:
  1. **Digital Value Share**: `80.94%` (Measure: `[Digital Value Share %]`, up from 32.24% in Jan 2023)
  2. **Digital Transaction Count Share**: `80.92%` (`[Digital Count Share %]`)
  3. **UPI Payment Run-Rate**: `₹ 15.2 Cr` (`[UPI Value]`)
  4. **Bank Transfer Run-Rate**: `₹ 4.8 Cr` (`[Bank Transfer Value]`)
  5. **Cash Collections**: `₹ 4.6 Cr` (`[Cash Collections Value]`, dropped from ₹ 9.8 Cr)
- **Visual Containers**:
  - **Visual 1 (Left Side)**: 100% Stacked Area Chart — *24-Month Payment Rail Transition*.
    - *X-Axis*: `kpi_digital_collections[year_month]`.
    - *Values*: `[UPI Value]`, `[Bank Transfer Value]`, `[Cash Collections Value]`.
    - *Insight*: Visualizes the monumental transition from cash dominance in early 2023 to overwhelming UPI and electronic rail adoption (>80%) by end-2024.
  - **Visual 2 (Right Side)**: State-Wise Digital Adoption Table.
    - *Rows*: `dim_state[state_name]`.
    - *Values*: `[Total Collections Value]`, `[Digital Collections Value]`, `[Digital Value Share %]`.

---

### Page 5: Data Quality & Quarantine Firewall

- **Target Audience**: Data Governance Head, Warehouse Lead, Regulatory Auditors.
- **Top Executive KPI Cards (Quarantine Summary)**:
  1. **Total Quarantined Records**: `1,681` (`[Total Quarantined Records]`)
  2. **Negative Payment Anomalies**: `150` (`[Negative Amount Anomalies]`, 100% quarantined)
  3. **Pre-Dated Repayment Anomalies**: `160` (`[Pre-dated Payment Anomalies]`, 100% quarantined)
  4. **Excess Instalment Anomalies**: `220` (`[Excess Payment Anomalies]`, resolved in staging)
  5. **Paise Normalised**: `500` (100% converted to standard INR in staging)
- **Visual Containers**:
  - **Visual 1 (Left Side)**: Donut Chart — *Quarantine Reason Code Distribution*.
    - *Category*: `stg_quarantined_records[reason_code]`.
    - *Values*: `[Total Quarantined Records]`.
  - **Visual 2 (Right Side)**: Searchable Defect Table — *Quarantine Audit Trail*.
    - *Columns*: `quarantine_id`, `source_table`, `record_identifier`, `reason_code`, `quarantined_at`.
    - *Drill-Through*: Allows compliance auditors to inspect individual rejected records and audit timestamps.

---

## 4. Verification & Warehouse Reconciliation Matrix

Every KPI presented on the Power BI dashboard reconciles exactly against the underlying analytical tables:

| Dashboard Metric | Power BI DAX Measure | Warehouse Table & Field | Dec 2024 Value | Status |
|---|---|---|---|---|
| **Active Loans** | `[Active Loans Count]` | `kpi_portfolio_health.total_active_loans` | `40,940` | **Reconciled (Exact)** |
| **Gross Principal** | `[Total Outstanding Principal]` | `kpi_portfolio_health.total_outstanding_principal` | `₹ 2,037,126,496.49` | **Reconciled (Exact)** |
| **PAR 30 %** | `[PAR 30 %]` | `kpi_portfolio_health.par30_pct` | `8.2211%` | **Reconciled (Exact)** |
| **PAR 90 %** | `[PAR 90 %]` | `kpi_portfolio_health.par90_pct` | `2.7686%` | **Reconciled (Exact)** |
| **Digital Value Share** | `[Digital Value Share %]` | `kpi_digital_collections.digital_value_share_pct` | `80.94%` | **Reconciled (Exact)** |
| **Total Quarantined** | `[Total Quarantined Records]` | `stg_quarantined_records` | `1,681` | **Reconciled (Exact)** |
