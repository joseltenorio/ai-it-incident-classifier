# Postman Cloud Validation Suite

This document explains how to validate the AI IT Incident Classifier API deployed on Cloud Run using Postman.

The suite validates the cloud runtime, incident classification contract, request validation errors and BigQuery-backed incident history endpoints.

## Files

```text
postman/ai_it_incident_classifier_cloud.postman_collection.json
postman/ai_it_incident_classifier_cloud.postman_environment.json
```

## Recommended Cloud Run Mode

For routine validation, keep Cloud Run in mock mode to avoid unnecessary Gemini API usage:

```bash
gcloud run services update "$SERVICE_NAME"   --region "$REGION"   --update-env-vars "CLASSIFIER_PROVIDER=mock"
```

Validate readiness:

```bash
curl -i "$SERVICE_URL/ready"
```

Expected readiness fields:

```json
{
  "status": "ready",
  "environment": "cloud",
  "classifier_provider": "mock",
  "bigquery_persistence_enabled": true
}
```

Gemini can be validated separately by switching Cloud Run to `CLASSIFIER_PROVIDER=gemini` and running only one or two classification requests.

## Import in Postman

1. Open Postman.
2. Click **Import**.
3. Import `ai_it_incident_classifier_cloud.postman_collection.json`.
4. Import `ai_it_incident_classifier_cloud.postman_environment.json`.
5. Select the environment **AI IT Incident Classifier - Cloud**.
6. Confirm that `base_url` points to the active Cloud Run URL.

Default value:

```text
https://ai-it-incident-classifier-api-n4pjkcgowq-uc.a.run.app
```

If Cloud Run generates a different service URL, update the `base_url` environment variable.

## Collection Structure

```text
AI IT Incident Classifier - Cloud Validation
│
├── 01 Runtime
│   ├── GET Root
│   ├── GET Health
│   └── GET Ready
│
├── 02 Classification - Valid Cases
│   ├── POST Classify VPN Incident
│   ├── POST Classify Access Incident
│   ├── POST Classify Security Incident
│   ├── POST Classify Cloud Incident
│   ├── POST Classify Database Incident
│   └── POST Classify Application Incident
│
├── 03 Classification - Validation Errors
│   ├── POST Missing Title
│   ├── POST Missing Description
│   ├── POST Short Title
│   ├── POST Short Description
│   ├── POST Invalid Email
│   └── POST Invalid Source Channel
│
├── 04 Incident History
│   ├── GET Recent Incidents
│   ├── GET Recent Incidents With Limit
│   ├── GET Incident Detail
│   ├── GET Unknown Incident
│   └── GET Invalid Limit
│
└── 05 Cloud Evidence
    ├── GET Ready Cloud Runtime
    ├── POST Classify Portfolio Demo Incident
    └── GET Portfolio Demo Incident Detail
```

## Variables

The collection and environment use variables to avoid hardcoded values:

| Variable | Purpose |
|---|---|
| `base_url` | Cloud Run service URL. |
| `incident_id` | Latest incident ID captured from classification/history responses. |
| `portfolio_incident_id` | Incident ID created by the portfolio demo request. |
| `reported_by` | Demo reporter email. |
| `source_channel` | Incident source channel, usually `api`. |
| `unknown_incident_id` | Non-existing incident ID used for 404 validation. |

Classification payloads also use variables such as `vpn_title`, `access_description`, `cloud_title`, and others.

## Suggested Execution Order

Run folders in this order:

```text
01 Runtime
02 Classification - Valid Cases
04 Incident History
03 Classification - Validation Errors
05 Cloud Evidence
```

The history detail request depends on `incident_id`, which is automatically saved by classification and history requests.

## Expected Results

Runtime checks:

```text
GET /                  → 200
GET /health            → 200
GET /ready             → 200
X-Request-ID header    → present
```

Classification checks:

```text
POST /incidents/classify → 200
incident_id starts with INC-
category is a controlled enum value
priority is a controlled enum value
responsible_area is a controlled enum value
model_name ends with -mock or -gemini
```

Validation checks:

```text
Invalid request payloads → 422
```

History checks:

```text
GET /incidents                 → 200
GET /incidents?limit=3         → 200 and at most 3 records
GET /incidents/{{incident_id}} → 200
GET /incidents/INC-UNKNOWN     → 404
GET /incidents?limit=0         → 422
```

## Newman Optional Execution

If Newman is installed, run:

```bash
newman run postman/ai_it_incident_classifier_cloud.postman_collection.json   -e postman/ai_it_incident_classifier_cloud.postman_environment.json
```

Run a specific folder:

```bash
newman run postman/ai_it_incident_classifier_cloud.postman_collection.json   -e postman/ai_it_incident_classifier_cloud.postman_environment.json   --folder "01 Runtime"
```

## BigQuery Evidence Query

After running classification requests, validate BigQuery:

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
FROM `ai-it-incident-classifier-jl.ai_operations.incident_classifications`
ORDER BY created_at DESC
LIMIT 10;
```

## Portfolio Evidence

Recommended screenshots:

1. Postman `GET /ready` with `status = ready`.
2. Postman `POST /incidents/classify` with `incident_id` and `model_name`.
3. Postman `GET /incidents` showing recent records.
4. Postman `GET /incidents/{{incident_id}}` showing full detail.
5. BigQuery table with the generated incident.
6. Cloud Run logs showing `X-Request-ID` and request completion logs.

## Notes

- The collection is safe to commit because it does not include API keys.
- Keep Gemini disabled during routine validation unless you intentionally want to test the real AI provider.
- The Secret Manager value for `GEMINI_API_KEY` must not be exported to Postman or committed to Git.
