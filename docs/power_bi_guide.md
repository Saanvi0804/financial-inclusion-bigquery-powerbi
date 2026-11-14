# Power BI Enterprise Dashboard Guide & Report Specifications

This document outlines the visual layout, UX architecture, DAX integration, and configuration guide for the **5-page Financial Inclusion Analytical Dashboard** connected to Google BigQuery.

---

## 1. Connecting Power BI to Google BigQuery

### Method A: Live DirectQuery / Import via Google BigQuery Connector
1. Open **Power BI Desktop**.
2. Click **Get Data** -> **More...** -> **Database** -> **Google BigQuery** -> **Connect**.
3. Sign in with your Google Cloud organizational account or service account.
4. Select Billing Project ID: `financial-inclusion-prod` (or your GCP project ID).
5. Navigate to the datasets:
   - `fin_warehouse` -> Select `dim_date`, `dim_state`, `dim_branch`, `dim_product`, `dim_borrower_segment`, `dim_loan`, `fact_loan_monthly`, `fact_payment`.
   - `fin_analytics` -> Select `kpi_portfolio_health`, `kpi_collection_efficiency`, `kpi_vintage_curves`, `kpi_digital_collections`.
   - `fin_staging` -> Select `stg_quarantined_records`.
6. Select **Import** (recommended for sub-second visual reactivity) or **DirectQuery**.
7. Click **Load**.

### Method B: Rapid Offline Evaluation via Curated Extracts
1. Run `python scripts/export_powerbi_data.py` to produce fresh CSV extracts in `data/powerbi_extracts/`.
2. In Power BI Desktop, click **Get Data** -> **Folder** or **Text/CSV**.
3. Load the 12 extracted tables directly.

---

## 2. Dashboard Theme & Financial Styling Standards

- **Primary Brand Palette**:
  - Primary Corporate Navy: `#0F172A`
  - Accent Financial Blue: `#1E40AF`
  - Digital / Growth Green: `#059669`
  - Overdue / Delinquency Amber: `#D97706`
  - NPA / Critical Default Red: `#DC2626`
  - Light Background: `#F8FAFC`
  - Card Background: `#FFFFFF` (with subtle `#E2E8F0` border)
- **Indian Number Conventions**:
  - Crores: `₹ #,##0.00 Cr` (for metrics $\ge$ ₹10,000,000)
  - Lakhs: `₹ #,##0.00 L` (for metrics between ₹100,000 and ₹9,999,999)
  - Standard: `₹ #,##0.00`
  - Percentages: `0.00%`

---

## 3. Page-by-Page Visual Architecture

### Page 1: Portfolio Health & Delinquency (Executive View)

```
+---------------------------------------------------------------------------------------------------------+
| [LOGO] FINANCIAL INCLUSION WAREHOUSE -- PORTFOLIO HEALTH               [FY: All | Product: All | State: All] |
+---------------------+---------------------+---------------------+---------------------+-----------------+
| ACTIVE LOANS COUNT  | GROSS PRINCIPAL     | PAR 30 (OVERDUE)    | PAR 90 (NPA)        | COLLECTION EFF. |
| 40,940              | ₹ 203.71 Cr         | 8.22% (₹ 16.75 Cr)  | 2.77% (₹ 5.64 Cr)   | 97.4%           |
+---------------------+---------------------+---------------------+---------------------+-----------------+
| MONTHLY ACTIVE LOANS & PORTFOLIO TREND (24 Months) | DELINQUENCY AGING MIGRATION (Stacked Bar)           |
| [Line Chart: Total Principal vs PAR30 Amount]     | [DPD 0 | DPD 1-30 | DPD 31-60 | DPD 61-90 | DPD 90+]     |
+---------------------------------------------------+-----------------------------------------------------+
| PORTFOLIO RISK BY PRODUCT CATEGORY                | STATE-WISE DELINQUENCY LEAGUE TABLE                 |
| [Donut: MFI 42% | Agri 28% | MSME 18% | Edu 12%]  | [Matrix: State | Loans | Principal | PAR30% | PAR90%]   |
+---------------------------------------------------------------------------------------------------------+
```

- **Top KPI Cards**:
  1. **Active Loans**: `40,940` (Card visual using measure `[Active Loans Count]`).
  2. **Gross Principal**: `₹ 203.71 Cr` (`[Outstanding Principal (INR Cr)]`).
  3. **PAR 30 %**: `8.22%` (`[PAR 30 %]` with conditional formatting: Green < 5%, Amber 5-10%, Red > 10%).
  4. **PAR 90 %**: `2.77%` (`[PAR 90 %]`).
  5. **Headline Collection Efficiency**: `97.4%`.
- **Visual 1**: **Monthly Seasoning Trend (24 Months)**
  - *Type*: Area Chart / Line Chart.
  - *X-Axis*: `dim_date[Year Month]` (2023-01 to 2024-12).
  - *Y-Axis*: `[Total Outstanding Principal]` (Area) and `[PAR 30 Principal]` (Line on Secondary Y-Axis).
