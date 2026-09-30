from __future__ import annotations

from app.services.agents.nodes import (
    critic_agent,
    gap_agent,
    report_agent,
    retrieval_agent,
    trend_agent,
)
from app.services.agents.state import DiscoveryState


def run_discovery_workflow(question: str) -> dict:
    state = DiscoveryState(question=question)
    for node in (retrieval_agent, gap_agent, trend_agent, critic_agent, report_agent):
        state = node(state)
    return {
        "question": state.question,
        "report": state.report,
        "trace": state.trace,
        "retrieval": state.retrieval,
        "gaps": state.gaps,
        "trends": state.trends,
        "critique": state.critique,
    }
