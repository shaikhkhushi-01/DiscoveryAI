from __future__ import annotations

from typing import Any

from app.services.knowledge_graph.neo4j import run
from app.services.trends.scoring import forecast_signal, trend_signal


def analyze_topic(topic: str) -> dict[str, Any]:
    from app.services.trends.temporal import topic_timeline
    timeline = topic_timeline(topic)
    return {
        "topic": topic,
        "timeline": timeline,
        "trend": trend_signal(timeline),
        "forecast": forecast_signal(timeline),
        "scope": "indexed_corpus",
    }


def analyze_all(limit: int = 30) -> dict[str, Any]:
    from app.services.trends.temporal import topic_trends, emerging_topics
    rows = topic_trends(limit)
    for row in rows:
        row["trend"] = trend_signal(row.get("timeline", []))
    return {
        "items": rows,
        "emerging_topics": emerging_topics(limit=min(limit, 50)),
        "scope": "indexed_corpus",
        "warning": "Trend and forecast signals depend on corpus coverage and publication-year completeness.",
    }
