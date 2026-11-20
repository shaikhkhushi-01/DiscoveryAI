# DiscoveryAI NLP pilot — reviewer operating guide

**Version:** 1.0  
**Protocol date:** 2026-11-20  
**Study scope:** NLP and language-model research only.  
**Status:** operational template; no reviewer has been recruited and no pilot annotations are claimed.

## Before assignment
1. The corpus coordinator confirms the paper/version is eligible under the Day 2 screening protocol and that the reviewer can lawfully access the exact full text for research review.
2. The coordinator records a stable work ID, exact version ID, source URL, access basis, and file checksum where permitted. Do not distribute copyrighted PDFs unless redistribution is permitted.
3. Each reviewer completes the conflict-of-interest declaration and confirms relevant NLP research/annotation competence.
4. Use pseudonymous reviewer IDs (for example, R-A and R-B). Keep the identity key offline and access-restricted.
5. Reviewers receive separate copies of the same paper list. They must not see each other's decisions, notes, or interim agreement statistics.

## Per-paper instructions
- Read the full paper, not only its title or abstract.
- Annotate the exact version assigned. If the paper is inaccessible, incomplete, corrupted, or not the assigned version, stop and flag it; do not guess.
- Record one primary category and any justified secondary categories.
- Distinguish author-stated claims from your interpretation.
- Every substantive decision must have an evidence locator (page and section, or table/figure identifier). Use NOT_REPORTED rather than inferring missing details.
- Mark UNCERTAIN when evidence is insufficient. Explain why.
- Do not use generative AI to make or finalize labels. Permitted navigation assistance must be disclosed and must not replace independent judgment.
- Submit the annotation file without discussing cases with the other reviewer.

## Required fields
Use `research/schemas/nlp_paper_annotation.schema.json` as the field contract and the current annotation validator before submission. The canonical values are defined in the Day 3 protocol.

## Lock and handoff
1. Save the completed reviewer file as JSONL, one annotation object per line.
2. Run the validator against the combined A+B file. Each paper/version must have exactly two distinct reviewer IDs.
3. Submit both files to the coordinator through a private, access-controlled channel; do not commit reviewer files, names, copyrighted full text, or rights evidence to this public repository.
4. The coordinator timestamps and freezes both files before revealing either reviewer’s decisions.
5. Only after freeze may the coordinator produce a disagreement table for adjudication.

## Disagreement handling
The third reviewer/adjudicator must be qualified, conflict-free, and independent of the initial decisions. Preserve both original labels. Record the adjudicated label, rationale, evidence locator, adjudicator pseudonym, and UTC timestamp. Never overwrite A or B.

## Stop conditions
Stop and notify the coordinator if there is a conflict of interest, unclear access permission, a wrong/incomplete version, a suspected duplicate, or insufficient evidence. A stop is not a negative label; it is a query for coordinator resolution.
