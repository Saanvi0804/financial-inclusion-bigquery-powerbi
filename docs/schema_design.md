# Star Schema Design & Data Warehouse Dimensional Model

This document outlines the Kimball star schema dimensional architecture implemented in the analytical warehouse (`fin_warehouse`), executed locally via DuckDB (`data/warehouse/financial_inclusion_bigquery.duckdb`) using BigQuery-compatible Standard SQL models. Power BI consumes curated CSV extracts produced by this pipeline.

---

## 1. Dimensional Model Overview

```mermaid
erDiagram
    dim_date {
        INT64 date_key PK
        DATE full_date
        INT64 year
        INT64 quarter
        INT64 month
        STRING month_name
        STRING year_month
        STRING financial_year
        STRING financial_quarter
        BOOL is_month_end
    }

    dim_state {
        INT64 state_key PK
        STRING state_id
        STRING state_name
        STRING region
    }

    dim_branch {
        INT64 branch_key PK
        STRING branch_id
        STRING branch_name
        STRING state_id
        STRING location_type
    }

    dim_product {
        INT64 product_key PK
        STRING product_id
        STRING product_name
        STRING product_category
        STRING interest_calc_method
    }

    dim_borrower_segment {
        INT64 borrower_segment_key PK
        STRING borrower_segment
        STRING income_band
        STRING location_type
        STRING occupation_category
    }

    dim_loan {
        INT64 loan_key PK
        STRING loan_id
        STRING borrower_id
        STRING branch_id
        STRING state_id
        STRING product_id
        DATE disbursement_date
        NUMERIC principal_amount
        NUMERIC annual_interest_rate
        INT64 tenure_months
        STRING loan_status
    }

    fact_payment {
        INT64 payment_key PK
        STRING transaction_id
        INT64 loan_key FK
        DATE payment_date
        INT64 payment_date_key FK
        INT64 branch_key FK
        INT64 state_key FK
        INT64 product_key FK
        INT64 borrower_segment_key FK
        NUMERIC payment_amount
        STRING payment_channel
    }

    fact_instalment_allocation {
        INT64 allocation_key PK
        STRING transaction_id
        STRING instalment_id
        INT64 loan_key FK
        DATE payment_date
        INT64 payment_date_key FK
        DATE due_date
        INT64 due_date_key FK
        INT64 branch_key FK
        INT64 state_key FK
        INT64 product_key FK
        INT64 borrower_segment_key FK
        INT64 instalment_number
        NUMERIC allocated_amount
        NUMERIC allocated_principal
        NUMERIC allocated_interest
        STRING payment_channel
    }

    fact_loan_monthly {
        INT64 snapshot_key PK
        STRING loan_id
        INT64 loan_key FK
        DATE snapshot_date
        INT64 snapshot_date_key FK
        INT64 branch_key FK
        INT64 state_key FK
        INT64 product_key FK
        INT64 borrower_segment_key FK
        NUMERIC outstanding_principal
        INT64 instalments_due
        INT64 instalments_paid
        NUMERIC amount_due
        NUMERIC amount_paid
        INT64 days_past_due
        NUMERIC overdue_amount
    }

    dim_date ||--o{ fact_payment : "payment_date_key"
    dim_branch ||--o{ fact_payment : "branch_key"
    dim_state ||--o{ fact_payment : "state_key"
    dim_product ||--o{ fact_payment : "product_key"
    dim_borrower_segment ||--o{ fact_payment : "borrower_segment_key"
    dim_loan ||--o{ fact_payment : "loan_key"

    dim_date ||--o{ fact_instalment_allocation : "payment_date_key"
    dim_branch ||--o{ fact_instalment_allocation : "branch_key"
    dim_state ||--o{ fact_instalment_allocation : "state_key"
    dim_product ||--o{ fact_instalment_allocation : "product_key"
    dim_borrower_segment ||--o{ fact_instalment_allocation : "borrower_segment_key"
    dim_loan ||--o{ fact_instalment_allocation : "loan_key"

    dim_date ||--o{ fact_loan_monthly : "snapshot_date_key"
    dim_branch ||--o{ fact_loan_monthly : "branch_key"
    dim_state ||--o{ fact_loan_monthly : "state_key"
    dim_product ||--o{ fact_loan_monthly : "product_key"
    dim_borrower_segment ||--o{ fact_loan_monthly : "borrower_segment_key"
    dim_loan ||--o{ fact_loan_monthly : "loan_key"
```

---

## 2. Dimension Tables Specification

