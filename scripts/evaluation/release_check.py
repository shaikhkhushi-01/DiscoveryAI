from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_PATHS = [
    "backend/app/main.py",
    "backend/app/api/public_dashboard.py",
    "backend/app/api/gaps.py",
    "backend/app/api/evidence.py",
    "backend/app/api/trends.py",
    "backend/app/api/agents.py",
    "backend/app/api/intelligence.py",
    "backend/app/services/evidence/scoring.py",
    "backend/app/services/trends/engine.py",
    "backend/app/services/agents/coordinator.py",
    "backend/app/services/experiments/planner.py",
    "backend/app/services/evaluation/discovery_gap_bench.py",
    "backend/app/services/evaluation/runner.py",
    "backend/app/services/evaluation/baselines.py",
    "backend/app/services/evaluation/ablations.py",
    "backend/app/services/evaluation/expert_validation.py",
    "backend/app/tests/test_discovery_gap_bench.py",
    "backend/app/tests/test_discovery_gap_bench_runner.py",
    "backend/app/tests/test_baseline_comparison.py",
    "backend/app/tests/test_ablation_studies.py",
    "backend/app/tests/test_expert_validation.py",
    "frontend/lib/api.ts",
    "frontend/app/page.tsx",
    "data/evaluation/discovery_gap_bench.schema.json",
    "research/discovery_gap_bench_annotation_rubric.md",
    "research/phase4_evaluation_runner_protocol.md",
    "research/phase4_baseline_comparison_protocol.md",
    "research/phase4_ablation_study_protocol.md",
    "research/phase4_expert_validation_protocol.md",
    "research/final_release_checklist.md",
]

# Verify that important route modules are both imported and registered by FastAPI.
ROUTER_WIRING = {
    "public_dashboard_router": "backend/app/api/public_dashboard.py",
    "gaps_router": "backend/app/api/gaps.py",
    "evidence_router": "backend/app/api/evidence.py",
    "trends_router": "backend/app/api/trends.py",
    "agents_router": "backend/app/api/agents.py",
    "intelligence_router": "backend/app/api/intelligence.py",
}

ROUTE_DECLARATIONS = {
    "backend/app/api/public_dashboard.py": [
        'prefix="/api/v1/public"',
        '@router.get("/overview")',
        '@router.get("/gaps")',
        '@router.get("/trends")',
        '@router.post("/graph-rag/retrieve")',
    ],
    "backend/app/api/gaps.py": [
        'prefix="/api/v1/gaps"',
        '@router.get("")',
        '@router.post("/critic")',
        '@router.post("/report")',
    ],
    "backend/app/api/evidence.py": [
        'prefix="/api/v1/evidence"',
        '@router.get("/opportunities")',
    ],
    "backend/app/api/trends.py": [
        'prefix="/api/v1/trends"',
        '@router.get("")',
    ],
    "backend/app/api/agents.py": [
        'prefix="/api/v1/agents"',
        '@router.post("/discover")',
    ],
    "backend/app/api/intelligence.py": [
        'prefix="/api/v1/intelligence"',
        '@router.post("/hypotheses")',
        '@router.post("/compare")',
        '@router.post("/literature-review")',
    ],
}


def main() -> int:
    errors: list[str] = []
    missing = [path for path in REQUIRED_PATHS if not (ROOT / path).is_file()]
    errors.extend(f"missing required file: {path}" for path in missing)

    main_path = ROOT / "backend/app/main.py"
    main_source = main_path.read_text(encoding="utf-8") if main_path.is_file() else ""
    if '@app.get("/health"' not in main_source:
        errors.append("missing /health endpoint")
    for router_name, module_path in ROUTER_WIRING.items():
        module_name = Path(module_path).stem
        if f"from app.api.{module_name} import router as {router_name}" not in main_source:
            errors.append(f"router import missing: {router_name}")
        if f"app.include_router({router_name})" not in main_source:
            errors.append(f"router registration missing: {router_name}")

    for relative_path, required_tokens in ROUTE_DECLARATIONS.items():
        path = ROOT / relative_path
        if not path.is_file():
            continue
        source = path.read_text(encoding="utf-8")
        for token in required_tokens:
            if token not in source:
                errors.append(f"route declaration missing in {relative_path}: {token}")

    compose_path = ROOT / "docker-compose.yml"
    compose = compose_path.read_text(encoding="utf-8") if compose_path.is_file() else ""
    for service in ("postgres", "neo4j", "qdrant", "redis", "backend", "frontend"):
        if re.search(rf"^  {service}:$", compose, re.MULTILINE) is None:
            errors.append(f"missing Compose service: {service}")

    schema_path = ROOT / "data/evaluation/discovery_gap_bench.schema.json"
    if schema_path.is_file():
        import json

        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            if schema.get("type") != "object" or not schema.get("properties"):
                errors.append("benchmark JSON Schema must define an object with properties")
        except (json.JSONDecodeError, OSError) as exc:
            errors.append(f"benchmark JSON Schema is invalid: {exc}")

    if errors:
        print("RELEASE CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("RELEASE CHECK: PASS")
    print(f"Required files verified: {len(REQUIRED_PATHS)}")
    print(f"Critical routers imported and registered: {len(ROUTER_WIRING)}")
    print(f"Critical route declarations verified: {sum(map(len, ROUTE_DECLARATIONS.values()))}")
    print("Compose services verified: 6")
    print("Benchmark JSON Schema: valid JSON object schema")
    print("Note: this is a static repository check, not a live integration or scientific validation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
