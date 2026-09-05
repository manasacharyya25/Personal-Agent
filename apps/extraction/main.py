"""Run Reddit ingestion: migrate or scrape. Pulls posts; does not score them."""

from __future__ import annotations

import argparse
import traceback
from pathlib import Path

from playwright.sync_api import sync_playwright

from packages.common.config import get_settings
from packages.common.logger import get_logger
from packages.database.database import Database
from packages.database.repositories import jobs as job_repo
from packages.integrations.reddit import RedditBrowser
from .reddit import run_reddit_ingestion

logger = get_logger(__name__)
ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS = ROOT / "migrations"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)


def migrate(db: Database) -> None:
    applied = db.apply_all_migrations(MIGRATIONS)
    logger.info("Applied %s", ", ".join(applied))


def scrape(db: Database) -> None:
    settings = get_settings()
    job_id = job_repo.create_job(db, "reddit")
    job_repo.mark_running(db, job_id)
    logger.info("Ingestion job %s running", job_id)

    profile = Path(settings.PLAYWRIGHT_USER_DATA_DIR)
    if not profile.is_absolute():
        profile = ROOT / profile
    profile.mkdir(parents=True, exist_ok=True)

    if settings.PLAYWRIGHT_HEADLESS:
        logger.info(
            "Headless is on. If Reddit asks for login, set PLAYWRIGHT_HEADLESS=false "
            "for this run so you can sign in; the profile is reused next time."
        )

    try:
        with sync_playwright() as playwright:
            # context = playwright.chromium.launch_persistent_context(
            #     user_data_dir=str(profile),
            #     headless=settings.PLAYWRIGHT_HEADLESS,
            #     viewport={"width": 1280, "height": 800},
            #     user_agent=USER_AGENT,
            # )
            context = playwright.chromium.launch_persistent_context(
                user_data_dir=str(profile),
                channel="chrome",  # real Chrome
                headless=False,
                ignore_default_args=["--enable-automation"],
                args=["--disable-blink-features=AutomationControlled"],
            )
            try:
                page = context.pages[0] if context.pages else context.new_page()
                reddit = RedditBrowser(
                    page,
                    request_delay_seconds=settings.REDDIT_REQUEST_DELAY_SECONDS,
                    max_retries=settings.REDDIT_MAX_RETRIES,
                )
                reddit.ensure_session()
                run_reddit_ingestion(
                    db,
                    reddit,
                    job_id,
                    max_pages=settings.REDDIT_MAX_PAGES_PER_TARGET,
                    post_delay_min=settings.REDDIT_POST_DELAY_MIN_SECONDS,
                    post_delay_max=settings.REDDIT_POST_DELAY_MAX_SECONDS,
                    subreddit_max_age_hours=settings.REDDIT_SUBREDDIT_MAX_AGE_HOURS,
                )
            finally:
                context.close()
        job_repo.mark_completed(db, job_id)
        logger.info("Ingestion job %s completed", job_id)
    except Exception:
        error = traceback.format_exc()
        logger.exception("Ingestion job %s failed", job_id)
        job_repo.mark_failed(db, job_id, error)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Reddit ingestion")
    parser.add_argument(
        "--migrate",
        action="store_true",
        help="Create pa_ tables and seed categories, then exit",
    )
    args = parser.parse_args()

    settings = get_settings()
    db = Database(settings.DB_CONNECTION_STRING)
    db.connect()
    try:
        if args.migrate:
            migrate(db)
        else:
            scrape(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
