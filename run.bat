@echo off
echo ===============================================================================
echo Financial Inclusion Analytics Warehouse
echo An End-to-End Financial Analytics and Business Intelligence Solution
echo ===============================================================================

echo.
echo [Step 1/6] Generating synthetic portfolio datasets (52,000 loans, 533k txns)...
python scripts/generate_data.py
if %ERRORLEVEL% NEQ 0 (echo [ERROR] Data generation failed! & exit /b %ERRORLEVEL%)

echo.
echo [Step 2/6] Ingesting raw tables with metadata and audit logging into BigQuery...
python scripts/ingest_bigquery.py
if %ERRORLEVEL% NEQ 0 (echo [ERROR] Ingestion failed! & exit /b %ERRORLEVEL%)

echo.
echo [Step 3/6] Running BigQuery Standard SQL transformations (Staging, Dims, Facts, KPIs)...
python scripts/run_pipeline.py
if %ERRORLEVEL% NEQ 0 (echo [ERROR] SQL pipeline execution failed! & exit /b %ERRORLEVEL%)

echo.
echo [Step 4/6] Profiling warehouse and generating exhaustive data quality report...
python scripts/profile_data.py
if %ERRORLEVEL% NEQ 0 (echo [ERROR] Profiling failed! & exit /b %ERRORLEVEL%)

echo.
echo [Step 5/6] Running independent Python financial verification and PAR30 reconciliation...
python scripts/verify_recalculation.py
if %ERRORLEVEL% NEQ 0 (echo [ERROR] Financial verification failed! & exit /b %ERRORLEVEL%)

echo.
echo [Step 6/6] Executing automated enterprise test suite (64 Pytest tests)...
python -m pytest tests -v
if %ERRORLEVEL% NEQ 0 (echo [ERROR] Automated tests failed! & exit /b %ERRORLEVEL%)

echo.
echo ===============================================================================
echo Pipeline execution successfully completed with 100%% verification!
echo ===============================================================================
