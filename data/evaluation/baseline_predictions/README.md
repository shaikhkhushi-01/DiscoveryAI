# Baseline prediction files

Place one JSON prediction file per system here. Files must use the P4.2 prediction contract in `discovery_gap_bench_predictions_template.json`.

Required system IDs:
- `llm_only`
- `vector_rag`
- `graph_rag`
- `hybrid_retrieval`
- `discoveryai_full`

All five files must use the same adjudicated benchmark version, corpus snapshot, split, record IDs, and evidence-item budget. Record actual model/provider, prompt, embedding, retrieval, system version, and code revision in every file. Do not copy one system's predictions and relabel them as another baseline. Store generated outputs with the experiment artifacts and preserve raw outputs for audit.