- **Visual 2**: **Delinquency Buckets Decomposition**
  - *Type*: 100% Stacked Bar Chart.
  - *Values*: `Current`, `DPD 1-30`, `DPD 31-60`, `DPD 61-90`, `DPD 90+`.
- **Visual 3**: **State Risk Matrix**
  - *Rows*: `dim_state[state_name]`.
  - *Columns / Values*: `[Active Loans Count]`, `[Total Outstanding Principal]`, `[PAR 30 %]`, `[PAR 90 %]`.

---

### Page 2: Periodic Collection Efficiency & Recovery

```
+---------------------------------------------------------------------------------------------------------+
| COLLECTION EFFICIENCY & BILLING RECOVERY                                [Month: Dec 2024 | Branch: All] |
+---------------------+---------------------+---------------------+---------------------+-----------------+
| SCHEDULED DUES      | CURRENT RECOVERED   | ARREARS RECOVERED   | ADVANCE CASH        | HEADLINE EFF.   |
| ₹ 14.82 Cr          | ₹ 14.43 Cr          | ₹ 1.25 Cr           | ₹ 0.42 Cr           | 97.38%          |
+---------------------+---------------------+---------------------+---------------------+-----------------+
| MONTHLY CASH RECOVERY WATERFALL (Scheduled vs Collections) | EFFICIENCY HEATMAP BY BRANCH               |
| [Clustered Column: Current Due vs Actual Cash Collected]    | [Matrix: 36 Branches x 24 Months Efficiency] |
+------------------------------------------------------------+--------------------------------------------+
| COLLECTIONS COMPONENT BREAKDOWN (Current vs Arrears vs Adv) | ANOMALY ALERT: BR025 OCTOBER 2024 OUTAGE   |
| [100% Stacked Area Chart across 24 Calendar Months]        | [Callout Card: 0 txns recorded in Oct 2024]|
+---------------------------------------------------------------------------------------------------------+
```

- **Top KPI Cards**:
  1. **Scheduled Billing Due**: `₹ 14.82 Cr` (`[Scheduled Billing Due]`).
  2. **Current Period Collections**: `₹ 14.43 Cr` (`[Current Period Collected]`).
  3. **Arrears Recovered**: `₹ 1.25 Cr` (`[Arrears Collected]`).
  4. **Headline Collection Efficiency**: `97.38%` (`[Current Period Collection Efficiency %]`).
  5. **Total Collection Ratio**: `108.6%` (`[Total Collection Ratio %]`).
- **Visual 1**: **Monthly Efficiency Evolution**
  - *Type*: Line and Clustered Column Chart.
  - *Columns*: `[Scheduled Billing Due]`, `[Total Cash Collected]`.
  - *Line*: `[Current Period Collection Efficiency %]`.
- **Visual 2**: **Branch Operational Performance Matrix**
  - *Rows*: `dim_branch[branch_name]`.
  - *Columns*: `dim_date[Year Month]`.
  - *Values*: `[Current Period Collection Efficiency %]` (Conditional formatting background: Red < 85%, Amber 85-95%, Green > 95%).
  - *Observation Highlight*: Branch `BR025` shows 0.00% in Oct 2024, rebounding to 96.8% in Nov 2024.

---

### Page 3: Repayment Vintage Analysis (Cohort Loss & Payoff)

```
+---------------------------------------------------------------------------------------------------------+
| LOAN REPAYMENT VINTAGE & MATURITY CURVES                                 [Product: All | Segment: All]  |
+---------------------------------------------------------------------------------------------------------+
| VINTAGE REPAYMENT MATURITY CURVES (Months-on-Book 1 to 24)                                              |
| [Line Chart: X=Month on Book (1..24), Y=Cumulative Repayment %, Legend=Disbursement Cohort Month]      |
+---------------------------------------------------------------------------------------------------------+
| COHORT REPAYMENT RATE MATRIX (% Cumulative Collected of Scheduled Dues)                                |
| Cohort    | MOB 1  | MOB 3  | MOB 6  | MOB 9  | MOB 12 | MOB 15 | MOB 18 | MOB 21 | MOB 24           |
| 2023-01   | 98.9%  | 98.0%  | 97.1%  | 96.4%  | 95.8%  | 95.2%  | 94.6%  | 94.1%  | 93.8%            |
| 2023-06   | 99.1%  | 98.4%  | 97.6%  | 96.9%  | 96.1%  | 95.5%  | 94.9%  | --     | --               |
| 2024-01   | 99.3%  | 98.8%  | 98.1%  | 97.4%  | 96.8%  | --     | --     | --     | --               |
+---------------------------------------------------------------------------------------------------------+
```

- **Visual 1**: **Vintage Curves (Months on Book 1 to 24)**
  - *Type*: Multi-line chart.
  - *X-Axis*: `kpi_vintage_curves[month_on_book]`.
  - *Y-Axis*: `[Vintage Repayment Rate %]`.
  - *Legend*: `kpi_vintage_curves[cohort_month]`.
