"""数据库自动化备份与恢复脚本。

支持两种后端：
- SQLite：先执行 WAL checkpoint，再用 shutil.copy2 物理复制数据库文件
- PostgreSQL：调用 pg_dump 导出 SQL 脚本（连接信息从 DATABASE_URL 解析为 PG* 环境变量）

备份保留策略：仅保留最近 N 份备份（BACKUP_RETENTION_COUNT，默认 30），
超出的旧备份按修改时间自动删除。

用法示例：
    # SQLite 备份（类型可省略，默认按 DATABASE_URL 自动推断）
    python scripts/backup_db.py --type sqlite
    # PostgreSQL 备份
    python scripts/backup_db.py --type postgres
    # 从备份恢复
    python scripts/backup_db.py --type sqlite --restore /data/backups/vuln_sentinel_sqlite_20260804_120000.db
    # 指定备份目录
    python scripts/backup_db.py --type sqlite --backup-dir /mnt/backups

环境变量：
    BACKUP_DIR               备份目录（默认 /data/backups）
    BACKUP_RETENTION_COUNT   保留备份数（默认 30）
    DATABASE_URL             数据库连接 URL（PostgreSQL 或 sqlite:///）
    DB_DIR / DB_NAME         SQLite 数据库目录与文件名（默认 /data / scans.db）

注意：执行 SQLite 备份/恢复前，建议先停止应用进程，避免 WAL 文件不一致。
"""

from __future__ import annotations

import argparse
import os
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

DEFAULT_BACKUP_DIR = "/data/backups"
DEFAULT_RETENTION_COUNT = 30
DEFAULT_DB_DIR = "/data"
DEFAULT_DB_NAME = "scans.db"

# 备份文件命名前缀（保留策略按前缀匹配，避免误删无关文件）
SQLITE_PREFIX = "vuln_sentinel_sqlite_"
POSTGRES_PREFIX = "vuln_sentinel_postgres_"


# --------------------------------------------------------------------------- #
# 路径与连接解析
# --------------------------------------------------------------------------- #


def _resolve_backup_dir(override: str | None) -> Path:
    """解析备份目录：命令行参数 > 环境变量 > 默认值。"""
    target = override or os.environ.get("BACKUP_DIR") or DEFAULT_BACKUP_DIR
    backup_dir = Path(target)
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def _resolve_retention_count() -> int:
    """解析保留份数（环境变量 BACKUP_RETENTION_COUNT，默认 30）。"""
    raw = os.environ.get("BACKUP_RETENTION_COUNT", str(DEFAULT_RETENTION_COUNT))
    try:
        count = int(raw)
    except ValueError:
        return DEFAULT_RETENTION_COUNT
    return count if count > 0 else DEFAULT_RETENTION_COUNT


def _default_db_type() -> str:
    """根据 DATABASE_URL 推断默认数据库类型。"""
    url = os.environ.get("DATABASE_URL", "").strip()
    if url.startswith("postgresql"):
        return "postgres"
    return "sqlite"


def _resolve_sqlite_path() -> Path:
    """解析 SQLite 数据库文件路径。

    优先级：DATABASE_URL（sqlite:///）> DB_DIR/DB_NAME 环境变量 > 默认值。
    """
    url = os.environ.get("DATABASE_URL", "").strip()
    if url.startswith("sqlite://"):
        rest = url[len("sqlite://"):]
        # sqlite:////abs/path -> "//abs/path" -> 绝对路径 "/abs/path"
        if rest.startswith("//"):
            return Path(rest[1:])
        # sqlite:///path -> "/path"：SQLAlchemy 视为相对路径，去掉前导斜杠
        if rest.startswith("/"):
            return Path(rest.lstrip("/"))
        return Path(rest)
    db_dir = os.environ.get("DB_DIR", DEFAULT_DB_DIR)
    db_name = os.environ.get("DB_NAME", DEFAULT_DB_NAME)
    return Path(db_dir) / db_name


