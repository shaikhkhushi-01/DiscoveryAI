#!/usr/bin/env python3
"""Run secret-safe, read-only preflight checks for Phase 4 live integrations."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.services.evaluation.phase4_readiness import run_phase4_readiness  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-blocked",
        action="store_true",
        help="Return exit code 0 even when one or more dependencies are not ready.",
    )
    args = parser.parse_args()
    report = run_phase4_readiness()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["ready"] or args.allow_blocked else 1


if __name__ == "__main__":
    raise SystemExit(main())
