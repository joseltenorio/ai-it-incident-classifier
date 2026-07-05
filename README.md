# AI IT Incident Classifier

Classifies IT support incidents with generative AI and stores results on Google Cloud for operational analysis.

## Overview

AI IT Incident Classifier is a cloud-oriented application for automating the initial triage of IT support incidents.

The system receives incident reports through a REST API, validates the input payload, classifies each incident by category, priority and responsible area, and returns a structured response with a technical summary, suggested action, confidence level and manual review flag.

The project demonstrates a practical Cloud, Infrastructure and AI automation use case: using generative AI to reduce repetitive manual triage work, standardize incident classification and prepare operational data for later analysis in Google Cloud.

## Use Case

Support teams often receive incidents that must be manually reviewed before they can be assigned to the correct technical area.

Examples:

```text
- I cannot connect to the corporate VPN.
- My account is locked.
- The application returns a 500 error.
- The database is responding slowly.
- A user reported suspicious login activity.
```

This application automates the first analysis step by producing a structured incident classification that can be reviewed, stored and analyzed.

## Architecture

```text
Client / Postman / Future Frontend
        ↓
Cloud Run
        ↓
FastAPI Backend
        ↓
Incident Payload Validation
        ↓
Classifier Provider
        ├── Mock Classifier
        └── Gemini API
        ↓
Structured Response Validation
        ↓
BigQuery Persistence
        ↓
Incident History API
```

BigQuery persistence is available as an optional storage layer. When `ENABLE_BIGQUERY_PERSISTENCE=true`, classified incidents are stored in BigQuery for traceability and operational analysis.

## Cloud Architecture

```text
Developer Workstation
        ↓
Cloud Build
        ↓
Artifact Registry
        ↓
Cloud Run Service
        ↓
BigQuery
        ↓
Cloud Logging
```

The Cloud Run deployment uses:

- Docker container image.
- Artifact Registry repository.
- Cloud Build image build.
- Runtime service account.
- BigQuery dataset and table.
- Secret Manager for Gemini API key access.
- Environment variables for provider selection and persistence settings.

## Core Capabilities

- Receives IT support incidents through a REST API.
- Validates request payloads with typed Pydantic schemas.
- Classifies incidents using controlled categories, priorities and responsible areas.
- Supports a deterministic mock classifier for local development, automated tests and quota-safe cloud validation.
- Supports Gemini API as the generative AI classifier provider.
- Builds controlled prompts using classification catalogs and triage rules.
- Validates structured classifier outputs before returning API responses.
- Generates a technical summary and suggested first action.
- Flags ambiguous or low-confidence incidents for human review.
- Generates stable incident identifiers for traceability.
- Persists classification records in BigQuery.
- Provides BigQuery-backed incident history and detail lookup endpoints.
- Adds request tracing with `X-Request-ID` response headers.
- Exposes health and readiness endpoints for local and cloud runtime validation.
- Includes a Postman Cloud Validation Suite for deployed API testing.

## Classification Contract

The classifier returns a structured response with the following fields:

```json
{
  "incident_id": "INC-20260705-D0E67AF9",
  "category": "Accesos",
  "priority": "Media",
  "responsible_area": "Aplicaciones",
  "summary": "The user cannot access the administrative panel because a 403 forbidden error appears after login.",
  "suggested_action": "Review user permissions, assigned roles and recent authorization changes in the application.",
  "confidence_level": "Alta",
  "needs_human_review": false,
  "model_name": "gemini-2.5-flash-lite-gemini",
  "created_at": "2026-07-05T15:05:21Z"
}
```

The response structure remains stable regardless of whether the backend uses the mock classifier or Gemini API.

## Controlled Values

### Categories

```text
VPN
Redes
Accesos
Correo
Hardware
Sistema Operativo
Base de Datos
Aplicaciones
Seguridad
Cloud
Otro
```

### Priorities

```text
Baja
Media
Alta
Crítica
```

### Responsible Areas

