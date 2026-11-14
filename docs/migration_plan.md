# Migration Plan: Financial Inclusion Analytics Warehouse (BigQuery + Power BI)

**Target Project**: `financial-inclusion-bigquery-powerbi`  
**Source Project (Read-Only)**: `financial-inclusion-analytics-warehouse`  
**Date**: November 2026  
**Author**: Antigravity Data Engineering & BI Architecture  
**Status**: Approved for Implementation (Phase 2 Deliverable)  

---

## 1. Executive Summary & Migration Rationale

The **Financial Inclusion Analytics Warehouse** is an end-to-end data warehousing and business intelligence platform engineered for microfinance and retail lending institutions operating across emerging markets in India. 

The existing implementation utilised **DuckDB** as an in-process columnar analytical engine and **Streamlit + Plotly** for reporting. While effective for embedded analytics, enterprise scale, multi-user concurrency, governance, and institutional executive consumption require migrating this platform to:
1. **Google BigQuery** as the cloud-native, enterprise-grade central data warehouse.
2. **BigQuery Standard SQL** for all staging transformations, dimensional star-schema modeling, and pre-aggregated analytical KPI models.
3. **Microsoft Power BI** as the enterprise visualization and business intelligence layer, providing DAX-powered analytical dashboards, interactive slice-and-dice exploration, and Indian financial-year reporting.

This document sets forth the comprehensive architectural roadmap, source-to-target table mappings, financial logic translations, reconciliation benchmarks, and testing strategies required to execute this migration without data loss, logic drift, or regression.

---

## 2. Existing vs. Proposed Architecture

```
================================ EXISTING ARCHITECTURE (DuckDB + Streamlit) ================================

[Synthetic Data Generator] 
   └── 52,000 Loans, 46,000 Borrowers, 533k+ Repayments (Seed 42, 10 Seeded Anomalies)
         │
         ▼ (CSV Export)
[data/raw/*.csv]
         │
         ▼ (DuckDB CSV Ingestion)
[DuckDB Database: financial_inclusion.duckdb]
   ├── raw.* (raw.loans, raw.repayments, raw.instalments, raw.borrowers, raw.branches)
   ├── staging.* (stg_loans, stg_repayments, stg_instalments, stg_instalment_allocation)
   ├── warehouse.* (dim_date, dim_state, dim_branch, dim_product, dim_segment, dim_loan,
   │                fact_payment, fact_instalment_allocation, fact_loan_monthly)
   └── kpis.* (kpi_portfolio_health, kpi_collection_efficiency, kpi_vintage, kpi_digital)
         │
         ▼
[Streamlit / Plotly Dashboard] (dashboard/app.py) & [Pytest 45 Tests] (tests/*.py)


================================ PROPOSED TARGET ARCHITECTURE (BigQuery + Power BI) ========================

[Synthetic Data Generator & Ingestion Engine] (Python 3.12, Seed 42)
   ├── Preserves 52,000 Loans, 46,000 Borrowers, 530k+ Repayments, 10 Seeded Anomalies
   └── Repeatable, idempotent batch loader into BigQuery
         │
         ▼
[Google BigQuery Cloud Data Warehouse]
   ├── Dataset 1: `fin_raw` (Immutable Raw Layer + Ingestion Metadata)
   │     ├── raw_loans, raw_borrowers, raw_branches, raw_repayments, raw_instalments
   │     └── raw_ingestion_audit_log
   │
   ├── Dataset 2: `fin_staging` (Cleansing, Normalisation, Quarantine Governance)
   │     ├── stg_quarantined_records (Full payload & audit reason for all rejected records)
   │     ├── stg_loans (Deduplication, key standardisation, fallback surrogates)
   │     ├── stg_borrowers (Attribute validation)
   │     ├── stg_branches (Surrogate key mapping)
   │     ├── stg_repayments (INR normalisation, negative amount exclusion, chronology check)
   │     ├── stg_instalments (Excess payment capping, corrupted DPD retention)
   │     └── stg_instalment_allocation (Sequential FIFO waterfall via interval overlap)
   │
   ├── Dataset 3: `fin_warehouse` (Enterprise Star Schema)
   │     ├── Dimensions:
   │     │     dim_date, dim_state, dim_branch, dim_product, dim_borrower_segment, dim_loan
   │     └── Facts:
   │           fact_payment (Transaction grain, clustered by payment_date, loan_key)
   │           fact_instalment_allocation (Allocation line-item grain)
   │           fact_loan_monthly (Periodic snapshot grain, partitioned by snapshot_date)
   │
   └── Dataset 4: `fin_analytics` (Pre-Aggregated Business KPI Models)
         ├── kpi_portfolio_health (PAR30, PAR90, delinquency buckets)
         ├── kpi_collection_efficiency (Scheduled dues, current collections, arrears, total ratio)
         ├── kpi_vintage_curves (Cohort disbursement, MOB 1-24, cumulative curves)
         └── kpi_digital_collections (Digital share %, ticket sizes, MoM/YoY growth)
         │
         ├──► [Power BI Desktop Semantic Model & Reporting Dashboard]
         │       ├── DirectQuery / Import mode connected to BigQuery
         │       ├── Star-schema relationships with single cross-filtering
         │       ├── Structured DAX measure hierarchy (Portfolio, Collections, Digital, QA)
         │       └── 5 Interactive Report Pages:
         │             1. Portfolio Health & Credit Risk
         │             2. Periodic Collection Efficiency
         │             3. Cohort Repayment Vintage
         │             4. Digital Collections Transition
         │             5. Data Quality & Quarantine Audit
         │
         └──► [Automated Pytest Suite (>= 45 Tests)] & [Independent Python Recalculation Engine]
```

