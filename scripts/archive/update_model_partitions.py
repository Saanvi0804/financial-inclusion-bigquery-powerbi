"""
Audits and updates Power Query M partition expressions in model.bim.
Ensures:
1. Resilient Location parameter resolution (handles Windows backslashes, forward slashes, and trailing paths).
2. Explicit column counts (Columns = N) for fast, low-memory parsing.
3. Appropriate QuoteStyle (QuoteStyle.None for large fact tables, QuoteStyle.Csv for stg_quarantined_records).
4. Explicit Table.TransformColumnTypes with invariant 'en-US' locale culture.
5. Simplified _Measures partition using native Table.FromRows.
"""

import json
import os
import csv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_BIM_PATH = os.path.join(PROJECT_ROOT, "powerbi", "Financial_Inclusion_Analytics.SemanticModel", "model.bim")
EXTRACTS_DIR = os.path.join(PROJECT_ROOT, "data", "powerbi_extracts")

TYPE_MAP = {
    "int64": "Int64.Type",
    "double": "type number",
    "string": "type text",
    "dateTime": "type datetime",
    "boolean": "type logical"
}

def update_partitions():
    with open(MODEL_BIM_PATH, "r", encoding="utf-8") as f:
        model = json.load(f)

    tables = model.get("model", {}).get("tables", [])
    
    for table in tables:
        tname = table.get("name")
        if tname == "_Measures":
            table["partitions"] = [
                {
                    "name": "_Measures",
                    "mode": "import",
                    "source": {
                        "type": "m",
                        "expression": [
                            "let",
                            "    Source = Table.FromRows({{\"1\"}}, type table [Dummy = text])",
                            "in",
                            "    Source"
                        ]
                    }
                }
            ]
            print(f"Updated partition for {tname}")
            continue

        csv_file = f"{tname}.csv"
        csv_path = os.path.join(EXTRACTS_DIR, csv_file)
        if not os.path.exists(csv_path):
            print(f"Warning: CSV not found for table {tname}: {csv_path}")
            continue

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)
            col_count = len(headers)

        quote_style = "QuoteStyle.Csv" if tname == "stg_quarantined_records" else "QuoteStyle.None"

        cols_metadata = {c["name"]: c.get("dataType", "string") for c in table.get("columns", [])}

        transform_lines = []
        for i, col_name in enumerate(headers):
            dtype = cols_metadata.get(col_name, "string")
            m_type = TYPE_MAP.get(dtype, "type text")
            comma = "," if i < len(headers) - 1 else ""
            transform_lines.append(f'        {{"{col_name}", {m_type}}}{comma}')

        expression = [
            "let",
            '    RawLocation = Text.TrimEnd(Text.Replace(Text.Replace(Text.From(Location), Character.FromNumber(92), "/"), "\\\\", "/"), {"/"}),',
            '    BaseDir = if Text.EndsWith(RawLocation, "/data/powerbi_extracts", Comparer.OrdinalIgnoreCase) then RawLocation else RawLocation & "/data/powerbi_extracts",',
            f'    FilePath = BaseDir & "/{csv_file}",',
            f'    Source = Csv.Document(File.Contents(FilePath), [Delimiter=",", Columns={col_count}, Encoding=65001, QuoteStyle={quote_style}]),',
            '    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),',
            '    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", {',
            *transform_lines,
            '    }, "en-US")',
            "in",
            '    #"Changed Type"'
        ]

        table["partitions"] = [
            {
                "name": tname,
                "mode": "import",
                "source": {
                    "type": "m",
                    "expression": expression
                }
            }
        ]
        print(f"Updated partition for {tname} ({col_count} columns, {quote_style})")

    with open(MODEL_BIM_PATH, "w", encoding="utf-8") as f:
        json.dump(model, f, indent=2)

    print("\nSuccessfully updated all partitions in model.bim!")

if __name__ == "__main__":
    update_partitions()
