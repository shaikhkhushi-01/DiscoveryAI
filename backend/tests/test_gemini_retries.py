import httpx
import pytest

from app.services.llm.gemini import GeminiProvider, GeminiUpstreamError


class SettingsStub:
    gemini_model = "gemini-test"
    gemini_api_key = type("Secret", (), {"get_secret_value": lambda self: "test-secret"})()
    gemini_base_url = "https://example.test/v1"


@pytest.mark.asyncio
async def test_gemini_retries_transient_503(monkeypatch):
    import app.services.llm.gemini as module

    monkeypatch.setattr(module, "settings", SettingsStub())
    calls = {"count": 0}

    class Client:
        def __init__(self, *args, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            return False
        async def post(self, *args, **kwargs):
            calls["count"] += 1
            if calls["count"] < 3:
                return httpx.Response(503, request=httpx.Request("POST", "https://example.test"))
            return httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": "{\\"ok\\": true}"}]}}]}, request=httpx.Request("POST", "https://example.test"))

    async def no_sleep(_):
        return None

    monkeypatch.setattr(module.httpx, "AsyncClient", Client)
    monkeypatch.setattr(module.asyncio, "sleep", no_sleep)
    provider = GeminiProvider()
    assert await provider.generate("hello") == '{"ok": true}'
    assert calls["count"] == 3


@pytest.mark.asyncio
async def test_gemini_final_503_is_sanitized(monkeypatch):
    import app.services.llm.gemini as module

    monkeypatch.setattr(module, "settings", SettingsStub())

    class Client:
        def __init__(self, *args, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            return False
        async def post(self, *args, **kwargs):
            return httpx.Response(503, request=httpx.Request("POST", "https://example.test"))

    async def no_sleep(_):
        return None

    monkeypatch.setattr(module.httpx, "AsyncClient", Client)
    monkeypatch.setattr(module.asyncio, "sleep", no_sleep)
    provider = GeminiProvider()
    with pytest.raises(GeminiUpstreamError) as error:
        await provider.generate("hello")
    assert "test-secret" not in str(error.value)
    assert "key=" not in str(error.value)
    assert error.value.status_code == 503
