# Phase 3 — Core AI research engine

**Date:** 2026-11-22  
**Scope:** NLP and scientific-paper literature analysis over the currently indexed corpus.

## Objective

Build a query-scoped research workflow that turns a research question into an evidence-bounded cross-paper synthesis, candidate research opportunities, falsifiable hypothesis proposals, and a skeptical critic assessment. This is a software capability milestone, not proof of scientific discovery quality.

## Existing capabilities reused

- Graph-RAG retrieval and hybrid vector/keyword ranking.
- Scientific paper extraction and normalization.
- Evidence validation and the research critic.
- LLM provider abstraction with structured JSON responses.
- Existing literature-review, comparison, gap, and hypothesis APIs.

## Phase 3 implementation in this PR

New authenticated endpoint:

`POST /api/v1/intelligence/discover`

Request:

```json
{
  "query": "How do retrieval-augmented language models handle evidence conflicts?",
  "limit": 12,
  "max_candidates": 3
}
```

Pipeline:
1. Retrieve a bounded set of Graph-RAG passages for the supplied question.
2. Deduplicate passages and cap each paper to two passages to reduce single-paper dominance.
3. Assign request-local evidence IDs and preserve paper/document/chunk provenance.
4. Require at least two distinct source papers before cross-paper gap or hypothesis generation.
5. Ask the configured LLM for themes, candidate gaps, falsifiable hypotheses, experiment proposals, disagreements, and limitations, using retrieved excerpts as its only factual source.
6. Drop gap/hypothesis items that lack at least two distinct cited papers or contain unknown evidence IDs.
7. Pass each candidate gap and the same retrieved evidence to the research critic.
8. Map critic source passages back to the original request-local evidence IDs. A critic acceptance is surfaced as supported only if at least two distinct critic sources map back to the original evidence set; otherwise it remains `needs_review`.
9. Return explicit indexed-corpus scope and proposal/novelty limitations.

## Safety and scientific-integrity rules

- No global novelty claim. The output is scoped to the indexed corpus and retrieved sample.
- No gap or hypothesis is generated when fewer than two distinct papers are retrieved.
- A gap/hypothesis needs valid citations from at least two distinct papers.
- Critic evidence IDs are remapped through source provenance rather than copied across independent evidence-ID namespaces.
- Critic `accept` is a bounded candidate assessment, not independent proof of novelty.
- Hypotheses and experiment plans are proposals, not established results.
- Model failure returns an explicit `generation_failed` state instead of fabricated output.
- The endpoint is authenticated and uses the existing provider configuration; no paid provider is mandated.

## Tests added

- Passage deduplication and per-paper diversity cap.
- Insufficient independent-paper coverage fails closed.
- Unknown citation IDs and one-paper gap claims are filtered.
- Hypothesis evidence and proposal disclaimers are retained.
- Critic citations map back to original retrieval evidence IDs.
- Retrieval provenance and corpus-scope metadata are returned.

## Acceptance criteria

- [x] Query-scoped research endpoint is wired into the existing authenticated intelligence router.
- [x] Retrieval provenance is preserved.
- [x] Cross-paper outputs require at least two distinct sources.
- [x] Unknown citation IDs are removed.
- [x] Critic source evidence is mapped to the original request evidence IDs.
- [x] Insufficient retrieval and model errors fail closed.
- [ ] Backend CI passes on the final PR commit.
- [ ] Live integration with configured embedding, vector, graph, database, and LLM services is verified.
- [ ] Output quality is evaluated on a locked, rights-compliant benchmark.

## Known limitations

- Retrieval relevance and completeness depend on the indexed corpus, embeddings, Qdrant, Neo4j, and current reranker.
- LLM-generated synthesis can still be wrong even when citations point to real retrieved passages; citations establish provenance, not entailment.
- The critic uses the same retrieved sample, so it is not an independent literature search.
- The 399-record OpenAlex pool remains provisional and is not a rights-cleared corpus.
- QASPER QA/evidence scores do not measure research-gap discovery or hypothesis quality.
- No real production credentials or connected services were exercised by unit tests.

## Manual API smoke test

After signing in and obtaining a normal user access token, send an authenticated request to `POST /api/v1/intelligence/discover` with the JSON request above. Do not paste tokens into issues, commits, or chat. If fewer than two distinct papers are retrieved, the expected status is `insufficient_evidence`; this is a safe outcome, not an error.
