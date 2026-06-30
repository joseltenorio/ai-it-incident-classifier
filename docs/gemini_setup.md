# Gemini API Setup

This document describes the Gemini API configuration used by the AI IT Incident Classifier.

The application supports two classifier providers:

```text
mock
gemini
```

The provider is selected through the `CLASSIFIER_PROVIDER` environment variable.

## Classifier Providers

### `mock`

The `mock` provider uses deterministic local classification rules.

It is intended for:

- Local development without external API calls.
- Automated tests.
- API contract validation.
- Running the backend without secrets.

### `gemini`

The `gemini` provider uses Gemini API to classify IT support incidents with generative AI.

It is intended for:

- Real incident classification.
- Local validation with a Gemini API key.
- Cloud runtime environments such as Cloud Run.

## Environment Variables

The Gemini integration uses the following environment variables:

```env
CLASSIFIER_PROVIDER=gemini
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-3.5-flash
```

## Required Variables

| Variable              |          Required | Description                                                                               |
| --------------------- | ----------------: | ----------------------------------------------------------------------------------------- |
| `CLASSIFIER_PROVIDER` |               Yes | Selects the classifier provider. Supported values: `mock`, `gemini`.                      |
| `GEMINI_API_KEY`      | Only for `gemini` | API key used to authenticate requests to Gemini API.                                      |
| `GEMINI_MODEL`        |                No | Gemini model used by the classifier. Defaults to the value configured in `app/config.py`. |

## Local Environment Example

```env
APP_NAME=AI IT Incident Classifier
APP_VERSION=0.1.0
ENVIRONMENT=local

CLASSIFIER_PROVIDER=gemini

GOOGLE_CLOUD_PROJECT=ai-it-incident-classifier
BIGQUERY_DATASET=ai_operations
BIGQUERY_TABLE=incident_classifications

GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-3.5-flash
```

## Security Requirements

Real API keys must never be committed to the repository.

The following files and locations must not contain real secrets:

- `README.md`
- `docs/`
- Pull request descriptions
- Public screenshots
- GitHub issues
- Source code files

The Gemini API key belongs only in:

- Local `.env` files.
- Cloud Run environment variables.
- Secret management systems, if added later.

## Runtime Behavior

When `CLASSIFIER_PROVIDER=mock`, the backend uses deterministic local rules.

When `CLASSIFIER_PROVIDER=gemini`, the backend uses Gemini API and validates the model output against the same incident classification contract used by the rest of the application.

The API response contract remains stable regardless of the selected provider.

## Classification Contract

The Gemini classifier must return a structured classification with the following fields:

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

The backend validates this output using controlled values for:

- Incident category
- Priority
- Responsible area
- Confidence level
- Manual review flag

Invalid or incomplete model responses are converted into a safe fallback classification that requires human review.

## Default Model

The default Gemini model for this project is:

```text
gemini-3.5-flash
```

This model is configured through `GEMINI_MODEL` and can be changed without modifying the classifier logic.
