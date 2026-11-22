# QASPER prediction generation

This runner creates model predictions from QASPER query and paper paragraph files. It never opens the references directory.

## Generate a deterministic, zero-cost extractive baseline

After preparing the dataset:

```bash
python scripts/benchmarks/generate_qasper_predictions.py \
  --split validation \
  --mode extractive \
  --top-k 5 \
  --code-revision <git-commit-sha>
```

Optional smoke test:

```bash
python scripts/benchmarks/generate_qasper_predictions.py \
  --split validation --mode extractive --max-questions 20 \
  --code-revision <git-commit-sha>
```

This baseline uses per-paper BM25 paragraph retrieval and returns the highest-ranked paragraph as an extractive answer. It is intentionally simple and reproducible, not a state-of-the-art QA model.

## Optional configured LLM + retrieval mode

```bash
python scripts/benchmarks/generate_qasper_predictions.py \
  --split validation --mode llm_rag --top-k 5 \
  --code-revision <git-commit-sha>
```

This uses the LLM provider already configured for the DiscoveryAI backend. It may require an existing provider configuration and may incur provider usage charges. No API key should be committed or pasted into source control. The default extractive baseline requires no model credentials or paid services.

## Output

- `data/benchmarks/qasper/predictions/<split>.<mode>.jsonl`
- matching `.metadata.json` with query/chunk/manifest hashes, code revision, mode, and an explicit `gold_references_loaded: false` marker.

The runner refuses the test split to prevent iterative test-set tuning. Generate and inspect validation predictions first. Gold references are loaded only by `evaluate_qasper.py`.

## Score validation

```bash
python scripts/benchmarks/evaluate_qasper.py \
  --gold data/benchmarks/qasper/normalized/references/validation.jsonl \
  --predictions data/benchmarks/qasper/predictions/validation.extractive.jsonl \
  --output data/benchmarks/qasper/reports/validation.extractive.json
```

The extractive baseline is a first reproducible comparator. QASPER Answer F1 / Evidence F1 measure scientific-paper QA and evidence retrieval, not the novelty or correctness of generated research gaps.
