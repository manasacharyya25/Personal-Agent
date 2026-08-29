from packages.database.database import Database
from packages.database.models import RedditSource


def _source_from_row(row: dict) -> RedditSource:
    return RedditSource(
        id=row["id"],
        subreddit=row["subreddit"],
        category_id=row["category_id"],
        active=row["active"],
        priority=row["priority"],
        last_seen_post_id=row["last_seen_post_id"],
        last_seen_created_at=row["last_seen_created_at"],
        pagination_state=row["pagination_state"],
        last_scanned_at=row["last_scanned_at"],
    )


def list_active_sources(db: Database) -> list[RedditSource]:
    rows = db.fetch_all(
        """
        SELECT id, subreddit, category_id, active, priority,
               last_seen_post_id, last_seen_created_at,
               pagination_state, last_scanned_at
        FROM pa_reddit_sources
        WHERE active = TRUE
        ORDER BY priority DESC, id ASC
        """
    )
    return [_source_from_row(row) for row in rows]


def update_source_checkpoint(
    db: Database,
    source_id: int,
    *,
    last_seen_post_id: str | None = None,
    last_seen_created_at=None,
    pagination_state: dict | None = None,
    last_scanned_at=None,
) -> None:
    from psycopg2.extras import Json

    db.execute(
        """
        UPDATE pa_reddit_sources
        SET last_seen_post_id = COALESCE(%s, last_seen_post_id),
            last_seen_created_at = COALESCE(%s, last_seen_created_at),
            pagination_state = %s,
            last_scanned_at = COALESCE(%s, last_scanned_at)
        WHERE id = %s
        """,
        (
            last_seen_post_id,
            last_seen_created_at,
            Json(pagination_state) if pagination_state is not None else None,
            last_scanned_at,
            source_id,
        ),
    )
