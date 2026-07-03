# tests/test_incident_history_mapper.py

from datetime import UTC, datetime

from app.schemas import (
    ConfidenceLevel,
    IncidentCategory,
    IncidentPriority,
    ResponsibleArea,
    SourceChannel,
)
from app.services.incident_history_mapper import (
    build_incident_detail_response,
    build_incident_history_item,
)


def test_build_incident_history_item_maps_compact_record() -> None:
    """Verify that compact BigQuery records map to history response items."""

    record = {
        "incident_id": "INC-20260704-8E878D27",
        "title": "No puedo conectarme a la VPN",
        "category": "VPN",
        "priority": "Media",
        "responsible_area": "Infraestructura",
        "confidence_level": "Media",
        "needs_human_review": False,
        "model_name": "gemini-2.5-flash-mock",
        "created_at": datetime(2026, 7, 4, 2, 41, 24, tzinfo=UTC),
    }

    item = build_incident_history_item(record)

    assert item.incident_id == "INC-20260704-8E878D27"
    assert item.category == IncidentCategory.VPN
    assert item.priority == IncidentPriority.MEDIUM
    assert item.responsible_area == ResponsibleArea.INFRASTRUCTURE
    assert item.confidence_level == ConfidenceLevel.MEDIUM


def test_build_incident_detail_response_maps_full_record() -> None:
    """Verify that full BigQuery records map to incident detail responses."""

    record = {
        "incident_id": "INC-20260704-8E878D27",
        "title": "No puedo conectarme a la VPN",
        "description": "Desde ayer intento conectarme a la VPN corporativa.",
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
        "created_at": datetime(2026, 7, 4, 2, 41, 24, tzinfo=UTC),
    }

    detail = build_incident_detail_response(record)

    assert detail.incident_id == "INC-20260704-8E878D27"
    assert detail.source_channel == SourceChannel.POSTMAN
    assert detail.category == IncidentCategory.VPN
    assert detail.model_latency_ms == 0