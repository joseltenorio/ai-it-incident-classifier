# AI IT Incident Classifier

Classifies IT support incidents with generative AI and stores results on Google Cloud for operational analysis.

## Overview

AI IT Incident Classifier is a cloud-oriented application that automates the initial triage of IT support incidents.

The system receives incident reports through a REST API, validates the input payload, classifies each incident by category, priority and responsible area, and returns a structured response with a technical summary, suggested action, confidence level and manual review flag.

The project is designed as a practical Cloud, Infrastructure and AI automation use case. It demonstrates how generative AI can support IT operations by reducing repetitive manual triage work, standardizing ticket classification and preparing incident data for later operational analysis in Google Cloud.

## Use Case

In many support teams, incoming incidents must be manually reviewed before they can be assigned to the right area.

Examples include:

```text
- I cannot connect to the corporate VPN.
- My account is locked.
- The application returns a 500 error.
- The database is responding slowly.
- A user reported suspicious login activity.
```

This application automates that first analysis step by producing a structured incident classification that can be reviewed, stored and analyzed.

## Architecture

```text
Client / Postman / Frontend
        ↓
FastAPI Backend
        ↓
Incident Payload Validation
        ↓
Generative AI Classifier
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
- Generates a technical summary and suggested first action.
- Flags ambiguous or low-confidence incidents for human review.
- Generates stable incident identifiers for traceability.
- Stores classification-ready records for operational analysis in Google Cloud.
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
  "model_name": "gemini-1.5-flash-mock",
  "created_at": "2026-06-29T10:30:00Z"
}
```

The current implementation uses a deterministic mock classifier to validate the API contract before integrating Gemini API. The mock classifier will later be replaced by the generative AI classifier while preserving the same public response structure.

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

### `GET /health`

Returns the runtime health status of the API.

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
  "model_name": "gemini-1.5-flash-mock",
  "created_at": "2026-06-29T10:30:00Z"
}
```

See [`docs/api_contract.md`](docs/api_contract.md) for the full request and response contract.

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
  services/     Classifier, incident ID and future cloud service integrations
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

Copy the environment template:

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

## Environment Variables

The project uses environment-based configuration.

```env
APP_NAME=AI IT Incident Classifier
APP_VERSION=0.1.0
ENVIRONMENT=local

GOOGLE_CLOUD_PROJECT=
BIGQUERY_DATASET=ai_operations
BIGQUERY_TABLE=incident_classifications

GEMINI_API_KEY=
GEMINI_MODEL=gemini-1.5-flash
```

Real secrets such as API keys must be configured locally or as Cloud Run environment variables. They should never be committed to the repository.

## Testing

Run the automated test suite:

```bash
python -m pytest
```

The current tests cover:

- Root and health endpoints.
- Incident request payload validation.
- Controlled classification catalogs.
- Incident ID generation.
- Classification output validation and fallback behavior.
- Mock classifier behavior.

## Current Status

The project currently includes the backend foundation and the incident classification contract.

Implemented:

- FastAPI application setup.
- Root and health endpoints.
- Environment-based configuration.
- Typed incident request and response schemas.
- Controlled classification catalogs.
- Priority and ownership rules.
- Stable incident ID generation.
- Mock incident classifier.
- Classification output validation.
- `POST /incidents/classify`.
- Automated tests for the current backend behavior.

Planned next steps:

- Integrate Gemini API as the real generative AI classifier.
- Store classification results in BigQuery.
- Add incident history query endpoints.
- Add Docker support and deploy the backend to Cloud Run.
- Add a lightweight React frontend demo.
- Add a Postman validation suite.
- Finalize portfolio documentation and screenshots.

## Portfolio Scope

This project is intended to demonstrate practical skills in:

- Cloud-native API development.
- Generative AI integration.
- IT operations automation.
- Backend validation and structured API contracts.
- Google Cloud deployment foundations.
- Operational data persistence for later analysis.
