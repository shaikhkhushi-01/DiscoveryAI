# Day 4 — Baseline runner integration audit

**Date:** 2026-11-21  
**Scope:** static repository audit of baseline execution and evaluation wiring.  
**Result:** evaluator plumbing is present; five-system prediction generation is not yet an executable, standardized pipeline.

## Verified implementation

- `run_discovery_gap_bench.py` evaluates one already-generated prediction JSON against an adjudicated benchmark.
- `compare_discovery_gap_baselines.py` compares five already-generated prediction JSON files. It does not invoke the five systems.
- `run_discovery_gap_ablations.py` compares six already-generated prediction JSON files. It does not disable components or generate outputs.
- `package_evaluation_run.py` hashes and packages an existing benchmark, prediction artifact and evaluation report.
- `runner.py` validates required metadata, exact selected-split record coverage, benchmark version, corpus ID, evidence references and rating/status fields.
- The synthetic end-to-end test exercises comparison CLI plumbing only. It is explicitly not research evidence.

## Integration gap

The evaluation scripts consume predictions as inputs. This audit did not find a single orchestrator/adapter contract that executes `llm_only`, `vector_rag`, `graph_rag`, `hybrid_retrieval`, and `discoveryai_full` on the same benchmark records and emits the required prediction artifacts with consistent provenance.

Consequently, the phrase “five baseline runners integrated” would be inaccurate. System implementations exist elsewhere in the application, but an auditable mapping from each baseline ID to a callable prediction-generation path, shared input contract, output serializer, and run-metadata builder remains to be implemented and tested.

## Fail-closed research gates

No scored baseline or ablation run is authorized until all of these are evidenced:

1. Day 2 corpus manifest is final, rights-cleared, version-resolved and SHA-256 frozen.
2. Gold benchmark has independently reviewed and adjudicated records, a frozen work-family split and a locked test set.
3. Each of the five systems has an explicit generation adapter and produces predictions for identical record IDs.
4. Each artifact passes the evaluator's schema, metadata, evidence provenance and coverage checks.
5. Model/provider/configuration, prompt, retrieval/index snapshots, commit, seed, runtime, token usage and failures are captured.
6. The five artifacts are compared only after the above checks pass.

## Day 4 disposition

| Criterion | Status | Evidence |
|---|---|---|
| Five-system comparison contract | PASS | Existing comparison CLI and baseline IDs |
| Prediction schema / metadata / record coverage validation | PASS | `runner.py` validation path |
| Synthetic comparison CLI smoke | PASS (engineering only) | `test_evaluation_pipeline_smoke.py` |
| Standardized five-system prediction-generation adapters | BLOCKED | No common generation orchestrator/adapter contract found |
| Genuine prediction artifacts | BLOCKED | No eligible frozen corpus and adjudicated benchmark |
| Scored baseline comparison | BLOCKED | Day 2 corpus and human adjudication gates remain open |
| Ablation generation and scored comparison | BLOCKED | Current CLI compares pre-generated artifacts; no execution adapter |

**Conclusion:** Day 4 protocol and evaluator plumbing are implemented and audited. Day 4 is not fully complete as an experiment milestone. The remaining work is concrete and must not be replaced with synthetic predictions or fabricated labels.
