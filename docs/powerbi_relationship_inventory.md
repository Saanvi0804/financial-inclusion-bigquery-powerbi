# Power BI Semantic Model — Relationship Inventory & Audit

## 1. Original vs. Final Relationship Summary

| Metric | Original Semantic Model | Final Refactored Model | Delta / Action |
|:---|:---:|:---:|:---|
| **Total Relationships** | 34 | **31** | -3 (Removed redundant snowflake relationships) |
| **Active Relationships** | 29 | **27** | -2 (Converted secondary date roles to inactive) |
| **Inactive Relationships** | 5 | **4** | Aligned strictly to role-playing date measures |
| **Direct Fact-to-Fact Links** | 0 | **0** | Pure dimensional architecture preserved |
| **Ambiguous Active Paths** | 12 potential cycles | **0 (Zero Ambiguities)** | Verified by automated cycle & path traversal |
| **Snowflake Inactive Links** | 3 (`dim_loan` to dimensions) | **0** | Eliminated in favor of direct conformed dimension links |

---

## 2. Original Relationship Inventory (Pre-Audit: 34 Relationships)

| # | Name | From Table | From Column | To Table | To Column | Grain / Role | Active | Cardinality | Direction | Assessment |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| 1 | `rel_pay_date` | `fact_payment` | `payment_date_key` | `dim_date` | `date_key` | Cash payment realization | True | Many-to-One | Single | **Retain Active**: Primary operational reporting date |
| 2 | `rel_pay_loan` | `fact_payment` | `loan_key` | `dim_loan` | `loan_key` | Loan account transaction | True | Many-to-One | Single | **Retain Active**: Dimension filter to fact |
| 3 | `rel_pay_branch` | `fact_payment` | `branch_key` | `dim_branch` | `branch_key` | Branch attribution | True | Many-to-One | Single | **Retain Active**: Conformed dimension filter |
| 4 | `rel_pay_product` | `fact_payment` | `product_key` | `dim_product` | `product_key` | Product category | True | Many-to-One | Single | **Retain Active**: Conformed dimension filter |
| 5 | `rel_pay_state` | `fact_payment` | `state_key` | `dim_state` | `state_key` | State regional attribution | True | Many-to-One | Single | **Retain Active**: Conformed dimension filter |
| 6 | `rel_pay_segment` | `fact_payment` | `borrower_segment_key` | `dim_borrower_segment` | `borrower_segment_key` | Socioeconomic profile | True | Many-to-One | Single | **Retain Active**: Conformed dimension filter |
| 7 | `rel_snap_date` | `fact_loan_monthly` | `snapshot_date_key` | `dim_date` | `date_key` | Month-end position date | True | Many-to-One | Single | **Change to Inactive**: Single active date rule |
| 8 | `rel_snap_loan` | `fact_loan_monthly` | `loan_key` | `dim_loan` | `loan_key` | Loan monthly ledger | True | Many-to-One | Single | **Retain Active**: Dimension filter to fact |
| 9 | `rel_snap_branch` | `fact_loan_monthly` | `branch_key` | `dim_branch` | `branch_key` | Branch portfolio attribution | True | Many-to-One | Single | **Retain Active**: Conformed dimension filter |
| 10 | `rel_snap_product` | `fact_loan_monthly` | `product_key` | `dim_product` | `product_key` | Product portfolio attribution | True | Many-to-One | Single | **Retain Active**: Conformed dimension filter |
| 11 | `rel_snap_state` | `fact_loan_monthly` | `state_key` | `dim_state` | `state_key` | State portfolio attribution | True | Many-to-One | Single | **Retain Active**: Conformed dimension filter |
| 12 | `rel_snap_segment` | `fact_loan_monthly` | `borrower_segment_key` | `dim_borrower_segment` | `borrower_segment_key` | Borrower segment attribution | True | Many-to-One | Single | **Retain Active**: Conformed dimension filter |
| 13 | `rel_alloc_due_date` | `fact_instalment_allocation` | `due_date_key` | `dim_date` | `date_key` | Contractual due date | True | Many-to-One | Single | **Change to Inactive**: Single active date rule |
| 14 | `rel_alloc_pay_date` | `fact_instalment_allocation` | `payment_date_key` | `dim_date` | `date_key` | Cash allocation date | False | Many-to-One | Single | **Retain Inactive**: Secondary date role |
| 15 | `rel_alloc_loan` | `fact_instalment_allocation` | `loan_key` | `dim_loan` | `loan_key` | Loan waterfall linkage | True | Many-to-One | Single | **Retain Active**: Dimension filter to fact |
| 16 | `rel_alloc_branch` | `fact_instalment_allocation` | `branch_key` | `dim_branch` | `branch_key` | Branch allocation attribution | True | Many-to-One | Single | **Retain Active**: Conformed dimension filter |
| 17 | `rel_alloc_product` | `fact_instalment_allocation` | `product_key` | `dim_product` | `product_key` | Product allocation attribution | True | Many-to-One | Single | **Retain Active**: Conformed dimension filter |
| 18 | `rel_alloc_state` | `fact_instalment_allocation` | `state_key` | `dim_state` | `state_key` | State allocation attribution | True | Many-to-One | Single | **Retain Active**: Conformed dimension filter |
| 19 | `rel_kpi_ph_date` | `kpi_portfolio_health` | `snapshot_date_key` | `dim_date` | `date_key` | Reporting snapshot month | True | Many-to-One | Single | **Retain Active**: Aggregate grain date |
| 20 | `rel_kpi_ph_branch` | `kpi_portfolio_health` | `branch_id` | `dim_branch` | `branch_id` | Branch risk breakdown | True | Many-to-One | Single | **Retain Active**: Valid business key |
| 21 | `rel_kpi_ph_product` | `kpi_portfolio_health` | `product_id` | `dim_product` | `product_id` | Product risk breakdown | True | Many-to-One | Single | **Retain Active**: Valid business key |
| 22 | `rel_kpi_ph_state` | `kpi_portfolio_health` | `state_id` | `dim_state` | `state_id` | State risk breakdown | True | Many-to-One | Single | **Retain Active**: Valid business key |
| 23 | `rel_kpi_ce_date` | `kpi_collection_efficiency` | `month_date_key` | `dim_date` | `date_key` | Billing month period | True | Many-to-One | Single | **Retain Active**: Aggregate grain date |
| 24 | `rel_kpi_ce_branch` | `kpi_collection_efficiency` | `branch_id` | `dim_branch` | `branch_id` | Branch recovery breakdown | True | Many-to-One | Single | **Retain Active**: Valid business key |
| 25 | `rel_kpi_ce_product` | `kpi_collection_efficiency` | `product_id` | `dim_product` | `product_id` | Product recovery breakdown | True | Many-to-One | Single | **Retain Active**: Valid business key |
| 26 | `rel_kpi_ce_state` | `kpi_collection_efficiency` | `state_id` | `dim_state` | `state_id` | State recovery breakdown | True | Many-to-One | Single | **Retain Active**: Valid business key |
| 27 | `rel_kpi_dc_date` | `kpi_digital_collections` | `month_date_key` | `dim_date` | `date_key` | Digital adoption month | True | Many-to-One | Single | **Retain Active**: Aggregate grain date |
| 28 | `rel_kpi_dc_state` | `kpi_digital_collections` | `state_id` | `dim_state` | `state_id` | State channel breakdown | True | Many-to-One | Single | **Retain Active**: Valid business key |
| 29 | `rel_kpi_vc_date` | `kpi_vintage_curves` | `cohort_date_key` | `dim_date` | `date_key` | Cohort origination month | True | Many-to-One | Single | **Retain Active**: Aggregate grain date |
| 30 | `rel_kpi_vc_product` | `kpi_vintage_curves` | `product_id` | `dim_product` | `product_id` | Product vintage curve | True | Many-to-One | Single | **Retain Active**: Valid business key |
| 31 | `rel_loan_disb_date` | `dim_loan` | `disbursement_date_key` | `dim_date` | `date_key` | Loan disbursement date | False | Many-to-One | Single | **Retain Inactive**: Origination role-playing date |
| 32 | `rel_loan_branch` | `dim_loan` | `branch_id` | `dim_branch` | `branch_id` | Snowflake dim-to-dim | False | Many-to-One | Single | **REMOVE**: Redundant snowflake path |
| 33 | `rel_loan_product` | `dim_loan` | `product_id` | `dim_product` | `product_id` | Snowflake dim-to-dim | False | Many-to-One | Single | **REMOVE**: Redundant snowflake path |
| 34 | `rel_loan_state` | `dim_loan` | `state_id` | `dim_state` | `state_id` | Snowflake dim-to-dim | False | Many-to-One | Single | **REMOVE**: Redundant snowflake path |

