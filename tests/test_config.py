# tests/test_config.py

import pytest
from pydantic import ValidationError

from app.config import ClassifierProvider, Settings


def test_settings_uses_mock_classifier_by_default() -> None:
    """Verify that the default classifier provider is mock."""

    settings = Settings(_env_file=None)

    assert settings.classifier_provider == ClassifierProvider.MOCK
    assert settings.use_gemini_classifier is False


def test_settings_detects_gemini_classifier_provider() -> None:
    """Verify that Gemini provider can be enabled through settings."""

    settings = Settings(
        _env_file=None,
        classifier_provider="gemini",
        gemini_api_key="fake-key-for-test",
    )

    assert settings.classifier_provider == ClassifierProvider.GEMINI
    assert settings.use_gemini_classifier is True


def test_settings_rejects_unknown_classifier_provider() -> None:
    """Verify that unsupported classifier providers fail fast."""

    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            classifier_provider="unknown",
        )