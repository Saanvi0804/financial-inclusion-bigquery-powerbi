import zipfile
import os

ZIP_PATH = r"C:\Users\Saanvi Shetty\Desktop\projects\financial-inclusion-bigquery-powerbi\submission\Financial_Inclusion_Analytics_Submission.zip"

print("=" * 80)
print("VERIFYING SUBMISSION ZIP INTEGRITY & REQUIRED DELIVERABLES")
print("=" * 80)

fsize_mb = os.path.getsize(ZIP_PATH) / (1024 * 1024)
print(f"ZIP Path: {ZIP_PATH}")
print(f"ZIP Size: {fsize_mb:.2f} MB")

with zipfile.ZipFile(ZIP_PATH, "r") as zf:
    # 1. CRC test
    print("\n--- Testing ZIP Archive Integrity (CRC Check) ---")
    bad_file = zf.testzip()
    if bad_file is None:
        print("CRC Check Result: PASS (0 CRC errors, archive is fully valid)")
    else:
        print(f"CRC Check Result: FAIL (Corrupted file: {bad_file})")

    namelist = zf.namelist()
    print(f"Total Entries in ZIP: {len(namelist)}")

    # 2. Check PBIX
    print("\n--- Verifying PBIX File ---")
    pbix_files = [f for f in namelist if f.endswith(".pbix")]
    for p in pbix_files:
        info = zf.getinfo(p)
        print(f"Found PBIX: {p} ({info.file_size / (1024 * 1024):.2f} MB)")
    if not pbix_files:
        print("PBIX NOT FOUND!")

    # 3. Check Screenshots
    print("\n--- Verifying Screenshots ---")
    screenshot_files = [f for f in namelist if "screenshots" in f and f.endswith(".png")]
    for s in sorted(screenshot_files):
        info = zf.getinfo(s)
        print(f"Found Screenshot: {s} ({info.file_size / 1024:.1f} KB)")
    print(f"Total Screenshots: {len(screenshot_files)} / 5")

    # 4. Check PBIP
    print("\n--- Verifying PBIP Project ---")
    pbip_files = [f for f in namelist if f.endswith(".pbip")]
    pbir_files = [f for f in namelist if f.endswith(".pbir")]
    report_json = [f for f in namelist if f.endswith("report.json")]
    model_bim = [f for f in namelist if f.endswith("model.bim")]
    print(f"Found .pbip: {pbip_files}")
    print(f"Found .pbir: {pbir_files}")
    print(f"Found report.json: {report_json}")
    print(f"Found model.bim: {model_bim}")

    # 5. Check DuckDB Warehouse
    print("\n--- Verifying Warehouse ---")
    duckdb_files = [f for f in namelist if f.endswith(".duckdb")]
    for d in duckdb_files:
        info = zf.getinfo(d)
        print(f"Found DuckDB: {d} ({info.file_size / (1024 * 1024):.2f} MB)")

    # 6. Check SQL and Tests
    sql_files = [f for f in namelist if f.endswith(".sql")]
    test_files = [f for f in namelist if f.startswith("financial-inclusion-bigquery-powerbi/tests/") and f.endswith(".py")]
    extract_files = [f for f in namelist if "powerbi_extracts" in f and f.endswith(".csv")]
    archive_files = [f for f in namelist if "scripts/archive" in f]
    print(f"\nSQL transformation files: {len(sql_files)}")
    print(f"Automated test files: {len(test_files)}")
    print(f"Curated CSV extracts: {len(extract_files)}")
    print(f"Archived historical scripts: {len(archive_files)}")

print("\n" + "=" * 80)
print("ZIP VERIFICATION COMPLETE")
print("=" * 80)
