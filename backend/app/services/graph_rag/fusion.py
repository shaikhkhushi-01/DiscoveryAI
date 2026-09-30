from __future__ import annotations

from collections import defaultdict
from typing import Any


def fuse(vector_items: list[dict[str, Any]], graph_items: list[dict[str, Any]], limit: int = 10) -> list[dict[str, Any]]:
    grouped: dict[int, dict[str, Any]] = defaultdict(dict)

    for item in vector_items:
        paper_id = item.get("paper_id")
        if paper_id is None:
            continue
        grouped[paper_id].update({
            "paper_id": paper_id,
            "document_id": item.get("document_id"),
            "title": item.get("title") or item.get("paper_title"),
            "text": item.get("text", ""),
            "semantic_score": float(item.get("semantic_score", item.get("score", 0.0))),
            "keyword_score": float(item.get("keyword_score", 0.0)),
            "rerank_score": float(item.get("rerank_score", 0.0)),
        })

    graph_counts: dict[int, int] = defaultdict(int)
    graph_names: dict[int, list[str]] = defaultdict(list)
    for item in graph_items:
        pid = item.get("paper_id")
        if pid is not None:
            graph_counts[pid] += 1
            name = item.get("node_name") or item.get("node_title")
            if name and name not in graph_names[pid]:
                graph_names[pid].append(name)

    for pid, item in grouped.items():
        item["graph_score"] = min(1.0, graph_counts[pid] / 5.0)
        item["graph_entities"] = graph_names[pid][:10]
        item["graph_rag_score"] = (
            0.55 * item["rerank_score"]
            + 0.25 * item["semantic_score"]
            + 0.20 * item["graph_score"]
        )

    return sorted(grouped.values(), key=lambda x: x["graph_rag_score"], reverse=True)[:limit]
