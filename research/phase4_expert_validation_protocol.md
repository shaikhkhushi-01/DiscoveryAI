# P4.5 — Expert Validation Protocol

## Objective
Create a reproducible, blinded, dual-annotator process for validating candidate research gaps and their evidence against a frozen corpus snapshot.

## Annotation procedure
1. Freeze benchmark version, corpus snapshot/date, research question, candidate gap, and the exact source passages before annotation.
2. Assign two independent domain-qualified reviewers pseudonymous IDs. Reviewers must not see each other's labels or model predictions.
3. Export separate reviewer packets using `python scripts/evaluation/export_blinded_annotation_packets.py --candidates path/to/candidate-records.json --output-dir private/annotation-batch`.
4. Give each reviewer only their packet and the locked rubric. Keep `CONFIDENTIAL-blind-id-crosswalk.json` private; it maps blind IDs back to benchmark record IDs.
5. **Important:** the exporter removes gold assessments and gold evidence. It does not fetch or package full source passages. A study coordinator must separately supply the same licensed, page/chunk-identified source excerpts to both reviewers, with no model labels or generated explanations.
6. Each reviewer independently labels gap status (supported / contradicted / inconclusive), four 0–3 ratings (novelty within corpus, relevance, feasibility, evidence quality), and supporting/contradictory evidence tuples with a written rationale.
7. Do not ask reviewers to judge global novelty. Novelty is bounded to the frozen corpus and snapshot.
8. Compute agreement before adjudication. The analysis tool reports nominal Cohen kappa for status, quadratic weighted Cohen kappa for ordinal ratings, and evidence tuple precision/recall/F1 and stance agreement.
9. A third reviewer or a documented consensus meeting adjudicates every disagreement. Preserve original annotations; never overwrite them with consensus labels.
10. Transfer only adjudicated gold labels into the canonical DiscoveryGapBench record, set adjudication_status=adjudicated, identify both annotators, and add a concise adjudication note with decision rationale.
11. Keep test labels access-controlled. System developers may tune on train/validation only; test labels remain held out until final evaluation.

## Quality safeguards
- Use a pilot batch to refine rubric wording before locking rubric version.
- Report raw agreement, kappa, category prevalence, sample size, and confidence intervals where supportable. Kappa is unstable for small or imbalanced samples.
- Document reviewer expertise/conflicts and any exclusions in a separate controlled study log; do not store unnecessary personal data in the public repository.
- Include negative and contradictory evidence, not only evidence supporting a candidate gap.
- Maintain immutable raw annotation artifacts and a separate adjudicated benchmark export.
- Do not infer global novelty from an indexed-corpus benchmark.

## Tooling
Two JSON annotation files must each contain an annotator_id and annotations array. Each annotation includes record_id, assessment (gap_status and the four 0–3 ratings), and evidence (paper_id, document_id, chunk_id, stance). Both files must contain the same record IDs.

Run agreement analysis:
`python scripts/evaluation/analyze_expert_agreement.py --annotator-a data/evaluation/annotations/reviewer-a.json --annotator-b data/evaluation/annotations/reviewer-b.json --output reports/evaluation/expert-agreement.json`

The agreement tool produces descriptive statistics and an adjudication queue. It does not recruit reviewers, verify credentials, or create gold labels automatically.

## Exit criteria
- Locked annotation rubric and frozen corpus snapshot.
- Two independent annotations for every benchmark record.
- Agreement report generated and disagreements adjudicated with traceable notes.
- Canonical benchmark contains only adjudicated labels for score-eligible splits.
- Held-out test set remains untouched until final evaluation.
- No benchmark performance claim until sufficient expert-labelled records are collected and evaluation is run.
