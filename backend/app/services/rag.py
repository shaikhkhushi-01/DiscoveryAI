from __future__ import annotations

from typing import Any

from app.services.llm.factory import get_llm_provider
from app.services.retrieval.hybrid import hybrid_search
from app.services.retrieval.reranker import rerank

SYSTEM = """You are DiscoveryAI, an evidence-grounded scientific research assistant.
Use only the supplied retrieved evidence. Do not claim that nobody has researched something.
If evidence is insufficient, say that no relevant evidence was identified within the indexed corpus and search scope.
Every factual claim about the literature must be traceable to a source ID."""

async def answer_question(query: str, *, limit: int = 8, filters: dict[str, Any] | None = None) -> dict[str, Any]:
    retrieved = hybrid_search(query, limit=max(limit * 3, 12), filters=filters)
    ranked = rerank(query, retrieved, limit=limit)
    context = "

".join(
        f"[EVIDENCE {i+1}] document={item.get('document_id')} chunk={item.get('chunk_id')}\n{item.get('text','')}"
        for i, item in enumerate(ranked)
    )
    if not context:
        return {"answer": "No relevant evidence was identified within the indexed corpus and search scope.", "sources": []}
    prompt = f"""Research question:
{query}

Retrieved evidence:
{context}

Answer concisely. Cite evidence using [EVIDENCE N] markers. Separate direct evidence from inference."""
    answer = await get_llm_provider().generate(prompt, system=SYSTEM, temperature=0.0)
    return {"answer": answer, "sources": ranked}
