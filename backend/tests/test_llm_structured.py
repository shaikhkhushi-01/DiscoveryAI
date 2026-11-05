import pytest

from app.services.llm.base import LLMProvider


class StubProvider(LLMProvider):
    def __init__(self, response: str):
        self.response = response

    async def generate(self, prompt, *, system=None, temperature=0.0):
        return self.response


@pytest.mark.asyncio
async def test_structured_unwraps_single_object_array():
    provider = StubProvider('[{"verdict":"review","evidence_ids":["EVIDENCE 1"]}]')

    result = await provider.structured("assess")

    assert result == {"verdict": "review", "evidence_ids": ["EVIDENCE 1"]}


@pytest.mark.asyncio
async def test_structured_rejects_multiple_object_array():
    provider = StubProvider('[{"verdict":"accept"},{"verdict":"reject"}]')

    with pytest.raises(ValueError, match="must be a JSON object"):
        await provider.structured("assess")
