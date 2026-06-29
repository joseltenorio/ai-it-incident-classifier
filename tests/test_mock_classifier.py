# tests/test_mock_classifier.py

from app.schemas import (
    ConfidenceLevel,
    IncidentCategory,
    IncidentPriority,
    IncidentRequest,
    ResponsibleArea,
)
from app.services.mock_classifier import classify_incident_with_mock


def test_mock_classifier_detects_vpn_incident() -> None:
    """Verify that VPN-related incidents are classified as infrastructure issues."""

    request = IncidentRequest(
        title="No puedo conectarme a la VPN",
        description="El cliente VPN muestra un error de autenticación desde ayer.",
    )

    classification = classify_incident_with_mock(request)

    assert classification.category == IncidentCategory.VPN
    assert classification.priority == IncidentPriority.MEDIUM
    assert classification.responsible_area == ResponsibleArea.INFRASTRUCTURE
    assert classification.confidence_level == ConfidenceLevel.MEDIUM
    assert classification.needs_human_review is False


def test_mock_classifier_detects_security_incident_as_high_priority() -> None:
    """Verify that security incidents are escalated with high priority."""

    request = IncidentRequest(
        title="Inicio de sesión sospechoso",
        description="El usuario reporta un acceso sospechoso y problemas con MFA.",
    )

    classification = classify_incident_with_mock(request)

    assert classification.category == IncidentCategory.SECURITY
    assert classification.priority == IncidentPriority.HIGH
    assert classification.responsible_area == ResponsibleArea.SECURITY


def test_mock_classifier_marks_unknown_incident_for_human_review() -> None:
    """Verify that unclear incidents are classified as Other and require review."""

    request = IncidentRequest(
        title="Problema extraño",
        description="El usuario indica que algo no funciona, pero no entrega detalles claros.",
    )

    classification = classify_incident_with_mock(request)

    assert classification.category == IncidentCategory.OTHER
    assert classification.responsible_area == ResponsibleArea.IT_SUPPORT
    assert classification.confidence_level == ConfidenceLevel.LOW
    assert classification.needs_human_review is True