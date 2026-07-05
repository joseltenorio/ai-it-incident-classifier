# app/services/gemini_classifier.py

import logging
import re
from time import perf_counter, sleep
from typing import Any

from google import genai
from google.genai import errors, types

from app.config import settings
from app.core.classification_validator import validate_or_fallback
from app.core.prompt_builder import build_incident_classification_prompt
from app.schemas import IncidentClassification, IncidentRequest

logger = logging.getLogger(__name__)

# Service-side failures can happen when the model is temporarily overloaded.
# These are safe to retry because the request is read-only from the model side.
TRANSIENT_GEMINI_STATUS_CODES = {500, 503, 504}


class GeminiClassifierError(RuntimeError):
    """Raised when the Gemini classifier cannot complete a request."""


def classify_incident_with_gemini(
    request: IncidentRequest,
) -> tuple[IncidentClassification, str, int]:
    """Classify an incident using Gemini API.

    The function returns the validated classification, the raw model output
    and the model latency in milliseconds. The raw output is stored later in
    BigQuery for traceability.
    """

    if not settings.gemini_api_key:
        raise GeminiClassifierError(
            "GEMINI_API_KEY is required when CLASSIFIER_PROVIDER=gemini."
        )

    prompt = build_incident_classification_prompt(request)

    client = genai.Client(
        api_key=settings.gemini_api_key,
        http_options=types.HttpOptions(
            retry_options=types.HttpRetryOptions(attempts=1),
        ),
    )

    started_at = perf_counter()

    try:
        response = _generate_content_with_retries(client, prompt)
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


def _generate_content_with_retries(
    client: genai.Client,
    prompt: str,
    max_attempts: int = 3,
) -> Any:
    """Call Gemini with retries for transient service-side failures.

    Transient errors such as 500, 503 and 504 can happen when the service is
    temporarily overloaded. Non-transient errors like invalid requests,
    authentication failures or billing failures are not retried.
    """

    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            return client.models.generate_content(
                model=settings.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0,
                    response_mime_type="application/json",
                    response_schema=IncidentClassification,
                ),
            )
        except errors.APIError as exc:
            status_code = _extract_gemini_status_code(exc)
            last_error = exc

            if status_code not in TRANSIENT_GEMINI_STATUS_CODES:
                logger.error(
                    "Gemini API failed with non-retryable status %s. Error: %s",
                    status_code,
                    exc,
                )
                raise

            if attempt == max_attempts:
                logger.error(
                    "Gemini API failed after %s attempts with status %s. Error: %s",
                    max_attempts,
                    status_code,
                    exc,
                )
                raise

            wait_seconds = attempt
            logger.warning(
                "Gemini API transient failure status=%s attempt=%s/%s. "
                "Retrying in %s second(s).",
                status_code,
                attempt,
                max_attempts,
                wait_seconds,
            )
            sleep(wait_seconds)

    raise GeminiClassifierError(f"Gemini API request failed: {last_error}")


def _extract_gemini_status_code(exc: Exception) -> int | None:
    """Extract an HTTP status code from a Gemini SDK exception.

    Different SDK exceptions may expose the status as status_code, code,
    response.status_code or only inside the string representation.
    """

    status_code = getattr(exc, "status_code", None)

    if isinstance(status_code, int):
        return status_code

    code = getattr(exc, "code", None)

    if isinstance(code, int):
        return code

    response = getattr(exc, "response", None)
    response_status = getattr(response, "status_code", None)

    if isinstance(response_status, int):
        return response_status

    match = re.search(r"\b(400|401|403|404|429|500|503|504)\b", str(exc))

    if match:
        return int(match.group(1))

    return None


def _extract_output_text(response: Any) -> str:
    """Extract the text output returned by the Gemini SDK response object."""

    output_text = getattr(response, "text", None)

    if not output_text:
        raise GeminiClassifierError("Gemini returned an empty response.")

    return str(output_text)


def _safe_empty_payload() -> dict[str, Any]:
    """Return an invalid payload that intentionally triggers fallback."""

    return {}