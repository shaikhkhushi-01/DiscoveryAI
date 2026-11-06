# P4.3 Baseline Comparison Protocol

## Systems

1. **LLM-only:** model receives the research question and candidate gap without retrieved corpus evidence. It must still emit the common prediction schema; evidence should be empty unless it can cite a supplied immutable corpus passage.
2. **Vector RAG:** dense-vector retrieval followed by the same output contract.
3. **GraphRAG:** knowledge-graph traversal/retrieval followed by the same output contract.
4. **Hybrid retrieval:** vector + graph/keyword retrieval under the shared evidence cap.
5. **Full DiscoveryAI:** production pipeline with the integrated retrieval, evidence validation, critic, and scoring components.

## Fair-comparison controls

- Freeze one DiscoveryGapBench version, corpus snapshot, test split, and exact record IDs.
- Use the same question/candidate text and the same adjudicated gold labels for every system.
- Use a common maximum evidence-item budget per record (default 8). Also record token budget, model/provider, prompt version, embedding model, retrieval settings, and code revision; the evidence-item cap alone does not equalize compute.
- Keep system-specific tuning on train/validation only. Do not tune against test labels.
- Run each system independently; never relabel copied outputs as a different baseline.
- Preserve raw predictions and full run metadata.
- If stochastic inference is used, perform multiple predeclared seeds/runs and report run-level variance rather than selecting the best run.

## Metrics

Use the P4.2 evaluation runner for every system:
- Gap status: accuracy, macro-F1, per-class precision/recall/F1, confusion matrix.
- Evidence: exact paper/document/chunk precision, recall, F1, and stance accuracy.
- Expert ratings: MAE for corpus-bounded novelty, relevance, feasibility, and evidence quality.
- Report per-record results and paired full-system-minus-baseline deltas with bootstrap intervals where sample size permits.

## Interpretation

Higher is better for status accuracy/F1 and evidence precision/recall/F1/stance accuracy. Lower is better for rating MAE. Report all systems and failure cases; do not collapse metrics into an unvalidated single score. Paired bootstrap intervals are descriptive, not formal proof of statistical significance.

## Command

```bash
python scripts/evaluation/compare_discovery_gap_baselines.py \
  --benchmark data/evaluation/discovery_gap_bench.json \
  --llm-only data/evaluation/baseline_predictions/llm_only.json \
  --vector-rag data/evaluation/baseline_predictions/vector_rag.json \
  --graph-rag data/evaluation/baseline_predictions/graph_rag.json \
  --hybrid-retrieval data/evaluation/baseline_predictions/hybrid_retrieval.json \
  --discoveryai-full data/evaluation/baseline_predictions/discoveryai_full.json \
  --split test --evidence-budget 8 \
  --output reports/evaluation/phase4-baseline-comparison.json
```

This harness compares real prediction artifacts. It does not execute or simulate the five model/retrieval systems itself, and it does not fabricate results when prediction files or adjudicated gold data are absent.
