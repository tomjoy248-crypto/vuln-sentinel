"""数据库连接与会话管理。

提供统一的数据库连接工厂，支持：
- SQLite（默认，开发环境）
- PostgreSQL（通过 database_url 配置，生产环境）

当前阶段保持 SQLite 为默认，但接口设计已兼容 PostgreSQL。
"""

from __future__ import annotations

import logging
import os
import sqlite3
from contextlib import contextmanager
from typing import Generator, Optional

logger = logging.getLogger("vuln_sentinel.db")

# 数据库路径（由 main.py 在启动时设置）
_db_path: str = ""
_database_url: str = ""


def init_db_path(db_path: str, database_url: str = "") -> None:
    """初始化数据库路径。

    由 main.py 在启动时调用。

    Args:
        db_path: SQLite 数据库文件路径
        database_url: PostgreSQL 连接 URL（留空则使用 SQLite）
    """
    global _db_path, _database_url
    _db_path = db_path
    _database_url = database_url
    if database_url:
        logger.info("Database URL configured (PostgreSQL mode): %s", _mask_url(database_url))
    else:
        logger.info("Database path configured (SQLite mode): %s", db_path)


def get_db() -> sqlite3.Connection:
    """获取数据库连接。

    当前实现：每次调用创建新的 SQLite 连接。
    未来实现：当 database_url 配置时，使用 SQLAlchemy 连接池。

    Returns:
        sqlite3.Connection 对象（设置了 row_factory = Row）
    """
    if _database_url and _database_url.startswith("postgresql"):
        # 阶段二：将切换到 SQLAlchemy 引擎
        raise NotImplementedError("PostgreSQL 支持将在阶段二实现")

    conn = sqlite3.connect(_db_path)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """上下文管理器：自动关闭连接。

    用法:
        with get_db_connection() as conn:
            conn.execute("SELECT 1")
    """
    conn = get_db()
    try:
        yield conn
    finally:
        conn.close()


def check_db_health() -> bool:
    """检查数据库连接是否正常。

    Returns:
        True 表示连接正常，False 表示连接失败
    """
    try:
        with get_db_connection() as conn:
            conn.execute("SELECT 1").fetchone()
        return True
    except Exception as e:
        logger.warning("Database health check failed: %s", e)
        return False


def _mask_url(url: str) -> str:
    """脱敏数据库 URL 中的密码。"""
    if "@" in url:
        scheme_rest = url.split("://", 1)
        if len(scheme_rest) == 2:
            scheme, rest = scheme_rest
            if "@" in rest:
                creds, host = rest.rsplit("@", 1)
                if ":" in creds:
                    user, _ = creds.rsplit(":", 1)
                    return f"{scheme}://{user}:****@{host}"
    return url
