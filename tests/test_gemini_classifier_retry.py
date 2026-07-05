# tests/test_gemini_classifier_retry.py

from unittest.mock import Mock

import pytest

from app.services import gemini_classifier
from app.services.gemini_classifier import _generate_content_with_retries


class FakeGeminiApiError(Exception):
    """Test double that behaves like a Gemini SDK error with status_code."""

    def __init__(self, status_code: int):
        super().__init__(f"fake Gemini error {status_code}")
        self.status_code = status_code


def test_generate_content_retries_transient_error(monkeypatch) -> None:
    """Verify that transient Gemini errors are retried."""

    calls = {"count": 0}

    def fake_sleep(seconds: int) -> None:
        return None

    def fake_generate_content(*args, **kwargs):
        calls["count"] += 1

        if calls["count"] == 1:
            raise FakeGeminiApiError(503)

        return Mock(text='{"category":"VPN"}')

    client = Mock()
    client.models.generate_content = fake_generate_content

    monkeypatch.setattr(gemini_classifier, "sleep", fake_sleep)
    monkeypatch.setattr(
        gemini_classifier.errors,
        "APIError",
        FakeGeminiApiError,
    )

    response = _generate_content_with_retries(client, "prompt", max_attempts=2)

    assert response.text == '{"category":"VPN"}'
    assert calls["count"] == 2


def test_generate_content_does_not_retry_non_transient_error(monkeypatch) -> None:
    """Verify that non-transient Gemini errors fail immediately."""

    calls = {"count": 0}

    def fake_generate_content(*args, **kwargs):
        calls["count"] += 1
        raise FakeGeminiApiError(400)

    client = Mock()
    client.models.generate_content = fake_generate_content

    monkeypatch.setattr(
        gemini_classifier.errors,
        "APIError",
        FakeGeminiApiError,
    )

    with pytest.raises(FakeGeminiApiError):
        _generate_content_with_retries(client, "prompt", max_attempts=3)

    assert calls["count"] == 1


def test_generate_content_raises_after_max_transient_attempts(monkeypatch) -> None:
    """Verify that repeated transient failures stop after max attempts."""

    calls = {"count": 0}

    def fake_sleep(seconds: int) -> None:
        return None

    def fake_generate_content(*args, **kwargs):
        calls["count"] += 1
        raise FakeGeminiApiError(503)

    client = Mock()
    client.models.generate_content = fake_generate_content

    monkeypatch.setattr(gemini_classifier, "sleep", fake_sleep)
    monkeypatch.setattr(
        gemini_classifier.errors,
        "APIError",
        FakeGeminiApiError,
    )

    with pytest.raises(FakeGeminiApiError):
        _generate_content_with_retries(client, "prompt", max_attempts=3)

    assert calls["count"] == 3