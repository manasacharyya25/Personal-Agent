from psycopg2.extras import Json

from packages.database.database import Database


def list_pending_pairs(db: Database, limit: int) -> list[dict]:
    return db.fetch_all(
        """
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
            c.examples,
            c.evaluation_metrics
        FROM pa_reddit_discovered_posts p
        CROSS JOIN pa_categories c
        WHERE c.active = TRUE
          AND c.prompt IS NOT NULL
          AND btrim(c.prompt) <> ''
          AND jsonb_typeof(c.evaluation_metrics) = 'array'
          AND jsonb_array_length(c.evaluation_metrics) > 0
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
