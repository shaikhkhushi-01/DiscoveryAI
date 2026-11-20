# Day 3 — NLP annotation and benchmark protocol

**Status:** protocol/design only. No papers have been independently annotated and no benchmark result is claimed.

## Scope
The initial study is limited to NLP and language-model research, including computational linguistics, NLP-oriented information retrieval, question answering, retrieval-augmented generation, evaluation, robustness and reproducibility. The discovery corpus window remains 2018-01-01 through 2025-12-31. A candidate is not eligible merely because metadata or an abstract appears relevant.

## Unit of analysis and identity
- Primary unit: one distinct scholarly work/version family, with the exact reviewed version recorded.
- Preserve DOI, OpenAlex ID, title, year, version group, source URL and full-text checksum where lawfully available.
- Link preprint and published versions when materially the same work; retain version-level provenance.
- Do not treat chunks, sections or multiple benchmark examples from one paper as independent papers.
- Split data by work/version family and research-question family, never by random text chunks.

## Research-question taxonomy
Assign one primary category and optional secondary categories:
1. MODEL_METHOD — model architecture, objective, training or inference method.
2. DATA_RESOURCE — dataset, corpus, annotation resource or data curation.
3. EVALUATION — metrics, evaluation methodology, benchmark or human evaluation.
4. ROBUSTNESS_SAFETY — robustness, generalization, bias, toxicity, safety or adversarial behavior in NLP.
5. RETRIEVAL_QA_RAG — NLP-focused retrieval, question answering or retrieval-augmented generation.
6. LINGUISTIC_ANALYSIS — empirical or computational analysis of language phenomena.
7. REPRODUCIBILITY — replication, reproducibility, reporting or empirical audit of NLP results.
8. OTHER_NLP — relevant NLP work not covered above; requires a short justification.
9. OUT_OF_SCOPE — not an NLP research contribution under this protocol.

## Annotation record
Each reviewer independently records:
- paper/work ID and exact version identifier;
- reviewer ID and annotation timestamp;
- primary and optional secondary research-question categories;
- NLP relevance decision (IN_SCOPE, OUT_OF_SCOPE, UNCERTAIN);
- contribution type (METHOD, DATA, EVALUATION, ANALYSIS, REPLICATION, POSITION, OTHER);
- concise research question, claimed contribution and evidence locator (page/section/table/figure);
- task/domain, model/system, data/resource and evaluation setup where applicable;
- baseline/comparator, outcome/metric and limitations where reported;
- reproducibility evidence (CODE_AVAILABLE, DATA_AVAILABLE, DETAILS_SUFFICIENT, NOT_REPORTED, NOT_APPLICABLE);
- reviewer confidence (LOW, MEDIUM, HIGH) and rationale for uncertainty.

Evidence must be traceable to the reviewed paper. Distinguish author claims from reviewer interpretation. Do not infer missing details; use NOT_REPORTED.

## Independent review and blinding
- Two qualified reviewers (A and B) independently annotate the same eligible paper version.
- Reviewers must not see one another's decisions or notes before both submissions are locked.
- Keep reviewer identity mapping private; use pseudonymous IDs in analysis exports.
- Record timestamps and immutable source/version identifiers.
- If a reviewer has a conflict of interest or prior involvement, reassign and document it.
- AI-assisted suggestions may support navigation but cannot count as an independent reviewer or make final decisions.

## Disagreement and adjudication
1. Freeze both initial records before comparison.
2. Calculate agreement on pre-specified fields before adjudication.
3. Flag disagreements in scope decision, primary category, contribution type and key extracted claims.
4. A third qualified adjudicator reviews the paper and both rationales without silently overwriting either record.
5. Preserve A, B and adjudicated values plus reason, adjudicator ID and timestamp.
6. If unresolved, retain UNRESOLVED and exclude from the confirmed benchmark set pending resolution.

## Agreement and statistical reporting
- For nominal labels, report raw agreement and Cohen's kappa with confidence intervals where feasible.
- For more than two raters or missing/unequal rating patterns, use an appropriate Krippendorff's alpha variant and state the unit/metric.
- Report category prevalence and confusion matrices; kappa can be prevalence-sensitive.
- Bootstrap confidence intervals by paper/work family, not by individual chunks.
- Pre-register primary fields, handling of missing ratings, confidence-interval method and any minimum agreement criterion before examining final results.
- Do not present a single agreement coefficient without sample size, prevalence and uncertainty.
- No universal pass threshold is asserted here; set thresholds in a dated protocol amendment before annotation begins.

## Benchmark construction and leakage controls
- Separate development, validation and locked test sets by work/version family and closely related research-question groups.
- Keep the locked test set inaccessible to prompt/model tuning and iterative system development.
- Record benchmark version, manifest checksum, split assignment, annotation schema version and evaluator version.
- Use the same permitted input information for every compared system; document exclusions and missing inputs.
- Predefine primary outcomes, baselines, ablations, statistical tests and correction for multiple comparisons.
- Report all attempted runs, failures and exclusions; retain seeds, configuration, code commit, model/version identifiers and environment metadata.
- Never tune on the locked test set. Any test-set access must be logged and may require a new holdout.
- Keep copyrighted full text, private reviewer materials and rights decisions out of public artifacts unless redistribution rights are established.

## Day 3 deliverables and exit checks
- [x] Taxonomy and annotation fields specified.
- [x] Two-reviewer blinded workflow and adjudication rules specified.
- [x] Agreement and benchmark leakage controls specified.
- [ ] Annotation schema validator and tests merged and CI-verified.
- [ ] Qualified reviewers recruited and conflicts checked.
- [ ] Pilot annotations completed and adjudicated.
- [ ] Statistical analysis plan locked before full annotation.

This document defines a protocol; it is not evidence that the corpus is rights-cleared, annotated, independently reviewed or scientifically validated. Day 2 remains open until its own exit criteria are met.
