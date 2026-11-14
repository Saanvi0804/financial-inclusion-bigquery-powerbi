# Seeded Data Quality Anomalies Registry & Remediation Architecture

To demonstrate enterprise data engineering, quality firewalling, and robust warehouse resilience, 10 deliberate data defects and operational anomalies were injected into the synthetic source datasets.

This document catalogues all 10 anomalies, their financial risks, exact detection SQL queries, quarantine isolation mechanisms, and cleaned warehouse resolutions.

---

## 1. Complete Seeded Issues Registry

| Issue # | Anomaly Description | Target Raw Table | Injected Count | Financial / Analytical Impact if Unhandled | Remediation & Warehouse Handling |
|---|---|---|---|---|---|
| **Issue 1** | Duplicate Loan Contracts | `fin_raw.raw_loans` | **200 duplicate rows** | Overstates active loan count and inflates portfolio principal | Window deduplication `ROW_NUMBER() OVER (PARTITION BY loan_id)` in `stg_loans`. Dupes logged to `stg_quarantined_records`. |
| **Issue 2** | Duplicate Payment Receipts | `fin_raw.raw_repayments` | **398 - 400 duplicates** | Artificial cash inflation; duplicate credits to borrower ledger | Deduplicated via `ROW_NUMBER() OVER (PARTITION BY transaction_id)` in `stg_repayments`. Logged to quarantine. |
| **Issue 3** | Branch Collection Outage | `fin_raw.raw_repayments` | **Branch BR025 (Oct 2024)** | 1,013 omitted payments; artificially collapses collection efficiency to 0% | Preserved in raw/clean data as a true operational incident. Handled smoothly without pipeline failure. |
| **Issue 4** | Currency Unit Mismatch (PAISE) | `fin_raw.raw_repayments` | **500 records** (`unit='PAISE'`) | 100x cash inflation if treated as INR (₹1,232,540 vs ₹1,232.54) | Explicit conditional conversion `CASE WHEN unit = 'PAISE' THEN amount / 100.0 ELSE amount END` applied exactly once in staging. |
| **Issue 5** | Negative Payment Amounts | `fin_raw.raw_repayments` | **150 records** | Negative cash flows; corrupts collection totals and DPD tracking | Strict quarantine firewall rejects negative amounts into `stg_quarantined_records`. Zero negative values in warehouse. |
| **Issue 6** | Pre-dated Repayments | `fin_raw.raw_repayments` | **160 records** | Chronological violation (repayments received before loan disbursement) | Identified by comparing `payment_date < disbursement_date`. Quarantined in `stg_quarantined_records`. |
| **Issue 7** | Future-dated Repayments | `fin_raw.raw_repayments` | **50 records** | Payments dated beyond operational simulation cut-off | Quarantined in `stg_quarantined_records`. |
| **Issue 8** | Excess Instalment Payments | `fin_raw.raw_instalments` | **220 records** (> 2x dues) | Violates instalment amortization schedule invariants | In `stg_instalments`, `amount_paid` capped at `amount_due`. Excess unallocated amounts isolated in `stg_quarantined_records`. |
| **Issue 9** | Corrupted Static DPD | `fin_raw.raw_instalments` | **350 records** (corrupted 0 DPD) | Masks chronic delinquency; understates PAR30 and NPA | Raw static DPD discarded. BigQuery dynamically recalculates point-in-time DPD in `fact_loan_monthly`. |
| **Issue 10** | Unmapped Foreign Keys | `fin_raw.raw_loans` | **250 Null Branches, 180 Invalid Products** | Referential integrity failures; missing dimensional joins | Fallback surrogate keys (`branch_key = -1`, `product_key = -1`) assigned to guarantee zero orphan facts. Defective records logged to quarantine. |

---

## 2. Detailed Detection Queries & Verification Evidence

