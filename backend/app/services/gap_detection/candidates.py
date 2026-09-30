from __future__ import annotations

from collections import defaultdict
from typing import Any

from app.services.knowledge_graph.neo4j import run
from app.services.gap_detection.types import GapType


def _graph_candidates(limit: int = 50) -> list[dict[str, Any]]:
    return run(
        """
        MATCH (t:Topic)
        OPTIONAL MATCH (p:Paper)-[:HAS_TOPIC]->(t)
        WITH t, count(DISTINCT p) AS papers
        WHERE papers > 0 AND papers <= 3
        RETURN t.name AS topic, papers
        ORDER BY papers ASC
        LIMIT $limit
        """,
        limit=max(1, min(limit, 200)),
    )


def _missing_experiments(limit: int = 50) -> list[dict[str, Any]]:
    return run(
        """
        MATCH (m:Method)
        MATCH (d:Dataset)
        OPTIONAL MATCH (p:Paper)-[:USES_METHOD]->(m)-[:USES_DATASET]->(d)
        WITH m, d, count(DISTINCT p) AS observed
        WITH m, collect({dataset:d.name, observed:observed}) AS coverage
        WHERE size([x IN coverage WHERE x.observed > 0]) = 1
        RETURN m.name AS method,
               [x IN coverage WHERE x.observed > 0][0].dataset AS observed_dataset,
               [x IN coverage WHERE x.observed = 0 | x.dataset][0..5] AS candidate_missing_datasets
        LIMIT $limit
        """,
        limit=max(1, min(limit, 200)),
    )


def generate_graph_candidates(limit: int = 50) -> list[dict[str, Any]]:
    candidates = []
    for row in _graph_candidates(limit):
        candidates.append({
            "gap_type": GapType.UNDEREXPLORED_TOPIC.value,
            "title": f"Underexplored topic: {row.get('topic')}",
            "description": f"The indexed graph contains {row.get('papers', 0)} paper(s) connected to this topic.",
            "evidence_count": row.get("papers", 0),
            "source": "neo4j_graph",
            "confidence": min(0.9, 0.25 + 0.1 * row.get("papers", 0)),
        })
    for row in _missing_experiments(limit):
        candidates.append({
            "gap_type": GapType.MISSING_EXPERIMENT.value,
            "title": f"Method-dataset coverage gap: {row.get('method')}",
            "description": f"Indexed evidence shows {row.get('method')} associated with {row.get('observed_dataset')}; candidate missing datasets from the indexed graph include {row.get('candidate_missing_datasets', [])}.",
            "evidence_count": row.get("papers", 0),
            "source": "neo4j_graph",
            "confidence": 0.45,
        })
    return candidates[:limit]