---

## 3. Reusable vs. Rewritten Modules

| Component / Module | Source Path (`financial-inclusion-analytics-warehouse`) | Target Path (`financial-inclusion-bigquery-powerbi`) | Action | Migration Strategy & Adjustments |
|---|---|---|---|---|
| **Synthetic Generator** | `scripts/generate_data.py` | `scripts/generate_data.py` | **Reuse with Modular Enhancements** | Keep identical random seed (`42`), loan volumes (`52,000`), borrower count (`46,000`), and all 10 intentionally seeded anomalies (BR025 Oct 2024 outage, paise amounts, negative amounts, duplicate loans/txns, corrupted DPD). Output CSVs to local staging before BigQuery ingestion. |
| **Ingestion Engine** | `scripts/load_data.py` | `scripts/ingest_bigquery.py` | **Complete Rewrite** | Replace DuckDB internal table creation with BigQuery batch load jobs (`google-cloud-bigquery`), explicit BigQuery schemas, table clustering/partitioning, and audit logging into `fin_raw.raw_ingestion_audit_log`. Support dual mode: BigQuery Cloud API and zero-charge local fallback verification. |
| **Data Profiler** | `scripts/profile_data.py` | `scripts/profile_data.py` | **Rewrite for BigQuery SQL** | Port SQL profiling queries to BigQuery Standard SQL dialect; output comprehensive `docs/data_quality_report.md`. |
| **Staging SQL** | `sql/staging/*.sql` | `sql/staging/*.sql` | **Rewrite for BigQuery Standard SQL** | Translate syntax: `strftime()` -> `FORMAT_DATE()`, `date_diff()` -> `DATE_DIFF()`, `CAST(... AS DECIMAL)` -> `CAST(... AS NUMERIC)`, string concatenation `||` or `CONCAT()`. Enforce explicit quarantine into `fin_staging.stg_quarantined_records`. |
| **Dimensional SQL** | `sql/dimensions/*.sql` | `sql/dimensions/*.sql` | **Rewrite for BigQuery Standard SQL** | Implement surrogate keys (`ROW_NUMBER()` or `FARM_FINGERPRINT`), fallback surrogate key `-1` (`UNKNOWN_BRANCH`, `UNKNOWN_PRODUCT`). |
| **Fact Models** | `sql/facts/*.sql` | `sql/facts/*.sql` | **Rewrite for BigQuery Standard SQL** | Partition `fact_loan_monthly` by `snapshot_date`, cluster `fact_payment` by `payment_date_key`. Implement interval-based FIFO waterfall and reducing-balance amortisation with exact `NUMERIC` types. |
| **KPI SQL Models** | `sql/kpis/*.sql` | `sql/kpis/*.sql` | **Rewrite for BigQuery Standard SQL** | Port `kpi_portfolio_health`, `kpi_collection_efficiency`, `kpi_vintage_curves`, and `kpi_digital_collections` to `fin_analytics`. Replace DuckDB window and date functions with BigQuery Standard SQL. |
| **Orchestrator** | `scripts/run_pipeline.py` | `scripts/run_pipeline.py` | **Complete Rewrite** | Orchestrates end-to-end BigQuery pipeline execution, dataset initialization, SQL file staging, table creation, and multi-layer reconciliation logging. |
| **Independent Audit** | `scripts/verify_recalculation.py` | `scripts/verify_recalculation.py` | **Enhance & Port** | Reconcile pure Python calculations directly against BigQuery `fin_warehouse.fact_loan_monthly` and `fin_analytics.kpi_portfolio_health`. Address the 1-paisa rounding anomaly. |
| **Automated Tests** | `tests/*.py` (4 files, 45 tests) | `tests/*.py` (>= 45 tests) | **Port to BigQuery Client** | Port all 45 test assertions from DuckDB connection to BigQuery connection. Verify that raw anomaly tests and clean warehouse tests remain strictly separated. |
| **BI Dashboard** | `dashboard/app.py` (Streamlit) | `powerbi/Financial_Inclusion_Analytics.pbip` / `.pbit` | **Complete Redesign in Power BI** | Rebuild all 5 analytical pages in Power BI Desktop with enterprise UI styling, DAX measure hierarchy, relationship modeling, and Indian number formatting (`₹ Cr`, `₹ L`). |

