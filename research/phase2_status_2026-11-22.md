# Phase 2 status — automated student-project track

**Last updated:** 2026-11-22  
**Scope decision:** Independent human reviewer recruitment and custom human annotation are out of scope. This is a student-level engineering/research prototype, not a human-validated scientific discovery study.

## Completed engineering

| Component | Status |
|---|---|
| QASPER v0.3.0 pinned archive acquisition with SHA-256 checks | Implemented |
| Safe archive member parsing and schema normalization | Implemented |
| Paper-level split leakage checks | Implemented |
| Query/reference separation | Implemented |
| QASPER Answer F1 / Evidence F1 evaluator | Implemented, aligned to AllenAI reference implementation |
| Deterministic per-paper BM25 extractive generator | Implemented |
| Abstract-only and full-text context variants | Implemented |
| Optional configured LLM-RAG generation | Implemented; optional and potentially metered |
| Aggregate-only comparison report | Implemented |
| One-click GitHub Actions workflow | Implemented in PR #92 (pending merge/CI) |

## Empirical status

No actual QASPER archive acquisition, normalized manifest, prediction generation, or benchmark scores are verified in this status document. Those become verified only after the manual QASPER Validation workflow succeeds and its aggregate artifact is inspected.

## Execution

Run the GitHub Actions workflow **QASPER Validation (zero-cost baselines)** manually from the Actions tab, or locally:

```bash
python scripts/benchmarks/prepare_qasper.py
python scripts/benchmarks/generate_qasper_predictions.py --split validation --mode extractive --context-scope abstract_only --code-revision <commit-sha>
python scripts/benchmarks/generate_qasper_predictions.py --split validation --mode extractive --context-scope full_text --code-revision <commit-sha>
python scripts/benchmarks/evaluate_qasper.py --gold data/benchmarks/qasper/normalized/references/validation.jsonl --predictions data/benchmarks/qasper/predictions/validation.abstract_only.jsonl --output data/benchmarks/qasper/reports/abstract_only.json
python scripts/benchmarks/evaluate_qasper.py --gold data/benchmarks/qasper/normalized/references/validation.jsonl --predictions data/benchmarks/qasper/predictions/validation.full_text.jsonl --output data/benchmarks/qasper/reports/full_text.json
```

The workflow additionally builds an aggregate-only report. It uploads the normalized manifest and aggregate metrics only; it does not upload raw archives, paper text, gold references, or individual predictions.

## Interpretation and limits

- QASPER evaluates scientific-paper question answering and evidence selection, not research-gap novelty, hypothesis quality, or scientific usefulness.
- Abstract-only vs full-text results compare context availability for a simple BM25 extractive baseline; they do not establish causal effects or SOTA performance.
- The custom OpenAlex candidate pool remains provisional and is not a rights-cleared research corpus. Since human review is explicitly waived, it must not be described as screened, rights-approved, or frozen.
- The Day 4 DiscoveryAI research-gap benchmark and six ablations remain gated because they require adjudicated research-gap gold records. Do not create fake labels or substitute QASPER QA annotations for gap-discovery labels.
- A credible student-level deliverable can report implementation, reproducibility, benchmark metrics and limitations, but not claim independent scientific discovery validation or MBZUAI affiliation/endorsement.
