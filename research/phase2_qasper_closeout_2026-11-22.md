# Phase 2 closeout — QASPER benchmark track

**Date:** 2026-11-22  
**Code revision evaluated:** `b60286214bf1943bcf176442a2150e49794089fc`  
**Track status:** Complete for the reproducible QASPER ingestion + validation benchmark pipeline. The separate OpenAlex candidate corpus is explicitly NOT complete.

## Scope decision

Phase 2 is closed against the public QASPER benchmark deliverable: pinned acquisition, deterministic normalization, split isolation, gold/input separation, zero-cost extractive baseline generation, Answer-F1/Evidence-F1 scoring, aggregate reporting, and an audited abstract-vs-full-text validation comparison.

This does not close the separate 399-record OpenAlex candidate-pool work. That pool still has pending relevance, version, and rights decisions. No paper is rights-approved merely because a metadata record says it is open access or a URL is reachable. The pool must not be described as a screened, rights-cleared, or frozen corpus.

## Reproducible dataset snapshot

- Dataset: `allenai/qasper`, v0.3.0.
- Dataset-card license claim: CC BY 4.0; attribution and source-content terms must still be respected.
- Metadata revision: `fdc9d8214fbab5dd782958601db4d678e6934a54`.
- Manifest SHA-256: `2f64f7b25759074faa2064c5dc9d8f08799a5707443f7a17931725fdbcedcb9e`.
- Train/dev archive SHA-256: `a28fdf966db827bcee3d873107d6b6669864fb7ca8fbf73a192f5e39191bdb5a`.
- Test archive SHA-256: `72a52a41193e2838b8074f80ac074b94f956b84886c36a61c58a7df4171bdd72`.

| Split | Papers | Normalized chunks | Questions |
|---|---:|---:|---:|
| Train | 888 | 47,770 | 2,593 |
| Validation | 281 | 13,547 | 1,005 |
| Test | 416 | 20,233 | 1,451 |
| **Total** | **1,585** | **61,550** | **5,049** |

Gold references are stored separately from query inputs. Paper IDs are disjoint across train, validation, and test. Test split generation remains locked.

## Full-text parsing audit

The first artifact had only one chunk per paper because the normalizer did not accept the list-of-section-objects representation. PR #95 fixed support for both list and columnar representations.

The corrected artifact confirms for validation:
- 281 abstract chunks;
- 13,266 non-abstract/body chunks;
- 0 unclassified chunks;
- abstract-only selects 281 chunks;
- full-text selects 13,547 chunks;
- all 281 papers contain abstract and non-abstract text.

This verifies that the two context modes now use distinct scopes.

## Validation experiment

Deterministic BM25 extractive baseline, validation split, 1,005 questions per mode, 1,005 predictions received, zero missing predictions.

| Metric | Abstract-only | Full-text |
|---|---:|---:|
| Answer F1 | 0.056412 | 0.075259 |
| Evidence F1 | 0.010945 | 0.158153 |

Full-text minus abstract-only:
- Answer F1: +0.018847.
- Evidence F1: +0.147208.

These are descriptive validation-set results only. No confidence interval, significance test, causal conclusion, SOTA claim, or research-gap discovery claim is made. The extractive answer scores are low and the evidence score is still modest.

## Phase 2 exit checklist — QASPER track

- [x] Pinned dataset release and archive checksums.
- [x] Safe archive parsing and schema normalization.
- [x] Paper-level split disjointness checks.
- [x] Query inputs separated from gold references.
- [x] Deterministic extractive baseline generation.
- [x] Test split generation blocked.
- [x] Answer-F1 and Evidence-F1 evaluator and aggregate-only report.
- [x] Abstract-only/full-text context audit and corrected full-text normalization.
- [x] Validation run inspected; aggregate artifact hashes and counts verified.
- [x] Strict summary validation for complete prediction coverage, consistent source hashes/revision, reconciled context inventory, and distinct context scopes (added in this closeout PR; CI must pass before merge).

## Explicitly not complete / next phases

- The OpenAlex 399-candidate pool remains provisional; 399 relevance/rights reviews and 16 version-review decisions were pending in the last inspected enrichment report.
- No custom full-text corpus freeze or rights-cleared manifest.
- No five-system DiscoveryAI research-gap benchmark run.
- No six ablation runs.
- No locked QASPER test evaluation or statistical uncertainty analysis.
- QASPER QA/evidence performance does not measure research-gap novelty, hypothesis quality, or usefulness.

## Reproduction

Use the repository workflow **QASPER Validation (zero-cost baselines)**. It runs the pinned preparation, validation predictions for abstract-only and full-text scopes, scoring, and aggregate-only report generation. The workflow intentionally does not publish raw papers, gold references, or per-question predictions.

The QASPER workflow is manually dispatched. Its successful artifact run is verified by the aggregate ZIP supplied on 2026-11-22; the PR #95 commit's ordinary CI run was not independently confirmed at the time this report was drafted.

## Final claim allowed

“DiscoveryAI implements a reproducible QASPER v0.3.0 scientific-paper QA/evidence benchmark pipeline and reports an abstract-only versus full-text BM25 extractive validation comparison.”

Do not claim that Phase 2 has produced a rights-cleared independent research corpus or that DiscoveryAI has demonstrated autonomous scientific discovery.
