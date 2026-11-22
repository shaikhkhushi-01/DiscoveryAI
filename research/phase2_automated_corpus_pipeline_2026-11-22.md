# DiscoveryAI Phase 2 — Automated corpus and benchmark pipeline

**Goal:** Reproducible, zero-budget, no-new-human-review-dependent NLP benchmark and corpus preparation.

## Workstreams

1. QASPER ingestion: official, version-pinned v0.3.0 archives; published SHA-256 verification; normalized paper chunks, questions, and answer/evidence references.
2. Leakage control: model query inputs and gold references are separate; paper-level split separation; references never enter prompts or retrieval indexes.
3. Discovery corpus automation: OpenAlex metadata discovery and automated enrichment remain candidate-discovery only. Keyword routing is not human screening.
4. Rights-aware content handling: QASPER attribution is preserved. The general OpenAlex corpus remains metadata/abstract-first. Existing full-text acquisition stays fail-closed on explicit permission evidence.
5. Reproducibility: local manifest records dataset version, source URLs, checksums, timestamp, split counts, and limitations. Raw and normalized data stay outside Git.

## Milestones

| Milestone | Exit evidence |
|---|---|
| P2.1 Acquisition utility | Pinned archive URLs and SHA-256; safe tar member handling |
| P2.2 Normalized layout | Paper/chunk/query/reference JSONL with stable IDs and separate gold references |
| P2.3 Integrity checks | Malformed record, split overlap, and gold/query separation tests |
| P2.4 Local snapshot | Manifest with actual counts, hashes, timestamp and label availability |
| P2.5 Evaluation adapter | QASPER-specific prediction contract and official metric path; no mixing with DiscoveryGapBench |
| P2.6 Corpus readiness | Rights-aware manifest and versioned NLP discovery snapshot; unclear rights excluded from full-text |

## Run locally

From repository root with Python 3.12+:

```bash
python scripts/benchmarks/prepare_qasper.py
```

To verify existing archives and normalize without downloading:

```bash
python scripts/benchmarks/prepare_qasper.py --verify-local-archives-only
```

Output is written to `data/benchmarks/qasper/`, which is gitignored. Do not upload this directory as a public workflow artifact: it contains full paper text and gold references.

## Integrity gates

- Preserve the official dataset card's CC BY 4.0 attribution; do not infer rights to independently redistribute original PDFs.
- Measure test gold-label availability from the actual acquired release.
- No benchmark result is claimed until an actual run completes using the official scorer.
- QASPER QA results cannot validate research-gap discovery quality.
- Automated relevance flags in the OpenAlex corpus are triage hints only, not eligibility decisions.
