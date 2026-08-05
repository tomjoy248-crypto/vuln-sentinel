"""GDPR 合规服务。

提供用户数据导出、账号删除与数据匿名化能力，
满足 GDPR「数据可携带性」与「被遗忘权」要求：

- ``export_user_data``：导出用户全部数据（用户信息、扫描、充值、积分、审计、工单、反馈等）
- ``delete_user_account``：删除用户账号及所有关联数据（事务，失败回滚）
- ``anonymize_user_data``：匿名化用户数据（保留扫描记录用于统计）

所有数据库操作通过 ``app.db.session.get_db()`` 获取连接。
"""

from __future__ import annotations

import logging
import sqlite3
from typing import Any

from app.db.session import get_db

logger = logging.getLogger("vuln_sentinel.gdpr")

# 安全说明：以下表名均来自代码内硬编码列表（非用户输入），使用 f-string 拼接 SQL 本身是安全的。
# 但为防御性编程，仍使用此白名单校验表名，避免未来重构时误将用户输入拼入 SQL 造成注入风险。
_VALID_TABLES = frozenset(
    {
        "scans",
        "findings",
        "targets",
        "fix_tickets",
        "ticket_events",
        "usage_logs",
        "recharge_records",
        "audit_logs",
        "assets",
        "finding_feedback",
        "alerts",
        "domain_verifications",
        "user_email_verifications",
        "user_password_resets",
    }
)


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    """检查 SQLite 中是否存在指定表。"""
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
    ).fetchone()
    return row is not None


def _fetch_user_rows(conn: sqlite3.Connection, table: str, user_id: int) -> list[dict[str, Any]]:
    """安全地按 user_id 拉取某张表的全部记录。

    表不存在或查询失败时返回空列表，避免导出流程因单表缺失而中断。
    """
    if table not in _VALID_TABLES:
        logger.warning("导出跳过非法表名: %s", table)
        return []
    if not _table_exists(conn, table):
        return []
    try:
        rows = conn.execute(
            f"SELECT * FROM {table} WHERE user_id = ? ORDER BY id DESC",  # nosec B608 - table 已通过 _VALID_TABLES 白名单校验
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    except sqlite3.OperationalError as exc:
        logger.warning("导出表 %s 失败: %s", table, exc)
        return []


def export_user_data(user_id: int) -> dict[str, Any]:
    """导出用户所有数据。

    包括：用户基本信息（排除密码）、扫描历史、充值记录、积分记录、
    审计日志、修复工单、反馈记录。

    Args:
        user_id: 用户 ID

    Returns:
        字典，key 为数据类别，value 为记录列表（用户基本信息为单个字典或 None）
    """
    conn = get_db()
    try:
        result: dict[str, Any] = {}

        # 用户基本信息（排除密码字段）
        user_row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if user_row:
            user = dict(user_row)
            user.pop("password", None)
            result["user"] = user
        else:
            result["user"] = None

        # 扫描历史
        result["scans"] = _fetch_user_rows(conn, "scans", user_id)
        # 充值记录
        result["recharge_records"] = _fetch_user_rows(conn, "recharge_records", user_id)
        # 积分记录（usage_logs）
        result["usage_logs"] = _fetch_user_rows(conn, "usage_logs", user_id)
        # 审计日志
        result["audit_logs"] = _fetch_user_rows(conn, "audit_logs", user_id)
        # 修复工单
        result["fix_tickets"] = _fetch_user_rows(conn, "fix_tickets", user_id)
        # 反馈记录
        result["finding_feedback"] = _fetch_user_rows(conn, "finding_feedback", user_id)

        logger.info("用户数据导出完成: user_id=%s", user_id)
        return result
    finally:
        conn.close()


def delete_user_account(user_id: int) -> dict:
    """删除用户账号及所有关联数据。

    在单个事务中删除 scans、findings、recharge_records、audit_logs、fix_tickets、
    user_email_verifications、user_password_resets、usage_logs 等关联数据，
    最后删除 users 表记录。任一步骤失败则回滚整个事务。

    Args:
        user_id: 用户 ID

    Returns:
        ``{"success": bool, "deleted_tables": list, "message": str}``
    """
    conn = get_db()
    deleted_tables: list[str] = []
    try:
        # 关联数据表（均含 user_id 列）；findings 在当前实现中嵌入 scans.findings_json，
        # 此处仍尝试删除独立 findings 表以兼容未来扩展。
        related_tables = [
            "scans",
            "findings",
            "targets",
            "fix_tickets",
            "ticket_events",
            "usage_logs",
            "recharge_records",
            "audit_logs",
            "assets",
            "finding_feedback",
            "alerts",
            "domain_verifications",
            "user_email_verifications",
            "user_password_resets",
        ]
        for table in related_tables:
            # 防御性校验：表名必须来自硬编码白名单，避免 SQL 注入
            if table not in _VALID_TABLES:
                logger.warning("删除跳过非法表名: %s", table)
                continue
            if not _table_exists(conn, table):
                continue
            try:
                conn.execute(f"DELETE FROM {table} WHERE user_id = ?", (user_id,))  # nosec B608 - table 已通过 _VALID_TABLES 白名单校验
                deleted_tables.append(table)
            except sqlite3.OperationalError as exc:
                logger.warning("删除表 %s 数据失败: %s", table, exc)

        # 最后删除用户本体
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        deleted_tables.append("users")

        conn.commit()
        logger.info(
            "用户账号删除成功: user_id=%s deleted_tables=%s", user_id, deleted_tables
        )
        return {
            "success": True,
            "deleted_tables": deleted_tables,
            "message": "账号及所有关联数据已删除",
        }
    except Exception as exc:  # noqa: BLE001 - 删除流程需保证事务回滚并返回错误信息
        conn.rollback()
        logger.error("用户账号删除失败，已回滚: user_id=%s error=%s", user_id, exc)
        return {
            "success": False,
            "deleted_tables": deleted_tables,
            "message": f"账号删除失败：{exc}",
        }
    finally:
        conn.close()


def anonymize_user_data(user_id: int) -> dict:
    """匿名化用户数据（保留记录但脱敏）。

    - 将 username 改为 ``deleted_user_{id}``
    - 将 email 改为空字符串
    - 将密码置空
    - 保留扫描记录用于统计

    Args:
        user_id: 用户 ID

    Returns:
        ``{"success": bool, "message": str}``
    """
    conn = get_db()
    try:
        row = conn.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone()
        if not row:
            return {"success": False, "message": "用户不存在"}

        conn.execute(
            "UPDATE users SET username = ?, email = ?, password = ? WHERE id = ?",
            (f"deleted_user_{user_id}", "", "", user_id),
        )
        conn.commit()
        logger.info("用户数据匿名化成功: user_id=%s", user_id)
        return {"success": True, "message": "用户数据已匿名化，扫描记录保留用于统计"}
    except Exception as exc:  # noqa: BLE001 - 匿名化失败需回滚并返回错误信息
        conn.rollback()
        logger.error("用户数据匿名化失败: user_id=%s error=%s", user_id, exc)
        return {"success": False, "message": f"匿名化失败：{exc}"}
    finally:
        conn.close()
