"""Alembic 运行环境配置。

本模块在 Alembic 执行迁移时被加载，负责：
- 从环境变量 ``DATABASE_URL`` 或 ``app.core.config.settings`` 读取数据库连接信息
  并注入 ``sqlalchemy.url``，兼容 SQLite（默认）与 PostgreSQL
- 设置 target_metadata（当前项目使用原生 SQL，未定义 ORM 模型，故为 None）

数据库 URL 解析优先级（高 -> 低）：
1. 命令行 ``-x dburl=<url>`` 临时覆盖
2. 环境变量 ``DATABASE_URL``
3. ``app.core.config.settings.database_url``（来自 .env / pydantic 配置）
4. SQLite 默认路径 ``{settings.db_dir}/{settings.db_name}``（兜底）

说明：因项目存在 ``alembic/`` 目录，ruff 会将 ``alembic`` 识别为本地模块，
故 sqlalchemy（第三方）需排在 alembic 之前以通过 isort 校验。运行时 Alembic
CLI 会先加载已安装的 alembic 包，再加载本文件，因此 ``from alembic import context``
可正确解析到第三方包。

首次使用流程：
1. 安装依赖：pip install alembic sqlalchemy
2. 对已有数据库执行 `alembic stamp head`，将其标记为最新版本（不执行任何迁移）
3. 新增迁移：`alembic revision -m "描述"`，编辑脚本后 `alembic upgrade head`
"""

from __future__ import annotations

import os
import sys
from logging.config import fileConfig

# 注意：因项目存在 alembic/ 目录，ruff 会将 `alembic` 识别为本地模块，
# 故 sqlalchemy（第三方）需排在 alembic 之前以通过 isort 校验。
from sqlalchemy import engine_from_config, pool

from alembic import context

# 将项目根目录加入 sys.path，以便导入 app 包
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Alembic 配置对象
config = context.config

# 应用日志配置（若 alembic.ini 存在）
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def _load_settings():
    """加载项目配置 settings 对象。

    项目中 ``settings`` 实例的实际位置随版本演进：
    - ``app.core.config`` 仅定义 ``AppSettings`` 类，未导出 ``settings`` 实例
    - 运行时 ``settings`` 由 ``main.py`` 中的 ``Settings()`` 实例化

    为兼容上述情况并避免导入重量级 ``main`` 模块（会触发 FastAPI 应用初始化），
    本函数按以下顺序尝试获取配置，任一成功即返回；全部失败时返回 None，
    由调用方回退到环境变量 / SQLite 默认路径：

    1. ``from app.core.config import settings``（若未来在 config 中导出实例）
    2. ``AppSettings()`` 直接实例化（轻量，仅依赖 pydantic-settings，含 DB 字段）
    3. ``from main import settings``（运行时真实实例，兜底；导入较重）

    Returns:
        settings 对象或 None
    """
    # 1. app.core.config.settings（若已导出实例）
    try:
        from app.core.config import settings  # type: ignore[import-not-found]

        return settings
    except Exception:
        pass

    # 2. 直接实例化 AppSettings（轻量，足以获取 database_url / db_dir / db_name）
    try:
        from app.core.config import AppSettings  # type: ignore[import-not-found]

        return AppSettings()
    except Exception as exc:  # noqa: BLE001 - 配置加载失败需降级而非中断迁移
        import logging

        logging.getLogger(__name__).warning(
            "无法实例化 app.core.config.AppSettings，将尝试 main.settings 或回退到"
            "环境变量 / SQLite 默认配置: %s",
            exc,
        )

    # 3. main.settings（运行时真实实例，导入较重，作为兜底）
    try:
        from main import settings  # type: ignore[import-not-found]

        return settings
    except Exception as exc:  # noqa: BLE001
        import logging

        logging.getLogger(__name__).warning(
            "无法加载 main.settings，将回退到环境变量 / SQLite 默认配置: %s",
            exc,
        )
        return None


def _resolve_database_url() -> str:
    """根据优先级解析数据库 URL，兼容 SQLite 与 PostgreSQL。

    Returns:
        SQLAlchemy 数据库连接 URL
    """
    # 1. 命令行 -x dburl=<url> 临时覆盖
    custom_url = context.get_x_argument(as_dictionary=True).get("dburl")
    if custom_url:
        return custom_url

    # 2. 环境变量 DATABASE_URL（最高优先级，推荐用于容器化 / CI 部署）
    env_url = os.environ.get("DATABASE_URL", "").strip()
    if env_url:
        return env_url

    # 3. 项目配置 settings.database_url
    settings = _load_settings()
    if settings is not None:
        if getattr(settings, "database_url", ""):
            return settings.database_url
        # 4. SQLite 默认路径：db_dir/db_name（绝对路径对应 sqlite:////... 形式）
        db_dir = str(getattr(settings, "db_dir", "/data")).rstrip("/")
        db_name = getattr(settings, "db_name", "scans.db")
        return f"sqlite:///{db_dir}/{db_name}"

    # 兜底：项目根目录下的 SQLite 文件，保证迁移命令始终可执行
    return f"sqlite:///{PROJECT_ROOT}/scans.db"


# 动态注入数据库 URL，覆盖 alembic.ini 中的占位符
database_url = _resolve_database_url()
config.set_main_option("sqlalchemy.url", database_url)

# 当前项目使用原生 SQL，未定义 SQLAlchemy ORM 模型，故 target_metadata 为 None。
# 待后续引入 ORM 模型后，将其设为 Base.metadata 即可启用 autogenerate。
target_metadata = None


def run_migrations_offline() -> None:
    """离线模式：仅生成 SQL 脚本，不连接数据库。"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # SQLite 下启用 batch 模式，以支持 ALTER TABLE 等受限操作
        render_as_batch=url.startswith("sqlite") if url else False,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """在线模式：连接数据库并执行迁移。"""
    section = config.get_section(config.config_ini_section)
    connectable = engine_from_config(
        section or {},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=database_url.startswith("sqlite"),
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
