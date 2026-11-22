# DiscoveryAI — Phase 1: Student-project scope lock

**Date:** 2026-11-22  
**Status:** Proposed scope for implementation; this document is not evidence of completed experiments or scientific validation.  
**Project type:** Individual/student-level, research-oriented NLP software project.  
**Working title:** Evidence-Grounded NLP Research Opportunity Discovery with Hybrid Retrieval.

## 1. Project objective

Build and evaluate a reproducible NLP research assistant that searches a bounded collection of scientific literature, retrieves traceable evidence, maps relationships among papers/methods/datasets/tasks, and proposes **candidate** research opportunities and hypotheses with explicit uncertainty.

The system must never claim that a gap is globally novel. Every gap is scoped to the corpus snapshot, query, sources, date range, retrieval coverage, and available evidence.

## 2. Problem statement

Researchers face a fragmented literature landscape. Keyword search alone can miss semantically related work, while language-model summaries can produce unsupported claims or overstate novelty. DiscoveryAI will combine semantic retrieval, graph context, evidence validation, temporal signals, and a research critic to produce inspectable candidate opportunities.

The project evaluates software behavior and task-specific NLP performance. It does not claim to replace literature review, domain expertise, or scientific peer review.

## 3. Locked domain and scope

**In scope**
- NLP and computational linguistics.
- Language models and their training/inference methods.
- NLP datasets, benchmarks, evaluation, robustness, safety, reproducibility.
- NLP-focused information retrieval, question answering, and RAG.
- Literature retrieval, evidence-grounded synthesis, corpus-bounded gap hypotheses.

**Out of scope**
- General scientific discovery outside NLP.
- Medical, biological, chemical, or physical-science recommendations.
- Autonomous execution of scientific experiments.
- Claims of globally new discoveries.
- Publication-grade validation or human-expert gold-label claims.

**Initial literature window:** 2018-01-01 to 2025-12-31 for the existing discovery corpus. Any later update must be a separately versioned snapshot.

## 4. Research questions

**RQ1 — Retrieval:** Does combining vector retrieval and graph-based context improve the relevance and coverage of evidence returned for NLP research questions compared with lexical/vector-only or graph-only retrieval?

**RQ2 — Grounding:** How reliably does DiscoveryAI attach generated claims to valid retrieved paper/chunk references, and how often does it emit unsupported or untraceable claims?

**RQ3 — Candidate opportunities:** Can the full pipeline produce corpus-bounded candidate research opportunities that satisfy predeclared structural and evidence-grounding criteria?

**RQ4 — Component contribution:** How do vector retrieval, graph retrieval, the research critic, temporal signals, and Discovery Score affect retrieval, grounding, and output completeness under controlled ablations?

**RQ5 — Usability/utility (exploratory):** Can a student researcher use the interface to inspect source papers, compare evidence, and export a reproducible opportunity report? This is assessed through functional task walkthroughs and transparent limitations, not fabricated user-study data.

## 5. Proposed contribution and falsifiable hypotheses

**Engineering/method contribution:** An integrated, provenance-aware NLP research-opportunity workflow that combines hybrid vector/graph retrieval, evidence checks, temporal context, and critic-based challenge into one reproducible application.

**H1 (retrieval):** Hybrid retrieval will improve at least one predeclared retrieval metric (e.g., Recall@K or nDCG@K) over the selected single-retriever baseline on a compatible public NLP retrieval benchmark. This is a hypothesis to test, not a result.

**H2 (grounding):** Evidence validation and the research critic will reduce the proportion of output claims without resolvable source references compared with the corresponding disabled-component variants, without silently increasing inconclusive/failure outputs.

**H3 (component contribution):** Removing one or more retrieval/critic/temporal/scoring components will measurably change the corresponding predeclared output or retrieval metrics. Direction and magnitude are empirical questions.

No hypothesis is accepted until a real run, with its configuration and artifacts, has been validated.

