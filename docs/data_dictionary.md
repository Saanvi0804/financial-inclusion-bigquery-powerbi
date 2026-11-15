# Enterprise Data Dictionary

This data dictionary provides a complete technical and business description of all tables and columns across the four warehouse schemas (`fin_raw`, `fin_staging`, `fin_warehouse`, and `fin_analytics`), executed locally in DuckDB using BigQuery-compatible Standard SQL.

---

## 1. Raw Layer (`fin_raw`)

### `raw_loans`
- **Description**: Raw landing table for originated loan contracts. Contains deliberate seeded duplicate records.
- **Grain**: One row per ingested record.

| Column | Data Type | Nullable | Description | Business Rules & Notes |
|---|---|---|---|---|
| `loan_id` | `STRING` | No | Loan identifier | Seeded with 200 duplicate records |
| `borrower_id` | `STRING` | No | Borrower identifier | Foreign key to `raw_borrowers` |
| `branch_id` | `STRING` | Yes | Originating branch ID | Contains 250 seeded NULL branch records |
| `state_id` | `STRING` | No | State code | e.g. `ST_UP`, `ST_MH`, `ST_BR` |
| `product_id` | `STRING` | No | Loan product code | Contains 180 invalid product codes (`PRD_INV`) |
| `disbursement_date` | `DATE` | No | Disbursement date | Ranging from 2023-01-01 to 2024-11-30 |
| `principal_amount` | `NUMERIC` | No | Principal disbursed | Between ₹10,000 and ₹300,000 |
| `annual_interest_rate` | `NUMERIC` | No | Annual interest rate | Stored as percentage (e.g. 18.0) |
| `tenure_months` | `INT64` | No | Loan tenure in months | 12, 18, 24, or 36 months |
| `loan_status` | `STRING` | No | Contract status | `Active`, `Closed`, `Defaulted`, `Written-Off` |
| `ingested_at` | `TIMESTAMP` | No | Ingestion timestamp | System generated metadata |
| `batch_run_id` | `STRING` | No | Batch UUID | Unique run ID |

### `raw_borrowers`
- **Description**: Raw landing table for borrower demographic and socioeconomic profiles.

| Column | Data Type | Nullable | Description |
|---|---|---|---|
| `borrower_id` | `STRING` | No | Unique borrower ID |
| `borrower_name` | `STRING` | No | Borrower full name |
| `gender` | `STRING` | No | Borrower gender (`Female`, `Male`) |
| `age` | `INT64` | No | Borrower age (18 to 65) |
| `borrower_segment` | `STRING` | No | Borrower category (e.g. `Women Self-Help Group`) |
| `income_band` | `STRING` | No | Income category (`Low`, `Lower-Middle`, `Middle`) |
| `location_type` | `STRING` | No | Residence type (`Rural`, `Semi-Urban`, `Urban`) |
| `occupation_category` | `STRING` | No | Economic occupation |
| `ingested_at` | `TIMESTAMP` | No | Ingestion timestamp |
| `batch_run_id` | `STRING` | No | Batch UUID |

### `raw_repayments`
- **Description**: Raw transaction stream of repayment receipts. Contains multiple seeded anomalies.

| Column | Data Type | Nullable | Description | Business Rules & Notes |
|---|---|---|---|---|
| `transaction_id` | `STRING` | No | Repayment receipt ID | Contains ~400 duplicate transaction IDs |
| `loan_id` | `STRING` | No | Loan reference | Links to `raw_loans` |
| `payment_date` | `DATE` | No | Receipt date | Contains 160 payments dated before loan disbursement |
| `payment_amount` | `NUMERIC` | No | Payment amount | Contains 150 negative amounts; 500 PAISE values |
| `amount_unit` | `STRING` | No | Currency unit | Explicitly tagged as `'INR'` or `'PAISE'` |
| `payment_channel` | `STRING` | No | Payment method | `'Cash'`, `'UPI'`, `'Bank_Transfer'` |
| `ingested_at` | `TIMESTAMP` | No | Ingestion timestamp | System generated |
| `batch_run_id` | `STRING` | No | Batch UUID | Unique run ID |

### `raw_instalments`
- **Description**: Contractual repayment schedule.

| Column | Data Type | Nullable | Description | Business Rules & Notes |
|---|---|---|---|---|
| `instalment_id` | `STRING` | No | Unique instalment ID | Format `INST_...` |
| `loan_id` | `STRING` | No | Loan reference | Links to `raw_loans` |
| `instalment_number` | `INT64` | No | Sequence number | 1 to $N$ |
| `due_date` | `DATE` | No | Contractual due date | Monthly due date |
| `opening_principal` | `NUMERIC` | No | Beginning balance | Amortisation balance |
| `amount_due` | `NUMERIC` | No | Scheduled instalment | EMI amount |
| `principal_component`| `NUMERIC` | No | Scheduled principal | Reduces outstanding balance |
| `interest_component` | `NUMERIC` | No | Scheduled interest | Monthly interest |
| `closing_principal` | `NUMERIC` | No | Ending balance | Expected closing balance |
| `amount_paid` | `NUMERIC` | No | Lifetime paid | Contains 220 seeded excess amounts (> 2x dues) |
| `days_past_due` | `INT64` | No | Static DPD in raw | Contains 350 seeded corrupted values (0 DPD despite arrears) |
| `ingested_at` | `TIMESTAMP` | No | Ingestion timestamp | System generated |
| `batch_run_id` | `STRING` | No | Batch UUID | Unique run ID |

