"""
Generates the complete, professional, interactive five-page Power BI report.json
for Financial_Inclusion_Analytics.Report.
"""

import os
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_PATH = os.path.join(PROJECT_ROOT, "powerbi", "Financial_Inclusion_Analytics.Report", "report.json")

def make_textbox(x, y, w, h, text, font_size="16pt", font_weight="bold", color="#0F172A"):
    config = {
        "singleVisual": {
            "visualType": "textbox",
            "objects": {
                "general": [{
                    "properties": {
                        "paragraphs": [{
                            "textRuns": [{
                                "value": text,
                                "textStyle": {
                                    "fontSize": font_size,
                                    "fontWeight": font_weight,
                                    "color": color
                                }
                            }]
                        }]
                    }
                }]
            }
        }
    }
    return {"x": x, "y": y, "width": w, "height": h, "z": 0, "config": json.dumps(config)}

def make_slicer(x, y, w, h, query_ref):
    config = {
        "singleVisual": {
            "visualType": "slicer",
            "projections": {
                "Values": [{"queryRef": query_ref}]
            }
        }
    }
    return {"x": x, "y": y, "width": w, "height": h, "z": 10, "config": json.dumps(config)}

def make_card(x, y, w, h, query_ref, title_text, label_color="#1E40AF"):
    config = {
        "singleVisual": {
            "visualType": "card",
            "projections": {
                "Values": [{"queryRef": query_ref}]
            },
            "objects": {
                "title": [{
                    "properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "text": {"expr": {"Literal": {"Value": f"'{title_text}'"}}}
                    }
                }],
                "labels": [{
                    "properties": {
                        "color": label_color
                    }
                }]
            }
        }
    }
    return {"x": x, "y": y, "width": w, "height": h, "z": 5, "config": json.dumps(config)}

def make_line_chart(x, y, w, h, category_ref, y_refs, title_text, series_ref=None):
    projections = {
        "Category": [{"queryRef": category_ref}],
        "Y": [{"queryRef": yr} for yr in y_refs]
    }
    if series_ref:
        projections["Series"] = [{"queryRef": series_ref}]
    
    config = {
        "singleVisual": {
            "visualType": "lineChart",
            "projections": projections,
            "objects": {
                "title": [{
                    "properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "text": {"expr": {"Literal": {"Value": f"'{title_text}'"}}}
                    }
                }]
            }
        }
    }
    return {"x": x, "y": y, "width": w, "height": h, "z": 2, "config": json.dumps(config)}

def make_column_chart(x, y, w, h, category_ref, y_refs, title_text):
    config = {
        "singleVisual": {
            "visualType": "clusteredColumnChart",
            "projections": {
                "Category": [{"queryRef": category_ref}],
                "Y": [{"queryRef": yr} for yr in y_refs]
            },
            "objects": {
                "title": [{
                    "properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "text": {"expr": {"Literal": {"Value": f"'{title_text}'"}}}
                    }
                }]
            }
        }
    }
    return {"x": x, "y": y, "width": w, "height": h, "z": 2, "config": json.dumps(config)}

def make_pie_chart(x, y, w, h, category_ref, y_ref, title_text):
    config = {
        "singleVisual": {
            "visualType": "pieChart",
            "projections": {
                "Category": [{"queryRef": category_ref}],
                "Y": [{"queryRef": y_ref}]
            },
            "objects": {
                "title": [{
                    "properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "text": {"expr": {"Literal": {"Value": f"'{title_text}'"}}}
                    }
                }]
            }
        }
    }
    return {"x": x, "y": y, "width": w, "height": h, "z": 2, "config": json.dumps(config)}

def make_combo_chart(x, y, w, h, category_ref, col_refs, line_refs, title_text):
    config = {
        "singleVisual": {
            "visualType": "lineClusteredColumnComboChart",
            "projections": {
                "Category": [{"queryRef": category_ref}],
                "ColumnValues": [{"queryRef": cr} for cr in col_refs],
                "LineValues": [{"queryRef": lr} for lr in line_refs]
            },
            "objects": {
                "title": [{
                    "properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "text": {"expr": {"Literal": {"Value": f"'{title_text}'"}}}
                    }
                }]
            }
        }
    }
    return {"x": x, "y": y, "width": w, "height": h, "z": 2, "config": json.dumps(config)}

