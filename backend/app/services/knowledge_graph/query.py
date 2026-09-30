from __future__ import annotations

from typing import Any

from app.services.knowledge_graph.neo4j import run


def paper_neighborhood(paper_id: int, limit: int = 50) -> list[dict[str, Any]]:
    return run(
        """
        MATCH (p:Paper {id:$paper_id})-[r]-(n)
        RETURN labels(n) AS labels, n.name AS name, n.title AS title,
               type(r) AS relationship
        LIMIT $limit
        """,
        paper_id=paper_id, limit=max(1, min(limit, 200)),
    )


def related_topics(topic: str, limit: int = 20) -> list[dict[str, Any]]:
    return run(
        """
        MATCH (t:Topic)
        WHERE toLower(t.name)=toLower($topic)
        MATCH (p:Paper)-[:HAS_TOPIC]->(t)
        OPTIONAL MATCH (p)-[:HAS_TOPIC]->(related:Topic)
        WHERE related <> t
        RETURN related.name AS topic, count(p) AS paper_count
        ORDER BY paper_count DESC
        LIMIT $limit
        """,
        topic=topic, limit=max(1, min(limit, 100)),
    )


def graph_overview(limit: int = 100) -> dict[str, Any]:
    nodes = run(
        "MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count ORDER BY count DESC"
    )
    relationships = run(
        "MATCH ()-[r]->() RETURN type(r) AS relationship, count(r) AS count ORDER BY count DESC LIMIT $limit",
        limit=max(1, min(limit, 100)),
    )
    return {"nodes": nodes, "relationships": relationships}
