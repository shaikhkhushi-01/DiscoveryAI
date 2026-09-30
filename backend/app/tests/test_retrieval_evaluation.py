from app.services.retrieval.evaluation import ndcg_at_k, recall_at_k, reciprocal_rank

def test_recall_at_k():
    assert recall_at_k(["a", "b", "c"], {"b", "c"}, 2) == 0.5

def test_mrr():
    assert reciprocal_rank(["x", "b"], {"b"}) == 0.5
    assert reciprocal_rank(["x"], {"b"}) == 0.0

def test_ndcg():
    score = ndcg_at_k(["b", "a"], {"a": 2, "b": 1}, 2)
    assert 0.0 < score < 1.0
