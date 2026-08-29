from packages.database.database import Database

JOB_PENDING = "pending"
JOB_RUNNING = "running"
JOB_COMPLETED = "completed"
JOB_FAILED = "failed"


def create_job(db: Database, job_type: str) -> int:
    row = db.execute_returning(
        """
        INSERT INTO pa_ingestion_jobs (job_type, status)
        VALUES (%s, %s)
        RETURNING id
        """,
        (job_type, JOB_PENDING),
    )
    return row["id"]


def mark_running(db: Database, job_id: int) -> None:
    db.execute(
        """
        UPDATE pa_ingestion_jobs
        SET status = %s, started_at = now()
        WHERE id = %s
        """,
        (JOB_RUNNING, job_id),
    )


def mark_completed(db: Database, job_id: int) -> None:
    db.execute(
        """
        UPDATE pa_ingestion_jobs
        SET status = %s, completed_at = now()
        WHERE id = %s
        """,
        (JOB_COMPLETED, job_id),
    )


def mark_failed(db: Database, job_id: int, error: str) -> None:
    db.execute(
        """
        UPDATE pa_ingestion_jobs
        SET status = %s, completed_at = now(), last_error = %s
        WHERE id = %s
        """,
        (JOB_FAILED, error[:4000], job_id),
    )


def increment_counts(db: Database, job_id: int, seen: int = 0, inserted: int = 0) -> None:
    db.execute(
        """
        UPDATE pa_ingestion_jobs
        SET posts_seen = posts_seen + %s,
            posts_inserted = posts_inserted + %s
        WHERE id = %s
        """,
        (seen, inserted, job_id),
    )
