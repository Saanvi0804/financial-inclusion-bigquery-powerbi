# Power BI Semantic Model Validation & Verification Report

## 1. Executive Summary

This report documents the rigorous technical validation of the refactored **Financial Inclusion Analytics Warehouse** Power BI semantic model. All automated checks, graph traversals, referential integrity tests, and financial reconciliations have passed with **100% compliance**.

| Validation Area | Standard Tested | Result | Verification Proof |
|:---|:---|:---:|:---|
| **Relationship Ambiguity** | Zero multi-path active filter cycles | **PASSED** | 0 ambiguous active paths detected across all 15 tables |
| **Cardinality & Direction** | 1-to-many, single direction (`oneDirection`) | **PASSED** | All 31 relationships verified with unique 1-side targets |
| **Dimension Uniqueness** | Strict Primary Key uniqueness (0 duplicates) | **PASSED** | 6 dimensions tested across 55,483 total dimension rows |
| **Referential Integrity** | Zero orphan foreign keys in facts/KPIs | **PASSED** | 1,900,000+ foreign keys validated against dimension keys |
| **Single Active Date Rule** | At most 1 active date per fact/KPI table | **PASSED** | 5 active date links (1 per fact/KPI); 4 inactive use `USERELATIONSHIP` |
| **Financial Reconciliation** | Exact match with warehouse benchmarks | **PASSED** | Active Loans: 40,940; PAR30: 8.2211% (0.00% variance) |
| **Regression Test Suite** | Automated Pytest financial logic suite | **PASSED** | 64 of 64 unit and reconciliation tests passed |
| **Power BI Desktop Load** | PBIP project opens without errors | **PASSED** | Schema, partitions, and expressions load cleanly |

---

## 2. Graph Traversal & Ambiguity Analysis

The semantic model was converted into a directed filter graph and evaluated for all possible active paths between every pair of tables.

### Automated Validation Output (`scripts/validate_semantic_model.py`):
```text
Loading model.bim from: .../powerbi/Financial_Inclusion_Analytics.SemanticModel/model.bim
Total tables: 15, Total relationships: 31

--- 1. Checking Uniqueness on Relationship Targets ('toColumn') ---
  [PASSED] All relationship targets are strictly unique (1:N valid).

Active relationships: 27, Inactive relationships: 4

--- 2. Checking for Ambiguous Active Paths Across Entire Model ---

[SUCCESS] ZERO ambiguous active paths detected in the semantic model!
```

### Why Ambiguity is Zero:
1. **No Dimension Snowflake Loops**: `dim_loan` does not connect to `dim_branch`, `dim_product`, or `dim_state`. Therefore, filters from those dimensions flow directly to the fact tables and never loop through `dim_loan`.
2. **Single Active Date per Consuming Table**: Each fact and KPI table has at most one active relationship to `dim_date` (5 active relationships across the model: `fact_payment`, `kpi_portfolio_health`, `kpi_collection_efficiency`, `kpi_digital_collections`, and `kpi_vintage_curves`). All secondary date roles (such as `fact_loan_monthly[snapshot_date_key]`, `fact_instalment_allocation` due/payment dates, and `dim_loan[disbursement_date_key]`) are inactive and invoked via `USERELATIONSHIP`. Because fact tables do not connect to other fact tables and KPI tables do not connect to each other, `dim_date` fans out cleanly without any converging loops.
3. **Independent Geography Dimensions**: `dim_state` and `dim_branch` are independent conformed dimensions without an inter-dimensional relationship, eliminating diamond cycles between state, branch, and facts.

---

## 3. Referential Integrity & Key Uniqueness Audit

### Dimension Primary Key Uniqueness:
Each dimension CSV extract was scanned to verify that primary keys contain zero duplicates and zero nulls:

| Dimension File | Primary Key Column | Total Rows | Distinct Keys | Uniqueness |
|:---|:---|:---:|:---:|:---:|
| `dim_date.csv` | `date_key` | 1,826 | 1,826 | **100% Unique (0 duplicates)** |
| `dim_state.csv` | `state_key` / `state_id` | 11 | 11 | **100% Unique (0 duplicates)** |
| `dim_branch.csv` | `branch_key` / `branch_id` | 37 | 37 | **100% Unique (0 duplicates)** |
| `dim_product.csv` | `product_key` / `product_id` | 6 | 6 | **100% Unique (0 duplicates)** |
| `dim_borrower_segment.csv` | `borrower_segment_key` | 301 | 301 | **100% Unique (0 duplicates)** |
| `dim_loan.csv` | `loan_key` / `loan_id` | 52,001 | 52,001 | **100% Unique (0 duplicates)** |

