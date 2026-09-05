from psycopg2 import errors as pg_errors
from psycopg2.extras import Json

from packages.database.database import Database


class CategoryInUseError(Exception):
    pass


class DuplicateNameError(Exception):
    pass


def _metrics(value) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return []


def list_categories(db: Database) -> list[dict]:
    return db.fetch_all(
        """
        SELECT id, name, purpose, prompt, examples, evaluation_metrics, active, created_at
        FROM pa_categories
        ORDER BY name ASC
        """
    )


def list_ready_categories(db: Database) -> list[dict]:
    rows = db.fetch_all(
        """
        SELECT id, name, purpose, prompt, examples, evaluation_metrics, active
        FROM pa_categories
        WHERE active = TRUE
          AND prompt IS NOT NULL
          AND btrim(prompt) <> ''
        ORDER BY name ASC
        """
    )
    return rows


def create_category(
    db: Database,
    name: str,
    *,
    purpose: str | None = None,
    prompt: str | None = None,
    examples: str | None = None,
    evaluation_metrics: list | None = None,
    active: bool = True,
) -> dict:
    try:
        row = db.execute_returning(
            """
            INSERT INTO pa_categories (name, purpose, prompt, examples, evaluation_metrics, active)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, name, purpose, prompt, examples, evaluation_metrics, active, created_at
            """,
            (
                name.strip(),
                purpose,
                prompt,
                examples,
                Json(_metrics(evaluation_metrics)),
                active,
            ),
        )
        return row
    except pg_errors.UniqueViolation:
        db.connection.rollback()
        raise DuplicateNameError(name)


def update_category(
    db: Database,
    category_id: int,
    *,
    name: str | None = None,
    purpose: str | None = None,
    prompt: str | None = None,
    examples: str | None = None,
    evaluation_metrics: list | None = None,
    active: bool | None = None,
) -> dict | None:
    row = db.fetch_one("SELECT * FROM pa_categories WHERE id = %s", (category_id,))
    if not row:
        return None
    next_metrics = (
        evaluation_metrics if evaluation_metrics is not None else row["evaluation_metrics"]
    )
    try:
        return db.execute_returning(
            """
            UPDATE pa_categories
            SET name = %s,
                purpose = %s,
                prompt = %s,
                examples = %s,
                evaluation_metrics = %s,
                active = %s
            WHERE id = %s
            RETURNING id, name, purpose, prompt, examples, evaluation_metrics, active, created_at
            """,
            (
                name if name is not None else row["name"],
                purpose if purpose is not None else row["purpose"],
                prompt if prompt is not None else row["prompt"],
                examples if examples is not None else row["examples"],
                Json(_metrics(next_metrics)),
                active if active is not None else row["active"],
                category_id,
            ),
        )
    except pg_errors.UniqueViolation:
        db.connection.rollback()
        raise DuplicateNameError(name or row["name"])


def delete_category(db: Database, category_id: int) -> bool:
    in_use = db.fetch_one(
        """
        SELECT
            (SELECT count(*) FROM pa_reddit_sources WHERE category_id = %s)
          + (SELECT count(*) FROM pa_reddit_search_queries WHERE category_id = %s)
            AS n
        """,
        (category_id, category_id),
    )
    if in_use and in_use["n"]:
        raise CategoryInUseError()
    row = db.execute_returning(
        "DELETE FROM pa_categories WHERE id = %s RETURNING id",
        (category_id,),
    )
    return row is not None
