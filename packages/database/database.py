from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor


class Database:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connection = None

    def connect(self) -> None:
        self.connection = psycopg2.connect(self.connection_string)

    def close(self) -> None:
        if self.connection:
            self.connection.close()
            self.connection = None

    def apply_migration(self, path: Path) -> None:
        sql = path.read_text(encoding="utf-8")
        with self.connection.cursor() as cursor:
            cursor.execute(sql)
        self.connection.commit()

    def execute(self, query: str, params=None) -> None:
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

    def fetch_all(self, query: str, params=None) -> list[dict]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            return list(cursor.fetchall())

    def fetch_one(self, query: str, params=None) -> dict | None:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()

    def execute_returning(self, query: str, params=None) -> dict | None:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                row = cursor.fetchone()
            self.connection.commit()
            return row
        except Exception:
            self.connection.rollback()
            raise
