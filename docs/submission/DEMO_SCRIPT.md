# DiscoveryAI Demonstration Script

**Target duration:** 7–9 minutes  
**Audience:** project evaluators, research supervisors, technical reviewers  
**Rule:** use a real uploaded paper and real API responses. If a dependency is unavailable or the corpus is empty, show the honest empty/error state rather than fabricated counts.

## Before the demo

- Confirm frontend and backend are reachable.
- Confirm PostgreSQL, Qdrant, Neo4j, and the configured LLM provider are reachable.
- Create a researcher account in the current database or sign in.
- Prepare one small, legally shareable research PDF.
- Upload and index it before the presentation if live indexing could exceed the demo time.
- Verify the document's extraction and indexing job status.
- Prepare a second paper only if it is genuinely indexed and can demonstrate cross-paper evidence.
- Do not show API keys, database URLs, access tokens, private PDFs, or personal data.

## 1. Problem and motivation — 45 seconds

"Scientific search helps researchers find papers, but identifying a defensible research opportunity requires more: understanding methods, datasets, experiments, limitations, and contradictory evidence. DiscoveryAI investigates whether combining scientific knowledge representation, hybrid retrieval, evidence validation, and a Research Critic can support that process within a defined corpus."

## 2. Product overview — 45 seconds

Show the dashboard. Explain that summary counts come from API endpoints. Explain any zero counts as an empty or not-yet-indexed corpus. Point out that trends and graph panels are not populated until verified live data is available.

## 3. Authentication and document ingestion — 90 seconds

- Sign in or create an account in the active database.
- Open Papers.
- Upload a small PDF.
- Show the document record, title/metadata, and extraction status.
- Explain checksum-based duplicate handling and the separation between upload/extraction and indexing.

## 4. Vector and graph indexing — 90 seconds

- Request indexing for the uploaded document.
- Show the indexing job state.
- Show vector status and knowledge-graph status independently.
- Explain Qdrant as semantic vector storage and Neo4j as scientific relationship storage.
- If either status is failed or pending, report that accurately; do not describe the index as complete.

## 5. Scientific search and grounded answers — 90 seconds

- Ask a question that is directly addressed by the uploaded paper.
- Show retrieved passages and source metadata.
- Explain the difference between retrieved evidence and generated synthesis.
- If only one paper is indexed, state that cross-paper reasoning is not yet demonstrated.

## 6. Research-gap detection and Research Critic — 90 seconds

- Open candidate research gaps.
- Select a candidate and run the critic.
- Show supporting and contradictory evidence, the verdict, and its scope.
- Emphasize that "supported candidate" means supported within the indexed corpus, not globally novel.
- If no candidates are returned, explain that the current corpus does not support a candidate result.

## 7. Hypothesis and experiment planning — 60 seconds

- Generate a hypothesis from a supported candidate.
- Show variables, expected direction, and falsification condition.
- Show the proposed datasets, baselines, metrics, protocol, and ablations.
- State explicitly that the plan is a proposal and no experiment result is implied.

## 8. Evaluation and reproducibility — 60 seconds

Show the benchmark schema, annotation rubric, baseline/ablation runner, and run metadata. Explain that the evaluation refuses to score empty or unadjudicated gold data. Report measured scores only if actual adjudicated annotations and prediction artifacts exist.

## Closing — 20 seconds

"DiscoveryAI is an evidence-grounded research prototype. Its key research claim is framed as a hypothesis and will be tested using a frozen corpus, independent expert annotations, matched baselines, and controlled ablations. The system reports its corpus scope and limitations rather than claiming global novelty."
