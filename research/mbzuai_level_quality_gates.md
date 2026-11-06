# MBZUAI-Level Research Quality Gates for DiscoveryAI

## What "MBZUAI-level" means in this repository

There is no single public checklist that certifies a project as "MBZUAI-level." For DiscoveryAI, the phrase is treated as an aspiration toward research-lab quality: a clearly scoped research question, defensible novelty positioning, reproducible methods, rigorous baselines, expert-reviewed data, transparent limitations, secure engineering, and a paper/demo that another researcher can inspect and reproduce.

This document is a quality plan, not a claim of institutional endorsement, benchmark success, or scientific validation.

## 1. Research contribution

The contribution should be stated narrowly and testably:

> DiscoveryAI investigates whether combining hybrid scientific retrieval, structured knowledge-graph context, evidence validation, temporal signals, and a research critic improves the identification and explanation of candidate research opportunities within a frozen scientific corpus.

The contribution is not "the AI discovers globally new science." The system's novelty judgments are bounded by corpus coverage, indexing quality, search protocol, and annotation quality.

Before publication:
- Complete a related-work review with dated search strings, databases, inclusion/exclusion criteria, and a PRISMA-style screening record where appropriate.
- Compare the proposed contribution against the closest scientific discovery, literature-based discovery, GraphRAG, scientific RAG, and research-gap detection systems.
- State what is genuinely new in the method, not merely the combination of familiar components.
- Provide at least one falsifiable research hypothesis and predefine primary outcomes.

## 2. Benchmark construction

- Freeze and identify a corpus snapshot, metadata source, deduplication method, and search cutoff date.
- Store stable provenance for every evidence item: paper, document, chunk, source location, and content checksum where feasible.
- Define record inclusion/exclusion rules before annotation.
- Ensure examples cover positive, negative, inconclusive, contradictory, sparse-evidence, and out-of-scope cases.
- Use separate train/validation/test splits and prevent paper, author, near-duplicate, and temporal leakage where relevant.
- Keep held-out test labels access-controlled until final evaluation.
- Pilot the rubric, revise it, then lock a version before collecting final test labels.

The starter JSON files in `data/evaluation/` are templates only. They are not expert labels and must never be reported as a completed benchmark.

## 3. Expert annotation and adjudication

- Use two independent domain-qualified reviewers for every scored item.
- Blind reviewers to model predictions and to the other reviewer's labels.
- Record pseudonymous reviewer IDs, rubric version, annotation timestamps, and documented exclusions; keep real identities in a separately controlled record.
- Report raw agreement and class prevalence alongside Cohen's kappa for nominal labels and weighted kappa for ordinal ratings.
- Explain missing/undefined kappa cases and the effect of class imbalance.
- Preserve both raw annotations. A third reviewer or documented consensus process adjudicates disagreements.
- Only adjudicated records enter the scored gold split.

Agreement statistics quantify consistency; they do not prove that the rubric is valid or that the gold labels are objectively correct.

## 4. Controlled evaluation

Every system must receive the same research question, frozen corpus, split, evidence budget, and output contract:
1. LLM-only
2. Vector RAG
3. GraphRAG
4. Hybrid retrieval
5. Full DiscoveryAI

Run planned component ablations under the same conditions. Report where components do not help or harm results.

Predefine primary and secondary metrics. The current harness supports gap-status classification, evidence precision/recall/F1 and stance agreement, rating MAE, paired record-level comparisons, and bootstrap intervals. Extend the study with retrieval Recall@K/MRR/nDCG, citation correctness, unsupported-claim rate, critic classification, and expert assessment of hypothesis/experiment quality where the benchmark supports them.

- Report per-record outputs and aggregate results.
- Include sample sizes, confidence intervals, class distributions, error slices, and negative results.
- Do not overinterpret bootstrap intervals from a small pilot.
- Record model/provider/version, prompt revision, embedding model, retrieval settings, reranker, code SHA, corpus ID, benchmark version, split, runtime, and random seed.
- Run the final test set once after configuration freeze; do not tune on test outcomes.

## 5. Engineering and responsible research

- Maintain reproducible setup, migration, test, and deployment instructions.
- Test dependency failures and partial service outages, not just the happy path.
- Use least-privilege credentials, secret management, explicit CORS, upload validation, and access controls for private corpora.
- Document licensing, copyright, privacy, retention, and deletion constraints for source papers and annotations.
- Make provenance inspectable from generated claims back to retrieved source passages.
- Clearly label candidate gaps, heuristic scores, generated hypotheses, and illustrative dashboard elements.
- Include human review before users treat a generated opportunity as a research conclusion.

## 6. Publication package

A credible submission package should contain:
- Research question, contribution statement, and closest-work comparison.
- System architecture and implementation details.
- Dataset card / corpus documentation and benchmark annotation protocol.
- Baseline and ablation results with reproducibility manifest.
- Error analysis, limitations, failure examples, and threats to validity.
- Ethics, licensing, privacy, and data-governance statement.
- A runnable artifact or reproducible demo with pinned dependencies and setup instructions.

## 7. Current status (2026-11-06)

### Implemented in the repository
- Core document, retrieval, knowledge-graph, evidence, gap-detection, critic, synthesis, hypothesis, and experiment-planning paths.
- DiscoveryGapBench schema, annotation rubric, validation, and offline evaluator.
- Five-system baseline comparison harness.
- Component ablation harness.
- Dual-annotator agreement and adjudication-queue tooling.
- CI and static release-readiness checks.

### Not yet demonstrated
- A populated, expert-reviewed, adjudicated gold benchmark.
- Measured inter-annotator agreement from real reviewers.
- Completed predictions for every baseline and ablation.
- Measured performance, confidence intervals, unsupported-claim rate, and error analysis.
- A publication-quality related-work study and independently reproducible results.

**Release rule:** until these items are completed, describe DiscoveryAI as an advanced research prototype with evaluation infrastructure—not as a scientifically validated discovery system.
