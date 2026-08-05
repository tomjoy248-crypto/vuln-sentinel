"""用户生命周期管理服务。

负责邮箱验证与密码重置流程：

- 生成 / 校验邮箱验证 token（有效期 24 小时）
- 生成 / 校验密码重置 token（有效期 30 分钟）
- 按邮箱查找用户

token 使用 uuid4 生成并落库，密码重置使用 bcrypt 哈希（与 main.py 保持一致）。
所有数据库操作通过 ``app.db.session.get_db()`` 获取连接。
"""

from __future__ import annotations

import logging
import re
import sqlite3
import uuid
from datetime import datetime, timedelta

import bcrypt

from app.db.session import get_db

logger = logging.getLogger("vuln_sentinel.user_lifecycle")

# token 有效期
EMAIL_VERIFICATION_TTL = timedelta(hours=24)
PASSWORD_RESET_TTL = timedelta(minutes=30)

# 时间格式（与项目其他服务保持一致）
_TIME_FMT = "%Y-%m-%d %H:%M:%S"

# 合法 SQL 标识符：字母/下划线开头，后跟字母、数字或下划线
_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _is_valid_identifier(name: str) -> bool:
    """校验标识符是否仅含字母、数字和下划线（且不以数字开头）。

    用于在拼入 ``PRAGMA table_info(...)`` 等 DDL 语句前做防御性校验，避免注入风险。
    """
    return bool(_IDENTIFIER_RE.match(name))


def _now() -> str:
    """返回当前时间的字符串表示。"""
    return datetime.now().strftime(_TIME_FMT)


def _column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    """检查 SQLite 表中是否已存在指定列。"""
    # 防御性校验：表名拼入 PRAGMA 语句前必须为合法标识符
    if not _is_valid_identifier(table):
        logger.warning("PRAGMA table_info 跳过非法表名: %s", table)
        return False
    try:
        cursor = conn.execute(f"PRAGMA table_info({table})")
        return any(row[1] == column for row in cursor.fetchall())
    except Exception:  # noqa: BLE001 - PRAGMA 失败时视为列不存在
        return False


def _hash_password(pwd: str) -> str:
    """使用 bcrypt 哈希密码（与 main.py 的 hash_password 逻辑一致）。

    bcrypt 限制密码最长 72 字节，超出部分截断。
    """
    return bcrypt.hashpw(pwd[:72].encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def ensure_lifecycle_tables() -> None:
    """创建生命周期所需的表（如果不存在）。

    包括：
    - user_email_verifications (id, user_id, token, created_at, used_at)
    - user_password_resets (id, user_id, token, created_at, expires_at, used_at)

    同时为 users 表迁移添加 email_verified 列（默认 0）。
    """
    conn = get_db()
    try:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS user_email_verifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL,
                used_at TEXT
            )"""
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS user_password_resets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                used_at TEXT
            )"""
        )
        # 索引：加速按 token / user_id 查询
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_uev_token ON user_email_verifications(token)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_uev_user_id ON user_email_verifications(user_id)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_upr_token ON user_password_resets(token)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_upr_user_id ON user_password_resets(user_id)"
        )
        # 迁移：为 users 表添加 email_verified 列
        if not _column_exists(conn, "users", "email_verified"):
            conn.execute("ALTER TABLE users ADD COLUMN email_verified INTEGER DEFAULT 0")
        conn.commit()
    finally:
        conn.close()


def generate_email_verification_token(user_id: int) -> str:
    """生成邮箱验证 token（uuid4）并存入数据库。

    Args:
        user_id: 用户 ID

    Returns:
        生成的验证 token 字符串
    """
    ensure_lifecycle_tables()
    token = str(uuid.uuid4())
    conn = get_db()
    try:
        conn.execute(
            """INSERT INTO user_email_verifications (user_id, token, created_at)
               VALUES (?, ?, ?)""",
            (user_id, token, _now()),
        )
        conn.commit()
        logger.info("生成邮箱验证 token: user_id=%s", user_id)
        return token
    finally:
        conn.close()


