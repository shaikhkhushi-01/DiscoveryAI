def test_discovery_workflow_trace():
    from unittest.mock import patch

    fake = {
        "items": [{"paper_id": 1}],
        "graph_hits": [],
        "graph_expansion": [],
    }
    with patch("app.services.agents.nodes.retrieve_graph_rag", return_value=fake),          patch("app.services.agents.nodes.score_opportunities", return_value={"items": [], "count": 0}),          patch("app.services.agents.nodes.analyze_all", return_value={"items": [], "emerging_topics": []}):
        from app.services.agents.coordinator import run_discovery_workflow
        result = run_discovery_workflow("What research gaps exist in GraphRAG?")
    agents = [x["agent"] for x in result["trace"]]
    assert agents == [
        "retrieval_agent",
        "gap_agent",
        "trend_agent",
        "research_critic",
        "report_agent",
    ]
    assert result["report"]["scope"] == "indexed_corpus"
