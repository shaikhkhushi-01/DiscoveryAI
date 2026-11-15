# DiscoveryAI: Evidence-Grounded Scientific Research Opportunity Discovery

**Project report — submission draft**  
**Codebase:** `shaikhkhushi-01/DiscoveryAI`  
**Report status:** Engineering and methodology draft; empirical results pending  
**Deployment targets:** Vercel frontend and Render FastAPI backend  
**Research scope:** Opportunities within an explicitly indexed scientific corpus

> **Integrity statement.** This report describes the implemented architecture and the evaluation methodology present in the repository. It does not claim that the system has discovered globally novel science, outperformed baselines, or passed a complete production end-to-end test. Benchmark results are intentionally marked pending until independently annotated gold data and reproducible prediction artifacts exist.

## Abstract

Scientific literature is expanding across papers, methods, datasets, tasks, metrics, and experimental settings. Conventional keyword search and retrieval-augmented generation help researchers locate relevant passages, but retrieval alone does not represent scientific relationships, systematically examine contradictory evidence, or validate whether a proposed research opportunity is sufficiently supported by a defined corpus.

DiscoveryAI is a research-oriented platform designed to investigate evidence-grounded research opportunity discovery. It combines PDF ingestion and scientific information extraction, relational metadata storage, vector retrieval, a scientific knowledge graph, hybrid retrieval and reranking, evidence validation, candidate research-gap detection, a Research Critic, literature synthesis, hypothesis generation, and experiment planning. The web application uses Next.js and TypeScript; the API uses FastAPI and Python; PostgreSQL stores application records; Qdrant stores semantic vectors; Neo4j represents scientific entities and relationships; and configurable language-model and embedding providers support extraction and reasoning.

The repository also contains a scientific evaluation framework: a versioned benchmark schema, adjudicated-gold evaluation runner, five-system baseline comparison, component ablations, expert-agreement analysis, and reproducibility metadata. These components define how the system should be evaluated, but the repository does not currently contain a populated independently annotated benchmark with reportable scores. The central research question is therefore framed as a testable hypothesis rather than a demonstrated result: whether structured scientific context, hybrid retrieval, evidence validation, and a Research Critic improve the quality and traceability of candidate research opportunities over simpler baselines.

## 1. Problem statement

Researchers must synthesize a growing and heterogeneous literature. A search engine can retrieve documents, and a standard RAG system can generate an answer from retrieved passages, but neither capability by itself establishes that a research gap exists. Gap discovery requires examining which problems are addressed, which methods and datasets are used, which metrics and experimental settings are reported, what limitations are repeated, and whether apparently missing work is contradicted by other papers.

The system addresses the following problem:

**Given a research question and a bounded, versioned corpus of scientific documents, can an AI system identify candidate research opportunities, support or challenge each candidate with traceable evidence, communicate uncertainty, and propose falsifiable hypotheses and reproducible experiments?**

The system must not infer global novelty from a finite or incomplete corpus. Its claims are scoped to the indexed documents, their extraction quality, and the search protocol.

## 2. Objectives

1. Ingest PDF research papers and preserve document metadata and extracted text.
2. Extract structured scientific information such as methods, datasets, topics, problems, applications, and metrics.
3. Build a semantic vector index and a graph of scientific entities and relationships.
4. Retrieve relevant evidence through hybrid semantic, lexical, graph, and reranking stages.
5. Identify candidate research gaps and validate them against supporting and potentially contradictory evidence.
6. Provide a skeptical Research Critic that distinguishes supported candidates, contradicted claims, and cases requiring review.
7. Generate source-aware literature synthesis, hypotheses, and experiment plans.
8. Define reproducible evaluation against adjudicated expert annotations, baselines, and ablations.
9. Deliver a documented, inspectable web application and reproducible local development setup.

## 3. Research questions and hypotheses

### RQ1 — Scientific extraction
How accurately can the pipeline extract scientific entities and metadata from PDF papers?

### RQ2 — Hybrid retrieval
Does combining vector, lexical, and graph retrieval improve evidence recall and ranking over a single retrieval strategy?

### RQ3 — Candidate gap validation
Does explicit evidence validation and Research Critic review reduce unsupported candidate-gap claims?

### RQ4 — Research planning
Can the system generate hypotheses and experiment plans that experts judge relevant, feasible, falsifiable, and appropriately grounded?

