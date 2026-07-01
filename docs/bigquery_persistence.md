# BigQuery Persistence Setup

This document explains how to configure BigQuery persistence for the AI IT Incident Classifier.

The API can classify incidents without BigQuery. Persistence is controlled through:

```env
ENABLE_BIGQUERY_PERSISTENCE=true
```

When enabled, every classified incident is stored in BigQuery for traceability and operational analysis.

## Required Google Cloud Resources

The persistence layer requires:

- Google Cloud project
- BigQuery API enabled
- BigQuery dataset
- BigQuery table
- Local or runtime credentials with BigQuery permissions

## Recommended Dataset

```text
ai_operations
```

## Recommended Table

```text
incident_classifications
```

## Environment Variables

Local `.env` example:

```env
APP_NAME=AI IT Incident Classifier
APP_VERSION=0.1.0
ENVIRONMENT=local

CLASSIFIER_PROVIDER=mock
ENABLE_BIGQUERY_PERSISTENCE=true

GOOGLE_CLOUD_PROJECT=your-google-cloud-project-id
BIGQUERY_DATASET=ai_operations
BIGQUERY_TABLE=incident_classifications

GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
```

## Local Authentication

Authenticate with the Google Cloud CLI:

```bash
gcloud auth login
```

Set the active project:

```bash
gcloud config set project your-google-cloud-project-id
```

Create local Application Default Credentials:

```bash
gcloud auth application-default login
```

The Python BigQuery client uses Application Default Credentials during local development.

## Enable BigQuery API

```bash
gcloud services enable bigquery.googleapis.com
```

## Create Dataset and Table

The SQL scripts are available in:

```text
sql/create_bigquery_dataset.sql
sql/create_incident_classifications_table.sql
```

Before running them, replace:

```text
your-project-id
```

with the real Google Cloud project ID.

Run the dataset script first, then the table script.

## Stored Fields

The BigQuery table stores:

- Original incident title and description
- Reporter and source channel
- Category, priority and responsible area
- Summary and suggested action
- Confidence level and manual review flag
- Model name
- Model latency in milliseconds
- Raw model response
- Creation timestamp

## Runtime Behavior

When `ENABLE_BIGQUERY_PERSISTENCE=false`, the API returns classifications without storing them.

When `ENABLE_BIGQUERY_PERSISTENCE=true`, the API attempts to insert each classification into BigQuery.

If BigQuery persistence fails, the API still returns the classification response and logs a warning. This keeps the classification flow available even when the persistence layer has a temporary issue.
