"""数据库连接与会话管理。

提供统一的数据库连接工厂，支持：
- SQLite（默认，开发环境）
- PostgreSQL（通过 database_url 配置，生产环境，基于 SQLAlchemy 连接池）

PostgreSQL 路径返回一个 ``_PgConnection`` 包装对象，它在语义上兼容
``sqlite3.Connection`` 的常用子集：

- ``conn.execute(sql, params)`` —— 支持 SQLite 风格的 ``?`` 占位符，
  内部自动转换为 SQLAlchemy ``text()`` 命名参数 ``:pN``。
- ``conn.executemany(sql, seq)`` / ``conn.executescript(script)``
- ``conn.commit()`` / ``conn.rollback()`` / ``conn.close()``
- ``conn.total_changes`` —— 通过累计写操作 rowcount 模拟。
- ``conn.row_factory`` —— 可读写属性（兼容 sqlite3 用法），返回的行对象
  本身即为 ``sqlite3.Row`` 兼容的 ``_RowProxy``。

返回的游标 / 行对象支持 ``fetchone()``、``fetchall()``、``lastrowid``、
``rowcount``，以及 ``dict(row)``、``row["col"]``、``row[0]``、``row.col``。
"""

from __future__ import annotations

import logging
import re
import sqlite3
from collections.abc import Generator, Iterable, Iterator, Sequence
from contextlib import contextmanager
from typing import Any

# SQLAlchemy 为可选依赖：仅在使用 PostgreSQL 时需要。
# 此处做容错导入，SQLite 路径完全不依赖 SQLAlchemy。
try:  # pragma: no cover - 导入分支取决于环境
    import sqlalchemy as _sa
    from sqlalchemy import create_engine, text

    def _parse_sa_version(v: str) -> tuple[int, ...]:
        parts: list[int] = []
        for chunk in v.split("."):
            digits = ""
            for ch in chunk:
                if ch.isdigit():
                    digits += ch
                else:
                    break
            if digits:
                parts.append(int(digits))
            else:
                break
        return tuple(parts)

    _SA_VERSION: tuple[int, ...] = _parse_sa_version(_sa.__version__)
except ImportError:  # pragma: no cover
    _sa = None  # type: ignore[assignment]
    create_engine = None  # type: ignore[assignment]
    text = None  # type: ignore[assignment]
    _SA_VERSION = ()

logger = logging.getLogger("vuln_sentinel.db")

# 数据库路径（由 main.py 在启动时设置）
_db_path: str = ""
_database_url: str = ""

# PostgreSQL 引擎单例（懒创建，进程级共享连接池）
_pg_engine: Any = None


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
        logger.info(
            "Database URL configured (PostgreSQL mode): %s", _mask_url(database_url)
        )
    else:
        logger.info("Database path configured (SQLite mode): %s", db_path)


def _apply_sqlite_pragmas(conn: sqlite3.Connection) -> None:
    """启用 SQLite 生产级优化：WAL 模式、外键、busy timeout 等。"""
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA cache_size=-64000")
    conn.execute("PRAGMA journal_size_limit=67108864")


# ---------------------------------------------------------------------------
# PostgreSQL 兼容层
# ---------------------------------------------------------------------------


def _get_pg_engine() -> Any:
    """懒创建并缓存 PostgreSQL SQLAlchemy 引擎。

    使用连接池配置：
      - pool_size=10
      - max_overflow=20
      - pool_pre_ping=True（取出连接前做一次轻量探活，避免使用已断开的连接）
      - pool_recycle=3600（每小时回收连接，防止被数据库 / 中间件踢掉）
    """
    global _pg_engine
    if _pg_engine is not None:
        return _pg_engine

    if create_engine is None:  # pragma: no cover
        raise RuntimeError(
            "PostgreSQL 模式需要 SQLAlchemy，请安装: pip install sqlalchemy psycopg2-binary"
        )

    kwargs: dict[str, Any] = {
        "pool_size": 10,
        "max_overflow": 20,
        "pool_pre_ping": True,
        "pool_recycle": 3600,
    }
    # SQLAlchemy 1.4 需要显式开启 future 模式以获得与 2.0 一致的
    # commit-as-you-go 语义；2.0 已默认该行为，传 future=True 会被忽略。
    if _SA_VERSION < (2, 0):
        kwargs["future"] = True

    try:
        _pg_engine = create_engine(_database_url, **kwargs)
    except ModuleNotFoundError as e:
        # SQLAlchemy 2.x 在创建引擎时即导入 DBAPI；缺少驱动时给出友好提示。
        raise RuntimeError(
            "PostgreSQL 驱动未安装，请执行: pip install psycopg2-binary"
        ) from e
    logger.info("PostgreSQL 引擎已创建: %s", _mask_url(_database_url))
    return _pg_engine


