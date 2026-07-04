# Runtime Observability

This document explains the runtime hardening and observability behavior of the AI IT Incident Classifier.

The backend is designed to run locally, in Docker and later on Cloud Run.

## Runtime Endpoints

The API exposes two runtime endpoints:

```text
GET /health
GET /ready
```

## Health Endpoint

### `GET /health`

The health endpoint checks whether the application process is alive and able to respond to HTTP requests.

Example response:

```json
{
  "status": "healthy"
}
```

This endpoint does not validate external configuration, Gemini API access or BigQuery access.

It is intended as a lightweight liveness check.

## Readiness Endpoint

### `GET /ready`

The readiness endpoint validates runtime configuration.

It checks whether the required settings are present for the selected classifier provider and persistence mode.

Example response when the service is ready:

```json
{
  "status": "ready",
  "environment": "local",
  "classifier_provider": "mock",
  "bigquery_persistence_enabled": false,
  "checks": {
    "gemini_api_key": "not_required",
    "google_cloud_project": "not_required",
    "bigquery_table_id": "not_required"
  }
}
```

Example response when Gemini is enabled but the API key is missing:

```json
{
  "status": "not_ready",
  "environment": "local",
  "classifier_provider": "gemini",
  "bigquery_persistence_enabled": false,
  "checks": {
    "gemini_api_key": "missing",
    "google_cloud_project": "not_required",
    "bigquery_table_id": "not_required"
  }
}
```

Example response when BigQuery persistence is enabled but the Google Cloud project is missing:

```json
{
  "status": "not_ready",
  "environment": "local",
  "classifier_provider": "mock",
  "bigquery_persistence_enabled": true,
  "checks": {
    "gemini_api_key": "not_required",
    "google_cloud_project": "missing",
    "bigquery_table_id": "missing"
  }
}
```

When the service is not ready, the endpoint returns HTTP 503.

## Request Tracing

Every HTTP response includes an `X-Request-ID` header.

If the client sends an existing `X-Request-ID`, the API preserves it.

If the client does not send one, the API generates a new request ID.

Example:

```text
X-Request-ID: 7f31c1b8-2d5f-4d39-ae1f-24d3b70cfd0e
```

This helps correlate API responses with application logs.

## Logging

Application logging is configured at startup.

The log format includes:

- Timestamp
- Log level
- Logger name
- Request ID
- Message

Example format:

```text
2026-07-04 10:31:22 INFO app.api.routes_incidents [request_id=7f31c1b8] Incident classified
```

Cloud Run captures application logs from stdout, so this format is suitable for both local debugging and cloud inspection.

## Centralized API Errors

Common API errors are centralized in:

```text
app/utils/api_errors.py
```

Currently standardized errors include:

- `incident_not_found`
- `incident_history_unavailable`

This keeps route handlers smaller and makes error responses consistent.

## Readiness Checks

The readiness endpoint validates configuration only.

It does not call Gemini API or BigQuery directly. This keeps the endpoint fast and safe for probes.

Configuration checks include:

| Setting                                 | Required When                       |
| --------------------------------------- | ----------------------------------- |
| `GEMINI_API_KEY`                        | `CLASSIFIER_PROVIDER=gemini`        |
| `GOOGLE_CLOUD_PROJECT`                  | `ENABLE_BIGQUERY_PERSISTENCE=true`  |
| `BIGQUERY_DATASET` and `BIGQUERY_TABLE` | Used to build the BigQuery table ID |

## Local Validation

Run tests:

```bash
pytest
```

Run the API:

```bash
uvicorn app.main:app --reload
```

Check health:

```text
http://127.0.0.1:8000/health
```

Check readiness:

```text
http://127.0.0.1:8000/ready
```

Check request tracing with curl:

```bash
curl -i http://127.0.0.1:8000/health
```

Expected header:

```text
x-request-id: <generated-request-id>
```

Check request tracing with a custom request ID:

```bash
curl -i -H "X-Request-ID: manual-test-123" http://127.0.0.1:8000/health
```

Expected header:

```text
x-request-id: manual-test-123
```

## Cloud Run Notes

Cloud Run captures stdout/stderr and forwards logs to Cloud Logging.

The current logging format is intentionally simple and compatible with local execution and Cloud Run logs.

Later deployment configuration can use:

```text
GET /health
```

as a liveness check and:

```text
GET /ready
```

as a readiness-style validation endpoint for runtime settings.
