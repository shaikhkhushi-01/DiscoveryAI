# DiscoveryGapBench Evaluation Runner Protocol (P4.2)

## Inputs

1. A DiscoveryGapBench JSON file validated by the P4.1 loader.
2. A prediction JSON file containing one system prediction for every adjudicated gold record in the selected split.
3. Explicit run metadata: run ID, system/version, code revision, corpus ID, benchmark version, model provider/name, prompt version, embedding model, and retrieval configuration.

The runner uses only adjudicated records in the selected split (default: `test`). Missing predictions, duplicate/unknown record IDs, metadata placeholders, or benchmark-version mismatches fail the run. Predictions must provide a gap-status label, four 0–3 ratings, and evidence passages with a supporting/contradictory stance.

## Metrics

- Gap-status accuracy, macro-F1, confusion matrix, and per-class precision/recall/F1.
- Exact paper/document/chunk evidence precision, recall, F1, and stance accuracy.
- Mean absolute error (MAE) for corpus-bounded novelty, relevance, feasibility, and evidence-quality ratings.
- Per-record metrics and aggregate means.
- Deterministic percentile bootstrap 95% intervals for per-record aggregate means when at least two records exist. For one record, interval is null.

## Reproducibility and limitations

The report includes the exact run metadata, benchmark/rubric versions, corpus IDs, split, sample counts, and per-record results. Bootstrap resampling uses a fixed seed. The generated timestamp is informational; all metric calculations are deterministic for fixed inputs.

These metrics evaluate predictions against the benchmark labels, not global scientific truth. Novelty is strictly scoped to the frozen corpus. Small pilot sets produce unstable intervals. Pending or non-adjudicated records are excluded, and the runner refuses to score a split with no adjudicated examples.

## Command

```bash
python scripts/evaluation/run_discovery_gap_bench.py \
  --benchmark data/evaluation/discovery_gap_bench.json \
  --predictions data/evaluation/predictions/discoveryai-run-001.json \
  --split test \
  --output reports/evaluation/discoveryai-run-001.json
```

The checked-in prediction template is a format example only; it contains placeholders and cannot be scored until populated with actual system outputs and matching run metadata.
