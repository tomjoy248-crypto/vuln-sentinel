"""统一配置管理。

扩展原有 Settings，新增生产级配置项：
- database_url: 支持 PostgreSQL 切换
- redis_url: 分布式缓存/限流
- sentry_dsn: 错误追踪
- enable_metrics: Prometheus 指标开关
- enable_structlog: 结构化日志开关
"""

from __future__ import annotations

import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """应用配置，支持 .env 文件与环境变量覆盖。

    本类是 main.py 中 Settings 的超集，新增了生产级配置项。
    main.py 中的 Settings 继承自此类以保持向后兼容。
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- 基础信息 ---
    app_title: str = "Vuln Sentinel"
    app_version: str = "1.0.10"
    build_time: str = "2026-06-25"
    port: int = 8000
    host: str = "0.0.0.0"  # nosec B104 - 默认监听所有接口，生产环境可通过环境变量覆盖
    env: str = "development"  # development / production

    # --- JWT ---
    jwt_secret: str = Field(default="", min_length=0, repr=False)
    jwt_expire_seconds: int = 24 * 3600

    # --- 扫描 ---
    scan_timeout: float = 12.0
    max_crawl_pages: int = 8
    db_name: str = "scans.db"
    db_dir: str = "/data"

    # --- 限流 ---
    rate_limit_global_per_minute: int = 30
    rate_limit_scan_per_minute: int = 10
    rate_limit_fix_per_minute: int = 10

    # --- 缓存 ---
    ssl_cache_ttl_seconds: int = 300

    # --- 免费试用 ---
    free_trial_enabled: bool = True

    # --- LLM ---
    llm_enabled: bool = False
    llm_provider: str = "openai"
    llm_api_key: str = Field(default="", repr=False)
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"
    llm_timeout: float = 15.0

    # --- 自动巡检 ---
    patrol_interval_hours: int = 6
    patrol_score_regression_threshold: int = 10

    # --- CORS ---
    cors_origins: str = (
        os.environ.get("ALLOWED_ORIGINS")
        or os.environ.get("CORS_ORIGINS")
        or "http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000,http://localhost:5173"
    )

    # --- 生产级新增配置 ---
    database_url: str = Field(
        default="",
        description=(
            "数据库连接 URL。留空则使用 db_dir + db_name 的 SQLite 路径。"
            "示例: postgresql://user:pass@localhost:5432/vuln_sentinel"
        ),
    )
    redis_url: str = Field(
        default="",
        description="Redis 连接 URL，用于分布式限流与缓存。留空则使用内存模式。",
    )
    sentry_dsn: str = Field(
        default="",
        repr=False,
        description="Sentry DSN，用于错误追踪。留空则不启用。",
    )
    enable_metrics: bool = Field(
        default=True,
        description="是否启用 Prometheus /metrics 端点。",
    )
    enable_structlog: bool = Field(
        default=True,
        description="是否启用 structlog 结构化 JSON 日志。",
    )
    log_level: str = Field(
        default="INFO",
        description="日志级别: DEBUG / INFO / WARNING / ERROR",
    )
    tls_verify: bool = Field(
        default=True,
        description="是否验证 TLS 证书（生产环境必须为 True）。",
    )
    public_demo_enabled: bool = Field(
        default=True,
        description="是否开放公开演示扫描端点。",
    )


def is_production(settings: AppSettings) -> bool:
    """判断是否为生产环境。"""
    return settings.env == "production" or os.environ.get("PRODUCTION", "").strip() in (
        "1",
        "true",
        "TRUE",
        "True",
        "yes",
        "YES",
    )


def validate_production_config(settings: AppSettings) -> None:
    """生产环境配置强制校验。

    - JWT_SECRET 必须设置且长度 >= 32
    - CORS 不能为空或通配符
    - CREDENTIAL_ENCRYPT_KEY 必须存在
    - 数据库不能落在临时目录
    - API 文档必须关闭
    - metrics 必须受控
    """
    if not is_production(settings):
        return

    if not settings.jwt_secret or len(settings.jwt_secret) < 32:
        raise RuntimeError("生产环境必须设置 JWT_SECRET 环境变量，且长度不少于 32 字符。")

    from utils import parse_cors_origins

    origins = parse_cors_origins(settings.cors_origins)
    if not origins:
        raise RuntimeError(
            "生产环境必须显式设置 ALLOWED_ORIGINS（或 CORS_ORIGINS）环境变量，"
            "例如：ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com"
        )
    if any(o == "*" for o in origins):
        raise RuntimeError(
            "生产环境禁止将 ALLOWED_ORIGINS 配置为通配符 '*'，"
            "请显式列出允许的来源域名，避免任意站点跨域访问。"
        )

    if not os.environ.get("CREDENTIAL_ENCRYPT_KEY", "").strip():
        raise RuntimeError(
            "生产环境必须设置 CREDENTIAL_ENCRYPT_KEY 环境变量（base64 编码的 32 字节密钥）。"
        )

    if not settings.database_url:
        normalized_db_dir = (settings.db_dir or "").strip()
        if normalized_db_dir in {"/tmp", "/var/tmp", "/dev/shm"}:
            raise RuntimeError("生产环境不能使用临时目录作为 DB_DIR。")

    if os.environ.get("DISABLE_API_DOCS", "").strip().lower() not in {"1", "true", "yes"}:
        raise RuntimeError("生产环境建议设置 DISABLE_API_DOCS=1。")

    metrics_public = os.environ.get("METRICS_PUBLIC", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    if settings.enable_metrics and not metrics_public and not os.environ.get("METRICS_AUTH_TOKEN", "").strip():
        raise RuntimeError("生产环境启用 /metrics 时应配置 METRICS_AUTH_TOKEN 或关闭公开暴露。")


# 模块级默认配置实例，供尚未加载 main.py 的模块安全读取。
settings = AppSettings()

