import json
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIM_PATH = os.path.join(PROJECT_ROOT, "powerbi", "Financial_Inclusion_Analytics.SemanticModel", "model.bim")
REPORT_PATH = os.path.join(PROJECT_ROOT, "powerbi", "Financial_Inclusion_Analytics.Report", "report.json")

with open(BIM_PATH, "r", encoding="utf-8") as f:
    bim = json.load(f)

valid_refs = set()
for t in bim["model"]["tables"]:
    tname = t["name"]
    for c in t.get("columns", []):
        valid_refs.add(f"{tname}.{c['name']}")
    for m in t.get("measures", []):
        valid_refs.add(f"{tname}.{m['name']}")

print(f"Total valid model references: {len(valid_refs)}")

with open(REPORT_PATH, "r", encoding="utf-8") as f:
    rep = json.load(f)

missing_refs = set()
out_of_bounds = []
total_refs = 0
total_visuals = 0

for s in rep["sections"]:
    for vc in s["visualContainers"]:
        total_visuals += 1
        x, y, w, h = vc.get("x", 0), vc.get("y", 0), vc.get("width", 0), vc.get("height", 0)
        if x + w > 1280 or y + h > 720:
            out_of_bounds.append((s["displayName"], x, y, w, h, x + w, y + h))
        cfg = json.loads(vc["config"])
        sv = cfg.get("singleVisual", {})
        for proj_list in sv.get("projections", {}).values():
            for p in proj_list:
                qref = p.get("queryRef")
                if qref:
                    total_refs += 1
                    if qref not in valid_refs:
                        missing_refs.add(qref)

print(f"Total visuals checked: {total_visuals}")
print(f"Total queryRefs checked: {total_refs}")
print(f"Missing queryRefs: {missing_refs}")
print(f"Out of bounds visuals: {out_of_bounds}")

assert len(missing_refs) == 0, f"Found missing refs: {missing_refs}"
assert len(out_of_bounds) == 0, f"Found out of bounds visuals: {out_of_bounds}"
print("SUCCESS: ALL VISUAL QUERY REFERENCES AND CANVAS BOUNDS ARE 100% VALID!")
