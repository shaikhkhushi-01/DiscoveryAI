#!/usr/bin/env python3
"""Compute inter-annotator agreement and emit an adjudication queue."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"backend"))
from app.services.evaluation.expert_validation import analyze_expert_agreement,write_agreement_report


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotator-a",required=True,type=Path)
    parser.add_argument("--annotator-b",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args()
    try:
        a=json.loads(args.annotator_a.read_text(encoding="utf-8"))
        b=json.loads(args.annotator_b.read_text(encoding="utf-8"))
        report=analyze_expert_agreement(a,b)
        write_agreement_report(report,args.output)
    except (OSError,json.JSONDecodeError,ValueError) as exc:
        print(json.dumps({"ok":False,"error":str(exc)},indent=2))
        return 1
    print(json.dumps({"ok":True,"record_count":report["record_count"],
        "adjudication_count":len(report["adjudication_queue"]),"output":str(args.output)},indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
