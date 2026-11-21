# Day 4 — Ablation generation integration audit

**Date:** 2026-11-21  
**Status:** implementation blocker identified; no ablation predictions generated.  
**Scope:** NLP/language-model research pipeline only.

## Executive finding

The existing ablation comparison CLI is a report consumer, not a generation runner. The baseline prediction adapter added in PR #83 exposes five retrieval choices, but it does not expose the six predeclared ablation configurations. Adding six output filenames or changing `ablation_id` metadata would be relabelling, not component removal, and is explicitly rejected.

## Component-by-component inspection

| Predeclared removal | Current code path | Finding |
|---|---|---|
| `without_vector_retrieval` | `prediction_adapters._graph` calls `retrieve_graph_rag`; `_hybrid` calls `hybrid_search`; `_full` calls `synthesize_research`, which itself calls hybrid search | No vector-free DiscoveryAI prediction path is exposed. Graph RAG also starts from hybrid/vector retrieval. |
| `without_graph_retrieval` | Baseline `_full` calls `synthesize_research`; other adapters have their own retrievers | The full adapter currently uses hybrid synthesis and does not call the graph pipeline, so this ablation is not currently a distinct treatment of the full adapter. |
| `without_research_critic` | `critique_research_gap` is a separate service | Baseline prediction generation does not invoke the critic, so full-vs-without-critic would be identical on this dimension unless the benchmark prediction pipeline is redesigned to include it. |
| `without_temporal_signals` | `app.services.trends.temporal` exposes timeline/trend queries | The baseline prediction adapter does not consume temporal outputs or have a temporal feature switch. |
| `without_discovery_score` | Discovery-score fields exist in the database migration | The baseline prediction adapter does not compute or consume Discovery Score; no scoring decision path or feature switch was identified in the inspected path. |

## Required engineering work before a valid ablation run

1. Define one explicit, production-representative full DiscoveryAI prediction pipeline. It must state where vector retrieval, graph retrieval, research critic, temporal signals, and discovery score affect the prediction.
2. Add explicit typed feature switches at the actual component boundaries. Each switch must change the executed path, not only metadata.
3. Make each ablation use the same input records, model/provider, prompt, decoding, evidence/token budget, corpus/index snapshot, and seed wherever technically possible.
4. Record active and disabled component names, effective configuration, code revision, model configuration, corpus/benchmark IDs, and per-record trace/provenance in every artifact.
5. Add tests that spy on component calls and prove the disabled component is not invoked while required unaffected components remain invoked.
6. Add integration smoke tests using mocked component outputs, then separately validate against a rights-cleared frozen corpus and adjudicated benchmark.

## Safe execution rule

Do not generate the five ablation prediction artifacts yet. The current comparison evaluator correctly checks `ablation_id` and `disabled_components`, but those metadata checks cannot prove that the implementation actually disabled a component. No score, ablation effect, or component-contribution claim is made by this audit.

## Current blockers

- Day 2 corpus eligibility, rights review, duplicate/version resolution, and checksum freeze remain open.
- Day 3 independent reviewer pilot and adjudication remain open.
- The full-system prediction pipeline does not yet compose all five named components behind controllable interfaces.
- No genuine ablation prediction artifacts exist.
