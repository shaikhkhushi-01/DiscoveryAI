# Phase 5 — Scientific Validation Execution Runbook

## Purpose and integrity rule
This runbook coordinates the seven remaining scientific-validation workstreams. The repository currently contains evaluation code and starter templates, but starter templates are not observations, annotations, or benchmark results. Never report a metric until it has been computed from real, frozen inputs.

## Repository readiness snapshot
- Benchmark schema and starter template: `data/evaluation/discovery_gap_bench.schema.json`, `data/evaluation/discovery_gap_bench_template.json`.
- Blinded annotation exporter: `scripts/evaluation/export_blinded_annotation_packets.py`.
- Agreement analysis: `scripts/evaluation/analyze_expert_agreement.py`.
- Benchmark validation and scoring: `scripts/evaluation/validate_discovery_gap_bench.py`, `scripts/evaluation/run_discovery_gap_bench.py`.
- Baseline and ablation runners: `scripts/evaluation/compare_discovery_gap_baselines.py`, `scripts/evaluation/run_discovery_gap_ablations.py`.
- Run packaging: `scripts/evaluation/package_evaluation_run.py`.

The tracked `data/raw/` and `data/evaluation/` directories currently contain placeholders/templates rather than a populated, adjudicated benchmark. No expert labels or model scores are assumed to exist.

## Workstream sequence

### 1. Freeze corpus and construct candidate pool
1. Select the scientific domain and research-question scope.
2. Record corpus source, licensing/permission, retrieval date, inclusion/exclusion criteria, and immutable paper/document/chunk identifiers.
3. Freeze a corpus snapshot and record its manifest/checksum.
4. Generate candidate gaps from that snapshot; deduplicate candidates and preserve provenance.
5. Sample candidates across gap types and include plausible negative, contradicted, and inconclusive cases. Do not select only attractive system outputs.
6. Split by research question or paper/corpus grouping before model evaluation to reduce leakage. Keep the test labels inaccessible to system developers.

### 2. Expert-reviewed benchmark
1. Pilot the rubric on a small batch and revise it before locking a rubric version.
2. Create benchmark records using the schema and validator.
3. Ensure each record has a bounded research question, candidate claim, corpus snapshot, and resolvable evidence provenance.
4. Have two qualified reviewers independently annotate every score-eligible record.
5. Adjudicate disagreements without overwriting either original annotation.
6. Validate the final benchmark; only adjudicated records may enter scored evaluation.

### 3. Independent annotations and agreement
Export candidate-only blinded packets using the protocol in `research/phase4_expert_validation_protocol.md`. Give both reviewers equivalent source excerpts and the same locked rubric. Keep the blind-ID crosswalk private. Compute agreement before adjudication; report raw agreement, Cohen's kappa for nominal gap status, weighted kappa for ordinal ratings, sample counts, category prevalence, and confidence intervals where statistically defensible. Do not interpret kappa without its prevalence/sample-size context.

### 4. Five baseline experiments
Run LLM-only, Vector RAG, GraphRAG, Hybrid Retrieval, and Full DiscoveryAI against the same frozen benchmark, corpus snapshot, splits, query set, and comparable evidence budget. Pin model/provider, prompt, embedding, retrieval, reranking, and code versions. Save raw predictions and a run manifest for each system. Do not tune on the held-out test split.

### 5. Ablations
Run the predeclared component-removal variants in the ablation protocol. Change one component at a time where possible; preserve all other run settings. Record failures and non-improvements, not just favorable outcomes.

### 6. Statistical analysis
Use paired per-record comparisons because systems are evaluated on the same records. Report effect sizes, uncertainty intervals, sample counts, missing/failure rates, and multiplicity handling for multiple comparisons. Use tests appropriate to the metric and design; check assumptions. Treat underpowered or exploratory analyses as such. Include error slices by gap type, evidence availability, and corpus coverage.

### 7. Paper
Write the paper only after the benchmark, annotations, runs, and analyses are frozen. Include research questions, corpus construction, reviewer qualifications at an appropriately privacy-preserving level, annotation protocol, agreement, system configurations, metrics, statistical methods, results, error analysis, limitations, reproducibility artifacts, and conflicts/ethics/licensing. Never claim global novelty from a bounded corpus or imply institutional affiliation/endorsement without authorization.

## Reproducibility and artifact layout
Keep private licensed documents and reviewer identity crosswalks out of the public repository. Commit only data that may legally and ethically be shared. Suggested local/private structure:

```text
private-study/
  corpus-manifest.json
  candidate-records.json
  reviewer-a/annotations.json
  reviewer-b/annotations.json
  adjudication-log.json
  predictions/
    llm_only.json
    vector_rag.json
    graph_rag.json
    hybrid_retrieval.json
    discoveryai_full.json
  ablations/
  run-manifests/
  reports/
```

Use the existing CLIs and protocols; check each command's `--help` before running. Store the exact command, environment (excluding secrets), git commit, model identifiers, timestamps, corpus/benchmark/rubric versions, and output checksums in each run manifest.

## Hard stop conditions
- No real corpus/candidate data: do not create a benchmark score.
- Fewer than two independent reviewers: do not report dual-annotator agreement.
- Unadjudicated gold labels: do not score the official test benchmark.
- Incompatible corpus, split, or benchmark versions: reject the run.
- Missing baseline predictions: mark the comparison incomplete.
- Failed or missing runs: report them; do not silently drop them.
- No statistical support: describe findings as exploratory, not conclusive.

## Current completion state
This commit adds an execution plan only. It does not populate the benchmark, recruit experts, execute model runs, or establish scientific results. Those steps require a real domain corpus, human reviewers, and execution access to the configured model/data services.
