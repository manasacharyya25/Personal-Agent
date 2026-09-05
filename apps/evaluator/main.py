"""Score discovered Reddit posts against ready categories."""

from __future__ import annotations

import argparse
import traceback
from pathlib import Path

from packages.common.config import get_settings
from packages.common.logger import get_logger
from packages.database.database import Database
from packages.database.repositories import jobs as job_repo
from packages.database.repositories.categories import get_category_by_name
from packages.llm.client import LlmClient

from .service import dump_prompts, run_evaluation

logger = get_logger(__name__)
ROOT = Path(__file__).resolve().parents[2]


def migrate(db: Database) -> None:
    applied = db.apply_all_migrations(ROOT / "migrations")
    logger.info("Applied %s", ", ".join(applied))


def dump_prompt_files(db: Database, limit: int, out_dir: Path) -> None:
    written = dump_prompts(db, out_dir, limit)
    if not written:
        logger.warning("No ready post/category pairs to dump")
        return
    logger.info("Wrote %s prompt files under %s", len(written), out_dir)


def evaluate(db: Database, limit: int, category: str | None = None) -> None:
    settings = get_settings()
    category_id = None
    if category:
        row = get_category_by_name(db, category)
        if not row:
            raise SystemExit(f"Category not found: {category}")
        category_id = row["id"]
        logger.info("Filtering to category %s (id %s)", row["name"], category_id)

    job_id = job_repo.create_job(db, "evaluate")
    job_repo.mark_running(db, job_id)
    logger.info(
        "Evaluate job %s running (%s @ %s)",
        job_id,
        settings.LLM_MODEL,
        settings.OLLAMA_BASE_URL,
    )
    try:
        llm = LlmClient(settings.LLM_MODEL, settings.OLLAMA_BASE_URL)
        done = run_evaluation(db, llm, job_id, limit, category_id=category_id)
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
    parser.add_argument(
        "--dump-prompts",
        action="store_true",
        help="Write evaluator prompts to text files; do not call the LLM",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "output" / "evaluator-prompts",
        help="Folder for --dump-prompts files",
    )
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument(
        "--category",
        help="Only evaluate posts for this category name",
    )
    args = parser.parse_args()

    settings = get_settings()
    db = Database(settings.DB_CONNECTION_STRING)
    db.connect()
    try:
        if args.migrate:
            migrate(db)
        elif args.dump_prompts:
            dump_prompt_files(db, args.limit or 10, args.out)
        else:
            evaluate(db, args.limit or 50, category=args.category)
    finally:
        db.close()


if __name__ == "__main__":
    main()
