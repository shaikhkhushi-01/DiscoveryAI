# Scientific Evaluation Status

**Status snapshot:** 2026-11-26  
**Purpose:** distinguish implemented evaluation tooling, completed public-benchmark measurements, preliminary experiments, and pending scientific validation.

## 1. DiscoveryGapBench evaluation tooling

Implemented in the repository:

- Versioned benchmark schema, validation, annotation rubric, and adjudication requirements.
- Evaluation runner for adjudicated gold records with prediction coverage and provenance checks.
- Gap-status accuracy, macro-F1, confusion matrix, evidence precision/recall/F1, stance accuracy, and rating MAE.
- Bootstrap confidence intervals where sample size permits.
- Five-system baseline harness: LLM-only, vector RAG, GraphRAG, hybrid retrieval, and full DiscoveryAI.
- Six planned configurations: full system and five component ablations (without vector retrieval, graph retrieval, Research Critic, temporal signals, or Discovery Score).
- Expert-agreement analysis and reproducibility metadata.

These are implemented evaluation tools, not completed experiments.

## 2. Public benchmark: QASPER

QASPER is a separate public scientific question-answering/evidence benchmark. It does **not** measure research-gap discovery and does not replace DiscoveryGapBench expert validation.

### Prepared dataset

Prepared version: QASPER v0.3.0.

- 1,585 papers
- 5,049 questions
- 81,550 normalized text chunks

| Split | Papers | Questions | Chunks |
|---|---:|---:|---:|
| Train | 888 | 2,593 | 47,770 |
| Validation | 281 | 1,005 | 13,547 |
| Test | 416 | Not used in the reported results | 20,233 |

Gold references are kept separate from generator inputs. Results below are validation results only; no held-out test result is claimed.

### Extractive answer/evidence evaluation

All 1,005 validation questions received predictions.

| Metric | Result |
|---|---:|
| Answer F1 | 0.0753 |
| Evidence F1 | 0.1582 |
| Missing predictions | 0 |

Answer F1 by question type:

| Type | F1 |
|---|---:|
| Extractive | 0.0938 |
| Abstractive | 0.0927 |
| Boolean | 0.0008 |
| None | 0.0000 |

The evaluator is adapted from the AllenAI QASPER LED baseline evaluator, pinned to source revision `afd0fb96bf78ce8cd8157639c6f6a6995e4f9089`.

### Text-evidence retrieval at k=5

| Metric | Extractive | Gemini LLM-RAG (incomplete) |
|---|---:|---:|
| Recall@5 | 0.4094 | 0.1865 |
| Precision@5 | 0.1275 | 0.0538 |
| MRR@5 | 0.3081 | 0.2327 |
| nDCG@5 | 0.2946 | 0.1893 |

Evidence mapping and coverage:

- 1,882 unique gold text-evidence entries; 1,782 mapped to normalized chunks; 100 unmatched.
- Gold text-evidence chunk coverage: 94.69%.
- 253 figure/table evidence entries excluded from text retrieval metrics.
- Extractive: 1,005 predictions; 888 questions evaluated; 5,009 returned paragraphs, all exact matches to corpus chunks.
- Gemini LLM-RAG: 663 predictions; 342 missing; 888 questions evaluated; 603 with retrievable gold; 658 questions returned zero evidence; 473 returned paragraphs, all exact matches to corpus chunks.

**Interpretation limits:**

1. Gemini LLM-RAG is incomplete. The evaluator assigns zero to missing predictions; its aggregate scores are not a complete validation result.
2. Both modes use the same BM25 retrieval function. This is not a comparison of two independent retrieval algorithms.
3. Relevance is exact paragraph-text matching within the same paper, not semantic relevance.
4. Metrics are conditional on gold text evidence being represented in normalized chunks.
5. A 100% exact chunk-match rate verifies corpus membership, not relevance or answer correctness.

### Gemini answer-generation smoke test

A separate five-question smoke test produced Answer F1 0.2751 and Evidence F1 0.2800 (5/5 predictions). This is a pipeline smoke test, not a representative benchmark result and must not be compared directly with the 1,005-question extractive evaluation.

### Report artifacts

- `data/benchmarks/qasper/reports/validation_extractive_metrics.json`
- `data/benchmarks/qasper/reports/validation_extractive_retrieval_metrics.json`
- `data/benchmarks/qasper/reports/validation_llm_rag_retrieval_metrics.json`
- `data/benchmarks/qasper/reports/validation_llm_rag_smoke_metrics.json`

The benchmark dataset and prediction files are local/ignored where applicable; do not imply that all raw data or predictions are committed to GitHub.

## 3. DiscoveryGapBench scientific validation: pending

Not yet established:

- A populated, independently annotated and adjudicated DiscoveryGapBench.
- A frozen corpus snapshot and verified provenance for all benchmark records.
- Valid prediction artifacts for all five baselines and six planned configurations.
- Measured baseline or ablation results.
- Agreement statistics from two real independent annotators.
- Held-out test error analysis.

QASPER results do not establish that DiscoveryAI identifies research gaps, generates novel hypotheses, or outperforms research-discovery systems.

## 4. Required next steps

### QASPER
1. Resolve Gemini provider quota/availability constraints.
2. Complete all remaining validation predictions.
3. Re-run answer and evidence evaluation on the complete prediction set.
4. Archive model/provider, prompt, retrieval configuration, code revision, and run metadata.
5. Keep the held-out test split untouched until configuration freeze.

### DiscoveryGapBench
1. Freeze corpus snapshot and search protocol.
2. Populate records with paper/document/chunk provenance.
3. Obtain two independent qualified annotations per record and adjudicate disagreements.
4. Freeze train/validation/test splits with leakage controls.
5. Generate all baseline and ablation predictions under identical conditions.
6. Run evaluation, agreement, and per-record error analysis.
7. Archive run manifests, predictions, reports, and code revision.

## 5. Research integrity and release rule

- Scope novelty statements to a named corpus snapshot and search protocol.
- Preserve provenance from claims to papers, documents, and chunks.
- Include contradictory evidence and uncertainty.
- Keep annotations, adjudication, and held-out labels separate.
- Record model/provider/version, prompt, embedding, retrieval configuration, code revision, corpus, benchmark, split, and random seed.
- Report negative results and limitations; do not tune on held-out test data.
- Do not claim DiscoveryGapBench performance, baseline superiority, ablation effects, or expert agreement until the required real artifacts have been evaluated.

**Overall status:** evaluation tooling is implemented and preliminary QASPER validation experiments exist. Complete Gemini validation, DiscoveryGapBench expert validation, and controlled baseline/ablation experiments remain pending.
