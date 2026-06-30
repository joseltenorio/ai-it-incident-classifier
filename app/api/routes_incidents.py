# app/api/routes_incidents.py

from datetime import UTC, datetime

from fastapi import APIRouter, status

from app.config import settings
from app.schemas import IncidentRequest, IncidentResponse
from app.services.incident_classifier import classify_incident
from app.services.incident_id_generator import generate_incident_id

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
    """Classify an IT incident using the configured classifier provider.

    The public response contract remains stable regardless of whether the
    backend uses the local mock classifier or Gemini API.
    """

    created_at = datetime.now(UTC)
    classification, _raw_output, _latency_ms = classify_incident(request)

    model_suffix = "gemini" if settings.use_gemini_classifier else "mock"

    return IncidentResponse(
        incident_id=generate_incident_id(created_at),
        model_name=f"{settings.gemini_model}-{model_suffix}",
        created_at=created_at,
        **classification.model_dump(),
    )