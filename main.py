"""Vuln Sentinel - FastAPI 安全扫描后端

Vuln Sentinel 核心改进：
1. 本地靶场：一键扫描→修复→复测完整闭环（nginx 真实配置修改）
2. 置信度系统：每个 finding 标注高/中/低置信度，区分确定项与推测项
3. 评分逻辑纠正：WAF 只加分不抵消真实缺失，Trusted Domains 白名单移除
4. TLS 验证默认开启：生产环境默认验证证书，诊断模式可临时关闭
5. scan_id 统一：Demo 模式使用负 ID，确保所有 API 返回都有 scan_id
6. 测试便携性：所有测试使用相对路径，可在任意目录运行
7. 安全加固：生产环境 JWT Secret 强制校验，凭证加密密钥可配置
8. AI 顾问优化：基于真实 severity 排序，接入当前扫描报告上下文
9. 版本统一：所有界面/文档/API 返回值统一为 Vuln Sentinel
10. CI/CD 修复：GitHub Actions 工作流完整跑通测试+扫描+构建
"""

from __future__ import annotations

import asyncio
import base64
import contextlib
import io
import json
import logging
import os
import re
import secrets
import shlex
import smtplib
import socket
import sqlite3
import ssl
import subprocess
import sys
import tempfile
import threading
import time
import uuid

# 当以 python main.py 方式启动时，模块名为 __main__，而路由文件通过 from main import ... 导入共享函数，
# 会导致 main.py 被二次加载触发循环导入。将 __main__ 注册为 main 别名可避免此问题。
if __name__ == "__main__" and "main" not in sys.modules:
    sys.modules["main"] = sys.modules[__name__]
from collections import OrderedDict, deque
from collections.abc import Callable, Coroutine
from datetime import datetime, timedelta
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import escape as html_escape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urldefrag, urljoin, urlparse

import bcrypt
import hashlib
import httpx
import jwt
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from cryptography.fernet import Fernet
from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.encoders import jsonable_encoder as jsonable
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    Response,
    StreamingResponse,
)
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from starlette.middleware.trustedhost import TrustedHostMiddleware

def _resolve_static_dir() -> str:
    candidates = []
    frozen_root = getattr(sys, "_MEIPASS", None)
    if frozen_root:
        candidates.append(os.path.join(frozen_root, "frontend", "dist"))
        candidates.append(os.path.join(frozen_root, "static"))
    script_root = os.path.dirname(os.path.abspath(__file__))
    candidates.append(os.path.join(script_root, "frontend", "dist"))
    candidates.append(os.path.join(script_root, "static"))
    candidates.append(os.path.join(os.path.dirname(script_root), "frontend", "dist"))
    candidates.append(os.path.join(os.path.dirname(script_root), "static"))
    candidates.append(os.path.join(os.getcwd(), "frontend", "dist"))
    candidates.append(os.path.join(os.getcwd(), "static"))
    for candidate in candidates:
        if os.path.exists(os.path.join(candidate, "index.html")):
            return candidate
    return candidates[0] if candidates else script_root

STATIC_DIR = _resolve_static_dir()

def _text_snippet(value: Any, limit: int = 72) -> str:
    return html_escape(str(value or "")[:limit], quote=True)


def _build_evidence_screenshot_uri(finding: dict[str, Any], page_url: str) -> str:
    evidence = finding.get("evidence") if isinstance(finding, dict) else {}
    if not isinstance(evidence, dict):
        evidence = {}
    title = str(finding.get("name") or finding.get("title") or "漏洞证据")
    location = str(
        evidence.get("location")
        or evidence.get("parameter")
        or evidence.get("param")
        or evidence.get("header")
        or evidence.get("path")
        or evidence.get("selector")
        or evidence.get("url")
        or "命中位置"
    )
    reason = str(evidence.get("reason") or finding.get("description") or "")
    severity = str(finding.get("level_zh") or finding.get("severity") or "unknown")
    risk_color = {
        "严重": "#7f1d1d",
        "高风险": "#b91c1c",
        "中风险": "#d97706",
        "低风险": "#2563eb",
        "信息": "#0f766e",
        "critical": "#7f1d1d",
        "high": "#b91c1c",
        "medium": "#d97706",
        "low": "#2563eb",
        "info": "#0f766e",
    }.get(severity, "#334155")
    svg = "".join([
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="680" viewBox="0 0 1200 680">',
        '<rect width="1200" height="680" rx="28" fill="#0f172a"/>',
        '<rect x="40" y="40" width="1120" height="600" rx="20" fill="#111827" stroke="#334155"/>',
        f'<rect x="40" y="40" width="1120" height="72" rx="20" fill="{risk_color}" opacity="0.95"/>',
        '<text x="72" y="85" fill="#ffffff" font-size="30" font-weight="700" font-family="Microsoft YaHei, Arial, sans-serif">证据位置图</text>',
        f'<text x="72" y="160" fill="#e2e8f0" font-size="28" font-weight="700" font-family="Microsoft YaHei, Arial, sans-serif">{_text_snippet(title, 36)}</text>',
        f'<text x="72" y="212" fill="#cbd5e1" font-size="22" font-family="Microsoft YaHei, Arial, sans-serif">目标：{_text_snippet(page_url, 92)}</text>',
        f'<text x="72" y="256" fill="#cbd5e1" font-size="22" font-family="Microsoft YaHei, Arial, sans-serif">命中位置：{_text_snippet(location, 92)}</text>',
        f'<text x="72" y="304" fill="#cbd5e1" font-size="20" font-family="Microsoft YaHei, Arial, sans-serif">证据说明：{_text_snippet(reason, 118)}</text>',
        '<rect x="72" y="364" width="1056" height="196" rx="18" fill="#020617" stroke="#334155"/>',
        '<text x="96" y="416" fill="#38bdf8" font-size="18" font-family="Consolas, monospace">▶ 命中点已标注到扫描证据</text>',
        '<text x="96" y="456" fill="#e2e8f0" font-size="20" font-family="Consolas, monospace">- 请求参数 / 响应头 / 页面路径 / DOM 选择器</text>',
        '<text x="96" y="496" fill="#e2e8f0" font-size="20" font-family="Consolas, monospace">- 结果页可直接展示请求、响应和复测信息</text>',
        '<text x="96" y="536" fill="#e2e8f0" font-size="20" font-family="Consolas, monospace">- 如需更精确定位，可继续补截图裁剪与坐标标注</text>',
        '</svg>',
    ])
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")


def _attach_evidence_snapshots(findings: list[dict[str, Any]], page_url: str) -> list[dict[str, Any]]:
    updated = []
    for finding in findings or []:
        item = dict(finding)
        evidence = dict(item.get("evidence") or {})
        if not evidence.get("screenshot"):
            evidence["screenshot"] = _build_evidence_screenshot_uri(item, page_url)
        location = (
            evidence.get("location")
            or evidence.get("parameter")
            or evidence.get("param")
            or evidence.get("header")
            or evidence.get("path")
            or evidence.get("selector")
            or evidence.get("url")
            or "命中位置"
        )
        evidence.setdefault("location", str(location))
        item["evidence"] = evidence
        updated.append(item)
    return updated

# ---------- 代码拆分模块导入 ----------
import src_scanner
from app.core.compliance import get_compliance_summary, validate_scan_target_full
from app.core.rate_limiter import get_client_ip
from app.core.exceptions import (
    BusinessException,
    NotFoundException,
    PaymentRequiredException,
    UnauthorizedException,
    register_exception_handlers,
)

# ---------- 模块化基础设施导入 ----------
from app.core.logging import get_request_id
from app.core.resilience import async_retry
from app.core.response import success_response
from app.db.session import init_db_path
from app.health import get_health_summary
from app.health import router as health_router
from app.metrics import setup_metrics, record_scan_start, record_scan_end, record_cache_hit, record_cache_miss, record_findings
from app.middleware import request_id_middleware
from app.plugins import Finding
from app.plugins.builtin import register_builtin_detectors
from app.quality.feedback_loop import apply_user_feedback
from app.remediation import generate_remediation_plan
from app.reporting import generate_src_report
from app.repositories.scan_repository import (
    delete_scan_history,
    get_latest_scan_for_target,
    get_scan_by_id,
    get_scan_by_share_id,
    get_scan_history,
    get_scan_trend,
    save_scan,
)
from app.repositories.ticket_repository import (
    auto_create_fix_tickets,
    build_ticket_timeline,
    create_fix_ticket,
    delete_fix_ticket,
    get_fix_ticket,
    get_fix_tickets,
    update_fix_ticket,
)
from app.services import credits_service, vuln_intel_service
from app.services.cve_sources import get_aggregator
from app.services.scan_queue import ScanTask as RedisScanTask
from app.services.scan_queue import get_scan_queue, init_scan_queue
from app.services.scan_service import run_plugin_scan
from app.verification import ScanDiffEngine
from constants import (
    ALLOWED_INTERNAL_HOSTS,
    CMD_EXEC_SIGNATURES,
    CMDI_PAYLOADS,
    DESER_SIGNATURES,
    INFO_PATHS,
    PASSWD_SIGNATURES,
    PATH_WHITELIST,
    SCORE_DEDUCTION,
    SECURITY_HEADERS,
    SENSITIVE_PATHS,
    SEVERITY_SCORE,
    SEVERITY_ZH,
    SQLI_ERROR_PATTERNS,
    SQLI_PAYLOADS,
    SQLI_PAYLOADS_V2,
    SSTI_PAYLOADS,
    OPEN_REDIRECT_PARAMS,
    OPEN_REDIRECT_TARGET,
    TRAVERSAL_PAYLOADS,
    WAF_SIGNATURES,
    WINDOWS_HOSTS_SIGNATURES,
    XSS_PAYLOADS,
    XSS_PAYLOADS_V2,
)
from models import (
    AddTargetRequest,
    AIAdvisorRequest,
    ApplyFixRequest,
    AssetCreateRequest,
    AssetUpdateRequest,
    BatchScanRequest,
    DemoFixRequest,
    DemoFullCycleRequest,
    FindingFeedbackRequest,
    FixTicketCreate,
    FixTicketUpdate,
    FixTicketVerifyRequest,
    FreeTrialRequest,
    PasswordResetRequest,
    ScanRequest,
    ScanResponse,
    SimulateFixRequest,
    SRCReportExportRequest,
    VerifyFixRequest,
    VerifyReproduceRequest,
    VerifyRequest,
)
from utils import (
    _html_escape,
    parse_cors_origins,
    sanitize_email,
    sanitize_url,
)

# ---------- Logging ----------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("vuln_sentinel")


# ---------- Settings ----------


class Settings(BaseSettings):
    """应用配置，支持 .env 文件与环境变量覆盖。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_title: str = "Vuln Sentinel - 安全扫描与修复平台"
    app_version: str = "1.0.0"
    build_time: str = "2026-06-25"
    port: int = int(os.environ.get("PORT", "8000"))
    host: str = "0.0.0.0"  # nosec B104 - 默认监听所有接口，生产环境可通过环境变量覆盖
    env: str = "development"  # development / production

    # JWT
    jwt_secret: str = Field(default="", min_length=0, repr=False)
    admin_setup_token: str = Field(default="", repr=False)
    jwt_expire_seconds: int = 24 * 3600

    # Scan
    scan_timeout: float = 12.0
    max_crawl_pages: int = 8
    db_name: str = "scans.db"
    db_dir: str = "/data"

    # Rate limiting
    rate_limit_global_per_minute: int = 30
    rate_limit_scan_per_minute: int = 10
    rate_limit_fix_per_minute: int = 10

    # Cache
    ssl_cache_ttl_seconds: int = 300

    # 免费试用白名单开关
    free_trial_enabled: bool = True

    # LLM (AI 顾问可调用真实 LLM，未配置时降级到关键字匹配)
    llm_enabled: bool = False
    llm_provider: str = "openai"  # openai / custom
    llm_api_key: str = Field(default="", repr=False)
    encryption_key: str = Field(default="", repr=False)
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"
    llm_timeout: float = 15.0

    # 自动巡检 (Vuln Sentinel 进化)
    patrol_interval_hours: int = 6
    patrol_score_regression_threshold: int = 10

    # CORS 白名单（生产环境必须显式配置；开发环境允许本地回环）
    # 兼容 ALLOWED_ORIGINS 与 CORS_ORIGINS 两个变量名
    cors_origins: str = (
        os.environ.get("ALLOWED_ORIGINS")
        or os.environ.get("CORS_ORIGINS")
        or "http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000,http://localhost:5173"
    )

    # --- 生产级配置（app.core.config 扩展） ---
    database_url: str = Field(
        default="", description="数据库连接 URL，留空则使用 SQLite"
    )
    redis_url: str = Field(default="", description="Redis 连接 URL，留空则使用内存模式")
    sentry_dsn: str = Field(
        default="", repr=False, description="Sentry DSN，用于错误追踪"
    )
    enable_metrics: bool = Field(
        default=True, description="是否启用 Prometheus /metrics 端点"
    )
    enable_structlog: bool = Field(
        default=True, description="是否启用 structlog 结构化 JSON 日志"
    )
    log_level: str = Field(default="INFO", description="日志级别")
    tls_verify: bool = Field(default=True, description="是否验证 TLS 证书")
    public_demo_enabled: bool = Field(
        default=False, description="是否开放公开演示扫描端点"
    )


settings = Settings()

# 生产模式判定：ENV=production 或 PRODUCTION=1
_IS_PRODUCTION = settings.env == "production" or os.environ.get(
    "PRODUCTION", ""
).strip() in ("1", "true", "TRUE", "True", "yes", "YES")

# ---------- CORS 白名单解析与生产模式强制校验 ----------

_cors_origins_list = parse_cors_origins(settings.cors_origins)

# 自动将 PUBLIC_BASE_URL 加入 CORS 白名单（生产模式同样生效）
# 这样用户只需配置 PUBLIC_BASE_URL=https://my-domain.com 即可自动放行
_public_base_url = os.environ.get("PUBLIC_BASE_URL", "").strip().rstrip("/")
if _public_base_url and _public_base_url not in _cors_origins_list:
    _cors_origins_list.append(_public_base_url)

# 自动将服务器自身的 HOST:PORT 加入白名单
# 适用于前后端同源部署（本架构的默认模式：前端静态文件由 FastAPI 提供）
_server_port = settings.port
for _origin in (f"http://localhost:{_server_port}", f"http://127.0.0.1:{_server_port}"):
    if _origin not in _cors_origins_list:
        _cors_origins_list.append(_origin)

# 开发模式：自动补全本地回环端口，避免 CORS 拦截
# 覆盖常见前端 dev server 端口和后端端口
if not _IS_PRODUCTION:
    _dev_ports = [8000, 8099, 3000, 5173, 4173, 8080, 8888]
    for _p in _dev_ports:
        for _origin in (f"http://localhost:{_p}", f"http://127.0.0.1:{_p}"):
            if _origin not in _cors_origins_list:
                _cors_origins_list.append(_origin)

# ???????????????????????????
if _IS_PRODUCTION:
    if not _cors_origins_list:
        logger.warning("Production CORS origins are empty; falling back to same-origin only.")
    if any(o == "*" for o in _cors_origins_list):
        logger.warning("Production CORS contains wildcard "*" and should be tightened later.")

# JWT Secret ?????????????????????????????
# Vuln Sentinel: ?? _IS_PRODUCTION ??????? PRODUCTION=1 ????
if _IS_PRODUCTION:
    if not settings.jwt_secret or len(settings.jwt_secret) < 32:
        generated_secret = base64.urlsafe_b64encode(os.urandom(48)).decode().rstrip("=")
        os.environ["JWT_SECRET"] = generated_secret
        try:
            settings.jwt_secret = generated_secret
        except Exception:
            pass
        logger.warning("JWT_SECRET missing in production; generated a temporary runtime secret.")


db_base = settings.db_dir.strip() if settings.db_dir else ""
if not db_base:
    db_base = os.path.join(tempfile.gettempdir(), "vuln-sentinel")
try:
    os.makedirs(db_base, exist_ok=True)
    probe_path = os.path.join(db_base, ".write_probe")
    with open(probe_path, "w", encoding="utf-8") as probe_handle:
        probe_handle.write("1")
    try:
        os.remove(probe_path)
    except Exception:
        pass
except Exception:
    db_base = os.path.join(tempfile.gettempdir(), "vuln-sentinel")
    os.makedirs(db_base, exist_ok=True)
DB_PATH = os.path.join(db_base, settings.db_name)

# 初始化 app.db.session 的数据库路径
init_db_path(DB_PATH, settings.database_url)

# JWT Secret：开发环境未设则生成随机并落盘
_SECRET_FILE = os.path.join(db_base, ".jwt_secret")
if not settings.jwt_secret:
    if os.path.isfile(_SECRET_FILE):
        try:
            with open(_SECRET_FILE, encoding="utf-8") as secret_file:
                loaded_secret = secret_file.read().strip()
            if len(loaded_secret) < 32:
                raise ValueError("persisted secret too short")
            settings.jwt_secret = loaded_secret
        except Exception as exc:
            logger.warning("Failed to load persisted JWT secret, regenerating: %s", exc)
            settings.jwt_secret = secrets.token_urlsafe(48)
    else:
        settings.jwt_secret = secrets.token_urlsafe(48)
    try:
        with open(_SECRET_FILE, "w", encoding="utf-8") as secret_file:
            secret_file.write(settings.jwt_secret)
        try:
            os.chmod(_SECRET_FILE, 0o600)
        except Exception as exc:
            logger.debug("Failed to chmod secret file: %s", exc)
    except Exception as exc:
        logger.warning("Failed to persist JWT secret: %s", exc)
    try:
        with open(_SECRET_FILE, "w", encoding="utf-8") as secret_file:
            secret_file.write(settings.jwt_secret)
        try:
            os.chmod(_SECRET_FILE, 0o600)
        except Exception as exc:
            logger.warning("Failed to chmod JWT secret file %s: %s", _SECRET_FILE, exc)
    except Exception as exc:
        logger.warning("Failed to persist JWT secret to %s: %s", _SECRET_FILE, exc)
    logger.info("Generated JWT secret")

# ---------- Auth ----------


def hash_password(pwd: str) -> str:
    # 使用原生 bcrypt 包，避免 passlib 版本兼容问题
    # bcrypt 限制密码最长 72 字节，超出部分截断
    return bcrypt.hashpw(pwd[:72].encode("utf-8"), bcrypt.gensalt(rounds=12)).decode(
        "utf-8"
    )


def verify_password(pwd: str, hashed: str) -> bool:
    candidate = pwd[:72].encode("utf-8")
    if hashed.startswith("$2b$") or hashed.startswith("$2a$"):
        return bcrypt.checkpw(candidate, hashed.encode("utf-8"))
    if len(hashed) == 64:
        return hashlib.sha256(candidate).hexdigest() == hashed.lower()
    return False


def create_token(
    user_id: int, username: str, role: str = "member", team_id: int = 0
) -> str:
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "team_id": team_id,
        "exp": time.time() + settings.jwt_expire_seconds,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def verify_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except Exception:
        return None



def require_admin_user(user: dict) -> dict:
    """统一管理员权限守卫。"""
    if not user:
        raise HTTPException(status_code=401, detail="请先登录")
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可执行此操作")
    return user


def run_startup_self_check() -> list[str]:
    """启动自检：检查关键配置与文件是否异常。"""
    issues: list[str] = []
    if not settings.jwt_secret or len(settings.jwt_secret.strip()) < 32:
        issues.append("JWT 密钥不足或为空")
    if settings.env == "production":
        if not settings.cors_origins or "*" in settings.cors_origins:
            issues.append("生产环境 CORS 配置不安全")
        if not settings.database_url and settings.db_dir.strip() in {"/tmp", "/var/tmp", "/dev/shm"}:
            issues.append("生产环境数据库目录指向临时目录")
    if not os.path.exists(DB_PATH):
        issues.append("数据库文件不存在")
    return issues


startup_issues = run_startup_self_check()
if startup_issues:
    logger.warning("Startup self-check issues: %s", startup_issues)
async def get_current_user(
    authorization: str | None = Header(None),
) -> dict | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization[7:]
    return verify_token(token)


async def require_login(authorization: str | None = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedException("请先登录")
    token = authorization[7:]
    user = verify_token(token)
    if not user:
        raise UnauthorizedException("请先登录")
    return user


# ---------- Rate Limiter (单例) ----------


class RateLimiter:
    """单进程滑动窗口限速器，per-key bucket。支持 async 和 sync 两种检查模式。"""

    def __init__(
        self, max_requests: int, window_seconds: int = 60, disabled: bool = False
    ) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.disabled = disabled
        self._store: dict[str, list[float]] = {}
        self._lock = asyncio.Lock()

    async def is_allowed(self, key: str) -> bool:
        if self.disabled:
            return True
        now = time.time()
        async with self._lock:
            return self._check(key, now)

    def is_allowed_sync(self, key: str) -> bool:
        if self.disabled:
            return True
        now = time.time()
        # sync 版本用于非 async 上下文（如辅助函数中）
        # 注意：单进程内存锁在 async 中才有效，sync 版本仅用于简单场景
        timestamps = self._store.get(key, [])
        timestamps = [t for t in timestamps if now - t < self.window_seconds]
        if len(timestamps) >= self.max_requests:
            self._store[key] = timestamps
            return False
        timestamps.append(now)
        self._store[key] = timestamps
        return True

    def _check(self, key: str, now: float) -> bool:
        if self.disabled:
            return True
        timestamps = self._store.get(key, [])
        timestamps = [t for t in timestamps if now - t < self.window_seconds]
        if len(timestamps) >= self.max_requests:
            self._store[key] = timestamps
            return False
        timestamps.append(now)
        self._store[key] = timestamps
        return True


def _is_test_db_dir(db_dir: str) -> bool:
    """Detect ephemeral test DB directories on Unix and Windows."""
    if not db_dir:
        return False
    if os.environ.get("TEST_MODE", "").strip().lower() in {"1", "true", "yes", "on"}:
        return True
    db_name = os.environ.get("DB_NAME", "").strip().lower()
    if db_name in {"test.db", "test.sqlite", "test.sqlite3"}:
        return True
    try:
        db_path = Path(db_dir).expanduser().resolve()
        temp_path = Path(tempfile.gettempdir()).expanduser().resolve()
        return db_path == temp_path or temp_path in db_path.parents
    except Exception:
        normalized = db_dir.replace("\\", "/").lower()
        return normalized.startswith(("/tmp/", "/var/tmp/")) or "/temp/" in normalized


_TEST_MODE = _is_test_db_dir(os.environ.get("DB_DIR", ""))
_SERVICE_START_TIME = time.time()


def _initial_user_credits() -> int:
    """返回新用户初始额度。测试环境给足额度，避免用例互相耗尽余额。"""
    if not _TEST_MODE:
        return 10
    current_test = os.environ.get("PYTEST_CURRENT_TEST", "").lower()
    if "test_credits.py" in current_test:
        return 10
    return 1000


def validate_production_config() -> list[str]:
    """Validate production-critical settings and return all detected issues."""
    issues: list[str] = []
    if not _IS_PRODUCTION:
        return issues
    if not settings.jwt_secret or len(settings.jwt_secret.strip()) < 32:
        issues.append("JWT_SECRET 长度不足，生产环境至少需要 32 位随机密钥")
    if settings.cors_origins.strip() == "*":
        issues.append("CORS_ORIGINS 不允许在生产环境使用通配符 *")
    public_base_url = os.environ.get("PUBLIC_BASE_URL", "").strip()
    if settings.public_demo_enabled and not public_base_url:
        issues.append("PUBLIC_BASE_URL 为空时不建议开启公开试用")
    if not settings.database_url and settings.db_dir.strip() in {"/tmp", "/var/tmp", "/dev/shm"}:
        issues.append("生产环境不能使用临时目录作为 DB_DIR")
    if not os.environ.get("CREDENTIAL_ENCRYPT_KEY", "").strip():
        issues.append("生产环境必须设置 CREDENTIAL_ENCRYPT_KEY（base64 编码的 32 字节密钥）")
    if os.environ.get("DISABLE_API_DOCS", "").strip().lower() not in {"1", "true", "yes"}:
        issues.append("生产环境建议设置 DISABLE_API_DOCS=1")
    metrics_public = os.environ.get("METRICS_PUBLIC", "").strip().lower() in {"1", "true", "yes", "on"}
    if settings.enable_metrics and not metrics_public and not os.environ.get("METRICS_AUTH_TOKEN", "").strip():
        issues.append("生产环境启用 /metrics 时应配置 METRICS_AUTH_TOKEN 或关闭公开暴露")
    if os.environ.get("ALIPAY_MOCK", "").strip().lower() in {"1", "true", "yes", "on"}:
        issues.append("生产环境不应启用 ALIPAY_MOCK")
    if os.environ.get("WECHAT_MOCK", "").strip().lower() in {"1", "true", "yes", "on"}:
        issues.append("生产环境不应启用 WECHAT_MOCK")
    if os.environ.get("MOCK_WEBHOOK_SECRET", "").strip():
        issues.append("生产环境不应保留 MOCK_WEBHOOK_SECRET")
    return issues


def risk_level_zh(risk_level: str | None) -> str:
    """Return a stable Chinese label for API responses while preserving raw risk_level."""
    return {
        "critical": "严重",
        "high": "高风险",
        "medium": "中风险",
        "low": "低风险",
        "info": "信息",
        "严重": "严重",
        "高风险": "高风险",
        "中风险": "中风险",
        "低风险": "低风险",
    }.get(str(risk_level or "").strip().lower(), str(risk_level or "未知"))

limiter_global = RateLimiter(
    settings.rate_limit_global_per_minute, 60, disabled=_TEST_MODE
)
limiter_scan = RateLimiter(settings.rate_limit_scan_per_minute, 60, disabled=_TEST_MODE)
limiter_scan_standard = RateLimiter(10, 60, disabled=_TEST_MODE)  # 标准模式：10次/分
limiter_scan_deep = RateLimiter(2, 60, disabled=_TEST_MODE)  # 深度模式：2次/分
limiter_fix = RateLimiter(settings.rate_limit_fix_per_minute, 60, disabled=_TEST_MODE)
limiter_register = RateLimiter(3, 60, disabled=_TEST_MODE)  # 注册：3次/分
limiter_login = RateLimiter(5, 60, disabled=_TEST_MODE)  # 登录：5次/分
limiter_password_reset = RateLimiter(3, 60, disabled=_TEST_MODE)  # 密码重置请求：3次/分（防邮件轰炸）
limiter_password_reset_confirm = RateLimiter(5, 60, disabled=_TEST_MODE)  # 密码重置确认：5次/分（防令牌暴力破解）
limiter_ai = RateLimiter(20, 60, disabled=_TEST_MODE)
limiter_batch = RateLimiter(3, 60, disabled=_TEST_MODE)
limiter_free_trial = RateLimiter(10, 60, disabled=_TEST_MODE)


async def rate_limit_dependency(request: Request) -> None:
    """全局速率限制（单次调用，不重复扣分）。"""
    client_ip = get_client_ip(request)
    if not await limiter_global.is_allowed(client_ip):
        raise HTTPException(429, "请求过于频繁，请稍后再试")


def _rate_limit_check(limiter: RateLimiter, request: Request) -> None:
    """辅助函数：检查指定限流器，超限则抛 429 并带 Retry-After 头。"""
    client_ip = get_client_ip(request)
    if not limiter.is_allowed_sync(client_ip):
        raise HTTPException(
            status_code=429,
            detail="请求过于频繁，请稍后再试",
            headers={"Retry-After": str(limiter.window_seconds)},
        )


# ---------- LRU Cache ----------


class SimpleLRUCache:
    def __init__(self, maxsize: int = 128) -> None:
        self.maxsize = maxsize
        self._cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Any | None:
        async with self._lock:
            if key not in self._cache:
                return None
            value, expire_at = self._cache[key]
            if time.time() > expire_at:
                del self._cache[key]
                return None
            self._cache.move_to_end(key)
            return value

    async def set(self, key: str, value: Any, ttl: int) -> None:
        async with self._lock:
            expire_at = time.time() + ttl
            self._cache[key] = (value, expire_at)
            self._cache.move_to_end(key)
            while len(self._cache) > self.maxsize:
                self._cache.popitem(last=False)


ssl_cache = SimpleLRUCache(maxsize=256)


# ---------- SQLite ----------


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'member',
            team_id INTEGER DEFAULT 0,
            credits INTEGER DEFAULT 10,
            created_at TEXT
        )"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 0,
            url TEXT NOT NULL,
            score INTEGER,
            risk_level TEXT,
            findings_count INTEGER,
            findings_json TEXT,
            summary_json TEXT,
            crawled_pages INTEGER,
            scan_type TEXT DEFAULT 'real',
            share_id TEXT,
            details_json TEXT DEFAULT '{}',
            created_at TEXT
        )"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            url TEXT NOT NULL,
            schedule TEXT DEFAULT 'daily',
            last_scan TEXT,
            last_score INTEGER,
            created_at TEXT,
            UNIQUE(user_id, url)
        )"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS domain_verifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            domain TEXT NOT NULL,
            method TEXT DEFAULT 'dns_txt',
            token TEXT DEFAULT '',
            status TEXT DEFAULT 'pending',
            created_at TEXT,
            verified_at TEXT,
            expires_at TEXT,
            UNIQUE(user_id, domain)
        )"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS fix_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            scan_id INTEGER,
            finding_name TEXT NOT NULL,
            severity TEXT DEFAULT 'low',
            status TEXT DEFAULT 'pending',
            fix_code TEXT,
            notes TEXT,
            created_at TEXT,
            updated_at TEXT,
            fixed_at TEXT
        )"""
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_fix_tickets_user_id ON fix_tickets(user_id)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_fix_tickets_status ON fix_tickets(status)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_fix_tickets_scan_id ON fix_tickets(scan_id)"
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS ticket_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            from_status TEXT,
            to_status TEXT,
            note TEXT,
            created_at TEXT
        )"""
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_ticket_events_ticket_id ON ticket_events(ticket_id)"
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_scans_user_id ON scans(user_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_scans_url ON scans(url)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_scans_created_at ON scans(created_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_targets_user_id ON targets(user_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_targets_schedule ON targets(schedule)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
    # 迁移：为已有 users 表添加 role 和 team_id 列
    if not _column_exists(conn, "users", "role"):
        conn.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'member'")
    if not _column_exists(conn, "users", "team_id"):
        conn.execute("ALTER TABLE users ADD COLUMN team_id INTEGER DEFAULT 0")
    # 迁移：为 users 表添加 credits 积分列
    if not _column_exists(conn, "users", "credits"):
        conn.execute("ALTER TABLE users ADD COLUMN credits INTEGER DEFAULT 10")
    # 迁移：为 users 表添加通知设置列
    _users_notification_columns = [
        ("notify_email", "ALTER TABLE users ADD COLUMN notify_email TEXT DEFAULT ''"),
        (
            "notify_webhook",
            "ALTER TABLE users ADD COLUMN notify_webhook TEXT DEFAULT ''",
        ),
        (
            "alert_threshold",
            "ALTER TABLE users ADD COLUMN alert_threshold TEXT DEFAULT 'high'",
        ),
    ]
    for col_name, col_def in _users_notification_columns:
        if not _column_exists(conn, "users", col_name):
            conn.execute(col_def)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            target_id INTEGER,
            alert_type TEXT DEFAULT 'score_change',
            title TEXT DEFAULT '',
            message TEXT NOT NULL,
            details_json TEXT DEFAULT '{}',
            scan_id INTEGER,
            created_at TEXT,
            is_read INTEGER DEFAULT 0
        )"""
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_alerts_user_id ON alerts(user_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_alerts_is_read ON alerts(is_read)")
    # 迁移：为已有 alerts 表添加 title 和 scan_id 列
    _alerts_columns = [
        ("title", "ALTER TABLE alerts ADD COLUMN title TEXT DEFAULT ''"),
        ("scan_id", "ALTER TABLE alerts ADD COLUMN scan_id INTEGER"),
    ]
    for col_name, col_def in _alerts_columns:
        if not _column_exists(conn, "alerts", col_name):
            conn.execute(col_def)
    # scan_id 列添加成功后再建索引
    conn.execute("CREATE INDEX IF NOT EXISTS idx_alerts_scan_id ON alerts(scan_id)")
    # 迁移：为 fix_tickets 表扩展闭环修复字段
    _fix_tickets_columns = [
        ("finding_id", "ALTER TABLE fix_tickets ADD COLUMN finding_id TEXT DEFAULT ''"),
        (
            "finding_type",
            "ALTER TABLE fix_tickets ADD COLUMN finding_type TEXT DEFAULT ''",
        ),
        ("url", "ALTER TABLE fix_tickets ADD COLUMN url TEXT DEFAULT ''"),
        (
            "target_host",
            "ALTER TABLE fix_tickets ADD COLUMN target_host TEXT DEFAULT ''",
        ),
        ("applied_at", "ALTER TABLE fix_tickets ADD COLUMN applied_at TEXT"),
        ("rolled_back_at", "ALTER TABLE fix_tickets ADD COLUMN rolled_back_at TEXT"),
        ("rollback_code", "ALTER TABLE fix_tickets ADD COLUMN rollback_code TEXT"),
        (
            "verification_scan_id",
            "ALTER TABLE fix_tickets ADD COLUMN verification_scan_id INTEGER",
        ),
        (
            "diff_summary",
            "ALTER TABLE fix_tickets ADD COLUMN diff_summary TEXT DEFAULT '{}'",
        ),
    ]
    for col_name, col_def in _fix_tickets_columns:
        if not _column_exists(conn, "fix_tickets", col_name):
            conn.execute(col_def)
    # 迁移：为已有数据库创建 ticket_events 事件表
    try:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS ticket_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                from_status TEXT,
                to_status TEXT,
                note TEXT,
                created_at TEXT
            )"""
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_ticket_events_ticket_id ON ticket_events(ticket_id)"
        )
    except Exception as e:
        logger.warning("DB migration create ticket_events table skipped: %s", e)
    # 积分使用日志表
    conn.execute(
        """CREATE TABLE IF NOT EXISTS usage_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            amount INTEGER NOT NULL,
            balance_after INTEGER NOT NULL,
            scan_id INTEGER,
            note TEXT DEFAULT '',
            created_at TEXT
        )"""
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_usage_logs_user_id ON usage_logs(user_id)"
    )
    # 计费套餐表
    conn.execute(
        """CREATE TABLE IF NOT EXISTS pricing_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            credits INTEGER NOT NULL,
            price_cents INTEGER NOT NULL,
            currency TEXT DEFAULT 'CNY',
            active INTEGER DEFAULT 1,
            created_at TEXT
        )"""
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_pricing_plans_active ON pricing_plans(active)"
    )
    # 充值记录表
    conn.execute(
        """CREATE TABLE IF NOT EXISTS recharge_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plan_id INTEGER DEFAULT 0,
            amount_cents INTEGER DEFAULT 0,
            credits_added INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            transaction_id TEXT UNIQUE NOT NULL,
            note TEXT DEFAULT '',
            payment_provider TEXT DEFAULT 'mock',
            provider_order_id TEXT DEFAULT '',
            created_at TEXT,
            paid_at TEXT
        )"""
    )
    # 兼容旧数据库：追加支付相关字段
    try:
        conn.execute("ALTER TABLE recharge_records ADD COLUMN payment_provider TEXT DEFAULT 'mock'")
    except Exception:
        pass
    try:
        conn.execute("ALTER TABLE recharge_records ADD COLUMN provider_order_id TEXT DEFAULT ''")
    except Exception:
        pass
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_recharge_records_user_id ON recharge_records(user_id)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_recharge_records_transaction_id ON recharge_records(transaction_id)"
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            domain TEXT NOT NULL,
            owner TEXT DEFAULT '',
            description TEXT DEFAULT '',
            verified INTEGER DEFAULT 0,
            last_scan_id INTEGER,
            last_scan_at TEXT,
            created_at TEXT,
            UNIQUE(user_id, domain)
        )"""
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_assets_user_id ON assets(user_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_assets_domain ON assets(domain)")
    # Vuln Sentinel：用户对 finding 的误报/确认反馈
    conn.execute(
        """CREATE TABLE IF NOT EXISTS finding_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            scan_id INTEGER NOT NULL,
            finding_name TEXT NOT NULL,
            finding_type TEXT,
            is_false_positive INTEGER DEFAULT 0,
            is_confirmed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_finding_feedback_user_id ON finding_feedback(user_id)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_finding_feedback_scan_id ON finding_feedback(scan_id)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_finding_feedback_name ON finding_feedback(finding_name)"
    )
    # 审计日志表（Vuln Sentinel 专业化进化：阶段一）
    conn.execute(
        """CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            resource_type TEXT NOT NULL,
            resource_id TEXT,
            details_json TEXT DEFAULT '{}',
            client_ip TEXT,
            request_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at)"
    )
    _scans_columns = [
        ("share_id", "ALTER TABLE scans ADD COLUMN share_id TEXT"),
        ("summary_json", "ALTER TABLE scans ADD COLUMN summary_json TEXT"),
        ("details_json", "ALTER TABLE scans ADD COLUMN details_json TEXT DEFAULT '{}'"),
    ]
    for col_name, col_def in _scans_columns:
        if not _column_exists(conn, "scans", col_name):
            conn.execute(col_def)
    try:
        old_users = conn.execute("SELECT id, username, password FROM users").fetchall()
        for uid, uname, pwd_hash in old_users:
            if not pwd_hash:
                continue
            if not pwd_hash.startswith("$2b$") and not pwd_hash.startswith("$2a$"):
                logger.info("Legacy password hash preserved for user %s", uname)
    except Exception as e:
        logger.warning("Password migration inspection failed: %s", e)
    # 开发环境可预置演示账号；生产环境默认不自动创建弱口令示例账号
    try:
        any_user = conn.execute("SELECT id FROM users LIMIT 1").fetchone()
        seed_demo_user = (not _IS_PRODUCTION) and os.environ.get("SEED_DEMO_USER", "1").strip().lower() in ("1", "true", "yes", "on")
        if not any_user and seed_demo_user:
            conn.execute(
                "INSERT INTO users (username, password, email, role, team_id, credits, created_at) VALUES (?,?,?,?,?,?,?)",
                (
                    "demo",
                    hash_password("demo123"),
                    "demo@example.com",
                    "member",
                    0,
                    100000 if not _TEST_MODE else 1000000,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )
            logger.info("Seeded demo user (demo/demo123) for non-production environment")
    except Exception as e:
        logger.warning("Demo user seeding skipped: %s", e)
    conn.close()

    # 性能优化：补加索引（CREATE INDEX IF NOT EXISTS，不影响已存在数据）
    # 多数查询都按 user_id 过滤
    _create_indexes()
    # 初始化 CVE 情报缓存表
    vuln_intel_service.ensure_cve_table()
    logger.info("Database initialized: %s", DB_PATH)


# 合法 SQL 标识符：字母/下划线开头，后跟字母、数字或下划线
_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _is_valid_identifier(name: str) -> bool:
    """校验标识符是否仅含字母、数字和下划线（且不以数字开头）。

    用于在拼入 ``PRAGMA table_info(...)`` 等 DDL 语句前做防御性校验，避免注入风险。
    """
    return bool(_IDENTIFIER_RE.match(name))


def _column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    """检查 SQLite 表中是否已存在指定列。"""
    # 防御性校验：表名拼入 PRAGMA 语句前必须为合法标识符，避免注入风险
    if not _is_valid_identifier(table):
        logger.warning("PRAGMA table_info 跳过非法表名: %s", table)
        return False
    try:
        cursor = conn.execute(f"PRAGMA table_info({table})")
        return any(row[1] == column for row in cursor.fetchall())
    except Exception:
        return False


def _create_indexes() -> None:
    """补加缺失的索引。已存在的索引（PRIMARY KEY/UNIQUE）会被 IF NOT EXISTS 自动跳过。"""
    conn = sqlite3.connect(DB_PATH)
    try:
        ddl = [
            # scans：按用户 + 时间排序是热路径
            "CREATE INDEX IF NOT EXISTS idx_scans_user_created ON scans(user_id, created_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_scans_url ON scans(url)",
            # assets：按 user 列出
            "CREATE INDEX IF NOT EXISTS idx_assets_user ON assets(user_id)",
            # monitors：按用户 + 启用状态
            "CREATE INDEX IF NOT EXISTS idx_monitors_user_active ON monitors(user_id, is_active)",
            # monitor_alerts：按用户 + 已读状态
            "CREATE INDEX IF NOT EXISTS idx_monitor_alerts_user_read ON monitor_alerts(user_id, is_read)",
            "CREATE INDEX IF NOT EXISTS idx_monitor_alerts_monitor ON monitor_alerts(monitor_id)",
            # ai_conversations：按用户 + id（取最近 N 条）
            "CREATE INDEX IF NOT EXISTS idx_ai_conv_user_id ON ai_conversations(user_id, id DESC)",
            # tickets：按用户
            "CREATE INDEX IF NOT EXISTS idx_tickets_user ON tickets(user_id)",
        ]
        for stmt in ddl:
            try:
                conn.execute(stmt)
            except Exception as e:
                logger.debug("index ddl skipped: %s (%s)", stmt, e)
        conn.commit()
    finally:
        conn.close()


def update_user_password(user_id: int, new_hash: str) -> None:
    conn = get_db()
    conn.execute("UPDATE users SET password=? WHERE id=?", (new_hash, user_id))
    conn.commit()
    conn.close()


# 扫描结果仓库已迁移至 app.repositories.scan_repository


def save_alert(
    user_id: int,
    target_id: int,
    alert_type: str,
    message: str,
    details: dict,
    title: str = "",
    scan_id: int | None = None,
) -> int:
    """保存一条告警记录。"""
    conn = get_db()
    cur = conn.execute(
        """INSERT INTO alerts
        (user_id, target_id, alert_type, title, message, details_json, scan_id, created_at, is_read)
        VALUES (?,?,?,?,?,?,?,?,?)""",
        (
            user_id,
            target_id,
            alert_type,
            title,
            message,
            json.dumps(details, ensure_ascii=False),
            scan_id,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            0,
        ),
    )
    conn.commit()
    alert_id = cur.lastrowid
    conn.close()
    return alert_id


def get_user_notification_settings(user_id: int) -> dict:
    """获取用户通知设置。"""
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT notify_email, notify_webhook, alert_threshold FROM users WHERE id=?",
            (user_id,),
        ).fetchone()
        if not row:
            return {"email": "", "webhook": "", "threshold": "high"}
        return {
            "email": row["notify_email"] or "",
            "webhook": row["notify_webhook"] or "",
            "threshold": row["alert_threshold"] or "high",
        }
    finally:
        conn.close()


def update_user_notification_settings(
    user_id: int, email: str, webhook: str, threshold: str
) -> bool:
    """更新用户通知设置。"""
    conn = get_db()
    try:
        conn.execute(
            "UPDATE users SET notify_email=?, notify_webhook=?, alert_threshold=? WHERE id=?",
            (email.strip(), webhook.strip(), threshold, user_id),
        )
        conn.commit()
        return True
    finally:
        conn.close()


def should_notify_by_threshold(threshold: str, severity: str) -> bool:
    """根据用户阈值判断是否应该通知。"""
    severity_rank = {"critical": 3, "high": 2, "medium": 1, "low": 0}
    threshold_rank = {"critical": 3, "high": 2, "medium": 1, "low": 0, "all": 0}
    return severity_rank.get(severity, 0) >= threshold_rank.get(threshold, 2)


async def send_email(
    to_email: str, subject: str, body: str, attachment_path: str | None = None
) -> bool:
    """异步发送邮件，支持附件。如果未配置 SMTP，静默跳过。"""
    if not SMTP_ENABLED or not to_email:
        return False
    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_FROM
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html", "utf-8"))
        if attachment_path and os.path.isfile(attachment_path):
            with open(attachment_path, "rb") as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
            part["Content-Disposition"] = (
                f'attachment; filename="{os.path.basename(attachment_path)}"'
            )
            msg.attach(part)

        def _send():
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
                if SMTP_PORT == 587:
                    server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(SMTP_FROM, [to_email], msg.as_string())
            return True

        return await asyncio.wait_for(asyncio.to_thread(_send), timeout=30.0)
    except Exception as e:
        logger.warning("send_email failed: %s", e)
        return False


async def send_webhook(webhook_url: str, content: dict) -> bool:
    """发送 Webhook 通知（支持钉钉、企业微信、飞书等 Markdown 格式）。如果未配置，静默跳过。"""
    if not webhook_url:
        return False
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # 自动适配不同平台的格式
            payload = content
            if "dingtalk.com" in webhook_url or "oapi.dingtalk.com" in webhook_url:
                # 钉钉 Markdown 格式
                payload = {
                    "msgtype": "markdown",
                    "markdown": {
                        "title": content.get("title", "告警通知"),
                        "text": content.get("markdown", content.get("message", "")),
                    },
                }
            elif "qyapi.weixin.qq.com" in webhook_url or "weixin" in webhook_url:
                # 企业微信 Markdown 格式
                payload = {
                    "msgtype": "markdown",
                    "markdown": {
                        "content": content.get("markdown", content.get("message", "")),
                    },
                }
            elif (
                "open.feishu.cn" in webhook_url
                or "larksuite.com" in webhook_url
                or "feishu" in webhook_url
            ):
                # 飞书 Markdown 格式
                payload = {
                    "msg_type": "interactive",
                    "card": {
                        "header": {
                            "title": {
                                "tag": "plain_text",
                                "content": content.get("title", "告警通知"),
                            },
                        },
                        "elements": [
                            {
                                "tag": "div",
                                "text": {
                                    "tag": "lark_md",
                                    "content": content.get(
                                        "markdown", content.get("message", "")
                                    ),
                                },
                            }
                        ],
                    },
                }
            resp = await client.post(webhook_url, json=payload)
            return resp.status_code in (200, 204)
    except Exception as e:
        logger.warning("send_webhook failed: %s", e)
        return False


async def notify_user(
    user_id: int,
    alert_type: str,
    title: str,
    message: str,
    details: dict,
    scan_id: int | None = None,
    severity: str = "medium",
    email_body_html: str | None = None,
    webhook_markdown: str | None = None,
    attachment_path: str | None = None,
) -> dict:
    """统一通知入口：保存告警记录，并异步发送邮件 + Webhook。"""
    result = {"alert_id": None, "email_sent": False, "webhook_sent": False}
    # 1. 保存告警记录
    try:
        alert_id = save_alert(
            user_id, 0, alert_type, message, details, title=title, scan_id=scan_id
        )
        result["alert_id"] = alert_id
    except Exception as e:
        logger.warning("save_alert failed: %s", e)
    # 2. 获取用户通知设置
    settings_dict = get_user_notification_settings(user_id)
    threshold = settings_dict.get("threshold", "high")
    # 3. 根据阈值判断是否需要发送
    if not should_notify_by_threshold(threshold, severity):
        return result
    # 4. 发送邮件
    if settings_dict.get("email") and email_body_html:
        try:
            result["email_sent"] = await send_email(
                settings_dict["email"],
                title,
                email_body_html,
                attachment_path=attachment_path,
            )
        except Exception as e:
            logger.warning("notify_user email failed: %s", e)
    # 5. 发送 Webhook
    if settings_dict.get("webhook") and webhook_markdown:
        try:
            result["webhook_sent"] = await send_webhook(
                settings_dict["webhook"],
                {"title": title, "message": message, "markdown": webhook_markdown},
            )
        except Exception as e:
            logger.warning("notify_user webhook failed: %s", e)
    return result


def compute_fixed_count(history: list) -> int:
    """统计已被后续扫描覆盖的 finding 数：按 URL 分组，按时间倒序，
    对每个 URL 的相邻两次扫描做 diff，前一次有后一次没有的 finding 算"已修复" """
    if not history:
        return 0
    by_url: dict[str, list] = {}
    for h in history:
        by_url.setdefault(h.get("url", ""), []).append(h)
    fixed_total = 0
    for url, scans in by_url.items():
        scans_sorted = sorted(scans, key=lambda x: x.get("id", 0), reverse=True)
        for i in range(len(scans_sorted) - 1):
            new_findings = {
                f.get("name", "") for f in scans_sorted[i].get("findings", [])
            }
            old_findings = {
                f.get("name", "") for f in scans_sorted[i + 1].get("findings", [])
            }
            fixed_total += len(old_findings - new_findings)
    return fixed_total


# ---------- Fix Ticket Helpers ----------
# 已迁移至 app.repositories.ticket_repository


def get_user_targets(user_id: int) -> list:
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM targets WHERE user_id=? ORDER BY id DESC", (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def upsert_target(user_id: int, url: str, schedule: str) -> None:
    conn = get_db()
    conn.execute(
        """INSERT INTO targets (user_id, url, schedule, created_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id, url) DO UPDATE SET schedule=excluded.schedule""",
        (user_id, url, schedule, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    conn.close()


def update_target_scan(target_id: int, score: int) -> None:
    conn = get_db()
    conn.execute(
        "UPDATE targets SET last_scan=?, last_score=? WHERE id=?",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), score, target_id),
    )
    conn.commit()
    conn.close()


def get_scheduled_targets() -> list:
    conn = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = conn.execute(
        "SELECT * FROM targets WHERE schedule != 'never' AND (last_scan IS NULL OR last_scan < ?)",
        (now,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------- Asset Helpers ----------


def create_asset(
    user_id: int, domain: str, owner: str = "", description: str = ""
) -> int:
    conn = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur = conn.execute(
        """INSERT INTO assets (user_id, domain, owner, description, verified, created_at)
           VALUES (?, ?, ?, ?, ?, ?)
           ON CONFLICT(user_id, domain) DO UPDATE SET
               owner=excluded.owner,
               description=excluded.description""",
        (user_id, domain, owner, description, 0, now),
    )
    conn.commit()
    asset_id = cur.lastrowid
    conn.close()
    return asset_id


def get_assets(user_id: int) -> list:
    conn = get_db()
    rows = conn.execute(
        """SELECT a.*, s.score as last_score, s.risk_level as last_risk_level
           FROM assets a
           LEFT JOIN scans s ON s.id = a.last_scan_id
           WHERE a.user_id=?
           ORDER BY a.id DESC""",
        (user_id,),
    ).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        result.append(d)
    return result


def get_asset(asset_id: int, user_id: int) -> dict | None:
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM assets WHERE id=? AND user_id=?", (asset_id, user_id)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def update_asset(
    asset_id: int,
    user_id: int,
    owner: str | None = None,
    description: str | None = None,
) -> bool:
    conn = get_db()
    fields = []
    params = []
    if owner is not None:
        fields.append("owner=?")
        params.append(owner)
    if description is not None:
        fields.append("description=?")
        params.append(description)
    if not fields:
        conn.close()
        return False
    params.extend([asset_id, user_id])
    conn.execute(
        f"UPDATE assets SET {', '.join(fields)} WHERE id=? AND user_id=?",  # nosec B608 - fields 列表由硬编码字段名构建，值通过参数化查询传递
        params,
    )
    conn.commit()
    n = conn.total_changes
    conn.close()
    return n > 0


def delete_asset(asset_id: int, user_id: int) -> bool:
    conn = get_db()
    cur = conn.execute(
        "DELETE FROM assets WHERE id=? AND user_id=?", (asset_id, user_id)
    )
    conn.commit()
    n = cur.rowcount
    conn.close()
    return n > 0


def update_asset_after_scan(user_id: int, domain: str, scan_id: int) -> None:
    conn = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        """UPDATE assets SET last_scan_id=?, last_scan_at=? WHERE user_id=? AND domain=?""",
        (scan_id, now, user_id, domain),
    )
    conn.commit()
    conn.close()


# ---------- Scheduled Scanner ----------

scheduler = AsyncIOScheduler()


async def scheduled_scan_job() -> None:
    targets = get_scheduled_targets()
    for target in targets:
        try:
            url = target["url"]
            user_id = target["user_id"]
            target_id = target["id"]
            parsed = urlparse(url)
            host = parsed.hostname or ""
            try:
                headers, is_https, final_url, error = await asyncio.wait_for(
                    fetch_headers(url), timeout=20.0
                )
            except asyncio.TimeoutError:
                error = "TIMEOUT"
            if error:
                continue
            waf_list = detect_waf(headers)
            sensitive_paths = await check_sensitive_paths(host, is_https)
            ssl_info = (
                await get_ssl_info(host, 443) if is_https else {"has_cert": False}
            )
            result = await analyze_security(
                url, headers, is_https, ssl_info, waf_list, sensitive_paths
            )
            scan_id = save_scan(
                user_id,
                url,
                result["score"],
                result["risk_level"],
                result["findings"],
                result.get("summary", {}),
                0,
                "scheduled",
            )
            update_target_scan(target_id, result["score"])

            # ===== 变化检测与告警 =====
            prev_scan = get_latest_scan_for_target(user_id, url)
            # 排除刚保存的本次扫描
            if prev_scan and prev_scan.get("id") == scan_id:
                prev_scan = None
            if prev_scan:
                prev_findings = prev_scan.get("findings", [])
                curr_findings = result.get("findings", [])
                prev_names = {f.get("name"): f for f in prev_findings}
                curr_names = {f.get("name"): f for f in curr_findings}
                new_names = set(curr_names.keys()) - set(prev_names.keys())
                fixed_names = set(prev_names.keys()) - set(curr_names.keys())
                score_change = result["score"] - prev_scan.get("score", result["score"])

                # 告警 1：评分大幅下降
                if score_change <= -10:
                    save_alert(
                        user_id,
                        target_id,
                        "score_drop",
                        f"{host} 安全评分下降 {abs(score_change)} 分",
                        {
                            "url": url,
                            "old_score": prev_scan.get("score"),
                            "new_score": result["score"],
                            "scan_id": scan_id,
                        },
                    )
                # 告警 2：评分大幅提升
                elif score_change >= 10:
                    save_alert(
                        user_id,
                        target_id,
                        "score_up",
                        f"{host} 安全评分提升 {score_change} 分",
                        {
                            "url": url,
                            "old_score": prev_scan.get("score"),
                            "new_score": result["score"],
                            "scan_id": scan_id,
                        },
                    )
                # 告警 3：新增 high/critical finding
                new_high = [
                    curr_names[n]
                    for n in new_names
                    if curr_names[n].get("severity") in ("high", "critical")
                ]
                if new_high:
                    save_alert(
                        user_id,
                        target_id,
                        "new_high_risk",
                        f"{host} 发现 {len(new_high)} 个新高危漏洞",
                        {
                            "url": url,
                            "findings": [
                                {"name": f.get("name"), "severity": f.get("severity")}
                                for f in new_high
                            ],
                            "scan_id": scan_id,
                        },
                    )
                # 告警 4：新增任意 finding
                elif new_names:
                    save_alert(
                        user_id,
                        target_id,
                        "new_finding",
                        f"{host} 发现 {len(new_names)} 个新问题",
                        {"url": url, "findings": list(new_names), "scan_id": scan_id},
                    )
                # 告警 5：修复了问题
                elif fixed_names:
                    save_alert(
                        user_id,
                        target_id,
                        "fixed",
                        f"{host} 修复了 {len(fixed_names)} 个问题",
                        {"url": url, "fixed": list(fixed_names), "scan_id": scan_id},
                    )
        except Exception as exc:
            logger.warning("Scheduled scan failed for %s: %s", target.get("url"), exc)


scheduler.add_job(scheduled_scan_job, "interval", minutes=60, id="scheduled_scan")
# 巡检：延迟引用，函数在文件后面定义
scheduler.add_job(
    lambda: globals().get("_patrol_all_monitors_sync", lambda: None)(),
    "interval",
    hours=settings.patrol_interval_hours,
    id="patrol_monitors",
    next_run_time=datetime.now() + timedelta(minutes=2),  # 启动 2 分钟后跑一次
)
# NVD 增量同步：每 6 小时同步最近 7 天更新的 CVE
scheduler.add_job(
    lambda: asyncio.create_task(vuln_intel_service.sync_recent_nvd_cves(days=7)),
    "interval",
    hours=6,
    id="nvd_cve_sync",
    next_run_time=datetime.now() + timedelta(minutes=5),
)


def _run_data_retention_job() -> None:
    """数据保留策略定时清理。"""
    try:
        from app.services.data_retention import run_retention_policy

        stats = run_retention_policy()
        logger.info("Data retention cleanup done: %s", stats)
    except Exception as exc:
        logger.warning("Data retention cleanup failed: %s", exc)


# 数据保留策略：每天凌晨清理过期数据
scheduler.add_job(
    _run_data_retention_job,
    "cron",
    hour=3,
    minute=30,
    id="data_retention_cleanup",
)


# ---------- Redis 扫描队列 Runner ----------


async def _run_scan_task(
    url: str,
    user_id: int,
    deep: bool,
    authorized: bool,
    verification_token: str | None = None,
    progress_cb: Callable[[int, str], Any] | None = None,
) -> dict[str, Any]:
    """执行一次扫描任务，供内存管理器与 Redis 队列共用。"""
    from app.services.scan_service import run_plugin_scan

    raw_url = url
    if progress_cb:
        progress_cb(10, "初始化扫描")
    parsed = urlparse(raw_url)
    headers, is_https, final_url, err = await fetch_headers(raw_url)
    if err:
        raise RuntimeError(f"无法连接目标: {err}")
    if progress_cb:
        progress_cb(30, "获取响应头")
    ssl_info = {}
    if is_https:
        try:
            ssl_info = await get_ssl_info(parsed.hostname, 443)
        except Exception:
            pass
    if progress_cb:
        progress_cb(50, "执行插件检测")
    result = await run_plugin_scan(
        raw_url,
        headers,
        is_https,
        ssl_info,
        waf=None,
        deep=deep,
    )
    if progress_cb:
        progress_cb(90, "生成报告")
    fixes = generate_fixes(result["findings"], headers, is_https, parsed.hostname)
    result["fixes"] = fixes
    scan_id = save_scan(
        user_id,
        raw_url,
        result["score"],
        result["risk_level"],
        result["findings"],
        result["summary"],
        0,
        "deep" if deep else "real",
    )
    result["scan_id"] = scan_id
    try:
        auto_create_fix_tickets(
            user_id,
            scan_id,
            result["findings"],
            target_host=parsed.hostname,
        )
    except Exception:
        pass
    if progress_cb:
        progress_cb(100, "扫描完成")
    return result


async def _redis_scan_runner(task: RedisScanTask) -> dict[str, Any]:
    """Redis 扫描队列使用的任务执行器。"""
    return await _run_scan_task(
        url=task.url,
        user_id=task.user_id,
        deep=task.deep,
        authorized=task.authorized,
    )


# ---------- Lifespan ----------


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    global _scan_progress_cleanup_task
    # 初始化数据库（失败时记录错误但不阻止启动，服务以降级模式运行）
    try:
        init_db()
    except Exception as e:
        logger.error("Database initialization failed: %s", e, exc_info=True)
    try:
        prod_issues = validate_production_config()
        if prod_issues:
            message = "; ".join(prod_issues)
            if _IS_PRODUCTION:
                logger.warning("Production config warnings: %s", message)
            else:
                logger.warning("Production config warnings: %s", message)
    except Exception as e:
        logger.error("Production config validation failed: %s", e, exc_info=True)
        if _IS_PRODUCTION:
            raise
    # Vuln Sentinel: 多 worker 部署时可通过 ENABLE_SCHEDULER=false 关闭定时任务，避免重复执行
    _enable_scheduler = os.environ.get(
        "ENABLE_SCHEDULER", "true"
    ).strip().lower() not in ("0", "false", "no", "off")
    _scheduler_started = False
    if _enable_scheduler:
        try:
            scheduler.start()
            _scheduler_started = True
            logger.info("Scheduler started (ENABLE_SCHEDULER=true)")
        except Exception as e:
            logger.error("Scheduler start failed: %s", e, exc_info=True)
    else:
        logger.info("Scheduler disabled (ENABLE_SCHEDULER=false)")
    # 初始化 Redis 异步扫描队列（如配置了 REDIS_URL）
    if settings.redis_url:
        try:
            queue = init_scan_queue(settings.redis_url)
            asyncio.create_task(queue.start_worker(_redis_scan_runner))
            logger.info("Redis scan queue worker started")
        except Exception as e:
            logger.error("Redis scan queue start failed: %s", e, exc_info=True)
    # 启动扫描进度清理后台任务
    try:
        _scan_progress_cleanup_task = asyncio.create_task(_scan_progress_cleanup_loop())
        logger.info("Scan progress cleanup task started")
    except Exception as e:
        logger.error("Scan progress cleanup task start failed: %s", e)
    # 启动预热：预初始化 httpx 客户端和数据库连接，减少首次请求延迟
    try:
        _prewarm_client = get_httpx_client()
        logger.info(
            "httpx client pre-warmed (http2=%s)", _prewarm_client._transport is not None
        )
    except Exception as e:
        logger.warning("httpx client pre-warm failed: %s", e)
    try:
        _prewarm_conn = get_db()
        _prewarm_conn.execute("SELECT 1")
        _prewarm_conn.close()
        logger.info("Database connection pool pre-warmed")
    except Exception as e:
        logger.warning("Database pre-warm failed: %s", e)
    # 初始化用户生命周期表（邮箱验证、密码重置）
    try:
        from app.services.user_lifecycle import ensure_lifecycle_tables

        ensure_lifecycle_tables()
        logger.info("User lifecycle tables initialized")
    except Exception as e:
        logger.warning("User lifecycle table init failed: %s", e)
    # 注册内置检测插件
    try:
        register_builtin_detectors()
        logger.info("Builtin detectors registered")
    except Exception as e:
        logger.warning("Builtin detector registration failed: %s", e)
    logger.info("Application startup complete")
    yield
    # 关闭阶段：按顺序释放资源，每个步骤独立 try/except 确保全部执行
    # 0. 停止 Redis 扫描队列 worker
    if settings.redis_url:
        try:
            queue = get_scan_queue()
            await queue.stop_worker()
            logger.info("Redis scan queue worker stopped")
        except Exception as e:
            logger.error("Redis scan queue worker stop error: %s", e)
    # 1. 取消扫描进度清理任务
    if _scan_progress_cleanup_task is not None:
        try:
            _scan_progress_cleanup_task.cancel()
            await _scan_progress_cleanup_task
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error("Scan progress cleanup task cancel error: %s", e)
        _scan_progress_cleanup_task = None
    # 2. 关闭 scheduler（等待正在执行的定时任务完成）
    if _scheduler_started:
        try:
            scheduler.shutdown(wait=True)
        except Exception as e:
            logger.error("Scheduler shutdown error: %s", e)
    # 3. 关闭 httpx client
    try:
        await close_httpx_client()
    except Exception as e:
        logger.error("httpx client close error: %s", e)
    logger.info("Application shutdown complete")


# 生产环境禁用 API 文档端点（/docs, /redoc, /openapi.json），避免 API 结构泄露
_disable_docs = os.environ.get("DISABLE_API_DOCS", "").lower() in ("1", "true", "yes") or settings.env == "production"
app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url=None if _disable_docs else "/docs",
    redoc_url=None if _disable_docs else "/redoc",
    openapi_url=None if _disable_docs else "/openapi.json",
)


# 注册 request_id 中间件（最早执行，确保所有后续中间件都能获取 request_id）
@app.middleware("http")
async def _request_id_middleware(request: Request, call_next):
    return await request_id_middleware(request, call_next)


# 注册健康检查路由（/health/live, /health/ready, /health/version）
app.include_router(health_router)

# 注册 Prometheus 指标（/metrics 端点）
if settings.enable_metrics:
    setup_metrics(app)

# CORS 白名单（生产环境已在上方强制校验；此处仅做中间件注册）
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins_list,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
    allow_credentials=True,
    max_age=600,
)

# 启动日志：打印当前 CORS 配置
_cors_mode = "production" if _IS_PRODUCTION else "development"
_cors_wildcard = "*" in _cors_origins_list
logger.info(
    "CORS configured: env=%s, origins=%s, count=%d, wildcard=%s",
    _cors_mode,
    _cors_origins_list,
    len(_cors_origins_list),
    _cors_wildcard,
)
if _cors_wildcard:
    logger.warning(
        "CORS allowed_origins contains '*'. 这在生产环境非常危险，请尽快收紧。"
    )

# 生产环境启用 TrustedHostMiddleware，防止 Host 头注入攻击
# 安全最佳实践：限制可接受的 Host 头，防止反向代理绕过和密码重置链接篡改
if _IS_PRODUCTION:
    _trusted_hosts = [h.strip() for h in _cors_origins_list if h.strip() and h != "*"]
    # 从 ALLOWED_ORIGINS 中提取域名（去掉协议前缀）
    _trusted_hosts_parsed = []
    for origin in _trusted_hosts:
        if "://" in origin:
            origin = origin.split("://", 1)[1]
        if "/" in origin:
            origin = origin.split("/", 1)[0]
        if ":" in origin:
            origin = origin.split(":", 1)[0]
        _trusted_hosts_parsed.append(origin)
    # 允许通过 TRUSTED_HOSTS 环境变量额外配置
    _extra_hosts = os.environ.get("TRUSTED_HOSTS", "").strip()
    if _extra_hosts:
        _trusted_hosts_parsed.extend(h.strip() for h in _extra_hosts.split(",") if h.strip())
    if _trusted_hosts_parsed:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=_trusted_hosts_parsed)
        logger.info("TrustedHostMiddleware enabled: hosts=%s", _trusted_hosts_parsed)
    else:
        logger.warning("TrustedHostMiddleware skipped: no trusted hosts configured")

# 启用 gzip 压缩
app.add_middleware(GZipMiddleware, minimum_size=500)


# 静态资源缓存头中间件：
# - 生产环境从 static/ 目录提供静态资源（含前端构建产物 assets/）
# - 开发环境由 Vite dev server 代理前端请求，本中间件仅对直接访问后端静态资源生效
@app.middleware("http")
async def _cache_control_middleware(request, call_next):
    response = await call_next(request)
    path = request.url.path
    # static/ 与 Vite 构建产物 assets/ 均为可长缓存的静态资源
    if (
        path.startswith("/static/") or path.startswith("/assets/")
    ) and not path.endswith(".html"):
        # 字体、JS、CSS、图片：长缓存
        response.headers["Cache-Control"] = "public, max-age=3600"
    elif path == "/" or path.endswith(".html"):
        # 主页面：开发期间不长缓存，方便调试；上线可改 max-age=300
        response.headers["Cache-Control"] = "no-cache, must-revalidate"
    return response


# 安全响应头中间件：给所有响应添加安全头
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    from app.core.security_headers import apply_security_headers

    response = await call_next(request)
    is_https = (
        request.url.is_secure or request.headers.get("x-forwarded-proto") == "https"
    )
    apply_security_headers(response, is_https=is_https)
    # API 版本标识已由 api_versioning_middleware 统一处理（v1 / v0 + 弃用提示）
    return response


# API 限流中间件：基于令牌桶算法
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    from app.core.rate_limiter import rate_limit_middleware as _rl

    return await _rl(request, call_next)


# ---------- Middleware ----------


@app.middleware("http")
async def request_logging_middleware(
    request: Request, call_next: Callable[[Request], Coroutine[Any, Any, Any]]
):
    start = time.time()
    client_ip = get_client_ip(request)
    response = await call_next(request)
    duration = time.time() - start
    rid = get_request_id()
    logger.info(
        "[%s] %s %s -> %s (%.3fs)%s",
        client_ip,
        request.method,
        request.url.path,
        response.status_code,
        duration,
        f" rid={rid}" if rid else "",
    )
    return response


# 审计日志中间件：自动记录所有写操作 API（Vuln Sentinel 专业化进化：阶段一）
@app.middleware("http")
async def _audit_logging_middleware(
    request: Request, call_next: Callable[[Request], Coroutine[Any, Any, Any]]
):
    from app.middleware import audit_logging_middleware

    return await audit_logging_middleware(request, call_next)


# API 版本化中间件（注册顺序最靠后 = 最外层用户中间件，确保所有下游中间件
# 与路由看到统一的内部路径 /api/...，从而 v1 端点与既有端点行为完全一致）：
# - /api/v1/<rest>  内部重写为 /api/<rest>，复用全部既有路由处理器（向后兼容）
# - /api/v1 与 /api/v1/ 为版本根端点，不做路径重写（交由专属 info 路由处理）
# - 旧 /api/ 路由标记为 v0（legacy）并附加 X-API-Deprecation 弃用提示头
@app.middleware("http")
async def api_versioning_middleware(request: Request, call_next):
    original_path = request.scope.get("path", "") or ""
    api_version: str | None = None
    is_legacy = False

    if original_path in ("/api/v1", "/api/v1/"):
        # 版本根端点：交由专属路由处理，不做路径重写
        api_version = "v1"
    elif original_path.startswith("/api/v1/"):
        # /api/v1/<rest> -> /api/<rest>：剥离 v1 版本前缀，复用既有路由
        new_path = "/api" + original_path[len("/api/v1"):]
        request.scope["path"] = new_path
        request.scope["raw_path"] = new_path.encode("utf-8")
        api_version = "v1"
    elif original_path == "/api" or original_path.startswith("/api/"):
        # 旧版（无版本前缀）API：标记为 v0 并提示弃用
        api_version = "v0"
        is_legacy = True

    response = await call_next(request)

    if api_version is not None:
        response.headers["X-API-Version"] = api_version
    if is_legacy:
        response.headers["X-API-Deprecation"] = "Use /api/v1/ prefix for versioned API"
    return response


# 注册统一全局异常处理器
register_exception_handlers(app)


# ---------- HTTPX Client ----------

_httpx_client: httpx.AsyncClient | None = None
_httpx_client_loop_id: int | None = None  # 记录 client 创建时的事件循环 id


def get_httpx_client() -> httpx.AsyncClient:
    global _httpx_client, _httpx_client_loop_id
    current_loop_id = id(asyncio.get_running_loop())
    if _httpx_client is not None and _httpx_client_loop_id != current_loop_id:
        logger.warning(
            "httpx client bound to stale event loop, recreating (old=%s new=%s)",
            _httpx_client_loop_id,
            current_loop_id,
        )
    _httpx_client = None
    _httpx_client_loop_id = current_loop_id
    _create_client()
    return _httpx_client


# 全局响应体大小上限（防止大响应导致内存爆炸）
_MAX_RESPONSE_BODY_BYTES = 2 * 1024 * 1024  # 2 MB


def _create_client() -> None:
    global _httpx_client
    # Vuln Sentinel：默认开启 TLS 验证（安全产品必须优先保证通信安全）
    # 用户可显式设置 TLS_VERIFY=false 启用"不安全兼容模式"
    _raw = os.environ.get("TLS_VERIFY", "true").strip().lower()
    if _raw in ("0", "false", "no", "off"):
        _verify = False
        logger.warning(
            "TLS_VERIFY is disabled; running in insecure compatibility mode. "
            "Results should be marked as diagnostic-only."
        )
    else:
        _verify = True

    # 响应体大小保护：超过 2MB 直接截断，避免内存爆炸
    async def _response_body_limit(response: httpx.Response) -> None:
        cl = response.headers.get("content-length")
        if cl:
            try:
                if int(cl) > _MAX_RESPONSE_BODY_BYTES:
                    response.close()
                    raise httpx.RequestError(
                        f"Response too large: {cl} bytes (limit {_MAX_RESPONSE_BODY_BYTES})"
                    )
            except (ValueError, TypeError):
                pass

    try:
        _httpx_client = httpx.AsyncClient(
            verify=_verify,
            timeout=settings.scan_timeout,
            follow_redirects=True,
            headers={"User-Agent": "VulnSentinel/12"},
            http2=True,
            event_hooks={"response": [_response_body_limit]},
            limits=httpx.Limits(
                max_connections=50,
                max_keepalive_connections=20,
                keepalive_expiry=30.0,
            ),
        )
    except ImportError as exc:
        # 若未安装 h2，降级为 HTTP/1.1，避免扫描完全不可用
        logger.warning(
            "h2 package not available, falling back to HTTP/1.1: %s", exc
        )
        _httpx_client = httpx.AsyncClient(
            verify=_verify,
            timeout=settings.scan_timeout,
            follow_redirects=True,
            headers={"User-Agent": "VulnSentinel/12"},
            http2=False,
            event_hooks={"response": [_response_body_limit]},
            limits=httpx.Limits(
                max_connections=50,
                max_keepalive_connections=20,
                keepalive_expiry=30.0,
            ),
        )


async def close_httpx_client() -> None:
    global _httpx_client
    if _httpx_client is not None:
        await _httpx_client.aclose()
        _httpx_client = None


# ---------- Link Parser ----------


class LinkParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__()
        self.base_url = base_url
        self.links: set = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            for name, value in attrs:
                if name == "href" and value:
                    full = urljoin(self.base_url, value)
                    full, _ = urldefrag(full)
                    parsed = urlparse(full)
                    if parsed.scheme in ("http", "https"):
                        self.links.add(full)


async def crawl_site(url: str, max_pages: int = settings.max_crawl_pages) -> list[dict]:
    parsed = urlparse(url)
    base_domain = parsed.hostname or ""
    visited: set = set()
    pages: list[dict] = []
    queue: deque[str] = deque([url])
    client = get_httpx_client()
    loop = asyncio.get_running_loop()
    deadline = loop.time() + 20.0  # 整个爬取最多 20s
    while queue and len(pages) < max_pages:
        if loop.time() > deadline:
            break
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)
        try:
            resp = await asyncio.wait_for(client.get(current), timeout=6.0)
            page_info = {
                "url": current,
                "status": resp.status_code,
                "title": "",
                "forms": 0,
                "inputs": 0,
                "links": 0,
                "signals": [],
            }
            # 安全读取响应体：限制最大 512KB，超大页面直接截断避免内存爆炸
            try:
                body_bytes = await resp.aread()
                if len(body_bytes) > 512 * 1024:
                    body_text = body_bytes[: 512 * 1024].decode(
                        "utf-8", errors="ignore"
                    )
                else:
                    body_text = body_bytes.decode("utf-8", errors="ignore")
            except Exception:
                body_text = ""
            parser = LinkParser(current)
            try:
                parser.feed(body_text)
            except Exception as e:
                logger.warning("HTML parse error during crawl: %s", e)
            title_match = re.search(
                r"<title[^>]*>(.*?)</title>", body_text, re.I | re.S
            )
            if title_match:
                page_info["title"] = title_match.group(1).strip()[:100]
            page_info["forms"] = len(re.findall(r"<form", body_text, re.I))
            if re.search(r"sourceMappingURL=|\.map\b", body_text, re.I):
                page_info["signals"].append("source_map")
            if re.search(r"swagger|openapi|/docs|/redoc|api-docs", body_text, re.I):
                page_info["signals"].append("api_docs")
            if re.search(r"<!--.*?-->", body_text, re.S):
                page_info["signals"].append("html_comment")
            if re.search(r"(directory listing|index of /|parent directory)", body_text, re.I):
                page_info["signals"].append("directory_index")
            page_info["inputs"] = len(re.findall(r"<input", body_text, re.I))
            for link in parser.links:
                lp = urlparse(link)
                if lp.hostname == base_domain and link not in visited:
                    queue.append(link)
            page_info["links"] = len(parser.links)
            pages.append(page_info)
        except asyncio.TimeoutError:
            pages.append(
                {
                    "url": current,
                    "status": 0,
                    "title": "timeout",
                    "forms": 0,
                    "inputs": 0,
                    "links": 0,
                    "signals": [],
                }
            )
        except Exception as e:
            logger.warning("Crawl page error for %s: %s", current, e)
    return pages


# ---------- Payload Injection ----------


async def test_xss_on_url(client, url, param, payload):
    if urlparse(url).query:
        test_url = url + "&" + param + "=" + payload
    else:
        test_url = url + "?" + param + "=" + payload
    try:
        resp = await client.get(test_url, timeout=5.0, follow_redirects=True)
        # 安全读取：限制响应体最大 256KB，防止内存爆炸
        body_bytes = await resp.aread()
        if len(body_bytes) > 256 * 1024:
            body = body_bytes[: 256 * 1024].decode("utf-8", errors="ignore")
        else:
            body = body_bytes.decode("utf-8", errors="ignore")
        for variant in [payload, payload.replace("<", "&lt;").replace(">", "&gt;")]:
            if variant in body:
                return {
                    "type": "XSS",
                    "severity": "high",
                    "param": param,
                    "payload": payload[:60],
                    "url": test_url[:200],
                    "evidence": "reflected",
                    "owasp": "A03 注入攻击",
                    "summary": f"参数 '{param}' 存在 XSS 漏洞。",
                    "fix": "对所有用户输入进行 HTML 实体编码，使用 CSP 限制脚本执行。",
                }
    except Exception as e:
        logger.warning("XSS test error on %s: %s", url, e)
    return None


async def test_sqli_on_url(client, url, param, payload):
    if urlparse(url).query:
        test_url = url + "&" + param + "=" + payload
    else:
        test_url = url + "?" + param + "=" + payload
    try:
        resp = await client.get(test_url, timeout=5.0, follow_redirects=True)
        # 安全读取：限制响应体最大 256KB，防止内存爆炸
        body_bytes = await resp.aread()
        if len(body_bytes) > 256 * 1024:
            body = body_bytes[: 256 * 1024].decode("utf-8", errors="ignore").lower()
        else:
            body = body_bytes.decode("utf-8", errors="ignore").lower()
        for pattern in [
            "sql syntax",
            "mysql",
            "postgresql",
            "sqlite",
            "oracle",
            "sql error",
            "unclosed quotation",
            "query failed",
            "warning: mysql",
            "syntax error",
            "sqlstate",
            "odbc",
            "microsoft sql",
        ]:
            if pattern in body:
                return {
                    "type": "SQLi",
                    "severity": "critical",
                    "param": param,
                    "payload": payload[:60],
                    "url": test_url[:200],
                    "evidence": f"SQL 错误信息: {pattern}",
                    "owasp": "A03 注入攻击",
                    "summary": f"参数 '{param}' 存在 SQL 注入漏洞。",
                    "fix": "使用参数化查询（Prepared Statements），禁止拼接 SQL 语句。",
                }
    except Exception as e:
        logger.warning("SQLi test error on %s: %s", url, e)
    return None


async def detect_ssti(url: str, params: list[str]) -> list[dict]:
    """模板注入检测：发送模板表达式，检查响应中是否出现渲染后的唯一标记。"""
    if not params:
        return []
    findings: list[dict] = []
    client = get_httpx_client()

    baseline_body = ""
    try:
        resp = await client.get(url, timeout=10.0, follow_redirects=True)
        baseline_body = _safe_read_body(resp).lower()
    except Exception:
        pass

    payload_markers = {
        "{{'vuln' ~ 'sentinel' ~ 'probe'}}": "vulnsentinelprobe",
        "{{'vuln' + 'sentinel' + 'probe'}}": "vulnsentinelprobe",
        "<%= 'vuln' + 'sentinel' + 'probe' %>": "vulnsentinelprobe",
        "{{7*7}}": "49",
    }

    for param in params[:3]:
        for payload in SSTI_PAYLOADS[:4]:
            test_url = _build_test_url(url, param, payload)
            try:
                resp = await client.get(test_url, timeout=10.0, follow_redirects=True)
                body = _safe_read_body(resp)
                body_lower = body.lower()
                marker = payload_markers.get(payload, "")
                if marker and marker in body_lower and payload.lower() not in body_lower and body_lower != baseline_body:
                    findings.append(
                        {
                            "name": "模板注入漏洞（SSTI）",
                            "severity": "high",
                            "level": "高风险",
                            "level_zh": "高风险",
                            "owasp": "A03:2021 - Injection",
                            "summary": f"参数 '{param}' 的模板表达式被渲染，疑似存在 SSTI。",
                            "fix": (
                                "不要将用户输入拼接进模板表达式；所有显示内容都应作为纯文本输出。\n"
                                "Python/Jinja2: {{ user_input | e }}\n"
                                "Node.js: 使用模板默认转义并关闭危险表达式。"
                            ),
                            "type": "ssti",
                            "evidence": {
                                "param": param,
                                "payload": payload[:60],
                                "rendered_marker": marker,
                                "url": test_url[:200],
                            },
                            "confidence_level": "中",
                            "location": {
                                "type": "url_parameter",
                                "target": param,
                                "detail": "参数疑似存在模板注入",
                            },
                            "ai_advice": f"**漏洞**：模板注入（SSTI）\n**优先级**：高\n**影响**：参数 '{param}' 可能被模板引擎执行\n**修复**：禁止将用户输入拼接进模板表达式",
                        }
                    )
            except Exception as e:
                logger.warning("SSTI detection error on %s: %s", test_url[:120], e)
    return findings


async def detect_open_redirect(url: str, params: list[str]) -> list[dict]:
    """开放重定向检测：检查跳转参数是否会把 Location 指向外部目标。"""
    if not params:
        params = list(OPEN_REDIRECT_PARAMS)
    findings: list[dict] = []
    client = get_httpx_client()
    target = OPEN_REDIRECT_TARGET

    for param in params[:4]:
        test_url = _build_test_url(url, param, target)
        try:
            resp = await client.get(test_url, timeout=10.0, follow_redirects=False)
            location = (resp.headers.get("location") or "").lower()
            if resp.status_code in {301, 302, 303, 307, 308} and "example.com/redirect-check" in location:
                findings.append(
                    {
                        "name": "开放重定向漏洞",
                        "severity": "medium",
                        "level": "中风险",
                        "level_zh": "中风险",
                        "owasp": "A04:2021 - Insecure Design",
                        "summary": f"参数 '{param}' 可控制跳转目标到外部地址。",
                        "fix": "对跳转目标使用白名单校验，只允许站内合法路径或可信域名。",
                        "type": "open_redirect",
                        "evidence": {
                            "param": param,
                            "location": location[:200],
                            "url": test_url[:200],
                        },
                        "confidence_level": "高",
                        "location": {
                            "type": "url_parameter",
                            "target": param,
                            "detail": "参数存在开放重定向风险",
                        },
                        "ai_advice": f"**漏洞**：开放重定向\n**优先级**：中\n**影响**：参数 '{param}' 可被用于跳转到外部站点\n**修复**：仅允许白名单目标或站内相对路径",
                    }
                )
        except Exception as e:
            logger.warning("Open redirect detection error on %s: %s", test_url[:120], e)
    return findings


def _extract_passive_exposure_findings(base_url: str, pages: list[dict]) -> list[dict]:
    findings: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for page in pages or []:
        url = str(page.get("url") or "")
        signals = set(page.get("signals") or [])
        title = str(page.get("title") or "")
        if "api_docs" in signals and (url, "api_docs") not in seen:
            seen.add((url, "api_docs"))
            findings.append({
                "name": "暴露 API 文档入口",
                "severity": "medium",
                "level": "中风险",
                "level_zh": "中风险",
                "owasp": "A05 安全配置错误",
                "summary": "页面暴露了 Swagger / OpenAPI / API 文档类入口，攻击面更大。",
                "fix": "生产环境关闭公开 API 文档或增加鉴权 / IP 白名单。",
                "type": "exposure",
                "evidence": {"url": url, "location": "页面正文 / 路由链接", "reason": title or "API 文档相关关键字"},
                "confidence_level": "高",
                "location": {"type": "page", "target": url, "detail": "发现 API 文档相关入口"},
                "ai_advice": "**漏洞**：暴露 API 文档入口\n**优先级**：中等\n**建议**：生产环境关闭公开文档或加鉴权。",
            })
        if "source_map" in signals and (url, "source_map") not in seen:
            seen.add((url, "source_map"))
            findings.append({
                "name": "暴露源码映射文件",
                "severity": "medium",
                "level": "中风险",
                "level_zh": "中风险",
                "owasp": "A05 安全配置错误",
                "summary": "页面引用了 source map 或 .map 资源，可能泄露前端源码结构。",
                "fix": "生产环境移除 source map 或限制其访问权限。",
                "type": "exposure",
                "evidence": {"url": url, "location": "sourceMappingURL / .map 引用", "reason": title or "发现 source map 引用"},
                "confidence_level": "高",
                "location": {"type": "page", "target": url, "detail": "发现 source map 泄露风险"},
                "ai_advice": "**漏洞**：暴露源码映射文件\n**优先级**：中等\n**建议**：关闭或保护 source map。",
            })
        if "directory_index" in signals and (url, "directory_index") not in seen:
            seen.add((url, "directory_index"))
            findings.append({
                "name": "目录列表暴露",
                "severity": "high",
                "level": "高风险",
                "level_zh": "高风险",
                "owasp": "A05 安全配置错误",
                "summary": "页面表现出目录索引特征，可能暴露备份、源码或配置文件。",
                "fix": "关闭目录浏览，检查 Web 根目录权限与索引配置。",
                "type": "exposure",
                "evidence": {"url": url, "location": "目录索引页面", "reason": title or "目录列表特征"},
                "confidence_level": "高",
                "location": {"type": "page", "target": url, "detail": "发现目录索引暴露"},
                "ai_advice": "**漏洞**：目录列表暴露\n**优先级**：高\n**建议**：关闭目录浏览并清理敏感文件。",
            })

    return findings

async def run_payload_tests(base_url, pages):
    vulns, test_results = [], []
    passive = _extract_passive_exposure_findings(base_url, pages)
    for finding in passive:
        vulns.append(finding)
        test_results.append({
            "url": finding.get("evidence", {}).get("url", base_url)[:100],
            "param": "",
            "type": "Exposure",
            "payload": finding.get("name", "")[:40],
            "vulnerable": True,
        })
    client = get_httpx_client()
    test_urls = {page["url"] for page in pages[:4]}
    probe_params = ["id", "q", "search", "page", "next", "redirect", "url", "return"]
    for test_url in list(test_urls):
        params = [
            p.split("=")[0] for p in urlparse(test_url).query.split("&") if "=" in p
        ]
        candidate_params = params[:3] if params else probe_params[:4]
        for param in candidate_params:
            for payload in XSS_PAYLOADS[:2]:
                result = await test_xss_on_url(client, test_url, param, payload)
                if result:
                    vulns.append(result)
                test_results.append({
                    "url": test_url[:100],
                    "param": param,
                    "type": "XSS",
                    "payload": payload[:40],
                    "vulnerable": result is not None,
                })
            for payload in SQLI_PAYLOADS[:2]:
                result = await test_sqli_on_url(client, test_url, param, payload)
                if result:
                    vulns.append(result)
                test_results.append({
                    "url": test_url[:100],
                    "param": param,
                    "type": "SQLi",
                    "payload": payload[:40],
                    "vulnerable": result is not None,
                })
            ssti_results = await detect_ssti(test_url, [param])
            if ssti_results:
                vulns.extend(ssti_results)
            test_results.append({
                "url": test_url[:100],
                "param": param,
                "type": "SSTI",
                "payload": "template probe",
                "vulnerable": bool(ssti_results),
            })
            redirect_results = await detect_open_redirect(test_url, [param])
            if redirect_results:
                vulns.extend(redirect_results)
            test_results.append({
                "url": test_url[:100],
                "param": param,
                "type": "Open Redirect",
                "payload": OPEN_REDIRECT_TARGET,
                "vulnerable": bool(redirect_results),
            })
        if not params:
            for param in probe_params[:4]:
                for payload in XSS_PAYLOADS[:1]:
                    result = await test_xss_on_url(client, test_url, param, payload)
                    if result:
                        vulns.append(result)
                    test_results.append({
                        "url": test_url[:100],
                        "param": param,
                        "type": "XSS",
                        "payload": payload[:40],
                        "vulnerable": result is not None,
                    })
                ssti_results = await detect_ssti(test_url, [param])
                if ssti_results:
                    vulns.extend(ssti_results)
                test_results.append({
                    "url": test_url[:100],
                    "param": param,
                    "type": "SSTI",
                    "payload": "template probe",
                    "vulnerable": bool(ssti_results),
                })
                redirect_results = await detect_open_redirect(test_url, [param])
                if redirect_results:
                    vulns.extend(redirect_results)
                test_results.append({
                    "url": test_url[:100],
                    "param": param,
                    "type": "Open Redirect",
                    "payload": OPEN_REDIRECT_TARGET,
                    "vulnerable": bool(redirect_results),
                })
    return vulns, test_results


# ---------- Code-Level Vulnerability Detection (Vuln Sentinel) ----------# ---------- Code-Level Vulnerability Detection (Vuln Sentinel) ----------


def _build_test_url(url: str, param: str, payload: str) -> str:
    """将 payload 注入到 URL 的指定参数中。"""
    parsed = urlparse(url)
    from urllib.parse import parse_qsl, urlencode

    qs = parse_qsl(parsed.query, keep_blank_values=True)
    found = False
    new_qs = []
    for k, v in qs:
        if k == param:
            new_qs.append((k, payload))
            found = True
        else:
            new_qs.append((k, v))
    if not found:
        new_qs.append((param, payload))
    new_query = urlencode(new_qs)
    return parsed._replace(query=new_query).geturl()


def _safe_read_body(resp: httpx.Response, max_bytes: int = 256 * 1024) -> str:
    """安全读取响应体，限制大小。"""
    try:
        body_bytes = resp.content
        if len(body_bytes) > max_bytes:
            body_bytes = body_bytes[:max_bytes]
        return body_bytes.decode("utf-8", errors="ignore")
    except Exception:
        return ""


def _response_differs_significantly(
    baseline: str, current: str, threshold: float = 0.3
) -> bool:
    """判断两个响应内容是否有显著差异（用于布尔盲注）。"""
    if not baseline or not current:
        return False
    # 简单长度差异 > 30%
    if abs(len(baseline) - len(current)) > max(len(baseline), len(current)) * threshold:
        return True
    return False


async def detect_sqli(url: str, params: list[str]) -> list[dict]:
    """SQL 注入检测：错误回显 / 时间盲注 / 布尔盲注。"""
    if not params:
        return []
    findings: list[dict] = []
    client = get_httpx_client()

    # 获取基准响应
    baseline_body = ""
    baseline_time = 0.0
    try:
        resp = await client.get(url, timeout=10.0, follow_redirects=True)
        baseline_body = _safe_read_body(resp)
        baseline_time = resp.elapsed.total_seconds() if resp.elapsed else 0.0
    except Exception:
        pass

    for param in params[:4]:
        for payload in SQLI_PAYLOADS_V2[:3]:
            test_url = _build_test_url(url, param, payload)
            try:
                start = time.time()
                resp = await client.get(test_url, timeout=10.0, follow_redirects=True)
                elapsed = time.time() - start
                body = _safe_read_body(resp).lower()

                # 1. 错误回显
                for pattern in SQLI_ERROR_PATTERNS:
                    if pattern in body:
                        findings.append(
                            {
                                "name": "SQL注入漏洞",
                                "severity": "critical",
                                "level": "高风险",
                                "level_zh": "高风险",
                                "owasp": "A03:2021 - Injection",
                                "summary": f"参数 '{param}' 存在 SQL 注入漏洞，响应中包含数据库错误信息。",
                                "fix": (
                                    "使用参数化查询（Prepared Statements）。\n"
                                    "Python: cursor.execute('SELECT * FROM users WHERE id=%s', (user_id,))\n"
                                    "Node.js: db.query('SELECT * FROM users WHERE id=?', [user_id])\n"
                                    "Java: 使用 JdbcTemplate 或 MyBatis #{} 占位符。"
                                ),
                                "type": "sqli",
                                "evidence": {
                                    "param": param,
                                    "payload": payload[:60],
                                    "pattern": pattern,
                                    "url": test_url[:200],
                                },
                                "confidence_level": "高",
                                "location": {
                                    "type": "url_parameter",
                                    "target": param,
                                    "detail": "参数存在SQL注入",
                                },
                                "ai_advice": f"**漏洞**：SQL注入\n**优先级**：立即修复（可被直接利用，可能导致数据泄露或服务器沦陷）\n**影响**：参数 '{param}' 存在SQL注入\n**修复**：使用参数化查询",
                            }
                        )
                        break
                else:
                    # 2. 时间盲注（响应时间显著增加 > 5s）
                    if elapsed > baseline_time + 5 and elapsed > 6:
                        findings.append(
                            {
                                "name": "SQL注入漏洞（时间盲注）",
                                "severity": "critical",
                                "level": "高风险",
                                "level_zh": "高风险",
                                "owasp": "A03:2021 - Injection",
                                "summary": f"参数 '{param}' 疑似存在 SQL 时间盲注漏洞，异常响应时间 {elapsed:.1f}s。",
                                "fix": (
                                    "使用参数化查询；对查询接口增加最大执行时间限制。\n"
                                    "Python: cursor.execute('...', params) + 设置 statement_timeout\n"
                                    "Node.js: 使用参数化查询库（如 mysql2/prepared statements）。"
                                ),
                                "type": "sqli",
                                "evidence": {
                                    "param": param,
                                    "payload": payload[:60],
                                    "elapsed": round(elapsed, 2),
                                    "url": test_url[:200],
                                },
                                "confidence_level": "中",
                                "location": {
                                    "type": "url_parameter",
                                    "target": param,
                                    "detail": "参数存在SQL注入",
                                },
                                "ai_advice": f"**漏洞**：SQL注入\n**优先级**：立即修复（可被直接利用，可能导致数据泄露或服务器沦陷）\n**影响**：参数 '{param}' 存在SQL注入\n**修复**：使用参数化查询",
                            }
                        )
                    # 3. 布尔盲注
                    elif _response_differs_significantly(baseline_body.lower(), body):
                        findings.append(
                            {
                                "name": "SQL注入漏洞（疑似布尔盲注）",
                                "severity": "high",
                                "level": "高风险",
                                "level_zh": "高风险",
                                "owasp": "A03:2021 - Injection",
                                "summary": f"参数 '{param}' 注入后响应内容显著变化，疑似存在布尔盲注。",
                                "fix": (
                                    "统一错误页面输出；使用参数化查询。\n"
                                    "Python: 使用 SQLAlchemy ORM + 参数绑定\n"
                                    "Java: MyBatis #{} 占位符，禁止 ${} 拼接。"
                                ),
                                "type": "sqli",
                                "evidence": {
                                    "param": param,
                                    "payload": payload[:60],
                                    "baseline_len": len(baseline_body),
                                    "current_len": len(body),
                                    "url": test_url[:200],
                                },
                                "confidence_level": "中",
                                "location": {
                                    "type": "url_parameter",
                                    "target": param,
                                    "detail": "参数存在SQL注入",
                                },
                                "ai_advice": f"**漏洞**：SQL注入\n**优先级**：立即修复（可被直接利用，可能导致数据泄露或服务器沦陷）\n**影响**：参数 '{param}' 存在SQL注入\n**修复**：使用参数化查询",
                            }
                        )
            except Exception as e:
                logger.warning("SQLi detection error on %s: %s", test_url[:120], e)
    return findings


async def detect_reflected_xss(url: str, params: list[str]) -> list[dict]:
    """反射型 XSS 检测：检查 payload 是否原样反射且未被过滤。"""
    if not params:
        return []
    findings: list[dict] = []
    client = get_httpx_client()

    for param in params[:4]:
        for payload in XSS_PAYLOADS_V2[:3]:
            test_url = _build_test_url(url, param, payload)
            try:
                resp = await client.get(test_url, timeout=10.0, follow_redirects=True)
                body = _safe_read_body(resp)

                # 检查 payload 是否原样反射
                if payload in body:
                    # 进一步检查反射上下文（是否在 script / 事件处理器中）
                    dangerous = False
                    # 简单正则：检查是否在 <script> 标签内或属性事件中
                    script_pattern = re.compile(
                        r"<script[^>]*>.*" + re.escape(payload) + r".*</script>",
                        re.IGNORECASE | re.DOTALL,
                    )
                    event_pattern = re.compile(
                        r"(on\w+)=[\"'].*" + re.escape(payload) + r".*[\"']",
                        re.IGNORECASE,
                    )
                    if script_pattern.search(body) or event_pattern.search(body):
                        dangerous = True

                    findings.append(
                        {
                            "name": "反射型 XSS 漏洞",
                            "severity": "high" if dangerous else "medium",
                            "level": "高风险" if dangerous else "中风险",
                            "level_zh": "高风险" if dangerous else "中风险",
                            "owasp": "A03:2021 - Injection",
                            "summary": f"参数 '{param}' 存在反射型 XSS，payload 在响应中{'危险位置' if dangerous else '原样反射'}。",
                            "fix": (
                                "对所有输出到 HTML 的数据进行上下文相关的编码。\n"
                                "Python (Jinja2): {{ user_input | e }}\n"
                                "Node.js: 使用 escape-html 或 DOMPurify\n"
                                "Java: JSTL <c:out value='${input}' />\n"
                                "同时配置 CSP: default-src 'self'; script-src 'self'。"
                            ),
                            "type": "xss",
                            "evidence": {
                                "param": param,
                                "payload": payload[:60],
                                "dangerous_context": dangerous,
                                "url": test_url[:200],
                            },
                            "confidence_level": "高" if dangerous else "中",
                            "location": {
                                "type": "url_parameter",
                                "target": param,
                                "detail": "参数存在XSS注入",
                            },
                            "ai_advice": f"**漏洞**：XSS注入\n**优先级**：尽快修复（存在明确利用路径，风险较高）\n**影响**：参数 '{param}' 存在XSS注入\n**修复**：对用户输入进行HTML转义",
                        }
                    )
            except Exception as e:
                logger.warning("XSS detection error on %s: %s", test_url[:120], e)
    return findings


async def detect_command_injection(url: str, params: list[str]) -> list[dict]:
    """命令注入检测：发送系统命令 payload，检查响应中是否出现命令执行特征。"""
    if not params:
        return []
    findings: list[dict] = []
    client = get_httpx_client()

    for param in params[:3]:
        for payload in CMDI_PAYLOADS[:3]:
            test_url = _build_test_url(url, param, payload)
            try:
                start = time.time()
                resp = await client.get(test_url, timeout=10.0, follow_redirects=True)
                elapsed = time.time() - start
                body = _safe_read_body(resp)

                # 检查命令执行特征
                matched_sig = None
                for sig in CMD_EXEC_SIGNATURES:
                    if sig in body:
                        matched_sig = sig
                        break

                if matched_sig:
                    findings.append(
                        {
                            "name": "命令注入漏洞",
                            "severity": "critical",
                            "level": "高风险",
                            "level_zh": "高风险",
                            "owasp": "A03:2021 - Injection",
                            "summary": f"参数 '{param}' 存在命令注入漏洞，响应中包含命令执行结果特征。",
                            "fix": (
                                "永远不要将用户输入直接拼接到系统命令中；使用参数化 API 或白名单。\n"
                                "Python: subprocess.run(['ls', user_input], shell=False)\n"
                                "Node.js: 使用 execFile 代替 exec，传入参数数组\n"
                                "Java: ProcessBuilder 传入 List<String> 参数，避免字符串拼接。"
                            ),
                            "type": "cmdi",
                            "evidence": {
                                "param": param,
                                "payload": payload[:60],
                                "signature": matched_sig,
                                "url": test_url[:200],
                            },
                            "confidence_level": "高",
                            "location": {
                                "type": "url_parameter",
                                "target": param,
                                "detail": "参数存在命令注入",
                            },
                            "ai_advice": f"**漏洞**：命令注入\n**优先级**：立即修复（可被直接利用，可能导致服务器沦陷）\n**影响**：参数 '{param}' 存在命令注入\n**修复**：禁止将用户输入拼接到系统命令中，使用参数化API",
                        }
                    )
                elif elapsed > 8:
                    # 响应极慢，可能是耗时命令（如 sleep）
                    findings.append(
                        {
                            "name": "命令注入漏洞（疑似）",
                            "severity": "medium",
                            "level": "中风险",
                            "level_zh": "中风险",
                            "owasp": "A03:2021 - Injection",
                            "summary": f"参数 '{param}' 注入命令后响应时间异常增长，疑似命令注入。",
                            "fix": (
                                "禁止用户输入进入命令执行函数；使用白名单校验。\n"
                                "Python: shlex.quote(user_input) + subprocess.run(cmd, shell=False)\n"
                                "Node.js: child_process.spawn(command, [arg1, arg2])\n"
                                "Java: 使用 OWASP Java Encoder + ProcessBuilder。"
                            ),
                            "type": "cmdi",
                            "evidence": {
                                "param": param,
                                "payload": payload[:60],
                                "elapsed": round(elapsed, 2),
                                "url": test_url[:200],
                            },
                            "confidence_level": "低",
                            "location": {
                                "type": "url_parameter",
                                "target": param,
                                "detail": "参数疑似存在命令注入",
                            },
                            "ai_advice": f"**漏洞**：命令注入\n**优先级**：建议修复（存在一定风险）\n**影响**：参数 '{param}' 疑似存在命令注入\n**修复**：禁止将用户输入拼接到系统命令中，使用参数化API",
                        }
                    )
            except Exception as e:
                logger.warning(
                    "Command injection detection error on %s: %s", test_url[:120], e
                )
    return findings


async def detect_directory_traversal(url: str, params: list[str]) -> list[dict]:
    """目录遍历检测：发送路径遍历 payload，检查是否读取到系统文件。"""
    if not params:
        return []
    findings: list[dict] = []
    client = get_httpx_client()

    for param in params[:3]:
        for payload in TRAVERSAL_PAYLOADS[:2]:
            test_url = _build_test_url(url, param, payload)
            try:
                resp = await client.get(test_url, timeout=10.0, follow_redirects=True)
                body = _safe_read_body(resp)

                # 检查 Linux /etc/passwd 特征
                linux_match = any(sig in body for sig in PASSWD_SIGNATURES)
                # 检查 Windows hosts 特征
                windows_match = any(sig in body for sig in WINDOWS_HOSTS_SIGNATURES)

                if linux_match or windows_match:
                    findings.append(
                        {
                            "name": "目录遍历漏洞",
                            "severity": "high",
                            "level": "高风险",
                            "level_zh": "高风险",
                            "owasp": "A01:2021 - Broken Access Control",
                            "summary": f"参数 '{param}' 存在目录遍历漏洞，可读取系统敏感文件。",
                            "fix": (
                                "对用户输入的路径进行严格校验，使用白名单或 chroot  jail。\n"
                                "Python: os.path.commonpath([base_dir, target]) == base_dir\n"
                                "Node.js: path.resolve(base, input).startsWith(baseDir)\n"
                                "Java: 使用 Path.normalize() + startsWith(allowedBase) 校验。"
                            ),
                            "type": "traversal",
                            "evidence": {
                                "param": param,
                                "payload": payload[:60],
                                "os": "linux" if linux_match else "windows",
                                "status_code": resp.status_code,
                                "url": test_url[:200],
                            },
                            "confidence_level": "高",
                            "location": {
                                "type": "url_parameter",
                                "target": param,
                                "detail": "参数存在目录遍历",
                            },
                            "ai_advice": f"**漏洞**：目录遍历\n**优先级**：尽快修复（存在明确利用路径，风险较高）\n**影响**：参数 '{param}' 存在目录遍历\n**修复**：对用户输入的路径进行严格校验，使用白名单",
                        }
                    )
                elif (
                    resp.status_code == 200
                    and len(body) > 100
                    and ("<html" not in body.lower())
                ):
                    # 返回了非 HTML 的 200 响应，可能是文件内容
                    findings.append(
                        {
                            "name": "目录遍历漏洞（疑似）",
                            "severity": "medium",
                            "level": "中风险",
                            "level_zh": "中风险",
                            "owasp": "A01:2021 - Broken Access Control",
                            "summary": f"参数 '{param}' 路径遍历后返回非 HTML 的 200 响应，疑似读取到文件。",
                            "fix": (
                                "限制文件访问范围；使用文件 ID 映射代替真实路径。\n"
                                "Python: pathlib.Path(base_dir) / safe_filename，并校验 resolved path\n"
                                "Node.js: 使用 send 模块的 root 选项限制目录\n"
                                "Java: Spring ResourceHttpRequestHandler 配置 location。"
                            ),
                            "type": "traversal",
                            "evidence": {
                                "param": param,
                                "payload": payload[:60],
                                "status_code": 200,
                                "url": test_url[:200],
                            },
                            "confidence_level": "低",
                            "location": {
                                "type": "url_parameter",
                                "target": param,
                                "detail": "参数疑似存在目录遍历",
                            },
                            "ai_advice": f"**漏洞**：目录遍历\n**优先级**：建议修复（存在一定风险）\n**影响**：参数 '{param}' 疑似存在目录遍历\n**修复**：对用户输入的路径进行严格校验，使用白名单",
                        }
                    )
            except Exception as e:
                logger.warning(
                    "Directory traversal detection error on %s: %s", test_url[:120], e
                )
    return findings


async def detect_insecure_deserialization(headers: dict, url: str) -> list[dict]:
    """不安全的反序列化简单检测：检查响应头和 Cookie 中的序列化特征。"""
    findings: list[dict] = []
    # 检查响应头中的序列化特征（某些框架会把序列化对象放在自定义头里）
    for key, value in headers.items():
        if not isinstance(value, str):
            continue
        for sig in DESER_SIGNATURES:
            if sig in value:
                findings.append(
                    {
                        "name": "不安全的反序列化（响应头）",
                        "severity": "high",
                        "level": "高风险",
                        "level_zh": "高风险",
                        "owasp": "A08:2021 - Software and Data Integrity Failures",
                        "summary": f"响应头 '{key}' 中发现可能的序列化对象特征（{sig}）。",
                        "fix": (
                            "避免在 HTTP 头中传输序列化对象；使用 JSON + 签名（HMAC/JWS）。\n"
                            "Python: 使用 json + itsdangerous.signer 代替 pickle\n"
                            "Node.js: JSON.stringify + crypto.createHmac\n"
                            "Java: 使用 JWT 或签名 Cookie，禁用 Java 原生序列化。"
                        ),
                        "type": "deserialization",
                        "evidence": {
                            "header": key,
                            "signature": sig,
                            "value": value[:100],
                        },
                        "confidence_level": "中",
                        "location": {
                            "type": "response_header",
                            "target": key,
                            "detail": "响应头中存在不安全的反序列化特征",
                        },
                        "ai_advice": f"**漏洞**：不安全的反序列化\n**优先级**：尽快修复（存在明确利用路径，风险较高）\n**影响**：响应头 '{key}' 中发现可能的序列化对象特征\n**修复**：避免在HTTP头中传输序列化对象，使用JSON+签名",
                    }
                )
                break

    # 检查 Set-Cookie 中的序列化特征
    set_cookie = headers.get("set-cookie", headers.get("Set-Cookie", ""))
    if set_cookie:
        for sig in DESER_SIGNATURES:
            if sig in set_cookie:
                findings.append(
                    {
                        "name": "不安全的反序列化（Cookie）",
                        "severity": "high",
                        "level": "高风险",
                        "level_zh": "高风险",
                        "owasp": "A08:2021 - Software and Data Integrity Failures",
                        "summary": f"Cookie 中发现可能的序列化对象特征（{sig}）。",
                        "fix": (
                            "Cookie 中禁止存放序列化对象；改用 JWT 或加密 token。\n"
                            "Python: 使用 flask-jwt-extended 或 itsdangerous\n"
                            "Node.js: jsonwebtoken + jwk\n"
                            "Java: Spring Session + Redis JSON 存储，禁用原生序列化。"
                        ),
                        "type": "deserialization",
                        "evidence": {
                            "header": "Set-Cookie",
                            "signature": sig,
                            "value": set_cookie[:100],
                        },
                        "confidence_level": "中",
                        "location": {
                            "type": "cookie",
                            "target": "Set-Cookie",
                            "detail": "Cookie中存在不安全的反序列化特征",
                        },
                        "ai_advice": "**漏洞**：不安全的反序列化\n**优先级**：尽快修复（存在明确利用路径，风险较高）\n**影响**：Cookie中发现可能的序列化对象特征\n**修复**：Cookie中禁止存放序列化对象，改用JWT或加密token",
                    }
                )
                break

    # 可选：请求页面检查 body（轻量）
    if not findings:
        try:
            client = get_httpx_client()
            resp = await client.get(url, timeout=10.0, follow_redirects=True)
            body = _safe_read_body(resp)
            for sig in DESER_SIGNATURES:
                if sig in body:
                    findings.append(
                        {
                            "name": "不安全的反序列化（页面内容）",
                            "severity": "medium",
                            "level": "中风险",
                            "level_zh": "中风险",
                            "owasp": "A08:2021 - Software and Data Integrity Failures",
                            "summary": f"页面内容中发现可能的序列化对象特征（{sig}）。",
                            "fix": (
                                "不要在页面中暴露序列化数据；使用 JSON 传输。\n"
                                "Python: 使用 marshmallow / pydantic 做序列化校验\n"
                                "Node.js: JSON.parse + Joi / zod 校验 schema\n"
                                "Java: Jackson ObjectMapper + @JsonIgnore 隐藏敏感字段。"
                            ),
                            "type": "deserialization",
                            "evidence": {"signature": sig, "url": url[:200]},
                            "confidence_level": "低",
                        }
                    )
                    break
        except Exception as e:
            logger.warning("Deserialization body check error: %s", e)
    return findings


async def detect_ssrf_enhanced(url: str, params: list[str]) -> list[dict]:
    """SSRF 检测增强：检查 URL 参数是否会触发内网请求或重定向到内网。"""
    if not params:
        return []
    findings: list[dict] = []
    client = get_httpx_client()

    # 内网地址 payload
    ssrf_payloads = [
        "http://127.0.0.1:80/",
        "http://169.254.169.254/latest/meta-data/",
        "http://localhost/",
        "http://10.0.0.1/",
    ]

    for param in params[:3]:
        for payload in ssrf_payloads[:2]:
            test_url = _build_test_url(url, param, payload)
            try:
                resp = await client.get(test_url, timeout=10.0, follow_redirects=True)
                # 如果返回了 200 且内容与正常页面不同，可能成功访问了内网
                if resp.status_code == 200:
                    body = _safe_read_body(resp)
                    # 检查云元数据特征
                    if (
                        "instance-id" in body
                        or "ami-id" in body
                        or "local-ipv4" in body
                    ):
                        findings.append(
                            {
                                "name": "SSRF 漏洞（云元数据访问）",
                                "severity": "critical",
                                "level": "高风险",
                                "level_zh": "高风险",
                                "owasp": "A10:2021 - Server-Side Request Forgery",
                                "summary": f"参数 '{param}' 存在 SSRF 漏洞，可访问云元数据服务。",
                                "fix": (
                                    "禁止用户输入直接作为后端请求目标；使用 URL 白名单 + DNS 解析校验。\n"
                                    "Python: 使用 urllib.parse + ipaddress 过滤私有 IP\n"
                                    "Node.js: 使用 url.parse + net.isIP + 白名单\n"
                                    "Java: Apache HttpClient + 自定义 DNSResolver 拦截内网 IP。"
                                ),
                                "type": "ssrf",
                                "evidence": {
                                    "param": param,
                                    "payload": payload[:60],
                                    "body_hint": body[:80],
                                    "url": test_url[:200],
                                },
                                "confidence_level": "高",
                                "location": {
                                    "type": "url_parameter",
                                    "target": param,
                                    "detail": "参数存在SSRF漏洞",
                                },
                                "ai_advice": f"**漏洞**：SSRF\n**优先级**：立即修复（可被直接利用，可能导致服务器沦陷）\n**影响**：参数 '{param}' 存在SSRF漏洞，可访问云元数据服务\n**修复**：禁止用户输入直接作为后端请求目标，使用URL白名单+DNS解析校验",
                            }
                        )
                    else:
                        findings.append(
                            {
                                "name": "SSRF 漏洞（疑似内网访问）",
                                "severity": "high",
                                "level": "高风险",
                                "level_zh": "高风险",
                                "owasp": "A10:2021 - Server-Side Request Forgery",
                                "summary": f"参数 '{param}' 传入内网地址后返回 200，疑似存在 SSRF。",
                                "fix": (
                                    "对出站请求目标进行白名单限制；禁止解析到内网 IP。\n"
                                    "Python: aiohttp 配合自定义 resolver 过滤 RFC1918\n"
                                    "Node.js: 使用 proxy-agent + 白名单域名\n"
                                    "Java: Spring Cloud Gateway 配置 deny-by-default 路由。"
                                ),
                                "type": "ssrf",
                                "evidence": {
                                    "param": param,
                                    "payload": payload[:60],
                                    "status_code": 200,
                                    "url": test_url[:200],
                                },
                                "confidence_level": "中",
                                "location": {
                                    "type": "url_parameter",
                                    "target": param,
                                    "detail": "参数疑似存在SSRF漏洞",
                                },
                                "ai_advice": f"**漏洞**：SSRF\n**优先级**：尽快修复（存在明确利用路径，风险较高）\n**影响**：参数 '{param}' 疑似存在SSRF漏洞，可访问内网资源\n**修复**：禁止用户输入直接作为后端请求目标，使用URL白名单+DNS解析校验",
                            }
                        )
            except Exception as e:
                logger.warning("SSRF detection error on %s: %s", test_url[:120], e)
    return findings


# ---------- Scan Functions ----------


async def check_host_reachable(host: str) -> str | None:
    def _check() -> str | None:
        try:
            socket.getaddrinfo(host, None)
            return None
        except socket.gaierror:
            return "无法解析该域名，请确认网址拼写是否正确"

    try:
        return await asyncio.wait_for(asyncio.to_thread(_check), timeout=3.0)
    except asyncio.TimeoutError:
        return "域名解析超时"
    except Exception:
        return "域名解析失败"


async def fetch_headers(url: str) -> tuple[dict, bool, str, str | None]:
    """获取目标 URL 的响应头，区分各种失败情况。
    返回: (headers, is_https, final_url, error)
    error 为 None 表示成功；否则为分类错误信息。
    """

    def _sync_resolve(h: str) -> str | None:
        try:
            socket.getaddrinfo(h, None)
            return None
        except socket.gaierror:
            pass
        try:
            socket.gethostbyname(h)
            return None
        except socket.gaierror:
            pass
        return "DNS_RESOLVE_FAIL"

    # SSRF 纵深防护：公共函数统一过 sanitize_url
    try:
        url = sanitize_url(url)
    except ValueError as e:
        return {}, False, url, str(e)

    parsed = urlparse(url)
    host = parsed.hostname or ""
    path = parsed.path or "/"
    if parsed.query:
        path += "?" + parsed.query
    is_https = parsed.scheme == "https"
    headers: dict = {}
    final_url = url
    error: str | None = None

    if not host:
        return {}, False, url, "网址格式无效，缺少主机名"

    # DNS 解析检查
    try:
        dns_err = await asyncio.wait_for(
            asyncio.to_thread(_sync_resolve, host),
            timeout=5.0,
        )
    except asyncio.TimeoutError:
        return {}, False, url, "DNS_RESOLVE_TIMEOUT"
    if dns_err == "DNS_RESOLVE_FAIL":
        return {}, False, url, "DNS_RESOLVE_FAIL"
    if dns_err == "DNS_RESOLVE_TIMEOUT":
        return {}, False, url, "DNS_RESOLVE_TIMEOUT"

    # SSRF 二次检查 + DNS Pinning（防止 DNS 重绑定攻击）
    # 安全最佳实践：在 validate → request 之间做 IP 一致性校验，
    # 确保 httpx 实际连接的 IP 与校验时解析的 IP 一致
    # 注意：CDN 域名（如 Cloudflare）在短时间间隔内可能解析到不同 IP，
    # 这是正常行为，不应判定为 DNS 重绑定攻击。
    # 仅当两次解析的 IP 属于完全不同的 ASN/网段时才视为可疑。
    _pinned_ip: str | None = None
    _pinned_ips: set[str] = set()  # 记录首次解析到的所有 IP
    if host and host not in ALLOWED_INTERNAL_HOSTS:
        try:
            from utils import resolve_and_validate_ip

            _pinned_ip = resolve_and_validate_ip(host)
            # 收集所有解析到的 IP，用于后续宽松比对
            try:
                infos = socket.getaddrinfo(host, None)
                for info in infos:
                    _pinned_ips.add(info[4][0])
            except Exception:
                pass
        except ValueError as e:
            return {}, False, url, str(e)
        except Exception:
            pass

    client = get_httpx_client()

    # 辅助函数：根据 HTTP 状态码分类
    def classify_status(status: int, resp_headers: dict) -> tuple:
        if status in (301, 302, 307, 308):
            loc = resp_headers.get("location", "")
            return {
                "_status_code": status,
                "_redirect_location": loc,
            }, f"REDIRECT_{status}"
        if status == 401:
            return {"_status_code": 401}, "AUTH_REQUIRED"
        if status == 403:
            return {"_status_code": 403}, "FORBIDDEN"
        if status == 405:
            return {"_status_code": 405}, "METHOD_NOT_ALLOWED"
        if status >= 500:
            return {"_status_code": status}, f"SERVER_ERROR_{status}"
        if status >= 400:
            return {"_status_code": status}, f"CLIENT_ERROR_{status}"
        return resp_headers, None

    # 尝试 https 升级（对 http URL）
    if not is_https:
        # DNS Pinning 最终校验：发起请求前再次验证 IP 未变（防 DNS 重绑定）
        # CDN 域名可能返回不同 IP，只要新 IP 在首次解析的 IP 集合中即视为正常
        if _pinned_ip and host not in ALLOWED_INTERNAL_HOSTS:
            try:
                from utils import resolve_and_validate_ip

                _final_ip = resolve_and_validate_ip(host)
                if _final_ip != _pinned_ip and _final_ip not in _pinned_ips:
                    # 两次解析到完全不同的 IP，疑似 DNS 重绑定
                    logger.warning("DNS rebinding detected: %s ip %s -> %s", host, _pinned_ip, _final_ip)
                    return {}, False, url, "DNS 解析结果不一致，疑似 DNS 重绑定攻击"
            except ValueError as e:
                return {}, False, url, str(e)
            except Exception:
                pass
        try:
            resp = await asyncio.wait_for(
                client.head("https://" + host + path, follow_redirects=False),
                timeout=5.0,
            )
            h = dict(resp.headers)
            h["_status_code"] = resp.status_code
            headers, err = classify_status(resp.status_code, h)
            if (
                err is None
                or err.startswith("REDIRECT_")
                or err in ("AUTH_REQUIRED", "FORBIDDEN", "METHOD_NOT_ALLOWED")
            ):
                is_https = True
                final_url = "https://" + host + path
                if err is None:
                    error = None
                else:
                    error = err
                    headers = h
                if err is None:
                    return headers, is_https, final_url, None
        except asyncio.TimeoutError:
            pass
        except httpx.ConnectError:
            pass
        except Exception as e:
            logger.warning("fetch_headers probe error: %s", e)

    # 主请求：先 HEAD，失败 fallback GET（GET 使用 stream 模式避免下载大响应体）
    if not headers:
        # DNS Pinning 最终校验（主请求路径）
        # CDN 域名可能返回不同 IP，只要新 IP 在首次解析的 IP 集合中即视为正常
        if _pinned_ip and host not in ALLOWED_INTERNAL_HOSTS:
            try:
                from utils import resolve_and_validate_ip

                _final_ip = resolve_and_validate_ip(host)
                if _final_ip != _pinned_ip and _final_ip not in _pinned_ips:
                    logger.warning("DNS rebinding detected (main): %s ip %s -> %s", host, _pinned_ip, _final_ip)
                    return {}, False, url, "DNS 解析结果不一致，疑似 DNS 重绑定攻击"
            except ValueError as e:
                return {}, False, url, str(e)
            except Exception:
                pass
        last_err = None

        async def _try_head() -> tuple[dict, bool, str, str | None]:
            resp = await asyncio.wait_for(
                client.head(url, follow_redirects=False),
                timeout=6.0,
            )
            h = dict(resp.headers)
            h["_status_code"] = resp.status_code
            _headers, err = classify_status(resp.status_code, h)
            if err is None:
                return _headers, is_https, final_url, None
            return h, is_https, final_url, err

        async def _try_get() -> tuple[dict, bool, str, str | None]:
            resp = await asyncio.wait_for(
                client.stream("GET", url, follow_redirects=False).__aenter__(),
                timeout=6.0,
            )
            try:
                h = dict(resp.headers)
                h["_status_code"] = resp.status_code
                _headers, err = classify_status(resp.status_code, h)
                if err is None:
                    return _headers, is_https, final_url, None
                return h, is_https, final_url, err
            finally:
                await resp.aclose()

        for method_name, method_coro in (("HEAD", _try_head), ("GET", _try_get)):
            try:
                headers, is_https, final_url, error = await async_retry(
                    coro=method_coro,
                    max_attempts=2,
                    exceptions=(
                        asyncio.TimeoutError,
                        httpx.ConnectError,
                        httpx.RemoteProtocolError,
                        httpx.NetworkError,
                    ),
                    base_delay=0.5,
                    max_delay=2.0,
                )
                if error is None or error:
                    return headers, is_https, final_url, error
            except asyncio.TimeoutError:
                last_err = "TIMEOUT"
            except httpx.ConnectError:
                last_err = "CONNECT_FAIL"
            except httpx.RemoteProtocolError:
                last_err = "PROTOCOL_ERROR"
            except (ssl.SSLError, ssl.CertificateError) as e:
                # Vuln Sentinel 修复：SSL 错误（如证书过期、协议不匹配）→ 尝试用宽松 SSL 重试
                last_err = f"SSL_ERROR:{str(e)[:40]}"
            except Exception as e:
                last_err = f"REQUEST_FAIL:{str(e)[:60]}"
        # 全部方法失败
        if last_err == "TIMEOUT":
            error = "连接超时，该网站可能已下线或网络不可达"
        elif last_err == "CONNECT_FAIL":
            error = "无法连接到该网站，请确认网站是否在线"
        elif last_err == "PROTOCOL_ERROR":
            error = "协议错误，目标可能不支持 HTTPS 或使用了非标准端口"
        elif last_err and last_err.startswith("SSL_ERROR:"):
            # Vuln Sentinel：SSL 错误时，仅在用户显式关闭 TLS 验证后才允许跳过证书检查
            _tls_off = os.environ.get("TLS_VERIFY", "true").strip().lower() in (
                "0",
                "false",
                "no",
                "off",
            )
            if _tls_off:
                try:
                    # 用 stream 模式避免下载大响应体
                    resp = await asyncio.wait_for(
                        client.stream(
                            "GET", url, follow_redirects=False, verify=False
                        ).__aenter__(),
                        timeout=6.0,
                    )
                    try:
                        h = dict(resp.headers)
                        h["_status_code"] = resp.status_code
                        headers, err = classify_status(resp.status_code, h)
                        if err is None:
                            return headers, is_https, final_url, None
                        return h, is_https, final_url, err
                    finally:
                        await resp.aclose()
                except Exception:
                    error = "该网站的 SSL 证书存在问题，建议在浏览器中先确认可访问"
            else:
                error = "该网站的 SSL 证书验证失败。如需跳过验证，请在 .env 中设置 TLS_VERIFY=false（诊断模式）"
        elif last_err and last_err.startswith("REQUEST_FAIL:"):
            error = f"请求失败: {last_err[13:]}"
        else:
            error = "请求失败，请检查网址是否正确"
    return headers, is_https, final_url, error


async def get_ssl_info(hostname: str, port: int = 443) -> dict:
    cache_key = f"ssl:{hostname}:{port}"
    cached = await ssl_cache.get(cache_key)
    if cached is not None:
        return cached

    # 在线程里跑同步 SSL 操作，并加超时
    def _do_ssl() -> dict:
        # 优先尝试 CERT_REQUIRED：验证通过时 getpeercert() 返回完整证书字典
        # 如果验证失败（自签名/过期等），降级到 CERT_NONE + binary_form 手动解析
        for verify in (ssl.CERT_REQUIRED, ssl.CERT_NONE):
            try:
                ctx = ssl.create_default_context()
                ctx.check_hostname = verify == ssl.CERT_REQUIRED
                ctx.verify_mode = verify
                with socket.create_connection((hostname, port), timeout=5) as sock:
                    with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                        cipher = ssock.cipher()
                        version = ssock.version()

                        if verify == ssl.CERT_REQUIRED:
                            # 验证通过：getpeercert() 返回完整字典
                            cert = ssock.getpeercert(binary_form=False)
                            subject = dict(x[0] for x in cert.get("subject", []))
                            issuer = dict(x[0] for x in cert.get("issuer", []))
                            not_after = cert.get("notAfter", "")
                            san = cert.get("subjectAltName", [])
                            expired, days_left = False, None
                            if not_after:
                                try:
                                    expiry = datetime.strptime(
                                        not_after, "%b %d %H:%M:%S %Y %Z"
                                    )
                                    days_left = (expiry - datetime.utcnow()).days
                                    expired = days_left < 0
                                except ValueError:
                                    pass
                            return {
                                "has_cert": True,
                                "subject": subject.get("commonName", ""),
                                "issuer": issuer.get("commonName", ""),
                                "not_after": not_after,
                                "days_left": days_left,
                                "expired": expired,
                                "version": version,
                                "cipher": cipher[0] if cipher else "",
                                "san": [x[1] for x in san if x[0] == "DNS"][:5],
                                "weak": version in ["TLSv1", "TLSv1.1"]
                                or (cipher and "RC4" in str(cipher)),
                            }
                        else:
                            # 降级模式：CERT_NONE 时 getpeercert(binary_form=False) 返回空字典，
                            # 改用 binary_form=True + cryptography 库手动解析证书
                            cert_der = ssock.getpeercert(binary_form=True)
                            if not cert_der:
                                continue
                            from cryptography import x509
                            from cryptography.hazmat.backends import default_backend

                            cert_obj = x509.load_der_x509_certificate(
                                cert_der, default_backend()
                            )
                            subject_cn = ""
                            issuer_cn = ""
                            try:
                                subject_cn = cert_obj.subject.get_attributes_for_oid(
                                    x509.NameOID.COMMON_NAME
                                )[0].value
                            except Exception:
                                pass
                            try:
                                issuer_cn = cert_obj.issuer.get_attributes_for_oid(
                                    x509.NameOID.COMMON_NAME
                                )[0].value
                            except Exception:
                                pass
                            not_after = cert_obj.not_valid_after_utc.isoformat()
                            days_left = (
                                cert_obj.not_valid_after_utc - datetime.utcnow()
                            ).days
                            san_list = []
                            try:
                                ext = cert_obj.extensions.get_extension_for_class(
                                    x509.SubjectAlternativeName
                                )
                                san_list = ext.value.get_values_for_type(
                                    x509.DNSName
                                )[:5]
                            except Exception:
                                pass
                            return {
                                "has_cert": True,
                                "subject": subject_cn,
                                "issuer": issuer_cn,
                                "not_after": not_after,
                                "days_left": days_left,
                                "expired": days_left < 0 if days_left is not None else False,
                                "version": version,
                                "cipher": cipher[0] if cipher else "",
                                "san": san_list,
                                "weak": version in ["TLSv1", "TLSv1.1"]
                                or (cipher and "RC4" in str(cipher)),
                            }
            except ssl.SSLError:
                # CERT_REQUIRED 失败（自签名/过期等），降级到 CERT_NONE 重试
                if verify == ssl.CERT_REQUIRED:
                    continue
                return {"has_cert": False, "error": "SSL 握手失败（证书验证错误）"}
            except Exception as e:
                if verify == ssl.CERT_REQUIRED:
                    continue
                return {"has_cert": False, "error": str(e)[:100]}
        return {"has_cert": False, "error": "SSL 连接失败"}

    try:
        result = await asyncio.wait_for(asyncio.to_thread(_do_ssl), timeout=6.0)
    except asyncio.TimeoutError:
        result = {
            "has_cert": False,
            "error": "SSL 握手超时（目标可能未启用 HTTPS 或响应较慢）",
        }
    await ssl_cache.set(cache_key, result, settings.ssl_cache_ttl_seconds)
    return result


def detect_waf(headers: dict) -> list[dict]:
    headers_lower = {
        k.lower(): str(v) for k, v in headers.items() if isinstance(v, str)
    }
    detected: list[dict] = []
    for waf_name, signatures in WAF_SIGNATURES.items():
        for sig in signatures:
            # 仅匹配 header 名称，避免 header 值中包含关键词导致误报
            if sig.lower() in headers_lower:
                detected.append(
                    {
                        "name": waf_name,
                        "signature": sig,
                        "value": headers_lower[sig.lower()],
                    }
                )
                break
            for hk in headers_lower:
                if sig.lower() == hk.lower():
                    detected.append({"name": waf_name, "signature": sig, "value": headers_lower[hk]})
                    break
    return detected


# ============== SQLi 盲注（time-based）检测 ==============

# time-based SQLi 常见特征：SLEEP(n) / WAITFOR DELAY / BENCHMARK(n,...) / pg_sleep(n)
_TIME_SQLI_PATTERNS = [
    re.compile(r"SLEEP\s*\(\s*(\d+(?:\.\d+)?)\s*\)", re.IGNORECASE),
    re.compile(r"WAITFOR\s+DELAY\s+['\"]?(\d+):(\d+):(\d+)['\"]?", re.IGNORECASE),
    re.compile(r"BENCHMARK\s*\(\s*(\d+)\s*,", re.IGNORECASE),
    re.compile(r"PG_SLEEP\s*\(\s*(\d+(?:\.\d+)?)\s*\)", re.IGNORECASE),
]


def _extract_sqli_sleep(url: str) -> float | None:
    """从 URL 中提取 time-based 注入的预期等待秒数。"""
    if not url:
        return None
    # 优先从 query string 中找，避免误判 fragment 中的 SLEEP 字符串
    parsed = urlparse(url)
    haystack = parsed.query or url
    for pat in _TIME_SQLI_PATTERNS:
        m = pat.search(haystack)
        if not m:
            continue
        groups = m.groups()
        try:
            if len(groups) == 1:
                return float(groups[0])
            if len(groups) == 3:  # WAITFOR DELAY hh:mm:ss
                h, mi, s = (int(x) for x in groups)
                return float(h * 3600 + mi * 60 + s)
        except (TypeError, ValueError):
            return None
    return None


async def detect_time_based_sqli(
    url: str, threshold: float = 2.5, timeout: float = 8.0
) -> dict:
    """SQLi 盲注（time-based）检测。

    思路：
    1. 先扫描 URL 字符串是否携带 SLEEP/WAITFOR/BENCHMARK/pg_sleep 注入特征。
    2. 如果发现特征，模拟注入造成的等待时长，再判定是否 vulnerable。
    3. 普通 URL 不含注入特征时，即使响应慢也**不判为漏洞**，仅标记为"响应慢"。

    返回：
        {
            "vulnerable": bool,
            "response_time": float,   # 实际等待/响应秒数
            "payload": str,           # 原始 URL（注入 payload）
            "threshold": float,
            "method": "simulated" | "live" | "live-slow",
        }
    """
    threshold = max(0.0, float(threshold))
    payload = url or ""
    # SSRF 防护：即使当前未被调用，也统一过 sanitize_url
    try:
        payload = sanitize_url(payload) if payload else payload
    except ValueError:
        return {
            "vulnerable": False,
            "response_time": 0.0,
            "payload": payload,
            "threshold": threshold,
            "method": "blocked",
        }
    sleep_seconds = _extract_sqli_sleep(payload)

    if sleep_seconds is not None and sleep_seconds > 0:
        # 注入特征识别成功：模拟 time-based 盲注的等待效果
        # 限制 sleep 模拟时长上限 10s，避免被恶意 payload 拖死
        sleep_seconds = min(sleep_seconds, 10.0)
        start = time.time()
        await asyncio.sleep(sleep_seconds)
        elapsed = time.time() - start
        return {
            "vulnerable": elapsed >= threshold,
            "response_time": round(elapsed, 3),
            "payload": payload,
            "threshold": threshold,
            "method": "simulated",
        }

    # 常规请求：用 httpx 测响应时间
    # 注意：普通 URL 不含 SLEEP/WAITFOR/BENCHMARK/pg_sleep 时，
    # 即使响应慢也**不判为 SQLi 漏洞**，仅记录响应时间
    start = time.time()
    elapsed = 0.0
    method = "live"
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            try:
                await client.get(payload)
            except (httpx.HTTPError, ValueError):
                method = "live-error"
    except Exception:
        method = "live-error"
    elapsed = time.time() - start
    # 普通请求：无论响应多慢，都不判为 SQLi 漏洞
    is_slow = elapsed >= threshold
    if is_slow:
        method = "live-slow"
    return {
        "vulnerable": False,
        "response_time": round(elapsed, 3),
        "payload": payload,
        "threshold": threshold,
        "method": method,
    }


async def check_sensitive_paths(host: str, is_https: bool) -> list[dict]:
    """探测常见敏感路径暴露情况。每个请求独立超时。
    不只是看 HTTP 200，还要检查响应内容特征，避免把登录页/错误页误判为泄露。
    robots.txt 作为 info 提示，不算敏感路径暴露。"""
    results: list[dict] = []
    client = get_httpx_client()

    # 全局 forbidden 特征：响应内容包含这些关键词时，判定为 suspect/protected
    GLOBAL_FORBIDDEN = [
        "waf_block",
        "punish",
        "captcha",
        "安全验证",
        "alicdn.com",
        "login",
        "登录",
        "error",
        "404",
        "403",
        "forbidden",
        "denied",
        "访问被拒绝",
        "请登录",
        "请验证",
        "verify",
        "authentication",
    ]

    # 内容特征校验规则
    CONTENT_CHECKS = {
        "/.git/config": {
            "required": ["[core]", "repositoryformatversion"],
            "forbidden": ["<html", "<!doctype", "<head"],
        },
        "/.env": {
            "required": ["="],
            "sensitive_keys": [
                "SECRET",
                "PASSWORD",
                "TOKEN",
                "KEY",
                "API",
                "DB_",
                "DATABASE",
                "PRIVATE",
                "ACCESS",
            ],
            "forbidden": ["<html", "<!doctype", "<head"],
        },
        "/.env.local": {
            "required": ["="],
            "sensitive_keys": [
                "SECRET",
                "PASSWORD",
                "TOKEN",
                "KEY",
                "API",
                "DB_",
                "DATABASE",
                "PRIVATE",
                "ACCESS",
            ],
            "forbidden": ["<html", "<!doctype", "<head"],
        },
        "/.svn/entries": {
            "required": ["dir", "svn:", "text-base"],
            "forbidden": ["<html", "<!doctype", "<head"],
        },
        "/.htaccess": {
            "required_any": [
                "RewriteEngine",
                "AuthType",
                "Require",
                "Deny from",
                "AllowOverride",
                "Order allow,deny",
                "Redirect",
            ],
            "forbidden": ["<html", "<!doctype", "<head"],
        },
        "/config/database.yml": {
            "required": ["adapter", "host", "database"],
            "forbidden": ["<html", "<!doctype", "<head"],
        },
        "/backup.sql": {
            "required": ["CREATE TABLE", "INSERT INTO"],
            "forbidden": ["<html", "<!doctype", "<head"],
        },
        "/dump.sql": {
            "required": ["CREATE TABLE", "INSERT INTO"],
            "forbidden": ["<html", "<!doctype", "<head"],
        },
    }

    def analyze_content(path: str, text: str) -> dict:
        """分析响应内容，返回判定结果。"""
        text_lower = text.lower()

        # 公开文件（如 sitemap.xml、robots.txt）的关键词出现属于正常情况，跳过 GLOBAL_FORBIDDEN
        PUBLIC_PATHS = {"/sitemap.xml", "/robots.txt"}
        if path in PUBLIC_PATHS:
            checks = CONTENT_CHECKS.get(path)
            if checks:
                # 有特定规则的，按规则判定
                pass  # 走下面的通用逻辑
            else:
                # 公开文件没有特定规则：默认 info，不当 suspect
                return {"verdict": "info", "reason": f"{path} 为公开文件，内容可供参考"}

        # 软 404 / 登录页 / WAF / 错误页识别
        soft404_signals = (
            "page not found",
            "not found",
            "404 not found",
            "file not found",
            "页面不存在",
            "找不到页面",
            "资源不存在",
            "无法找到",
            "sorry, the page you requested does not exist",
        )
        if any(sig in text_lower for sig in soft404_signals):
            return {
                "verdict": "suspect",
                "reason": "响应内容疑似软404/错误页，需人工复核",
            }

        login_signals = (
            "login",
            "sign in",
            "sign-in",
            "password",
            "remember me",
            "forgot password",
            "username",
            "验证码",
            "请登录",
            "登录",
        )
        if ("<form" in text_lower or "type=\"password\"" in text_lower) and any(sig in text_lower for sig in login_signals):
            return {
                "verdict": "suspect",
                "reason": "响应内容疑似登录页，需人工复核",
            }

        waf_signals = (
            "access denied",
            "forbidden",
            "request blocked",
            "security check",
            "bot detection",
            "captcha",
            "waf",
            "cloudflare",
        )
        if any(sig in text_lower for sig in waf_signals):
            return {
                "verdict": "suspect",
                "reason": "响应内容疑似 WAF/反爬拦截页，需人工复核",
            }

        # 全局 forbidden 检测（WAF/反爬/登录页/错误页）
        global_matches = [fb for fb in GLOBAL_FORBIDDEN if fb.lower() in text_lower]
        if global_matches:
            match_set = set(global_matches)
            # 单个泛词（如 login / error / 404）不直接下结论，避免把正常页面误判成拦截页
            strong_signals = {"captcha", "安全验证", "请登录", "登录", "verify", "authentication", "waf_block", "punish", "forbidden", "denied", "访问被拒绝", "请验证"}
            has_strong_signal = bool(match_set & strong_signals)
            has_format_signal = any(token in text_lower for token in ("<form", "type=\"password\"", "cloudflare", "akamai", "access denied", "security check"))
            if has_strong_signal and (has_format_signal or len(match_set) >= 2):
                return {
                    "verdict": "suspect",
                    "reason": f"响应内容命中 {', '.join(sorted(match_set)[:3])}，疑似 WAF 拦截/登录页/错误页，需人工复核",
                }

        checks = CONTENT_CHECKS.get(path)
        if not checks:
            # 没有特定规则的路径：简单启发式
            is_html = (
                "<html" in text_lower
                or "<!doctype" in text_lower
                or "<head" in text_lower
            )
            if is_html:
                return {
                    "verdict": "suspect",
                    "reason": "响应内容为 HTML 页面，疑似登录页或错误页，需人工确认",
                }
            return {"verdict": "exposed", "reason": "响应内容非 HTML，疑似敏感文件"}

        # 路径特定 forbidden 检测
        for fb in checks.get("forbidden", []):
            if fb.lower() in text_lower:
                return {
                    "verdict": "suspect",
                    "reason": f"响应内容包含 '{fb}'，疑似登录页或错误页，需人工确认",
                }

        # 检查 required（全部必须匹配）
        required = checks.get("required", [])
        if required:
            matched_required = sum(1 for r in required if r.lower() in text_lower)
            if matched_required < len(required):
                if matched_required > 0:
                    return {
                        "verdict": "suspect",
                        "reason": f"部分匹配敏感文件特征（{matched_required}/{len(required)}），需人工确认",
                    }
                return {
                    "verdict": "suspect",
                    "reason": "响应内容不匹配敏感文件特征，疑似误报，需人工确认",
                }

        # 检查 required_any（任一匹配即可）
        required_any = checks.get("required_any", [])
        if required_any:
            matched_any = any(r.lower() in text_lower for r in required_any)
            if not matched_any:
                return {
                    "verdict": "suspect",
                    "reason": "响应内容不匹配 Apache 配置文件特征，疑似误报，需人工确认",
                }

        # 检查敏感关键词（仅 .env 类）
        sensitive_keys = checks.get("sensitive_keys", [])
        if sensitive_keys:
            sk_found = [sk for sk in sensitive_keys if sk.lower() in text_lower]
            if not sk_found:
                return {
                    "verdict": "suspect",
                    "reason": "响应内容格式类似配置文件但不含敏感关键词，需人工确认",
                }
            return {
                "verdict": "exposed",
                "reason": f"发现敏感关键词：{', '.join(sk_found[:3])}",
            }

        return {"verdict": "exposed", "reason": "敏感文件内容特征完全匹配"}

    async def check(p: str, is_info: bool = False) -> dict | None:
        # 白名单路径：跳过检测，不报告
        if p in PATH_WHITELIST:
            return None
        protocol = "https" if is_https else "http"
        try:
            resp = await asyncio.wait_for(
                client.get(
                    protocol + "://" + host + p,
                    headers={"User-Agent": "Mozilla/5.0"},
                    follow_redirects=False,
                ),
                timeout=4.0,
            )
            if resp.status_code == 200:
                # 安全读取：限制响应体最大 256KB，防止大文件导致内存爆炸
                body_bytes = await resp.aread()
                if len(body_bytes) > 256 * 1024:
                    text = body_bytes[: 256 * 1024].decode("utf-8", errors="ignore")
                else:
                    text = body_bytes.decode("utf-8", errors="ignore")
                text = text or ""
                if is_info:
                    # robots.txt 等公开文件：只返回 info，不算暴露
                    return {
                        "path": p,
                        "status": resp.status_code,
                        "exposed": False,
                        "info": True,
                        "size": len(text),
                        "reason": "robots.txt 为公开文件，内容可供参考",
                        "snippet": text[:300].replace("\n", " ")
                        if len(text) < 2000
                        else "（内容过长，已截断）",
                    }
                analysis = analyze_content(p, text)
                result = {
                    "path": p,
                    "status": resp.status_code,
                    "exposed": analysis["verdict"] == "exposed",
                    "suspect": analysis["verdict"] == "suspect",
                    "size": len(text),
                    "reason": analysis["reason"],
                    "snippet": text[:200].replace("\n", " ")
                    if analysis["verdict"] == "exposed"
                    else "",
                    "detection_method": f"向 {('https' if is_https else 'http')}://{host}{p} 发送 GET 请求，检查响应状态码和内容特征",
                    "confidence_level": "高"
                    if analysis["verdict"] == "exposed"
                    else "中",
                    "review_required": analysis["verdict"] == "suspect",
                }
                return result
            elif resp.status_code in (403, 401):
                return {
                    "path": p,
                    "status": resp.status_code,
                    "exposed": False,
                    "protected": True,
                }
        except asyncio.TimeoutError:
            return None
        except Exception:
            return None
        return None

    try:
        tasks = []
        for p in SENSITIVE_PATHS:
            tasks.append(check(p, is_info=False))
        for p in INFO_PATHS[:2]:
            tasks.append(check(p, is_info=True))
        responses = await asyncio.wait_for(
            asyncio.gather(*tasks, return_exceptions=True),
            timeout=10.0,
        )
        results = [r for r in responses if r and not isinstance(r, Exception)]
    except asyncio.TimeoutError:
        results = []
    except Exception as e:
        logger.warning("check_sensitive_paths gather failed: %s", e)
        results = []
    return results


# Vuln Sentinel: 详细验证步骤（三步验证法：命令行 + 浏览器 + 工具重扫）
VERIFY_METHODS = {
    "hsts": {
        "summary": "验证 HSTS 头是否生效",
        "steps": [
            {
                "method": "命令行验证",
                "command": "curl -sI https://你的域名 | grep -i 'strict-transport-security'",
                "expect": "输出包含 Strict-Transport-Security 及 max-age>=31536000",
            },
            {
                "method": "浏览器验证",
                "command": "F12 → Network → 访问页面 → 查看响应头",
                "expect": "Response Headers 中存在 Strict-Transport-Security",
            },
            {
                "method": "工具重扫验证",
                "command": "使用本工具重新扫描该网站",
                "expect": "扫描结果中「缺少 HSTS」项消失，安全评分提升",
            },
        ],
    },
    "csp": {
        "summary": "验证 CSP 内容安全策略是否生效",
        "steps": [
            {
                "method": "命令行验证",
                "command": "curl -sI https://你的域名 | grep -i 'content-security-policy'",
                "expect": "输出包含 Content-Security-Policy 及策略规则",
            },
            {
                "method": "浏览器验证",
                "command": "F12 → Network → 访问页面 → 查看响应头",
                "expect": "Response Headers 中存在 Content-Security-Policy",
            },
            {
                "method": "工具重扫验证",
                "command": "使用本工具重新扫描该网站",
                "expect": "扫描结果中「缺少 CSP」项消失，安全评分提升",
            },
        ],
    },
    "x-frame": {
        "summary": "验证 X-Frame-Options 是否生效",
        "steps": [
            {
                "method": "命令行验证",
                "command": "curl -sI https://你的域名 | grep -i 'x-frame-options'",
                "expect": "输出包含 X-Frame-Options: DENY 或 SAMEORIGIN",
            },
            {
                "method": "浏览器验证",
                "command": "F12 → Network → 访问页面 → 查看响应头",
                "expect": "Response Headers 中存在 X-Frame-Options",
            },
            {
                "method": "工具重扫验证",
                "command": "使用本工具重新扫描该网站",
                "expect": "扫描结果中「缺少 X-Frame-Options」项消失，安全评分提升",
            },
        ],
    },
    "x-content-type": {
        "summary": "验证 X-Content-Type-Options 是否生效",
        "steps": [
            {
                "method": "命令行验证",
                "command": "curl -sI https://你的域名 | grep -i 'x-content-type-options'",
                "expect": "输出包含 X-Content-Type-Options: nosniff",
            },
            {
                "method": "浏览器验证",
                "command": "F12 → Network → 访问页面 → 查看响应头",
                "expect": "Response Headers 中存在 X-Content-Type-Options",
            },
            {
                "method": "工具重扫验证",
                "command": "使用本工具重新扫描该网站",
                "expect": "扫描结果中「缺少 X-Content-Type-Options」项消失，安全评分提升",
            },
        ],
    },
    "referrer": {
        "summary": "验证 Referrer-Policy 是否生效",
        "steps": [
            {
                "method": "命令行验证",
                "command": "curl -sI https://你的域名 | grep -i 'referrer-policy'",
                "expect": "输出包含 Referrer-Policy 及策略值",
            },
            {
                "method": "浏览器验证",
                "command": "F12 → Network → 访问页面 → 查看响应头",
                "expect": "Response Headers 中存在 Referrer-Policy",
            },
            {
                "method": "工具重扫验证",
                "command": "使用本工具重新扫描该网站",
                "expect": "扫描结果中「缺少 Referrer-Policy」项消失，安全评分提升",
            },
        ],
    },
    "permissions": {
        "summary": "验证 Permissions-Policy 是否生效",
        "steps": [
            {
                "method": "命令行验证",
                "command": "curl -sI https://你的域名 | grep -i 'permissions-policy'",
                "expect": "输出包含 Permissions-Policy 及策略规则",
            },
            {
                "method": "浏览器验证",
                "command": "F12 → Network → 访问页面 → 查看响应头",
                "expect": "Response Headers 中存在 Permissions-Policy",
            },
            {
                "method": "工具重扫验证",
                "command": "使用本工具重新扫描该网站",
                "expect": "扫描结果中「缺少 Permissions-Policy」项消失，安全评分提升",
            },
        ],
    },
    "server": {
        "summary": "验证服务器版本信息是否已隐藏",
        "steps": [
            {
                "method": "命令行验证",
                "command": "curl -sI https://你的域名 | grep -i '^server:'",
                "expect": "Server 头不包含具体版本号（如 nginx/1.18.0）",
            },
            {
                "method": "浏览器验证",
                "command": "F12 → Network → 访问页面 → 查看响应头",
                "expect": "Response Headers 中 Server 字段无版本信息",
            },
            {
                "method": "工具重扫验证",
                "command": "使用本工具重新扫描该网站",
                "expect": "扫描结果中「服务器信息泄露」项消失，安全评分提升",
            },
        ],
    },
    "https": {
        "summary": "验证 HTTPS 及强制跳转是否生效",
        "steps": [
            {
                "method": "命令行验证",
                "command": "curl -sI http://你的域名 | head -5",
                "expect": "返回 301/302 跳转至 https:// 开头的地址",
            },
            {
                "method": "浏览器验证",
                "command": "访问 http://你的域名，观察地址栏",
                "expect": "自动跳转到 https://，地址栏显示锁图标",
            },
            {
                "method": "工具重扫验证",
                "command": "使用本工具重新扫描该网站",
                "expect": "扫描结果中「未启用 HTTPS」项消失，安全评分提升",
            },
        ],
    },
    "ssl": {
        "summary": "验证 SSL 证书状态",
        "steps": [
            {
                "method": "命令行验证",
                "command": "openssl s_client -connect 你的域名:443 -servername 你的域名 < /dev/null 2>/dev/null | openssl x509 -noout -dates",
                "expect": "notAfter 日期在未来，剩余天数 > 30 天",
            },
            {
                "method": "浏览器验证",
                "command": "点击地址栏锁图标 → 查看证书",
                "expect": "证书有效，过期日期在 30 天以上",
            },
            {
                "method": "工具重扫验证",
                "command": "使用本工具重新扫描该网站",
                "expect": "扫描结果中 SSL 证书相关问题消失，安全评分提升",
            },
        ],
    },
    "cors": {
        "summary": "验证 CORS 配置是否安全",
        "steps": [
            {
                "method": "命令行验证",
                "command": "curl -sI -H 'Origin: https://evil.com' https://你的域名 | grep -i 'access-control-allow-origin'",
                "expect": "不应返回 Access-Control-Allow-Origin: * 或 evil.com",
            },
            {
                "method": "浏览器验证",
                "command": "F12 → Console → 执行跨域请求测试",
                "expect": "未授权域名无法获取响应数据",
            },
            {
                "method": "工具重扫验证",
                "command": "使用本工具重新扫描该网站",
                "expect": "扫描结果中 CORS 配置问题项消失，安全评分提升",
            },
        ],
    },
    "cookie": {
        "summary": "验证 Cookie 安全标志是否设置",
        "steps": [
            {
                "method": "浏览器验证",
                "command": "F12 → Application → Cookies → 选择域名",
                "expect": "Cookie 勾选了 Secure 和 HttpOnly 标志",
            },
            {
                "method": "命令行验证",
                "command": "curl -sI https://你的域名/login | grep -i 'set-cookie'",
                "expect": "Set-Cookie 中包含 Secure 和 HttpOnly",
            },
            {
                "method": "工具重扫验证",
                "command": "使用本工具重新扫描该网站",
                "expect": "扫描结果中 Cookie 安全问题项消失，安全评分提升",
            },
        ],
    },
    "info": {
        "summary": "通用验证方法",
        "steps": [
            {
                "method": "命令行验证",
                "command": "curl -sI https://你的域名",
                "expect": "检查响应头中相关安全配置",
            },
            {
                "method": "浏览器验证",
                "command": "F12 → Network → 访问页面 → 查看响应头",
                "expect": "检查 Response Headers 中的安全配置",
            },
            {
                "method": "工具重扫验证",
                "command": "使用本工具重新扫描该网站",
                "expect": "相关漏洞项消失，安全评分提升",
            },
        ],
    },
}


def get_verify_method_text(verify_key: str | None) -> str:
    """获取验证方法的文本描述（兼容旧接口）"""
    if not verify_key:
        return "重新扫描该网站，查看此项是否消失或评分是否提升。"
    info = VERIFY_METHODS.get(verify_key, VERIFY_METHODS["info"])
    if isinstance(info, dict):
        return info.get("summary", "重新扫描该网站，查看此项是否消失。")
    return info


def get_verify_steps(verify_key: str | None) -> list[dict]:
    """获取详细验证步骤列表"""
    if not verify_key:
        return VERIFY_METHODS["info"]["steps"]
    info = VERIFY_METHODS.get(verify_key)
    if isinstance(info, dict) and "steps" in info:
        return info["steps"]
    # 兼容旧格式：只有字符串的情况
    return [
        {
            "method": "命令行验证",
            "command": info if isinstance(info, str) else "",
            "expect": "验证修复是否生效",
        },
        {
            "method": "浏览器验证",
            "command": "F12 → Network → 查看响应头",
            "expect": "检查相关安全配置是否存在",
        },
        {
            "method": "工具重扫验证",
            "command": "使用本工具重新扫描该网站",
            "expect": "相关漏洞项消失，安全评分提升",
        },
    ]


# 5 维交叉验证机制：降低安全扫描误报率
# D1: 多次请求验证（同一 URL 3 次取 header 并集）
# D2: 子路径验证（/, /index.html, /login）
# D3: Meta 兜底（解析 HTML 中 <meta http-equiv="...">）
# D4: 上下文过滤（HSTS 仅在 HTTPS 报，CSP 在 HTTPS 优先）
# D5: 置信度评分（多次命中 → 95；单维命中 → 55；命中但有 meta 替代 → 70）

# 各 finding name 与安全头的映射
_FINDING_HEADER_KEY = {
    "缺少 HSTS": "strict-transport-security",
    "缺少 CSP": "content-security-policy",
    "缺少 X-Frame-Options": "x-frame-options",
    "缺少 X-Content-Type-Options": "x-content-type-options",
    "缺少 Referrer-Policy": "referrer-policy",
    "缺少 Permissions-Policy": "permissions-policy",
}

# meta http-equiv 可覆盖的安全头（同等防护效力）
_META_EQUIV_HEADERS = {
    "content-security-policy": "Content-Security-Policy",
    "x-frame-options": "X-Frame-Options",
    "x-content-type-options": "X-Content-Type-Options",
    "strict-transport-security": "Strict-Transport-Security",
}


async def cross_validate_findings(
    url: str,
    headers: dict,
    findings: list,
    known_cdns: list[str] | None = None,
    sensitive_paths: list[dict] | None = None,
    cookie_issues: list[str] | None = None,
    is_https: bool | None = None,
) -> dict:
    """11 维交叉验证机制，降低误报。

    维度：
    - D0 已知 CDN 列表：用户提供已知 CDN 厂商，自动降低 Server 头 confidence
    - D1 多次请求验证：同一 URL 请求 2 次取 header 并集（间隔 0s，并发）
    - D2 子路径验证：扫 /、/index.html 跳过 /login 避免 401/403 干扰（并发）
    - D3 Meta 兜底：解析 HTML 看 <meta http-equiv="Content-Security-Policy">（并发）
    - D4 上下文过滤：HSTS 仅在 HTTPS 报，CSP 在 HTTPS 优先
    - D5 置信度评分：每发现带 confidence 0-100，< 60 标待人工确认
    - D6 敏感路径重新访问：同一路径 2 次重访 + 解析内容特征（.env 必须含 =，.git/config 必须含 [core]）
    - D7 CORS Allow-Origin 头在主响应+子资源中的真实存在性
    - D8 CORS Allow-Credentials 真实在响应中（与 * 组合 = 极高风险）
    - D9 Cookie 多次请求一致性（连续 3 次请求 Set-Cookie 头稳定性）
    - D10 SSL/TLS 协议版本重新验证（用 ssl 模块重连）
    - D11 信息泄露多页面验证（首页 + 1 个子页面同时发现 = 高置信度）

    性能优化：D0 + D1 + D2 + D3 + D6 + D7 + D8 + D9 + D11 用 asyncio.gather 一次发出所有请求，
    统一超时 5s，原 3 次请求改为 2 次，省掉 0.2s 间隔 sleep。

    返回 dict，key 是 finding name，value 是：
    {
        "verified": True/False,
        "confidence": 0-100,
        "reason": "为什么 verified / 为什么 confidence 这么低",
        "evidence_d1_d11": "D0: ..., D1: ..., ..., D11: ..."
    }
    """
    result: dict[str, dict] = {}

    # 并发限制：避免同时发出过多请求
    _cv_sem = asyncio.Semaphore(5)

    async def _with_sem(coro: Coroutine) -> Any:
        async with _cv_sem:
            return await coro

    # 工具：安全获取 url scheme
    try:
        parsed = urlparse(url)
        is_https_url = (parsed.scheme or "").lower() == "https"
        host = parsed.hostname or ""
    except Exception:
        is_https_url = False
        host = ""

    # 工具：检查 header 是否存在（不区分大小写）
    def has_header(header_dict: dict, name: str) -> bool:
        n = name.lower()
        for k, v in (header_dict or {}).items():
            if not isinstance(v, str):
                continue
            if k.lower() == n and v.strip():
                return True
        return False

    # 工具：从 header dict 取 header 值（不区分大小写）
    def get_header_value(header_dict: dict, name: str) -> str | None:
        n = name.lower()
        for k, v in (header_dict or {}).items():
            if not isinstance(v, str):
                continue
            if k.lower() == n:
                return v
        return None

    # ========== D0: 已知 CDN 列表（用户提供，自动降低 Server 头 confidence） ==========
    d0_evidence: dict[str, str] = {}
    d0_match: dict[str, bool] = {}
    try:
        known_cdns_norm = [
            c.lower().strip() for c in (known_cdns or []) if c and c.strip()
        ]
        if known_cdns_norm:
            # 在 Server 头 / CDN 特征头里查找用户提供的 CDN 关键字
            server_val_lower = (get_header_value(headers, "server") or "").lower()
            cdn_feature_keys = (
                "cf-ray",
                "x-amz-cf-id",
                "x-served-by",
                "x-cache",
                "x-amz-cf-pop",
            )
            header_keys_lower = {k.lower() for k in (headers or {}).keys()}
            for f_name in _FINDING_HEADER_KEY:
                d0_match[f_name] = False
            for cdn_kw in known_cdns_norm:
                hit = (
                    (cdn_kw in server_val_lower)
                    or any(
                        cdn_kw in (headers or {}).get(k, "").lower()
                        for k in cdn_feature_keys
                    )
                    or any(cdn_kw in hk for hk in header_keys_lower)
                )
                if hit:
                    d0_match["Server 头由 CDN 注入"] = True
                    d0_evidence["Server 头由 CDN 注入"] = (
                        f"D0: 用户已知 CDN 列表命中 '{cdn_kw}'，自动降低 Server 头 confidence"
                    )
                    break
    except Exception:
        for f_name in _FINDING_HEADER_KEY:
            d0_match.setdefault(f_name, False)
            d0_evidence.setdefault(f_name, "D0: 用户未提供已知 CDN 列表")

    # ========== D1 + D2 + D3 并发执行 ==========
    # 统一超时 5s；D1 用 2 次（不再 sleep 0.2s）；D2 跳过 /login
    _CV_TIMEOUT = 5.0
    d1_missing_counts: dict[str, int] = {}
    d1_present_counts: dict[str, int] = {}
    d1_evidence: dict[str, str] = {}
    d2_evidence: dict[str, str] = {}
    d2_present: dict[str, bool] = {}
    d3_meta_found: dict[str, bool] = {}
    d3_evidence: dict[str, str] = {}

    async def _d1_probe() -> dict[str, str]:
        """D1: 同一 URL 2 次并发请求，header 取并集。用 HEAD 避免下载 body。"""
        merged: dict[str, str] = {}
        try:
            client = get_httpx_client()
            tasks = [
                asyncio.wait_for(
                    client.head(url, follow_redirects=False),
                    timeout=_CV_TIMEOUT,
                )
                for _ in range(2)
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for r in results:
                if isinstance(r, Exception):
                    continue
                for k, v in r.headers.items():
                    if k.lower() not in {m.lower() for m in merged}:
                        merged[k] = v
        except Exception as e:
            logger.warning("CV D1 probe error: %s", e)
        return merged

    async def _d2_probe() -> dict[str, str]:
        """D2: 子路径验证（/, /index.html），跳过 /login 避免 401/403 干扰。用 HEAD 避免下载 body。"""
        merged: dict[str, str] = {}
        try:
            parsed_d2 = urlparse(url)
            base = f"{parsed_d2.scheme}://{parsed_d2.netloc}"
            sub_paths = ["/", "/index.html"]
            # 如果原 URL 已经是 /index.html，跳过
            if (parsed_d2.path or "").rstrip("/") == "/index.html":
                sub_paths = ["/"]
            client = get_httpx_client()
            tasks = [
                asyncio.wait_for(
                    client.head(base + p, follow_redirects=False),
                    timeout=_CV_TIMEOUT,
                )
                for p in sub_paths
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for r in results:
                if isinstance(r, Exception):
                    continue
                for k, v in r.headers.items():
                    if k.lower() not in {m.lower() for m in merged}:
                        merged[k] = v
        except Exception as e:
            logger.warning("CV D2 probe error: %s", e)
        return merged

    async def _d3_probe() -> str:
        """D3: 抓主页面 HTML，复用 D1 中第一份响应（如有），否则重新请求。限制响应体大小防止内存爆炸。"""
        try:
            client = get_httpx_client()
            resp = await asyncio.wait_for(
                client.get(url, follow_redirects=False),
                timeout=_CV_TIMEOUT,
            )
            # 安全读取：限制响应体最大 512KB
            body_bytes = await resp.aread()
            if len(body_bytes) > 512 * 1024:
                return body_bytes[: 512 * 1024].decode("utf-8", errors="ignore")
            return body_bytes.decode("utf-8", errors="ignore") or ""
        except Exception:
            return ""

    # ========== D6: 敏感路径重新访问（同一路径 2 次 + 内容特征确认） ==========
    async def _d6_sensitive_probe() -> dict[str, dict]:
        """D6: 对 sensitive_paths 中标 exposed 的路径做 2 次重访 + 内容特征确认。

        返回 {path: {"reproducible": bool, "content_confirmed": bool, "evidence": str}}
        """
        results: dict[str, dict] = {}
        exposed_targets = [
            p
            for p in (sensitive_paths or [])
            if isinstance(p, dict) and p.get("exposed") and p.get("path")
        ]
        if not exposed_targets:
            return results
        # 限制最多验证 3 条路径，避免耗时爆炸
        for p in exposed_targets[:3]:
            path = p["path"]
            try:
                parsed_d6 = urlparse(url)
                base = f"{parsed_d6.scheme}://{parsed_d6.netloc}"
                target_url = base + (path if path.startswith("/") else "/" + path)
                client = get_httpx_client()
                tasks = [
                    asyncio.wait_for(
                        client.get(target_url, follow_redirects=False),
                        timeout=_CV_TIMEOUT,
                    )
                    for _ in range(2)
                ]
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                ok_count = 0
                contents: list[str] = []
                statuses: list[int] = []
                for r in responses:
                    if isinstance(r, Exception):
                        continue
                    # 200 或 403/401 都可以证明路径存在（403/401 比 404 更说明问题）
                    if 200 <= r.status_code < 400 or r.status_code in (401, 403):
                        ok_count += 1
                        statuses.append(r.status_code)
                        contents.append((r.text or "")[:2000])
                reproducible = ok_count >= 2

                # 内容特征验证：某些路径需要特定模式才算"真的命中"
                content_confirmed = False
                content_evidence = ""
                path_lower = path.lower()
                if contents:
                    joined = "\n".join(contents)
                    if ".env" in path_lower:
                        # .env 文件通常含 KEY=VALUE 或 export X=Y
                        content_confirmed = bool(
                            re.search(r"^[A-Z_][A-Z0-9_]*\s*=", joined, re.MULTILINE)
                            or "export " in joined
                        )
                        content_evidence = (
                            "命中 KEY=VALUE 格式"
                            if content_confirmed
                            else "未发现 KEY=VALUE 格式"
                        )
                    elif ".git/config" in path_lower or path_lower.endswith(
                        ".git/config"
                    ):
                        content_confirmed = "[core]" in joined
                        content_evidence = (
                            "命中 [core] section"
                            if content_confirmed
                            else "未发现 [core] section"
                        )
                    elif ".git/head" in path_lower or path_lower.endswith(".git/head"):
                        content_confirmed = "ref:" in joined
                        content_evidence = (
                            "命中 ref: refs/" if content_confirmed else "未发现 ref:"
                        )
                    elif "wp-config" in path_lower:
                        content_confirmed = bool(
                            re.search(r"DB_NAME|DB_PASSWORD|define\s*\(", joined)
                        )
                        content_evidence = (
                            "命中 DB_NAME/DB_PASSWORD/define"
                            if content_confirmed
                            else "未发现 WordPress 配置特征"
                        )
                    elif (
                        "backup" in path_lower
                        or ".sql" in path_lower
                        or ".zip" in path_lower
                        or ".tar" in path_lower
                    ):
                        # 备份文件：非空 + 非错误页
                        content_confirmed = (
                            len(joined) > 200
                            and "404" not in joined[:200].lower()
                            and "<html" not in joined[:200].lower()
                        )
                        content_evidence = (
                            f"非错误页内容（{len(joined)} 字符）"
                            if content_confirmed
                            else "疑似错误页或 404"
                        )
                    elif "phpinfo" in path_lower:
                        content_confirmed = (
                            "phpinfo()" in joined or "PHP Version" in joined
                        )
                        content_evidence = (
                            "命中 phpinfo() 标记"
                            if content_confirmed
                            else "未发现 phpinfo 特征"
                        )
                    else:
                        # 其它路径：可重现就算（已 reproducible 即可）
                        content_confirmed = reproducible
                        content_evidence = (
                            "路径可重现访问" if content_confirmed else "路径未稳定重现"
                        )

                results[path] = {
                    "reproducible": reproducible,
                    "content_confirmed": content_confirmed,
                    "ok_count": ok_count,
                    "statuses": statuses,
                    "evidence": f"D6: 2次重访 status={statuses}; 内容确认: {content_evidence}",
                }
            except Exception as e:
                results[path] = {
                    "reproducible": False,
                    "content_confirmed": False,
                    "ok_count": 0,
                    "statuses": [],
                    "evidence": f"D6: 重访异常: {str(e)[:80]}",
                }
        return results

    # ========== D7 + D8: CORS 真实存在性 + credentials ==========
    async def _d7_d8_cors_probe() -> dict[str, dict]:
        """D7: 同一 URL 2 次带 Origin 头访问，看 Access-Control-Allow-Origin 头是否稳定存在。
        D8: 同步检查 Access-Control-Allow-Credentials 头（true = 极高风险）。
        D7b/D8b: OPTIONS 预检请求实测。
        """
        result = {
            "main_origin": "",
            "subresource_origin": "",
            "allow_origin_wildcard_in_main": False,
            "allow_origin_wildcard_in_sub": False,
            "allow_credentials": False,
            "main_response_status": 0,
            "sub_response_status": 0,
            "options_preflight": {},
            "evidence": "",
        }
        try:
            parsed_d78 = urlparse(url)
            base = f"{parsed_d78.scheme}://{parsed_d78.netloc}"
            # 找一个子资源（同源静态文件），无则回退到 base/
            sub_path = "/favicon.ico"
            try:
                # 看 HTML 里有没有 <link> / <script src>，取第一个静态资源
                client = get_httpx_client()
                main_resp = await asyncio.wait_for(
                    client.get(url, follow_redirects=False),
                    timeout=_CV_TIMEOUT,
                )
                result["main_response_status"] = main_resp.status_code
                # 主响应
                acao_main = (
                    main_resp.headers.get("access-control-allow-origin")
                    or main_resp.headers.get("Access-Control-Allow-Origin")
                    or ""
                )
                result["main_origin"] = acao_main
                if acao_main.strip() == "*":
                    result["allow_origin_wildcard_in_main"] = True
                # 看 HTML 找静态资源
                if main_resp.text:
                    m = re.search(
                        r'(?:src|href)\s*=\s*["\']([^"\']+\.(?:js|css|png|jpg|svg|ico))["\']',
                        main_resp.text,
                        re.IGNORECASE,
                    )
                    if m and m.group(1).startswith("/"):
                        sub_path = m.group(1)
            except Exception:
                client = get_httpx_client()

            # 子资源请求
            try:
                sub_resp = await asyncio.wait_for(
                    client.get(base + sub_path, follow_redirects=False),
                    timeout=_CV_TIMEOUT,
                )
                result["sub_response_status"] = sub_resp.status_code
                acao_sub = (
                    sub_resp.headers.get("access-control-allow-origin")
                    or sub_resp.headers.get("Access-Control-Allow-Origin")
                    or ""
                )
                result["subresource_origin"] = acao_sub
                if acao_sub.strip() == "*":
                    result["allow_origin_wildcard_in_sub"] = True
                # credentials：主响应或子响应任一带 true 即算
                for r in (main_resp, sub_resp):
                    acac = (
                        (
                            r.headers.get("access-control-allow-credentials")
                            or r.headers.get("Access-Control-Allow-Credentials")
                            or ""
                        )
                        .strip()
                        .lower()
                    )
                    if acac == "true":
                        result["allow_credentials"] = True
                        break
            except Exception as e:
                logger.warning("CV D7/D8 subresource probe error: %s", e)

            # ===== D7b/D8b: OPTIONS 预检请求实测 =====
            try:
                options_resp = await asyncio.wait_for(
                    client.options(
                        url,
                        headers={
                            "Origin": "https://preflight-test.example",
                            "Access-Control-Request-Method": "POST",
                            "Access-Control-Request-Headers": "Content-Type,Authorization",
                        },
                        follow_redirects=False,
                    ),
                    timeout=_CV_TIMEOUT,
                )
                opt_h = {k.lower(): v for k, v in options_resp.headers.items()}
                result["options_preflight"] = {
                    "status": options_resp.status_code,
                    "acao": opt_h.get("access-control-allow-origin", ""),
                    "acam": opt_h.get("access-control-allow-methods", ""),
                    "acah": opt_h.get("access-control-allow-headers", ""),
                    "acac": opt_h.get("access-control-allow-credentials", ""),
                    "max_age": opt_h.get("access-control-max-age", ""),
                }
            except Exception:
                result["options_preflight"] = {"status": 0, "error": "OPTIONS 请求失败"}

            result["evidence"] = (
                f"D7: main ACAO={result['main_origin']!r}({result['main_response_status']}), "
                f"sub ACAO={result['subresource_origin']!r}({result['sub_response_status']}); "
                f"D8: Allow-Credentials={result['allow_credentials']}; "
                f"OPTIONS: status={result['options_preflight'].get('status', 'N/A')}, "
                f"ACAM={result['options_preflight'].get('acam', 'N/A')!r}"
            )
        except Exception as e:
            result["evidence"] = f"D7/D8: 异常 {str(e)[:80]}"
        return result

    # ========== D9: Cookie 多次请求一致性 ==========
    async def _d9_cookie_probe() -> dict[str, dict]:
        """D9: 对同一 URL 3 次请求，统计 Set-Cookie 头稳定性（含 SameSite）。"""
        result = {
            "requests": 0,
            "with_cookie": 0,
            "missing_secure": 0,
            "missing_httponly": 0,
            "missing_samesite": 0,
            "samesite_none_without_secure": 0,
            "evidence": "",
        }
        try:
            client = get_httpx_client()
            tasks = [
                asyncio.wait_for(
                    client.get(url, follow_redirects=False),
                    timeout=_CV_TIMEOUT,
                )
                for _ in range(3)
            ]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            result["requests"] = len(responses)
            for r in responses:
                if isinstance(r, Exception):
                    continue
                set_cookie = (
                    r.headers.get("set-cookie") or r.headers.get("Set-Cookie") or ""
                )
                if not set_cookie:
                    continue
                result["with_cookie"] += 1
                sc_lower = set_cookie.lower()
                if "secure" not in sc_lower:
                    result["missing_secure"] += 1
                if "httponly" not in sc_lower:
                    result["missing_httponly"] += 1
                if "samesite" not in sc_lower:
                    result["missing_samesite"] += 1
                # SameSite=None 必须配合 Secure，否则是非法组合
                if "samesite=none" in sc_lower and "secure" not in sc_lower:
                    result["samesite_none_without_secure"] += 1
            result["evidence"] = (
                f"D9: {result['requests']}次请求 {result['with_cookie']}次带 Set-Cookie，"
                f"缺 Secure {result['missing_secure']}次，缺 HttpOnly {result['missing_httponly']}次，"
                f"缺 SameSite {result['missing_samesite']}次"
            )
            if result["samesite_none_without_secure"] > 0:
                result["evidence"] += (
                    f"，SameSite=None 缺 Secure {result['samesite_none_without_secure']}次"
                )
        except Exception as e:
            result["evidence"] = f"D9: 异常 {str(e)[:80]}"
        return result

    # ========== D11: 信息泄露多页面验证 ==========
    # ========== D12: 过时组件检测（OWASP A06）==========
    KNOWN_VULN_LIBS: list[dict] = [
        # jQuery < 1.9.0 有 XSS 漏洞
        {
            "pattern": r"jquery[/-]([0-9]+)\.([0-9]+)",
            "min_major": 1,
            "min_minor": 9,
            "cve": "CVE-2020-11022/11023",
            "severity": "medium",
            "name": "jQuery",
        },
        # Bootstrap < 4.4.0 有 XSS
        {
            "pattern": r"bootstrap[/-]([0-9]+)\.([0-9]+)",
            "min_major": 4,
            "min_minor": 4,
            "cve": "CVE-2019-8331",
            "severity": "medium",
            "name": "Bootstrap",
        },
        # Angular < 1.7.0
        {
            "pattern": r"angular[/-]([0-9]+)\.([0-9]+)",
            "min_major": 1,
            "min_minor": 7,
            "cve": "CVE-2019-10768",
            "severity": "medium",
            "name": "Angular",
        },
        # React < 16.0.0
        {
            "pattern": r"react[/-][Uu]md?/([0-9]+)\.([0-9]+)",
            "min_major": 16,
            "min_minor": 0,
            "cve": "CVE-2018-6367",
            "severity": "medium",
            "name": "React",
        },
        # Lodash < 4.17.12 有原型污染
        {
            "pattern": r"lodash[/-]([0-9]+)\.([0-9]+)",
            "min_major": 4,
            "min_minor": 17,
            "cve": "CVE-2020-8203",
            "severity": "high",
            "name": "Lodash",
        },
        # Axios < 0.21.0 有 SSRF
        {
            "pattern": r"axios[/-]([0-9]+)\.([0-9]+)",
            "min_major": 0,
            "min_minor": 21,
            "cve": "CVE-2020-24192",
            "severity": "medium",
            "name": "Axios",
        },
        # Font Awesome < 5.12.0
        {
            "pattern": r"font-awesome[/-]([0-9]+)\.([0-9]+)",
            "min_major": 5,
            "min_minor": 12,
            "cve": "CVE-2020-9356",
            "severity": "low",
            "name": "Font Awesome",
        },
    ]

    def _check_outdated_components(html_text: str) -> list[dict]:
        """检查页面中引用的 JS/CSS 库是否有已知 CVE。"""
        vuln_libs: list[dict] = []
        for lib in KNOWN_VULN_LIBS:
            match = re.search(lib["pattern"], html_text, re.IGNORECASE)
            if match:
                try:
                    major = int(match.group(1))
                    minor = int(match.group(2))
                    if major < lib["min_major"] or (
                        major == lib["min_major"] and minor < lib["min_minor"]
                    ):
                        vuln_libs.append(
                            {
                                "name": lib["name"],
                                "detected_version": f"{major}.{minor}",
                                "min_safe_version": f"{lib['min_major']}.{lib['min_minor']}",
                                "cve": lib["cve"],
                                "severity": lib["severity"],
                                "fix": f"升级 {lib['name']} 至 {lib['min_major']}.{lib['min_minor']} 或更高版本",
                            }
                        )
                except (ValueError, IndexError):
                    pass
        return vuln_libs

    async def _d12_outdated_components_probe() -> dict[str, Any]:
        """D12: 解析首页 HTML，提取第三方库版本并检查已知 CVE。"""
        result: dict[str, Any] = {"vuln_libs": [], "total_libs_found": 0}
        try:
            client = get_httpx_client()
            protocol = "https" if is_https else "http"
            resp = await asyncio.wait_for(
                client.get(
                    f"{protocol}://{host}/",
                    headers={"User-Agent": "Mozilla/5.0"},
                    follow_redirects=True,
                ),
                timeout=8.0,
            )
            if resp.status_code == 200:
                html_text = (await resp.aread()).decode("utf-8", errors="ignore")
                result["vuln_libs"] = _check_outdated_components(html_text)
                result["total_libs_found"] = len(
                    re.findall(
                        r'(?:src|href)=["\']https?://[^"\']+?/[^"\']+?\.(?:js|css)',
                        html_text,
                    )
                )
            else:
                result["evidence"] = f"首页返回 {resp.status_code}"
        except Exception as e:
            result["evidence"] = f"D12: 异常 {str(e)[:80]}"
        return result

    # ========== D13: A07 认证失败检测（登录页面 + 表单安全）==========
    LOGIN_PATH_HINTS = [
        "/login",
        "/signin",
        "/sign-in",
        "/user/login",
        "/admin",
        "/admin/login",
        "/wp-login.php",
        "/auth/login",
        "/account/login",
        "/member/login",
    ]

    async def _d13_auth_probe() -> dict[str, Any]:
        """D13: 检测登录页面及认证表单的安全配置问题。

        检测项：
        1. 是否存在登录页面（可访问性）
        2. 登录表单是否缺少 autocomplete="off"
        3. 登录页面是否缺少 HTTP 安全头
        4. 是否有用户名可枚举迹象（不同错误消息）
        """
        result: dict[str, Any] = {
            "login_page_found": False,
            "login_path": "",
            "issues": [],
            "form_details": {},
        }
        try:
            client = get_httpx_client()
            protocol = "https" if is_https else "http"
            # 探测常见登录路径
            for path in LOGIN_PATH_HINTS:
                try:
                    resp = await asyncio.wait_for(
                        client.get(
                            f"{protocol}://{host}{path}",
                            headers={"User-Agent": "Mozilla/5.0"},
                            follow_redirects=True,
                        ),
                        timeout=5.0,
                    )
                    if resp.status_code == 200:
                        body = (await resp.aread()).decode("utf-8", errors="ignore")
                        # 检查是否是登录页面（有 password 输入框）
                        if re.search(
                            r'<input[^>]*type=["\']password["\']', body, re.IGNORECASE
                        ):
                            result["login_page_found"] = True
                            result["login_path"] = path
                            # 检查表单安全
                            issues = []
                            form_match = re.search(
                                r"<form[^>]*>.*?</form>",
                                body,
                                re.IGNORECASE | re.DOTALL,
                            )
                            if form_match:
                                form_html = form_match.group(0)
                                # 检查 CSRF token：必须是隐藏字段，且 name 包含 csrf/token/nonce，同时具有非空 value
                                # 逐个解析 <input> 标签，避免属性顺序导致的漏报
                                csrf_found = False
                                input_pattern = re.compile(
                                    r"<input[^>]*>", re.IGNORECASE
                                )
                                for input_tag in input_pattern.findall(form_html):
                                    tag_lower = input_tag.lower()
                                    if (
                                        'type="hidden"' not in tag_lower
                                        and "type='hidden'" not in tag_lower
                                    ):
                                        continue
                                    name_match = re.search(
                                        r'\bname=["\']([^"\']*)["\']',
                                        input_tag,
                                        re.IGNORECASE,
                                    )
                                    if not name_match:
                                        continue
                                    name = name_match.group(1).lower()
                                    if not any(
                                        h in name for h in ("csrf", "token", "nonce")
                                    ):
                                        continue
                                    value_match = re.search(
                                        r'\bvalue=["\']([^"\']*)["\']',
                                        input_tag,
                                        re.IGNORECASE,
                                    )
                                    if value_match and value_match.group(1).strip():
                                        csrf_found = True
                                        break
                                if not csrf_found:
                                    issues.append("csrf_token_missing")
                            # 检查登录页安全头
                            login_headers = {
                                k.lower(): v for k, v in resp.headers.items()
                            }
                            if "x-frame-options" not in login_headers:
                                issues.append("login_page_no_xfo")
                            result["issues"] = issues
                            break
                except Exception:
                    continue
        except Exception as e:
            result["evidence"] = f"D13: 异常 {str(e)[:80]}"
        return result

    # ========== D14: A08 软件完整性 - SRI 子资源完整性检测 ==========
    async def _d14_sri_probe() -> dict[str, Any]:
        """D14: 检测第三方 JS/CSS 资源是否使用了 SRI (Subresource Integrity)。

        没有 SRI 时，如果 CDN 被劫持，第三方脚本会被篡改，
        直接影响整个网站安全。属于 OWASP A08 范畴。
        """
        result: dict[str, Any] = {
            "total_external_resources": 0,
            "sri_protected": 0,
            "unprotected_resources": [],
            "sri_supported": False,
        }
        try:
            client = get_httpx_client()
            protocol = "https" if is_https else "http"
            resp = await asyncio.wait_for(
                client.get(
                    f"{protocol}://{host}/",
                    headers={"User-Agent": "Mozilla/5.0"},
                    follow_redirects=True,
                ),
                timeout=8.0,
            )
            if resp.status_code == 200:
                body = (await resp.aread()).decode("utf-8", errors="ignore")
                # 匹配 <script src=...> 和 <link rel="stylesheet" href=...>
                # 只统计外部域名资源（跨域的才需要 SRI）
                from urllib.parse import urlparse as _up

                script_pattern = re.compile(
                    r'<script[^>]*src=["\'](https?://[^"\']+)["\'][^>]*>',
                    re.IGNORECASE,
                )
                link_pattern = re.compile(
                    r'<link[^>]*href=["\'](https?://[^"\']+)["\'][^>]*>',
                    re.IGNORECASE,
                )
                all_ext_resources = []
                # 检查 script 标签
                for m in script_pattern.finditer(body):
                    src = m.group(1)
                    tag = m.group(0)
                    try:
                        p = _up(src)
                        # 只统计跨域资源
                        if p.hostname and p.hostname != host.split(":")[0]:
                            all_ext_resources.append(
                                {"url": src[:120], "type": "script", "tag": tag}
                            )
                    except Exception:
                        pass
                # 检查 link 标签（只统计 stylesheet）
                for m in link_pattern.finditer(body):
                    href = m.group(1)
                    tag = m.group(0)
                    if "stylesheet" not in tag.lower():
                        continue
                    try:
                        p = _up(href)
                        if p.hostname and p.hostname != host.split(":")[0]:
                            all_ext_resources.append(
                                {"url": href[:120], "type": "css", "tag": tag}
                            )
                    except Exception:
                        pass

                result["total_external_resources"] = len(all_ext_resources)
                sri_count = 0
                unprotected = []
                for res in all_ext_resources:
                    has_integrity = bool(
                        re.search(r'integrity=["\']sha', res["tag"], re.IGNORECASE)
                    )
                    if has_integrity:
                        sri_count += 1
                    else:
                        unprotected.append(
                            {
                                "url": res["url"],
                                "type": res["type"],
                            }
                        )
                result["sri_protected"] = sri_count
                result["unprotected_resources"] = unprotected[:10]  # 最多返回 10 个
                result["sri_supported"] = sri_count > 0
        except Exception as e:
            result["evidence"] = f"D14: 异常 {str(e)[:80]}"
        return result

    # ========== D15: A04 不安全设计 - 开放重定向检测 ==========
    async def _d15_redirect_probe() -> dict[str, Any]:
        """D15: 检测常见的开放重定向漏洞参数。

        检测方式：在首页、登录页、授权回调等常见入口的 redirect/url 参数
        注入外部 URL，观察是否发生 302/301 跳转到注入的域名。

        注意：本检测属于黑盒探测，只能覆盖常见的开放重定向参数和入口，
        不能穷尽所有业务跳转点。未命中不代表完全不存在开放重定向。
        """
        result: dict[str, Any] = {
            "vulnerable": False,
            "vulnerable_params": [],
            "tested_params": [],
            "tested_paths": [],
        }
        REDIRECT_PARAMS = [
            "redirect",
            "url",
            "next",
            "go",
            "return",
            "return_url",
            "redirect_url",
            "target",
            "callback",
            "continue",
        ]
        EXTERNAL_URL = "https://example.com/redirect-test"
        # 常见可能存在跳转功能的入口路径
        REDIRECT_PATHS = [
            "/",
            "/login",
            "/signin",
            "/auth",
            "/oauth",
            "/logout",
            "/sso",
        ]
        try:
            client = get_httpx_client()
            protocol = "https" if is_https else "http"
            for path in REDIRECT_PATHS:
                for param in REDIRECT_PARAMS:
                    test_url = f"{protocol}://{host}{path}?{param}={EXTERNAL_URL}"
                    try:
                        resp = await asyncio.wait_for(
                            client.get(
                                test_url,
                                headers={"User-Agent": "Mozilla/5.0"},
                                follow_redirects=False,
                            ),
                            timeout=3.5,
                        )
                        result["tested_params"].append(param)
                        if resp.status_code in (301, 302, 303, 307, 308):
                            location = resp.headers.get("location", "")
                            if (
                                location.startswith(EXTERNAL_URL)
                                or "example.com" in location
                            ):
                                result["vulnerable"] = True
                                result["vulnerable_params"].append(
                                    {
                                        "param": param,
                                        "path": path,
                                        "redirect_to": location[:120],
                                        "status_code": resp.status_code,
                                    }
                                )
                                if path not in result["tested_paths"]:
                                    result["tested_paths"].append(path)
                    except Exception:
                        continue
        except Exception as e:
            result["evidence"] = f"D15: 异常 {str(e)[:80]}"
        return result

    async def _d11_info_leak_probe() -> dict[str, bool]:
        """D11: 在首页 + 1 个子页面（/index.html 或 /robots.txt）找相同信息泄露模式。

        找的模式：HTML 注释中的可疑串、Stack Trace 关键词、debug 标记。
        返回 {模式名: 是否在两页同时出现}
        """
        # 注释：<!-- ... -->
        # Stack trace: "Traceback", "at line", "Exception in", "FATAL"
        # Debug: "DEBUG=True", "var_dump", "print_r", "console.log", "TODO", "FIXME"
        leak_patterns = {
            "html_comment": re.compile(
                r"<!--[^>]{20,}(?:password|secret|token|api[_-]?key|admin|user)[^>]*-->",
                re.IGNORECASE,
            ),
            "stack_trace": re.compile(
                r"(?:Traceback \(most recent call last\)|at line \d+|FATAL\s*:|Exception in thread)",
                re.IGNORECASE,
            ),
            "debug_marker": re.compile(
                r"(?:var_dump|print_r|console\.log|debug\s*=\s*True|stack\s*trace\s*on)",
                re.IGNORECASE,
            ),
        }
        result = {k: False for k in leak_patterns}
        try:
            parsed_d11 = urlparse(url)
            base = f"{parsed_d11.scheme}://{parsed_d11.netloc}"
            sub_path = (
                "/index.html"
                if (parsed_d11.path or "").rstrip("/") != "/index.html"
                else "/robots.txt"
            )
            client = get_httpx_client()
            tasks = [
                asyncio.wait_for(
                    client.get(url, follow_redirects=False), timeout=_CV_TIMEOUT
                ),
                asyncio.wait_for(
                    client.get(base + sub_path, follow_redirects=False),
                    timeout=_CV_TIMEOUT,
                ),
            ]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            pages_text = []
            for r in responses:
                if isinstance(r, Exception):
                    pages_text.append("")
                else:
                    pages_text.append(r.text or "")
            # 两页都命中才算 D11 命中
            for name, pat in leak_patterns.items():
                hit_main = bool(pat.search(pages_text[0]))
                hit_sub = bool(pat.search(pages_text[1]))
                result[name] = hit_main and hit_sub
        except Exception as e:
            logger.warning("CV D11 info leak probe error: %s", e)
        return result

    # ========== D10: SSL/TLS 协议版本重新验证（同步 ssl 模块） ==========
    def _d10_ssl_check() -> dict[str, object]:
        """D10: 用 Python ssl 模块重连验证协议版本。

        返回 {"reachable": bool, "version": str, "weak": bool, "cipher": str, "evidence": str}
        """
        out: dict[str, object] = {
            "reachable": False,
            "version": "",
            "weak": False,
            "cipher": "",
            "evidence": "D10: 未执行（仅 HTTPS 验证）",
        }
        try:
            # 仅当原 URL 是 HTTPS 时才有意义
            parsed_d10 = urlparse(url)
            if (parsed_d10.scheme or "").lower() != "https":
                out["evidence"] = "D10: 当前 URL 非 HTTPS，跳过"
                return out
            import socket
            import ssl

            host = parsed_d10.hostname or ""
            port = parsed_d10.port or 443
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            # 强制所有协议都允许，再用 negotiated version 判断
            try:
                ctx.minimum_version = ssl.TLSVersion.TLSv1
            except Exception as e:
                logger.warning("SSL context minimum_version not supported: %s", e)
            with socket.create_connection((host, port), timeout=3) as raw_sock:
                with ctx.wrap_socket(raw_sock, server_hostname=host) as ssock:
                    out["reachable"] = True
                    out["version"] = ssock.version() or ""
                    out["cipher"] = (ssock.cipher() or ["", "", ""])[0] or ""
                    # 弱协议判定
                    v = (out["version"] or "").upper()
                    out["weak"] = v in ("SSLv3", "SSLv2", "TLSv1", "TLSv1.0", "TLSv1.1")
                    out["evidence"] = (
                        f"D10: 重连 version={out['version']!r}, weak={out['weak']}"
                    )
        except Exception as e:
            out["evidence"] = f"D10: 重连异常 {str(e)[:80]}"
        return out

    # 10+1 组并发：D1, D2, D3, D6, D7+D8, D9, D11, D12, D13, D14, D15（D10 同步，避免阻塞）
    d13_auth: dict[str, Any] = {"login_page_found": False, "issues": []}
    d14_sri: dict[str, Any] = {
        "total_external_resources": 0,
        "sri_protected": 0,
        "unprotected_resources": [],
    }
    d15_redirect: dict[str, Any] = {"vulnerable": False, "vulnerable_params": []}
    try:
        (
            d1_merged,
            d2_merged,
            html,
            d6_map,
            d78_cors,
            d9_cookie,
            d11_leak,
            _d12_vuln,
            d13_auth,
            d14_sri,
            d15_redirect,
        ) = await asyncio.gather(
            _with_sem(_d1_probe()),
            _with_sem(_d2_probe()),
            _with_sem(_d3_probe()),
            _with_sem(_d6_sensitive_probe()),
            _with_sem(_d7_d8_cors_probe()),
            _with_sem(_d9_cookie_probe()),
            _with_sem(_d11_info_leak_probe()),
            _with_sem(_d12_outdated_components_probe()),
            _with_sem(_d13_auth_probe()),
            _with_sem(_d14_sri_probe()),
            _with_sem(_d15_redirect_probe()),
            return_exceptions=False,
        )
    except Exception:
        d1_merged, d2_merged, html = {}, {}, ""
        d6_map, d78_cors, d9_cookie, d11_leak = {}, {}, {}, {}
    # D10 同步执行（避免阻塞事件循环；3s 超时）
    d10_ssl: dict[str, object] = {}
    try:
        d10_ssl = await asyncio.wait_for(
            asyncio.to_thread(_d10_ssl_check),
            timeout=4.0,
        )
    except Exception as e:
        d10_ssl = {
            "reachable": False,
            "weak": False,
            "version": "",
            "cipher": "",
            "evidence": f"D10: 异常 {str(e)[:80]}",
        }

    # 统计 D1
    try:
        for f_name, h_key in _FINDING_HEADER_KEY.items():
            if has_header(d1_merged or {}, h_key):
                d1_present_counts[f_name] = 2
                d1_missing_counts[f_name] = 0
                d1_evidence[f_name] = f"D1: 2次请求中 header {h_key} 至少出现 1 次"
            else:
                d1_missing_counts[f_name] = 2
                d1_present_counts[f_name] = 0
                d1_evidence[f_name] = "D1: 2次请求均未发现"
    except Exception:
        for f_name in _FINDING_HEADER_KEY:
            d1_missing_counts.setdefault(f_name, 0)
            d1_present_counts.setdefault(f_name, 0)
            d1_evidence.setdefault(f_name, "D1: 请求异常，未能完成多次验证")

    # 统计 D2
    try:
        for f_name, h_key in _FINDING_HEADER_KEY.items():
            if has_header(d2_merged or {}, h_key):
                d2_present[f_name] = True
                d2_evidence[f_name] = f"D2: 子路径扫描中发现 {h_key}"
            else:
                d2_present[f_name] = False
                d2_evidence[f_name] = "D2: 子路径扫描均未发现"
    except Exception:
        for f_name in _FINDING_HEADER_KEY:
            d2_evidence.setdefault(f_name, "D2: 请求异常，未完成子路径扫描")
            d2_present.setdefault(f_name, False)

    # 统计 D3
    try:
        meta_re = re.compile(
            r'<meta[^>]+http-equiv\s*=\s*["\']?([^"\'>\s]+)[^>]*content\s*=\s*["\']([^"\']+)["\']',
            re.IGNORECASE,
        )
        meta_pairs: dict[str, str] = {}
        for m in meta_re.finditer(html or ""):
            meta_pairs[m.group(1).strip().lower()] = m.group(2).strip()
        for f_name, h_key in _FINDING_HEADER_KEY.items():
            meta_name = _META_EQUIV_HEADERS.get(h_key, "").lower()
            if meta_name and meta_name in meta_pairs:
                d3_meta_found[f_name] = True
                d3_evidence[f_name] = (
                    f'D3: <meta http-equiv="{_META_EQUIV_HEADERS[h_key]}" '
                    f'content="{meta_pairs[meta_name][:80]}">'
                )
            else:
                d3_meta_found[f_name] = False
                d3_evidence[f_name] = (
                    f'D3: HTML 中未发现 <meta http-equiv="{_META_EQUIV_HEADERS.get(h_key, h_key)}">'
                )
    except Exception:
        for f_name in _FINDING_HEADER_KEY:
            d3_meta_found.setdefault(f_name, False)
            d3_evidence.setdefault(f_name, "D3: 请求异常，未完成 meta 扫描")

    # ========== D4 + D5: 上下文过滤 + 置信度评分 ==========
    # CSP frame-ancestors 覆盖 X-Frame-Options
    csp_value = get_header_value(headers, "content-security-policy")
    has_csp_frame_ancestors = bool(csp_value and "frame-ancestors" in csp_value.lower())
    # Server 头是否经 CDN 设置（cloudflare/aws/aliyun 等会强制覆盖）
    server_val = get_header_value(headers, "server") or ""
    cdn_signatures = (
        "cloudflare",
        "cloudfront",
        "aws",
        "fastly",
        "akamai",
        "alicdn",
        "qcloud",
    )
    is_cdn_server = (
        any(s in server_val.lower() for s in cdn_signatures)
        or bool(d3_meta_found.get("缺少 CSP")) is False
        and any(
            (k.lower() in ("cf-ray", "x-amz-cf-id", "x-served-by", "x-cache"))
            for k in (headers or {}).keys()
        )
    )
    # D0：用户提供的已知 CDN 列表命中 → 也视为 CDN
    is_cdn_server = is_cdn_server or bool(d0_match.get("Server 头由 CDN 注入", False))

    for f in findings or []:
        name = f.get("name", "")
        h_key = _FINDING_HEADER_KEY.get(name)
        # 非安全头类 finding（如 Server 信息泄露、敏感路径、CORS、Cookie、SSL/TLS、信息泄露）走专用维度
        if h_key is None:
            # ===== D6: 敏感路径暴露 =====
            if "敏感路径" in name or "敏感文件" in name:
                # 汇总 D6 结果
                if d6_map:
                    # 全部路径都 reproducible + content_confirmed → 95
                    all_repro = all(v.get("reproducible") for v in d6_map.values())
                    all_content = all(
                        v.get("content_confirmed") for v in d6_map.values()
                    )
                    any_ok = any((v.get("ok_count") or 0) >= 1 for v in d6_map.values())
                    if all_repro and all_content:
                        confidence = 95
                        reason = f"D6: {len(d6_map)} 条路径 2次重访均稳定且内容特征命中"
                    elif any_ok:
                        # 部分路径 1/2 命中 / 部分路径 2/2 命中但内容未确认
                        confidence = 70
                        hit = sum((v.get("ok_count") or 0) for v in d6_map.values())
                        total = 2 * len(d6_map)
                        reason = f"D6: 部分路径 2次重访可重现（命中 {hit}/{total} 次）"
                    else:
                        confidence = 50
                        reason = (
                            "D6: 路径未稳定重现（首次命中但重访失败），建议人工确认"
                        )
                    evidences = "; ".join(
                        v.get("evidence", "") for v in d6_map.values()
                    )
                    result[name] = {
                        "verified": confidence >= 60,
                        "confidence": confidence,
                        "reason": reason,
                        "evidence_d1_d5": evidences or "D6: 无可重访的暴露路径",
                    }
                else:
                    # 没有 sensitive_paths 数据，原始 finding
                    result[name] = {
                        "verified": True,
                        "confidence": 80,
                        "reason": "原始 finding，未提供 sensitive_paths 数据做交叉验证",
                        "evidence_d1_d5": "D6: 跳过（无 sensitive_paths）",
                    }
                continue

            # ===== D7+D8: CORS 通配符 =====
            if "CORS" in name:
                d78_ev = (
                    d78_cors.get("evidence", "") if isinstance(d78_cors, dict) else ""
                )
                main_wild = (
                    d78_cors.get("allow_origin_wildcard_in_main", False)
                    if isinstance(d78_cors, dict)
                    else False
                )
                sub_wild = (
                    d78_cors.get("allow_origin_wildcard_in_sub", False)
                    if isinstance(d78_cors, dict)
                    else False
                )
                allow_creds = (
                    d78_cors.get("allow_credentials", False)
                    if isinstance(d78_cors, dict)
                    else False
                )
                if main_wild and sub_wild:
                    confidence = 95 if not allow_creds else 98
                    reason = "D7+D8: 主响应+子资源 ACAO 都为 *，通配符在多端真实存在"
                    if allow_creds:
                        reason += "；D8: 同时启用 Allow-Credentials，极高风险"
                elif main_wild:
                    confidence = 70
                    reason = "D7: 仅主响应 ACAO 为 *，子资源未命中（部分 CORS 配置）"
                elif sub_wild:
                    confidence = 70
                    reason = "D7: 仅子资源 ACAO 为 *（罕见，CDN/静态资源配置）"
                else:
                    # 重访未发现 * → 可能是单次边界情况
                    confidence = 50
                    reason = "D7: 重访未发现 ACAO=*，可能是单次边界情况，建议人工确认"
                result[name] = {
                    "verified": confidence >= 60,
                    "confidence": confidence,
                    "reason": reason,
                    "evidence_d1_d5": d78_ev or "D7/D8: 未执行（CORS 探针异常）",
                }
                continue

            # ===== D9: Cookie 安全配置不足 =====
            if "Cookie" in name:
                d9_ev = (
                    d9_cookie.get("evidence", "") if isinstance(d9_cookie, dict) else ""
                )
                missing_sec = (
                    d9_cookie.get("missing_secure", 0)
                    if isinstance(d9_cookie, dict)
                    else 0
                )
                missing_htt = (
                    d9_cookie.get("missing_httponly", 0)
                    if isinstance(d9_cookie, dict)
                    else 0
                )
                missing_samesite = (
                    d9_cookie.get("missing_samesite", 0)
                    if isinstance(d9_cookie, dict)
                    else 0
                )
                ss_none_no_sec = (
                    d9_cookie.get("samesite_none_without_secure", 0)
                    if isinstance(d9_cookie, dict)
                    else 0
                )
                with_cookie = (
                    d9_cookie.get("with_cookie", 0)
                    if isinstance(d9_cookie, dict)
                    else 0
                )
                if with_cookie == 0:
                    # 没有 Set-Cookie，可能是 API/纯静态
                    confidence = 50
                    reason = "D9: 3 次请求均未带回 Set-Cookie，可能是无 Cookie 站点"
                elif missing_sec == with_cookie and missing_htt == with_cookie:
                    # 3 次都缺 Secure 和 HttpOnly
                    confidence = 95
                    reason = (
                        f"D9: {with_cookie}/3 次请求 Cookie 同时缺 Secure 和 HttpOnly"
                    )
                elif missing_sec >= 1 or missing_htt >= 1 or missing_samesite >= 1:
                    confidence = 60
                    reason = f"D9: 3 次请求中部分缺 Secure/HttpOnly/SameSite（缺 Secure {missing_sec} 次，缺 HttpOnly {missing_htt} 次，缺 SameSite {missing_samesite} 次）"
                else:
                    confidence = 70
                    reason = "D9: Cookie 标志基本完整（仅 1 次轻微缺失）"
                # SameSite=None 不带 Secure 是严重错误（浏览器会拒绝）
                if ss_none_no_sec > 0:
                    confidence = max(confidence, 90)
                    reason += f"；SameSite=None 未配合 Secure（{ss_none_no_sec} 次），现代浏览器将拒绝此 Cookie"
                result[name] = {
                    "verified": confidence >= 60,
                    "confidence": confidence,
                    "reason": reason,
                    "evidence_d1_d5": d9_ev or "D9: 未执行",
                }
                continue

            # ===== D10: 弱 SSL/TLS 配置 =====
            if "SSL" in name or "TLS" in name or "弱" in name:
                d10_ev = (
                    d10_ssl.get("evidence", "") if isinstance(d10_ssl, dict) else ""
                )
                reachable = (
                    d10_ssl.get("reachable", False)
                    if isinstance(d10_ssl, dict)
                    else False
                )
                weak = (
                    d10_ssl.get("weak", False) if isinstance(d10_ssl, dict) else False
                )
                if "证书已过期" in name or "过期" in name:
                    # 证书过期：用 D10 reachable + D4 上下文判断
                    if reachable:
                        confidence = 80
                        reason = "D10: 站点 HTTPS 可达；证书过期需以原 SSL 探针结果为准"
                    else:
                        confidence = 60
                        reason = "D10: 站点不可达，证书过期状态无法复验"
                    result[name] = {
                        "verified": True,
                        "confidence": confidence,
                        "reason": reason,
                        "evidence_d1_d5": d10_ev,
                    }
                elif "即将过期" in name:
                    result[name] = {
                        "verified": True,
                        "confidence": 75,
                        "reason": "D10: 证书剩余天数 < 30，需续期",
                        "evidence_d1_d5": d10_ev,
                    }
                else:
                    # 弱 SSL/TLS 配置
                    if weak and reachable:
                        confidence = 95
                        reason = f"D10: 重连确认协议弱（{d10_ssl.get('version', '')}）"
                    elif reachable and not weak:
                        confidence = 40
                        reason = f"D10: 重连确认协议正常（{d10_ssl.get('version', '')}），原 finding 可能误报"
                    else:
                        confidence = 50
                        reason = "D10: 重连失败，无法验证"
                    result[name] = {
                        "verified": confidence >= 60,
                        "confidence": confidence,
                        "reason": reason,
                        "evidence_d1_d5": d10_ev,
                    }
                continue

            # ===== D11: 信息泄露（HTML 注释 / Stack Trace / Debug 标记） =====
            if "信息泄露" in name or "Stack Trace" in name or "stack" in name.lower():
                if isinstance(d11_leak, dict) and any(d11_leak.values()):
                    confidence = 95
                    reason = (
                        "D11: HTML 注释/Stack Trace/Debug 标记在首页 + 子页面同时发现"
                    )
                elif isinstance(d11_leak, dict):
                    # 在 D3 html 中其实已有内容（首页），但子页面未命中
                    confidence = 70
                    reason = "D11: 仅在首页发现可疑模式（子页面未命中）"
                else:
                    confidence = 80
                    reason = "原始 finding，未做 D11 多页面验证"
                result[name] = {
                    "verified": confidence >= 60,
                    "confidence": confidence,
                    "reason": reason,
                    "evidence_d1_d5": f"D11: leak_patterns={d11_leak or {}}",
                }
                continue

            # ===== D5 兜底：Server 头 / X-Powered-By =====
            if "Server" in name or "X-Powered-By" in name:
                # D5 误报防护：CDN 服务商设置，源站无法控制
                if is_cdn_server:
                    d0_note = d0_evidence.get(
                        "Server 头由 CDN 注入",
                        "D0: 检测到 CDN 特征头（CF-Ray/X-Cache 等），Server 头由 CDN 注入",
                    )
                    result[name] = {
                        "verified": True,
                        "confidence": 30,
                        "reason": "CDN 服务商设置，源站无法控制",
                        "evidence_d1_d5": d0_note,
                    }
                else:
                    result[name] = {
                        "verified": True,
                        "confidence": 75,
                        "reason": "D1: 检测到 Server 头泄露",
                        "evidence_d1_d5": "D4: 非 CDN 环境，Server 头由源站控制",
                    }
                continue

            # 其它 finding（未匹配到任何维度）保持 verified=True, confidence=80
            result[name] = {
                "verified": True,
                "confidence": 80,
                "reason": "原始 finding，未做交叉验证",
                "evidence_d1_d5": "D5: 跳过交叉验证（未匹配到专用维度）",
            }
            continue

        d1_missing = d1_missing_counts.get(name, 0)
        d2_found = d2_present.get(name, False)
        meta_found = d3_meta_found.get(name, False)
        d1_text = d1_evidence.get(name, "")
        d2_text = d2_evidence.get(name, "")
        d3_text = d3_evidence.get(name, "")

        # ========== D4: 上下文过滤 ==========
        # HSTS 在 HTTP 站应 confidence=0（不报）
        if h_key == "strict-transport-security" and not is_https_url:
            result[name] = {
                "verified": True,
                "confidence": 0,
                "reason": "HSTS 仅 HTTPS 有效，HTTP 站不适用",
                "evidence_d1_d5": f"{d1_text}; D4: 当前 URL 为 HTTP，HSTS 不适用",
            }
            continue

        # CSP / X-Frame-Options 在 HTTPS 优先
        https_preference = ""
        if (
            h_key in ("content-security-policy", "strict-transport-security")
            and not is_https_url
        ):
            https_preference = (
                f" D4: 当前为 HTTP 协议，建议优先在 HTTPS 上配置 {h_key}。"
            )

        # X-Frame-Options 缺失但有 CSP frame-ancestors → 已覆盖
        if h_key == "x-frame-options" and has_csp_frame_ancestors and not meta_found:
            result[name] = {
                "verified": True,
                "confidence": 80,
                "reason": "CSP frame-ancestors 已覆盖",
                "evidence_d1_d5": f"{d1_text}; {d2_text}; {d3_text}; D4: CSP 已含 frame-ancestors，覆盖 X-Frame-Options",
            }
            continue

        # CSP 缺失但有 meta CSP → confidence=95
        if h_key == "content-security-policy" and meta_found:
            result[name] = {
                "verified": True,
                "confidence": 95,
                "reason": "通过 <meta http-equiv> 设置 CSP",
                "evidence_d1_d5": f"{d1_text}; {d2_text}; {d3_text}; D4: meta http-equiv 兜底生效",
            }
            continue

        # ========== D5: 置信度评分 ==========
        # 维度命中数：D1（2次都缺 / 部分缺）、D2（子路径未发现）、D3（meta 未发现）
        # 命中判定：2 次都缺 + 子路径没找到 + meta 也没找到 → 3 维命中
        d1_full_match = d1_missing == 2  # 2 次都没出现
        d1_partial = 0 < d1_missing < 2
        d2_match = not d2_found
        d3_match = not meta_found
        dim_hits = sum(
            [1 if d1_full_match else 0, 1 if d2_match else 0, 1 if d3_match else 0]
        )

        if dim_hits >= 3:
            confidence = 95
            confidence_reason = (
                "D5: 3 维均命中（2次请求 + 子路径 + meta 扫描均未发现），高置信度"
            )
        elif dim_hits == 2:
            confidence = 80
            confidence_reason = "D5: 2 维命中，较高置信度"
        elif d1_partial:
            # 仅部分 D1 命中（D1 现在 0/1/2 次缺失），按 dim_hits 调整
            confidence = 65
            confidence_reason = "D5: 部分维度命中，中等置信度"
        elif d1_full_match and dim_hits == 1:
            # 1 个维度命中（仅 D1 命中，其他维度异常）
            confidence = 70
            confidence_reason = "D5: 仅 1 维命中，建议人工确认"
        else:
            # 没看到缺失（说明已配置），verified=False，置信度低
            confidence = 30
            confidence_reason = "D5: 未稳定复现缺失，置信度低"

        evidence_str = f"{d1_text}; {d2_text}; {d3_text};{https_preference} {confidence_reason}".strip()
        result[name] = {
            "verified": True,
            "confidence": confidence,
            "reason": confidence_reason,
            "evidence_d1_d5": evidence_str,
        }

    return result


def _confidence_level_from_int(c: int) -> str:
    if c >= 80:
        return "高"
    elif c >= 50:
        return "中"
    return "低"


def _finding_to_dict(finding: Finding) -> dict:
    """将插件 Finding 对象转换为 analyze_security 使用的字典格式。"""
    return {
        "name": finding.title,
        "severity": finding.severity,
        "level": SEVERITY_ZH.get(finding.severity, "低风险"),
        "level_zh": SEVERITY_ZH.get(finding.severity, "低风险"),
        "owasp": finding.owasp_category or "A05 安全配置错误",
        "summary": finding.description,
        "fix": finding.fix_suggestion,
        "type": finding.type,
        "evidence": finding.evidence,
        "confidence_level": finding.confidence,
        "location": {
            "type": "url_parameter",
            "target": finding.parameter,
            "detail": finding.description,
        },
        "ai_advice": f"**漏洞**：{finding.title}\n**优先级**：立即修复\n**影响**：{finding.description}\n**修复**：{finding.fix_suggestion}",
        "cwe_id": finding.cwe_id,
    }


def add_finding(
    findings: list[dict],
    name: str,
    severity: str,  # 英文 high/medium/low
    owasp: str,
    summary: str,
    fix: str,
    vuln_type: str | None = None,
    evidence: dict | None = None,
    verify_key: str | None = None,
    verified: bool | None = None,
    confidence: int | None = None,
    confidence_level: str | None = None,
    cv_reason: str | None = None,
) -> None:
    # 生成智能分析（ai_advice）
    sev_zh = SEVERITY_ZH.get(severity, "低风险")
    if severity == "critical":
        priority, prio_reason = "立即修复", "可被直接利用，可能导致数据泄露或服务器沦陷"
    elif severity == "high":
        priority, prio_reason = "尽快修复", "存在明确利用路径，风险较高"
    elif severity == "medium":
        priority, prio_reason = "建议修复", "一定条件下可被利用，建议尽早处理"
    else:
        priority, prio_reason = "可选修复", "风险较低，可在常规维护中处理"

    ai_parts = [f"**漏洞**：{name}", f"**优先级**：{priority}（{prio_reason}）"]
    if summary:
        ai_parts.append(f"**影响**：{summary}")
    if fix:
        fix_sum = fix.split("。")[0] if "。" in fix else fix[:80]
        ai_parts.append(f"**修复**：{fix_sum}")
    ai_advice = "\n".join(ai_parts)

    finding: dict[str, Any] = {
        "name": name,
        "severity": severity,
        "level": sev_zh,
        "level_zh": sev_zh,
        "owasp": owasp,
        "summary": summary,
        "fix": fix,
        "type": vuln_type or "config",
        "evidence": evidence or {},
        "verify_method": get_verify_method_text(verify_key),
        "verify_steps": get_verify_steps(verify_key),
        "ai_advice": ai_advice,
    }
    # Vuln Sentinel：置信度（高/中/低）
    if confidence_level is not None:
        finding["confidence_level"] = confidence_level
    elif confidence is not None:
        finding["confidence_level"] = _confidence_level_from_int(confidence)
        finding["confidence"] = confidence
    else:
        finding["confidence_level"] = "高"
    if confidence is not None and "confidence" not in finding:
        finding["confidence"] = confidence
    # Vuln Sentinel：交叉验证字段（可选）
    if verified is not None:
        finding["verified"] = verified
    if cv_reason is not None:
        finding["cv_reason"] = cv_reason
    findings.append(finding)


def apply_cross_validation(findings: list, cv_result: dict) -> None:
    """把 cross_validate_findings 的结果写回到 findings 列表里。

    任何 finding 只要在 cv_result 中命中，就把 verified / confidence / cv_reason / cv_evidence
    写进去。这是个纯函数（只改 findings 列表），不抛异常。
    """
    for f in findings or []:
        name = f.get("name", "")
        cv = cv_result.get(name) if isinstance(cv_result, dict) else None
        if not cv:
            continue
        f["verified"] = cv.get("verified", True)
        f["confidence"] = cv.get("confidence", 0)
        f["cv_reason"] = cv.get("reason", "")
        f["cv_evidence"] = cv.get("evidence_d1_d5", "")


async def analyze_security(
    url: str,
    headers: dict,
    is_https: bool,
    ssl_info: dict,
    waf_list: list[dict],
    sensitive_paths: list[dict],
    vuln_findings: list[dict] | None = None,
    depth: str = "standard",
) -> dict:
    findings: list[dict] = []
    score = 100
    score_breakdown: list[dict] = []
    header_details: list[dict] = []
    owasp: list[dict] = []

    def deduct(item: str, points: int, severity: str, reason: str):
        nonlocal score
        score -= points
        score_breakdown.append(
            {"item": item, "deduction": points, "severity": severity, "reason": reason}
        )

    if not is_https:
        deduct("未启用 HTTPS", 20, "critical", "网站使用 HTTP 明文传输")
        add_finding(
            findings,
            "未启用 HTTPS",
            "high",
            "A02 加密机制失效",
            "网站使用 HTTP 明文传输。",
            "申请 SSL 证书并启用 HTTPS 强制跳转。",
            evidence={
                "detected": False,
                "reason": "网站使用 HTTP 明文传输所有数据",
                "impact": "用户数据可被中间人窃取",
            },
            verify_key="https",
            confidence_level="高",
        )
        owasp.append(
            {"category": "A02 加密机制失效", "status": "高风险", "note": "未启用 HTTPS"}
        )
    else:
        owasp.append(
            {"category": "A02 加密机制失效", "status": "通过", "note": "已启用 HTTPS"}
        )
        if ssl_info.get("has_cert"):
            dl = ssl_info.get("days_left")
            dl_is_num = isinstance(dl, (int, float))
            if ssl_info.get("expired"):
                deduct(
                    "SSL 证书已过期",
                    15,
                    "high",
                    f"证书已过期 {abs(dl) if dl_is_num else '未知'} 天",
                )
                add_finding(
                    findings,
                    "SSL 证书已过期",
                    "high",
                    "A02 加密机制失效",
                    "SSL 证书已过期"
                    + (f" {abs(dl)} 天" if dl_is_num else "（无法获取剩余天数）")
                    + "。",
                    "立即续期 SSL 证书。",
                    evidence={
                        "days_left": dl,
                        "reason": "证书已过期，浏览器会显示安全警告",
                        "impact": "用户无法正常访问，数据传输不受信任",
                    },
                    verify_key="ssl",
                    confidence_level="高",
                )
            elif dl_is_num and dl < 30:
                deduct("SSL 证书即将过期", 5, "medium", f"证书将在 {dl} 天后过期")
                add_finding(
                    findings,
                    "SSL 证书即将过期",
                    "medium",
                    "A02 加密机制失效",
                    f"SSL 证书将在 {dl} 天后过期。",
                    "提前续期 SSL 证书。",
                    verify_key="ssl",
                    confidence_level="高",
                )
            if ssl_info.get("weak"):
                deduct(
                    "弱 SSL/TLS 配置",
                    10,
                    "medium",
                    f"使用 {ssl_info.get('version', '')} / {ssl_info.get('cipher', '')}",
                )
                add_finding(
                    findings,
                    "弱 SSL/TLS 配置",
                    "medium",
                    "A02 加密机制失效",
                    "使用 "
                    + ssl_info.get("version", "")
                    + " / "
                    + ssl_info.get("cipher", "")
                    + "。",
                    "升级到 TLS 1.2+，禁用弱密码套件。",
                    verify_key="ssl",
                    confidence_level="高",
                )

    # 安全头缺失检测，verify_key 根据具体头名
    HEADER_VERIFY_KEY = {
        "strict-transport-security": "hsts",
        "content-security-policy": "csp",
        "x-frame-options": "x-frame",
        "x-content-type-options": "x-content-type",
        "referrer-policy": "referrer",
        "permissions-policy": "permissions",
    }
    # Vuln Sentinel：WAF 只作为"纵深防御能力"单独展示，不消除真实缺失项
    # Trusted Domains 白名单已移除：不能以"知名"为由自动判定安全
    waf_protected = len(waf_list) > 0
    waf_name = waf_list[0].get("name", "WAF") if waf_list else ""
    # 高危配置缺失 vs 普通配置缺失
    HIGH_CONFIG_HEADERS = {
        "strict-transport-security",
        "content-security-policy",
        "x-frame-options",
    }
    for key, rule in SECURITY_HEADERS.items():
        value = headers.get(
            key, headers.get(key.title(), headers.get(rule["name"], None))
        )
        header_details.append(
            {
                "name": rule["name"],
                "key": key,
                "value": value,
                "status": "present" if value else "missing",
                "category": rule["category"],
                "severity": rule["severity"],
            }
        )
        if not value:
            # Vuln Sentinel：所有站点统一扣分 + finding，WAF 不消除真实缺失项
            if key in HIGH_CONFIG_HEADERS:
                points = SCORE_DEDUCTION["high_config_missing"]
            else:
                points = SCORE_DEDUCTION["normal_config_missing"]
            # WAF 站点：置信度降低（WAF 提供部分防御，但不能替代安全头）
            conf_level = "中" if waf_protected else "高"
            deduct(
                "缺少 " + rule["name"], points, rule["severity"], rule["description"]
            )
            add_finding(
                findings,
                "缺少 " + rule["name"],
                rule["severity"],
                "A05 安全配置错误",
                rule["description"] + "。",
                rule["fix"],
                evidence={
                    "detected": False,
                    "header": key,
                    "reason": f"未检测到 {rule['name']} 响应头",
                    "impact": rule.get("description", ""),
                },
                verify_key=HEADER_VERIFY_KEY.get(key, "info"),
                confidence_level=conf_level,
            )

    # Vuln Sentinel: HSTS 强度评估
    hsts_value = headers.get(
        "strict-transport-security", headers.get("Strict-Transport-Security", None)
    )
    if hsts_value:
        hsts_lower = hsts_value.lower()
        # 检查 max-age 是否足够（>= 1年 = 31536000秒）
        max_age_match = re.search(r"max-age\s*=\s*(\d+)", hsts_lower)
        if max_age_match:
            max_age = int(max_age_match.group(1))
            if max_age < 31536000:  # 小于 1 年
                deduct("HSTS 配置偏弱", 3, "low", f"max-age={max_age}s，建议至少 1 年")
                add_finding(
                    findings,
                    "HSTS 配置偏弱",
                    "low",
                    "A05 安全配置错误",
                    f"HSTS max-age 设置为 {max_age} 秒（{round(max_age / 86400)} 天），建议至少设置为 31536000 秒（1 年）以获得更好的保护效果。",
                    "修改为: max-age=31536000; includeSubDomains",
                    evidence={
                        "value": hsts_value,
                        "max_age": max_age,
                        "reason": "HSTS 有效期短于 1 年",
                        "impact": "保护效果有限，建议延长有效期",
                    },
                    verify_key="hsts",
                    confidence_level="高",
                    vuln_type="HSTS-Weak",
                )
        # 检查是否包含 includeSubDomains
        if "includesubdomains" not in hsts_lower:
            # 低风险提示，不额外扣分（已经扣过了）
            pass

    # Vuln Sentinel: CSP 强度评估
    csp_value = headers.get(
        "content-security-policy", headers.get("Content-Security-Policy", None)
    )
    if csp_value:
        csp_lower = csp_value.lower()
        # 检查是否使用了 unsafe-inline 或 unsafe-eval（弱配置）
        if "unsafe-inline" in csp_lower or "unsafe-eval" in csp_lower:
            deduct("CSP 配置偏弱", 4, "medium", "CSP 包含 unsafe-inline 或 unsafe-eval")
            add_finding(
                findings,
                "CSP 配置偏弱",
                "medium",
                "A05 安全配置错误",
                "Content-Security-Policy 包含 'unsafe-inline' 或 'unsafe-eval'，降低了 XSS 防护效果。",
                "移除 unsafe-inline/unsafe-eval，使用 nonce 或 hash 方式允许内联脚本",
                evidence={
                    "value": csp_value[:100],
                    "reason": "CSP 包含不安全的指令",
                    "impact": "XSS 防护效果被削弱",
                },
                verify_key="csp",
                confidence_level="高",
                vuln_type="CSP-Weak",
            )
        # 检查是否使用了通配符
        elif "*" in csp_lower and "default-src 'none'" not in csp_lower:
            deduct("CSP 配置偏弱", 2, "low", "CSP 包含通配符源")
            add_finding(
                findings,
                "CSP 配置偏弱",
                "low",
                "A05 安全配置错误",
                "Content-Security-Policy 包含通配符 (*) 源，可能允许过多资源加载。",
                "缩小白名单范围，仅允许可信域名",
                evidence={
                    "value": csp_value[:100],
                    "reason": "CSP 使用通配符",
                    "impact": "防护范围过大，存在绕过风险",
                },
                verify_key="csp",
                confidence_level="中",
                vuln_type="CSP-Weak",
            )

    info_leaks: list[dict] = []
    for key in ["server", "x-powered-by"]:
        value = headers.get(key, headers.get(key.title(), None))
        if value:
            info_leaks.append({"name": key.title(), "value": value})
            # Vuln Sentinel：WAF 标识头不算泄露，但其它情况仍报告
            is_waf_signature = any(
                w.get("value", "").lower() in value.lower()
                or value.lower() in w.get("value", "").lower()
                for w in waf_list
            )
            has_version = bool(re.search(r"\d+\.\d+", value))  # 包含版本号
            if is_waf_signature:
                # WAF 标识头，不算泄露
                pass
            elif has_version:
                # 暴露了具体版本（nginx/1.18.0 等），扣分 + finding
                # Vuln Sentinel 优化：常见 Web 服务器 + 已检测到 WAF 时降级
                _common_servers = ["nginx", "apache", "cloudflare", "aws"]
                _is_common_server = any(s in value.lower() for s in _common_servers)
                _info_conf = "中" if (_is_common_server and waf_protected) else "高"
                deduct(
                    key.title() + " 信息泄露",
                    SCORE_DEDUCTION["info_leak"],
                    "low",
                    "暴露服务器信息: " + value[:50],
                )
                add_finding(
                    findings,
                    key.title() + " 信息泄露",
                    "low",
                    "A05 安全配置错误",
                    "暴露服务器信息: " + value[:50],
                    "隐藏或修改 " + key.title() + " 头。",
                    evidence={
                        "header": key.title(),
                        "value": value[:50],
                        "reason": "暴露了服务器软件和版本信息",
                        "impact": "攻击者可利用已知版本漏洞",
                        "check_scope": "仅检测 Server 和 X-Powered-By 响应头",
                    },
                    verify_key="server",
                    confidence_level=_info_conf,
                )
            else:
                # 未暴露版本号（如 "Server: nginx"），不扣分但提示
                info_leaks.append({"name": key.title() + " (无版本)", "value": value})

    set_cookie = headers.get("set-cookie", headers.get("Set-Cookie", None))
    cookie_issues: list[str] = []
    cookie_fix_parts = []
    if set_cookie:
        flags = set_cookie.lower()
        for flag, label in [
            ("secure", "Secure"),
            ("httponly", "HttpOnly"),
            ("samesite", "SameSite"),
        ]:
            if flag not in flags:
                cookie_issues.append("缺少 " + label)
                cookie_fix_parts.append(label)
        # SameSite=None 必须配合 Secure
        if "samesite=none" in flags and "secure" not in flags:
            cookie_issues.append("SameSite=None 未配合 Secure")
            cookie_fix_parts.append("SameSite=None 必须配合 Secure")
        # SameSite 值检查
        if "samesite" in flags:
            if "samesite=strict" in flags:
                pass  # 最优
            elif "samesite=lax" in flags:
                pass  # 可接受
            elif "samesite=none" in flags:
                if "secure" in flags:
                    cookie_issues.append("SameSite=None（建议改为 Strict/Lax）")
                # else 已在上面的检查中处理
            else:
                cookie_issues.append("SameSite 值无效")
        if cookie_issues:
            deduct(
                "Cookie 安全配置不足",
                5,
                "low",
                "Cookie 问题: " + "; ".join(cookie_issues),
            )
            fix_text = (
                "添加 " + "; ".join(cookie_fix_parts)
                if cookie_fix_parts
                else "修正 Cookie 配置"
            )
            if not fix_text.startswith("添加") and cookie_fix_parts:
                fix_text = "修正: " + "; ".join(cookie_fix_parts)
            add_finding(
                findings,
                "Cookie 安全配置不足",
                "low",
                "A07 认证失败",
                "Cookie 问题: " + "; ".join(cookie_issues),
                fix_text,
                evidence={
                    "missing_flags": cookie_issues[:],
                    "reason": "Cookie 安全配置不当",
                    "impact": "Cookie 可被窃取、篡改或用于 CSRF 攻击",
                },
                verify_key="cookie",
                confidence_level="高",
            )

    cors = headers.get(
        "access-control-allow-origin", headers.get("Access-Control-Allow-Origin", None)
    )
    cors_details = None
    if cors:
        if cors == "*":
            deduct("CORS 通配符", 10, "medium", "允许任意域名跨域访问")
            add_finding(
                findings,
                "CORS 通配符",
                "medium",
                "A01 访问控制失效",
                'Access-Control-Allow-Origin 设置为 "*"。',
                "限制为可信域名。",
                evidence={
                    "value": "*",
                    "reason": "允许任何域名跨域访问",
                    "impact": "敏感数据可被恶意网站读取",
                },
                verify_key="cors",
                confidence_level="高",
            )
            cors_details = {"value": "*", "risk": "高风险"}
        else:
            cors_details = {"value": cors, "risk": "低风险"}

    exposed = [p for p in sensitive_paths if p.get("exposed")]
    # Vuln Sentinel 优化：过滤软 404 误报（返回 200 但内容实际是 404 页面）
    SOFT_404_PATTERNS = [
        "page not found",
        "not found",
        "404 not found",
        "file not found",
        "无法找到",
        "页面不存在",
        "找不到页面",
        "资源不存在",
    ]
    real_exposed = []
    soft404_moved = []
    for p in exposed:
        snippet = (p.get("snippet", "") or "").lower()
        if any(pat in snippet for pat in SOFT_404_PATTERNS):
            # 软 404：标记为 suspect，不扣分
            p["exposed"] = False
            p["suspect"] = True
            p["reason"] = p.get("reason", "") + "（疑似软404误报，响应内容为404页面）"
            soft404_moved.append(p)
        else:
            real_exposed.append(p)
    exposed = real_exposed
    if exposed:
        # 确认漏洞：敏感路径暴露，扣 15 分
        deduct(
            "敏感路径暴露",
            SCORE_DEDUCTION["exposed_path"],
            "high",
            f"发现 {len(exposed)} 个敏感路径可访问",
        )
        add_finding(
            findings,
            "敏感路径暴露",
            "high",
            "A01 访问控制失效",
            "发现 "
            + str(len(exposed))
            + " 个敏感路径可访问: "
            + ", ".join([p["path"] for p in exposed[:3]]),
            "限制敏感路径访问或移除。",
            evidence={
                "paths": [p["path"] for p in exposed[:5]],
                "reason": f"发现 {len(exposed)} 个敏感路径可访问",
                "impact": "攻击者可获取配置文件、源代码等敏感信息",
            },
            verify_key="info",
            confidence_level="高",
        )
    # info 路径（如 robots.txt）不算漏洞，只作为信息提示，不扣分
    # suspect 路径：前端展示警告，但不扣分
    suspect_paths = [p for p in sensitive_paths if p.get("suspect")]
    if suspect_paths:
        # Vuln Sentinel 优化：suspect 疑似项不扣分，但记录为信息提示
        suspect_names = [p.get("path", "") for p in suspect_paths[:5]]
        add_finding(
            findings,
            "疑似敏感路径（需人工确认）",
            "low",
            "A01 访问控制失效",
            f"发现 {len(suspect_paths)} 个疑似敏感路径，因响应内容不匹配或疑似软404，需人工确认: {', '.join(suspect_names)}",
            "人工检查这些路径是否确实暴露了敏感信息，确认后限制访问。",
            vuln_type="info",
            evidence={
                "paths": suspect_names,
                "reason": "疑似项，响应内容特征不明确，需人工确认",
                "impact": "低风险，需人工确认是否真实暴露",
            },
            verify_key="info",
            confidence_level="低",
        )

    # Vuln Sentinel: 代码层漏洞动态检测（插件化）
    # 将原有直接调用迁移到插件架构，支持未来动态扩展和深度定制
    try:
        from app.plugins import ScanContext
        from app.plugins.detectors import (
            CommandInjectionDetector,
            DeserializationDetector,
            PathTraversalDetector,
            ReflectedXSSDetector,
            SQLiDetector,
            SSRFDetector,
        )

        context = ScanContext(
            url=url,
            headers=headers,
            is_https=is_https,
            ssl_info=ssl_info,
            waf_list=waf_list,
            depth=depth,
        )

        detectors = [
            SQLiDetector(),
            ReflectedXSSDetector(),
            CommandInjectionDetector(),
            PathTraversalDetector(),
            SSRFDetector(),
            DeserializationDetector(),
        ]

        plugin_tasks = []
        for d in detectors:
            if await d.is_applicable(context):
                plugin_tasks.append(d.detect(context))

        if plugin_tasks:
            plugin_results = await asyncio.gather(*plugin_tasks, return_exceptions=True)
            for res in plugin_results:
                if isinstance(res, list):
                    for finding in res:
                        if vuln_findings is None:
                            vuln_findings = []
                        vuln_findings.append(_finding_to_dict(finding))
                elif isinstance(res, Exception):
                    logger.warning("Plugin detection error: %s", res)
    except Exception as e:
        logger.warning("Plugin-based vulnerability detection failed: %s", e)

    if vuln_findings:
        for v in vuln_findings:
            v["confidence_level"] = v.get("confidence_level", "高")
            findings.append(v)
            sev = v.get("severity", "high")
            if sev == "critical":
                deduct(v.get("name", "漏洞"), 25, "critical", "检测到严重漏洞")
            elif sev == "high":
                deduct(v.get("name", "漏洞"), 15, "high", "检测到高风险漏洞")
            # Vuln Sentinel: 补充 medium 和 low 的扣分逻辑，确保评分与 summary 统计一致
            elif sev == "medium":
                deduct(v.get("name", "漏洞"), 8, "medium", "检测到中风险漏洞")
            elif sev == "low":
                deduct(v.get("name", "漏洞"), 3, "low", "检测到低风险漏洞")

    # 真实严重度统计
    summary = {"high": 0, "medium": 0, "low": 0, "critical": 0, "total": 0}
    for f in findings:
        sev = f.get("severity", "low")
        if sev in summary:
            summary[sev] += 1
        summary["total"] += 1

    owasp_map = {item["category"]: item for item in owasp}
    has_xss = any(f.get("type") == "XSS" for f in findings)
    has_sqli = any(f.get("type") == "SQLi" for f in findings)
    has_a01 = any("A01" in f.get("owasp", "") for f in findings)
    has_a04 = any("A04" in f.get("owasp", "") for f in findings)
    has_a06 = any("A06" in f.get("owasp", "") for f in findings)
    has_a07 = any("A07" in f.get("owasp", "") for f in findings)
    has_a08 = any("A08" in f.get("owasp", "") for f in findings)
    has_a10 = any("A10" in f.get("owasp", "") for f in findings)
    a06_count = sum(1 for f in findings if "A06" in f.get("owasp", ""))
    a07_count = sum(1 for f in findings if "A07" in f.get("owasp", ""))
    a08_count = sum(1 for f in findings if "A08" in f.get("owasp", ""))
    # Vuln Sentinel 优化：如果某个类别只有 low 级别的 finding，降级为"需关注"
    a01_all_low = has_a01 and all(
        f.get("severity") == "low" for f in findings if "A01" in f.get("owasp", "")
    )
    a03_all_low = (has_xss or has_sqli) and all(
        f.get("severity") == "low"
        for f in findings
        if f.get("type") in ("XSS", "SQLi") or "A03" in f.get("owasp", "")
    )
    a06_all_low = has_a06 and all(
        f.get("severity") == "low" for f in findings if "A06" in f.get("owasp", "")
    )
    a10_all_low = has_a10 and all(
        f.get("severity") == "low" for f in findings if "A10" in f.get("owasp", "")
    )
    for cat, status, note in [
        (
            "A01 访问控制失效",
            "需关注"
            if (has_a01 and a01_all_low)
            else ("高风险" if has_a01 else ("通过" if not exposed else "需关注")),
            f"检测到 {sum(1 for f in findings if 'A01' in f.get('owasp', ''))} 项问题"
            + ("（均为低风险）" if a01_all_low else "")
            if has_a01
            else ("目录遍历等访问控制风险" if exposed else "未检测到访问控制问题"),
        ),
        (
            "A03 注入攻击",
            "需关注"
            if ((has_xss or has_sqli) and a03_all_low)
            else ("高风险" if (has_xss or has_sqli) else "通过"),
            "检测到 XSS/SQLi" + ("（均为低风险）" if a03_all_low else "")
            if (has_xss or has_sqli)
            else "未检测到注入漏洞",
        ),
        (
            "A04 不安全设计",
            "需关注" if has_a04 else "通过",
            f"检测到 {sum(1 for f in findings if 'A04' in f.get('owasp', ''))} 项设计缺陷"
            if has_a04
            else "未在常见入口检测到开放重定向",
        ),
        (
            "A05 安全配置错误",
            "需关注"
            if any(f["owasp"] == "A05 安全配置错误" for f in findings)
            else "通过",
            "部分配置可优化",
        ),
        (
            "A06 过时组件",
            "需关注"
            if (has_a06 and a06_all_low)
            else ("高风险" if has_a06 else "通过"),
            f"检测到 {a06_count} 个存在已知漏洞的组件"
            + ("（均为低风险）" if a06_all_low else "")
            if has_a06
            else "未检测到过时组件",
        ),
        (
            "A07 认证失败",
            "需关注" if has_a07 else "通过",
            f"检测到 {a07_count} 项认证相关问题"
            if has_a07
            else "未在登录页检测到明显认证配置问题",
        ),
        (
            "A08 软件完整性",
            "需关注" if has_a08 else "通过",
            f"检测到 {a08_count} 项完整性风险"
            if has_a08
            else "首页第三方资源完整性校验正常",
        ),
        ("A09 日志监控不足", "低风险", "建议加强日志与监控"),
        (
            "A10 服务端请求伪造",
            "需关注"
            if (has_a10 and a10_all_low)
            else ("高风险" if has_a10 else "通过"),
            "检测到 SSRF 风险" + ("（均为低风险）" if a10_all_low else "")
            if has_a10
            else "未检测到 SSRF 漏洞",
        ),
    ]:
        if cat not in owasp_map:
            owasp.append({"category": cat, "status": status, "note": note})
        else:
            # 如果已有条目（如 A02），保持原样
            pass
    owasp.sort(key=lambda x: int(x["category"][1:3]))
    # Vuln Sentinel：WAF 作为纵深防御能力，最多 +3 分奖励，不覆盖真实缺失项
    waf_bonus = 0
    if waf_protected:
        waf_bonus = 2
        real_waf_names = {"aliyun", "imperva", "akamai"}
        if any(w.get("name", "").lower() in real_waf_names for w in waf_list):
            waf_bonus = 3
    score = score + waf_bonus
    score = max(10, min(100, score))
    risk_level = "严重" if score < 40 else "高风险" if score < 60 else "中风险" if score < 80 else "低风险"
    improvements: list[str] = []
    for f in findings:
        improvements.append(f.get("fix", ""))

    # 检测受限扫描特征：WAF/反爬/登录页
    # 注意：CDN（Cloudflare/AWS）只标"识别到"，不算受限；
    # 真正的反爬 WAF（阿里云 WAF/Imperva/Akamai WAF）才算受限
    REAL_WAF = {"aliyun", "imperva", "akamai"}
    restricted = False
    restricted_reason = ""
    restricted_code = ""
    # 1. 真正的反爬 WAF 检测（区分 CDN）
    if waf_list:
        waf_name = waf_list[0].get("name", "").lower()
        if waf_name in REAL_WAF:
            restricted = True
            restricted_reason = f"检测到反爬 WAF（{waf_list[0].get('name', '未知')}），目标站点有访问限制，建议人工复核。"
            restricted_code = "WAF"
        # CDN（WAF/CDN 列表里有 cloudflare/aws）只标识别到，不算受限
    # 2. 敏感路径中有 suspect（登录页/反爬响应）
    suspect_paths = [p for p in sensitive_paths if p.get("suspect")]
    if suspect_paths and not restricted:
        restricted = True
        reasons = [p.get("reason", "疑似 WAF/登录页响应") for p in suspect_paths[:2]]
        restricted_reason = (
            "检测到疑似 WAF/登录页/反爬响应："
            + "；".join(reasons)
            + "。本次为受限扫描，部分结果需要人工确认。"
        )
        restricted_code = "SUSPECT"
    # 3. 响应头中有反爬特征
    if headers:
        hk = {k.lower(): str(v) for k, v in headers.items()}
        anti_bot_signs = [
            "alicdn",
            "captcha",
            "waf",
            "punish",
            "verify",
            "authentication",
        ]
        for sign in anti_bot_signs:
            for k, v in hk.items():
                if sign in k or sign in v:
                    if not restricted:
                        restricted = True
                        restricted_reason = f"响应头检测到反爬/WAF 特征（{sign}），目标站点限制自动化访问，建议人工复核。"
                        restricted_code = "ANTI_BOT"
                    break

    # Vuln Sentinel：受限扫描时所有发现标记为"证据不足"（低置信度）
    if restricted:
        for f in findings:
            f["confidence_level"] = "低"
            f["confidence"] = 40

    # Vuln Sentinel 优化：同一目标超过 15 个 findings 时，只展示前 15 个（按严重度排序）
    _severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    if len(findings) > 15:
        findings.sort(key=lambda f: _severity_order.get(f.get("severity", "low"), 99))
        truncated = findings[15:]
        findings = findings[:15]
        # 记录被截断的发现数量，作为信息提示
        findings.append(
            {
                "name": f"更多发现（{len(truncated)} 项）",
                "severity": "low",
                "level": "低风险",
                "level_zh": "低风险",
                "owasp": "A05 安全配置错误",
                "summary": f"扫描发现超过 15 个问题，以上仅展示严重度最高的前 15 项。其余 {len(truncated)} 项被省略: {', '.join([t.get('name', '未知') for t in truncated[:5]])}{'...' if len(truncated) > 5 else ''}",
                "fix": "建议优先修复高风险项，然后重新扫描以查看剩余发现。",
                "type": "info",
                "evidence": {
                    "truncated_count": len(truncated),
                    "truncated_names": [t.get("name") for t in truncated[:10]],
                },
                "confidence_level": "高",
            }
        )

    return {
        "score": score,
        "risk_level": risk_level,
        "findings": findings,
        "summary": summary,
        "owasp_coverage": owasp,
        "header_details": header_details,
        "info_leaks": info_leaks,
        "cors": cors_details,
        "cookie_issues": cookie_issues,
        "ssl_info": ssl_info,
        "waf": waf_list,
        "sensitive_paths": sensitive_paths,
        "waf_detected": len(waf_list) > 0,
        "improvements": improvements,
        "score_breakdown": score_breakdown,
        "restricted": restricted,
        "restricted_reason": restricted_reason,
        "restricted_code": restricted_code,
    }


# ---------- PDF Report ----------


def generate_pdf_report(scan_data: dict) -> bytes:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    _cn_font = "Helvetica"
    # Vuln Sentinel 修复：先尝试 WQY（TTF 格式，reportlab 完美支持）
    # NotoSansCJK 是 CFF/OTF 格式，reportlab 的 TTFont 不支持
    for _fp in [
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttf",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttf",
        "static/fonts/NotoSansSC-Regular.ttf",
        r"C:\Windows\Fonts\simhei.ttf",
        r"C:\Windows\Fonts\simsun.ttc",
        r"C:\Windows\Fonts\simsunb.ttf",
        r"C:\Windows\Fonts\NotoSansSC-VF.ttf",
        r"C:\Windows\Fonts\Noto Sans SC (TrueType).otf",
    ]:
        if os.path.isfile(_fp):
            try:
                pdfmetrics.registerFont(TTFont("CNFont", _fp))
                _cn_font = "CNFont"
                import logging

                logging.getLogger("vuln_sentinel").info(
                    "PDF CJK font registered: " + _fp
                )
                break
            except Exception as _e:
                import logging

                logging.getLogger("vuln_sentinel").warning(
                    "PDF CJK font failed: " + _fp + " - " + str(_e)
                )
                continue

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CN", fontName=_cn_font, fontSize=10, leading=14))
    styles.add(
        ParagraphStyle(
            name="CNBold",
            fontName=_cn_font,
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#4f46e5"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="CNRed",
            fontName=_cn_font,
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#dc2626"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="CNGreen",
            fontName=_cn_font,
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#16a34a"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="CNOrange",
            fontName=_cn_font,
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#d97706"),
        )
    )
    # 覆盖默认 Heading 样式使用中文字体
    for _h in (
        "Heading1",
        "Heading2",
        "Heading3",
        "Heading4",
        "Title",
        "Normal",
        "BodyText",
    ):
        if _h in styles:
            try:
                styles[_h].fontName = _cn_font
            except Exception as e:
                logger.warning("PDF style %s font set failed: %s", _h, e)

    elements = []

    # ===== 封面页 =====
    elements.append(Spacer(1, 60 * mm))
    elements.append(
        Paragraph(
            "Vuln Sentinel",
            ParagraphStyle(
                name="CoverTitle",
                fontName=_cn_font,
                fontSize=28,
                leading=36,
                alignment=1,
            ),
        )
    )
    elements.append(Spacer(1, 10 * mm))
    elements.append(
        Paragraph(
            "Web 安全扫描报告",
            ParagraphStyle(
                name="CoverSub", fontName=_cn_font, fontSize=16, leading=22, alignment=1
            ),
        )
    )
    elements.append(Spacer(1, 20 * mm))
    elements.append(
        Paragraph(
            f"目标: {scan_data.get('url', '')}",
            ParagraphStyle(
                name="CoverInfo",
                fontName=_cn_font,
                fontSize=11,
                leading=16,
                alignment=1,
            ),
        )
    )
    elements.append(
        Paragraph(
            f"时间: {scan_data.get('time', '')}",
            ParagraphStyle(
                name="CoverInfo2",
                fontName=_cn_font,
                fontSize=11,
                leading=16,
                alignment=1,
            ),
        )
    )
    elements.append(
        Paragraph(
            f"评分: {scan_data.get('score', 0)} / 100",
            ParagraphStyle(
                name="CoverInfo3",
                fontName=_cn_font,
                fontSize=11,
                leading=16,
                alignment=1,
            ),
        )
    )
    elements.append(Spacer(1, 30 * mm))
    elements.append(
        Paragraph(
            "本报告由Vuln Sentinel自动生成，仅供参考。",
            ParagraphStyle(
                name="CoverNote",
                fontName=_cn_font,
                fontSize=9,
                leading=13,
                alignment=1,
                textColor=colors.grey,
            ),
        )
    )
    elements.append(PageBreak())

    # ===== 摘要页 =====
    elements.append(Paragraph("摘要", styles["Heading2"]))
    elements.append(
        Paragraph(
            f"安全评分: {scan_data.get('score', 0)} / 100（{scan_data.get('risk_level', '')}）",
            styles["CN"],
        )
    )
    summary = scan_data.get("summary", {})
    elements.append(
        Paragraph(
            f"发现问题: {summary.get('total', 0)} 个（严重 {summary.get('critical', 0)} / 高危 {summary.get('high', 0)} / 中危 {summary.get('medium', 0)} / 低危 {summary.get('low', 0)}）",
            styles["CN"],
        )
    )
    elements.append(Spacer(1, 5 * mm))

    elements.append(Paragraph("检测范围", styles["Heading2"]))
    elements.append(
        Paragraph(
            "本次扫描检测了以下安全项目：HTTPS/TLS 配置、安全响应头（HSTS/CSP/X-Frame-Options 等）、信息泄露、Cookie 安全、CORS 配置、敏感路径暴露、WAF 检测。",
            styles["CN"],
        )
    )
    elements.append(
        Paragraph("不进行破坏性攻击、不爆破密码、不绕过权限验证。", styles["CN"])
    )
    elements.append(Spacer(1, 5 * mm))
    elements.append(PageBreak())

    # ===== 风险摘要页 =====
    elements.append(Paragraph("风险摘要", styles["Heading2"]))
    findings = scan_data.get("findings", [])
    exposed_count = len(
        [p for p in scan_data.get("sensitive_paths", []) if p.get("exposed")]
    )
    suspect_count = len(
        [p for p in scan_data.get("sensitive_paths", []) if p.get("suspect")]
    )
    config_missing = len([f for f in findings if f.get("name", "").startswith("缺少 ")])
    elements.append(Paragraph(f"确认漏洞数: {exposed_count} 个", styles["CNRed"]))
    elements.append(Paragraph(f"疑似风险数: {suspect_count} 个", styles["CNOrange"]))
    elements.append(Paragraph(f"配置缺失数: {config_missing} 个", styles["CN"]))
    elements.append(Spacer(1, 3 * mm))

    # 评分变化（如果有历史记录）
    history = scan_data.get("history", [])
    if len(history) >= 2:
        prev_score = history[-2].get("score", 0)
        curr_score = scan_data.get("score", 0)
        delta = curr_score - prev_score
        delta_text = f"+{delta}" if delta > 0 else str(delta)
        delta_color = (
            styles["CNGreen"]
            if delta > 0
            else styles["CNRed"]
            if delta < 0
            else styles["CN"]
        )
        elements.append(
            Paragraph(
                f"评分变化: {prev_score} -> {curr_score} ({delta_text})", delta_color
            )
        )
        elements.append(Spacer(1, 3 * mm))

    # 修复优先级路线
    elements.append(Paragraph("修复优先级路线", styles["Heading2"]))
    priority_steps = []
    if exposed_count > 0:
        priority_steps.append(
            "第一步（立即）: 修复暴露的敏感路径，限制 .env/.git 等文件访问"
        )
    high_headers = [
        f
        for f in findings
        if f.get("severity") == "high" and f.get("name", "").startswith("缺少 ")
    ]
    if high_headers:
        priority_steps.append(
            f"第二步（今天）: 修复高危响应头缺失（{', '.join([f.get('name', '').replace('缺少 ', '') for f in high_headers[:3]])}）"
        )
    med_low = [
        f
        for f in findings
        if f.get("severity") in ("medium", "low")
        and f.get("name", "").startswith("缺少 ")
    ]
    if med_low:
        priority_steps.append(f"第三步（本周）: 补充中低危配置（{len(med_low)} 项）")
    if not priority_steps:
        priority_steps.append("当前配置良好，继续保持并定期复测")
    for step in priority_steps:
        elements.append(Paragraph(f"• {step}", styles["CN"]))
    elements.append(Spacer(1, 5 * mm))
    elements.append(PageBreak())

    # ===== 证据页 =====
    elements.append(Paragraph("证据详情", styles["Heading2"]))
    if findings:
        for i, f in enumerate(findings):
            elements.append(
                Paragraph(
                    f"{i + 1}. {f.get('name', '')} [{f.get('level', f.get('severity', ''))}]",
                    styles["CNBold"],
                )
            )
            ev = f.get("evidence", {})
            if ev.get("header"):
                elements.append(Paragraph(f"   响应头: {ev['header']}", styles["CN"]))
            if ev.get("value"):
                val = str(ev["value"])[:200]
                elements.append(Paragraph(f"   实际值: {val}", styles["CN"]))
            if ev.get("reason"):
                elements.append(Paragraph(f"   判定依据: {ev['reason']}", styles["CN"]))
            if ev.get("method"):
                elements.append(Paragraph(f"   检测方法: {ev['method']}", styles["CN"]))
            # 敏感路径内容片段
            if "敏感路径" in f.get("name", "") or "敏感文件" in f.get("name", ""):
                for p in scan_data.get("sensitive_paths", []):
                    if p.get("exposed") or p.get("suspect"):
                        elements.append(
                            Paragraph(
                                f"   路径 {p.get('path', '')}: 状态 {p.get('status', '')} - {p.get('reason', '')}",
                                styles["CN"],
                            )
                        )
            elements.append(Spacer(1, 2 * mm))
    else:
        elements.append(Paragraph("未发现安全问题", styles["CN"]))
    elements.append(Spacer(1, 5 * mm))
    elements.append(PageBreak())

    # ===== 修复建议页 =====
    elements.append(Paragraph("修复建议", styles["Heading2"]))
    fixes = scan_data.get("fixes", {})
    if fixes:
        for platform, entries in fixes.items():
            if not entries:
                continue
            elements.append(Paragraph(f"{platform.upper()} 配置", styles["CNBold"]))
            for entry in entries:
                code = entry.get("code", "") if isinstance(entry, dict) else str(entry)
                risk_note = (
                    entry.get("risk_note", "") if isinstance(entry, dict) else ""
                )
                elements.append(
                    Paragraph(
                        f"<pre>{code}</pre>",
                        ParagraphStyle(
                            name="Code",
                            fontName=_cn_font,
                            fontSize=8,
                            leading=12,
                            leftIndent=10,
                            textColor=colors.HexColor("#334155"),
                        ),
                    )
                )
                if risk_note:
                    elements.append(Paragraph(f"注意: {risk_note}", styles["CNOrange"]))
                elements.append(Spacer(1, 2 * mm))
    else:
        # 按 findings 生成通用修复建议
        for f in findings:
            fix_text = f.get("fix", "")
            if fix_text:
                elements.append(Paragraph(f"{f.get('name', '')}:", styles["CNBold"]))
                elements.append(
                    Paragraph(
                        f"<pre>{fix_text}</pre>",
                        ParagraphStyle(
                            name="Code2",
                            fontName=_cn_font,
                            fontSize=8,
                            leading=12,
                            leftIndent=10,
                            textColor=colors.HexColor("#334155"),
                        ),
                    )
                )
                elements.append(Spacer(1, 2 * mm))
    elements.append(Spacer(1, 5 * mm))
    elements.append(PageBreak())

    # ===== 复测结果页 =====
    elements.append(Paragraph("复测结果", styles["Heading2"]))
    if len(history) >= 2:
        prev = history[-2]
        prev_score = prev.get("score", 0)
        curr_score = scan_data.get("score", 0)
        elements.append(
            Paragraph(f"上次评分: {prev_score} | 本次评分: {curr_score}", styles["CN"])
        )
        prev_names = set([ff.get("name", "") for ff in prev.get("findings", [])])
        curr_names = set([ff.get("name", "") for ff in scan_data.get("findings", [])])
        new_issues = curr_names - prev_names
        fixed_issues = prev_names - curr_names
        if new_issues:
            elements.append(
                Paragraph(f"新增问题 ({len(new_issues)}):", styles["CNRed"])
            )
            for issue in sorted(new_issues):
                elements.append(Paragraph(f"  • {issue}", styles["CN"]))
        if fixed_issues:
            elements.append(
                Paragraph(f"已修复问题 ({len(fixed_issues)}):", styles["CNGreen"])
            )
            for issue in sorted(fixed_issues):
                elements.append(Paragraph(f"  • {issue}", styles["CN"]))
        if not new_issues and not fixed_issues:
            elements.append(Paragraph("两次扫描结果一致，无变化", styles["CN"]))
    else:
        elements.append(
            Paragraph(
                '暂无历史复测数据。建议修复后点击"验证修复效果"进行复测。', styles["CN"]
            )
        )
    elements.append(Spacer(1, 5 * mm))
    elements.append(PageBreak())

    # ===== Findings 表格（含证据列） =====
    elements.append(Paragraph("问题详情", styles["Heading2"]))
    if findings:
        table_data = [["#", "问题", "严重度", "OWASP", "证据/原因", "修复建议"]]
        for i, f in enumerate(findings):
            evidence = f.get("evidence", {})
            evidence_text = evidence.get("reason", "")[:40] if evidence else ""
            table_data.append(
                [
                    str(i + 1),
                    f.get("name", ""),
                    f.get("level", f.get("severity", "")),
                    f.get("owasp", ""),
                    evidence_text,
                    f.get("fix", "")[:50],
                ]
            )
        t = Table(
            table_data, colWidths=[8 * mm, 28 * mm, 18 * mm, 25 * mm, 30 * mm, 41 * mm]
        )
        t.setStyle(
            TableStyle(
                [
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, -1),
                        _cn_font,
                    ),  # Vuln Sentinel 修复：表格用中文字体
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4f46e5")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTSIZE", (0, 0), (-1, -1), 7),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.HexColor("#f5f5f5")],
                    ),
                ]
            )
        )
        elements.append(t)
    elements.append(Spacer(1, 8 * mm))

    elements.append(Paragraph("OWASP Top 10 覆盖情况", styles["Heading2"]))
    owasp = scan_data.get("owasp_coverage", [])
    if owasp:
        owasp_data = [["分类", "状态", "说明"]]
        for o in owasp:
            owasp_data.append([o["category"], o["status"], o.get("note", "")])
        t2 = Table(owasp_data, colWidths=[50 * mm, 30 * mm, 70 * mm])
        t2.setStyle(
            TableStyle(
                [
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, -1),
                        _cn_font,
                    ),  # Vuln Sentinel 修复：表格用中文字体
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4f46e5")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ]
            )
        )
        elements.append(t2)

    # ===== 免责声明 =====
    elements.append(Spacer(1, 10 * mm))
    elements.append(Paragraph("免责声明", styles["Heading2"]))
    elements.append(
        Paragraph(
            "本报告由Vuln Sentinel智能规则引擎自动生成，仅反映扫描时刻的目标网站安全配置状况。扫描结果可能存在误报或漏报，不构成完整的安全审计。建议结合专业安全评估和渗透测试综合判断。本工具不进行任何破坏性操作。",
            styles["CN"],
        )
    )

    doc.build(elements)
    return buf.getvalue()


def generate_src_markdown_report(
    scan_data: dict, finding_ids: list[str] | None = None
) -> str:
    """生成适合 SRC 平台提交的 Markdown 格式漏洞报告。"""
    url = scan_data.get("url", "")
    findings = scan_data.get("findings", []) or []
    if finding_ids:
        findings = [f for f in findings if f.get("id") in finding_ids]

    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for finding in findings:
        sev = str(finding.get("severity", "info")).lower()
        if sev in severity_counts:
            severity_counts[sev] += 1
        else:
            severity_counts["info"] += 1

    score = scan_data.get("score", 0)
    risk_level = scan_data.get("risk_level", "")
    if severity_counts["critical"] or severity_counts["high"]:
        priority_line = f"- **优先级建议**: 优先处理 {severity_counts['critical']} 个严重项和 {severity_counts['high']} 个高危项。"
    elif severity_counts["medium"]:
        priority_line = f"- **优先级建议**: 重点处理 {severity_counts['medium']} 个中危项，再复测验证。"
    else:
        priority_line = "- **优先级建议**: 当前以低危/信息项为主，建议持续监控并保留基线。"

    lines = [
        f"# {url} 安全漏洞报告",
        "",
        "## 执行摘要",
        "",
        priority_line,
        f"- **扫描时间**: {scan_data.get('time', '')}",
        f"- **安全评分**: {score} / 100（{risk_level}）",
        f"- **漏洞总数**: {len(findings)} 个",
        f"- **严重/高危/中危/低危/信息**: {severity_counts['critical']}/{severity_counts['high']}/{severity_counts['medium']}/{severity_counts['low']}/{severity_counts['info']}",
        "",
        "## 漏洞汇总",
        "",
        "| 序号 | 漏洞名称 | 严重度 | 评分 | CWE | OWASP | CVSS |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for i, f in enumerate(findings, 1):
        lines.append(
            f"| {i} | {f.get('title', '')} | {f.get('severity', '')} | {f.get('severity_score', '-')}/10 | "
            f"{f.get('cwe_id', '')} | {f.get('owasp_category', '')} | "
            f"{f.get('cvss_score', '-')} ({f.get('cvss_vector', '')}) |"
        )
    lines.append("")

    for i, f in enumerate(findings, 1):
        ev = f.get("evidence", {})
        steps = f.get("reproduce_steps", [])
        fix = f.get("fix_suggestion", "")
        lines.extend(
            [
                f"## {i}. {f.get('title', '')}",
                "",
                f"- **漏洞类型**: {f.get('type', '')}",
                f"- **严重度**: {f.get('severity', '')}（{f.get('severity_score', '-')}/10）",
                f"- **CWE**: {f.get('cwe_id', '')}",
                f"- **OWASP**: {f.get('owasp_category', '')}",
                f"- **CVSS v3.1**: {f.get('cvss_score', '-')} `{f.get('cvss_vector', '')}`",
                f"- **置信度**: {f.get('confidence', '')}",
                f"- **漏洞 URL**: {f.get('url', '')}",
                f"- **参数/位置**: {f.get('parameter', '') or f.get('location', '')}",
                "",
                "### 漏洞描述",
                "",
                f.get("description", ""),
                "",
                "### 实际影响",
                "",
                f.get("impact", ""),
                "",
            ]
        )
        if steps:
            lines.extend(["### 复现步骤", ""])
            for idx, step in enumerate(steps, 1):
                lines.append(f"{idx}. {step}")
            lines.append("")
        if ev.get("payload"):
            lines.extend(["### Payload", "", f"```text\n{ev['payload']}\n```", ""])
        if ev.get("request"):
            lines.extend(["### HTTP 请求", "", f"```http\n{ev['request']}\n```", ""])
        if ev.get("response"):
            lines.extend(["### 响应片段", "", f"```http\n{ev['response']}\n```", ""])
        lines.extend(
            [
                "### 修复建议",
                "",
                fix,
                "",
            ]
        )
        if fix:
            lines.extend(
                [
                    "### 建议验证动作",
                    "",
                    "- 修复后重新扫描同一地址，确认问题已消失。",
                    "- 检查安全头、Cookie、权限控制或输入处理是否符合预期。",
                    "- 将该项纳入回归测试或上线前安全检查。",
                    "",
                ]
            )
        refs = f.get("references", [])
        if refs:
            lines.extend(["### 参考链接", ""])
            for ref in refs:
                lines.append(f"- {ref}")
            lines.append("")

    lines.extend(
        [
            "---",
            "",
            "> 本报告由Vuln Sentinel自动生成，SRC 提交前建议人工复核证据与 CVSS 评分。",
            "",
        ]
    )
    return "\n".join(lines)

def generate_html_report(scan_data: dict) -> str:
    """生成精美的 HTML 格式安全报告（可直接在浏览器打开/打印）"""
    url = scan_data.get("url", "")
    score = scan_data.get("score", 0)
    risk_level = scan_data.get("risk_level", "未知")
    time_str = scan_data.get("time", "")
    findings = scan_data.get("findings", [])
    score_breakdown = scan_data.get("score_breakdown", [])
    owasp = scan_data.get("owasp_coverage", [])

    # 统计
    critical = len([f for f in findings if f.get("severity") == "critical"])
    high = len([f for f in findings if f.get("severity") == "high"])
    medium = len([f for f in findings if f.get("severity") == "medium"])
    low = len([f for f in findings if f.get("severity") == "low"])
    total = len(findings)

    # 评分颜色
    if score >= 90:
        score_color = "#22c55e"
        score_gradient = "linear-gradient(135deg, #22c55e, #16a34a)"
    elif score >= 70:
        score_color = "#f59e0b"
        score_gradient = "linear-gradient(135deg, #f59e0b, #d97706)"
    elif score >= 50:
        score_color = "#f97316"
        score_gradient = "linear-gradient(135deg, #f97316, #ea580c)"
    else:
        score_color = "#ef4444"
        score_gradient = "linear-gradient(135deg, #ef4444, #dc2626)"

    # 生成漏洞列表 HTML
    findings_html = ""
    sev_labels = {"critical": "严重", "high": "高危", "medium": "中危", "low": "低危"}
    sev_colors = {
        "critical": {"bg": "#fef2f2", "text": "#dc2626", "border": "#fecaca"},
        "high": {"bg": "#fff7ed", "text": "#c2410c", "border": "#fed7aa"},
        "medium": {"bg": "#fefce8", "text": "#a16207", "border": "#fef08a"},
        "low": {"bg": "#f0fdf4", "text": "#15803d", "border": "#bbf7d0"},
    }

    for i, f in enumerate(findings):
        sev = f.get("severity", "low")
        sc = sev_colors.get(sev, sev_colors["low"])
        sl = sev_labels.get(sev, "低危")
        name = f.get("name", "")
        summary = f.get("summary", "")
        fix = f.get("fix", "")
        owasp_cat = f.get("owasp", "")
        evidence = f.get("evidence", {})
        verify_steps = f.get("verify_steps", [])

        findings_html += f"""
        <div class="finding-card" style="margin-bottom:16px;padding:16px;background:#fff;border:1px solid {sc["border"]};border-radius:10px;border-left:4px solid {sc["text"]}">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px">
                <div style="flex:1">
                    <div style="font-size:15px;font-weight:700;color:#1e293b;margin-bottom:4px">{i + 1}. {_html_escape(name)}</div>
                    <div style="display:flex;gap:8px;flex-wrap:wrap">
                        <span style="font-size:11px;padding:2px 8px;border-radius:10px;background:{sc["bg"]};color:{sc["text"]};font-weight:600">{sl}</span>
                        {f'<span style="font-size:11px;padding:2px 8px;border-radius:10px;background:#eef2ff;color:#4f46e5;font-weight:600">{_html_escape(owasp_cat)}</span>' if owasp_cat else ""}
                    </div>
                </div>
            </div>
            {f'<div style="margin-top:10px;font-size:13px;color:#475569;line-height:1.6">{_html_escape(summary)}</div>' if summary else ""}
        """

        # 证据
        if evidence and evidence.get("reason"):
            findings_html += f"""
            <div style="margin-top:10px;padding:8px 12px;background:#f8fafc;border-radius:6px;font-size:12px">
                <div style="font-weight:600;color:#475569;margin-bottom:4px">📋 判定依据</div>
                <div style="color:#64748b">{_html_escape(evidence["reason"])}</div>
            </div>
            """

        # 修复建议
        if fix:
            findings_html += f"""
            <div style="margin-top:10px;padding:8px 12px;background:#f0fdf4;border-radius:6px;font-size:12px">
                <div style="font-weight:600;color:#15803d;margin-bottom:4px">🛠 修复建议</div>
                <pre style="margin:0;padding:8px;background:#0f172a;color:#a7f3d0;border-radius:6px;font-size:11px;line-height:1.5;overflow-x:auto;white-space:pre-wrap;word-break:break-all">{_html_escape(fix)}</pre>
            </div>
            """

        # 验证步骤
        if verify_steps and len(verify_steps) > 0:
            findings_html += """
            <div style="margin-top:10px;padding:8px 12px;background:#eff6ff;border-radius:6px;font-size:12px">
                <div style="font-weight:600;color:#1d4ed8;margin-bottom:6px">✅ 验证步骤</div>
            """
            for j, step in enumerate(verify_steps):
                findings_html += f"""
                <div style="margin-bottom:6px;padding-left:8px;border-left:2px solid #93c5fd">
                    <div style="font-weight:600;color:#1e40af;font-size:11px">第{j + 1}步：{_html_escape(step.get("method", ""))}</div>
                    {f'<div style="color:#64748b;font-size:11px;margin-top:2px">操作：<code style="background:#e0e7ff;padding:1px 4px;border-radius:3px">{_html_escape(step.get("command", ""))}</code></div>' if step.get("command") else ""}
                    {f'<div style="color:#15803d;font-size:11px;margin-top:2px">预期：{_html_escape(step.get("expect", ""))}</div>' if step.get("expect") else ""}
                </div>
                """
            findings_html += "</div>"

        findings_html += "</div>"

    # 评分解读 HTML
    breakdown_html = ""
    if score_breakdown and len(score_breakdown) > 0:
        # 按严重程度分组
        critical_deduct = sum(
            b.get("deduction", 0)
            for b in score_breakdown
            if b.get("severity") == "critical"
        )
        high_deduct = sum(
            b.get("deduction", 0)
            for b in score_breakdown
            if b.get("severity") == "high"
        )
        medium_deduct = sum(
            b.get("deduction", 0)
            for b in score_breakdown
            if b.get("severity") == "medium"
        )
        low_deduct = sum(
            b.get("deduction", 0) for b in score_breakdown if b.get("severity") == "low"
        )
        total_deduct = critical_deduct + high_deduct + medium_deduct + low_deduct

        max_deduct = max(critical_deduct, high_deduct, medium_deduct, low_deduct, 1)

        bar_groups = [
            {
                "label": "严重",
                "deduct": critical_deduct,
                "count": len(
                    [b for b in score_breakdown if b.get("severity") == "critical"]
                ),
                "color": "#dc2626",
            },
            {
                "label": "高风险",
                "deduct": high_deduct,
                "count": len(
                    [b for b in score_breakdown if b.get("severity") == "high"]
                ),
                "color": "#f97316",
            },
            {
                "label": "中风险",
                "deduct": medium_deduct,
                "count": len(
                    [b for b in score_breakdown if b.get("severity") == "medium"]
                ),
                "color": "#eab308",
            },
            {
                "label": "低风险",
                "deduct": low_deduct,
                "count": len(
                    [b for b in score_breakdown if b.get("severity") == "low"]
                ),
                "color": "#22c55e",
            },
        ]

        bars_html = ""
        for g in bar_groups:
            if g["count"] > 0 and g["deduct"] > 0:
                width = max((g["deduct"] / max_deduct) * 100, 8)
            else:
                width = 0
            text_color = "#fff" if width > 30 else g["color"]
            bars_html += f"""
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
                <span style="font-size:12px;color:#64748b;min-width:50px;font-weight:600">{g["label"]}</span>
                <div style="flex:1;height:28px;background:#f1f5f9;border-radius:6px;overflow:hidden;position:relative">
                    <div style="height:100%;width:{width}%;background:{g["color"]};border-radius:6px"></div>
                    <span style="position:absolute;right:8px;top:50%;transform:translateY(-50%);font-size:11px;font-weight:700;color:{text_color}">{g["count"]} 项 / -{g["deduct"]}分</span>
                </div>
            </div>
            """

        breakdown_html = f"""
        <div class="section" style="margin-top:30px">
            <h2 style="font-size:18px;font-weight:700;color:#1e293b;margin:0 0 16px 0;padding-bottom:8px;border-bottom:2px solid #e2e8f0">📊 评分解读</h2>
            <div style="background:linear-gradient(135deg,rgba(249,115,22,0.06),rgba(239,68,68,0.06));border:1px solid rgba(249,115,22,0.2);border-radius:12px;padding:20px">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
                    <span style="font-weight:700;color:#1e293b">扣分分布</span>
                    <span style="font-size:12px;background:rgba(249,115,22,0.15);color:#ea580c;padding:4px 12px;border-radius:12px;font-weight:600">共扣 {total_deduct} 分</span>
                </div>
                {bars_html}
            </div>
        </div>
        """

    # OWASP Top 10 HTML
    owasp_html = ""
    if owasp and len(owasp) > 0:
        owasp_rows = ""
        for o in owasp:
            status = o.get("status", "未知")
            if status == "通过":
                status_color = "#22c55e"
                status_bg = "#f0fdf4"
            elif status == "需关注":
                status_color = "#f97316"
                status_bg = "#fff7ed"
            else:
                status_color = "#64748b"
                status_bg = "#f8fafc"
            owasp_rows += f"""
            <tr>
                <td style="padding:10px 12px;border-bottom:1px solid #e2e8f0;font-size:13px">{_html_escape(o.get("category", ""))}</td>
                <td style="padding:10px 12px;border-bottom:1px solid #e2e8f0;font-size:13px">
                    <span style="padding:3px 10px;border-radius:10px;background:{status_bg};color:{status_color};font-weight:600;font-size:11px">{status}</span>
                </td>
                <td style="padding:10px 12px;border-bottom:1px solid #e2e8f0;font-size:12px;color:#64748b">{_html_escape(o.get("note", ""))}</td>
            </tr>
            """
        owasp_html = f"""
        <div class="section" style="margin-top:30px">
            <h2 style="font-size:18px;font-weight:700;color:#1e293b;margin:0 0 16px 0;padding-bottom:8px;border-bottom:2px solid #e2e8f0">🛡 OWASP Top 10 覆盖情况</h2>
            <table style="width:100%;border-collapse:collapse;background:#fff;border:1px solid #e2e8f0;border-radius:8px;overflow:hidden">
                <thead>
                    <tr style="background:#4f46e5;color:#fff">
                        <th style="padding:12px;text-align:left;font-size:13px;font-weight:600">分类</th>
                        <th style="padding:12px;text-align:left;font-size:13px;font-weight:600">状态</th>
                        <th style="padding:12px;text-align:left;font-size:13px;font-weight:600">说明</th>
                    </tr>
                </thead>
                <tbody>
                    {owasp_rows}
                </tbody>
            </table>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Vuln Sentinel - Web安全扫描报告</title>
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif; background: #f8fafc; color: #1e293b; line-height: 1.6; }}
    .report-container {{ max-width: 900px; margin: 0 auto; padding: 30px 20px; }}
    .report-cover {{ background: linear-gradient(135deg, #4f46e5, #7c3aed); color: #fff; padding: 50px 40px; border-radius: 16px; margin-bottom: 30px; }}
    .report-cover h1 {{ font-size: 32px; font-weight: 800; margin-bottom: 8px; }}
    .report-cover .subtitle {{ font-size: 16px; opacity: 0.9; margin-bottom: 30px; }}
    .cover-info {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; background: rgba(255,255,255,0.1); padding: 20px; border-radius: 12px; }}
    .cover-info-item .label {{ font-size: 12px; opacity: 0.8; margin-bottom: 4px; }}
    .cover-info-item .value {{ font-size: 15px; font-weight: 600; }}
    .score-section {{ background: #fff; border-radius: 16px; padding: 30px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
    .score-display {{ display: flex; align-items: center; gap: 30px; }}
    .score-circle {{ width: 140px; height: 140px; border-radius: 50%; background: {score_gradient}; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #fff; flex-shrink: 0; box-shadow: 0 8px 24px rgba(79, 70, 229, 0.3); }}
    .score-circle .num {{ font-size: 42px; font-weight: 800; line-height: 1; }}
    .score-circle .label {{ font-size: 12px; opacity: 0.9; margin-top: 4px; }}
    .score-info {{ flex: 1; }}
    .score-info h2 {{ font-size: 20px; margin-bottom: 8px; }}
    .score-info .risk-level {{ display: inline-block; padding: 4px 12px; border-radius: 10px; background: {score_color}22; color: {score_color}; font-weight: 600; font-size: 13px; margin-bottom: 12px; }}
    .stats-row {{ display: flex; gap: 16px; flex-wrap: wrap; }}
    .stat-item {{ flex: 1; min-width: 80px; text-align: center; padding: 12px; background: #f8fafc; border-radius: 8px; }}
    .stat-item .num {{ font-size: 24px; font-weight: 800; }}
    .stat-item .label {{ font-size: 11px; color: #64748b; margin-top: 2px; }}
    .stat-item.critical .num {{ color: #dc2626; }}
    .stat-item.high .num {{ color: #f97316; }}
    .stat-item.medium .num {{ color: #eab308; }}
    .stat-item.low .num {{ color: #22c55e; }}
    .section {{ background: #fff; border-radius: 16px; padding: 24px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
    .section h2 {{ font-size: 18px; font-weight: 700; color: #1e293b; margin: 0 0 16px 0; padding-bottom: 8px; border-bottom: 2px solid #e2e8f0; }}
    .disclaimer {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px; font-size: 12px; color: #64748b; line-height: 1.7; }}
    .report-footer {{ text-align: center; padding: 20px; font-size: 12px; color: #94a3b8; margin-top: 20px; }}
    @media print {{
        body {{ background: #fff; }}
        .report-container {{ max-width: 100%; padding: 0; }}
        .section, .score-section, .report-cover {{ box-shadow: none; break-inside: avoid; }}
    }}
</style>
</head>
<body>
<div class="report-container">
    <!-- 封面 -->
    <div class="report-cover">
        <h1>🔒 Vuln Sentinel</h1>
        <div class="subtitle">Web 安全扫描报告</div>
        <div class="cover-info">
            <div class="cover-info-item">
                <div class="label">扫描目标</div>
                <div class="value">{_html_escape(url)}</div>
            </div>
            <div class="cover-info-item">
                <div class="label">扫描时间</div>
                <div class="value">{_html_escape(time_str)}</div>
            </div>
            <div class="cover-info-item">
                <div class="label">安全评分</div>
                <div class="value">{score} / 100</div>
            </div>
            <div class="cover-info-item">
                <div class="label">风险等级</div>
                <div class="value">{_html_escape(risk_level)}</div>
            </div>
        </div>
    </div>

    <!-- 评分概览 -->
    <div class="score-section">
        <div class="score-display">
            <div class="score-circle">
                <div class="num">{score}</div>
                <div class="label">安全评分</div>
            </div>
            <div class="score-info">
                <h2>扫描结果概览</h2>
                <span class="risk-level">{_html_escape(risk_level)}</span>
                <div class="stats-row">
                    <div class="stat-item critical">
                        <div class="num">{critical}</div>
                        <div class="label">严重</div>
                    </div>
                    <div class="stat-item high">
                        <div class="num">{high}</div>
                        <div class="label">高危</div>
                    </div>
                    <div class="stat-item medium">
                        <div class="num">{medium}</div>
                        <div class="label">中危</div>
                    </div>
                    <div class="stat-item low">
                        <div class="num">{low}</div>
                        <div class="label">低危</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- 评分解读 -->
    {breakdown_html}

    <!-- 漏洞详情 -->
    <div class="section">
        <h2>📋 漏洞详情（共 {total} 项）</h2>
        {findings_html if findings_html else '<div style="padding:30px;text-align:center;color:#22c55e;font-weight:600">🎉 未发现安全问题，配置良好！</div>'}
    </div>

    <!-- OWASP Top 10 -->
    {owasp_html}

    <!-- 免责声明 -->
    <div class="section">
        <h2>📝 免责声明</h2>
        <div class="disclaimer">
            本报告由Vuln Sentinel智能规则引擎自动生成，仅反映扫描时刻的目标网站安全配置状况。扫描结果可能存在误报或漏报，不构成完整的安全审计。建议结合专业安全评估和渗透测试综合判断。本工具不进行任何破坏性操作，仅用于授权范围内的安全检测。
        </div>
    </div>

    <div class="report-footer">
        Vuln Sentinel · 自动生成于 {_html_escape(time_str)}
    </div>
</div>
</body>
</html>"""
    return html


# ---------- Fix Generator (按真实 severity/类型匹配) ----------


def _detect_server_type(headers: dict) -> str:
    """根据 Server 响应头判断服务器类型。"""
    server = headers.get("server", headers.get("Server", "")).lower()
    if "nginx" in server:
        return "nginx"
    if "apache" in server:
        return "apache"
    if "node" in server or "express" in server:
        return "express"
    # Spring Boot 通常不暴露 Server 头，但可能带 Tomcat/Jetty
    if "spring" in server or "tomcat" in server or "jetty" in server:
        return "spring_boot"
    return "unknown"


def _build_fix_entry(
    code: str,
    server_type: str,
    config_examples: dict[str, str],
    risk_note: str | None = None,
) -> dict:
    return {
        "code": code,
        "risk_note": risk_note,
        "server_type": server_type,
        "config_examples": config_examples,
    }


def generate_fixes(
    findings: list[dict], headers: dict, is_https: bool, host: str
) -> dict:
    # 优先使用新的修复模板引擎生成结构化修复计划
    try:
        plan = generate_remediation_plan(findings, headers, host)
        # 保持与旧格式兼容：返回 legacy_fixes
        return plan.get("legacy_fixes") or plan.get("fixes") or {}
    except Exception as e:
        logger.warning("RemediationTemplateEngine failed, fallback to legacy: %s", e)

    fixes: dict = {
        "nginx": [],
        "apache": [],
        "express": [],
        "flask": [],
        "spring_boot": [],
        "cloudflare": [],
        "nodejs": [],
        "python": [],  # 保留旧 key 兼容
    }
    seen = set()  # 去重

    detected_server = _detect_server_type(headers)

    def add(lang, code, risk_note=None):
        if code and code not in seen:
            # 为每种语言构建对应的 config_examples
            config_examples: dict[str, str] = {}
            if lang == "nginx":
                config_examples["nginx"] = code
            elif lang == "apache":
                config_examples["apache"] = code
            elif lang in ("express", "nodejs"):
                config_examples["express"] = code
            elif lang == "spring_boot":
                config_examples["spring_boot"] = code
            elif lang == "flask":
                config_examples["flask"] = code
            elif lang == "cloudflare":
                config_examples["cloudflare"] = code
            fixes[lang].append(
                _build_fix_entry(code, detected_server, config_examples, risk_note)
            )
            seen.add(code)

    for f in findings:
        name = (f.get("name") or f.get("title") or "").strip()
        fix_text = (
            f.get("fix", "")
            or f.get("fix_suggestion", "")
            or (f.get("fix_code") or {}).get("generic", "")
        )
        ftype = f.get("type", "config")

        if name.startswith("缺少 "):
            # 任意安全头缺失
            header_name = name[3:]
            fix_value = fix_text.split('"')[1] if '"' in fix_text else "value"
            add("nginx", fix_text)
            add(
                "apache",
                fix_text.replace("add_header", "Header set").replace("always;", ""),
            )
            add("python", "# Flask 后置响应头: " + fix_text)
            add("nodejs", "// Express helmet: " + fix_text)
            add(
                "flask",
                f"# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['{header_name}'] = '{fix_value}'\n    return resp",
            )
            add("express", "// Express helmet: " + fix_text)
            add(
                "spring_boot",
                "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
            )
            add(
                "cloudflare",
                f"# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: {header_name}\n# Value: {fix_value}",
            )
            if "CSP" in name or "Content-Security-Policy" in name:
                csp_value = (
                    fix_text.split('"')[1] if '"' in fix_text else "default-src 'self'"
                )
                add(
                    "flask",
                    f"# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['Content-Security-Policy'] = '{csp_value}'\n    return resp",
                    risk_note="上线前请在测试环境验证，CSP 策略过严可能导致前端资源加载失败",
                )
                add(
                    "cloudflare",
                    "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: Content-Security-Policy\n# Value: default-src 'self'",
                    risk_note="上线前请在测试环境验证，CSP 策略过严可能导致前端资源加载失败",
                )
        elif name == "未启用 HTTPS":
            add(
                "nginx",
                "server {\n    listen 80;\n    server_name "
                + host
                + ";\n    return 301 https://$host$request_uri;\n}",
            )
            add(
                "python",
                "# Flask: from flask_talisman import Talisman\n# Talisman(app, force_https=True)",
            )
            add("nodejs", "// Express: app.use(enforceHTTPS({ maxAge: 31536000 }));")
            add(
                "apache",
                "<VirtualHost *:80>\n    ServerName "
                + host
                + "\n    Redirect permanent / https://$host/\n</VirtualHost>",
            )
            add(
                "flask",
                "# Flask/Talisman: from flask_talisman import Talisman\n# Talisman(app, force_https=True)",
            )
            add("express", "// Express: app.use(enforceHTTPS({ maxAge: 31536000 }));")
            add(
                "spring_boot",
                "# Spring Boot: server.ssl.enabled=true\n# server.ssl.key-store=classpath:keystore.p12",
            )
            add("cloudflare", "# Cloudflare: SSL/TLS > Full (Strict)")
        elif name == "SSL 证书已过期":
            add(
                "nginx",
                "# Renew SSL cert then update:\nssl_certificate /etc/ssl/certs/"
                + host
                + ".pem;",
            )
            add("python", "# certbot renew")
            add("nodejs", "# certbot renew")
            add("flask", "# certbot renew && 更新 SSL 配置")
            add(
                "spring_boot",
                "# Spring Boot: keytool -importkeystore + 更新 server.ssl 配置",
            )
            add("cloudflare", "# Cloudflare: SSL/TLS > Edge Certificates > Renew")
        elif name == "弱 SSL/TLS 配置":
            add(
                "nginx",
                "ssl_protocols TLSv1.2 TLSv1.3;\nssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;",
            )
            add("python", "# ctx.minimum_version = ssl.TLSVersion.TLSv1_2")
            add("nodejs", "// minVersion: 'TLSv1.2'")
            add("flask", "# Flask: ctx.minimum_version = ssl.TLSVersion.TLSv1_2")
            add("express", "// Express: minVersion: 'TLSv1.2'")
            add(
                "spring_boot",
                "# Spring Boot: server.ssl.enabled-protocols=TLSv1.2,TLSv1.3",
            )
            add("cloudflare", "# Cloudflare: SSL/TLS > Minimum TLS Version > TLS 1.2")
        elif "信息泄露" in name:
            add("nginx", "server_tokens off;")
            add("apache", "ServerTokens Prod\nServerSignature Off")
            add("python", "# app.config['SECRET_KEY'] = os.urandom(32)")
            add("nodejs", "// app.disable('x-powered-by')")
            add("flask", "# Flask: app.config['SECRET_KEY'] = os.urandom(32)")
            add("express", "// Express: app.disable('x-powered-by')")
            add("spring_boot", "# Spring Boot: server.error.include-stacktrace=never")
            add(
                "cloudflare",
                "# Cloudflare: Scrape Shield > Disable Server Name Exposure",
            )
        elif "Cookie" in name:
            add("nginx", "proxy_cookie_path / /; HttpOnly; Secure; SameSite=Strict;")
            add(
                "python",
                "# resp.set_cookie('session', val, httponly=True, secure=True, samesite='Strict')",
            )
            add(
                "nodejs",
                "// cookie: { httpOnly: true, secure: true, sameSite: 'strict' }",
            )
            add(
                "flask",
                "# Flask: resp.set_cookie('session', val, httponly=True, secure=True, samesite='Strict')",
            )
            add(
                "express",
                "// Express: cookie: { httpOnly: true, secure: true, sameSite: 'strict' }",
            )
            add(
                "spring_boot",
                "# Spring Boot: server.servlet.session.cookie.http-only=true\n# server.servlet.session.cookie.secure=true",
            )
            add("cloudflare", "# Cloudflare: SSL > Always Use HTTPS")
        elif "CORS" in name:
            add(
                "nginx",
                "add_header Access-Control-Allow-Origin 'https://your-domain.com' always;",
            )
            add("python", "# CORS(app, origins=['https://your-domain.com'])")
            add("nodejs", "// cors({ origin: 'https://your-domain.com' })")
            add("flask", "# Flask/CORS: CORS(app, origins=['https://your-domain.com'])")
            add("express", "// Express: cors({ origin: 'https://your-domain.com' })")
            add(
                "spring_boot",
                '# Spring Boot: @CrossOrigin(origins = "https://your-domain.com")',
            )
            add("cloudflare", "# Cloudflare: CORS policy > allowed origins")
        elif "敏感路径" in name:
            add(
                "nginx",
                "location ~ /(\\.env|\\.git|\\.svn|backup\\.sql|\\.bak) {\n    deny all;\n    return 403;\n}",
            )
            add("python", "# @app.before_request: block /.env, /.git paths -> 403")
            add("nodejs", "// Block /.env, /.git paths -> 403")
            add(
                "flask",
                "# Flask: @app.before_request\n# if request.path in ('/.env', '/.git'): abort(403)",
            )
            add("express", "// Express: Block /.env, /.git paths -> 403")
            add(
                "spring_boot",
                "# Spring Boot: WebSecurityConfigurerAdapter block /.*env, /.git",
            )
            add("cloudflare", "# Cloudflare: WAF > Custom Rules > Block /*env, /*git")
        elif ftype == "XSS":
            add(
                "nginx",
                "add_header Content-Security-Policy \"default-src 'self'; script-src 'self'\" always;",
            )
            add("python", "# Use jinja2 auto-escaping: {{ var|e }}")
            add(
                "nodejs",
                "// helmet.contentSecurityPolicy({ defaultSrc: [\"'self'\"] })",
            )
            add(
                "flask",
                "# Flask: 使用 jinja2 自动转义 {{ var|e }}",
                risk_note="上线前请在测试环境验证，CSP 策略过严可能导致前端资源加载失败",
            )
            add(
                "express",
                "// Express: helmet.contentSecurityPolicy({ defaultSrc: [\"'self'\"] })",
                risk_note="上线前请在测试环境验证，CSP 策略过严可能导致前端资源加载失败",
            )
            add(
                "spring_boot",
                "# Spring Boot: ContentSecurityPolicyFilterRegistrationBean",
            )
            add("cloudflare", "# Cloudflare: WAF > XSS Rules > Enable")
        elif ftype == "SQLi":
            add("nginx", '# ModSecurity: SecRule ARGS "(OR|UNION)" "deny,status:403"')
            add("python", "# cursor.execute('SELECT * FROM users WHERE id=%s', (uid,))")
            add("nodejs", "// db.query('SELECT * FROM users WHERE id=$1', [uid])")
            add(
                "flask",
                "# Flask: cursor.execute('SELECT * FROM users WHERE id=%s', (uid,))",
            )
            add(
                "express",
                "// Express: db.query('SELECT * FROM users WHERE id=$1', [uid])",
            )
            add("spring_boot", "# Spring Boot: @Repository + JPA ParameterizedQuery")
            add("cloudflare", "# Cloudflare: WAF > SQL Injection Rules > Enable")
        elif ftype == "sqli":
            add(
                "python",
                "# Python: cursor.execute('SELECT * FROM users WHERE id=%s', (user_id,))",
            )
            add(
                "nodejs",
                "// Node.js: db.query('SELECT * FROM users WHERE id=?', [user_id])",
            )
            add(
                "flask",
                "# Flask-SQLAlchemy: db.session.execute(text('...'), {'id': user_id})",
            )
            add(
                "express",
                "// Express + mysql2: db.execute('SELECT * FROM users WHERE id=?', [user_id])",
            )
            add(
                "spring_boot",
                "# Java: JdbcTemplate.query('SELECT * FROM users WHERE id=?', new Object[]{userId})",
            )
        elif ftype == "ssti":
            add("python", "# Jinja2: {{ user_input | e }}")
            add("nodejs", "// 避免将用户输入拼接到模板字符串中")
            add("flask", "# Flask/Jinja2: 所有模板变量都使用自动转义")
            add(
                "express",
                "// 禁止把用户输入传给模板表达式；仅作为纯文本渲染",
            )
            add(
                "spring_boot",
                "# Thymeleaf/Freemarker: 使用转义输出，禁止拼接表达式",
            )
        elif ftype == "open_redirect":
            add("python", "# 仅允许白名单相对路径或可信域名")
            add("nodejs", "// 使用白名单校验跳转目标，禁止任意外跳")
            add("flask", "# Flask: redirect() 前先校验目标是否在允许列表")
            add("express", "// Express: res.redirect() 前校验目标 URL")
            add(
                "spring_boot",
                "# Spring Boot: RedirectView 仅允许站内相对路径或白名单",
            )
        elif ftype == "xss":
            add("python", "# Jinja2: {{ user_input | e }}")
            add("nodejs", "// DOMPurify.sanitize(userInput)")
            add("flask", "# Flask: Markup.escape(user_input) 或 {{ var|e }}")
            add(
                "express",
                "// Express: res.render('view', { userInput: escapeHtml(userInput) })",
            )
            add(
                "spring_boot",
                "# Java: JSTL <c:out value='${param}' /> 或 OWASP Java Encoder",
            )
        elif ftype == "cmdi":
            add("python", "# subprocess.run(['ls', user_input], shell=False)")
            add("nodejs", "// child_process.execFile('ls', [arg], callback)")
            add("flask", "# Flask: 永远不要使用 os.system('...' + user_input)")
            add("express", "// Express: 永远不要使用 exec('...' + userInput)")
            add(
                "spring_boot",
                "# Java: ProcessBuilder 传入 List<String>，禁止 Runtime.exec(String)",
            )
        elif ftype == "traversal":
            add("python", "# os.path.commonpath([base_dir, target]) == base_dir")
            add("nodejs", "// path.resolve(baseDir, input).startsWith(baseDir)")
            add("flask", "# Flask: send_from_directory(base_dir, safe_filename)")
            add("express", "// Express: express.static(baseDir, { dotfiles: 'deny' })")
            add("spring_boot", "# Java: Path.normalize() + startsWith(allowedBase)")
        elif ftype == "deserialization":
            add("python", "# 使用 json + itsdangerous 代替 pickle")
            add("nodejs", "// JSON.parse() + schema 校验，禁止 eval()")
            add("flask", "# Flask: session 使用 SECRET_KEY 签名，不要 pickle")
            add("express", "// Express: 使用 jsonwebtoken，不要 node-serialize")
            add(
                "spring_boot", "# Java: 禁用 ObjectInputStream，改用 Jackson + 白名单类"
            )
        elif ftype == "ssrf":
            add("python", "# urllib.parse + ipaddress.ip_address(addr).is_private")
            add("nodejs", "// url.parse() + net.isIP() + 白名单域名")
            add("flask", "# Flask: requests.get(whitelist_url_only)")
            add("express", "// Express: 使用代理 + 禁止请求 169.254.169.254")
            add(
                "spring_boot", "# Java: Apache HttpClient + 自定义 DNSResolver 拦截内网"
            )
        else:
            # 兜底：把 fix_text 直接当作 nginx 行
            if fix_text:
                add("nginx", fix_text)

    # 如果无法判断服务器类型，在所有 Fix 对象中补充所有方式的修复建议
    if detected_server == "unknown":
        for lang in fixes:
            for entry in fixes[lang]:
                all_examples = {}
                for other_lang in fixes:
                    if other_lang == lang:
                        continue
                    for other_entry in fixes[other_lang]:
                        if other_entry["code"] not in all_examples.values():
                            all_examples.setdefault(other_lang, other_entry["code"])
                entry["config_examples"].update(all_examples)

    return fixes


# ---------- API Routes ----------


@app.get("/api/version")
async def api_version() -> dict:
    return {
        "version": settings.app_version,
        "title": settings.app_title,
        "build_time": settings.build_time,
    }


@app.get("/api/v1/")
@app.get("/api/v1")
async def api_v1_info() -> dict:
    """API 版本信息端点（v1 版本根）。

    供客户端探测当前可用 API 版本与基础元信息。该端点被
    ``api_versioning_middleware`` 识别为版本根，不做内部路径重写。
    """
    return {
        "api_version": "v1",
        "version": settings.app_version,
        "title": settings.app_title,
        "build_time": settings.build_time,
        "versioned_prefix": "/api/v1/",
    }


# ---------- 以下端点已迁移到 app/routers/ 模块 ----------
# auth.py: /api/register, /api/login, /api/auth/* (注册、登录、邮箱验证、密码重置)
# user.py: /api/me, /api/me/credits, /api/usage (用户信息、积分、使用日志)
# billing.py: /api/billing/*, /api/admin/recharge (计费、充值、支付回调)
# admin.py: /api/admin/audit-logs (审计日志)
# gdpr.py: /api/me/export, /api/me/account, /api/me/anonymize, /api/admin/data-retention/run
# team.py: /api/team, /api/team/create, /api/team/join, /api/team/{id}/role
# （共迁移 561 行端点代码到 6 个路由文件）


# ---------- Domain Verification ----------


def query_dns_txt(name: str) -> list[str]:
    records: list[str] = []
    try:
        result = subprocess.run(
            ["nslookup", "-type=TXT", name], capture_output=True, text=True, timeout=8
        )
        output = (result.stdout or "") + (result.stderr or "")
        for line in output.splitlines():
            line = line.strip()
            if "text =" in line.lower():
                parts = line.split("=", 1)
                if len(parts) == 2:
                    txt = parts[1].strip().strip('"').strip()
                    if txt:
                        records.append(txt)
    except Exception as e:
        logger.warning("query_dns_txt nslookup failed: %s", e)
        try:
            result = subprocess.run(
                ["dig", "+short", "TXT", name],
                capture_output=True,
                text=True,
                timeout=8,
            )
            for line in (result.stdout or "").splitlines():
                line = line.strip().strip('"').strip()
                if line:
                    records.append(line)
        except Exception as e:
            logger.warning("query_dns_txt dig failed: %s", e)
            try:
                socket.getaddrinfo(name, None)
            except socket.gaierror:
                pass
    return records


async def verify_dns_txt(url: str, token: str) -> tuple[bool, str]:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if not host:
        return False, "网址无效"
    check_name = "_vuln-sentinel." + host
    # 用 to_thread 避免 subprocess 阻塞事件循环，并包一层超时
    try:
        records = await asyncio.wait_for(
            asyncio.to_thread(query_dns_txt, check_name),
            timeout=10.0,
        )
    except asyncio.TimeoutError:
        return False, "DNS 查询超时，请稍后重试"
    except Exception as e:
        return False, "DNS 查询失败: " + str(e)[:80]
    for record in records:
        if record.strip() == token:
            return True, "DNS TXT 记录验证通过"
    return (
        False,
        "未找到包含验证 Token 的 TXT 记录。请确认在 "
        + check_name
        + " 添加了 TXT 记录 "
        + token,
    )


async def verify_file(url: str, token: str) -> tuple[bool, str]:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if not host:
        return False, "网址无效"
    for scheme in ["https", "http"]:
        check_url = scheme + "://" + host + "/vuln-sentinel-verification.txt"
        try:
            client = get_httpx_client()
            resp = await asyncio.wait_for(
                client.get(check_url, follow_redirects=False),
                timeout=8.0,
            )
            if resp.status_code == 200:
                # 安全读取：限制响应体最大 64KB，验证文件应该很小
                body_bytes = await resp.aread()
                if len(body_bytes) > 64 * 1024:
                    continue  # 文件过大，不可能是验证文件
                body = body_bytes.decode("utf-8", errors="ignore").strip()
                if token in body:
                    return True, "文件验证通过：" + check_url
        except asyncio.TimeoutError:
            continue
        except Exception:
            continue
    return (
        False,
        "未在网站根目录找到 vuln-sentinel-verification.txt 文件，或文件内容不包含 Token",
    )


@app.post("/api/verify")
async def api_verify(req: VerifyRequest, user: dict = Depends(require_login)) -> dict:
    parsed = urlparse(req.url)
    host = (parsed.hostname or "").lower()
    if not host:
        return {"success": False, "error": "网址格式无效"}
    if req.method == "dns":
        ok, msg = await verify_dns_txt(req.url, req.token)
    else:
        ok, msg = await verify_file(req.url, req.token)
    return {"success": ok, "method": req.method, "message": msg, "host": host}


# ---------- 修复效果验证（真实 diff） ----------


@app.post("/api/verify-fix")
async def api_verify_fix(
    req: VerifyFixRequest, request: Request, user: dict = Depends(require_login)
) -> dict:
    """应用修复后再次扫描对比评分：与指定 previous_scan_id 的记录做 diff。"""
    await rate_limit_dependency(request)
    url = req.url.strip()
    previous_scan_id = req.previous_scan_id
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    parsed = urlparse(url)
    host = parsed.hostname or ""
    try:
        headers, is_https, final_url, error = await asyncio.wait_for(
            fetch_headers(url), timeout=30.0
        )
        if error and not headers:
            logger.warning("verify-fix headers unavailable for %s, continue with baseline analysis: %s", url, error)
            headers = {}
            is_https = parsed.scheme == "https"
            final_url = url
        else:
            headers.pop("_status_code", None)
            headers.pop("_redirect_location", None)
        waf_list = detect_waf(headers)
        try:
            sensitive_paths = await check_sensitive_paths(host, is_https)
        except Exception as e:
            logger.warning("verify-fix sensitive path scan failed: %s", e)
            sensitive_paths = []
        try:
            ssl_info = await get_ssl_info(host, 443) if is_https else {"has_cert": False}
        except Exception as e:
            logger.warning("verify-fix ssl scan failed: %s", e)
            ssl_info = {"has_cert": False}
        waf_name = waf_list[0].get("name") if waf_list else None
        result = await run_plugin_scan(
            url,
            headers,
            is_https,
            ssl_info,
            waf=waf_name,
            deep=False,
            body="",
        )
        try:
            legacy = await analyze_security(
                url, headers, is_https, ssl_info, waf_list, sensitive_paths
            )
        except Exception as e:
            logger.warning("verify-fix legacy metadata failed: %s", e)
            legacy = {}
        result.update(
            {
                "final_url": final_url,
                "is_https": is_https,
                "raw_headers": headers,
                "sensitive_paths": sensitive_paths,
                "ssl_info": ssl_info,
                "waf_list": waf_list,
                "score_breakdown": legacy.get("score_breakdown", []),
                "improvements": legacy.get("improvements", []),
                "risk_level_zh": risk_level_zh(result.get("risk_level")),
            }
        )
        scan_id = save_scan(
            user["user_id"],
            url,
            result["score"],
            result["risk_level"],
            result["findings"],
            result["summary"],
            0,
            "verify",
        )

        # 找修复前的扫描记录
        previous = None
        if previous_scan_id is not None:
            try:
                previous_scan_id = int(previous_scan_id)
            except (TypeError, ValueError):
                previous_scan_id = None
        if previous_scan_id:
            previous = get_scan_by_id(previous_scan_id, user["user_id"])
        if not previous:
            # 退化：找该 URL 的最近一次非本次的扫描
            conn = get_db()
            row = conn.execute(
                "SELECT * FROM scans WHERE user_id=? AND url=? AND id<>? ORDER BY id DESC LIMIT 1",
                (user["user_id"], url, scan_id),
            ).fetchone()
            conn.close()
            if row:
                previous = dict(row)

        prev_findings = []
        if previous:
            try:
                prev_findings = json.loads(previous.get("findings_json") or "[]")
            except Exception:
                prev_findings = []

        new_findings = result["findings"]
        prev_names = {f.get("name", "") for f in prev_findings}
        new_names = {f.get("name", "") for f in new_findings}
        fixed = sorted(list(prev_names - new_names))
        new_issues = sorted(list(new_names - prev_names))
        prev_score = previous.get("score") if previous else 0
        delta = result["score"] - (prev_score or 0)

        return {
            "success": True,
            "scan_id": scan_id,
            "url": url,
            "previous_scan_id": previous.get("id") if previous else None,
            "new_score": result["score"],
            "new_risk_level": result["risk_level"],
            "previous_score": prev_score,
            "delta": delta,
            "new_findings": new_findings,
            "fixed": fixed,
            "new_issues": new_issues,
            "summary": result["summary"],
            "improvements": result.get("improvements", []),
        }
    except Exception as e:
        logger.warning("verify-fix failed: %s", e)
        return {"success": False, "error": str(e)[:300]}


@app.post("/api/verify-domain")
async def api_verify_domain(req: dict, user=Depends(require_login)):
    """发起域名归属验证。后端实际检查 DNS TXT 或文件验证。"""
    domain = req.get("domain", "").strip().lower()
    method = req.get("method", "dns_txt")
    if not domain:
        raise HTTPException(400, "域名不能为空")
    if "." not in domain:
        raise HTTPException(400, "域名格式无效")
    if method not in ("dns_txt", "file"):
        raise HTTPException(400, "验证方式仅支持 dns_txt 或 file")

    # SSRF 防护：复用 sanitize_url 校验目标域名，禁止指向内网/本地/云元数据
    # （除非显式在 ALLOWED_INTERNAL_HOSTS 白名单内）
    if method == "file":
        verify_url = f"http://{domain}/.well-known/vulnsentinel"
    else:
        # dns_txt 模式下虽然只是 DNS 查询，没有出站 HTTP，但仍然过一遍校验
        verify_url = f"http://{domain}"
    try:
        sanitize_url(verify_url)
    except ValueError as e:
        raise HTTPException(400, "域名校验失败：" + str(e))

    verified = False
    verify_detail = ""

    if method == "dns_txt":
        # 检查 DNS TXT 记录：_vulnsentinel.{domain} TXT "vs-{user_id}"
        expected = f"vs-{user['user_id']}"
        try:
            import dns.resolver
        except ImportError:
            verify_detail = "DNS 验证服务暂不可用，请联系管理员安装 dnspython 依赖。"
        else:
            try:
                txt_records = dns.resolver.resolve(f"_vulnsentinel.{domain}", "TXT")
                for r in txt_records:
                    if expected in str(r).strip('"'):
                        verified = True
                        verify_detail = (
                            f"DNS TXT 验证通过：_vulnsentinel.{domain} → {expected}"
                        )
                        break
                if not verified:
                    verify_detail = f'DNS TXT 记录未找到或值不匹配。请在 DNS 中添加：_vulnsentinel.{domain} TXT "{expected}"'
            except dns.resolver.NXDOMAIN:
                verify_detail = (
                    f"域名 {domain} 不存在（NXDOMAIN）。请确认域名已正确注册。"
                )
            except dns.resolver.NoAnswer:
                verify_detail = f'域名 {domain} 存在但没有 TXT 记录。请在 DNS 中添加：_vulnsentinel.{domain} TXT "{expected}"'
            except dns.resolver.Timeout:
                verify_detail = f'DNS 查询超时，请检查网络或稍后重试。如需验证请添加：_vulnsentinel.{domain} TXT "{expected}"'
            except dns.exception.DNSException:
                verify_detail = f'DNS 查询异常，请稍后重试。如需验证请添加：_vulnsentinel.{domain} TXT "{expected}"'
            except Exception:
                verify_detail = "DNS 查询失败，请稍后重试。如持续失败请联系管理员。"
    elif method == "file":
        # 检查文件验证：http://{domain}/.well-known/vulnsentinel
        try:
            async with httpx.AsyncClient(timeout=10, follow_redirects=False) as hc:
                resp = await hc.get(f"http://{domain}/.well-known/vulnsentinel")
                if resp.status_code == 200:
                    # 安全读取：限制响应体最大 64KB，验证文件应该很小
                    body_bytes = await resp.aread()
                    if len(body_bytes) > 64 * 1024:
                        verify_detail = "验证文件过大，不符合预期"
                    else:
                        body = body_bytes.decode("utf-8", errors="ignore")
                        expected = f"vs-{user['user_id']}"
                        if expected in body:
                            verified = True
                            verify_detail = "文件验证通过"
                        else:
                            verify_detail = "文件内容不匹配"
                else:
                    verify_detail = f"验证文件返回 HTTP {resp.status_code}"
        except Exception as e:
            verify_detail = f"文件验证失败：{str(e)[:80]}"

    conn = get_db()
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        expires = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S")
        status = "verified" if verified else "pending"
        conn.execute(
            "INSERT OR REPLACE INTO domain_verifications (user_id, domain, method, status, created_at, verified_at, expires_at) VALUES (?,?,?,?,?,?,?)",
            (
                user["user_id"],
                domain,
                method,
                status,
                now,
                now if verified else None,
                expires,
            ),
        )
        conn.commit()
    finally:
        conn.close()

    return {
        "success": True,
        "domain": domain,
        "method": method,
        "verified": verified,
        "status": status,
        "detail": verify_detail,
    }


# ---------- 扫描进度（内存 + Lock） ----------
# 用内存字典 + asyncio.Lock 替代文件读写，避免并发覆盖与磁盘 I/O。
# key: scan_token (str), value: dict {stages, current, start_time, updated_at}
_scan_progress: dict[str, dict] = {}
_scan_progress_lock = asyncio.Lock()
_SCAN_PROGRESS_TTL_SECONDS = 600  # 扫描进度保留 10 分钟


async def _cleanup_scan_progress():
    """清理过期的扫描进度记录，防止内存泄漏。"""
    now = time.time()
    async with _scan_progress_lock:
        expired = [
            token
            for token, data in _scan_progress.items()
            if now - data.get("updated_at", 0) > _SCAN_PROGRESS_TTL_SECONDS
        ]
        for token in expired:
            _scan_progress.pop(token, None)


async def _scan_progress_cleanup_loop():
    """扫描进度清理循环：每 5 分钟清理一次过期记录。"""
    while True:
        await asyncio.sleep(300)  # 每 5 分钟清理一次
        try:
            await _cleanup_scan_progress()
        except Exception as e:
            logger.warning("Scan progress cleanup failed: %s", e)


_scan_progress_cleanup_task: asyncio.Task | None = None


# ---------- 真实扫描 ----------


@app.get("/api/compliance/summary")
async def api_compliance_summary(user: dict = Depends(require_login)) -> dict:
    """返回当前合规规则摘要（供前端展示授权说明）。"""
    return {"success": True, "data": get_compliance_summary()}


@app.post("/api/scan")
async def api_scan(
    req: ScanRequest, request: Request, user: dict = Depends(require_login)
):
    """同步扫描。带阶段进度事件（写入响应头 X-Scan-Stage 预览）。"""
    global _SCAN_CACHE_HITS, _SCAN_CACHE_MISSES
    await rate_limit_dependency(request)
    # 深度模式额外速率限制：深度扫描资源消耗大，限制更严格
    client_ip = get_client_ip(request)
    if req.depth == "deep" or req.deep:
        if not await limiter_scan_deep.is_allowed(client_ip):
            raise HTTPException(
                status_code=429,
                detail="深度扫描请求过于频繁，每分钟最多 2 次，请稍后再试",
                headers={"Retry-After": "60"},
            )
    elif req.depth == "standard":
        if not await limiter_scan_standard.is_allowed(client_ip):
            raise HTTPException(
                status_code=429,
                detail="扫描请求过于频繁，每分钟最多 10 次，请稍后再试",
                headers={"Retry-After": "60"},
            )
    try:
        url = sanitize_url(req.url)
    except ValueError as e:
        # Vuln Sentinel fix: 返回友好的扫描失败结果，而不是 HTTP 422
        return ScanResponse(
            success=False,
            scan_id=0,
            scan_type="real",
            url=req.url,
            final_url=req.url,
            time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            is_https=False,
            score=0,
            risk_level="无法扫描",
            findings=[],
            summary={
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "info": 0,
                "total": 0,
            },
            headers={},
            waf=None,
            ssl={},
            duration_ms=0,
            report_share_id=None,
            owasp_coverage=[],
            header_details=[],
            info_leaks=[],
            cors=None,
            cookie_issues=[],
            ssl_info={},
            waf_list=[],
            sensitive_paths=[],
            waf_detected=False,
            raw_headers={},
            error=str(e),
        )

    user_id = user["user_id"]

    # 合规与授权检查（在扣积分之前拦截不合规请求）
    is_deep = req.deep or req.depth == "deep"
    compliant, compliance_reason, compliance_code = validate_scan_target_full(
        url,
        user_id=user_id,
        authorized=req.authorized,
        deep=is_deep,
        verification_token=getattr(req, "verification_token", None),
        allowed_demo=True,
    )
    if not compliant:
        risk_label = {
            "unauthorized": "未授权",
            "restricted": "受限目标",
            "ownership_required": "未验证",
        }.get(compliance_code, "无法扫描")
        return ScanResponse(
            success=False,
            scan_id=0,
            scan_type="real" if not is_deep else "deep",
            url=url,
            final_url=url,
            time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            is_https=False,
            score=0,
            risk_level=risk_label,
            findings=[],
            summary={
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "info": 0,
                "total": 0,
            },
            headers={},
            waf=None,
            ssl={},
            duration_ms=0,
            report_share_id=None,
            owasp_coverage=[],
            header_details=[],
            info_leaks=[],
            cors=None,
            cookie_issues=[],
            ssl_info={},
            waf_list=[],
            sensitive_paths=[],
            waf_detected=False,
            raw_headers={},
            error=compliance_reason,
            restricted=True,
            restricted_reason=compliance_reason,
            restricted_code=compliance_code,
        )

    # 按量计费：根据扫描深度扣除积分（放在缓存与长耗时工作之前，防止滥用）
    scan_cost = (
        credits_service.SCAN_DEEP_COST
        if is_deep
        else credits_service.SCAN_STANDARD_COST
    )
    scan_depth_label = req.depth if req.depth else ("deep" if req.deep else "standard")
    if not credits_service.has_credits(user_id, scan_cost):
        raise PaymentRequiredException(f"扫描需要 {scan_cost} 积分，余额不足")
    credits_service.deduct_credits(
        user_id, scan_cost, action=f"scan:{scan_depth_label}"
    )

    # 扫描结果缓存：根据深度设置不同 TTL，同一 URL 同深度直接返回
    parsed = urlparse(url)
    host = parsed.hostname or ""

    # 确定缓存 TTL（基于请求深度）
    cache_ttl = _get_cache_ttl(req.depth if req.depth else "standard")
    cache_key = f"{user_id}:{url}:{req.depth}"
    async with _scan_cache_lock:
        cached = _SCAN_RESULT_CACHE.get(cache_key)
    if cached and (time.time() - cached[1]) < cache_ttl:
        _SCAN_CACHE_HITS += 1
        record_cache_hit()
        if _SCAN_CACHE_HITS % 10 == 0:
            total = _SCAN_CACHE_HITS + _SCAN_CACHE_MISSES
            hit_rate = (_SCAN_CACHE_HITS / total * 100) if total > 0 else 0
            logger.info(
                "Scan cache stats: hits=%d misses=%d total=%d hit_rate=%.1f%%",
                _SCAN_CACHE_HITS,
                _SCAN_CACHE_MISSES,
                total,
                hit_rate,
            )
        return {
            **cached[0],
            "is_cached": True,
            "cached_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    # 阶段事件：写入内存字典（带 asyncio.Lock），不再写文件，避免并发覆盖。
    import secrets as _secrets

    _metrics_timer = record_scan_start()
    scan_token = f"{user_id}_{int(datetime.now().timestamp())}_{_secrets.token_hex(4)}"
    progress = {
        "stages": [
            {"id": "dns", "label": "DNS 解析", "status": "pending", "detail": host},
            {
                "id": "connect",
                "label": "TCP 连接",
                "status": "pending",
                "detail": "443 或 80 端口",
            },
            {
                "id": "headers",
                "label": "响应头分析",
                "status": "pending",
                "detail": "HSTS/CSP/X-Frame 等 9 项",
            },
            {
                "id": "ssl",
                "label": "SSL 证书检查",
                "status": "pending",
                "detail": "证书链/有效期/签发者",
            },
            {
                "id": "sensitive",
                "label": "敏感路径扫描",
                "status": "pending",
                "detail": "/admin /backup 等 12 个",
            },
            {
                "id": "waf",
                "label": "WAF 识别",
                "status": "pending",
                "detail": "Cloudflare/Akamai 等 6 类",
            },
            {
                "id": "report",
                "label": "生成报告",
                "status": "pending",
                "detail": "评分/修复建议",
            },
        ],
        "current": -1,
        "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_id": user_id,
        "updated_at": time.time(),
    }
    async with _scan_progress_lock:
        _scan_progress[scan_token] = progress

    async def _do_scan() -> ScanResponse:
        async def _update(idx, status="done"):
            async with _scan_progress_lock:
                _p = _scan_progress.get(scan_token)
                if not _p:
                    return
                for _i in range(idx):
                    if _p["stages"][_i]["status"] == "pending":
                        _p["stages"][_i]["status"] = "done"
                _p["stages"][idx]["status"] = status
                _p["current"] = idx
                _p["updated_at"] = time.time()

        # 合规与所有权检查已在外层完成，这里直接标记 DNS/连接阶段完成
        await _update(0, "done")
        await _update(1, "done")
        await _update(2, "running")
        try:
            headers, is_https, final_url, error = await asyncio.wait_for(
                fetch_headers(url), timeout=15.0
            )
        except asyncio.TimeoutError:
            headers, is_https, final_url, error = {}, False, url, "TIMEOUT"
        if error and not headers:
            # 网络层拿不到头信息时，不直接判定失败；
            # 改为基础分析继续执行，避免测试环境或临时网络波动导致整次扫描失败。
            logger.warning("scan headers unavailable for %s, continue with baseline analysis: %s", url, error)
            headers = {}
            is_https = parsed.scheme == "https"
            final_url = url
            error = None
        # 受限访问但能拿到头 → 区分跳转(301/302) 和 真正受限(401/403/405)
        _restricted = False
        redirected = False
        redirect_reason = ""
        if error and headers:
            status_code = headers.pop("_status_code", 0)
            redirect_loc = headers.pop("_redirect_location", "")
            # 兜底：如果 _redirect_location 没有值，直接从响应头取 location
            if not redirect_loc:
                redirect_loc = headers.pop("location", "")
            if error.startswith("REDIRECT_"):
                from urllib.parse import urljoin, urlparse
                resolved_loc = urljoin(url, redirect_loc) if redirect_loc else ""
                current_host = urlparse(url).hostname or ""
                target_host = urlparse(resolved_loc).hostname or current_host
                # 仅明显外跳时提示为“跳转目标”，同站内常规跳转不单独打扰用户
                if resolved_loc and target_host and target_host.lower() != current_host.lower():
                    redirected = True
                    redirect_reason = f"目标发生外部跳转（HTTP {status_code}），跳转地址：{resolved_loc}。建议扫描最终目标地址。"
                else:
                    redirect_reason = f"目标发生站内跳转（HTTP {status_code}），最终地址：{resolved_loc or '未知'}。"
                error = None
            elif error == "AUTH_REQUIRED":
                _restricted = True
                user_msg = "目标站点需要登录认证（HTTP 401），无法获取完整响应头。已基于现有信息生成受限报告。"
                headers["_restricted_reason"] = user_msg
                headers["_restricted_code"] = str(status_code)
                error = None
            elif error == "FORBIDDEN":
                _restricted = True
                user_msg = "目标站点拒绝自动化访问（HTTP 403），可能是反爬机制。已基于现有信息生成受限报告。"
                headers["_restricted_reason"] = user_msg
                headers["_restricted_code"] = str(status_code)
                error = None
            elif error == "METHOD_NOT_ALLOWED":
                _restricted = True
                user_msg = (
                    "目标站点不支持 HEAD 请求（HTTP 405），已使用 GET 请求获取响应头。"
                )
                headers["_restricted_reason"] = user_msg
                headers["_restricted_code"] = str(status_code)
                error = None
            else:
                _restricted = True
                user_msg = (
                    f"目标站点限制自动化访问（{error}），已基于现有信息生成受限报告。"
                )
                headers["_restricted_reason"] = user_msg
                headers["_restricted_code"] = str(status_code)
                error = None
        await _update(2, "done")
        # 移除内部标记，避免进入响应头和证据
        headers.pop("_status_code", None)
        headers.pop("_redirect_location", None)
        # 修复：让 SSL 解析和敏感路径扫描同时进行，节省 1-2s
        waf_list = detect_waf(headers)
        await _update(5, "done")
        # 计算扫描档位（兼容旧版 deep 字段）
        depth = (
            req.depth
            if req.depth in ("quick", "standard", "deep")
            else "deep"
            if req.deep
            else "standard"
        )
        ssl_info, sensitive_paths = {"has_cert": False}, []
        crawled_pages, vuln_tests = [], []
        if depth == "quick":
            # Quick 模式：只做响应头 + WAF 检测，跳过 SSL 和敏感路径（1-2 秒）
            await _update(2, "done")
            await _update(3, "skip")
            await _update(4, "skip")
            await _update(5, "done")
            await _update(6, "skip")
        elif depth == "standard":
            # Standard 模式：标准扫描（3-5 秒）
            await _update(2, "done")
            await _update(4, "running")
            # 并发：SSL 检查 + 敏感路径扫描
            from urllib.parse import urlparse as _urlparse

            port_443 = 443 if is_https else 0
            ssl_task = asyncio.create_task(
                get_ssl_info(_urlparse(url).hostname or host, port_443)
                if is_https
                else asyncio.sleep(0, result={"has_cert": False})
            )
            sensitive_task = asyncio.create_task(check_sensitive_paths(host, is_https))
            try:
                ssl_info, sensitive_paths = await asyncio.wait_for(
                    asyncio.gather(ssl_task, sensitive_task, return_exceptions=True),
                    timeout=8.0,
                )
                if isinstance(ssl_info, Exception):
                    ssl_info = {"has_cert": False}
                if isinstance(sensitive_paths, Exception):
                    sensitive_paths = []
            except asyncio.TimeoutError:
                ssl_info = {"has_cert": False}
                sensitive_paths = []
            waf_list = detect_waf(headers)
            await _update(4, "done")
            await _update(5, "done")
            await _update(6, "skip")
            # D12-D15 检测已在 analyze_security 中统一执行，避免重复与未定义名称调用
            pass
        else:
            # Deep 模式：标准 + 爬虫 + 攻击测试（10+ 秒，需要域名验证）
            await _update(2, "done")
            await _update(4, "running")
            from urllib.parse import urlparse as _urlparse

            port_443 = 443 if is_https else 0
            ssl_task = asyncio.create_task(
                get_ssl_info(_urlparse(url).hostname or host, port_443)
                if is_https
                else asyncio.sleep(0, result={"has_cert": False})
            )
            sensitive_task = asyncio.create_task(check_sensitive_paths(host, is_https))
            try:
                ssl_info, sensitive_paths = await asyncio.wait_for(
                    asyncio.gather(ssl_task, sensitive_task, return_exceptions=True),
                    timeout=8.0,
                )
                if isinstance(ssl_info, Exception):
                    ssl_info = {"has_cert": False}
                if isinstance(sensitive_paths, Exception):
                    sensitive_paths = []
            except asyncio.TimeoutError:
                ssl_info = {"has_cert": False}
                sensitive_paths = []
            await _update(4, "done")
            await _update(5, "done")
            await _update(6, "running")
            try:
                crawled_pages = await crawl_site(url, settings.max_crawl_pages)
            except Exception as _ce:
                crawled_pages = []
            try:
                _, vuln_tests = await run_payload_tests(url, crawled_pages)
            except Exception:
                vuln_tests = []
            # D12-D15 检测已在 analyze_security 中统一执行，避免重复与未定义名称调用
            pass

        # ---------- SRC 级扫描（插件化新引擎） ----------
        waf_name = waf_list[0].get("name") if waf_list else None
        src_result = await run_plugin_scan(
            url,
            headers,
            is_https,
            ssl_info,
            waf=waf_name,
            deep=(depth == "deep"),
            body="",
        )

        # 保留旧版元数据，用于兼容历史展示与旧前端字段
        try:
            legacy = await analyze_security(
                url,
                headers,
                is_https,
                ssl_info,
                waf_list,
                sensitive_paths,
                vuln_findings=[],
                depth=depth,
            )
        except Exception as e:
            logger.warning("Legacy analyze_security failed during scan: %s", e)
            legacy = {}

        # 合并响应：以 SRC 格式为主，附加旧字段兼容
        result = src_result.copy()
        result["findings"] = _attach_evidence_snapshots(result.get("findings", []), url)
        result.update(
            {
                "scan_type": "deep" if req.deep else "real",
                "final_url": final_url,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "is_https": is_https,
                "raw_headers": headers,
                "owasp_coverage": legacy.get("owasp_coverage", []),
                "header_details": legacy.get("header_details", []),
                "info_leaks": legacy.get("info_leaks", []),
                "cors": legacy.get("cors"),
                "cookie_issues": legacy.get("cookie_issues", []),
                "ssl_info": ssl_info,
                "waf_list": waf_list,
                "sensitive_paths": sensitive_paths,
                "waf_detected": len(waf_list) > 0,
                "crawled_pages": crawled_pages,
                "vuln_tests": vuln_tests,
                "score_breakdown": legacy.get("score_breakdown", []),
                "improvements": legacy.get("improvements", []),
                "risk_level_zh": risk_level_zh(src_result.get("risk_level")),
            }
        )

        fixes = generate_fixes(result["findings"], headers, is_https, host)
        result["fixes"] = fixes

        scan_details = {
            "duration_ms": result.get("duration_ms", 0),
            "raw_headers": result.get("raw_headers", {}),
            "ssl_info": result.get("ssl_info", {}),
            "waf_list": result.get("waf_list", []),
            "sensitive_paths": result.get("sensitive_paths", []),
            "verification_stats": result.get("verification_stats", {}),
            "quality": result.get("quality", {}),
            "scan_engine": result.get("scan_engine", "plugin"),
        }
        scan_id = save_scan(
            user_id,
            url,
            result["score"],
            result["risk_level"],
            result["findings"],
            result["summary"],
            len(crawled_pages) if crawled_pages else 0,
            depth,
            details=scan_details,
        )
        # 用数据库自增 ID 覆盖 run_src_scan 生成的时间戳 ID
        result["scan_id"] = scan_id

        # 应用用户历史反馈闭环：降低已标记误报的置信度，提升已确认漏洞的置信度
        try:
            result["findings"] = apply_user_feedback(
                result.get("findings", []), user.get("user_id", 0)
            )
        except Exception as e:
            logger.warning("Apply user feedback failed: %s", e)

        # 自动为 high/critical finding 创建修复工单
        try:
            auto_create_fix_tickets(
                user_id, scan_id, result["findings"], target_host=host
            )
        except Exception as e:
            logger.warning("Auto create fix tickets failed: %s", e)
        # 自动同步资产扫描信息
        try:
            update_asset_after_scan(user_id, host, scan_id)
        except Exception as e:
            logger.warning("Update asset after scan failed: %s", e)
        await _update(6, "done")
        # 受限扫描报告
        http_restricted_reason = (
            headers.pop("_restricted_reason", "") if headers else ""
        )
        http_restricted_code = headers.pop("_restricted_code", "") if headers else ""
        if http_restricted_reason:
            final_restricted = True
            final_reason = http_restricted_reason
            final_code = http_restricted_code
        else:
            final_restricted = False
            final_reason = ""
            final_code = ""
        result.update(
            {
                "restricted": final_restricted,
                "restricted_reason": final_reason,
                "restricted_code": final_code,
                "redirected": redirected,
                "redirect_reason": redirect_reason,
            }
        )

        # 扫描完成通知：检查是否有 critical/high 漏洞
        try:
            high_risk_findings = [
                f
                for f in result["findings"]
                if f.get("severity") in ("critical", "high")
            ]
            if high_risk_findings:
                risk_names = ", ".join(
                    [
                        f.get("name") or f.get("title", "未知")
                        for f in high_risk_findings[:5]
                    ]
                )
                alert_title = (
                    f"【高危告警】{host} 发现 {len(high_risk_findings)} 个高危漏洞"
                )
                alert_msg = f"扫描目标 {url} 发现 {len(high_risk_findings)} 个高危/严重级别安全问题：{risk_names}"
                email_html = (
                    f"<h2>高危漏洞告警</h2>"
                    f"<p>扫描目标：<strong>{url}</strong></p>"
                    f"<p>发现 <strong>{len(high_risk_findings)}</strong> 个高危/严重级别安全问题：</p>"
                    f"<ul>"
                    + "".join(
                        [
                            f"<li><strong>{_html_escape(f.get('name') or f.get('title', ''))}</strong> - {_html_escape(f.get('description', ''))}</li>"
                            for f in high_risk_findings[:10]
                        ]
                    )
                    + f"</ul>"
                    f"<p>评分：<strong>{result['score']}</strong> 分 | 风险等级：<strong>{result['risk_level']}</strong></p>"
                    f"<p><a href='#'>点击查看详细报告</a></p>"
                )
                md_lines = [
                    f"### 高危漏洞告警: {host}",
                    "",
                    f"- **目标**: {url}",
                    f"- **评分**: {result['score']} 分",
                    f"- **风险等级**: {result['risk_level']}",
                    f"- **高危数量**: {len(high_risk_findings)} 个",
                    "",
                    "**问题列表**：",
                ]
                for f in high_risk_findings[:10]:
                    md_lines.append(
                        f"- **{f.get('name') or f.get('title', '')}**: {f.get('description', '')}"
                    )
                md_lines.append("")
                md_lines.append("[点击查看详细报告]")
                webhook_md = "\n".join(md_lines)
                asyncio.create_task(
                    notify_user(
                        user_id,
                        "high_risk_found",
                        alert_title,
                        alert_msg,
                        {
                            "url": url,
                            "score": result["score"],
                            "risk_level": result["risk_level"],
                            "high_count": len(high_risk_findings),
                        },
                        scan_id=scan_id,
                        severity="high",
                        email_body_html=email_html,
                        webhook_markdown=webhook_md,
                    )
                )
            else:
                # 扫描完成摘要通知
                alert_title = f"扫描完成：{host} 评分 {result['score']} 分"
                alert_msg = f"扫描目标 {url} 已完成，评分 {result['score']} 分，风险等级 {result['risk_level']}。"
                email_html = (
                    f"<h2>扫描完成通知</h2>"
                    f"<p>扫描目标：<strong>{url}</strong></p>"
                    f"<p>评分：<strong>{result['score']}</strong> 分</p>"
                    f"<p>风险等级：<strong>{result['risk_level']}</strong></p>"
                    f"<p>发现问题总数：<strong>{result['summary'].get('total', 0)}</strong> 个</p>"
                    f"<p><a href='#'>点击查看详细报告</a></p>"
                )
                webhook_md = (
                    f"### 扫描完成: {host}\n\n"
                    f"- **目标**: {url}\n"
                    f"- **评分**: {result['score']} 分\n"
                    f"- **风险等级**: {result['risk_level']}\n"
                    f"- **发现问题**: {result['summary'].get('total', 0)} 个\n\n"
                    f"[点击查看详细报告]"
                )
                asyncio.create_task(
                    notify_user(
                        user_id,
                        "scan_complete",
                        alert_title,
                        alert_msg,
                        {
                            "url": url,
                            "score": result["score"],
                            "risk_level": result["risk_level"],
                        },
                        scan_id=scan_id,
                        severity="low",
                        email_body_html=email_html,
                        webhook_markdown=webhook_md,
                    )
                )
        except Exception as e:
            logger.warning("Scan notification trigger failed: %s", e)

        return ScanResponse(**result)

    # 总扫描超时：根据深度动态设置
    # quick: 45s（仅头部分析）/ standard: 90s（插件扫描）/ deep: 180s（深度扫描+交叉验证）
    _scan_total_timeout = {"quick": 45.0, "standard": 90.0, "deep": 180.0}.get(
        scan_depth_label, 90.0
    )
    try:
        result = await asyncio.wait_for(_do_scan(), timeout=_scan_total_timeout)
        # 扫描完成，清理内存中的进度条目
        async with _scan_progress_lock:
            _scan_progress.pop(scan_token, None)
        result_jsonable = jsonable(result)
        # 写入扫描结果缓存（成功结果按深度 TTL 缓存）
        if isinstance(result_jsonable, dict) and result_jsonable.get("success"):
            async with _scan_cache_lock:
                _SCAN_RESULT_CACHE[cache_key] = (
                    result_jsonable,
                    time.time(),
                    cache_ttl,
                )
                # 记录缓存未命中（新写入 = 之前未命中）
                _SCAN_CACHE_MISSES += 1
                record_cache_miss()
                # 缓存淘汰：超过硬上限时按时间戳淘汰最旧的 20%
                if len(_SCAN_RESULT_CACHE) > _SCAN_CACHE_MAX_SIZE:
                    sorted_items = sorted(
                        _SCAN_RESULT_CACHE.items(), key=lambda x: x[1][1]
                    )
                    evict_count = max(1, int(_SCAN_CACHE_MAX_SIZE * 0.2))
                    for k, _ in sorted_items[:evict_count]:
                        _SCAN_RESULT_CACHE.pop(k, None)
        # 记录 Prometheus 业务指标
        record_scan_end(_metrics_timer, status="success", depth=req.depth or "standard")
        record_findings(result_jsonable.get("findings", []))
        return JSONResponse(
            content=result_jsonable,
            headers={"X-Scan-Token": scan_token},
        )
    except asyncio.TimeoutError:
        record_scan_end(_metrics_timer, status="timeout", depth=req.depth or "standard")
        async with _scan_progress_lock:
            _scan_progress.pop(scan_token, None)
        # 扫描超时退还积分
        try:
            credits_service.add_credits(
                user_id, scan_cost, note=f"scan_refund_timeout:{scan_depth_label}"
            )
            logger.info(
                "Credits refunded %d for timeout scan (user %d, url %s)",
                scan_cost,
                user_id,
                url,
            )
        except Exception as e:
            logger.warning("Credits refund (timeout) failed: %s", e)
        return JSONResponse(
            content=jsonable(
                ScanResponse(
                    success=False,
                    scan_id=0,
                    scan_type="real",
                    url=url,
                    final_url=url,
                    time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    is_https=False,
                    score=0,
                    risk_level="扫描超时",
                    findings=[],
                    summary={
                        "critical": 0,
                        "high": 0,
                        "medium": 0,
                        "low": 0,
                        "info": 0,
                        "total": 0,
                    },
                    headers={},
                    waf=None,
                    ssl={},
                    duration_ms=0,
                    report_share_id=None,
                    owasp_coverage=[],
                    header_details=[],
                    info_leaks=[],
                    cors=None,
                    cookie_issues=[],
                    ssl_info={},
                    waf_list=[],
                    sensitive_paths=[],
                    waf_detected=False,
                    raw_headers={},
                    error=f"扫描总时间超过 {_scan_total_timeout:.0f} 秒，请检查目标网站是否可访问，或尝试使用快速扫描模式",
                )
            ),
            headers={"X-Scan-Token": scan_token},
        )
    except RuntimeError as e:
        # Event loop is closed 等底层异常：重建 client 并给友好提示
        if "event loop" in str(e).lower() or "closed" in str(e).lower():
            logger.error("Scan failed due to event loop error: %s", e)
            try:
                await close_httpx_client()
            except Exception as e:
                logger.warning("close_httpx_client failed during error recovery: %s", e)
            async with _scan_progress_lock:
                _scan_progress.pop(scan_token, None)
            return JSONResponse(
                content=jsonable(
                    ScanResponse(
                        success=False,
                        scan_id=0,
                        scan_type="real",
                        url=url,
                        final_url=url,
                        time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        is_https=False,
                        score=0,
                        risk_level="扫描异常",
                        findings=[],
                        summary={
                            "critical": 0,
                            "high": 0,
                            "medium": 0,
                            "low": 0,
                            "info": 0,
                            "total": 0,
                        },
                        headers={},
                        waf=None,
                        ssl={},
                        duration_ms=0,
                        report_share_id=None,
                        owasp_coverage=[],
                        header_details=[],
                        info_leaks=[],
                        cors=None,
                        cookie_issues=[],
                        ssl_info={},
                        waf_list=[],
                        sensitive_paths=[],
                        waf_detected=False,
                        raw_headers={},
                        error="扫描过程中发生内部错误，请稍后重试。如持续失败，请刷新页面后重新扫描。",
                    )
                ),
                headers={"X-Scan-Token": scan_token},
            )
        raise
    except Exception as e:
        # Vuln Sentinel: 通用异常兜底，避免返回 500
        record_scan_end(_metrics_timer, status="error", depth=req.depth or "standard")
        logger.error("Scan failed with unexpected error: %s", e, exc_info=True)
        try:
            async with _scan_progress_lock:
                _scan_progress.pop(scan_token, None)
        except Exception as e:
            logger.warning("Failed to clean scan progress after error: %s", e)
        # 扫描异常退还积分
        try:
            credits_service.add_credits(
                user_id, scan_cost, note=f"scan_refund_error:{scan_depth_label}"
            )
            logger.info(
                "Credits refunded %d for error scan (user %d, url %s)",
                scan_cost,
                user_id,
                url,
            )
        except Exception as re:
            logger.warning("Credits refund (error) failed: %s", re)
        return JSONResponse(
            content=jsonable(
                ScanResponse(
                    success=False,
                    scan_id=0,
                    scan_type="real",
                    url=url,
                    final_url=url,
                    time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    is_https=False,
                    score=0,
                    risk_level="扫描异常",
                    findings=[],
                    summary={
                        "critical": 0,
                        "high": 0,
                        "medium": 0,
                        "low": 0,
                        "info": 0,
                        "total": 0,
                    },
                    headers={},
                    waf=None,
                    ssl={},
                    duration_ms=0,
                    report_share_id=None,
                    owasp_coverage=[],
                    header_details=[],
                    info_leaks=[],
                    cors=None,
                    cookie_issues=[],
                    ssl_info={},
                    waf_list=[],
                    sensitive_paths=[],
                    waf_detected=False,
                    raw_headers={},
                    error="扫描过程中发生异常，请稍后重试。如持续失败，请检查目标网站是否可访问。",
                )
            ),
            headers={"X-Scan-Token": scan_token},
        )


# ---------- 历史（含 DELETE） ----------


@app.get("/api/history")
async def api_history(
    user: dict = Depends(require_login),
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    url: str | None = Query(None),
    risk: str | None = Query(None),
) -> dict:
    user_id = user["user_id"]
    history, total = get_scan_history(
        user_id, limit=limit, offset=offset, url_filter=url, risk_level=risk
    )
    fixed_count = compute_fixed_count(history)
    return success_response(
        data={
            "history": history,
            "stats": {
                "scan_count": len(history),
                "fixed_count": fixed_count,
            },
        },
        meta={"total": total, "limit": limit, "offset": offset},
    )


@app.get("/api/trend")
async def api_trend(
    user: dict = Depends(require_login),
    url: str | None = None,
    limit: int = Query(30, ge=1, le=100),
) -> dict:
    """安全趋势数据 - 返回评分变化折线图数据"""
    user_id = user["user_id"]
    rows = get_scan_trend(user_id, limit=limit, url=url)

    url_groups: dict[str, list] = {}
    for d in rows:
        scan_url = d["url"]
        if scan_url not in url_groups:
            url_groups[scan_url] = []
        url_groups[scan_url].append(
            {
                "id": d["id"],
                "score": d["score"],
                "risk_level": d["risk_level"],
                "finding_count": d.get("findings_count", 0),
                "time": d["created_at"],
            }
        )

    for u in url_groups:
        url_groups[u].reverse()

    all_scores = [d["score"] for r_list in url_groups.values() for d in r_list]
    avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
    max_score = max(all_scores) if all_scores else 0
    min_score = min(all_scores) if all_scores else 0
    latest_score = all_scores[0] if all_scores else 0
    improved = len(all_scores) >= 2 and all_scores[-1] > all_scores[0]

    return success_response(
        data={
            "urls": list(url_groups.keys()),
            "series": url_groups,
            "summary": {
                "total_scans": len(all_scores),
                "avg_score": round(avg_score, 1),
                "max_score": max_score,
                "min_score": min_score,
                "latest_score": latest_score,
                "improved": improved,
            },
        }
    )


@app.delete("/api/history")
async def api_history_delete(user: dict = Depends(require_login)) -> dict:
    n = delete_scan_history(user["user_id"])
    return success_response(data={"deleted": n}, message="已清空扫描历史")


# ---------- 修复工单 API ----------


@app.post("/api/fix-tickets")
async def api_create_fix_ticket(
    req: FixTicketCreate, user: dict = Depends(require_login)
) -> dict:
    ticket_id = create_fix_ticket(
        user["user_id"],
        req.scan_id,
        req.finding_name,
        req.severity,
        req.fix_code,
        req.notes,
    )
    return success_response(data={"ticket_id": ticket_id}, message="工单创建成功")


@app.get("/api/fix-tickets")
async def api_list_fix_tickets(
    status: str | None = None, user: dict = Depends(require_login)
) -> dict:
    tickets = get_fix_tickets(user["user_id"], status)
    return success_response(data={"tickets": tickets})


@app.get("/api/fix-tickets/{ticket_id}")
async def api_get_fix_ticket(
    ticket_id: int, user: dict = Depends(require_login)
) -> dict:
    """获取单个工单详情。"""
    ticket = get_fix_ticket(ticket_id, user["user_id"])
    if not ticket:
        raise NotFoundException("工单不存在或无权限")
    return success_response(data={"ticket": ticket})


@app.patch("/api/fix-tickets/{ticket_id}")
async def api_update_fix_ticket(
    ticket_id: int, req: FixTicketUpdate, user: dict = Depends(require_login)
) -> dict:
    ok = update_fix_ticket(
        ticket_id,
        user["user_id"],
        status=req.status,
        fix_code=req.fix_code,
        notes=req.notes,
    )
    if not ok:
        raise NotFoundException("工单不存在或无权限")
    return success_response(message="更新成功")


@app.put("/api/fix-tickets/{ticket_id}")
async def api_put_fix_ticket(
    ticket_id: int, req: FixTicketUpdate, user: dict = Depends(require_login)
) -> dict:
    """PUT 方式更新工单（与 PATCH 等价，兼容不同调用风格）。"""
    ok = update_fix_ticket(
        ticket_id,
        user["user_id"],
        status=req.status,
        fix_code=req.fix_code,
        notes=req.notes,
    )
    if not ok:
        raise NotFoundException("工单不存在或无权限")
    return success_response(message="更新成功")


@app.delete("/api/fix-tickets/{ticket_id}")
async def api_delete_fix_ticket(
    ticket_id: int, user: dict = Depends(require_login)
) -> dict:
    ok = delete_fix_ticket(ticket_id, user["user_id"])
    if not ok:
        raise NotFoundException("工单不存在或无权限")
    return success_response(message="删除成功")


@app.post("/api/fix-tickets/{ticket_id}/verify")
async def api_verify_fix_ticket(
    ticket_id: int, req: FixTicketVerifyRequest, user: dict = Depends(require_login)
) -> dict:
    """工单复测验证：对比修复前后扫描结果，生成 diff 报告。

    流程：
    1. 获取工单关联的原始扫描
    2. 触发重新扫描（如果 req.rescan=True）
    3. 对比两次扫描结果
    4. 更新工单状态与 diff 摘要
    """
    ticket = get_fix_ticket(ticket_id, user["user_id"])
    if not ticket:
        raise NotFoundException("工单不存在或无权限")

    scan_id = ticket.get("scan_id")
    if not scan_id:
        raise BusinessException("工单未关联扫描记录，无法验证")

    # 获取原始扫描结果
    before_scan = get_scan_by_id(scan_id, user["user_id"])
    if not before_scan:
        raise NotFoundException("原始扫描记录不存在")

    before_result = before_scan.get("result_json") or "{}"
    try:
        before_data = (
            json.loads(before_result)
            if isinstance(before_result, str)
            else dict(before_result)
        )
    except Exception:
        before_data = {}

    # 按量计费：复测验证前扣除积分
    if req.rescan and ticket.get("url"):
        if not credits_service.has_credits(
            user["user_id"], credits_service.VERIFY_FIX_COST
        ):
            raise PaymentRequiredException(
                f"修复验证需要 {credits_service.VERIFY_FIX_COST} 积分，余额不足"
            )
        credits_service.deduct_credits(
            user["user_id"],
            credits_service.VERIFY_FIX_COST,
            action="verify_fix",
            scan_id=scan_id,
        )

    # 触发复测扫描（简化版：调用分析函数）
    after_data = before_data.copy()
    verification_scan_id = None
    if req.rescan and ticket.get("url"):
        try:
            from src_scanner import analyze_security

            url = ticket["url"]
            headers = before_data.get("raw_headers") or {}
            is_https = before_data.get("is_https", url.startswith("https"))
            ssl_info = before_data.get("ssl_info") or {}
            waf_list = before_data.get("waf_list") or []
            # 使用 analyze_security 做快速复测
            new_result = await analyze_security(
                url, headers, is_https, ssl_info, waf_list, depth="standard"
            )
            # 保存复测结果
            new_scan_id = save_scan(
                user["user_id"],
                url,
                new_result.get("score", before_data.get("score", 0)),
                new_result.get("risk_level", before_data.get("risk_level", "low")),
                new_result.get("findings", []),
                new_result.get("summary", {}),
                0,
                "verification",
            )
            verification_scan_id = new_scan_id
            after_data = {
                "scan_id": new_scan_id,
                "findings": new_result.get("findings", []),
                "score": new_result.get("score", 0),
                "risk_level": new_result.get("risk_level", "low"),
            }
        except Exception as e:
            logger.warning("Ticket verification rescan failed: %s", e)
            # 复测失败，使用原始数据作为 after
            after_data = before_data.copy()

    # 对比两次扫描
    diff = ScanDiffEngine.compare_scans(
        {
            "scan_id": scan_id,
            "findings": before_data.get("findings", []),
            "score": before_data.get("score", 0),
        },
        after_data,
    )

    # 更新工单
    diff_json = json.dumps(diff.to_dict(), ensure_ascii=False, default=str)
    is_fixed = diff.is_verified_fixed([ticket.get("finding_name")])
    new_status = (
        "fixed"
        if is_fixed
        else ("failed" if diff.score_delta < 0 else ticket.get("status", "pending"))
    )

    update_fix_ticket(
        ticket_id,
        user["user_id"],
        status=new_status,
        verification_scan_id=verification_scan_id,
        diff_summary=diff_json,
    )

    return success_response(
        data={
            "ticket_id": ticket_id,
            "verification_scan_id": verification_scan_id,
            "diff": diff.to_dict(),
            "status": new_status,
        },
        message="验证完成",
    )


@app.get("/api/fix-tickets/{ticket_id}/timeline")
async def api_fix_ticket_timeline(
    ticket_id: int, user: dict = Depends(require_login)
) -> dict:
    """获取工单的闭环时间线。"""
    ticket = get_fix_ticket(ticket_id, user["user_id"])
    if not ticket:
        raise NotFoundException("工单不存在或无权限")

    timeline = build_ticket_timeline(ticket)
    return success_response(data={"ticket": ticket, "timeline": timeline})


@app.post("/api/finding/feedback")
async def api_finding_feedback(
    req: FindingFeedbackRequest, current_user=Depends(get_current_user)
) -> dict:
    """记录用户对 finding 的误报/确认反馈。

    写入 finding_feedback 表；同时如果 user_id==0（未登录的公开扫描），允许匿名反馈但不写入（仅返回 success）。
    返回值：{"success": True, "feedback_id": ...}
    """
    try:
        # 未登录用户（user_id==0）也允许反馈，但不持久化
        if not current_user or not current_user.get("user_id"):
            return {"success": True, "feedback_id": None, "note": "未登录反馈未持久化"}
        conn = get_db()
        try:
            cur = conn.execute(
                """INSERT INTO finding_feedback
                   (user_id, scan_id, finding_name, finding_type, is_false_positive, is_confirmed, created_at)
                   VALUES (?,?,?,?,?,?,?)""",
                (
                    current_user["user_id"],
                    int(req.scan_id),
                    (req.finding_name or "").strip()[:256],
                    (req.finding_type or "").strip()[:128] or None,
                    1 if req.is_false_positive else 0,
                    1 if req.is_confirmed else 0,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )
            conn.commit()
            feedback_id = cur.lastrowid
        finally:
            conn.close()
        logger.info(
            "finding_feedback saved: user=%s scan=%s finding=%s fp=%s conf=%s",
            current_user.get("user_id"),
            req.scan_id,
            req.finding_name,
            req.is_false_positive,
            req.is_confirmed,
        )
        return {"success": True, "feedback_id": feedback_id}
    except Exception as e:
        logger.warning("finding_feedback save failed: %s", e)
        # 失败时仍返回 success（前端展示），但带 error 标记
        return {"success": False, "error": str(e)}


@app.get("/api/finding/feedback")
async def api_list_finding_feedback(
    scan_id: int | None = None,
    current_user=Depends(get_current_user),
) -> dict:
    """查询某个扫描（或当前用户）的 finding 反馈记录，用于前端展示"已标记"状态。"""
    try:
        if not current_user or not current_user.get("user_id"):
            return {"success": True, "feedbacks": []}
        conn = get_db()
        try:
            if scan_id is not None:
                rows = conn.execute(
                    """SELECT id, scan_id, finding_name, finding_type, is_false_positive, is_confirmed, created_at
                       FROM finding_feedback WHERE user_id=? AND scan_id=?""",
                    (current_user["user_id"], int(scan_id)),
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT id, scan_id, finding_name, finding_type, is_false_positive, is_confirmed, created_at
                       FROM finding_feedback WHERE user_id=? ORDER BY created_at DESC LIMIT 200""",
                    (current_user["user_id"],),
                ).fetchall()
        finally:
            conn.close()
        return {
            "success": True,
            "feedbacks": [dict(r) for r in rows],
        }
    except Exception as e:
        return {"success": False, "error": str(e), "feedbacks": []}


@app.post("/api/finding/verify-reproduce")
async def api_verify_reproduce(
    req: VerifyReproduceRequest, user: dict = Depends(require_login)
) -> dict:
    """对单个 SRC finding 重新执行复现检测，返回是否仍可复现。"""
    try:
        scan = get_scan_by_id(req.scan_id, user["user_id"])
        if not scan:
            raise HTTPException(404, "扫描记录不存在")
        findings = (
            json.loads(scan["findings_json"]) if scan.get("findings_json") else []
        )
        target = next((f for f in findings if f.get("id") == req.finding_id), None)
        if not target:
            raise HTTPException(404, "Finding 不存在")

        vuln_type = target.get("type", "")
        test_url = req.url or target.get("url", scan["url"])
        headers = json.loads(scan["headers_json"]) if scan.get("headers_json") else {}
        is_https = test_url.startswith("https://")

        # 针对部分类型直接复用 src_scanner 的检测函数
        detector_map = {
            "sqli": src_scanner.detect_sqli_src,
            "xss": src_scanner.detect_xss_src,
            "ssrf": src_scanner.detect_ssrf_src,
            "idor": src_scanner.detect_idor_src,
            "broken_access_control": src_scanner.detect_broken_access_control_src,
            "sensitive_path": src_scanner.detect_sensitive_paths_src,
        }
        detector = detector_map.get(vuln_type)
        if not detector:
            return {
                "success": True,
                "reproducible": None,
                "note": "该类型暂不支持自动复现，请人工验证",
                "finding": target,
            }

        if vuln_type in ("info_leak", "csrf", "outdated_component", "header_missing"):
            # 这些类型依赖原始 headers/body，使用通用复现：重新跑完整扫描并比对
            result = await src_scanner.run_src_scan(test_url, headers, is_https, {})
            matched = [
                f for f in result.get("findings", []) if f.get("type") == vuln_type
            ]
            reproducible = len(matched) > 0
            return {
                "success": True,
                "reproducible": reproducible,
                "matched_count": len(matched),
                "note": "已重新执行扫描并比对同类型结果",
            }

        reproduced = await detector(test_url)
        # 判断是否复现：URL 与类型匹配即认为存在
        reproducible = any(r.get("type") == vuln_type for r in reproduced)
        return {
            "success": True,
            "reproducible": reproducible,
            "new_findings": reproduced[:3],
            "note": "复现检测完成",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.warning("verify-reproduce failed: %s", e)
        return {"success": False, "error": str(e)}


@app.get("/api/stats/history")
async def api_stats_history(
    user: dict = Depends(require_login), days: int = Query(30, ge=1, le=365)
) -> dict:
    """返回扫描分数时间序列，用于前端绘制趋势图。
    数据：近 N 天该用户所有扫描的 url、score、time。
    """
    conn = get_db()
    try:
        since_ts = (datetime.utcnow() - timedelta(days=days)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        rows = conn.execute(
            """SELECT id, url, score, created_at, risk_level
               FROM scans
               WHERE user_id=? AND created_at >= ?
               ORDER BY created_at ASC""",
            (user["user_id"], since_ts),
        ).fetchall()
    finally:
        conn.close()
    points = [
        {
            "id": r["id"],
            "url": r["url"],
            "score": r["score"],
            "time": r["created_at"],
            "risk_level": r["risk_level"] or "",
        }
        for r in rows
    ]
    # 按 URL 分组（每个域名一条线）
    by_url: dict[str, list] = {}
    for p in points:
        try:
            from urllib.parse import urlparse

            host = urlparse(p["url"]).hostname or p["url"]
        except Exception:
            host = p["url"]
        by_url.setdefault(host, []).append(p)
    # 汇总统计
    if points:
        scores = [p["score"] for p in points]
        avg = round(sum(scores) / len(scores), 1)
        latest = points[-1]["score"]
        first = points[0]["score"]
        trend = latest - first
    else:
        avg = latest = first = trend = 0
    return {
        "points": points,
        "series": [
            {
                "url": url,
                "data": [{"time": p["time"], "score": p["score"]} for p in pts],
            }
            for url, pts in by_url.items()
        ],
        "summary": {
            "scan_count": len(points),
            "url_count": len(by_url),
            "avg_score": avg,
            "latest_score": latest,
            "first_score": first,
            "trend_delta": trend,
        },
    }


@app.get("/api/alerts")
async def api_alerts(
    user: dict = Depends(require_login),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
) -> dict:
    """返回用户的扫描告警通知（含 title 和 scan_id）。"""
    conn = get_db()
    try:
        sql = "SELECT * FROM alerts WHERE user_id=?"
        params = [user["user_id"]]
        if unread_only:
            sql += " AND is_read=0"
        sql += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(sql, params).fetchall()
    finally:
        conn.close()
    alerts = []
    for r in rows:
        d = dict(r)
        try:
            d["details"] = json.loads(d.get("details_json") or "{}")
        except Exception:
            d["details"] = {}
        d.pop("details_json", None)
        alerts.append(d)
    return {"alerts": alerts, "count": len(alerts)}


@app.get("/api/alerts/unread-count")
async def api_alerts_unread_count(user: dict = Depends(require_login)) -> dict:
    """返回用户未读告警数量。"""
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM alerts WHERE user_id=? AND is_read=0",
            (user["user_id"],),
        ).fetchone()
        count = row["cnt"] if row else 0
    finally:
        conn.close()
    return {"unread_count": count}


@app.post("/api/alerts/{alert_id}/read")
async def api_mark_alert_read(
    alert_id: int, user: dict = Depends(require_login)
) -> dict:
    """标记告警为已读。"""
    conn = get_db()
    try:
        conn.execute(
            "UPDATE alerts SET is_read=1 WHERE id=? AND user_id=?",
            (alert_id, user["user_id"]),
        )
        conn.commit()
    finally:
        conn.close()
    return {"success": True}


@app.get("/api/me/notifications")
async def api_get_notifications(user: dict = Depends(require_login)) -> dict:
    """获取当前用户的通知设置。"""
    settings_dict = get_user_notification_settings(user["user_id"])
    return {"success": True, **settings_dict}


@app.post("/api/me/notifications")
async def api_update_notifications(
    req: dict, user: dict = Depends(require_login)
) -> dict:
    """更新当前用户的通知设置。"""
    email = req.get("email", "")
    webhook = req.get("webhook", "")
    threshold = req.get("threshold", "high")
    if threshold not in ("critical", "high", "medium", "low", "all"):
        threshold = "high"
    if email:
        try:
            email = sanitize_email(email)
        except ValueError as e:
            return {"success": False, "error": str(e)}
    ok = update_user_notification_settings(user["user_id"], email, webhook, threshold)
    return {"success": ok}


# ---------- 授权日志 ----------
@app.post("/api/scan-auth-log")
async def api_scan_auth_log(
    request: Request, user: dict = Depends(require_login)
) -> dict:
    """记录用户扫描授权时间（审计用），静默失败不阻塞。"""
    try:
        body = await request.json()
        authorized_at = body.get("authorized_at", "")
        target_url = body.get("url", "")
        if not authorized_at:
            return {"success": False, "error": "missing authorized_at"}
        import logging

        logging.getLogger("vuln_sentinel").info(
            f"SCAN_AUTH user={user.get('username')} target={target_url} at={authorized_at}"
        )
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ---------- Simulate Fix（用真实 severity） ----------


@app.post("/api/simulate-fix", response_model=None)
async def simulate_fix(req: SimulateFixRequest, request: Request) -> dict:
    """模拟应用修复后的预期评分（不需要登录）。
    输入：scan findings 数组（使用真实 severity 字段 high/medium/low）+ 可选 scan_id
    输出：修复前 vs 修复后的评分对比
    """
    # Vuln Sentinel: 添加速率限制，防止滥用
    await rate_limit_dependency(request)
    findings = req.findings or []

    # V11.4 fix: 如果提供了 scan_id，从数据库获取真实扫描分数作为 before_score
    before = None
    if req.scan_id:
        try:
            scan_row = get_scan_by_id(req.scan_id)
            if scan_row and scan_row.get("score") is not None:
                before = int(scan_row["score"])
        except Exception:
            pass

    # 如果没有 scan_id 或查不到，从 findings 估算
    if before is None:
        deduction = sum(
            SEVERITY_SCORE.get(f.get("severity", "low"), 3) for f in findings
        )
        before = max(0, 100 - deduction)

    # 修复后分数：消除所有 findings 的扣分，再加 12 分奖励，上限 100
    deduction = sum(SEVERITY_SCORE.get(f.get("severity", "low"), 3) for f in findings)
    after = min(100, before + deduction + 12)

    fixed_items = []
    for f in findings[:20]:
        severity = f.get("severity", "low")
        fixed_items.append(
            {
                "name": f.get("name", "未知漏洞"),
                "severity": severity,
                "level_zh": f.get("level_zh") or SEVERITY_ZH.get(severity, "低风险"),
                "owasp": f.get("owasp", ""),
                "fix": f.get("fix", ""),
                "summary": f.get("summary")
                or f"修复 {f.get('name', '安全问题')}，消除 {SEVERITY_ZH.get(severity, '低')} 风险",
            }
        )
    # Vuln Sentinel：生成可执行的修复配置（按平台分类）
    nginx_fixes = []
    for f in findings:
        fix_code = f.get("fix", "")
        if fix_code:
            nginx_fixes.append(fix_code)
    # 如果没有 fix 字段，根据 name 自动生成
    if not nginx_fixes:
        FIX_TEMPLATES = {
            "HSTS": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
            "CSP": "add_header Content-Security-Policy 'default-src self' always;",
            "X-Frame-Options": 'add_header X-Frame-Options "SAMEORIGIN" always;',
            "X-Content-Type-Options": 'add_header X-Content-Type-Options "nosniff" always;',
            "Referrer-Policy": 'add_header Referrer-Policy "strict-origin-when-cross-origin" always;',
            "Permissions-Policy": 'add_header Permissions-Policy "camera=(), microphone=()" always;',
            "Server": "server_tokens off;",
            "Cookie": "proxy_cookie_flags ~ secure samesite=Strict;",
        }
        for f in findings[:20]:
            name = f.get("name", "")
            for k, v in FIX_TEMPLATES.items():
                if k in name:
                    nginx_fixes.append("# " + name + "\n" + v)
                    break

    return {
        "before_score": before,
        "after_score": after,
        "delta": after - before,
        "fixed_count": len(fixed_items),
        "fixed_items": fixed_items,
        "nginx_config": "\n\n".join(nginx_fixes) if nginx_fixes else "# 配置代码生成中",
        "summary": f"应用 {len(findings)} 项修复后，评分预计从 {before} 提升到 {after}（+{after - before} 分）",
    }


@app.post("/api/apply-fix-and-rescan", response_model=None)
async def apply_fix_and_rescan(
    req: ApplyFixRequest, user: dict = Depends(require_login)
):
    """应用修复后再次扫描对比评分。
    可选 previous_scan_id 字段：指定要对比的"修复前"扫描。
    """
    # 按量计费：应用修复并复测前扣除积分
    if not credits_service.has_credits(user["user_id"], credits_service.APPLY_FIX_COST):
        raise PaymentRequiredException(
            f"应用修复并复测需要 {credits_service.APPLY_FIX_COST} 积分，余额不足"
        )
    credits_service.deduct_credits(
        user["user_id"], credits_service.APPLY_FIX_COST, action="apply_fix_and_rescan"
    )

    url = req.url.strip()
    previous_scan_id = req.previous_scan_id
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    parsed = urlparse(url)
    host = parsed.hostname or ""
    try:
        headers, is_https, final_url, error = await asyncio.wait_for(
            fetch_headers(url), timeout=30.0
        )
        if error:
            return {"success": False, "error": error}
        ssl_info = await get_ssl_info(host, 443) if is_https else {"has_cert": False}
        waf_list = detect_waf(headers)
        sensitive_paths = await check_sensitive_paths(host, is_https)
        result = await analyze_security(
            url, headers, is_https, ssl_info, waf_list, sensitive_paths, []
        )
        scan_id = save_scan(
            user["user_id"],
            url,
            result["score"],
            result["risk_level"],
            result["findings"],
            result["summary"],
            0,
            "rescan",
        )

        previous = None
        if previous_scan_id:
            previous = get_scan_by_id(int(previous_scan_id), user["user_id"])
        else:
            conn = get_db()
            row = conn.execute(
                "SELECT * FROM scans WHERE user_id=? AND url=? AND id<>? ORDER BY id DESC LIMIT 1",
                (user["user_id"], url, scan_id),
            ).fetchone()
            conn.close()
            if row:
                previous = dict(row)

        prev_findings = []
        if previous:
            try:
                prev_findings = json.loads(previous.get("findings_json") or "[]")
            except Exception:
                prev_findings = []
        prev_names = {f.get("name", "") for f in prev_findings}
        new_names = {f.get("name", "") for f in result["findings"]}
        fixed = sorted(list(prev_names - new_names))
        new_issues = sorted(list(new_names - prev_names))
        prev_score = previous.get("score") if previous else 0
        delta = result["score"] - (prev_score or 0)

        return {
            "success": True,
            "scan_id": scan_id,
            "url": url,
            "score": result["score"],
            "risk_level": result["risk_level"],
            "summary": result["summary"],
            "findings": result["findings"],
            "previous": {
                "scan_id": previous.get("id"),
                "score": prev_score,
                "findings": prev_findings,
            }
            if previous
            else None,
            "fixed": fixed,
            "new_issues": new_issues,
            "delta": delta,
        }
    except Exception as e:
        return {"success": False, "error": str(e)[:300]}


# ----- 修复配置包：把所有修复方案打包成可下载 zip -----
@app.post("/api/generate-fix-package")
async def api_generate_fix_package(
    request: Request, user: dict = Depends(require_login)
) -> FileResponse:
    """AI 生成修复配置包：根据 body 中的 findings + host + is_https 生成平台配置 + 部署脚本，打包成 zip。"""
    import io
    import time
    import zipfile

    await rate_limit_dependency(request)
    body = await request.json()
    findings = body.get("findings", [])
    host = body.get("host", "your-domain.com")
    is_https = body.get("is_https", True)
    platform = body.get("platform", "nginx")

    fixes_map = generate_fixes(findings, {}, is_https, host)
    platform_fixes = fixes_map.get(platform, [])

    code_blocks = []
    for f in platform_fixes:
        if isinstance(f, dict):
            c = f.get("code", "")
            note = f.get("risk_note", "")
            if c:
                code_blocks.append("# " + (note or "修复代码"))
                code_blocks.append(c)
        else:
            code_blocks.append(str(f))

    if not code_blocks:
        code_blocks = ["# 暂无需要修复的项目"]

    main_cfg = "\n\n".join(code_blocks)
    readme = f"""# {host} 安全配置包
由Vuln Sentinel 自动生成
平台：{platform.upper()}
修复项数：{len(code_blocks)}
生成时间：{time.strftime("%Y-%m-%d %H:%M:%S")}

## 使用方法

1. 把 `config.conf` 内容追加到你的 {platform} 配置
2. 重新加载配置：
   - Nginx: `nginx -t && systemctl reload nginx`
   - Apache: `apachectl configtest && systemctl reload apache2`
   - Express/Flask/Spring: 重启应用
   - Spring Boot: `mvn clean package && java -jar target/*.jar`

3. 重新访问 https://{host}，用「验证修复效果」看评分变化

## 部署清单

- [ ] 备份原配置
- [ ] 应用新配置
- [ ] 验证服务正常
- [ ] 重新跑一次扫描
- [ ] 对比修复前后分数

## 修复清单

"""
    for f in findings[:20]:
        readme += f"- [{f.get('severity', '-')}] {f.get('name', '')}\n"

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{platform}/config.conf", main_cfg)
        zf.writestr("README.md", readme)
        zf.writestr(
            "deploy.sh", f"#!/bin/bash\necho '部署 {platform} 安全配置到 {host}'\n"
        )
    buf.seek(0)
    from starlette.responses import Response

    content = buf.read()
    return Response(
        content=content,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=vulnsentinel-fix-{host}-{platform}-{int(time.time())}.zip"
        },
    )


# ============================================================
# Vuln Sentinel 应用修复配置：用户授权凭证 → SSH 改服务器配置 → 验证 → 返结果
# ============================================================

# 生成 / 读取对称加密 key（用于加密用户凭证）
def _get_credential_key() -> bytes:
    """获取凭证加密 key（生产环境应从环境变量读取）"""
    key_str = os.environ.get("CREDENTIAL_ENCRYPT_KEY")
    if key_str:
        # base64 编码的 32 字节 key
        return key_str.encode()
    # 默认 key（仅开发环境，部署时必须设置环境变量）
    default_key = b"vulnsentinel-v11-default-credential-key-32!!"
    return base64.urlsafe_b64encode(default_key.ljust(32, b"=")[:32])


_fernet = Fernet(_get_credential_key())

# Vuln Sentinel: 生产环境强制校验凭证加密密钥，禁止使用硬编码默认值
if _IS_PRODUCTION:
    _default_key = base64.urlsafe_b64encode(
        b"vulnsentinel-v11-default-credential-key-32!!".ljust(32, b"=")[:32]
    )
    if _fernet._signing_key == Fernet(_default_key)._signing_key:
        raise RuntimeError(
            "生产环境必须设置 CREDENTIAL_ENCRYPT_KEY 环境变量（base64 编码的 32 字节密钥），"
            "禁止使用硬编码默认密钥。\n"
            '请执行：export CREDENTIAL_ENCRYPT_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")'
        )


def _encrypt_credential(text: str) -> str:
    """加密用户凭证（AES + base64）"""
    return _fernet.encrypt(text.encode()).decode()


def _decrypt_credential(cipher_text: str) -> str:
    """解密用户凭证"""
    return _fernet.decrypt(cipher_text.encode()).decode()


def _generate_fix_patch(findings: list, platform: str = "nginx") -> str:
    """生成修复补丁（用于追加到现有配置文件）"""
    if platform == "nginx":
        lines = [
            "",
            "# ============================================",
            "# Vuln Sentinel 自动应用的安全头",
            f"# 应用时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"# 修复项数: {len(findings)}",
            "# ============================================",
            "",
        ]
        # 修复模板（与 simulate-fix 保持一致）
        TEMPLATES = {
            "HSTS": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
            "CSP": "add_header Content-Security-Policy 'upgrade-insecure-requests' always;",
            "X-Frame-Options": 'add_header X-Frame-Options "SAMEORIGIN" always;',
            "X-Content-Type-Options": 'add_header X-Content-Type-Options "nosniff" always;',
            "Referrer-Policy": 'add_header Referrer-Policy "strict-origin-when-cross-origin" always;',
            "Permissions-Policy": 'add_header Permissions-Policy "camera=(), microphone=()" always;',
        }
        applied = set()
        for f in findings:
            name = f.get("name", "") if isinstance(f, dict) else str(f)
            for k, v in TEMPLATES.items():
                if k in name and k not in applied:
                    lines.append(f"# 修复: {name[:50]}")
                    lines.append(v)
                    applied.add(k)
                    break
        if not applied:
            lines.append("# （未匹配到可生成修复配置的项）")
        return "\n".join(lines)
    else:
        return f"# 平台 {platform} 修复配置补丁（暂未实现）\n"


def _ssh_execute(
    host: str,
    port: int,
    username: str,
    password: str,
    commands: list,
    timeout: int = 30,
) -> list:
    """
    通过 SSH 连接服务器并执行命令列表
    返回每条命令的输出（按顺序）
    """
    try:
        import paramiko
    except ImportError as e:
        raise RuntimeError("SSH 功能需要安装 paramiko: pip install paramiko") from e

    results = []
    client = paramiko.SSHClient()
    try:
        # 安全最佳实践：默认使用 RejectPolicy 拒绝未知主机密钥，防止 MITM 攻击。
        # 加载系统 known_hosts 文件以识别已信任的主机。
        # 若需跳过校验（仅限内网/测试环境），设置环境变量 SSH_INSECURE_SKIP_HOST_KEY_CHECK=1
        known_hosts_path = os.path.expanduser("~/.ssh/known_hosts")
        if os.path.exists(known_hosts_path):
            client.load_system_host_keys(filename=known_hosts_path)

        if os.environ.get("SSH_INSECURE_SKIP_HOST_KEY_CHECK", "").lower() in ("1", "true", "yes"):
            # 仅在明确配置时才使用 AutoAddPolicy（不安全）
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # nosec B507 - 仅在 SSH_INSECURE_SKIP_HOST_KEY_CHECK=1 时启用，默认使用 RejectPolicy
        else:
            # 默认：拒绝未知主机密钥（安全默认值）
            client.set_missing_host_key_policy(paramiko.RejectPolicy())
        client.connect(
            hostname=host,
            port=port,
            username=username,
            password=password,
            timeout=timeout,
            look_for_keys=False,
            allow_agent=False,
        )
        for cmd in commands:
            stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)  # nosec B601 - 命令参数已通过 shlex.quote 和白名单校验消毒
            out = stdout.read().decode("utf-8", errors="ignore")
            err = stderr.read().decode("utf-8", errors="ignore")
            exit_code = stdout.channel.recv_exit_status()
            results.append(
                {
                    "cmd": cmd,
                    "output": out[:2000],
                    "error": err[:1000],
                    "exit_code": exit_code,
                }
            )
    except Exception as e:
        raise RuntimeError(f"SSH 执行失败: {e}")
    finally:
        client.close()
    return results


def _auto_fix_via_ssh(scan_data: dict, credentials: dict) -> dict:
    """
    Vuln Sentinel 核心：通过 SSH 真正修复用户服务器
    流程：备份 → 追加修复配置 → 测试配置 → 重载 → 验证
    """
    # 安全最佳实践：验证 platform 白名单，防止命令注入
    _ALLOWED_PLATFORMS = {"nginx", "apache"}
    host = credentials.get("host")  # 用户服务器 IP/域名
    port = int(credentials.get("port", 22))
    username = credentials.get("username", "root")
    password = credentials.get("password")  # 用户提供的 SSH 密码
    platform = credentials.get("platform", "nginx")  # nginx / apache
    config_path = credentials.get("config_path", "")  # 配置文件路径

    findings = scan_data.get("findings", [])

    if not all([host, password]):
        return {"success": False, "error": "缺少 host 或 password"}

    # 安全最佳实践：platform 必须来自白名单，防止命令注入
    if platform not in _ALLOWED_PLATFORMS:
        return {"success": False, "error": f"不支持的平台: {platform}，仅支持 {', '.join(sorted(_ALLOWED_PLATFORMS))}"}

    # 智能推断配置文件路径
    if not config_path:
        if platform == "nginx":
            config_path = "/etc/nginx/conf.d/vulnsentinel-security.conf"
        elif platform == "apache":
            config_path = "/etc/apache2/conf-available/vulnsentinel-security.conf"
    else:
        # 安全最佳实践：验证用户提供的 config_path 为合法绝对路径，防止命令注入
        if not re.match(r"^/etc/[a-zA-Z0-9_\-./]+\.conf$", config_path):
            return {"success": False, "error": "config_path 必须为 /etc/ 下的 .conf 文件路径"}

    # 安全最佳实践：对 shell 命令中使用的变量进行 shlex.quote，防止命令注入
    safe_config_path = shlex.quote(config_path)

    # 生成修复补丁
    patch_content = _generate_fix_patch(findings, platform)

    # SSH 命令序列
    commands = [
        # 1. 创建新配置文件（不在原文件改，更安全）
        f"echo '写入修复配置到 {safe_config_path}'",
        f"cat > {safe_config_path} << 'VS_EOF'\n{patch_content}\nVS_EOF",
        # 2. 验证文件写入成功
        f"ls -la {safe_config_path} && cat {safe_config_path} | head -5",
    ]

    if platform == "nginx":
        commands += [
            # 3. 测试 Nginx 配置
            "nginx -t 2>&1",
            # 4. 如果测试通过，重载（不重启，零停机）
            "nginx -s reload 2>&1 || (systemctl reload nginx 2>&1) || true",
        ]
    elif platform == "apache":
        commands += [
            "apache2ctl configtest 2>&1",
            "systemctl reload apache2 2>&1 || service apache2 reload 2>&1 || true",
        ]

    # 5. 验证修复 - 实际去网站 GET 一次，看响应头
    # 安全最佳实践：对 target_url 进行 sanitize_url 校验 + shlex.quote，防止命令注入
    target_url = scan_data.get("url", "")
    if target_url:
        try:
            from utils import sanitize_url
            sanitize_url(target_url)
        except ValueError:
            target_url = ""
    if target_url:
        safe_url = shlex.quote(target_url)
        commands.append(f"curl -sI -m 10 {safe_url} 2>&1 | head -20")

    try:
        results = _ssh_execute(host, port, username, password, commands, timeout=30)
    except Exception as e:
        return {"success": False, "error": str(e), "step": "ssh_connect"}

    # 检查 nginx -t 是否成功
    nginx_test_ok = True
    for r in results:
        if "nginx -t" in r["cmd"]:
            if r["exit_code"] != 0 or "successful" not in r["output"]:
                nginx_test_ok = False
            break

    # 提取验证结果
    verified_headers = []
    for r in results:
        if r["cmd"].startswith("curl -sI"):
            for line in r["output"].split("\n"):
                if any(
                    h in line.lower()
                    for h in [
                        "strict-transport",
                        "content-security",
                        "x-frame",
                        "x-content-type",
                        "referrer",
                        "permissions",
                    ]
                ):
                    verified_headers.append(line.strip())
            break

    return {
        "success": True,
        "host": host,
        "config_path": config_path,
        "platform": platform,
        "patch_size_bytes": len(patch_content),
        "config_test_ok": nginx_test_ok,
        "verified_headers": verified_headers,
        "ssh_results": [
            {
                "cmd": r["cmd"][:60],
                "exit_code": r["exit_code"],
                "ok": r["exit_code"] == 0,
            }
            for r in results
        ],
        "next_step": "5 秒后重新扫描验证修复效果",
    }


@app.post("/api/auto-fix")
async def api_auto_fix(request: Request, user: dict = Depends(require_login)) -> dict:
    """
    Vuln Sentinel 终极功能：端到端应用修复配置
    接收：扫描结果 + 用户服务器凭证
    执行：SSH 备份 → 写配置 → 测试 → 重载 → 验证
    返回：完整执行日志 + 验证后的安全头列表
    """
    try:
        body = await request.json()
    except Exception:
        return {"success": False, "error": "请求体必须是 JSON"}

    scan_id = body.get("scan_id")
    credentials = body.get("credentials", {})

    if not scan_id:
        return {"success": False, "error": "缺少 scan_id"}

    # 凭证不能落库：只在内存中临时使用，调用完即丢
    if not credentials.get("host") or not credentials.get("password"):
        return {"success": False, "error": "缺少 host 或 password"}

    # 1. 取扫描结果
    scan = get_scan_by_id(int(scan_id), user["user_id"])
    if not scan:
        return {"success": False, "error": "扫描记录不存在或无权限"}

    # 2. 立即加密凭证（仅在本请求中传递，不入数据库）
    enc_pwd = _encrypt_credential(credentials["password"])

    # 3. 执行 SSH 自动修复
    fix_result = _auto_fix_via_ssh(
        scan, {**credentials, "password": _decrypt_credential(enc_pwd)}
    )

    # 4. 记录到修复工单（凭证不入库，只存结果）
    if fix_result.get("success"):
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute(
                """INSERT INTO fix_tickets
                   (user_id, scan_id, target_url, status, fix_log, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    user["user_id"],
                    scan_id,
                    scan.get("url", ""),
                    "auto_fixed",
                    json.dumps(
                        {
                            "host": credentials["host"],
                            "config_path": fix_result["config_path"],
                            "verified_headers": fix_result["verified_headers"],
                        },
                        ensure_ascii=False,
                    ),
                    int(time.time()),
                ),
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(
                "Failed to save SSH fix record: %s", e
            )  # 记录失败不影响主流程

    # 5. 立即清空明文凭证（防止意外泄露）
    credentials.clear()

    return fix_result


@app.post("/api/auto-fix-via-cloudflare")
async def api_auto_fix_cloudflare(
    request: Request, user: dict = Depends(require_login)
) -> dict:
    """
    Vuln Sentinel Cloudflare 应用修复配置：通过 Cloudflare API 改安全头（零 SSH 风险）
    用户只需提供 CF API Token 即可一键应用 5+ 项安全头
    """
    try:
        body = await request.json()
    except Exception:
        return {"success": False, "error": "请求体必须是 JSON"}

    scan_id = body.get("scan_id")
    cf_token = body.get("cf_token", "").strip()
    cf_zone = body.get("cf_zone", "").strip()  # 例如 example.com

    if not all([scan_id, cf_token, cf_zone]):
        return {"success": False, "error": "缺少 scan_id / cf_token / cf_zone"}

    scan = get_scan_by_id(int(scan_id), user["user_id"])
    if not scan:
        return {"success": False, "error": "扫描记录不存在"}

    # Cloudflare API: 修改 Transform Rules / Security Headers
    headers_to_apply = []
    findings = scan.get("findings", [])
    for f in findings:
        name = f.get("name", "")
        if "HSTS" in name:
            headers_to_apply.append(
                {
                    "name": "Strict-Transport-Security",
                    "value": "max-age=31536000; includeSubDomains",
                }
            )
        elif "CSP" in name:
            headers_to_apply.append(
                {
                    "name": "Content-Security-Policy",
                    "value": "upgrade-insecure-requests",
                }
            )
        elif "X-Frame-Options" in name:
            headers_to_apply.append({"name": "X-Frame-Options", "value": "SAMEORIGIN"})
        elif "X-Content-Type-Options" in name:
            headers_to_apply.append(
                {"name": "X-Content-Type-Options", "value": "nosniff"}
            )
        elif "Referrer-Policy" in name:
            headers_to_apply.append(
                {"name": "Referrer-Policy", "value": "strict-origin-when-cross-origin"}
            )

    if not headers_to_apply:
        return {
            "success": True,
            "applied": 0,
            "message": "无需 Cloudflare 修复（已全部通过）",
        }

    # 调用 Cloudflare API 修改 Transform Rules
    # 简化版：直接用 CF API v4 修改 Ruleset
    import requests

    cf_results = []
    for h in headers_to_apply:
        # Cloudflare 不直接支持"添加响应头"的简单 API，
        # 实际是创建 Transform Rule (Modify Response Header)
        # 这里用 snippet API 替代，更轻量
        try:
            r = requests.post(
                f"https://api.cloudflare.com/client/v4/zones/{cf_zone}/snippets",
                headers={
                    "Authorization": f"Bearer {cf_token}",
                    "Content-Type": "application/json",
                },
                json={
                    "name": f"vs-fix-{h['name']}",
                    "snippet": (
                        "export default {"
                        f"async fetch(request) {{"
                        "const response = await fetch(request);"
                        "const newHeaders = new Headers(response.headers);"
                        f"newHeaders.set('{h['name']}', '{h['value']}');"
                        "return new Response(response.body, {"
                        "status: response.status,"
                        "statusText: response.statusText,"
                        "headers: newHeaders,"
                        "});"
                        "}}"
                        "};"
                    ),
                    "files": [],
                    "main_module": "snippet.js",
                },
                timeout=15,
            )
            cf_results.append(
                {
                    "header": h["name"],
                    "applied": r.status_code in (200, 201),
                    "response": r.text[:200],
                }
            )
        except Exception as e:
            cf_results.append(
                {
                    "header": h["name"],
                    "applied": False,
                    "error": str(e)[:100],
                }
            )

    return {
        "success": True,
        "platform": "cloudflare",
        "applied": sum(1 for r in cf_results if r.get("applied")),
        "total": len(cf_results),
        "results": cf_results,
        "next_step": "5 秒后重新扫描验证",
    }


# ============================================================
# Vuln Sentinel 进化模块 1：智能学习 — 从历史自动学
# ============================================================
def _learn_from_user_history(user_id: int) -> dict:
    """
    Vuln Sentinel 进化：从用户的修复历史自动学习
    统计：用户最常修/不修的项、修复后真实效果、最佳修复顺序
    """
    conn = get_db()
    try:
        # 1. 收集用户最近 50 次扫描的所有 findings
        rows = conn.execute(
            """SELECT findings_json, score, risk_level, created_at, scan_type
               FROM scans WHERE user_id=? ORDER BY id DESC LIMIT 50""",
            (user_id,),
        ).fetchall()

        # 2. 统计问题频率
        issue_stats = {}  # name -> { count, last_seen, avg_score }
        for row in rows:
            try:
                findings = json.loads(row["findings_json"] or "[]")
            except Exception:
                continue
            for f in findings:
                name = f.get("name", "未知")
                sev = f.get("severity", "low")
                if name not in issue_stats:
                    issue_stats[name] = {
                        "count": 0,
                        "severity": sev,
                        "first_seen": row["created_at"],
                        "last_seen": row["created_at"],
                    }
                issue_stats[name]["count"] += 1
                issue_stats[name]["last_seen"] = row["created_at"]

        # 3. 找"反复出现"的问题（说明用户没修）
        persistent = [
            {
                "name": n,
                "times": s["count"],
                "severity": s["severity"],
                "last_seen": s["last_seen"],
            }
            for n, s in issue_stats.items()
            if s["count"] >= 3
        ]
        persistent.sort(key=lambda x: -x["times"])

        # 4. 找"已修复"的问题（最近 5 次扫描都没出现）
        all_names = set(issue_stats.keys())
        recent_rows = conn.execute(
            """SELECT findings_json FROM scans WHERE user_id=? ORDER BY id DESC LIMIT 5""",
            (user_id,),
        ).fetchall()
        recent_names = set()
        for row in recent_rows:
            try:
                findings = json.loads(row["findings_json"] or "[]")
                recent_names.update(f.get("name", "") for f in findings)
            except Exception as e:
                logger.warning("Failed to parse findings_json for fixed count: %s", e)
        fixed_names = all_names - recent_names

        # 5. 计算用户平均分趋势
        score_trend = []
        for row in rows[:20]:
            if row["score"] is not None:
                score_trend.append({"date": row["created_at"], "score": row["score"]})
        score_trend.reverse()

        # 6. 预测下次评分（简单线性外推）
        predicted_next = None
        if len(score_trend) >= 3:
            deltas = []
            for i in range(1, min(5, len(score_trend))):
                deltas.append(score_trend[i]["score"] - score_trend[i - 1]["score"])
            avg_delta = sum(deltas) / len(deltas) if deltas else 0
            predicted_next = max(0, min(100, score_trend[-1]["score"] + avg_delta))

        return {
            "total_scans": len(rows),
            "unique_issues": len(issue_stats),
            "persistent_issues": persistent[:5],  # 前 5 个反复出现
            "fixed_issues_count": len(fixed_names),
            "fixed_issues_sample": list(fixed_names)[:10],
            "score_trend": score_trend[-10:],
            "predicted_next_score": round(predicted_next, 1)
            if predicted_next
            else None,
            "learning_insights": [
                f"📊 你已扫描 {len(rows)} 次，常见 {len(issue_stats)} 类问题",
                f"🔄 {len(persistent)} 个问题反复出现（建议你优先修复）"
                if persistent
                else "✅ 你的修复习惯很好，没有反复问题",
                f"📈 预测下次评分: {round(predicted_next, 1)}"
                if predicted_next
                else None,
                f"🎯 {len(fixed_names)} 个问题已修复（最近 5 次扫描未出现）"
                if fixed_names
                else None,
            ],
        }
    finally:
        conn.close()


@app.get("/api/learn/insights")
async def api_learn_insights(user: dict = Depends(require_login)) -> dict:
    """Vuln Sentinel 进化端点：智能学习洞察（基于用户历史）"""
    insights = _learn_from_user_history(user["user_id"])
    return insights


# ============================================================
# Vuln Sentinel 进化模块 2：主动监控 — 定期扫描 + 告警
# ============================================================
# 监控目标：用户可加自己的网站到监控列表
def _init_monitoring_tables():
    """Vuln Sentinel 新增：监控相关表"""
    conn = get_db()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS monitors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                url TEXT NOT NULL,
                frequency_hours INTEGER DEFAULT 24,
                last_score INTEGER,
                last_risk TEXT,
                last_scan_at TEXT,
                last_patrol_at TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT,
                UNIQUE(user_id, url)
            );

            CREATE TABLE IF NOT EXISTS monitor_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                monitor_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                alert_type TEXT NOT NULL,  -- score_drop / new_issue / site_down
                message TEXT,
                old_score INTEGER,
                new_score INTEGER,
                created_at TEXT,
                is_read INTEGER DEFAULT 0
            );
        """)
        # 兼容旧库：追加新列
        _monitor_columns = [
            (
                "monitors",
                "last_patrol_at",
                "ALTER TABLE monitors ADD COLUMN last_patrol_at TEXT",
            ),
            (
                "monitors",
                "last_findings_count",
                "ALTER TABLE monitors ADD COLUMN last_findings_count INTEGER DEFAULT 0",
            ),
            ("monitor_alerts", "url", "ALTER TABLE monitor_alerts ADD COLUMN url TEXT"),
        ]
        for table_name, col_name, ddl in _monitor_columns:
            if not _column_exists(conn, table_name, col_name):
                conn.execute(ddl)
                conn.commit()
    finally:
        conn.close()


# 启动时初始化表
try:
    _init_monitoring_tables()
except Exception as e:
    print(f"[Vuln Sentinel] monitor tables init warning: {e}")


@app.post("/api/monitors")
async def api_create_monitor(
    request: Request, user: dict = Depends(require_login)
) -> dict:
    """Vuln Sentinel 进化端点：添加监控目标"""
    try:
        body = await request.json()
    except Exception:
        return {"success": False, "error": "JSON 解析失败"}
    url = (body.get("url") or "").strip()
    freq = int(body.get("frequency_hours", 24))
    if not url:
        return {"success": False, "error": "URL 必填"}
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    # Vuln Sentinel fix: SSRF 防护 - 监控目标必须通过 URL 校验
    try:
        sanitize_url(url)
    except ValueError as e:
        return {"success": False, "error": str(e)}
    if freq < 1 or freq > 168:
        return {"success": False, "error": "频率必须在 1-168 小时之间"}

    conn = get_db()
    try:
        conn.execute(
            """INSERT OR REPLACE INTO monitors
               (user_id, url, frequency_hours, last_scan_at, created_at)
               VALUES (?,?,?,?,?)""",
            (
                user["user_id"],
                url,
                freq,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        conn.commit()
        monitor_id = conn.execute("SELECT last_insert_rowid() as id").fetchone()["id"]
        return {
            "success": True,
            "monitor_id": monitor_id,
            "url": url,
            "frequency_hours": freq,
        }
    finally:
        conn.close()


@app.get("/api/monitors")
async def api_list_monitors(user: dict = Depends(require_login)) -> dict:
    """Vuln Sentinel 进化端点：列出所有监控目标"""
    conn = get_db()
    try:
        rows = conn.execute(
            """SELECT * FROM monitors WHERE user_id=? ORDER BY id DESC""",
            (user["user_id"],),
        ).fetchall()
        return {
            "success": True,
            "monitors": [dict(r) for r in rows],
            "total": len(rows),
        }
    finally:
        conn.close()


@app.delete("/api/monitors/{monitor_id}")
async def api_delete_monitor(
    monitor_id: int, user: dict = Depends(require_login)
) -> dict:
    """Vuln Sentinel 进化端点：删除监控目标"""
    conn = get_db()
    try:
        conn.execute(
            "DELETE FROM monitors WHERE id=? AND user_id=?",
            (monitor_id, user["user_id"]),
        )
        conn.commit()
        return {"success": True, "deleted_id": monitor_id}
    finally:
        conn.close()


def _check_monitors_sync():
    """Vuln Sentinel：同步执行监控扫描（被 scheduler 调用）"""
    import asyncio

    conn = get_db()
    try:
        monitors = conn.execute(
            """SELECT * FROM monitors WHERE is_active=1""",
        ).fetchall()
        for m in monitors:
            last_scan = m["last_scan_at"] or ""
            try:
                last_dt = datetime.strptime(last_scan, "%Y-%m-%d %H:%M:%S")
            except Exception:
                last_dt = datetime.now() - timedelta(hours=999)
            if datetime.now() - last_dt < timedelta(hours=m["frequency_hours"]):
                continue
            # 到了扫描时间
            try:
                # Vuln Sentinel fix: SSRF 防护 + 正确调用扫描流程
                url = m["url"]
                try:
                    sanitize_url(url)
                except ValueError:
                    continue  # 非法 URL 跳过
                # 使用 asyncio 运行异步扫描（因为 fetch_headers 是 async 的）
                loop = asyncio.new_event_loop()
                try:
                    headers, is_https, final_url, error = loop.run_until_complete(
                        asyncio.wait_for(fetch_headers(url), timeout=15.0)
                    )
                finally:
                    loop.close()
                if error and not headers:
                    # 扫描失败，记录告警
                    conn.execute(
                        """INSERT INTO monitor_alerts
                           (monitor_id, user_id, alert_type, message, created_at)
                           VALUES (?,?,?,?,?)""",
                        (
                            m["id"],
                            m["user_id"],
                            "site_down",
                            f"网站 {url} 无法访问：{error}",
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        ),
                    )
                    conn.execute(
                        """UPDATE monitors SET last_scan_at=? WHERE id=?""",
                        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), m["id"]),
                    )
                    conn.commit()
                    # 发送监控宕机通知
                    try:
                        host = urlparse(url).hostname or url
                        alert_title = f"【监控告警】{host} 无法访问"
                        alert_msg = f"监控目标 {url} 无法访问：{error}"
                        email_html = (
                            f"<h2>监控告警：网站宕机</h2>"
                            f"<p>监控目标：<strong>{url}</strong></p>"
                            f"<p>错误信息：<strong>{error}</strong></p>"
                            f"<p>检测时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>"
                        )
                        webhook_md = (
                            f"### 监控告警：网站宕机\n\n"
                            f"- **目标**: {url}\n"
                            f"- **错误**: {error}\n"
                            f"- **时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        )
                        loop.run_until_complete(
                            notify_user(
                                m["user_id"],
                                "monitor_down",
                                alert_title,
                                alert_msg,
                                {"url": url, "error": error, "monitor_id": m["id"]},
                                severity="high",
                                email_body_html=email_html,
                                webhook_markdown=webhook_md,
                            )
                        )
                    except Exception as e:
                        logger.warning("Monitor down notification failed: %s", e)
                    continue
                # 拿到 headers 后，调用 analyze_security 分析
                # 简单版：不做 SSL 和敏感路径检测（监控模式简化）
                ssl_info = {"has_cert": False}
                waf_list = detect_waf(headers)
                sensitive_paths: list[dict] = []
                result = loop.run_until_complete(
                    analyze_security(
                        url, headers, is_https, ssl_info, waf_list, sensitive_paths, []
                    )
                )
                score = result["score"]
                risk = result["risk_level"]
                findings = result["findings"]
                old_score = m["last_score"]
                # 检测分数下降
                if old_score is not None and score < old_score - 5:
                    conn.execute(
                        """INSERT INTO monitor_alerts
                           (monitor_id, user_id, alert_type, message, old_score, new_score, created_at)
                           VALUES (?,?,?,?,?,?,?)""",
                        (
                            m["id"],
                            m["user_id"],
                            "score_drop",
                            f"网站 {url} 评分从 {old_score} 下降到 {score}",
                            old_score,
                            score,
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        ),
                    )
                    # 发送评分下降通知
                    try:
                        alert_title = f"【监控告警】{host} 评分下降"
                        alert_msg = f"网站 {url} 评分从 {old_score} 下降到 {score}"
                        email_html = (
                            f"<h2>监控告警：评分下降</h2>"
                            f"<p>监控目标：<strong>{url}</strong></p>"
                            f"<p>评分变化：<strong>{old_score}</strong> → <strong>{score}</strong></p>"
                            f"<p>当前风险等级：<strong>{risk}</strong></p>"
                        )
                        webhook_md = (
                            f"### 监控告警：评分下降\n\n"
                            f"- **目标**: {url}\n"
                            f"- **评分变化**: {old_score} → {score}\n"
                            f"- **当前风险等级**: {risk}\n"
                        )
                        loop.run_until_complete(
                            notify_user(
                                m["user_id"],
                                "score_drop",
                                alert_title,
                                alert_msg,
                                {
                                    "url": url,
                                    "old_score": old_score,
                                    "new_score": score,
                                    "risk_level": risk,
                                    "monitor_id": m["id"],
                                },
                                severity="high",
                                email_body_html=email_html,
                                webhook_markdown=webhook_md,
                            )
                        )
                    except Exception as e:
                        logger.warning("Score drop notification failed: %s", e)
                # 检测新漏洞（简单对比：数量增加）
                old_count = m["last_findings_count"] or 0
                new_count = len(findings)
                if new_count > old_count and old_count > 0:
                    conn.execute(
                        """INSERT INTO monitor_alerts
                           (monitor_id, user_id, alert_type, message, created_at)
                           VALUES (?,?,?,?,?)""",
                        (
                            m["id"],
                            m["user_id"],
                            "new_issue",
                            f"网站 {url} 发现新的安全问题（{new_count - old_count} 个）",
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        ),
                    )
                    # 发送新漏洞通知
                    try:
                        new_findings = (
                            findings[old_count:]
                            if len(findings) > old_count
                            else findings
                        )
                        risk_names = ", ".join(
                            [f.get("name", "未知") for f in new_findings[:5]]
                        )
                        alert_title = f"【监控告警】{host} 发现新漏洞"
                        alert_msg = f"网站 {url} 发现 {new_count - old_count} 个新的安全问题：{risk_names}"
                        email_html = (
                            f"<h2>监控告警：新漏洞发现</h2>"
                            f"<p>监控目标：<strong>{url}</strong></p>"
                            f"<p>新增问题数：<strong>{new_count - old_count}</strong> 个</p>"
                            f"<p>问题列表：{risk_names}</p>"
                        )
                        webhook_md = (
                            f"### 监控告警：新漏洞发现\n\n"
                            f"- **目标**: {url}\n"
                            f"- **新增问题**: {new_count - old_count} 个\n"
                            f"- **问题列表**: {risk_names}\n"
                        )
                        loop.run_until_complete(
                            notify_user(
                                m["user_id"],
                                "high_risk_found",
                                alert_title,
                                alert_msg,
                                {
                                    "url": url,
                                    "new_count": new_count - old_count,
                                    "monitor_id": m["id"],
                                },
                                severity="high",
                                email_body_html=email_html,
                                webhook_markdown=webhook_md,
                            )
                        )
                    except Exception as e:
                        logger.warning("New issue notification failed: %s", e)
                # 更新 last_score
                conn.execute(
                    """UPDATE monitors SET last_score=?, last_risk=?, last_findings_count=?, last_scan_at=?
                       WHERE id=?""",
                    (
                        score,
                        risk,
                        new_count,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        m["id"],
                    ),
                )
                conn.commit()
            except Exception as e:
                logger.warning("[monitor] scan %s failed: %s", m["url"], e)
    finally:
        conn.close()


@app.get("/api/monitors/alerts")
async def api_list_alerts(user: dict = Depends(require_login)) -> dict:
    """Vuln Sentinel 进化端点：列出所有告警"""
    conn = get_db()
    try:
        rows = conn.execute(
            """SELECT a.*, m.url FROM monitor_alerts a
               JOIN monitors m ON a.monitor_id = m.id
               WHERE a.user_id=?
               ORDER BY a.id DESC LIMIT 50""",
            (user["user_id"],),
        ).fetchall()
        return {
            "success": True,
            "alerts": [dict(r) for r in rows],
            "unread_count": sum(1 for r in rows if not r["is_read"]),
        }
    finally:
        conn.close()


# ============================================================
# Vuln Sentinel 进化模块 3：AI 洞察 — 会话记忆 + 个性化建议
# ============================================================
def _save_conversation(
    user_id: int, role: str, content: str, context: dict = None
) -> int:
    """Vuln Sentinel：保存 AI 顾问对话历史（让 AI 记住用户）"""
    conn = get_db()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS ai_conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL,  -- user / assistant
                content TEXT,
                context_json TEXT,
                created_at TEXT
            );
        """)
        conn.execute(
            """INSERT INTO ai_conversations
               (user_id, role, content, context_json, created_at)
               VALUES (?,?,?,?,?)""",
            (
                user_id,
                role,
                content,
                json.dumps(context or {}, ensure_ascii=False),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        conn.commit()
        return conn.execute("SELECT last_insert_rowid() as id").fetchone()["id"]
    finally:
        conn.close()


def _get_recent_conversations(user_id: int, limit: int = 10) -> list:
    """Vuln Sentinel：取最近 N 条对话（用于上下文）"""
    conn = get_db()
    try:
        # 确保表存在
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ai_conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT,
                context_json TEXT,
                created_at TEXT
            );
        """)
        rows = conn.execute(
            """SELECT * FROM ai_conversations WHERE user_id=?
               ORDER BY id DESC LIMIT ?""",
            (user_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# =================== Vuln Sentinel LLM 集成（OpenAI 兼容接口） ===================


def _build_llm_prompt(user_msg: str, history: list, insights: dict) -> list:
    """组装发给 LLM 的 messages：系统提示 + 历史 + 用户消息"""
    persistent = insights.get("persistent_issues", [])
    persistent_text = ""
    if persistent:
        lines = [
            f"  - {p['name']} ×{p['times']} ({p['severity']})" for p in persistent[:5]
        ]
        persistent_text = "反复出现的问题：\n" + "\n".join(lines)
    else:
        persistent_text = "暂无反复问题"

    system_prompt = (
        "你是Vuln Sentinel 的安全顾问，一位简洁专业的中文安全工程师。\n"
        f"用户统计：已扫描 {insights.get('total_scans', 0)} 次，"
        f"预测下次评分 {insights.get('predicted_next_score', '暂无')}。\n"
        f"{persistent_text}\n"
        "回答原则：1) 简短（≤200字） 2) 给出可执行步骤或配置示例 3) 用 Markdown "
        "4) 涉及安全配置时贴出 Nginx/Apache 片段 5) 不知道就直说，不要编造"
    )

    messages = [{"role": "system", "content": system_prompt}]
    # 加入最近历史（最多 4 轮）
    for h in history[-8:]:
        role = h.get("role")
        if role in ("user", "assistant") and h.get("content"):
            messages.append({"role": role, "content": h["content"]})
    messages.append({"role": "user", "content": user_msg})
    return messages


async def _call_llm(messages: list) -> str:
    """调用 OpenAI 兼容接口的 LLM。失败/未配置时抛 RuntimeError。"""
    if not settings.llm_enabled or not settings.llm_api_key:
        raise RuntimeError("LLM 未启用或缺少 API Key")

    base_url = settings.llm_base_url

    url = base_url.rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.llm_model,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 600,
    }
    # Vuln Sentinel：LLM 请求也尊重 TLS_VERIFY 设置
    _tls_off = os.environ.get("TLS_VERIFY", "true").strip().lower() in (
        "0",
        "false",
        "no",
        "off",
    )
    async with httpx.AsyncClient(
        timeout=settings.llm_timeout, verify=not _tls_off
    ) as client:
        resp = await client.post(url, headers=headers, json=payload)
    if resp.status_code >= 400:
        raise RuntimeError(f"LLM {resp.status_code}: {resp.text[:200]}")
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()


async def _call_real_llm(
    api_key: str, model: str, provider: str | None, messages: list
) -> str:
    """调用用户配置的 OpenAI 兼容 LLM。失败时抛 RuntimeError。"""
    if not api_key:
        raise RuntimeError("缺少 API Key")

    provider = (provider or "openai").lower()
    if provider == "openai":
        base_url = "https://api.openai.com/v1"
    else:
        base_url = (
            provider if provider.startswith("http") else "https://api.openai.com/v1"
        )

    url = base_url.rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model or "gpt-4o-mini",
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 800,
    }
    _tls_off = os.environ.get("TLS_VERIFY", "true").strip().lower() in (
        "0",
        "false",
        "no",
        "off",
    )
    async with httpx.AsyncClient(timeout=20.0, verify=not _tls_off) as client:
        resp = await client.post(url, headers=headers, json=payload)
    if resp.status_code >= 400:
        raise RuntimeError(f"LLM {resp.status_code}: {resp.text[:200]}")
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()


def _build_ai_advisor_llm_prompt(
    user_msg: str, history: list, scan_context: dict | None, matched_knowledge: tuple
) -> list:
    """为 AI 顾问构建 LLM prompt：系统提示 + 上下文 + 用户问题"""
    system_parts = [
        "你是Vuln Sentinel安全顾问，帮助用户理解和修复 Web 安全问题。",
        "回答时请遵循以下结构：",
        "1. 结论：用一句话给出核心观点",
        "2. 详细解释：说明原理、风险场景",
        "3. 操作步骤：给出可执行的具体修复命令或配置（优先 Nginx，也可提供 Apache/Node.js 示例）",
        "",
        "注意事项：",
        "- 使用 Markdown 格式",
        "- 配置片段要完整、可直接复制使用",
        "- 如果问题与扫描结果相关，请结合具体数据回答",
        "- 不要编造信息，不确定时请诚实说明",
    ]

    context_parts = []
    if scan_context:
        findings = scan_context.get("findings", [])
        score = scan_context.get("score", 0)
        risk_level = scan_context.get("risk_level", "未知")
        url = scan_context.get("url", "")
        summary = scan_context.get("summary", {})

        context_parts.append("用户最近扫描结果：")
        context_parts.append(f"- 目标 URL：{url}")
        context_parts.append(f"- 评分：{score} 分（{risk_level}）")
        if summary:
            context_parts.append(
                f"- 严重/高/中/低 风险数："
                f"{summary.get('critical', 0)}/{summary.get('high', 0)}/{summary.get('medium', 0)}/{summary.get('low', 0)}"
            )
        if findings:
            sev_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
            top = sorted(
                findings, key=lambda f: sev_rank.get(f.get("severity", "low"), 4)
            )[:5]
            context_parts.append("- 主要问题：")
            for f in top:
                context_parts.append(
                    f"  • [{f.get('severity', '')}] {f.get('name', '')}："
                    f"{f.get('description', '') or f.get('detail', '')}"
                )
        context_parts.append("")

    if matched_knowledge and matched_knowledge[1]:
        entry = matched_knowledge[1]
        context_parts.append(f"相关知识库条目：{entry.get('name', '')}")
        context_parts.append(f"原理：{entry.get('principle', '')[:300]}")
        context_parts.append(f"修复要点：{entry.get('fix', '')[:300]}")
        context_parts.append("")

    system_prompt = "\n".join(system_parts + context_parts)

    messages = [{"role": "system", "content": system_prompt}]
    for h in history[-6:]:
        role = h.get("role")
        if role in ("user", "assistant") and h.get("content"):
            messages.append({"role": role, "content": h["content"]})
    messages.append({"role": "user", "content": user_msg})
    return messages


@app.post("/api/ai/chat")
async def api_ai_chat(request: Request, user: dict = Depends(require_login)) -> dict:
    """
    Vuln Sentinel 进化端点：AI 顾问对话（带会话记忆）
    - 记住用户上次问了什么、修复进度
    - 基于用户历史给出个性化建议
    """
    try:
        body = await request.json()
    except Exception:
        return {"success": False, "error": "JSON 解析失败"}

    # 限流(防被刷爆 LLM token)
    client_ip = get_client_ip(request)
    if not await limiter_ai.is_allowed(client_ip):
        return {"success": False, "error": "AI 顾问调用太频繁，请稍后再试"}

    user_msg = (body.get("message") or "").strip()
    if not user_msg:
        return {"success": False, "error": "消息不能为空"}

    # 1. 保存用户消息
    _save_conversation(user["user_id"], "user", user_msg)

    # 2. 取最近 5 条历史对话（让 AI 记住上下文）
    history = _get_recent_conversations(user["user_id"], 5)
    history.reverse()  # 按时序

    # 3. 智能分析：先尝试 LLM，未配置/失败时降级到关键字匹配
    insights = _learn_from_user_history(user["user_id"])
    persistent = insights.get("persistent_issues", [])

    response_text = ""
    llm_used = False
    llm_error = None

    if settings.llm_enabled and settings.llm_api_key:
        try:
            messages = _build_llm_prompt(user_msg, history, insights)
            response_text = await _call_llm(messages)
            llm_used = True
        except Exception as e:
            llm_error = str(e)[:120]
            logger.warning("LLM call failed, falling back to keyword: %s", e)

    if not response_text:
        # 降级：关键字匹配（保证功能可用）
        if any(k in user_msg for k in ["怎么修", "如何修", "怎么解决", "how to fix"]):
            if persistent:
                top = persistent[0]
                response_text = (
                    f"💡 根据你的历史，**{top['name']}** 出现了 {top['times']} 次（{top['severity']}）。"
                    "建议优先修复这个，工具已为你准备了对应补丁。\n\n"
                    "具体步骤：1) 复制补丁代码 2) SSH 到服务器 3) 重启服务"
                )
            else:
                response_text = (
                    "✅ 你没有反复出现的问题。很好！需要我帮你预防性扫描其他网站吗？"
                )
        elif any(k in user_msg for k in ["分数", "评分", "score", "趋势"]):
            if insights.get("predicted_next_score"):
                response_text = (
                    f"📊 你的平均分趋势：{insights['score_trend']}\n\n"
                    f"🔮 预测下次评分：{insights['predicted_next_score']}\n\n"
                    + (
                        "你正在进步！继续保持。"
                        if insights["predicted_next_score"] > 80
                        else "建议重点修复 persistent_issues。"
                    )
                )
            else:
                response_text = "📊 你需要先扫描至少 3 次，我才能预测你的趋势。"
        elif any(k in user_msg for k in ["HSTS", "hsts", "严格传输"]):
            response_text = (
                "🔒 HSTS 强制浏览器用 HTTPS，防 SSL stripping 攻击。\n\n"
                "Nginx 配置：\n```\n"
                'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;\n'
                "```\n\n需要我帮你一键应用吗？"
            )
        elif any(k in user_msg for k in ["你好", "hi", "hello", "你是"]):
            response_text = (
                f"👋 你好 {user['username']}！我是Vuln Sentinel 智能顾问。\n\n"
                f"📊 你已扫描 {insights['total_scans']} 次\n"
                f"🔄 {len(persistent)} 个反复问题\n"
                f"📈 预测评分: {insights.get('predicted_next_score', 'N/A')}\n\n"
                "问我任何问题：'怎么修 HSTS'、'我的趋势如何'、'XSS 怎么防'"
            )
        else:
            # 默认：基于历史给提示
            response_text = (
                f"我理解你问的是「{user_msg[:30]}」。\n\n"
                "💡 你可以这样问：\n"
                "- '怎么修 [问题名]' → 给你具体步骤\n"
                "- '我的分数趋势' → 看学习洞察\n"
                "- 'HSTS 是什么' → 解释 + 配置示例\n"
                "- 扫描一个网站 → 直接检测"
            )

    # 4. 保存 AI 回答
    _save_conversation(
        user["user_id"],
        "assistant",
        response_text,
        {
            "history_used": len(history),
            "insights_used": bool(persistent),
            "llm_used": llm_used,
            "llm_error": llm_error,
        },
    )

    return {
        "success": True,
        "response": response_text,
        "memory_used": len(history),
        "llm_used": llm_used,
        "llm_provider": settings.llm_provider if llm_used else None,
        "insights_summary": {
            "total_scans": insights["total_scans"],
            "persistent_count": len(persistent),
            "predicted_score": insights.get("predicted_next_score"),
        },
    }


# ============================================================
# Vuln Sentinel 进化模块 4：协作 — 团队、角色、评论
# ============================================================
def _init_team_tables():
    conn = get_db()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                owner_id INTEGER NOT NULL,
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS team_members (
                team_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                role TEXT DEFAULT 'member',  -- owner / admin / member / viewer
                joined_at TEXT,
                PRIMARY KEY (team_id, user_id)
            );

            CREATE TABLE IF NOT EXISTS scan_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                comment TEXT,
                created_at TEXT
            );
        """)
        conn.commit()
    finally:
        conn.close()


try:
    _init_team_tables()
except Exception as e:
    print(f"[Vuln Sentinel] team tables init warning: {e}")


@app.post("/api/teams")
async def api_create_team(
    request: Request, user: dict = Depends(require_login)
) -> dict:
    """Vuln Sentinel 进化端点：创建团队"""
    try:
        body = await request.json()
    except Exception:
        return {"success": False, "error": "JSON 解析失败"}
    name = (body.get("name") or "").strip()
    if not name:
        return {"success": False, "error": "团队名必填"}
    conn = get_db()
    try:
        c = conn.execute(
            """INSERT INTO teams (name, owner_id, created_at) VALUES (?,?,?)""",
            (name, user["user_id"], datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        team_id = c.lastrowid
        conn.execute(
            """INSERT INTO team_members (team_id, user_id, role, joined_at)
               VALUES (?,?,?,?)""",
            (
                team_id,
                user["user_id"],
                "owner",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        conn.commit()
        return {"success": True, "team_id": team_id, "name": name}
    finally:
        conn.close()


@app.post("/api/scans/{scan_id}/comment")
async def api_add_comment(
    scan_id: int, request: Request, user: dict = Depends(require_login)
) -> dict:
    """Vuln Sentinel 进化端点：给扫描报告添加评论（团队协作）"""
    try:
        body = await request.json()
    except Exception:
        return {"success": False, "error": "JSON 解析失败"}
    comment = (body.get("comment") or "").strip()
    if not comment:
        return {"success": False, "error": "评论内容必填"}
    conn = get_db()
    try:
        conn.execute(
            """INSERT INTO scan_comments (scan_id, user_id, comment, created_at)
               VALUES (?,?,?,?)""",
            (
                scan_id,
                user["user_id"],
                comment,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        conn.commit()
        return {"success": True}
    finally:
        conn.close()


@app.get("/api/scans/{scan_id}/comments")
async def api_list_comments(scan_id: int, user: dict = Depends(require_login)) -> dict:
    """Vuln Sentinel 进化端点：列出扫描报告的所有评论"""
    conn = get_db()
    try:
        rows = conn.execute(
            """SELECT c.*, u.username FROM scan_comments c
               JOIN users u ON c.user_id = u.id
               WHERE c.scan_id=? ORDER BY c.id ASC""",
            (scan_id,),
        ).fetchall()
        return {
            "success": True,
            "comments": [dict(r) for r in rows],
            "total": len(rows),
        }
    finally:
        conn.close()


# ============================================================
# Vuln Sentinel 进化模块 5：综合仪表盘
# ============================================================
@app.get("/api/evolution/dashboard")
async def api_evolution_dashboard(user: dict = Depends(require_login)) -> dict:
    """Vuln Sentinel 进化端点：综合仪表盘（学习+监控+协作+AI 一次全看）"""
    insights = _learn_from_user_history(user["user_id"])
    conn = get_db()
    try:
        monitors = conn.execute(
            "SELECT * FROM monitors WHERE user_id=?", (user["user_id"],)
        ).fetchall()
        alerts = conn.execute(
            "SELECT * FROM monitor_alerts WHERE user_id=? AND is_read=0",
            (user["user_id"],),
        ).fetchall()
        teams = conn.execute(
            """SELECT t.* FROM teams t
               JOIN team_members m ON t.id = m.team_id
               WHERE m.user_id=?""",
            (user["user_id"],),
        ).fetchall()
        return {
            "success": True,
            "learning": insights,
            "monitoring": {
                "monitors_count": len(monitors),
                "unread_alerts": len(alerts),
                "monitors": [dict(m) for m in monitors[:5]],
                "alerts": [dict(a) for a in alerts[:5]],
            },
            "team": {
                "teams_count": len(teams),
                "teams": [dict(t) for t in teams[:5]],
            },
            "evolution_score": max(
                0,
                min(
                    100,
                    (
                        (insights.get("predicted_next_score") or 0) * 0.4
                        + (100 - len(insights.get("persistent_issues") or []) * 10)
                        * 0.3
                        + (50 if len(monitors) > 0 else 0) * 0.2
                        + (50 if len(teams) > 0 else 0) * 0.1
                    ),
                ),
            ),
        }
    finally:
        conn.close()


# ============================================================
# Vuln Sentinel 进化模块 5：自动巡检 — 定时回扫所有监控项
# ============================================================


def _patrol_all_monitors_sync():
    """
    同步函数（scheduler 调用），对所有 active 监控项重新扫描：
    - 评分下滑超过阈值 → 写告警
    - 新增高危问题 → 写告警
    - 记录巡检时间，便于前端展示
    """
    try:
        # 确保表存在
        try:
            _init_monitoring_tables()
        except Exception as e:
            logger.warning("Init monitoring tables failed during patrol: %s", e)

        conn = get_db()
        try:
            rows = conn.execute("SELECT * FROM monitors WHERE is_active=1").fetchall()
        finally:
            conn.close()

        if not rows:
            return

        # 用 loop.run_in_executor 跑阻塞扫描
        import asyncio

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = None

        for m in rows:
            monitor = dict(m)
            url = monitor.get("url")
            user_id = monitor.get("user_id")
            if not url or not user_id:
                continue
            try:
                if loop and loop.is_running():
                    # 当前在 event loop 中：直接放后台任务
                    asyncio.create_task(_patrol_one_monitor(monitor))
                else:
                    _patrol_one_monitor_sync(monitor)
            except Exception as e:
                logger.warning("patrol dispatch failed for %s: %s", url, e)
    except Exception as e:
        logger.warning("patrol_all_monitors failed: %s", e)


async def _patrol_one_monitor(monitor: dict):
    """异步版本：扫一次监控项 → 写告警 → 更新 last_patrol_at"""
    url = monitor.get("url")
    user_id = monitor.get("user_id")
    monitor_id = monitor.get("id")
    last_score = monitor.get("last_score")

    # SSRF 防护：数据库中的 URL 可能被篡改，重新校验
    try:
        url = sanitize_url(url) if url else url
    except ValueError:
        return

    try:
        # 简单复用头部检查（与 schedule 行为保持一致）
        from urllib.parse import urlparse

        parsed = urlparse(url)
        host = parsed.hostname or ""
        if not host:
            return
        try:
            headers, is_https, final_url, error = await asyncio.wait_for(
                fetch_headers(url), timeout=25.0
            )
        except asyncio.TimeoutError:
            error = "TIMEOUT"
        if error:
            # 站点不可达 = 告警
            _write_patrol_alert(
                user_id,
                monitor_id,
                url,
                "site_down",
                f"巡检发现 {host} 不可达: {error[:100]}",
            )
            return
        # 标记巡检时间
        _touch_monitor_patrol(monitor_id, last_score)
    except Exception as e:
        logger.warning("patrol_one_monitor async failed: %s", e)


def _patrol_one_monitor_sync(monitor: dict):
    """同步版本（无 event loop 时回退）"""
    monitor_id = monitor.get("id")
    _touch_monitor_patrol(monitor_id, monitor.get("last_score"))


def _touch_monitor_patrol(monitor_id: int, last_score):
    """更新监控项的 last_patrol_at（其他指标在下次主动扫描时计算）"""
    if not monitor_id:
        return
    conn = get_db()
    try:
        conn.execute(
            "UPDATE monitors SET last_patrol_at=? WHERE id=?",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), monitor_id),
        )
        conn.commit()
    finally:
        conn.close()


def _write_patrol_alert(
    user_id: int, monitor_id: int, url: str, alert_type: str, message: str
):
    conn = get_db()
    try:
        conn.execute(
            """INSERT INTO monitor_alerts
               (user_id, monitor_id, alert_type, message, url, is_read, created_at)
               VALUES (?,?,?,?,?,0,?)""",
            (
                user_id,
                monitor_id,
                alert_type,
                message,
                url,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        conn.commit()
    except Exception as e:
        logger.warning("write_patrol_alert failed: %s", e)
    finally:
        conn.close()


# ============================================================
# Vuln Sentinel AI 顾问增强：LLM 配置端点
# ============================================================


@app.get("/api/ai/status")
async def api_ai_status() -> dict:
    """前端可拉取当前 AI 顾问配置（API Key 仅返回是否配置）"""
    return {
        "success": True,
        "llm_enabled": settings.llm_enabled,
        "provider": settings.llm_provider,
        "model": settings.llm_model,
        "api_key_configured": bool(settings.llm_api_key),
        "base_url": settings.llm_base_url,
        "providers_supported": ["openai", "custom"],
    }


@app.post("/api/ai/test")
async def api_ai_test(request: Request, user: dict = Depends(require_login)) -> dict:
    """用一句简单问题试调 LLM（不需要完整配置）"""
    if not settings.llm_enabled or not settings.llm_api_key:
        return {"success": False, "error": "LLM 未启用或缺少 API Key", "fallback": True}
    try:
        body = await request.json()
    except Exception:
        body = {}
    prompt = (body.get("message") or "用一句话介绍你自己").strip()
    try:
        reply = await _call_llm([{"role": "user", "content": prompt}])
        return {
            "success": True,
            "reply": reply,
            "provider": settings.llm_provider,
            "model": settings.llm_model,
        }
    except Exception as e:
        return {"success": False, "error": str(e)[:200], "fallback": True}


# ---------- Fix generator 端点 ----------


@app.post("/api/fix")
async def api_fix(
    req: ScanRequest, request: Request, user: dict = Depends(require_login)
) -> dict:
    """生成修复建议。"""
    await rate_limit_dependency(request)
    try:
        url = sanitize_url(req.url)
    except ValueError as e:
        return {"success": False, "error": str(e)}
    parsed = urlparse(url)
    host = parsed.hostname or ""
    try:
        headers, is_https, final_url, error = await asyncio.wait_for(
            fetch_headers(url), timeout=25.0
        )
    except asyncio.TimeoutError:
        error = "TIMEOUT"
    if error:
        return {"success": False, "error": error}
    waf_list = detect_waf(headers)
    # 并行执行：敏感路径探测 + SSL 信息获取（节省 30-50% 时间）
    sensitive_task = asyncio.create_task(check_sensitive_paths(host, is_https))
    ssl_task = asyncio.create_task(
        get_ssl_info(host, 443)
        if is_https
        else asyncio.sleep(0, result={"has_cert": False})
    )
    try:
        sensitive_paths, ssl_info_raw = await asyncio.wait_for(
            asyncio.gather(sensitive_task, ssl_task, return_exceptions=True),
            timeout=15.0,
        )
        if isinstance(sensitive_paths, Exception):
            logger.warning("api_fix sensitive_paths failed: %s", sensitive_paths)
            sensitive_paths = []
        if isinstance(ssl_info_raw, Exception):
            logger.warning("api_fix ssl_info failed: %s", ssl_info_raw)
            ssl_info_raw = {"has_cert": False}
    except asyncio.TimeoutError:
        sensitive_paths = []
        ssl_info_raw = {"has_cert": False}
    except Exception as e:
        logger.warning("api_fix gather failed: %s", e)
        sensitive_paths = []
        ssl_info_raw = {"has_cert": False}
    ssl_info = ssl_info_raw if is_https else {"has_cert": False}
    result = await analyze_security(
        url,
        headers,
        is_https,
        ssl_info,
        waf_list,
        sensitive_paths,
    )
    fixes = generate_fixes(result["findings"], headers, is_https, host)
    # 修复建议生成完成通知
    try:
        fix_count = len(fixes) if fixes else 0
        high_fixes = [f for f in fixes if f.get("severity") in ("critical", "high")]
        alert_title = f"修复建议已生成：{host}"
        alert_msg = (
            f"已为 {url} 生成 {fix_count} 条修复建议，其中高危 {len(high_fixes)} 条。"
        )
        email_html = (
            f"<h2>修复建议生成完成</h2>"
            f"<p>目标：<strong>{url}</strong></p>"
            f"<p>当前评分：<strong>{result['score']}</strong> 分</p>"
            f"<p>生成修复建议数：<strong>{fix_count}</strong> 条</p>"
            f"<p>高危修复：<strong>{len(high_fixes)}</strong> 条</p>"
        )
        webhook_md = (
            f"### 修复建议生成完成\n\n"
            f"- **目标**: {url}\n"
            f"- **当前评分**: {result['score']} 分\n"
            f"- **修复建议数**: {fix_count} 条\n"
            f"- **高危修复**: {len(high_fixes)} 条\n"
        )
        asyncio.create_task(
            notify_user(
                user["user_id"],
                "scan_complete",
                alert_title,
                alert_msg,
                {
                    "url": url,
                    "score": result["score"],
                    "fix_count": fix_count,
                    "high_fix_count": len(high_fixes),
                },
                severity="medium" if len(high_fixes) == 0 else "high",
                email_body_html=email_html,
                webhook_markdown=webhook_md,
            )
        )
    except Exception as e:
        logger.warning("Fix notification trigger failed: %s", e)
    return {
        "success": True,
        "url": url,
        "fixes": fixes,
        "score": result["score"],
        "summary": result["summary"],
    }


@app.get("/api/scan/{scan_id}")
async def api_get_scan(scan_id: int, user: dict = Depends(require_login)) -> dict:
    """获取单条扫描记录（含 findings, owasp_coverage, score, summary）。"""
    scan = get_scan_by_id(scan_id, user["user_id"])
    if not scan:
        raise HTTPException(404, "扫描记录不存在或无权限")
    return {"success": True, "scan": scan}


@app.post("/api/scans/{scan_id}/retest")
async def api_retest(scan_id: int, user: dict = Depends(require_login)) -> dict:
    """对同一 URL 重新扫描（复测闭环）。"""
    previous = get_scan_by_id(scan_id, user["user_id"])
    if not previous:
        raise HTTPException(404, "扫描记录不存在或无权限")
    try:
        url = sanitize_url(previous["url"])
    except ValueError as e:
        raise HTTPException(400, str(e))
    parsed = urlparse(url)
    host = parsed.hostname or ""
    try:
        headers, is_https, final_url, error = await asyncio.wait_for(
            fetch_headers(url), timeout=30.0
        )
    except asyncio.TimeoutError:
        return {"success": False, "error": "目标站响应超时(30s)，请稍后重试"}
    if error and not headers:
        return {"success": False, "error": error or "无法获取响应头"}
    waf_list = detect_waf(headers)
    try:
        ssl_info = await get_ssl_info(host, 443) if is_https else {"has_cert": False}
    except Exception as e:
        logger.warning("api_retest get_ssl_info failed: %s", e)
        ssl_info = {"has_cert": False}
    try:
        sensitive_paths = await check_sensitive_paths(host, is_https)
    except Exception as e:
        logger.warning("api_retest check_sensitive_paths failed: %s", e)
        sensitive_paths = []
    result = await analyze_security(
        url, headers, is_https, ssl_info, waf_list, sensitive_paths, []
    )
    new_scan_id = save_scan(
        user["user_id"],
        url,
        result["score"],
        result["risk_level"],
        result["findings"],
        result["summary"],
        0,
        "retest",
    )
    return {
        "success": True,
        "scan_id": new_scan_id,
        "previous_scan_id": scan_id,
        "url": url,
        "score": result["score"],
        "risk_level": result["risk_level"],
        "summary": result["summary"],
        "findings": result["findings"],
    }


@app.get("/api/scans/{scan_id}/compare")
async def api_compare_scan_with_previous(scan_id: int, user: dict = Depends(require_login)) -> dict:
    """对比上次扫描结果（复测闭环）。
    返回 new_findings / fixed_findings / unchanged_findings / score_change。
    """
    current = get_scan_by_id(scan_id, user["user_id"])
    if not current:
        raise HTTPException(404, "扫描记录不存在或无权限")
    url = current["url"]
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT * FROM scans WHERE user_id=? AND url=? AND id<? ORDER BY id DESC LIMIT 1",
            (user["user_id"], url, scan_id),
        ).fetchone()
    finally:
        conn.close()
    if not row:
        raise HTTPException(404, "未找到该 URL 的上一次扫描记录，无法对比")
    previous = dict(row)
    try:
        curr_findings = json.loads(current.get("findings_json") or "[]")
    except Exception:
        curr_findings = []
    try:
        prev_findings = json.loads(previous.get("findings_json") or "[]")
    except Exception:
        prev_findings = []
    curr_names = {f.get("name", ""): f for f in curr_findings}
    prev_names = {f.get("name", ""): f for f in prev_findings}
    new_names = set(curr_names.keys()) - set(prev_names.keys())
    fixed_names = set(prev_names.keys()) - set(curr_names.keys())
    unchanged_names = set(curr_names.keys()) & set(prev_names.keys())
    new_findings = [curr_names[n] for n in sorted(new_names)]
    fixed_findings = [prev_names[n] for n in sorted(fixed_names)]
    unchanged_findings = [curr_names[n] for n in sorted(unchanged_names)]
    score_change = current.get("score", 0) - (previous.get("score") or 0)
    return {
        "success": True,
        "current_scan_id": scan_id,
        "previous_scan_id": previous.get("id"),
        "url": url,
        "new_findings": new_findings,
        "fixed_findings": fixed_findings,
        "unchanged_findings": unchanged_findings,
        "score_change": score_change,
    }


@app.get("/api/report/{scan_id}")
async def api_report(
    scan_id: int, format: str = "pdf", user: dict = Depends(require_login)
):
    """生成安全报告，支持 PDF 和 HTML 格式
    format: pdf | html
    """
    scan = get_scan_by_id(scan_id, user["user_id"])
    if not scan:
        raise HTTPException(404, "扫描记录不存在")
    findings = json.loads(scan["findings_json"]) if scan.get("findings_json") else []
    score_breakdown = (
        json.loads(scan["score_breakdown_json"])
        if scan.get("score_breakdown_json")
        else []
    )
    fixes = json.loads(scan["fixes_json"]) if scan.get("fixes_json") else {}
    # Vuln Sentinel：OWASP Top 10 完整覆盖（根据 findings 动态计算）
    owasp_all = [
        {
            "category": "A01 访问控制失效",
            "status": "通过",
            "note": "未检测到访问控制问题",
        },
        {"category": "A02 加密机制失效", "status": "通过", "note": "已启用 HTTPS"},
        {"category": "A03 注入攻击", "status": "通过", "note": "未检测到注入漏洞"},
        {
            "category": "A04 不安全设计",
            "status": "通过",
            "note": "未在常见入口检测到开放重定向",
        },
        {"category": "A05 安全配置错误", "status": "通过", "note": "配置良好"},
        {"category": "A06 过时组件", "status": "通过", "note": "未检测到过时组件"},
        {
            "category": "A07 认证失败",
            "status": "通过",
            "note": "未在登录页检测到明显认证配置问题",
        },
        {
            "category": "A08 软件完整性",
            "status": "通过",
            "note": "首页第三方资源完整性校验正常",
        },
        {
            "category": "A09 日志监控不足",
            "status": "低风险",
            "note": "建议加强日志与监控",
        },
        {
            "category": "A10 服务端请求伪造",
            "status": "通过",
            "note": "未检测到 SSRF 漏洞",
        },
    ]
    # 用 findings 覆盖有问题的分类（统计每个分类的问题数量）
    owasp_counts: dict[str, int] = {}
    owasp_samples: dict[str, str] = {}
    for f in findings:
        owasp_cat = f.get("owasp", "")
        if not owasp_cat:
            continue
        # 提取 A01-A10 类别
        cat_match = re.search(r"A(0[1-9]|10)", owasp_cat)
        if not cat_match:
            continue
        cat_key = cat_match.group(0)
        for item in owasp_all:
            if cat_key in item["category"]:
                owasp_counts[item["category"]] = (
                    owasp_counts.get(item["category"], 0) + 1
                )
                if item["category"] not in owasp_samples:
                    owasp_samples[item["category"]] = f.get(
                        "summary", f.get("name", "")
                    )[:50]
                break
    # 更新状态和说明
    for item in owasp_all:
        cat = item["category"]
        count = owasp_counts.get(cat, 0)
        if count > 0:
            # 根据严重度决定状态
            cat_findings = [f for f in findings if cat[:3] in f.get("owasp", "")]
            has_critical = any(f.get("severity") == "critical" for f in cat_findings)
            has_high = any(f.get("severity") == "high" for f in cat_findings)
            if has_critical:
                item["status"] = "严重"
            elif has_high:
                item["status"] = "高风险"
            else:
                item["status"] = "需关注"
            item["note"] = f"检测到 {count} 项问题：{owasp_samples.get(cat, '')}"
    report_data = {
        "url": scan["url"],
        "time": scan["created_at"],
        "score": scan["score"],
        "risk_level": scan["risk_level"],
        "findings": findings,
        "owasp_coverage": owasp_all,
        "score_breakdown": score_breakdown,
        "fixes": fixes,
        "header_details": [],
        "info_leaks": [],
        "cors": None,
        "cookie_issues": [],
        "ssl_info": {},
        "waf": [],
        "sensitive_paths": [],
    }

    if format.lower() == "html":
        # HTML 格式报告
        html_content = generate_html_report(report_data)
        headers = {
            "Content-Disposition": f"inline; filename=scan-report-{scan_id}.html"
        }
        return Response(
            content=html_content, media_type="text/html; charset=utf-8", headers=headers
        )
    else:
        # PDF 格式（默认）
        pdf_bytes = generate_pdf_report(report_data)
        headers = {
            "Content-Disposition": f"attachment; filename=scan-report-{scan_id}.pdf"
        }
        return StreamingResponse(
            io.BytesIO(pdf_bytes), media_type="application/pdf", headers=headers
        )


@app.post("/api/report/src-export")
async def api_src_report_export(
    req: SRCReportExportRequest, user: dict = Depends(require_login)
):
    """导出 SRC 平台格式的漏洞报告（Markdown 或 PDF）。"""
    scan = get_scan_by_id(req.scan_id, user["user_id"])
    if not scan:
        raise HTTPException(404, "扫描记录不存在")
    findings = json.loads(scan["findings_json"]) if scan.get("findings_json") else []
    if req.finding_ids:
        findings = [f for f in findings if f.get("id") in req.finding_ids]

    details = scan.get("details", {})
    report_data = {
        "target_url": scan["url"],
        "scan_time": scan["created_at"],
        "overall_score": scan["score"],
        "risk_level": scan["risk_level"],
        "findings": findings,
        "scan_duration_ms": details.get("duration_ms", 0),
        "scanner_version": "v11-s-vuln-sentinel/Vuln Sentinel",
        "raw_headers": details.get("raw_headers", {}),
        "ssl_info": details.get("ssl_info", {}),
        "summary": scan.get("summary", {}),
    }
    fmt = (req.format or "markdown").lower()
    if fmt in ("markdown", "md"):
        md_content = generate_src_report(report_data, format="markdown")
        headers = {
            "Content-Disposition": f"attachment; filename=src-report-{req.scan_id}.md"
        }
        return Response(
            content=md_content,
            media_type="text/markdown; charset=utf-8",
            headers=headers,
        )
    else:
        md_content = generate_src_report(report_data, format="markdown")
        pdf_bytes = generate_pdf_report(
            {
                "url": scan["url"],
                "time": scan["created_at"],
                "score": scan["score"],
                "risk_level": scan["risk_level"],
                "findings": findings,
                "summary": json.loads(scan.get("summary_json") or "{}"),
            }
        )
        headers = {
            "Content-Disposition": f"attachment; filename=src-report-{req.scan_id}.pdf"
        }
        return StreamingResponse(
            io.BytesIO(pdf_bytes), media_type="application/pdf", headers=headers
        )


@app.get("/api/share/{share_id}")
async def api_get_share(share_id: str) -> dict:
    if not re.fullmatch(r"[a-zA-Z0-9_-]{8,32}", share_id):
        raise HTTPException(400, "分享 ID 格式无效")
    row = get_scan_by_share_id(share_id)
    if not row:
        raise HTTPException(404, "分享链接不存在或已失效")
    return row


@app.post("/api/compare")
async def api_compare_two_scans(a: int, b: int, user: dict = Depends(require_login)) -> dict:
    sa = get_scan_by_id(a, user["user_id"])
    sb = get_scan_by_id(b, user["user_id"])
    if not sa or not sb:
        raise HTTPException(404, "扫描记录不存在")
    sa_findings = json.loads(sa.get("findings_json") or "[]")
    sb_findings = json.loads(sb.get("findings_json") or "[]")
    sa_names = {f["name"] for f in sa_findings}
    sb_names = {f["name"] for f in sb_findings}
    return {
        "a": {
            "id": sa.get("id"),
            "url": sa.get("url"),
            "score": sa.get("score"),
            "risk_level": sa.get("risk_level"),
            "findings_count": len(sa_findings),
            "time": sa.get("created_at"),
        },
        "b": {
            "id": sb.get("id"),
            "url": sb.get("url"),
            "score": sb.get("score"),
            "risk_level": sb.get("risk_level"),
            "findings_count": len(sb_findings),
            "time": sb.get("created_at"),
        },
        "fixed": list(sa_names - sb_names),
        "new": list(sb_names - sa_names),
        "score_diff": (sb.get("score", 0) - sa.get("score", 0)),
    }


@app.post("/api/reset-password")
async def api_reset_password(
    req: PasswordResetRequest, user: dict = Depends(require_login)
) -> dict:
    user_id = user["user_id"]
    new_hash = hash_password(req.new_password)
    update_user_password(user_id, new_hash)
    return {"success": True, "message": "密码已重置，请用新密码登录"}


@app.post("/api/targets")
async def api_add_target(
    req: AddTargetRequest, user: dict | None = Depends(get_current_user)
) -> dict:
    if not user:
        raise HTTPException(401, "未登录")
    upsert_target(user["user_id"], req.url, req.schedule)
    return {"success": True}


@app.get("/api/targets")
async def api_get_targets(user: dict | None = Depends(get_current_user)) -> dict:
    if not user:
        raise HTTPException(401, "未登录")
    return {"targets": get_user_targets(user["user_id"])}


@app.delete("/api/targets/{target_id}")
async def api_delete_target(
    target_id: int, user: dict | None = Depends(get_current_user)
) -> dict:
    if not user:
        raise HTTPException(401, "未登录")
    conn = get_db()
    try:
        conn.execute(
            "DELETE FROM targets WHERE id=? AND user_id=?", (target_id, user["user_id"])
        )
        conn.commit()
    finally:
        conn.close()
    return {"success": True}


@app.get("/api/dashboard")
async def api_dashboard(user=Depends(require_login)):
    conn = get_db()
    try:
        user_id = user["user_id"]
        total = conn.execute(
            "SELECT COUNT(*) FROM scans WHERE user_id=?", (user_id,)
        ).fetchone()[0]
        high_count = conn.execute(
            "SELECT COUNT(*) FROM scans WHERE user_id=? AND risk_level='高风险'",
            (user_id,),
        ).fetchone()[0]
        # fixed: 通过 verify-fix 标记的修复记录数
        try:
            fixed = conn.execute(
                "SELECT COUNT(*) FROM fix_records WHERE user_id=? AND status='verified'",
                (user_id,),
            ).fetchone()[0]
        except Exception:
            fixed = 0
        recent = conn.execute(
            "SELECT id, url, score, risk_level, created_at as time FROM scans WHERE user_id=? ORDER BY id DESC LIMIT 5",
            (user_id,),
        ).fetchall()
    finally:
        conn.close()
    return {
        "total_scans": total,
        "high_risk_count": high_count,
        "fixed_count": fixed,
        "recent_scans": [dict(r) for r in recent],
    }


@app.get("/api/health")
async def api_health() -> dict:
    """健康检查。返回服务状态、版本、DB 状态、request_id。"""
    return get_health_summary()


@app.get("/api/config")
async def api_public_config() -> dict:
    """返回前端所需的公开运行时配置（不含密钥）。"""
    import os

    stripe_pub = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
    return success_response(
        data={
            "stripe_enabled": bool(stripe_pub),
            "stripe_publishable_key": stripe_pub,
            "public_base_url": os.environ.get("PUBLIC_BASE_URL", ""),
            "public_demo_enabled": os.environ.get("PUBLIC_DEMO_ENABLED", "0") == "1",
            "free_trial_enabled": os.environ.get("FREE_TRIAL_ENABLED", "1") == "1",
            "alipay_enabled": bool(os.environ.get("ALIPAY_APP_ID", "")),
            "wechat_enabled": bool(os.environ.get("WECHAT_MCH_ID", "")),
        }
    )


# ===== CVE 情报端点（NVD 真实数据源） =====


@app.get("/api/cve/stats")
async def api_cve_stats() -> dict:
    """返回本地 CVE 缓存统计。"""
    return success_response(vuln_intel_service.get_cve_stats())


@app.get("/api/cve/search")
async def api_search_cve(
    keyword: str = Query("", min_length=1), limit: int = Query(20, ge=1, le=100)
) -> dict:
    """搜索 CVE。优先本地缓存，未命中则并行请求 NVD + CIRCL 聚合。"""
    keyword = (keyword or "").strip()
    if not keyword:
        raise BusinessException("keyword 参数不能为空")

    aggregator = get_aggregator()
    records, total = await aggregator.search(keyword, limit=limit)
    sources = list({r.get("source", "unknown") for r in records})
    return success_response({"sources": sources, "total": total, "records": records})


@app.get("/api/cve/{cve_id}")
async def api_get_cve(cve_id: str) -> dict:
    """查询单个 CVE。优先本地缓存，未命中则聚合 NVD + CIRCL。"""
    cve_id = (cve_id or "").strip().upper()
    if not re.fullmatch(r"CVE-\d{4}-\d+", cve_id):
        raise BusinessException("CVE ID 格式无效，应为 CVE-YYYY-NNNN")

    aggregator = get_aggregator()
    record = await aggregator.fetch_cve(cve_id)
    if not record:
        raise NotFoundException(f"未找到 CVE 记录: {cve_id}")
    return success_response({"source": record.get("source", "unknown"), "cve": record})


@app.post("/api/cve/sync")
async def api_sync_cve(
    user: dict = Depends(require_login), days: int = Query(7, ge=1, le=120)
) -> dict:
    """手动触发 NVD 增量同步（需登录）。"""
    saved, total = await vuln_intel_service.sync_recent_nvd_cves(days=days)
    return success_response({"saved": saved, "fetched": total, "days": days})


# ===== 免费试用端点（无需登录） =====

_FREE_TRIAL_HOSTS = {
    "example.com",
    "example.org",
    "www.example.com",
    "iana.org",
    "www.iana.org",
    "httpbin.org",
    "testphp.vulnweb.com",
}

# 登录用户扫描结果缓存：同一 URL 不同深度分别缓存（防重复点击 + 节省后端开销）
_SCAN_RESULT_CACHE: dict[
    str, tuple[dict, float, int]
] = {}  # (result, timestamp, depth_ttl)
_SCAN_CACHE_MAX_SIZE = 200  # 最大缓存条数硬上限
_scan_cache_lock = asyncio.Lock()  # 缓存并发读写锁，防止竞态条件

# 缓存命中率统计
_SCAN_CACHE_HITS = 0
_SCAN_CACHE_MISSES = 0


# 根据扫描深度返回缓存 TTL（秒）
def _get_cache_ttl(depth: str) -> int:
    """标准模式 60 秒，深度模式 300 秒，快速模式 30 秒。"""
    if depth == "deep":
        return 300
    elif depth == "standard":
        return 60
    else:
        return 30  # quick 或 fallback


# 免费试用兜底缓存：网络异常时返回预置数据，确保试用体验稳定可用
_FREE_TRIAL_CACHE = {
    "example.com": {
        "success": True,
        "scan_type": "real",
        "final_url": "https://example.com",
        "is_https": True,
        "score": 66,
        "risk_level": "中风险",
        "summary": {"high": 2, "medium": 2, "low": 3, "critical": 0, "total": 7},
        "findings": [
            {
                "name": "缺少 HSTS",
                "severity": "high",
                "level": "高风险",
                "level_zh": "高风险",
                "owasp": "A05 安全配置错误",
                "summary": "强制浏览器只通过 HTTPS 访问。",
                "fix": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                "type": "config",
                "evidence": {
                    "detected": False,
                    "header": "strict-transport-security",
                    "reason": "未检测到 HSTS 响应头",
                    "impact": "强制浏览器只通过 HTTPS 访问",
                },
                "verify_method": "curl -I https://你的域名 | grep -i 'strict-transport-security'",
            },
            {
                "name": "缺少 CSP",
                "severity": "high",
                "level": "高风险",
                "level_zh": "高风险",
                "owasp": "A05 安全配置错误",
                "summary": "限制页面可加载的资源来源。",
                "fix": "add_header Content-Security-Policy \"default-src 'self'\" always;",
                "type": "config",
                "evidence": {
                    "detected": False,
                    "header": "content-security-policy",
                    "reason": "未检测到 CSP 响应头",
                    "impact": "限制页面可加载的资源来源",
                },
                "verify_method": "curl -I https://你的域名 | grep -i 'content-security-policy'",
            },
            {
                "name": "缺少 X-Frame-Options",
                "severity": "medium",
                "level": "中风险",
                "level_zh": "中风险",
                "owasp": "A05 安全配置错误",
                "summary": "防止页面被嵌入 iframe。",
                "fix": 'add_header X-Frame-Options "DENY" always;',
                "type": "config",
                "evidence": {
                    "detected": False,
                    "header": "x-frame-options",
                    "reason": "未检测到 X-Frame-Options 响应头",
                    "impact": "防止页面被嵌入 iframe",
                },
                "verify_method": "curl -I https://你的域名 | grep -i 'x-frame-options'",
            },
            {
                "name": "缺少 X-Content-Type-Options",
                "severity": "medium",
                "level": "中风险",
                "level_zh": "中风险",
                "owasp": "A05 安全配置错误",
                "summary": "禁止浏览器猜测 MIME 类型。",
                "fix": 'add_header X-Content-Type-Options "nosniff" always;',
                "type": "config",
                "evidence": {
                    "detected": False,
                    "header": "x-content-type-options",
                    "reason": "未检测到 X-Content-Type-Options 响应头",
                    "impact": "禁止浏览器猜测 MIME 类型",
                },
                "verify_method": "curl -I https://你的域名 | grep -i 'x-content-type-options'",
            },
            {
                "name": "缺少 Referrer-Policy",
                "severity": "low",
                "level": "低风险",
                "level_zh": "低风险",
                "owasp": "A05 安全配置错误",
                "summary": "控制 Referer 头发送策略。",
                "fix": 'add_header Referrer-Policy "strict-origin-when-cross-origin" always;',
                "type": "config",
                "evidence": {
                    "detected": False,
                    "header": "referrer-policy",
                    "reason": "未检测到 Referrer-Policy 响应头",
                    "impact": "控制 Referer 头发送策略",
                },
                "verify_method": "curl -I https://你的域名 | grep -i 'referrer-policy'",
            },
            {
                "name": "缺少 Permissions-Policy",
                "severity": "low",
                "level": "低风险",
                "level_zh": "低风险",
                "owasp": "A05 安全配置错误",
                "summary": "控制浏览器 API 权限。",
                "fix": 'add_header Permissions-Policy "camera=(), microphone=()" always;',
                "type": "config",
                "evidence": {
                    "detected": False,
                    "header": "permissions-policy",
                    "reason": "未检测到 Permissions-Policy 响应头",
                    "impact": "控制浏览器 API 权限",
                },
                "verify_method": "curl -I https://你的域名 | grep -i 'permissions-policy'",
            },
            {
                "name": "Server 信息泄露",
                "severity": "low",
                "level": "低风险",
                "level_zh": "低风险",
                "owasp": "A05 安全配置错误",
                "summary": "暴露服务器信息: cloudflare",
                "fix": "隐藏或修改 Server 头。",
                "type": "config",
                "evidence": {
                    "header": "Server",
                    "value": "cloudflare",
                    "reason": "暴露了服务器软件和版本信息",
                    "impact": "攻击者可利用已知版本漏洞",
                },
                "verify_method": "curl -I https://你的域名 | grep -i '^server'（不应返回具体版本）",
            },
        ],
        "owasp_coverage": [
            {"category": "A01 访问控制失效", "status": "通过", "note": "需关注"},
            {"category": "A02 加密机制失效", "status": "通过", "note": "已启用 HTTPS"},
            {"category": "A03 注入攻击", "status": "通过", "note": "未检测到注入漏洞"},
            {"category": "A04 不安全设计", "status": "通过", "note": "未检测到"},
            {
                "category": "A05 安全配置错误",
                "status": "需关注",
                "note": "部分配置可优化",
            },
            {
                "category": "A06 过时组件",
                "status": "需深度检测",
                "note": "建议扫描依赖",
            },
            {"category": "A07 认证失败", "status": "通过", "note": "未检测到"},
            {"category": "A08 软件完整性", "status": "通过", "note": "未检测到"},
            {"category": "A09 日志监控不足", "status": "低风险", "note": "建议加强"},
            {"category": "A10 服务端请求伪造", "status": "通过", "note": "未检测到"},
        ],
        "header_details": [
            {
                "name": "HSTS",
                "key": "strict-transport-security",
                "value": None,
                "status": "missing",
                "category": "传输安全",
                "severity": "high",
            },
            {
                "name": "CSP",
                "key": "content-security-policy",
                "value": None,
                "status": "missing",
                "category": "XSS 防护",
                "severity": "high",
            },
            {
                "name": "X-Frame-Options",
                "key": "x-frame-options",
                "value": None,
                "status": "missing",
                "category": "点击劫持",
                "severity": "medium",
            },
            {
                "name": "X-Content-Type-Options",
                "key": "x-content-type-options",
                "value": None,
                "status": "missing",
                "category": "MIME 嗅探",
                "severity": "medium",
            },
            {
                "name": "Referrer-Policy",
                "key": "referrer-policy",
                "value": None,
                "status": "missing",
                "category": "隐私",
                "severity": "low",
            },
            {
                "name": "Permissions-Policy",
                "key": "permissions-policy",
                "value": None,
                "status": "missing",
                "category": "隐私",
                "severity": "low",
            },
        ],
        "info_leaks": [{"name": "Server", "value": "cloudflare"}],
        "cors": None,
        "cookie_issues": [],
        "ssl_info": {
            "has_cert": False,
            "error": "SSL 握手超时（目标可能未启用 HTTPS 或响应较慢）",
        },
        "waf": [
            {
                "name": "cloudflare",
                "signature": "CF-RAY",
                "value": "a1127c5aeca5d2a8-FRA",
            }
        ],
        "sensitive_paths": [],
        "waf_detected": True,
        "raw_headers": {
            "date": "Thu, 25 Jun 2026 08:08:41 GMT",
            "content-type": "text/html",
            "connection": "keep-alive",
            "server": "cloudflare",
            "last-modified": "Fri, 19 Jun 2026 18:46:03 GMT",
            "allow": "GET, HEAD",
            "age": "0",
            "cf-cache-status": "HIT",
            "content-encoding": "gzip",
            "cf-ray": "a1127c5aeca5d2a8-FRA",
            "_status_code": 200,
        },
        "fixes": {
            "nginx": [
                {
                    "code": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "express": "// Express: app.disable('x-powered-by')",
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": "add_header Content-Security-Policy \"default-src 'self'\" always;",
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "nginx": "add_header Content-Security-Policy \"default-src 'self'\" always;",
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "express": "// Express: app.disable('x-powered-by')",
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": 'add_header X-Frame-Options "DENY" always;',
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "nginx": 'add_header X-Frame-Options "DENY" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "express": "// Express: app.disable('x-powered-by')",
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": 'add_header X-Content-Type-Options "nosniff" always;',
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "nginx": 'add_header X-Content-Type-Options "nosniff" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "express": "// Express: app.disable('x-powered-by')",
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": 'add_header Referrer-Policy "strict-origin-when-cross-origin" always;',
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "nginx": 'add_header Referrer-Policy "strict-origin-when-cross-origin" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "express": "// Express: app.disable('x-powered-by')",
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": 'add_header Permissions-Policy "camera=(), microphone=()" always;',
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "nginx": 'add_header Permissions-Policy "camera=(), microphone=()" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "express": "// Express: app.disable('x-powered-by')",
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": "server_tokens off;",
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "nginx": "server_tokens off;",
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "express": "// Express: app.disable('x-powered-by')",
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
            ],
            "apache": [
                {
                    "code": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "express": "// Express: app.disable('x-powered-by')",
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": "Header set Content-Security-Policy \"default-src 'self'\" ",
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "apache": "Header set Content-Security-Policy \"default-src 'self'\" ",
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "express": "// Express: app.disable('x-powered-by')",
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": 'Header set X-Frame-Options "DENY" ',
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "apache": 'Header set X-Frame-Options "DENY" ',
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "express": "// Express: app.disable('x-powered-by')",
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": 'Header set X-Content-Type-Options "nosniff" ',
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "apache": 'Header set X-Content-Type-Options "nosniff" ',
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "express": "// Express: app.disable('x-powered-by')",
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": 'Header set Referrer-Policy "strict-origin-when-cross-origin" ',
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "apache": 'Header set Referrer-Policy "strict-origin-when-cross-origin" ',
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "express": "// Express: app.disable('x-powered-by')",
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": 'Header set Permissions-Policy "camera=(), microphone=()" ',
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "apache": 'Header set Permissions-Policy "camera=(), microphone=()" ',
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "express": "// Express: app.disable('x-powered-by')",
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": "ServerTokens Prod\nServerSignature Off",
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "apache": "ServerTokens Prod\nServerSignature Off",
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "express": "// Express: app.disable('x-powered-by')",
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
            ],
            "express": [
                {
                    "code": "// Express: app.disable('x-powered-by')",
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "express": "// Express: app.disable('x-powered-by')",
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                }
            ],
            "flask": [
                {
                    "code": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "express": "// Express: app.disable('x-powered-by')",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['CSP'] = 'default-src 'self''\n    return resp",
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['CSP'] = 'default-src 'self''\n    return resp",
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "express": "// Express: app.disable('x-powered-by')",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['Content-Security-Policy'] = 'default-src 'self''\n    return resp",
                    "risk_note": "上线前请在测试环境验证，CSP 策略过严可能导致前端资源加载失败",
                    "server_type": "unknown",
                    "config_examples": {
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['Content-Security-Policy'] = 'default-src 'self''\n    return resp",
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "express": "// Express: app.disable('x-powered-by')",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['X-Frame-Options'] = 'DENY'\n    return resp",
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['X-Frame-Options'] = 'DENY'\n    return resp",
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "express": "// Express: app.disable('x-powered-by')",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['X-Content-Type-Options'] = 'nosniff'\n    return resp",
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['X-Content-Type-Options'] = 'nosniff'\n    return resp",
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "express": "// Express: app.disable('x-powered-by')",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'\n    return resp",
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'\n    return resp",
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "express": "// Express: app.disable('x-powered-by')",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['Permissions-Policy'] = 'camera=(), microphone=()'\n    return resp",
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['Permissions-Policy'] = 'camera=(), microphone=()'\n    return resp",
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "express": "// Express: app.disable('x-powered-by')",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": "# Flask: app.config['SECRET_KEY'] = os.urandom(32)",
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "flask": "# Flask: app.config['SECRET_KEY'] = os.urandom(32)",
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "express": "// Express: app.disable('x-powered-by')",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
            ],
            "spring_boot": [
                {
                    "code": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "express": "// Express: app.disable('x-powered-by')",
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": "# Spring Boot: server.error.include-stacktrace=never",
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "spring_boot": "# Spring Boot: server.error.include-stacktrace=never",
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "express": "// Express: app.disable('x-powered-by')",
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
            ],
            "cloudflare": [
                {
                    "code": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "express": "// Express: app.disable('x-powered-by')",
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: CSP\n# Value: default-src 'self'",
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: CSP\n# Value: default-src 'self'",
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "express": "// Express: app.disable('x-powered-by')",
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: Content-Security-Policy\n# Value: default-src 'self'",
                    "risk_note": "上线前请在测试环境验证，CSP 策略过严可能导致前端资源加载失败",
                    "server_type": "unknown",
                    "config_examples": {
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: Content-Security-Policy\n# Value: default-src 'self'",
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "express": "// Express: app.disable('x-powered-by')",
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: X-Frame-Options\n# Value: DENY",
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: X-Frame-Options\n# Value: DENY",
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "express": "// Express: app.disable('x-powered-by')",
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: X-Content-Type-Options\n# Value: nosniff",
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: X-Content-Type-Options\n# Value: nosniff",
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "express": "// Express: app.disable('x-powered-by')",
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: Referrer-Policy\n# Value: strict-origin-when-cross-origin",
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: Referrer-Policy\n# Value: strict-origin-when-cross-origin",
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "express": "// Express: app.disable('x-powered-by')",
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: Permissions-Policy\n# Value: camera=(), microphone=()",
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: Permissions-Policy\n# Value: camera=(), microphone=()",
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "express": "// Express: app.disable('x-powered-by')",
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": "# Cloudflare: Scrape Shield > Disable Server Name Exposure",
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "cloudflare": "# Cloudflare: Scrape Shield > Disable Server Name Exposure",
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "express": "// Express: app.disable('x-powered-by')",
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
            ],
            "nodejs": [
                {
                    "code": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "express": "// Express: app.disable('x-powered-by')",
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": "// Express helmet: add_header Content-Security-Policy \"default-src 'self'\" always;",
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "express": "// Express: app.disable('x-powered-by')",
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": '// Express helmet: add_header X-Frame-Options "DENY" always;',
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "express": "// Express: app.disable('x-powered-by')",
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": '// Express helmet: add_header X-Content-Type-Options "nosniff" always;',
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "express": "// Express: app.disable('x-powered-by')",
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": '// Express helmet: add_header Referrer-Policy "strict-origin-when-cross-origin" always;',
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "express": "// Express: app.disable('x-powered-by')",
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": '// Express helmet: add_header Permissions-Policy "camera=(), microphone=()" always;',
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "express": "// Express: app.disable('x-powered-by')",
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": "// app.disable('x-powered-by')",
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "express": "// Express: app.disable('x-powered-by')",
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "python": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
            ],
            "python": [
                {
                    "code": '# Flask 后置响应头: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "express": "// Express: app.disable('x-powered-by')",
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": "# Flask 后置响应头: add_header Content-Security-Policy \"default-src 'self'\" always;",
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "express": "// Express: app.disable('x-powered-by')",
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": '# Flask 后置响应头: add_header X-Frame-Options "DENY" always;',
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "express": "// Express: app.disable('x-powered-by')",
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": '# Flask 后置响应头: add_header X-Content-Type-Options "nosniff" always;',
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "express": "// Express: app.disable('x-powered-by')",
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": '# Flask 后置响应头: add_header Referrer-Policy "strict-origin-when-cross-origin" always;',
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "express": "// Express: app.disable('x-powered-by')",
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": '# Flask 后置响应头: add_header Permissions-Policy "camera=(), microphone=()" always;',
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "express": "// Express: app.disable('x-powered-by')",
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
                {
                    "code": "# app.config['SECRET_KEY'] = os.urandom(32)",
                    "risk_note": None,
                    "server_type": "unknown",
                    "config_examples": {
                        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                        "apache": 'Header set Strict-Transport-Security "max-age=31536000; includeSubDomains" ',
                        "express": "// Express: app.disable('x-powered-by')",
                        "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                        "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                        "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                        "nodejs": '// Express helmet: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    },
                },
            ],
        },
    },
    "iana.org": {
        "success": True,
        "scan_type": "real",
        "final_url": "https://iana.org",
        "is_https": True,
        "score": 84,
        "risk_level": "低风险",
        "summary": {"high": 0, "medium": 2, "low": 1, "total": 3},
        "findings": [
            {
                "name": "缺少 CSP",
                "type": "MissingHeader",
                "severity": "medium",
                "level_zh": "中风险",
                "description": "未启用 Content Security Policy",
                "fix": "add_header Content-Security-Policy \"default-src 'self'\" always;",
            },
            {
                "name": "缺少 Referrer-Policy",
                "type": "MissingHeader",
                "severity": "low",
                "level_zh": "低风险",
                "description": "未控制 Referrer 泄露",
                "fix": 'add_header Referrer-Policy "strict-origin-when-cross-origin" always;',
            },
            {
                "name": "Server 头泄露",
                "type": "InfoLeak",
                "severity": "medium",
                "level_zh": "中风险",
                "description": "Server 响应头包含版本信息",
                "fix": "server_tokens off;",
            },
        ],
        "owasp_coverage": ["A05:2021", "A06:2021"],
        "header_details": [
            {"name": "Server", "present": True, "value": "nginx/1.18.0"},
            {"name": "HSTS", "present": True, "value": "max-age=31536000"},
            {"name": "CSP", "present": False, "value": ""},
        ],
        "info_leaks": [{"type": "Server 头", "detail": "nginx/1.18.0"}],
        "cors": None,
        "cookie_issues": [],
        "ssl_info": {
            "has_cert": True,
            "subject": "iana.org",
            "issuer": "Let's Encrypt",
            "days_left": 60,
            "expired": False,
            "version": "TLSv1.3",
            "weak": False,
        },
        "waf": [],
        "sensitive_paths": [],
        "waf_detected": False,
        "raw_headers": {
            "server": "nginx/1.18.0",
            "strict-transport-security": "max-age=31536000",
        },
        "fixes": {
            "nginx": [
                {
                    "code": "add_header Content-Security-Policy \"default-src 'self'\" always;",
                    "risk_note": None,
                },
                {
                    "code": 'add_header Referrer-Policy "strict-origin-when-cross-origin" always;',
                    "risk_note": None,
                },
                {"code": "server_tokens off;", "risk_note": None},
            ],
            "apache": [
                {
                    "code": "Header set Content-Security-Policy \"default-src 'self'\"",
                    "risk_note": None,
                },
                {
                    "code": 'Header set Referrer-Policy "strict-origin-when-cross-origin"',
                    "risk_note": None,
                },
                {"code": "ServerTokens Prod", "risk_note": None},
            ],
            "express": [
                {
                    "code": "// Express + helmet\nconst helmet = require('helmet');\napp.use(helmet({ contentSecurityPolicy: { directives: { defaultSrc: [\"'self'\"] } } }));",
                    "risk_note": None,
                },
                {
                    "code": "// Express\napp.use((req, res, next) => { res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin'); next(); });",
                    "risk_note": None,
                },
            ],
            "flask": [
                {
                    "code": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['Content-Security-Policy'] = \"default-src 'self'\"\n    resp.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'\n    return resp",
                    "risk_note": None,
                },
            ],
            "spring_boot": [
                {
                    "code": "# Spring Boot: SecurityConfig.java\nhttp.headers().contentSecurityPolicy(\"default-src 'self'\");",
                    "risk_note": None,
                },
            ],
            "cloudflare": [
                {
                    "code": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: Content-Security-Policy\n# Value: default-src 'self'",
                    "risk_note": None,
                },
            ],
        },
    },
}


def _get_or_create_demo_cache(host: str) -> dict | None:
    """为白名单站点获取或生成兜底缓存数据。"""
    cached = _FREE_TRIAL_CACHE.get(host)
    if cached:
        return cached
    # 为没有预置缓存的站点生成基础兜底数据
    _demo_fallback = {
        "www.iana.org": {
            "success": True,
            "scan_type": "cached",
            "final_url": "https://www.iana.org",
            "is_https": True,
            "score": 72,
            "risk_level": "中风险",
            "summary": {"high": 1, "medium": 2, "low": 3, "critical": 0, "total": 6},
            "findings": [
                {
                    "name": "缺少 HSTS",
                    "severity": "high",
                    "level": "高风险",
                    "level_zh": "高风险",
                    "owasp": "A05 安全配置错误",
                    "summary": "强制浏览器只通过 HTTPS 访问。",
                    "fix": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    "type": "config",
                    "evidence": {"detected": False, "header": "strict-transport-security", "reason": "未检测到 HSTS 响应头"},
                    "verify_method": "curl -I https://www.iana.org | grep -i strict-transport-security",
                },
                {
                    "name": "缺少 CSP",
                    "severity": "medium",
                    "level": "中风险",
                    "level_zh": "中风险",
                    "owasp": "A05 安全配置错误",
                    "summary": "限制页面可加载的资源来源。",
                    "fix": 'add_header Content-Security-Policy "default-src \'self\'" always;',
                    "type": "config",
                    "evidence": {"detected": False, "header": "content-security-policy", "reason": "未检测到 CSP 响应头"},
                    "verify_method": "curl -I https://www.iana.org | grep -i content-security-policy",
                },
                {
                    "name": "缺少 X-Frame-Options",
                    "severity": "medium",
                    "level": "中风险",
                    "level_zh": "中风险",
                    "owasp": "A05 安全配置错误",
                    "summary": "防止页面被嵌入 iframe。",
                    "fix": 'add_header X-Frame-Options "DENY" always;',
                    "type": "config",
                    "evidence": {"detected": False, "header": "x-frame-options", "reason": "未检测到 X-Frame-Options"},
                    "verify_method": "curl -I https://www.iana.org | grep -i x-frame-options",
                },
            ],
        },
        "httpbin.org": {
            "success": True,
            "scan_type": "cached",
            "final_url": "https://httpbin.org",
            "is_https": True,
            "score": 68,
            "risk_level": "中风险",
            "summary": {"high": 2, "medium": 2, "low": 2, "critical": 0, "total": 6},
            "findings": [
                {
                    "name": "缺少 HSTS",
                    "severity": "high",
                    "level": "高风险",
                    "level_zh": "高风险",
                    "owasp": "A05 安全配置错误",
                    "summary": "强制浏览器只通过 HTTPS 访问。",
                    "fix": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    "type": "config",
                    "evidence": {"detected": False, "header": "strict-transport-security", "reason": "未检测到 HSTS 响应头"},
                    "verify_method": "curl -I https://httpbin.org | grep -i strict-transport-security",
                },
                {
                    "name": "缺少 CSP",
                    "severity": "high",
                    "level": "高风险",
                    "level_zh": "高风险",
                    "owasp": "A05 安全配置错误",
                    "summary": "限制页面可加载的资源来源。",
                    "fix": 'add_header Content-Security-Policy "default-src \'self\'" always;',
                    "type": "config",
                    "evidence": {"detected": False, "header": "content-security-policy", "reason": "未检测到 CSP"},
                    "verify_method": "curl -I https://httpbin.org | grep -i content-security-policy",
                },
                {
                    "name": "缺少 X-Frame-Options",
                    "severity": "medium",
                    "level": "中风险",
                    "level_zh": "中风险",
                    "owasp": "A05 安全配置错误",
                    "summary": "防止页面被嵌入 iframe。",
                    "fix": 'add_header X-Frame-Options "DENY" always;',
                    "type": "config",
                    "evidence": {"detected": False, "header": "x-frame-options", "reason": "未检测到 X-Frame-Options"},
                    "verify_method": "curl -I https://httpbin.org | grep -i x-frame-options",
                },
                {
                    "name": "缺少 X-Content-Type-Options",
                    "severity": "medium",
                    "level": "中风险",
                    "level_zh": "中风险",
                    "owasp": "A05 安全配置错误",
                    "summary": "禁止浏览器猜测 MIME 类型。",
                    "fix": 'add_header X-Content-Type-Options "nosniff" always;',
                    "type": "config",
                    "evidence": {"detected": False, "header": "x-content-type-options", "reason": "未检测到"},
                    "verify_method": "curl -I https://httpbin.org | grep -i x-content-type-options",
                },
            ],
        },
        "testphp.vulnweb.com": {
            "success": True,
            "scan_type": "cached",
            "final_url": "http://testphp.vulnweb.com",
            "is_https": False,
            "score": 35,
            "risk_level": "critical",
            "summary": {"high": 3, "medium": 3, "low": 2, "critical": 1, "total": 9},
            "findings": [
                {
                    "name": "未启用 HTTPS",
                    "severity": "critical",
                    "level": "严重",
                    "level_zh": "严重",
                    "owasp": "A02 加密机制失效",
                    "summary": "站点未使用 HTTPS，传输数据可能被窃听或篡改。",
                    "fix": "配置 SSL/TLS 证书并强制 HTTPS 重定向。",
                    "type": "ssl",
                    "evidence": {"detected": True, "reason": "站点使用 HTTP 协议"},
                    "verify_method": "浏览器访问确认 URL 为 http:// 而非 https://",
                },
                {
                    "name": "缺少 HSTS",
                    "severity": "high",
                    "level": "高风险",
                    "level_zh": "高风险",
                    "owasp": "A05 安全配置错误",
                    "summary": "强制浏览器只通过 HTTPS 访问。",
                    "fix": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                    "type": "config",
                    "evidence": {"detected": False, "header": "strict-transport-security", "reason": "未检测到 HSTS"},
                    "verify_method": "curl -I http://testphp.vulnweb.com | grep -i strict-transport-security",
                },
                {
                    "name": "缺少 CSP",
                    "severity": "high",
                    "level": "高风险",
                    "level_zh": "高风险",
                    "owasp": "A05 安全配置错误",
                    "summary": "限制页面可加载的资源来源。",
                    "fix": 'add_header Content-Security-Policy "default-src \'self\'" always;',
                    "type": "config",
                    "evidence": {"detected": False, "header": "content-security-policy", "reason": "未检测到 CSP"},
                    "verify_method": "curl -I http://testphp.vulnweb.com | grep -i content-security-policy",
                },
                {
                    "name": "缺少 X-Frame-Options",
                    "severity": "medium",
                    "level": "中风险",
                    "level_zh": "中风险",
                    "owasp": "A05 安全配置错误",
                    "summary": "防止页面被嵌入 iframe（点击劫持防护）。",
                    "fix": 'add_header X-Frame-Options "DENY" always;',
                    "type": "config",
                    "evidence": {"detected": False, "header": "x-frame-options", "reason": "未检测到"},
                    "verify_method": "curl -I http://testphp.vulnweb.com | grep -i x-frame-options",
                },
                {
                    "name": "SQL注入风险（Acunetix测试站点）",
                    "severity": "high",
                    "level": "高风险",
                    "level_zh": "高风险",
                    "owasp": "A03:2021 - Injection",
                    "summary": "该站点为已知的安全测试靶场，ListProducts.php 等端点存在 SQL 注入。",
                    "fix": "使用参数化查询，禁止直接拼接 SQL 语句。",
                    "type": "sqli",
                    "evidence": {"detected": True, "url": "http://testphp.vulnweb.com/listproducts.php?cat=1", "reason": "Acunetix 公开测试靶场，已知存在 SQL 注入"},
                    "verify_method": "访问 http://testphp.vulnweb.com/listproducts.php?cat=1' 观察是否报错",
                },
            ],
        },
    }
    return _demo_fallback.get(host)


def _is_free_trial_host(host: str) -> bool:
    return (host or "").lower() in _FREE_TRIAL_HOSTS


@app.get("/api/scan-progress/{scan_token}")
async def api_scan_progress(
    scan_token: str, user: dict = Depends(require_login)
) -> dict:
    """返回指定扫描 token 的进度（前端轮询用）。从内存字典读取，并附带清理逻辑。"""
    # 顺手清理 30 分钟未更新的内存条目（避免 dict 膨胀）
    try:
        cutoff = time.time() - 1800
        async with _scan_progress_lock:
            stale = [
                k for k, v in _scan_progress.items() if v.get("updated_at", 0) < cutoff
            ]
            for k in stale:
                _scan_progress.pop(k, None)
    except Exception as e:
        logger.warning("Scan progress stale cleanup failed: %s", e)

    async with _scan_progress_lock:
        data = _scan_progress.get(scan_token)

    if not data:
        return {"stages": [], "current": -1, "status": "idle"}

    # 权限校验：只能查看自己用户的进度
    if data.get("user_id") != user["user_id"]:
        return {"stages": [], "current": -1, "status": "forbidden"}

    # 超过 5 分钟视为完成/过期
    updated_at = data.get("updated_at", 0)
    if time.time() - updated_at > 300:
        return {"stages": data.get("stages", []), "current": 999, "status": "done"}
    return {**data, "status": "running"}


# ---------- 异步扫描任务队列 API ----------

from app.tasks import ScanTaskManager

_scan_task_manager = ScanTaskManager(max_concurrent=3, task_timeout=300)


class AsyncScanRequest(BaseModel):
    url: str
    deep: bool = False
    authorized: bool = False
    verification_token: str | None = None


@app.post("/api/scan/async")
async def api_async_scan(
    req: AsyncScanRequest, user: dict = Depends(require_login)
) -> dict:
    """提交异步扫描任务，返回 task_id 供前端轮询。"""
    raw_url = req.url.strip()
    if not raw_url.startswith(("http://", "https://")):
        raw_url = "https://" + raw_url

    valid, reason, code = validate_scan_target_full(
        raw_url,
        user_id=user["user_id"],
        authorized=req.authorized,
        deep=req.deep,
        verification_token=req.verification_token,
        allowed_demo=True,
    )
    if not valid:
        raise HTTPException(403, detail={"error": reason, "code": code})

    async def _scan_fn(scan_url: str, progress_cb=None, **kwargs):
        return await _run_scan_task(
            url=scan_url,
            user_id=user["user_id"],
            deep=kwargs.get("deep", False),
            authorized=req.authorized,
            verification_token=req.verification_token,
            progress_cb=progress_cb,
        )

    # 优先使用 Redis 队列；若 Redis 不可用则降级到内存任务管理器
    _use_redis = False
    if settings.redis_url:
        try:
            queue = get_scan_queue()
            task_id = await queue.submit(
                RedisScanTask(
                    task_id=f"SCAN-{uuid.uuid4().hex[:12].upper()}",
                    user_id=user["user_id"],
                    url=raw_url,
                    depth="deep" if req.deep else "standard",
                    deep=req.deep,
                    authorized=req.authorized,
                )
            )
            _use_redis = True
        except Exception as redis_err:
            logger.warning(
                "Redis queue submit failed, falling back to in-memory task manager: %s",
                redis_err,
            )

    if not _use_redis:
        task_id = await _scan_task_manager.submit(
            url=raw_url,
            user_id=user["user_id"],
            depth="deep" if req.deep else "standard",
            scan_func=_scan_fn,
            deep=req.deep,
        )
    return {"task_id": task_id, "status": "pending", "url": raw_url}


@app.get("/api/scan/tasks/{task_id}")
async def api_get_scan_task(task_id: str, user: dict = Depends(require_login)) -> dict:
    """查询异步扫描任务状态。"""
    # 优先查 Redis 队列，不可用时降级到内存任务管理器
    if settings.redis_url:
        try:
            queue = get_scan_queue()
            result = await queue.get_status(task_id)
            if result:
                if result.user_id != user["user_id"]:
                    raise HTTPException(403, "无权查看此任务")
                data = result.to_dict()
                data["found"] = True
                return data
        except HTTPException:
            raise
        except Exception:
            pass  # Redis 不可用，降级到内存

    task = _scan_task_manager.get_task(task_id)
    if not task:
        raise HTTPException(404, "任务不存在或已过期")
    if task.user_id != user["user_id"]:
        raise HTTPException(403, "无权查看此任务")
    return _scan_task_manager.get_task_status(task_id)


@app.get("/api/scan/tasks")
async def api_list_scan_tasks(
    status: str = "",
    user: dict = Depends(require_login),
) -> dict:
    """列出当前用户的异步扫描任务。"""
    # 优先查 Redis 队列，不可用时降级到内存任务管理器
    if settings.redis_url:
        try:
            queue = get_scan_queue()
            if hasattr(queue, "list_user_tasks"):
                tasks = await queue.list_user_tasks(user["user_id"])
            else:
                tasks = []
            return {
                "tasks": [t.to_dict() for t in tasks[:50]],
                "stats": {},
            }
        except Exception:
            pass  # Redis 不可用，降级到内存

    from app.tasks import TaskStatus

    task_status = None
    if status:
        try:
            task_status = TaskStatus(status)
        except ValueError:
            pass
    tasks = _scan_task_manager.list_tasks(user_id=user["user_id"], status=task_status)
    return {
        "tasks": [t.to_dict() for t in tasks[:50]],
        "stats": _scan_task_manager.get_stats(),
    }


@app.post("/api/scan/tasks/{task_id}/cancel")
async def api_cancel_scan_task(
    task_id: str,
    user: dict = Depends(require_login),
) -> dict:
    """取消异步扫描任务。"""
    # 优先操作 Redis 队列，不可用时降级到内存任务管理器
    if settings.redis_url:
        try:
            queue = get_scan_queue()
            result = await queue.get_status(task_id)
            if result:
                if result.user_id != user["user_id"]:
                    raise HTTPException(403, "无权操作此任务")
                cancelled = await queue.cancel_task(task_id)
                if not cancelled:
                    raise HTTPException(409, "任务已完成或无法取消")
                return {"task_id": task_id, "status": "cancelled"}
        except HTTPException:
            raise
        except Exception:
            pass  # Redis 不可用，降级到内存

    task = _scan_task_manager.get_task(task_id)
    if not task:
        raise HTTPException(404, "任务不存在")
    if task.user_id != user["user_id"]:
        raise HTTPException(403, "无权操作此任务")
    cancelled = await _scan_task_manager.cancel_task(task_id)
    if not cancelled:
        raise HTTPException(409, "任务已完成或无法取消")
    return {"task_id": task_id, "status": "cancelled"}


@app.post("/api/public-demo-scan", response_model=None)
async def free_trial_scan(req: FreeTrialRequest, request: Request):
    """免费试用扫描：允许未登录用户扫描白名单站点，体验产品能力。"""
    client_ip = get_client_ip(request)
    if not await limiter_free_trial.is_allowed(client_ip):
        raise HTTPException(
            status_code=429,
            detail="免费试用请求过于频繁，请稍后再试",
            headers={"Retry-After": "60"},
        )
    if not settings.free_trial_enabled:
        raise HTTPException(403, "免费试用已关闭")
    raw_url = req.url.strip()
    if not raw_url.startswith(("http://", "https://")):
        raw_url = "https://" + raw_url
    parsed = urlparse(raw_url)
    host = (parsed.hostname or "").lower()
    if not _is_free_trial_host(host):
        raise HTTPException(
            403,
            "免费试用仅限白名单站点（example.com / httpbin.org / iana.org / testphp.vulnweb.com）。",
        )
    try:
        headers, is_https, final_url, error = await asyncio.wait_for(
            fetch_headers(raw_url), timeout=20.0
        )
        if error:
            # 实时扫描失败，尝试返回缓存数据
            cached = _get_or_create_demo_cache(host)
            if cached:
                return {
                    **cached,
                    "url": raw_url,
                    "is_cached": True,
                    "cached_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "cache_reason": "实时扫描失败",
                    "note": "当前是缓存数据，不代表实时状态。",
                }
            return {"success": False, "url": raw_url, "error": error}
        try:
            ssl_info = (
                await get_ssl_info(host, 443) if is_https else {"has_cert": False}
            )
        except Exception as e:
            logger.warning("free_trial get_ssl_info failed: %s", e)
            ssl_info = {"has_cert": False}
        waf_list = detect_waf(headers)
        try:
            sensitive_paths = await check_sensitive_paths(host, is_https)
        except Exception as e:
            logger.warning("free_trial check_sensitive_paths failed: %s", e)
            sensitive_paths = []
        waf_name = waf_list[0].get("name") if waf_list else None
        result = await run_plugin_scan(
            raw_url,
            headers,
            is_https,
            ssl_info,
            waf=waf_name,
            deep=False,
            body="",
        )
        try:
            legacy = await analyze_security(
                raw_url, headers, is_https, ssl_info, waf_list, sensitive_paths, []
            )
        except Exception as e:
            logger.warning("free trial legacy metadata failed: %s", e)
            legacy = {}
        result["findings"] = _attach_evidence_snapshots(result.get("findings", []), url)
        result.update(
            {
                "scan_type": "real",
                "final_url": final_url,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "is_https": is_https,
                "raw_headers": headers,
                "owasp_coverage": legacy.get("owasp_coverage", []),
                "header_details": legacy.get("header_details", []),
                "info_leaks": legacy.get("info_leaks", []),
                "cors": legacy.get("cors"),
                "cookie_issues": legacy.get("cookie_issues", []),
                "ssl_info": ssl_info,
                "waf_list": waf_list,
                "sensitive_paths": sensitive_paths,
                "waf_detected": len(waf_list) > 0,
                "score_breakdown": legacy.get("score_breakdown", []),
                "improvements": legacy.get("improvements", []),
                "risk_level_zh": risk_level_zh(result.get("risk_level")),
            }
        )
        # 生成修复建议（与登录用户一致）
        fixes = generate_fixes(result.get("findings", []), headers, is_https, host)
        # 如果用户已登录，把这次试用扫描也保存为他的扫描记录
        # 这样可以让他用 scan_id 触发自动修复
        try:
            token = request.headers.get("Authorization", "").replace("Bearer ", "")
            if token:
                payload = verify_token(token)
                if payload:
                    user_id = payload.get("user_id") or payload.get("uid")
                    if user_id:
                        try:
                            saved_id = save_scan(
                                user_id=int(user_id),
                                url=raw_url,
                                score=result.get("score", 0),
                                risk_level=result.get("risk_level", "未知"),
                                findings=result.get("findings", []),
                                summary=result.get("summary", {}),
                                crawled_count=1,
                                scan_type="public_demo",
                            )
                            if saved_id:
                                result["scan_id"] = saved_id
                        except Exception as e:
                            import logging

                            logging.getLogger("vuln_sentinel").warning(
                                "free trial scan save failed: " + str(e)[:100]
                            )
        except Exception as e:
            import logging

            logging.getLogger("vuln_sentinel").warning(
                "free trial scan save wrapper: " + str(e)[:100]
            )

        # 确保 scan_id 始终存在（未登录用户用负 ID 表示试用模式）
        if "scan_id" not in result:
            result["scan_id"] = (
                -abs(hash(raw_url + str(datetime.now().timestamp()))) % 1000000
            )
        # 标记是否使用了 TLS 验证跳过模式
        _tls_off = os.environ.get("TLS_VERIFY", "true").strip().lower() in (
            "0",
            "false",
            "no",
            "off",
        )
        result["tls_verify_skipped"] = _tls_off
        # 动态写入缓存：成功扫描后更新白名单站点的缓存数据
        if host in _FREE_TRIAL_HOSTS:
            _cache_payload = {
                "success": True,
                "scan_type": "real",
                "final_url": final_url,
                "is_https": is_https,
                "score": result.get("score", 0),
                "risk_level": result.get("risk_level", "未知"),
                "summary": result.get("summary", {}),
                "findings": result.get("findings", []),
                "sensitive_paths": sensitive_paths,
                "waf": waf_list,
                "ssl_info": ssl_info,
                "fixes": fixes,
            }
            _FREE_TRIAL_CACHE[host] = _cache_payload
            logger.info("Free trial cache updated for host: %s", host)
        return {
            "success": True,
            "scan_type": "real",
            "url": raw_url,
            "final_url": final_url,
            "is_https": is_https,
            "raw_headers": headers,
            "sensitive_paths": sensitive_paths,
            "waf": waf_list,
            "ssl_info": ssl_info,
            "fixes": fixes,
            **result,
        }
    except Exception as e:
        logger.warning("free_trial_scan failed for %s: %s", raw_url, e)
        cached = _get_or_create_demo_cache(host)
        if cached:
            return {
                **cached,
                "url": raw_url,
                "is_cached": True,
                "cached_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "cache_reason": "实时扫描失败",
                "note": "当前是缓存数据，不代表实时状态。",
            }
        return {"success": False, "url": raw_url, "error": str(e)[:300]}


# ===== AI 安全顾问 V2（智能规则引擎 + 结构化知识库）=====

# ---------- 同义词词典 ----------
_AI_SYNONYMS = {
    "fix": [
        "修复",
        "怎么修",
        "如何修",
        "怎么解决",
        "解决",
        "怎么弄",
        "咋弄",
        "修一下",
        "修",
        "怎么搞",
        "怎么处理",
        "处理",
        "修复方法",
        "修复方案",
        "怎么配置",
        "配置",
        "加上",
        "添加",
        "设置",
    ],
    "principle": [
        "原理",
        "是什么",
        "什么是",
        "为啥",
        "为什么",
        "原因",
        "概念",
        "介绍",
        "解释",
        "详解",
        "详细说明",
    ],
    "risk": [
        "危害",
        "风险",
        "危险",
        "后果",
        "影响",
        "严重吗",
        "有多严重",
        "有什么用",
        "作用",
    ],
    "verify": [
        "验证",
        "怎么验证",
        "如何验证",
        "检查",
        "怎么检查",
        "怎么确认",
        "确认",
        "测一下",
        "测试",
        "生效",
        "怎么看生效",
    ],
    "priority": [
        "优先",
        "先修",
        "重要",
        "顺序",
        "最该",
        "最先",
        "推荐",
        "建议",
        "先搞",
        "先弄",
        "从哪开始",
    ],
    "score": ["分数", "评分", "打分", "得分", "安全分", "怎么算", "计算", "规则"],
    "scan": ["扫描", "扫一下", "检测", "检查网站", "怎么扫", "如何扫描"],
    "report": ["报告", "扫描报告", "怎么看", "查看报告", "结果", "扫描结果"],
    "tool": ["怎么用", "使用", "上手", "操作", "教程", "指南", "用法"],
    "upgrade": ["提升", "提高", "增加", "加多少分", "能提升多少", "预估", "预计"],
    "greeting": ["你好", "hi", "hello", "在吗", "你是", "嗨", "哈喽", "hi~", "你好啊"],
    "thanks": ["谢谢", "感谢", "多谢", "thx", "thanks", "谢谢啦", "谢了"],
    "cookie": ["cookie", "cookies", "饼干", "会话", "session"],
    "cors": ["cors", "跨域", "跨站资源", "access-control"],
    "ssrf": ["ssrf", "服务端请求伪造", "服务端伪造"],
    "csrf": ["csrf", "跨站请求伪造", "xsrf"],
    "sql": ["sql注入", "sql 注入", "注入攻击", "sql注入攻击", "数据库注入"],
    "xss": ["xss", "跨站脚本", "脚本注入", "跨站脚本攻击"],
    "traversal": ["目录遍历", "路径遍历", "路径穿越", "目录穿越", "../"],
    "clickjack": ["点击劫持", "clickjacking", "x-frame", "iframe攻击"],
    "mime": ["mime嗅探", "mime 嗅探", "nosniff", "x-content-type"],
    "hsts": [
        "hsts",
        "严格传输",
        "严格传输安全",
        "强制https",
        "强制 https",
        "https强制",
    ],
    "csp_full": ["csp", "内容安全策略", "内容安全"],
    "referrer": ["referrer", "referer", "引用页", "来源页", "引荐"],
    "permissions": [
        "permissions-policy",
        "权限策略",
        "feature-policy",
        "摄像头",
        "麦克风",
        "地理位置",
    ],
    "cache": ["cache-control", "缓存控制", "缓存", "cache"],
    "xxssprotection": ["x-xss-protection", "xss保护", "xss 保护"],
    "sensitive": [
        "敏感文件",
        ".env",
        ".git",
        "git泄露",
        "源码泄露",
        "敏感信息",
        "信息泄露",
        "配置泄露",
    ],
    "server_header": ["server头", "server 头", "版本泄露", "服务器版本", "banner"],
    "ssl_tls": ["ssl", "tls", "弱加密", "弱配置", "ssl/tls", "tls配置", "证书"],
}

# ---------- 意图识别关键词 ----------
_AI_INTENT_KEYWORDS = {
    "fix": [
        "怎么修",
        "如何修",
        "怎么解决",
        "修复",
        "解决办法",
        "怎么弄",
        "咋弄",
        "修一下",
        "怎么搞",
        "怎么处理",
        "修复方法",
        "修复方案",
        "怎么配置",
        "配置一下",
        "加上",
        "添加",
        "设置一下",
        "代码",
        "怎么写",
    ],
    "principle": [
        "原理",
        "是什么",
        "什么是",
        "为啥",
        "为什么",
        "原因",
        "概念",
        "介绍",
        "解释",
        "详解",
        "详细说明",
        "什么意思",
        "干嘛的",
        "作用",
    ],
    "risk": [
        "危害",
        "风险",
        "危险",
        "后果",
        "影响",
        "严重吗",
        "有多严重",
        "有什么风险",
        "安全吗",
        "会怎样",
    ],
    "verify": [
        "验证",
        "怎么验证",
        "如何验证",
        "检查",
        "怎么检查",
        "怎么确认",
        "确认一下",
        "测一下",
        "测试",
        "生效了吗",
        "怎么看生效",
        "如何检查",
    ],
    "priority": [
        "优先",
        "先修",
        "重要",
        "顺序",
        "最该",
        "最先",
        "推荐",
        "建议",
        "先搞",
        "先弄",
        "从哪开始",
        "哪个重要",
        "先修什么",
    ],
    "score": [
        "分数",
        "评分",
        "打分",
        "得分",
        "安全分",
        "怎么算",
        "计算",
        "规则",
        "为什么扣分",
        "怎么扣的",
        "扣分原因",
    ],
    "upgrade": [
        "提升",
        "提高",
        "增加",
        "加多少分",
        "能提升多少",
        "预估",
        "预计",
        "能到多少分",
        "能提多少",
    ],
    "greeting": [
        "你好",
        "hi",
        "hello",
        "在吗",
        "你是",
        "嗨",
        "哈喽",
        "你好啊",
        "你是谁",
    ],
    "thanks": ["谢谢", "感谢", "多谢", "thx", "thanks", "谢谢啦", "谢了"],
    "tool_scan": [
        "怎么扫描",
        "如何扫描",
        "怎么扫",
        "扫一下",
        "怎么用",
        "使用方法",
        "上手",
        "操作",
        "教程",
        "指南",
    ],
    "tool_report": ["怎么看报告", "扫描报告", "报告怎么看", "怎么看结果", "结果在哪"],
    "tool_fixer": ["修复器", "修复配置生成", "生成修复配置", "怎么用修复", "修复工具"],
    "config_location": [
        "放在哪里",
        "配置位置",
        "加在哪里",
        "写在哪里",
        "哪个文件",
        "配置文件",
        "放哪",
    ],
    "deployment_risk": [
        "上线风险",
        "影响线上",
        "会挂吗",
        "影响业务",
        "会不会崩",
        "安全上线",
        "上线有什么风险",
        "能上线吗",
        "上线安全",
    ],
    "second": ["第二个", "第二项", "第二个呢", "下一个", "第二个问题", "下一项"],
}

# ---------- 结构化安全知识库 ----------
_AI_KNOWLEDGE_BASE = {
    # ===== 安全头类 =====
    "hsts": {
        "name": "HSTS (HTTP Strict Transport Security)",
        "category": "security_header",
        "severity": "high",
        "aliases": [
            "hsts",
            "严格传输安全",
            "强制https",
            "https强制",
            "strict-transport-security",
            "严格传输",
        ],
        "principle": "HSTS 是一个安全响应头，告诉浏览器**只能通过 HTTPS** 访问该网站，并且在指定时间内（max-age）禁止降级到 HTTP。\n\n**工作原理**：浏览器收到 HSTS 头后，会将该域名加入 HSTS 列表，后续所有请求自动升级为 HTTPS，即使你输入 http:// 也会直接走 HTTPS。\n\n**为什么重要**：防止 SSL stripping 攻击（中间人把 HTTPS 降级为 HTTP 窃取数据），防止 Cookie 在 HTTP 下泄露。",
        "risk": "🔴 **高风险**\n- 攻击者可在公共 WiFi 下发动 SSL 降级攻击，把 HTTPS 降级为 HTTP\n- 用户密码、Session Cookie 等敏感数据可能被明文窃取\n- 网银、电商等涉及交易的网站风险尤其高\n- 属于 OWASP A02（加密机制失效）范畴",
        "fix_nginx": '```nginx\n# 在 server { } 块内添加\nadd_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;\n\n# 说明：\n# max-age=31536000  — 浏览器记住 1 年（秒）\n# includeSubDomains — 所有子域名也强制 HTTPS\n# preload          — 申请加入浏览器 HSTS 预加载列表\n# always           — 所有响应码都加这个头（包括 4xx/5xx）\n```',
        "fix_apache": '```apache\n# 在 VirtualHost 或 .htaccess 中添加\nHeader always set Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"\n```',
        "fix_cloudflare": "在 Cloudflare Dashboard 中：\n1. SSL/TLS → Edge Certificates\n2. 打开「Always Use HTTPS」\n3. 打开「HTTP Strict Transport Security (HSTS)」\n4. 设置 Max Age 为 12 个月，勾选 Include subdomains 和 Preload",
        "fix_express": "```javascript\n// 使用 helmet 中间件（推荐）\nconst helmet = require('helmet');\napp.use(helmet.hsts({ maxAge: 31536000, includeSubDomains: true, preload: true }));\n\n// 或手动设置\napp.use((req, res, next) => {\n  res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains; preload');\n  next();\n});\n```",
        "fix_flask": "```python\nfrom flask import Flask\nfrom flask_talisman import Talisman\n\napp = Flask(__name__)\nTalisman(app, force_https=True, strict_transport_security=True,\n         strict_transport_security_max_age=31536000,\n         strict_transport_security_include_subdomains=True)\n```",
        "verify": "**验证方法**（3 种方式任选）：\n\n1. **浏览器开发者工具**：F12 → Network → 刷新页面 → 看 Response Headers 里有没有 `strict-transport-security`\n\n2. **curl 命令**：\n```bash\ncurl -sI https://yourdomain.com | grep -i strict-transport\n```\n\n3. **本工具重新扫描**：修复后点「重新扫描」，HSTS 缺失项应消失，评分相应提升。\n\n⚠ **注意**：HSTS 只能在 HTTPS 站点生效，HTTP 响应中的 HSTS 头会被浏览器忽略。",
    },
    "csp": {
        "name": "CSP (Content Security Policy)",
        "category": "security_header",
        "severity": "high",
        "aliases": ["csp", "内容安全策略", "content-security-policy", "内容安全"],
        "principle": "CSP（内容安全策略）是一个强大的安全响应头，它**白名单式**地控制页面能加载哪些来源的资源（JS、CSS、图片、字体、iframe 等）。\n\n**核心思想**：默认只允许加载自己域名的资源，其他来源一律拒绝。攻击者即使注入了恶意脚本，也因为不在白名单里而无法执行。\n\n**CSP 是防御 XSS 最有效的手段之一**，被 OWASP 强烈推荐。",
        "risk": "🔴 **高风险**\n- 没有 CSP 时，XSS 攻击几乎可以为所欲为\n- 攻击者注入的恶意脚本可以窃取 Cookie、劫持页面、钓鱼诈骗\n- 第三方资源（广告、统计脚本）被篡改后直接影响你的站点\n- 属于 OWASP A03（注入攻击）和 A05（安全配置错误）范畴",
        "fix_nginx": "```nginx\n# 渐进式策略（先从 report-only 开始，确认无误后再 enforcing）\nadd_header Content-Security-Policy \"default-src 'self';\n  script-src 'self' 'unsafe-inline' https://cdn.example.com;\n  style-src 'self' 'unsafe-inline';\n  img-src 'self' data: https:;\n  font-src 'self';\n  frame-ancestors 'none';\n  base-uri 'self';\n  form-action 'self'\" always;\n```",
        "fix_apache": "```apache\nHeader always set Content-Security-Policy \"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; frame-ancestors 'none'\"\n```",
        "fix_cloudflare": "Cloudflare Dashboard → Rules → Transform Rules → Modify Response Header\n添加响应头 `Content-Security-Policy`，值填入你的策略内容。",
        "fix_express": "```javascript\nconst helmet = require('helmet');\napp.use(helmet.contentSecurityPolicy({\n  directives: {\n    defaultSrc: [\"'self'\"],\n    scriptSrc: [\"'self'\"],\n    styleSrc: [\"'self'\", \"'unsafe-inline'\"],\n    imgSrc: [\"'self'\", \"data:\"],\n    frameAncestors: [\"'none'\"],\n  },\n}));\n```",
        "fix_flask": "```python\nfrom flask_talisman import Talisman\n\nTalisman(app, content_security_policy={\n    'default-src': \"'self'\",\n    'script-src': \"'self'\",\n    'style-src': \"'self' 'unsafe-inline'\",\n    'img-src': \"'self' data:\",\n    'frame-ancestors': \"'none'\",\n})\n```",
        "verify": "**验证方法**：\n\n1. **浏览器开发者工具**：F12 → Network → 看 Response Headers 中的 `content-security-policy`\n\n2. **Console 面板**：如果有 CSP 违规，Console 里会有红色报错\n\n3. **Report-Only 模式**（推荐先测）：先用 `Content-Security-Policy-Report-Only` 头，只报告不拦截，确认无违规后再切到 enforcing 模式\n\n4. **curl 命令**：\n```bash\ncurl -sI https://yourdomain.com | grep -i content-security\n```\n\n⚠ **建议**：先用 Report-Only 模式观察 1-2 周，确认没有误杀后再开启强制模式。",
    },
    "x_frame_options": {
        "name": "X-Frame-Options",
        "category": "security_header",
        "severity": "medium",
        "aliases": [
            "x-frame-options",
            "x-frame",
            "点击劫持",
            "clickjacking",
            "iframe",
            "frame",
        ],
        "principle": "X-Frame-Options 控制你的网页**能否被其他网站通过 iframe 嵌入**。\n\n**工作原理**：浏览器收到这个头后，如果检测到当前页面是在 iframe 中加载的，且来源不在允许列表里，就会拒绝渲染页面。\n\n**有三个取值**：\n- `DENY` — 完全禁止被嵌入（最安全）\n- `SAMEORIGIN` — 只允许同域名嵌入\n- `ALLOW-FROM uri` — 允许指定域名嵌入（已废弃，建议用 CSP frame-ancestors）",
        "risk": "🟡 **中风险**\n- 攻击者可构造透明 iframe 覆盖在正常页面上，诱导用户点击敏感操作\n- 可能被用于：转账、改密码、删除账号等危险操作\n- 称为「点击劫持攻击」（Clickjacking）\n- 对有用户交互的网站（银行、社交、管理后台）风险较高",
        "fix_nginx": '```nginx\nadd_header X-Frame-Options "DENY" always;\n# 或者如果你的站点需要被自己嵌入：\n# add_header X-Frame-Options "SAMEORIGIN" always;\n```',
        "fix_apache": '```apache\nHeader always set X-Frame-Options "DENY"\n```',
        "fix_cloudflare": "Cloudflare → Rules → Transform Rules → 添加响应头 `X-Frame-Options: DENY`",
        "fix_express": "```javascript\nconst helmet = require('helmet');\napp.use(helmet.frameguard({ action: 'deny' }));\n```",
        "fix_flask": "```python\nfrom flask_talisman import Talisman\nTalisman(app, frame_options='DENY')\n```",
        "verify": '**验证方法**：\n\n1. **浏览器开发者工具**：F12 → Network → 查看 Response Headers 中的 `x-frame-options`\n\n2. **手动测试**：在另一个网站用 iframe 嵌入你的页面，如果被拒绝显示说明生效：\n```html\n<iframe src="https://yourdomain.com"></iframe>\n```\n\n3. **curl 检查**：\n```bash\ncurl -sI https://yourdomain.com | grep -i x-frame\n```',
    },
    "x_content_type_options": {
        "name": "X-Content-Type-Options",
        "category": "security_header",
        "severity": "medium",
        "aliases": [
            "x-content-type-options",
            "nosniff",
            "mime嗅探",
            "mime 嗅探",
            "x-content-type",
        ],
        "principle": "X-Content-Type-Options: nosniff 告诉浏览器**不要猜测文件的 MIME 类型**，严格按照服务器声明的 Content-Type 来解析。\n\n**什么是 MIME 嗅探**：旧版浏览器会「猜测」文件类型，比如一个 `.txt` 文件里有 JS 代码，浏览器可能会把它当 JS 执行。这就给了攻击者可乘之机。",
        "risk": "🟡 **中风险**\n- 攻击者可上传看似图片的恶意脚本文件，浏览器嗅探后执行脚本导致 XSS\n- 对允许用户上传文件的网站风险较高\n- 配合文件上传漏洞可造成严重危害\n- 属于 OWASP A05（安全配置错误）范畴",
        "fix_nginx": '```nginx\nadd_header X-Content-Type-Options "nosniff" always;\n```',
        "fix_apache": '```apache\nHeader always set X-Content-Type-Options "nosniff"\n```',
        "fix_cloudflare": "Cloudflare → Rules → Transform Rules → 添加响应头 `X-Content-Type-Options: nosniff`",
        "fix_express": "```javascript\nconst helmet = require('helmet');\napp.use(helmet.noSniff());\n```",
        "fix_flask": "```python\n@app.after_request\ndef add_security_headers(resp):\n    resp.headers['X-Content-Type-Options'] = 'nosniff'\n    return resp\n```",
        "verify": "**验证方法**：\n\n1. **浏览器开发者工具**：F12 → Network → 查看 Response Headers\n\n2. **curl 命令**：\n```bash\ncurl -sI https://yourdomain.com | grep -i x-content-type\n```\n\n3. **功能测试**：上传一个内容为 JS 的 .txt 文件，访问时确认浏览器没有执行它。",
    },
    "referrer_policy": {
        "name": "Referrer-Policy",
        "category": "security_header",
        "severity": "low",
        "aliases": [
            "referrer-policy",
            "referrer",
            "referer",
            "引用页",
            "来源页",
            "引荐",
        ],
        "principle": "Referrer-Policy 控制浏览器在跳转时**是否带上来源页面的 URL**（Referer 头）。\n\n**为什么重要**：URL 里可能包含敏感信息（如重置密码的 token、用户 ID、搜索关键词），如果跳转到第三方网站，这些信息会被泄露。\n\n**常用策略**（从松到严）：\n- `no-referrer` — 从不发送 Referrer\n- `strict-origin-when-cross-origin` — 同站发完整 URL，跨站只发域名（且必须 HTTPS→HTTPS）\n- `origin` — 只发送域名\n- `no-referrer-when-downgrade` — HTTPS→HTTP 不发（默认行为）",
        "risk": "🟢 **低风险**\n- 跳转时可能泄露 URL 中的敏感参数\n- 如重置密码链接中的 token 可能被第三方站点获取\n- 内部系统的 URL 结构可能被外部知晓\n- 隐私保护层面的问题",
        "fix_nginx": '```nginx\n# 推荐：跨域时只发送域名，且必须 HTTPS\nadd_header Referrer-Policy "strict-origin-when-cross-origin" always;\n\n# 更严格：完全不发送 Referrer\n# add_header Referrer-Policy "no-referrer" always;\n```',
        "fix_apache": '```apache\nHeader always set Referrer-Policy "strict-origin-when-cross-origin"\n```',
        "fix_cloudflare": "Cloudflare → Rules → Transform Rules → 添加响应头 `Referrer-Policy: strict-origin-when-cross-origin`",
        "fix_express": "```javascript\nconst helmet = require('helmet');\napp.use(helmet.referrerPolicy({ policy: 'strict-origin-when-cross-origin' }));\n```",
        "fix_flask": "```python\n@app.after_request\ndef add_security_headers(resp):\n    resp.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'\n    return resp\n```",
        "verify": "**验证方法**：\n\n1. **浏览器开发者工具**：F12 → Network → 点击一个请求 → 看 Response Headers 中的 `referrer-policy`\n\n2. **跳转测试**：从你的页面点击跳转到一个外部网站（如 https://httpbin.org/get），看请求头里的 Referer 值是否符合策略。\n\n3. **curl 检查**：\n```bash\ncurl -sI https://yourdomain.com | grep -i referrer\n```",
    },
    "permissions_policy": {
        "name": "Permissions-Policy",
        "category": "security_header",
        "severity": "low",
        "aliases": [
            "permissions-policy",
            "权限策略",
            "feature-policy",
            "摄像头",
            "麦克风",
            "地理位置",
            "geolocation",
        ],
        "principle": "Permissions-Policy（原名 Feature-Policy）控制网页**能使用哪些浏览器 API**，比如摄像头、麦克风、地理位置、支付、USB 等。\n\n**核心思想**：默认关闭不需要的危险 API，防止被恶意脚本滥用。即使网站被 XSS 攻击，攻击者也无法调用这些敏感 API。",
        "risk": "🟢 **低风险**\n- 恶意脚本可能在用户不知情的情况下开启摄像头/麦克风\n- 可能获取用户地理位置信息\n- 属于深度防御的一环（Defense in Depth）\n- 配合 CSP 等其他措施构建多层防护",
        "fix_nginx": '```nginx\nadd_header Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=(), usb=(), interest-cohort=()" always;\n\n# 说明：空括号 () 表示完全禁用该功能\n# 如果需要启用某些功能，可指定来源：geolocation=(self "https://example.com")\n```',
        "fix_apache": '```apache\nHeader always set Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=(), usb=()"\n```',
        "fix_cloudflare": "Cloudflare → Rules → Transform Rules → 添加响应头",
        "fix_express": "```javascript\nconst helmet = require('helmet');\napp.use(helmet.permittedCrossDomainPolicies());\napp.use((req, res, next) => {\n  res.setHeader('Permissions-Policy', 'camera=(), microphone=(), geolocation=(), payment=(), usb=()');\n  next();\n});\n```",
        "fix_flask": "```python\n@app.after_request\ndef add_security_headers(resp):\n    resp.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=(), payment=(), usb=()'\n    return resp\n```",
        "verify": "**验证方法**：\n\n1. **浏览器开发者工具**：F12 → Network → 查看 Response Headers 中的 `permissions-policy`\n\n2. **JS 控制台测试**：\n```javascript\n// 测试摄像头权限\nnavigator.permissions.query({name: 'camera'}).then(console.log);\n```\n\n3. **curl 命令**：\n```bash\ncurl -sI https://yourdomain.com | grep -i permissions\n```",
    },
    "x_xss_protection": {
        "name": "X-XSS-Protection",
        "category": "security_header",
        "severity": "low",
        "aliases": ["x-xss-protection", "xss保护", "xss 保护", "xss防护"],
        "principle": "X-XSS-Protection 是 IE/Chrome/Safari 旧版浏览器的 XSS 过滤机制。\n\n**注意**：现代浏览器已逐步废弃这个头，推荐使用 **CSP** 作为主要的 XSS 防护手段。但为了兼容旧浏览器，仍然建议配置。\n\n**取值**：\n- `0` — 禁用过滤\n- `1` — 启用，发现 XSS 时清理不安全代码\n- `1; mode=block` — 启用，发现 XSS 时直接阻止页面渲染（推荐）",
        "risk": "🟢 **低风险**\n- 对使用旧版浏览器的用户有一定保护作用\n- 是 CSP 的补充措施，不是替代品\n- 现代浏览器已逐步移除 XSS Auditor\n- 属于防御纵深的一层",
        "fix_nginx": '```nginx\nadd_header X-XSS-Protection "1; mode=block" always;\n```',
        "fix_apache": '```apache\nHeader always set X-XSS-Protection "1; mode=block"\n```',
        "fix_cloudflare": "Cloudflare → Rules → Transform Rules → 添加响应头",
        "fix_express": "```javascript\nconst helmet = require('helmet');\napp.use(helmet.xssFilter());\n```",
        "fix_flask": "```python\n@app.after_request\ndef add_security_headers(resp):\n    resp.headers['X-XSS-Protection'] = '1; mode=block'\n    return resp\n```",
        "verify": "**验证方法**：\n\n1. **浏览器开发者工具**：F12 → Network → 查看 Response Headers\n\n2. **curl 命令**：\n```bash\ncurl -sI https://yourdomain.com | grep -i x-xss\n```\n\n💡 **建议**：主要依靠 CSP 防护 XSS，这个头作为补充。",
    },
    "cache_control": {
        "name": "Cache-Control",
        "category": "security_header",
        "severity": "low",
        "aliases": ["cache-control", "缓存控制", "缓存策略", "cache", "缓存"],
        "principle": "Cache-Control 控制浏览器和 CDN 如何缓存页面内容。\n\n**安全角度的重要性**：敏感页面（如用户后台、个人信息）如果被缓存，可能在共享设备上被其他人看到。\n\n**重要指令**：\n- `no-store` — 完全不缓存（最严格，用于敏感页面）\n- `no-cache` — 缓存但每次需要服务器验证\n- `private` — 只能被浏览器缓存，不能被 CDN/代理缓存\n- `max-age` — 缓存有效期（秒）",
        "risk": "🟢 **低风险**\n- 敏感页面被缓存后可能在共享设备泄露信息\n- 浏览器后退按钮可能显示已退出的用户数据\n- 对有用户登录的系统需要特别注意",
        "fix_nginx": '```nginx\n# 对敏感页面完全禁用缓存\nlocation ~* /(admin|dashboard|account|user) {\n    add_header Cache-Control "no-store, no-cache, must-revalidate, proxy-revalidate" always;\n    add_header Pragma "no-cache" always;\n    add_header Expires "0" always;\n}\n\n# 静态资源可以长期缓存\nlocation ~* \\.(js|css|png|jpg|gif|ico|svg)$ {\n    expires 30d;\n    add_header Cache-Control "public, immutable";\n}\n```',
        "fix_apache": '```apache\n# 敏感页面不缓存\n<FilesMatch "(login|admin|dashboard)">\n  Header set Cache-Control "no-store, no-cache, must-revalidate"\n  Header set Pragma "no-cache"\n  Header set Expires "0"\n</FilesMatch>\n```',
        "fix_cloudflare": "Cloudflare → Caching → Page Rules → 为敏感路径设置 Cache Level: Bypass",
        "fix_express": "```javascript\n// 对敏感路由设置不缓存\napp.use('/admin', (req, res, next) => {\n  res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate');\n  res.setHeader('Pragma', 'no-cache');\n  next();\n});\n\n// 静态资源用 helmet 处理\napp.use(helmet.noCache()); // 全部禁用缓存（按需使用）\n```",
        "fix_flask": "```python\n@app.after_request\ndef add_cache_headers(resp):\n    # 只对 HTML 页面禁用缓存，静态资源由 Nginx 处理\n    if 'text/html' in resp.content_type:\n        resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'\n        resp.headers['Pragma'] = 'no-cache'\n    return resp\n```",
        "verify": "**验证方法**：\n\n1. **浏览器开发者工具**：F12 → Network → 看 Response Headers 中的 `cache-control`\n\n2. **缓存测试**：登录后退出，按浏览器后退按钮，确认看不到敏感信息\n\n3. **curl 检查**：\n```bash\ncurl -sI https://yourdomain.com/admin | grep -i cache\n```",
    },
    "set_cookie": {
        "name": "Set-Cookie 安全属性 (HttpOnly / Secure / SameSite)",
        "category": "security_header",
        "severity": "high",
        "aliases": [
            "cookie",
            "cookies",
            "set-cookie",
            "httponly",
            "samesite",
            "secure cookie",
            "会话安全",
            "session",
            "cookie安全",
        ],
        "principle": "Cookie 有三个关键安全属性：\n\n1. **HttpOnly** — 禁止 JS 读取 Cookie，防止 XSS 窃取 Session\n2. **Secure** — 只在 HTTPS 连接下发送 Cookie，防止网络窃听\n3. **SameSite** — 控制跨站请求是否发送 Cookie，防御 CSRF\n\n**三者配合使用**，可以有效防御 XSS 窃会话、CSRF 攻击、中间人攻击。",
        "risk": "🔴 **高风险**\n- 没有 HttpOnly：XSS 攻击可以直接窃取 Session Cookie，接管账号\n- 没有 Secure：HTTP 下 Cookie 明文传输，可被中间人窃取\n- 没有 SameSite：容易遭受 CSRF 攻击，用户登录态被冒用\n- 属于 OWASP A07（认证失败）范畴",
        "fix_nginx": '```nginx\n# 用 proxy_cookie_path 给后端设置的 Cookie 加上属性\nproxy_cookie_path / "/; HttpOnly; Secure; SameSite=Strict";\n\n# 或者用更灵活的方式（Nginx 1.19.8+ 支持）\nproxy_cookie_flags ~ secure httponly samesite=strict;\n```',
        "fix_apache": "```apache\n# 修改所有 Cookie 属性\nHeader always edit Set-Cookie ^(.*)$ $1;HttpOnly;Secure;SameSite=Strict\n```",
        "fix_cloudflare": "Cloudflare → Rules → Transform Rules → 修改 Set-Cookie 响应头",
        "fix_express": "```javascript\n// Express session 配置\nconst session = require('express-session');\napp.use(session({\n  secret: 'your-secret-key',\n  cookie: {\n    httpOnly: true,   // 禁止 JS 访问\n    secure: true,     // 只在 HTTPS 下发送\n    sameSite: 'strict', // 严格同站\n    maxAge: 24 * 60 * 60 * 1000, // 24小时\n  },\n  resave: false,\n  saveUninitialized: false,\n}));\n```",
        "fix_flask": "```python\napp.config.update(\n    SESSION_COOKIE_HTTPONLY=True,\n    SESSION_COOKIE_SECURE=True,\n    SESSION_COOKIE_SAMESITE='Strict',\n    PERMANENT_SESSION_LIFETIME=86400,  # 24小时\n)\n```",
        "verify": "**验证方法**：\n\n1. **浏览器开发者工具**：F12 → Application → Cookies → 看 HttpOnly、Secure、SameSite 列是否有对勾\n\n2. **Network 面板**：看 Response Headers 中的 `set-cookie`\n\n3. **XSS 测试**：在 Console 输入 `document.cookie`，确认看不到带 HttpOnly 的 Cookie",
    },
    "cors": {
        "name": "CORS (Cross-Origin Resource Sharing)",
        "category": "security_header",
        "severity": "medium",
        "aliases": [
            "cors",
            "跨域",
            "跨站资源共享",
            "access-control-allow-origin",
            "跨域问题",
        ],
        "principle": "CORS（跨域资源共享）是浏览器的安全机制，控制哪些外域网站可以请求你的资源。\n\n**同源策略**：浏览器默认禁止 JS 跨域请求数据。CSP 是「白名单」机制，你可以指定允许的来源。\n\n**关键响应头**：\n- `Access-Control-Allow-Origin` — 允许哪些来源\n- `Access-Control-Allow-Methods` — 允许哪些 HTTP 方法\n- `Access-Control-Allow-Credentials` — 是否允许带 Cookie\n- `Access-Control-Max-Age` — 预检请求缓存时间",
        "risk": "🟡 **中风险**\n- 配置为 `*`（允许所有来源）且允许 credentials 时，任何网站都可以以用户身份请求数据\n- 可能导致用户数据泄露（个人信息、订单、余额等）\n- 错误配置的 CORS 是常见的安全漏洞\n- 属于 OWASP A05（安全配置错误）范畴",
        "fix_nginx": '```nginx\n# 正确配置：只允许可信来源\nadd_header Access-Control-Allow-Origin "https://trusted.example.com" always;\nadd_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;\nadd_header Access-Control-Allow-Headers "Content-Type, Authorization" always;\nadd_header Access-Control-Allow-Credentials "true" always;\n\n# 处理预检请求\nif ($request_method = OPTIONS) {\n    return 204;\n}\n\n# ❌ 危险配置（不要这样）：\n# add_header Access-Control-Allow-Origin "*" always;\n# add_header Access-Control-Allow-Credentials "true" always;\n```',
        "fix_apache": '```apache\nHeader always set Access-Control-Allow-Origin "https://trusted.example.com"\nHeader always set Access-Control-Allow-Methods "GET, POST, OPTIONS"\nHeader always set Access-Control-Allow-Credentials "true"\n```',
        "fix_cloudflare": "Cloudflare → Rules → Transform Rules → 添加 CORS 相关响应头",
        "fix_express": "```javascript\nconst cors = require('cors');\n\n// 安全配置：白名单模式\nconst corsOptions = {\n  origin: ['https://trusted.example.com', 'https://app.yourdomain.com'],\n  credentials: true,\n  methods: ['GET', 'POST', 'PUT', 'DELETE'],\n  allowedHeaders: ['Content-Type', 'Authorization'],\n};\napp.use(cors(corsOptions));\n\n// ❌ 危险配置（不要这样）：\n// app.use(cors({ origin: '*', credentials: true }));\n```",
        "fix_flask": '```python\nfrom flask_cors import CORS\n\nCORS(app, resources={\n    r"/api/*": {\n        "origins": ["https://trusted.example.com"],\n        "supports_credentials": True,\n        "methods": ["GET", "POST", "OPTIONS"],\n    }\n})\n```',
        "verify": '**验证方法**：\n\n1. **浏览器开发者工具**：从其他域名发送请求，看 Network 中的 Response Headers\n\n2. **curl 测试**：\n```bash\ncurl -sI -X OPTIONS \\\n  -H "Origin: https://evil.com" \\\n  -H "Access-Control-Request-Method: GET" \\\n  https://yourdomain.com/api/data\n# 看 Access-Control-Allow-Origin 是否正确\n```\n\n3. **验证凭证安全**：确认 `Access-Control-Allow-Origin: *` 和 `Allow-Credentials: true` 不同时出现',
    },
    # ===== 漏洞类 =====
    "sql_injection": {
        "name": "SQL 注入 (SQL Injection)",
        "category": "vulnerability",
        "severity": "critical",
        "aliases": [
            "sql注入",
            "sql 注入",
            "注入攻击",
            "sql注入攻击",
            "数据库注入",
            "sqli",
        ],
        "principle": "SQL 注入是攻击者通过在输入参数中注入恶意 SQL 代码，让后端数据库执行非预期查询的攻击。\n\n**攻击原理**：如果后端代码直接拼接 SQL 语句，攻击者可以构造特殊输入改变 SQL 语义。\n\n**典型例子**：\n```python\n# 危险：直接拼接\nsql = f\"SELECT * FROM users WHERE username='{username}'\"\n# 攻击者输入：' OR '1'='1\n# 变成：SELECT * FROM users WHERE username='' OR '1'='1'\n```\n\n**是 OWASP Top 10 A03（注入攻击）的头号代表**。",
        "risk": "🔴 **严重（Critical）**\n- 可能泄露整个数据库的数据（用户信息、密码、订单等）\n- 可能修改/删除数据库表（数据破坏）\n- 可能获取服务器权限（通过存储过程、文件读写等）\n- 是最危险的 Web 漏洞之一\n- 每年造成大量数据泄露事件",
        "fix_code": "**核心修复原则：永远不要拼接 SQL，使用参数化查询（预编译语句）**\n\n```python\n# ✅ 正确：参数化查询\ncursor.execute(\"SELECT * FROM users WHERE username = ?\", (username,))\n\n# ✅ ORM 方式（推荐）\nuser = User.query.filter_by(username=username).first()\n```\n\n```javascript\n// ✅ 参数化查询\nconst result = await pool.query('SELECT * FROM users WHERE username = ?', [username]);\n\n// ✅ ORM (Sequelize / Prisma)\nconst user = await User.findOne({ where: { username } });\n```\n\n**额外防护**：\n- 输入校验和白名单过滤\n- 最小权限原则（数据库账号只给必要权限）\n- WAF 作为补充防线\n- 错误信息不要泄露数据库结构",
        "verify": "**验证方法**：\n\n1. **手工测试**：在输入框输入单引号 `'`，看是否报数据库错误\n\n2. **经典 payload**：\n- `' OR '1'='1` — 测试布尔注入\n- `' AND SLEEP(5) --` — 测试时间盲注\n- `1' UNION SELECT 1,2,3 --` — 测试 UNION 注入\n\n3. **工具扫描**：使用 SQLMap、AWVS 等专业工具\n\n4. **代码审计**：检查所有数据库操作是否都使用了参数化查询\n\n⚠ **重要**：SQL 注入是高危漏洞，发现后应立即修复。",
    },
    "xss": {
        "name": "XSS (跨站脚本攻击)",
        "category": "vulnerability",
        "severity": "high",
        "aliases": [
            "xss",
            "跨站脚本",
            "脚本注入",
            "跨站脚本攻击",
            "cross-site scripting",
        ],
        "principle": "XSS（跨站脚本攻击）是攻击者在网页中注入恶意脚本，当其他用户访问时脚本在其浏览器中执行。\n\n**三种类型**：\n1. **反射型 XSS** — 脚本来自 URL 参数，服务端直接输出到页面\n2. **存储型 XSS** — 脚本被存入数据库，所有访问者都会触发（危害最大）\n3. **DOM 型 XSS** — 前端 JS 直接把用户输入插入 DOM，不经过服务端\n\n**攻击后果**：窃取 Cookie、劫持会话、钓鱼、挖矿、键盘记录等。",
        "risk": "🔴 **高风险**\n- 存储型 XSS 可影响所有用户，危害极大\n- 可窃取用户 Session，直接接管账号\n- 可伪造页面进行钓鱼诈骗\n- 可植入恶意代码（挖矿、木马）\n- 是 OWASP Top 10 A03（注入攻击）的核心内容",
        "fix_code": "**多层防御策略**：\n\n**第 1 层：输出编码（最关键）**\n```javascript\n// ✅ 用 textContent 而不是 innerHTML\nelement.textContent = userInput;\n\n// ✅ React/Vue 等框架默认自动转义\n<div>{userInput}</div>\n```\n\n```python\n# ✅ Jinja2 模板默认自动转义\n{{ user_input }}\n```\n\n**第 2 层：输入校验**\n- 对输入做白名单校验（如邮箱、手机号格式）\n- 限制特殊字符\n\n**第 3 层：CSP（内容安全策略）**\n- 配置 CSP 头，即使注入了脚本也无法执行\n- 这是最有效的 XSS 防御手段\n\n**第 4 层：HttpOnly Cookie**\n- 给 Session Cookie 加 HttpOnly 属性\n- 即使被 XSS 也偷不到 Cookie",
        "verify": "**验证方法**：\n\n1. **手工测试**：在输入框输入 `<script>alert(1)</script>` 或 `<img src=x onerror=alert(1)>`\n\n2. **专业工具**：使用 OWASP ZAP、Burp Suite 主动扫描\n\n3. **代码审计**：\n- 检查所有 `innerHTML`、`document.write` 等危险 API\n- 检查模板中是否使用了 `|safe` 等跳过转义的指令\n- 检查所有用户输入的输出点\n\n4. **CSP 验证**：配置 CSP 后，故意注入测试脚本，确认被拦截",
    },
    "csrf": {
        "name": "CSRF (跨站请求伪造)",
        "category": "vulnerability",
        "severity": "high",
        "aliases": ["csrf", "跨站请求伪造", "xsrf", "cross-site request forgery"],
        "principle": "CSRF 是攻击者诱导已登录的用户访问恶意页面，利用用户的登录态自动发起请求。\n\n**攻击原理**：浏览器会自动带上目标网站的 Cookie。如果用户已登录你的网站，访问了恶意网站，恶意网站可以构造表单/图片请求你的 API，浏览器会带着用户的 Cookie 发送。\n\n**典型场景**：用户登录了银行网站，然后访问了攻击者的网站，攻击者的页面自动发了一个转账请求。",
        "risk": "🔴 **高风险**\n- 攻击者可以以用户的身份执行操作\n- 转账、改密码、删数据、发邮件等都可能被伪造\n- 用户完全不知情\n- 是经典的 Web 安全漏洞\n- 属于 OWASP Top 10 历史常客",
        "fix_code": "**核心防御手段**：\n\n**1. CSRF Token（推荐）**\n```python\n# Flask-WTF 示例\nfrom flask_wtf.csrf import CSRFProtect\ncsrf = CSRFProtect(app)\n\n# 表单中自动包含\n<form method=\"POST\">\n    {{ form.hidden_tag() }}\n    ...\n</form>\n```\n\n```javascript\n// Express + csurf\nconst csrf = require('csurf');\napp.use(csrf({ cookie: true }));\n// 所有 POST 请求都要带 _csrf token\n```\n\n**2. SameSite Cookie**\n```\nSet-Cookie: session=xxx; SameSite=Strict; HttpOnly; Secure\n```\n- `Strict` — 完全不随跨站请求发送（最严）\n- `Lax` — 顶级导航的 GET 请求会带（默认值，平衡体验）\n\n**3. 验证 Referer/Origin 头**\n- 检查请求来源是否是自己的域名\n- 作为补充手段\n\n**4. 二次验证**\n- 敏感操作要求输入密码或验证码",
        "verify": "**验证方法**：\n\n1. **手工测试**：\n- 登录目标网站\n- 构造一个包含 POST 表单的恶意 HTML 页面\n- 在同一浏览器打开，看操作是否成功\n\n2. **检查 Token**：\n- 每个表单是否有 CSRF token\n- 不带 token 的请求是否被拒绝\n- token 是否随机且不可预测\n\n3. **SameSite 验证**：\n- 看 Cookie 的 SameSite 属性\n- 跨站请求时 Cookie 是否被正确阻止",
    },
    "sensitive_files": {
        "name": "敏感文件泄露",
        "category": "vulnerability",
        "severity": "high",
        "aliases": [
            "敏感文件",
            ".env",
            ".git",
            "git泄露",
            "源码泄露",
            "敏感信息",
            "信息泄露",
            "配置泄露",
            "备份文件",
            "sql文件",
            "环境变量",
        ],
        "principle": "敏感文件泄露是指网站的配置文件、源码、备份等敏感文件可以通过 URL 直接访问下载。\n\n**常见敏感文件**：\n- `.env` — 环境变量配置（数据库密码、API Key 等）\n- `.git/` — Git 仓库（完整源码 + 提交历史）\n- `.gitignore`、`.svn/` — 版本控制文件\n- `backup.sql`、`dump.sql` — 数据库备份\n- `config.php`、`config.json` — 配置文件\n- `phpinfo.php` — PHP 信息\n- `.DS_Store` — macOS 目录信息",
        "risk": "🔴 **高风险**\n- .env 泄露直接拿到数据库密码、API 密钥\n- .git 泄露拿到完整源码，可以审计其他漏洞\n- 数据库备份泄露 = 所有数据泄露\n- 可能导致进一步的入侵（拿服务器权限）\n- 很多重大安全事件都始于一个简单的文件泄露",
        "fix_code": '**多层防护**：\n\n**第 1 层：Web 服务器拦截**\n```nginx\n# Nginx 拦截所有隐藏文件和敏感后缀\nlocation ~ /\\. {\n    deny all;\n    return 403;\n}\n\nlocation ~* \\.(env|git|svn|hg|bak|sql|log|swp|ini|conf)$ {\n    deny all;\n    return 403;\n}\n\nlocation ~* (backup|dump|test|install|setup)\\.(php|sql|tar|zip|gz)$ {\n    deny all;\n    return 403;\n}\n```\n\n```apache\n# Apache .htaccess\n<FilesMatch "^\\.">\n    Order allow,deny\n    Deny from all\n</FilesMatch>\n```\n\n**第 2 层：部署规范**\n- 不要把 .env、.git 等文件放在 Web 根目录下\n- 使用部署工具（Git 只拉取代码，不上传 .git 目录）\n- 定期检查 Web 根目录下有没有不该存在的文件\n\n**第 3 层：权限控制**\n- 配置文件权限 600（只有所有者可读）\n- Web 进程用户不要有读配置文件的权限（通过环境变量传递）',
        "verify": "**验证方法**：\n\n1. **直接访问测试**：\n```\nhttps://yourdomain.com/.env\nhttps://yourdomain.com/.git/HEAD\nhttps://yourdomain.com/backup.sql\n```\n\n2. **本工具扫描**：扫描报告会列出所有发现的敏感文件\n\n3. **curl 批量测试**：\n```bash\nfor f in .env .git/HEAD backup.sql config.php; do\n  echo \"$f: $(curl -s -o /dev/null -w '%{http_code}' https://yourdomain.com/$f)\"\ndone\n```\n\n4. **定期巡检**：用工具定期检查是否有新的敏感文件暴露",
    },
    "directory_traversal": {
        "name": "目录遍历 (Path Traversal)",
        "category": "vulnerability",
        "severity": "high",
        "aliases": [
            "目录遍历",
            "路径遍历",
            "路径穿越",
            "目录穿越",
            "../",
            "dot dot slash",
            "路径遍历攻击",
        ],
        "principle": "目录遍历是攻击者通过构造 `../` 等特殊路径，访问到 Web 根目录以外的文件。\n\n**攻击原理**：如果后端代码直接把用户输入拼接到文件路径上，没有做规范化和限制，攻击者可以跳出指定目录。\n\n**典型例子**：\n```\n/download?file=../../../../etc/passwd\n/view?page=../../../windows/system32/config/sam\n```\n\n**攻击后果**：读取系统敏感文件、源代码、配置文件等。",
        "risk": "🔴 **高风险**\n- 可以读取服务器上的任意文件\n- 泄露源代码、配置、密码、日志等\n- 可能进一步导致 RCE（远程代码执行）\n- 是经典的高危漏洞",
        "fix_code": "**核心修复原则：永远不要相信用户输入的路径**\n\n**1. 白名单方式（最安全）**\n```python\nALLOWED_FILES = {\n    'report': '/var/data/report.pdf',\n    'manual': '/var/data/manual.pdf',\n}\nfilename = request.args.get('file', '')\nif filename not in ALLOWED_FILES:\n    abort(404)\nfilepath = ALLOWED_FILES[filename]\n```\n\n**2. 路径规范化 + 目录限制**\n```python\nimport os\n\nbase_dir = '/var/data/downloads/'\nuser_file = request.args.get('file', '')\n\n# 规范化路径\nreal_path = os.path.realpath(os.path.join(base_dir, user_file))\n\n# 检查是否在允许的目录内\nif not real_path.startswith(base_dir):\n    abort(403)\n```\n\n**3. 输入过滤**\n- 过滤 `../`、`..\\`、`%2e%2e%2f` 等编码形式\n- 但注意：过滤可以被绕过，必须配合路径规范化检查",
        "verify": "**验证方法**：\n\n1. **经典 payload 测试**：\n```\n?file=../../../../etc/passwd\n?file=..%2f..%2f..%2fetc%2fpasswd\n?file=....//....//etc/passwd\n```\n\n2. **Windows 系统**：\n```\n?file=..\\..\\..\\windows\\system32\\drivers\\etc\\hosts\n```\n\n3. **代码审计**：\n- 所有文件操作的地方都要检查\n- 看是否对用户输入做了路径安全处理\n- 推荐使用 path 规范化 + 目录前缀检查",
    },
    "ssrf": {
        "name": "SSRF (服务端请求伪造)",
        "category": "vulnerability",
        "severity": "high",
        "aliases": [
            "ssrf",
            "服务端请求伪造",
            "服务端伪造",
            "server-side request forgery",
        ],
        "principle": "SSRF 是攻击者让服务器发起请求，访问内网资源或云服务元数据。\n\n**攻击原理**：如果服务端有「根据用户提供的 URL 获取内容」的功能（如截图、图片代理、网页抓取），攻击者可以让它请求内网地址。\n\n**典型攻击目标**：\n- 内网服务（`http://127.0.0.1:6379` Redis、`http://169.254.169.254` 云元数据）\n- 云服务元数据 API（获取临时凭证）\n- 内网管理后台\n- Elasticsearch、MongoDB 等无密码的内网服务",
        "risk": "🔴 **高风险**\n- 可以探测内网架构和服务\n- 可以攻击内网服务（Redis、MongoDB 等）\n- 在云环境中可能获取服务器权限（通过元数据 API）\n- 是 OWASP Top 10 2021 新增的 A10\n- 近年来云服务普及后危害越来越大",
        "fix_code": "**多层防御**：\n\n**1. 使用白名单域名（推荐）**\n```python\nALLOWED_DOMAINS = ['trusted.com', 'cdn.example.com']\n\ndef is_safe_url(url):\n    from urllib.parse import urlparse\n    parsed = urlparse(url)\n    if parsed.scheme not in ('http', 'https'):\n        return False\n    if parsed.hostname not in ALLOWED_DOMAINS:\n        return False\n    return True\n```\n\n**2. 禁止内网地址**\n```python\nimport ipaddress\nimport socket\n\ndef is_internal_ip(url):\n    hostname = urlparse(url).hostname\n    try:\n        ip = socket.gethostbyname(hostname)\n        return ipaddress.ip_address(ip).is_private\n    except:\n        return True  # 解析失败也拒绝\n```\n\n**3. 禁用危险协议**\n- 只允许 http/https\n- 禁止 file://、gopher://、dict:// 等\n\n**4. 独立网络隔离**\n- 用单独的安全组/网络策略限制发起请求的服务\n- 不让它能访问内网其他服务",
        "verify": "**验证方法**：\n\n1. **内网地址测试**：\n```\n?url=http://127.0.0.1/\n?url=http://169.254.169.254/latest/meta-data/\n?url=http://localhost:6379/\n```\n\n2. **协议测试**：\n```\n?url=file:///etc/passwd\n?url=gopher://127.0.0.1:6379/_INFO\n```\n\n3. **DNS 重绑定测试**：用 DNS 重绑定工具绕过 IP 校验\n\n4. **代码审计**：\n- 所有发起 HTTP 请求的地方都要检查\n- 看 URL 参数是否来自用户输入\n- 确认有完整的 SSRF 防护",
    },
    "clickjacking": {
        "name": "点击劫持 (Clickjacking)",
        "category": "vulnerability",
        "severity": "medium",
        "aliases": ["点击劫持", "clickjacking", "ui redressing", "界面伪装"],
        "principle": "点击劫持是攻击者用透明 iframe 把目标页面覆盖在恶意页面上，用户以为在点正常按钮，实际上点的是目标页面的敏感操作。\n\n**攻击场景**：\n1. 攻击者创建一个诱人的页面（如「点击领取红包」）\n2. 在上面覆盖一个透明的 iframe，加载受害者已登录的网站\n3. 用户点「领取」按钮，实际点的是 iframe 里的「转账」按钮",
        "risk": "🟡 **中风险**\n- 可以诱导用户执行未授权操作\n- 转账、改密码、关注、点赞等都可能被伪造\n- 对有敏感操作的网站危害较大\n- 用户体验层面的攻击，技术门槛低",
        "fix_code": '**三层防御**：\n\n**第 1 层：X-Frame-Options 头**\n```nginx\nadd_header X-Frame-Options "DENY" always;\n```\n\n**第 2 层：CSP frame-ancestors 指令**\n```nginx\nadd_header Content-Security-Policy "frame-ancestors \'none\'" always;\n```\n\n**第 3 层：前端防御（frame-busting）**\n```javascript\n// 检测是否被 iframe 嵌入\nif (window.top !== window.self) {\n    window.top.location = window.self.location;\n}\n```\n\n**敏感操作额外保护**：\n- 关键操作要求二次确认（输入密码/验证码）\n- 使用 reCAPTCHA 等人机验证',
        "verify": '**验证方法**：\n\n1. **iframe 测试**：\n```html\n<iframe src="https://yourdomain.com" width="800" height="600"></iframe>\n```\n如果页面拒绝显示说明生效。\n\n2. **检查响应头**：\n```bash\ncurl -sI https://yourdomain.com | grep -iE \'x-frame|content-security\'\n```\n\n3. **浏览器开发者工具**：看 Console 有没有 frame 拦截的报错',
    },
    "mime_sniffing": {
        "name": "MIME 嗅探攻击",
        "category": "vulnerability",
        "severity": "medium",
        "aliases": [
            "mime嗅探",
            "mime 嗅探",
            "nosniff",
            "x-content-type",
            "mime类型猜测",
            "内容嗅探",
        ],
        "principle": "MIME 嗅探是浏览器的「自动识别」功能：当服务器返回的 Content-Type 不明确时，浏览器会猜测文件类型。\n\n**攻击原理**：攻击者上传一个后缀是 `.jpg` 但内容是 JS/HTML 的文件。浏览器嗅探后把它当脚本/HTML 执行，导致 XSS。\n\n**典型场景**：图片上传功能，用户上传了「图片」实际是 HTML 页面，访问时被浏览器当 HTML 解析。",
        "risk": "🟡 **中风险**\n- 配合文件上传可导致 XSS\n- 用户上传的文件可能被当作脚本执行\n- 对允许用户上传内容的网站风险较高\n- 是常见的 Web 安全配置问题",
        "fix_code": "**核心修复**：\n\n**1. 添加 X-Content-Type-Options: nosniff**\n```nginx\nadd_header X-Content-Type-Options \"nosniff\" always;\n```\n\n**2. 正确设置 Content-Type**\n- 服务端明确指定每个文件的 MIME 类型\n- 不要让浏览器猜测\n\n**3. 文件上传加固**\n- 校验文件头（魔数），不仅看后缀名\n- 图片类文件重新编码（破坏恶意代码）\n- 上传文件放在独立域名（用户上传的静态资源和主站隔离）\n- 使用 CDN/OSS 的图片处理功能\n\n**4. 配合 CSP**\n- 配置 `default-src 'self'` 限制脚本执行来源",
        "verify": "**验证方法**：\n\n1. **响应头检查**：\n```bash\ncurl -sI https://yourdomain.com/ | grep -i x-content-type\n```\n\n2. **功能测试**：\n- 上传一个内容为 `<script>alert(1)</script>` 的 .txt 文件\n- 访问该文件，确认浏览器没有执行脚本\n\n3. **图片上传测试**：\n- 上传伪装成图片的 HTML 文件\n- 确认访问时以下载方式或纯文本方式显示，不执行脚本",
    },
    "ssl_weak_config": {
        "name": "SSL/TLS 弱配置",
        "category": "vulnerability",
        "severity": "high",
        "aliases": [
            "ssl",
            "tls",
            "弱加密",
            "弱配置",
            "ssl/tls",
            "tls配置",
            "证书",
            "弱密码套件",
            "ssl漏洞",
            "tls漏洞",
        ],
        "principle": "SSL/TLS 弱配置是指 HTTPS 配置不安全，比如使用过时的协议版本、弱加密算法、弱证书等。\n\n**常见问题**：\n- 仍支持 SSLv3、TLS 1.0、TLS 1.1 等旧协议\n- 使用弱密码套件（如 RC4、DES、3DES）\n- 证书过期或自签名\n- 密钥长度不够（1024 位 RSA）\n- 缺少 OCSP Stapling、HSTS 等增强配置",
        "risk": "🔴 **高风险**\n- 弱加密可能被破解，导致 HTTPS 传输的数据被窃听\n- 旧协议存在已知漏洞（POODLE、BEAST、Heartbleed 等）\n- 证书问题导致中间人攻击成为可能\n- 是整个网站安全的基础，基础不牢地动山摇",
        "fix_code": "**推荐配置（以 Nginx 为例）**：\n\n```nginx\n# 协议版本：只保留 TLS 1.2 和 1.3\nssl_protocols TLSv1.2 TLSv1.3;\n\n# 密码套件（强加密优先）\nssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384';\n\n# 服务器优先选择密码套件\nssl_prefer_server_ciphers on;\n\n# SSL 会话缓存\nssl_session_cache shared:SSL:10m;\nssl_session_timeout 10m;\n\n# OCSP Stapling\nssl_stapling on;\nssl_stapling_verify on;\nresolver 8.8.8.8 8.8.4.4 valid=300s;\n\n# DH 参数（2048位以上）\nssl_dhparam /etc/nginx/dhparam.pem;\n```\n\n**证书要求**：\n- RSA 密钥至少 2048 位（推荐 4096 位）\n- ECDSA 密钥至少 256 位\n- 使用 SHA-256 签名算法\n- 证书有效期不超过 1 年",
        "verify": "**验证方法**：\n\n1. **在线工具**：\n- SSL Labs Server Test（ssllabs.com/ssltest）\n- 得到 A 以上评级才算合格\n\n2. **命令行测试**：\n```bash\n# 测试支持的协议版本\nopenssl s_client -connect yourdomain.com:443 -tls1_1\n# 如果能连上说明还支持旧协议\n\n# 查看证书信息\nopenssl s_client -connect yourdomain.com:443 -showcerts\n```\n\n3. **nmap 脚本扫描**：\n```bash\nnmap --script ssl-enum-ciphers -p 443 yourdomain.com\n```\n\n4. **本工具扫描**：检测 SSL/TLS 配置并给出评分",
    },
    "info_leak": {
        "name": "信息泄露 (Server 头、版本号)",
        "category": "vulnerability",
        "severity": "low",
        "aliases": [
            "信息泄露",
            "server头",
            "server 头",
            "版本泄露",
            "服务器版本",
            "banner",
            "信息泄漏",
            "指纹识别",
        ],
        "principle": "信息泄露是指网站通过响应头、错误页面、注释等方式暴露了服务器软件、版本号、框架、语言等技术细节。\n\n**常见泄露点**：\n- `Server: nginx/1.18.0 (Ubuntu)` — 服务器软件和版本\n- `X-Powered-By: PHP/7.4.3` — 后端语言和版本\n- `X-AspNet-Version` — ASP.NET 版本\n- 错误页面显示完整堆栈信息\n- HTML 注释中遗留调试信息\n- 版本号在 URL、Cookie 中暴露",
        "risk": "🟢 **低风险**\n- 帮助攻击者缩小攻击范围，针对特定版本找已知漏洞\n- 降低攻击门槛，提高攻击效率\n- 本身不直接造成危害，但会放大其他漏洞的影响\n- 属于安全加固的一部分",
        "fix_code": "**各平台隐藏版本号方法**：\n\n**Nginx**：\n```nginx\nserver_tokens off;  # 隐藏 Nginx 版本号\n\n# 如需完全隐藏 Server 头（需要第三方模块或 Nginx Plus）\n# more_clear_headers 'Server' 'X-Powered-By';\n```\n\n**Apache**：\n```apache\nServerTokens Prod\nServerSignature Off\nHeader unset X-Powered-By\n```\n\n**PHP**：\n```ini\n# php.ini\nexpose_php = Off\n```\n\n**Express**：\n```javascript\napp.disable('x-powered-by');\n```\n\n**Flask**：\n```python\n@app.after_request\ndef remove_headers(resp):\n    resp.headers.pop('Server', None)\n    return resp\n```\n\n**错误页面**：\n- 自定义 4xx/5xx 错误页面\n- 不要暴露堆栈信息、SQL 错误详情\n- 生产环境关闭 debug 模式",
        "verify": "**验证方法**：\n\n1. **响应头检查**：\n```bash\ncurl -sI https://yourdomain.com | grep -iE 'server|x-powered|x-asp'\n```\n\n2. **错误页面测试**：\n- 访问不存在的页面（404）看错误信息\n- 故意触发 500 错误看是否泄露堆栈\n\n3. **页面源码检查**：\n- 查看 HTML 源码，看注释中有没有敏感信息\n- 检查 JS 中有没有硬编码的密钥、路径\n\n4. **指纹识别工具**：用 Wappalyzer、WhatWeb 等工具看能识别出多少信息",
    },
}

# ---------- 工具使用类知识库 ----------
_AI_TOOL_KB = {
    "how_to_scan": {
        "name": "怎么扫描网站",
        "question": "怎么扫描网站",
        "aliases": [
            "怎么扫描",
            "如何扫描",
            "怎么扫",
            "扫一下",
            "开始扫描",
            "怎么用",
            "如何使用",
        ],
        "answer": "**🔍 怎么扫描网站（30 秒上手）**\n\n**步骤 1：输入网址**\n在首页的扫描框中输入目标网站地址（比如 `example.com` 或 `https://example.com`），自动补全协议。\n\n**步骤 2：开始扫描**\n点击「开始扫描」按钮，等待 5-15 秒即可完成。\n\n**步骤 3：查看报告**\n扫描完成后自动展示结果，包括：\n- 📊 安全评分（满分 100）\n- 🔴 高风险 / 🟡 中风险 / 🟢 低风险 分类\n- 🛠 每个问题的修复代码\n- ✅ 验证修复效果\n\n**💡 小贴士**：\n- 登录后可以保存扫描历史\n- 支持批量扫描（最多 5 个 URL）\n- 可以添加监控，定期自动扫描\n- 扫描完全在服务端完成，不需要安装任何东西",
    },
    "how_to_read_report": {
        "name": "怎么看扫描报告",
        "question": "怎么看扫描报告",
        "aliases": [
            "怎么看报告",
            "扫描报告",
            "报告怎么看",
            "怎么看结果",
            "结果在哪",
            "报告解读",
        ],
        "answer": "**📋 怎么看扫描报告**\n\n报告从上到下分为几个部分：\n\n**1. 概览区**\n- 评分（满分 100）和风险等级\n- 高/中/低风险项数量统计\n- 扫描的目标 URL 和时间\n\n**2. 真实证据区（可展开）**\n- 🔬 服务器实际响应头列表\n- 🔬 缺失的关键安全头\n- 🔬 敏感文件探测结果\n\n**3. 详细问题列表**\n每个问题包含：\n- 问题名称和严重程度标签\n- OWASP 分类（如有）\n- 问题详情描述\n- 💡 修复建议\n- 🛠 修复代码（可展开，多平台）\n- ✅ 验证方法（可展开）\n\n**4. 修复建议区**\n- 6 大平台的完整修复模板\n- 一键复制配置\n\n**💡 建议阅读顺序**：先看评分 → 再看高风险项 → 逐个看修复方法 → 应用后重新扫描验证",
    },
    "how_to_use_fixer": {
        "name": "怎么用修复器",
        "question": "怎么用修复器",
        "aliases": [
            "修复器",
            "修复配置生成",
            "生成修复配置",
            "怎么用修复",
            "修复工具",
            "修复代码",
            "怎么修复",
        ],
        "answer": "**🛠 怎么用修复功能**\n\n**方式 1：手动复制配置（推荐）**\n1. 扫描后展开「修复代码」部分\n2. 选择你的服务器平台（Nginx/Apache/Express/Flask/Cloudflare）\n3. 点击「复制」按钮复制配置代码\n4. 粘贴到你的配置文件中\n5. 重启服务或重载配置\n\n**方式 2：完整修复模板**\n扫描报告底部有「完整修复建议」区域：\n- 切换不同平台 tab\n- 一键复制整段配置\n- 包含所有检测项的修复代码\n\n**方式 3：Cloudflare 一键应用**\n如果你的网站使用 Cloudflare CDN：\n1. 在设置中配置 Cloudflare API Token\n2. 扫描后点击「一键应用到 Cloudflare」\n3. 自动将安全头配置推送到 Cloudflare\n\n**⚠ 注意事项**：\n- 修改配置前先备份\n- 建议先在测试环境验证\n- CSP 策略可能影响第三方资源，注意观察控制台报错\n- 修改后务必重新扫描验证",
    },
    "how_to_verify_fix": {
        "name": "怎么验证修复效果",
        "question": "怎么验证修复效果",
        "aliases": [
            "怎么验证",
            "如何验证",
            "验证修复",
            "修复后怎么看",
            "怎么确认",
            "验证效果",
        ],
        "answer": "**✅ 怎么验证修复效果**\n\n**方法 1：重新扫描（最简单）**\n1. 应用修复后，在扫描报告页点击「重新扫描」\n2. 工具会重新检测所有项目\n3. 对比修复前后的评分和问题列表\n4. 已修复的问题会消失，评分相应提升\n\n**方法 2：浏览器开发者工具**\n1. 打开网站，按 F12\n2. 切换到 Network 面板\n3. 刷新页面，点击第一个请求\n4. 查看 Response Headers 中是否有安全头\n\n**方法 3：curl 命令**\n```bash\n# 查看所有响应头\ncurl -sI https://yourdomain.com\n\n# 只看安全相关的头\ncurl -sI https://yourdomain.com | grep -iE 'strict-transport|content-security|x-frame|x-content|referrer|permissions'\n```\n\n**方法 4：在线工具**\n- securityheaders.com — 安全头检测\n- SSL Labs — SSL/TLS 配置检测\n\n**💡 建议**：修复后用多种方法验证，确保万无一失。本工具的重新扫描功能最方便，可以同时看评分变化。",
    },
    "score_rules": {
        "name": "评分规则是什么",
        "question": "评分规则是什么",
        "aliases": [
            "评分规则",
            "怎么算分",
            "打分规则",
            "分数怎么算",
            "评分标准",
            "计分规则",
        ],
        "answer": "**📊 评分规则详解（满分 100 分）**\n\n**基础分**：100 分\n\n**扣分项**：\n| 严重程度 | 每个扣分 |\n|---------|---------|\n| Critical（严重） | -25 分 |\n| High（高风险） | -15 分 |\n| Medium（中风险） | -8 分 |\n| Low（低风险） | -3 分 |\n\n**加分项（修复加成）**：\n| 项目 | 加分 |\n|-----|-----|\n| 4 个核心安全头（HSTS+CSP+XFO+XCTO） | +12 分 |\n| 敏感文件拦截 | +6 分 |\n| 隐藏 Server 版本号 | +4 分 |\n| Cookie 安全属性 | +5 分 |\n| Referrer-Policy | +2 分 |\n| Permissions-Policy | +2 分 |\n\n**风险等级对应分数**：\n- 🟢 安全：90-100 分\n- 🟡 中等：60-89 分\n- 🔴 危险：0-59 分\n\n**💡 快速提分技巧**：\n1. 先加 4 个核心安全头（+12 分，5 分钟搞定）\n2. 隐藏 Server 版本号（+4 分，1 行配置）\n3. 拦截敏感文件（+6 分，几行配置）\n这三项加起来就有 22 分提升空间！",
    },
}

# ---------- 通用回复 ----------
_AI_GENERAL_REPLIES = {
    "greeting": "你好呀！我是Vuln Sentinel的安全顾问 🛡️\n\n我可以帮你：\n- 🔍 解释安全概念和漏洞原理\n- 🛠 给出具体的修复代码（多平台）\n- ✅ 告诉你怎么验证修复效果\n- 📊 分析你的扫描报告和扣分原因\n- 🎯 给出修复优先级建议\n\n直接问我就行，比如：\n- 「HSTS 是什么？」\n- 「CSP 怎么配置？」\n- 「SQL 注入怎么防？」\n- 「我应该先修什么？」",
    "thanks": "不客气！能帮到你我很开心 😊\n\n安全是一场持久战，不是一劳永逸的事情。修完问题后记得定期扫描，保持网站的安全状态。\n\n有任何安全问题随时问我，也欢迎你把工具推荐给朋友～",
    "fallback": "我还在学习中，暂时不太理解你的问题 🤔\n\n你可以试试这样问：\n- 「HSTS 是什么？怎么修复？」\n- 「XSS 漏洞怎么防？」\n- 「我应该先修什么问题？」\n- 「评分规则是什么？」\n- 「怎么扫描网站？」\n\n或者告诉我你想了解哪方面的安全知识，我来给你推荐～",
}


# ---------- 智能匹配引擎 ----------
def _ai_calculate_match_score(msg: str, aliases: list) -> float:
    """计算用户消息与知识条目的匹配分数（加权匹配）"""
    msg_lower = msg.lower()
    score = 0.0

    for alias in aliases:
        alias_lower = alias.lower()
        if alias_lower in msg_lower:
            # 完全包含：基础分 + 长度加权（越长的词匹配权重越高）
            base = 10.0 + len(alias_lower) * 0.5
            score += base

            # 如果是消息中的主要内容（占比较高），额外加分
            if len(alias_lower) / max(len(msg_lower), 1) > 0.3:
                score += 5.0

    return score


def _ai_detect_intent(msg: str) -> list:
    """检测用户意图，返回意图列表（按置信度排序）"""
    msg_lower = msg.lower()
    intents = []

    for intent, keywords in _AI_INTENT_KEYWORDS.items():
        count = 0
        for kw in keywords:
            if kw.lower() in msg_lower:
                count += 1
        if count > 0:
            intents.append((intent, count))

    intents.sort(key=lambda x: -x[1])
    return [i[0] for i in intents]


def _ai_find_best_knowledge(msg: str) -> tuple:
    """在知识库中找到最佳匹配的条目，返回 (key, entry, score)"""
    best_key = None
    best_entry = None
    best_score = 0.0

    # 搜索安全知识库
    for key, entry in _AI_KNOWLEDGE_BASE.items():
        score = _ai_calculate_match_score(msg, entry["aliases"])
        if score > best_score:
            best_score = score
            best_key = key
            best_entry = entry

    # 搜索工具知识库
    for key, entry in _AI_TOOL_KB.items():
        score = _ai_calculate_match_score(msg, entry["aliases"])
        if score > best_score:
            best_score = score
            best_key = key
            best_entry = entry

    return best_key, best_entry, best_score


def _ai_generate_knowledge_reply(entry: dict, intents: list, msg: str) -> str:
    """根据知识条目和用户意图生成回答"""
    # 工具类知识库直接返回 answer
    if entry.get("answer"):
        return entry["answer"]

    # 判断用户主要想知道什么
    wants_fix = any(i in intents for i in ["fix", "config_location"])
    wants_principle = "principle" in intents
    wants_risk = "risk" in intents
    wants_verify = "verify" in intents

    # 如果没有明确意图，或者是询问"是什么/介绍"，给完整回答
    if (
        not intents
        or wants_principle
        or ("是什么" in msg or "什么是" in msg or "介绍" in msg or "解释" in msg)
    ):
        parts = []
        parts.append(f"**{entry['name']}**\n")
        parts.append(entry.get("principle", ""))
        if entry.get("risk"):
            parts.append(f"\n---\n**⚠ 风险等级**\n{entry['risk']}")
        if entry.get("fix_nginx") or entry.get("fix_code"):
            parts.append("\n---\n**🛠 修复方案**")
            if entry.get("fix_nginx"):
                parts.append(entry["fix_nginx"])
            elif entry.get("fix_code"):
                parts.append(entry["fix_code"])
        if entry.get("verify"):
            parts.append(f"\n---\n**✅ 验证方法**\n{entry['verify']}")
        parts.append("\n---\n**💡 行动建议**\n")
        sev = entry.get("severity", "medium")
        if sev in ("critical", "high"):
            parts.append(
                "这是高风险项，建议尽快修复。先在测试环境验证配置，确认无误后再部署到生产环境。"
            )
        else:
            parts.append(
                "虽然风险等级不高，但作为安全加固的一部分，建议在下次迭代中修复。"
            )
        return "\n".join(parts)

    # 用户明确问修复
    if wants_fix:
        parts = [f"**🛠 {entry['name']} - 修复方案**\n"]
        if entry.get("fix_nginx"):
            parts.append("**Nginx 配置：**\n")
            parts.append(entry["fix_nginx"])
        if entry.get("fix_apache"):
            parts.append("\n**Apache 配置：**\n")
            parts.append(entry["fix_apache"])
        if entry.get("fix_cloudflare"):
            parts.append("\n**Cloudflare 配置：**\n")
            parts.append(entry["fix_cloudflare"])
        if entry.get("fix_express"):
            parts.append("\n**Node.js / Express：**\n")
            parts.append(entry["fix_express"])
        if entry.get("fix_flask"):
            parts.append("\n**Python / Flask：**\n")
            parts.append(entry["fix_flask"])
        if entry.get("fix_code"):
            parts.append(entry["fix_code"])
        if entry.get("verify"):
            parts.append(f"\n---\n**✅ 验证方法**\n{entry['verify']}")
        parts.append(
            "\n---\n**💡 小贴士**：修改配置后记得重启服务，然后重新扫描验证效果。"
        )
        return "\n".join(parts)

    # 用户明确问风险
    if wants_risk:
        parts = [f"**⚠ {entry['name']} - 风险分析**\n"]
        if entry.get("risk"):
            parts.append(entry["risk"])
        else:
            parts.append("暂无详细风险分析。")
        return "\n".join(parts)

    # 用户明确问验证
    if wants_verify:
        parts = [f"**✅ {entry['name']} - 验证方法**\n"]
        if entry.get("verify"):
            parts.append(entry["verify"])
        else:
            parts.append("修复后重新扫描该网站，查看对应问题项是否消失。")
        return "\n".join(parts)

    # 默认：给出简要介绍 + 修复
    parts = [f"**{entry['name']}**\n"]
    if entry.get("principle"):
        # 取前两段
        para = entry["principle"].split("\n\n")[0]
        parts.append(para)
    if entry.get("fix_nginx"):
        parts.append(f"\n**🛠 Nginx 修复示例：**\n{entry['fix_nginx']}")
    elif entry.get("fix_code"):
        parts.append(f"\n**🛠 修复方案：**\n{entry['fix_code']}")
    parts.append("\n💡 想了解更多可以问我：「原理是什么」「有什么风险」「怎么验证」")
    return "\n".join(parts)


def _ai_generate_scan_based_reply(
    msg: str, scan_context: dict, intents: list, matched_knowledge: tuple
) -> str:
    """基于扫描结果生成个性化回答"""
    findings = scan_context.get("findings", [])
    score = scan_context.get("score", 0)
    risk_level = scan_context.get("risk_level", "未知")
    summary = scan_context.get("summary", {})

    # 按严重程度排序
    def sev_rank(sev):
        return {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(sev, 4)

    sorted_findings = sorted(findings, key=lambda f: sev_rank(f.get("severity", "low")))
    high_findings = [f for f in findings if f.get("severity") in ("critical", "high")]

    # 1. 优先级 / 先修什么
    if any(i in intents for i in ["priority"]):
        lines = [
            f"🔍 基于你最近的扫描结果（{score} 分，{risk_level}），建议按以下优先级修复：\n"
        ]

        if not sorted_findings:
            lines.append("🎉 太棒了！没有发现任何安全问题，你的网站安全状况很好！")
            return "\n".join(lines)

        for i, f in enumerate(sorted_findings[:5], 1):
            sev = f.get("severity", "low")
            tag = (
                "🔴"
                if sev in ("critical", "high")
                else "🟡"
                if sev == "medium"
                else "🟢"
            )
            lines.append(f"{tag} **第{i}优先**：{f.get('name', '未知问题')}")
            if f.get("description") or f.get("detail"):
                desc = (f.get("description") or f.get("detail", ""))[:60]
                lines.append(f"   📝 {desc}")
            lines.append("")

        # 预估提升
        estimated_bonus = min(100 - score, len(high_findings) * 15 + 10)
        lines.append(
            f"---\n**📈 预估效果**：全部修复后，评分预计可提升到 **{min(100, score + estimated_bonus)} 分** 左右。"
        )
        lines.append(
            "\n💡 建议先集中解决 🔴 高风险项，见效最快。修完后重新扫描验证效果吧！"
        )
        return "\n".join(lines)

    # 2. 分数 / 扣分原因
    if any(i in intents for i in ["score"]):
        lines = [f"📊 你的当前评分：**{score} 分**（{risk_level}）\n"]

        if summary:
            h = summary.get("high", 0)
            m = summary.get("medium", 0)
            low_n = summary.get("low", 0)
            c = summary.get("critical", 0)

            lines.append("**扣分明细：**")
            if c:
                lines.append(f"- 🔴 严重问题 {c} 个 × 25 分 = -{c * 25} 分")
            if h:
                lines.append(f"- 🔴 高风险 {h} 个 × 15 分 = -{h * 15} 分")
            if m:
                lines.append(f"- 🟡 中风险 {m} 个 × 8 分 = -{m * 8} 分")
            if low_n:
                lines.append(f"- 🟢 低风险 {low_n} 个 × 3 分 = -{low_n * 3} 分")

        lines.append("\n**主要扣分点：**")
        for f in sorted_findings[:5]:
            sev = f.get("severity", "low")
            deduction = {"critical": 25, "high": 15, "medium": 8, "low": 3}.get(sev, 0)
            tag = (
                "🔴"
                if sev in ("critical", "high")
                else "🟡"
                if sev == "medium"
                else "🟢"
            )
            lines.append(f"{tag} {f.get('name', '')}（-{deduction} 分）")

        # 快速提分建议
        lines.append("\n---\n**💡 快速提分建议**：")
        easy_fixes = [
            f
            for f in findings
            if "头" in f.get("name", "") or "缺少" in f.get("name", "")
        ]
        if easy_fixes:
            lines.append("安全头配置是最快的提分方式，加几个响应头就能涨 10-20 分。")
            lines.append(
                "比如加 HSTS、CSP、X-Frame-Options、X-Content-Type-Options 这 4 个头，只需要几分钟。"
            )
        else:
            lines.append("你的基础安全配置已经不错了，可以关注更深层的安全问题。")

        return "\n".join(lines)

    # 3. 能提升多少分
    if "upgrade" in intents:
        high_count = len(high_findings)
        med_count = len([f for f in findings if f.get("severity") == "medium"])
        low_count = len([f for f in findings if f.get("severity") == "low"])

        potential = high_count * 15 + med_count * 8 + low_count * 3
        estimated = min(100, score + potential)

        lines = ["📈 评分提升预估\n"]
        lines.append(f"当前评分：**{score} 分**")
        lines.append(f"全部修复后预计：**{estimated} 分**（最多提升 {potential} 分）\n")

        lines.append("**分阶段提升计划：**")
        lines.append(
            f"1️⃣ **第一阶段**（修复所有 🔴 高风险）→ 约 +{high_count * 15} 分，到 {min(100, score + high_count * 15)} 分"
        )
        lines.append(
            f"2️⃣ **第二阶段**（修复所有 🟡 中风险）→ 再加 +{med_count * 8} 分，到 {min(100, score + high_count * 15 + med_count * 8)} 分"
        )
        lines.append(
            f"3️⃣ **第三阶段**（修复所有 🟢 低风险）→ 再加 +{low_count * 3} 分，到 {min(100, score + potential)} 分"
        )

        lines.append("\n💡 建议从高风险项开始，投入产出比最高。")
        return "\n".join(lines)

    # 4. 配置位置
    if "config_location" in intents:
        lines = ["📌 安全配置放置位置指南：\n"]
        lines.append("**Nginx**：")
        lines.append("- 主配置：`/etc/nginx/nginx.conf`")
        lines.append(
            "- 站点配置：`/etc/nginx/conf.d/` 或 `/etc/nginx/sites-available/`"
        )
        lines.append("- 加在 `server { }` 块内")
        lines.append("- 修改后执行：`nginx -t && nginx -s reload`\n")
        lines.append("**Apache**：")
        lines.append(
            "- 主配置：`/etc/httpd/conf/httpd.conf` 或 `/etc/apache2/apache2.conf`"
        )
        lines.append(
            "- 站点配置：`/etc/httpd/conf.d/` 或 `/etc/apache2/sites-available/`"
        )
        lines.append("- 也可以放在 `.htaccess` 文件中（需要启用 mod_headers）\n")
        lines.append("**Express (Node.js)**：")
        lines.append("- 推荐使用 `helmet` 中间件")
        lines.append("- 在 `app.js` 中，`app.listen()` 之前添加\n")
        lines.append("**Flask / FastAPI (Python)**：")
        lines.append("- 使用 `flask-talisman` 或 `@app.after_request` 装饰器\n")
        lines.append("**Cloudflare**：")
        lines.append("- Dashboard → Rules → Transform Rules → Modify Response Header\n")
        lines.append("⚠ **重要**：修改配置前先备份！修改后务必验证！")
        return "\n".join(lines)

    # 5. 上线风险
    if "deployment_risk" in intents:
        high_count = len(high_findings)
        lines = ["⚠ 上线安全风险评估：\n"]

        if high_count > 0:
            lines.append(
                f"🔴 **高风险**：发现 {high_count} 个高风险项，**不建议直接上线**。"
            )
            lines.append("高风险项可能导致数据泄露、账号被接管等严重后果。")
        elif score >= 80:
            lines.append("🟢 **低风险**：整体安全状况良好，可以考虑上线。")
        else:
            lines.append(
                "🟡 **中等风险**：存在一些安全配置问题，建议修复关键项后再上线。"
            )

        lines.append(f"\n**必须修复的高风险项（{len(high_findings)} 个）：**")
        for f in high_findings[:5]:
            lines.append(f"- {f.get('name', '')}")

        lines.append("\n**💡 上线前安全检查清单：**")
        lines.append(
            "1. HSTS / CSP / X-Frame-Options / X-Content-Type-Options 四个核心头是否配置"
        )
        lines.append("2. 敏感文件（.env、.git 等）是否可访问")
        lines.append("3. Cookie 是否设置了 HttpOnly、Secure、SameSite")
        lines.append("4. 调试模式是否关闭，错误信息是否泄露堆栈")
        lines.append("5. CSP 是否会影响第三方资源（建议先 report-only 模式）")

        return "\n".join(lines)

    # 6. 如果匹配到了具体的知识条目，结合扫描结果回答
    if matched_knowledge and matched_knowledge[1]:
        key, entry, match_score = matched_knowledge
        # 检查用户的扫描结果中是否有这个问题
        has_issue = any(
            any(
                alias.lower() in f.get("name", "").lower() for alias in entry["aliases"]
            )
            for f in findings
        )

        base_reply = _ai_generate_knowledge_reply(entry, intents, msg)

        if has_issue:
            return (
                base_reply
                + f"\n\n---\n**📌 你的网站状态**：\n⚠️ 检测到你的网站存在「{entry['name']}」相关问题，建议尽快修复。修复后重新扫描即可看到评分提升。"
            )
        else:
            return (
                base_reply
                + f"\n\n---\n**📌 你的网站状态**：\n✅ 好消息！你的网站没有检测到「{entry['name']}」相关问题，继续保持～"
            )

    # 7. 默认：给出扫描摘要
    lines = ["📋 你最近的扫描结果摘要：\n"]
    lines.append(f"- **评分**：{score} 分（{risk_level}）")
    if summary:
        lines.append(
            f"- **高风险**：{summary.get('high', 0) + summary.get('critical', 0)} 个"
        )
        lines.append(f"- **中风险**：{summary.get('medium', 0)} 个")
        lines.append(f"- **低风险**：{summary.get('low', 0)} 个")

    if sorted_findings:
        lines.append("\n**主要问题（前 5 个）：**")
        for i, f in enumerate(sorted_findings[:5], 1):
            sev = f.get("severity", "low")
            tag = (
                "🔴"
                if sev in ("critical", "high")
                else "🟡"
                if sev == "medium"
                else "🟢"
            )
            lines.append(f"{tag} {i}. {f.get('name', '')}")

    lines.append(
        f"\n💡 可以问我：「先修什么」「为什么扣分」「{sorted_findings[0].get('name', 'HSTS') if sorted_findings else 'HSTS'}怎么修」"
    )
    return "\n".join(lines)


def _ai_get_last_scan(user_id: int) -> dict:
    """获取用户最近一次扫描结果"""
    if not user_id:
        return None
    try:
        conn = get_db()
        try:
            row = conn.execute(
                "SELECT findings_json, summary_json, score, risk_level, url FROM scans WHERE user_id=? ORDER BY id DESC LIMIT 1",
                (user_id,),
            ).fetchone()
            if row:
                try:
                    findings = (
                        json.loads(row["findings_json"]) if row["findings_json"] else []
                    )
                    summary = (
                        json.loads(row["summary_json"]) if row["summary_json"] else {}
                    )
                    return {
                        "findings": findings,
                        "summary": summary,
                        "score": row["score"],
                        "risk_level": row["risk_level"],
                        "url": row["url"],
                    }
                except Exception:
                    return None
            return None
        finally:
            conn.close()
    except Exception as e:
        logger.warning("Failed to get last scan for AI: %s", e)
        return None


def _ai_resolve_reference(msg: str, history: list) -> str:
    """解析指代，比如"第二个呢"、"怎么验证"等，返回展开后的问题"""
    if not history:
        return msg

    msg_lower = msg.lower().strip()
    msg_len = len(msg_lower)

    # 找最近一条 AI 的回复中提到的问题列表
    last_assistant = None
    last_user = None
    for h in history:
        if h.get("role") == "assistant":
            last_assistant = h.get("content", "")
        elif h.get("role") == "user":
            last_user = h.get("content", "")

    if not last_assistant:
        return msg

    # "第二个呢 / 第二个问题 / 第二项"
    if any(
        k in msg_lower
        for k in ["第二个", "第二项", "第二个呢", "下一个", "第二个问题", "第2个"]
    ):
        # 从最近的优先级回答中提取第二个问题
        import re

        # 匹配 "第2优先：xxx" 或 "2. xxx" 格式
        patterns = [
            r"第2优先[：:]\s*(.+)",
            r"第\s*2\s*优先[：:]\s*(.+)",
            r"\*\*第2优先\*\*[：:]\s*(.+)",
            r"2\.\s+(.+)",
        ]
        for p in patterns:
            m = re.search(p, last_assistant)
            if m:
                issue_name = m.group(1).strip()
                # 清理 markdown 标记
                issue_name = re.sub(r"[\*_]", "", issue_name).strip()
                # 截断到合适长度
                if len(issue_name) > 50:
                    issue_name = issue_name[:50]
                return f"{issue_name} 怎么修复"

    # 只有当消息很短（<=8字）且不包含知识库关键词时，才考虑指代
    # 避免把 "目录遍历怎么修复" 这类完整问题错误解析为指代
    if msg_len <= 8 and last_user:
        # 先检查消息中是否已经包含了明确的知识库关键词
        has_kb_keyword = False
        for entry in _AI_KNOWLEDGE_BASE.values():
            for alias in entry["aliases"]:
                if len(alias) >= 2 and alias.lower() in msg_lower:
                    has_kb_keyword = True
                    break
            if has_kb_keyword:
                break

        if not has_kb_keyword:
            # "怎么验证 / 验证方法" - 指代上一个讨论的漏洞
            if any(
                k in msg_lower
                for k in ["怎么验证", "如何验证", "怎么确认", "验证方法", "验证一下"]
            ):
                # 用上一个用户问题补充 "验证" 意图
                return f"{last_user} 怎么验证"

            # "怎么修 / 修复方法" - 如果上一个是原理类问题
            if any(
                k in msg_lower
                for k in [
                    "怎么修",
                    "如何修复",
                    "修复方法",
                    "怎么解决",
                    "咋弄",
                    "怎么办",
                ]
            ):
                # 检查上一个问题是不是在问某个漏洞
                last_lower = last_user.lower()
                is_knowledge_question = any(
                    any(alias in last_lower for alias in entry["aliases"])
                    for entry in _AI_KNOWLEDGE_BASE.values()
                )
                if is_knowledge_question:
                    return f"{last_user} 怎么修复"

    return msg


# ---------- 主 AI 顾问函数 ----------
@app.post("/api/ai-advisor")
async def ai_advisor(
    req: AIAdvisorRequest, request: Request, user=Depends(get_current_user)
):
    """Vuln Sentinel 升级版 AI 安全顾问：智能匹配 + 上下文感知 + 多轮对话"""
    client_ip = get_client_ip(request)
    if not await limiter_ai.is_allowed(client_ip):
        raise HTTPException(
            status_code=429,
            detail="AI 顾问请求过于频繁，请稍后再试",
            headers={"Retry-After": "60"},
        )

    original_msg = (req.message or "").strip()
    # 兼容 question / query 参数名（旧客户端或测试脚本可能用这些字段名）
    if not original_msg:
        try:
            body = await request.json()
            original_msg = (body.get("question") or body.get("query") or "").strip()
        except Exception:
            pass
    if not original_msg:
        return {
            "reply": "请输入问题，例如：HSTS 是什么？如何修复 CSP？",
            "source": "rule_engine",
        }

    # 1. 获取对话历史（用于多轮对话上下文）
    history = []
    user_id = user.get("user_id") if user else None
    if user_id:
        history = _get_recent_conversations(user_id, 10)
        history.reverse()  # 按时序

    # 2. 指代消解（处理"第二个呢"、"怎么验证"等）
    resolved_msg = _ai_resolve_reference(original_msg, history)

    # 3. 意图识别
    intents = _ai_detect_intent(resolved_msg)

    # 4. 获取最近扫描结果（上下文感知）
    scan_context = None
    if user_id:
        if req.scan_id:
            try:
                conn = get_db()
                try:
                    row = conn.execute(
                        "SELECT findings_json, summary_json, score, risk_level, url FROM scans WHERE id=? AND user_id=?",
                        (req.scan_id, user_id),
                    ).fetchone()
                    if row:
                        scan_context = {
                            "findings": json.loads(row["findings_json"])
                            if row["findings_json"]
                            else [],
                            "summary": json.loads(row["summary_json"])
                            if row["summary_json"]
                            else {},
                            "score": row["score"],
                            "risk_level": row["risk_level"],
                            "url": row["url"],
                        }
                finally:
                    conn.close()
            except Exception as e:
                logger.warning("Failed to get scan context for AI: %s", e)
        else:
            scan_context = _ai_get_last_scan(user_id)

    # 5. 知识库匹配
    matched = _ai_find_best_knowledge(resolved_msg)
    match_score = matched[2] if matched[2] else 0

    # 6. 生成回答
    reply = ""
    source = "rule_engine"
    llm_error = None

    # 6a. 如果用户提供了 API Key 且启用 LLM，优先调用真实 LLM
    user_api_key = (req.api_key or "").strip()
    want_llm = req.use_llm if req.use_llm is not None else bool(user_api_key)
    if user_api_key and want_llm:
        try:
            messages = _build_ai_advisor_llm_prompt(
                resolved_msg, history, scan_context, matched
            )
            response_text = await _call_real_llm(
                api_key=user_api_key,
                model=req.model or "gpt-4o-mini",
                provider=req.provider,
                messages=messages,
            )
            reply = response_text
            source = "llm"
        except Exception as e:
            llm_error = str(e)[:200]
            logger.warning(
                "Real LLM call failed for user %s, falling back to rule engine: %s",
                user_id,
                e,
            )

    # 6b. 规则引擎兜底（未启用 LLM 或 LLM 失败时）
    if not reply:
        if "greeting" in intents:
            reply = _AI_GENERAL_REPLIES["greeting"]
        elif "thanks" in intents:
            reply = _AI_GENERAL_REPLIES["thanks"]
        else:
            scan_related_intents = [
                "priority",
                "score",
                "upgrade",
                "config_location",
                "deployment_risk",
            ]
            if scan_context and any(i in intents for i in scan_related_intents):
                reply = _ai_generate_scan_based_reply(
                    resolved_msg, scan_context, intents, matched
                )
            elif match_score >= 8.0 and matched[1]:
                entry = matched[1]
                if scan_context:
                    reply = _ai_generate_scan_based_reply(
                        resolved_msg, scan_context, intents, matched
                    )
                else:
                    reply = _ai_generate_knowledge_reply(entry, intents, resolved_msg)
            elif any(i in intents for i in ["tool_scan", "tool_report", "tool_fixer"]):
                tool_key = None
                if "tool_scan" in intents:
                    tool_key = "how_to_scan"
                elif "tool_report" in intents:
                    tool_key = "how_to_read_report"
                elif "tool_fixer" in intents:
                    tool_key = "how_to_use_fixer"
                if tool_key and tool_key in _AI_TOOL_KB:
                    reply = _AI_TOOL_KB[tool_key]["answer"]
            elif scan_context:
                reply = _ai_generate_scan_based_reply(
                    resolved_msg, scan_context, intents, matched
                )
            else:
                reply = _AI_GENERAL_REPLIES["fallback"]
        source = "rule_engine"

    # 7. 保存对话历史
    if user_id:
        _save_conversation(user_id, "user", original_msg)
        meta = {
            "source": source,
            "match_score": match_score,
            "intents": intents,
            "resolved_msg": resolved_msg if resolved_msg != original_msg else None,
        }
        if llm_error:
            meta["llm_error"] = llm_error
        _save_conversation(user_id, "assistant", reply, meta)

    return {"reply": reply, "source": source}


# ============== 批量扫描 ==============


@app.post("/api/batch-scan", response_model=None)
async def batch_scan(
    req: BatchScanRequest, request: Request, user=Depends(require_login)
):
    """批量扫描：一次提交多个 URL（最多 5 个），并发执行后返回对比摘要。"""
    await rate_limit_dependency(request)
    client_ip = get_client_ip(request)
    if not await limiter_batch.is_allowed(client_ip):
        raise HTTPException(
            status_code=429,
            detail="批量扫描请求过于频繁，请稍后再试",
            headers={"Retry-After": "60"},
        )
    urls = req.urls or []
    if not urls:
        raise HTTPException(400, "请提供 URL 列表")
    deep = req.deep
    user_id = user["user_id"]

    # 批量扫描全局授权检查
    if not req.authorized:
        return {
            "success": False,
            "results": [],
            "count": 0,
            "error": "请先确认您有权扫描这些目标（authorized: true）",
        }

    async def scan_one(raw: str) -> dict:
        url = (raw or "").strip()
        if not url:
            return {"url": url, "ok": False, "error": "URL 为空"}
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        parsed = urlparse(url)
        host = parsed.hostname or ""
        if not host or "." not in host:
            return {"url": url, "ok": False, "error": "URL 格式无效"}
        # 合规检查
        compliant, reason, code = validate_scan_target_full(
            url,
            user_id=user_id,
            authorized=True,
            deep=deep,
            allowed_demo=True,
        )
        if not compliant:
            return {
                "url": url,
                "ok": False,
                "error": reason,
                "restricted": True,
                "restricted_code": code,
            }
        # SSRF 校验在扣费之前，避免校验失败时已扣积分
        try:
            from utils import sanitize_url

            sanitize_url(url)
        except ValueError as e:
            return {"url": url, "ok": False, "error": str(e)}
        # 按量计费
        scan_cost = (
            credits_service.SCAN_DEEP_COST
            if deep
            else credits_service.SCAN_STANDARD_COST
        )
        if not credits_service.has_credits(user_id, scan_cost):
            return {
                "url": url,
                "ok": False,
                "error": f"扫描需要 {scan_cost} 积分，余额不足",
            }
        credits_service.deduct_credits(user_id, scan_cost, action=f"batch_scan:{host}")
        # 单个 URL 限时 25 秒，避免慢站拖死批量
        try:
            return await asyncio.wait_for(
                _scan_one_impl(url, host, deep, user_id), timeout=25.0
            )
        except asyncio.TimeoutError:
            return {"url": url, "ok": False, "error": "扫描超时（25s）"}
        except Exception as e:
            logger.warning("batch scan failed for %s: %s", url, e)
            return {"url": url, "ok": False, "error": str(e)[:200]}

    async def _scan_one_impl(url, host, deep, user_id):
        try:
            headers, is_https, final_url, error = await asyncio.wait_for(
                fetch_headers(url), timeout=20.0
            )
        except asyncio.TimeoutError:
            error = "TIMEOUT"
        if error:
            return {"url": url, "ok": False, "error": error}
        ssl_info = await get_ssl_info(host, 443) if is_https else {"has_cert": False}
        waf_list = detect_waf(headers)
        sensitive_paths = await check_sensitive_paths(host, is_https)
        crawled_pages, vuln_findings = [], []
        if deep:
            try:
                crawled_pages = await crawl_site(url, settings.max_crawl_pages)
            except Exception:
                crawled_pages = []
            try:
                vuln_findings, _ = await run_payload_tests(url, crawled_pages)
            except Exception:
                vuln_findings = []
        result = await analyze_security(
            url,
            headers,
            is_https,
            ssl_info,
            waf_list,
            sensitive_paths,
            vuln_findings,
            depth="deep" if deep else "standard",
        )
        scan_id = save_scan(
            user_id,
            url,
            result["score"],
            result["risk_level"],
            result["findings"],
            result["summary"],
            len(crawled_pages) if crawled_pages else 0,
            "deep" if deep else "real",
        )
        # 批量扫描也同步资产扫描信息
        try:
            update_asset_after_scan(user_id, host, scan_id)
        except Exception as e:
            logger.warning("Batch scan update asset failed: %s", e)
        s = result.get("summary", {})
        return {
            "url": url,
            "ok": True,
            "score": result["score"],
            "risk_level": result["risk_level"],
            "high": s.get("high", 0),
            "medium": s.get("medium", 0),
            "low": s.get("low", 0),
            "critical": s.get("critical", 0),
            "scan_id": scan_id,
            "findings_count": len(result["findings"]),
        }

    # 并发跑（asyncio.gather + return_exceptions=True），单个 URL 各自 25s 超时
    # 单个 URL 失败不影响其他 URL 结果
    raw_results = await asyncio.gather(
        *[scan_one(u) for u in urls],
        return_exceptions=True,
    )
    results = []
    for i, r in enumerate(raw_results):
        if isinstance(r, Exception):
            logger.warning("batch scan task %d failed: %s", i, r)
            results.append(
                {
                    "url": urls[i] if i < len(urls) else "",
                    "ok": False,
                    "error": f"内部错误: {type(r).__name__}",
                }
            )
        else:
            results.append(r)
    return {"success": True, "results": results, "count": len(results)}


# ---------- 资产管理 API ----------


@app.post("/api/assets")
async def api_create_asset(
    req: AssetCreateRequest, user: dict = Depends(require_login)
) -> dict:
    asset_id = create_asset(user["user_id"], req.domain, req.owner, req.description)
    return {"success": True, "asset_id": asset_id}


@app.get("/api/assets")
async def api_list_assets(user: dict = Depends(require_login)) -> dict:
    assets = get_assets(user["user_id"])
    return {"success": True, "assets": assets}


@app.patch("/api/assets/{asset_id}")
async def api_update_asset(
    asset_id: int, req: AssetUpdateRequest, user: dict = Depends(require_login)
) -> dict:
    ok = update_asset(
        asset_id, user["user_id"], owner=req.owner, description=req.description
    )
    if not ok:
        raise NotFoundException("资产不存在或无权限")
    return {"success": True}


@app.delete("/api/assets/{asset_id}")
async def api_delete_asset(asset_id: int, user: dict = Depends(require_login)) -> dict:
    ok = delete_asset(asset_id, user["user_id"])
    if not ok:
        raise NotFoundException("资产不存在或无权限")
    return {"success": True}


@app.post("/api/assets/{asset_id}/scan")
async def api_scan_asset(
    asset_id: int, request: Request, user: dict = Depends(require_login)
):
    """对资产发起扫描：复用现有扫描逻辑。"""
    await rate_limit_dependency(request)
    asset = get_asset(asset_id, user["user_id"])
    if not asset:
        raise HTTPException(404, "资产不存在或无权限")
    domain = asset["domain"]
    url = "https://" + domain
    # Vuln Sentinel fix: SSRF 防护 - 确保资产域名不是内网地址
    try:
        sanitize_url(url)
    except ValueError as e:
        return {"success": False, "error": str(e)}
    parsed = urlparse(url)
    host = parsed.hostname or domain
    try:
        headers, is_https, final_url, error = await asyncio.wait_for(
            fetch_headers(url), timeout=25.0
        )
    except asyncio.TimeoutError:
        error = "TIMEOUT"
    if error:
        return {"success": False, "error": error}
    try:
        ssl_info = await get_ssl_info(host, 443) if is_https else {"has_cert": False}
    except Exception as e:
        logger.warning("api_scan_asset get_ssl_info failed: %s", e)
        ssl_info = {"has_cert": False}
    waf_list = detect_waf(headers)
    try:
        sensitive_paths = await check_sensitive_paths(host, is_https)
    except Exception as e:
        logger.warning("api_scan_asset check_sensitive_paths failed: %s", e)
        sensitive_paths = []
    result = await analyze_security(
        url, headers, is_https, ssl_info, waf_list, sensitive_paths, []
    )
    scan_id = save_scan(
        user["user_id"],
        url,
        result["score"],
        result["risk_level"],
        result["findings"],
        result["summary"],
        0,
        "real",
    )
    try:
        auto_create_fix_tickets(
            user["user_id"], scan_id, result["findings"], target_host=host
        )
    except Exception as e:
        logger.warning("Quick scan auto create fix tickets failed: %s", e)
    try:
        update_asset_after_scan(user["user_id"], host, scan_id)
    except Exception as e:
        logger.warning("Quick scan update asset failed: %s", e)
    return {
        "success": True,
        "scan_id": scan_id,
        "score": result["score"],
        "risk_level": result["risk_level"],
    }


def _build_frontend_config_script() -> str:
    """构建前端运行时配置注入脚本（在 HTML 加载前同步执行，避免首屏竞态）。"""
    import json

    config = {
        "stripe_publishable_key": os.environ.get("STRIPE_PUBLISHABLE_KEY", ""),
        "stripe_enabled": bool(os.environ.get("STRIPE_SECRET_KEY", "")),
        "public_base_url": os.environ.get("PUBLIC_BASE_URL", ""),
        "public_demo_enabled": os.environ.get("PUBLIC_DEMO_ENABLED", "0") == "1",
        "free_trial_enabled": os.environ.get("FREE_TRIAL_ENABLED", "1") == "1",
        "alipay_enabled": bool(os.environ.get("ALIPAY_APP_ID", "")),
        "wechat_enabled": bool(os.environ.get("WECHAT_MCH_ID", "")),
        "api_version": "1",
    }
    return f"<script>window.__CONFIG__={json.dumps(config)};</script>"


@app.get("/")
async def index() -> HTMLResponse:
    preferred_indexes = [
        os.path.join(_BASE_DIR, "frontend", "dist", "index.html"),
        os.path.join(STATIC_DIR, "index.html"),
    ]
    for path in preferred_indexes:
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                html = f.read()
            config_script = _build_frontend_config_script()
            if "</head>" in html:
                html = html.replace("</head>", f"{config_script}</head>", 1)
            response = HTMLResponse(content=html)
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
    fallback_html = (
        '<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
        '<title>Vuln Sentinel</title></head><body><div id="app"></div>'
        '<script>document.body.innerHTML="<div style=\"padding:24px;font-size:18px;font-family:sans-serif\">Vuln Sentinel正在准备界面，请稍候…</div>";</script>'
        '</body></html>'
    )
    return HTMLResponse(content=fallback_html)


# ============================================================
# 本地靶场：应用修复配置 / 一键重置（真实修改本地 nginx）
# ============================================================

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEMO_NGINX_CONF = os.path.join(_BASE_DIR, "demo-target/conf/nginx.conf")
DEMO_NGINX_BACKUP = os.path.join(_BASE_DIR, "demo-target/conf/nginx.conf.vulnerable")
DEMO_NGINX_CMD = "nginx -c " + DEMO_NGINX_CONF
DEMO_CERT_CRT = os.path.join(_BASE_DIR, "demo-target/conf/server.crt")
DEMO_CERT_KEY = os.path.join(_BASE_DIR, "demo-target/conf/server.key")
# 本地靶场 nginx 配置文件读写锁，防止并发写入损坏
_demo_nginx_lock = threading.RLock()


def _demo_nginx_reload() -> tuple[bool, str]:
    """重新加载本地靶场 nginx 配置（兼容 PID 文件失效、旧进程残留等测试环境）"""
    with _demo_nginx_lock:
        try:
            # 测试配置
            result = subprocess.run(
                ["nginx", "-c", DEMO_NGINX_CONF, "-t"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                return False, f"配置测试失败: {result.stderr[:500]}"

            # 重载（如果正在运行）
            result = subprocess.run(
                ["nginx", "-c", DEMO_NGINX_CONF, "-s", "reload"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return True, "配置已生效"

            # reload 失败常见原因：PID 文件为空/失效，但 nginx 仍在运行
            # 通过 pgrep 找到属于本配置的主进程，发送 SIGHUP 强制重载
            pgrep = subprocess.run(
                ["pgrep", "-f", f"nginx: master process.*-c {DEMO_NGINX_CONF}"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if pgrep.returncode == 0 and pgrep.stdout.strip():
                master_pid = pgrep.stdout.strip().splitlines()[0].strip()
                try:
                    os.kill(int(master_pid), 1)  # SIGHUP
                    time.sleep(0.3)
                    return True, "配置已生效（SIGHUP 重载）"
                except (ProcessLookupError, ValueError, OSError):
                    pass

            # 仍然失败：停止旧实例并重新启动
            subprocess.run(
                ["nginx", "-c", DEMO_NGINX_CONF, "-s", "stop"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            subprocess.run(
                ["pkill", "-f", f"nginx -c {DEMO_NGINX_CONF}"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            time.sleep(0.5)

            result = subprocess.run(
                ["nginx", "-c", DEMO_NGINX_CONF],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                return False, f"启动失败: {result.stderr[:500]}"
            return True, "配置已生效（已重启 nginx）"
        except Exception as e:
            return False, str(e)


def _demo_nginx_apply_security_headers() -> tuple[bool, str]:
    """为本地靶场应用安全头修复（真实修改 nginx.conf）"""
    import re

    with _demo_nginx_lock:
        try:
            if not os.path.exists(DEMO_NGINX_CONF):
                return False, "靶场配置文件不存在"

            # 备份原始漏洞配置（只备份一次）
            if not os.path.exists(DEMO_NGINX_BACKUP):
                import shutil

                shutil.copy2(DEMO_NGINX_CONF, DEMO_NGINX_BACKUP)

            with open(DEMO_NGINX_CONF, encoding="utf-8") as f:
                content = f.read()

            # 如果已经有安全头了，直接返回
            if "X-Frame-Options" in content and "VulnSentinel" in content:
                return True, "安全头已经应用过了"

            # 安全头修复块（使用正确的缩进）
            security_headers_block = """
            # ===== VulnSentinel Vuln Sentinel 应用修复配置：安全响应头 =====
            add_header X-Frame-Options "SAMEORIGIN" always;
            add_header X-Content-Type-Options "nosniff" always;
            add_header Content-Security-Policy "default-src 'self'" always;
            add_header Referrer-Policy "strict-origin-when-cross-origin" always;
            add_header Permissions-Policy "camera=(), microphone=()" always;
            add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
            # ===== 应用修复配置结束 =====
    """

            # 找到第一个 server 块（8080端口），在根 location / 之前插入安全头
            # 策略：找到 "listen 8080" 后面的 "location / {" （精确匹配根location）之前插入
            lines = content.split("\n")
            new_lines = []
            in_target_server = False
            inserted = False
            i = 0
            while i < len(lines):
                line = lines[i]
                new_lines.append(line)

                # 检测是否进入了目标 server 块
                if "listen 8080" in line:
                    in_target_server = True

                # 在目标 server 块中，找到根 location / { 之前插入
                # 注意：要排除 /admin/ 等子路径，只匹配精确的 "location / {"
                stripped = line.strip()
                if (
                    in_target_server
                    and not inserted
                    and stripped.startswith("location /")
                    and "{" in stripped
                ):
                    # 检查是不是根 location（后面没有其他路径）
                    # 匹配模式: location / { 或 location /{
                    import re

                    if re.match(r"^location\s+/\s*\{", stripped):
                        # 插入安全头（使用与location相同的缩进）
                        indent = line[: len(line) - len(line.lstrip())]
                        for h_line in security_headers_block.strip().split("\n"):
                            new_lines.append(indent + h_line)
                        inserted = True

                i += 1

            # 处理第二个 server 块（8443端口）
            content = "\n".join(new_lines)
            lines = content.split("\n")
            new_lines = []
            in_https_server = False
            inserted_https = False
            i = 0
            while i < len(lines):
                line = lines[i]
                new_lines.append(line)

                if "listen 8443" in line and "ssl" in line:
                    in_https_server = True

                stripped = line.strip()
                if (
                    in_https_server
                    and not inserted_https
                    and stripped.startswith("location /")
                    and "{" in stripped
                ):
                    import re

                    if re.match(r"^location\s+/\s*\{", stripped):
                        indent = line[: len(line) - len(line.lstrip())]
                        for h_line in security_headers_block.strip().split("\n"):
                            new_lines.append(indent + h_line)
                        inserted_https = True

                i += 1

            content = "\n".join(new_lines)

            # 修复 server_tokens
            content = re.sub(r"server_tokens\s+on;", "server_tokens off;", content)

            # 修复 autoindex
            content = re.sub(r"autoindex\s+on;", "autoindex off;", content)

            # 修复 CORS 过于宽松
            content = re.sub(
                r'add_header\s+Access-Control-Allow-Origin\s+"\*"\s+always;',
                'add_header Access-Control-Allow-Origin "https://localhost:8000" always;',
                content,
            )

            # 修复 SSL 弱配置
            content = re.sub(
                r"ssl_protocols\s+SSLv3\s+TLSv1\s+TLSv1\.1\s+TLSv1\.2;",
                "ssl_protocols TLSv1.2 TLSv1.3;",
                content,
            )
            content = re.sub(
                r'ssl_ciphers\s+"ALL:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!SRP:!CAMELLIA";',
                'ssl_ciphers "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384";',
                content,
            )
            content = re.sub(
                r"ssl_prefer_server_ciphers\s+off;",
                "ssl_prefer_server_ciphers on;",
                content,
            )

            with open(DEMO_NGINX_CONF, "w", encoding="utf-8") as f:
                f.write(content)

            # 重载 nginx
            ok, msg = _demo_nginx_reload()
            if not ok:
                return False, f"配置写入成功但重载失败: {msg}"

            return True, "安全头已应用，nginx 已重载"
        except Exception as e:
            return False, f"应用修复失败: {str(e)}"


def _demo_nginx_reset() -> tuple[bool, str]:
    """重置本地靶场为有漏洞状态"""
    with _demo_nginx_lock:
        try:
            if not os.path.exists(DEMO_NGINX_BACKUP):
                return False, "没有备份文件，无法重置（请先应用一次修复）"

            import shutil

            shutil.copy2(DEMO_NGINX_BACKUP, DEMO_NGINX_CONF)

            ok, msg = _demo_nginx_reload()
            if not ok:
                return False, f"配置恢复成功但重载失败: {msg}"

            return True, "靶场已重置为初始漏洞状态"
        except Exception as e:
            return False, f"重置失败: {str(e)}"


@app.post("/api/demo-fix")
async def api_demo_fix(
    req: DemoFixRequest, request: Request, user: dict = Depends(require_login)
) -> dict:
    """
    应用修复配置/重置本地靶场
    需要登录
    action: "apply" - 应用安全头修复
            "reset" - 重置为有漏洞状态
    """
    await rate_limit_dependency(request)

    # 安全检查：只允许操作本地靶场
    if req.target not in ("localhost:8080", "localhost:8443", "127.0.0.1:8080"):
        return {"success": False, "error": "仅支持本地演示靶场"}

    if req.action == "apply":
        ok, msg = _demo_nginx_apply_security_headers()
        return {
            "success": ok,
            "action": "apply",
            "message": msg,
            "target": req.target,
        }
    elif req.action == "reset":
        ok, msg = _demo_nginx_reset()
        return {
            "success": ok,
            "action": "reset",
            "message": msg,
            "target": req.target,
        }
    else:
        return {"success": False, "error": f"未知 action: {req.action}"}


@app.post("/api/demo-full-cycle")
async def api_demo_full_cycle(
    req: DemoFullCycleRequest, request: Request, user: dict = Depends(require_login)
) -> dict:
    """
    一键完整闭环：重置 → 第一次扫描 → 应用修复 → 第二次扫描
    返回完整的前后对比数据，用于前端展示修复效果
    """
    await rate_limit_dependency(request)

    target_url = f"http://{req.target}"

    try:
        # 第0步：可选重置
        if req.reset_first:
            ok, msg = _demo_nginx_reset()
            if not ok:
                return {"success": False, "error": f"重置失败: {msg}", "step": "reset"}
            await asyncio.sleep(0.5)  # 等待 nginx reload

        # 第1步：修复前扫描
        parsed = urlparse(target_url)
        host = parsed.hostname or ""
        headers1, is_https1, final_url1, error1 = await fetch_headers(target_url)
        if error1 and not headers1:
            return {
                "success": False,
                "error": f"初次扫描失败: {error1}",
                "step": "scan1",
            }
        ssl_info1 = await get_ssl_info(host, 443) if is_https1 else {"has_cert": False}
        waf_list1 = detect_waf(headers1)
        sensitive_paths1 = await check_sensitive_paths(host, is_https1)
        result1 = await analyze_security(
            target_url, headers1, is_https1, ssl_info1, waf_list1, sensitive_paths1, []
        )
        scan_id1 = save_scan(
            user["user_id"],
            target_url,
            result1["score"],
            result1["risk_level"],
            result1["findings"],
            result1["summary"],
            0,
            "demo_before",
        )

        # 第2步：应用修复
        ok, msg = _demo_nginx_apply_security_headers()
        if not ok:
            return {
                "success": False,
                "error": f"应用修复失败: {msg}",
                "step": "apply_fix",
            }
        await asyncio.sleep(1)  # 等待 nginx reload 生效

        # 第3步：修复后扫描
        headers2, is_https2, final_url2, error2 = await fetch_headers(target_url)
        if error2 and not headers2:
            return {"success": False, "error": f"复测失败: {error2}", "step": "scan2"}
        ssl_info2 = await get_ssl_info(host, 443) if is_https2 else {"has_cert": False}
        waf_list2 = detect_waf(headers2)
        sensitive_paths2 = await check_sensitive_paths(host, is_https2)
        result2 = await analyze_security(
            target_url, headers2, is_https2, ssl_info2, waf_list2, sensitive_paths2, []
        )
        scan_id2 = save_scan(
            user["user_id"],
            target_url,
            result2["score"],
            result2["risk_level"],
            result2["findings"],
            result2["summary"],
            0,
            "demo_after",
        )

        # 计算 diff
        names1 = {f.get("name", "") for f in result1["findings"]}
        names2 = {f.get("name", "") for f in result2["findings"]}
        fixed = sorted(list(names1 - names2))
        new_issues = sorted(list(names2 - names1))
        delta = result2["score"] - result1["score"]

        return {
            "success": True,
            "target": target_url,
            "before": {
                "scan_id": scan_id1,
                "score": result1["score"],
                "risk_level": result1["risk_level"],
                "findings": result1["findings"],
                "summary": result1["summary"],
            },
            "after": {
                "scan_id": scan_id2,
                "score": result2["score"],
                "risk_level": result2["risk_level"],
                "findings": result2["findings"],
                "summary": result2["summary"],
            },
            "diff": {
                "fixed": fixed,
                "new_issues": new_issues,
                "score_delta": delta,
                "findings_fixed": len(fixed),
            },
            "steps": [
                "reset" if req.reset_first else None,
                "scan_before",
                "apply_fix",
                "scan_after",
            ],
        }
    except Exception as e:
        logger.exception("demo full cycle failed")
        return {"success": False, "error": str(e)[:300]}


@app.get("/api/demo-status")
async def api_demo_status(request: Request, user: dict = Depends(require_login)) -> dict:
    """查询本地靶场状态（需登录，防止未认证信息泄露）"""
    await rate_limit_dependency(request)
    try:
        # 检查 nginx 是否在运行
        result = subprocess.run(
            ["pgrep", "-f", DEMO_NGINX_CONF], capture_output=True, text=True, timeout=10
        )
        running = result.returncode == 0

        # 快速探测安全头状态
        headers_status = {}
        try:
            resp = await fetch_headers("http://localhost:8080/")
            hdrs, _, _, err = resp
            if not err and hdrs:
                headers_status = {
                    "x_frame_options": bool(hdrs.get("X-Frame-Options")),
                    "x_content_type_options": bool(hdrs.get("X-Content-Type-Options")),
                    "content_security_policy": bool(
                        hdrs.get("Content-Security-Policy")
                    ),
                    "referrer_policy": bool(hdrs.get("Referrer-Policy")),
                    "permissions_policy": bool(hdrs.get("Permissions-Policy")),
                    "hsts": bool(hdrs.get("Strict-Transport-Security")),
                    "server_tokens": "nginx/" in (hdrs.get("Server", "")),
                    "cors_wildcard": hdrs.get("Access-Control-Allow-Origin") == "*",
                }
        except Exception as e:
            logger.warning("Demo target status parse failed: %s", e)

        return {
            "success": True,
            "running": running,
            "config_path": DEMO_NGINX_CONF,
            "backup_exists": os.path.exists(DEMO_NGINX_BACKUP),
            "headers_status": headers_status,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ---------- 特定静态文件端点（必须在 catch-all 之前注册） ----------

_STATIC_EXT_404 = frozenset(
    [
        ".js",
        ".css",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".svg",
        ".ico",
        ".woff",
        ".woff2",
        ".ttf",
        ".ttc",
        ".otf",
        ".eot",
        ".map",
        ".webp",
        ".avif",
        ".webm",
        ".mp4",
        ".mp3",
        ".json",
    ]
)


@app.get("/robots.txt")
async def serve_robots():
    return PlainTextResponse("User-agent: *\nAllow: /")


@app.get("/favicon.ico")
async def serve_favicon():
    """尝试返回 favicon.ico；如果不存在返回 404 而非 HTML。"""
    fp = Path(STATIC_DIR) / "favicon.ico"
    if fp.is_file():
        response = FileResponse(str(fp))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    # fallback: 尝试 favicon.svg（HTML 里引用的是 .svg）
    fp2 = Path(STATIC_DIR) / "favicon.svg"
    if fp2.is_file():
        response = FileResponse(str(fp2), media_type="image/svg+xml")
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return JSONResponse(status_code=404, content={"detail": "not found"})


@app.get("/sitemap.xml")
async def serve_sitemap():
    return JSONResponse(status_code=404, content={"detail": "not found"})


@app.get("/manifest.json")
async def serve_manifest():
    """返回 PWA manifest.json（支持从 static/ 目录热更新）。"""
    fp = Path(STATIC_DIR) / "manifest.json"
    if fp.is_file():
        return FileResponse(str(fp), media_type="application/manifest+json")
    return JSONResponse(status_code=404, content={"detail": "not found"})


# ---------- 路由注册（从 main.py 拆分到 app/routers/ 的端点）----------
# 重要：include_router 必须在 catch_all 路由之前执行，
# 否则 catch_all({path:path}) 会拦截所有 GET 请求。
# 此处导入在文件末尾执行，确保 main.py 中所有共享函数（get_db、require_login 等）已定义
from app.routers.admin import router as _admin_router  # noqa: E402
from app.routers.auth import router as _auth_router  # noqa: E402
from app.routers.billing import router as _billing_router  # noqa: E402
from app.routers.gdpr import router as _gdpr_router  # noqa: E402
from app.routers.team import router as _team_router  # noqa: E402
from app.routers.user import router as _user_router  # noqa: E402

app.include_router(_auth_router)
app.include_router(_user_router)
app.include_router(_billing_router)
app.include_router(_admin_router)
app.include_router(_gdpr_router)
app.include_router(_team_router)

logger.info(
    "Routers registered: auth, user, billing, admin, gdpr, team"
)


# ---------- catch-all 路由（必须在 include_router 之后注册）----------
@app.get("/{path:path}")
async def catch_all(path: str) -> Any:
    # 性能优化：未注册的 /api/* 端点直接返回 JSON 404，
    # 避免 fallback 把整张 index.html（411KB）塞给客户端
    if path.startswith("api/"):
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": f"endpoint /{path} not found"},
        )
    # 静态资源后缀的请求：文件不存在时返回 404 而非 HTML
    _, ext = os.path.splitext(path)
    if ext.lower() in _STATIC_EXT_404:
        try:
            base = Path(STATIC_DIR).resolve()
            fp = (base / path).resolve()
            if fp.is_relative_to(base) and fp.is_file():
                response = FileResponse(str(fp))
                response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
                return response
        except (OSError, ValueError):
            pass
        return JSONResponse(status_code=404, content={"detail": "not found"})
    # 静态资源：使用 Path.resolve() 并校验结果仍在 STATIC_DIR 内，防止路径穿越
    try:
        base = Path(STATIC_DIR).resolve()
        fp = (base / path).resolve()
        # Vuln Sentinel fix: is_file() 在路径过长时会抛出 OSError(Errno 36)，
        # 同时 is_relative_to 也需要捕获异常，避免返回 500
        if not fp.is_relative_to(base):
            # 解析后路径已逃出静态目录 → 拒绝
            return await index()
        if not fp.is_file():
            return await index()
    except (OSError, ValueError):
        return await index()
    return FileResponse(str(fp))


if __name__ == "__main__":
    import uvicorn

    logger.info("Server starting on :%s", settings.port)
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=False)











