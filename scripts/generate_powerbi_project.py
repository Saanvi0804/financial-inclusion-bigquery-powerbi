"""
Generates the Power BI Project (PBIP) directory structure and files:
- powerbi/Financial_Inclusion_Analytics.pbip
- powerbi/Financial_Inclusion_Analytics.Report/definition.pbir
- powerbi/Financial_Inclusion_Analytics.Report/report.json
- powerbi/Financial_Inclusion_Analytics.SemanticModel/definition.pbism
- powerbi/Financial_Inclusion_Analytics.SemanticModel/model.bim

Enables direct one-click opening in Power BI Desktop on Windows.
"""

import os
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("GeneratePBIP")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POWERBI_DIR = os.path.join(PROJECT_ROOT, "powerbi")
REPORT_DIR = os.path.join(POWERBI_DIR, "Financial_Inclusion_Analytics.Report")
MODEL_DIR = os.path.join(POWERBI_DIR, "Financial_Inclusion_Analytics.SemanticModel")

def generate_pbip():
    os.makedirs(REPORT_DIR, exist_ok=True)
    os.makedirs(MODEL_DIR, exist_ok=True)

    # 1. Main .pbip file
    pbip_path = os.path.join(POWERBI_DIR, "Financial_Inclusion_Analytics.pbip")
    pbip_content = {
        "version": "1.0",
        "artifacts": [
            {
                "report": {
                    "path": "Financial_Inclusion_Analytics.Report"
                }
            }
        ],
        "settings": {
            "enableAutoAuth": True
        }
    }
    with open(pbip_path, "w", encoding="utf-8") as f:
        json.dump(pbip_content, f, indent=2)
    logger.info("Wrote %s", pbip_path)

    # 2. definition.pbir
    pbir_path = os.path.join(REPORT_DIR, "definition.pbir")
    pbir_content = {
        "version": "1.0",
        "datasetReference": {
            "byPath": {
                "path": "../Financial_Inclusion_Analytics.SemanticModel"
            },
            "byConnection": None
        }
    }
    with open(pbir_path, "w", encoding="utf-8") as f:
        json.dump(pbir_content, f, indent=2)
    logger.info("Wrote %s", pbir_path)

    # 3. definition.pbism
    pbism_path = os.path.join(MODEL_DIR, "definition.pbism")
    pbism_content = {
        "version": "1.0"
    }
    with open(pbism_path, "w", encoding="utf-8") as f:
        json.dump(pbism_content, f, indent=2)
    logger.info("Wrote %s", pbism_path)

    # 4. model.bim (TMSL tabular model)
    model_bim_path = os.path.join(MODEL_DIR, "model.bim")
    
    # We will build model.bim with parameters, tables, measures, and relationships
    model_bim = {
        "name": "Financial_Inclusion_Analytics",
        "compatibilityLevel": 1567,
        "model": {
            "culture": "en-US",
            "dataAccessOptions": {
                "legacyRedirects": True,
                "returnErrorValuesAsNull": True
            },
            "defaultPowerBIDataSourceVersion": "powerBI_V3",
            "sourceQueryCulture": "en-US",
            "expressions": [
                {
                    "name": "Location",
                    "kind": "m",
                    "expression": [
                        f'"{PROJECT_ROOT.replace(chr(92), "/")}" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]'
                    ],
                    "lineageTag": "param-location-root",
                    "description": "Root directory path for financial-inclusion-bigquery-powerbi. Update this parameter in 'Home > Transform Data > Edit Parameters' if moving to a different folder or machine."
                }
            ],
            "tables": [
                {
                    "name": "_Measures",
                    "lineageTag": "measures-table-lineage",
                    "columns": [
                        {
                            "name": "Dummy",
                            "dataType": "string",
                            "isHidden": True,
                            "sourceColumn": "Dummy"
                        }
                    ],
                    "partitions": [
                        {
                            "name": "_Measures-Partition",
                            "mode": "import",
                            "source": {
                                "type": "m",
                                "expression": [
                                    "let",
                                    "    Source = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText(\"i44FAA==\", BinaryEncoding.Base64), Compression.Deflate)), let _t = ((type nullable text) meta [Serialized.Text = true]) in type table [Dummy = _t])",
                                    "in",
                                    "    Source"
                                ]
                            }
                        }
                    ],
                    "measures": [
                        {
                            "name": "Active Loans Count",
                            "expression": "VAR MaxDate = MAX(fact_loan_monthly[snapshot_date_key]) RETURN CALCULATE(DISTINCTCOUNT(fact_loan_monthly[loan_key]), fact_loan_monthly[snapshot_date_key] = MaxDate, fact_loan_monthly[outstanding_principal] > 0)",
                            "formatString": "#,##0"
                        },
                        {
                            "name": "Total Outstanding Principal",
                            "expression": "VAR MaxDate = MAX(fact_loan_monthly[snapshot_date_key]) RETURN CALCULATE(SUM(fact_loan_monthly[outstanding_principal]), fact_loan_monthly[snapshot_date_key] = MaxDate)",
                            "formatString": "\"₹\"\\ #,##0.00"
                        },
                        {
                            "name": "Outstanding Principal (INR Cr)",
                            "expression": "DIVIDE([Total Outstanding Principal], 10000000, 0)",
                            "formatString": "\"₹\"\\ #,##0.00\\ \"Cr\""
                        },
                        {
                            "name": "PAR 30 Principal",
                            "expression": "VAR MaxDate = MAX(fact_loan_monthly[snapshot_date_key]) RETURN CALCULATE(SUM(fact_loan_monthly[outstanding_principal]), fact_loan_monthly[snapshot_date_key] = MaxDate, fact_loan_monthly[days_past_due] > 30)",
                            "formatString": "\"₹\"\\ #,##0.00"
                        },
                        {
                            "name": "PAR 30 %",
                            "expression": "DIVIDE([PAR 30 Principal], [Total Outstanding Principal], 0)",
                            "formatString": "0.00%"
                        },
                        {
                            "name": "PAR 90 Principal",
                            "expression": "VAR MaxDate = MAX(fact_loan_monthly[snapshot_date_key]) RETURN CALCULATE(SUM(fact_loan_monthly[outstanding_principal]), fact_loan_monthly[snapshot_date_key] = MaxDate, fact_loan_monthly[days_past_due] > 90)",
                            "formatString": "\"₹\"\\ #,##0.00"
                        },
                        {
                            "name": "PAR 90 %",
                            "expression": "DIVIDE([PAR 90 Principal], [Total Outstanding Principal], 0)",
                            "formatString": "0.00%"
                        },
                        {
                            "name": "Current Principal",
                            "expression": "VAR MaxDate = MAX(fact_loan_monthly[snapshot_date_key]) RETURN CALCULATE(SUM(fact_loan_monthly[outstanding_principal]), fact_loan_monthly[snapshot_date_key] = MaxDate, fact_loan_monthly[days_past_due] = 0)",
                            "formatString": "\"₹\"\\ #,##0.00"
                        },
                        {
                            "name": "Delinquency DPD 1-30",
                            "expression": "VAR MaxDate = MAX(fact_loan_monthly[snapshot_date_key]) RETURN CALCULATE(SUM(fact_loan_monthly[outstanding_principal]), fact_loan_monthly[snapshot_date_key] = MaxDate, fact_loan_monthly[days_past_due] >= 1, fact_loan_monthly[days_past_due] <= 30)",
                            "formatString": "\"₹\"\\ #,##0.00"
                        },
                        {
                            "name": "Delinquency DPD 31-60",
                            "expression": "VAR MaxDate = MAX(fact_loan_monthly[snapshot_date_key]) RETURN CALCULATE(SUM(fact_loan_monthly[outstanding_principal]), fact_loan_monthly[snapshot_date_key] = MaxDate, fact_loan_monthly[days_past_due] >= 31, fact_loan_monthly[days_past_due] <= 60)",
                            "formatString": "\"₹\"\\ #,##0.00"
                        },
                        {
                            "name": "Delinquency DPD 61-90",
                            "expression": "VAR MaxDate = MAX(fact_loan_monthly[snapshot_date_key]) RETURN CALCULATE(SUM(fact_loan_monthly[outstanding_principal]), fact_loan_monthly[snapshot_date_key] = MaxDate, fact_loan_monthly[days_past_due] >= 61, fact_loan_monthly[days_past_due] <= 90)",
                            "formatString": "\"₹\"\\ #,##0.00"
                        },
                        {
                            "name": "Scheduled Billing Due",
                            "expression": "SUM(kpi_collection_efficiency[scheduled_amount_due])",
                            "formatString": "\"₹\"\\ #,##0.00"
                        },
                        {
                            "name": "Current Period Collected",
                            "expression": "SUM(kpi_collection_efficiency[current_period_collected])",
                            "formatString": "\"₹\"\\ #,##0.00"
                        },
                        {
                            "name": "Arrears Collected",
                            "expression": "SUM(kpi_collection_efficiency[arrears_collected])",
                            "formatString": "\"₹\"\\ #,##0.00"
                        },
                        {
                            "name": "Advance Collected",
                            "expression": "SUM(kpi_collection_efficiency[advance_collected])",
                            "formatString": "\"₹\"\\ #,##0.00"
                        },
                        {
                            "name": "Total Cash Collected",
                            "expression": "SUM(kpi_collection_efficiency[total_amount_collected])",
                            "formatString": "\"₹\"\\ #,##0.00"
                        },
                        {
                            "name": "Current Period Collection Efficiency %",
                            "expression": "DIVIDE([Current Period Collected], [Scheduled Billing Due], 0)",
                            "formatString": "0.00%"
                        },
                        {
                            "name": "Total Collection Ratio %",
                            "expression": "DIVIDE([Total Cash Collected], [Scheduled Billing Due], 0)",
                            "formatString": "0.00%"
                        },
                        {
                            "name": "Total Collections Value",
                            "expression": "SUM(kpi_digital_collections[total_collection_value])",
                            "formatString": "\"₹\"\\ #,##0.00"
                        },
                        {
                            "name": "Digital Collections Value",
                            "expression": "SUM(kpi_digital_collections[digital_collection_value])",
                            "formatString": "\"₹\"\\ #,##0.00"
                        },
                        {
                            "name": "Cash Collections Value",
                            "expression": "SUM(kpi_digital_collections[cash_collection_value])",
                            "formatString": "\"₹\"\\ #,##0.00"
                        },
                        {
                            "name": "UPI Value",
                            "expression": "SUM(kpi_digital_collections[upi_value])",
                            "formatString": "\"₹\"\\ #,##0.00"
                        },
                        {
                            "name": "Bank Transfer Value",
                            "expression": "SUM(kpi_digital_collections[bank_transfer_value])",
                            "formatString": "\"₹\"\\ #,##0.00"
                        },
                        {
                            "name": "Digital Value Share %",
                            "expression": "DIVIDE([Digital Collections Value], [Total Collections Value], 0)",
                            "formatString": "0.00%"
                        },
                        {
                            "name": "Digital Count Share %",
                            "expression": "DIVIDE(SUM(kpi_digital_collections[digital_transaction_count]), SUM(kpi_digital_collections[total_transaction_count]), 0)",
                            "formatString": "0.00%"
                        },
                        {
                            "name": "Cumulative Scheduled Due (Vintage)",
                            "expression": "SUM(kpi_vintage_curves[cumulative_scheduled_due])",
                            "formatString": "\"₹\"\\ #,##0.00"
                        },
                        {
                            "name": "Cumulative Amount Paid (Vintage)",
                            "expression": "SUM(kpi_vintage_curves[cumulative_amount_paid])",
                            "formatString": "\"₹\"\\ #,##0.00"
                        },
                        {
                            "name": "Vintage Repayment Rate %",
                            "expression": "DIVIDE([Cumulative Amount Paid (Vintage)], [Cumulative Scheduled Due (Vintage)], 0)",
                            "formatString": "0.00%"
                        },
                        {
                            "name": "Total Quarantined Records",
                            "expression": "COUNTROWS(stg_quarantined_records)",
                            "formatString": "#,##0"
                        },
                        {
                            "name": "Negative Amount Anomalies",
                            "expression": "CALCULATE(COUNTROWS(stg_quarantined_records), stg_quarantined_records[reason_code] = \"NEGATIVE_PAYMENT_AMOUNT\")",
                            "formatString": "#,##0"
                        },
                        {
                            "name": "Pre-dated Payment Anomalies",
                            "expression": "CALCULATE(COUNTROWS(stg_quarantined_records), stg_quarantined_records[reason_code] = \"PAYMENT_BEFORE_DISBURSEMENT\")",
                            "formatString": "#,##0"
                        },
                        {
                            "name": "Excess Payment Anomalies",
                            "expression": "CALCULATE(COUNTROWS(stg_quarantined_records), stg_quarantined_records[reason_code] = \"EXCESS_INSTALMENT_PAYMENT\")",
                            "formatString": "#,##0"
                        },
                        {
                            "name": "Loans Disbursed Count",
                            "expression": "CALCULATE(DISTINCTCOUNT(dim_loan[loan_key]), USERELATIONSHIP(dim_loan[disbursement_date_key], dim_date[date_key]))",
                            "formatString": "#,##0"
                        },
                        {
                            "name": "Total Disbursed Principal",
                            "expression": "CALCULATE(SUM(dim_loan[principal_amount]), USERELATIONSHIP(dim_loan[disbursement_date_key], dim_date[date_key]))",
                            "formatString": "\"₹\"\\ #,##0.00"
                        },
                        {
                            "name": "Disbursed Principal (INR Cr)",
                            "expression": "DIVIDE([Total Disbursed Principal], 10000000, 0)",
                            "formatString": "\"₹\"\\ #,##0.00\\ \"Cr\""
                        },
                        {
                            "name": "Payments by Loan Disbursement Date",
                            "expression": "CALCULATE(SUM(fact_payment[payment_amount]), USERELATIONSHIP(dim_loan[disbursement_date_key], dim_date[date_key]))",
                            "formatString": "\"₹\"\\ #,##0.00"
                        },
                        {
                            "name": "Allocations by Cash Payment Date",
                            "expression": "CALCULATE(SUM(fact_instalment_allocation[allocated_amount]), USERELATIONSHIP(fact_instalment_allocation[payment_date_key], dim_date[date_key]))",
                            "formatString": "\"₹\"\\ #,##0.00"
                        }
                    ]
                }
            ],
            "relationships": []
        }
    }

    # Helper function to generate table definition
    def create_table_def(table_name, csv_filename, columns_schema):
        cols = []
        for col_name, col_type in columns_schema.items():
            col_def = {
                "name": col_name,
                "dataType": col_type,
                "sourceColumn": col_name
            }
            if "key" in col_name.lower():
                col_def["isHidden"] = True
            cols.append(col_def)

        m_expr = [
            "let",
            '    CleanLocation = Text.TrimEnd(Text.Replace(Location, "\\\\", "/"), {"/"}),',
            f'    FilePath = CleanLocation & "/data/powerbi_extracts/{csv_filename}",',
            '    Source = Csv.Document(File.Contents(FilePath), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),',
            '    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])',
            "in",
            '    #"Promoted Headers"'
        ]

        return {
            "name": table_name,
            "lineageTag": f"{table_name}-lineage",
            "columns": cols,
            "partitions": [
                {
                    "name": f"{table_name}-Partition",
                    "mode": "import",
                    "source": {
                        "type": "m",
                        "expression": m_expr
                    }
                }
            ]
        }

    # 1. Dimensions
    model_bim["model"]["tables"].append(create_table_def("dim_date", "dim_date.csv", {
        "date_key": "int64",
        "full_date": "dateTime",
        "day_of_month": "int64",
        "month_number": "int64",
        "month_name": "string",
        "year_month": "string",
        "quarter_number": "int64",
        "quarter_name": "string",
        "calendar_year": "int64",
        "financial_year": "string",
        "financial_quarter": "string",
        "is_weekend": "boolean",
        "is_month_end": "boolean"
    }))

    model_bim["model"]["tables"].append(create_table_def("dim_state", "dim_state.csv", {
        "state_key": "int64",
        "state_id": "string",
        "state_name": "string",
        "region": "string"
    }))

    model_bim["model"]["tables"].append(create_table_def("dim_branch", "dim_branch.csv", {
        "branch_key": "int64",
        "branch_id": "string",
        "branch_name": "string",
        "state_id": "string",
        "location_type": "string"
    }))

    model_bim["model"]["tables"].append(create_table_def("dim_product", "dim_product.csv", {
        "product_key": "int64",
        "product_id": "string",
        "product_name": "string",
        "category": "string",
        "min_rate": "double",
        "max_rate": "double",
        "min_tenure": "int64",
        "max_tenure": "int64"
    }))

    model_bim["model"]["tables"].append(create_table_def("dim_borrower_segment", "dim_borrower_segment.csv", {
        "borrower_segment_key": "int64",
        "borrower_segment": "string",
        "income_band": "string",
        "location_type": "string",
        "occupation_category": "string"
    }))

    model_bim["model"]["tables"].append(create_table_def("dim_loan", "dim_loan.csv", {
        "loan_key": "int64",
        "loan_id": "string",
        "borrower_id": "string",
        "branch_id": "string",
        "state_id": "string",
        "product_id": "string",
        "disbursement_date": "dateTime",
        "disbursement_date_key": "int64",
        "principal_amount": "double",
        "annual_interest_rate": "double",
        "tenure_months": "int64",
        "loan_status": "string"
    }))

    # 2. Granular Facts
    model_bim["model"]["tables"].append(create_table_def("fact_payment", "fact_payment.csv", {
        "payment_key": "int64",
        "transaction_id": "string",
        "loan_key": "int64",
        "payment_date": "dateTime",
        "payment_date_key": "int64",
        "branch_key": "int64",
        "state_key": "int64",
        "product_key": "int64",
        "borrower_segment_key": "int64",
        "payment_amount": "double",
        "payment_channel": "string",
        "raw_payment_amount": "double",
        "raw_amount_unit": "string"
    }))

    model_bim["model"]["tables"].append(create_table_def("fact_instalment_allocation", "fact_instalment_allocation.csv", {
        "allocation_key": "int64",
        "transaction_id": "string",
        "instalment_id": "string",
        "loan_key": "int64",
        "payment_date": "dateTime",
        "payment_date_key": "int64",
        "due_date": "dateTime",
        "due_date_key": "int64",
        "branch_key": "int64",
        "state_key": "int64",
        "product_key": "int64",
        "borrower_segment_key": "int64",
        "instalment_number": "int64",
        "allocated_amount": "double",
        "allocated_principal": "double",
        "allocated_interest": "double",
        "payment_channel": "string"
    }))

    model_bim["model"]["tables"].append(create_table_def("fact_loan_monthly", "fact_loan_monthly.csv", {
        "snapshot_key": "int64",
        "loan_id": "string",
        "loan_key": "int64",
        "snapshot_date": "dateTime",
        "snapshot_date_key": "int64",
        "branch_key": "int64",
        "state_key": "int64",
        "product_key": "int64",
        "borrower_segment_key": "int64",
        "outstanding_principal": "double",
        "instalments_due": "int64",
        "instalments_paid": "int64",
        "amount_due": "double",
        "amount_paid": "double",
        "days_past_due": "int64",
        "overdue_amount": "double"
    }))

    # 3. Analytical KPI Marts
    model_bim["model"]["tables"].append(create_table_def("kpi_portfolio_health", "kpi_portfolio_health.csv", {
        "year_month": "string",
        "snapshot_date": "dateTime",
        "snapshot_date_key": "int64",
        "state_id": "string",
        "state_name": "string",
        "region": "string",
        "branch_id": "string",
        "branch_name": "string",
        "branch_location_type": "string",
        "product_id": "string",
        "product_name": "string",
        "product_category": "string",
        "borrower_segment": "string",
        "total_active_loans": "int64",
        "total_cumulative_loans": "int64",
        "total_outstanding_principal": "double",
        "principal_current": "double",
        "principal_dpd_1_30": "double",
        "principal_dpd_31_60": "double",
        "principal_dpd_61_90": "double",
        "principal_dpd_90_plus": "double",
        "par30_principal": "double",
        "par90_principal": "double",
        "par30_pct": "double",
        "par90_pct": "double"
    }))

    model_bim["model"]["tables"].append(create_table_def("kpi_collection_efficiency", "kpi_collection_efficiency.csv", {
        "year_month": "string",
        "month_date_key": "int64",
        "state_id": "string",
        "state_name": "string",
        "branch_id": "string",
        "branch_name": "string",
        "product_id": "string",
        "product_name": "string",
        "scheduled_amount_due": "double",
        "current_period_collected": "double",
        "arrears_collected": "double",
        "advance_collected": "double",
        "total_amount_collected": "double",
        "current_period_efficiency_pct": "double",
        "total_collection_ratio_pct": "double",
        "collection_efficiency_pct": "double"
    }))

    model_bim["model"]["tables"].append(create_table_def("kpi_vintage_curves", "kpi_vintage_curves.csv", {
        "cohort_month": "string",
        "cohort_date_key": "int64",
        "product_id": "string",
        "product_name": "string",
        "product_category": "string",
        "month_on_book": "int64",
        "total_cohort_loans": "int64",
        "scheduled_due_mob": "double",
        "amount_paid_mob": "double",
        "cumulative_scheduled_due": "double",
        "cumulative_amount_paid": "double",
        "vintage_repayment_rate_pct": "double"
    }))

    model_bim["model"]["tables"].append(create_table_def("kpi_digital_collections", "kpi_digital_collections.csv", {
        "year_month": "string",
        "month_date_key": "int64",
        "state_id": "string",
        "state_name": "string",
        "total_collection_value": "double",
        "total_transaction_count": "int64",
        "digital_collection_value": "double",
        "digital_transaction_count": "int64",
        "cash_collection_value": "double",
        "cash_transaction_count": "int64",
        "upi_value": "double",
        "upi_count": "int64",
        "bank_transfer_value": "double",
        "bank_transfer_count": "int64",
        "avg_ticket_upi": "double",
        "avg_ticket_bank_transfer": "double",
        "avg_ticket_cash": "double",
        "avg_ticket_overall": "double",
        "digital_value_share_pct": "double",
        "digital_count_share_pct": "double",
        "prev_month_digital_value_share": "double",
        "mom_digital_value_share_pts": "double",
        "mom_digital_value_growth_pct": "double",
        "prev_year_digital_value_share": "double",
        "yoy_digital_value_share_pts": "double",
        "yoy_digital_value_growth_pct": "double"
    }))

    model_bim["model"]["tables"].append(create_table_def("stg_quarantined_records", "stg_quarantined_records.csv", {
        "quarantine_id": "string",
        "batch_run_id": "string",
        "quarantined_at": "dateTime",
        "source_table": "string",
        "record_identifier": "string",
        "reason_code": "string",
        "raw_payload": "string"
    }))

    # 4. Strict Star Schema Dimension Relationships (Many-to-One, No ambiguity, No cycles)
    model_bim["model"]["relationships"] = [
        # fact_payment
        {"name": "rel_pay_date", "fromTable": "fact_payment", "fromColumn": "payment_date_key", "toTable": "dim_date", "toColumn": "date_key"},
        {"name": "rel_pay_loan", "fromTable": "fact_payment", "fromColumn": "loan_key", "toTable": "dim_loan", "toColumn": "loan_key"},
        {"name": "rel_pay_branch", "fromTable": "fact_payment", "fromColumn": "branch_key", "toTable": "dim_branch", "toColumn": "branch_key"},
        {"name": "rel_pay_product", "fromTable": "fact_payment", "fromColumn": "product_key", "toTable": "dim_product", "toColumn": "product_key"},
        {"name": "rel_pay_state", "fromTable": "fact_payment", "fromColumn": "state_key", "toTable": "dim_state", "toColumn": "state_key"},
        {"name": "rel_pay_segment", "fromTable": "fact_payment", "fromColumn": "borrower_segment_key", "toTable": "dim_borrower_segment", "toColumn": "borrower_segment_key"},

        # fact_loan_monthly
        {"name": "rel_snap_date", "fromTable": "fact_loan_monthly", "fromColumn": "snapshot_date_key", "toTable": "dim_date", "toColumn": "date_key"},
        {"name": "rel_snap_loan", "fromTable": "fact_loan_monthly", "fromColumn": "loan_key", "toTable": "dim_loan", "toColumn": "loan_key"},
        {"name": "rel_snap_branch", "fromTable": "fact_loan_monthly", "fromColumn": "branch_key", "toTable": "dim_branch", "toColumn": "branch_key"},
        {"name": "rel_snap_product", "fromTable": "fact_loan_monthly", "fromColumn": "product_key", "toTable": "dim_product", "toColumn": "product_key"},
        {"name": "rel_snap_state", "fromTable": "fact_loan_monthly", "fromColumn": "state_key", "toTable": "dim_state", "toColumn": "state_key"},
        {"name": "rel_snap_segment", "fromTable": "fact_loan_monthly", "fromColumn": "borrower_segment_key", "toTable": "dim_borrower_segment", "toColumn": "borrower_segment_key"},

        # fact_instalment_allocation (Active role: contractual Due Date; Inactive role: Cash Payment Date)
        {"name": "rel_alloc_due_date", "fromTable": "fact_instalment_allocation", "fromColumn": "due_date_key", "toTable": "dim_date", "toColumn": "date_key", "isActive": True},
        {"name": "rel_alloc_pay_date", "fromTable": "fact_instalment_allocation", "fromColumn": "payment_date_key", "toTable": "dim_date", "toColumn": "date_key", "isActive": False},
        {"name": "rel_alloc_loan", "fromTable": "fact_instalment_allocation", "fromColumn": "loan_key", "toTable": "dim_loan", "toColumn": "loan_key", "isActive": True},
        {"name": "rel_alloc_branch", "fromTable": "fact_instalment_allocation", "fromColumn": "branch_key", "toTable": "dim_branch", "toColumn": "branch_key", "isActive": True},
        {"name": "rel_alloc_product", "fromTable": "fact_instalment_allocation", "fromColumn": "product_key", "toTable": "dim_product", "toColumn": "product_key", "isActive": True},
        {"name": "rel_alloc_state", "fromTable": "fact_instalment_allocation", "fromColumn": "state_key", "toTable": "dim_state", "toColumn": "state_key", "isActive": True},

        # kpi_portfolio_health (Direct Many-to-One to Dimensions)
        {"name": "rel_kpi_ph_date", "fromTable": "kpi_portfolio_health", "fromColumn": "snapshot_date_key", "toTable": "dim_date", "toColumn": "date_key", "isActive": True},
        {"name": "rel_kpi_ph_branch", "fromTable": "kpi_portfolio_health", "fromColumn": "branch_id", "toTable": "dim_branch", "toColumn": "branch_id", "isActive": True},
        {"name": "rel_kpi_ph_product", "fromTable": "kpi_portfolio_health", "fromColumn": "product_id", "toTable": "dim_product", "toColumn": "product_id", "isActive": True},
        {"name": "rel_kpi_ph_state", "fromTable": "kpi_portfolio_health", "fromColumn": "state_id", "toTable": "dim_state", "toColumn": "state_id", "isActive": True},

        # kpi_collection_efficiency (Direct Many-to-One to Dimensions)
        {"name": "rel_kpi_ce_date", "fromTable": "kpi_collection_efficiency", "fromColumn": "month_date_key", "toTable": "dim_date", "toColumn": "date_key", "isActive": True},
        {"name": "rel_kpi_ce_branch", "fromTable": "kpi_collection_efficiency", "fromColumn": "branch_id", "toTable": "dim_branch", "toColumn": "branch_id", "isActive": True},
        {"name": "rel_kpi_ce_product", "fromTable": "kpi_collection_efficiency", "fromColumn": "product_id", "toTable": "dim_product", "toColumn": "product_id", "isActive": True},
        {"name": "rel_kpi_ce_state", "fromTable": "kpi_collection_efficiency", "fromColumn": "state_id", "toTable": "dim_state", "toColumn": "state_id", "isActive": True},

        # kpi_digital_collections (Direct Many-to-One to Dimensions)
        {"name": "rel_kpi_dc_date", "fromTable": "kpi_digital_collections", "fromColumn": "month_date_key", "toTable": "dim_date", "toColumn": "date_key", "isActive": True},
        {"name": "rel_kpi_dc_state", "fromTable": "kpi_digital_collections", "fromColumn": "state_id", "toTable": "dim_state", "toColumn": "state_id", "isActive": True},

        # kpi_vintage_curves (Direct Many-to-One to Dimensions)
        {"name": "rel_kpi_vc_date", "fromTable": "kpi_vintage_curves", "fromColumn": "cohort_date_key", "toTable": "dim_date", "toColumn": "date_key", "isActive": True},
        {"name": "rel_kpi_vc_product", "fromTable": "kpi_vintage_curves", "fromColumn": "product_id", "toTable": "dim_product", "toColumn": "product_id", "isActive": True},

        # dim_loan (Inactive snowflake relationships to eliminate multi-path ambiguity with granular facts)
        # Use USERELATIONSHIP(dim_loan[disbursement_date_key], dim_date[date_key]) in DAX for disbursement analysis
        {"name": "rel_loan_disb_date", "fromTable": "dim_loan", "fromColumn": "disbursement_date_key", "toTable": "dim_date", "toColumn": "date_key", "isActive": False},
        {"name": "rel_loan_branch", "fromTable": "dim_loan", "fromColumn": "branch_id", "toTable": "dim_branch", "toColumn": "branch_id", "isActive": False},
        {"name": "rel_loan_product", "fromTable": "dim_loan", "fromColumn": "product_id", "toTable": "dim_product", "toColumn": "product_id", "isActive": False},
        {"name": "rel_loan_state", "fromTable": "dim_loan", "fromColumn": "state_id", "toTable": "dim_state", "toColumn": "state_id", "isActive": False}
    ]

    with open(model_bim_path, "w", encoding="utf-8") as f:
        json.dump(model_bim, f, indent=2)
    logger.info("Wrote %s", model_bim_path)

    # 5. report.json (Visual report definitions for the 5 pages)
    report_json_path = os.path.join(REPORT_DIR, "report.json")
    
    report_def = {
        "config": json.dumps({
            "version": "5.50",
            "themeCollection": {
                "baseTheme": {
                    "name": "FinancialWarehouseTheme",
                    "version": "1.0",
                    "type": 2
                }
            }
        }),
        "layoutOptimization": 0,
        "sections": [
            {
                "id": "Section_PortfolioHealth",
                "name": "Section_PortfolioHealth",
                "displayName": "1. Portfolio Health & Risk",
                "width": 1280,
                "height": 720,
                "visualContainers": [
                    {
                        "x": 20, "y": 15, "width": 800, "height": 45,
                        "config": json.dumps({"singleVisual": {"visualType": "textbox", "objects": {"general": [{"properties": {"paragraphs": [{"textRuns": [{"value": "Financial Inclusion Analytics — Portfolio Health & Delinquency", "textStyle": {"fontSize": "18pt", "fontWeight": "bold", "color": "#0F172A"}}]}]}}]}}})
                    },
                    {
                        "x": 840, "y": 15, "width": 200, "height": 45,
                        "config": json.dumps({"singleVisual": {"visualType": "slicer", "projections": {"Values": [{"queryRef": "dim_date.calendar_year"}]}}})
                    },
                    {
                        "x": 1050, "y": 15, "width": 210, "height": 45,
                        "config": json.dumps({"singleVisual": {"visualType": "slicer", "projections": {"Values": [{"queryRef": "dim_state.state_name"}]}}})
                    },
                    {
                        "x": 20, "y": 70, "width": 230, "height": 90,
                        "config": json.dumps({"singleVisual": {"visualType": "card", "projections": {"Values": [{"queryRef": "_Measures.Active Loans Count"}]}, "objects": {"labels": [{"properties": {"color": "#1E40AF"}}]}}})
                    },
                    {
                        "x": 270, "y": 70, "width": 230, "height": 90,
                        "config": json.dumps({"singleVisual": {"visualType": "card", "projections": {"Values": [{"queryRef": "_Measures.Outstanding Principal (INR Cr)"}]}, "objects": {"labels": [{"properties": {"color": "#0F172A"}}]}}})
                    },
                    {
                        "x": 520, "y": 70, "width": 230, "height": 90,
                        "config": json.dumps({"singleVisual": {"visualType": "card", "projections": {"Values": [{"queryRef": "_Measures.PAR 30 %"}]}, "objects": {"labels": [{"properties": {"color": "#D97706"}}]}}})
                    },
                    {
                        "x": 770, "y": 70, "width": 230, "height": 90,
                        "config": json.dumps({"singleVisual": {"visualType": "card", "projections": {"Values": [{"queryRef": "_Measures.PAR 90 %"}]}, "objects": {"labels": [{"properties": {"color": "#DC2626"}}]}}})
                    },
                    {
                        "x": 1020, "y": 70, "width": 240, "height": 90,
                        "config": json.dumps({"singleVisual": {"visualType": "card", "projections": {"Values": [{"queryRef": "_Measures.Current Period Collection Efficiency %"}]}, "objects": {"labels": [{"properties": {"color": "#059669"}}]}}})
                    },
                    {
                        "x": 20, "y": 170, "width": 600, "height": 280,
                        "config": json.dumps({"singleVisual": {"visualType": "lineChart", "projections": {"Category": [{"queryRef": "dim_date.financial_quarter"}], "Y": [{"queryRef": "_Measures.Total Outstanding Principal"}, {"queryRef": "_Measures.PAR 30 Principal"}]}}})
                    },
                    {
                        "x": 640, "y": 170, "width": 620, "height": 280,
                        "config": json.dumps({"singleVisual": {"visualType": "clusteredColumnChart", "projections": {"Category": [{"queryRef": "dim_date.financial_quarter"}], "Y": [{"queryRef": "_Measures.Current Principal"}, {"queryRef": "_Measures.Delinquency DPD 1-30"}, {"queryRef": "_Measures.Delinquency DPD 31-60"}, {"queryRef": "_Measures.Delinquency DPD 61-90"}, {"queryRef": "_Measures.PAR 90 Principal"}]}}})
                    },
                    {
                        "x": 20, "y": 460, "width": 600, "height": 240,
                        "config": json.dumps({"singleVisual": {"visualType": "pieChart", "projections": {"Category": [{"queryRef": "dim_product.product_name"}], "Y": [{"queryRef": "_Measures.Total Outstanding Principal"}]}}})
                    },
                    {
                        "x": 640, "y": 460, "width": 620, "height": 240,
                        "config": json.dumps({"singleVisual": {"visualType": "pivotTable", "projections": {"Rows": [{"queryRef": "dim_state.state_name"}], "Values": [{"queryRef": "_Measures.Active Loans Count"}, {"queryRef": "_Measures.Outstanding Principal (INR Cr)"}, {"queryRef": "_Measures.PAR 30 %"}, {"queryRef": "_Measures.PAR 90 %"}]}}})
                    }
                ]
            },
            {
                "id": "Section_CollectionEfficiency",
                "name": "Section_CollectionEfficiency",
                "displayName": "2. Collection Efficiency & Billing",
                "width": 1280,
                "height": 720,
                "visualContainers": [
                    {
                        "x": 20, "y": 15, "width": 800, "height": 45,
                        "config": json.dumps({"singleVisual": {"visualType": "textbox", "objects": {"general": [{"properties": {"paragraphs": [{"textRuns": [{"value": "Monthly Collection Efficiency & Arrears Cash Recovery", "textStyle": {"fontSize": "18pt", "fontWeight": "bold", "color": "#0F172A"}}]}]}}]}}})
                    },
                    {
                        "x": 840, "y": 15, "width": 200, "height": 45,
                        "config": json.dumps({"singleVisual": {"visualType": "slicer", "projections": {"Values": [{"queryRef": "dim_branch.branch_name"}]}}})
                    },
                    {
                        "x": 1050, "y": 15, "width": 210, "height": 45,
                        "config": json.dumps({"singleVisual": {"visualType": "slicer", "projections": {"Values": [{"queryRef": "dim_product.product_name"}]}}})
                    },
                    {
                        "x": 20, "y": 70, "width": 230, "height": 90,
                        "config": json.dumps({"singleVisual": {"visualType": "card", "projections": {"Values": [{"queryRef": "_Measures.Scheduled Billing Due"}]}}})
                    },
                    {
                        "x": 270, "y": 70, "width": 230, "height": 90,
                        "config": json.dumps({"singleVisual": {"visualType": "card", "projections": {"Values": [{"queryRef": "_Measures.Current Period Collected"}]}}})
                    },
                    {
                        "x": 520, "y": 70, "width": 230, "height": 90,
                        "config": json.dumps({"singleVisual": {"visualType": "card", "projections": {"Values": [{"queryRef": "_Measures.Arrears Collected"}]}}})
                    },
                    {
                        "x": 770, "y": 70, "width": 230, "height": 90,
                        "config": json.dumps({"singleVisual": {"visualType": "card", "projections": {"Values": [{"queryRef": "_Measures.Advance Collected"}]}}})
                    },
                    {
                        "x": 1020, "y": 70, "width": 240, "height": 90,
                        "config": json.dumps({"singleVisual": {"visualType": "card", "projections": {"Values": [{"queryRef": "_Measures.Current Period Collection Efficiency %"}]}}})
                    },
                    {
                        "x": 20, "y": 170, "width": 700, "height": 530,
                        "config": json.dumps({"singleVisual": {"visualType": "lineClusteredColumnComboChart", "projections": {"Category": [{"queryRef": "kpi_collection_efficiency.year_month"}], "ColumnValues": [{"queryRef": "_Measures.Scheduled Billing Due"}, {"queryRef": "_Measures.Total Cash Collected"}], "LineValues": [{"queryRef": "_Measures.Current Period Collection Efficiency %"}]}}})
                    },
                    {
                        "x": 740, "y": 170, "width": 520, "height": 530,
                        "config": json.dumps({"singleVisual": {"visualType": "pivotTable", "projections": {"Rows": [{"queryRef": "dim_branch.branch_name"}], "Values": [{"queryRef": "_Measures.Scheduled Billing Due"}, {"queryRef": "_Measures.Current Period Collected"}, {"queryRef": "_Measures.Current Period Collection Efficiency %"}]}}})
                    }
                ]
            },
            {
                "id": "Section_VintageCurves",
                "name": "Section_VintageCurves",
                "displayName": "3. Repayment Vintage Curves",
                "width": 1280,
                "height": 720,
                "visualContainers": [
                    {
                        "x": 20, "y": 15, "width": 800, "height": 45,
                        "config": json.dumps({"singleVisual": {"visualType": "textbox", "objects": {"general": [{"properties": {"paragraphs": [{"textRuns": [{"value": "Cohort Repayment Vintage Analysis (Months-on-Book 1 to 24)", "textStyle": {"fontSize": "18pt", "fontWeight": "bold", "color": "#0F172A"}}]}]}}]}}})
                    },
                    {
                        "x": 840, "y": 15, "width": 420, "height": 45,
                        "config": json.dumps({"singleVisual": {"visualType": "slicer", "projections": {"Values": [{"queryRef": "dim_product.product_name"}]}}})
                    },
                    {
                        "x": 20, "y": 70, "width": 1240, "height": 340,
                        "config": json.dumps({"singleVisual": {"visualType": "lineChart", "projections": {"Category": [{"queryRef": "kpi_vintage_curves.month_on_book"}], "Series": [{"queryRef": "kpi_vintage_curves.cohort_month"}], "Y": [{"queryRef": "_Measures.Vintage Repayment Rate %"}]}}})
                    },
                    {
                        "x": 20, "y": 420, "width": 1240, "height": 280,
                        "config": json.dumps({"singleVisual": {"visualType": "pivotTable", "projections": {"Rows": [{"queryRef": "kpi_vintage_curves.cohort_month"}], "Columns": [{"queryRef": "kpi_vintage_curves.month_on_book"}], "Values": [{"queryRef": "_Measures.Vintage Repayment Rate %"}]}}})
                    }
                ]
            },
            {
                "id": "Section_DigitalCollections",
                "name": "Section_DigitalCollections",
                "displayName": "4. Digital Collections & Transformation",
                "width": 1280,
                "height": 720,
                "visualContainers": [
                    {
                        "x": 20, "y": 15, "width": 800, "height": 45,
                        "config": json.dumps({"singleVisual": {"visualType": "textbox", "objects": {"general": [{"properties": {"paragraphs": [{"textRuns": [{"value": "Digital Collections & Cash-to-Digital UPI Transition", "textStyle": {"fontSize": "18pt", "fontWeight": "bold", "color": "#0F172A"}}]}]}}]}}})
                    },
                    {
                        "x": 840, "y": 15, "width": 420, "height": 45,
                        "config": json.dumps({"singleVisual": {"visualType": "slicer", "projections": {"Values": [{"queryRef": "dim_state.state_name"}]}}})
                    },
                    {
                        "x": 20, "y": 70, "width": 230, "height": 90,
                        "config": json.dumps({"singleVisual": {"visualType": "card", "projections": {"Values": [{"queryRef": "_Measures.Digital Value Share %"}]}}})
                    },
                    {
                        "x": 270, "y": 70, "width": 230, "height": 90,
                        "config": json.dumps({"singleVisual": {"visualType": "card", "projections": {"Values": [{"queryRef": "_Measures.Digital Count Share %"}]}}})
                    },
                    {
                        "x": 520, "y": 70, "width": 230, "height": 90,
                        "config": json.dumps({"singleVisual": {"visualType": "card", "projections": {"Values": [{"queryRef": "_Measures.UPI Value"}]}}})
                    },
                    {
                        "x": 770, "y": 70, "width": 230, "height": 90,
                        "config": json.dumps({"singleVisual": {"visualType": "card", "projections": {"Values": [{"queryRef": "_Measures.Bank Transfer Value"}]}}})
                    },
                    {
                        "x": 1020, "y": 70, "width": 240, "height": 90,
                        "config": json.dumps({"singleVisual": {"visualType": "card", "projections": {"Values": [{"queryRef": "_Measures.Cash Collections Value"}]}}})
                    },
                    {
                        "x": 20, "y": 170, "width": 700, "height": 530,
                        "config": json.dumps({"singleVisual": {"visualType": "stackedAreaChart", "projections": {"Category": [{"queryRef": "kpi_digital_collections.year_month"}], "Y": [{"queryRef": "_Measures.UPI Value"}, {"queryRef": "_Measures.Bank Transfer Value"}, {"queryRef": "_Measures.Cash Collections Value"}]}}})
                    },
                    {
                        "x": 740, "y": 170, "width": 520, "height": 530,
                        "config": json.dumps({"singleVisual": {"visualType": "pivotTable", "projections": {"Rows": [{"queryRef": "dim_state.state_name"}], "Values": [{"queryRef": "_Measures.Total Collections Value"}, {"queryRef": "_Measures.Digital Collections Value"}, {"queryRef": "_Measures.Digital Value Share %"}]}}})
                    }
                ]
            },
            {
                "id": "Section_DataQuality",
                "name": "Section_DataQuality",
                "displayName": "5. Data Quality & Quarantine Firewall",
                "width": 1280,
                "height": 720,
                "visualContainers": [
                    {
                        "x": 20, "y": 15, "width": 1240, "height": 45,
                        "config": json.dumps({"singleVisual": {"visualType": "textbox", "objects": {"general": [{"properties": {"paragraphs": [{"textRuns": [{"value": "Data Quality Quarantine Firewall & Anomaly Surveillance", "textStyle": {"fontSize": "18pt", "fontWeight": "bold", "color": "#0F172A"}}]}]}}]}}})
                    },
                    {
                        "x": 20, "y": 70, "width": 230, "height": 90,
                        "config": json.dumps({"singleVisual": {"visualType": "card", "projections": {"Values": [{"queryRef": "_Measures.Total Quarantined Records"}]}}})
                    },
                    {
                        "x": 270, "y": 70, "width": 230, "height": 90,
                        "config": json.dumps({"singleVisual": {"visualType": "card", "projections": {"Values": [{"queryRef": "_Measures.Negative Amount Anomalies"}]}}})
                    },
                    {
                        "x": 520, "y": 70, "width": 230, "height": 90,
                        "config": json.dumps({"singleVisual": {"visualType": "card", "projections": {"Values": [{"queryRef": "_Measures.Pre-dated Payment Anomalies"}]}}})
                    },
                    {
                        "x": 770, "y": 70, "width": 230, "height": 90,
                        "config": json.dumps({"singleVisual": {"visualType": "card", "projections": {"Values": [{"queryRef": "_Measures.Excess Payment Anomalies"}]}}})
                    },
                    {
                        "x": 1020, "y": 70, "width": 240, "height": 90,
                        "config": json.dumps({"singleVisual": {"visualType": "card", "projections": {"Values": [{"queryRef": "_Measures.Total Quarantined Records"}]}}})
                    },
                    {
                        "x": 20, "y": 170, "width": 500, "height": 530,
                        "config": json.dumps({"singleVisual": {"visualType": "pieChart", "projections": {"Category": [{"queryRef": "stg_quarantined_records.reason_code"}], "Y": [{"queryRef": "_Measures.Total Quarantined Records"}]}}})
                    },
                    {
                        "x": 540, "y": 170, "width": 720, "height": 530,
                        "config": json.dumps({"singleVisual": {"visualType": "tableEx", "projections": {"Values": [{"queryRef": "stg_quarantined_records.quarantine_id"}, {"queryRef": "stg_quarantined_records.source_table"}, {"queryRef": "stg_quarantined_records.record_identifier"}, {"queryRef": "stg_quarantined_records.reason_code"}, {"queryRef": "stg_quarantined_records.quarantined_at"}]}}})
                    }
                ]
            }
        ]
    }

    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(report_def, f, indent=2)
    logger.info("Wrote %s", report_json_path)

    logger.info("Power BI Project (PBIP) generation complete!")

if __name__ == "__main__":
    generate_pbip()
