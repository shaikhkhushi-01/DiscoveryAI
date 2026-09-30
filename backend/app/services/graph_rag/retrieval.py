from __future__ import annotations

import re
from typing import Any

from app.services.knowledge_graph.neo4j import run


def _terms(query: str) -> list[str]:
    return list(dict.fromkeys(
        x for x in re.findall(r"[A-Za-z0-9][A-Za-z0-9_-]+", query.lower())
        if len(x) > 2
    ))[:12]


def graph_search(query: str, limit: int = 12) -> list[dict[str, Any]]:
    terms = _terms(query)
    if not terms:
        return []

    rows = run(
        """
        MATCH (n)
        WHERE any(term IN $terms WHERE
            (n.name IS NOT NULL AND toLower(n.name) CONTAINS term) OR
            (n.title IS NOT NULL AND toLower(n.title) CONTAINS term))
        OPTIONAL MATCH (p:Paper)-[r]-(n)
        WITH n, p, r,
             size([term IN $terms WHERE
                 (n.name IS NOT NULL AND toLower(n.name) CONTAINS term) OR
                 (n.title IS NOT NULL AND toLower(n.title) CONTAINS term)]) AS matches
        RETURN labels(n) AS node_labels,
               n.name AS node_name,
               n.title AS node_title,
               p.id AS paper_id,
               p.title AS paper_title,
               type(r) AS relationship,
               matches
        ORDER BY matches DESC
        LIMIT $limit
        """,
        terms=terms,
        limit=max(1, min(limit, 100)),
    )
    return rows


def graph_expand(paper_ids: list[int], limit: int = 30) -> list[dict[str, Any]]:
    if not paper_ids:
        return []
    return run(
        """
        MATCH (p:Paper)-[r]-(n)
        WHERE p.id IN $paper_ids
        RETURN p.id AS paper_id, p.title AS paper_title,
               labels(n) AS node_labels, n.name AS node_name,
               type(r) AS relationship
        LIMIT $limit
        """,
        paper_ids=paper_ids,
        limit=max(1, min(limit, 200)),
    )
