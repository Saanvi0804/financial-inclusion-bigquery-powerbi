"""
Packages the complete Financial Inclusion Analytics Warehouse recruitment submission.
Generates submission/Financial_Inclusion_Analytics_Submission.zip containing:
- README.md, run.bat, requirements.txt, .env.example, .gitignore
- scripts/
- sql/
- tests/
- docs/
- powerbi/
- data/powerbi_extracts/

Excludes:
- .git, .pytest_cache, __pycache__, *.pyc, *.duckdb, data/raw, .env, temporary files
"""

import os
import zipfile
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("CreateSubmissionZip")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUBMISSION_DIR = os.path.join(PROJECT_ROOT, "submission")
ZIP_PATH = os.path.join(SUBMISSION_DIR, "Financial_Inclusion_Analytics_Submission.zip")

EXCLUDE_DIRS = {
    ".git",
    ".pytest_cache",
    "__pycache__",
    ".venv",
    "venv",
    "raw"  # Exclude data/raw to keep zip lightweight; powerbi_extracts has clean data
}

EXCLUDE_EXTS = {
    ".pyc",
    ".duckdb",
    ".duckdb.wal",
    ".log",
    ".tmp"
}

EXCLUDE_FILES = {
    ".env",
    "Financial_Inclusion_Analytics_Submission.zip"
}

def create_zip():
    os.makedirs(SUBMISSION_DIR, exist_ok=True)
    logger.info("Creating submission package at: %s", ZIP_PATH)

    total_files = 0
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
        for root, dirs, files in os.walk(PROJECT_ROOT):
            # Prune excluded directories in-place
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.endswith(".egg-info")]
            
            # Don't include submission folder itself inside the zip
            if os.path.abspath(root).startswith(os.path.abspath(SUBMISSION_DIR)):
                continue

            for file in files:
                if file in EXCLUDE_FILES:
                    continue
                _, ext = os.path.splitext(file)
                if ext.lower() in EXCLUDE_EXTS:
                    continue
                
                # Check if it's inside data/raw
                rel_path = os.path.relpath(os.path.join(root, file), PROJECT_ROOT)
                if rel_path.startswith(os.path.join("data", "raw")):
                    continue

                abs_file = os.path.join(root, file)
                zip_arcname = os.path.join("financial-inclusion-bigquery-powerbi", rel_path)
                zipf.write(abs_file, zip_arcname)
                total_files += 1

    zip_size_mb = os.path.getsize(ZIP_PATH) / (1024 * 1024)
    logger.info("Submission package created successfully!")
    logger.info("  Total files bundled: %d", total_files)
    logger.info("  Package size: %.2f MB", zip_size_mb)
    logger.info("  Location: %s", ZIP_PATH)

if __name__ == "__main__":
    create_zip()
