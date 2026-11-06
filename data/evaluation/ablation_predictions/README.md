# Ablation prediction artifacts

Store independently generated JSON prediction files here: full.json, without_vector_retrieval.json, without_graph_retrieval.json, without_research_critic.json, without_temporal_signals.json, and without_discovery_score.json.

Each follows the P4.2 prediction schema and adds run_metadata.ablation_id and run_metadata.disabled_components. See research/phase4_ablation_study_protocol.md for controls and expected values.

Do not copy one prediction file six times or relabel outputs: every variant must be executed independently. Never commit credentials, unpublished manuscripts, or sensitive user data. This placeholder directory is not a benchmark result and must not be scored.
