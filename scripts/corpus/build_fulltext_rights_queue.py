#!/usr/bin/env python3
"""Build an auditable per-paper full-text and rights review queue.
No downloads or legal determinations are performed.
"""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path

FIELDS = ["openalex_id","doi","title","publication_year","candidate_pdf_url",
"candidate_landing_page_url","locations_json","openalex_license_claims",
"fulltext_url_status","abstract_status","rights_status","approved_for_text_mining",
"reviewer_id","evidence_url","license_name","license_url","review_notes"]

def read_jsonl(path):
    rows=[]
    for n,line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(),1):
        if not line.strip(): continue
        try: item=json.loads(line)
        except json.JSONDecodeError as exc: raise ValueError(f"Invalid JSONL at line {n}: {exc}") from exc
        if not isinstance(item,dict): raise ValueError(f"JSONL line {n} must be an object")
        rows.append(item)
    return rows

def build_row(item):
    locations=item.get("locations") or []
    if not isinstance(locations,list): locations=[]
    claims=item.get("license_claims_openalex") or []
    if isinstance(claims,str): claims=[claims] if claims else []
    return {
      "openalex_id":item.get("openalex_id") or item.get("id") or "",
      "doi":item.get("doi") or "", "title":item.get("title") or "",
      "publication_year":item.get("publication_year") or "",
      "candidate_pdf_url":item.get("candidate_pdf_url") or "",
      "candidate_landing_page_url":item.get("candidate_landing_page_url") or "",
      "locations_json":json.dumps(locations,ensure_ascii=False,sort_keys=True),
      "openalex_license_claims":";".join(str(x) for x in claims),
      "fulltext_url_status":item.get("full_text_access_status") or "not_checked",
      "abstract_status":item.get("abstract_status") or "unknown",
      "rights_status":"PENDING_HUMAN_REVIEW","approved_for_text_mining":"false",
      "reviewer_id":"","evidence_url":"","license_name":"","license_url":"",
      "review_notes":"Verify exact article version and license terms; URL reachability and OpenAlex metadata are not permission."
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    rows=[build_row(x) for x in read_jsonl(args.input)]
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS); w.writeheader(); w.writerows(rows)
    print(json.dumps({"candidate_count":len(rows),"rights_pending":len(rows),"downloads_performed":0,"output":str(out)},indent=2))
if __name__=="__main__": main()
