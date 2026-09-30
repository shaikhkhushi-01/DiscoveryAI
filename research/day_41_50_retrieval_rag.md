# Days 41–50 — Embeddings, Retrieval and RAG V1

## Implemented

### Day 41 — Embedding architecture
- Provider-neutral EmbeddingProvider interface.
- Sentence Transformers implementation.
- Configurable model and vector dimension.

### Day 42 — Sentence Transformers
- Default model: sentence-transformers/all-MiniLM-L6-v2.
- Normalized dense vectors.
- Embedding provider factory.
- Evaluation protocol requires query/document relevance judgments; no fabricated quality scores.

### Day 43 — Qdrant
- Qdrant client and collection creation.
- Cosine-distance vectors.
- Configurable collection name.
- Deterministic point IDs.

### Day 44 — Scientific chunk indexing
- Section-aware chunks are indexed.
- Payload contains document ID, paper ID, section, year, topics, datasets and source text.
- Extraction metadata is reused during indexing.

### Day 45 — Semantic search
- Authenticated semantic search endpoint.
- Query embedding to Qdrant top-K retrieval.

### Day 46 — Metadata filtering
- Year filtering.
- Topic filtering.
- Dataset filtering.

### Day 47 — Hybrid retrieval
- Keyword retrieval from PostgreSQL.
- Dense retrieval from Qdrant.
- Score fusion: 0.75 semantic + 0.25 keyword.

### Day 48 — Reranking
- Cross-encoder reranker with configurable model.
- Graceful fallback to hybrid score if reranker model is unavailable.

### Day 49 — Retrieval evaluation
- Recall@K.
- MRR.
- nDCG@K.
- Gold-set template and evaluation protocol.
- Metrics must not be reported until expert relevance judgments exist.

### Day 50 — RAG V1
Pipeline: query → hybrid retrieval → reranking → context construction → LLM → source attribution.
The RAG system explicitly instructs the model to ground literature claims in supplied evidence and to state when no relevant evidence was identified within the indexed corpus/search scope.

## APIs
- GET /api/v1/search/semantic
- POST /api/v1/search/index/{document_id}
- POST /api/v1/rag/ask

## Runtime requirement
Qdrant and the embedding model must be available to execute semantic retrieval. Live retrieval quality metrics require a populated scientific gold set.

## Milestone 4
DiscoveryAI now has the software path for evidence-based semantic retrieval and RAG V1. Live retrieval quality is an empirical question and must be established with the documented evaluation protocol.