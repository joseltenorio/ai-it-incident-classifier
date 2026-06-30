# Gemini Classifier Integration

This document describes how the AI IT Incident Classifier uses Gemini API as the generative AI provider for IT incident triage.

## Purpose

The Gemini classifier analyzes IT support incidents written in natural language and converts them into a controlled structured classification.

The classifier produces:

- Incident category
- Priority
- Responsible support area
- Technical summary
- Suggested first action
- Qualitative confidence level
- Manual review flag

The integration is designed to support operational triage, not to replace human support teams. Ambiguous, risky or low-confidence incidents are flagged for manual review.

## Classification Flow

```text
IncidentRequest
      ↓
Prompt Builder
      ↓
Gemini API
      ↓
Structured JSON Response
      ↓
Pydantic Validation
      ↓
IncidentClassification
      ↓
API Response
```

The API endpoint remains stable regardless of the classifier provider:

```text
POST /incidents/classify
```

## Provider-Based Design

The backend supports two classifier providers:

```text
mock
gemini
```

The provider is selected through the `CLASSIFIER_PROVIDER` environment variable.

### Mock Provider

The mock provider uses deterministic local rules.

It is used for:

- Automated tests
- Local development without external API calls
- API contract validation
- Running the backend without secrets

The mock classifier is intentionally simple. Its purpose is to keep the application testable and predictable before or without using Gemini.

### Gemini Provider

The Gemini provider uses Gemini API to classify incidents with generative AI.

It is used for:

- Real AI-powered incident classification
- Local validation with a Gemini API key
- Cloud runtime environments such as Cloud Run

The Gemini provider preserves the same public API response contract used by the mock provider.

## Prompt Strategy

The prompt builder prepares a controlled instruction for Gemini.

The prompt includes:

- Incident title
- Incident description
- Allowed categories
- Allowed priorities
- Allowed responsible areas
- Allowed confidence levels
- Priority rules
- Responsible area hints
- Strict JSON response instructions

The model is instructed to use only controlled values and to avoid inventing new categories, priorities, responsible areas or confidence levels.

## Controlled Output

Gemini must return a JSON object compatible with the `IncidentClassification` schema.

Expected structure:

```json
{
  "category": "VPN",
  "priority": "Media",
  "responsible_area": "Infraestructura",
  "summary": "The user cannot connect to the corporate VPN due to an authentication issue.",
  "suggested_action": "Validate user credentials, account status, VPN client configuration and VPN service logs.",
  "confidence_level": "Alta",
  "needs_human_review": false
}
```

The API validates the model output before returning it to the client.

## Controlled Categories

The classifier must return one of the following categories:

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

## Controlled Priorities

The classifier must return one of the following priorities:

```text
Baja
Media
Alta
Crítica
```

## Responsible Areas

The classifier must return one of the following responsible areas:

```text
Soporte TI
Infraestructura
Seguridad
Base de Datos
Aplicaciones
Cloud
```

## Confidence Levels

The classifier must return one of the following confidence levels:

```text
Baja
Media
Alta
```

The `confidence_level` field is qualitative. It is not a statistical probability.

## Validation Layer

The backend validates Gemini responses using the same Pydantic schema used by the rest of the API.

The validation layer checks that:

- Required fields are present.
- Values belong to controlled catalogs.
- Text fields satisfy the expected shape.
- The response can be safely converted into an `IncidentClassification`.

This prevents uncontrolled model output from leaking into the API response.

## Fallback Behavior

If Gemini fails, returns an empty response or produces invalid structured output, the backend returns a safe fallback classification.

Fallback response:

```json
{
  "category": "Otro",
  "priority": "Media",
  "responsible_area": "Soporte TI",
  "summary": "The incident requires manual review because it could not be classified automatically.",
  "suggested_action": "Review the ticket details manually and assign it to the appropriate support area.",
  "confidence_level": "Baja",
  "needs_human_review": true
}
```

This behavior keeps the API predictable and ensures that uncertain classifications are escalated for human review.

## Runtime Metadata

The Gemini classifier returns additional runtime metadata internally:

```text
raw_model_response
model_latency_ms
```

These fields are useful for traceability and will be stored later when BigQuery persistence is added.

The public API currently returns:

```text
model_name
created_at
```

## Current Scope

The current integration focuses on:

- Prompt construction
- Gemini API execution
- Structured response validation
- Provider selection
- Fallback handling
- API contract preservation

BigQuery persistence, incident history queries and Cloud Run deployment are handled in later project blocks.