def verify_email(token: str) -> dict:
    """验证邮箱。

    校验 token 是否存在、是否已使用、是否在 24 小时有效期内，
    通过后标记 token 已使用并将 users 表 email_verified 置为 1。

    Args:
        token: 邮箱验证 token

    Returns:
        ``{"success": bool, "message": str}``
    """
    ensure_lifecycle_tables()
    conn = get_db()
    try:
        row = conn.execute(
            """SELECT id, user_id, created_at, used_at
               FROM user_email_verifications
               WHERE token = ?""",
            (token,),
        ).fetchone()
        if not row:
            return {"success": False, "message": "验证链接无效或不存在"}
        if row["used_at"]:
            return {"success": False, "message": "该验证链接已被使用，请勿重复验证"}

        created_at = datetime.strptime(row["created_at"], _TIME_FMT)
        if datetime.now() - created_at > EMAIL_VERIFICATION_TTL:
            return {"success": False, "message": "验证链接已过期，请重新发送验证邮件"}

        # 标记 token 已使用
        conn.execute(
            "UPDATE user_email_verifications SET used_at = ? WHERE id = ?",
            (_now(), row["id"]),
        )
        # 更新用户邮箱验证状态
        cur = conn.execute(
            "UPDATE users SET email_verified = 1 WHERE id = ?",
            (row["user_id"],),
        )
        if cur.rowcount == 0:
            conn.rollback()
            return {"success": False, "message": "用户不存在，邮箱验证失败"}
        conn.commit()
        logger.info("邮箱验证成功: user_id=%s", row["user_id"])
        return {"success": True, "message": "邮箱验证成功"}
    finally:
        conn.close()


def generate_password_reset_token(user_id: int) -> str:
    """生成密码重置 token（uuid4）并存入数据库，有效期 30 分钟。

    Args:
        user_id: 用户 ID

    Returns:
        生成的密码重置 token 字符串
    """
    ensure_lifecycle_tables()
    token = str(uuid.uuid4())
    now = datetime.now()
    expires_at = (now + PASSWORD_RESET_TTL).strftime(_TIME_FMT)
    conn = get_db()
    try:
        conn.execute(
            """INSERT INTO user_password_resets (user_id, token, created_at, expires_at)
               VALUES (?, ?, ?, ?)""",
            (user_id, token, now.strftime(_TIME_FMT), expires_at),
        )
        conn.commit()
        logger.info("生成密码重置 token: user_id=%s expires_at=%s", user_id, expires_at)
        return token
    finally:
        conn.close()


def reset_password(token: str, new_password: str) -> dict:
    """验证密码重置 token 并重置密码。

    校验 token 是否存在、是否已使用、是否在 30 分钟有效期内，
    通过后使用 bcrypt 哈希新密码并更新 users 表，同时标记 token 已使用。

    Args:
        token: 密码重置 token
        new_password: 新密码明文

    Returns:
        ``{"success": bool, "message": str}``
    """
    ensure_lifecycle_tables()
    if not new_password:
        return {"success": False, "message": "新密码不能为空"}

    conn = get_db()
    try:
        row = conn.execute(
            """SELECT id, user_id, expires_at, used_at
               FROM user_password_resets
               WHERE token = ?""",
            (token,),
        ).fetchone()
        if not row:
            return {"success": False, "message": "密码重置链接无效或不存在"}
        if row["used_at"]:
            return {"success": False, "message": "该密码重置链接已被使用"}

        expires_at = datetime.strptime(row["expires_at"], _TIME_FMT)
        if datetime.now() > expires_at:
            return {"success": False, "message": "密码重置链接已过期，请重新申请"}

        hashed = _hash_password(new_password)
        cur = conn.execute(
            "UPDATE users SET password = ? WHERE id = ?",
            (hashed, row["user_id"]),
        )
        if cur.rowcount == 0:
            conn.rollback()
            return {"success": False, "message": "用户不存在，密码重置失败"}
        # 标记 token 已使用，防止重复使用
        conn.execute(
            "UPDATE user_password_resets SET used_at = ? WHERE id = ?",
            (_now(), row["id"]),
        )
        conn.commit()
        logger.info("密码重置成功: user_id=%s", row["user_id"])
        return {"success": True, "message": "密码重置成功"}
    finally:
        conn.close()


def get_user_by_email(email: str) -> dict | None:
    """按邮箱查找用户。

    Args:
        email: 用户邮箱

    Returns:
        用户记录字典（包含全部字段），未找到返回 None
    """
    if not email:
        return None
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
