"""Check Postgres/Supabase: connect, insert, read, delete."""

from packages.common.config import get_settings
from packages.database.database import Database

NOTE = "pa-connection-test"


def main() -> None:
    settings = get_settings()
    db = Database(settings.DB_CONNECTION_STRING)
    db.connect()
    print("connected")

    try:
        db.execute("CREATE TEMP TABLE pa_connection_test (id SERIAL PRIMARY KEY, note TEXT)")
        row = db.execute_returning(
            "INSERT INTO pa_connection_test (note) VALUES (%s) RETURNING id, note",
            (NOTE,),
        )
        print(f"wrote id={row['id']} note={row['note']}")

        found = db.fetch_one(
            "SELECT id, note FROM pa_connection_test WHERE id = %s",
            (row["id"],),
        )
        if not found:
            raise SystemExit("read failed: row missing after insert")
        print(f"read id={found['id']}")

        deleted = db.execute_returning(
            "DELETE FROM pa_connection_test WHERE id = %s RETURNING id",
            (row["id"],),
        )
        leftover = db.fetch_one(
            "SELECT id FROM pa_connection_test WHERE id = %s",
            (row["id"],),
        )
        if not deleted or leftover:
            raise SystemExit("delete failed")
        print("deleted")
        print("ok")
    finally:
        db.close()


if __name__ == "__main__":
    main()
