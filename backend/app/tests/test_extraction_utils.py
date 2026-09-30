import pytest
from app.services.normalization import classify_future_work, classify_limitation, normalize_concepts
from app.services.retry import with_retry

@pytest.mark.asyncio
async def test_retry_eventually_succeeds():
    state={"n":0}
    async def fn():
        state["n"] += 1
        if state["n"] < 2: raise RuntimeError("temporary")
        return "ok"
    assert await with_retry(fn, attempts=3, base_delay=0) == "ok"

def test_normalization_and_classification():
    assert normalize_concepts([" BERT ", "bert", "GPT-4"]) == ["BERT", "GPT-4"]
    assert classify_limitation("The dataset is too small") == "data"
    assert classify_future_work("Evaluate on a larger benchmark") == "data"
