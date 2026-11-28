import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime

import httpx
import pytest
from pydantic import SecretStr

from app.services.llm.gemini import (
    GeminiProvider,
    GeminiUpstreamError,
    RETRYABLE_STATUS_CODES,
)


def configure_settings(monkeypatch, fallback=None, api_key="test-api-key"):
    """Configure isolated Gemini settings without using the real API key."""
    from app.core.config import settings

    monkeypatch.setattr(
        settings,
        "gemini_api_key",
        SecretStr(api_key) if api_key else None,
    )
    monkeypatch.setattr(settings, "gemini_model", "test-primary")
    monkeypatch.setattr(settings, "gemini_fallback_model", fallback)
    monkeypatch.setattr(
        settings,
        "gemini_base_url",
        "https://example.test/v1beta/",
    )


def mock_response(status_code=200, data=None, headers=None):
    response = MagicMock()
    response.status_code = status_code
    response.is_error = status_code >= 400
    response.headers = headers or {}
    response.json.return_value = data or {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": '{"answer": "test response"}'}]
                }
            }
        ]
    }
    return response


def test_provider_requires_api_key(monkeypatch):
    configure_settings(monkeypatch, api_key=None)

    with pytest.raises(ValueError, match="GEMINI_API_KEY is required"):
        GeminiProvider()


def test_provider_uses_configured_model_and_fallback(monkeypatch):
    configure_settings(monkeypatch, fallback="test-fallback")

    provider = GeminiProvider()

    assert provider.model == "test-primary"
    assert provider.fallback_model == "test-fallback"
    assert provider.base_url == "https://example.test/v1beta"


def test_provider_disables_duplicate_fallback(monkeypatch):
    configure_settings(monkeypatch, fallback="test-primary")

    provider = GeminiProvider()

    assert provider.fallback_model is None


@pytest.mark.asyncio
async def test_generate_returns_candidate_text(monkeypatch):
    configure_settings(monkeypatch)
    provider = GeminiProvider()

    response = mock_response()
    post = AsyncMock(return_value=response)

    with (
        patch("app.services.llm.gemini.asyncio.sleep", new_callable=AsyncMock),
        patch("app.services.llm.gemini.httpx.AsyncClient") as client_class,
    ):
        client = AsyncMock()
        client.post = post
        client_class.return_value.__aenter__.return_value = client

        result = await provider.generate(
            "Test prompt",
            system="Test system",
            temperature=0.2,
        )

    assert result == '{"answer": "test response"}'
    assert post.await_count == 1

    request = post.await_args
    assert request.args[0] == (
        "https://example.test/v1beta/models/test-primary:generateContent"
    )
    assert request.kwargs["headers"]["x-goog-api-key"] == "test-api-key"
    assert request.kwargs["json"]["generationConfig"]["temperature"] == 0.2


@pytest.mark.asyncio
async def test_generate_stops_immediately_on_http_429(monkeypatch):
    configure_settings(monkeypatch, fallback="test-fallback")
    provider = GeminiProvider()
    provider.max_attempts = 4

    post = AsyncMock(return_value=mock_response(429))

    with (
        patch("app.services.llm.gemini.asyncio.sleep", new_callable=AsyncMock),
        patch("app.services.llm.gemini.httpx.AsyncClient") as client_class,
    ):
        client = AsyncMock()
        client.post = post
        client_class.return_value.__aenter__.return_value = client

        with pytest.raises(GeminiUpstreamError) as error:
            await provider.generate("Test prompt")

    assert error.value.status_code == 429
    assert error.value.retryable is False
    assert "quota" in str(error.value).lower()
    assert post.await_count == 1


@pytest.mark.asyncio
async def test_generate_retries_network_timeout(monkeypatch):
    configure_settings(monkeypatch)
    provider = GeminiProvider()
    provider.max_attempts = 2

    post = AsyncMock(
        side_effect=[
            httpx.TimeoutException("simulated timeout"),
            mock_response(200),
        ]
    )

    with (
        patch("app.services.llm.gemini.asyncio.sleep", new_callable=AsyncMock),
        patch("app.services.llm.gemini.httpx.AsyncClient") as client_class,
    ):
        client = AsyncMock()
        client.post = post
        client_class.return_value.__aenter__.return_value = client

        result = await provider.generate("Test prompt")

    assert result == '{"answer": "test response"}'
    assert post.await_count == 2


