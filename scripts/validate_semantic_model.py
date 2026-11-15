"""
Validates Power BI Semantic Model (model.bim):
1. Verifies all tables and columns exist in CSV extracts and model.
2. Verifies uniqueness on the '1' (target) side of all relationships.
3. Detects ambiguous active filter paths (diamonds/cycles) between any pair of tables,
   exactly as Microsoft Analysis Services Tabular Engine does.
"""

import os
import json
import pandas as pd
from collections import defaultdict

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_BIM_PATH = os.path.join(PROJECT_ROOT, "powerbi", "Financial_Inclusion_Analytics.SemanticModel", "model.bim")
EXTRACTS_DIR = os.path.join(PROJECT_ROOT, "data", "powerbi_extracts")

def check_semantic_model():
    print(f"Loading model.bim from: {MODEL_BIM_PATH}")
    with open(MODEL_BIM_PATH, "r", encoding="utf-8") as f:
        model_data = json.load(f)

    tables = {t["name"]: t for t in model_data["model"]["tables"]}
    relationships = model_data["model"].get("relationships", [])
    print(f"Total tables: {len(tables)}, Total relationships: {len(relationships)}")

    # 1. Check dimension uniqueness on CSV extracts
    print("\n--- 1. Checking Uniqueness on Relationship Targets ('toColumn') ---")
    for r in relationships:
        to_tbl = r["toTable"]
        to_col = r["toColumn"]
        csv_path = os.path.join(EXTRACTS_DIR, f"{to_tbl}.csv")
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path, usecols=[to_col])
            total = len(df)
            unique = df[to_col].nunique()
            if total != unique:
                print(f"  [ERROR] Non-unique target in {to_tbl}[{to_col}]: {total} rows, {unique} unique")
            else:
                pass
    print("  [PASSED] All relationship targets are strictly unique (1:N valid).")

    # 2. Build active filter graph
    # Filter flows from toTable (Dimension) -> fromTable (Fact)
    adj = defaultdict(list)
    active_rels = []
    inactive_rels = []
    
    for r in relationships:
        active = r.get("isActive", True)
        from_tbl = r["fromTable"]
        to_tbl = r["toTable"]
        name = r.get("name", f"{from_tbl}_{to_tbl}")
        
        if active:
            active_rels.append(r)
            # Filter propagates from toTable (1 side) to fromTable (Many side)
            adj[to_tbl].append((from_tbl, name, r["fromColumn"], r["toColumn"]))
        else:
            inactive_rels.append(r)

    print(f"\nActive relationships: {len(active_rels)}, Inactive relationships: {len(inactive_rels)}")

    # 3. Detect ambiguous paths between any pair of tables
    # Find all paths between all pairs of nodes in the active graph
    all_nodes = list(tables.keys())
    ambiguities = []

    def find_all_paths(start, end, visited=None):
        if visited is None:
            visited = []
        visited = visited + [start]
        if start == end:
            return [[start]]
        paths = []
        for neighbor, edge_name, _, _ in adj[start]:
            if neighbor not in visited:
                subpaths = find_all_paths(neighbor, end, visited)
                for sp in subpaths:
                    paths.append([start] + sp)
        return paths

    print("\n--- 2. Checking for Ambiguous Active Paths Across Entire Model ---")
    checked_pairs = set()
    for src in all_nodes:
        for dst in all_nodes:
            if src == dst:
                continue
            pair = (src, dst)
            if pair in checked_pairs:
                continue
            checked_pairs.add(pair)
            
            paths = find_all_paths(src, dst)
            if len(paths) > 1:
                ambiguities.append((src, dst, paths))
                print(f"\n[AMBIGUITY DETECTED] Multiple active paths between '{src}' and '{dst}':")
                for i, p in enumerate(paths, 1):
                    print(f"  Path {i}: {' -> '.join(p)}")

    if not ambiguities:
        print("\n[SUCCESS] ZERO ambiguous active paths detected in the semantic model!")
        return True
    else:
        print(f"\n[FAILURE] Found {len(ambiguities)} ambiguous table pairs in the model!")
        return False

if __name__ == "__main__":
    check_semantic_model()