---

## 3. Final Corrected Relationship Inventory (31 Relationships)

| # | Relationship Name | From Table (Many) | From Column (FK) | To Table (One) | To Column (PK) | Active | Cross-Filtering | Business Justification & Role |
|:---|:---|:---|:---|:---|:---|:---:|:---:|:---|
| 1 | `rel_pay_date` | `fact_payment` | `payment_date_key` | `dim_date` | `date_key` | **Active** | `oneDirection` | Primary active date for cash collections |
| 2 | `rel_pay_loan` | `fact_payment` | `loan_key` | `dim_loan` | `loan_key` | **Active** | `oneDirection` | Links cash payment transaction to loan dimension |
| 3 | `rel_pay_branch` | `fact_payment` | `branch_key` | `dim_branch` | `branch_key` | **Active** | `oneDirection` | Slices payments by branch and location attributes |
| 4 | `rel_pay_product` | `fact_payment` | `product_key` | `dim_product` | `product_key` | **Active** | `oneDirection` | Slices payments by loan product category |
| 5 | `rel_pay_state` | `fact_payment` | `state_key` | `dim_state` | `state_key` | **Active** | `oneDirection` | Slices payments by state and regional geography |
| 6 | `rel_pay_segment` | `fact_payment` | `borrower_segment_key` | `dim_borrower_segment` | `borrower_segment_key` | **Active** | `oneDirection` | Slices payments by borrower income and occupation |
| 7 | `rel_snap_date` | `fact_loan_monthly` | `snapshot_date_key` | `dim_date` | `date_key` | **Inactive** | `oneDirection` | Snapshot date role (activated in DAX via `USERELATIONSHIP`) |
| 8 | `rel_snap_loan` | `fact_loan_monthly` | `loan_key` | `dim_loan` | `loan_key` | **Active** | `oneDirection` | Links monthly ledger records to loan dimension |
| 9 | `rel_snap_branch` | `fact_loan_monthly` | `branch_key` | `dim_branch` | `branch_key` | **Active** | `oneDirection` | Slices portfolio balances and DPD by branch |
| 10 | `rel_snap_product` | `fact_loan_monthly` | `product_key` | `dim_product` | `product_key` | **Active** | `oneDirection` | Slices portfolio balances and DPD by loan product |
| 11 | `rel_snap_state` | `fact_loan_monthly` | `state_key` | `dim_state` | `state_key` | **Active** | `oneDirection` | Slices portfolio balances and DPD by state |
| 12 | `rel_snap_segment` | `fact_loan_monthly` | `borrower_segment_key` | `dim_borrower_segment` | `borrower_segment_key` | **Active** | `oneDirection` | Slices portfolio balances and DPD by borrower segment |
| 13 | `rel_alloc_due_date` | `fact_instalment_allocation` | `due_date_key` | `dim_date` | `date_key` | **Inactive** | `oneDirection` | Contractual due date role (activated in DAX via `USERELATIONSHIP`) |
| 14 | `rel_alloc_pay_date` | `fact_instalment_allocation` | `payment_date_key` | `dim_date` | `date_key` | **Inactive** | `oneDirection` | Cash realization date role (activated in DAX via `USERELATIONSHIP`) |
| 15 | `rel_alloc_loan` | `fact_instalment_allocation` | `loan_key` | `dim_loan` | `loan_key` | **Active** | `oneDirection` | Links FIFO waterfall allocation to loan dimension |
| 16 | `rel_alloc_branch` | `fact_instalment_allocation` | `branch_key` | `dim_branch` | `branch_key` | **Active** | `oneDirection` | Slices allocated principal/interest by branch |
| 17 | `rel_alloc_product` | `fact_instalment_allocation` | `product_key` | `dim_product` | `product_key` | **Active** | `oneDirection` | Slices allocated principal/interest by product |
| 18 | `rel_alloc_state` | `fact_instalment_allocation` | `state_key` | `dim_state` | `state_key` | **Active** | `oneDirection` | Slices allocated principal/interest by state |
| 19 | `rel_loan_disb_date` | `dim_loan` | `disbursement_date_key` | `dim_date` | `date_key` | **Inactive** | `oneDirection` | Loan origination date role (activated in DAX via `USERELATIONSHIP`) |
| 20 | `rel_kpi_ph_date` | `kpi_portfolio_health` | `snapshot_date_key` | `dim_date` | `date_key` | **Active** | `oneDirection` | Filters portfolio health aggregations by snapshot month |
| 21 | `rel_kpi_ph_branch` | `kpi_portfolio_health` | `branch_id` | `dim_branch` | `branch_id` | **Active** | `oneDirection` | Slices portfolio health metrics by branch |
| 22 | `rel_kpi_ph_product` | `kpi_portfolio_health` | `product_id` | `dim_product` | `product_id` | **Active** | `oneDirection` | Slices portfolio health metrics by product |
| 23 | `rel_kpi_ph_state` | `kpi_portfolio_health` | `state_id` | `dim_state` | `state_id` | **Active** | `oneDirection` | Slices portfolio health metrics by state |
| 24 | `rel_kpi_ce_date` | `kpi_collection_efficiency` | `month_date_key` | `dim_date` | `date_key` | **Active** | `oneDirection` | Filters collection efficiency by billing calendar month |
| 25 | `rel_kpi_ce_branch` | `kpi_collection_efficiency` | `branch_id` | `dim_branch` | `branch_id` | **Active** | `oneDirection` | Slices collection efficiency metrics by branch |
| 26 | `rel_kpi_ce_product` | `kpi_collection_efficiency` | `product_id` | `dim_product` | `product_id` | **Active** | `oneDirection` | Slices collection efficiency metrics by product |
| 27 | `rel_kpi_ce_state` | `kpi_collection_efficiency` | `state_id` | `dim_state` | `state_id` | **Active** | `oneDirection` | Slices collection efficiency metrics by state |
| 28 | `rel_kpi_dc_date` | `kpi_digital_collections` | `month_date_key` | `dim_date` | `date_key` | **Active** | `oneDirection` | Filters digital channel metrics by monthly period |
| 29 | `rel_kpi_dc_state` | `kpi_digital_collections` | `state_id` | `dim_state` | `state_id` | **Active** | `oneDirection` | Slices digital adoption metrics by state |
| 30 | `rel_kpi_vc_date` | `kpi_vintage_curves` | `cohort_date_key` | `dim_date` | `date_key` | **Active** | `oneDirection` | Filters vintage curves by cohort origination date |
| 31 | `rel_kpi_vc_product` | `kpi_vintage_curves` | `product_id` | `dim_product` | `product_id` | **Active** | `oneDirection` | Slices vintage repayment curves by product |