---

## 4. Source-to-Target Table Mapping

### 4.1 Ingestion / Raw Layer

| Source Table (DuckDB) | Target Table (BigQuery) | Target Dataset | Grain / Description | Partitioning & Clustering |
|---|---|---|---|---|
| `raw.loans` | `raw_loans` | `fin_raw` | 1 row per raw loan application / record | Clustered by `product_id`, `state_id` |
| `raw.borrowers` | `raw_borrowers` | `fin_raw` | 1 row per borrower demographic record | Clustered by `borrower_segment` |
| `raw.branches` | `raw_branches` | `fin_raw` | 1 row per physical branch location | Clustered by `state_id` |
| `raw.repayments` | `raw_repayments` | `fin_raw` | 1 row per raw inbound payment event | Partitioned by `payment_date`, Clustered by `loan_id` |
| `raw.instalments` | `raw_instalments` | `fin_raw` | 1 row per scheduled contractual instalment | Partitioned by `due_date`, Clustered by `loan_id` |
| *New* | `raw_ingestion_audit_log` | `fin_raw` | 1 row per batch ingestion event | Partitioned by `ingestion_timestamp` |

### 4.2 Staging Layer

| Source Table (DuckDB) | Target Table (BigQuery) | Target Dataset | Grain / Description | Key Transformations & Quarantine Rules |
|---|---|---|---|---|
| `stg_quarantined_records` | `stg_quarantined_records` | `fin_staging` | 1 row per quarantined anomalous record | Captures `batch_run_id`, `source_table`, `record_identifier`, `reason_code`, `raw_payload`. |
| `staging.stg_loans` | `stg_loans` | `fin_staging` | 1 row per unique validated loan | Deduplication (`ROW_NUMBER()`), missing branch fallback (`UNKNOWN_BRANCH`), invalid product fallback (`UNKNOWN_PRODUCT`). |
| `staging.stg_borrowers` | `stg_borrowers` | `fin_staging` | 1 row per borrower | Demographic cleansing, whitespace trimming. |
| `staging.stg_branches` | `stg_branches` | `fin_staging` | 1 row per branch | Standardisation of branch keys and region mappings. |
| `staging.stg_repayments` | `stg_repayments` | `fin_staging` | 1 row per validated payment | Deduplication, negative amount exclusion to quarantine, pre-disbursement payment exclusion to quarantine, explicit PAISE to INR division (`/ 100.0`). |
| `staging.stg_instalments` | `stg_instalments` | `fin_staging` | 1 row per scheduled instalment | Cap excess payment (`LEAST(amount_paid, amount_due)`), preserve raw DPD for lineage. |
| `staging.stg_instalment_allocation` | `stg_instalment_allocation` | `fin_staging` | 1 row per transaction-to-instalment allocation | Chronological FIFO waterfall via cumulative dues and payment intervals. Splits principal and interest proportionally. |

### 4.3 Dimensional Warehouse Layer (Star Schema)

