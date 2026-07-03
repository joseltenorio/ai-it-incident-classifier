# app/core/runtime_checks.py

from typing import Any

from app.config import settings


def build_runtime_readiness_report() -> dict[str, Any]:
    """Build a readiness report from runtime configuration.

    This check validates configuration only. It does not call Gemini or BigQuery,
    so it remains fast and safe for health/readiness probes.
    """

    checks: dict[str, str] = {}
    is_ready = True

    if settings.use_gemini_classifier:
        if settings.gemini_api_key:
            checks["gemini_api_key"] = "configured"
        else:
            checks["gemini_api_key"] = "missing"
            is_ready = False
    else:
        checks["gemini_api_key"] = "not_required"

    if settings.enable_bigquery_persistence:
        if settings.google_cloud_project:
            checks["google_cloud_project"] = "configured"
        else:
            checks["google_cloud_project"] = "missing"
            is_ready = False

        if settings.bigquery_table_id:
            checks["bigquery_table_id"] = "configured"
        else:
            checks["bigquery_table_id"] = "missing"
            is_ready = False
    else:
        checks["google_cloud_project"] = "not_required"
        checks["bigquery_table_id"] = "not_required"

    return {
        "status": "ready" if is_ready else "not_ready",
        "environment": settings.environment,
        "classifier_provider": settings.classifier_provider.value,
        "bigquery_persistence_enabled": settings.enable_bigquery_persistence,
        "checks": checks,
    }