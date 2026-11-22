# DiscoveryAI — Phase 1 benchmark decision register

**Review date:** 2026-11-22  
**Budget constraint:** zero; public/free access only.  
**Important:** Selected means a justified candidate for implementation, not that the dataset has already been downloaded, hashed, legally reviewed at item level, or scored.

## Decision summary

| Benchmark / resource | Task fit | Public terms observed | Decision | Allowed project use / restrictions |
|---|---|---|---|---|
| **QASPER** (Dasigi et al., NAACL 2021) | Direct fit for scientific-paper QA and evidence selection; 5,049 questions over 1,585 NLP papers | Official Hugging Face dataset card declares CC BY 4.0. Card reports QA and evidence-selection tasks, F1 metrics, and Longformer baselines. Source papers' full text is extracted from S2ORC. | **Selected as primary candidate for QA/evidence-selection evaluation, conditional on a pinned revision and source-content review.** | Use only the dataset release fields under the dataset card's stated terms with attribution and exact version/checksum. Before independently re-ingesting/re-hosting/indexing full-text paper content, verify the underlying paper/version permissions; dataset-card licensing must not be treated as a blanket relicensing of every source paper. Confirm actual available splits and gold-label visibility at download time. Never tune on the held-out split. |
| **BEIR framework** | Suitable common harness for IR evaluation | Toolkit repository is open source; BEIR explicitly warns that each underlying dataset retains its own license and user must verify permissions. | **Framework candidate only; no dataset blanket approval.** | Can reuse evaluation code subject to toolkit license. Select an individual dataset only after its own license, source, task fit and split are checked. |
| **SciFact** | Scientific claim verification and evidence retrieval; useful adjacent task, but its primary domain is biomedical, outside DiscoveryAI's locked NLP-only domain | Official SciFact repo links data/code; Hugging Face mirror labels dataset CC-BY-NC-2.0, while other surfaced source descriptions report different terms for claims/abstracts. | **Not selected for this project baseline at present.** | Domain mismatch plus conflicting surfaced license descriptions. Do not download, redistribute, or use until canonical component-level terms are reconciled. |
| **QASPER-derived MTEB retrieval package** | Potential scientific paper retrieval task | Surfaced MTEB mirror declares CC-BY-NC-4.0, which differs from QASPER's own card and has its own packaging. | **Not selected.** | Do not infer QASPER's original terms automatically apply to a third-party repackaging. Reconsider only after package-specific terms and provenance are reviewed. |
| **Synthetic workflow fixtures** | Schema, traceability, abstention, failure-path and reproducibility checks | Created by this repository; synthetic records contain no real benchmark claims | **Approved for engineering tests only.** | Must be labelled synthetic. Never report these as benchmark scores or evidence of research-gap quality. |

## Primary candidate: QASPER

Canonical sources:
- Paper: https://aclanthology.org/2021.naacl-main.365/
- Dataset card: https://huggingface.co/datasets/allenai/qasper
- Dataset card license link: https://creativecommons.org/licenses/by/4.0/

Reported task details:
- 5,049 questions over 1,585 NLP papers.
- QA and evidence-selection tasks.
- Dataset card reports F1 as the task metric and lists official Longformer baseline scores (33.63 Token F1 for QA and 39.37 F1 for evidence selection).
- The card documents train and validation counts and shows a three-split dataset viewer; exact test-split accessibility and labels must be checked from the pinned release before the final protocol is frozen.

### QASPER evaluation plan

1. Pin an exact dataset repository revision and record retrieval timestamp, file checksums and dataset-library version.
2. Inspect actual split names, counts, labels and test visibility before selecting the final holdout.
3. Use train for development only. Use validation for development/model selection only. If an official test split with scoring labels is available, keep it locked until final evaluation; otherwise do not invent a test result and document the limitation.
4. Run retrieval/evidence-selection and QA separately. Use the dataset's official evaluation implementation/metric where available; record exact normalization and aggregation.
5. Compare only systems that can consume equivalent inputs and return comparable outputs. Do not force the five research-gap systems into a QASPER score if their output contracts/tasks do not match.
6. Preserve paper-level split boundaries. Do not split paragraphs/questions from one paper across train and held-out sets.
7. Audit overlap between QASPER papers and the DiscoveryAI indexed corpus; disclose overlap and do not use held-out questions/answers for prompt tuning.
8. Report the benchmark as scientific paper QA/evidence selection, not as research-gap discovery validation.

## License and provenance guardrails

- A benchmark toolkit license is not the underlying dataset license.
- A dataset card's declared license is a source claim; preserve the card revision and source URL.
- If a dataset includes third-party full-text material, inspect source-paper rights before re-hosting, redistributing, or separately ingesting that content.
- Do not commit downloaded datasets or full-text material unless redistribution is explicitly permitted.
- Unknown or conflicting terms mean pending / do not use, not implied permission.

## Phase 1 benchmark decision

QASPER is the only primary candidate selected for the student project's task-specific QA/evidence-selection evaluation. This is conditional selection, not proof that all source paper content can be independently redistributed or that a final test split is accessible. BEIR remains a framework option, not a blanket dataset approval. SciFact is deferred.
