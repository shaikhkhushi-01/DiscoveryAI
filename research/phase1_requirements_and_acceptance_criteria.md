# DiscoveryAI — Requirements and acceptance criteria

**Status:** Proposed acceptance contract for the student-project release.

These criteria define observable behavior. A feature is not complete because a route, UI component, or class exists; its end-to-end acceptance test must pass.

| ID | Requirement | Acceptance evidence |
|---|---|---|
| RQ-01 | NLP-only research scope | Scope document and UI/docs consistently describe NLP/language-model domain |
| RQ-02 | Source provenance | Every indexed paper has stable ID, source URL, version, retrieval timestamp, and permitted metadata |
| RQ-03 | Rights-aware full-text ingestion | Missing/unclear permission blocks full-text acquisition; positive path requires recorded evidence |
| RQ-04 | Deduplication/version handling | DOI-first dedup plus normalized fallback; related versions linked without erasing provenance |
| RQ-05 | Paper/document ingestion | Valid permitted document is parsed; invalid/corrupt/oversized input fails safely with a clear error |
| RQ-06 | Evidence identity | Every returned chunk/evidence reference resolves to the exact stored document/chunk |
| RQ-07 | Vector retrieval | Query returns ranked, traceable results and a stable response schema |
| RQ-08 | Graph retrieval | Query returns graph-supported relations with provenance; unsupported graph-only claims are not invented |
| RQ-09 | Hybrid retrieval | Vector and graph results are fused with documented ranking/configuration and traceable source IDs |
| RQ-10 | Research synthesis | Output separates source-supported statements, inference, uncertainty, and missing evidence |
| RQ-11 | Candidate-gap generation | Each candidate is bounded to the indexed corpus/query and includes supporting/contradictory evidence or an inconclusive state |
| RQ-12 | Critic | Critic can challenge unsupported/contradicted claims; failure to retrieve evidence produces an inconclusive response |
| RQ-13 | Hypothesis generation | Hypothesis includes rationale, evidence references, assumptions, and testable outcome; no global novelty claim |
| RQ-14 | Five-system comparison | Five configurations receive matched inputs/config and emit validated prediction artifacts with run metadata |
| RQ-15 | Ablation comparison | Six variants execute real component switches and emit exact disabled-component metadata |
| RQ-16 | Public benchmark evaluation | At least one task-compatible benchmark has verified terms, pinned split/version, official metric, and reproducible run; if no legal/feasible benchmark qualifies, document the blocker and do not invent scores |
| RQ-17 | Workflow proxy evaluation | Automated validators report evidence resolvability, schema validity, unsupported-reference proxies, failures, and limitations |
| RQ-18 | Reproducible experiment | Each run records commit, data/benchmark hashes, model/provider/version, prompt/config, timestamp, seed where applicable, environment, outputs, and failure reasons |
| RQ-19 | Dashboard | User can navigate paper search, paper details, evidence, graph, candidate gaps, hypotheses, and evaluation reports without dead ends |
| RQ-20 | API reliability | Health and core endpoints return documented schemas; invalid inputs and dependency failures return safe, actionable errors |
| RQ-21 | Security | No secrets in repository/logs; authz checks protect private routes; upload limits and CORS are verified |
| RQ-22 | Release package | README, architecture, data/benchmark cards, methodology, limitations, demo guide, and exact release commit are available |

## Evaluation metric definitions to lock before runs

- **Retrieval:** use the benchmark's official relevance labels and official Recall@K/MRR/nDCG definition; state K and query aggregation.
- **Evidence resolvability:** fraction of emitted evidence references that resolve to the exact indexed document/chunk and source version.
- **Citation coverage:** fraction of externally verifiable factual output claims carrying at least one resolvable source reference. If claim segmentation is heuristic, label it as such.
- **Unsupported-reference proxy:** proportion of emitted references that are missing, invalid, or do not match the indexed record. This does not measure semantic entailment.
- **Failure rate:** failed or invalid runs divided by all attempted runs; report exclusions and retries.
- **Latency:** wall-clock end-to-end time with warm/cold conditions stated.
- **Token/cost:** report only when provider exposes reliable usage; do not estimate as measured.

## Acceptance policy

- A passing unit test is evidence for the tested code path, not full system correctness.
- Synthetic fixtures are engineering tests, never public benchmark scores.
- A public benchmark result supports only the task and split actually evaluated.
- Research-gap quality remains exploratory without independent ground truth.
- Any failed criterion remains visibly open in the release report.
