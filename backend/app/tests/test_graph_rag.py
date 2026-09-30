from app.services.graph_rag.fusion import fuse

def test_graph_fusion_adds_graph_signal():
    items = fuse(
        [{"paper_id": 1, "document_id": 4, "text": "evidence", "semantic_score": .8, "rerank_score": .9}],
        [
            {"paper_id": 1, "node_name": "RAG"},
            {"paper_id": 1, "node_name": "GraphRAG"},
            {"paper_id": 1, "node_name": "Benchmark"},
        ],
        limit=5,
    )
    assert items[0]["paper_id"] == 1
    assert items[0]["graph_score"] > 0
    assert "RAG" in items[0]["graph_entities"]
