# Full-text acquisition and rights-review pipeline

## Stage A: create the review queue (no downloads)

From the repository root:

python scripts/corpus/build_fulltext_rights_queue.py --input data/processed/nlp_corpus_snapshot/candidate_manifest.jsonl --out data/private_review/fulltext_rights_queue.csv

Every candidate starts as PENDING_HUMAN_REVIEW and approved_for_text_mining=false.
OpenAlex license claims and URL reachability are leads only, not legal permission.

## Stage B: human review

For each paper, inspect the exact article/version and record:
- approved_for_text_mining=true only when evidence supports that use;
- reviewer_id;
- evidence_url pointing to the publisher/repository license or permission;
- license_name and license_url;
- candidate_pdf_url (HTTPS).

Separately consider downloading, text mining, local storage, redistribution and public release. Approval for text mining does not imply permission to redistribute the PDF. If unclear, leave false.

Keep the completed approval CSV private and outside Git. Do not commit PDFs, reviewer identities or rights-review records to this public repository.

## Stage C: acquire only approved PDFs

python scripts/corpus/acquire_approved_fulltext.py --approvals data/private_review/rights_approved.csv --out data/private_fulltext --audit data/private_fulltext_download_audit.jsonl

The downloader requires explicit human approval and evidence fields, HTTPS, a PDF signature and PDF/octet-stream content type, and a 50 MiB per-file limit. It writes SHA-256 audit records. It does not infer permission from an OA flag.

## Constraints

- Do not publish PDFs or approval spreadsheets in GitHub Actions artifacts.
- Keep private files in a local ignored directory; verify .gitignore before use.
- Download success proves technical retrieval only, not legal permission.
- A license URL must be read for the exact version and intended use.
- This is an auditable workflow, not legal advice or a substitute for institutional review.