---

## 2. Staging Layer (`fin_staging`)

### `stg_quarantined_records`
- **Description**: Quality firewall capturing rejected or quarantined source records.

| Column | Data Type | Nullable | Description |
|---|---|---|---|
| `quarantine_id` | `INT64` | No | Surrogate key |
| `batch_run_id` | `STRING` | No | Batch ingestion UUID |
| `quarantined_at` | `TIMESTAMP` | No | Timestamp of quarantine action |
| `source_table` | `STRING` | No | Origin table (`raw_repayments`, `raw_loans`, etc.) |
| `record_identifier` | `STRING` | No | Primary business key of quarantined record |
| `reason_code` | `STRING` | No | Defect classification (`NEGATIVE_PAYMENT_AMOUNT`, `PAYMENT_BEFORE_DISBURSEMENT`, `EXCESS_INSTALMENT_PAYMENT`, `CORRUPTED_ZERO_DPD`, `DUPLICATE_LOAN_ID`, `DUPLICATE_TXN_ID`, `MISSING_BRANCH_ID`, `INVALID_PRODUCT_KEY`) |
| `raw_payload` | `STRING` | No | Full JSON serialization of rejected row |

### `stg_loans`
- **Description**: Cleaned, deduplicated loan dimension source. Replaces missing branches and products with fallback tokens. 52,000 distinct loans.

### `stg_repayments`
- **Description**: Cleaned repayments stream. Filters negative, duplicate, and pre-dated payments. Normalises `amount_unit = 'PAISE'` by dividing by 100.0 exactly once. 533,147 transactions.

### `stg_instalment_allocation`
- **Description**: In-memory payment-to-instalment chronological FIFO waterfall table. 723,600 allocation legs.

---

## 3. Dimensional Warehouse Layer (`fin_warehouse`)

*(Detailed in `docs/schema_design.md`)*
- `dim_date`: 1,826 days (2021 to 2025).
- `dim_state`: 11 rows.
- `dim_branch`: 37 rows.
- `dim_product`: 6 rows.
- `dim_borrower_segment`: 301 socioeconomic combinations.
- `dim_loan`: 52,001 rows.
- `fact_payment`: 533,147 payment transactions (₹2,414,272,241.51).
- `fact_instalment_allocation`: 723,600 allocation legs (₹2,414,272,241.51).
- `fact_loan_monthly`: 651,542 month-end loan snapshots (24 calendar months).

---

## 4. Analytics & KPI Layer (`fin_analytics`)

### `kpi_portfolio_health`
- **Grain**: One row per `snapshot_date`, `state_name`, `branch_name`, `product_name`, `borrower_segment`.
- **Columns**: `total_active_loans`, `total_cumulative_loans`, `total_outstanding_principal`, `principal_current`, `principal_dpd_1_30`, `principal_dpd_31_60`, `principal_dpd_61_90`, `principal_dpd_90_plus`, `par30_principal`, `par90_principal`, `par30_pct`, `par90_pct`.

### `kpi_collection_efficiency`
- **Grain**: One row per `year_month`, `state_name`, `branch_name`, `product_name`.
- **Columns**: `scheduled_amount_due`, `current_period_collected`, `arrears_collected`, `advance_collected`, `total_amount_collected`, `current_period_efficiency_pct`, `total_collection_ratio_pct`, `collection_efficiency_pct`.

### `kpi_vintage_curves`
- **Grain**: One row per `cohort_month`, `product_name`, `month_on_book`.
- **Columns**: `total_cohort_loans`, `scheduled_due_mob`, `amount_paid_mob`, `cumulative_scheduled_due`, `cumulative_amount_paid`, `vintage_repayment_rate_pct`.

### `kpi_digital_collections`
- **Grain**: One row per `year_month`, `state_name`.
- **Columns**: `total_collection_value`, `total_transaction_count`, `digital_collection_value`, `digital_transaction_count`, `cash_collection_value`, `cash_transaction_count`, `upi_value`, `upi_count`, `bank_transfer_value`, `bank_transfer_count`, `avg_ticket_upi`, `avg_ticket_bank_transfer`, `avg_ticket_cash`, `avg_ticket_overall`, `digital_value_share_pct`, `digital_count_share_pct`, `mom_digital_value_share_pts`, `yoy_digital_value_share_pts`.
