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


def list_sources(db: Database) -> list[dict]:
    return db.fetch_all(
        """
        SELECT s.id, s.subreddit, s.category_id, c.name AS category_name,
               s.active, s.priority, s.added_by,
               s.last_seen_post_id, s.last_seen_created_at, s.last_scanned_at
        FROM pa_reddit_sources s
        JOIN pa_categories c ON c.id = s.category_id
        ORDER BY s.priority DESC, s.id ASC
        """
    )


def create_source(
    db: Database,
    subreddit: str,
    category_id: int,
    active: bool = True,
    priority: int = 0,
    added_by: str = "dashboard",
) -> dict:
    from psycopg2 import errors as pg_errors

    name = subreddit.removeprefix("r/").strip("/")
    try:
        return db.execute_returning(
            """
            INSERT INTO pa_reddit_sources (subreddit, category_id, active, priority, added_by)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, subreddit, category_id, active, priority, added_by
            """,
            (name, category_id, active, priority, added_by),
        )
    except pg_errors.UniqueViolation:
        db.connection.rollback()
        raise
    except pg_errors.ForeignKeyViolation:
        db.connection.rollback()
        raise


def update_source(
    db: Database,
    source_id: int,
    *,
    category_id: int | None = None,
    active: bool | None = None,
    priority: int | None = None,
) -> dict | None:
    row = db.fetch_one("SELECT * FROM pa_reddit_sources WHERE id = %s", (source_id,))
    if not row:
        return None
    next_category = category_id if category_id is not None else row["category_id"]
    next_active = active if active is not None else row["active"]
    next_priority = priority if priority is not None else row["priority"]
    return db.execute_returning(
        """
        UPDATE pa_reddit_sources
        SET category_id = %s, active = %s, priority = %s
        WHERE id = %s
        RETURNING id, subreddit, category_id, active, priority
        """,
        (next_category, next_active, next_priority, source_id),
    )


def delete_source(db: Database, source_id: int) -> bool:
    row = db.execute_returning(
        "DELETE FROM pa_reddit_sources WHERE id = %s RETURNING id",
        (source_id,),
    )
    return row is not None


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
