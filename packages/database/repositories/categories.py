from psycopg2 import errors as pg_errors

from packages.database.database import Database


class CategoryInUseError(Exception):
    pass


class DuplicateNameError(Exception):
    pass


def list_categories(db: Database) -> list[dict]:
    return db.fetch_all(
        """
        SELECT id, name, created_at
        FROM pa_categories
        ORDER BY name ASC
        """
    )


def create_category(db: Database, name: str) -> dict:
    try:
        row = db.execute_returning(
            """
            INSERT INTO pa_categories (name)
            VALUES (%s)
            RETURNING id, name, created_at
            """,
            (name.strip(),),
        )
        return row
    except pg_errors.UniqueViolation:
        db.connection.rollback()
        raise DuplicateNameError(name)


def rename_category(db: Database, category_id: int, name: str) -> dict | None:
    try:
        return db.execute_returning(
            """
            UPDATE pa_categories
            SET name = %s
            WHERE id = %s
            RETURNING id, name, created_at
            """,
            (name.strip(), category_id),
        )
    except pg_errors.UniqueViolation:
        db.connection.rollback()
        raise DuplicateNameError(name)


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