## 6. Evaluation design — two separate tracks

### Track A: established NLP task benchmarks

Select public benchmarks only after verifying:
- the canonical dataset card or publisher/source;
- the exact dataset version/configuration and split;
- license/terms and permitted use;
- task compatibility with the implemented component;
- official metrics and evaluation procedure;
- availability without paid access.

Potential task families to investigate (not pre-approved datasets): scientific-document retrieval, passage retrieval, scientific QA, and semantic similarity. Do not use a benchmark merely because its name is familiar. The selection protocol must document why each dataset matches the specific task and the actual license/terms. If no appropriate free/usable benchmark is verified, report that limitation and use clearly labelled engineering tests rather than inventing benchmark scores.

Track A measures task-specific capabilities only. A retrieval benchmark does not prove research-gap quality.

### Track B: DiscoveryAI-specific workflow checks

Evaluate:
- schema validity and required output fields;
- evidence reference resolvability against the exact indexed snapshot;
- source-paper coverage and duplicate citation rate;
- unsupported/untraceable claim rate under an explicitly defined automated proxy;
- contradiction handling and uncertainty behavior;
- reproducibility of identical configured runs where deterministic behavior is expected;
- latency, failures, token usage/cost where measurable.

Automated proxies and synthetic fixtures are not expert judgments. No human-annotated gap-quality score, inter-annotator agreement, or gold-standard discovery-quality metric will be claimed in this project track.

## 7. Dataset and rights policy

- Metadata discovery does not confer rights to download, store, redistribute, or text-mine full text.
- A reachable URL, repository presence, or OpenAlex OA/license field alone is not sufficient permission evidence.
- Full-text ingestion is allowed only when the exact source/version has documented permission compatible with the intended processing and storage.
- If rights are unclear, use permitted metadata/abstract only where terms allow, or exclude the item from full-text processing.
- Do not publish copyrighted full-text PDFs or private credentials in repository artifacts.
- Preserve source, retrieval timestamp, identifier, version, license/permission evidence reference, and checksums where legally permitted.

## 8. System boundary and deliverable

The finished student project includes:
1. Next.js research dashboard.
2. FastAPI backend and documented APIs.
3. NLP paper metadata/corpus ingestion with rights-aware full-text gating.
4. Vector, graph, and hybrid retrieval.
5. Evidence-grounded synthesis, candidate-gap generation, critic, hypothesis and report generation.
6. Five comparable system configurations: LLM-only, vector RAG, graph RAG, hybrid retrieval, full DiscoveryAI.
7. Six controlled ablation configurations.
8. Automated task benchmark adapter(s) where license/task fit is verified.
9. Evaluation reports, run manifests, error analysis, and limitations.
10. Reproducible setup, test, deployment, and demo documentation.

## 9. Explicit non-goals and claim boundaries

The project will not claim:
- MBZUAI affiliation, endorsement, certification, or equivalence.
- Globally novel research discoveries.
- Expert-validated gap quality or human-reviewed corpus eligibility.
- Independent gold benchmark labels or inter-annotator agreement.
- Superiority unless a fair, valid, completed comparison supports it.
- Reproducibility or deployment success unless verified on the stated commit/environment.

## 10. Phase 1 exit criteria

- [x] NLP-only domain and scope stated.
- [x] Problem statement and five research questions stated.
- [x] Falsifiable hypotheses and claim boundaries stated.
- [x] Evaluation separated into public task benchmarks and DiscoveryAI workflow proxies.
- [x] Rights-aware data policy stated.
- [x] Student-project deliverables and non-goals stated.
- [ ] Closest-work/related-work search strategy and benchmark candidates documented with source/terms verification.
- [ ] Architecture-to-requirements mapping and measurable feature acceptance criteria reviewed.
- [ ] Phase 1 scope document merged to main.

Phase 1 is complete only after all applicable exit criteria have evidence. The checkboxes above distinguish completed scope decisions from remaining documentation/repository work.
