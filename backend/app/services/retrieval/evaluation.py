from __future__ import annotations

import math
from typing import Iterable

def recall_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    if not relevant:
        return 0.0
    return len(set(retrieved[:k]) & relevant) / len(relevant)

def reciprocal_rank(retrieved: list[str], relevant: set[str]) -> float:
    for rank, item in enumerate(retrieved, start=1):
        if item in relevant:
            return 1.0 / rank
    return 0.0

def ndcg_at_k(retrieved: list[str], relevance: dict[str, float], k: int) -> float:
    def dcg(values: Iterable[float]) -> float:
        return sum((2**v - 1) / math.log2(i + 2) for i, v in enumerate(values))
    actual = [relevance.get(item, 0.0) for item in retrieved[:k]]
    ideal = sorted(relevance.values(), reverse=True)[:k]
    denominator = dcg(ideal)
    return dcg(actual) / denominator if denominator else 0.0
