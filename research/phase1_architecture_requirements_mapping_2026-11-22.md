# DiscoveryAI — Phase 1 architecture-to-requirements mapping

**Status:** Design-level mapping based on the repository's existing architecture and code surfaces. This document does not assert every mapped component is end-to-end verified.

## 1. End-to-end target flow

Research question -> API validation / research workflow -> NLP corpus metadata + rights gate -> permitted document/abstract ingestion -> parsing / chunk IDs / provenance -> embeddings -> Qdrant -> entity/relation extraction -> Neo4j -> lexical/vector/graph/hybrid retrieval -> evidence filtering + reranking -> synthesis + research critic -> candidate gap + contradiction/uncertainty assessment -> hypothesis + experiment plan + report -> dashboard evidence inspection / export -> evaluation run manifest + benchmark/proxy reports.

## 2. Layer map

| Layer | Current intended technology/service | Responsibility | Main acceptance evidence |
|---|---|---|---|
| Presentation | Next.js / React / TypeScript | Search, paper explorer, graph, gap/hypothesis/report and evaluation views | Build passes; pages use live API data; loading/error/empty states work |
| API | FastAPI / Pydantic | Request validation, auth, research/document/evaluation endpoints | Contract tests, auth tests, dependency-failure tests |
| Workflow/services | Python application services | Orchestrate ingestion, retrieval, synthesis and reports | End-to-end service tests with isolated dependencies |
| LLM | Provider factory / configured Gemini path | Structured synthesis, candidate gap and hypothesis generation | Schema validation, timeout/retry/failure handling, prompt/version manifest |
| Embeddings | Embedding provider factory | Embed permitted paper/abstract/chunk text and queries | Dimension/model consistency and reproducible index metadata |
| Vector store | Qdrant | Dense retrieval over permitted indexed material | Recall/ranking test and resolvable document/chunk provenance |
| Knowledge graph | Neo4j / graph-RAG services | Store and traverse paper/topic/method/dataset relations | Graph query tests; graph-only evidence must resolve to source records |
| Relational metadata | Supabase/Postgres | Users, jobs, paper/document metadata, run metadata | Migration, constraints, backup/restore and integration tests |
| Corpus workflow | OpenAlex metadata collector + rights queue/acquirer | Candidate discovery, enrichment, dedup/version tracking, explicit full-text approval | Rights-pending blocks acquisition; manifest/checksum reproducible |
| Evaluation | Prediction adapters, benchmark/ablation runners and packager | Generate comparable predictions, validate, score and archive manifests | Same task/split/config controls; real benchmark run artifacts |
| Deployment | Vercel frontend + Render backend (existing deployment targets) | Serve application | Production health/API/browser smoke tests on exact release SHA |

## 3. Requirement traceability

| Requirement IDs | Architecture components | Acceptance tests / artifacts |
|---|---|---|
| RQ-01 to RQ-04 | Corpus workflow, metadata DB, provenance layer | Scope check, DOI dedup/version tests, rights fail-closed tests, manifest checksum |
| RQ-05 to RQ-06 | Upload/parser, document store, chunk identity | Valid/invalid PDF tests; evidence reference resolution |
| RQ-07 to RQ-09 | Embedding provider, Qdrant, Neo4j, hybrid fusion/reranker | Retrieval ranking tests, graph provenance tests, hybrid result contract |
| RQ-10 to RQ-13 | Synthesis, evidence validator, critic, gap/hypothesis/experiment services | Grounding/contradiction/abstention tests; no unsupported IDs; bounded claim language |
| RQ-14 to RQ-15 | Five-system adapters and six ablation adapters | Distinct component paths, identical inputs, artifact schema and metadata checks |
| RQ-16 to RQ-17 | QASPER adapter (planned), evaluation validators, proxy evaluator | Official QA/evidence metric; schema/traceability/failure proxy report |
| RQ-18 | Run packager and artifact manifests | Code/data/model/prompt/config/split hashes, timestamps and reproducible CLI |
| RQ-19 | Next.js dashboard and API | User can navigate full workflow without dead ends |
| RQ-20 to RQ-21 | FastAPI, auth, upload, deployment config | Contract/security/integration tests and production smoke checks |
| RQ-22 | Documentation and release packaging | Reproducible setup, methodology, data cards, limitations, demo and release SHA |

## 4. Scope corrections

The existing architecture document describes a broad scientific platform. For the student-project release, the scope is narrowed to NLP/language-model literature. Medical/biomedical discovery, general science, and other non-NLP domains are not release targets.

The five-system DiscoveryGapBench adapters currently expect the repository's own DiscoveryGapBench record contract. QASPER is a separate QA/evidence-selection task. It requires a dedicated adapter and official metric implementation; it must not be passed directly to the gap-status evaluator or treated as an annotated research-gap benchmark.

## 5. Known integration risks to resolve in implementation

1. Graph-only retrieval may return graph metadata without source chunk text; evidence must resolve before generation/citation.
2. The existing discoveryai_full baseline path uses research synthesis sources; verify component parity before claiming it represents all full-system components.
3. Five-system gap predictions require DiscoveryGapBench records; because human annotation is out of scope, do not manufacture gold gap labels. Keep that comparison as engineering prediction generation/proxy analysis unless a valid public gap benchmark is found.
4. QASPER requires a separate paper-QA/evidence-selection evaluator and paper-level split handling.
5. LLM-as-judge metrics need model/prompt disclosure and are exploratory proxies, not independent ground truth.
6. Free-tier hosted services may sleep, rate-limit or impose storage/compute constraints; report actual availability and costs rather than assuming continuous operation.

## 6. Phase 1 exit criteria mapping

- Scope/research questions/hypotheses: phase1_student_project_scope_2026-11-22.md
- Related-work review/positioning: phase1_related_work_review_2026-11-22.md
- Benchmark decision/terms: phase1_benchmark_decision_register_2026-11-22.md
- Architecture/acceptance mapping: this document and phase1_requirements_and_acceptance_criteria.md
- Overall phase decision: phase1_exit_status_2026-11-22.md