def make_stacked_area_chart(x, y, w, h, category_ref, y_refs, title_text):
    config = {
        "singleVisual": {
            "visualType": "stackedAreaChart",
            "projections": {
                "Category": [{"queryRef": category_ref}],
                "Y": [{"queryRef": yr} for yr in y_refs]
            },
            "objects": {
                "title": [{
                    "properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "text": {"expr": {"Literal": {"Value": f"'{title_text}'"}}}
                    }
                }]
            }
        }
    }
    return {"x": x, "y": y, "width": w, "height": h, "z": 2, "config": json.dumps(config)}

def make_matrix(x, y, w, h, row_refs, val_refs, title_text, col_refs=None):
    projections = {
        "Rows": [{"queryRef": rr} for rr in row_refs],
        "Values": [{"queryRef": vr} for vr in val_refs]
    }
    if col_refs:
        projections["Columns"] = [{"queryRef": cr} for cr in col_refs]
    
    config = {
        "singleVisual": {
            "visualType": "pivotTable",
            "projections": projections,
            "objects": {
                "title": [{
                    "properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "text": {"expr": {"Literal": {"Value": f"'{title_text}'"}}}
                    }
                }]
            }
        }
    }
    return {"x": x, "y": y, "width": w, "height": h, "z": 2, "config": json.dumps(config)}

def make_table(x, y, w, h, val_refs, title_text):
    config = {
        "singleVisual": {
            "visualType": "tableEx",
            "projections": {
                "Values": [{"queryRef": vr} for vr in val_refs]
            },
            "objects": {
                "title": [{
                    "properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "text": {"expr": {"Literal": {"Value": f"'{title_text}'"}}}
                    }
                }]
            }
        }
    }
    return {"x": x, "y": y, "width": w, "height": h, "z": 2, "config": json.dumps(config)}

