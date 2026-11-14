# Power BI Enterprise DAX Measure Catalogue

This catalogue defines all institutional DAX measures for the **Financial Inclusion Analytics Warehouse** Power BI model.
All measures are grouped in a dedicated `_Measures` table or associated fact tables with standardized Indian currency formatting (`₹ #,##0.00 Cr`, `₹ #,##0.00 L`, `₹ #,##0.00`), percentage formatting (`0.00%`), and integer counts.

---

## 1. Portfolio Health & Risk Measures

### `[Active Loans Count]`
- **Description**: Count of distinct active loans with outstanding principal as of the selected snapshot date (semi-additive).
- **DAX Formula**:
```dax
Active Loans Count = 
VAR MaxDate = MAX(fact_loan_monthly[snapshot_date_key])
RETURN
    CALCULATE(
        DISTINCTCOUNT(fact_loan_monthly[loan_key]),
        fact_loan_monthly[snapshot_date_key] = MaxDate,
        fact_loan_monthly[outstanding_principal] > 0
    )
```
- **Format**: `#,##0`

### `[Total Outstanding Principal]`
- **Description**: Gross remaining principal balance owed across active loans as of the latest selected snapshot.
- **DAX Formula**:
```dax
Total Outstanding Principal = 
VAR MaxDate = MAX(fact_loan_monthly[snapshot_date_key])
RETURN
    CALCULATE(
        SUM(fact_loan_monthly[outstanding_principal]),
        fact_loan_monthly[snapshot_date_key] = MaxDate
    )
```
- **Format**: `₹ #,##0.00` (or dynamic format string for Crores `₹ 0.00,, "Cr"`)

### `[Outstanding Principal (INR Cr)]`
- **Description**: Outstanding principal formatted in Crores (1 Cr = 10,000,000 INR) for executive KPI cards.
- **DAX Formula**:
```dax
Outstanding Principal (INR Cr) = 
DIVIDE([Total Outstanding Principal], 10000000, 0)
```
- **Format**: `₹ #,##0.00 "Cr"`

### `[PAR 30 Principal]`
- **Description**: Outstanding principal balance on loans having at least one overdue instalment past 30 days past due (DPD > 30).
- **DAX Formula**:
```dax
PAR 30 Principal = 
VAR MaxDate = MAX(fact_loan_monthly[snapshot_date_key])
RETURN
    CALCULATE(
        SUM(fact_loan_monthly[outstanding_principal]),
        fact_loan_monthly[snapshot_date_key] = MaxDate,
        fact_loan_monthly[days_past_due] > 30
    )
```
- **Format**: `₹ #,##0.00`

### `[PAR 30 %]`
- **Description**: Portfolio-at-Risk > 30 days ratio as a percentage of gross outstanding principal.
- **DAX Formula**:
```dax
PAR 30 % = 
DIVIDE(
    [PAR 30 Principal],
    [Total Outstanding Principal],
    0
)
```
- **Format**: `0.00%`

### `[PAR 90 Principal]`
- **Description**: Outstanding principal balance on non-performing loans (NPL / Gross NPA) with DPD > 90 days.
- **DAX Formula**:
```dax
PAR 90 Principal = 
VAR MaxDate = MAX(fact_loan_monthly[snapshot_date_key])
RETURN
    CALCULATE(
        SUM(fact_loan_monthly[outstanding_principal]),
        fact_loan_monthly[snapshot_date_key] = MaxDate,
        fact_loan_monthly[days_past_due] > 90
    )
```
- **Format**: `₹ #,##0.00`

### `[PAR 90 %]`
- **Description**: Non-performing asset (NPA / PAR90) ratio as a percentage of gross outstanding principal.
- **DAX Formula**:
```dax
PAR 90 % = 
DIVIDE(
    [PAR 90 Principal],
    [Total Outstanding Principal],
    0
)
```
- **Format**: `0.00%`