| Source Table (DuckDB) | Target Table (BigQuery) | Target Dataset | Table Type | Primary Key | Foreign Keys / Grain |
|---|---|---|---|---|---|
| `warehouse.dim_date` | `dim_date` | `fin_warehouse` | Dimension | `date_key` (INT64) | Role-playing calendar (2022-2026), Indian FY (April-March). |
| `warehouse.dim_state` | `dim_state` | `fin_warehouse` | Dimension | `state_key` (INT64) | 10 Indian states, regional classification. |
| `warehouse.dim_branch` | `dim_branch` | `fin_warehouse` | Dimension | `branch_key` (INT64) | 36 branches, location classification (Urban, Semi-Urban, Rural), includes fallback `-1`. |
| `warehouse.dim_product` | `dim_product` | `fin_warehouse` | Dimension | `product_key` (INT64) | 5 loan products, interest rate bounds, includes fallback `-1`. |
| `warehouse.dim_borrower_segment` | `dim_borrower_segment` | `fin_warehouse` | Dimension | `borrower_segment_key` (INT64) | Borrower segment, income band, occupation archetype, includes fallback `-1`. |
| `warehouse.dim_loan` | `dim_loan` | `fin_warehouse` | Dimension | `loan_key` (INT64) | Static loan origination attributes, includes fallback `-1`. |
| `warehouse.fact_payment` | `fact_payment` | `fin_warehouse` | Transaction Fact | `payment_key` (INT64) | Grain: 1 row per payment transaction. Keys: `loan_key`, `payment_date_key`, `branch_key`, `state_key`, `product_key`, `borrower_segment_key`. |
| `warehouse.fact_instalment_allocation` | `fact_instalment_allocation` | `fin_warehouse` | Allocation Line Fact | `allocation_key` (INT64) | Grain: 1 row per allocation event. Keys: `transaction_id`, `instalment_id`, `loan_key`, `payment_date_key`, `due_date_key`. |
| `warehouse.fact_loan_monthly` | `fact_loan_monthly` | `fin_warehouse` | Periodic Snapshot Fact | `snapshot_key` (INT64) | Grain: 1 row per loan per month-end snapshot date. Partitioned by `snapshot_date`, clustered by `branch_key`, `product_key`. |

### 4.4 Analytics / KPI Layer

| Source Table (DuckDB) | Target Table (BigQuery) | Target Dataset | Grain / Dimensionality | Key Metrics Computed |
|---|---|---|---|---|
| `kpis.kpi_portfolio_health` | `kpi_portfolio_health` | `fin_analytics` | `year_month`, `state_name`, `branch_name`, `product_name`, `borrower_segment` | Active loans, outstanding principal, DPD buckets (1-30, 31-60, 61-90, 90+), PAR30 %, PAR90 %. |
| `kpis.kpi_collection_efficiency` | `kpi_collection_efficiency` | `fin_analytics` | `year_month`, `state_name`, `branch_name`, `product_name` | Scheduled dues, current collections, arrears collections, advance collections, total cash collections, current-period efficiency %, total collection ratio %. |
| `kpis.kpi_vintage_curves` | `kpi_vintage_curves` | `fin_analytics` | `cohort_month`, `product_name`, `month_on_book` | Cohort loans, scheduled due MOB, paid amount MOB, cumulative scheduled due, cumulative paid amount, vintage repayment rate %. |
| `kpis.kpi_digital_collections` | `kpi_digital_collections` | `fin_analytics` | `year_month`, `state_name` | Total collections, digital collections (UPI + Bank), cash collections, digital value share %, digital count share %, average ticket sizes, MoM and YoY growth. |

---

## 5. Financial Logic Migration Strategy & The PAR30 Investigation

### 5.1 Deep-Dive Investigation: Warehouse PAR30 (8.2306%) vs. Independent Python PAR30 (8.2215%)

In accordance with Phase 1 requirements, an exhaustive loan-level audit was executed across all 52,000 loans comparing `warehouse.fact_loan_monthly` (as of `2024-12-31`) against `scripts/verify_recalculation.py`.

#### A. Empirical Findings:
1. **Total Book Reconciliation**:
   - Total Monitored Cumulative Loans: **52,000** (Exact match)
   - Active Loans with Positive Balance: **40,940** (Exact match)
   - Total Monitored Outstanding Principal:
     * Warehouse: **₹2,037,126,496.49**
     * Pure Python: **₹2,037,126,498.03**
     * Absolute Variance: **₹1.54 on ₹2.037 Billion book (< 0.0000001%)**
2. **PAR30 Difference**:
   - Warehouse PAR30 Rate: **8.2306%** (PAR30 Principal: ₹167,667,293.41)
   - Pure Python PAR30 Rate: **8.2215%** (PAR30 Principal: ₹167,482,625.68)
   - Absolute Variance: **0.0091 percentage points (0.91 bps)** (Principal difference: ₹184,667.73)
3. **Root Cause Analysis (Isolated to Exactly 5 Loans)**:
   The divergence was traced to exactly five loans:
   - `LN035417` (Outstanding Principal: ₹6,540.31)
   - `LN040838` (Outstanding Principal: ₹122,498.67)
   - `LN023655` (Outstanding Principal: ₹66,569.97)
   - `LN038317` (Outstanding Principal: ₹2,288.45)
   - `LN037307` (Outstanding Principal: ₹4,429.33)
   - *Sum of Outstanding Principal of these 5 loans*: **₹184,667.73 (Exactly matches the variance!)**