def build_report():
    sections = [
        # -------------------------------------------------------------
        # PAGE 1: PORTFOLIO HEALTH & RISK
        # -------------------------------------------------------------
        {
            "id": "Section_PortfolioHealth",
            "name": "Section_PortfolioHealth",
            "displayName": "1. Portfolio Health & Risk",
            "width": 1280,
            "height": 720,
            "visualContainers": [
                make_textbox(20, 10, 540, 45, "Financial Inclusion Analytics — Portfolio Health & Risk Exposure"),
                make_slicer(580, 10, 160, 45, "dim_date.calendar_year"),
                make_slicer(750, 10, 160, 45, "dim_state.state_name"),
                make_slicer(920, 10, 170, 45, "dim_branch.branch_name"),
                make_slicer(1100, 10, 160, 45, "dim_product.product_name"),
                
                # 6 KPI Cards
                make_card(20, 65, 195, 85, "_Measures.Total Loans Count", "Total Portfolio Loans", "#1E40AF"),
                make_card(230, 65, 195, 85, "_Measures.Active Loans Count", "Active Loans", "#0F172A"),
                make_card(440, 65, 195, 85, "_Measures.Disbursed Principal (INR Cr)", "Total Disbursed (₹ Cr)", "#0D9488"),
                make_card(650, 65, 195, 85, "_Measures.Outstanding Principal (INR Cr)", "Outstanding Principal (₹ Cr)", "#2563EB"),
                make_card(860, 65, 195, 85, "_Measures.PAR 30 %", "PAR 30 Rate", "#D97706"),
                make_card(1070, 65, 190, 85, "_Measures.PAR 90 %", "PAR 90 Rate (NPL)", "#DC2626"),
                
                # Visuals
                make_line_chart(20, 160, 610, 270, "dim_date.financial_quarter", 
                                ["_Measures.Total Outstanding Principal", "_Measures.PAR 30 Principal"], 
                                "Monthly Portfolio Outstanding & PAR 30 Balance Trend"),
                make_column_chart(650, 160, 610, 270, "dim_date.financial_quarter",
                                  ["_Measures.Current Principal", "_Measures.Delinquency DPD 1-30", "_Measures.Delinquency DPD 31-60", "_Measures.Delinquency DPD 61-90", "_Measures.PAR 90 Principal"],
                                  "Delinquency Aging by DPD Buckets (Current vs Overdue)"),
                make_pie_chart(20, 440, 500, 265, "dim_product.product_name", 
                               "_Measures.Total Outstanding Principal", 
                                "Portfolio Exposure by Product Category"),
                make_matrix(540, 440, 720, 265, ["dim_state.state_name"], 
                            ["_Measures.Active Loans Count", "_Measures.Outstanding Principal (INR Cr)", "_Measures.PAR 30 %", "_Measures.PAR 90 %"], 
                            "State-wise Portfolio Risk & Outstanding Balance Breakdown")
            ]
        },
        
        # -------------------------------------------------------------
        # PAGE 2: COLLECTION EFFICIENCY & BILLING
        # -------------------------------------------------------------
        {
            "id": "Section_CollectionEfficiency",
            "name": "Section_CollectionEfficiency",
            "displayName": "2. Collection Efficiency & Billing",
            "width": 1280,
            "height": 720,
            "visualContainers": [
                make_textbox(20, 10, 540, 45, "Repayment Collection Performance & Cash Recovery Billing"),
                make_slicer(580, 10, 160, 45, "kpi_collection_efficiency.year_month"),
                make_slicer(750, 10, 160, 45, "dim_state.state_name"),
                make_slicer(920, 10, 170, 45, "dim_branch.branch_name"),
                make_slicer(1100, 10, 160, 45, "dim_product.product_name"),
                
                # 6 KPI Cards
                make_card(20, 65, 195, 85, "_Measures.Scheduled Billing Due", "Scheduled Billing Due", "#0F172A"),
                make_card(230, 65, 195, 85, "_Measures.Total Cash Collected", "Total Cash Collected", "#059669"),
                make_card(440, 65, 195, 85, "_Measures.Current Period Collected", "Current Dues Collected", "#2563EB"),
                make_card(650, 65, 195, 85, "_Measures.Arrears Collected", "Arrears Overdue Collected", "#D97706"),
                make_card(860, 65, 195, 85, "_Measures.Advance Collected", "Advance Prepayments", "#7C3AED"),
                make_card(1070, 65, 190, 85, "_Measures.Current Period Collection Efficiency %", "Current Billing Efficiency %", "#059669"),
                
                # Visuals
                make_combo_chart(20, 160, 710, 545, "kpi_collection_efficiency.year_month",
                                 ["_Measures.Scheduled Billing Due", "_Measures.Total Cash Collected"],
                                 ["_Measures.Current Period Collection Efficiency %"],
                                 "Monthly Scheduled Billing Dues vs Cash Recovered & Efficiency Ratio"),
                make_matrix(750, 160, 510, 545, ["dim_branch.branch_name"],
                            ["_Measures.Scheduled Billing Due", "_Measures.Current Period Collected", "_Measures.Arrears Collected", "_Measures.Current Period Collection Efficiency %"],
                            "Operational Branch Collection & Arrears Performance Matrix")
            ]
        },
        
        # -------------------------------------------------------------
        # PAGE 3: REPAYMENT VINTAGE CURVES
        # -------------------------------------------------------------
        {
            "id": "Section_VintageCurves",
            "name": "Section_VintageCurves",
            "displayName": "3. Repayment Vintage Curves",
            "width": 1280,
            "height": 720,
            "visualContainers": [
                make_textbox(20, 10, 620, 45, "Disbursement Cohort Repayment Vintage Analysis (MOB 1 to 24)"),
                make_slicer(660, 10, 290, 45, "dim_product.product_name"),
                make_slicer(970, 10, 290, 45, "kpi_vintage_curves.cohort_month"),
                
                # 4 KPI Cards
                make_card(20, 65, 295, 85, "_Measures.Total Disbursed Principal", "Cohort Disbursed Principal", "#1E40AF"),
                make_card(335, 65, 295, 85, "_Measures.Cumulative Amount Paid (Vintage)", "Cumulative Cash Repaid", "#059669"),
                make_card(650, 65, 295, 85, "_Measures.Cumulative Scheduled Due (Vintage)", "Cumulative Scheduled Dues", "#0F172A"),
                make_card(965, 65, 295, 85, "_Measures.Vintage Repayment Rate %", "Portfolio Vintage Repayment Rate %", "#2563EB"),
                
                # Visuals
                make_line_chart(20, 160, 1240, 275, "kpi_vintage_curves.month_on_book",
                                ["_Measures.Vintage Repayment Rate %"],
                                "Repayment Vintage Curve: Cumulative Repayment Rate % by Month-on-Book",
                                series_ref="kpi_vintage_curves.cohort_month"),
                make_matrix(20, 445, 1240, 260, ["kpi_vintage_curves.cohort_month"],
                            ["_Measures.Vintage Repayment Rate %"],
                            "Cohort Repayment Performance Matrix (Cohort Month × Months on Book)",
                            col_refs=["kpi_vintage_curves.month_on_book"])
            ]
        },
        
        # -------------------------------------------------------------
        # PAGE 4: DIGITAL COLLECTIONS GROWTH
        # -------------------------------------------------------------
        {
            "id": "Section_DigitalCollections",
            "name": "Section_DigitalCollections",
            "displayName": "4. Digital Collections & Transformation",
            "width": 1280,
            "height": 720,
            "visualContainers": [
                make_textbox(20, 10, 540, 45, "Digital Collections Growth & Payment Channel Transformation"),
                make_slicer(580, 10, 220, 45, "dim_state.state_name"),
                make_slicer(815, 10, 220, 45, "kpi_digital_collections.year_month"),
                make_slicer(1050, 10, 210, 45, "fact_payment.payment_channel"),
                
                # 7 KPI Cards
                make_card(20, 65, 165, 85, "_Measures.Digital Collections Value", "Digital Value", "#0D9488"),
                make_card(199, 65, 165, 85, "_Measures.Digital Transactions Count", "Digital Txns", "#2563EB"),
                make_card(378, 65, 165, 85, "_Measures.Digital Value Share %", "Digital Share %", "#059669"),
                make_card(557, 65, 165, 85, "_Measures.Digital Count Share %", "Txn Share %", "#059669"),
                make_card(736, 65, 165, 85, "_Measures.UPI Value", "UPI Value", "#4F46E5"),
                make_card(915, 65, 165, 85, "_Measures.Bank Transfer Value", "Net Banking", "#0284C7"),
                make_card(1094, 65, 166, 85, "_Measures.Average Digital Payment Amount", "Avg Digital Ticket", "#0F172A"),
                
                # Visuals
                make_stacked_area_chart(20, 160, 710, 545, "kpi_digital_collections.year_month",
                                        ["_Measures.UPI Value", "_Measures.Bank Transfer Value", "_Measures.Cash Collections Value"],
                                        "Monthly Cash vs UPI vs Bank Transfer Channel Volume Distribution"),
                make_matrix(750, 160, 510, 545, ["dim_state.state_name"],
                            ["_Measures.Total Collections Value", "_Measures.Digital Collections Value", "_Measures.Digital Value Share %", "_Measures.Digital Count Share %"],
                            "State-wise Digital Adoption & Channel Volume Breakdown")
            ]
        },
        
        # -------------------------------------------------------------
        # PAGE 5: DATA QUALITY MONITORING
        # -------------------------------------------------------------
        {
            "id": "Section_DataQuality",
            "name": "Section_DataQuality",
            "displayName": "5. Data Quality & Quarantine Firewall",
            "width": 1280,
            "height": 720,
            "visualContainers": [
                make_textbox(20, 10, 620, 45, "Data Quality Quarantine Firewall & Ingestion Anomaly Surveillance"),
                make_slicer(660, 10, 290, 45, "stg_quarantined_records.source_table"),
                make_slicer(970, 10, 290, 45, "stg_quarantined_records.reason_code"),
                
                # 5 KPI Cards
                make_card(20, 65, 230, 85, "_Measures.Total Raw Records", "Raw Ingestion Payloads", "#0F172A"),
                make_card(270, 65, 230, 85, "_Measures.Total Clean Records", "Clean Verified Records", "#059669"),
                make_card(520, 65, 230, 85, "_Measures.Total Quarantined Records", "Quarantined Anomalies", "#DC2626"),
                make_card(770, 65, 230, 85, "_Measures.Data Quality Pass Rate %", "Ingestion Pass Rate %", "#2563EB"),
                make_card(1020, 65, 240, 85, "_Measures.Issue Categories Count", "Active Anomaly Categories", "#D97706"),
                
                # Visuals
                make_pie_chart(20, 160, 480, 545, "stg_quarantined_records.reason_code",
                               "_Measures.Total Quarantined Records",
                               "Distribution of Quarantined Anomalies by Reason Code"),
                make_table(520, 160, 740, 545,
                           ["stg_quarantined_records.quarantine_id", "stg_quarantined_records.batch_run_id", "stg_quarantined_records.source_table", "stg_quarantined_records.reason_code", "stg_quarantined_records.record_identifier", "stg_quarantined_records.quarantined_at"],
                           "Audit Trail of Quarantined Payloads (Source, Identifier & Reason Code)")
            ]
        }
    ]
    
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
        "sections": sections
    }
    
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report_def, f, indent=2)
    
    print(f"Successfully generated complete report.json at: {REPORT_PATH}")
    print(f"Total Sections: {len(sections)}")
    for s in sections:
        print(f"  {s['displayName']}: {len(s['visualContainers'])} visuals")

if __name__ == "__main__":
    build_report()
