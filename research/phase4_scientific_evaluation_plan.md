# Phase 4 — Scientific Evaluation and Benchmarking

## Goal

Move DiscoveryAI from a feature-complete prototype to a scientifically evaluated system. Phase 4 measures whether its retrieval, evidence validation, gap ranking, critic, and hypothesis/experiment outputs are reliable against human-annotated references.

**Core rule:** do not publish performance scores until a real, reviewed gold set exists and every evaluated system uses the same corpus, queries, and evidence pool.

## Current baseline

The repository already contains:
- Retrieval metrics: Recall@K, MRR, and nDCG@K.
- Extraction and retrieval gold-set templates.
- Evaluation protocols for extraction and retrieval.
- A release-readiness check and CI workflow.
- Research-gap, evidence, critic, hypothesis, and experiment-plan APIs.

What is missing is a populated expert-annotated benchmark and reproducible end-to-end baseline/ablation runs. No benchmark performance is claimed at Phase 4 kickoff.

## Workstreams and exit criteria

### 4.1 DiscoveryGapBench specification and dataset
- Define a versioned record format for research questions, corpus snapshots, candidate gaps, gap types, supporting and contradictory evidence, and expert judgments.
- Include evidence identifiers that resolve to immutable paper/document/chunk provenance.
- Record annotator identity in a privacy-preserving form, annotation date, rubric version, adjudication state, and disagreement.
- Build a small pilot set before scaling; require independent annotations and adjudication.
- Exclude unresolved or incomplete records from scored evaluation.

**Exit:** schema validation, annotation rubric, and a reviewed pilot gold set with documented corpus coverage.

### 4.2 Reproducible evaluation runner
- Freeze corpus, model/provider, prompt, embedding, retrieval, and code versions for each run.
- Evaluate retrieval, evidence/citation correctness, gap ranking, critic verdicts, and hypothesis/experiment quality.
- Report sample counts, per-query results, aggregate metrics, confidence intervals where justified, and error slices.
- Fail closed when gold data is empty, malformed, or incompatible with the run.

**Exit:** deterministic, machine-readable evaluation report with provenance and no fabricated metrics.

### 4.3 Baselines
Compare on the same benchmark:
1. LLM-only
2. Standard vector RAG
3. GraphRAG
4. Hybrid retrieval
5. Full DiscoveryAI

**Exit:** all baselines run on identical query/corpus splits with comparable evidence budgets and recorded configurations.

### 4.4 Ablations
Measure contribution of:
- Knowledge graph
- Vector retrieval
- Temporal signals
- Research Critic
- Discovery Score
- Multi-agent orchestration

**Exit:** controlled ablation report, including cases where a component does not improve results.

### 4.5 Expert evaluation and error analysis
Experts assess novelty within the stated corpus scope, relevance, feasibility, evidence quality, testability, and reproducibility. Report inter-annotator agreement and adjudication procedure.

**Exit:** expert-reviewed results, limitations, and failure taxonomy. No claim of global novelty from a bounded corpus.

## Required metric families

| Component | Metrics / checks |
|---|---|
| Retrieval | Recall@K, Precision@K, MRR, nDCG@K |
| Extraction | Precision, Recall, F1, schema validity, unsupported extraction rate |
| Evidence | Citation correctness, evidence faithfulness, contradiction recall, unsupported-claim rate |
| Gap ranking | Precision@K, Recall@K, nDCG, false discovery rate |
| Critic | Per-class precision/recall/F1, calibration where sample size permits |
| Hypotheses | Expert testability, falsifiability, relevance, novelty-in-corpus |
| Experiment plans | Reproducibility, completeness, baseline/metric appropriateness |
| Trends | Temporal holdout performance and calibration |

## Phase 4 milestones

- **P4.1:** Benchmark schema, annotation rubric, pilot dataset.
- **P4.2:** Evaluation runner and provenance-rich reports.
- **P4.3:** Baseline and ablation execution.
- **P4.4:** Expert review, error analysis, and release decision.

## Release gate

Phase 4 is complete only when:
- The gold set is populated, versioned, and reviewed.
- Evaluation runs are reproducible from recorded configuration.
- Baselines and planned ablations are reported.
- Expert review and error analysis are documented.
- Unsupported-claim and citation correctness are measured.
- Limitations and confidence intervals are reported honestly.

A passing engineering test suite alone does not satisfy this scientific validation gate.
