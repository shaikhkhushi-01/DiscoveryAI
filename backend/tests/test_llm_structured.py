import pytest

from app.services.llm.base import LLMProvider


class StubProvider(LLMProvider):
    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls = 0

    async def generate(self, prompt, *, system=None, temperature=0.0):
        response = self.responses[min(self.calls, len(self.responses) - 1)]
        self.calls += 1
        return response


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


@pytest.mark.asyncio
async def test_structured_repairs_trailing_comma_json():
    provider = StubProvider('not json at all', '{"topics":["RAG",],"methods":[],}')
    result = await provider.structured("extract")
    assert result == {"topics": ["RAG"], "methods": []}
    assert provider.calls == 2


@pytest.mark.asyncio
async def test_structured_extracts_object_from_markdown_fence():
    provider = StubProvider('\`\`\`json\\n{"topics":["RAG"]}\\n\`\`\`')
    assert await provider.structured("extract") == {"topics": ["RAG"]}
