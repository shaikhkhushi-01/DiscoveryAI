#!/usr/bin/env python3
"""Run DiscoveryGapBench evaluation from adjudicated gold and system predictions."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.services.evaluation.runner import evaluate_benchmark, write_report  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", required=True, type=Path, help="Validated DiscoveryGapBench JSON")
    parser.add_argument("--predictions", required=True, type=Path, help="System prediction JSON")
    parser.add_argument("--split", default="test", choices=("train", "validation", "test"))
    parser.add_argument("--output", required=True, type=Path, help="Output report JSON path")
    args = parser.parse_args()
    try:
        report = evaluate_benchmark(args.benchmark, args.predictions, split=args.split)
        write_report(report, args.output)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 1
    print(json.dumps({
        "ok": True,
        "output": str(args.output),
        "evaluated_record_count": report["benchmark"]["evaluated_record_count"],
        "metrics": report["metrics"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