### 2.1 `dim_date`
- **Grain**: Exactly one row per calendar day from 2021-01-01 to 2025-12-31 (1,826 days).
- **Primary Key**: `date_key` (Format `YYYYMMDD`, e.g. `20241231`).
- **Special Attributes**: Indian financial year (April 1 to March 31, e.g. `FY2024-25`), `financial_quarter`, `is_month_end` boolean.

### 2.2 `dim_state`
- **Grain**: One row per Indian state in the portfolio operational footprint plus fallback row.
- **Primary Key**: `state_key` (Surrogate integer).
- **Business Key**: `state_id` (e.g. `ST_UP`, `ST_MH`, `ST_BR`).
- **Row Count**: 11 rows (10 operational states + 1 fallback `-1`).

### 2.3 `dim_branch`
- **Grain**: One row per microfinance branch plus fallback row.
- **Primary Key**: `branch_key` (Surrogate integer).
- **Business Key**: `branch_id` (e.g. `BR001` through `BR036`).
- **Row Count**: 37 rows (36 operating branches + 1 fallback `-1`).

### 2.4 `dim_product`
- **Grain**: One row per financial inclusion loan product plus fallback row.
- **Primary Key**: `product_key` (Surrogate integer).
- **Business Key**: `product_id` (`PRD_MFI`, `PRD_AGR`, `PRD_MSME`, `PRD_EDU`, `PRD_EMG`).
- **Row Count**: 6 rows (5 products + 1 fallback `-1`).

### 2.5 `dim_borrower_segment`
- **Grain**: Unique combination of socioeconomic cohort attributes: `borrower_segment`, `income_band`, `location_type`, and `occupation_category`.
- **Primary Key**: `borrower_segment_key` (Surrogate integer).
- **Row Count**: 301 rows.

### 2.6 `dim_loan`
- **Grain**: Exactly one row per unique contracted loan facility.
- **Primary Key**: `loan_key` (Surrogate integer).
- **Business Key**: `loan_id` (e.g. `LN000001` through `LN052000`).
- **Row Count**: 52,001 rows (52,000 valid loans + 1 fallback row).

---

## 3. Fact Tables Specification

### 3.1 `fact_payment` (Transaction Fact)
- **Grain**: Exactly one row per received repayment transaction.
- **Primary Key**: `payment_key` (Surrogate integer).
- **Business Key**: `transaction_id` (e.g. `TXN00000001`).
- **Financial Measures**:
  - `payment_amount` (`NUMERIC` in INR): Exact payment amount received.
- **Row Count**: 533,147 rows.
- **Reconciliation Total**: ₹2,414,272,241.51.

### 3.2 `fact_instalment_allocation` (Allocation Sub-Fact)
- **Grain**: Exactly one row per payment allocation leg against a specific scheduled instalment.
- **Primary Key**: `allocation_key` (Surrogate integer).
- **Foreign Keys**: `loan_key`, `payment_date_key`, `due_date_key`, `branch_key`, `state_key`, `product_key`, `borrower_segment_key`.
- **Financial Measures**:
  - `allocated_amount` (`NUMERIC` in INR): Portioned cash applied to instalment.
  - `allocated_principal` (`NUMERIC` in INR): Principal component paid.
  - `allocated_interest` (`NUMERIC` in INR): Interest component paid.
- **Invariant**: `allocated_amount = allocated_principal + allocated_interest`.
- **Row Count**: 723,600 rows.
- **Reconciliation Total**: ₹2,414,272,241.51 (100.0% conservation with `fact_payment`).

### 3.3 `fact_loan_monthly` (Periodic Snapshot Fact)
- **Grain**: Exactly one row per loan per month-end reporting snapshot date.
- **Primary Key**: `snapshot_key` (Surrogate integer) / Composite Key `(loan_id, snapshot_date_key)`.
- **Temporal Coverage**: 24 calendar month-ends (2023-01-31 to 2024-12-31).
- **Financial Measures**:
  - `outstanding_principal` (`NUMERIC`): Point-in-time remaining principal balance calculated from initial principal minus cumulative principal allocations received on or before snapshot date.
  - `amount_due` (`NUMERIC`): Cumulative dues scheduled on or before snapshot date.
  - `amount_paid` (`NUMERIC`): Cumulative payments allocated on or before snapshot date.
  - `days_past_due` (`INT64`): Dynamic days elapsed since the oldest unsatisfied instalment due on or before snapshot date (excluding future dues and with $\le$ 1-paisa residual threshold).
  - `overdue_amount` (`NUMERIC`): Overdue arrears as of snapshot date.
- **Row Count**: 651,542 rows.
