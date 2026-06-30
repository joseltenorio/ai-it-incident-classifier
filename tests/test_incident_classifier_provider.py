# tests/test_incident_classifier_provider.py

from app.schemas import IncidentCategory, IncidentRequest
from app.services.incident_classifier import classify_incident


def test_incident_classifier_uses_mock_provider_by_default() -> None:
    """Verify that the default provider keeps local classification deterministic."""

    request = IncidentRequest(
        title="No puedo conectarme a la VPN",
        description="El cliente VPN muestra error de autenticación desde ayer.",
    )

    classification, raw_output, latency_ms = classify_incident(request)

    assert classification.category == IncidentCategory.VPN
    assert "VPN" in raw_output
    assert latency_ms == 0