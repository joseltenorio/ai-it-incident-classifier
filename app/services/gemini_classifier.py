# app/services/gemini_classifier.py

from time import perf_counter
from typing import Any

from google import genai

from app.config import settings
from app.core.classification_validator import validate_or_fallback
from app.core.prompt_builder import build_incident_classification_prompt
from app.schemas import IncidentClassification, IncidentRequest


class GeminiClassifierError(RuntimeError):
    """Raised when the Gemini classifier cannot complete a request."""


def classify_incident_with_gemini(
    request: IncidentRequest,
) -> tuple[IncidentClassification, str, int]:
    """Classify an incident using Gemini API.

    The function returns the validated classification, the raw model output
    and the model latency in milliseconds. The raw output will later be useful
    for BigQuery traceability.
    """

    if not settings.gemini_api_key:
        raise GeminiClassifierError(
            "GEMINI_API_KEY is required when CLASSIFIER_PROVIDER=gemini."
        )

    prompt = build_incident_classification_prompt(request)
    client = genai.Client(api_key=settings.gemini_api_key)

    started_at = perf_counter()

    try:
        interaction = client.interactions.create(
            model=settings.gemini_model,
            input=prompt,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": IncidentClassification.model_json_schema(),
            },
        )
    except Exception as exc:
        raise GeminiClassifierError("Gemini API request failed.") from exc

    latency_ms = int((perf_counter() - started_at) * 1000)
    raw_output = _extract_output_text(interaction)

    try:
        classification = IncidentClassification.model_validate_json(raw_output)
    except Exception:
        classification = validate_or_fallback(_safe_empty_payload())

    return classification, raw_output, latency_ms


def _extract_output_text(interaction: Any) -> str:
    """Extract the text output returned by the Gemini SDK interaction object."""

    output_text = getattr(interaction, "output_text", None)

    if not output_text:
        raise GeminiClassifierError("Gemini returned an empty response.")

    return str(output_text)


def _safe_empty_payload() -> dict[str, Any]:
    """Return an invalid payload that intentionally triggers fallback."""

    return {}