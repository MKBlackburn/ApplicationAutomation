"""Local metadata tracking. Keep applicant answers, credentials, and resumes out of events."""
import sqlite3
from pathlib import Path

STATUSES = {"discovered", "qualification_blocked", "qualified", "preparation_approved",
            "awaiting_final_review", "blocked"}


class Tracker:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        with sqlite3.connect(path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, job_id TEXT NOT NULL, status TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)")

    def record(self, job_id: str, status: str) -> None:
        if status not in STATUSES or not job_id.strip():
            raise ValueError("Invalid tracking event")
        with sqlite3.connect(self.path) as db:
            db.execute("INSERT INTO events (job_id, status) VALUES (?, ?)", (job_id, status))

    def events(self) -> list[tuple]:
        with sqlite3.connect(self.path) as db:
            return db.execute("SELECT job_id, status FROM events ORDER BY id").fetchall()
