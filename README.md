# AI IT Incident Classifier

Classifies IT support incidents with generative AI and stores results on Google Cloud for operational analysis.

## Overview

AI IT Incident Classifier is a cloud-oriented application for automating the initial triage of IT support incidents.

The system receives incident reports through a REST API, validates the input payload, classifies each incident by category, priority and responsible area, and returns a structured response with a technical summary, suggested action, confidence level and manual review flag.

The project demonstrates a practical Cloud, Infrastructure and AI automation use case: using generative AI to reduce repetitive manual triage work, standardize incident classification and prepare operational data for later analysis in Google Cloud.

## Use Case

Support teams often receive incidents that must be manually reviewed before they can be assigned to the correct area.

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
Client / Postman / Frontend
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
BigQuery
        ↓
Operational Analysis
```

## Core Capabilities

- Receives IT support incidents through a REST API.
- Validates request payloads with typed Pydantic schemas.
- Classifies incidents using controlled categories, priorities and responsible areas.
- Supports a deterministic mock classifier for local development and tests.
- Supports Gemini API as the generative AI classifier provider.
- Generates a technical summary and suggested first action.
- Flags ambiguous or low-confidence incidents for human review.
- Generates stable incident identifiers for traceability.
- Exposes health endpoints for local and cloud runtime validation.
- Provides automated tests for API health checks, payload validation and classification contract behavior.

## Classification Contract

The classifier returns a structured response with the following fields:

```json
{
  "incident_id": "INC-20260629-A3F91C2B",
  "category": "VPN",
  "priority": "Media",
  "responsible_area": "Infraestructura",
  "summary": "The incident was classified as VPN based on the provided title and description.",
  "suggested_action": "Validate user credentials, account status, VPN client configuration and VPN service logs.",
  "confidence_level": "Media",
  "needs_human_review": false,
  "model_name": "gemini-3.5-flash-mock",
  "created_at": "2026-06-29T10:30:00Z"
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
POST /incidents/classify
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
  "incident_id": "INC-20260629-A3F91C2B",
  "category": "VPN",
  "priority": "Media",
  "responsible_area": "Infraestructura",
  "summary": "The incident was classified as VPN based on the provided title and description: No puedo conectarme a la VPN.",
  "suggested_action": "Validate user credentials, account status, VPN client configuration and VPN service logs.",
  "confidence_level": "Media",
  "needs_human_review": false,
  "model_name": "gemini-3.5-flash-mock",
  "created_at": "2026-06-29T10:30:00Z"
}
```

See [`docs/api_contract.md`](docs/api_contract.md) for the full request and response contract.

## Classifier Providers

The backend supports two classifier providers:

```text
mock
gemini
```

The provider is selected through:

```env
CLASSIFIER_PROVIDER=mock
```

or:

```env
CLASSIFIER_PROVIDER=gemini
```

### Mock Classifier

The mock classifier uses deterministic local rules.

It is useful for:

- Local development.
- Automated tests.
- Contract validation.
- Running the API without external services.

### Gemini Classifier

The Gemini classifier uses Gemini API to classify IT incidents with generative AI.

The integration uses:

- Controlled catalogs
- Prompt construction
- Structured JSON output
- Pydantic validation
- Fallback handling for invalid model responses

See [`docs/gemini_setup.md`](docs/gemini_setup.md) for Gemini API configuration.

## Environment Variables

The project uses environment-based configuration.

```env
APP_NAME=AI IT Incident Classifier
APP_VERSION=0.1.0
ENVIRONMENT=local

CLASSIFIER_PROVIDER=mock

GOOGLE_CLOUD_PROJECT=your-google-cloud-project-id
BIGQUERY_DATASET=ai_operations
BIGQUERY_TABLE=incident_classifications

GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.5-flash
```

Real secrets such as API keys must be configured locally or as cloud runtime environment variables. They must never be committed to the repository.

## Tech Stack

- Python
- FastAPI
- Pydantic
- Gemini API
- Google Cloud Run
- BigQuery
- Docker
- Postman
- React + Vite

## Repository Structure

```text
app/
  api/          API route modules
  core/         Domain catalogs, validation rules and classification utilities
  services/     Classifier, incident ID and cloud service integrations
  utils/        Shared runtime utilities

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

- Root and health endpoints.
- Incident request payload validation.
- Controlled classification catalogs.
- Incident ID generation.
- Classification output validation and fallback behavior.
- Mock classifier behavior.
- Classification endpoint behavior.

## Current Implementation

The current implementation includes:

- FastAPI application setup.
- Root and health endpoints.
- Environment-based configuration.
- Typed incident request and response schemas.
- Controlled classification catalogs.
- Priority and ownership rules.
- Stable incident ID generation.
- Mock incident classifier.
- Gemini classifier provider configuration.
- Classification output validation.
- `POST /incidents/classify`.
- Automated tests for the current backend behavior.

## Portfolio Scope

This project demonstrates practical skills in:

- Cloud-native API development.
- Generative AI integration.
- IT operations automation.
- Backend validation and structured API contracts.
- Google Cloud deployment foundations.
- Operational data persistence for analysis.
