import json
import re

model_bim_path = 'powerbi/Financial_Inclusion_Analytics.SemanticModel/model.bim'
dax_path = 'powerbi/dax_measures.dax'
md_path = 'powerbi/dax_measures.md'

new_paid_dax = """SUMX(
    SUMMARIZE(
        kpi_vintage_curves,
        kpi_vintage_curves[cohort_month],
        kpi_vintage_curves[product_id]
    ),
    VAR _CurCohort = kpi_vintage_curves[cohort_month]
    VAR _CurProduct = kpi_vintage_curves[product_id]
    VAR _MaxMOB = 
        CALCULATE(
            MAX(kpi_vintage_curves[month_on_book]),
            kpi_vintage_curves[cohort_month] = _CurCohort,
            kpi_vintage_curves[product_id] = _CurProduct
        )
    RETURN
        CALCULATE(
            SUM(kpi_vintage_curves[cumulative_amount_paid]),
            kpi_vintage_curves[cohort_month] = _CurCohort,
            kpi_vintage_curves[product_id] = _CurProduct,
            kpi_vintage_curves[month_on_book] = _MaxMOB
        )
)"""

new_due_dax = """SUMX(
    SUMMARIZE(
        kpi_vintage_curves,
        kpi_vintage_curves[cohort_month],
        kpi_vintage_curves[product_id]
    ),
    VAR _CurCohort = kpi_vintage_curves[cohort_month]
    VAR _CurProduct = kpi_vintage_curves[product_id]
    VAR _MaxMOB = 
        CALCULATE(
            MAX(kpi_vintage_curves[month_on_book]),
            kpi_vintage_curves[cohort_month] = _CurCohort,
            kpi_vintage_curves[product_id] = _CurProduct
        )
    RETURN
        CALCULATE(
            SUM(kpi_vintage_curves[cumulative_scheduled_due]),
            kpi_vintage_curves[cohort_month] = _CurCohort,
            kpi_vintage_curves[product_id] = _CurProduct,
            kpi_vintage_curves[month_on_book] = _MaxMOB
        )
)"""

# 1. Update model.bim
with open(model_bim_path, 'r', encoding='utf-8') as f:
    bim = json.load(f)

measures_table = [t for t in bim['model']['tables'] if t.get('name') == '_Measures'][0]
for m in measures_table['measures']:
    if m['name'] == 'Cumulative Amount Paid (Vintage)':
        m['expression'] = new_paid_dax
        print("Updated 'Cumulative Amount Paid (Vintage)' in model.bim")
    elif m['name'] == 'Cumulative Scheduled Due (Vintage)':
        m['expression'] = new_due_dax
        print("Updated 'Cumulative Scheduled Due (Vintage)' in model.bim")

with open(model_bim_path, 'w', encoding='utf-8') as f:
    json.dump(bim, f, indent=2)

# 2. Update dax_measures.dax
with open(dax_path, 'r', encoding='utf-8') as f:
    dax_content = f.read()

# Replace Cumulative Scheduled Due (Vintage)
old_due_pattern = r"(MEASURE '_Measures'\[Cumulative Scheduled Due \(Vintage\)\] =\s*)\n\s*SUM\(kpi_vintage_curves\[cumulative_scheduled_due\]\)"
new_due_block = r"\1\n    " + new_due_dax.replace("\n", "\n    ")
dax_content = re.sub(old_due_pattern, new_due_block, dax_content)

# Replace Cumulative Amount Paid (Vintage)
old_paid_pattern = r"(MEASURE '_Measures'\[Cumulative Amount Paid \(Vintage\)\] =\s*)\n\s*SUM\(kpi_vintage_curves\[cumulative_amount_paid\]\)"
new_paid_block = r"\1\n    " + new_paid_dax.replace("\n", "\n    ")
dax_content = re.sub(old_paid_pattern, new_paid_block, dax_content)

with open(dax_path, 'w', encoding='utf-8') as f:
    f.write(dax_content)
print("Updated dax_measures.dax")

# 3. Update dax_measures.md
with open(md_path, 'r', encoding='utf-8') as f:
    md_content = f.read()

old_paid_md = r"(### Cumulative Amount Paid \(Vintage\)[\s\S]*?```dax\n)([\s\S]*?)(```)"
new_paid_md = r"\1" + new_paid_dax + r"\n\3"
md_content = re.sub(old_paid_md, new_paid_md, md_content)

old_due_md = r"(### Cumulative Scheduled Due \(Vintage\)[\s\S]*?```dax\n)([\s\S]*?)(```)"
new_due_md = r"\1" + new_due_dax + r"\n\3"
md_content = re.sub(old_due_md, new_due_md, md_content)

with open(md_path, 'w', encoding='utf-8') as f:
    f.write(md_content)
print("Updated dax_measures.md")
