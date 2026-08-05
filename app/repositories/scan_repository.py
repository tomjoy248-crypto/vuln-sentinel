"""扫描结果持久化与分页查询仓库"""

import json
from datetime import datetime
from typing import Any

from app.db.session import get_db


def _deserialize_scan(row: dict[str, Any]) -> dict[str, Any]:
    """将 scans 表行反序列化为标准字典"""
    d = dict(row)
    for json_col in ("findings_json", "summary_json", "details_json"):
        raw = d.pop(json_col, None)
        if raw:
            key = json_col.replace("_json", "")
            try:
                d[key] = json.loads(raw)
            except Exception:
                d[key] = [] if key == "findings" else {}
        elif json_col == "findings_json":
            d["findings"] = []
        elif json_col == "summary_json":
            d["summary"] = {}
        elif json_col == "details_json":
            d["details"] = {}
    return d


def save_scan(
    user_id: int,
    url: str,
    score: int,
    risk_level: str,
    findings: list[dict[str, Any]],
    summary: dict[str, Any] | None,
    crawled_count: int,
    scan_type: str,
    details: dict[str, Any] | None = None,
) -> int:
    import secrets

    share_id = secrets.token_urlsafe(9)[:12]
    conn = get_db()
    try:
        cur = conn.execute(
            """INSERT INTO scans
            (user_id, url, score, risk_level, findings_count, findings_json, summary_json,
             crawled_pages, scan_type, share_id, details_json, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                user_id,
                url,
                score,
                risk_level,
                len(findings),
                json.dumps(findings, ensure_ascii=False),
                json.dumps(summary or {}, ensure_ascii=False),
                crawled_count,
                scan_type,
                share_id,
                json.dumps(details or {}, ensure_ascii=False),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_scan_by_id(
    scan_id: int, user_id: int | None = None
) -> dict[str, Any] | None:
    conn = get_db()
    try:
        if user_id is not None:
            row = conn.execute(
                "SELECT * FROM scans WHERE id=? AND user_id=?", (scan_id, user_id)
            ).fetchone()
        else:
            row = conn.execute("SELECT * FROM scans WHERE id=?", (scan_id,)).fetchone()
        return _deserialize_scan(row) if row else None
    finally:
        conn.close()


def get_scan_by_share_id(share_id: str) -> dict[str, Any] | None:
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT * FROM scans WHERE share_id=?", (share_id,)
        ).fetchone()
        if not row:
            return None
        d = _deserialize_scan(row)
        d.pop("user_id", None)
        return d
    finally:
        conn.close()


def get_scan_history(
    user_id: int,
    limit: int = 20,
    offset: int = 0,
    url_filter: str | None = None,
    risk_level: str | None = None,
) -> tuple[list[dict[str, Any]], int]:
    """获取扫描历史，支持分页和过滤，返回 (items, total)"""
    conn = get_db()
    try:
        where = "WHERE user_id=?"
        params: list[Any] = [user_id]
        if url_filter:
            where += " AND url LIKE ?"
            params.append(f"%{url_filter}%")
        if risk_level:
            where += " AND risk_level=?"
            params.append(risk_level)

        total_row = conn.execute(
            f"SELECT COUNT(*) FROM scans {where}", params  # nosec B608 - where 子句由硬编码条件构建，值通过参数化查询传递
        ).fetchone()
        total = total_row[0] if total_row else 0

        rows = conn.execute(
            f"SELECT * FROM scans {where} ORDER BY id DESC LIMIT ? OFFSET ?",  # nosec B608 - where 子句由硬编码条件构建，值通过参数化查询传递
            params + [limit, offset],
        ).fetchall()
        return [_deserialize_scan(r) for r in rows], total
    finally:
        conn.close()


def get_latest_scan_for_target(user_id: int, url: str) -> dict[str, Any] | None:
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT * FROM scans WHERE user_id=? AND url=? ORDER BY id DESC LIMIT 1",
            (user_id, url),
        ).fetchone()
        return _deserialize_scan(row) if row else None
    finally:
        conn.close()


def get_scan_trend(
    user_id: int,
    limit: int = 30,
    url: str | None = None,
) -> list[dict[str, Any]]:
    """返回用于趋势图的数据点列表"""
    conn = get_db()
    try:
        if url:
            rows = conn.execute(
                "SELECT id, url, score, risk_level, findings_count, created_at "
                "FROM scans WHERE user_id=? AND url LIKE ? ORDER BY id DESC LIMIT ?",
                (user_id, f"%{url}%", limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, url, score, risk_level, findings_count, created_at "
                "FROM scans WHERE user_id=? ORDER BY id DESC LIMIT ?",
                (user_id, limit),
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def delete_scan_history(user_id: int) -> int:
    conn = get_db()
    try:
        cur = conn.execute("DELETE FROM scans WHERE user_id=?", (user_id,))
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()
