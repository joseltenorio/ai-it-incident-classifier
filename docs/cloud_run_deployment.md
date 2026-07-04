# Cloud Run Deployment

This document explains how to deploy the AI IT Incident Classifier backend to Google Cloud Run.

Cloud Run runs the backend as a containerized service. The container must listen on `0.0.0.0` and the port provided by the `PORT` environment variable.

The Dockerfile follows this requirement by running Uvicorn with:

```text
--host 0.0.0.0 --port ${PORT}
```

## Required Google Cloud Services

Enable the required APIs:

```bash
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable bigquery.googleapis.com
```

## Variables

### Bash

```bash
export GCP_PROJECT_ID="your-google-cloud-project-id"
export REGION="us-central1"
export ARTIFACT_REPOSITORY="ai-it-incident-classifier"
export SERVICE_NAME="ai-it-incident-classifier-api"
export IMAGE_NAME="ai-it-incident-classifier-api"
```

### PowerShell

```powershell
$env:GCP_PROJECT_ID="your-google-cloud-project-id"
$env:REGION="us-central1"
$env:ARTIFACT_REPOSITORY="ai-it-incident-classifier"
$env:SERVICE_NAME="ai-it-incident-classifier-api"
$env:IMAGE_NAME="ai-it-incident-classifier-api"
```

Set the active project.

### Bash

```bash
gcloud config set project $GCP_PROJECT_ID
```

### PowerShell

```powershell
gcloud config set project $env:GCP_PROJECT_ID
```

## Create Artifact Registry Repository

### Bash

```bash
gcloud artifacts repositories create $ARTIFACT_REPOSITORY \
  --repository-format=docker \
  --location=$REGION \
  --description="Docker images for AI IT Incident Classifier"
```

### PowerShell

```powershell
gcloud artifacts repositories create $env:ARTIFACT_REPOSITORY `
  --repository-format=docker `
  --location=$env:REGION `
  --description="Docker images for AI IT Incident Classifier"
```

## Build and Push Image With Cloud Build

### Bash

```bash
gcloud builds submit \
  --tag $REGION-docker.pkg.dev/$GCP_PROJECT_ID/$ARTIFACT_REPOSITORY/$IMAGE_NAME:latest
```

### PowerShell

```powershell
gcloud builds submit `
  --tag "$env:REGION-docker.pkg.dev/$env:GCP_PROJECT_ID/$env:ARTIFACT_REPOSITORY/$env:IMAGE_NAME`:latest"
```

## Deploy With Mock Classifier

This mode is useful for validating Cloud Run without external Gemini API calls.

### Bash

```bash
gcloud run deploy $SERVICE_NAME \
  --image $REGION-docker.pkg.dev/$GCP_PROJECT_ID/$ARTIFACT_REPOSITORY/$IMAGE_NAME:latest \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars ENVIRONMENT=cloud,CLASSIFIER_PROVIDER=mock,ENABLE_BIGQUERY_PERSISTENCE=true,GOOGLE_CLOUD_PROJECT=$GCP_PROJECT_ID,BIGQUERY_DATASET=ai_operations,BIGQUERY_TABLE=incident_classifications,GEMINI_MODEL=gemini-2.5-flash
```

### PowerShell

```powershell
gcloud run deploy $env:SERVICE_NAME `
  --image "$env:REGION-docker.pkg.dev/$env:GCP_PROJECT_ID/$env:ARTIFACT_REPOSITORY/$env:IMAGE_NAME`:latest" `
  --region $env:REGION `
  --platform managed `
  --allow-unauthenticated `
  --set-env-vars "ENVIRONMENT=cloud,CLASSIFIER_PROVIDER=mock,ENABLE_BIGQUERY_PERSISTENCE=true,GOOGLE_CLOUD_PROJECT=$env:GCP_PROJECT_ID,BIGQUERY_DATASET=ai_operations,BIGQUERY_TABLE=incident_classifications,GEMINI_MODEL=gemini-2.5-flash"
```

## Deploy With Gemini Classifier

Gemini mode requires `GEMINI_API_KEY`.

For portfolio validation, you can set it as an environment variable first:

```bash
export GEMINI_API_KEY="your-api-key"
```

Then deploy.

### Bash

```bash
gcloud run deploy $SERVICE_NAME \
  --image $REGION-docker.pkg.dev/$GCP_PROJECT_ID/$ARTIFACT_REPOSITORY/$IMAGE_NAME:latest \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars ENVIRONMENT=cloud,CLASSIFIER_PROVIDER=gemini,ENABLE_BIGQUERY_PERSISTENCE=true,GOOGLE_CLOUD_PROJECT=$GCP_PROJECT_ID,BIGQUERY_DATASET=ai_operations,BIGQUERY_TABLE=incident_classifications,GEMINI_MODEL=gemini-2.5-flash,GEMINI_API_KEY=$GEMINI_API_KEY
```

For a more secure production setup, use Secret Manager instead of passing secrets directly as environment variables.

## Validate Deployment

Get the Cloud Run service URL.

### Bash

```bash
gcloud run services describe $SERVICE_NAME \
  --region $REGION \
  --format="value(status.url)"
```

### PowerShell

```powershell
gcloud run services describe $env:SERVICE_NAME `
  --region $env:REGION `
  --format="value(status.url)"
```

Test runtime endpoints:

```bash
curl -i $SERVICE_URL/health
curl -i $SERVICE_URL/ready
```

Test classification:

```bash
curl -X POST $SERVICE_URL/incidents/classify \
  -H "Content-Type: application/json" \
  -d '{
    "title": "No puedo conectarme a la VPN",
    "description": "Desde ayer intento conectarme a la VPN de la empresa, pero aparece error de autenticación.",
    "reported_by": "usuario.demo@empresa.com",
    "source_channel": "api"
  }'
```

Query incident history:

```bash
curl -i $SERVICE_URL/incidents
```

## BigQuery Validation

Run this query in BigQuery:

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

## Expected Result

After deployment, the service should support:

```text
GET  /
GET  /health
GET  /ready
POST /incidents/classify
GET  /incidents
GET  /incidents/{incident_id}
```
