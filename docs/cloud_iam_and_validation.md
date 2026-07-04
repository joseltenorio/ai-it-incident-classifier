# Cloud IAM and Deployment Validation

This document describes the IAM permissions and validation checks needed for the Cloud Run deployment of the AI IT Incident Classifier.

## Runtime Service Account

Cloud Run runs the backend using a service account.

For a portfolio project, you can start with the default Compute service account, but a dedicated service account is cleaner.

Recommended service account name:

```text
ai-it-incident-classifier-runtime
```

## Create Runtime Service Account

### Bash

```bash
gcloud iam service-accounts create ai-it-incident-classifier-runtime \
  --display-name="AI IT Incident Classifier Runtime"
```

### PowerShell

```powershell
gcloud iam service-accounts create ai-it-incident-classifier-runtime `
  --display-name="AI IT Incident Classifier Runtime"
```

Service account email format:

```text
ai-it-incident-classifier-runtime@your-google-cloud-project-id.iam.gserviceaccount.com
```

## Required Runtime Permissions

The Cloud Run runtime service account needs to insert and query rows in BigQuery.

Minimum recommended roles for this project:

```text
roles/bigquery.jobUser
roles/bigquery.dataEditor
```

For stricter access, assign dataset-level permissions where possible.

## Grant Project-Level BigQuery Job User

```bash
gcloud projects add-iam-policy-binding your-google-cloud-project-id \
  --member="serviceAccount:ai-it-incident-classifier-runtime@your-google-cloud-project-id.iam.gserviceaccount.com" \
  --role="roles/bigquery.jobUser"
```

## Grant BigQuery Data Editor

For a simple portfolio deployment:

```bash
gcloud projects add-iam-policy-binding your-google-cloud-project-id \
  --member="serviceAccount:ai-it-incident-classifier-runtime@your-google-cloud-project-id.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataEditor"
```

For a stricter setup, prefer granting access only to the `ai_operations` dataset from the BigQuery console.

## Deploy Using Runtime Service Account

```bash
gcloud run deploy ai-it-incident-classifier-api \
  --service-account ai-it-incident-classifier-runtime@your-google-cloud-project-id.iam.gserviceaccount.com
```

This flag should be combined with the full deployment command from `docs/cloud_run_deployment.md`.

## Validation Checklist

After deployment, validate:

```text
GET /health
GET /ready
POST /incidents/classify
GET /incidents
GET /incidents/{incident_id}
```

## Health Check

```bash
curl -i https://your-cloud-run-url/health
```

Expected:

```json
{
  "status": "healthy"
}
```

## Readiness Check

```bash
curl -i https://your-cloud-run-url/ready
```

Expected when correctly configured:

```json
{
  "status": "ready",
  "environment": "cloud",
  "classifier_provider": "mock",
  "bigquery_persistence_enabled": true
}
```

## Classification Check

```bash
curl -X POST https://your-cloud-run-url/incidents/classify \
  -H "Content-Type: application/json" \
  -d '{
    "title": "No puedo conectarme a la VPN",
    "description": "Desde ayer intento conectarme a la VPN de la empresa, pero aparece error de autenticación.",
    "reported_by": "usuario.demo@empresa.com",
    "source_channel": "api"
  }'
```

Expected:

- HTTP 200
- `incident_id` starts with `INC-`
- `category` is a controlled value
- Response includes `X-Request-ID`

## BigQuery Check

Run:

```sql
SELECT
  incident_id,
  title,
  category,
  priority,
  responsible_area,
  confidence_level,
  needs_human_review,
  model_name,
  model_latency_ms,
  created_at
FROM `your-google-cloud-project-id.ai_operations.incident_classifications`
ORDER BY created_at DESC
LIMIT 10;
```

Expected:

- New incident records appear after calling `POST /incidents/classify`.
- `model_name` reflects the active provider.
- `model_latency_ms` is `0` for mock and greater than `0` for Gemini responses.

## Incident History Check

```bash
curl -i https://your-cloud-run-url/incidents
```

Expected:

- HTTP 200
- Recent BigQuery records are returned.

Then test one detail endpoint:

```bash
curl -i https://your-cloud-run-url/incidents/INC-YYYYMMDD-XXXXXXXX
```

Expected:

- HTTP 200 for an existing incident.
- HTTP 404 for a non-existing incident.
