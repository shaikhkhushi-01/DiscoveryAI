#!/usr/bin/env python3
"""Compare full DiscoveryAI with controlled component-removal runs."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.services.evaluation.ablations import ABLATION_VARIANTS, compare_ablations, write_ablation_report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", required=True, type=Path)
    parser.add_argument("--split", default="test", choices=("train", "validation", "test"))
    parser.add_argument("--output", required=True, type=Path)
    for variant in ABLATION_VARIANTS:
        parser.add_argument(f"--{variant.replace('_', '-')}", required=True, type=Path, dest=variant)
    args = parser.parse_args()
    try:
        files = {variant: getattr(args, variant) for variant in ABLATION_VARIANTS}
        report = compare_ablations(args.benchmark, files, split=args.split)
        write_ablation_report(report, args.output)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 1
    print(json.dumps({"ok": True, "output": str(args.output), "variants": list(report["variants"]),
                      "record_count": report["protocol"]["record_count"], "split": report["protocol"]["split"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
