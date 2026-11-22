# Day 4 — Controlled ablation prediction generation

**Status:** implementation added; awaiting CI validation. No benchmark predictions or scientific results are claimed.

## Component switch contract

The generator `scripts/evaluation/generate_discovery_gap_ablations.py` executes six independent configurations through `backend/app/services/evaluation/ablation_prediction_adapters.py`:

| Variant | Vector | Graph | Research critic | Temporal | Discovery score |
|---|---:|---:|---:|---:|---:|
| full | on | on | on | on | on |
| without_vector_retrieval | off | on | on | on | on |
| without_graph_retrieval | on | off | on | on | on |
| without_research_critic | on | on | off | on | on |
| without_temporal_signals | on | on | on | off | on |
| without_discovery_score | on | on | on | on | off |

The retrieval switches select different executed paths. Vector-off uses graph search/expansion without calling hybrid/vector retrieval. Graph-off uses hybrid/vector retrieval and reranking without calling GraphRAG. Critic, temporal and scoring calls are separately gated. The critic accepts the current variant's retrieved evidence so it does not silently reintroduce the removed retrieval path.

**Important limitation:** the current graph-only search returns graph metadata, not guaranteed document/chunk text. Such rows are not promoted into traceable benchmark evidence. If there are no traceable chunks, the model output is forced to inconclusive with zero ratings and no citations. This is a conservative limitation, not a claim that graph-only retrieval has no value.

## Generate artifacts

Only use a locally held, rights-cleared frozen benchmark with adjudicated labels. Keep raw prediction files private where required by corpus licences.

```bash
python scripts/evaluation/generate_discovery_gap_ablations.py \
  --benchmark PATH_TO_ADJUDICATED_BENCHMARK.json \
  --output-dir PRIVATE_ABLATION_OUTPUT_DIR \
  --split test \
  --evidence-budget 8 \
  --code-revision FROZEN_GIT_COMMIT \
  --model-provider PROVIDER_NAME \
  --model-name MODEL_VERSION \
  --prompt-version ablation-prompt-v1 \
  --embedding-model EMBEDDING_MODEL_VERSION \
  --retrieval-config "top_k=8;reranker=repository-default"
```

The command fails closed when the selected split has no adjudicated records. It creates one prediction JSON per variant, each with `ablation_id`, exact `disabled_components`, `enabled_components`, shared benchmark/corpus/model metadata and evidence budget. The generator does not create gold labels.

Compare only after all six independently generated artifacts exist:

```bash
python scripts/evaluation/run_discovery_gap_ablations.py \
  --benchmark PATH_TO_ADJUDICATED_BENCHMARK.json \
  --split test \
  --full PRIVATE_ABLATION_OUTPUT_DIR/full.predictions.json \
  --without-vector-retrieval PRIVATE_ABLATION_OUTPUT_DIR/without_vector_retrieval.predictions.json \
  --without-graph-retrieval PRIVATE_ABLATION_OUTPUT_DIR/without_graph_retrieval.predictions.json \
  --without-research-critic PRIVATE_ABLATION_OUTPUT_DIR/without_research_critic.predictions.json \
  --without-temporal-signals PRIVATE_ABLATION_OUTPUT_DIR/without_temporal_signals.predictions.json \
  --without-discovery-score PRIVATE_ABLATION_OUTPUT_DIR/without_discovery_score.predictions.json \
  --output PRIVATE_ABLATION_OUTPUT_DIR/ablation-report.json
```

## Validation and limits

Unit tests assert that disabled component calls are skipped and retrieval modes differ. CLI help is smoke-tested in CI. These tests do not verify live Qdrant/Neo4j/provider connectivity, full system parity, statistical power, or scientific efficacy.

Before scored experiments, Day 2 corpus eligibility/rights/version review/freeze and Day 3 independent human annotation/adjudication gates must pass. Use the locked test split only once under the pre-registered protocol. Record failed runs and never tune against test gold labels.
