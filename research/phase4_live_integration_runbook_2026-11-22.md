# Phase 4 — Five-system integration and live preflight

**Engineering status:** five baseline adapters and six controlled ablation adapters are implemented and CI-tested. This is not a claim that live integrations or benchmark experiments have run.

## Read-only live dependency preflight

From the repository root, activate the backend environment and run:

```bash
python scripts/evaluation/check_phase4_readiness.py
```

The command independently checks:
- PostgreSQL connectivity and aggregate paper/document counts.
- The configured Qdrant collection and exact point count.
- Neo4j connectivity plus paper-node, node, and relationship counts.
- The selected LLM provider configuration (Ollama endpoint reachability, or presence—not validity—of Gemini/OpenAI credentials).
- The embedding provider package/configuration.

It emits no credentials or paper text, makes no schema/index changes, and does not send generation or embedding requests. A non-zero exit means one or more prerequisites are blocked. Use `--allow-blocked` to print the report without a failing exit code.

**Important:** a ready preflight means dependencies and non-empty indexes are reachable; it does not prove the indexes contain the intended frozen corpus, does not generate predictions, and does not validate research quality.

## Generate five Discovery Gap systems

Only run after a private, rights-cleared, frozen corpus and a compatible adjudicated DiscoveryGapBench are available:

```bash
python scripts/evaluation/generate_discovery_gap_baselines.py \
  --benchmark PRIVATE_ADJUDICATED_BENCHMARK.json \
  --output-dir PRIVATE_BASELINE_OUTPUT_DIR \
  --split validation --evidence-budget 8 \
  --code-revision FULL_GIT_COMMIT_SHA \
  --model-provider CONFIGURED_PROVIDER --model-name CONFIGURED_MODEL
```

The five systems are `llm_only`, `vector_rag`, `graph_rag`, `hybrid_retrieval`, and `discoveryai_full`. Note that `graph_rag` is the repository's fused GraphRAG pipeline, not a graph-only baseline. The closed-book `llm_only` arm is deliberately inconclusive with zero corpus ratings and no citations.

## Generate six ablations

```bash
python scripts/evaluation/generate_discovery_gap_ablations.py \
  --benchmark PRIVATE_ADJUDICATED_BENCHMARK.json \
  --output-dir PRIVATE_ABLATION_OUTPUT_DIR \
  --split validation --evidence-budget 8 \
  --code-revision FULL_GIT_COMMIT_SHA \
  --model-provider CONFIGURED_PROVIDER --model-name CONFIGURED_MODEL
```

The six variants execute the declared retrieval/component switches. The graph-only retrieval arm may return graph metadata without traceable chunk text; such records correctly fail closed as inconclusive.

## Current scientific boundary

QASPER is a scientific-paper question-answering/evidence benchmark, not a research-gap gold benchmark. It cannot be substituted for DiscoveryGapBench or used to claim research-gap accuracy. The current student-project track has explicitly deferred independent human annotation; therefore no independently adjudicated gap labels or valid scored gap experiment can be claimed. Any automated/proxy evaluation must be labelled separately and must not be presented as expert-validated discovery performance.

## Exit gates still required for a scientific Phase 4 closeout

1. Run the preflight in the actual backend environment and preserve its secret-free JSON report.
2. Verify that database, Qdrant, and Neo4j contain the same intended, rights-cleared corpus snapshot; non-zero counts alone are insufficient.
3. Supply a compatible benchmark with lawful corpus provenance and a clearly described automated or independently adjudicated reference standard.
4. Generate all five baseline artifacts and all six ablation artifacts on the same frozen records, corpus, split, model/provider, and configuration.
5. Validate every artifact with the comparison/ablation runners; package hashes and metadata; report errors and limitations.
6. Do not claim expert validation or causal component effects without the corresponding study design and evidence.
