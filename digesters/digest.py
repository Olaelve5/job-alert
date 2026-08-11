import sqlite3
from typing import List
from dotenv import load_dotenv

load_dotenv()


class BaseDigest:
    """Base class for fetching pending jobs and marking them as notified."""

    def __init__(
        self,
        db_path: str = "jobs.db",
        min_score: int = 6,
        max_jobs: int = 10,
    ):
        self.db_path = db_path
        self.min_score = min_score
        self.max_jobs = max_jobs

    def get_unnotified_jobs(self, max_jobs: int = None) -> List[sqlite3.Row]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM jobs 
            WHERE is_junior = 1
              AND is_notified = 0
              AND score >= ?
            ORDER BY score DESC
        """,
            (self.min_score,),
        )

        jobs = cursor.fetchall()
        if max_jobs is not None:
            jobs = jobs[:max_jobs]

        conn.commit()   
        conn.close()
        return jobs

    def mark_as_notified(self, job_ids: List[str]):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.executemany(
            "UPDATE jobs SET is_notified = 1 WHERE job_id = ?",
            [(j_id,) for j_id in job_ids],
        )
        conn.commit()
        conn.close()

    def send(self) -> None:
        raise NotImplementedError("Subclasses must implement send()")