### Testable hypotheses
- **H1:** Hybrid retrieval will improve retrieval quality over vector-only and graph-only retrieval on a frozen, expert-labelled corpus.
- **H2:** The Research Critic and evidence-validation stages will reduce unsupported candidate-gap claims relative to an uncriticized generation pipeline.
- **H3:** The full system will produce higher expert-rated evidence quality and testability than an LLM-only baseline.

These hypotheses remain unconfirmed until the evaluation protocol is executed on valid gold data.

## 4. Related-work context

The repository's existing research review discusses the following research areas:

- **Retrieval-Augmented Generation:** Lewis et al. (2020), *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. RAG combines a language model with retrieved external evidence. It motivates evidence-conditioned answers, while leaving corpus-level scientific structure and gap validation as additional tasks.
- **Knowledge graphs:** Structured entity and relation representations can make relationships among papers, methods, datasets, problems, and metrics explicit. They complement rather than replace text retrieval.
- **Graph-based retrieval and GraphRAG:** Graph context can expand retrieval beyond lexical similarity, but the usefulness of graph expansion depends on extraction and graph quality.
- **Scientific information extraction and hypothesis generation:** Structured extraction and generative systems can support literature synthesis, but generated statements require provenance, contradiction checks, and expert evaluation.
- **Research trend analysis:** Temporal aggregation can expose changes in corpus activity, but counts and trends are sensitive to corpus coverage and metadata quality.

This is a focused background review, not a completed systematic literature review. Before publication, the related-work section must be expanded with current primary sources, dated search strings, databases, inclusion/exclusion criteria, and a documented screening process. No novelty claim is made solely from combining established components.

## 5. Methodology and system design

### 5.1 Document ingestion and extraction
The authenticated document API accepts PDF uploads, validates the file, computes a checksum for duplicate detection, parses text and metadata, extracts sections/references/tables/figures, and requests structured scientific extraction. Document and paper metadata are persisted in PostgreSQL. An indexing job is then queued separately from the web request.

### 5.2 Scientific representation
PostgreSQL stores application entities and document metadata. Qdrant stores embeddings for document chunks and supports semantic similarity search. Neo4j stores paper nodes and linked entities such as authors, institutions, datasets, methods, topics, problems, applications, and metrics. The graph provides structural context for retrieval and gap analysis.

### 5.3 Hybrid retrieval and scientific answers
The retrieval pipeline combines vector similarity, keyword matching, graph search/expansion, fusion, and reranking. The RAG answer service uses retrieved evidence to construct scientific answers. Answers should preserve source identifiers and distinguish retrieved evidence from model-generated synthesis.

### 5.4 Gap detection and evidence validation
Graph-derived candidates are checked against retrieved evidence. The evidence layer records supporting and potentially contradictory signals and computes a heuristic opportunity score. The Research Critic reviews candidate claims using indexed-corpus evidence and returns a bounded verdict. A supported candidate means the corpus contains specific supporting context; it does not prove global novelty. Ambiguous or contradictory cases should be sent for human review.

### 5.5 Hypothesis generation and experiment planning
The hypothesis service generates testable proposals from candidate opportunities and evidence. Experiment plans specify objectives, candidate datasets, baselines, metrics, protocol steps, and ablations. The API explicitly marks proposed experiments as not run; the platform must never present proposed outcomes as measured results.

## 6. Implementation and technology

| Layer | Implementation |
|---|---|
| Frontend | Next.js, React, TypeScript |
| Backend | Python 3.12, FastAPI, Pydantic |
| Authentication | Password hashing, JWT bearer tokens, researcher role |
| Relational database | PostgreSQL, SQLAlchemy, Alembic |
| Vector database | Qdrant |
| Knowledge graph | Neo4j |
| LLM | Configurable provider abstraction, including Gemini |
| Embeddings | Configurable embedding provider |
| PDF processing | PyMuPDF and deterministic extraction utilities |
| Evaluation | pytest, benchmark runner, baseline and ablation CLIs |
| CI | GitHub Actions |
| Deployment target | Vercel frontend, Render backend |

The current public deployment configuration is documented in the root README. A healthy API process does not by itself verify all external dependencies or user journeys.

## 7. Scientific evaluation plan

### 7.1 Benchmark construction
Create a frozen corpus snapshot and benchmark records containing a research question, candidate gap, corpus identifiers, evidence provenance, expert assessments, split, rubric version, and adjudication state. Two qualified reviewers should independently annotate each scored record while blinded to model predictions. Disagreements must be preserved and adjudicated. Starter templates are not gold labels and must not be scored as completed data.

