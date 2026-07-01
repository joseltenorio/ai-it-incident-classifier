# app/services/gemini_classifier.py

import logging
from time import perf_counter
from typing import Any

from google import genai
from google.genai import types

from app.config import settings
from app.core.classification_validator import validate_or_fallback
from app.core.prompt_builder import build_incident_classification_prompt
from app.schemas import IncidentClassification, IncidentRequest

logger = logging.getLogger(__name__)


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

    # Retries are limited to one attempt during local development.
    # This prevents one Swagger/Postman request from being multiplied into
    # several Gemini API attempts when the API returns 429 rate-limit errors.
    client = genai.Client(
        api_key=settings.gemini_api_key,
        http_options=types.HttpOptions(
            retry_options=types.HttpRetryOptions(attempts=1),
        ),
    )

    started_at = perf_counter()

    try:
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
                response_schema=IncidentClassification,
            ),
        )
    except Exception as exc:
        logger.exception("Gemini API request failed.")
        raise GeminiClassifierError(f"Gemini API request failed: {exc}") from exc

    latency_ms = int((perf_counter() - started_at) * 1000)
    raw_output = _extract_output_text(response)

    try:
        classification = IncidentClassification.model_validate_json(raw_output)
    except Exception:
        logger.exception("Gemini returned invalid structured output.")
        classification = validate_or_fallback(_safe_empty_payload())

    return classification, raw_output, latency_ms


def _extract_output_text(response: Any) -> str:
    """Extract the text output returned by the Gemini SDK response object."""

    output_text = getattr(response, "text", None)

    if not output_text:
        raise GeminiClassifierError("Gemini returned an empty response.")

    return str(output_text)


def _safe_empty_payload() -> dict[str, Any]:
    """Return an invalid payload that intentionally triggers fallback."""

    return {}