"""
Generates the complete, professional, interactive five-page Power BI report.json
with full config, prototypeQuery, query, and dataTransforms bindings for every visual.
This ensures Power BI Desktop immediately queries the model and displays live data
instead of blank visual placeholders.
"""

import os
import json
import uuid

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_PATH = os.path.join(PROJECT_ROOT, "powerbi", "Financial_Inclusion_Analytics.Report", "report.json")

def gen_id():
    return str(uuid.uuid4()).replace("-", "")[:20]

def build_textbox(x, y, w, h, text, font_size="16pt", font_weight="bold", color="#0F172A"):
    config = {
        "name": gen_id(),
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

def build_slicer(x, y, w, h, table_name, col_name, title_text=None):
    v_id = gen_id()
    query_ref = f"{table_name}.{col_name}"
    
    from_clause = [{"Name": "d", "Entity": table_name, "Type": 0}]
    select_clause = [{
        "Column": {
            "Expression": {"SourceRef": {"Source": "d"}},
            "Property": col_name
        },
        "Name": query_ref
    }]
    
    prototype_query = {
        "Version": 2,
        "From": from_clause,
        "Select": select_clause
    }
    
    config = {
        "name": v_id,
        "singleVisual": {
            "visualType": "slicer",
            "projections": {
                "Values": [{"queryRef": query_ref}]
            },
            "prototypeQuery": prototype_query
        }
    }
    if title_text:
        config["singleVisual"]["objects"] = {
            "title": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": f"'{title_text}'"}}}
                }
            }]
        }
        
    query = {
        "Commands": [{
            "SemanticQueryDataShapeCommand": {
                "Query": prototype_query,
                "Binding": {
                    "Primary": {
                        "Groupings": [{"Projections": [0]}]
                    }
                }
            }
        }]
    }
    
    data_transforms = {
        "projectionOrdering": {"Values": [0]},
        "queryMetadata": {
            "Select": [{
                "Restatement": col_name,
                "Name": query_ref,
                "Type": 2048
            }]
        }
    }
    
    return {
        "x": x, "y": y, "width": w, "height": h, "z": 10,
        "config": json.dumps(config),
        "query": json.dumps(query),
        "dataTransforms": json.dumps(data_transforms)
    }

