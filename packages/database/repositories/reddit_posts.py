from psycopg2.extras import Json

from packages.database.database import Database
from packages.database.models import ParsedPost


def upsert_discovered_post(db: Database, post: ParsedPost) -> tuple[int, bool]:
    """Insert a post. Returns (id, inserted). Idempotent on reddit_post_id."""
    row = db.execute_returning(
        """
        INSERT INTO pa_reddit_discovered_posts (
            reddit_post_id, subreddit, author, title, body, url, created_at, metadata
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (reddit_post_id) DO NOTHING
        RETURNING id
        """,
        (
            post.reddit_post_id,
            post.subreddit,
            post.author,
            post.title,
            post.body,
            post.url,
            post.created_at,
            Json(post.metadata),
        ),
    )
    if row:
        return row["id"], True

    existing = db.fetch_one(
        "SELECT id FROM pa_reddit_discovered_posts WHERE reddit_post_id = %s",
        (post.reddit_post_id,),
    )
    if not existing:
        raise RuntimeError(f"Post {post.reddit_post_id} missing after upsert")
    return existing["id"], False


def add_discovery_method(
    db: Database,
    post_id: int,
    discovery_method: str,
    discovery_query: str,
    job_id: int | None,
) -> None:
    db.execute(
        """
        INSERT INTO pa_reddit_post_discovery_method (
            post_id, discovery_method, discovery_query, job_id
        )
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (post_id, discovery_method, discovery_query) DO NOTHING
        """,
        (post_id, discovery_method, discovery_query, job_id),
    )