- **Visual 2**: **Cohort Quality Matrix Heatmap**
  - *Rows*: `cohort_month` (2023-01 through 2024-11).
  - *Columns*: `month_on_book` (1, 3, 6, 9, 12, 15, 18, 21, 24).
  - *Values*: `[Vintage Repayment Rate %]`.

---

### Page 4: Digital Collections & UPI Adoption

```
+---------------------------------------------------------------------------------------------------------+
| DIGITAL COLLECTIONS & CASH-TO-DIGITAL TRANSFORMATION                    [State: All | Channel: All]     |
+---------------------+---------------------+---------------------+---------------------+-----------------+
| DIGITAL VALUE SHARE | UPI VALUE SHARE     | DIGITAL TXN SHARE   | DIGITAL VALUE YoY   | CASH VALUE      |
| 80.94% (+47.3 pts)  | 62.45%              | 80.92%              | +22.8% YoY          | ₹ 4.61 Cr       |
+---------------------+---------------------+---------------------+---------------------+-----------------+
| 24-MONTH DIGITAL VS CASH CHANNEL VALUE MIGRATION    | AVERAGE TICKET SIZE BY CHANNEL                     |
| [100% Stacked Area: UPI vs Bank Transfer vs Cash]  | [Bar Chart: Bank Transfer ₹18.4K | UPI ₹4.2K | Cash]|
+----------------------------------------------------+----------------------------------------------------+
| REGIONAL DIGITAL ADOPTION RANKING                  | DIGITAL ADOPTION PACE BY BORROWER SEGMENT          |
| [Horizontal Bar: Southern States 84% vs Central 77%]| [Line: Salaried 89% vs Rural Farmers 73%]         |
+---------------------------------------------------------------------------------------------------------+
```

- **Top KPI Cards**:
  1. **Digital Value Share**: `80.94%` (up from 32.24% in Jan 2023).
  2. **Digital Transaction Volume Share**: `80.92%`.
  3. **UPI Payment Value**: `₹ 15.2 Cr` (monthly run-rate).
  4. **Bank Transfer Value**: `₹ 4.8 Cr`.
  5. **Cash Payment Value**: `₹ 4.6 Cr` (down from ₹ 9.8 Cr).
- **Visual 1**: **24-Month Channel Migration**
  - *Type*: 100% Stacked Area Chart.
  - *X-Axis*: `year_month`.
  - *Series*: `UPI`, `Bank Transfer`, `Cash`.
- **Visual 2**: **Ticket Size Analysis**
  - *Type*: Clustered Column Chart.
  - *Values*: `[Avg Ticket Size UPI]`, `[Avg Ticket Size Bank Transfer]`, `[Avg Ticket Size Cash]`.

---

### Page 5: Data Quality, Quarantine & Pipeline Audit

```
+---------------------------------------------------------------------------------------------------------+
| BIGQUERY DATA QUALITY & QUARANTINE AUDIT MONITOR                        [Batch Run: Latest | Table: All]|
+---------------------+---------------------+---------------------+---------------------+-----------------+
| TOTAL QUARANTINED   | NEGATIVE PAYMENTS   | PRE-DATED PAYMENTS  | EXCESS INSTALMENTS  | PAISE CONVERSIONS|
| 1,681 records       | 150 records (100%)  | 160 records (100%)  | 220 records (100%)  | 500 txns (100%) |
+---------------------+---------------------+---------------------+---------------------+-----------------+
| QUARANTINE REASON BREAKDOWN BY SEVERITY             | PIPELINE INGESTION RUN AUDIT TRAIL                |
| [Donut Chart: Negative | Predated | Excess | Zero] | [Table: Table Name | Raw Rows | Loaded | Status]  |
+-----------------------------------------------------+---------------------------------------------------+
| QUARANTINED DEFECT LOG (Searchable Drill-Through)                                                       |
| [Matrix: Quarantine ID | Source Table | Record Identifier | Reason Code | Quarantined Timestamp]        |
+---------------------------------------------------------------------------------------------------------+
```

- **Top KPI Cards**:
  1. **Total Quarantined**: `1,681` (`[Total Quarantined Records]`).
  2. **Negative Payment Anomalies**: `150` (100% isolated).
  3. **Pre-dated Payment Anomalies**: `160` (100% isolated).
  4. **Excess Instalment Anomalies**: `220` (100% resolved in staging).
  5. **Paise Normalised**: `500` (100% converted to INR).
- **Visual 1**: **Quarantine Reason Distribution**
  - *Type*: Donut Chart.
  - *Dimension*: `stg_quarantined_records[reason_code]`.
  - *Values*: `[Total Quarantined Records]`.
- **Visual 2**: **Quarantine Defect Log**
  - *Table*: `quarantine_id`, `source_table`, `record_identifier`, `reason_code`, `quarantined_at`.
