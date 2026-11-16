#!/usr/bin/env python3
"""Enrich an OpenAlex discovery artifact and create an auditable screening snapshot.

This script deliberately does NOT make legal determinations or final human eligibility
decisions. It reconstructs abstracts, triages topical relevance, checks URL reachability,
and records license claims as unverified metadata.
"""
from __future__ import annotations
import argparse, concurrent.futures, csv, hashlib, json, os, re, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

API = "https://api.openalex.org/works/"
UA = "DiscoveryAI-CorpusAudit/1.0 (research metadata enrichment)"
TERMS = {
 "nlp": ["natural language processing", "language model", "language modeling", "text",
         "machine translation", "question answering", "information extraction",
         "named entity", "sentiment", "summarization", "dialogue", "dialog",
         "speech recognition", "tokeniz", "parsing", "text generation", "retrieval",
         "transformer", "large language model", "llm", "nlp"],
 "out_of_scope": ["medical diagnosis", "clinical", "robotics", "climate model",
                  "weather forecasting", "protein folding"]
}
def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
def read_jsonl(path: Path):
    rows=[]
    for n,line in enumerate(path.read_text(encoding="utf-8").splitlines(),1):
        if line.strip():
            try: rows.append(json.loads(line))
            except Exception as e: raise ValueError(f"Invalid JSONL line {n}: {e}")
    return rows
def reconstruct(index):
    if not isinstance(index, dict): return ""
    tokens=[]
    for word, positions in index.items():
        for pos in positions or []:
            tokens.append((int(pos), word))
    return " ".join(w for _,w in sorted(tokens))
def get_work(openalex_id, retries=4):
    wid = openalex_id.rstrip("/").split("/")[-1]
    url = API + quote(wid, safe="")
    for attempt in range(retries):
        try:
            req=Request(url, headers={"User-Agent":UA, "Accept":"application/json"})
            with urlopen(req, timeout=35) as r:
                return json.loads(r.read().decode("utf-8")), None
        except HTTPError as e:
            detail=e.read(1000).decode("utf-8","replace")
            if e.code in (429,500,502,503,504) and attempt < retries-1:
                time.sleep(2**attempt); continue
            return None, f"HTTP {e.code}: {detail}"
        except (URLError, TimeoutError, json.JSONDecodeError) as e:
            if attempt < retries-1: time.sleep(2**attempt); continue
            return None, str(e)
def check_url(url):
    if not url: return {"status":"no_url","http_status":None,"final_url":None}
    try:
        req=Request(url, method="HEAD", headers={"User-Agent":UA})
        with urlopen(req, timeout=12) as r:
            return {"status":"reachable" if r.status in (200,206) else "http_error",
                    "http_status":r.status,"final_url":r.geturl()}
    except HTTPError as e:
        # Some repositories reject HEAD; a 405 is inconclusive, not proof of absence.
        return {"status":"inconclusive" if e.code in (403,405,429) else "unreachable",
                "http_status":e.code,"final_url":url}
    except Exception as e:
        return {"status":"inconclusive","http_status":None,"final_url":url,"error":str(e)[:300]}
