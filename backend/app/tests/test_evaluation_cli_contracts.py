import subprocess
import sys
from pathlib import Path

import pytest

from app.services.evaluation.baselines import BASELINE_SYSTEMS, compare_baselines
from app.tests.test_baseline_comparison import _write_baseline_inputs


ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.parametrize(
    "script",
    [
        "run_discovery_gap_bench.py",
        "compare_discovery_gap_baselines.py",
        "run_discovery_gap_ablations.py",
        "package_evaluation_run.py",
    ],
)
def test_evaluation_cli_help_smoke(script):
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "evaluation" / script), "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=20,
    )
    assert completed.returncode == 0, completed.stderr
    assert "usage:" in completed.stdout.lower()


def test_baseline_comparison_rejects_non_object_prediction_row(tmp_path):
    benchmark, paths = _write_baseline_inputs(tmp_path)
    import json

    payload = json.loads(paths["llm_only"].read_text(encoding="utf-8"))
    payload["predictions"][0] = "not-an-object"
    paths["llm_only"].write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match=r"predictions\\[0\\] must be an object"):
        compare_baselines(benchmark, paths)


def test_baseline_comparison_rejects_missing_run_metadata(tmp_path):
    benchmark, paths = _write_baseline_inputs(tmp_path)
    import json

    payload = json.loads(paths["graph_rag"].read_text(encoding="utf-8"))
    payload.pop("run_metadata")
    paths["graph_rag"].write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="run_metadata must be an object"):
        compare_baselines(benchmark, paths)


def test_baseline_system_contract_has_exactly_five_systems():
    assert BASELINE_SYSTEMS == (
        "llm_only",
        "vector_rag",
        "graph_rag",
        "hybrid_retrieval",
        "discoveryai_full",
    )
