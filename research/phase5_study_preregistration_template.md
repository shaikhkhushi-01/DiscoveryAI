# Phase 5 Study Preregistration Template

> Complete and freeze this document before inspecting held-out test results. Replace every bracketed field. This template is not a completed preregistration.

## Study identity
- Study title: [title]
- Protocol version/date: [version / YYYY-MM-DD]
- Responsible team: [roles]
- Repository commit: [commit SHA]
- Scientific domain and scope: [bounded domain]
- Primary research question: [question]

## Corpus
- Corpus sources and licenses: [sources, permissions]
- Inclusion criteria: [criteria]
- Exclusion criteria: [criteria]
- Snapshot date and timezone: [date/time]
- Corpus manifest location and checksum: [path/checksum]
- Known coverage gaps: [description]

## Benchmark construction
- Candidate-generation method: [method]
- Sampling strategy, including negative/contradicted cases: [method]
- Planned record count and rationale: [count/rationale]
- Deduplication policy: [policy]
- Leakage prevention and split strategy: [strategy]
- Benchmark schema version: [version]
- Annotation rubric version: [version]

## Human annotation
- Reviewer eligibility/subject expertise: [criteria]
- Reviewer A pseudonymous ID: [ID]
- Reviewer B pseudonymous ID: [ID]
- Blinding procedure: [procedure]
- Source excerpts provided identically to both reviewers: [yes/no and provenance]
- Disagreement/adjudication procedure: [procedure]
- Exclusion/missing-annotation policy: [policy]
- Privacy, consent, compensation, and conflict-of-interest handling: [details]

## Systems and controls
For each of the five systems, freeze code commit, model/provider/version, prompt, embedding model, retrieval configuration, reranker, evidence budget, and any randomness/seed:
- LLM-only: [configuration]
- Vector RAG: [configuration]
- GraphRAG: [configuration]
- Hybrid Retrieval: [configuration]
- Full DiscoveryAI: [configuration]

## Ablations
List each component-removal condition and confirm that all other settings remain fixed:
- [condition 1]
- [condition 2]
- [condition 3]
- [condition 4]
- [condition 5]

## Outcomes and statistical plan
- Primary outcome(s): [metric and aggregation]
- Secondary outcome(s): [metrics]
- Unit of analysis: [record/query/paper]
- Paired comparison method: [method and rationale]
- Confidence interval method and level: [method]
- Multiple-comparison handling: [method]
- Missing/failure handling: [policy]
- Planned subgroup/error analyses: [slices]
- Minimum practically important effect: [threshold and rationale]
- Power/sample-size rationale: [calculation or explicit exploratory rationale]

## Deviations and publication
- Rules for protocol deviations: [policy]
- Test-set access control: [owners/process]
- Reproducibility artifacts to release: [list]
- Data/code licensing restrictions: [details]
- Limitations anticipated: [list]
- Publication target and authorship criteria: [criteria]

## Sign-off
- Protocol frozen by: [role]
- Date: [YYYY-MM-DD]
- Deviations after freeze will be logged with date, reason, and impact: [yes/no]