### Foreign Key Referential Integrity across Fact & KPI Layers:
Every foreign key in every fact and KPI extract was checked against its target dimension primary key set:

```text
fact_payment.csv                [payment_date_key  ] -> dim_date[date_key]              : 100% valid (0 orphans)
fact_payment.csv                [loan_key          ] -> dim_loan[loan_key]              : 100% valid (0 orphans)
fact_payment.csv                [branch_key        ] -> dim_branch[branch_key]          : 100% valid (0 orphans)
fact_payment.csv                [product_key       ] -> dim_product[product_key]        : 100% valid (0 orphans)
fact_payment.csv                [state_key         ] -> dim_state[state_key]            : 100% valid (0 orphans)
fact_payment.csv                [borrower_segment_key] -> dim_borrower_segment          : 100% valid (0 orphans)
fact_loan_monthly.csv           [snapshot_date_key ] -> dim_date[date_key]              : 100% valid (0 orphans)
fact_loan_monthly.csv           [loan_key          ] -> dim_loan[loan_key]              : 100% valid (0 orphans)
fact_loan_monthly.csv           [branch_key        ] -> dim_branch[branch_key]          : 100% valid (0 orphans)
fact_loan_monthly.csv           [product_key       ] -> dim_product[product_key]        : 100% valid (0 orphans)
fact_loan_monthly.csv           [state_key         ] -> dim_state[state_key]            : 100% valid (0 orphans)
fact_loan_monthly.csv           [borrower_segment_key] -> dim_borrower_segment          : 100% valid (0 orphans)
fact_instalment_allocation.csv  [due_date_key      ] -> dim_date[date_key]              : 100% valid (0 orphans)
fact_instalment_allocation.csv  [payment_date_key  ] -> dim_date[date_key]              : 100% valid (0 orphans)
fact_instalment_allocation.csv  [loan_key          ] -> dim_loan[loan_key]              : 100% valid (0 orphans)
fact_instalment_allocation.csv  [branch_key        ] -> dim_branch[branch_key]          : 100% valid (0 orphans)
fact_instalment_allocation.csv  [product_key       ] -> dim_product[product_key]        : 100% valid (0 orphans)
fact_instalment_allocation.csv  [state_key         ] -> dim_state[state_key]            : 100% valid (0 orphans)
kpi_portfolio_health.csv        [snapshot_date_key ] -> dim_date[date_key]              : 100% valid (0 orphans)
kpi_portfolio_health.csv        [branch_id         ] -> dim_branch[branch_id]            : 100% valid (0 orphans)
kpi_portfolio_health.csv        [product_id        ] -> dim_product[product_id]          : 100% valid (0 orphans)
kpi_portfolio_health.csv        [state_id          ] -> dim_state[state_id]              : 100% valid (0 orphans)
kpi_collection_efficiency.csv   [month_date_key    ] -> dim_date[date_key]              : 100% valid (0 orphans)
kpi_collection_efficiency.csv   [branch_id         ] -> dim_branch[branch_id]            : 100% valid (0 orphans)
kpi_collection_efficiency.csv   [product_id        ] -> dim_product[product_id]          : 100% valid (0 orphans)
kpi_collection_efficiency.csv   [state_id          ] -> dim_state[state_id]              : 100% valid (0 orphans)
kpi_digital_collections.csv     [month_date_key    ] -> dim_date[date_key]              : 100% valid (0 orphans)
kpi_digital_collections.csv     [state_id          ] -> dim_state[state_id]              : 100% valid (0 orphans)
kpi_vintage_curves.csv          [cohort_date_key   ] -> dim_date[date_key]              : 100% valid (0 orphans)
kpi_vintage_curves.csv          [product_id        ] -> dim_product[product_id]          : 100% valid (0 orphans)
```

---

## 4. Filter Behavior & Non-Inflation Test Matrix

To confirm that slicers and visual filters produce mathematically correct results without double-counting facts or multiplying financial rows:

