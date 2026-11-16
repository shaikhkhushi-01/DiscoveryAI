# Day 2 OpenAlex candidate collection

This is the reproducible first-pass discovery collector for the NLP/language-model
study defined in `research/day2_ai_ml_scope_and_corpus_protocol_2026-11-16.md`.

## Run

From the repository root (Python 3.10+; standard library only):

```bash
python scripts/corpus/collect_openalex_candidates.py
```

Optional controls:

```bash
python scripts/corpus/collect_openalex_candidates.py --max-per-query 100 --from-date 2018-01-01 --to-date 2025-12-31
```

The default run executes four explicit search strings and retrieves up to 100
records per query (before deduplication). It writes:

- `data/raw/openalex_discovery/raw_pages/*.json`: untouched API page responses
- `data/raw/openalex_discovery/candidate_pool.jsonl`: deduplicated metadata records
- `data/raw/openalex_discovery/retrieval_log.json`: exact queries, parameters,
  UTC timestamps, per-page counts, raw-response SHA-256 hashes, and pool hash

Generated data stays under `data/raw/`, which is intentionally git-ignored.
Do not commit downloaded full-text PDFs or reviewer materials to the public repo.

## Screening is a separate human-reviewed stage

Every row begins with:

- `screening_status=not_screened`
- `full_text_rights_status=not_verified`
- `full_text_access_status=not_checked`

Do not change these fields to eligible or rights-cleared based only on an
OpenAlex result. Review the title/abstract against the inclusion/exclusion
criteria, confirm the authoritative published/preprint version, inspect the
actual full-text license and permitted uses, and record a reason for every
exclusion. A PDF URL or an OpenAlex open-access flag is not a license grant.

Deduplication uses DOI where available, otherwise normalized title + first
author + year. This is a discovery-stage heuristic; human review must link
preprint/published versions and resolve false merges/splits before corpus freeze.

## Evidence boundary

A successful script run proves only that a reproducible metadata discovery pool
was retrieved. It does not prove 200–300 eligible papers, lawful full-text
reuse, expert annotation, benchmark readiness, or a frozen corpus.
