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
        MATCH (p:Paper)-[:USES_METHOD]->(m:Method)
        MATCH (p)-[:USES_DATASET]->(d:Dataset)
        WITH m, collect(DISTINCT d.name) AS datasets, count(DISTINCT p) AS papers
        WHERE papers > 0 AND size(datasets) = 1
        RETURN m.name AS method, datasets[0] AS observed_dataset, papers
        ORDER BY papers DESC
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
            "description": f"Indexed evidence shows {row.get('method')} evaluated with {row.get('observed_dataset')} but no second dataset was identified in this graph query.",
            "evidence_count": row.get("papers", 0),
            "source": "neo4j_graph",
            "confidence": 0.45,
        })
    return candidates[:limit]
