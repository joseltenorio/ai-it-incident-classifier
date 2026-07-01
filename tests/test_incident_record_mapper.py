# tests/test_incident_record_mapper.py

from datetime import UTC, datetime

from app.schemas import (
    ConfidenceLevel,
    IncidentCategory,
    IncidentClassification,
    IncidentPriority,
    IncidentRequest,
    ResponsibleArea,
    SourceChannel,
)
from app.services.incident_record_mapper import build_incident_record


def test_build_incident_record_maps_request_classification_and_metadata() -> None:
    """Verify that a classification is mapped to the BigQuery row contract."""

    request = IncidentRequest(
        title="No puedo conectarme a la VPN",
        description="El cliente VPN muestra error de autenticación desde ayer.",
        reported_by="usuario.demo@empresa.com",
        source_channel=SourceChannel.POSTMAN,
    )
    classification = IncidentClassification(
        category=IncidentCategory.VPN,
        priority=IncidentPriority.MEDIUM,
        responsible_area=ResponsibleArea.INFRASTRUCTURE,
        summary="The user cannot connect to the corporate VPN.",
        suggested_action="Validate credentials and review VPN logs.",
        confidence_level=ConfidenceLevel.MEDIUM,
        needs_human_review=False,
    )
    created_at = datetime(2026, 7, 1, 10, 30, tzinfo=UTC)

    record = build_incident_record(
        request=request,
        classification=classification,
        incident_id="INC-20260701-ABC12345",
        model_name="gemini-2.5-flash-mock",
        model_latency_ms=0,
        raw_model_response='{"category":"VPN"}',
        created_at=created_at,
    )

    assert record == {
        "incident_id": "INC-20260701-ABC12345",
        "title": "No puedo conectarme a la VPN",
        "description": "El cliente VPN muestra error de autenticación desde ayer.",
        "reported_by": "usuario.demo@empresa.com",
        "source_channel": "postman",
        "category": "VPN",
        "priority": "Media",
        "responsible_area": "Infraestructura",
        "summary": "The user cannot connect to the corporate VPN.",
        "suggested_action": "Validate credentials and review VPN logs.",
        "confidence_level": "Media",
        "needs_human_review": False,
        "model_name": "gemini-2.5-flash-mock",
        "model_latency_ms": 0,
        "raw_model_response": '{"category":"VPN"}',
        "created_at": "2026-07-01T10:30:00+00:00",
    }