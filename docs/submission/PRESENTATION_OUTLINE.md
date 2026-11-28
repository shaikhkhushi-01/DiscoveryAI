# DiscoveryAI Presentation Outline

**Recommended length:** 10 slides / 8–10 minutes

1. **Title** — DiscoveryAI: Evidence-Grounded Scientific Research Opportunity Discovery.
2. **Problem** — Literature growth, fragmented evidence, and why search alone does not validate a research gap.
3. **Research question and hypotheses** — RQ1–RQ4; H1 hybrid retrieval, H2 critic/evidence validation, H3 expert-rated planning quality.
4. **System architecture** — Next.js 15 / React 19, FastAPI, PostgreSQL, Qdrant, Neo4j, Gemini/configurable LLM and embedding providers.
5. **Document intelligence** — PDF upload, parsing, scientific extraction, provenance, indexing job.
6. **Hybrid retrieval and grounded reasoning** — vector + lexical + graph retrieval, fusion, reranking, source-linked answer.
7. **Research intelligence** — candidate gaps, evidence validator, Research Critic, hypotheses, experiment plans.
8. **Scientific evaluation design** — DiscoveryGapBench, independent annotation, five baselines, component ablations, metrics.
9. **Current evidence and limitations** — show the verified Explore answer with 8 retrieved passages and working citation navigation; clearly separate this functional smoke test from benchmark results and pending expert validation.
10. **Conclusion and next steps** — bounded corpus claims, expert validation, reproducible experiments, roadmap.

## Slide integrity rules

- Do not invent screenshots, dataset sizes, benchmark scores, latency, or accuracy.
- Do not present an illustrative diagram as a live knowledge graph.
- Label proposed hypotheses and experiments as not yet run.
- Include corpus scope and known limitations on the results slide.


## Suggested live demo evidence

Use the verified public Explore query recorded in `docs/submission/EVALUATION_STATUS.md`. Capture screenshots only from the live deployed interface: (1) answer with citations, (2) grouped source/evidence list, and (3) the page after clicking Evidence 1. Label the capture date and do not present it as a benchmark result.
