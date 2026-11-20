"""End-to-end engineering smoke test for the five-system comparison CLI.

All inputs are synthetic fixtures. This test validates plumbing only and must
never be interpreted as a research benchmark result.
"""
import json
import subprocess
import sys
from pathlib import Path

from app.services.evaluation.baselines import BASELINE_SYSTEMS
from app.tests.test_baseline_comparison import _write_baseline_inputs


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
COMPARISON_SCRIPT = REPOSITORY_ROOT / "scripts" / "evaluation" / "compare_discovery_gap_baselines.py"


def test_five_system_comparison_cli_end_to_end_with_synthetic_fixture(tmp_path):
    benchmark, prediction_paths = _write_baseline_inputs(tmp_path, evidence_count=1)
    output = tmp_path / "synthetic-comparison.json"

    command = [
        sys.executable,
        str(COMPARISON_SCRIPT),
        "--benchmark", str(benchmark),
        "--split", "test",
        "--evidence-budget", "2",
        "--output", str(output),
    ]
    for system in BASELINE_SYSTEMS:
        command.extend([f"--{system.replace('_', '-')}", str(prediction_paths[system])])

    completed = subprocess.run(
        command, cwd=REPOSITORY_ROOT, capture_output=True, text=True,
        check=False, timeout=30,
    )
    assert completed.returncode == 0, completed.stdout + "\n" + completed.stderr
    cli_result = json.loads(completed.stdout)
    report = json.loads(output.read_text(encoding="utf-8"))

    assert cli_result["ok"] is True
    assert cli_result["systems"] == list(BASELINE_SYSTEMS)
    assert cli_result["record_count"] == 1
    assert report["protocol"]["split"] == "test"
    assert report["protocol"]["shared_max_evidence_items_per_record"] == 2
    assert set(report["systems"]) == set(BASELINE_SYSTEMS)
    assert set(report["paired_full_system_comparisons"]) == set(BASELINE_SYSTEMS) - {"discoveryai_full"}