_WRITE_RE = re.compile(r"^\s*(INSERT|UPDATE|DELETE|REPLACE|MERGE)\b", re.IGNORECASE)
_INSERT_RE = re.compile(r"^\s*INSERT\b", re.IGNORECASE)
_RETURNING_RE = re.compile(r"\bRETURNING\b", re.IGNORECASE)


def _convert_qmark(sql: str) -> tuple[str, bool]:
    """将 SQLite qmark(``?``) 占位符转换为 SQLAlchemy ``text()`` 命名参数。

    仅替换位于字符串字面量、双引号标识符、行注释、块注释之外的 ``?``。
    转换后形如 ``:p0, :p1, ...``。

    Returns:
        (converted_sql, had_qmark)
    """
    out: list[str] = []
    i = 0
    n = len(sql)
    idx = 0
    had_qmark = False
    while i < n:
        ch = sql[i]

        # 单引号字符串（'' 转义）
        if ch == "'":
            out.append(ch)
            i += 1
            while i < n:
                c = sql[i]
                out.append(c)
                if c == "'":
                    if i + 1 < n and sql[i + 1] == "'":
                        out.append("'")
                        i += 2
                        continue
                    i += 1
                    break
                i += 1
            continue

        # 双引号标识符（"" 转义）
        if ch == '"':
            out.append(ch)
            i += 1
            while i < n:
                c = sql[i]
                out.append(c)
                if c == '"':
                    if i + 1 < n and sql[i + 1] == '"':
                        out.append('"')
                        i += 2
                        continue
                    i += 1
                    break
                i += 1
            continue

        # 行注释 --
        if ch == "-" and i + 1 < n and sql[i + 1] == "-":
            while i < n and sql[i] != "\n":
                out.append(sql[i])
                i += 1
            continue

        # 块注释 /* */
        if ch == "/" and i + 1 < n and sql[i + 1] == "*":
            out.append("/*")
            i += 2
            while i < n:
                if sql[i] == "*" and i + 1 < n and sql[i + 1] == "/":
                    out.append("*/")
                    i += 2
                    break
                out.append(sql[i])
                i += 1
            continue

        if ch == "?":
            out.append(f":p{idx}")
            idx += 1
            had_qmark = True
            i += 1
            continue

        out.append(ch)
        i += 1

    return "".join(out), had_qmark


def _bind_params(params: Any) -> dict[str, Any]:
    """将序列参数转换为 :pN 命名字典。"""
    if params is None:
        return {}
    if isinstance(params, dict):
        return dict(params)
    return {f"p{i}": v for i, v in enumerate(params)}


class _RowProxy:
    """``sqlite3.Row`` 兼容的行对象。

    支持：``dict(row)``、``row["col"]``、``row[0]``、``row.col``、
    ``row.keys()``、``row.values()``、``row.items()``、``len(row)``、
    ``"col" in row``、``row.get("col")``。
    """

    __slots__ = ("_data", "_keys")

    def __init__(self, mapping: Any, keys: Sequence[str] | None = None) -> None:
        self._data: dict[str, Any] = dict(mapping)
        self._keys: Sequence[str] = list(keys) if keys else list(self._data.keys())

    def __getitem__(self, key: Any) -> Any:
        if isinstance(key, int):
            return self._data[self._keys[key]]
        return self._data[key]

    def __iter__(self) -> Iterator[Any]:
        return iter(self._data.values())

    def __len__(self) -> int:
        return len(self._data)

    def __contains__(self, key: object) -> bool:
        return key in self._data

    def keys(self) -> list[str]:
        return list(self._data.keys())

    def values(self) -> list[Any]:
        return list(self._data.values())

    def items(self) -> list[tuple[str, Any]]:
        return list(self._data.items())

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def __getattr__(self, name: str) -> Any:
        # 仅在常规属性查找失败时触发；屏蔽私有名以防递归。
        if name.startswith("_"):
            raise AttributeError(name)
        data = object.__getattribute__(self, "_data")
        if name in data:
            return data[name]
        raise AttributeError(name)

    def __repr__(self) -> str:
        return f"_RowProxy({self._data!r})"


