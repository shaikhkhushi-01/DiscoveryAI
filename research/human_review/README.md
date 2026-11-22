# Human reviewer packet — NLP corpus pilot

**Status:** blank templates only. No papers have been screened or annotated by this packet.

## Hard prerequisite
Do not select the 30-paper pilot from the current 399-record provisional metadata pool. Day 2 remains open. First create a final, rights-cleared, version-resolved corpus manifest, record its SHA-256, and freeze it. The pilot sampling frame must be that frozen manifest only. Items without documented permission for the intended full-text processing must not enter full-text annotation or model inputs.

## Pilot design (after corpus freeze)
1. Freeze the eligible corpus manifest; record checksum, date, schema version, and inclusion rules.
2. Draw 30 distinct work/version families using a reproducible random seed. If reliable topic strata exist, stratify across publication year and NLP topic; otherwise use a simple random sample and document that limitation.
3. Assign opaque study IDs. Keep the ID-to-paper key restricted to the coordinator.
4. Give the same 30 records independently to Reviewer A and Reviewer B. No discussion of individual cases before both first-pass files are submitted and locked.
5. Declare conflicts before assignment; reassign conflicted records and log the change.
6. After both files are locked, calculate agreement. Send disagreements and UNCERTAIN cases to a third qualified adjudicator.
7. Preserve original decisions; never overwrite them with adjudicated values.

## Roles
- Reviewer A and B: independently qualified NLP/ML researchers or trained domain reviewers.
- Adjudicator: third qualified reviewer, not either initial reviewer.
- Coordinator: manages blinded IDs, access, completeness, provenance; does not silently resolve scientific disagreements.

## Files
- REVIEWER_INSTRUCTIONS.md — operational instructions and decision rules.
- title_abstract_screening_template.csv — independent scope decisions.
- fulltext_rights_review_template.csv — separate rights evidence and permission decision.
- adjudication_template.csv — third-reviewer resolution log.
- pilot_annotation_template.csv — paper-level research annotation fields.

## Data handling
- Do not commit full-text PDFs, copyrighted excerpts, private reviewer identities, contact details, conflict declarations, or private rights correspondence.
- Keep reviewer identity/contact and conflict declarations in restricted storage, separate from paper labels.
- Use opaque reviewer codes A/B/C and study IDs in repository artifacts.
- Never infer permission from OpenAlex has_fulltext, an accessible PDF URL, or a metadata license field alone. Record actual evidence and whether it permits the intended mining/reuse.
- Do not send papers to an external model/provider unless documented permission covers that processing and provider terms are acceptable.

## Current status
These are blank operational templates. No reviewer has been recruited or verified, no records have been sampled from a frozen corpus, and no human labels or agreement statistics are claimed.