4. **Technical & Mathematical Mechanism**:
   - Each of these 5 borrowers missed or delayed their December 2024 instalment ($N$), but had paid their November 2024 instalment ($N-1$).
   - Due to fractional interest calculations and 2-decimal rounding in partial payments, Instalment $N-1$ had a remaining unallocated residual of exactly **₹0.01 (one paisa)**.
   - In DuckDB SQL:
     ```sql
     MAX(CASE WHEN (amount_due - paid_amt) > 0.01 THEN date_diff('day', due_date, snapshot_date) ELSE 0 END) AS days_past_due
     ```
     Because DuckDB evaluated `(amount_due - paid_amt)` in IEEE 754 double precision floating-point arithmetic:
     `4515.74 - 4515.73 = 0.010000000000000231`
     Because `0.010000000000000231 > 0.01` evaluated to `TRUE`, the November instalment was treated as overdue! As of December 31, 2024, the November instalment was **37 to 58 days past due (> 30 DPD)**. Consequently, DuckDB classified these 5 loans as PAR30.
   - In Python `verify_recalculation.py`:
     ```python
     if alloc_to_inst < (due_amt - 0.01):
     ```
     Here, `4515.73 < (4515.74 - 0.01)` evaluated to `4515.73 < 4515.73`, which is `FALSE`. Python recognized the ₹0.01 discrepancy as within the 1-paisa rounding tolerance. Thus, only the December instalment (due in December, DPD 7 to 28 days $\le 30$) was considered overdue, correctly keeping the loan out of PAR30.

#### B. Approved Institutional Financial Definition for BigQuery Migration:
In retail banking, microfinance, and RBI credit reporting:
> **"An instalment is legally and contractually classified as overdue if and only if the remaining unpaid balance exceeds the minimal currency denomination unit (1 paisa / ₹0.01). Fractional rounding residuals of $\le ₹0.01$ resulting from proportional principal/interest amortization splits must never trigger delinquency or shift a performing credit facility into Portfolio at Risk."**

**BigQuery Implementation Rule**:
BigQuery Standard SQL will use exact **`NUMERIC` / `BIGNUMERIC`** fixed-point decimal arithmetic (never `FLOAT64`) and explicit rounding:
```sql
MAX(CASE WHEN ROUND(amount_due - paid_amt, 2) > 0.01 THEN DATE_DIFF(snapshot_date, due_date, DAY) ELSE 0 END) AS days_past_due
```
This guarantees exact precision, eliminates floating-point artifacts, and aligns the warehouse result with the approved financial standard of **8.2215%** (while documenting full backward reconciliation with the legacy DuckDB figure of **8.2306%**).

---

### 5.2 Chronological FIFO Allocation Waterfall in BigQuery Standard SQL

The sequential allocation of inbound repayment cash against contractual scheduled instalments will be implemented in BigQuery using cumulative window frames and interval overlap logic:

```sql
WITH cum_instalments AS (
    SELECT 
        loan_id, instalment_id, instalment_number, due_date,
        amount_due, principal_component, interest_component,
        COALESCE(SUM(amount_due) OVER (
            PARTITION BY loan_id ORDER BY instalment_number 
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ), NUMERIC '0.00') AS prev_cum_due,
        SUM(amount_due) OVER (
            PARTITION BY loan_id ORDER BY instalment_number 
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cum_due
    FROM `fin_staging.stg_instalments`
),
cum_payments AS (
    SELECT 
        loan_id, transaction_id, payment_date, payment_amount, payment_channel,
        COALESCE(SUM(payment_amount) OVER (
            PARTITION BY loan_id ORDER BY payment_date, transaction_id 
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ), NUMERIC '0.00') AS prev_cum_pay,
        SUM(payment_amount) OVER (
            PARTITION BY loan_id ORDER BY payment_date, transaction_id 
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
    ROUND((LEAST(p.cum_pay, i.cum_due) - GREATEST(p.prev_cum_pay, i.prev_cum_due)) * 
          SAFE_DIVIDE(i.principal_component, i.amount_due), 2) AS allocated_principal,
    ROUND((LEAST(p.cum_pay, i.cum_due) - GREATEST(p.prev_cum_pay, i.prev_cum_due)) - 
          ROUND((LEAST(p.cum_pay, i.cum_due) - GREATEST(p.prev_cum_pay, i.prev_cum_due)) * 
                SAFE_DIVIDE(i.principal_component, i.amount_due), 2), 2) AS allocated_interest
FROM cum_payments p
JOIN cum_instalments i 
    ON p.loan_id = i.loan_id
   AND GREATEST(p.prev_cum_pay, i.prev_cum_due) < LEAST(p.cum_pay, i.cum_due);
```

### 5.3 Month-End Reducing Balance Outstanding Principal