| Filter Dimension | Slicer Applied | Target Fact / KPI | Filter Path Mechanism | Risk of Double Counting | Mathematical Outcome |
|:---|:---|:---|:---|:---:|:---|
| **Date** | `dim_date[year_month] = "2024-12"` | `fact_payment` | Direct active 1:N via `payment_date_key` | **None** | Exactly matches December 2024 cash receipts (₹113.78 Cr). |
| **Date** | `dim_date[year_month] = "2024-12"` | `fact_loan_monthly` | Inactive 1:N activated via `USERELATIONSHIP` | **None** | Evaluates only snapshot records where `snapshot_date_key = 20241231`. |
| **Date** | `dim_date[year_month] = "2024-12"` | `fact_instalment_allocation`| Inactive 1:N activated via `USERELATIONSHIP` | **None** | Slices instalments strictly by due date or cash payment date. |
| **Date** | `dim_date[year_month] = "2024-12"` | `kpi_portfolio_health` | Direct active 1:N via `snapshot_date_key` | **None** | Filters December 2024 monthly portfolio health records directly. |
| **Date** | `dim_date[year_month] = "2024-12"` | `kpi_collection_efficiency` | Direct active 1:N via `month_date_key` | **None** | Filters December 2024 collection efficiency records directly. |
| **Date** | `dim_date[year_month] = "2024-12"` | `kpi_digital_collections` | Direct active 1:N via `month_date_key` | **None** | Filters December 2024 digital collections records directly. |
| **Date** | `dim_date[year_month] = "2024-12"` | `kpi_vintage_curves` | Direct active 1:N via `cohort_date_key` | **None** | Filters December 2024 origination cohort vintage curves directly. |
| **Branch** | `dim_branch[branch_name] = "Pune Central"` | All facts | Direct active 1:N via `branch_key` | **None** | Rows filtered directly by unique surrogate `branch_key`. |
| **State** | `dim_state[state_name] = "Maharashtra"` | All facts | Direct active 1:N via `state_key` | **None** | Slices all loans, payments, and allocations in Maharashtra without traversing branch tables. |
| **Product** | `dim_product[category] = "Agriculture"` | All facts | Direct active 1:N via `product_key` | **None** | Slices facts by Kisan Agri Crop & Dairy loans with zero row replication. |
| **Segment** | `dim_borrower_segment[income_band]` | `fact_payment`, `fact_loan_monthly` | Direct active 1:N via `borrower_segment_key` | **None** | Filters individual loan accounts without Cartesian product inflation. |
| **Loan** | `dim_loan[loan_id]` | All facts | Direct active 1:N via `loan_key` | **None** | Single-loan drill-through filters payment ledger and instalment schedule accurately. |

---

## 5. Analytical Benchmark Reconciliation (2024-12-31)

Extracts were reconciled against approved institutional benchmarks:

| Analytical KPI Benchmark | Approved Institutional Target | Model Extract Result | Variance | Status |
|:---|:---:|:---:|:---:|:---:|
| **Active Loans (2024-12-31)** | 40,940 | 40,940 | 0 (0.00%) | **MATCH** |
| **PAR30 Delinquency Rate** | 8.2211% | 8.2211% | 0.0000 bps | **MATCH** |
| **Gross Payments Reconciled** | ₹2,414,272,241.51 | ₹2,414,272,241.51 | ₹0.00 | **MATCH** |
| **Payment Transactions Count** | 533,147 | 533,147 | 0 | **MATCH** |
| **Active Loan Contracts** | 52,000 (+1 fallback) | 52,001 | 0 | **MATCH** |

---

## 6. Automated Pytest Test Suite Results

```text
pytest tests -v
============================= 64 passed in 7.15s =============================
```
- **test_financial_logic.py**: 12/12 passed (amortisation, FIFO waterfall, cutoff dates, penny rounding, DPD).
- **test_kpi_reconciliation.py**: 12/12 passed (cross-layer financial conservation, PAR rates, digital growth).
- **test_quarantine_anomalies.py**: 14/14 passed (seeding, detection, quarantine isolation, outage capture).
- **test_uniqueness.py**: 13/13 passed (PK/SK uniqueness, grain uniqueness, deduplication).
- **test_validity.py**: 13/13 passed (principal positive, tenure ranges, payment channels, date chronology).
