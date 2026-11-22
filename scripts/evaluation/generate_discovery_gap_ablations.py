#!/usr/bin/env python3
"""Generate the six predeclared, component-controlled ablation predictions."""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.services.evaluation.ablation_prediction_adapters import generate_ablation_predictions  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--split", choices=("train", "validation", "test"), default="test")
    parser.add_argument("--evidence-budget", type=int, default=8)
    parser.add_argument("--code-revision", required=True)
    parser.add_argument("--model-provider", required=True)
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--prompt-version", default="ablation-prompt-v1")
    parser.add_argument("--embedding-model", default="configured-embedding-provider")
    parser.add_argument("--retrieval-config", default="top_k=8;reranker=repository-default")
    args = parser.parse_args()
    try:
        outputs = asyncio.run(generate_ablation_predictions(
            args.benchmark, args.output_dir, split=args.split,
            evidence_budget=args.evidence_budget, code_revision=args.code_revision,
            model_provider=args.model_provider, model_name=args.model_name,
            prompt_version=args.prompt_version, embedding_model=args.embedding_model,
            retrieval_config=args.retrieval_config,
        ))
    except (OSError, json.JSONDecodeError, ValueError, RuntimeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 1
    print(json.dumps({"ok": True, "outputs": outputs, "variants": sorted(outputs),
                      "split": args.split}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
