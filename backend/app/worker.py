"""Durable PostgreSQL-backed indexing worker.

Run continuously with `python -m app.worker`, or use `--drain` in
short-lived schedulers such as GitHub Actions. Drain mode processes queued jobs
until the queue is empty or its runtime budget is reached, then exits cleanly.
"""
from __future__ import annotations

import argparse
import logging
import signal
import time

from app.core.config import settings
from app.core.logging import configure_logging
# Register ORM relationships before opening worker database sessions.
import app.models.registry  # noqa: F401

from app.services.indexing import WORKER_POLL_SECONDS, run_once

_running = True


def _stop(signum, frame):
    global _running
    logging.getLogger(__name__).info("worker shutdown requested signal=%s", signum)
    _running = False


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="DiscoveryAI durable indexing worker")
    parser.add_argument(
        "--drain",
        action="store_true",
        help="Process queued jobs until the queue is empty, then exit (for scheduled runners).",
    )
    parser.add_argument(
        "--max-runtime-seconds",
        type=int,
        default=21_000,
        help="Maximum time to spend draining jobs (default: 5h50m; ignored without --drain).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.max_runtime_seconds < 1:
        raise SystemExit("--max-runtime-seconds must be a positive integer")

    configure_logging()
    logger = logging.getLogger("discoveryai.worker")
    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)
    logger.info(
        "durable indexing worker started provider=%s model=%s poll_seconds=%s drain=%s",
        settings.embedding_provider,
        settings.embedding_model,
        WORKER_POLL_SECONDS,
        args.drain,
    )

    started = time.monotonic()
    while _running:
        if args.drain and time.monotonic() - started >= args.max_runtime_seconds:
            logger.warning("worker drain runtime budget reached; remaining jobs stay queued")
            break

        try:
            # run_once() recovers expired leases, atomically claims one job,
            # processes it, and returns None when the durable queue is empty.
            result = run_once()
            if result is None:
                if args.drain:
                    logger.info("worker queue is empty; drain completed")
                    break
                time.sleep(WORKER_POLL_SECONDS)
            else:
                logger.info("worker processed job result=%s", result)
        except Exception:
            logger.exception("worker loop failed")
            if args.drain:
                # Fail the scheduled run visibly. The next schedule can retry
                # queued work after stale-job recovery.
                return 1
            time.sleep(WORKER_POLL_SECONDS)

    logger.info("durable indexing worker stopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
