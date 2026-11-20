# Day 2 — Corpus blocker register

**Last reviewed:** 2026-11-20  
**Status:** OPEN — provisional metadata pool is not an eligible full-text corpus.

## Known discovery snapshot

- OpenAlex candidate pool: 399 deduplicated metadata candidates.
- Enrichment artifact: 399 candidate records.
- Abstracts present: 374; missing: 25.
- URL checks: 333 reachable, 51 inconclusive, 14 HTTP errors, 1 unreachable.
- License metadata: 278 unverified, 121 missing.
- Relevance decisions: pending human review for all candidates.
- Rights decisions: pending human review for all candidates.
- Version groups: 8 possible groups / 16 records awaiting version review.
- These are discovery/enrichment observations only. URL reachability is not full-text verification; OpenAlex OA/license metadata is not a legal permission determination.

## Required closure workflow

1. **Relevance screening:** inspect title/abstract and record a reason-coded decision. Unclear cases remain unresolved; keyword triage is not a human decision.
2. **Full-text eligibility:** inspect the exact paper version and confirm it is a complete research paper with sufficient methods/results for the study.
3. **Rights review:** record the applicable license/permission evidence for the exact full-text location. Default is pending and text-mining approval remains false until a qualified human records evidence. Exclude unresolved rights.
4. **Version resolution:** adjudicate possible preprint/published duplicates at the work-family level. Preserve all identifiers and exact selected version.
5. **Extraction QA:** verify extracted text completeness, page/section provenance and checksum. Corrupt or incomplete text is excluded with reason.
6. **Final freeze:** create a versioned manifest containing included IDs, exact version, source, rights evidence reference (not private credentials), text checksum, screening decisions, exclusions and protocol version. Hash the manifest and never silently mutate it.

## Current blockers

| Gate | Current state | Closure evidence |
|---|---|---|
| Candidate discovery | DONE (provisional) | OpenAlex run 43854679463 and enrichment artifact |
| Title/abstract screening | OPEN | Human decision ledger with reason codes |
| Full-text eligibility | OPEN | Per-paper full-text review record |
| Text-mining rights | OPEN | Explicit license/permission evidence per exact version |
| Version-family adjudication | OPEN | Resolved version ledger |
| Text extraction QA | OPEN | Verified extracted text and source checksum |
| Frozen eligible corpus | BLOCKED | Final manifest + SHA-256 |

## Non-negotiable safeguards

- Never infer reuse rights from OA status, a reachable URL, or metadata alone.
- Do not upload copyrighted PDFs, private reviewer files or rights evidence into public GitHub artifacts.
- Do not sample the Day 3 pilot from the provisional 399-candidate pool. Sampling frame must be the final eligible, rights-cleared corpus.
- If fewer than the operational 200–300 target qualify, report the actual eligible count; do not lower criteria to reach a target.
- Keep a complete exclusion log and retain unresolved items outside the included corpus.

## Owner-facing next action

The software pipeline and review queue can be prepared automatically, but paper-level relevance, exact-version full-text inspection and legal permission decisions require documented human review. Until those decisions exist, Day 2 remains open and Day 4 scored benchmark experiments remain gated.