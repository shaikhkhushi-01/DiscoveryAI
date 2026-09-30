# Days 61–70 — GraphRAG and Evidence Fusion

## Implemented

### Day 61 — Graph-aware retrieval
Graph search identifies scientific graph nodes matching query terms and links them back to papers.

### Day 62 — Graph expansion
Retrieved vector papers are expanded through Neo4j one-hop relationships to expose methods, datasets, topics, problems and other scientific entities.

### Day 63 — Evidence fusion
Vector/reranker evidence is combined with graph connectivity. The GraphRAG score uses reranked evidence, semantic similarity and a normalized graph signal.

### Day 64 — Graph entities in context
Graph entities are included alongside vector evidence before LLM generation.

### Day 65 — GraphRAG retrieval pipeline
Query → hybrid vector retrieval → reranking → graph search → graph expansion → evidence fusion.

### Day 66 — GraphRAG answer generation
LLM answers are grounded in fused vector and graph evidence with explicit evidence markers.

### Day 67 — Filter propagation
Existing year/topic/dataset filters are passed into the vector retrieval stage while graph retrieval remains corpus-scoped.

### Day 68 — API
POST /api/v1/graph-rag/retrieve and POST /api/v1/graph-rag/ask.

### Day 69 — Testing
Graph evidence fusion has unit-test coverage.

### Day 70 — Documentation
This document records the GraphRAG milestone and its runtime requirements.

## Architecture
`Query → Vector Retrieval → Reranker → Neo4j Graph Search/Expansion → Fusion → Evidence Context → LLM`

## Runtime note
Live GraphRAG requires both Qdrant and Neo4j to be populated and reachable. No live retrieval-quality score is claimed by this implementation.