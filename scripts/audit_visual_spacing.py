import json
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_PATH = os.path.join(PROJECT_ROOT, "powerbi", "Financial_Inclusion_Analytics.Report", "report.json")

with open(REPORT_PATH, "r", encoding="utf-8") as f:
    rep = json.load(f)

print("=" * 80)
print("AUDITING POWER BI DASHBOARD VISUAL SPACING, GAPS AND ALIGNMENT")
print("=" * 80)

for s_idx, s in enumerate(rep["sections"], 1):
    dname = s["displayName"]
    vcs = s["visualContainers"]
    print(f"\n--- Section {s_idx}: {dname} ({len(vcs)} visuals) ---")
    
    # Sort visuals by y then x
    sorted_vcs = []
    for vc in vcs:
        x, y, w, h = vc["x"], vc["y"], vc["width"], vc["height"]
        cfg = json.loads(vc["config"])
        vtype = cfg.get("singleVisual", {}).get("visualType", "unknown")
        title = "No Title"
        objects = cfg.get("singleVisual", {}).get("objects", {})
        if "title" in objects and objects["title"]:
            t_obj = objects["title"][0].get("properties", {}).get("text", {})
            title = t_obj.get("expr", {}).get("Literal", {}).get("Value", title)
        sorted_vcs.append({
            "x": x, "y": y, "w": w, "h": h, 
            "right": x + w, "bottom": y + h,
            "type": vtype, "title": title.strip("'")
        })
    
    # Group by approximate rows based on y coordinate
    rows = {}
    for v in sorted_vcs:
        # snap y within 5px
        found_row = None
        for r_y in rows:
            if abs(v["y"] - r_y) <= 8:
                found_row = r_y
                break
        if found_row is not None:
            rows[found_row].append(v)
        else:
            rows[v["y"]] = [v]
            
    sorted_row_ys = sorted(rows.keys())
    print(f"Total Rows detected: {len(sorted_row_ys)}")
    
    prev_row_bottom = 0
    for r_idx, r_y in enumerate(sorted_row_ys, 1):
        row_vcs = sorted(rows[r_y], key=lambda item: item["x"])
        min_x = row_vcs[0]["x"]
        max_r = max(v["right"] for v in row_vcs)
        row_h = max(v["h"] for v in row_vcs)
        row_bottom = max(v["bottom"] for v in row_vcs)
        v_gap = r_y - prev_row_bottom if prev_row_bottom > 0 else 0
        
        print(f"  Row {r_idx} (y={r_y}, h={row_h}, bottom={row_bottom}, V-Gap from prev: {v_gap}px): {len(row_vcs)} visuals")
        print(f"    Left Margin: {min_x}px | Right Margin: {1280 - max_r}px | Span: {max_r - min_x}px")
        
        # Check horizontal gaps between visuals in this row
        if len(row_vcs) > 1:
            h_gaps = []
            for i in range(len(row_vcs) - 1):
                gap = row_vcs[i+1]["x"] - row_vcs[i]["right"]
                h_gaps.append(gap)
                if gap < 0:
                    print(f"    [ERROR] Overlap between visual {i+1} and {i+2}: gap = {gap}px!")
            print(f"    H-Gaps between visuals: {h_gaps} (Min: {min(h_gaps)}px, Max: {max(h_gaps)}px)")
            
        prev_row_bottom = row_bottom

print("\n" + "=" * 80)
print("AUDIT COMPLETE")
print("=" * 80)
