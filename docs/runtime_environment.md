# Runtime Environment Variables

This document describes the environment variables used by the AI IT Incident Classifier backend.

The same settings are used in local development, Docker and Cloud Run.

## Application Settings

| Variable | Required | Default | Description |
|---|---:|---|---|
| `APP_NAME` | no | `AI IT Incident Classifier` | Application name displayed by FastAPI and root endpoint. |
| `APP_VERSION` | no | `0.1.0` | Application version displayed by FastAPI and root endpoint. |
| `ENVIRONMENT` | no | `local` | Runtime environment name. Suggested values: `local`, `cloud`. |

## Classifier Settings

| Variable | Required | Default | Description |
|---|---:|---|---|
| `CLASSIFIER_PROVIDER` | no | `mock` | Classifier provider. Supported values: `mock`, `gemini`. |
| `GEMINI_MODEL` | no | `gemini-2.5-flash` | Gemini model name used by the Gemini provider and metadata fields. |
| `GEMINI_API_KEY` | yes, when Gemini is enabled | empty | API key required when `CLASSIFIER_PROVIDER=gemini`. |

## BigQuery Settings

| Variable | Required | Default | Description |
|---|---:|---|---|
| `ENABLE_BIGQUERY_PERSISTENCE` | no | `false` | Enables or disables persistence of classified incidents in BigQuery. |
| `GOOGLE_CLOUD_PROJECT` | yes, when BigQuery persistence or history API is used | empty | Google Cloud project ID. |
| `BIGQUERY_DATASET` | no | `ai_operations` | BigQuery dataset used by the backend. |
| `BIGQUERY_TABLE` | no | `incident_classifications` | BigQuery table used by the backend. |

## Cloud Run Notes

Cloud Run injects the `PORT` environment variable into the container.

The Dockerfile starts Uvicorn with:

```text
--host 0.0.0.0 --port ${PORT}
```

The application does not require a local `.env` file in Cloud Run. Runtime values are configured as Cloud Run service environment variables.

## Recommended Local Mock Configuration

```env
ENVIRONMENT=local
CLASSIFIER_PROVIDER=mock
ENABLE_BIGQUERY_PERSISTENCE=false
GEMINI_MODEL=gemini-2.5-flash
```

## Recommended Cloud Mock Configuration

```env
ENVIRONMENT=cloud
CLASSIFIER_PROVIDER=mock
ENABLE_BIGQUERY_PERSISTENCE=true
GOOGLE_CLOUD_PROJECT=your-google-cloud-project-id
BIGQUERY_DATASET=ai_operations
BIGQUERY_TABLE=incident_classifications
GEMINI_MODEL=gemini-2.5-flash
```

## Recommended Cloud Gemini Configuration

```env
ENVIRONMENT=cloud
CLASSIFIER_PROVIDER=gemini
ENABLE_BIGQUERY_PERSISTENCE=true
GOOGLE_CLOUD_PROJECT=your-google-cloud-project-id
BIGQUERY_DATASET=ai_operations
BIGQUERY_TABLE=incident_classifications
GEMINI_MODEL=gemini-2.5-flash
GEMINI_API_KEY=your-api-key
```

For a production-grade deployment, store `GEMINI_API_KEY` in Secret Manager instead of passing it directly as a plain environment variable.
