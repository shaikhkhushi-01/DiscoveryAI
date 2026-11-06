# P4.4 — DiscoveryAI Ablation Study Protocol

## Purpose
Estimate the contribution of individual DiscoveryAI components by comparing the full system with controlled component-removal variants. This is a paired benchmark experiment, not a synthetic simulation.

## Predeclared variants
1. full: production DiscoveryAI configuration; no components disabled.
2. without_vector_retrieval: remove dense-vector retrieval.
3. without_graph_retrieval: remove knowledge-graph retrieval.
4. without_research_critic: bypass the Research Critic.
5. without_temporal_signals: remove temporal trend/recency signals.
6. without_discovery_score: remove Discovery Score from the decision path.

Every artifact must include standard P4.2 run metadata plus ablation_id and disabled_components. The full run has an empty disabled_components array; each ablation lists exactly its removed component.

## Controls
- Freeze benchmark version, rubric, corpus snapshot, test split, and record IDs.
- Hold model/provider, prompts, token budget, sampling settings, and retrieval limits constant except where the ablated component requires change.
- Record all unavoidable configuration changes and code revisions.
- Execute each variant independently; never relabel copied predictions.
- Tune only on train/validation. Do not inspect test gold labels during configuration.
- Prefer at least three predeclared random seeds and report every run.

## Metrics
Report status accuracy, macro-F1/confusion matrix, evidence precision/recall/F1/stance accuracy, and expert-rating MAE. Paired per-record full-minus-ablation deltas are included. Positive values favor full DiscoveryAI (MAE sign is inverted). Bootstrap intervals are descriptive, not proof of significance.

## Execution
Run scripts/evaluation/run_discovery_gap_ablations.py with --benchmark, --full, --without-vector-retrieval, --without-graph-retrieval, --without-research-critic, --without-temporal-signals, --without-discovery-score, --split test, and --output reports/evaluation/phase4-ablation-study.json.

The harness consumes independently generated prediction files; it does not execute the application pipeline. It fails closed for missing/mislabelled variants or mismatched gold corpus, split, or record IDs.

## Limitations
Component removals can alter downstream inputs and interactions; effects are not additive and do not establish isolated causal effects. Meaningful conclusions require an adjudicated benchmark with adequate sample size and independent variant runs. The starter benchmark is not score-eligible; this implementation makes no performance claims.
