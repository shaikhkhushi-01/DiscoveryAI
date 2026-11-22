# DiscoveryAI Phase 1 — Exit status

**Review date:** 2026-11-22  
**Decision:** **Phase 1 scope and planning deliverables complete.** Implementation and empirical validation remain future phases.

## Exit criteria

| Criterion | Status | Evidence |
|---|---|---|
| NLP-only scope locked | PASS | phase1_student_project_scope_2026-11-22.md |
| Problem statement and research questions | PASS | Scope document |
| Falsifiable hypotheses and claim boundaries | PASS | Scope document |
| Evaluation tracks separated | PASS | Scope document and benchmark register |
| Rights-aware dataset policy | PASS | Scope document and benchmark register |
| Related-work search strategy and initial comparison | PASS (targeted review) | phase1_related_work_review_2026-11-22.md |
| Benchmark candidate selection and terms assessment | PASS (conditional) | phase1_benchmark_decision_register_2026-11-22.md |
| Architecture-to-requirements mapping | PASS (design-level) | phase1_architecture_requirements_mapping_2026-11-22.md |
| Measurable feature acceptance criteria | PASS | phase1_requirements_and_acceptance_criteria.md |
| Human reviewer dependency removed from current scope | PASS | Scope explicitly excludes new reviewer recruitment/manual annotation |
| Phase 1 documentation committed | PASS after merge of this closeout PR | This file and related closeout docs |

## Decisions locked

1. DiscoveryAI is an NLP/language-model research assistant for corpus-bounded candidate research opportunities.
2. No human reviewer recruitment or new manual annotation is required for the student-project track.
3. QASPER is the primary candidate public benchmark for scientific paper QA/evidence-selection, conditional on exact revision, split visibility, and source-content checks.
4. BEIR may be used as an evaluation framework only; each dataset requires separate license and task review.
5. SciFact is deferred because it is biomedical (outside scope) and surfaced license descriptions need reconciliation.
6. Research-gap generation quality is not considered validated by QASPER, RAGAS, synthetic tests, or task-specific QA metrics.
7. The five gap-comparison systems cannot be scored against a gold gap benchmark without legitimate gap labels. They may be used for controlled prediction generation and engineering/proxy analysis, with clear limitations.
8. No claim of global novelty, MBZUAI affiliation/endorsement, expert validation, or superiority is authorized by Phase 1.

## Explicitly not completed by Phase 1

- No dataset download or checksum freeze.
- No QASPER adapter or evaluation run.
- No real five-system predictions or ablation scores.
- No final NLP corpus rights clearance or frozen corpus.
- No end-to-end production validation.
- No independent validation of research-gap quality.

These are Phase 2+ implementation/evaluation deliverables, not missing Phase 1 planning tasks.

## Phase 1 completion rule

Phase 1 is complete when this closeout document and supporting artifacts are merged to main. The project may then proceed to Phase 2 implementation. Passing Phase 1 does not mean the whole DiscoveryAI application or scientific study is complete.
