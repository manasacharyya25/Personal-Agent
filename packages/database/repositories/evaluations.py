from psycopg2.extras import Json

from packages.database.database import Database


def list_pending_pairs(db: Database, limit: int) -> list[dict]:
    """Posts paired only with categories on the subreddit or search that found them."""
    return db.fetch_all(
        """
        WITH post_categories AS (
            SELECT d.post_id, s.category_id
            FROM pa_reddit_post_discovery_method d
            JOIN pa_reddit_sources s
              ON d.discovery_method = 'subreddit'
             AND s.subreddit = d.discovery_query
            UNION
            SELECT d.post_id, q.category_id
            FROM pa_reddit_post_discovery_method d
            JOIN pa_reddit_search_queries q
              ON d.discovery_method = 'search'
             AND q.query = d.discovery_query
        )
        SELECT
            p.id AS post_id,
            p.reddit_post_id,
            p.subreddit,
            p.author,
            p.title,
            p.body,
            p.url,
            c.id AS category_id,
            c.name AS category_name,
            c.purpose,
            c.prompt,
            c.examples
        FROM post_categories pc
        JOIN pa_reddit_discovered_posts p ON p.id = pc.post_id
        JOIN pa_categories c ON c.id = pc.category_id
        WHERE c.active = TRUE
          AND c.prompt IS NOT NULL
          AND btrim(c.prompt) <> ''
          AND NOT EXISTS (
              SELECT 1
              FROM pa_post_evaluations e
              WHERE e.post_id = p.id AND e.category_id = c.id
          )
        ORDER BY p.first_discovered_at DESC, c.id ASC
        LIMIT %s
        """,
        (limit,),
    )


def list_dump_pairs(db: Database, limit: int) -> list[dict]:
    """Source-linked pairs for prompt preview. Includes discovery method/query."""
    return db.fetch_all(
        """
        WITH post_sources AS (
            SELECT d.post_id, d.discovery_method, d.discovery_query, s.category_id
            FROM pa_reddit_post_discovery_method d
            JOIN pa_reddit_sources s
              ON d.discovery_method = 'subreddit'
             AND s.subreddit = d.discovery_query
            UNION
            SELECT d.post_id, d.discovery_method, d.discovery_query, q.category_id
            FROM pa_reddit_post_discovery_method d
            JOIN pa_reddit_search_queries q
              ON d.discovery_method = 'search'
             AND q.query = d.discovery_query
        )
        SELECT
            p.id AS post_id,
            p.reddit_post_id,
            p.subreddit,
            p.author,
            p.title,
            p.body,
            p.url,
            p.first_discovered_at,
            ps.discovery_method,
            ps.discovery_query,
            c.id AS category_id,
            c.name AS category_name,
            c.purpose,
            c.prompt,
            c.examples
        FROM post_sources ps
        JOIN pa_reddit_discovered_posts p ON p.id = ps.post_id
        JOIN pa_categories c ON c.id = ps.category_id
        WHERE c.active = TRUE
          AND c.prompt IS NOT NULL
          AND btrim(c.prompt) <> ''
        ORDER BY
            CASE WHEN btrim(COALESCE(p.body, '')) = '' THEN 1 ELSE 0 END,
            p.first_discovered_at DESC,
            c.id ASC
        LIMIT %s
        """,
        (limit,),
    )


def upsert_evaluation(
    db: Database,
    *,
    post_id: int,
    category_id: int,
    scores: dict,
    mean_score: float,
    reason: str,
    job_id: int | None,
) -> None:
    db.execute(
        """
        INSERT INTO pa_post_evaluations (
            post_id, category_id, scores, mean_score, reason, job_id
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (post_id, category_id) DO UPDATE SET
            scores = EXCLUDED.scores,
            mean_score = EXCLUDED.mean_score,
            reason = EXCLUDED.reason,
            evaluated_at = now(),
            job_id = EXCLUDED.job_id
        """,
        (post_id, category_id, Json(scores), mean_score, reason, job_id),
    )


def list_evaluations(
    db: Database,
    *,
    category_id: int | None = None,
    limit: int = 100,
) -> list[dict]:
    return db.fetch_all(
        """
        SELECT
            e.id,
            e.post_id,
            e.category_id,
            e.scores,
            e.mean_score,
            e.reason,
            e.evaluated_at,
            p.reddit_post_id,
            p.subreddit,
            p.author,
            p.title,
            p.body,
            p.url,
            c.name AS category_name
        FROM pa_post_evaluations e
        JOIN pa_reddit_discovered_posts p ON p.id = e.post_id
        JOIN pa_categories c ON c.id = e.category_id
        WHERE (%s IS NULL OR e.category_id = %s)
        ORDER BY e.mean_score DESC, e.evaluated_at DESC
        LIMIT %s
        """,
        (category_id, category_id, limit),
    )