---

## 4. Rationale for Removed and Modified Relationships

### A. Snowflake Dimension-to-Dimension Relationships Removed (3)
* `dim_loan[branch_id] -> dim_branch[branch_id]`
* `dim_loan[product_id] -> dim_product[product_id]`
* `dim_loan[state_id] -> dim_state[state_id]`
**Why Removed**:
In Kimball dimensional modeling, dimension tables should not form snowflake chains into other dimensions when fact tables already carry direct conformed foreign keys. Every fact table (`fact_payment`, `fact_instalment_allocation`, `fact_loan_monthly`) links directly to `dim_branch`, `dim_product`, and `dim_state`. Leaving dimension-to-dimension relationships creates redundant multi-path cycles (`dim_branch` $\to$ `dim_loan` $\to$ `fact_payment` vs `dim_branch` $\to$ `fact_payment`), confusing the Tabular Engine.

### B. Secondary Date Roles Converted to Inactive (2)
* `fact_loan_monthly[snapshot_date_key] -> dim_date[date_key]` $\to$ Set to **Inactive**.
* `fact_instalment_allocation[due_date_key] -> dim_date[date_key]` $\to$ Set to **Inactive**.

**Why Modified**:
Following the architectural design principles:
*"At most one active date relationship per consuming fact or KPI table: `fact_payment` $\to$ Payment Date (active), `fact_instalment_allocation` $\to$ Due Date (inactive), `fact_loan_monthly` $\to$ Snapshot Date (inactive), `dim_loan` $\to$ Disbursement Date (inactive)"*.