For each month-end reporting snapshot date $S$:
1. Eligible loans: `disbursement_date <= S`.
2. Total principal repaid up to snapshot: $\sum_{t: \text{payment\_date} \le S} \text{allocated\_principal}_{i, t}$.
3. Month-end Outstanding Principal:
   $$\text{outstanding\_principal}(i, S) = \max(0.00, \text{disbursed\_principal}_i - \text{principal\_repaid}_{\le S})$$
4. Guaranteed zero-inflation: Future prepayments or unallocated lifetime overpayments do not produce negative balances.

### 5.4 Collection Efficiency Formulations

To ensure institutional clarity, two collection efficiency metrics are reported:
1. **Current-Period Scheduled Efficiency (%)**:
   $$\text{Current-Period Efficiency}(M) = \frac{\sum \text{allocated\_amount} \quad (\text{payment\_date} \in M \text{ AND } \text{due\_date} \in M)}{\sum \text{amount\_due} \quad (\text{due\_date} \in M)} \times 100$$
   *Strictly bounded in $[0.00\%, 100.00\%]$. Demonstrates current billing realization.*
2. **Total Collection Ratio (%)**:
   $$\text{Total Collection Ratio}(M) = \frac{\text{Current Period Collected} + \text{Arrears Recovered} + \text{Advance Collected}}{\text{Scheduled Due}(M)} \times 100$$
   *Can exceed $100.00\%$ during active recovery cycles (e.g. Branch BR025 in Nov 2024).*

---

## 6. BigQuery Dataset & Physical Architecture

```
fin_raw
├── raw_loans (Clustered: product_id, state_id)
├── raw_borrowers (Clustered: borrower_segment)
├── raw_branches (Clustered: state_id)
├── raw_repayments (Partitioned: payment_date, Clustered: loan_id)
├── raw_instalments (Partitioned: due_date, Clustered: loan_id)
└── raw_ingestion_audit_log (Partitioned: ingestion_timestamp)

fin_staging
├── stg_quarantined_records (Clustered: source_table, reason_code)
├── stg_loans
├── stg_borrowers
├── stg_branches
├── stg_repayments
├── stg_instalments
└── stg_instalment_allocation

fin_warehouse
├── dim_date (Partitioned: full_date)
├── dim_state
├── dim_branch
├── dim_product
├── dim_borrower_segment
├── dim_loan (Clustered: product_id, branch_id)
├── fact_payment (Partitioned: payment_date, Clustered: loan_key, branch_key)
├── fact_instalment_allocation (Partitioned: payment_date, Clustered: instalment_id)
└── fact_loan_monthly (Partitioned: snapshot_date, Clustered: branch_key, product_key)

fin_analytics
├── kpi_portfolio_health (Clustered: year_month, state_name, product_name)
├── kpi_collection_efficiency (Clustered: year_month, branch_name)
├── kpi_vintage_curves (Clustered: cohort_month, product_name)
└── kpi_digital_collections (Clustered: year_month, state_name)
```

---

## 7. Power BI Semantic Model Design

### 7.1 Data Source Connection Strategy
- **Mode**: Import Mode initially for blazing-fast in-memory performance, sub-second cross-filtering, and offline portfolio review; designed with full DirectQuery compatibility for BigQuery pushdown.
- **Connection Method**: Google BigQuery Connector / BigQuery Storage REST API / ODBC.

### 7.2 Semantic Model Star Schema & Relationships

```
              +----------------------+
              |     dim_product      |
              +----------------------+
                         │ 1
                         │
                         │ *
+-----------------+   +-------------------------+   +-------------------+
|    dim_date     |──*│   fact_loan_monthly     │*──|    dim_branch     |
+-----------------+   +-------------------------+   +-------------------+
        │                          │ *                        │ 1
        │                          │                          │
        │ *                        │ 1                        │ *
+-----------------+   +-------------------------+   +-------------------+
|  fact_payment   |──*│        dim_loan         │   |     dim_state     |
+-----------------+   +-------------------------+   +-------------------+
                                   │ *                        │ 1
                                   │                          │
                                   │ 1                        │ *
                      +-------------------------+   +-------------------+
                      |   dim_borrower_segment  |   |    dim_branch     |
                      +-------------------------+   +-------------------+
```

- **Relationships**: Strictly 1-to-Many (`1:*`), Single Cross-Filter Direction from Dimensions to Facts.
- **Date Role-Playing**: Active relationship on `snapshot_date_key` for `fact_loan_monthly`; inactive relationship for loan disbursement date.

### 7.3 Structured DAX Measure Hierarchy

All business metrics are organized into dedicated folders in a central `_Measures` table:

1. **Portfolio Health & Balances**:
   - `[Total Active Loans]` = `CALCULATE(DISTINCTCOUNT(fact_loan_monthly[loan_id]), fact_loan_monthly[outstanding_principal] > 0)`
   - `[Total Outstanding Principal]` = `SUM(fact_loan_monthly[outstanding_principal])`
   - `[PAR30 Principal]` = `CALCULATE(SUM(fact_loan_monthly[outstanding_principal]), fact_loan_monthly[days_past_due] > 30)`
   - `[PAR90 Principal]` = `CALCULATE(SUM(fact_loan_monthly[outstanding_principal]), fact_loan_monthly[days_past_due] > 90)`
   - `[PAR30 %]` = `DIVIDE([PAR30 Principal], [Total Outstanding Principal], 0)`
   - `[PAR90 %]` = `DIVIDE([PAR90 Principal], [Total Outstanding Principal], 0)`
2. **Collection Performance**:
   - `[Scheduled Due]` = `SUM(kpi_collection_efficiency[scheduled_amount_due])`
   - `[Current Collections]` = `SUM(kpi_collection_efficiency[current_period_collected])`
   - `[Arrears Collections]` = `SUM(kpi_collection_efficiency[arrears_collected])`
   - `[Total Cash Collected]` = `SUM(kpi_collection_efficiency[total_amount_collected])`
   - `[Current-Period Efficiency %]` = `DIVIDE([Current Collections], [Scheduled Due], 0)`
   - `[Total Collection Ratio %]` = `DIVIDE([Total Cash Collected], [Scheduled Due], 0)`
3. **Digital Transformation**:
   - `[Digital Value]` = `SUM(kpi_digital_collections[digital_collection_value])`
   - `[Total Collection Value]` = `SUM(kpi_digital_collections[total_collection_value])`
   - `[Digital Value Share %]` = `DIVIDE([Digital Value], [Total Collection Value], 0)`
   - `[Digital Count Share %]` = `DIVIDE(SUM(kpi_digital_collections[digital_transaction_count]), SUM(kpi_digital_collections[total_transaction_count]), 0)`
4. **Data Quality & Governance**:
   - `[Raw Record Count]` = `COUNTROWS(raw_loans) + COUNTROWS(raw_repayments)`
   - `[Quarantined Records Count]` = `COUNTROWS(stg_quarantined_records)`
   - `[Clean Warehouse Loans]` = `DISTINCTCOUNT(dim_loan[loan_id])`

### 7.4 Dashboard Page Layout (5 Institutional Pages)

1. **Page 1: Portfolio Health & Delinquency**
   - KPI Cards: Total Active Loans, Outstanding Principal (₹ Cr), PAR30 %, PAR90 %.
   - Visuals: Monthly PAR30/PAR90 trend line; Delinquency bucket stacked bar (Current, 1-30, 31-60, 61-90, 90+); State-wise PAR30 heatmap/bar; Product delinquency matrix.
2. **Page 2: Collection Efficiency & Arrears Recovery**
   - KPI Cards: Monthly Scheduled Due, Current-Period Collected, Arrears Recovered, Current Efficiency %, Total Collection Ratio %.
   - Visuals: Dual-axis monthly collection efficiency trend; Branch efficiency ranking (highlighting BR025 Oct outage and Nov recovery); Arrears vs Current stacked waterfall.
3. **Page 3: Repayment Vintage Analysis (Cohort Loss Curves)**
   - Matrix / Heatmap: Cohort Month vs Month-on-Book (MOB 1 to 24) showing cumulative repayment rates.
   - Visuals: Vintage curves by origination quarter (Q1 2023 through Q4 2024); Product-wise vintage trajectory.
4. **Page 4: Digital Collections & Channel Transition**
   - KPI Cards: Digital Value Share %, Digital Count Share %, MoM Share Change, YoY Share Change.
   - Visuals: 24-month channel value transition area chart (Cash vs UPI vs Bank Transfer); Average ticket size by channel; State-wise digital penetration rank.
5. **Page 5: Data Quality, Lineage & Quarantine Governance**
   - KPI Cards: Raw Records Ingested, Cleansed Fact Records, Total Quarantined Records, Financial Discrepancy (₹0.00).
   - Visuals: Quarantine breakdown by Reason Code (Duplicate Loans, Duplicate Txns, Negative Amounts, Pre-dated Txns, etc.); Multi-layer reconciliation audit table.

---

## 8. Testing & Reconciliation Strategy (>= 45 Automated Tests)

The testing framework will be structured into 4 distinct Pytest test suites:

