# Phase 4 — Five-system integration hardening

**Status:** adapter contract hardening implemented; CI and live integration are pending. This document does not claim generated benchmark predictions or scientific results.

## Systems

The generator dispatches the same selected, adjudicated benchmark records to five named systems:

1. `llm_only` — closed-book control, with no retrieval access.
2. `vector_rag` — vector retrieval.
3. `graph_rag` — the repository's GraphRAG retrieval pipeline.
4. `hybrid_retrieval` — hybrid search plus configured reranking.
5. `discoveryai_full` — current literature-synthesis pipeline.

All systems share the same structured prediction schema and evidence-ID allowlisting. The closed-book arm is explicitly constrained to `inconclusive`, zero corpus-bounded ratings, and no citations: without a corpus it cannot establish whether a gap is supported or contradicted within that corpus. Any retrieval arm with no traceable non-empty text evidence is also forced to that conservative output.

## Generation

Run from the repository root after configuring the existing backend database, Qdrant, embedding, and LLM settings:

```bash
python scripts/evaluation/generate_discovery_gap_baselines.py \
  --benchmark PATH_TO_ADJUDICATED_BENCHMARK.json \
  --output-dir PRIVATE_BASELINE_OUTPUT_DIR \
  --split validation \
  --evidence-budget 8 \
  --code-revision FROZEN_GIT_COMMIT \
  --model-provider CONFIGURED_PROVIDER \
  --model-name CONFIGURED_MODEL
```

The generator fails closed when the selected split has no adjudicated records. It generates all five systems before replacing output artifacts, so a failed arm does not leave a newly written partial set. Each artifact includes run metadata and predictions. Keep outputs private when source data or benchmark terms require it.

## Validation gates and limitations

- CI contract tests validate dispatch, evidence allowlisting, empty-text rejection, empty-retrieval behavior, and malformed provider output. Passing unit tests does not prove live service connectivity.
- The vector, graph, hybrid, and synthesis paths still require a configured indexed corpus and live Qdrant/Neo4j/database/provider integration.
- The five systems are not necessarily perfectly compute-equivalent: their retrieval and synthesis pipelines differ. Record actual model/provider, embedding model, retrieval settings, code revision, corpus snapshot, and runtime for every run.
- `llm_only` is a closed-book negative/control arm, not a comparable evidence-grounded system; its conservative zero/inconclusive output is intentional.
- `graph_rag` uses the existing GraphRAG pipeline, which itself fuses vector/hybrid and graph results. It must not be described as graph-only.
- `discoveryai_full` reuses the current literature-synthesis service; it is not proof that every product feature/critic/temporal component is active.
- QASPER is a scientific-paper question-answering/evidence benchmark, not a gold benchmark for research-gap discovery. Do not score Discovery Gap metrics against QASPER answers.
- No predictions, baseline scores, ablation effects, or research conclusions are claimed by this implementation.

## Next acceptance checks

1. Backend CI passes on the integration PR.
2. A private, rights-cleared, frozen and schema-compatible adjudicated benchmark exists for the Discovery Gap task. QASPER alone does not satisfy this requirement.
3. All required backend services are live and configured; generate all five artifacts with matching record coverage and auditable metadata.
4. Validate artifacts with the existing comparison runner before reporting any metrics.
5. Preserve failed runs and disclose missing services, empty retrieval, and system-specific limitations.