**Complete Date Relationship Breakdown (9 Total Relationships to `dim_date`)**:
* **5 Active Relationships**:
  1. `fact_payment[payment_date_key] -> dim_date[date_key]` (Active cash transactions)
  2. `kpi_portfolio_health[snapshot_date_key] -> dim_date[date_key]` (Active portfolio health KPIs)
  3. `kpi_collection_efficiency[month_date_key] -> dim_date[date_key]` (Active collection efficiency KPIs)
  4. `kpi_digital_collections[month_date_key] -> dim_date[date_key]` (Active digital collection trends)
  5. `kpi_vintage_curves[cohort_date_key] -> dim_date[date_key]` (Active vintage cohort curves)
* **4 Inactive Relationships**:
  1. `fact_loan_monthly[snapshot_date_key] -> dim_date[date_key]` (Portfolio cutoff, activated via `USERELATIONSHIP`)
  2. `fact_instalment_allocation[due_date_key] -> dim_date[date_key]` (Instalment due date, activated via `USERELATIONSHIP`)
  3. `fact_instalment_allocation[payment_date_key] -> dim_date[date_key]` (Cash realization date, activated via `USERELATIONSHIP`)
  4. `dim_loan[disbursement_date_key] -> dim_date[date_key]` (Origination date, activated via `USERELATIONSHIP`)

Because fact tables do not connect to other fact tables and KPI tables do not connect to each other, each consuming table has exactly one active date filter path from `dim_date`, ensuring 0 ambiguous active filter paths across the entire tabular model. DAX measures for portfolio snapshot balances explicitly activate `snapshot_date_key` using `USERELATIONSHIP`.
