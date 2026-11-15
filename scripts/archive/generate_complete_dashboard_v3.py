"""
Generates the complete, professional, interactive five-page Power BI report.json (v3)
with Phase 2B layout refinements:
1. Snapshot DAX measures fix integration (resolves Page 1 blank cards & blank matrix).
2. Slicer redesign: Spacious top filter bar (w=300-616px, h=46px) with Dropdown mode.
3. Page 2 layout re-balancing: eliminates whitespace, fixes combo chart projections (Y & Y2).
4. Page 3 vintage layout polishing: symmetric cards and spacious matrix.
5. Page 4 digital collections layout balancing and trend data validation.
6. Page 5 quarantine firewall alignment.
"""

import os
import json
import uuid

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_PATH = os.path.join(PROJECT_ROOT, "powerbi", "Financial_Inclusion_Analytics.Report", "report.json")

def gen_id():
    return str(uuid.uuid4()).replace("-", "")[:20]

def build_textbox(x, y, w, h, title_text, subtitle_text=None, font_size="14pt", color="#0F172A"):
    runs = [{
        "value": title_text,
        "textStyle": {
            "fontSize": font_size,
            "fontWeight": "bold",
            "color": color
        }
    }]
    if subtitle_text:
        runs.append({
            "value": f"  |  {subtitle_text}",
            "textStyle": {
                "fontSize": "10pt",
                "fontWeight": "normal",
                "color": "#64748B"
            }
        })
        
    config = {
        "name": gen_id(),
        "singleVisual": {
            "visualType": "textbox",
            "objects": {
                "general": [{
                    "properties": {
                        "paragraphs": [{
                            "textRuns": runs
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
    
    objects = {
        "data": [{
            "properties": {
                "mode": {"expr": {"Literal": {"Value": "'Dropdown'"}}}
            }
        }],
        "general": [{
            "properties": {
                "filter": {
                    "filter": {
                        "Version": 2,
                        "From": from_clause,
                        "Where": []
                    }
                }
            }
        }]
    }
    
    if title_text:
        objects["title"] = [{
            "properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "text": {"expr": {"Literal": {"Value": f"'{title_text}'"}}}
            }
        }]
        objects["header"] = [{
            "properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "text": {"expr": {"Literal": {"Value": f"'{title_text}'"}}}
            }
        }]
        
    config = {
        "name": v_id,
        "singleVisual": {
            "visualType": "slicer",
            "projections": {
                "Values": [{"queryRef": query_ref}]
            },
            "prototypeQuery": prototype_query,
            "objects": objects
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
                "Restatement": col_name,
                "Name": query_ref,
                "Type": 2048
            }]
        }
    }
    
    return {
        "x": x, "y": y, "width": w, "height": h, "z": 1,
        "config": json.dumps(config),
        "query": json.dumps(query),
        "dataTransforms": json.dumps(data_transforms)
    }

def build_card(x, y, w, h, measure_name, title_text, accent_color="#0F172A"):
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
                        "color": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{accent_color}'"}}}}},
                        "fontSize": {"expr": {"Literal": {"Value": "20D"}}}
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
        "x": x, "y": y, "width": w, "height": h, "z": 2,
        "config": json.dumps(config),
        "query": json.dumps(query),
        "dataTransforms": json.dumps(data_transforms)
    }

def build_line_chart(x, y, w, h, cat_table, cat_col, measures_list, title_text, series_table=None, series_col=None):
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
    
    projections = {"Category": [{"queryRef": cat_ref, "active": True}]}
    proj_ordering = {"Category": [0]}
    query_meta_select = [{"Restatement": cat_col, "Name": cat_ref, "Type": 2048}]
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
        query_meta_select.append({"Restatement": series_col, "Name": series_ref, "Type": 2048})
        curr_idx += 1
        
    y_projs = []
    y_indices = []
    for m in measures_list:
        m_ref = f"_Measures.{m}"
        select_clause.append({
            "Measure": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": m},
            "Name": m_ref
        })
        y_projs.append({"queryRef": m_ref})
        y_indices.append(curr_idx)
        query_meta_select.append({"Restatement": m, "Name": m_ref, "Type": 1})
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
        "queryMetadata": {"Select": query_meta_select}
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
        "Y": col_projs,
        "Y2": line_projs
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
            "Y": col_indices,
            "Y2": line_indices
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

def build_report_v3():
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
                # Row 1: Header Banner (y=12, h=38)
                build_textbox(16, 12, 1248, 38, 
                              "Financial Inclusion Analytics — Portfolio Health & Risk Exposure", 
                              "Asset Quality, PAR Surveillance & Delinquency Aging Monitor"),
                
                # Row 2: Spacious Slicers Bar (y=54, h=48) - 4 Slicers across 1248px
                build_slicer(16, 54, 300, 48, "dim_date", "calendar_year", "Select Calendar Year"),
                build_slicer(332, 54, 300, 48, "dim_state", "state_name", "Select State"),
                build_slicer(648, 54, 300, 48, "dim_branch", "branch_name", "Select Operating Branch"),
                build_slicer(964, 54, 300, 48, "dim_product", "product_name", "Select Credit Product"),
                
                # Row 3: 6 Executive KPI Cards (y=106, h=80)
                build_card(16, 106, 194, 80, "Total Loans Count", "Total Cumulative Loans", "#1E40AF"),
                build_card(226, 106, 194, 80, "Active Loans Count", "Active Portfolio Loans", "#0F172A"),
                build_card(436, 106, 194, 80, "Disbursed Principal (INR Cr)", "Gross Disbursed (₹ Cr)", "#0D9488"),
                build_card(646, 106, 194, 80, "Outstanding Principal (INR Cr)", "Gross Outstanding (₹ Cr)", "#2563EB"),
                build_card(856, 106, 194, 80, "PAR 30 %", "PAR 30 Rate (Early Arrears)", "#D97706"),
                build_card(1066, 106, 198, 80, "PAR 90 %", "PAR 90 Rate (NPA Default)", "#DC2626"),
                
                # Row 4: Analytics Body Upper Row (y=190, h=252)
                build_line_chart(16, 190, 616, 252, "dim_date", "year_month", 
                                 ["Total Outstanding Principal", "PAR 30 Principal"], 
                                 "Monthly Portfolio Outstanding & PAR 30 Balance Progression"),
                build_column_chart(648, 190, 616, 252, "dim_date", "year_month",
                                   ["Current Principal", "Delinquency DPD 1-30", "Delinquency DPD 31-60", "Delinquency DPD 61-90", "PAR 90 Principal"],
                                   "Monthly Delinquency Aging Profile by DPD Buckets"),
                
                # Row 5: Analytics Body Lower Row (y=446, h=262)
                build_pie_chart(16, 446, 460, 262, "dim_product", "product_name", 
                                "_Measures", "Total Outstanding Principal", 
                                "Outstanding Principal Exposure by Product Category", is_measure=True),
                build_matrix(488, 446, 776, 262, "dim_state", "state_name", 
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
                # Row 1: Header Banner (y=12, h=38)
                build_textbox(16, 12, 1248, 38, 
                              "Repayment Collection Performance & Cash Recovery Billing", 
                              "Scheduled Instalments, Realised Cash Receipts & Recovery Ratios"),
                
                # Row 2: Spacious Slicers Bar (y=54, h=48)
                build_slicer(16, 54, 300, 48, "kpi_collection_efficiency", "year_month", "Select Billing Month"),
                build_slicer(332, 54, 300, 48, "dim_state", "state_name", "Select State"),
                build_slicer(648, 54, 300, 48, "dim_branch", "branch_name", "Select Operating Branch"),
                build_slicer(964, 54, 300, 48, "dim_product", "product_name", "Select Credit Product"),
                
                # Row 3: 6 Executive KPI Cards (y=106, h=80)
                build_card(16, 106, 194, 80, "Scheduled Billing Due", "Scheduled Billing Due", "#0F172A"),
                build_card(226, 106, 194, 80, "Total Cash Collected", "Total Realised Cash", "#059669"),
                build_card(436, 106, 194, 80, "Current Period Collected", "Current Dues Collected", "#2563EB"),
                build_card(646, 106, 194, 80, "Arrears Collected", "Prior Arrears Recovered", "#D97706"),
                build_card(856, 106, 194, 80, "Advance Collected", "Advance Prepayments", "#7C3AED"),
                build_card(1066, 106, 198, 80, "Current Period Collection Efficiency %", "Headline Current Efficiency %", "#059669"),
                
                # Row 4: Analytics Body - Balanced 2-Column Grid (y=190, h=518)
                build_combo_chart(16, 190, 680, 518, "kpi_collection_efficiency", "year_month",
                                  ["Scheduled Billing Due", "Total Cash Collected"],
                                  ["Current Period Collection Efficiency %"],
                                  "Monthly Scheduled Billing Dues vs Cash Recovered & Efficiency Ratio"),
                build_matrix(708, 190, 556, 518, "dim_branch", "branch_name",
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
                # Row 1: Header Banner (y=12, h=38)
                build_textbox(16, 12, 1248, 38, 
                              "Disbursement Cohort Repayment Vintage Analysis (MOB 1 to 24)", 
                              "Cumulative Repayment Curves & Maturation Performance by Loan Cohort"),
                
                # Row 2: 2 Spacious Slicers Bar (y=54, h=48)
                build_slicer(16, 54, 616, 48, "dim_product", "product_name", "Select Credit Product"),
                build_slicer(648, 54, 616, 48, "kpi_vintage_curves", "cohort_month", "Select Disbursement Cohort Month"),
                
                # Row 3: 4 Executive KPI Cards (y=106, h=80)
                build_card(16, 106, 300, 80, "Total Disbursed Principal", "Cohort Disbursed Principal", "#1E40AF"),
                build_card(332, 106, 300, 80, "Cumulative Amount Paid (Vintage)", "Cumulative Cash Repaid", "#059669"),
                build_card(648, 106, 300, 80, "Cumulative Scheduled Due (Vintage)", "Cumulative Scheduled Dues", "#0F172A"),
                build_card(964, 106, 300, 80, "Vintage Repayment Rate %", "Portfolio Vintage Repayment Rate %", "#2563EB"),
                
                # Row 4: Vintage Curve Chart (y=190, h=252)
                build_line_chart(16, 190, 1248, 252, "kpi_vintage_curves", "month_on_book",
                                 ["Vintage Repayment Rate %"],
                                 "Repayment Vintage Curve: Cumulative Repayment Rate % by Month-on-Book",
                                 series_table="kpi_vintage_curves", series_col="cohort_month"),
                
                # Row 5: Cohort Matrix (y=446, h=262)
                build_matrix(16, 446, 1248, 262, "kpi_vintage_curves", "cohort_month",
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
                # Row 1: Header Banner (y=12, h=38)
                build_textbox(16, 12, 1248, 38, 
                              "Digital Collections Growth & Payment Channel Transformation", 
                              "Cashless Migration, UPI Penetration & Banking Channel Velocity (2023-2024 Core Horizon)"),
                
                # Row 2: 3 Spacious Slicers Bar (y=54, h=48)
                build_slicer(16, 54, 405, 48, "dim_state", "state_name", "Select State"),
                build_slicer(437, 54, 405, 48, "kpi_digital_collections", "year_month", "Select Reporting Month"),
                build_slicer(858, 54, 406, 48, "fact_payment", "payment_channel", "Select Payment Channel Mode"),
                
                # Row 3: 7 Executive KPI Cards (y=106, h=80)
                build_card(16, 106, 164, 80, "Digital Collections Value", "Digital Value (INR)", "#0D9488"),
                build_card(196, 106, 164, 80, "Digital Transactions Count", "Digital Txns", "#2563EB"),
                build_card(376, 106, 164, 80, "Digital Value Share %", "Digital Value %", "#059669"),
                build_card(556, 106, 164, 80, "Digital Count Share %", "Digital Txn %", "#059669"),
                build_card(736, 106, 164, 80, "UPI Value", "UPI Collections", "#4F46E5"),
                build_card(916, 106, 164, 80, "Bank Transfer Value", "Net Banking / NEFT", "#0284C7"),
                build_card(1096, 106, 168, 80, "Average Digital Payment Amount", "Avg Digital Ticket", "#0F172A"),
                
                # Row 4: Analytics Body - Balanced 2-Column Grid (y=190, h=518)
                build_stacked_area_chart(16, 190, 680, 518, "kpi_digital_collections", "year_month",
                                         ["UPI Value", "Bank Transfer Value", "Cash Collections Value"],
                                         "Monthly Cash vs UPI vs Bank Transfer Volume Distribution (2023-2024 Full Horizon)"),
                build_matrix(708, 190, 556, 518, "dim_state", "state_name",
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
                # Row 1: Header Banner (y=12, h=38)
                build_textbox(16, 12, 1248, 38, 
                              "Data Quality Quarantine Firewall & Ingestion Anomaly Surveillance", 
                              "Automated Quarantine Isolation, Anomaly Forensics & Pipeline Integrity"),
                
                # Row 2: 2 Spacious Slicers Bar (y=54, h=48)
                build_slicer(16, 54, 616, 48, "stg_quarantined_records", "source_table", "Select Ingestion Source Table"),
                build_slicer(648, 54, 616, 48, "stg_quarantined_records", "reason_code", "Select Anomaly Reason Code"),
                
                # Row 3: 5 Executive KPI Cards (y=106, h=80)
                build_card(16, 106, 236, 80, "Total Raw Records", "Raw Ingested Records", "#0F172A"),
                build_card(268, 106, 236, 80, "Total Clean Records", "Clean Verified Records", "#059669"),
                build_card(520, 106, 236, 80, "Total Quarantined Records", "Quarantined Anomalies", "#DC2626"),
                build_card(772, 106, 236, 80, "Data Quality Pass Rate %", "Pipeline Pass Rate %", "#2563EB"),
                build_card(1024, 106, 240, 80, "Issue Categories Count", "Anomaly Root Causes", "#D97706"),
                
                # Row 4: Analytics Body - Balanced 2-Column Grid (y=190, h=518)
                build_pie_chart(16, 190, 480, 518, "stg_quarantined_records", "reason_code",
                                "_Measures", "Total Quarantined Records",
                                "Distribution of Quarantined Anomalies by Reason Code", is_measure=True),
                build_table(508, 190, 756, 518, "stg_quarantined_records",
                            ["quarantine_id", "batch_run_id", "source_table", "reason_code", "record_identifier", "quarantined_at"],
                            "Forensic Audit Trail of Quarantined Payloads (Source, Identifier & Reason Code)")
            ]
        }
    ]
    
    report_def = {
        "config": json.dumps({
            "version": "5.50",
            "themeCollection": {
                "baseTheme": {
                    "name": "CY24SU10",
                    "version": "5.50",
                    "type": 2
                }
            },
            "activeSectionName": "Section_PortfolioHealth"
        }),
        "layoutOptimization": 0,
        "sections": sections
    }
    
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report_def, f, indent=2)
        
    print(f"Successfully generated complete refined report.json at: {REPORT_PATH}")
    print(f"Total Sections: {len(sections)}")
    for s in sections:
        print(f"  - {s['displayName']}: {len(s['visualContainers'])} visual containers")

if __name__ == "__main__":
    build_report_v3()
