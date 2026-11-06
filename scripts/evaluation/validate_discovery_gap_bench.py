#!/usr/bin/env python3
"""Validate a DiscoveryGapBench JSON file without computing scores."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.services.evaluation.discovery_gap_bench import load_benchmark  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("benchmark", type=Path, help="Path to a DiscoveryGapBench JSON file")
    parser.add_argument(
        "--require-evaluable",
        action="store_true",
        help="Exit non-zero unless at least one adjudicated record is available",
    )
    args = parser.parse_args()
    try:
        _, report = load_benchmark(args.benchmark, require_evaluable=args.require_evaluable)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, indent=2))
        return 1
    print(json.dumps(report.to_dict(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
