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


def list_search_queries(db: Database) -> list[dict]:
    return db.fetch_all(
        """
        SELECT q.id, q.query, q.time_filter, q.category_id, c.name AS category_name,
               q.active, q.priority, q.added_by,
               q.last_seen_post_id, q.last_seen_created_at, q.last_scanned_at
        FROM pa_reddit_search_queries q
        JOIN pa_categories c ON c.id = q.category_id
        ORDER BY q.priority DESC, q.id ASC
        """
    )


def create_search_query(
    db: Database,
    query: str,
    time_filter: str,
    category_id: int,
    active: bool = True,
    priority: int = 0,
    added_by: str = "dashboard",
) -> dict:
    from psycopg2 import errors as pg_errors

    try:
        return db.execute_returning(
            """
            INSERT INTO pa_reddit_search_queries
                (query, time_filter, category_id, active, priority, added_by)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, query, time_filter, category_id, active, priority, added_by
            """,
            (query.strip(), time_filter, category_id, active, priority, added_by),
        )
    except pg_errors.UniqueViolation:
        db.connection.rollback()
        raise
    except pg_errors.ForeignKeyViolation:
        db.connection.rollback()
        raise


def update_search_query(
    db: Database,
    query_id: int,
    *,
    time_filter: str | None = None,
    category_id: int | None = None,
    active: bool | None = None,
    priority: int | None = None,
) -> dict | None:
    row = db.fetch_one(
        "SELECT * FROM pa_reddit_search_queries WHERE id = %s", (query_id,)
    )
    if not row:
        return None
    return db.execute_returning(
        """
        UPDATE pa_reddit_search_queries
        SET time_filter = %s, category_id = %s, active = %s, priority = %s
        WHERE id = %s
        RETURNING id, query, time_filter, category_id, active, priority
        """,
        (
            time_filter if time_filter is not None else row["time_filter"],
            category_id if category_id is not None else row["category_id"],
            active if active is not None else row["active"],
            priority if priority is not None else row["priority"],
            query_id,
        ),
    )


def delete_search_query(db: Database, query_id: int) -> bool:
    row = db.execute_returning(
        "DELETE FROM pa_reddit_search_queries WHERE id = %s RETURNING id",
        (query_id,),
    )
    return row is not None


def list_active_search_queries(db: Database) -> list[RedditSearchQuery]:
    rows = db.fetch_all(
        """
        SELECT q.id, q.query, q.time_filter, q.category_id, q.active, q.priority,
               q.last_seen_post_id, q.last_seen_created_at,
               q.pagination_state, q.last_scanned_at
        FROM pa_reddit_search_queries q
        JOIN pa_categories c ON c.id = q.category_id
        WHERE q.active = TRUE
          AND c.active = TRUE
        ORDER BY q.priority DESC, q.id ASC
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
