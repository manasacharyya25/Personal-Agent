"""Scan subreddits and search queries; store posts; do not score relevance."""

from datetime import datetime, timezone

from packages.common.logger import get_logger
from packages.database.database import Database
from packages.database.models import ParsedPost
from packages.database.repositories import jobs as job_repo
from packages.database.repositories import reddit_posts as post_repo
from packages.database.repositories import search_queries as search_repo
from packages.database.repositories import sources as source_repo
from packages.integrations.reddit import RedditBrowser

logger = get_logger(__name__)


def run_reddit_ingestion(
    db: Database,
    browser: RedditBrowser,
    job_id: int,
    max_pages: int,
) -> None:
    for source in source_repo.list_active_sources(db):
        logger.info("Scanning subreddit r/%s", source.subreddit)
        start_url = source.pagination_state.get("next_url") if source.pagination_state else None
        start_url = start_url or browser.subreddit_new_url(source.subreddit)
        _crawl_target(
            db,
            browser,
            job_id=job_id,
            start_url=start_url,
            last_seen_post_id=source.last_seen_post_id,
            last_seen_created_at=source.last_seen_created_at,
            pagination_state=source.pagination_state,
            max_pages=max_pages,
            discovery_method="subreddit",
            discovery_query=source.subreddit,
            save_pagination=lambda state, sid=source.id: source_repo.update_source_checkpoint(
                db, sid, pagination_state=state
            ),
            finish=lambda newest_id, newest_at, sid=source.id: source_repo.update_source_checkpoint(
                db,
                sid,
                last_seen_post_id=newest_id,
                last_seen_created_at=newest_at,
                pagination_state=None,
                last_scanned_at=datetime.now(timezone.utc),
            ),
        )

    for search in search_repo.list_active_search_queries(db):
        logger.info("Searching Reddit for %r (%s)", search.query, search.time_filter)
        start_url = search.pagination_state.get("next_url") if search.pagination_state else None
        start_url = start_url or browser.search_url(search.query, search.time_filter)
        _crawl_target(
            db,
            browser,
            job_id=job_id,
            start_url=start_url,
            last_seen_post_id=search.last_seen_post_id,
            last_seen_created_at=search.last_seen_created_at,
            pagination_state=search.pagination_state,
            max_pages=max_pages,
            discovery_method="search",
            discovery_query=search.query,
            save_pagination=lambda state, qid=search.id: search_repo.update_search_checkpoint(
                db, qid, pagination_state=state
            ),
            finish=lambda newest_id, newest_at, qid=search.id: search_repo.update_search_checkpoint(
                db,
                qid,
                last_seen_post_id=newest_id,
                last_seen_created_at=newest_at,
                pagination_state=None,
                last_scanned_at=datetime.now(timezone.utc),
            ),
        )


def _crawl_target(
    db: Database,
    browser: RedditBrowser,
    *,
    job_id: int,
    start_url: str,
    last_seen_post_id: str | None,
    last_seen_created_at,
    pagination_state: dict | None,
    max_pages: int,
    discovery_method: str,
    discovery_query: str,
    save_pagination,
    finish,
) -> None:
    state = dict(pagination_state or {})
    url = start_url
    run_newest_id = state.get("run_newest_post_id")
    run_newest_created = _parse_iso(state.get("run_newest_created_at"))
    hit_checkpoint = False
    pages = 0

    while url and pages < max_pages:
        posts, next_url = browser.fetch_listing(url)
        pages += 1

        if not posts:
            logger.info("No posts on page %s", url)
            url = None
            break

        if not run_newest_id:
            run_newest_id = posts[0].reddit_post_id
            run_newest_created = posts[0].created_at

        for post in posts:
            if last_seen_post_id and post.reddit_post_id == last_seen_post_id:
                hit_checkpoint = True
                break
            if (
                last_seen_created_at
                and post.created_at
                and post.created_at < last_seen_created_at
            ):
                hit_checkpoint = True
                break

            _save_post(db, post, discovery_method, discovery_query, job_id)

        state = {
            "next_url": next_url,
            "run_newest_post_id": run_newest_id,
            "run_newest_created_at": run_newest_created.isoformat()
            if run_newest_created
            else None,
        }
        save_pagination(state)

        if hit_checkpoint:
            break
        url = next_url

    caught_up = hit_checkpoint or not url
    first_run_capped = pages >= max_pages and not last_seen_post_id
    if caught_up or first_run_capped:
        finish(run_newest_id, run_newest_created)


def _save_post(
    db: Database,
    post: ParsedPost,
    discovery_method: str,
    discovery_query: str,
    job_id: int,
) -> None:
    post_id, inserted = post_repo.upsert_discovered_post(db, post)
    post_repo.add_discovery_method(
        db, post_id, discovery_method, discovery_query, job_id
    )
    job_repo.increment_counts(db, job_id, seen=1, inserted=1 if inserted else 0)


def _parse_iso(value: str | None):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None