```text
Soporte TI
Infraestructura
Seguridad
Base de Datos
Aplicaciones
Cloud
```

### Confidence Levels

```text
Baja
Media
Alta
```

The `confidence_level` field is qualitative. It is not intended to represent a statistical probability.

## API Endpoints

```text
GET  /
GET  /health
GET  /ready
POST /incidents/classify
GET  /incidents
GET  /incidents/{incident_id}
```

### `GET /`

Returns basic service metadata.

Example response:

```json
{
  "service": "AI IT Incident Classifier",
  "status": "running",
  "version": "0.1.0"
}
```

### `GET /health`

Returns the runtime health status of the API.

Example response:

```json
{
  "status": "healthy"
}
```

### `GET /ready`

Returns runtime readiness based on configuration checks.

Example response:

```json
{
  "status": "ready",
  "environment": "cloud",
  "classifier_provider": "mock",
  "bigquery_persistence_enabled": true,
  "checks": {
    "gemini_api_key": "not_required",
    "google_cloud_project": "configured",
    "bigquery_table_id": "configured"
  }
}
```

`GET /health` verifies that the API process is alive.

`GET /ready` verifies whether required runtime settings are present for the selected classifier provider and BigQuery persistence mode.

### `POST /incidents/classify`

Classifies an IT support incident.

Example request:

```json
{
  "title": "No puedo conectarme a la VPN",
  "description": "Desde ayer intento conectarme a la VPN de la empresa, pero aparece error de autenticación.",
  "reported_by": "usuario.demo@empresa.com",
  "source_channel": "postman"
}
```

Example response:

```json
{
  "incident_id": "INC-20260704-E0DEA5EB",
  "category": "VPN",
  "priority": "Media",
  "responsible_area": "Infraestructura",
  "summary": "The incident was classified as VPN based on the provided title and description: No puedo conectarme a la VPN.",
  "suggested_action": "Validate user credentials, account status, VPN client configuration and VPN service logs.",
  "confidence_level": "Media",
  "needs_human_review": false,
  "model_name": "gemini-2.5-flash-mock",
  "created_at": "2026-07-04T23:44:43Z"
}
```

See [`docs/api_contract.md`](docs/api_contract.md) for the full request and response contract.

## Classifier Providers

The backend supports two classifier providers:

```text
mock
gemini
```

The selected provider is controlled by the `CLASSIFIER_PROVIDER` environment variable.

### `mock`

The mock provider uses deterministic local rules.

It is used for:

- Automated tests.
- Local contract validation.
- Development without external API calls.
- Running cloud validation without consuming Gemini quota.
- API smoke testing after deployment.

### `gemini`

The Gemini provider uses Gemini API to classify IT incidents with generative AI.

The Gemini integration is responsible for:

- Building a controlled prompt from the incident payload.
- Sending the classification request to Gemini API.
- Requesting a structured JSON response.
- Validating the response with Pydantic.
- Returning a stable API response.
- Falling back to manual review when the model output is invalid or unavailable.

The response structure remains the same whether the backend uses the deterministic mock provider or the Gemini provider.

## Gemini Output Validation

Gemini responses are validated against the same controlled classification contract used by the rest of the API.

The model must return only supported values for:

- Category.
- Priority.
- Responsible area.
- Confidence level.

If the model response is invalid, incomplete or unavailable, the backend returns a safe fallback classification marked for human review.

See [`docs/gemini_setup.md`](docs/gemini_setup.md) for Gemini API configuration.

See [`docs/gemini_classifier.md`](docs/gemini_classifier.md) for the Gemini classifier technical design.

## BigQuery Persistence

The API can store classified incidents in BigQuery for traceability and operational analysis.

Persistence is controlled through:

```env
ENABLE_BIGQUERY_PERSISTENCE=true
```

When enabled, the backend stores each classification in:

```text
ai_operations.incident_classifications
```

Stored records include the original incident, classification output, model metadata, raw model response and creation timestamp.