### Issue 1: Duplicate Loan Contracts
- **Detection Query**:
```sql
SELECT loan_id, COUNT(*) AS occurrences
FROM `fin_raw.raw_loans`
GROUP BY loan_id
HAVING COUNT(*) > 1;
```
- **Verification**: Exactly 200 duplicate records detected. `fin_staging.stg_loans` contains exactly 52,000 distinct loans.

### Issue 2: Duplicate Payment Transactions
- **Detection Query**:
```sql
SELECT transaction_id, COUNT(*) AS occurrences
FROM `fin_raw.raw_repayments`
GROUP BY transaction_id
HAVING COUNT(*) > 1;
```
- **Verification**: 398 distinct transaction IDs duplicated (400 duplicate records total). `fin_warehouse.fact_payment` contains strictly unique transaction IDs.

### Issue 3: Collection Outage at Branch BR025 (October 2024)
- **Detection Query**:
```sql
SELECT 
    l.branch_id,
    FORMAT_DATE('%Y-%m', r.payment_date) AS yr_mo,
    COUNT(*) AS txn_count
FROM `fin_staging.stg_repayments` r
JOIN `fin_staging.stg_loans` l ON r.loan_id = l.loan_id
WHERE l.branch_id = 'BR025' AND r.payment_date BETWEEN '2024-09-01' AND '2024-11-30'
GROUP BY 1, 2
ORDER BY 2;
```
- **Result**:
  - `2024-09`: 1,002 transactions
  - `2024-10`: **0 transactions** (outage window)
  - `2024-11`: 1,072 transactions (recovery window)

### Issue 4: Paise Identification & Single Normalisation
- **Detection Query**:
```sql
SELECT 
    COUNT(*) AS paise_txns,
    MIN(payment_amount) AS min_paise,
    MAX(payment_amount) AS max_paise
FROM `fin_raw.raw_repayments`
WHERE UPPER(TRIM(amount_unit)) = 'PAISE';
```
- **Verification**: 500 records identified. Converted to INR in staging (`payment_amount = raw_amount / 100.0`). Standardised unit set to `'INR'`.

### Issue 5: Negative Payment Amounts
- **Detection Query**:
```sql
SELECT COUNT(*) FROM `fin_raw.raw_repayments` WHERE payment_amount < 0;
```
- **Verification**: Exactly 150 negative payments detected and rejected into `stg_quarantined_records`. `fact_payment` contains 0 negative amounts.

### Issue 6: Pre-dated Payments Before Disbursement
- **Detection Query**:
```sql
SELECT COUNT(*) 
FROM `fin_raw.raw_repayments` r
JOIN `fin_raw.raw_loans` l ON r.loan_id = l.loan_id
WHERE CAST(r.payment_date AS DATE) < CAST(l.disbursement_date AS DATE);
```
- **Verification**: Exactly 160 pre-dated transactions detected and quarantined.

### Issue 8: Excess Instalment Payments
- **Detection Query**:
```sql
SELECT COUNT(*) FROM `fin_raw.raw_instalments` WHERE amount_paid > (amount_due * 2.0);
```
- **Verification**: Exactly 220 records detected. Quarantined under reason `EXCESS_INSTALMENT_PAYMENT`.

### Issue 9 & 10: Corrupted DPD and Quarantine Completeness
- **Quarantine Summary Query**:
```sql
SELECT reason_code, COUNT(*) AS count
FROM `fin_staging.stg_quarantined_records`
GROUP BY reason_code
ORDER BY count DESC;
```
- **Audit Result**:
  1. `DUPLICATE_TXN_ID`: 398
  2. `MISSING_BRANCH_ID`: 250
  3. `EXCESS_INSTALMENT_PAYMENT`: 220
  4. `DUPLICATE_LOAN_ID`: 200
  5. `INVALID_PRODUCT_KEY`: 180
  6. `PAYMENT_BEFORE_DISBURSEMENT`: 160
  7. `NEGATIVE_PAYMENT_AMOUNT`: 150
  8. `CORRUPTED_ZERO_DPD`: 123
  - **Total Quarantined**: **1,681 records**
