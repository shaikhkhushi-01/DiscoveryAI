# Phase 2 status — 2026-11-22

## Implemented in repository (pending PR #90 merge)

| Item | Engineering status | Empirical status |
|---|---|---|
| Pinned QASPER v0.3.0 acquisition | Implemented with SHA-256 and size/HTTPS checks | Real archive download not yet run |
| Safe archive parsing | Implemented; reads named regular members only | Real archives not yet parsed |
| QASPER schema normalization | Implemented for canonical QA list and nested answer annotation structure | Real split counts not yet verified |
| Train/validation/test split integrity | Paper-ID duplicate check implemented | Real manifest not yet generated |
| Gold/query separation | Separate JSONL outputs and regression tests | End-to-end actual data audit pending |
| Answer F1 and Evidence F1 | Evaluator adapted from official AllenAI evaluator; tests added | No predictions scored |
| QASPER system generation adapter | Not yet implemented | No predictions generated |
| General OpenAlex corpus freeze | Existing metadata candidate/enrichment pipeline only | Rights/eligibility/final corpus freeze pending |

## Required local execution evidence

After PR #90 is merged, run from the repository root with Python 3.12+:

```bash
python scripts/benchmarks/prepare_qasper.py
```

Then inspect `data/benchmarks/qasper/normalized/manifest.json`. Verify:
- archive checksums equal the pinned values;
- paper counts are train 888, validation 281, test 416;
- observed question counts and answer annotation availability are plausible and non-zero where expected;
- paper IDs are disjoint across splits;
- query JSONL contains no answer/evidence fields;
- references are separate from all model input paths.

Do not upload the raw archives or normalized full text as a public Actions artifact. The manifest can be reviewed locally; share only aggregate counts and checksums if publishing status.

## Research limitations

QASPER validates scientific-paper question answering and evidence selection, not research-gap novelty or hypothesis quality. Automated OpenAlex triage is not human screening. Unknown full-text rights remain excluded. No benchmark performance claim exists until a real prediction file is generated and scored.
