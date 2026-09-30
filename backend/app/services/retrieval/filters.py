from typing import Any

def build_filters(*, year: int | None = None, topic: str | None = None, dataset: str | None = None) -> dict[str, Any]:
    return {"year": year, "topic": topic, "dataset": dataset}

def matches_metadata(payload: dict[str, Any], filters: dict[str, Any]) -> bool:
    if filters.get("year") is not None and payload.get("year") != filters["year"]:
        return False
    if filters.get("topic") and filters["topic"].lower() not in {str(x).lower() for x in payload.get("topics", [])}:
        return False
    if filters.get("dataset") and filters["dataset"].lower() not in {str(x).lower() for x in payload.get("datasets", [])}:
        return False
    return True
