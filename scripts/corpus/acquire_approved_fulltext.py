#!/usr/bin/env python3
"""Download only PDFs explicitly approved by a human rights reviewer."""
from __future__ import annotations
import argparse,csv,hashlib,json,re
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import URLError,HTTPError

MAX_BYTES=50*1024*1024
REQUIRED=["candidate_pdf_url","reviewer_id","evidence_url","license_name","license_url"]
def safe_name(value):
    return (re.sub(r"[^A-Za-z0-9._-]+","_",value or "")[:120] or "paper")
def approved(row):
    return (row.get("approved_for_text_mining","").strip().lower()=="true"
      and all(row.get(k,"").strip() for k in REQUIRED)
      and bool((row.get("openalex_id") or "").strip() or (row.get("doi") or "").strip()))
def download_one(row,out_dir):
    url=row["candidate_pdf_url"].strip()
    if not url.lower().startswith("https://"): return {"status":"blocked_non_https","url":url}
    ident=safe_name(row.get("openalex_id") or row.get("doi"))
    req=Request(url,headers={"User-Agent":"DiscoveryAI-ApprovedFullText/1.0","Accept":"application/pdf"})
    try:
        with urlopen(req,timeout=30) as response:
            final=response.geturl()
            if not final.lower().startswith("https://"): return {"status":"blocked_redirect_non_https","url":final}
            ctype=response.headers.get("Content-Type","").lower()
            data=response.read(MAX_BYTES+1)
            if len(data)>MAX_BYTES: return {"status":"blocked_size_limit","url":final}
            if not data.startswith(b"%PDF-") or not ("pdf" in ctype or "octet-stream" in ctype):
                return {"status":"not_verified_pdf","url":final,"content_type":ctype}
            digest=hashlib.sha256(data).hexdigest()
            path=out_dir/(ident+".pdf"); path.write_bytes(data)
            return {"status":"downloaded_after_human_approval","url":final,"path":str(path),
              "bytes":len(data),"sha256":digest,"reviewer_id":row["reviewer_id"],
              "evidence_url":row["evidence_url"],"license_name":row["license_name"],"license_url":row["license_url"]}
    except (HTTPError,URLError,TimeoutError,OSError) as exc:
        return {"status":"download_error","url":url,"error":str(exc)[:500]}
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--approvals",required=True,help="Private human-reviewed approval CSV; never commit it")
    ap.add_argument("--out",default="data/private_fulltext")
    ap.add_argument("--audit",default="data/private_fulltext_download_audit.jsonl")
    args=ap.parse_args()
    out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    audit=Path(args.audit); audit.parent.mkdir(parents=True,exist_ok=True)
    results=[]
    with open(args.approvals,newline="",encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if not approved(row):
                result={"status":"skipped_not_fully_approved","openalex_id":row.get("openalex_id"),"doi":row.get("doi")}
            else: result=download_one(row,out)
            result["openalex_id"]=row.get("openalex_id"); result["doi"]=row.get("doi")
            results.append(result)
    with audit.open("w",encoding="utf-8") as f:
        for item in results: f.write(json.dumps(item,ensure_ascii=False,sort_keys=True)+"\n")
    counts={}
    for item in results: counts[item["status"]]=counts.get(item["status"],0)+1
    print(json.dumps({"processed":len(results),"status_counts":counts,"audit":str(audit)},indent=2))
if __name__=="__main__": main()
