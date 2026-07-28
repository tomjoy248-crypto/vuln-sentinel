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
import sqlite3
from typing import Any, Dict, List, Optional

from app.core.logging import get_request_id
from app.db.session import get_db

logger = logging.getLogger("vuln_sentinel.audit")


def save_audit_log(
    user_id: Optional[int],
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    client_ip: Optional[str] = None,
) -> Optional[int]:
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
                json.dumps(details or {}, ensure_ascii=False),
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
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Dict[str, Any]]:
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
        params: List[Any] = []
        if user_id is not None:
            where_parts.append("user_id = ?")
            params.append(user_id)
        if action:
            where_parts.append("action = ?")
            params.append(action)
        if resource_type:
            where_parts.append("resource_type = ?")
            params.append(resource_type)
        where_clause = "WHERE " + " AND ".join(where_parts) if where_parts else ""
        sql = f"""SELECT id, user_id, action, resource_type, resource_id,
                         details_json, client_ip, request_id, created_at
                  FROM audit_logs
                  {where_clause}
                  ORDER BY created_at DESC
                  LIMIT ? OFFSET ?"""
        params.extend([limit, offset])
        rows = conn.execute(sql, params).fetchall()
        conn.close()
        return [
            {
                "id": r["id"],
                "user_id": r["user_id"],
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
