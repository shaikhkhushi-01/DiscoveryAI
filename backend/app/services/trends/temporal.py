from __future__ import annotations

from typing import Any

from app.services.knowledge_graph.neo4j import run


def topic_timeline(topic: str, limit: int = 20) -> list[dict[str, Any]]:
    return run(
        """
        MATCH (p:Paper)-[:HAS_TOPIC]->(t:Topic)
        WHERE toLower(t.name) = toLower($topic) AND p.year IS NOT NULL
        RETURN p.year AS year, count(DISTINCT p) AS paper_count
        ORDER BY year ASC
        LIMIT $limit
        """,
        topic=topic,
        limit=max(1, min(limit, 100)),
    )


def topic_trends(limit: int = 50) -> list[dict[str, Any]]:
    return run(
        """
        MATCH (p:Paper)-[:HAS_TOPIC]->(t:Topic)
        WHERE p.year IS NOT NULL
        WITH t.name AS topic, p.year AS year, count(DISTINCT p) AS papers
        WITH topic, collect({year: year, papers: papers}) AS timeline,
             min(year) AS first_year, max(year) AS last_year
        WITH topic, timeline, first_year, last_year,
             reduce(total = 0, x IN timeline | total + x.papers) AS total_papers
        RETURN topic, first_year, last_year, total_papers, timeline
        ORDER BY total_papers DESC
        LIMIT $limit
        """,
        limit=max(1, min(limit, 200)),
    )


def emerging_topics(limit: int = 30) -> list[dict[str, Any]]:
    return run(
        """
        MATCH (p:Paper)-[:HAS_TOPIC]->(t:Topic)
        WHERE p.year IS NOT NULL
        WITH t.name AS topic, p.year AS year, count(DISTINCT p) AS papers
        WITH topic,
             sum(CASE WHEN year >= date().year - 2 THEN papers ELSE 0 END) AS recent,
             sum(CASE WHEN year >= date().year - 5 AND year < date().year - 2 THEN papers ELSE 0 END) AS prior
        WHERE recent > 0
        RETURN topic, recent, prior,
               CASE WHEN prior = 0 THEN 1.0 ELSE toFloat(recent - prior) / prior END AS growth
        ORDER BY growth DESC, recent DESC
        LIMIT $limit
        """,
        limit=max(1, min(limit, 100)),
    )
