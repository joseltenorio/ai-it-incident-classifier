-- sql/create_bigquery_dataset.sql

-- Creates the BigQuery dataset used to store classified IT incidents.
-- Replace `your-project-id` with the active Google Cloud project ID before
-- running this script in the BigQuery console.

CREATE SCHEMA IF NOT EXISTS `your-project-id.ai_operations`
OPTIONS (
  location = "US",
  description = "Operational dataset for AI-classified IT support incidents"
);