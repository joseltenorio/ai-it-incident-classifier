# app/api/routes_incidents.py

import logging
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Query, status

from app.config import settings
from app.schemas import (
    ErrorResponse,
    IncidentDetailResponse,
    IncidentHistoryItem,
    IncidentRequest,
    IncidentResponse,
)
from app.services.bigquery_repository import (
    BigQueryPersistenceError,
    BigQueryRepositoryError,
    get_incident_classification_by_id,
    insert_incident_classification,
    list_recent_incident_classifications,
)
from app.services.incident_classifier import classify_incident
from app.services.incident_history_mapper import (
    build_incident_detail_response,
    build_incident_history_item,
)
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


@router.get(
    "",
    response_model=list[IncidentHistoryItem],
    status_code=status.HTTP_200_OK,
    summary="List recent classified incidents",
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse},
    },
)
def list_incidents_endpoint(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of recent incidents to return.",
    ),
) -> list[IncidentHistoryItem]:
    """Return recent classified incidents stored in BigQuery."""

    try:
        records = list_recent_incident_classifications(limit=limit)
    except BigQueryRepositoryError as exc:
        logger.warning("Incident history could not be queried: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "incident_history_unavailable",
                "message": "Incident history is temporarily unavailable.",
            },
        ) from exc

    return [build_incident_history_item(record) for record in records]


@router.get(
    "/{incident_id}",
    response_model=IncidentDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get classified incident detail",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse},
    },
)
def get_incident_endpoint(incident_id: str) -> IncidentDetailResponse:
    """Return one classified incident by its incident ID."""

    try:
        record = get_incident_classification_by_id(incident_id)
    except BigQueryRepositoryError as exc:
        logger.warning("Incident detail could not be queried: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "incident_history_unavailable",
                "message": "Incident history is temporarily unavailable.",
            },
        ) from exc

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "incident_not_found",
                "message": "No incident was found for the provided incident_id.",
            },
        )

    return build_incident_detail_response(record)