from __future__ import annotations

import argparse
import time

# Import the complete model registry before creating database sessions so all
# SQLAlchemy relationships are resolved in the worker process too.
import app.models.registry  # noqa: F401

from app.services.indexing import run_once


def main() -> None:
    parser = argparse.ArgumentParser(description="DiscoveryAI background indexing worker")
    parser.add_argument("--once", action="store_true", help="Process at most one queued job and exit")
    parser.add_argument("--interval", type=float, default=5.0, help="Polling interval in seconds")
    args = parser.parse_args()

    if args.once:
        result = run_once()
        print(result or {"status": "idle"})
        return

    print("DiscoveryAI indexing worker started")
    while True:
        result = run_once()
        if result is not None:
            print(result, flush=True)
        else:
            time.sleep(max(args.interval, 1.0))


if __name__ == "__main__":
    main()
