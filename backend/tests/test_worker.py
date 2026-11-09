from __future__ import annotations

import pytest

from app import worker


def test_drain_mode_processes_jobs_until_queue_is_empty(monkeypatch):
    calls = iter([
        {"job_id": 1, "status": "completed"},
        {"job_id": 2, "status": "completed"},
        None,
    ])
    processed = []

    monkeypatch.setattr(worker, "configure_logging", lambda: None)
    monkeypatch.setattr(worker.signal, "signal", lambda *_args: None)

    def fake_run_once():
        result = next(calls)
        processed.append(result)
        return result

    monkeypatch.setattr(worker, "run_once", fake_run_once)

    assert worker.main(["--drain"]) == 0
    assert len(processed) == 3
    assert processed[-1] is None


def test_drain_mode_rejects_non_positive_runtime():
    with pytest.raises(SystemExit, match="positive integer"):
        worker.main(["--drain", "--max-runtime-seconds", "0"])
