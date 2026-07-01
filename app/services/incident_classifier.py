# app/services/incident_classifier.py

import logging

from app.config import settings
from app.core.classification_validator import build_fallback_classification
from app.schemas import IncidentClassification, IncidentRequest
from app.services.gemini_classifier import (
    GeminiClassifierError,
    classify_incident_with_gemini,
)
from app.services.mock_classifier import classify_incident_with_mock

logger = logging.getLogger(__name__)


def classify_incident(
    request: IncidentRequest,
) -> tuple[IncidentClassification, str, int]:
    """Classify an incident using the configured classifier provider.

    The mock provider keeps local development deterministic. The Gemini provider
    enables the real AI classifier while preserving the same API contract.
    """

    if settings.use_gemini_classifier:
        try:
            return classify_incident_with_gemini(request)
        except GeminiClassifierError as exc:
            logger.warning("Gemini classifier failed. Returning fallback: %s", exc)
            fallback = build_fallback_classification()
            return fallback, str(exc), 0

    classification = classify_incident_with_mock(request)
    return classification, classification.model_dump_json(), 0