# QASPER benchmark pipeline — runbook

## Install

No third-party Python package is required for acquisition, normalization, or scoring. Use Python 3.12+ from the repository root.

## Acquire and normalize

```bash
python scripts/benchmarks/prepare_qasper.py
```

The command downloads only the pinned official QASPER v0.3.0 archives, verifies SHA-256 before parsing, validates the expected 888/281/416 paper split sizes, and writes a local manifest.

Output:
- `data/benchmarks/qasper/raw/`: compressed source archives.
- `data/benchmarks/qasper/normalized/papers/`: paper metadata.
- `data/benchmarks/qasper/normalized/chunks/`: abstract and paragraph chunks.
- `data/benchmarks/qasper/normalized/queries/`: questions and safe model input metadata.
- `data/benchmarks/qasper/normalized/references/`: answer and evidence annotations; never feed these files to a model.
- `data/benchmarks/qasper/normalized/manifest.json`: provenance and observed counts.

To re-normalize without downloading:

```bash
python scripts/benchmarks/prepare_qasper.py --verify-local-archives-only
```

The raw and normalized dataset is gitignored. Do not commit it or upload it as a public CI artifact.

## Prediction contract

The evaluator expects one JSON object per line:

```json
{"question_id":"Q1","predicted_answer":"the generated answer","predicted_evidence":["exact source paragraph text"]}
```

Predicted evidence must be the exact source paragraph strings selected by the system. A future adapter should preserve paragraph provenance and should never use gold answer/evidence fields.

## Evaluate

Example for validation:

```bash
python scripts/benchmarks/evaluate_qasper.py \
  --gold data/benchmarks/qasper/normalized/references/validation.jsonl \
  --predictions data/benchmarks/qasper/predictions/validation.jsonl \
  --output data/benchmarks/qasper/reports/validation.json
```

Use `--text-evidence-only` to exclude figure/table evidence records marked `FLOAT SELECTED`, matching the official evaluator option.

The scorer is adapted from the official AllenAI QASPER LED baseline evaluator and reports Answer F1, Answer F1 by answer type, Evidence F1, missing predictions, and ignored extra predictions. A missing prediction receives zero, as in the official implementation.

## Split policy

- Train: development/training only.
- Validation: model selection and iteration.
- Test: locked final evaluation; do not inspect test scores repeatedly while tuning.
- The official test release may not expose answer annotations. The preparation manifest records actual annotation availability. The evaluator intentionally errors if the selected reference file contains no annotated questions.

## Research interpretation

QASPER results measure scientific-paper question answering and evidence selection. They do not establish research-gap novelty, scientific usefulness, hypothesis quality, or independent discovery validity. Report this limitation wherever results are presented.

## Attribution

Dasigi et al. (2021), *A Dataset of Information-Seeking Questions and Answers Anchored in Research Papers*, NAACL-HLT. Dataset card states CC BY 4.0; cite the dataset and paper. The QASPER card describes the paper full text as sourced from S2ORC; this pipeline does not grant permission to separately redistribute source-paper PDFs.
