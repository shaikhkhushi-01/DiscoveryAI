# Expert annotation artifacts

Store two independent JSON files per study batch (for example reviewer-a.json and reviewer-b.json). Each file has an annotator_id and annotations array. Each record contains record_id, assessment (gap_status plus four integer ratings from 0–3), and evidence tuples with supporting/contradictory stance.

Both reviewers must annotate identical record IDs independently and must not see model predictions or each other's labels. Use pseudonymous reviewer IDs. Preserve raw files unchanged; keep personal/confidential study records outside the public repository. See research/phase4_expert_validation_protocol.md.

The agreement CLI produces descriptive inter-annotator statistics and a disagreement queue. It does not adjudicate disagreements or create a gold dataset automatically.
