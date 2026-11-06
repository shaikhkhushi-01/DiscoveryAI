# DiscoveryGapBench Annotation Rubric v1.0

## Purpose and unit of annotation

Each record binds one research question and one candidate gap to a frozen corpus snapshot. Annotators judge only what is supported by the supplied corpus and evidence passages. Do not infer global novelty from an incomplete or bounded collection.

## Independent annotation and adjudication

1. Two qualified annotators independently review the same question, candidate, corpus scope, and evidence.
2. Annotators assign ratings independently and provide a short rationale for every evidence passage and assessment.
3. Disagreements are preserved; an adjudicator records the resolution in `adjudication_notes`.
4. A record is score-eligible only after adjudication. Pending records remain valid draft annotations but must not enter scored benchmark runs.
5. Use pseudonymous annotator IDs; do not store names, email addresses, or other personal identifiers in the benchmark.

## Rating scale

Use integer ratings from 0 to 3. Record the rationale and apply the scale consistently.

| Rating | General interpretation |
|---|---|
| 0 | No support / not demonstrated in the supplied corpus |
| 1 | Weak or indirect |
| 2 | Moderate / relevant but incomplete |
| 3 | Strong / direct |

For `novelty_within_corpus`, a higher score means the candidate appears less directly addressed within the frozen corpus, not that it is globally novel. For `relevance`, `feasibility`, and `evidence_quality`, a higher score means stronger relevance, feasibility, or evidence quality.

## Gap status

- `supported`: evidence supports the existence of the stated opportunity within the corpus scope.
- `contradicted`: evidence substantially addresses or refutes the proposed gap.
- `inconclusive`: evidence is mixed, sparse, indirect, or insufficient to decide.

## Evidence annotation

Every evidence item must identify `paper_id`, `document_id`, and `chunk_id`, assign relevance 0–3, and explain why the passage supports or challenges the candidate. Each paper ID must belong to the record's corpus snapshot. Preserve both supporting and contradictory evidence when present.

## Split and leakage control

Use train, validation, and test labels. Keep papers and near-duplicate versions from leaking across splits where feasible. Freeze the split before comparing systems. Do not tune prompts or thresholds against the test split.

## Scope and reporting

Always report corpus ID, snapshot date, number of records, adjudicated count, and annotation rubric version. Report inter-annotator agreement before adjudication where sample size permits. Never report aggregate benchmark scores when there are zero adjudicated records.
