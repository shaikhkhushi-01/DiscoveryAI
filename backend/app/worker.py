"""Durable PostgreSQL-backed indexing worker."""
from __future__ import annotations
import logging
import signal
import time
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.session import SessionLocal
from app.services.indexing import WORKER_POLL_SECONDS, recover_abandoned_jobs, run_once

_running = True

def _stop(signum, frame):
    global _running
    logging.getLogger(__name__).info("worker shutdown requested signal=%s", signum)
    _running = False

def main() -> None:
    configure_logging()
    logger = logging.getLogger("discoveryai.worker")
    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)
    logger.info("durable indexing worker started provider=%s model=%s poll_seconds=%s",
                settings.embedding_provider, settings.embedding_model, WORKER_POLL_SECONDS)
    while _running:
        try:
            db = SessionLocal()
            try:
                recovered = recover_abandoned_jobs(db)
                if recovered:
                    logger.warning("worker recovered abandoned jobs count=%s", recovered)
            finally:
                db.close()
            result = run_once()
            if result is None:
                time.sleep(WORKER_POLL_SECONDS)
            else:
                logger.info("worker processed job result=%s", result)
        except Exception:
            logger.exception("worker loop failed; will retry")
            time.sleep(WORKER_POLL_SECONDS)
    logger.info("durable indexing worker stopped")

if __name__ == "__main__":
    main()