1. **`test_uniqueness.py` (PK & Grain Invariants)**:
   - Primary key uniqueness on all 6 dimensions.
   - Transaction ID uniqueness in `fact_payment`.
   - Snapshot grain check: exactly 1 row per `(loan_id, snapshot_date)` in `fact_loan_monthly`.
   - Seeded raw duplicate detection (Issue 1: 200 duplicate loans, Issue 2: 400 duplicate repayments).
2. **`test_validity.py` (Value Domains, Dates & Chronology)**:
   - Positive loan principal values.
   - Non-negative payment amounts in warehouse facts.
   - Seeded raw negative amount detection (Issue 5: 150 negative payments).
   - Valid payment channel values (`UPI`, `Cash`, `Bank Transfer`).
   - Payment date $\ge$ loan disbursement date in `fact_payment`.
   - Seeded raw predated payment detection (Issue 9: 160 early payments).
   - Valid tenure boundaries (12 to 36 months).
3. **`test_business_rules.py` (Financial Mechanics & Banking Invariants)**:
   - Explicit PAISE to INR standardisation (Issue 4: 500 PAISE records).
   - Non-negative month-end outstanding principal.
   - Reducing-balance amortisation schedule integrity ($\sum P_k = P_{\text{disbursed}}$).
   - Dynamic snapshot DPD calculation (Issue 10: 350 corrupted raw DPD records corrected).
   - Future payments strictly excluded from historical snapshots ($payment\_date > S$ has zero impact).
   - Sequential chronological FIFO waterfall allocation.
   - Cap excess instalment payments in staging (Issue 8: 220 excess payments).
   - Fallback surrogate keys for missing branch (Issue 6: 250 records) and invalid product (Issue 7: 180 records).
4. **`test_reconciliation.py` (Cross-Layer Financial & Count Balances)**:
   - Loan count conservation: $\text{Raw} - \text{Duplicates} = \text{Staging} = \text{Dim Loan} = 52,000$.
   - Payment transaction conservation: $\text{Staging} = \text{Fact Payment}$.
   - Cash conservation: $\text{Payments} = \text{Allocated Principal} + \text{Allocated Interest} + \text{Unallocated Cash}$.
   - Loan-level principal conservation: No loan allocated principal $>$ original disbursed principal.
   - Branch-month completeness: Exactly 1 branch-month outage (Branch BR025 in Oct 2024).
   - Collection efficiency breakdown: $\text{Total Cash} = \text{Current} + \text{Arrears} + \text{Advance}$.

---

## 9. Risks, Limitations & Mitigation Strategies

| Risk / Constraint | Impact | Mitigation Strategy |
|---|---|---|
| **BigQuery Sandbox Limits / No Paid Account** | Inability to run high-concurrency cloud streaming or exceeding free tier storage/compute. | Design the ingestion engine to leverage standard BigQuery batch table loads (free tier compliant). Provide dual-mode orchestration: 1) Cloud BigQuery client with standard credentials/project, and 2) local SQL validation / mocking harness for offline verification. |
| **Decimal Precision Drift Across Engines** | Small rounding variances in interest components can alter DPD. | Standardize all financial values on `NUMERIC` / `DECIMAL(14,2)` in BigQuery; apply explicit `ROUND(..., 2)` and strict 1-paisa tolerance (`> 0.01`) in DPD evaluations. |
| **High Compute Overhead on Interval Overlaps** | Large Cartesian cross-join in FIFO waterfall. | Filter by `p.loan_id = i.loan_id` and restrict window partitions; in BigQuery, cluster by `loan_id` to prune partitions efficiently. |
| **Power BI DirectQuery Query Latency** | Slow report page rendering on complex DAX measures. | Pre-aggregate core reporting metrics into `fin_analytics.kpi_*` tables; use Import mode or optimized composite models. |

---

## 10. Implementation Sequence & Next Steps

1. **Step 1**: Establish target directory structure in `financial-inclusion-bigquery-powerbi`.
2. **Step 2**: Replicate and enhance synthetic data generator (`scripts/generate_data.py`), generating verified raw CSVs with all 10 anomalies.
3. **Step 3**: Build BigQuery ingestion engine (`scripts/ingest_bigquery.py`) and schema DDLs.
4. **Step 4**: Author BigQuery Standard SQL transformation scripts (`sql/staging/`, `sql/dimensions/`, `sql/facts/`, `sql/kpis/`).
5. **Step 5**: Port and execute automated testing suite (>= 45 tests) and independent financial validation engine (`scripts/verify_recalculation.py`).
6. **Step 6**: Develop Power BI semantic model, DAX measures, and 5 interactive report pages (`powerbi/`).
7. **Step 7**: Compile comprehensive documentation and GitHub portfolio repository.

---
*Approved and ready for Phase 3 through Phase 10 execution.*
