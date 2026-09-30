# Retrieval Evaluation Protocol — DiscoveryAI

## Scope
Evaluate semantic retrieval, hybrid retrieval, and reranking using expert-annotated scientific queries.

## Metrics
- Recall@K: fraction of relevant evidence retrieved in the top K.
- MRR: reciprocal rank of the first relevant result.
- nDCG@K: graded ranking quality using relevance judgments.

## Required baselines
1. Keyword-only retrieval
2. Dense semantic retrieval
3. Hybrid keyword + dense retrieval
4. Hybrid + reranker

## Evaluation set
Each query must have explicit relevant document/chunk IDs and, for nDCG, graded relevance labels.

## Reporting
Report aggregate metrics with the number of queries, K values, confidence intervals where appropriate, and error analysis. Never fabricate scores when the gold set is empty or incomplete.

## Retrieval limitations
Metrics measure performance against the indexed corpus and annotation set; they do not establish that a research topic is globally unexplored.
