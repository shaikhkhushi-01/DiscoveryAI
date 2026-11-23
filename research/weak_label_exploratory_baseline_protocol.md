# Weak-label exploratory TF-IDF baseline

This experiment is deliberately separate from the Phase 4 adjudicated benchmark.
It transfers an LLM-inferred research-gap sentence from the most similar
training abstract using TF-IDF cosine similarity.

## Scientific boundary

- Input: abstract only.
- Training/reference pool: train split only.
- Target: `research_gap_llm_inferred`.
- Prediction: copy the target attached to the nearest training abstract.
- Evaluation labels: used only to calculate lexical overlap metrics.
- This is a retrieval/label-transfer baseline, not a trained generative model.
- It measures reproduction of weak-label phrasing, not correctness or discovery
  of genuinely novel scientific gaps.
- Labels are LLM-inferred from title and abstract, not expert validated.
- ROUGE-L and token F1 are lexical metrics, not semantic or evidence-grounding
  measures. Generator and category subgroup results are descriptive only.
- The script refuses a non-weak-label artifact and checks paper-ID and exact
  normalized-abstract separation between train and evaluation partitions.
- The provided random split does not support chronological generalization.

## Run

First run validation only:

```bash
python scripts/evaluation/weak_label_exploratory_baseline.py \
  --input artifacts/weak_labels/research_gap_dataset_v2.json \
  --output artifacts/weak_labels/tfidf_baseline_validation.json \
  --split validation
```

Inspect the validation report and freeze the method before running test. Do not
tune the vectorizer or select settings based on test results.

Then run the final exploratory test report:

```bash
python scripts/evaluation/weak_label_exploratory_baseline.py \
  --input artifacts/weak_labels/research_gap_dataset_v2.json \
  --output artifacts/weak_labels/tfidf_baseline_test.json \
  --split test
```

Both outputs are local generated artifacts and should not be committed. They
are excluded by the repository's `artifacts/` ignore rule.

## Report contents

Each JSON report records the source provenance, method, partition sizes,
overall token F1 / ROUGE-L F1 / nearest-neighbour cosine similarity, subgroup
summaries by generator and primary category, and per-record predictions with
the nearest training paper ID. Small subgroup counts must not be interpreted
as reliable domain rankings.

This experiment does not unblock or replace the Phase 4 five-system baseline
or six-ablation experiments. Those still require a compatible corpus-linked
benchmark with traceable evidence and valid gold/adjudicated annotations.