### `[Current Principal]`
- **Description**: Outstanding principal on non-delinquent loans (DPD = 0).
- **DAX Formula**:
```dax
Current Principal = 
VAR MaxDate = MAX(fact_loan_monthly[snapshot_date_key])
RETURN
    CALCULATE(
        SUM(fact_loan_monthly[outstanding_principal]),
        fact_loan_monthly[snapshot_date_key] = MaxDate,
        fact_loan_monthly[days_past_due] = 0
    )
```
- **Format**: `₹ #,##0.00`

### `[Delinquency Bucket: DPD 1-30]`
- **Description**: Outstanding principal in early-stage arrears (1 to 30 days past due).
- **DAX Formula**:
```dax
Delinquency DPD 1-30 = 
CALCULATE(
    SUM(fact_loan_monthly[outstanding_principal]),
    fact_loan_monthly[days_past_due] >= 1,
    fact_loan_monthly[days_past_due] <= 30
)
```
- **Format**: `₹ #,##0.00`

### `[Delinquency Bucket: DPD 31-60]`
- **DAX Formula**:
```dax
Delinquency DPD 31-60 = 
CALCULATE(
    SUM(fact_loan_monthly[outstanding_principal]),
    fact_loan_monthly[days_past_due] >= 31,
    fact_loan_monthly[days_past_due] <= 60
)
```
- **Format**: `₹ #,##0.00`

### `[Delinquency Bucket: DPD 61-90]`
- **DAX Formula**:
```dax
Delinquency DPD 61-90 = 
CALCULATE(
    SUM(fact_loan_monthly[outstanding_principal]),
    fact_loan_monthly[days_past_due] >= 61,
    fact_loan_monthly[days_past_due] <= 90
)
```
- **Format**: `₹ #,##0.00`

---

## 2. Collection Efficiency Measures

### `[Scheduled Billing Due]`
- **Description**: Total scheduled instalment amount due in the selected period.
- **DAX Formula**:
```dax
Scheduled Billing Due = 
SUM(kpi_collection_efficiency[scheduled_amount_due])
```
- **Format**: `₹ #,##0.00`

### `[Current Period Collected]`
- **Description**: Cash collected against current month billing dues (on-time repayments).
- **DAX Formula**:
```dax
Current Period Collected = 
SUM(kpi_collection_efficiency[current_period_collected])
```
- **Format**: `₹ #,##0.00`

### `[Arrears Collected]`
- **Description**: Overdue arrears recovered against prior-period overdue instalments.
- **DAX Formula**:
```dax
Arrears Collected = 
SUM(kpi_collection_efficiency[arrears_collected])
```
- **Format**: `₹ #,##0.00`

### `[Advance Collected]`
- **Description**: Prepayments and advance collections against future-dated instalments.
- **DAX Formula**:
```dax
Advance Collected = 
SUM(kpi_collection_efficiency[advance_collected])
```
- **Format**: `₹ #,##0.00`

### `[Total Cash Collected]`
- **Description**: Total cash collections received (Current + Arrears + Advance).
- **DAX Formula**:
```dax
Total Cash Collected = 
SUM(kpi_collection_efficiency[total_amount_collected])
```
- **Format**: `₹ #,##0.00`

### `[Current Period Collection Efficiency %] (Headline Metric)`
- **Description**: Current billing collected divided by current scheduled dues.
- **DAX Formula**:
```dax
Current Period Collection Efficiency % = 
DIVIDE(
    [Current Period Collected],
    [Scheduled Billing Due],
    0
)
```
- **Format**: `0.00%`

### `[Total Collection Ratio %]`
- **Description**: Total cash collections divided by scheduled current dues (reflects gross cash recovery).
- **DAX Formula**:
```dax
Total Collection Ratio % = 
DIVIDE(
    [Total Cash Collected],
    [Scheduled Billing Due],
    0
)
```
- **Format**: `0.00%`

---

## 3. Digital Collections & Transformation Measures

### `[Total Collections Value]`
- **DAX Formula**:
```dax
Total Collections Value = 
SUM(kpi_digital_collections[total_collection_value])
```
- **Format**: `₹ #,##0.00`

