import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from core.models import Task

DB_PATH = Path(__file__).parent.parent / "data" / "never_forget.db"


def _dt(val) -> datetime:
    if val is None:
        return None
    if isinstance(val, datetime):
        return val
    return datetime.fromisoformat(str(val))


def _connect():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _connect() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS tasks (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                title        TEXT NOT NULL,
                description  TEXT DEFAULT '',
                deadline     TIMESTAMP NOT NULL,
                status       TEXT DEFAULT 'active',
                threat_level INTEGER DEFAULT 0,
                created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reminded_at  TIMESTAMP,
                completed_at TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS reminder_log (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id      INTEGER NOT NULL,
                triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                method       TEXT,
                acknowledged INTEGER DEFAULT 0,
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            );
        """)


def _row_to_task(row) -> Task:
    return Task(
        id=row["id"],
        title=row["title"],
        description=row["description"] or "",
        deadline=_dt(row["deadline"]),
        status=row["status"],
        threat_level=row["threat_level"],
        created_at=_dt(row["created_at"]),
        reminded_at=_dt(row["reminded_at"]),
        completed_at=_dt(row["completed_at"]),
    )


def add_task(task: Task) -> int:
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO tasks (title, description, deadline) VALUES (?, ?, ?)",
            (task.title, task.description, task.deadline.isoformat()),
        )
        return cur.lastrowid


def get_active_tasks() -> List[Task]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM tasks WHERE status = 'active' ORDER BY deadline ASC"
        ).fetchall()
    return [_row_to_task(r) for r in rows]


def get_all_tasks() -> List[Task]:
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM tasks ORDER BY deadline ASC").fetchall()
    return [_row_to_task(r) for r in rows]


def update_reminded_at(task_id: int):
    with _connect() as conn:
        conn.execute(
            "UPDATE tasks SET reminded_at = ? WHERE id = ?",
            (datetime.now().isoformat(), task_id),
        )


def escalate_threat(task_id: int):
    with _connect() as conn:
        conn.execute(
            "UPDATE tasks SET threat_level = MIN(threat_level + 1, 4) WHERE id = ?",
            (task_id,),
        )


def mark_completed(task_id: int):
    with _connect() as conn:
        conn.execute(
            "UPDATE tasks SET status = 'completed', completed_at = ? WHERE id = ?",
            (datetime.now().isoformat(), task_id),
        )


def update_task(task_id: int, title: str, description: str, deadline):
    with _connect() as conn:
        conn.execute(
            "UPDATE tasks SET title=?, description=?, deadline=? WHERE id=?",
            (title, description, deadline.isoformat(), task_id),
        )


def delete_task(task_id: int):
    with _connect() as conn:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))


def log_reminder(task_id: int, method: str):
    with _connect() as conn:
        conn.execute(
            "INSERT INTO reminder_log (task_id, method) VALUES (?, ?)",
            (task_id, method),
        )
