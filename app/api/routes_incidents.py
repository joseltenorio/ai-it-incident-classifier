# app/api/routes_incidents.py

import logging
from datetime import UTC, datetime

from fastapi import APIRouter, status

from app.config import settings
from app.schemas import IncidentRequest, IncidentResponse
from app.services.bigquery_repository import (
    BigQueryPersistenceError,
    insert_incident_classification,
)
from app.services.incident_classifier import classify_incident
from app.services.incident_id_generator import generate_incident_id
from app.services.incident_record_mapper import build_incident_record

logger = logging.getLogger(__name__)

# Incident routes contain the core business endpoints of the API.
# The classifier provider is selected through configuration so local tests can
# use the mock classifier while deployed environments can use Gemini.
router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.post(
    "/classify",
    response_model=IncidentResponse,
    status_code=status.HTTP_200_OK,
    summary="Classify an IT support incident",
)
def classify_incident_endpoint(request: IncidentRequest) -> IncidentResponse:
    """Classify an IT incident and optionally persist it in BigQuery.

    The public response contract remains stable regardless of whether the
    backend uses the local mock classifier or Gemini API. BigQuery persistence
    is controlled through ENABLE_BIGQUERY_PERSISTENCE.
    """

    created_at = datetime.now(UTC)
    classification, raw_output, latency_ms = classify_incident(request)

    model_suffix = "gemini" if settings.use_gemini_classifier else "mock"
    model_name = f"{settings.gemini_model}-{model_suffix}"
    incident_id = generate_incident_id(created_at)

    if settings.enable_bigquery_persistence:
        record = build_incident_record(
            request=request,
            classification=classification,
            incident_id=incident_id,
            model_name=model_name,
            model_latency_ms=latency_ms,
            raw_model_response=raw_output,
            created_at=created_at,
        )

        try:
            insert_incident_classification(record)
        except BigQueryPersistenceError as exc:
            logger.warning(
                "Incident classification was returned but not persisted: %s",
                exc,
            )

    return IncidentResponse(
        incident_id=incident_id,
        model_name=model_name,
        created_at=created_at,
        **classification.model_dump(),
    )