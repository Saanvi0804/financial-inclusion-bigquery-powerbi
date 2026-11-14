-- BigQuery DDL: 01_create_datasets.sql
-- Initializes the four core datasets for Financial Inclusion Analytics Warehouse

CREATE SCHEMA IF NOT EXISTS `fin_raw`
OPTIONS (
  description = "Immutable raw landing zone for financial inclusion loan feeds, transaction streams, and branch directories.",
  location = "US"
);

CREATE SCHEMA IF NOT EXISTS `fin_staging`
OPTIONS (
  description = "Cleansed, deduplicated, and normalized staging models, FIFO waterfall allocation, and quarantined record store.",
  location = "US"
);

CREATE SCHEMA IF NOT EXISTS `fin_warehouse`
OPTIONS (
  description = "Production enterprise star schema consisting of 6 dimension models and 3 fact models.",
  location = "US"
);

CREATE SCHEMA IF NOT EXISTS `fin_analytics`
OPTIONS (
  description = "Pre-aggregated analytical KPI models for Portfolio Health, Collection Efficiency, Vintage Curves, and Digital Adoption.",
  location = "US"
);
