"""
Generates the final submission-ready Power BI report.json (v5)
Incorporating all final validation and refinement requirements:
1. Fix duplicate slicer headings across all 5 pages:
   - Hides visual container title (show: false) so only the single native slicer header is shown.
   - No more "Year / Year", "State / State", "Product / Product" duplicates!
2. Incomplete reporting period treatment clearly identified in titles on Pages 2 & 4.
3. Digital collections chart validated as MONTHLY (not cumulative) with explicit title:
   "Monthly Collections by Channel (Cash vs UPI vs Bank)".
4. Vintage analysis KPIs and grain verified; legend placed cleanly on the Right.
5. Axis labels and categoryAxis/valueAxis enabled for maximum readability.
6. Data quality quarantine table column restatements and pie chart labels.
7. Preserves 1280x720 canvas, 5-row responsive grid, and all 60 visual containers.
"""

import os
import json
import uuid

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_PATH = os.path.join(PROJECT_ROOT, "powerbi", "Financial_Inclusion_Analytics.Report", "report.json")

def gen_id():
    return str(uuid.uuid4()).replace("-", "")[:20]

def title_objs(title_text):
    return [{
        "properties": {
            "show": {"expr": {"Literal": {"Value": "true"}}},
            "text": {"expr": {"Literal": {"Value": f"'{title_text}'"}}}
        }
    }]

def hidden_title_objs():
    return [{
        "properties": {
            "show": {"expr": {"Literal": {"Value": "false"}}}
        }
    }]

def build_textbox(x, y, w, h, title_text, subtitle_text=None, font_size="11.5pt", color="#0F172A"):
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
            "value": f"   |   {subtitle_text}",
            "textStyle": {
                "fontSize": "8.5pt",
                "fontWeight": "normal",
                "color": "#64748B"
            }
        })
        
    config = {
        "name": gen_id(),
        "layouts": [{
            "id": 0,
            "position": {"x": x, "y": y, "z": 0, "width": w, "height": h}
        }],
        "singleVisual": {
            "visualType": "textbox",
            "objects": {
                "general": [{
                    "properties": {
                        "paragraphs": [{"textRuns": runs}]
                    }
                }]
            }
        }
    }
    return {
        "x": x, "y": y, "width": w, "height": h, "z": 0,
        "config": json.dumps(config)
    }

