-- sql/create_incident_classifications_table.sql

-- Creates the BigQuery table that stores classified IT support incidents.
-- Replace `your-project-id` with the active Google Cloud project ID before
-- running this script in the BigQuery console.

CREATE TABLE IF NOT EXISTS `your-project-id.ai_operations.incident_classifications` (
  incident_id STRING NOT NULL,
  title STRING NOT NULL,
  description STRING NOT NULL,
  reported_by STRING,
  source_channel STRING NOT NULL,

  category STRING NOT NULL,
  priority STRING NOT NULL,
  responsible_area STRING NOT NULL,
  summary STRING NOT NULL,
  suggested_action STRING NOT NULL,
  confidence_level STRING NOT NULL,
  needs_human_review BOOL NOT NULL,

  model_name STRING NOT NULL,
  model_latency_ms INT64 NOT NULL,
  raw_model_response STRING,

  created_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(created_at)
CLUSTER BY category, priority, responsible_area
OPTIONS (
  description = "Stores AI-classified IT support incidents for operational analysis"
);