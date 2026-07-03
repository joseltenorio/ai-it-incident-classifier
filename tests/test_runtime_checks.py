# tests/test_runtime_checks.py

from app.config import ClassifierProvider
from app.core.runtime_checks import build_runtime_readiness_report


def test_runtime_readiness_is_ready_with_default_mock_configuration(
    monkeypatch,
) -> None:
    """Verify that the default mock runtime is ready without external secrets."""

    from app.core import runtime_checks

    monkeypatch.setattr(
        runtime_checks.settings,
        "classifier_provider",
        ClassifierProvider.MOCK,
    )
    monkeypatch.setattr(runtime_checks.settings, "enable_bigquery_persistence", False)
    monkeypatch.setattr(runtime_checks.settings, "gemini_api_key", None)
    monkeypatch.setattr(runtime_checks.settings, "google_cloud_project", None)

    report = build_runtime_readiness_report()

    assert report["status"] == "ready"
    assert report["checks"]["gemini_api_key"] == "not_required"
    assert report["checks"]["google_cloud_project"] == "not_required"


def test_runtime_readiness_requires_gemini_key_when_provider_is_gemini(
    monkeypatch,
) -> None:
    """Verify that Gemini mode requires a configured API key."""

    from app.core import runtime_checks

    monkeypatch.setattr(
        runtime_checks.settings,
        "classifier_provider",
        ClassifierProvider.GEMINI,
    )
    monkeypatch.setattr(runtime_checks.settings, "gemini_api_key", None)
    monkeypatch.setattr(runtime_checks.settings, "enable_bigquery_persistence", False)

    report = build_runtime_readiness_report()

    assert report["status"] == "not_ready"
    assert report["checks"]["gemini_api_key"] == "missing"


def test_runtime_readiness_requires_project_when_bigquery_is_enabled(
    monkeypatch,
) -> None:
    """Verify that BigQuery persistence requires a Google Cloud project."""

    from app.core import runtime_checks

    monkeypatch.setattr(
        runtime_checks.settings,
        "classifier_provider",
        ClassifierProvider.MOCK,
    )
    monkeypatch.setattr(runtime_checks.settings, "enable_bigquery_persistence", True)
    monkeypatch.setattr(runtime_checks.settings, "google_cloud_project", None)

    report = build_runtime_readiness_report()

    assert report["status"] == "not_ready"
    assert report["checks"]["google_cloud_project"] == "missing"
    assert report["checks"]["bigquery_table_id"] == "missing"