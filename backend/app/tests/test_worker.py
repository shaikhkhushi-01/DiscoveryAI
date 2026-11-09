from __future__ import annotations

from app import worker


class _FakeSession:
    def close(self) -> None:
        pass


def test_drain_mode_processes_until_queue_is_empty(monkeypatch):
    results = iter([{"job_id": 1, "status": "completed"}, None])
    recovered_calls: list[bool] = []

    monkeypatch.setattr(worker, "configure_logging", lambda: None)
    monkeypatch.setattr(worker, "SessionLocal", _FakeSession)
    monkeypatch.setattr(
        worker,
        "recover_abandoned_jobs",
        lambda db: recovered_calls.append(True) or 0,
    )
    monkeypatch.setattr(worker, "run_once", lambda: next(results))
    monkeypatch.setattr(worker.signal, "signal", lambda *args: None)

    assert worker.main(["--drain", "--max-runtime-seconds", "30"]) == 0
    assert len(recovered_calls) == 2


def test_worker_rejects_non_positive_runtime_budget():
    try:
        worker.main(["--drain", "--max-runtime-seconds", "0"])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("Expected invalid runtime budget to exit")