@pytest.mark.asyncio
async def test_generate_uses_fallback_after_retryable_failure(monkeypatch):
    configure_settings(monkeypatch, fallback="test-fallback")
    provider = GeminiProvider()
    provider.max_attempts = 1

    responses = [
        mock_response(503),
        mock_response(200),
    ]

    post = AsyncMock(side_effect=responses)

    with (
        patch("app.services.llm.gemini.asyncio.sleep", new_callable=AsyncMock),
        patch("app.services.llm.gemini.httpx.AsyncClient") as client_class,
    ):
        client = AsyncMock()
        client.post = post
        client_class.return_value.__aenter__.return_value = client

        result = await provider.generate("Test prompt")

    assert result == '{"answer": "test response"}'
    assert post.await_count == 2

    called_urls = [
        call.args[0]
        for call in post.await_args_list
    ]

    assert "test-primary" in called_urls[0]
    assert "test-fallback" in called_urls[1]


@pytest.mark.asyncio
async def test_generate_does_not_fallback_for_non_retryable_error(monkeypatch):
    configure_settings(monkeypatch, fallback="test-fallback")
    provider = GeminiProvider()
    provider.max_attempts = 1

    post = AsyncMock(return_value=mock_response(400))

    with (
        patch("app.services.llm.gemini.asyncio.sleep", new_callable=AsyncMock),
        patch("app.services.llm.gemini.httpx.AsyncClient") as client_class,
    ):
        client = AsyncMock()
        client.post = post
        client_class.return_value.__aenter__.return_value = client

        with pytest.raises(GeminiUpstreamError) as error:
            await provider.generate("Test prompt")

    assert error.value.status_code == 400
    assert error.value.retryable is False
    assert post.await_count == 1


@pytest.mark.asyncio
async def test_generate_stops_after_quota_limit(monkeypatch):
    configure_settings(monkeypatch)
    provider = GeminiProvider()
    provider.max_attempts = 2

    post = AsyncMock(return_value=mock_response(429))

    with (
        patch("app.services.llm.gemini.asyncio.sleep", new_callable=AsyncMock),
        patch("app.services.llm.gemini.httpx.AsyncClient") as client_class,
    ):
        client = AsyncMock()
        client.post = post
        client_class.return_value.__aenter__.return_value = client

        with pytest.raises(GeminiUpstreamError) as error:
            await provider.generate("Test prompt")

    assert error.value.status_code == 429
    assert error.value.retryable is False
    assert post.await_count == 1


@pytest.mark.asyncio
async def test_generate_rejects_empty_candidates(monkeypatch):
    configure_settings(monkeypatch)
    provider = GeminiProvider()

    post = AsyncMock(
        return_value=mock_response(
            200,
            data={"candidates": []},
        )
    )

    with (
        patch("app.services.llm.gemini.asyncio.sleep", new_callable=AsyncMock),
        patch("app.services.llm.gemini.httpx.AsyncClient") as client_class,
    ):
        client = AsyncMock()
        client.post = post
        client_class.return_value.__aenter__.return_value = client

        with pytest.raises(ValueError, match="no candidates"):
            await provider.generate("Test prompt")


@pytest.mark.asyncio
async def test_generate_rejects_empty_candidate_text(monkeypatch):
    configure_settings(monkeypatch)
    provider = GeminiProvider()

    post = AsyncMock(
        return_value=mock_response(
            200,
            data={
                "candidates": [
                    {"content": {"parts": [{"text": ""}]}}
                ]
            },
        )
    )

    with (
        patch("app.services.llm.gemini.asyncio.sleep", new_callable=AsyncMock),
        patch("app.services.llm.gemini.httpx.AsyncClient") as client_class,
    ):
        client = AsyncMock()
        client.post = post
        client_class.return_value.__aenter__.return_value = client

        with pytest.raises(ValueError, match="empty response"):
            await provider.generate("Test prompt")


def test_retryable_status_codes_are_defined():
    assert 429 in RETRYABLE_STATUS_CODES
    assert 503 in RETRYABLE_STATUS_CODES
    assert 400 not in RETRYABLE_STATUS_CODES

