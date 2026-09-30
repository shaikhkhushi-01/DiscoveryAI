from __future__ import annotations

from functools import lru_cache
from typing import Any

from neo4j import GraphDatabase

from app.core.config import settings


@lru_cache
def get_driver():
    return GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_username, settings.neo4j_password.get_secret_value()),
    )


def close_driver() -> None:
    get_driver().close()
    get_driver.cache_clear()


def run(query: str, **params: Any) -> list[dict[str, Any]]:
    with get_driver().session(database=settings.neo4j_database) as session:
        result = session.run(query, **params)
        return [record.data() for record in result]


def ensure_schema() -> None:
    statements = [
        "CREATE CONSTRAINT paper_id IF NOT EXISTS FOR (n:Paper) REQUIRE n.id IS UNIQUE",
        "CREATE CONSTRAINT author_key IF NOT EXISTS FOR (n:Author) REQUIRE n.key IS UNIQUE",
        "CREATE CONSTRAINT institution_key IF NOT EXISTS FOR (n:Institution) REQUIRE n.key IS UNIQUE",
        "CREATE CONSTRAINT dataset_key IF NOT EXISTS FOR (n:Dataset) REQUIRE n.key IS UNIQUE",
        "CREATE CONSTRAINT method_key IF NOT EXISTS FOR (n:Method) REQUIRE n.key IS UNIQUE",
        "CREATE CONSTRAINT topic_key IF NOT EXISTS FOR (n:Topic) REQUIRE n.key IS UNIQUE",
        "CREATE CONSTRAINT problem_key IF NOT EXISTS FOR (n:Problem) REQUIRE n.key IS UNIQUE",
        "CREATE CONSTRAINT application_key IF NOT EXISTS FOR (n:Application) REQUIRE n.key IS UNIQUE",
        "CREATE CONSTRAINT metric_key IF NOT EXISTS FOR (n:Metric) REQUIRE n.key IS UNIQUE",
        "CREATE CONSTRAINT gap_key IF NOT EXISTS FOR (n:ResearchGap) REQUIRE n.key IS UNIQUE",
        "CREATE CONSTRAINT hypothesis_key IF NOT EXISTS FOR (n:Hypothesis) REQUIRE n.key IS UNIQUE",
        "CREATE CONSTRAINT experiment_key IF NOT EXISTS FOR (n:Experiment) REQUIRE n.key IS UNIQUE",
    ]
    for statement in statements:
        run(statement)
