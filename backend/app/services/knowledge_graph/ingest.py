from __future__ import annotations

from typing import Any

from app.services.knowledge_graph.mapper import build_graph_payload, key
from app.services.knowledge_graph.neo4j import ensure_schema, run


def _merge_many(label: str, values: list[str], relation: str, paper_id: int) -> int:
    count = 0
    for value in values:
        run(
            f"""
            MATCH (p:Paper {{id: $paper_id}})
            MERGE (n:{label} {{key: $key}})
            ON CREATE SET n.name = $name
            MERGE (p)-[:{relation}]->(n)
            """,
            paper_id=paper_id, key=key(value), name=value,
        )
        count += 1
    return count


def index_extraction(document_id: int, extraction: dict[str, Any]) -> dict[str, Any]:
    ensure_schema()
    payload = build_graph_payload(document_id, extraction)
    run(
        """
        MERGE (p:Paper {id: $paper_id})
        SET p.title=$title, p.year=$year, p.doi=$doi
        """,
        paper_id=document_id, title=payload["title"], year=payload["year"], doi=payload["doi"],
    )
    totals = {"Paper": 1}
    for field, label, relation in [
        ("authors", "Author", "AUTHORED_BY"),
        ("institutions", "Institution", "AFFILIATED_WITH"),
        ("datasets", "Dataset", "USES_DATASET"),
        ("methods", "Method", "USES_METHOD"),
        ("topics", "Topic", "HAS_TOPIC"),
        ("problems", "Problem", "ADDRESSES"),
        ("applications", "Application", "APPLIED_TO"),
        ("metrics", "Metric", "USES_METRIC"),
    ]:
        n = _merge_many(label, payload[field], relation, document_id)
        totals[label] = n
    return {"document_id": document_id, "indexed": totals}
