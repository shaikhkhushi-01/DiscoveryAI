# DiscoveryAI Release Checklist

This checklist deliberately separates software readiness from scientific evidence. A passing CI pipeline does not establish research validity.

## A. Engineering release gate

### Repository and CI
- [ ] GitHub Actions CI passes on the exact release commit.
- [ ] Backend compilation succeeds.
- [ ] All backend tests pass, including `backend/tests/` regression tests.
- [ ] Frontend production build succeeds.
- [ ] Static release check succeeds.
- [ ] Docker Compose configuration validates.
- [ ] Dependency versions and deployment runtime are recorded.

### Runtime and integration
- [ ] Local six-service stack starts successfully.
- [ ] Alembic migrations apply successfully against a clean database.
- [ ] API and frontend start from documented instructions.
- [ ] Health endpoint responds; dependency health is checked separately.
- [ ] Authentication, authorization, token expiry, and protected-route behavior are verified.
- [ ] PDF upload, extraction, indexing, retrieval, critic, report, and hypothesis workflows pass end-to-end.
- [ ] Failure paths are tested for unavailable LLM, Qdrant, Neo4j, and PostgreSQL.
- [ ] Request IDs, sanitized errors, and useful operational logs are verified.

### Security and operations
- [ ] Production secrets are unique, strong, and stored only in the hosting secret manager.
- [ ] No secrets, tokens, reviewer identities, or private paper content are committed or logged.
- [ ] CORS is restricted to intended frontend origins.
- [ ] Public endpoints expose only intentionally public information.
- [ ] Upload size/type validation and storage permissions are verified.
- [ ] Database backups, retention, restore, and data deletion procedures are documented.
- [ ] Rate limits and abuse controls are defined for expensive LLM routes.
- [ ] Production dependency versions and vulnerability review are recorded.
- [ ] Monitoring, alerting, and incident/rollback procedure are documented.

### Product and UX
- [ ] Dashboard metrics are sourced from live endpoints or explicitly labelled illustrative.
- [ ] No placeholder chart, static graph, or demo count is presented as live research evidence.
- [ ] Empty, loading, partial-failure, and API-unavailable states are usable.
- [ ] Keyboard navigation, semantic labels, contrast, and responsive layouts are checked.
- [ ] API and user-facing terminology distinguish candidate gaps from expert-validated findings.

## B. Scientific validation gate

- [ ] A corpus snapshot and search protocol are frozen and versioned.
- [ ] Benchmark records have traceable paper/document/chunk provenance.
- [ ] Annotation rubric and inclusion/exclusion rules are locked before test annotation.
- [ ] Two independent, qualified reviewers annotate records blindly.
- [ ] Raw annotations are preserved; disagreements are adjudicated separately.
- [ ] Cohen's kappa / weighted kappa, raw agreement, prevalence, sample counts, and uncertainty are reported.
- [ ] Only adjudicated gold records enter scored splits.
- [ ] Train/validation/test split and leakage controls are documented.
- [ ] LLM-only, Vector RAG, GraphRAG, Hybrid RAG, and full DiscoveryAI use the same queries, corpus, split, and evidence budget.
- [ ] Planned ablations are executed with the same frozen evaluation conditions.
- [ ] Retrieval, gap ranking, evidence correctness, unsupported-claim rate, critic, hypothesis, and experiment-plan metrics are reported as applicable.
- [ ] Per-record errors, negative results, confidence intervals, and limitations are included.
- [ ] No global novelty or unsupported superiority claim is made.

## C. Release decision

- [ ] Engineering gate is signed off.
- [ ] Scientific gate is signed off, or release is explicitly labelled an unevaluated research prototype.
- [ ] Final report records code revision, model/provider/version, prompts, embedding model, retrieval config, corpus snapshot, benchmark version, split, and random seed.
- [ ] Release notes and known limitations are published.
