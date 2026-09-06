"""Best-effort persistence for local scan task state.

Only task metadata and scan results are stored. Authentication headers are
intentionally excluded so a desktop database never becomes a session vault.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from app.db.session import get_db

logger = logging.getLogger("vuln_sentinel.task_persistence")


def _ensure_table(conn: Any) -> None:
    conn.execute(
        """CREATE TABLE IF NOT EXISTS scan_task_records (
            task_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            url TEXT NOT NULL,
            depth TEXT NOT NULL,
            status TEXT NOT NULL,
            progress INTEGER DEFAULT 0,
            created_at TEXT,
            started_at TEXT,
            completed_at TEXT,
            result_json TEXT,
            error TEXT,
            retry_count INTEGER DEFAULT 0,
            previous_task_id TEXT,
            has_sensitive_context INTEGER DEFAULT 0,
            updated_at TEXT
        )"""
    )
    # Keep existing desktop databases compatible with the persistence upgrade.
    try:
        columns = {
            row["name"] if hasattr(row, "keys") else row[1]
            for row in conn.execute("PRAGMA table_info(scan_task_records)").fetchall()
        }
    except Exception:
        # PostgreSQL does not implement PRAGMA; an idempotent ALTER below is
        # enough for its migration path.
        columns = set()
    if "has_sensitive_context" not in columns:
        try:
            conn.execute(
                "ALTER TABLE scan_task_records ADD COLUMN has_sensitive_context INTEGER DEFAULT 0"
            )
        except Exception:
            # The column may already exist in PostgreSQL after a concurrent
            # worker completed the migration.
            pass
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_scan_task_records_user ON scan_task_records(user_id)"
    )


def save_task(task: Any) -> None:
    """Persist a task snapshot without authentication material."""
    try:
        conn = get_db()
        _ensure_table(conn)
        result = task.result
        result_json = json.dumps(result, ensure_ascii=False, default=str) if result is not None else None
        if result_json and len(result_json) > 2 * 1024 * 1024:
            result_json = result_json[:2 * 1024 * 1024]
        conn.execute(
            """INSERT INTO scan_task_records
               (task_id, user_id, url, depth, status, progress, created_at,
               started_at, completed_at, result_json, error, retry_count,
                previous_task_id, has_sensitive_context, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
               ON CONFLICT(task_id) DO UPDATE SET
                status=excluded.status, progress=excluded.progress,
                started_at=excluded.started_at, completed_at=excluded.completed_at,
                result_json=excluded.result_json, error=excluded.error,
                retry_count=excluded.retry_count, previous_task_id=excluded.previous_task_id,
                has_sensitive_context=excluded.has_sensitive_context,
                updated_at=CURRENT_TIMESTAMP""",
            (
                task.task_id,
                str(task.user_id),
                task.url,
                task.depth,
                task.status.value,
                task.progress,
                task.created_at,
                task.started_at,
                task.completed_at,
                result_json,
                task.error,
                getattr(task, "retry_count", 0),
                getattr(task, "previous_task_id", None),
                int(bool(getattr(task, "has_sensitive_context", False))),
            ),
        )
        conn.commit()
        conn.close()
    except Exception as exc:
        logger.debug("Task persistence unavailable: %s", exc)


def load_tasks() -> list[dict[str, Any]]:
    """Load persisted task metadata, returning an empty list on cold start."""
    try:
        conn = get_db()
        _ensure_table(conn)
        rows = conn.execute(
            "SELECT * FROM scan_task_records ORDER BY COALESCE(updated_at, created_at) DESC LIMIT 500"
        ).fetchall()
        conn.close()
        tasks: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            try:
                item["result"] = json.loads(item.pop("result_json") or "null")
            except (TypeError, ValueError):
                item["result"] = None
            tasks.append(item)
        return tasks
    except Exception as exc:
        logger.debug("Task persistence load unavailable: %s", exc)
        return []
