# Phase 4 end-to-end execution

The single-command orchestrator runs the complete live workflow in the configured backend environment:

```bash
python scripts/evaluation/run_phase4_end_to_end.py \
  --benchmark PRIVATE_ADJUDICATED_BENCHMARK.json \
  --output-dir PRIVATE_PHASE4_RUN \
  --split test \
  --code-revision FULL_GIT_COMMIT_SHA \
  --model-provider CONFIGURED_PROVIDER \
  --model-name CONFIGURED_MODEL
```

It performs, in order:

1. Read-only readiness checks for PostgreSQL, Qdrant, Neo4j, LLM and embeddings.
2. Five-system prediction generation.
3. Strict shared-record/corpus/split comparison of all five systems.
4. Six controlled ablation prediction generation.
5. Strict paired comparison of all six variants.
6. A private run summary with SHA-256 hashes, selected protocol metadata, and explicit limitations.

If readiness fails, it saves the secret-free readiness report and stops before generation. If any generation or comparison step fails, it records a failure summary and exits non-zero. It never uploads private artifacts to GitHub.

## Preconditions

- Run only in the backend environment with the actual service configuration.
- The selected benchmark split must contain compatible records already marked adjudicated; the adapters reject an empty/non-adjudicated split.
- Database, vector index and graph must represent the intended rights-cleared corpus snapshot. Non-empty counts are not sufficient proof of snapshot identity.
- Keep benchmark, predictions and reports private if required by source/data terms.
- QASPER is not a Discovery Gap benchmark and must not be passed as one.

The orchestrator is an execution convenience, not a substitute for rights review, corpus identity verification, or independent scientific validation. It does not bypass any existing fail-closed checks.
