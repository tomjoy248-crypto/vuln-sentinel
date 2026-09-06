"""审计日志模块。

提供结构化的审计日志记录与查询能力，
覆盖所有写操作：登录、扫描、导出、角色变更、敏感数据删除。

设计原则：
- 不阻塞主流程：失败时静默丢弃，不影响业务
- request_id 关联：每个审计记录自动关联当前请求的 request_id
- JSON 详情：详情字段存储为 JSON，便于扩展和查询
"""

from __future__ import annotations

import json
import logging
from collections import Counter
from datetime import datetime, timedelta
from typing import Any

from app.core.logging import get_request_id
from app.core.sanitization import redact_sensitive_data
from app.db.session import get_db

logger = logging.getLogger("vuln_sentinel.audit")


def save_audit_log(
    user_id: int | None,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    details: dict[str, Any] | None = None,
    client_ip: str | None = None,
) -> int | None:
    """保存审计日志。

    Args:
        user_id: 操作用户 ID（未登录为 None）
        action: 动作名称，如 login, scan, export, delete, role_change
        resource_type: 资源类型，如 user, scan, ticket, asset, team
        resource_id: 资源标识（可选）
        details: 额外详情字典（可选）
        client_ip: 客户端 IP（可选）

    Returns:
        插入的审计日志 ID，失败返回 None
    """
    # 审计日志必须脱敏，避免密码、Token、密钥等敏感信息入库
    safe_details = redact_sensitive_data(details or {})
    try:
        conn = get_db()
        conn.execute(
            """INSERT INTO audit_logs
                (user_id, action, resource_type, resource_id, details_json, client_ip, request_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                user_id,
                action,
                resource_type,
                resource_id,
                json.dumps(safe_details, ensure_ascii=False),
                client_ip,
                get_request_id(),
            ),
        )
        conn.commit()
        row_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.close()
        return row_id
    except Exception as e:
        logger.warning("Audit log save failed: %s", e)
        return None


def get_audit_logs(
    user_id: int | None = None,
    action: str | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    username: str | None = None,
    status: str | None = None,
    start_at: str | None = None,
    end_at: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """查询审计日志。

    Args:
        user_id: 过滤特定用户（None 不过滤）
        action: 过滤特定动作（None 不过滤）
        resource_type: 过滤资源类型（None 不过滤）
        limit: 返回条数上限
        offset: 偏移量

    Returns:
        审计日志列表
    """
    try:
        conn = get_db()
        where_parts = []
        params: list[Any] = []
        if user_id is not None:
            where_parts.append("user_id = ?")
            params.append(user_id)
        if action:
            where_parts.append("action = ?")
            params.append(action)
        if resource_type:
            where_parts.append("resource_type = ?")
            params.append(resource_type)
        if resource_id:
            where_parts.append("resource_id LIKE ?")
            params.append(f"%{resource_id}%")
        if username:
            where_parts.append("u.username LIKE ?")
            params.append(f"%{username}%")
        if status:
            where_parts.append("json_extract(details_json, '$.status') = ?")
            params.append(status)
        if start_at:
            where_parts.append("created_at >= ?")
            params.append(start_at)
        if end_at:
            where_parts.append("created_at <= ?")
            params.append(end_at)
        where_clause = "WHERE " + " AND ".join(where_parts) if where_parts else ""
        sql = f"""SELECT id, user_id, action, resource_type, resource_id,
                         details_json, client_ip, request_id, created_at,
                         u.username AS username
                  FROM audit_logs
                  LEFT JOIN users u ON u.id = audit_logs.user_id
                  {where_clause}
                  ORDER BY created_at DESC
                  LIMIT ? OFFSET ?"""  # nosec B608 - where_clause 由硬编码列名构建，值通过参数化查询传递
        params.extend([limit, offset])
        rows = conn.execute(sql, params).fetchall()
        conn.close()
        return [
            {
                "id": r["id"],
                "user_id": r["user_id"],
                "username": r["username"],
                "action": r["action"],
                "resource_type": r["resource_type"],
                "resource_id": r["resource_id"],
                "details": json.loads(r["details_json"] or "{}"),
                "client_ip": r["client_ip"],
                "request_id": r["request_id"],
                "created_at": r["created_at"],
            }
            for r in rows
        ]
    except Exception as e:
        logger.warning("Audit log query failed: %s", e)
        return []


def get_audit_summary() -> dict[str, Any]:
    """Return compact aggregate counts for the administrator dashboard."""
    try:
        conn = get_db()
        total = conn.execute("SELECT COUNT(*) AS count FROM audit_logs").fetchone()["count"]
        by_action = conn.execute(
            "SELECT action, COUNT(*) AS count FROM audit_logs GROUP BY action ORDER BY count DESC LIMIT 50"
        ).fetchall()
        by_status = conn.execute(
            "SELECT COALESCE(json_extract(details_json, '$.status'), 'unknown') AS status, COUNT(*) AS count "
            "FROM audit_logs GROUP BY status ORDER BY count DESC"
        ).fetchall()
        conn.close()
        return {
            "total": total,
            "by_action": [{"action": row["action"], "count": row["count"]} for row in by_action],
            "by_status": [{"status": row["status"], "count": row["count"]} for row in by_status],
        }
    except Exception as e:
        logger.warning("Audit summary query failed: %s", e)
        return {"total": 0, "by_action": [], "by_status": []}


def get_admin_dashboard_stats(days: int = 30) -> dict[str, Any]:
    """Build bounded dashboard aggregates for administrators.

    Aggregation is performed in Python for finding JSON so the same endpoint
    works with both the local SQLite database and the PostgreSQL compatibility
    layer. No request bodies, credentials, or raw response contents are
    returned.

    Args:
        days: Number of recent calendar days to include, from 1 to 365.

    Returns:
        Scan, finding, task, and audit aggregates suitable for charts.
    """
    days = max(1, min(int(days), 365))
    today = datetime.utcnow().date()
    period_dates = [
        (today - timedelta(days=days - index - 1)).isoformat()
        for index in range(days)
    ]
    since = period_dates[0]
    empty = {
        "period_days": days,
        "scans": {"total": 0, "by_day": [{"date": day, "count": 0} for day in period_dates], "by_risk": []},
        "findings": {"total": 0, "by_severity": [], "by_type": []},
        "tasks": {"total": 0, "by_status": [], "failed": 0},
        "audit": {"total": 0, "by_action": []},
    }
    try:
        conn = get_db()
        scan_rows = conn.execute(
            "SELECT created_at, risk_level, findings_json FROM scans WHERE created_at >= ? ORDER BY created_at ASC LIMIT 10000",
            (since,),
        ).fetchall()
        day_counts: Counter[str] = Counter()
        risk_counts: Counter[str] = Counter()
        severity_counts: Counter[str] = Counter()
        finding_type_counts: Counter[str] = Counter()
        day_counts.update({day: 0 for day in period_dates})
        for row in scan_rows:
            created = str(row["created_at"] or "")
            day_counts[created[:10] or "unknown"] += 1
            risk_counts[str(row["risk_level"] or "unknown")] += 1
            try:
                findings = json.loads(row["findings_json"] or "[]")
            except (TypeError, ValueError):
                findings = []
            if isinstance(findings, list):
                for finding in findings:
                    if isinstance(finding, dict):
                        severity_counts[str(finding.get("severity") or "info")] += 1
                        finding_type_counts[str(finding.get("type") or finding.get("name") or "unknown")] += 1
        try:
            task_rows = conn.execute(
                "SELECT status, COUNT(*) AS count FROM scan_task_records WHERE updated_at >= ? GROUP BY status",
                (since,),
            ).fetchall()
        except Exception:
            task_rows = []
        try:
            audit_rows = conn.execute(
                "SELECT action, COUNT(*) AS count FROM audit_logs WHERE created_at >= ? GROUP BY action ORDER BY count DESC LIMIT 30",
                (since,),
            ).fetchall()
        except Exception:
            audit_rows = []
        try:
            audit_total = conn.execute(
                "SELECT COUNT(*) AS count FROM audit_logs WHERE created_at >= ?", (since,)
            ).fetchone()["count"]
        except Exception:
            audit_total = 0
        conn.close()
        task_counts = {str(row["status"]): int(row["count"] or 0) for row in task_rows}
        return {
            "period_days": days,
            "scans": {
                "total": len(scan_rows),
                "by_day": [{"date": key, "count": day_counts[key]} for key in period_dates],
                "by_risk": [
                    {"risk": key, "count": value}
                    for key, value in risk_counts.most_common()
                ],
            },
            "findings": {
                "total": sum(severity_counts.values()),
                "by_severity": [
                    {"severity": key, "count": value}
                    for key, value in severity_counts.most_common()
                ],
                "by_type": [
                    {"type": key, "count": value}
                    for key, value in finding_type_counts.most_common(30)
                ],
            },
            "tasks": {
                "total": sum(task_counts.values()),
                "by_status": [
                    {"status": key, "count": value}
                    for key, value in sorted(task_counts.items())
                ],
                "failed": task_counts.get("failed", 0) + task_counts.get("timeout", 0),
            },
            "audit": {
                "total": int(audit_total or 0),
                "by_action": [
                    {"action": row["action"], "count": int(row["count"] or 0)}
                    for row in audit_rows
                ],
            },
        }
    except Exception as exc:
        logger.warning("Admin dashboard aggregation failed: %s", exc)
        return empty
