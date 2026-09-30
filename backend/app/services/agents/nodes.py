from __future__ import annotations
from typing import Any

from app.services.agents.state import DiscoveryState
from app.services.evidence.engine import score_opportunities
from app.services.graph_rag.pipeline import retrieve_graph_rag
from app.services.trends.engine import analyze_all


def _record(state: DiscoveryState, agent: str, status: str, data: dict[str, Any] | None = None) -> None:
    state.trace.append({"agent": agent, "status": status, "data": data or {}})


def retrieval_agent(state: DiscoveryState) -> DiscoveryState:
    state.retrieval = retrieve_graph_rag(state.question, limit=8)
    _record(state, "retrieval_agent", "completed", {"items": len(state.retrieval.get("items", []))})
    return state


def gap_agent(state: DiscoveryState) -> DiscoveryState:
    state.gaps = score_opportunities(limit=10)
    _record(state, "gap_agent", "completed", {"items": state.gaps.get("count", 0)})
    return state


def evidence_agent(state: DiscoveryState) -> DiscoveryState:
    state.evidence = {
        "items": state.gaps.get("items", []),
        "validated_count": sum(
            1 for item in state.gaps.get("items", [])
            if item.get("evidence_status") == "evidence_supported"
        ),
        "review_count": sum(
            1 for item in state.gaps.get("items", [])
            if item.get("evidence_status") == "contradicted_or_needs_review"
        ),
    }
    _record(state, "evidence_validator", "completed", {
        "validated": state.evidence["validated_count"],
        "review": state.evidence["review_count"],
    })
    return state


def trend_agent(state: DiscoveryState) -> DiscoveryState:
    state.trends = analyze_all(limit=20)
    _record(state, "trend_agent", "completed", {"items": len(state.trends.get("items", []))})
    return state


def critic_agent(state: DiscoveryState) -> DiscoveryState:
    items = state.gaps.get("items", [])
    issues = []
    for item in items:
        if item.get("evidence_status") in {"contradicted_or_needs_review", "insufficient_evidence"}:
            issues.append({
                "title": item.get("title"),
                "issue": item.get("evidence_status"),
            })
    state.critique = {
        "issues": issues,
        "passed": len(issues) == 0,
        "rule": "No candidate is treated as globally novel solely because retrieval is sparse.",
    }
    _record(state, "research_critic", "completed", {"issues": len(issues)})
    return state


def report_agent(state: DiscoveryState) -> DiscoveryState:
    opportunities = state.gaps.get("items", [])[:5]
    state.report = {
        "question": state.question,
        "opportunities": opportunities,
        "trend_signals": state.trends.get("emerging_topics", [])[:10],
        "evidence_count": len(state.retrieval.get("items", [])),
        "critic": state.critique,
        "evidence_validation": state.evidence,
        "scope": "indexed_corpus",
    }
    _record(state, "report_agent", "completed", {"opportunities": len(opportunities)})
    return state
