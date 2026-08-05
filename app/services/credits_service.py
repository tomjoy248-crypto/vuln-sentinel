"""积分 / 按量计费服务。

提供用户积分查询、扣减、充值以及使用日志记录。
所有涉及积分变更的操作都在单个连接内完成事务，保证原子性。
"""

from __future__ import annotations

import logging
from datetime import datetime

from app.core.exceptions import BusinessException
from app.db.session import get_db

logger = logging.getLogger("vuln_sentinel.credits")

# 各项操作消耗的积分
SCAN_STANDARD_COST = 1
SCAN_DEEP_COST = 3
VERIFY_FIX_COST = 1
APPLY_FIX_COST = 2


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_credits(user_id: int) -> int:
    """获取用户当前积分。"""
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT credits FROM users WHERE id=?", (user_id,)
        ).fetchone()
        return row["credits"] if row else 0
    finally:
        conn.close()


def has_credits(user_id: int, amount: int) -> bool:
    """检查用户积分是否不少于指定数量。"""
    return get_credits(user_id) >= amount


def log_usage(
    user_id: int,
    amount: int,
    balance_after: int,
    action: str,
    scan_id: int | None = None,
    note: str = "",
) -> int:
    """记录一条积分使用日志，返回日志 ID。"""
    conn = get_db()
    try:
        cur = conn.execute(
            """INSERT INTO usage_logs
               (user_id, action, amount, balance_after, scan_id, note, created_at)
               VALUES (?,?,?,?,?,?,?)""",
            (user_id, action, amount, balance_after, scan_id, note, _now()),
        )
        conn.commit()
        return cur.lastrowid or 0
    finally:
        conn.close()


def deduct_credits(
    user_id: int,
    amount: int,
    action: str,
    scan_id: int | None = None,
    note: str = "",
) -> int:
    """从用户账户扣除积分，返回扣除后的余额。

    整个操作在同一连接中以事务方式完成：查询余额 -> 扣减 -> 写日志。
    余额不足时抛出 BusinessException。
    """
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT credits FROM users WHERE id=?", (user_id,)
        ).fetchone()
        current = row["credits"] if row else 0
        if current < amount:
            raise BusinessException(
                detail=f"额度不足，当前余额 {current}，需要 {amount}",
                code="PAYMENT_REQUIRED",
                status_code=402,
            )
        new_balance = current - amount
        conn.execute("UPDATE users SET credits=? WHERE id=?", (new_balance, user_id))
        conn.execute(
            """INSERT INTO usage_logs
               (user_id, action, amount, balance_after, scan_id, note, created_at)
               VALUES (?,?,?,?,?,?,?)""",
            (user_id, action, amount, new_balance, scan_id, note, _now()),
        )
        conn.commit()
        return new_balance
    finally:
        conn.close()


def add_credits(user_id: int, amount: int, note: str = "") -> int:
    """为用户充值积分，返回充值后的余额。"""
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT credits FROM users WHERE id=?", (user_id,)
        ).fetchone()
        current = row["credits"] if row else 0
        new_balance = current + amount
        conn.execute("UPDATE users SET credits=? WHERE id=?", (new_balance, user_id))
        conn.execute(
            """INSERT INTO usage_logs
               (user_id, action, amount, balance_after, scan_id, note, created_at)
               VALUES (?,?,?,?,?,?,?)""",
            (user_id, "recharge", amount, new_balance, None, note, _now()),
        )
        conn.commit()
        return new_balance
    finally:
        conn.close()


def get_usage_logs(
    user_id: int, limit: int = 50, offset: int = 0
) -> tuple[list[dict], int]:
    """获取用户的使用日志列表与总数。"""
    conn = get_db()
    try:
        total_row = conn.execute(
            "SELECT COUNT(*) FROM usage_logs WHERE user_id=?", (user_id,)
        ).fetchone()
        total = total_row[0] if total_row else 0

        rows = conn.execute(
            """SELECT id, user_id, action, amount, balance_after, scan_id, note, created_at
               FROM usage_logs
               WHERE user_id=?
               ORDER BY id DESC
               LIMIT ? OFFSET ?""",
            (user_id, limit, offset),
        ).fetchall()

        logs = [
            {
                "id": r["id"],
                "user_id": r["user_id"],
                "action": r["action"],
                "amount": r["amount"],
                "balance_after": r["balance_after"],
                "scan_id": r["scan_id"],
                "note": r["note"] or "",
                "created_at": r["created_at"],
            }
            for r in rows
        ]
        return logs, total
    finally:
        conn.close()