def _pg_env_from_url(url: str) -> tuple[dict[str, str], str]:
    """从 PostgreSQL 连接 URL 解析出 PG* 环境变量与库名。

    通过环境变量传递凭据，避免在进程命令行中暴露密码。

    Args:
        url: postgresql://user:pass@host:port/dbname

    Returns:
        (含 PG* 变量的环境字典, 数据库名)
    """
    parsed = urlparse(url)
    env = dict(os.environ)
    if parsed.username:
        env["PGUSER"] = parsed.username
    if parsed.password:
        env["PGPASSWORD"] = parsed.password
    if parsed.hostname:
        env["PGHOST"] = parsed.hostname
    if parsed.port:
        env["PGPORT"] = str(parsed.port)
    db_name = parsed.path.lstrip("/")
    if db_name:
        env["PGDATABASE"] = db_name
    return env, db_name


def _resolve_pg_url() -> str:
    """获取 PostgreSQL 连接 URL。"""
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url.startswith("postgresql"):
        raise RuntimeError(
            "PostgreSQL 模式需要设置 DATABASE_URL 环境变量（如 postgresql://user:pass@host:5432/db）"
        )
    return url


# --------------------------------------------------------------------------- #
# 备份
# --------------------------------------------------------------------------- #


def _timestamp() -> str:
    """生成备份文件时间戳后缀（YYYYMMDD_HHMMSS）。"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def backup_sqlite(backup_dir: Path) -> Path:
    """备份 SQLite 数据库文件。

    先执行 PRAGMA wal_checkpoint(TRUNCATE) 将 WAL 日志合并回主库，再复制文件，
    以保证备份完整性。

    Args:
        backup_dir: 备份目录

    Returns:
        备份文件路径
    """
    src = _resolve_sqlite_path()
    if not src.exists():
        raise FileNotFoundError(f"SQLite 数据库文件不存在: {src}")

    # 合并 WAL，确保主库文件包含全部已提交数据
    try:
        conn = sqlite3.connect(str(src))
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        conn.close()
    except sqlite3.Error as e:
        print(f"[警告] WAL checkpoint 失败（继续复制）: {e}", file=sys.stderr)

    dest = backup_dir / f"{SQLITE_PREFIX}{_timestamp()}.db"
    shutil.copy2(src, dest)
    # 同步复制 WAL/SHM 副文件（checkpoint 后通常为空，复制仅为兜底）
    for suffix in ("-wal", "-shm"):
        side = Path(str(src) + suffix)
        if side.exists() and side.stat().st_size > 0:
            shutil.copy2(side, Path(str(dest) + suffix))
    return dest


def backup_postgres(backup_dir: Path) -> Path:
    """使用 pg_dump 备份 PostgreSQL 数据库。

    Args:
        backup_dir: 备份目录

    Returns:
        备份文件路径
    """
    url = _resolve_pg_url()
    env, db_name = _pg_env_from_url(url)
    dest = backup_dir / f"{POSTGRES_PREFIX}{_timestamp()}.sql"
    cmd = ["pg_dump", "--file", str(dest)]
    if db_name:
        cmd.append(db_name)
    try:
        subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)
    except FileNotFoundError as e:
        raise RuntimeError("未找到 pg_dump 命令，请先安装 PostgreSQL 客户端工具") from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"pg_dump 失败: {e.stderr or e.stdout}") from e
    return dest


# --------------------------------------------------------------------------- #
# 恢复
# --------------------------------------------------------------------------- #


def restore_sqlite(backup_file: Path) -> Path:
    """从备份文件恢复 SQLite 数据库。

    将备份覆盖回数据库路径。恢复前会清理可能存在的 WAL/SHM 副文件。

    Args:
        backup_file: 备份文件路径

    Returns:
        恢复后的数据库文件路径
    """
    if not backup_file.exists():
        raise FileNotFoundError(f"备份文件不存在: {backup_file}")
    dest = _resolve_sqlite_path()
    dest.parent.mkdir(parents=True, exist_ok=True)
    # 清理旧 WAL/SHM，避免与新主库不一致
    for suffix in ("-wal", "-shm"):
        side = Path(str(dest) + suffix)
        if side.exists():
            side.unlink()
    shutil.copy2(backup_file, dest)
    return dest


def restore_postgres(backup_file: Path) -> None:
    """从 SQL 备份文件恢复 PostgreSQL 数据库。

    Args:
        backup_file: SQL 备份文件路径
    """
    if not backup_file.exists():
        raise FileNotFoundError(f"备份文件不存在: {backup_file}")
    url = _resolve_pg_url()
    env, db_name = _pg_env_from_url(url)
    cmd = ["psql", "--file", str(backup_file)]
    if db_name:
        cmd.append(db_name)
    try:
        subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)
    except FileNotFoundError as e:
        raise RuntimeError("未找到 psql 命令，请先安装 PostgreSQL 客户端工具") from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"psql 恢复失败: {e.stderr or e.stdout}") from e


# --------------------------------------------------------------------------- #
# 保留策略
# --------------------------------------------------------------------------- #


def cleanup_old_backups(backup_dir: Path, prefix: str, retention: int) -> list[Path]:
    """删除超出保留数量的旧备份。

    按修改时间倒序排列，仅保留最近 retention 份，其余删除。

    Args:
        backup_dir: 备份目录
        prefix: 备份文件名前缀
        retention: 保留份数

    Returns:
        被删除的文件路径列表
    """
    if retention <= 0:
        return []
    files = sorted(
        backup_dir.glob(f"{prefix}*"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    to_delete = files[retention:]
    for f in to_delete:
        f.unlink()
    return to_delete


# --------------------------------------------------------------------------- #
# 主入口
# --------------------------------------------------------------------------- #


def main() -> int:
    """命令行入口。"""
    parser = argparse.ArgumentParser(
        description="Vuln Sentinel数据库备份/恢复工具（支持 SQLite 与 PostgreSQL）"
    )
    parser.add_argument(
        "--type",
        choices=["sqlite", "postgres"],
        default=_default_db_type(),
        help="数据库类型（默认按 DATABASE_URL 自动推断）",
    )
    parser.add_argument(
        "--backup-dir",
        default=None,
        help="备份目录（默认读取 BACKUP_DIR 环境变量，否则 /data/backups）",
    )
    parser.add_argument(
        "--restore",
        metavar="FILE",
        default=None,
        help="从指定备份文件恢复数据库",
    )
    args = parser.parse_args()

    backup_dir = _resolve_backup_dir(args.backup_dir)
    retention = _resolve_retention_count()

    # 恢复模式
    if args.restore:
        backup_file = Path(args.restore)
        print(f"[恢复] 类型={args.type} 备份文件={backup_file}")
        try:
            if args.type == "sqlite":
                target = restore_sqlite(backup_file)
                print(f"[恢复] 成功：已恢复到 {target}")
            else:
                restore_postgres(backup_file)
                print("[恢复] 成功：PostgreSQL 数据已导入")
        except Exception as e:
            print(f"[恢复] 失败：{e}", file=sys.stderr)
            return 1
        return 0

    # 备份模式
    print(f"[备份] 类型={args.type} 目录={backup_dir} 保留={retention} 份")
    try:
        if args.type == "sqlite":
            backup_file = backup_sqlite(backup_dir)
        else:
            backup_file = backup_postgres(backup_dir)
    except Exception as e:
        print(f"[备份] 失败：{e}", file=sys.stderr)
        return 1

    size = backup_file.stat().st_size
    print(f"[备份] 成功：{backup_file}（{size} 字节）")

    # 清理过期备份
    prefix = SQLITE_PREFIX if args.type == "sqlite" else POSTGRES_PREFIX
    deleted = cleanup_old_backups(backup_dir, prefix, retention)
    print(f"[清理] 删除过期备份 {len(deleted)} 份，当前保留 {retention} 份")
    for f in deleted:
        print(f"  - 删除：{f.name}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