def relevance(title, abstract, topics, keywords, language):
    text=" ".join([title or "", abstract or "",
        " ".join(t.get("display_name","") for t in (topics or [])),
        " ".join(k.get("display_name","") for k in (keywords or []))]).lower()
    hits=[t for t in TERMS["nlp"] if t in text]
    negatives=[t for t in TERMS["out_of_scope"] if t in (title or "").lower()]
    if language not in (None,"en"): return "manual_language_review", hits
    if negatives and not hits: return "likely_out_of_scope_manual_review", hits
    if len(hits)>=2 or any(t in (title or "").lower() for t in TERMS["nlp"]):
        return "likely_in_scope_manual_confirmation", hits
    return "uncertain_manual_review", hits
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",default="data/raw/openalex_discovery/candidate_pool.jsonl")
    ap.add_argument("--out",default="data/processed/nlp_corpus_snapshot")
    args=ap.parse_args()
    src=Path(args.input); out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    candidates=read_jsonl(src)
    enriched=[]; errors=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        futures={ex.submit(get_work,r.get("id","")):r for r in candidates}
        for fut in concurrent.futures.as_completed(futures):
            base=futures[fut]; work,err=fut.result()
            if err:
                errors.append({"openalex_id":base.get("id"),"error":err})
                work={}
            abstract=reconstruct(work.get("abstract_inverted_index"))
            locs=work.get("locations") or base.get("locations") or []
            # Prefer a URL explicitly returned as a PDF; otherwise test landing page.
            pdf=next((x.get("pdf_url") for x in locs if x.get("pdf_url")),None)
            landing=next((x.get("landing_page_url") for x in locs if x.get("landing_page_url")),None)
            license_claims=sorted({x.get("license") for x in locs if x.get("license")})
            urlcheck=check_url(pdf or landing)
            topics=work.get("topics") or base.get("topics") or []
            kws=work.get("keywords") or base.get("keywords") or []
            title=work.get("title") or base.get("title") or ""
            lang=work.get("language") or base.get("language")
            rel,hits=relevance(title,abstract,topics,kws,lang)
            row={
              "openalex_id":base.get("id"),"doi":work.get("doi") or base.get("doi"),
              "title":title,"authors":[a.get("author",{}).get("display_name") for a in (work.get("authorships") or base.get("authorships") or [])],
              "publication_date":work.get("publication_date") or base.get("publication_date"),
              "publication_year":work.get("publication_year") or base.get("publication_year"),
              "type":work.get("type") or base.get("type"),"language":lang,
              "abstract":abstract,"abstract_status":"retrieved" if abstract else ("not_available_from_openalex" if not err else "retrieval_error"),
              "topics":[t.get("display_name") for t in topics],
              "keywords":[k.get("display_name") for k in kws],
              "relevance_triage":rel,"relevance_terms":hits,
              "manual_relevance_decision":"pending","manual_reviewer_id":None,
              "candidate_pdf_url":pdf,"candidate_landing_page_url":landing,
              "access_url_checked":pdf or landing,"access_check":urlcheck,
              "full_text_access_status":"reachable_url_not_content_verified" if urlcheck["status"]=="reachable" else urlcheck["status"],
              "license_claims_openalex":license_claims,
              "license_rights_status":"unverified_metadata_claim" if license_claims else "unknown_no_license_metadata",
              "rights_reviewer_decision":"pending","rights_evidence_url":None,
              "source_record_url":base.get("id"),"retrieved_at_utc":datetime.now(timezone.utc).isoformat(),
              "enrichment_error":err
            }
            enriched.append(row)
    enriched.sort(key=lambda x:x.get("openalex_id") or "")
    manifest_path=out/"candidate_manifest.jsonl"
    payload="".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in enriched).encode()
    manifest_path.write_bytes(payload)
    ledger=out/"screening_ledger.csv"
    cols=["openalex_id","doi","title","publication_year","type","language","abstract_status",
          "relevance_triage","manual_relevance_decision","full_text_access_status",
          "candidate_pdf_url","candidate_landing_page_url","license_claims_openalex",
          "license_rights_status","rights_reviewer_decision","rights_evidence_url"]
    with ledger.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=cols); w.writeheader()
        for r in enriched:
            item={k:r.get(k) for k in cols}; item["license_claims_openalex"]=";".join(r["license_claims_openalex"])
            w.writerow(item)
    summary={
      "generated_at_utc":datetime.now(timezone.utc).isoformat(),"input_file":str(src),
      "input_sha256":sha256(src.read_bytes()),"candidate_count":len(candidates),
      "enriched_count":len(enriched),"api_errors":len(errors),
      "abstract_retrieved":sum(r["abstract_status"]=="retrieved" for r in enriched),
      "abstract_missing_or_error":sum(r["abstract_status"]!="retrieved" for r in enriched),
      "relevance_triage_counts":dict(__import__("collections").Counter(r["relevance_triage"] for r in enriched)),
      "access_check_counts":dict(__import__("collections").Counter(r["access_check"]["status"] for r in enriched)),
      "license_status_counts":dict(__import__("collections").Counter(r["license_rights_status"] for r in enriched)),
      "manual_relevance_pending":len(enriched),"rights_review_pending":len(enriched),
      "manifest_sha256":sha256(payload),"screening_ledger_sha256":sha256(ledger.read_bytes()),
      "freeze_status":"PROVISIONAL_DISCOVERY_SNAPSHOT_ONLY_NOT_AN_ELIGIBLE_CORPUS",
      "limitations":["Keyword/topic relevance is triage only, not a validated classifier or human screening.",
       "URL reachability does not verify full-text completeness or lawful access.",
       "OpenAlex license labels are metadata claims and are not independently verified legal permissions.",
       "Every candidate requires human relevance and rights review before final corpus eligibility."]
    }
    (out/"api_errors.json").write_text(json.dumps(errors,indent=2),encoding="utf-8")
    (out/"snapshot_report.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    (out/"SHA256SUMS.txt").write_text(
      f'{summary["manifest_sha256"]}  candidate_manifest.jsonl\n{summary["screening_ledger_sha256"]}  screening_ledger.csv\n',encoding="utf-8")
    print(json.dumps(summary,indent=2))
    # Retrieval failures are reported but don't hide partial auditable output.
    return 0
if __name__=="__main__": sys.exit(main())