class _PgResult:
    """游标结果包装器，兼容 sqlite3.Cursor 的常用接口。"""

    __slots__ = ("_r", "_lastrowid", "_keys")

    def __init__(self, sa_result: Any, lastrowid: Any = None) -> None:
        self._r = sa_result
        self._lastrowid = lastrowid
        try:
            self._keys: list[str] = (
                list(sa_result.keys()) if sa_result.returns_rows else []
            )
        except Exception:
            self._keys = []

    @property
    def rowcount(self) -> int:
        try:
            return int(self._r.rowcount)
        except Exception:
            return -1

    @property
    def lastrowid(self) -> Any:
        return self._lastrowid

    def _wrap(self, row: Any) -> _RowProxy | None:
        if row is None:
            return None
        try:
            mapping = row._mapping
        except AttributeError:
            mapping = row
        return _RowProxy(mapping, self._keys)

    def fetchone(self) -> _RowProxy | None:
        return self._wrap(self._r.fetchone())

    def fetchall(self) -> list[_RowProxy]:
        return [self._wrap(r) for r in self._r.fetchall()]

    def fetchmany(self, size: int | None = None) -> list[_RowProxy]:
        if size is None:
            rows = self._r.fetchmany()
        else:
            rows = self._r.fetchmany(size)
        return [self._wrap(r) for r in rows]

    def close(self) -> None:
        try:
            self._r.close()
        except Exception:
            pass


class _PgCursor:
    """独立游标，兼容 sqlite3 ``conn.cursor()`` / ``c.execute()`` 用法。"""

    __slots__ = ("_parent", "_result")

    def __init__(self, parent: _PgConnection) -> None:
        self._parent = parent
        self._result: _PgResult | None = None

    def execute(self, sql: str, parameters: Any = ()) -> _PgCursor:
        self._result = self._parent._exec(sql, parameters, many=False)
        return self

    def executemany(self, sql: str, seq_of_parameters: Iterable[Any]) -> _PgCursor:
        self._result = self._parent.executemany(sql, seq_of_parameters)
        return self

    def fetchone(self) -> _RowProxy | None:
        return self._result.fetchone() if self._result else None

    def fetchall(self) -> list[_RowProxy]:
        return self._result.fetchall() if self._result else []

    def fetchmany(self, size: int | None = None) -> list[_RowProxy]:
        if not self._result:
            return []
        return self._result.fetchmany(size)

    @property
    def rowcount(self) -> int:
        return self._result.rowcount if self._result else -1

    @property
    def lastrowid(self) -> Any:
        return self._result.lastrowid if self._result else None

    def close(self) -> None:
        if self._result:
            self._result.close()
            self._result = None


