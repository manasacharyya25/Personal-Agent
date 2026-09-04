"""Score discovered Reddit posts against ready categories."""

from __future__ import annotations

import argparse
import traceback
from pathlib import Path

from packages.common.config import get_settings
from packages.common.logger import get_logger
from packages.database.database import Database
from packages.database.repositories import jobs as job_repo
from packages.llm.client import LlmClient

from .service import run_evaluation

logger = get_logger(__name__)
ROOT = Path(__file__).resolve().parents[2]


def migrate(db: Database) -> None:
    applied = db.apply_all_migrations(ROOT / "migrations")
    logger.info("Applied %s", ", ".join(applied))


def evaluate(db: Database, limit: int) -> None:
    settings = get_settings()
    if not settings.LLM_API_KEY:
        raise SystemExit("LLM_API_KEY is missing from .env")

    job_id = job_repo.create_job(db, "evaluate")
    job_repo.mark_running(db, job_id)
    logger.info("Evaluate job %s running", job_id)
    try:
        llm = LlmClient(settings.LLM_API_KEY, settings.LLM_MODEL)
        done = run_evaluation(db, llm, job_id, limit)
        job_repo.mark_completed(db, job_id)
        logger.info("Evaluate job %s completed (%s pairs)", job_id, done)
    except Exception:
        error = traceback.format_exc()
        logger.exception("Evaluate job %s failed", job_id)
        job_repo.mark_failed(db, job_id, error)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Reddit post evaluator")
    parser.add_argument("--migrate", action="store_true")
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()

    settings = get_settings()
    db = Database(settings.DB_CONNECTION_STRING)
    db.connect()
    try:
        if args.migrate:
            migrate(db)
        else:
            evaluate(db, args.limit)
    finally:
        db.close()


if __name__ == "__main__":
    main()