def build_card(x, y, w, h, measure_name, title_text, label_color="#1E40AF"):
    v_id = gen_id()
    query_ref = f"_Measures.{measure_name}"
    
    from_clause = [{"Name": "m", "Entity": "_Measures", "Type": 0}]
    select_clause = [{
        "Measure": {
            "Expression": {"SourceRef": {"Source": "m"}},
            "Property": measure_name
        },
        "Name": query_ref
    }]
    
    prototype_query = {
        "Version": 2,
        "From": from_clause,
        "Select": select_clause
    }
    
    config = {
        "name": v_id,
        "singleVisual": {
            "visualType": "card",
            "projections": {
                "Values": [{"queryRef": query_ref}]
            },
            "prototypeQuery": prototype_query,
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
    
    query = {
        "Commands": [{
            "SemanticQueryDataShapeCommand": {
                "Query": prototype_query,
                "Binding": {
                    "Primary": {
                        "Groupings": [{"Projections": [0]}]
                    }
                }
            }
        }]
    }
    
    data_transforms = {
        "projectionOrdering": {"Values": [0]},
        "queryMetadata": {
            "Select": [{
                "Restatement": measure_name,
                "Name": query_ref,
                "Type": 1
            }]
        }
    }
    
    return {
        "x": x, "y": y, "width": w, "height": h, "z": 5,
        "config": json.dumps(config),
        "query": json.dumps(query),
        "dataTransforms": json.dumps(data_transforms)
    }

def build_line_chart(x, y, w, h, cat_table, cat_col, measures_list, title_text, series_table=None, series_col=None):
    v_id = gen_id()
    cat_ref = f"{cat_table}.{cat_col}"
    
    from_clause = [{"Name": "c", "Entity": cat_table, "Type": 0}]
    from_clause.append({"Name": "m", "Entity": "_Measures", "Type": 0})
    
    select_clause = [{
        "Column": {
            "Expression": {"SourceRef": {"Source": "c"}},
            "Property": cat_col
        },
        "Name": cat_ref
    }]
    
    projections = {
        "Category": [{"queryRef": cat_ref, "active": True}]
    }
    
    proj_ordering = {"Category": [0]}
    query_meta_select = [{
        "Restatement": cat_col,
        "Name": cat_ref,
        "Type": 2048
    }]
    
    curr_idx = 1
    if series_table and series_col:
        series_ref = f"{series_table}.{series_col}"
        if series_table != cat_table:
            from_clause.append({"Name": "s", "Entity": series_table, "Type": 0})
            s_source = "s"
        else:
            s_source = "c"
        select_clause.append({
            "Column": {
                "Expression": {"SourceRef": {"Source": s_source}},
                "Property": series_col
            },
            "Name": series_ref
        })
        projections["Series"] = [{"queryRef": series_ref}]
        proj_ordering["Series"] = [curr_idx]
        query_meta_select.append({
            "Restatement": series_col,
            "Name": series_ref,
            "Type": 2048
        })
        curr_idx += 1
        
    y_projs = []
    y_indices = []
    for mname in measures_list:
        m_ref = f"_Measures.{mname}"
        select_clause.append({
            "Measure": {
                "Expression": {"SourceRef": {"Source": "m"}},
                "Property": mname
            },
            "Name": m_ref
        })
        y_projs.append({"queryRef": m_ref})
        y_indices.append(curr_idx)
        query_meta_select.append({
            "Restatement": mname,
            "Name": m_ref,
            "Type": 1
        })
        curr_idx += 1
        
    projections["Y"] = y_projs
    proj_ordering["Y"] = y_indices
    
    prototype_query = {
        "Version": 2,
        "From": from_clause,
        "Select": select_clause
    }
    
    config = {
        "name": v_id,
        "singleVisual": {
            "visualType": "lineChart",
            "projections": projections,
            "prototypeQuery": prototype_query,
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
    
    query = {
        "Commands": [{
            "SemanticQueryDataShapeCommand": {
                "Query": prototype_query,
                "Binding": {
                    "Primary": {
                        "Groupings": [{"Projections": list(range(len(select_clause)))}]
                    }
                }
            }
        }]
    }
    
    data_transforms = {
        "projectionOrdering": proj_ordering,
        "queryMetadata": {
            "Select": query_meta_select
        }
    }
    
    return {
        "x": x, "y": y, "width": w, "height": h, "z": 2,
        "config": json.dumps(config),
        "query": json.dumps(query),
        "dataTransforms": json.dumps(data_transforms)
    }

def build_column_chart(x, y, w, h, cat_table, cat_col, measures_list, title_text):
    v_id = gen_id()
    cat_ref = f"{cat_table}.{cat_col}"
    
    from_clause = [
        {"Name": "c", "Entity": cat_table, "Type": 0},
        {"Name": "m", "Entity": "_Measures", "Type": 0}
    ]
    
    select_clause = [{
        "Column": {
            "Expression": {"SourceRef": {"Source": "c"}},
            "Property": cat_col
        },
        "Name": cat_ref
    }]
    
    y_projs = []
    y_indices = []
    query_meta_select = [{
        "Restatement": cat_col,
        "Name": cat_ref,
        "Type": 2048
    }]
    
    for i, mname in enumerate(measures_list, 1):
        m_ref = f"_Measures.{mname}"
        select_clause.append({
            "Measure": {
                "Expression": {"SourceRef": {"Source": "m"}},
                "Property": mname
            },
            "Name": m_ref
        })
        y_projs.append({"queryRef": m_ref})
        y_indices.append(i)
        query_meta_select.append({
            "Restatement": mname,
            "Name": m_ref,
            "Type": 1
        })
        
    projections = {
        "Category": [{"queryRef": cat_ref, "active": True}],
        "Y": y_projs
    }
    
    prototype_query = {
        "Version": 2,
        "From": from_clause,
        "Select": select_clause
    }
    
    config = {
        "name": v_id,
        "singleVisual": {
            "visualType": "clusteredColumnChart",
            "projections": projections,
            "prototypeQuery": prototype_query,
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
    
    query = {
        "Commands": [{
            "SemanticQueryDataShapeCommand": {
                "Query": prototype_query,
                "Binding": {
                    "Primary": {
                        "Groupings": [{"Projections": list(range(len(select_clause)))}]
                    }
                }
            }
        }]
    }
    
    data_transforms = {
        "projectionOrdering": {
            "Category": [0],
            "Y": y_indices
        },
        "queryMetadata": {
            "Select": query_meta_select
        }
    }
    
    return {
        "x": x, "y": y, "width": w, "height": h, "z": 2,
        "config": json.dumps(config),
        "query": json.dumps(query),
        "dataTransforms": json.dumps(data_transforms)
    }

def build_pie_chart(x, y, w, h, cat_table, cat_col, val_table, val_prop, title_text, is_measure=True):
    v_id = gen_id()
    cat_ref = f"{cat_table}.{cat_col}"
    val_ref = f"{val_table}.{val_prop}"
    
    from_clause = [{"Name": "c", "Entity": cat_table, "Type": 0}]
    if val_table != cat_table:
        from_clause.append({"Name": "v", "Entity": val_table, "Type": 0})
        v_source = "v"
    else:
        v_source = "c"
        
    select_clause = [
        {
            "Column": {
                "Expression": {"SourceRef": {"Source": "c"}},
                "Property": cat_col
            },
            "Name": cat_ref
        }
    ]
    
    if is_measure:
        select_clause.append({
            "Measure": {
                "Expression": {"SourceRef": {"Source": v_source}},
                "Property": val_prop
            },
            "Name": val_ref
        })
        val_type = 1
    else:
        select_clause.append({
            "Column": {
                "Expression": {"SourceRef": {"Source": v_source}},
                "Property": val_prop
            },
            "Name": val_ref
        })
        val_type = 2048
        
    prototype_query = {
        "Version": 2,
        "From": from_clause,
        "Select": select_clause
    }
    
    config = {
        "name": v_id,
        "singleVisual": {
            "visualType": "pieChart",
            "projections": {
                "Category": [{"queryRef": cat_ref, "active": True}],
                "Y": [{"queryRef": val_ref}]
            },
            "prototypeQuery": prototype_query,
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
    
    query = {
        "Commands": [{
            "SemanticQueryDataShapeCommand": {
                "Query": prototype_query,
                "Binding": {
                    "Primary": {
                        "Groupings": [{"Projections": [0, 1]}]
                    }
                }
            }
        }]
    }
    
    data_transforms = {
        "projectionOrdering": {
            "Category": [0],
            "Y": [1]
        },
        "queryMetadata": {
            "Select": [
                {"Restatement": cat_col, "Name": cat_ref, "Type": 2048},
                {"Restatement": val_prop, "Name": val_ref, "Type": val_type}
            ]
        }
    }
    
    return {
        "x": x, "y": y, "width": w, "height": h, "z": 2,
        "config": json.dumps(config),
        "query": json.dumps(query),
        "dataTransforms": json.dumps(data_transforms)
    }

def build_combo_chart(x, y, w, h, cat_table, cat_col, col_measures, line_measures, title_text):
    v_id = gen_id()
    cat_ref = f"{cat_table}.{cat_col}"
    
    from_clause = [
        {"Name": "c", "Entity": cat_table, "Type": 0},
        {"Name": "m", "Entity": "_Measures", "Type": 0}
    ]
    
    select_clause = [{
        "Column": {
            "Expression": {"SourceRef": {"Source": "c"}},
            "Property": cat_col
        },
        "Name": cat_ref
    }]
    
    query_meta_select = [{"Restatement": cat_col, "Name": cat_ref, "Type": 2048}]
    col_projs = []
    col_indices = []
    curr_idx = 1
    
    for m in col_measures:
        m_ref = f"_Measures.{m}"
        select_clause.append({
            "Measure": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": m},
            "Name": m_ref
        })
        col_projs.append({"queryRef": m_ref})
        col_indices.append(curr_idx)
        query_meta_select.append({"Restatement": m, "Name": m_ref, "Type": 1})
        curr_idx += 1
        
    line_projs = []
    line_indices = []
    for m in line_measures:
        m_ref = f"_Measures.{m}"
        select_clause.append({
            "Measure": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": m},
            "Name": m_ref
        })
        line_projs.append({"queryRef": m_ref})
        line_indices.append(curr_idx)
        query_meta_select.append({"Restatement": m, "Name": m_ref, "Type": 1})
        curr_idx += 1
        
    projections = {
        "Category": [{"queryRef": cat_ref, "active": True}],
        "ColumnValues": col_projs,
        "LineValues": line_projs
    }
    
    prototype_query = {
        "Version": 2,
        "From": from_clause,
        "Select": select_clause
    }
    
    config = {
        "name": v_id,
        "singleVisual": {
            "visualType": "lineClusteredColumnComboChart",
            "projections": projections,
            "prototypeQuery": prototype_query,
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
    
    query = {
        "Commands": [{
            "SemanticQueryDataShapeCommand": {
                "Query": prototype_query,
                "Binding": {
                    "Primary": {
                        "Groupings": [{"Projections": list(range(len(select_clause)))}]
                    }
                }
            }
        }]
    }
    
    data_transforms = {
        "projectionOrdering": {
            "Category": [0],
            "ColumnValues": col_indices,
            "LineValues": line_indices
        },
        "queryMetadata": {
            "Select": query_meta_select
        }
    }
    
    return {
        "x": x, "y": y, "width": w, "height": h, "z": 2,
        "config": json.dumps(config),
        "query": json.dumps(query),
        "dataTransforms": json.dumps(data_transforms)
    }

def build_stacked_area_chart(x, y, w, h, cat_table, cat_col, measures_list, title_text):
    v_id = gen_id()
    cat_ref = f"{cat_table}.{cat_col}"
    
    from_clause = [
        {"Name": "c", "Entity": cat_table, "Type": 0},
        {"Name": "m", "Entity": "_Measures", "Type": 0}
    ]
    
    select_clause = [{
        "Column": {
            "Expression": {"SourceRef": {"Source": "c"}},
            "Property": cat_col
        },
        "Name": cat_ref
    }]
    
    y_projs = []
    y_indices = []
    query_meta_select = [{"Restatement": cat_col, "Name": cat_ref, "Type": 2048}]
    
    for i, mname in enumerate(measures_list, 1):
        m_ref = f"_Measures.{mname}"
        select_clause.append({
            "Measure": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": mname},
            "Name": m_ref
        })
        y_projs.append({"queryRef": m_ref})
        y_indices.append(i)
        query_meta_select.append({"Restatement": mname, "Name": m_ref, "Type": 1})
        
    projections = {
        "Category": [{"queryRef": cat_ref, "active": True}],
        "Y": y_projs
    }
    
    prototype_query = {
        "Version": 2,
        "From": from_clause,
        "Select": select_clause
    }
    
    config = {
        "name": v_id,
        "singleVisual": {
            "visualType": "stackedAreaChart",
            "projections": projections,
            "prototypeQuery": prototype_query,
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
    
    query = {
        "Commands": [{
            "SemanticQueryDataShapeCommand": {
                "Query": prototype_query,
                "Binding": {
                    "Primary": {
                        "Groupings": [{"Projections": list(range(len(select_clause)))}]
                    }
                }
            }
        }]
    }
    
    data_transforms = {
        "projectionOrdering": {
            "Category": [0],
            "Y": y_indices
        },
        "queryMetadata": {
            "Select": query_meta_select
        }
    }
    
    return {
        "x": x, "y": y, "width": w, "height": h, "z": 2,
        "config": json.dumps(config),
        "query": json.dumps(query),
        "dataTransforms": json.dumps(data_transforms)
    }

def build_matrix(x, y, w, h, row_table, row_col, val_measures, title_text, col_table=None, col_col=None):
    v_id = gen_id()
    row_ref = f"{row_table}.{row_col}"
    
    from_clause = [
        {"Name": "r", "Entity": row_table, "Type": 0},
        {"Name": "m", "Entity": "_Measures", "Type": 0}
    ]
    
    select_clause = [{
        "Column": {"Expression": {"SourceRef": {"Source": "r"}}, "Property": row_col},
        "Name": row_ref
    }]
    
    projections = {"Rows": [{"queryRef": row_ref}]}
    proj_ordering = {"Rows": [0]}
    query_meta_select = [{"Restatement": row_col, "Name": row_ref, "Type": 2048}]
    curr_idx = 1
    
    if col_table and col_col:
        col_ref = f"{col_table}.{col_col}"
        if col_table != row_table:
            from_clause.append({"Name": "c", "Entity": col_table, "Type": 0})
            c_source = "c"
        else:
            c_source = "r"
        select_clause.append({
            "Column": {"Expression": {"SourceRef": {"Source": c_source}}, "Property": col_col},
            "Name": col_ref
        })
        projections["Columns"] = [{"queryRef": col_ref}]
        proj_ordering["Columns"] = [curr_idx]
        query_meta_select.append({"Restatement": col_col, "Name": col_ref, "Type": 2048})
        curr_idx += 1
        
    val_projs = []
    val_indices = []
    for m in val_measures:
        m_ref = f"_Measures.{m}"
        select_clause.append({
            "Measure": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": m},
            "Name": m_ref
        })
        val_projs.append({"queryRef": m_ref})
        val_indices.append(curr_idx)
        query_meta_select.append({"Restatement": m, "Name": m_ref, "Type": 1})
        curr_idx += 1
        
    projections["Values"] = val_projs
    proj_ordering["Values"] = val_indices
    
    prototype_query = {
        "Version": 2,
        "From": from_clause,
        "Select": select_clause
    }
    
    config = {
        "name": v_id,
        "singleVisual": {
            "visualType": "pivotTable",
            "projections": projections,
            "prototypeQuery": prototype_query,
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
    
    query = {
        "Commands": [{
            "SemanticQueryDataShapeCommand": {
                "Query": prototype_query,
                "Binding": {
                    "Primary": {
                        "Groupings": [{"Projections": list(range(len(select_clause)))}]
                    }
                }
            }
        }]
    }
    
    data_transforms = {
        "projectionOrdering": proj_ordering,
        "queryMetadata": {
            "Select": query_meta_select
        }
    }
    
    return {
        "x": x, "y": y, "width": w, "height": h, "z": 2,
        "config": json.dumps(config),
        "query": json.dumps(query),
        "dataTransforms": json.dumps(data_transforms)
    }

def build_table(x, y, w, h, table_name, cols_list, title_text):
    v_id = gen_id()
    from_clause = [{"Name": "t", "Entity": table_name, "Type": 0}]
    
    select_clause = []
    val_projs = []
    val_indices = []
    query_meta_select = []
    
    for i, c in enumerate(cols_list):
        c_ref = f"{table_name}.{c}"
        select_clause.append({
            "Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": c},
            "Name": c_ref
        })
        val_projs.append({"queryRef": c_ref})
        val_indices.append(i)
        query_meta_select.append({"Restatement": c, "Name": c_ref, "Type": 2048})
        
    projections = {"Values": val_projs}
    
    prototype_query = {
        "Version": 2,
        "From": from_clause,
        "Select": select_clause
    }
    
    config = {
        "name": v_id,
        "singleVisual": {
            "visualType": "tableEx",
            "projections": projections,
            "prototypeQuery": prototype_query,
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
    
    query = {
        "Commands": [{
            "SemanticQueryDataShapeCommand": {
                "Query": prototype_query,
                "Binding": {
                    "Primary": {
                        "Groupings": [{"Projections": val_indices}]
                    }
                }
            }
        }]
    }
    
    data_transforms = {
        "projectionOrdering": {"Values": val_indices},
        "queryMetadata": {"Select": query_meta_select}
    }
    
    return {
        "x": x, "y": y, "width": w, "height": h, "z": 2,
        "config": json.dumps(config),
        "query": json.dumps(query),
        "dataTransforms": json.dumps(data_transforms)
    }

def build_report_v2():
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
                build_textbox(20, 10, 540, 45, "Financial Inclusion Analytics — Portfolio Health & Risk Exposure"),
                build_slicer(580, 10, 160, 45, "dim_date", "calendar_year", "Year"),
                build_slicer(750, 10, 160, 45, "dim_state", "state_name", "State"),
                build_slicer(920, 10, 170, 45, "dim_branch", "branch_name", "Branch"),
                build_slicer(1100, 10, 160, 45, "dim_product", "product_name", "Product"),
                
                # 6 KPI Cards
                build_card(20, 65, 195, 85, "Total Loans Count", "Total Portfolio Loans", "#1E40AF"),
                build_card(230, 65, 195, 85, "Active Loans Count", "Active Loans", "#0F172A"),
                build_card(440, 65, 195, 85, "Disbursed Principal (INR Cr)", "Total Disbursed (₹ Cr)", "#0D9488"),
                build_card(650, 65, 195, 85, "Outstanding Principal (INR Cr)", "Outstanding Principal (₹ Cr)", "#2563EB"),
                build_card(860, 65, 195, 85, "PAR 30 %", "PAR 30 Rate", "#D97706"),
                build_card(1070, 65, 190, 85, "PAR 90 %", "PAR 90 Rate (NPL)", "#DC2626"),
                
                # Visuals
                build_line_chart(20, 160, 610, 270, "dim_date", "financial_quarter", 
                                 ["Total Outstanding Principal", "PAR 30 Principal"], 
                                 "Monthly Portfolio Outstanding & PAR 30 Balance Trend"),
                build_column_chart(650, 160, 610, 270, "dim_date", "financial_quarter",
                                   ["Current Principal", "Delinquency DPD 1-30", "Delinquency DPD 31-60", "Delinquency DPD 61-90", "PAR 90 Principal"],
                                   "Delinquency Aging by DPD Buckets (Current vs Overdue)"),
                build_pie_chart(20, 440, 500, 265, "dim_product", "product_name", 
                                "_Measures", "Total Outstanding Principal", 
                                "Portfolio Exposure by Product Category", is_measure=True),
                build_matrix(540, 440, 720, 265, "dim_state", "state_name", 
                             ["Active Loans Count", "Outstanding Principal (INR Cr)", "PAR 30 %", "PAR 90 %"], 
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
                build_textbox(20, 10, 540, 45, "Repayment Collection Performance & Cash Recovery Billing"),
                build_slicer(580, 10, 160, 45, "kpi_collection_efficiency", "year_month", "Month"),
                build_slicer(750, 10, 160, 45, "dim_state", "state_name", "State"),
                build_slicer(920, 10, 170, 45, "dim_branch", "branch_name", "Branch"),
                build_slicer(1100, 10, 160, 45, "dim_product", "product_name", "Product"),
                
                # 6 KPI Cards
                build_card(20, 65, 195, 85, "Scheduled Billing Due", "Scheduled Billing Due", "#0F172A"),
                build_card(230, 65, 195, 85, "Total Cash Collected", "Total Cash Collected", "#059669"),
                build_card(440, 65, 195, 85, "Current Period Collected", "Current Dues Collected", "#2563EB"),
                build_card(650, 65, 195, 85, "Arrears Collected", "Arrears Overdue Collected", "#D97706"),
                build_card(860, 65, 195, 85, "Advance Collected", "Advance Prepayments", "#7C3AED"),
                build_card(1070, 65, 190, 85, "Current Period Collection Efficiency %", "Current Billing Efficiency %", "#059669"),
                
                # Visuals
                build_combo_chart(20, 160, 710, 545, "kpi_collection_efficiency", "year_month",
                                  ["Scheduled Billing Due", "Total Cash Collected"],
                                  ["Current Period Collection Efficiency %"],
                                  "Monthly Scheduled Billing Dues vs Cash Recovered & Efficiency Ratio"),
                build_matrix(750, 160, 510, 545, "dim_branch", "branch_name",
                             ["Scheduled Billing Due", "Current Period Collected", "Arrears Collected", "Current Period Collection Efficiency %"],
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
                build_textbox(20, 10, 620, 45, "Disbursement Cohort Repayment Vintage Analysis (MOB 1 to 24)"),
                build_slicer(660, 10, 290, 45, "dim_product", "product_name", "Product"),
                build_slicer(970, 10, 290, 45, "kpi_vintage_curves", "cohort_month", "Cohort Month"),
                
                # 4 KPI Cards
                build_card(20, 65, 295, 85, "Total Disbursed Principal", "Cohort Disbursed Principal", "#1E40AF"),
                build_card(335, 65, 295, 85, "Cumulative Amount Paid (Vintage)", "Cumulative Cash Repaid", "#059669"),
                build_card(650, 65, 295, 85, "Cumulative Scheduled Due (Vintage)", "Cumulative Scheduled Dues", "#0F172A"),
                build_card(965, 65, 295, 85, "Vintage Repayment Rate %", "Portfolio Vintage Repayment Rate %", "#2563EB"),
                
                # Visuals
                build_line_chart(20, 160, 1240, 275, "kpi_vintage_curves", "month_on_book",
                                 ["Vintage Repayment Rate %"],
                                 "Repayment Vintage Curve: Cumulative Repayment Rate % by Month-on-Book",
                                 series_table="kpi_vintage_curves", series_col="cohort_month"),
                build_matrix(20, 445, 1240, 260, "kpi_vintage_curves", "cohort_month",
                             ["Vintage Repayment Rate %"],
                             "Cohort Repayment Performance Matrix (Cohort Month × Months on Book)",
                             col_table="kpi_vintage_curves", col_col="month_on_book")
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
                build_textbox(20, 10, 540, 45, "Digital Collections Growth & Payment Channel Transformation"),
                build_slicer(580, 10, 220, 45, "dim_state", "state_name", "State"),
                build_slicer(815, 10, 220, 45, "kpi_digital_collections", "year_month", "Month"),
                build_slicer(1050, 10, 210, 45, "fact_payment", "payment_channel", "Payment Channel"),
                
                # 7 KPI Cards
                build_card(20, 65, 165, 85, "Digital Collections Value", "Digital Value", "#0D9488"),
                build_card(199, 65, 165, 85, "Digital Transactions Count", "Digital Txns", "#2563EB"),
                build_card(378, 65, 165, 85, "Digital Value Share %", "Digital Share %", "#059669"),
                build_card(557, 65, 165, 85, "Digital Count Share %", "Txn Share %", "#059669"),
                build_card(736, 65, 165, 85, "UPI Value", "UPI Value", "#4F46E5"),
                build_card(915, 65, 165, 85, "Bank Transfer Value", "Net Banking", "#0284C7"),
                build_card(1094, 65, 166, 85, "Average Digital Payment Amount", "Avg Digital Ticket", "#0F172A"),
                
                # Visuals
                build_stacked_area_chart(20, 160, 710, 545, "kpi_digital_collections", "year_month",
                                         ["UPI Value", "Bank Transfer Value", "Cash Collections Value"],
                                         "Monthly Cash vs UPI vs Bank Transfer Channel Volume Distribution"),
                build_matrix(750, 160, 510, 545, "dim_state", "state_name",
                             ["Total Collections Value", "Digital Collections Value", "Digital Value Share %", "Digital Count Share %"],
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
                build_textbox(20, 10, 620, 45, "Data Quality Quarantine Firewall & Ingestion Anomaly Surveillance"),
                build_slicer(660, 10, 290, 45, "stg_quarantined_records", "source_table", "Source Table"),
                build_slicer(970, 10, 290, 45, "stg_quarantined_records", "reason_code", "Reason Code"),
                
                # 5 KPI Cards
                build_card(20, 65, 230, 85, "Total Raw Records", "Raw Ingestion Payloads", "#0F172A"),
                build_card(270, 65, 230, 85, "Total Clean Records", "Clean Verified Records", "#059669"),
                build_card(520, 65, 230, 85, "Total Quarantined Records", "Quarantined Anomalies", "#DC2626"),
                build_card(770, 65, 230, 85, "Data Quality Pass Rate %", "Ingestion Pass Rate %", "#2563EB"),
                build_card(1020, 65, 240, 85, "Issue Categories Count", "Active Anomaly Categories", "#D97706"),
                
                # Visuals
                build_pie_chart(20, 160, 480, 545, "stg_quarantined_records", "reason_code",
                                "_Measures", "Total Quarantined Records",
                                "Distribution of Quarantined Anomalies by Reason Code", is_measure=True),
                build_table(520, 160, 740, 545, "stg_quarantined_records",
                            ["quarantine_id", "batch_run_id", "source_table", "reason_code", "record_identifier", "quarantined_at"],
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
    
    print(f"Successfully generated complete report.json with FULL query & dataTransforms at: {REPORT_PATH}")
    print(f"Total Sections: {len(sections)}")
    for s in sections:
        print(f"  {s['displayName']}: {len(s['visualContainers'])} visuals")

if __name__ == "__main__":
    build_report_v2()
