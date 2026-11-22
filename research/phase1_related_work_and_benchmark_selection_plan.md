# Phase 1 — Related-work and benchmark selection plan

**Status:** Search and selection protocol; no dataset is approved and no literature review is claimed complete.

## 1. Related-work search objective

Position DiscoveryAI against the closest work in:
1. Literature-based discovery and scientific discovery systems.
2. Scientific document retrieval and scientific question answering.
3. GraphRAG and knowledge-graph-enhanced retrieval.
4. Evidence-grounded RAG and citation/attribution evaluation.
5. Research-gap detection, trend analysis, and hypothesis generation.
6. Evaluation of LLM factuality, faithfulness, and retrieval quality.

## 2. Search sources and reproducibility

Use public scholarly indexes and publisher/conference archives as discovery sources, prioritizing:
- ACL Anthology for NLP conference/journal papers.
- OpenAlex for broad scholarly metadata and citation relationships.
- arXiv for preprints, with published-version linking.
- Crossref for DOI metadata.
- Official project/paper pages for method and benchmark documentation.

For every search, record:
- source/index and interface/API;
- exact query string and filters;
- retrieval date/time (UTC);
- date range and language filters;
- result count and export identifier/checksum;
- inclusion/exclusion reason;
- duplicate and version-family resolution;
- whether full text was actually inspected and whether its reuse rights were verified.

Searches are discovery evidence, not proof of exhaustive coverage. State coverage limitations.

## 3. Inclusion criteria for related work

Include work that materially informs one or more of the six topic areas in Section 1 of the scope document. Prefer peer-reviewed full papers for claims about established methods; preprints may be included when clearly labelled and version-linked. Exclude unrelated domains, marketing claims, incomplete abstracts when full-text claims are required, and duplicate versions (while retaining version provenance).

Create a comparison table with columns:
- citation and stable identifier;
- publication/version status;
- problem/task;
- data/benchmark;
- retrieval/graph/LLM methods;
- evidence and evaluation metrics;
- limitations acknowledged by authors;
- relation to DiscoveryAI;
- what is distinct vs reused.

Do not state novelty until the closest-work comparison is actually completed.

## 4. Public benchmark selection gates

A candidate benchmark is eligible only if all gates are documented:
1. **Task fit:** task directly measures a component DiscoveryAI implements.
2. **Canonical provenance:** official dataset card, paper, publisher, or maintainer source identified.
3. **Terms:** explicit license or terms reviewed for access, processing, derived outputs, and redistribution; unknown terms mean do not include.
4. **Versioning:** exact version/configuration/split can be pinned.
5. **Evaluation:** official metric and scoring procedure are available.
6. **No leakage:** benchmark data are not already inadvertently mixed into tuning/indexing in a way that invalidates the intended test.
7. **Feasibility:** can be obtained and evaluated within zero budget and available compute.
8. **Reporting:** dataset citation, license/terms, retrieval date, checksum, and any restrictions can be recorded.

A benchmark may be usable for local evaluation while its data cannot be redistributed. Keep raw data outside public artifacts where required.

## 5. Candidate task families to investigate (not approvals)

- Scientific paper / passage retrieval: evaluate retrieval ranking using Recall@K, MRR, and/or nDCG as defined by the benchmark.
- Scientific question answering: evaluate answer correctness using the official task metric and a separate evidence-grounding check.
- Semantic similarity or classification: only if the benchmark directly matches an implemented NLP module and its label/task assumptions.

Do not force a research-gap detection claim onto a dataset designed for unrelated tasks. Public QA or retrieval benchmarks can validate those components, not the full research-gap generation capability.

## 6. Benchmark decision register

Create one row per candidate with:
- benchmark name and canonical URL;
- paper/card citation;
- task and exact subset/config;
- version/date;
- license/terms URL and conclusion (approved / not approved / unclear);
- permitted actions and restrictions;
- official metrics;
- split and leakage assessment;
- download/access method;
- estimated storage/compute;
- final decision and rationale;
- reviewer/date for internal terms check.

No benchmark should be described as selected until its canonical terms and task fit have been checked.

## 7. Phase 1 deliverables

- Search log with exact queries and retrieval timestamps.
- Closest-work comparison matrix.
- Benchmark decision register with explicit approved/rejected/pending statuses.
- A short novelty-positioning statement supported by the completed comparison (or a statement that novelty remains unresolved).

This plan does not itself establish that a search was performed, any benchmark was licensed, or any novelty claim is supported.
