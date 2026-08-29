from packages.database.database import Database
from packages.database.models import RedditSearchQuery


def _query_from_row(row: dict) -> RedditSearchQuery:
    return RedditSearchQuery(
        id=row["id"],
        query=row["query"],
        time_filter=row["time_filter"],
        category_id=row["category_id"],
        active=row["active"],
        priority=row["priority"],
        last_seen_post_id=row["last_seen_post_id"],
        last_seen_created_at=row["last_seen_created_at"],
        pagination_state=row["pagination_state"],
        last_scanned_at=row["last_scanned_at"],
    )


def list_active_search_queries(db: Database) -> list[RedditSearchQuery]:
    rows = db.fetch_all(
        """
        SELECT id, query, time_filter, category_id, active, priority,
               last_seen_post_id, last_seen_created_at,
               pagination_state, last_scanned_at
        FROM pa_reddit_search_queries
        WHERE active = TRUE
        ORDER BY priority DESC, id ASC
        """
    )
    return [_query_from_row(row) for row in rows]


def update_search_checkpoint(
    db: Database,
    query_id: int,
    *,
    last_seen_post_id: str | None = None,
    last_seen_created_at=None,
    pagination_state: dict | None = None,
    last_scanned_at=None,
) -> None:
    from psycopg2.extras import Json

    db.execute(
        """
        UPDATE pa_reddit_search_queries
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
            query_id,
        ),
    )
