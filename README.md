# AI IT Incident Classifier

Classifies IT support incidents with generative AI and stores results on Google Cloud for operational analysis.

## Overview

AI IT Incident Classifier is a cloud-based application for automating the initial triage of IT support incidents.

The system receives incident reports, analyzes their technical context with generative AI, and returns a structured classification with category, priority, responsible area, summary and suggested action. Classification results are designed to be stored in Google Cloud for traceability and operational analysis.

This project focuses on a practical Cloud, Infrastructure and AI automation use case: helping support teams reduce manual triage work and standardize incident classification.

## Architecture

```text
Client / Postman / Frontend
        ↓
FastAPI Backend
        ↓
Generative AI Classifier
        ↓
Response Validation
        ↓
BigQuery
        ↓
Operational Analysis
```

## Core Capabilities

- Receive IT support incidents through a REST API.
- Validate incident payloads with typed request schemas.
- Classify incidents by category, priority and responsible area.
- Generate a technical summary and suggested action.
- Store classification results for traceability and later analysis.
- Expose health endpoints for local and cloud runtime validation.

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
  api/
  core/
  services/
  utils/
tests/
docs/
postman/
sql/
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

Copy the example environment file before running the project locally:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Real secrets such as API keys must be configured locally or as Cloud Run environment variables. They should never be committed to the repository.

## Project Scope

The backend foundation includes:

- FastAPI application setup.
- Root and health endpoints.
- Environment-based configuration.
- Typed incident request and response schemas.
- Basic automated tests.

Additional modules extend this foundation with AI classification, BigQuery persistence, Cloud Run deployment, Postman validation and a lightweight frontend demo.
