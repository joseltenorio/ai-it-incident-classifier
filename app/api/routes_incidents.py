# app/api/routes_incidents.py

from datetime import UTC, datetime

from fastapi import APIRouter, status

from app.config import settings
from app.schemas import IncidentRequest, IncidentResponse
from app.services.incident_id_generator import generate_incident_id
from app.services.mock_classifier import classify_incident_with_mock

# Incident routes contain the core business endpoints of the API.
# The first implementation uses a deterministic mock classifier so the request
# and response contract can be tested before integrating Gemini.
router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.post(
    "/classify",
    response_model=IncidentResponse,
    status_code=status.HTTP_200_OK,
    summary="Classify an IT support incident",
)
def classify_incident(request: IncidentRequest) -> IncidentResponse:
    """Classify an IT incident using the current classifier implementation.

    This first version uses a local mock classifier. A later block will replace
    the mock with Gemini while preserving this public API contract.
    """

    created_at = datetime.now(UTC)
    classification = classify_incident_with_mock(request)

    return IncidentResponse(
        incident_id=generate_incident_id(created_at),
        model_name=f"{settings.gemini_model}-mock",
        created_at=created_at,
        **classification.model_dump(),
    )