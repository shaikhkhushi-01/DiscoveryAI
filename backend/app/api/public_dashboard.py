from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.services.gap_detection.engine import detect_gaps
from app.services.graph_rag.pipeline import retrieve_graph_rag
from app.services.knowledge_graph.neo4j import run
from app.services.trends.engine import analyze_all

router = APIRouter(prefix="/api/v1/public", tags=["public-dashboard"])


@router.get("/overview")
def overview() -> dict[str, Any]:
    rows = run(
        "MATCH (n) WITH labels(n)[0] AS label, count(n) AS count "
        "RETURN label, count ORDER BY count DESC"
    )
    relationships = run("MATCH ()-[r]->() RETURN count(r) AS count")
    counts = {str(row["label"]): int(row["count"]) for row in rows if row.get("label")}
    return {
        "source": "neo4j",
        "papers_indexed": counts.get("Paper", 0),
        "concepts": sum(v for k, v in counts.items() if k != "Paper"),
        "evidence_links": int(relationships[0]["count"]) if relationships else 0,
        "node_counts": counts,
    }


@router.get("/gaps")
def public_gaps(limit: int = Query(20, ge=1, le=50)):
    return detect_gaps(limit=limit)


@router.get("/trends")
def public_trends(limit: int = Query(30, ge=1, le=50)):
    return analyze_all(limit)


class GraphRAGRequest(BaseModel):
    query: str = Field(min_length=2, max_length=2000)
    limit: int = Field(default=8, ge=1, le=20)
    year: int | None = Field(default=None, ge=1900, le=2100)
    topic: str | None = None
    dataset: str | None = None


@router.post("/graph-rag/retrieve")
def public_graph_rag(payload: GraphRAGRequest):
    filters = {"year": payload.year, "topic": payload.topic, "dataset": payload.dataset}
    return retrieve_graph_rag(payload.query, limit=payload.limit, filters=filters)
