# Day 4 — Baseline systems and experiment infrastructure

**Date:** 2026-11-20  
**Status:** protocol and execution controls; no benchmark run or result is claimed.  
**Scope:** NLP and language-model research only.

## 1. Objective

Prepare a reproducible, fair comparison of five systems for corpus-bounded NLP research-gap assessment. Day 4 first establishes the execution contract and validates the run artifacts. Actual benchmark scoring is gated on a frozen, rights-cleared corpus and an adjudicated benchmark with a locked test split.

## 2. Systems under comparison

The repository evaluator requires exactly these system identifiers:

1. `llm_only`
2. `vector_rag`
3. `graph_rag`
4. `hybrid_retrieval`
5. `discoveryai_full`

The evaluator compares the same benchmark ID/version, annotation-rubric version, corpus snapshot IDs, split and record IDs. Every prediction artifact must include `run_metadata.system_id` matching its system identifier.

## 3. Fairness and execution controls

Before any scored run, freeze and record:

- Benchmark version, schema version, adjudication status and SHA-256.
- Corpus manifest version, snapshot ID and SHA-256; exact permitted input materials.
- Exact question/record IDs and split; work/version-family leakage checks.
- Model provider/name/version, decoding parameters, prompt version and system commit.
- Embedding model/version, vector index snapshot, graph snapshot, retrieval/reranking configuration.
- Shared maximum evidence-item budget (default evaluator value: 8); additionally report token counts and latency because equal item counts do not equalize token or compute cost.
- Random seeds where supported, environment/dependency lock, timestamps, retries and failed runs.
- Cost/usage where available, without putting secrets or private text into public logs.

Run all systems against identical inputs. No system may see gold labels, adjudication notes, locked-test answers, or reviewer identities during prediction generation. Do not tune prompts, thresholds, retrieval parameters or model selection on the locked test split.

## 4. Required prediction artifacts

For each system, produce a separate JSON prediction artifact conforming to the DiscoveryGapBench prediction schema. Include unique record IDs, predictions, evidence references and run metadata. Validate every artifact before scoring. Preserve raw outputs privately where they contain licensed text or sensitive material; publish only permitted summaries and hashes.

The baseline comparison command is:

```bash
python scripts/evaluation/compare_discovery_gap_baselines.py \
  --benchmark PATH_TO_ADJUDICATED_BENCHMARK.json \
  --split test --evidence-budget 8 \
  --llm-only PATH_TO_LLM_ONLY.json \
  --vector-rag PATH_TO_VECTOR_RAG.json \
  --graph-rag PATH_TO_GRAPH_RAG.json \
  --hybrid-retrieval PATH_TO_HYBRID_RETRIEVAL.json \
  --discoveryai-full PATH_TO_DISCOVERYAI_FULL.json \
  --output reports/evaluation/baseline-comparison.json
```

This command is not to be run on starter templates or unadjudicated labels.

## 5. Outcomes and interpretation

Report, with denominators and per-record outputs where permitted:

- Gap-status accuracy and macro-F1.
- Evidence precision, recall and F1.
- Evidence stance accuracy.
- Rating MAE where defined.
- Paired per-record full-system differences, bootstrap intervals, win rates and sample size.
- Runtime, failure rate, token usage and cost/usage when measurable.
- Missing predictions and exclusions, with reasons.

The existing evaluator's paired bootstrap intervals are descriptive. They are not by themselves a pre-registered hypothesis test or proof of statistical significance. Do not claim superiority from a small pilot, synthetic labels, template data or a single metric.

## 6. Ablation sequence

After the baseline configuration is frozen, run the full system and five predeclared variants:

- `full`
- `without_vector_retrieval`
- `without_graph_retrieval`
- `without_research_critic`
- `without_temporal_signals`
- `without_discovery_score`

Each artifact must record `run_metadata.ablation_id` and exact `disabled_components`. All variants must use identical benchmark/corpus/split/record IDs and otherwise matched configuration. A component-removal effect is conditional on this implementation and is not automatically causal or additive.

## 7. Hard gates before scored experiments

Do not execute or publish scored test results until all applicable gates pass:

- [ ] Day 2 final eligible corpus manifest exists and is checksum-frozen.
- [ ] Full-text processing rights are documented for every included item; unresolved rights are excluded.
- [ ] Duplicate/version families are resolved and preserved.
- [ ] Benchmark records have traceable evidence and adjudicated gold labels; no starter-template labels.
- [ ] Train/validation/test split is frozen by work/version family and related-question groups.
- [ ] Locked test set is inaccessible to developers and prompt/model tuning.
- [ ] Five prediction artifacts pass schema/ID/metadata validation.
- [ ] Run configuration and code revision are captured in the provenance manifest.
- [ ] Deviations and failed runs are logged.

If human annotation remains deferred, the system can be exercised in **engineering smoke mode** using clearly synthetic fixtures, but those results must be labelled synthetic, excluded from research metrics and never described as benchmark performance.

## 8. Day 4 exit criteria

- [x] Five-system comparison interface and baseline identifiers inspected in the repository.
- [x] Required run metadata and fairness controls documented.
- [x] Benchmark and corpus hard gates documented.
- [ ] Run-artifact validation executed against genuine system outputs.
- [ ] Five comparable prediction artifacts produced on an eligible benchmark.
- [ ] Scored baseline comparison executed on a locked, adjudicated split.

Day 4 is therefore **in progress**. Protocol readiness is not experiment completion.