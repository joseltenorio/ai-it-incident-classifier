# app/core/classification_validator.py

from typing import Any, Mapping

from pydantic import ValidationError

from app.schemas import (
    ConfidenceLevel,
    IncidentCategory,
    IncidentClassification,
    IncidentPriority,
    ResponsibleArea,
)


def validate_classification_output(
    raw_classification: Mapping[str, Any],
) -> IncidentClassification:
    """Validate a raw classification dictionary against the API contract.

    The AI model integration will later produce dictionaries from model output.
    This function ensures those dictionaries are converted into a strongly typed
    IncidentClassification only when all fields match the controlled schema.
    """

    return IncidentClassification.model_validate(raw_classification)


def build_fallback_classification() -> IncidentClassification:
    """Build a safe manual-review classification for invalid model responses.

    This fallback keeps the API predictable when the classifier cannot produce
    a trusted structured response.
    """

    return IncidentClassification(
        category=IncidentCategory.OTHER,
        priority=IncidentPriority.MEDIUM,
        responsible_area=ResponsibleArea.IT_SUPPORT,
        summary=(
            "The incident requires manual review because it could not be "
            "classified automatically."
        ),
        suggested_action=(
            "Review the ticket details manually and assign it to the appropriate "
            "support area."
        ),
        confidence_level=ConfidenceLevel.LOW,
        needs_human_review=True,
    )


def validate_or_fallback(raw_classification: Mapping[str, Any]) -> IncidentClassification:
    """Return a validated classification or fallback when validation fails."""

    try:
        return validate_classification_output(raw_classification)
    except ValidationError:
        return build_fallback_classification()