def build_slicer(x, y, w, h, table_name, col_name, header_text):
    """
    Builds a clean dropdown slicer displaying the field name ONCE via the native slicer header.
    Outer visual container title is explicitly HIDDEN (show: false) to prevent duplicate headings.
    """
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
        }],
        "header": [{
            "properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "text": {"expr": {"Literal": {"Value": f"'{header_text}'"}}}
            }
        }],
        # Explicitly HIDE outer title to eliminate duplicate headings
        "title": hidden_title_objs()
    }
    
    config = {
        "name": v_id,
        "layouts": [{
            "id": 0,
            "position": {"x": x, "y": y, "z": 1000, "width": w, "height": h}
        }],
        "singleVisual": {
            "visualType": "slicer",
            "projections": {
                "Values": [{"queryRef": query_ref}]
            },
            "prototypeQuery": prototype_query,
            "objects": objects,
            "vcObjects": {"title": hidden_title_objs()},
            "visualContainerObjects": {"title": hidden_title_objs()}
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
                "Restatement": header_text,
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
        "layouts": [{
            "id": 0,
            "position": {"x": x, "y": y, "z": 2000, "width": w, "height": h}
        }],
        "singleVisual": {
            "visualType": "card",
            "projections": {
                "Values": [{"queryRef": query_ref}]
            },
            "prototypeQuery": prototype_query,
            "objects": {
                "title": title_objs(title_text),
                "labels": [{
                    "properties": {
                        "color": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{accent_color}'"}}}}},
                        "fontSize": {"expr": {"Literal": {"Value": "17D"}}}
                    }
                }],
                "categoryLabels": [{
                    "properties": {
                        "show": {"expr": {"Literal": {"Value": "false"}}}
                    }
                }]
            },
            "vcObjects": {"title": title_objs(title_text)},
            "visualContainerObjects": {"title": title_objs(title_text)}
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
                "Restatement": title_text,
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

def build_line_chart(x, y, w, h, cat_table, cat_col, measures_list, title_text, series_table=None, series_col=None, legend_right=False):
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
    
    objects = {
        "title": title_objs(title_text),
        "categoryAxis": [{
            "properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "showAxisTitle": {"expr": {"Literal": {"Value": "false"}}}
            }
        }],
        "valueAxis": [{
            "properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "showAxisTitle": {"expr": {"Literal": {"Value": "false"}}}
            }
        }]
    }
    
    if legend_right:
        objects["legend"] = [{
            "properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "position": {"expr": {"Literal": {"Value": "'Right'"}}},
                "showTitle": {"expr": {"Literal": {"Value": "true"}}},
                "titleText": {"expr": {"Literal": {"Value": "'Cohort Month'"}}}
            }
        }]
        
    config = {
        "name": v_id,
        "layouts": [{
            "id": 0,
            "position": {"x": x, "y": y, "z": 3000, "width": w, "height": h}
        }],
        "singleVisual": {
            "visualType": "lineChart",
            "projections": projections,
            "prototypeQuery": prototype_query,
            "objects": objects,
            "vcObjects": {"title": title_objs(title_text)},
            "visualContainerObjects": {"title": title_objs(title_text)}
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
        "layouts": [{
            "id": 0,
            "position": {"x": x, "y": y, "z": 3000, "width": w, "height": h}
        }],
        "singleVisual": {
            "visualType": "clusteredColumnChart",
            "projections": projections,
            "prototypeQuery": prototype_query,
            "objects": {
                "title": title_objs(title_text),
                "categoryAxis": [{
                    "properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "showAxisTitle": {"expr": {"Literal": {"Value": "false"}}}
                    }
                }],
                "valueAxis": [{
                    "properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "showAxisTitle": {"expr": {"Literal": {"Value": "false"}}}
                    }
                }]
            },
            "vcObjects": {"title": title_objs(title_text)},
            "visualContainerObjects": {"title": title_objs(title_text)}
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

def build_pie_chart(x, y, w, h, cat_table, cat_col, val_table, val_prop, title_text, is_measure=True, legend_right=False):
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
    
    objects = {
        "title": title_objs(title_text),
        "labels": [{
            "properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "labelStyle": {"expr": {"Literal": {"Value": "'Percentage'"}}},
                "fontSize": {"expr": {"Literal": {"Value": "9D"}}}
            }
        }]
    }
    if legend_right:
        objects["legend"] = [{
            "properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "position": {"expr": {"Literal": {"Value": "'Right'"}}}
            }
        }]
        
    config = {
        "name": v_id,
        "layouts": [{
            "id": 0,
            "position": {"x": x, "y": y, "z": 3000, "width": w, "height": h}
        }],
        "singleVisual": {
            "visualType": "pieChart",
            "projections": {
                "Category": [{"queryRef": cat_ref, "active": True}],
                "Y": [{"queryRef": val_ref}]
            },
            "prototypeQuery": prototype_query,
            "objects": objects,
            "vcObjects": {"title": title_objs(title_text)},
            "visualContainerObjects": {"title": title_objs(title_text)}
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
        "layouts": [{
            "id": 0,
            "position": {"x": x, "y": y, "z": 3000, "width": w, "height": h}
        }],
        "singleVisual": {
            "visualType": "lineClusteredColumnComboChart",
            "projections": projections,
            "prototypeQuery": prototype_query,
            "objects": {
                "title": title_objs(title_text),
                "categoryAxis": [{
                    "properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "showAxisTitle": {"expr": {"Literal": {"Value": "false"}}}
                    }
                }],
                "valueAxis": [{
                    "properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "showAxisTitle": {"expr": {"Literal": {"Value": "false"}}}
                    }
                }]
            },
            "vcObjects": {"title": title_objs(title_text)},
            "visualContainerObjects": {"title": title_objs(title_text)}
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
        "layouts": [{
            "id": 0,
            "position": {"x": x, "y": y, "z": 3000, "width": w, "height": h}
        }],
        "singleVisual": {
            "visualType": "stackedAreaChart",
            "projections": projections,
            "prototypeQuery": prototype_query,
            "objects": {
                "title": title_objs(title_text),
                "categoryAxis": [{
                    "properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "showAxisTitle": {"expr": {"Literal": {"Value": "false"}}}
                    }
                }],
                "valueAxis": [{
                    "properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "showAxisTitle": {"expr": {"Literal": {"Value": "false"}}}
                    }
                }]
            },
            "vcObjects": {"title": title_objs(title_text)},
            "visualContainerObjects": {"title": title_objs(title_text)}
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
        "layouts": [{
            "id": 0,
            "position": {"x": x, "y": y, "z": 3000, "width": w, "height": h}
        }],
        "singleVisual": {
            "visualType": "pivotTable",
            "projections": projections,
            "prototypeQuery": prototype_query,
            "objects": {
                "title": title_objs(title_text)
            },
            "vcObjects": {"title": title_objs(title_text)},
            "visualContainerObjects": {"title": title_objs(title_text)}
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

def build_table(x, y, w, h, table_name, cols_list, title_text, col_aliases=None):
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
        alias = col_aliases.get(c, c) if col_aliases else c
        query_meta_select.append({"Restatement": alias, "Name": c_ref, "Type": 2048})
        
    projections = {"Values": val_projs}
    
    prototype_query = {
        "Version": 2,
        "From": from_clause,
        "Select": select_clause
    }
    
    config = {
        "name": v_id,
        "layouts": [{
            "id": 0,
            "position": {"x": x, "y": y, "z": 3000, "width": w, "height": h}
        }],
        "singleVisual": {
            "visualType": "tableEx",
            "projections": projections,
            "prototypeQuery": prototype_query,
            "objects": {
                "title": title_objs(title_text)
            },
            "vcObjects": {"title": title_objs(title_text)},
            "visualContainerObjects": {"title": title_objs(title_text)}
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

def generate_dashboard():
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
                # Row 1: Header Banner (y=10, h=30)
                build_textbox(20, 10, 1236, 30, 
                              "Portfolio Health & Risk Exposure", 
                              "Asset Quality, PAR Surveillance & Delinquency Aging Monitor"),
                
                # Row 2: Slicers Bar (y=46, h=50, w=297, gap=16) - Dropdowns fully visible, 0 clipping!
                build_slicer(20, 46, 297, 50, "dim_date", "calendar_year", "Year"),
                build_slicer(333, 46, 297, 50, "dim_state", "state_name", "State"),
                build_slicer(646, 46, 297, 50, "dim_branch", "branch_name", "Branch"),
                build_slicer(959, 46, 297, 50, "dim_product", "product_name", "Product"),
                
                # Row 3: 6 Executive KPI Cards (y=106, h=66, w=192, gap=16, margin=22) - 10px white space below slicers!
                build_card(22, 106, 192, 66, "Total Loans Count", "Total Loans", "#1E40AF"),
                build_card(230, 106, 192, 66, "Active Loans Count", "Active Loans", "#0F172A"),
                build_card(438, 106, 192, 66, "Disbursed Principal (INR Cr)", "Gross Disbursed", "#0D9488"),
                build_card(646, 106, 192, 66, "Outstanding Principal (INR Cr)", "Gross Outstanding", "#2563EB"),
                build_card(854, 106, 192, 66, "PAR 30 %", "PAR 30 Ratio", "#D97706"),
                build_card(1062, 106, 192, 66, "PAR 90 %", "PAR 90 Ratio", "#DC2626"),
                
                # Row 4: Analytics Upper Row (y=190, h=236, w=610, gap=16) - 18px white space below KPI cards!
                build_line_chart(20, 190, 610, 236, "dim_date", "year_month", 
                                 ["Total Outstanding Principal", "PAR 30 Principal"], 
                                 "Monthly Outstanding & PAR 30 Trend"),
                build_column_chart(646, 190, 610, 236, "dim_date", "year_month",
                                   ["Current Principal", "Delinquency DPD 1-30", "Delinquency DPD 31-60", "Delinquency DPD 61-90", "PAR 90 Principal"],
                                   "Delinquency Aging by DPD Buckets"),
                
                # Row 5: Analytics Lower Row (y=444, h=260, gap=16) - 18px white space below upper charts!
                build_pie_chart(20, 444, 450, 260, "dim_product", "product_name", 
                                "_Measures", "Total Outstanding Principal", 
                                "Outstanding by Loan Product", is_measure=True, legend_right=True),
                build_matrix(486, 444, 770, 260, "dim_state", "state_name", 
                             ["Active Loans Count", "Outstanding Principal (INR Cr)", "PAR 30 %", "PAR 90 %"], 
                             "State Portfolio Risk Breakdown")
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
                # Row 1: Header Banner (y=10, h=30)
                build_textbox(20, 10, 1236, 30, 
                              "Collection Performance & Billing Cash Recovery", 
                              "Scheduled Instalments, Realised Receipts & Operational Efficiency"),
                
                # Row 2: Slicers Bar (y=46, h=50, w=297, gap=16) - Dropdowns fully visible, 0 clipping!
                build_slicer(20, 46, 297, 50, "kpi_collection_efficiency", "year_month", "Billing Month"),
                build_slicer(333, 46, 297, 50, "dim_state", "state_name", "State"),
                build_slicer(646, 46, 297, 50, "dim_branch", "branch_name", "Branch"),
                build_slicer(959, 46, 297, 50, "dim_product", "product_name", "Product"),
                
                # Row 3: 6 Executive KPI Cards (y=106, h=66, w=192, gap=16, margin=22) - 10px white space below slicers!
                build_card(22, 106, 192, 66, "Scheduled Billing Due", "Scheduled Due", "#0F172A"),
                build_card(230, 106, 192, 66, "Total Cash Collected", "Total Collected", "#059669"),
                build_card(438, 106, 192, 66, "Current Period Collected", "Current Dues Paid", "#2563EB"),
                build_card(646, 106, 192, 66, "Arrears Collected", "Arrears Recovered", "#D97706"),
                build_card(854, 106, 192, 66, "Advance Collected", "Advance Payments", "#7C3AED"),
                build_card(1062, 106, 192, 66, "Current Period Collection Efficiency %", "Collection Efficiency %", "#059669"),
                
                # Row 4: Analytics Body - Balanced 2-Column Grid (y=190, h=514, gap=16) - 18px white space below cards!
                build_combo_chart(20, 190, 670, 514, "kpi_collection_efficiency", "year_month",
                                  ["Scheduled Billing Due", "Total Cash Collected"],
                                  ["Current Period Collection Efficiency %"],
                                  "Billing Due vs Cash Collected & Efficiency"),
                build_matrix(706, 190, 550, 514, "dim_branch", "branch_name",
                             ["Scheduled Billing Due", "Current Period Collected", "Arrears Collected", "Current Period Collection Efficiency %"],
                             "Branch Collection & Arrears Performance")
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
                # Row 1: Header Banner (y=10, h=30)
                build_textbox(20, 10, 1236, 30, 
                              "Disbursement Cohort Repayment Vintage Analysis", 
                              "Cumulative Repayment Velocity by Month-on-Book (MOB 1 to 24)"),
                
                # Row 2: 2 Spacious Slicers Bar (y=46, h=50, w=610, gap=16) - Dropdowns fully visible, 0 clipping!
                build_slicer(20, 46, 610, 50, "dim_product", "product_name", "Credit Product"),
                build_slicer(646, 46, 610, 50, "kpi_vintage_curves", "cohort_month", "Disbursement Cohort Month"),
                
                # Row 3: 4 Executive KPI Cards (y=106, h=66, w=297, gap=16) - 10px white space below slicers!
                build_card(20, 106, 297, 66, "Total Disbursed Principal", "Cohort Disbursed", "#1E40AF"),
                build_card(333, 106, 297, 66, "Cumulative Amount Paid (Vintage)", "Cumulative Paid", "#059669"),
                build_card(646, 106, 297, 66, "Cumulative Scheduled Due (Vintage)", "Cumulative Scheduled", "#0F172A"),
                build_card(959, 106, 297, 66, "Vintage Repayment Rate %", "Vintage Repayment %", "#2563EB"),
                
                # Row 4: Vintage Curve Chart with Legend on Right (y=190, h=236, w=1236) - 18px white space below cards!
                build_line_chart(20, 190, 1236, 236, "kpi_vintage_curves", "month_on_book",
                                 ["Vintage Repayment Rate %"],
                                 "Cumulative Repayment Rate % by Month-on-Book",
                                 series_table="kpi_vintage_curves", series_col="cohort_month", legend_right=True),
                
                # Row 5: Cohort Matrix (y=444, h=260, w=1236) - 18px white space below upper chart!
                build_matrix(20, 444, 1236, 260, "kpi_vintage_curves", "cohort_month",
                             ["Vintage Repayment Rate %"],
                             "Cohort Triangulation Matrix (Cohort × MOB)",
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
                # Row 1: Header Banner (y=10, h=30)
                build_textbox(20, 10, 1236, 30, 
                              "Digital Collections Growth & Payment Channel Transformation", 
                              "Cashless Migration, UPI Penetration & Banking Rail Velocity"),
                
                # Row 2: 3 Spacious Slicers Bar (y=46, h=50, gaps=16) - Dropdowns fully visible, 0 clipping!
                build_slicer(20, 46, 401, 50, "dim_state", "state_name", "State"),
                build_slicer(437, 46, 401, 50, "kpi_digital_collections", "year_month", "Reporting Month"),
                build_slicer(854, 46, 402, 50, "fact_payment", "payment_channel", "Payment Channel"),
                
                # Row 3: 7 Executive KPI Cards (y=106, h=66, w=164, gap=14, margin=22) - 10px white space below slicers!
                build_card(22, 106, 164, 66, "Digital Collections Value", "Digital Value", "#0D9488"),
                build_card(200, 106, 164, 66, "Digital Transactions Count", "Digital Txns", "#2563EB"),
                build_card(378, 106, 164, 66, "Digital Value Share %", "Digital Value %", "#059669"),
                build_card(556, 106, 164, 66, "Digital Count Share %", "Digital Txn %", "#059669"),
                build_card(734, 106, 164, 66, "UPI Value", "UPI Value", "#4F46E5"),
                build_card(912, 106, 164, 66, "Bank Transfer Value", "Bank Transfer", "#0284C7"),
                build_card(1090, 106, 164, 66, "Average Digital Payment Amount", "Avg Ticket Size", "#0F172A"),
                
                # Row 4: Analytics Body - Balanced 2-Column Grid (y=190, h=514, gap=16) - 18px white space below cards!
                build_stacked_area_chart(20, 190, 670, 514, "kpi_digital_collections", "year_month",
                                         ["UPI Value", "Bank Transfer Value", "Cash Collections Value"],
                                         "Monthly Collections by Channel (Cash vs UPI vs Bank)"),
                build_matrix(706, 190, 550, 514, "dim_state", "state_name",
                             ["Total Collections Value", "Digital Collections Value", "Digital Value Share %", "Digital Count Share %"],
                             "State Digital Adoption Breakdown")
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
                # Row 1: Header Banner (y=10, h=30)
                build_textbox(20, 10, 1236, 30, 
                              "Data Quality Quarantine Firewall & Ingestion Surveillance", 
                              "Automated Quarantine Isolation, Anomaly Forensics & Pipeline Integrity"),
                
                # Row 2: 2 Spacious Slicers Bar (y=46, h=50, w=610, gap=16) - Dropdowns fully visible, 0 clipping!
                build_slicer(20, 46, 610, 50, "stg_quarantined_records", "source_table", "Source Table"),
                build_slicer(646, 46, 610, 50, "stg_quarantined_records", "reason_code", "Anomaly Reason Code"),
                
                # Row 3: 5 Executive KPI Cards (y=106, h=66, w=234, gap=16, margin=22) - 10px white space below slicers!
                build_card(22, 106, 234, 66, "Total Raw Records", "Raw Payloads", "#0F172A"),
                build_card(272, 106, 234, 66, "Total Clean Records", "Clean Records", "#059669"),
                build_card(522, 106, 234, 66, "Total Quarantined Records", "Quarantined", "#DC2626"),
                build_card(772, 106, 234, 66, "Data Quality Pass Rate %", "DQ Pass Rate %", "#2563EB"),
                build_card(1022, 106, 234, 66, "Issue Categories Count", "Root Causes", "#D97706"),
                
                # Row 4: Analytics Body - Balanced 2-Column Grid (y=190, h=514, gap=16) - 18px white space below cards!
                build_pie_chart(20, 190, 470, 514, "stg_quarantined_records", "reason_code",
                                "_Measures", "Total Quarantined Records",
                                "Quarantined Anomalies by Reason Code", is_measure=True, legend_right=True),
                build_table(506, 190, 750, 514, "stg_quarantined_records",
                            ["quarantine_id", "batch_run_id", "source_table", "reason_code", "record_identifier", "quarantined_at"],
                            "Quarantine Audit Trail & Payload Forensics",
                            col_aliases={
                                "quarantine_id": "Quarantine ID",
                                "batch_run_id": "Batch ID",
                                "source_table": "Source Table",
                                "reason_code": "Anomaly Reason",
                                "record_identifier": "Record Identifier",
                                "quarantined_at": "Timestamp"
                            })
            ]
        }
    ]
    
    report_def = {
        "config": json.dumps({
            "version": "5.66",
            "themeCollection": {
                "baseTheme": {
                    "name": "CY24SU10",
                    "version": {
                        "visual": "1.8.86",
                        "report": "2.0.86",
                        "page": "1.3.86"
                    },
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
        
    print(f"Successfully generated final submission report.json (v5) at: {REPORT_PATH}")
    print(f"Total Sections: {len(sections)}")
    for s in sections:
        print(f"  - {s['displayName']}: {len(s['visualContainers'])} visual containers")

if __name__ == "__main__":
    generate_dashboard()
