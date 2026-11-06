#!/usr/bin/env python3
"""Compare LLM-only, vector RAG, GraphRAG, hybrid, and full DiscoveryAI."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.services.evaluation.baselines import (  # noqa: E402
    BASELINE_SYSTEMS,
    compare_baselines,
    write_comparison,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", required=True, type=Path)
    parser.add_argument("--split", default="test", choices=("train", "validation", "test"))
    parser.add_argument("--evidence-budget", type=int, default=8)
    parser.add_argument("--output", required=True, type=Path)
    for system in BASELINE_SYSTEMS:
        parser.add_argument(f"--{system.replace('_', '-')}", required=True, type=Path, dest=system)
    args = parser.parse_args()
    try:
        predictions = {system: getattr(args, system) for system in BASELINE_SYSTEMS}
        report = compare_baselines(
            args.benchmark,
            predictions,
            split=args.split,
            evidence_budget=args.evidence_budget,
        )
        write_comparison(report, args.output)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 1
    print(json.dumps({
        "ok": True,
        "output": str(args.output),
        "systems": list(report["systems"]),
        "record_count": report["protocol"]["record_count"],
        "split": report["protocol"]["split"],
        "evidence_budget": report["protocol"]["shared_max_evidence_items_per_record"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
