# Local Docker Execution

This document explains how to build and run the AI IT Incident Classifier backend as a Docker container.

The Docker image is used later as the runtime artifact for Cloud Run.

## Build Image

From the project root:

```bash
docker build -t ai-it-incident-classifier-api:local .
```

## Run With Mock Classifier

This mode does not require Gemini API or BigQuery credentials.

### Bash

```bash
docker run --rm -p 8080:8080 \
  -e ENVIRONMENT=local \
  -e CLASSIFIER_PROVIDER=mock \
  -e ENABLE_BIGQUERY_PERSISTENCE=false \
  -e GEMINI_MODEL=gemini-2.5-flash \
  ai-it-incident-classifier-api:local
```

### PowerShell

```powershell
docker run --rm -p 8080:8080 `
  -e ENVIRONMENT=local `
  -e CLASSIFIER_PROVIDER=mock `
  -e ENABLE_BIGQUERY_PERSISTENCE=false `
  -e GEMINI_MODEL=gemini-2.5-flash `
  ai-it-incident-classifier-api:local
```

## Validate Runtime Endpoints

Open another terminal and run:

```bash
curl -i http://localhost:8080/health
```

Expected response:

```json
{
  "status": "healthy"
}
```

Check readiness:

```bash
curl -i http://localhost:8080/ready
```

Expected behavior:

- HTTP 200 when runtime configuration is valid.
- HTTP 503 when required settings are missing.

## Validate Classification Endpoint

### Bash

```bash
curl -X POST http://localhost:8080/incidents/classify \
  -H "Content-Type: application/json" \
  -d '{
    "title": "No puedo conectarme a la VPN",
    "description": "Desde ayer intento conectarme a la VPN de la empresa, pero aparece error de autenticación.",
    "reported_by": "usuario.demo@empresa.com",
    "source_channel": "api"
  }'
```

### PowerShell

```powershell
$body = @{
  title = "No puedo conectarme a la VPN"
  description = "Desde ayer intento conectarme a la VPN de la empresa, pero aparece error de autenticación."
  reported_by = "usuario.demo@empresa.com"
  source_channel = "api"
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:8080/incidents/classify" `
  -ContentType "application/json" `
  -Body $body
```

## Run With Gemini

Gemini mode requires a valid API key.

```bash
docker run --rm -p 8080:8080 \
  -e ENVIRONMENT=local \
  -e CLASSIFIER_PROVIDER=gemini \
  -e ENABLE_BIGQUERY_PERSISTENCE=false \
  -e GEMINI_API_KEY=your_api_key_here \
  -e GEMINI_MODEL=gemini-2.5-flash \
  ai-it-incident-classifier-api:local
```

## Run With BigQuery Persistence

When BigQuery persistence is enabled inside Docker, the container must have access to Google Cloud credentials.

For simple local validation, prefer testing BigQuery persistence outside Docker first using:

```bash
gcloud auth application-default login
```

Then run the API locally with Uvicorn.

Cloud Run will use its service account instead of local credentials.
