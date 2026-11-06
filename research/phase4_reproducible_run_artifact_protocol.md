# Reproducible Evaluation Run Artifact Protocol

## Purpose
Every reported benchmark, baseline, or ablation result must be traceable to exact source artifacts and a code revision. This protocol packages the benchmark, predictions, evaluation report, protocol/rubric references, and dependency-lock hashes into a small JSON manifest.

## Required procedure
1. Freeze the benchmark, corpus snapshot, annotation rubric, and evaluation protocol.
2. Generate each system's predictions independently and preserve the raw prediction JSON unchanged.
3. Run the P4.2 evaluator and preserve its machine-readable report.
4. Package the run manifest:

```bash
python scripts/evaluation/package_evaluation_run.py \
  --benchmark data/evaluation/discovery_gap_bench.json \
  --predictions data/evaluation/predictions/discoveryai-full-test.json \
  --report reports/evaluation/discoveryai-full-test.json \
  --protocol research/phase4_evaluation_runner_protocol.md \
  --rubric research/discovery_gap_bench_annotation_rubric.md \
  --dependency-lock backend/requirements.txt \
  --dependency-lock frontend/package-lock.json \
  --code-revision <full-git-commit-sha> \
  --output reports/evaluation/discoveryai-full-test.manifest.json
```

5. Store the manifest next to the report in the private study artifact store. Publish hashes and non-sensitive metadata where appropriate; do not publish restricted papers, reviewer identities, secrets, or private annotation data.
6. Repeat for every baseline and ablation variant. The five baseline and six ablation runs must share the frozen benchmark/corpus/split and comply with the corresponding protocol.
7. Before publication, independently verify hashes against the preserved source artifacts.

## Integrity checks
The packager fails if:
- benchmark ID/version/rubric version in the report do not match the benchmark file;
- report run metadata differs from prediction run metadata;
- prediction record IDs are malformed or duplicated;
- the code revision is not recorded;
- any explicitly supplied protocol/rubric/lock artifact is missing.

## Limitations
A hash proves file identity, not scientific validity, correct model execution, reviewer qualifications, or protocol compliance. A manifest is necessary provenance, not a substitute for independent replication. Never place secrets, reviewer identities, prompts containing private data, or raw source passages in the manifest.