### `[Digital Collections Value]`
- **DAX Formula**:
```dax
Digital Collections Value = 
SUM(kpi_digital_collections[digital_collection_value])
```
- **Format**: `₹ #,##0.00`

### `[Cash Collections Value]`
- **DAX Formula**:
```dax
Cash Collections Value = 
SUM(kpi_digital_collections[cash_collection_value])
```
- **Format**: `₹ #,##0.00`

### `[Digital Value Share %]`
- **Description**: Share of total repayment value received through digital channels (UPI + Bank Transfer).
- **DAX Formula**:
```dax
Digital Value Share % = 
DIVIDE(
    [Digital Collections Value],
    [Total Collections Value],
    0
)
```
- **Format**: `0.00%`

### `[Digital Count Share %]`
- **Description**: Share of total transaction volume processed via digital channels.
- **DAX Formula**:
```dax
Digital Count Share % = 
DIVIDE(
    SUM(kpi_digital_collections[digital_transaction_count]),
    SUM(kpi_digital_collections[total_transaction_count]),
    0
)
```
- **Format**: `0.00%`

### `[UPI Value]`
- **DAX Formula**:
```dax
UPI Value = SUM(kpi_digital_collections[upi_value])
```
- **Format**: `₹ #,##0.00`

### `[Bank Transfer Value]`
- **DAX Formula**:
```dax
Bank Transfer Value = SUM(kpi_digital_collections[bank_transfer_value])
```
- **Format**: `₹ #,##0.00`

### `[Average Ticket Size (Overall)]`
- **DAX Formula**:
```dax
Avg Ticket Size = 
DIVIDE(
    [Total Collections Value],
    SUM(kpi_digital_collections[total_transaction_count]),
    0
)
```
- **Format**: `₹ #,##0.00`

---

## 4. Repayment Vintage Measures

### `[Cumulative Scheduled Due (Vintage)]`
- **DAX Formula**:
```dax
Cumulative Scheduled Due (Vintage) = 
SUM(kpi_vintage_curves[cumulative_scheduled_due])
```
- **Format**: `₹ #,##0.00`

### `[Cumulative Amount Paid (Vintage)]`
- **DAX Formula**:
```dax
Cumulative Amount Paid (Vintage) = 
SUM(kpi_vintage_curves[cumulative_amount_paid])
```
- **Format**: `₹ #,##0.00`

### `[Vintage Repayment Rate %]`
- **Description**: Cumulative cash collected divided by cumulative scheduled dues at month on book $k$.
- **DAX Formula**:
```dax
Vintage Repayment Rate % = 
DIVIDE(
    [Cumulative Amount Paid (Vintage)],
    [Cumulative Scheduled Due (Vintage)],
    0
)
```
- **Format**: `0.00%`

---

## 5. Data Quality & Audit Measures

### `[Total Quarantined Records]`
- **DAX Formula**:
```dax
Total Quarantined Records = 
COUNTROWS(stg_quarantined_records)
```
- **Format**: `#,##0`

### `[Negative Amount Anomalies]`
- **DAX Formula**:
```dax
Negative Amount Anomalies = 
CALCULATE(
    COUNTROWS(stg_quarantined_records),
    stg_quarantined_records[reason_code] = "NEGATIVE_PAYMENT_AMOUNT"
)
```
- **Format**: `#,##0`

### `[Pre-dated Payment Anomalies]`
- **DAX Formula**:
```dax
Pre-dated Payment Anomalies = 
CALCULATE(
    COUNTROWS(stg_quarantined_records),
    stg_quarantined_records[reason_code] = "PAYMENT_BEFORE_DISBURSEMENT"
)
```
- **Format**: `#,##0`

### `[Excess Payment Anomalies]`
- **DAX Formula**:
```dax
Excess Payment Anomalies = 
CALCULATE(
    COUNTROWS(stg_quarantined_records),
    stg_quarantined_records[reason_code] = "EXCESS_INSTALMENT_PAYMENT"
)
```
- **Format**: `#,##0`
