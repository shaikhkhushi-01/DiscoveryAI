# Scientific Evaluation Status

**Status snapshot:** 2026-11-15  
**Purpose:** distinguish implemented evaluation tooling from completed scientific evaluation.

## Implemented in the repository

- Versioned DiscoveryGapBench JSON schema and validation.
- Annotation rubric and adjudication requirements.
- Evaluation runner that accepts adjudicated gold records only and validates prediction coverage and provenance.
- Gap-status accuracy, macro-F1, confusion matrix, evidence precision/recall/F1, stance accuracy, and rating MAE.
- Bootstrap confidence intervals where sample size permits.
- Five-system baseline harness: LLM-only, vector RAG, GraphRAG, hybrid retrieval, full DiscoveryAI.
- Component ablation harness: full, without vector retrieval, without graph retrieval, without Research Critic, without temporal signals, without Discovery Score.
- Expert agreement analysis for nominal and ordinal assessments.
- Reproducibility metadata and CLI scripts.

## Not yet established

- A populated, independently annotated and adjudicated benchmark.
- A frozen production corpus snapshot with verified provenance for all benchmark records.
- Valid prediction artifacts for every baseline and ablation.
- Measured baseline or ablation results.
- Expert agreement statistics from two real independent annotators.
- Per-record error analysis on a held-out test split.

## Release rule

Do not report numeric performance, baseline superiority, ablation effects, or expert agreement until the relevant input artifacts have been created, validated, and evaluated. The files in `data/evaluation/*template*` are templates, not labelled examples.

## Required execution sequence

1. Freeze corpus snapshot and search protocol.
2. Populate benchmark records with paper/document/chunk provenance.
3. Obtain two independent qualified annotations per record.
4. Adjudicate disagreements and freeze train/validation/test splits.
5. Generate predictions from all five baseline systems using identical query/corpus/split/evidence budgets.
6. Generate all predeclared ablation predictions under identical conditions.
7. Run evaluation, agreement, and error-analysis scripts.
8. Archive run manifests, raw predictions, aggregate reports, and code revision.