### 7.2 Baselines
The implemented comparison harness expects five systems under the same benchmark, corpus snapshot, split, record IDs, and evidence budget:
1. LLM-only
2. Vector RAG
3. GraphRAG
4. Hybrid retrieval
5. Full DiscoveryAI

### 7.3 Ablations
The implemented ablation harness compares the full system with variants removing vector retrieval, graph retrieval, the Research Critic, temporal signals, or the Discovery Score.

### 7.4 Metrics
- Retrieval: Recall@K, Precision@K, MRR, nDCG@K.
- Extraction: precision, recall, F1, schema validity, unsupported extraction rate.
- Gap assessment: status accuracy, macro-F1, precision@K, recall@K, nDCG, false discovery rate.
- Evidence: evidence precision/recall/F1, citation correctness, stance accuracy, unsupported-claim rate.
- Critic: per-class precision/recall/F1 and calibration where sample size permits.
- Expert assessment: relevance, feasibility, evidence quality, novelty within corpus, raw agreement, Cohen's kappa, and weighted kappa for ordinal ratings.
- Hypothesis and experiment plan: expert-rated testability, falsifiability, completeness, reproducibility, and baseline/metric appropriateness.

### 7.5 Reproducibility
Every run must record code revision, model/provider/version, prompt version, embedding model, retrieval configuration, corpus snapshot, benchmark version, split, random seed, and run ID. Per-record predictions and errors must be retained. Confidence intervals should be reported only where sample size and design justify them.

## 8. Results and current evidence

**No scientific performance results are reported in this draft.** The benchmark framework and comparison tooling exist in the repository, but a populated, independently annotated and adjudicated gold dataset and corresponding system prediction files have not been verified. Therefore:
- No baseline is claimed to be best.
- No ablation effect is claimed.
- No expert agreement statistic is claimed.
- No global novelty claim is made.

Engineering evidence must be reported separately. The current PR #55 CI run has repository and frontend jobs completed successfully; the backend job was still running at the time of this report snapshot. Production end-to-end tests for PDF upload, extraction, Qdrant indexing, Neo4j indexing, and source-grounded answer generation remain to be completed.

## 9. Limitations and failure analysis

1. **Corpus coverage:** missing papers can create false candidate gaps; conclusions are bounded by the indexed corpus.
2. **PDF quality:** scanned, malformed, multi-column, or publisher-formatted PDFs can impair parsing.
3. **Extraction errors:** incorrect entities or relationships can propagate into the graph and retrieval.
4. **Vector/graph availability:** external services may be unavailable, asleep, quota-limited, or misconfigured.
5. **LLM variability:** model outputs may be inconsistent, incomplete, or unsupported despite prompting.
6. **Evidence relevance:** semantically related passages may not directly address the specific gap claim.
7. **Temporal bias:** publication metadata and corpus collection windows can distort trends.
8. **Benchmark validity:** expert judgements depend on reviewer expertise, rubric clarity, and adjudication.
9. **Operational constraints:** free-tier services may have cold starts, quotas, storage limits, and resource ceilings.
10. **Security and privacy:** production readiness requires verified secret rotation, access control, upload limits, retention, backup, and deletion procedures.

A release must document observed failures and negative results rather than hiding them.

## 10. Conclusion

DiscoveryAI implements a modular platform and a research-evaluation framework for evidence-grounded scientific opportunity discovery. Its proposed contribution is a testable pipeline that combines scientific structure, hybrid retrieval, evidence validation, temporal context, and skeptical review. The codebase provides a foundation for evaluating this approach, but scientific validation requires a real expert-annotated benchmark, controlled baseline and ablation runs, and end-to-end deployment evidence. Until those gates are satisfied, the correct classification is an advanced research prototype rather than a scientifically validated discovery system.

## References and further reading

- Lewis, P. et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. NeurIPS.
- Additional primary literature on scientific knowledge graphs, GraphRAG, scientific information extraction, literature-based discovery, and hypothesis generation must be added after a documented systematic search.

## Appendix A — Reproduction entry points

See the root README for environment setup, API routes, local execution, and CLI commands. The main evaluation entry points are:
- `scripts/evaluation/validate_discovery_gap_bench.py`
- `scripts/evaluation/run_discovery_gap_bench.py`
- `scripts/evaluation/compare_discovery_gap_baselines.py`
- `scripts/evaluation/run_discovery_gap_ablations.py`
- `scripts/evaluation/analyze_expert_agreement.py`
- `scripts/evaluation/release_check.py`
