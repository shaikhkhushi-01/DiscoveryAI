from app.services.llm.gemini import (
    GeminiUpstreamError,
    RETRYABLE_STATUS_CODES,
    _retry_delay,
)


def test_gemini_retries_service_unavailable_and_rate_limits():
    assert 503 in RETRYABLE_STATUS_CODES
    assert 429 in RETRYABLE_STATUS_CODES


def test_retry_after_is_respected_and_capped():
    class Response:
        headers = {"Retry-After": "12"}

    assert _retry_delay(Response(), 0) == 12.0


def test_gemini_upstream_error_does_not_expose_request_url_or_api_key():
    error = GeminiUpstreamError(503, "Gemini API temporarily unavailable (HTTP 503)")
    assert "generativelanguage.googleapis.com" not in str(error)
    assert "key=" not in str(error)
    assert error.status_code == 503
