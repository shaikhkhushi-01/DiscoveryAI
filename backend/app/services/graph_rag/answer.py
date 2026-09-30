from __future__ import annotations

from typing import Any

from app.services.graph_rag.pipeline import retrieve_graph_rag
from app.services.llm.factory import get_llm_provider

SYSTEM = """You are DiscoveryAI using GraphRAG for scientific discovery.
Use only the supplied vector evidence and graph evidence.
Do not claim that nobody has researched something.
If evidence is insufficient, state: "No relevant evidence was identified within the indexed corpus and search scope."
Distinguish direct evidence from graph-derived relationships and inference.
Every literature claim must be traceable to an evidence or graph item."""

async def answer_graph_rag(query: str, *, limit: int = 8, filters: dict[str, Any] | None = None) -> dict[str, Any]:
    result = retrieve_graph_rag(query, limit=limit, filters=filters)
    items = result["items"]

    if not items:
        return {
            "answer": "No relevant evidence was identified within the indexed corpus and search scope.",
            "sources": [],
            "graph_evidence": [],
        }

    context_parts = []
    for i, item in enumerate(items, start=1):
        context_parts.append(
            f"[VECTOR EVIDENCE {i}] paper={item.get('paper_id')} document={item.get('document_id')} "
            f"score={item.get('graph_rag_score', 0):.4f}\n{item.get('text','')}"
            f"\n[GRAPH ENTITIES] {', '.join(item.get('graph_entities', []))}"
        )

    prompt = f"""Research question:
{query}

GraphRAG evidence:
{"\n\n".join(context_parts)}

Answer using the evidence above. Cite vector evidence as [VECTOR EVIDENCE N].
Mention graph relationships only when they are supported by the supplied graph entities."""
    answer = await get_llm_provider().generate(prompt, system=SYSTEM, temperature=0.0)

    return {
        "answer": answer,
        "sources": items,
        "graph_evidence": result["graph_hits"] + result["graph_expansion"],
    }