@pytest.mark.asyncio
async def test_generate_rejects_invalid_json(monkeypatch):
    configure_settings(monkeypatch)
    provider = GeminiProvider()

    response = mock_response()
    response.json.side_effect = ValueError("Invalid JSON")

    post = AsyncMock(return_value=response)

    with (
        patch("app.services.llm.gemini.asyncio.sleep", new_callable=AsyncMock),
        patch("app.services.llm.gemini.httpx.AsyncClient") as client_class,
    ):
        client = AsyncMock()
        client.post = post
        client_class.return_value.__aenter__.return_value = client

        with pytest.raises(
            GeminiUpstreamError,
            match="invalid JSON",
        ) as error:
            await provider.generate("Test prompt")

    assert error.value.status_code == 200
    assert error.value.retryable is False


@pytest.mark.asyncio
async def test_generate_rejects_non_dict_response(monkeypatch):
    configure_settings(monkeypatch)
    provider = GeminiProvider()

    response = mock_response()
    response.json.return_value = ["unexpected", "response"]

    post = AsyncMock(return_value=response)

    with (
        patch("app.services.llm.gemini.asyncio.sleep", new_callable=AsyncMock),
        patch("app.services.llm.gemini.httpx.AsyncClient") as client_class,
    ):
        client = AsyncMock()
        client.post = post
        client_class.return_value.__aenter__.return_value = client

        with pytest.raises(
            GeminiUpstreamError,
            match="unexpected response",
        ):
            await provider.generate("Test prompt")


def test_retry_after_http_date(monkeypatch):
    configure_settings(monkeypatch)
    provider = GeminiProvider()

    future_date = datetime.now(timezone.utc) + timedelta(seconds=60)
    retry_after = format_datetime(future_date, usegmt=True)

    delay = provider._get_retry_delay(retry_after, 0)

    assert 0 < delay <= 30


def test_retry_after_invalid_date_uses_backoff(monkeypatch):
    configure_settings(monkeypatch)
    provider = GeminiProvider()

    with patch(
        "app.services.llm.gemini.random.uniform",
        return_value=0.1,
    ):
        delay = provider._get_retry_delay(
            "not-a-valid-date",
            0,
        )

    assert delay == pytest.approx(0.85)


@pytest.mark.asyncio
async def test_generate_uses_configured_request_interval(monkeypatch):
    configure_settings(monkeypatch)

    from app.core.config import settings

    monkeypatch.setattr(
        settings,
        "gemini_request_interval_seconds",
        2.5,
    )

    provider = GeminiProvider()

    post = AsyncMock(return_value=mock_response())

    with (
        patch(
            "app.services.llm.gemini.asyncio.sleep",
            new_callable=AsyncMock,
        ) as sleep_mock,
        patch("app.services.llm.gemini.httpx.AsyncClient") as client_class,
    ):
        client = AsyncMock()
        client.post = post
        client_class.return_value.__aenter__.return_value = client

        await provider.generate("Test prompt")

    sleep_mock.assert_awaited_once_with(2.5)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "data,error_message",
    [
        (
            {"candidates": ["invalid"]},
            "candidate structure",
        ),
        (
            {"candidates": [{"content": []}]},
            "content structure",
        ),
        (
            {"candidates": [{"content": {"parts": "invalid"}}]},
            "parts structure",
        ),
        (
            {"candidates": [{"content": {"parts": ["invalid"]}}]},
            "response part",
        ),
    ],
)
async def test_generate_rejects_malformed_candidate_structure(
    monkeypatch,
    data,
    error_message,
):
    configure_settings(monkeypatch)
    provider = GeminiProvider()

    post = AsyncMock(
        return_value=mock_response(200, data=data)
    )

    with (
        patch("app.services.llm.gemini.asyncio.sleep", new_callable=AsyncMock),
        patch("app.services.llm.gemini.httpx.AsyncClient") as client_class,
    ):
        client = AsyncMock()
        client.post = post
        client_class.return_value.__aenter__.return_value = client

        with pytest.raises(ValueError, match=error_message):
            await provider.generate("Test prompt")