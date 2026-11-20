# DiscoveryAI NLP annotation pilot — statistical analysis plan

**Protocol version:** 1.0  
**Locked:** 2026-11-20, before any pilot annotation  
**Scope:** NLP/language-model papers; paper/version family is the unit.  
**Status:** prospective plan only; no data have been annotated and no statistics have been calculated.

## 1. Purpose and estimand
The pilot assesses whether two trained, independent reviewers can apply the annotation codebook consistently to eligible NLP papers. The primary estimand is inter-reviewer agreement for (a) NLP relevance and (b) primary research-question category on the same exact paper version. This is a feasibility/codebook pilot, not a test of DiscoveryAI scientific performance and not a corpus prevalence estimate.

## 2. Pilot sample
- Target: 30 eligible paper/version families, selected by reproducible simple random sampling from the Day 2 frozen, rights-cleared eligible pool.
- If fewer than 30 eligible items exist, annotate all eligible items and report the actual number; do not backfill with unverified candidates.
- Operational feasibility target only; it is not a power calculation and must not be described as statistically powered.
- Record the sampling frame checksum, inclusion criteria, random seed, selection timestamp, and any substitutions. No substitution without a documented reason.
- The exact paper version must be frozen before assignment. Multiple versions of one work count as one work family for sampling.

## 3. Review and adjudication sequence
1. Two conflict-free reviewers independently annotate every selected item.
2. Both initial files are frozen before either reviewer sees the other's decisions.
3. Calculate pre-adjudication agreement on the primary fields.
4. A third qualified adjudicator resolves disagreements while preserving both original annotations and a reasoned adjudicated value.
5. Keep unresolved items explicitly unresolved; do not silently force consensus.

## 4. Outcomes and order
**Primary outcomes**
1. Cohen's kappa for `nlp_relevance`.
2. Cohen's kappa for `primary_category`.

**Secondary outcomes**
- Raw percent agreement and category prevalence for each primary field.
- Cohen's kappa for `contribution_type`.
- Confusion matrices and disagreement counts.
- Missing/uncertain label counts, adjudication rate, and unresolved count.

Report denominators for every statistic. Do not collapse UNCERTAIN into IN_SCOPE or OUT_OF_SCOPE. Report the complete label distribution because kappa is prevalence-sensitive.

## 5. Confidence intervals and missingness
- For each primary kappa, compute a two-sided 95% percentile bootstrap confidence interval using 2,000 resamples of paper/work-family units, with replacement; fixed seed 20261120.
- Resample whole paper families, never chunks, pages, or multiple records from one work as independent observations.
- If a resample has undefined kappa (expected agreement equals 1), omit that replicate from interval calculation and report the number omitted. If too few valid replicates remain for a stable interval, report the interval as not estimable.
- Report all missing ratings and exclusions with reasons. Primary agreement uses only items with both valid independent ratings for that field; report that denominator explicitly.
- If the design later has more than two raters or unequal/missing rating patterns that invalidate pairwise Cohen's kappa, use nominal Krippendorff's alpha as a separately specified analysis and report its software/version and missing-data handling. Do not switch metrics after seeing which gives a more favorable result.

## 6. Operational pilot decision rule
The pilot is intended to diagnose the codebook, not to certify scientific validity.
- If either primary point estimate of kappa is below 0.70, or if a primary field has more than 20% unresolved/missing ratings, pause full annotation, review disagreement reasons, revise the codebook, retrain reviewers, and run a newly sampled pilot.
- If both primary point estimates are at least 0.70, proceed only after documented review of the confidence intervals, prevalence, confusion matrices, and adjudication burden by the study lead.
- This 0.70 value is a predeclared operational trigger for this pilot, not a universal scientific standard or proof of validity. Do not claim reliability from a small pilot alone.
- Any material codebook change creates a new version and requires a new pilot; do not pool pre- and post-change labels without a justified bridge study.

## 7. Data integrity and leakage
- Keep initial reviewer labels blinded until both files are frozen.
- Keep the locked benchmark test set inaccessible to system developers and prompt/model tuning.
- Do not use pilot annotations to tune and then report the same pilot as a held-out test.
- Preserve protocol version, schema version, corpus manifest checksum, sampling seed, reviewer pseudonyms, timestamps, code commit, and analysis software version.
- Do not publish reviewer identity mappings, private notes, copyrighted full text, or unverified rights evidence.

## 8. Reporting
Report the sample flow (eligible frame, sampled, attempted, completed, excluded), reviewer qualifications/conflicts in aggregate, exact versions, raw agreement, kappa, 95% CI, label prevalence, confusion matrices, adjudication burden, missingness, protocol deviations, and limitations. Do not present the pilot as an independent external validation of DiscoveryAI.

## 9. Deviations and amendments
Any change to sample size, outcomes, thresholds, bootstrap method, exclusion rules, or adjudication process must be dated and versioned before examining the affected results. Report all amendments and distinguish prospective from post hoc analyses.