class _PgConnection:
    """PostgreSQL 连接包装器，对外提供 sqlite3.Connection 兼容接口。

    内部持有 SQLAlchemy ``Connection``（commit-as-you-go 模式），
    每次 ``get_db()`` 从连接池借出一条连接，``close()`` 归还。
    """

    __slots__ = ("_sa", "_row_factory", "_total_changes", "_closed")

    def __init__(self, sa_conn: Any) -> None:
        self._sa = sa_conn
        self._row_factory: Any = None
        self._total_changes = 0
        self._closed = False

    # ---- row_factory：可读写，兼容 sqlite3 用法 ----
    @property
    def row_factory(self) -> Any:
        return self._row_factory

    @row_factory.setter
    def row_factory(self, value: Any) -> None:
        self._row_factory = value

    @property
    def total_changes(self) -> int:
        """模拟 sqlite3.Connection.total_changes：本连接累计影响的行数。"""
        return self._total_changes

    # ---- 核心执行逻辑 ----
    def _exec(self, sql: str, params: Any, many: bool = False) -> _PgResult:
        converted, had_qmark = _convert_qmark(sql)
        bind = _bind_params(params) if had_qmark else (
            params if isinstance(params, dict) else {}
        )

        is_insert = (not many) and _INSERT_RE.match(sql) is not None
        has_returning = _RETURNING_RE.search(sql) is not None

        # 单行 INSERT：自动追加 RETURNING id 以获取自增主键
        # （PostgreSQL 的 DBAPI lastrowid 通常不可靠 / 为 None）。
        if is_insert and not has_returning:
            exec_sql = converted.rstrip().rstrip(";").rstrip() + " RETURNING id"
            result = self._sa.execute(text(exec_sql), bind)
            try:
                lastrowid = result.scalar()
            except Exception:
                lastrowid = result.lastrowid
            self._total_changes += max(0, int(result.rowcount or 0))
            return _PgResult(result, lastrowid=lastrowid)

        if many:
            result = self._sa.execute(text(converted), bind)
            self._total_changes += max(0, int(result.rowcount or 0))
            return _PgResult(result)

        result = self._sa.execute(text(converted), bind)
        if _WRITE_RE.match(sql):
            self._total_changes += max(0, int(result.rowcount or 0))
        return _PgResult(result, lastrowid=result.lastrowid)

    def execute(self, sql: str, parameters: Any = ()) -> _PgResult:
        return self._exec(sql, parameters, many=False)

    def executemany(self, sql: str, seq_of_parameters: Iterable[Any]) -> _PgResult:
        converted, had_qmark = _convert_qmark(sql)
        rows: list[dict[str, Any]] = []
        for p in seq_of_parameters:
            if isinstance(p, dict):
                rows.append(dict(p))
            else:
                rows.append({f"p{i}": v for i, v in enumerate(p)})
        result = self._sa.execute(text(converted), rows)
        self._total_changes += max(0, int(result.rowcount or 0))
        return _PgResult(result)

    def executescript(self, script: str) -> _PgConnection:
        """执行多语句脚本（兼容 sqlite3.Connection.executescript）。

        psycopg2 原生支持在单次 execute 中执行以 ``;`` 分隔的多条语句。
        执行前先提交当前挂起的事务，执行后再次提交。
        """
        self._sa.commit()
        raw = self._sa.connection  # 底层 DBAPI 连接
        cur = raw.cursor()
        try:
            cur.execute(script)
        finally:
            try:
                cur.close()
            except Exception:
                pass
        self._sa.commit()
        return self

    def cursor(self) -> _PgCursor:
        return _PgCursor(self)

    def commit(self) -> None:
        self._sa.commit()

    def rollback(self) -> None:
        self._sa.rollback()

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            self._sa.close()
        except Exception:
            pass

    def __enter__(self) -> _PgConnection:
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()


def get_db() -> Any:
    """获取数据库连接。

    - 当 ``database_url`` 以 ``postgresql`` 开头时，使用 SQLAlchemy 引擎
      从连接池借出一条连接，并包装为 ``_PgConnection``（兼容 sqlite3 接口）。
    - 否则创建新的 SQLite 连接，并自动启用 WAL 等生产优化。

    Returns:
        ``sqlite3.Connection``（SQLite 模式）或 ``_PgConnection``（PostgreSQL 模式）。
        两者均设置了行工厂，行对象支持 ``dict(row)`` / ``row["col"]`` / ``row[0]``。
    """
    if _database_url and _database_url.startswith("postgresql"):
        engine = _get_pg_engine()
        sa_conn = engine.connect()
        return _PgConnection(sa_conn)

    conn = sqlite3.connect(_db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    _apply_sqlite_pragmas(conn)
    return conn


@contextmanager
def get_db_connection() -> Generator[Any, None, None]:
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
