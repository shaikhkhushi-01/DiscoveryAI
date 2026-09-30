from unittest.mock import patch

def test_mapper_key_is_deterministic():
    from app.services.knowledge_graph.mapper import key
    assert key("Graph RAG") == key(" Graph   RAG ")

def test_graph_payload_maps_entities():
    from app.services.knowledge_graph.mapper import build_graph_payload
    payload = build_graph_payload(7, {"title": "Test Paper", "year": 2025, "entities": {"topics": ["RAG"], "methods": ["GraphRAG"], "datasets": []}})
    assert payload["document_id"] == 7
    assert payload["topics"] == ["RAG"]
    assert payload["methods"] == ["GraphRAG"]

@patch("app.services.knowledge_graph.ingest.ensure_schema")
@patch("app.services.knowledge_graph.ingest.run")
def test_graph_ingest_creates_paper(mock_run, mock_schema):
    from app.services.knowledge_graph.ingest import index_extraction
    result = index_extraction(3, {"title": "Paper", "year": 2025, "entities": {}})
    assert result["document_id"] == 3
    mock_schema.assert_called_once()
    assert mock_run.call_count >= 1
