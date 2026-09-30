# Days 31–40 — Paper Understanding V1

## Day 31 — OpenAI + provider switching
Added `OpenAIProvider`, configurable model/API key, and `get_llm_provider()` supporting Ollama/OpenAI without changing extraction code.

## Day 32 — Entity extraction
Scientific extraction schema covers topics, keywords, methods, and algorithms.

## Day 33 — Scientific entities
Schema covers datasets, problems, applications, and domains.

## Day 34 — Evaluation extraction
Schema covers metrics, baselines, experimental settings, and results.

## Day 35 — Limitations
Limitations are returned with deterministic categories (`data`, `computational`, `generalization`, `evaluation`, `other`).

## Day 36 — Future work
Future directions are normalized into categories such as data, evaluation, extension, application, and research_direction.

## Day 37 — Structured scientific JSON
`ScientificDocument` validates metadata, entities, limitations, and future-work output using Pydantic.

## Day 38 — Extraction pipeline
PDF → parser → sections → LLM extraction → normalization/classification → structured scientific output.

## Day 39 — Extraction evaluation
Evaluation fixture format and deterministic schema/utility tests are included. Real-paper expert annotation is intentionally not fabricated; it must be populated from a labeled sample corpus.

## Day 40 — Paper Understanding V1
Authenticated extraction endpoint produces the structured paper-understanding payload from a stored PDF.

Runtime note: LLM and database execution requires configured local/hosted services and is not claimed as executed through GitHub repository tooling.