The SQL setup scripts are available in:

```text
sql/create_bigquery_dataset.sql
sql/create_incident_classifications_table.sql
```

See [`docs/bigquery_persistence.md`](docs/bigquery_persistence.md) for the full setup guide.

## Incident History API

The backend can query classified incidents stored in BigQuery.

Available endpoints:

```text
GET /incidents
GET /incidents/{incident_id}
```

`GET /incidents` returns recent classified incidents with compact fields for operational review.

`GET /incidents/{incident_id}` returns a full incident detail response, excluding `raw_model_response`, which remains stored in BigQuery for audit and troubleshooting.

These endpoints require the BigQuery table configured through:

```env
GOOGLE_CLOUD_PROJECT=your-google-cloud-project-id
BIGQUERY_DATASET=ai_operations
BIGQUERY_TABLE=incident_classifications
```

See [`docs/api_contract.md`](docs/api_contract.md) for request and response examples.

## Runtime Observability

The backend includes basic runtime hardening for local and cloud execution:

- Structured application logging.
- Request tracing middleware.
- `X-Request-ID` response headers.
- Centralized API error helpers.
- Health endpoint: `GET /health`.
- Readiness endpoint: `GET /ready`.

Every HTTP response includes an `X-Request-ID` header.

If the client sends an existing `X-Request-ID`, the API preserves it. If the client does not send one, the API generates a new request ID.

Example header:

```text
X-Request-ID: 7f31c1b8-2d5f-4d39-ae1f-24d3b70cfd0e
```

The API logs request completion with the current request ID, making it easier to correlate responses with local logs or Cloud Logging entries.

See [`docs/runtime_observability.md`](docs/runtime_observability.md) for more details.

## Docker

The backend can run as a Docker container.

Build the image:

```bash
docker build -t ai-it-incident-classifier-api:local .
```

Run with the mock classifier:

```bash
docker run --rm -p 8080:8080 \
  -e ENVIRONMENT=local \
  -e CLASSIFIER_PROVIDER=mock \
  -e ENABLE_BIGQUERY_PERSISTENCE=false \
  -e GEMINI_MODEL=gemini-2.5-flash \
  ai-it-incident-classifier-api:local
```

See [`docs/docker_local.md`](docs/docker_local.md) for local Docker execution details.

## Cloud Run Deployment

The backend is designed to run on Cloud Run as a containerized FastAPI service.

Deployment uses:

- Docker.
- Cloud Build.
- Artifact Registry.
- Cloud Run.
- BigQuery.
- Secret Manager.
- Runtime environment variables.
- Runtime service account.

The deployed service was validated with:

```text
GET  /health
GET  /ready
POST /incidents/classify
GET  /incidents
GET  /incidents/{incident_id}
```

See [`docs/cloud_run_deployment.md`](docs/cloud_run_deployment.md) for deployment instructions.

## Runtime Environment

Runtime behavior is controlled through environment variables.

Important variables include:

- `CLASSIFIER_PROVIDER`
- `ENABLE_BIGQUERY_PERSISTENCE`
- `GOOGLE_CLOUD_PROJECT`
- `BIGQUERY_DATASET`
- `BIGQUERY_TABLE`
- `GEMINI_MODEL`
- `GEMINI_API_KEY`

See [`docs/runtime_environment.md`](docs/runtime_environment.md) for the full environment variable reference.

## Cloud IAM and Validation

Cloud Run requires a runtime service account with permissions to insert and query BigQuery records.

Recommended roles for this project:

- `roles/bigquery.jobUser`
- `roles/bigquery.dataEditor`

Gemini API access is managed through Secret Manager when running in cloud mode.

See [`docs/cloud_iam_and_validation.md`](docs/cloud_iam_and_validation.md) for IAM setup and deployment validation checks.

## Postman Cloud Validation

The project includes a Postman validation suite for the deployed Cloud Run API.

Files:

```text
postman/ai_it_incident_classifier_cloud_validation.postman_collection.json
postman/ai_it_incident_classifier_cloud_validation.postman_environment.json
docs/postman_cloud_validation_suite.md
```

The collection validates:

- Runtime endpoints.
- Request tracing headers.
- Valid incident classification cases.
- Payload validation errors.
- Incident history retrieval.
- Incident detail lookup.
- Unknown incident handling.

The collection can run by itself using collection variables. The environment file is optional and can be imported when a separate Postman environment is preferred.

Recommended execution order:

```text
01 Runtime
02 Classification - Valid Cases
04 Incident History
03 Classification - Validation Errors
05 Cloud Evidence
```

Run the suite with Cloud Run in `mock` mode for normal validation to avoid consuming Gemini quota.

See [`docs/postman_cloud_validation_suite.md`](docs/postman_cloud_validation_suite.md) for the full validation guide.

## Environment Variables

The project uses environment-based configuration.

```env
APP_NAME="AI IT Incident Classifier"
APP_VERSION=0.1.0
ENVIRONMENT=local

CLASSIFIER_PROVIDER=mock
ENABLE_BIGQUERY_PERSISTENCE=false

GOOGLE_CLOUD_PROJECT=your-google-cloud-project-id
BIGQUERY_DATASET=ai_operations
BIGQUERY_TABLE=incident_classifications

GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
```

Real secrets such as API keys must be configured locally or as cloud runtime secrets. They must never be committed to the repository.

## Tech Stack

- Python.
- FastAPI.
- Pydantic.
- Gemini API.
- Google Cloud Run.
- Cloud Build.
- Artifact Registry.
- Secret Manager.
- BigQuery.
- Docker.
- Postman.
- React + Vite.

## Repository Structure

```text
app/
  api/          API route modules
  core/         Domain catalogs, validation rules and runtime checks
  services/     Classifier, incident ID and cloud service integrations
  utils/        Shared runtime utilities
  middleware.py Request tracing middleware

tests/          Automated test suite
docs/           Technical documentation
postman/        API validation collections
sql/            BigQuery dataset and table definitions
```

## Local Development

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Create a local environment file from the template:

```powershell
Copy-Item .env.example .env
```

Run the API locally:

```bash
uvicorn app.main:app --reload
```

Open the API documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

## Testing

Run the automated test suite:

```bash
python -m pytest
```

The test suite covers:

- Root, health and readiness endpoints.
- Incident request payload validation.
- Controlled classification catalogs.
- Incident ID generation.
- Classification output validation and fallback behavior.
- Mock classifier behavior.
- Prompt construction for Gemini.
- Classifier provider selection.
- Classification endpoint behavior.
- BigQuery record mapping and incident history responses.
- Request tracing and readiness behavior.

## Current Implementation

The current implementation includes:

- FastAPI application setup.
- Root, health and readiness endpoints.
- Environment-based configuration.
- Typed incident request and response schemas.
- Controlled classification catalogs.
- Priority and ownership rules.
- Stable incident ID generation.
- Mock incident classifier.
- Gemini classifier provider configuration.
- Prompt builder for Gemini classification.
- Classification output validation.
- Fallback handling for invalid classifier responses.
- `POST /incidents/classify`.
- `GET /incidents`.
- `GET /incidents/{incident_id}`.
- BigQuery-backed incident persistence and history queries.
- Structured application logging.
- Request tracing middleware with `X-Request-ID` response headers.
- Centralized API error helpers.
- Runtime readiness checks.
- Docker image build support.
- Cloud Run deployment.
- Gemini API key access through Secret Manager.
- Postman Cloud Validation Suite.
- Automated tests for the current backend behavior.

## Portfolio Scope

This project demonstrates practical skills in:

- Cloud-native API development.
- Generative AI integration.
- IT operations automation.
- Backend validation and structured API contracts.
- Google Cloud deployment.
- Containerized serverless APIs.
- Operational data persistence for analysis.
- API validation with Postman.
