"""Safe local SQLite backup and restore helpers for the desktop app."""

from __future__ import annotations

import os
import shutil
import sqlite3
import tempfile
from pathlib import Path


MAX_BACKUP_BYTES = 512 * 1024 * 1024


def backup_database(db_path: str, destination: str) -> dict[str, object]:
    """Create a consistent SQLite backup using the SQLite backup API."""
    source = Path(db_path).resolve()
    target = Path(destination).resolve()
    if not source.is_file():
        raise FileNotFoundError("数据库文件不存在")
    if source == target:
        raise ValueError("备份文件不能覆盖当前数据库")
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix="vuln-sentinel-db-", suffix=".db", dir=str(target.parent))
    os.close(fd)
    try:
        with sqlite3.connect(str(source), timeout=10) as source_conn, sqlite3.connect(temp_name) as target_conn:
            source_conn.backup(target_conn)
        shutil.move(temp_name, target)
    finally:
        if os.path.exists(temp_name):
            os.remove(temp_name)
    return {"path": str(target), "bytes": target.stat().st_size}


def validate_backup(path: str) -> dict[str, object]:
    """Validate that a backup is a readable SQLite database."""
    candidate = Path(path).resolve()
    if not candidate.is_file() or candidate.stat().st_size > MAX_BACKUP_BYTES:
        raise ValueError("备份文件不存在或超过 512MB")
    with sqlite3.connect(str(candidate), timeout=5) as conn:
        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        tables = conn.execute("SELECT count(*) FROM sqlite_master WHERE type='table'").fetchone()[0]
    if integrity != "ok":
        raise ValueError("备份数据库完整性校验失败")
    return {"path": str(candidate), "bytes": candidate.stat().st_size, "tables": int(tables), "integrity": integrity}
