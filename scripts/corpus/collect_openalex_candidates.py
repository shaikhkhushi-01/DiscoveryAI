#!/usr/bin/env python3
"""Collect a reproducible OpenAlex discovery pool for the Day 2 NLP corpus.

This script collects bibliographic metadata only. It does not download papers,
decide inclusion, or certify full-text reuse rights.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE_URL = "https://api.openalex.org/works"
QUERIES = [
    'natural language processing transformer language model',
    'large language model evaluation benchmark reasoning',
    'language models retrieval question answering summarization',
    'neural machine translation text generation information extraction',
]
SELECT = ",".join([
    "id", "doi", "title", "publication_date", "publication_year", "type",
    "authorships", "primary_location", "open_access", "best_oa_location",
    "locations", "ids", "language", "topics", "keywords", "has_fulltext",
])


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_title(value: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (value or "").casefold()).strip()


def first_author(record: dict[str, Any]) -> str:
    authors = record.get("authorships") or []
    if not authors:
        return ""
    author = (authors[0].get("author") or {}).get("display_name") or ""
    return normalize_title(author)


def dedup_key(record: dict[str, Any]) -> str:
    doi = (record.get("doi") or "").strip().lower()
    if doi:
        return "doi:" + doi.removeprefix("https://doi.org/")
    return "title-author-year:{}|{}|{}".format(
        normalize_title(record.get("title")),
        first_author(record),
        record.get("publication_year") or "",
    )


def request_page(params: dict[str, str], retries: int = 5) -> tuple[bytes, dict[str, Any]]:
    url = BASE_URL + "?" + urllib.parse.urlencode(params)
    headers = {"User-Agent": "DiscoveryAI-CorpusResearch/0.1 (reproducible academic metadata collection)"}
    for attempt in range(retries):
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=45) as response:
                raw = response.read()
                return raw, json.loads(raw.decode("utf-8"))
        except urllib.error.HTTPError as exc:
            # Preserve the API's response body; it usually identifies invalid
            # filters/parameters far more clearly than the HTTP status alone.
            detail = exc.read().decode("utf-8", errors="replace").strip()
            if exc.code not in (429, 500, 502, 503, 504) or attempt == retries - 1:
                raise RuntimeError(
                    f"OpenAlex HTTP {exc.code} {exc.reason}: {detail[:2000]}"
                ) from exc
            time.sleep(min(2 ** attempt, 30))
        except (urllib.error.URLError, TimeoutError):
            if attempt == retries - 1:
                raise
            time.sleep(min(2 ** attempt, 30))
    raise RuntimeError("OpenAlex request retries exhausted")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="data/raw/openalex_discovery")
    parser.add_argument("--from-date", default="2018-01-01")
    parser.add_argument("--to-date", default="2025-12-31")
    parser.add_argument("--max-per-query", type=int, default=100)
    parser.add_argument("--email", default="", help="Optional polite-pool contact email; not required.")
    parser.add_argument("--pause-seconds", type=float, default=0.15)
    args = parser.parse_args()

    if args.max_per_query < 1 or args.max_per_query > 100:
        parser.error("--max-per-query must be between 1 and 100 (one free unauthenticated API page per query)")
    if args.from_date > args.to_date:
        parser.error("--from-date must be on or before --to-date")

    out = Path(args.output_dir)
    raw_dir = out / "raw_pages"
    raw_dir.mkdir(parents=True, exist_ok=True)
    started = utc_now()
    collected: dict[str, dict[str, Any]] = {}
    page_log: list[dict[str, Any]] = []

    for query_index, query in enumerate(QUERIES, start=1):
        # The workflow deliberately caps each query at 100 records. Use
        # OpenAlex basic paging for this single-page collection: unauthenticated
        # cursor paging is limited and can fail when following next_cursor.
        page_number = 1
        params = {
            "search": query,
            "filter": (
                f"from_publication_date:{args.from_date},"
                f"to_publication_date:{args.to_date},type:article|preprint|proceedings-article"
            ),
            "per_page": str(args.max_per_query),
            "page": "1",
            "select": SELECT,
        }
        if args.email:
            params["mailto"] = args.email
        raw, payload = request_page(params)
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            raw_name = f"q{query_index:02d}_page{page_number:03d}_{stamp}.json"
            (raw_dir / raw_name).write_bytes(raw)
            results = payload.get("results") or []
            page_log.append({
                "query_index": query_index,
                "query": query,
                "page": page_number,
                "retrieved_at_utc": utc_now(),
                "request_parameters": params,
                "result_count": len(results),
                "raw_response_file": f"raw_pages/{raw_name}",
                "raw_response_sha256": sha256_bytes(raw),
                "openalex_meta": payload.get("meta", {}),
            })
            for record in results:
                key = dedup_key(record)
                if key not in collected:
                    record["_discovery"] = {
                        "query_indices": [query_index],
                        "dedup_key": key,
                        "screening_status": "not_screened",
                        "screening_reason": "",
                        "full_text_rights_status": "not_verified",
                        "full_text_access_status": "not_checked",
                    }
                    collected[key] = record
                else:
                    info = collected[key]["_discovery"]
                    if query_index not in info["query_indices"]:
                        info["query_indices"].append(query_index)
            time.sleep(max(0.0, args.pause_seconds))

    records = sorted(
        collected.values(),
        key=lambda r: (r.get("publication_date") or "", r.get("id") or ""),
    )
    jsonl_path = out / "candidate_pool.jsonl"
    with jsonl_path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    log = {
        "schema_version": "1.0",
        "source": "OpenAlex Works API",
        "api_endpoint": BASE_URL,
        "collection_started_at_utc": started,
        "collection_finished_at_utc": utc_now(),
        "date_window": {"from": args.from_date, "to": args.to_date},
        "queries": QUERIES,
        "max_per_query": args.max_per_query,
        "unique_candidate_count": len(records),
        "raw_page_count": len(page_log),
        "candidate_pool_file": "candidate_pool.jsonl",
        "candidate_pool_sha256": sha256_bytes(jsonl_path.read_bytes()),
        "pages": page_log,
        "important_limitations": [
            "Discovery pool only; not a screened or frozen research corpus.",
            "OpenAlex relevance ranking and metadata are not proof of topical eligibility.",
            "Open-access flags and PDF URLs do not establish a redistribution license.",
            "Full-text access, license, version, peer-review status, and eligibility require manual verification.",
            "Preprint and published versions must be linked and adjudicated before counting unique works.",
        ],
    }
    log_path = out / "retrieval_log.json"
    log_path.write_text(json.dumps(log, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "discovery_pool_collected",
        "unique_candidates": len(records),
        "raw_pages": len(page_log),
        "candidate_pool": str(jsonl_path),
        "retrieval_log": str(log_path),
        "candidate_pool_sha256": log["candidate_pool_sha256"],
        "warning": "Not screened, not license-cleared, and not frozen.",
    }, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
