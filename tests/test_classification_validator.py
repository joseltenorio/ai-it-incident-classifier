# tests/test_classification_validator.py

import pytest
from pydantic import ValidationError

from app.core.classification_validator import (
    build_fallback_classification,
    validate_classification_output,
    validate_or_fallback,
)
from app.schemas import (
    ConfidenceLevel,
    IncidentCategory,
    IncidentPriority,
    ResponsibleArea,
)


def test_validate_classification_output_accepts_valid_payload() -> None:
    """Verify that a valid classification dictionary is accepted."""

    classification = validate_classification_output(
        {
            "category": "VPN",
            "priority": "Media",
            "responsible_area": "Infraestructura",
            "summary": "The user cannot connect to the corporate VPN.",
            "suggested_action": "Validate credentials and review VPN service logs.",
            "confidence_level": "Alta",
            "needs_human_review": False,
        }
    )

    assert classification.category == IncidentCategory.VPN
    assert classification.priority == IncidentPriority.MEDIUM
    assert classification.responsible_area == ResponsibleArea.INFRASTRUCTURE
    assert classification.confidence_level == ConfidenceLevel.HIGH
    assert classification.needs_human_review is False


def test_validate_classification_output_rejects_unknown_category() -> None:
    """Verify that uncontrolled categories are rejected."""

    with pytest.raises(ValidationError):
        validate_classification_output(
            {
                "category": "Inventada",
                "priority": "Media",
                "responsible_area": "Infraestructura",
                "summary": "The user cannot connect to the corporate VPN.",
                "suggested_action": "Validate credentials and review VPN service logs.",
                "confidence_level": "Alta",
                "needs_human_review": False,
            }
        )


def test_validate_or_fallback_returns_fallback_for_invalid_payload() -> None:
    """Verify that invalid classifications are converted to manual review."""

    classification = validate_or_fallback(
        {
            "category": "Inventada",
            "priority": "Media",
            "responsible_area": "Infraestructura",
        }
    )

    assert classification.category == IncidentCategory.OTHER
    assert classification.priority == IncidentPriority.MEDIUM
    assert classification.responsible_area == ResponsibleArea.IT_SUPPORT
    assert classification.confidence_level == ConfidenceLevel.LOW
    assert classification.needs_human_review is True


def test_build_fallback_classification_marks_human_review() -> None:
    """Verify that fallback classifications are always flagged for review."""

    classification = build_fallback_classification()

    assert classification.needs_human_review is True
    assert classification.confidence_level == ConfidenceLevel.LOW