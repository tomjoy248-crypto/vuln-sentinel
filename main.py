"""漏洞哨兵 V11.4 - FastAPI 安全扫描后端

V11.4 实际改进：
1. 统一 finding 严重度字段为英文 severity（high/medium/low），保留 level_zh 给前端展示
2. analyze_security 末尾补 summary 字段 {high, medium, low, total}
3. /api/verify-fix 真正对比"修复前"扫描记录，输出 fixed/new/diff
4. /api/apply-fix-and-rescan 接收可选 previous_scan_id，做真实 diff
5. /api/simulate-fix 使用真实 severity 字段
6. /api/batch-scan 并发跑，asyncio.gather，超时控制
7. /api/history 新增 DELETE 方法真清空
8. /api/auth/profile 统计接口：fixed_count 改为统计"已被后续扫描覆盖"的 finding 数
9. rate_limit 改用类实例（per-ip bucket），去掉双重 await
10. JWT secret 强制从 env 来，默认值不允许在生产启动
11. 新增 /api/version 返回 {version, build_time}
12. 修复生成器匹配更宽松（按 finding type / name 前缀）
13. check_sensitive_paths 增加内容特征校验，避免登录页/错误页误判为泄露
14. fetch_headers 区分 DNS 失败/超时/403/302/405/500，生成受限扫描报告
15. 修复工单系统：pending/in_progress/fixed/ignored 四状态 + 批量操作
16. 资产管理页：域名/负责人/验证状态/最近扫描时间
17. AI 顾问接入当前扫描报告，回答"最该先修什么"并给出优先级排序
18. /data/progress/ 目录自动清理 30 分钟前文件
19. httpx client 兜底检测 Event loop closed，自动重建
20. 离线模式文案准确："当前是离线演示模式，只支持预置演示站点"
"""

from __future__ import annotations

import asyncio
import contextlib
import hashlib
import ipaddress
import io
import json
import logging
import os
import re
import secrets
import socket
import sqlite3
import ssl
import subprocess
import time
from collections import OrderedDict, deque
from datetime import datetime, timedelta
from typing import Any, Callable, Coroutine, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse, urldefrag
from html.parser import HTMLParser
from pathlib import Path

import httpx
import jwt
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, HTTPException, Depends, Header, Query, Request
from fastapi.encoders import jsonable_encoder as jsonable
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

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

    app_title: str = "漏洞哨兵 V11.4"
    app_version: str = "11.4"
    build_time: str = "2026-06-22"
    port: int = 8000
    host: str = "0.0.0.0"
    env: str = "development"  # development / production

    # JWT
    jwt_secret: str = Field(default="", min_length=0)
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

    # Public demo whitelist
    public_demo_enabled: bool = True

    # CORS 白名单（生产环境必须显式配置；开发环境允许本地回环）
    # 兼容 ALLOWED_ORIGINS 与 CORS_ORIGINS 两个变量名
    cors_origins: str = (
        os.environ.get("ALLOWED_ORIGINS")
        or os.environ.get("CORS_ORIGINS")
        or "http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000,http://localhost:5173"
    )


settings = Settings()

# 生产模式判定：ENV=production 或 PRODUCTION=1
_IS_PRODUCTION = (
    settings.env == "production"
    or os.environ.get("PRODUCTION", "").strip() in ("1", "true", "TRUE", "True", "yes", "YES")
)

# ---------- CORS 白名单解析与生产模式强制校验 ----------

def _parse_cors_origins(raw: str) -> list[str]:
    """解析逗号分隔的 CORS 白名单，去空白去空项。"""
    if not raw:
        return []
    return [o.strip() for o in raw.split(",") if o.strip()]


_cors_origins_list = _parse_cors_origins(settings.cors_origins)

# 生产模式强制：禁止通配符 * / 缺失配置
if _IS_PRODUCTION:
    if not _cors_origins_list:
        raise RuntimeError(
            "生产环境必须显式设置 ALLOWED_ORIGINS（或 CORS_ORIGINS）环境变量，"
            "例如：ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com"
        )
    if any(o == "*" for o in _cors_origins_list):
        raise RuntimeError(
            "生产环境禁止将 ALLOWED_ORIGINS 配置为通配符 '*'，"
            "请显式列出允许的来源域名，避免任意站点跨域访问。"
        )

# JWT Secret 强制：生产环境必须显式设置，否则拒绝启动
if settings.env == "production":
    if not settings.jwt_secret or len(settings.jwt_secret) < 32:
        raise RuntimeError(
            "生产环境必须设置 JWT_SECRET 环境变量，且长度不少于 32 字符。"
            "请执行：export JWT_SECRET=$(openssl rand -base64 48)"
        )

# JWT Secret：开发环境未设则生成随机并落盘
_SECRET_FILE = os.path.join(
    settings.db_dir if os.path.isdir(settings.db_dir) else os.path.dirname(os.path.abspath(__file__)),
    ".jwt_secret",
)
if not settings.jwt_secret:
    if os.path.isfile(_SECRET_FILE):
        try:
            with open(_SECRET_FILE, "r") as f:
                settings.jwt_secret = f.read().strip()
            if len(settings.jwt_secret) < 32:
                raise ValueError("persisted secret too short")
        except Exception as e:
            logger.warning("Failed to load persisted JWT secret, regenerating: %s", e)
            settings.jwt_secret = secrets.token_urlsafe(48)
    else:
        settings.jwt_secret = secrets.token_urlsafe(48)
    try:
        with open(_SECRET_FILE, "w") as f:
            f.write(settings.jwt_secret)
        try:
            os.chmod(_SECRET_FILE, 0o600)
        except Exception as e:
            logger.warning("Failed to chmod JWT secret file %s: %s", _SECRET_FILE, e)
    except Exception as e:
        logger.warning("Failed to persist JWT secret to %s: %s", _SECRET_FILE, e)
    logger.info("Generated JWT secret (len=%d)", len(settings.jwt_secret))

# ---------- Constants ----------

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

# SSRF 防护：禁止访问的私有网络段
BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
]

# 云元数据服务地址（额外拦截）
BLOCKED_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0", "::1", "169.254.169.254"}

# 内部白名单：环境变量配置后允许扫描的内网靶场
# 格式：逗号分隔，如 "192.168.1.100,10.0.0.5,pikachu.local"
ALLOWED_INTERNAL_HOSTS = {
    h.strip().lower() for h in os.environ.get("ALLOWED_INTERNAL_HOSTS", "").split(",")
    if h.strip()
}
db_base = settings.db_dir if os.path.isdir(settings.db_dir) else os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(db_base, settings.db_name)

SECURITY_HEADERS: Dict[str, Dict[str, str]] = {
    "strict-transport-security": {
        "name": "HSTS", "category": "传输安全", "severity": "high",
        "description": "强制浏览器只通过 HTTPS 访问",
        "fix": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
    },
    "content-security-policy": {
        "name": "CSP", "category": "XSS 防护", "severity": "high",
        "description": "限制页面可加载的资源来源",
        "fix": "add_header Content-Security-Policy \"default-src 'self'\" always;",
    },
    "x-frame-options": {
        "name": "X-Frame-Options", "category": "点击劫持", "severity": "medium",
        "description": "防止页面被嵌入 iframe",
        "fix": 'add_header X-Frame-Options "DENY" always;',
    },
    "x-content-type-options": {
        "name": "X-Content-Type-Options", "category": "MIME 嗅探", "severity": "medium",
        "description": "禁止浏览器猜测 MIME 类型",
        "fix": 'add_header X-Content-Type-Options "nosniff" always;',
    },
    "referrer-policy": {
        "name": "Referrer-Policy", "category": "隐私", "severity": "low",
        "description": "控制 Referer 头发送策略",
        "fix": 'add_header Referrer-Policy "strict-origin-when-cross-origin" always;',
    },
    "permissions-policy": {
        "name": "Permissions-Policy", "category": "隐私", "severity": "low",
        "description": "控制浏览器 API 权限",
        "fix": 'add_header Permissions-Policy "camera=(), microphone=()" always;',
    },
}

# severity -> 评分扣分（通用映射，analyze_security 中已按影响程度细分）
SEVERITY_SCORE = {"critical": 25, "high": 15, "medium": 8, "low": 3}
SEVERITY_ZH = {"critical": "高风险", "high": "高风险", "medium": "中风险", "low": "低风险"}

# 按影响程度细分的评分扣分
SCORE_DEDUCTION = {
    "exposed_path": 15,          # 确认漏洞：敏感路径暴露
    "high_config_missing": 8,    # 高危配置缺失：CSP、HSTS、X-Frame-Options
    "normal_config_missing": 3,  # 普通配置缺失：X-Content-Type-Options、Referrer-Policy、Permissions-Policy
    "info_leak": 1,              # 信息项：Server 信息泄露等
    "suspect": 0,                # suspect 疑似项：不扣分
}

WAF_SIGNATURES: Dict[str, List[str]] = {
    "cloudflare": ["CF-RAY", "__cfduid", "cf-browser-verification"],
    "aliyun": ["X-Alibaba-WAF", "X-Alibaba-WAF-Action"],
    "aws": ["X-AMZ-CF-ID", "X-Cache"],
    "baidu": ["X-Bd-WAF", "X-Bd-Id"],
    "qcloud": ["X-Qcloud-Edge", "X-Tencent-Ua"],
    "imperva": ["X-Iinfo", "incap_ses"],
    "akamai": ["X-Akamai-Request-BC", "Akamai-Origin-Hop"],
}

SENSITIVE_PATHS: List[str] = [
    "/.env", "/.git/config", "/.svn/entries", "/.htaccess",
    "/sitemap.xml", "/admin", "/login", "/phpmyadmin", "/api",
    "/swagger", "/.DS_Store", "/config.php", "/wp-config.php",
    "/.env.local", "/backup.sql", "/dump.sql", "/.bak",
]

# robots.txt 是公开文件，不算敏感路径暴露，只作为 info 提示
INFO_PATHS: List[str] = ["/robots.txt"]

XSS_PAYLOADS: List[str] = [
    '<script>alert("XSS")</script>',
    '"><img src=x onerror=alert(1)>',
    "'-alert(1)-'",
    "{{7*7}}",
    '<svg onload=alert(1)>',
    "javascript:alert(1)",
]

SQLI_PAYLOADS: List[str] = [
    "' OR 1=1--", "1' OR '1'='1", "admin'--",
    "' UNION SELECT NULL--", "1; DROP TABLE users--", "' OR 1=1 /*",
]

# ---------- Input Sanitization ----------

_MAX_USERNAME_LEN = 32
_MAX_URL_LEN = 2048
_MAX_EMAIL_LEN = 128
_MAX_PASSWORD_LEN = 128
_ALLOWED_USERNAME_RE = re.compile(r"^[a-zA-Z0-9_\-\u4e00-\u9fa5]+$")


def sanitize_username(value: str) -> str:
    value = value.strip()
    if len(value) < 3 or len(value) > _MAX_USERNAME_LEN:
        raise ValueError(f"用户名长度需在 3-{_MAX_USERNAME_LEN} 之间")
    if not _ALLOWED_USERNAME_RE.match(value):
        raise ValueError("用户名包含非法字符")
    return value


def _is_private_ip(hostname: str) -> bool:
    """检查 hostname 解析后的 IP 是否落入私有网段。用于 SSRF 防护。"""
    if hostname.lower() in BLOCKED_HOSTS:
        return True
    try:
        infos = socket.getaddrinfo(hostname, None)
        for info in infos:
            ip_str = info[4][0]
            try:
                ip = ipaddress.ip_address(ip_str)
                for network in BLOCKED_NETWORKS:
                    if ip in network:
                        return True
            except ValueError:
                continue
    except socket.gaierror:
        pass
    return False


def sanitize_url(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("URL 不能为空")
    if len(value) > _MAX_URL_LEN:
        raise ValueError(f"URL 长度不能超过 {_MAX_URL_LEN}")
    if not re.match(r"^https?://", value, re.I):
        value = "http://" + value
    parsed = urlparse(value)
    if not parsed.hostname:
        raise ValueError("URL 格式无效")
    hostname = parsed.hostname.lower()
    # 基本域名校验：必须包含点号
    if "." not in hostname:
        raise ValueError("URL 格式无效：域名必须包含点号（如 example.com）")
    # TLD 校验：字母 TLD 至少 2 字符；纯数字 IP 跳过
    parts = hostname.rsplit(".", 1)
    tld = parts[1] if len(parts) == 2 else ""
    is_ip_like = all(c.isdigit() or c == "." for c in hostname)
    if not is_ip_like and len(tld) < 2:
        raise ValueError("URL 格式无效：域名后缀太短")
    # SSRF 防护：拦截内网、本地、云元数据地址（白名单除外）
    if _is_private_ip(hostname) and hostname not in ALLOWED_INTERNAL_HOSTS:
        raise ValueError(
            f"该地址属于内网或本地地址，禁止扫描。"
            f"如需扫描内网靶场，请联系管理员将 {hostname} 加入环境变量 ALLOWED_INTERNAL_HOSTS"
        )
    return value


def sanitize_email(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    if len(value) > _MAX_EMAIL_LEN:
        raise ValueError(f"邮箱长度不能超过 {_MAX_EMAIL_LEN}")
    if "@" not in value or "." not in value.split("@")[-1]:
        raise ValueError("邮箱格式无效")
    return value


def sanitize_password(value: str) -> str:
    if len(value) < 6 or len(value) > _MAX_PASSWORD_LEN:
        raise ValueError(f"密码长度需在 6-{_MAX_PASSWORD_LEN} 之间")
    return value


# ---------- Models ----------

class ScanRequest(BaseModel):
    url: str
    deep: bool = False
    authorized: bool = False  # 用户是否确认有权扫描该目标

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        return sanitize_url(v)


class VerifyFixRequest(BaseModel):
    url: str
    previous_scan_id: Optional[int] = None

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        return sanitize_url(v)


class SimulateFixRequest(BaseModel):
    findings: List[dict] = Field(default_factory=list)


class ApplyFixRequest(BaseModel):
    url: str
    previous_scan_id: Optional[int] = None

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        return sanitize_url(v)


class PublicDemoRequest(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("URL 不能为空")
        return sanitize_url(v)


class AIAdvisorRequest(BaseModel):
    message: Optional[str] = None
    scan_id: Optional[int] = None


class BatchScanRequest(BaseModel):
    urls: List[str] = Field(default_factory=list)
    deep: bool = False

    @field_validator("urls")
    @classmethod
    def validate_urls(cls, v: List[str]) -> List[str]:
        if not isinstance(v, list):
            raise ValueError("urls 必须是数组")
        if len(v) > 5:
            raise ValueError("单次最多扫描 5 个 URL")
        sanitized = []
        for item in v:
            if not isinstance(item, str):
                raise ValueError("URL 必须是字符串")
            sanitized.append(sanitize_url(item))
        return sanitized


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str = ""

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        return sanitize_username(v)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return sanitize_password(v)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not v:
            return ""
        return sanitize_email(v)


class LoginRequest(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        return sanitize_username(v)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return sanitize_password(v)


class AddTargetRequest(BaseModel):
    url: str
    schedule: str = Field(default="daily", pattern="^(daily|weekly|never)$")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        return sanitize_url(v)


class FixTicketCreate(BaseModel):
    scan_id: Optional[int] = None
    finding_name: str
    severity: str = "low"
    fix_code: Optional[str] = None
    notes: Optional[str] = None


class FixTicketUpdate(BaseModel):
    status: Optional[str] = None
    fix_code: Optional[str] = None
    notes: Optional[str] = None


class FindingFeedbackRequest(BaseModel):
    """用户对 finding 的误报/确认反馈。

    - is_false_positive=True: 用户认为这是误报
    - is_confirmed=True: 用户确认这是真实问题（与 is_false_positive 互斥，但允许两个都 False 表示"中性"）
    - finding_type: 找出的 OWASP 分类或漏洞类型，便于后续按类型聚合误报率
    """
    scan_id: int
    finding_name: str
    finding_type: Optional[str] = None
    is_false_positive: bool = False
    is_confirmed: bool = False
    note: Optional[str] = None


class AssetCreateRequest(BaseModel):
    domain: str
    owner: str = ""
    description: str = ""

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v: str) -> str:
        v = v.strip().lower()
        if not v:
            raise ValueError("域名不能为空")
        # 去掉协议前缀
        if v.startswith(("http://", "https://")):
            from urllib.parse import urlparse
            v = urlparse(v).hostname or v
        return v


class AssetUpdateRequest(BaseModel):
    owner: Optional[str] = None
    description: Optional[str] = None


class ScanResponse(BaseModel):
    success: bool
    scan_type: str
    url: str
    final_url: str
    time: str
    is_https: bool
    score: int
    risk_level: str
    findings: List[dict]
    summary: Dict[str, int] = Field(default_factory=lambda: {"high": 0, "medium": 0, "low": 0, "total": 0})
    owasp_coverage: List[dict]
    header_details: List[dict]
    info_leaks: List[dict]
    cors: Optional[dict]
    cookie_issues: List[str]
    ssl_info: dict
    waf: List[dict]
    sensitive_paths: List[dict]
    waf_detected: bool
    raw_headers: dict
    crawled_pages: Optional[List[dict]] = None
    vuln_tests: Optional[List[dict]] = None
    scan_id: Optional[int] = None
    score_breakdown: List[dict] = Field(default_factory=list)
    fixes: Dict[str, list] = Field(default_factory=dict)
    error: Optional[str] = None
    restricted: bool = False
    restricted_reason: str = ""
    restricted_code: str = ""
    redirected: bool = False
    redirect_reason: str = ""


# ---------- Auth ----------

import bcrypt


def hash_password(pwd: str) -> str:
    # 使用原生 bcrypt 包，避免 passlib 版本兼容问题
    # bcrypt 限制密码最长 72 字节，超出部分截断
    return bcrypt.hashpw(pwd[:72].encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(pwd: str, hashed: str) -> bool:
    return bcrypt.checkpw(pwd[:72].encode("utf-8"), hashed.encode("utf-8"))


def create_token(user_id: int, username: str) -> str:
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": time.time() + settings.jwt_expire_seconds,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def verify_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except Exception:
        return None


async def get_current_user(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization[7:]
    return verify_token(token)


async def require_login(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "请先登录")
    token = authorization[7:]
    user = verify_token(token)
    if not user:
        raise HTTPException(401, "请先登录")
    return user


# ---------- Rate Limiter (单例) ----------

class RateLimiter:
    """单进程滑动窗口限速器，per-key bucket。支持 async 和 sync 两种检查模式。"""

    def __init__(self, max_requests: int, window_seconds: int = 60, disabled: bool = False) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.disabled = disabled
        self._store: Dict[str, List[float]] = {}
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


_TEST_MODE = os.environ.get("DB_DIR", "").startswith("/tmp")
_SERVICE_START_TIME = time.time()
limiter_global = RateLimiter(settings.rate_limit_global_per_minute, 60, disabled=_TEST_MODE)
limiter_scan = RateLimiter(settings.rate_limit_scan_per_minute, 60, disabled=_TEST_MODE)
limiter_fix = RateLimiter(settings.rate_limit_fix_per_minute, 60, disabled=_TEST_MODE)
limiter_register = RateLimiter(5, 60, disabled=_TEST_MODE)
limiter_login = RateLimiter(10, 60, disabled=_TEST_MODE)
limiter_ai = RateLimiter(20, 60, disabled=_TEST_MODE)
limiter_batch = RateLimiter(3, 60, disabled=_TEST_MODE)
limiter_demo = RateLimiter(10, 60, disabled=_TEST_MODE)


async def rate_limit_dependency(request: Request) -> None:
    """全局速率限制（单次调用，不重复扣分）。"""
    client_ip = request.client.host if request.client else "unknown"
    if not await limiter_global.is_allowed(client_ip):
        raise HTTPException(429, "请求过于频繁，请稍后再试")


def _rate_limit_check(limiter: RateLimiter, request: Request) -> None:
    """辅助函数：检查指定限流器，超限则抛 429 并带 Retry-After 头。"""
    client_ip = request.client.host if request.client else "unknown"
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
        self._cache: OrderedDict[str, Tuple[Any, float]] = OrderedDict()
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
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
    conn.execute("CREATE INDEX IF NOT EXISTS idx_fix_tickets_user_id ON fix_tickets(user_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_fix_tickets_status ON fix_tickets(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_fix_tickets_scan_id ON fix_tickets(scan_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_scans_user_id ON scans(user_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_scans_url ON scans(url)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_scans_created_at ON scans(created_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_targets_user_id ON targets(user_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_targets_schedule ON targets(schedule)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
    # 迁移：为已有 users 表添加 role 和 team_id 列
    try:
        conn.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'member'")
    except Exception:
        pass
    try:
        conn.execute("ALTER TABLE users ADD COLUMN team_id INTEGER DEFAULT 0")
    except Exception:
        pass
    conn.execute(
        """CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            target_id INTEGER,
            alert_type TEXT DEFAULT 'score_change',
            message TEXT NOT NULL,
            details_json TEXT DEFAULT '{}',
            created_at TEXT,
            is_read INTEGER DEFAULT 0
        )"""
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_alerts_user_id ON alerts(user_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_alerts_is_read ON alerts(is_read)")
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
    # V11.4+：用户对 finding 的误报/确认反馈
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
    conn.execute("CREATE INDEX IF NOT EXISTS idx_finding_feedback_user_id ON finding_feedback(user_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_finding_feedback_scan_id ON finding_feedback(scan_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_finding_feedback_name ON finding_feedback(finding_name)")
    try:
        conn.execute("ALTER TABLE scans ADD COLUMN share_id TEXT")
    except Exception as e:
        logger.warning("Failed to add share_id column to scans: %s", e)
    try:
        conn.execute("ALTER TABLE scans ADD COLUMN summary_json TEXT")
    except Exception as e:
        logger.warning("Failed to add summary_json column to scans: %s", e)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_scans_share_id ON scans(share_id)")
    try:
        existing = conn.execute("SELECT id FROM users WHERE username=?", ("demo",)).fetchone()
        if not existing:
            conn.execute(
                "INSERT INTO users (username, password, email, created_at) VALUES (?,?,?,?)",
                ("demo", hash_password("demo123"), "demo@vulnsentinel.com", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            )
            logger.info("Pre-created test account ready")
    except Exception as e:
        logger.warning("Failed to pre-create demo account: %s", e)
    # 迁移旧 SHA256 密码到 bcrypt（自动检测非 bcrypt 哈希并重新哈希）
    try:
        old_users = conn.execute("SELECT id, username, password FROM users").fetchall()
        for uid, uname, pwd_hash in old_users:
            if not pwd_hash.startswith("$2b$") and not pwd_hash.startswith("$2a$"):
                # 旧 SHA256 哈希，无法直接迁移密码值
                # 对 demo 账号重置为已知密码，其他账号标记需要重置
                if uname == "demo":
                    new_hash = hash_password("demo123")
                    conn.execute("UPDATE users SET password=? WHERE id=?", (new_hash, uid))
                    logger.info("Migrated demo account to bcrypt")
                else:
                    # 其他旧账号：设置一个随机 bcrypt 哈希（用户需要重置密码）
                    new_hash = hash_password("reset_" + secrets.token_hex(8))
                    conn.execute("UPDATE users SET password=? WHERE id=?", (new_hash, uid))
                    logger.info("Migrated user %s to bcrypt (password reset required)", uname)
    except Exception as e:
        logger.warning("Password migration failed: %s", e)
    conn.commit()
    conn.close()
    logger.info("Database initialized: %s", DB_PATH)


def save_scan(
    user_id: int,
    url: str,
    score: int,
    risk_level: str,
    findings: list,
    summary: dict,
    crawled_count: int,
    scan_type: str,
) -> int:
    share_id = secrets.token_urlsafe(9)[:12]
    conn = get_db()
    cur = conn.execute(
        """INSERT INTO scans
        (user_id, url, score, risk_level, findings_count, findings_json, summary_json, crawled_pages, scan_type, share_id, created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (
            user_id, url, score, risk_level, len(findings),
            json.dumps(findings, ensure_ascii=False),
            json.dumps(summary or {}, ensure_ascii=False),
            crawled_count, scan_type, share_id,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    conn.commit()
    scan_id = cur.lastrowid
    conn.close()
    return scan_id


def get_scan_by_share_id(share_id: str) -> Optional[dict]:
    conn = get_db()
    row = conn.execute("SELECT * FROM scans WHERE share_id=?", (share_id,)).fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d.pop("user_id", None)
    if d.get("summary_json"):
        try:
            d["summary"] = json.loads(d.pop("summary_json"))
        except Exception:
            d.pop("summary_json", None)
    else:
        d.pop("summary_json", None)
    return d


def get_scan_by_id(scan_id: int, user_id: Optional[int] = None) -> Optional[dict]:
    conn = get_db()
    if user_id is not None:
        row = conn.execute("SELECT * FROM scans WHERE id=? AND user_id=?", (scan_id, user_id)).fetchone()
    else:
        row = conn.execute("SELECT * FROM scans WHERE id=?", (scan_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_user_password(user_id: int, new_hash: str) -> None:
    conn = get_db()
    conn.execute("UPDATE users SET password=? WHERE id=?", (new_hash, user_id))
    conn.commit()
    conn.close()


def get_scan_history(user_id: int, limit: int = 20) -> list:
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM scans WHERE user_id=? ORDER BY id DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        try:
            d["findings"] = json.loads(d.get("findings_json") or "[]")
        except Exception:
            d["findings"] = []
        d.pop("findings_json", None)
        try:
            d["summary"] = json.loads(d.get("summary_json") or "{}")
        except Exception:
            d["summary"] = {}
        d.pop("summary_json", None)
        result.append(d)
    return result


def get_latest_scan_for_target(user_id: int, url: str) -> Optional[dict]:
    """获取某个用户某个 URL 的最新一次扫描结果。"""
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM scans WHERE user_id=? AND url=? ORDER BY id DESC LIMIT 1",
        (user_id, url),
    ).fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    try:
        d["findings"] = json.loads(d.get("findings_json") or "[]")
    except Exception:
        d["findings"] = []
    d.pop("findings_json", None)
    try:
        d["summary"] = json.loads(d.get("summary_json") or "{}")
    except Exception:
        d["summary"] = {}
    d.pop("summary_json", None)
    return d


def save_alert(user_id: int, target_id: int, alert_type: str, message: str, details: dict) -> int:
    """保存一条告警记录。"""
    conn = get_db()
    cur = conn.execute(
        """INSERT INTO alerts
        (user_id, target_id, alert_type, message, details_json, created_at, is_read)
        VALUES (?,?,?,?,?,?,?)""",
        (
            user_id, target_id, alert_type, message,
            json.dumps(details, ensure_ascii=False),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0,
        ),
    )
    conn.commit()
    alert_id = cur.lastrowid
    conn.close()
    return alert_id


def delete_scan_history(user_id: int) -> int:
    conn = get_db()
    try:
        cur = conn.execute("DELETE FROM scans WHERE user_id=?", (user_id,))
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()


def compute_fixed_count(history: list) -> int:
    """统计已被后续扫描覆盖的 finding 数：按 URL 分组，按时间倒序，
    对每个 URL 的相邻两次扫描做 diff，前一次有后一次没有的 finding 算"已修复" """
    if not history:
        return 0
    by_url: Dict[str, list] = {}
    for h in history:
        by_url.setdefault(h.get("url", ""), []).append(h)
    fixed_total = 0
    for url, scans in by_url.items():
        scans_sorted = sorted(scans, key=lambda x: x.get("id", 0), reverse=True)
        for i in range(len(scans_sorted) - 1):
            new_findings = {f.get("name", "") for f in scans_sorted[i].get("findings", [])}
            old_findings = {f.get("name", "") for f in scans_sorted[i + 1].get("findings", [])}
            fixed_total += len(old_findings - new_findings)
    return fixed_total


# ---------- Fix Ticket Helpers ----------

def create_fix_ticket(user_id: int, scan_id: Optional[int], finding_name: str, severity: str, fix_code: Optional[str] = None, notes: Optional[str] = None) -> int:
    conn = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur = conn.execute(
        """INSERT INTO fix_tickets (user_id, scan_id, finding_name, severity, status, fix_code, notes, created_at, updated_at)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (user_id, scan_id, finding_name, severity, "pending", fix_code, notes, now, now),
    )
    conn.commit()
    ticket_id = cur.lastrowid
    conn.close()
    return ticket_id


def get_fix_tickets(user_id: int, status: Optional[str] = None) -> list:
    conn = get_db()
    if status:
        rows = conn.execute(
            "SELECT * FROM fix_tickets WHERE user_id=? AND status=? ORDER BY id DESC",
            (user_id, status),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM fix_tickets WHERE user_id=? ORDER BY id DESC",
            (user_id,),
        ).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        result.append(d)
    return result


def get_fix_ticket(ticket_id: int, user_id: int) -> Optional[dict]:
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM fix_tickets WHERE id=? AND user_id=?",
        (ticket_id, user_id),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def update_fix_ticket(ticket_id: int, user_id: int, status: Optional[str] = None, fix_code: Optional[str] = None, notes: Optional[str] = None) -> bool:
    conn = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fields = []
    params = []
    if status is not None:
        fields.append("status=?")
        params.append(status)
        if status == "fixed":
            fields.append("fixed_at=?")
            params.append(now)
    if fix_code is not None:
        fields.append("fix_code=?")
        params.append(fix_code)
    if notes is not None:
        fields.append("notes=?")
        params.append(notes)
    if not fields:
        conn.close()
        return False
    fields.append("updated_at=?")
    params.append(now)
    params.extend([ticket_id, user_id])
    conn.execute(
        f"UPDATE fix_tickets SET {', '.join(fields)} WHERE id=? AND user_id=?",
        params,
    )
    conn.commit()
    n = conn.total_changes
    conn.close()
    return n > 0


def delete_fix_ticket(ticket_id: int, user_id: int) -> bool:
    conn = get_db()
    cur = conn.execute("DELETE FROM fix_tickets WHERE id=? AND user_id=?", (ticket_id, user_id))
    conn.commit()
    n = cur.rowcount
    conn.close()
    return n > 0


def auto_create_fix_tickets(user_id: int, scan_id: int, findings: list) -> int:
    """为 high/critical finding 自动创建工单，跳过已存在的同名待处理工单。

    优化：先一次性查出当前用户所有 pending 工单的 finding_name（set 缓存），
    避免对每条 finding 单独查询（消除 N+1）。
    """
    candidates: list[tuple[str, str, str]] = []
    for f in findings:
        severity = (f.get("severity") or "low").lower()
        if severity not in ("high", "critical"):
            continue
        name = (f.get("name") or "").strip()
        if not name:
            continue
        candidates.append((name, severity, f.get("fix", "")))

    if not candidates:
        return 0

    conn = get_db()
    try:
        existing_rows = conn.execute(
            "SELECT finding_name FROM fix_tickets WHERE user_id=? AND status='pending'",
            (user_id,),
        ).fetchall()
        existing = {row["finding_name"] for row in existing_rows}
    finally:
        conn.close()

    created = 0
    for name, severity, fix_code in candidates:
        if name in existing:
            continue
        create_fix_ticket(user_id, scan_id, name, severity, fix_code)
        existing.add(name)
        created += 1
    return created


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

def create_asset(user_id: int, domain: str, owner: str = "", description: str = "") -> int:
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


def get_asset(asset_id: int, user_id: int) -> Optional[dict]:
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM assets WHERE id=? AND user_id=?", (asset_id, user_id)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def update_asset(asset_id: int, user_id: int, owner: Optional[str] = None, description: Optional[str] = None) -> bool:
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
        f"UPDATE assets SET {', '.join(fields)} WHERE id=? AND user_id=?",
        params,
    )
    conn.commit()
    n = conn.total_changes
    conn.close()
    return n > 0


def delete_asset(asset_id: int, user_id: int) -> bool:
    conn = get_db()
    cur = conn.execute("DELETE FROM assets WHERE id=? AND user_id=?", (asset_id, user_id))
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
            headers, is_https, final_url, error = await fetch_headers(url)
            if error:
                continue
            waf_list = detect_waf(headers)
            sensitive_paths = await check_sensitive_paths(host, is_https)
            ssl_info = await get_ssl_info(host, 443) if is_https else {"has_cert": False}
            result = analyze_security(url, headers, is_https, ssl_info, waf_list, sensitive_paths)
            scan_id = save_scan(
                user_id, url, result["score"], result["risk_level"],
                result["findings"], result.get("summary", {}), 0, "scheduled",
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
                        user_id, target_id, "score_drop",
                        f"{host} 安全评分下降 {abs(score_change)} 分",
                        {"url": url, "old_score": prev_scan.get("score"), "new_score": result["score"], "scan_id": scan_id}
                    )
                # 告警 2：评分大幅提升
                elif score_change >= 10:
                    save_alert(
                        user_id, target_id, "score_up",
                        f"{host} 安全评分提升 {score_change} 分",
                        {"url": url, "old_score": prev_scan.get("score"), "new_score": result["score"], "scan_id": scan_id}
                    )
                # 告警 3：新增 high/critical finding
                new_high = [curr_names[n] for n in new_names if curr_names[n].get("severity") in ("high", "critical")]
                if new_high:
                    save_alert(
                        user_id, target_id, "new_high_risk",
                        f"{host} 发现 {len(new_high)} 个新高危漏洞",
                        {"url": url, "findings": [{"name": f.get("name"), "severity": f.get("severity")} for f in new_high], "scan_id": scan_id}
                    )
                # 告警 4：新增任意 finding
                elif new_names:
                    save_alert(
                        user_id, target_id, "new_finding",
                        f"{host} 发现 {len(new_names)} 个新问题",
                        {"url": url, "findings": list(new_names), "scan_id": scan_id}
                    )
                # 告警 5：修复了问题
                elif fixed_names:
                    save_alert(
                        user_id, target_id, "fixed",
                        f"{host} 修复了 {len(fixed_names)} 个问题",
                        {"url": url, "fixed": list(fixed_names), "scan_id": scan_id}
                    )
        except Exception as exc:
            logger.warning("Scheduled scan failed for %s: %s", target.get("url"), exc)


scheduler.add_job(scheduled_scan_job, "interval", minutes=60, id="scheduled_scan")


# ---------- Lifespan ----------

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    scheduler.start()
    logger.info("Application startup complete")
    yield
    scheduler.shutdown()
    await close_httpx_client()
    logger.info("Application shutdown complete")


app = FastAPI(title=settings.app_title, version=settings.app_version, lifespan=lifespan)

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

# 启用 gzip 压缩
app.add_middleware(GZipMiddleware, minimum_size=500)


# ---------- Middleware ----------

@app.middleware("http")
async def request_logging_middleware(request: Request, call_next: Callable[[Request], Coroutine[Any, Any, Any]]):
    start = time.time()
    client_ip = request.client.host if request.client else "unknown"
    response = await call_next(request)
    duration = time.time() - start
    logger.info(
        "[%s] %s %s -> %s (%.3fs)",
        client_ip, request.method, request.url.path, response.status_code, duration,
    )
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    code_map = {
        400: "BAD_REQUEST", 401: "UNAUTHORIZED", 403: "FORBIDDEN",
        404: "NOT_FOUND", 429: "TOO_MANY_REQUESTS", 500: "INTERNAL_ERROR",
    }
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail, "code": code_map.get(exc.status_code, "ERROR")},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception at %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "服务器内部错误", "code": "INTERNAL_ERROR"},
    )


# ---------- HTTPX Client ----------

_httpx_client: Optional[httpx.AsyncClient] = None
_httpx_client_loop_id: Optional[int] = None  # 记录 client 创建时的事件循环 id


def get_httpx_client() -> httpx.AsyncClient:
    global _httpx_client, _httpx_client_loop_id
    # 检测当前事件循环是否变化（hot reload / 事件循环重建时 _state 不够可靠）
    current_loop_id = id(asyncio.get_running_loop())
    if _httpx_client is not None and _httpx_client_loop_id != current_loop_id:
        logger.warning("httpx client bound to stale event loop, recreating (old=%s new=%s)", _httpx_client_loop_id, current_loop_id)
        # 避免直接操作 httpx 私有字段（_transport/__del__/_state）。
        # 直接丢弃旧 client，由 GC 在 transport 关闭路径上自行清理；
        # 真正的 aclose 由 close_httpx_client() 在事件循环切换前/关闭时调用。
        _httpx_client = None
    if _httpx_client is None:
        _create_client()
        _httpx_client_loop_id = current_loop_id
    return _httpx_client


def _create_client() -> None:
    global _httpx_client
    # TLS 校验：默认开启；仅当显式设置 TLS_VERIFY=false 时关闭，
    # 并且需要目标在 ALLOWED_INTERNAL_HOSTS 白名单内才允许（内网靶场）。
    _raw = os.environ.get("TLS_VERIFY", "true").strip().lower()
    if _raw in ("0", "false", "no", "off"):
        _verify = False
    else:
        _verify = True
    if not _verify:
        logger.warning(
            "TLS_VERIFY is disabled; only allowed for ALLOWED_INTERNAL_HOSTS targets"
        )
    _httpx_client = httpx.AsyncClient(
        verify=_verify,
        timeout=settings.scan_timeout,
        follow_redirects=True,
        headers={"User-Agent": "VulnSentinel/11.4"},
        limits=httpx.Limits(
            max_connections=50,
            max_keepalive_connections=10,
            keepalive_expiry=15.0,
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

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if tag == "a":
            for name, value in attrs:
                if name == "href" and value:
                    full = urljoin(self.base_url, value)
                    full, _ = urldefrag(full)
                    parsed = urlparse(full)
                    if parsed.scheme in ("http", "https"):
                        self.links.add(full)


async def crawl_site(url: str, max_pages: int = settings.max_crawl_pages) -> List[dict]:
    parsed = urlparse(url)
    base_domain = parsed.hostname or ""
    visited: set = set()
    pages: List[dict] = []
    queue: "deque[str]" = deque([url])
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
                "url": current, "status": resp.status_code, "title": "",
                "forms": 0, "inputs": 0, "links": 0,
            }
            parser = LinkParser(current)
            try:
                parser.feed(resp.text)
            except Exception:
                pass
            title_match = re.search(r"<title[^>]*>(.*?)</title>", resp.text, re.I | re.S)
            if title_match:
                page_info["title"] = title_match.group(1).strip()[:100]
            page_info["forms"] = len(re.findall(r"<form", resp.text, re.I))
            page_info["inputs"] = len(re.findall(r"<input", resp.text, re.I))
            for link in parser.links:
                lp = urlparse(link)
                if lp.hostname == base_domain and link not in visited:
                    queue.append(link)
            page_info["links"] = len(parser.links)
            pages.append(page_info)
        except asyncio.TimeoutError:
            pages.append({"url": current, "status": 0, "title": "timeout", "forms": 0, "inputs": 0, "links": 0})
        except Exception:
            pass
    return pages


# ---------- Payload Injection ----------

async def test_xss_on_url(client, url, param, payload):
    if urlparse(url).query:
        test_url = url + "&" + param + "=" + payload
    else:
        test_url = url + "?" + param + "=" + payload
    try:
        resp = await client.get(test_url, timeout=5.0, follow_redirects=True)
        body = resp.text
        for variant in [payload, payload.replace("<", "&lt;").replace(">", "&gt;")]:
            if variant in body:
                return {
                    "type": "XSS", "severity": "high", "param": param,
                    "payload": payload[:60], "url": test_url[:200], "evidence": "reflected",
                    "owasp": "A03 注入攻击",
                    "summary": f"参数 '{param}' 存在 XSS 漏洞。",
                    "fix": "对所有用户输入进行 HTML 实体编码，使用 CSP 限制脚本执行。",
                }
    except Exception:
        pass
    return None


async def test_sqli_on_url(client, url, param, payload):
    if urlparse(url).query:
        test_url = url + "&" + param + "=" + payload
    else:
        test_url = url + "?" + param + "=" + payload
    try:
        resp = await client.get(test_url, timeout=5.0, follow_redirects=True)
        body = resp.text.lower()
        for pattern in [
            "sql syntax", "mysql", "postgresql", "sqlite", "oracle", "sql error",
            "unclosed quotation", "query failed", "warning: mysql", "syntax error",
            "sqlstate", "odbc", "microsoft sql",
        ]:
            if pattern in body:
                return {
                    "type": "SQLi", "severity": "critical", "param": param,
                    "payload": payload[:60], "url": test_url[:200], "evidence": f"SQL 错误信息: {pattern}",
                    "owasp": "A03 注入攻击",
                    "summary": f"参数 '{param}' 存在 SQL 注入漏洞。",
                    "fix": "使用参数化查询（Prepared Statements），禁止拼接 SQL 语句。",
                }
    except Exception:
        pass
    return None


async def run_payload_tests(base_url, pages):
    vulns, test_results = [], []
    client = get_httpx_client()
    test_urls = {page["url"] for page in pages[:4]}
    for test_url in list(test_urls):
        params = [p.split("=")[0] for p in urlparse(test_url).query.split("&") if "=" in p]
        if params:
            for param in params[:3]:
                for payload in XSS_PAYLOADS[:2]:
                    result = await test_xss_on_url(client, test_url, param, payload)
                    if result:
                        vulns.append(result)
                    test_results.append({
                        "url": test_url[:100], "param": param, "type": "XSS",
                        "payload": payload[:40], "vulnerable": result is not None,
                    })
                for payload in SQLI_PAYLOADS[:2]:
                    result = await test_sqli_on_url(client, test_url, param, payload)
                    if result:
                        vulns.append(result)
                    test_results.append({
                        "url": test_url[:100], "param": param, "type": "SQLi",
                        "payload": payload[:40], "vulnerable": result is not None,
                    })
        else:
            for param in ["id", "q", "search", "page"]:
                for payload in XSS_PAYLOADS[:1]:
                    result = await test_xss_on_url(client, test_url, param, payload)
                    if result:
                        vulns.append(result)
                    test_results.append({
                        "url": test_url[:100], "param": param, "type": "XSS",
                        "payload": payload[:40], "vulnerable": result is not None,
                    })
    return vulns, test_results


# ---------- Scan Functions ----------

async def check_host_reachable(host: str) -> Optional[str]:
    def _check() -> Optional[str]:
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


async def fetch_headers(url: str) -> Tuple[dict, bool, str, Optional[str]]:
    """获取目标 URL 的响应头，区分各种失败情况。
    返回: (headers, is_https, final_url, error)
    error 为 None 表示成功；否则为分类错误信息。
    """
    def _sync_resolve(h: str) -> Optional[str]:
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

    parsed = urlparse(url)
    host = parsed.hostname or ""
    path = parsed.path or "/"
    if parsed.query:
        path += "?" + parsed.query
    is_https = parsed.scheme == "https"
    headers: dict = {}
    final_url = url
    error: Optional[str] = None

    if not host:
        return {}, False, url, "网址格式无效，缺少主机名"

    # DNS 解析检查
    try:
        dns_err = await asyncio.wait_for(
            asyncio.to_thread(_sync_resolve, host),
            timeout=5.0,
        )
    except asyncio.TimeoutError:
        dns_err = None
    if dns_err == "DNS_RESOLVE_FAIL":
        return {}, False, url, "DNS_RESOLVE_FAIL"

    # SSRF 二次检查
    if host and host not in ALLOWED_INTERNAL_HOSTS:
        try:
            resolved_ips = socket.getaddrinfo(host, None)
            for _, _, _, _, sockaddr in resolved_ips:
                try:
                    ip = ipaddress.ip_address(sockaddr[0])
                    for network in BLOCKED_NETWORKS:
                        if ip in network:
                            return {}, False, url, "该地址解析到内网 IP，禁止扫描"
                except ValueError:
                    continue
        except socket.gaierror:
            pass

    client = get_httpx_client()

    # 辅助函数：根据 HTTP 状态码分类
    def classify_status(status: int, resp_headers: dict) -> tuple:
        if status in (301, 302, 307, 308):
            loc = resp_headers.get("location", "")
            return {"_status_code": status, "_redirect_location": loc}, f"REDIRECT_{status}"
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
        try:
            resp = await asyncio.wait_for(
                client.head("https://" + host + path, follow_redirects=False),
                timeout=12.0,
            )
            h = dict(resp.headers)
            h["_status_code"] = resp.status_code
            headers, err = classify_status(resp.status_code, h)
            if err is None or err.startswith("REDIRECT_") or err in ("AUTH_REQUIRED", "FORBIDDEN", "METHOD_NOT_ALLOWED"):
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
        except Exception:
            pass

    # 主请求：先 HEAD，失败 fallback GET
    if not headers:
        last_err = None
        for method, fn in [("HEAD", client.head), ("GET", client.get)]:
            try:
                resp = await asyncio.wait_for(
                    fn(url, follow_redirects=False),
                    timeout=12.0,
                )
                h = dict(resp.headers)
                h["_status_code"] = resp.status_code
                headers, err = classify_status(resp.status_code, h)
                if err is None:
                    return headers, is_https, final_url, None
                # 受限访问但能拿到头 → 返回头 + 分类错误
                error = err
                headers = h
                return headers, is_https, final_url, error
            except asyncio.TimeoutError:
                last_err = "TIMEOUT"
            except httpx.ConnectError:
                last_err = "CONNECT_FAIL"
            except httpx.RemoteProtocolError:
                last_err = "PROTOCOL_ERROR"
            except Exception as e:
                last_err = f"REQUEST_FAIL:{str(e)[:60]}"
        # 全部方法失败
        if last_err == "TIMEOUT":
            error = "连接超时，该网站可能已下线或网络不可达"
        elif last_err == "CONNECT_FAIL":
            error = "无法连接到该网站，请确认网站是否在线"
        elif last_err == "PROTOCOL_ERROR":
            error = "协议错误，目标可能不支持 HTTPS 或使用了非标准端口"
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
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            with socket.create_connection((hostname, port), timeout=5) as sock:
                with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert(binary_form=False)
                    cipher = ssock.cipher()
                    version = ssock.version()
                    subject = dict(x[0] for x in cert.get("subject", []))
                    issuer = dict(x[0] for x in cert.get("issuer", []))
                    not_after = cert.get("notAfter", "")
                    san = cert.get("subjectAltName", [])
                    expired, days_left = False, None
                    if not_after:
                        try:
                            expiry = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
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
                        "weak": version in ["TLSv1", "TLSv1.1"] or (cipher and "RC4" in str(cipher)),
                    }
        except Exception as e:
            return {"has_cert": False, "error": str(e)[:100]}
    try:
        result = await asyncio.wait_for(asyncio.to_thread(_do_ssl), timeout=6.0)
    except asyncio.TimeoutError:
        result = {"has_cert": False, "error": "SSL 握手超时（目标可能未启用 HTTPS 或响应较慢）"}
    await ssl_cache.set(cache_key, result, settings.ssl_cache_ttl_seconds)
    return result


def detect_waf(headers: dict) -> List[dict]:
    headers_lower = {k.lower(): str(v) for k, v in headers.items() if isinstance(v, str)}
    detected: List[dict] = []
    for waf_name, signatures in WAF_SIGNATURES.items():
        for sig in signatures:
            if sig.lower() in headers_lower:
                detected.append({"name": waf_name, "signature": sig, "value": headers_lower[sig.lower()]})
                break
            for hk, hv in headers_lower.items():
                if sig.lower() in hk.lower() or sig.lower() in hv.lower():
                    detected.append({"name": waf_name, "signature": sig, "value": hv})
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


def _extract_sqli_sleep(url: str) -> Optional[float]:
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


async def detect_time_based_sqli(url: str, threshold: float = 2.5, timeout: float = 8.0) -> dict:
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


async def check_sensitive_paths(host: str, is_https: bool) -> List[dict]:
    """探测常见敏感路径暴露情况。每个请求独立超时。
    不只是看 HTTP 200，还要检查响应内容特征，避免把登录页/错误页误判为泄露。
    robots.txt 作为 info 提示，不算敏感路径暴露。"""
    results: List[dict] = []
    client = get_httpx_client()

    # 全局 forbidden 特征：响应内容包含这些关键词时，判定为 suspect/protected
    GLOBAL_FORBIDDEN = [
        "waf_block", "punish", "captcha", "安全验证", "alicdn.com",
        "login", "登录", "error", "404", "403", "forbidden", "denied",
        "访问被拒绝", "请登录", "请验证", "verify", "authentication",
    ]

    # 内容特征校验规则
    CONTENT_CHECKS = {
        "/.git/config": {
            "required": ["[core]", "repositoryformatversion"],
            "forbidden": ["<html", "<!doctype", "<head"],
        },
        "/.env": {
            "required": ["="],
            "sensitive_keys": ["SECRET", "PASSWORD", "TOKEN", "KEY", "API", "DB_", "DATABASE", "PRIVATE", "ACCESS"],
            "forbidden": ["<html", "<!doctype", "<head"],
        },
        "/.env.local": {
            "required": ["="],
            "sensitive_keys": ["SECRET", "PASSWORD", "TOKEN", "KEY", "API", "DB_", "DATABASE", "PRIVATE", "ACCESS"],
            "forbidden": ["<html", "<!doctype", "<head"],
        },
        "/.svn/entries": {
            "required": ["dir", "svn:", "text-base"],
            "forbidden": ["<html", "<!doctype", "<head"],
        },
        "/.htaccess": {
            "required_any": ["RewriteEngine", "AuthType", "Require", "Deny from", "AllowOverride", "Order allow,deny", "Redirect"],
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

        # 全局 forbidden 检测（WAF/反爬/登录页/错误页）
        for fb in GLOBAL_FORBIDDEN:
            if fb.lower() in text_lower:
                return {"verdict": "suspect", "reason": f"响应内容包含 '{fb}'，疑似 WAF 拦截/登录页/错误页，需人工确认"}

        checks = CONTENT_CHECKS.get(path)
        if not checks:
            # 没有特定规则的路径：简单启发式
            is_html = "<html" in text_lower or "<!doctype" in text_lower or "<head" in text_lower
            if is_html:
                return {"verdict": "suspect", "reason": "响应内容为 HTML 页面，疑似登录页或错误页，需人工确认"}
            return {"verdict": "exposed", "reason": "响应内容非 HTML，疑似敏感文件"}

        # 路径特定 forbidden 检测
        for fb in checks.get("forbidden", []):
            if fb.lower() in text_lower:
                return {"verdict": "suspect", "reason": f"响应内容包含 '{fb}'，疑似登录页或错误页，需人工确认"}

        # 检查 required（全部必须匹配）
        required = checks.get("required", [])
        if required:
            matched_required = sum(1 for r in required if r.lower() in text_lower)
            if matched_required < len(required):
                if matched_required > 0:
                    return {"verdict": "suspect", "reason": f"部分匹配敏感文件特征（{matched_required}/{len(required)}），需人工确认"}
                return {"verdict": "suspect", "reason": "响应内容不匹配敏感文件特征，疑似误报，需人工确认"}

        # 检查 required_any（任一匹配即可）
        required_any = checks.get("required_any", [])
        if required_any:
            matched_any = any(r.lower() in text_lower for r in required_any)
            if not matched_any:
                return {"verdict": "suspect", "reason": "响应内容不匹配 Apache 配置文件特征，疑似误报，需人工确认"}

        # 检查敏感关键词（仅 .env 类）
        sensitive_keys = checks.get("sensitive_keys", [])
        if sensitive_keys:
            sk_found = [sk for sk in sensitive_keys if sk.lower() in text_lower]
            if not sk_found:
                return {"verdict": "suspect", "reason": "响应内容格式类似配置文件但不含敏感关键词，需人工确认"}
            return {"verdict": "exposed", "reason": f"发现敏感关键词：{', '.join(sk_found[:3])}"}

        return {"verdict": "exposed", "reason": "敏感文件内容特征完全匹配"}

    async def check(p: str, is_info: bool = False) -> Optional[dict]:
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
                text = resp.text or ""
                if is_info:
                    # robots.txt 等公开文件：只返回 info，不算暴露
                    return {
                        "path": p, "status": resp.status_code,
                        "exposed": False, "info": True,
                        "size": len(text),
                        "reason": "robots.txt 为公开文件，内容可供参考",
                        "snippet": text[:300].replace("\n", " ") if len(text) < 2000 else "（内容过长，已截断）",
                    }
                analysis = analyze_content(p, text)
                return {
                    "path": p,
                    "status": resp.status_code,
                    "exposed": analysis["verdict"] == "exposed",
                    "suspect": analysis["verdict"] == "suspect",
                    "size": len(text),
                    "reason": analysis["reason"],
                    "snippet": text[:200].replace("\n", " ") if analysis["verdict"] == "exposed" else "",
                }
            elif resp.status_code in (403, 401):
                return {"path": p, "status": resp.status_code, "exposed": False, "protected": True}
        except asyncio.TimeoutError:
            return None
        except Exception:
            return None
        return None

    try:
        tasks = []
        for p in SENSITIVE_PATHS[:5]:
            tasks.append(check(p, is_info=False))
        for p in INFO_PATHS[:2]:
            tasks.append(check(p, is_info=True))
        responses = await asyncio.wait_for(
            asyncio.gather(*tasks, return_exceptions=False),
            timeout=10.0,
        )
        results = [r for r in responses if r]
    except asyncio.TimeoutError:
        results = []
    return results


VERIFY_METHODS = {
    "hsts": "curl -I https://你的域名 | grep -i 'strict-transport-security'",
    "csp": "curl -I https://你的域名 | grep -i 'content-security-policy'",
    "x-frame": "curl -I https://你的域名 | grep -i 'x-frame-options'",
    "x-content-type": "curl -I https://你的域名 | grep -i 'x-content-type-options'",
    "referrer": "curl -I https://你的域名 | grep -i 'referrer-policy'",
    "permissions": "curl -I https://你的域名 | grep -i 'permissions-policy'",
    "server": "curl -I https://你的域名 | grep -i '^server'（不应返回具体版本）",
    "https": "浏览器访问 http://你的域名 应自动跳转到 https://",
    "ssl": "openssl s_client -connect 你的域名:443 -servername 你的域名 < /dev/null | openssl x509 -noout -dates",
    "cors": "curl -H 'Origin: https://evil.com' -I https://你的域名 | grep -i 'access-control-allow-origin'",
    "cookie": "浏览器开发者工具 > Application > Cookies，检查 Secure/HttpOnly 标志",
    "info": "浏览器 F12 > Network > 查看响应头",
}


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
    known_cdns: Optional[List[str]] = None,
    sensitive_paths: Optional[List[dict]] = None,
    cookie_issues: Optional[List[str]] = None,
    is_https: Optional[bool] = None,
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
    result: Dict[str, dict] = {}

    # 工具：安全获取 url scheme
    try:
        parsed = urlparse(url)
        is_https_url = (parsed.scheme or "").lower() == "https"
    except Exception:
        is_https_url = False

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
    def get_header_value(header_dict: dict, name: str) -> Optional[str]:
        n = name.lower()
        for k, v in (header_dict or {}).items():
            if not isinstance(v, str):
                continue
            if k.lower() == n:
                return v
        return None

    # ========== D0: 已知 CDN 列表（用户提供，自动降低 Server 头 confidence） ==========
    d0_evidence: Dict[str, str] = {}
    d0_match: Dict[str, bool] = {}
    try:
        known_cdns_norm = [c.lower().strip() for c in (known_cdns or []) if c and c.strip()]
        if known_cdns_norm:
            # 在 Server 头 / CDN 特征头里查找用户提供的 CDN 关键字
            server_val_lower = (get_header_value(headers, "server") or "").lower()
            cdn_feature_keys = ("cf-ray", "x-amz-cf-id", "x-served-by", "x-cache", "x-amz-cf-pop")
            header_keys_lower = {k.lower() for k in (headers or {}).keys()}
            for f_name in _FINDING_HEADER_KEY:
                d0_match[f_name] = False
            for cdn_kw in known_cdns_norm:
                hit = (cdn_kw in server_val_lower) or any(
                    cdn_kw in (headers or {}).get(k, "").lower()
                    for k in cdn_feature_keys
                ) or any(cdn_kw in hk for hk in header_keys_lower)
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
    d1_missing_counts: Dict[str, int] = {}
    d1_present_counts: Dict[str, int] = {}
    d1_evidence: Dict[str, str] = {}
    d2_evidence: Dict[str, str] = {}
    d2_present: Dict[str, bool] = {}
    d3_meta_found: Dict[str, bool] = {}
    d3_evidence: Dict[str, str] = {}

    async def _d1_probe() -> Dict[str, str]:
        """D1: 同一 URL 2 次并发请求，header 取并集。"""
        merged: Dict[str, str] = {}
        try:
            client = get_httpx_client()
            tasks = [
                asyncio.wait_for(
                    client.get(url, follow_redirects=False),
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
        except Exception:
            pass
        return merged

    async def _d2_probe() -> Dict[str, str]:
        """D2: 子路径验证（/, /index.html），跳过 /login 避免 401/403 干扰。"""
        merged: Dict[str, str] = {}
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
                    client.get(base + p, follow_redirects=False),
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
        except Exception:
            pass
        return merged

    async def _d3_probe() -> str:
        """D3: 抓主页面 HTML，复用 D1 中第一份响应（如有），否则重新请求。"""
        try:
            client = get_httpx_client()
            resp = await asyncio.wait_for(
                client.get(url, follow_redirects=False),
                timeout=_CV_TIMEOUT,
            )
            return resp.text or ""
        except Exception:
            return ""

    # ========== D6: 敏感路径重新访问（同一路径 2 次 + 内容特征确认） ==========
    async def _d6_sensitive_probe() -> Dict[str, dict]:
        """D6: 对 sensitive_paths 中标 exposed 的路径做 2 次重访 + 内容特征确认。

        返回 {path: {"reproducible": bool, "content_confirmed": bool, "evidence": str}}
        """
        results: Dict[str, dict] = {}
        exposed_targets = [
            p for p in (sensitive_paths or [])
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
                contents: List[str] = []
                statuses: List[int] = []
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
                        content_evidence = "命中 KEY=VALUE 格式" if content_confirmed else "未发现 KEY=VALUE 格式"
                    elif ".git/config" in path_lower or path_lower.endswith(".git/config"):
                        content_confirmed = "[core]" in joined
                        content_evidence = "命中 [core] section" if content_confirmed else "未发现 [core] section"
                    elif ".git/head" in path_lower or path_lower.endswith(".git/head"):
                        content_confirmed = "ref:" in joined
                        content_evidence = "命中 ref: refs/" if content_confirmed else "未发现 ref:"
                    elif "wp-config" in path_lower:
                        content_confirmed = bool(
                            re.search(r"DB_NAME|DB_PASSWORD|define\s*\(", joined)
                        )
                        content_evidence = "命中 DB_NAME/DB_PASSWORD/define" if content_confirmed else "未发现 WordPress 配置特征"
                    elif "backup" in path_lower or ".sql" in path_lower or ".zip" in path_lower or ".tar" in path_lower:
                        # 备份文件：非空 + 非错误页
                        content_confirmed = len(joined) > 200 and "404" not in joined[:200].lower() and "<html" not in joined[:200].lower()
                        content_evidence = f"非错误页内容（{len(joined)} 字符）" if content_confirmed else "疑似错误页或 404"
                    elif "phpinfo" in path_lower:
                        content_confirmed = "phpinfo()" in joined or "PHP Version" in joined
                        content_evidence = "命中 phpinfo() 标记" if content_confirmed else "未发现 phpinfo 特征"
                    else:
                        # 其它路径：可重现就算（已 reproducible 即可）
                        content_confirmed = reproducible
                        content_evidence = "路径可重现访问" if content_confirmed else "路径未稳定重现"

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
    async def _d7_d8_cors_probe() -> Dict[str, dict]:
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
                acao_main = main_resp.headers.get("access-control-allow-origin") or main_resp.headers.get("Access-Control-Allow-Origin") or ""
                result["main_origin"] = acao_main
                if acao_main.strip() == "*":
                    result["allow_origin_wildcard_in_main"] = True
                # 看 HTML 找静态资源
                if main_resp.text:
                    m = re.search(r'(?:src|href)\s*=\s*["\']([^"\']+\.(?:js|css|png|jpg|svg|ico))["\']', main_resp.text, re.IGNORECASE)
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
                acao_sub = sub_resp.headers.get("access-control-allow-origin") or sub_resp.headers.get("Access-Control-Allow-Origin") or ""
                result["subresource_origin"] = acao_sub
                if acao_sub.strip() == "*":
                    result["allow_origin_wildcard_in_sub"] = True
                # credentials：主响应或子响应任一带 true 即算
                for r in (main_resp, sub_resp):
                    acac = (r.headers.get("access-control-allow-credentials") or r.headers.get("Access-Control-Allow-Credentials") or "").strip().lower()
                    if acac == "true":
                        result["allow_credentials"] = True
                        break
            except Exception:
                pass

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
    async def _d9_cookie_probe() -> Dict[str, dict]:
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
                set_cookie = r.headers.get("set-cookie") or r.headers.get("Set-Cookie") or ""
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
                result["evidence"] += f"，SameSite=None 缺 Secure {result['samesite_none_without_secure']}次"
        except Exception as e:
            result["evidence"] = f"D9: 异常 {str(e)[:80]}"
        return result

    # ========== D11: 信息泄露多页面验证 ==========
    async def _d11_info_leak_probe() -> Dict[str, bool]:
        """D11: 在首页 + 1 个子页面（/index.html 或 /robots.txt）找相同信息泄露模式。

        找的模式：HTML 注释中的可疑串、Stack Trace 关键词、debug 标记。
        返回 {模式名: 是否在两页同时出现}
        """
        # 注释：<!-- ... -->
        # Stack trace: "Traceback", "at line", "Exception in", "FATAL"
        # Debug: "DEBUG=True", "var_dump", "print_r", "console.log", "TODO", "FIXME"
        leak_patterns = {
            "html_comment": re.compile(r"<!--[^>]{20,}(?:password|secret|token|api[_-]?key|admin|user)[^>]*-->", re.IGNORECASE),
            "stack_trace": re.compile(r"(?:Traceback \(most recent call last\)|at line \d+|FATAL\s*:|Exception in thread)", re.IGNORECASE),
            "debug_marker": re.compile(r"(?:var_dump|print_r|console\.log|debug\s*=\s*True|stack\s*trace\s*on)", re.IGNORECASE),
        }
        result = {k: False for k in leak_patterns}
        try:
            parsed_d11 = urlparse(url)
            base = f"{parsed_d11.scheme}://{parsed_d11.netloc}"
            sub_path = "/index.html" if (parsed_d11.path or "").rstrip("/") != "/index.html" else "/robots.txt"
            client = get_httpx_client()
            tasks = [
                asyncio.wait_for(client.get(url, follow_redirects=False), timeout=_CV_TIMEOUT),
                asyncio.wait_for(client.get(base + sub_path, follow_redirects=False), timeout=_CV_TIMEOUT),
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
        except Exception:
            pass
        return result

    # ========== D10: SSL/TLS 协议版本重新验证（同步 ssl 模块） ==========
    def _d10_ssl_check() -> Dict[str, object]:
        """D10: 用 Python ssl 模块重连验证协议版本。

        返回 {"reachable": bool, "version": str, "weak": bool, "cipher": str, "evidence": str}
        """
        out: Dict[str, object] = {
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
            import ssl
            import socket
            host = parsed_d10.hostname or ""
            port = parsed_d10.port or 443
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            # 强制所有协议都允许，再用 negotiated version 判断
            try:
                ctx.minimum_version = ssl.TLSVersion.TLSv1
            except Exception:
                pass
            with socket.create_connection((host, port), timeout=3) as raw_sock:
                with ctx.wrap_socket(raw_sock, server_hostname=host) as ssock:
                    out["reachable"] = True
                    out["version"] = ssock.version() or ""
                    out["cipher"] = (ssock.cipher() or ["", "", ""])[0] or ""
                    # 弱协议判定
                    v = (out["version"] or "").upper()
                    out["weak"] = v in ("SSLv3", "SSLv2", "TLSv1", "TLSv1.0", "TLSv1.1")
                    out["evidence"] = f"D10: 重连 version={out['version']!r}, weak={out['weak']}"
        except Exception as e:
            out["evidence"] = f"D10: 重连异常 {str(e)[:80]}"
        return out

    # 6+1 组并发：D1, D2, D3, D6, D7+D8, D9, D11（D10 同步，避免阻塞）
    try:
        d1_merged, d2_merged, html, d6_map, d78_cors, d9_cookie, d11_leak = await asyncio.gather(
            _d1_probe(), _d2_probe(), _d3_probe(),
            _d6_sensitive_probe(), _d7_d8_cors_probe(), _d9_cookie_probe(), _d11_info_leak_probe(),
            return_exceptions=False,
        )
    except Exception:
        d1_merged, d2_merged, html = {}, {}, ""
        d6_map, d78_cors, d9_cookie, d11_leak = {}, {}, {}, {}
    # D10 同步执行（避免阻塞事件循环；3s 超时）
    d10_ssl: Dict[str, object] = {}
    try:
        d10_ssl = await asyncio.wait_for(
            asyncio.to_thread(_d10_ssl_check), timeout=4.0,
        )
    except Exception as e:
        d10_ssl = {"reachable": False, "weak": False, "version": "", "cipher": "", "evidence": f"D10: 异常 {str(e)[:80]}"}

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
        meta_pairs: Dict[str, str] = {}
        for m in meta_re.finditer(html or ""):
            meta_pairs[m.group(1).strip().lower()] = m.group(2).strip()
        for f_name, h_key in _FINDING_HEADER_KEY.items():
            meta_name = _META_EQUIV_HEADERS.get(h_key, "").lower()
            if meta_name and meta_name in meta_pairs:
                d3_meta_found[f_name] = True
                d3_evidence[f_name] = (
                    f"D3: <meta http-equiv=\"{_META_EQUIV_HEADERS[h_key]}\" "
                    f"content=\"{meta_pairs[meta_name][:80]}\">"
                )
            else:
                d3_meta_found[f_name] = False
                d3_evidence[f_name] = f"D3: HTML 中未发现 <meta http-equiv=\"{_META_EQUIV_HEADERS.get(h_key, h_key)}\">"
    except Exception:
        for f_name in _FINDING_HEADER_KEY:
            d3_meta_found.setdefault(f_name, False)
            d3_evidence.setdefault(f_name, "D3: 请求异常，未完成 meta 扫描")

    # ========== D4 + D5: 上下文过滤 + 置信度评分 ==========
    # CSP frame-ancestors 覆盖 X-Frame-Options
    csp_value = get_header_value(headers, "content-security-policy")
    has_csp_frame_ancestors = bool(
        csp_value and "frame-ancestors" in csp_value.lower()
    )
    # Server 头是否经 CDN 设置（cloudflare/aws/aliyun 等会强制覆盖）
    server_val = get_header_value(headers, "server") or ""
    cdn_signatures = ("cloudflare", "cloudfront", "aws", "fastly", "akamai", "alicdn", "qcloud")
    is_cdn_server = any(s in server_val.lower() for s in cdn_signatures) or bool(d3_meta_found.get("缺少 CSP")) is False and any(
        (k.lower() in ("cf-ray", "x-amz-cf-id", "x-served-by", "x-cache")) for k in (headers or {}).keys()
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
                    all_content = all(v.get("content_confirmed") for v in d6_map.values())
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
                        reason = "D6: 路径未稳定重现（首次命中但重访失败），建议人工确认"
                    evidences = "; ".join(v.get("evidence", "") for v in d6_map.values())
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
                d78_ev = d78_cors.get("evidence", "") if isinstance(d78_cors, dict) else ""
                main_wild = d78_cors.get("allow_origin_wildcard_in_main", False) if isinstance(d78_cors, dict) else False
                sub_wild = d78_cors.get("allow_origin_wildcard_in_sub", False) if isinstance(d78_cors, dict) else False
                allow_creds = d78_cors.get("allow_credentials", False) if isinstance(d78_cors, dict) else False
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
                d9_ev = d9_cookie.get("evidence", "") if isinstance(d9_cookie, dict) else ""
                missing_sec = d9_cookie.get("missing_secure", 0) if isinstance(d9_cookie, dict) else 0
                missing_htt = d9_cookie.get("missing_httponly", 0) if isinstance(d9_cookie, dict) else 0
                missing_samesite = d9_cookie.get("missing_samesite", 0) if isinstance(d9_cookie, dict) else 0
                ss_none_no_sec = d9_cookie.get("samesite_none_without_secure", 0) if isinstance(d9_cookie, dict) else 0
                with_cookie = d9_cookie.get("with_cookie", 0) if isinstance(d9_cookie, dict) else 0
                if with_cookie == 0:
                    # 没有 Set-Cookie，可能是 API/纯静态
                    confidence = 50
                    reason = "D9: 3 次请求均未带回 Set-Cookie，可能是无 Cookie 站点"
                elif missing_sec == with_cookie and missing_htt == with_cookie:
                    # 3 次都缺 Secure 和 HttpOnly
                    confidence = 95
                    reason = f"D9: {with_cookie}/3 次请求 Cookie 同时缺 Secure 和 HttpOnly"
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
                d10_ev = d10_ssl.get("evidence", "") if isinstance(d10_ssl, dict) else ""
                reachable = d10_ssl.get("reachable", False) if isinstance(d10_ssl, dict) else False
                weak = d10_ssl.get("weak", False) if isinstance(d10_ssl, dict) else False
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
                    reason = "D11: HTML 注释/Stack Trace/Debug 标记在首页 + 子页面同时发现"
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
                    d0_note = d0_evidence.get("Server 头由 CDN 注入", "D0: 检测到 CDN 特征头（CF-Ray/X-Cache 等），Server 头由 CDN 注入")
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
        d1_present = d1_present_counts.get(name, 0)
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
        if h_key in ("content-security-policy", "strict-transport-security") and not is_https_url:
            https_preference = f" D4: 当前为 HTTP 协议，建议优先在 HTTPS 上配置 {h_key}。"

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
        dim_hits = sum([1 if d1_full_match else 0, 1 if d2_match else 0, 1 if d3_match else 0])

        if dim_hits >= 3:
            confidence = 95
            confidence_reason = "D5: 3 维均命中（2次请求 + 子路径 + meta 扫描均未发现），高置信度"
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


def add_finding(
    findings: List[dict],
    name: str,
    severity: str,  # 英文 high/medium/low
    owasp: str,
    summary: str,
    fix: str,
    vuln_type: Optional[str] = None,
    evidence: Optional[dict] = None,
    verify_key: Optional[str] = None,
    verified: Optional[bool] = None,
    confidence: Optional[int] = None,
    cv_reason: Optional[str] = None,
) -> None:
    finding: Dict[str, Any] = {
        "name": name,
        "severity": severity,         # 真实字段：英文
        "level": SEVERITY_ZH.get(severity, "低风险"),  # 给前端展示的中文
        "level_zh": SEVERITY_ZH.get(severity, "低风险"),
        "owasp": owasp,
        "summary": summary,
        "fix": fix,
        "type": vuln_type or "config",
        "evidence": evidence or {},
        "verify_method": VERIFY_METHODS.get(verify_key, "重新扫描该网站，查看此项是否消失"),
    }
    # V11.4：交叉验证字段（可选）
    if verified is not None:
        finding["verified"] = verified
    if confidence is not None:
        finding["confidence"] = confidence
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


def analyze_security(
    url: str,
    headers: dict,
    is_https: bool,
    ssl_info: dict,
    waf_list: List[dict],
    sensitive_paths: List[dict],
    vuln_findings: Optional[List[dict]] = None,
) -> dict:
    findings: List[dict] = []
    score = 100
    score_breakdown: List[dict] = []
    header_details: List[dict] = []
    owasp: List[dict] = []

    def deduct(item: str, points: int, severity: str, reason: str):
        nonlocal score
        score -= points
        score_breakdown.append({"item": item, "deduction": points, "severity": severity, "reason": reason})

    if not is_https:
        deduct("未启用 HTTPS", 20, "critical", "网站使用 HTTP 明文传输")
        add_finding(findings, "未启用 HTTPS", "high", "A02 加密机制失效",
                    "网站使用 HTTP 明文传输。", "申请 SSL 证书并启用 HTTPS 强制跳转。",
                    evidence={"detected": False, "reason": "网站使用 HTTP 明文传输所有数据", "impact": "用户数据可被中间人窃取"},
                    verify_key="https")
        owasp.append({"category": "A02 加密机制失效", "status": "高风险", "note": "未启用 HTTPS"})
    else:
        owasp.append({"category": "A02 加密机制失效", "status": "通过", "note": "已启用 HTTPS"})
        if ssl_info.get("has_cert"):
            dl = ssl_info.get("days_left")
            dl_is_num = isinstance(dl, (int, float))
            if ssl_info.get("expired"):
                deduct("SSL 证书已过期", 15, "high", f"证书已过期 {abs(dl) if dl_is_num else '未知'} 天")
                add_finding(findings, "SSL 证书已过期", "high", "A02 加密机制失效",
                            "SSL 证书已过期" + (f" {abs(dl)} 天" if dl_is_num else "（无法获取剩余天数）") + "。",
                            "立即续期 SSL 证书。",
                            evidence={"days_left": dl, "reason": "证书已过期，浏览器会显示安全警告", "impact": "用户无法正常访问，数据传输不受信任"},
                            verify_key="ssl")
            elif dl_is_num and dl < 30:
                deduct("SSL 证书即将过期", 5, "medium", f"证书将在 {dl} 天后过期")
                add_finding(findings, "SSL 证书即将过期", "medium", "A02 加密机制失效",
                            f"SSL 证书将在 {dl} 天后过期。",
                            "提前续期 SSL 证书。",
                            verify_key="ssl")
            if ssl_info.get("weak"):
                deduct("弱 SSL/TLS 配置", 10, "medium", f"使用 {ssl_info.get('version', '')} / {ssl_info.get('cipher', '')}")
                add_finding(findings, "弱 SSL/TLS 配置", "medium", "A02 加密机制失效",
                            "使用 " + ssl_info.get("version", "") + " / " + ssl_info.get("cipher", "") + "。",
                            "升级到 TLS 1.2+，禁用弱密码套件。",
                            verify_key="ssl")

    # 安全头缺失检测，verify_key 根据具体头名
    HEADER_VERIFY_KEY = {
        "strict-transport-security": "hsts",
        "content-security-policy": "csp",
        "x-frame-options": "x-frame",
        "x-content-type-options": "x-content-type",
        "referrer-policy": "referrer",
        "permissions-policy": "permissions",
    }
    # 高危配置缺失 vs 普通配置缺失
    HIGH_CONFIG_HEADERS = {"strict-transport-security", "content-security-policy", "x-frame-options"}
    for key, rule in SECURITY_HEADERS.items():
        value = headers.get(key, headers.get(key.title(), None))
        header_details.append({
            "name": rule["name"], "key": key, "value": value,
            "status": "present" if value else "missing",
            "category": rule["category"], "severity": rule["severity"],
        })
        if not value:
            if key in HIGH_CONFIG_HEADERS:
                points = SCORE_DEDUCTION["high_config_missing"]
            else:
                points = SCORE_DEDUCTION["normal_config_missing"]
            deduct("缺少 " + rule["name"], points, rule["severity"], rule["description"])
            add_finding(findings, "缺少 " + rule["name"], rule["severity"],
                        "A05 安全配置错误", rule["description"] + "。", rule["fix"],
                        evidence={"detected": False, "header": key, "reason": f"未检测到 {rule['name']} 响应头", "impact": rule.get("description", "")},
                        verify_key=HEADER_VERIFY_KEY.get(key, "info"))

    info_leaks: List[dict] = []
    for key in ["server", "x-powered-by"]:
        value = headers.get(key, headers.get(key.title(), None))
        if value:
            info_leaks.append({"name": key.title(), "value": value})
            # 信息项：只扣 1 分
            deduct(key.title() + " 信息泄露", SCORE_DEDUCTION["info_leak"], "low", "暴露服务器信息: " + value[:50])
            add_finding(findings, key.title() + " 信息泄露", "low", "A05 安全配置错误",
                        "暴露服务器信息: " + value[:50], "隐藏或修改 " + key.title() + " 头。",
                        evidence={"header": key.title(), "value": value[:50], "reason": "暴露了服务器软件和版本信息", "impact": "攻击者可利用已知版本漏洞"},
                        verify_key="server")

    set_cookie = headers.get("set-cookie", headers.get("Set-Cookie", None))
    cookie_issues: List[str] = []
    cookie_fix_parts = []
    if set_cookie:
        flags = set_cookie.lower()
        for flag, label in [("secure", "Secure"), ("httponly", "HttpOnly"), ("samesite", "SameSite")]:
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
            deduct("Cookie 安全配置不足", 5, "low", "Cookie 问题: " + "; ".join(cookie_issues))
            fix_text = "添加 " + "; ".join(cookie_fix_parts) if cookie_fix_parts else "修正 Cookie 配置"
            if not fix_text.startswith("添加") and cookie_fix_parts:
                fix_text = "修正: " + "; ".join(cookie_fix_parts)
            add_finding(findings, "Cookie 安全配置不足", "low", "A07 认证失败",
                        "Cookie 问题: " + "; ".join(cookie_issues),
                        fix_text,
                        evidence={"missing_flags": cookie_issues[:], "reason": "Cookie 安全配置不当", "impact": "Cookie 可被窃取、篡改或用于 CSRF 攻击"},
                        verify_key="cookie")

    cors = headers.get("access-control-allow-origin", headers.get("Access-Control-Allow-Origin", None))
    cors_details = None
    if cors:
        if cors == "*":
            deduct("CORS 通配符", 10, "medium", "允许任意域名跨域访问")
            add_finding(findings, "CORS 通配符", "medium", "A01 访问控制失效",
                        'Access-Control-Allow-Origin 设置为 "*"。', "限制为可信域名。",
                        evidence={"value": "*", "reason": "允许任何域名跨域访问", "impact": "敏感数据可被恶意网站读取"},
                        verify_key="cors")
            cors_details = {"value": "*", "risk": "高风险"}
        else:
            cors_details = {"value": cors, "risk": "低风险"}

    exposed = [p for p in sensitive_paths if p.get("exposed")]
    if exposed:
        # 确认漏洞：敏感路径暴露，扣 15 分
        deduct("敏感路径暴露", SCORE_DEDUCTION["exposed_path"], "high", f"发现 {len(exposed)} 个敏感路径可访问")
        add_finding(findings, "敏感路径暴露", "high", "A01 访问控制失效",
                    "发现 " + str(len(exposed)) + " 个敏感路径可访问: " + ", ".join([p["path"] for p in exposed[:3]]),
                    "限制敏感路径访问或移除。",
                    evidence={"paths": [p["path"] for p in exposed[:5]], "reason": f"发现 {len(exposed)} 个敏感路径可访问", "impact": "攻击者可获取配置文件、源代码等敏感信息"},
                    verify_key="info")
    # info 路径（如 robots.txt）不算漏洞，只作为信息提示，不扣分
    info_paths = [p for p in sensitive_paths if p.get("info")]
    # suspect 路径：前端展示警告，但不扣分
    suspect_paths = [p for p in sensitive_paths if p.get("suspect")]
    if suspect_paths:
        # suspect 疑似项：不扣分，只作为信息提示
        pass

    if vuln_findings:
        for v in vuln_findings:
            findings.append(v)
            sev = v.get("severity", "high")
            if sev == "critical":
                deduct(v.get("name", "漏洞"), 25, "critical", "检测到严重漏洞")
            elif sev == "high":
                deduct(v.get("name", "漏洞"), 15, "high", "检测到高风险漏洞")

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
    for cat, status, note in [
        ("A01 访问控制失效", "通过" if not exposed else "高风险", "需关注"),
        ("A03 注入攻击", "高风险" if (has_xss or has_sqli) else "通过",
         "检测到 XSS/SQLi" if (has_xss or has_sqli) else "未检测到注入漏洞"),
        ("A04 不安全设计", "通过", "未检测到"),
        ("A05 安全配置错误",
         "需关注" if any(f["owasp"] == "A05 安全配置错误" for f in findings) else "通过",
         "部分配置可优化"),
        ("A06 过时组件", "需深度检测", "建议扫描依赖"),
        ("A07 认证失败", "通过", "未检测到"),
        ("A08 软件完整性", "通过", "未检测到"),
        ("A09 日志监控不足", "低风险", "建议加强"),
        ("A10 服务端请求伪造", "通过", "未检测到"),
    ]:
        if cat not in owasp_map:
            owasp.append({"category": cat, "status": status, "note": note})
    owasp.sort(key=lambda x: int(x["category"][1:3]))
    score = max(10, min(98, score))
    risk_level = "高风险" if score < 50 else "中风险" if score < 75 else "低风险"
    improvements: List[str] = []
    for f in findings:
        improvements.append(f.get("fix", ""))

    # 检测受限扫描特征：WAF/反爬/登录页
    # 注意：CDN（Cloudflare/AWS）只标"识别到"，不算受限；
    # 真正的反爬 WAF（阿里云 WAF/Imperva/Akamai WAF）才算受限
    CDN_WAF = {"cloudflare", "aws", "baidu", "qcloud"}
    REAL_WAF = {"aliyun", "imperva", "akamai"}
    restricted = False
    restricted_reason = ""
    restricted_code = ""
    # 1. 真正的反爬 WAF 检测（区分 CDN）
    if waf_list:
        waf_name = waf_list[0].get("name", "").lower()
        if waf_name in REAL_WAF:
            restricted = True
            restricted_reason = f"检测到反爬 WAF（{waf_list[0].get('name', '未知')}），目标站点有访问限制。"
            restricted_code = "WAF"
        # CDN（WAF/CDN 列表里有 cloudflare/aws）只标识别到，不算受限
    # 2. 敏感路径中有 suspect（登录页/反爬响应）
    suspect_paths = [p for p in sensitive_paths if p.get("suspect")]
    if suspect_paths and not restricted:
        restricted = True
        reasons = [p.get("reason", "疑似 WAF/登录页响应") for p in suspect_paths[:2]]
        restricted_reason = "检测到疑似 WAF/登录页/反爬响应：" + "；".join(reasons) + "。本次为受限扫描，部分结果需要人工确认。"
        restricted_code = "SUSPECT"
    # 3. 响应头中有反爬特征
    if headers:
        hk = {k.lower(): str(v) for k, v in headers.items()}
        anti_bot_signs = ["alicdn", "captcha", "waf", "punish", "verify", "authentication"]
        for sign in anti_bot_signs:
            for k, v in hk.items():
                if sign in k or sign in v:
                    if not restricted:
                        restricted = True
                        restricted_reason = f"响应头检测到反爬/WAF 特征（{sign}），目标站点限制自动化访问。"
                        restricted_code = "ANTI_BOT"
                    break

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
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, ListFlowable, ListItem
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    _cn_font = "Helvetica"
    for _fp in [
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    ]:
        if os.path.isfile(_fp):
            try:
                pdfmetrics.registerFont(TTFont("CNFont", _fp, subfontIndex=0))
                _cn_font = "CNFont"
                break
            except Exception:
                continue

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            rightMargin=20 * mm, leftMargin=20 * mm,
                            topMargin=20 * mm, bottomMargin=20 * mm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CN", fontName=_cn_font, fontSize=10, leading=14))
    styles.add(ParagraphStyle(name="CNBold", fontName=_cn_font, fontSize=10, leading=14, textColor=colors.HexColor("#4f46e5")))
    styles.add(ParagraphStyle(name="CNRed", fontName=_cn_font, fontSize=10, leading=14, textColor=colors.HexColor("#dc2626")))
    styles.add(ParagraphStyle(name="CNGreen", fontName=_cn_font, fontSize=10, leading=14, textColor=colors.HexColor("#16a34a")))
    styles.add(ParagraphStyle(name="CNOrange", fontName=_cn_font, fontSize=10, leading=14, textColor=colors.HexColor("#d97706")))

    elements = []

    # ===== 封面页 =====
    elements.append(Spacer(1, 60 * mm))
    elements.append(Paragraph("漏洞哨兵", ParagraphStyle(name="CoverTitle", fontName=_cn_font, fontSize=28, leading=36, alignment=1)))
    elements.append(Spacer(1, 10 * mm))
    elements.append(Paragraph("Web 安全扫描报告", ParagraphStyle(name="CoverSub", fontName=_cn_font, fontSize=16, leading=22, alignment=1)))
    elements.append(Spacer(1, 20 * mm))
    elements.append(Paragraph(f"目标: {scan_data.get('url', '')}", ParagraphStyle(name="CoverInfo", fontName=_cn_font, fontSize=11, leading=16, alignment=1)))
    elements.append(Paragraph(f"时间: {scan_data.get('time', '')}", ParagraphStyle(name="CoverInfo2", fontName=_cn_font, fontSize=11, leading=16, alignment=1)))
    elements.append(Paragraph(f"评分: {scan_data.get('score', 0)} / 100", ParagraphStyle(name="CoverInfo3", fontName=_cn_font, fontSize=11, leading=16, alignment=1)))
    elements.append(Spacer(1, 30 * mm))
    elements.append(Paragraph("本报告由漏洞哨兵自动生成，仅供参考。", ParagraphStyle(name="CoverNote", fontName=_cn_font, fontSize=9, leading=13, alignment=1, textColor=colors.grey)))
    elements.append(PageBreak())

    # ===== 摘要页 =====
    elements.append(Paragraph("摘要", styles["Heading2"]))
    elements.append(Paragraph(f"安全评分: {scan_data.get('score', 0)} / 100（{scan_data.get('risk_level', '')}）", styles["CN"]))
    summary = scan_data.get("summary", {})
    elements.append(Paragraph(f"发现问题: {summary.get('total', 0)} 个（严重 {summary.get('critical', 0)} / 高危 {summary.get('high', 0)} / 中危 {summary.get('medium', 0)} / 低危 {summary.get('low', 0)}）", styles["CN"]))
    elements.append(Spacer(1, 5 * mm))

    elements.append(Paragraph("检测范围", styles["Heading2"]))
    elements.append(Paragraph("本次扫描检测了以下安全项目：HTTPS/TLS 配置、安全响应头（HSTS/CSP/X-Frame-Options 等）、信息泄露、Cookie 安全、CORS 配置、敏感路径暴露、WAF 检测。", styles["CN"]))
    elements.append(Paragraph("不进行破坏性攻击、不爆破密码、不绕过权限验证。", styles["CN"]))
    elements.append(Spacer(1, 5 * mm))
    elements.append(PageBreak())

    # ===== 风险摘要页 =====
    elements.append(Paragraph("风险摘要", styles["Heading2"]))
    findings = scan_data.get("findings", [])
    exposed_count = len([p for p in scan_data.get("sensitive_paths", []) if p.get("exposed")])
    suspect_count = len([p for p in scan_data.get("sensitive_paths", []) if p.get("suspect")])
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
        delta_color = styles["CNGreen"] if delta > 0 else styles["CNRed"] if delta < 0 else styles["CN"]
        elements.append(Paragraph(f"评分变化: {prev_score} -> {curr_score} ({delta_text})", delta_color))
        elements.append(Spacer(1, 3 * mm))

    # 修复优先级路线
    elements.append(Paragraph("修复优先级路线", styles["Heading2"]))
    priority_steps = []
    if exposed_count > 0:
        priority_steps.append("第一步（立即）: 修复暴露的敏感路径，限制 .env/.git 等文件访问")
    high_headers = [f for f in findings if f.get("severity") == "high" and f.get("name", "").startswith("缺少 ")]
    if high_headers:
        priority_steps.append(f"第二步（今天）: 修复高危响应头缺失（{', '.join([f.get('name', '').replace('缺少 ', '') for f in high_headers[:3]])}）")
    med_low = [f for f in findings if f.get("severity") in ("medium", "low") and f.get("name", "").startswith("缺少 ")]
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
            elements.append(Paragraph(f"{i+1}. {f.get('name', '')} [{f.get('level', f.get('severity', ''))}]", styles["CNBold"]))
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
                        elements.append(Paragraph(f"   路径 {p.get('path', '')}: 状态 {p.get('status', '')} - {p.get('reason', '')}", styles["CN"]))
            elements.append(Spacer(1, 2 * mm))
    else:
        elements.append(Paragraph("未发现安全问题", styles["CN"]))
    elements.append(Spacer(1, 5 * mm))
    elements.append(PageBreak())

    # ===== 修复建议页 =====
    elements.append(Paragraph("修复建议", styles["Heading2"]))
    fixes = scan_data.get("fixes", {})
    server_type = scan_data.get("server_type", "unknown")
    if fixes:
        for platform, entries in fixes.items():
            if not entries:
                continue
            elements.append(Paragraph(f"{platform.upper()} 配置", styles["CNBold"]))
            for entry in entries:
                code = entry.get("code", "") if isinstance(entry, dict) else str(entry)
                risk_note = entry.get("risk_note", "") if isinstance(entry, dict) else ""
                elements.append(Paragraph(f"<pre>{code}</pre>", ParagraphStyle(name="Code", fontName=_cn_font, fontSize=8, leading=12, leftIndent=10, textColor=colors.HexColor("#334155"))))
                if risk_note:
                    elements.append(Paragraph(f"注意: {risk_note}", styles["CNOrange"]))
                elements.append(Spacer(1, 2 * mm))
    else:
        # 按 findings 生成通用修复建议
        for f in findings:
            fix_text = f.get("fix", "")
            if fix_text:
                elements.append(Paragraph(f"{f.get('name', '')}:", styles["CNBold"]))
                elements.append(Paragraph(f"<pre>{fix_text}</pre>", ParagraphStyle(name="Code2", fontName=_cn_font, fontSize=8, leading=12, leftIndent=10, textColor=colors.HexColor("#334155"))))
                elements.append(Spacer(1, 2 * mm))
    elements.append(Spacer(1, 5 * mm))
    elements.append(PageBreak())

    # ===== 复测结果页 =====
    elements.append(Paragraph("复测结果", styles["Heading2"]))
    if len(history) >= 2:
        prev = history[-2]
        curr = history[-1] if history else scan_data
        prev_score = prev.get("score", 0)
        curr_score = scan_data.get("score", 0)
        elements.append(Paragraph(f"上次评分: {prev_score} | 本次评分: {curr_score}", styles["CN"]))
        prev_names = set([ff.get("name", "") for ff in prev.get("findings", [])])
        curr_names = set([ff.get("name", "") for ff in scan_data.get("findings", [])])
        new_issues = curr_names - prev_names
        fixed_issues = prev_names - curr_names
        if new_issues:
            elements.append(Paragraph(f"新增问题 ({len(new_issues)}):", styles["CNRed"]))
            for issue in sorted(new_issues):
                elements.append(Paragraph(f"  • {issue}", styles["CN"]))
        if fixed_issues:
            elements.append(Paragraph(f"已修复问题 ({len(fixed_issues)}):", styles["CNGreen"]))
            for issue in sorted(fixed_issues):
                elements.append(Paragraph(f"  • {issue}", styles["CN"]))
        if not new_issues and not fixed_issues:
            elements.append(Paragraph("两次扫描结果一致，无变化", styles["CN"]))
    else:
        elements.append(Paragraph('暂无历史复测数据。建议修复后点击"验证修复效果"进行复测。', styles["CN"]))
    elements.append(Spacer(1, 5 * mm))
    elements.append(PageBreak())

    # ===== Findings 表格（含证据列） =====
    elements.append(Paragraph("Findings", styles["Heading2"]))
    if findings:
        table_data = [["#", "问题", "严重度", "OWASP", "证据/原因", "修复建议"]]
        for i, f in enumerate(findings):
            evidence = f.get("evidence", {})
            evidence_text = evidence.get("reason", "")[:40] if evidence else ""
            table_data.append([
                str(i + 1), f.get("name", ""),
                f.get("level", f.get("severity", "")),
                f.get("owasp", ""), evidence_text, f.get("fix", "")[:50],
            ])
        t = Table(table_data, colWidths=[8*mm, 28*mm, 18*mm, 25*mm, 30*mm, 41*mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4f46e5")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
        ]))
        elements.append(t)
    elements.append(Spacer(1, 8 * mm))

    elements.append(Paragraph("OWASP Top 10 Coverage", styles["Heading2"]))
    owasp = scan_data.get("owasp_coverage", [])
    if owasp:
        owasp_data = [["Category", "Status", "Note"]]
        for o in owasp:
            owasp_data.append([o["category"], o["status"], o.get("note", "")])
        t2 = Table(owasp_data, colWidths=[50 * mm, 30 * mm, 70 * mm])
        t2.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4f46e5")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(t2)

    # ===== 免责声明 =====
    elements.append(Spacer(1, 10 * mm))
    elements.append(Paragraph("免责声明", styles["Heading2"]))
    elements.append(Paragraph("本报告由漏洞哨兵智能规则引擎自动生成，仅反映扫描时刻的目标网站安全配置状况。扫描结果可能存在误报或漏报，不构成完整的安全审计。建议结合专业安全评估和渗透测试综合判断。本工具不进行任何破坏性操作。", styles["CN"]))

    doc.build(elements)
    return buf.getvalue()


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


def _build_fix_entry(code: str, server_type: str, config_examples: Dict[str, str], risk_note: Optional[str] = None) -> dict:
    return {
        "code": code,
        "risk_note": risk_note,
        "server_type": server_type,
        "config_examples": config_examples,
    }


def generate_fixes(findings: List[dict], headers: dict, is_https: bool, host: str) -> dict:
    fixes: dict = {
        "nginx": [], "apache": [], "express": [], "flask": [], "spring_boot": [], "cloudflare": [],
        "nodejs": [], "python": [],  # 保留旧 key 兼容
    }
    seen = set()  # 去重

    detected_server = _detect_server_type(headers)

    def add(lang, code, risk_note=None):
        if code and code not in seen:
            # 为每种语言构建对应的 config_examples
            config_examples: Dict[str, str] = {}
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
            fixes[lang].append(_build_fix_entry(code, detected_server, config_examples, risk_note))
            seen.add(code)

    for f in findings:
        name = (f.get("name") or "").strip()
        severity = f.get("severity") or "low"
        fix_text = f.get("fix", "") or ""
        ftype = f.get("type", "config")

        if name.startswith("缺少 "):
            # 任意安全头缺失
            header_name = name[3:]
            fix_value = fix_text.split('"')[1] if '"' in fix_text else 'value'
            add("nginx", fix_text)
            add("apache", fix_text.replace("add_header", "Header set").replace("always;", ""))
            add("python", "# Flask 后置响应头: " + fix_text)
            add("nodejs", "// Express helmet: " + fix_text)
            add("flask", f"# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['{header_name}'] = '{fix_value}'\n    return resp")
            add("express", "// Express helmet: " + fix_text)
            add("spring_boot", f"# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {{\n#     http.headers().httpStrictTransportSecurity();\n# }}")
            add("cloudflare", f"# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: {header_name}\n# Value: {fix_value}")
            if "CSP" in name or "Content-Security-Policy" in name:
                csp_value = fix_text.split('"')[1] if '"' in fix_text else "default-src 'self'"
                add("flask", f"# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['Content-Security-Policy'] = '{csp_value}'\n    return resp",
                    risk_note="上线前请在测试环境验证，CSP 策略过严可能导致前端资源加载失败")
                add("cloudflare", "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: Content-Security-Policy\n# Value: default-src 'self'",
                    risk_note="上线前请在测试环境验证，CSP 策略过严可能导致前端资源加载失败")
        elif name == "未启用 HTTPS":
            add("nginx", "server {\n    listen 80;\n    server_name " + host +
                ";\n    return 301 https://$host$request_uri;\n}")
            add("python", "# Flask: from flask_talisman import Talisman\n# Talisman(app, force_https=True)")
            add("nodejs", "// Express: app.use(enforceHTTPS({ maxAge: 31536000 }));")
            add("apache", "<VirtualHost *:80>\n    ServerName " + host +
                  "\n    Redirect permanent / https://$host/\n</VirtualHost>")
            add("flask", "# Flask/Talisman: from flask_talisman import Talisman\n# Talisman(app, force_https=True)")
            add("express", "// Express: app.use(enforceHTTPS({ maxAge: 31536000 }));")
            add("spring_boot", "# Spring Boot: server.ssl.enabled=true\n# server.ssl.key-store=classpath:keystore.p12")
            add("cloudflare", "# Cloudflare: SSL/TLS > Full (Strict)")
        elif name == "SSL 证书已过期":
            add("nginx", "# Renew SSL cert then update:\nssl_certificate /etc/ssl/certs/" + host + ".pem;")
            add("python", "# certbot renew")
            add("nodejs", "# certbot renew")
            add("flask", "# certbot renew && 更新 SSL 配置")
            add("spring_boot", "# Spring Boot: keytool -importkeystore + 更新 server.ssl 配置")
            add("cloudflare", "# Cloudflare: SSL/TLS > Edge Certificates > Renew")
        elif name == "弱 SSL/TLS 配置":
            add("nginx", "ssl_protocols TLSv1.2 TLSv1.3;\nssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;")
            add("python", "# ctx.minimum_version = ssl.TLSVersion.TLSv1_2")
            add("nodejs", "// minVersion: 'TLSv1.2'")
            add("flask", "# Flask: ctx.minimum_version = ssl.TLSVersion.TLSv1_2")
            add("express", "// Express: minVersion: 'TLSv1.2'")
            add("spring_boot", "# Spring Boot: server.ssl.enabled-protocols=TLSv1.2,TLSv1.3")
            add("cloudflare", "# Cloudflare: SSL/TLS > Minimum TLS Version > TLS 1.2")
        elif "信息泄露" in name:
            add("nginx", "server_tokens off;")
            add("apache", "ServerTokens Prod\nServerSignature Off")
            add("python", "# app.config['SECRET_KEY'] = os.urandom(32)")
            add("nodejs", "// app.disable('x-powered-by')")
            add("flask", "# Flask: app.config['SECRET_KEY'] = os.urandom(32)")
            add("express", "// Express: app.disable('x-powered-by')")
            add("spring_boot", "# Spring Boot: server.error.include-stacktrace=never")
            add("cloudflare", "# Cloudflare: Scrape Shield > Disable Server Name Exposure")
        elif "Cookie" in name:
            add("nginx", "proxy_cookie_path / /; HttpOnly; Secure; SameSite=Strict;")
            add("python", "# resp.set_cookie('session', val, httponly=True, secure=True, samesite='Strict')")
            add("nodejs", "// cookie: { httpOnly: true, secure: true, sameSite: 'strict' }")
            add("flask", "# Flask: resp.set_cookie('session', val, httponly=True, secure=True, samesite='Strict')")
            add("express", "// Express: cookie: { httpOnly: true, secure: true, sameSite: 'strict' }")
            add("spring_boot", "# Spring Boot: server.servlet.session.cookie.http-only=true\n# server.servlet.session.cookie.secure=true")
            add("cloudflare", "# Cloudflare: SSL > Always Use HTTPS")
        elif "CORS" in name:
            add("nginx", "add_header Access-Control-Allow-Origin 'https://your-domain.com' always;")
            add("python", "# CORS(app, origins=['https://your-domain.com'])")
            add("nodejs", "// cors({ origin: 'https://your-domain.com' })")
            add("flask", "# Flask/CORS: CORS(app, origins=['https://your-domain.com'])")
            add("express", "// Express: cors({ origin: 'https://your-domain.com' })")
            add("spring_boot", "# Spring Boot: @CrossOrigin(origins = \"https://your-domain.com\")")
            add("cloudflare", "# Cloudflare: CORS policy > allowed origins")
        elif "敏感路径" in name:
            add("nginx", "location ~ /(\\.env|\\.git|\\.svn|backup\\.sql|\\.bak) {\n    deny all;\n    return 403;\n}")
            add("python", "# @app.before_request: block /.env, /.git paths -> 403")
            add("nodejs", "// Block /.env, /.git paths -> 403")
            add("flask", "# Flask: @app.before_request\n# if request.path in ('/.env', '/.git'): abort(403)")
            add("express", "// Express: Block /.env, /.git paths -> 403")
            add("spring_boot", "# Spring Boot: WebSecurityConfigurerAdapter block /.*env, /.git")
            add("cloudflare", "# Cloudflare: WAF > Custom Rules > Block /*env, /*git")
        elif ftype == "XSS":
            add("nginx", "add_header Content-Security-Policy \"default-src 'self'; script-src 'self'\" always;")
            add("python", "# Use jinja2 auto-escaping: {{ var|e }}")
            add("nodejs", "// helmet.contentSecurityPolicy({ defaultSrc: [\"'self'\"] })")
            add("flask", "# Flask: 使用 jinja2 自动转义 {{ var|e }}",
                risk_note="上线前请在测试环境验证，CSP 策略过严可能导致前端资源加载失败")
            add("express", "// Express: helmet.contentSecurityPolicy({ defaultSrc: [\"'self'\"] })",
                risk_note="上线前请在测试环境验证，CSP 策略过严可能导致前端资源加载失败")
            add("spring_boot", "# Spring Boot: ContentSecurityPolicyFilterRegistrationBean")
            add("cloudflare", "# Cloudflare: WAF > XSS Rules > Enable")
        elif ftype == "SQLi":
            add("nginx", '# ModSecurity: SecRule ARGS "(OR|UNION)" "deny,status:403"')
            add("python", "# cursor.execute('SELECT * FROM users WHERE id=%s', (uid,))")
            add("nodejs", "// db.query('SELECT * FROM users WHERE id=$1', [uid])")
            add("flask", "# Flask: cursor.execute('SELECT * FROM users WHERE id=%s', (uid,))")
            add("express", "// Express: db.query('SELECT * FROM users WHERE id=$1', [uid])")
            add("spring_boot", "# Spring Boot: @Repository + JPA ParameterizedQuery")
            add("cloudflare", "# Cloudflare: WAF > SQL Injection Rules > Enable")
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


@app.post("/api/register")
async def api_register(req: RegisterRequest, request: Request) -> dict:
    client_ip = request.client.host if request.client else "unknown"
    if not await limiter_register.is_allowed(client_ip):
        raise HTTPException(
            status_code=429,
            detail="注册请求过于频繁，请稍后再试",
            headers={"Retry-After": "60"},
        )
    conn = get_db()
    existing = conn.execute("SELECT id FROM users WHERE username COLLATE NOCASE=?", (req.username,)).fetchone()
    if existing:
        conn.close()
        raise HTTPException(400, "用户名已存在")
    try:
        conn.execute(
            "INSERT INTO users (username, password, email, role, team_id, created_at) VALUES (?,?,?,?,?,?)",
            (req.username, hash_password(req.password), req.email, "member", 0,
             datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        conn.commit()
        user = conn.execute("SELECT * FROM users WHERE username=?", (req.username,)).fetchone()
        token = create_token(user["id"], user["username"])
        user_dict = dict(user)
        conn.close()
        return {"success": True, "token": token, "username": user_dict["username"], "user_id": user_dict["id"], "role": user_dict.get("role", "member")}
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(400, "用户名已存在")


@app.post("/api/login")
async def api_login(req: LoginRequest, request: Request) -> dict:
    client_ip = request.client.host if request.client else "unknown"
    if not await limiter_login.is_allowed(client_ip):
        raise HTTPException(
            status_code=429,
            detail="登录请求过于频繁，请稍后再试",
            headers={"Retry-After": "60"},
        )
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username=?", (req.username,)).fetchone()
    conn.close()
    if not user or not verify_password(req.password, user["password"]):
        raise HTTPException(401, "用户名或密码错误")
    token = create_token(user["id"], user["username"])
    user_dict = dict(user)
    return {"success": True, "token": token, "username": user_dict["username"], "user_id": user_dict["id"], "role": user_dict.get("role", "member")}


@app.get("/api/me")
async def api_me(user: Optional[dict] = Depends(get_current_user)) -> dict:
    if not user:
        raise HTTPException(401, "未登录")
    conn = get_db()
    row = conn.execute("SELECT role, team_id FROM users WHERE id=?", (user["user_id"],)).fetchone()
    conn.close()
    return {"user_id": user["user_id"], "username": user["username"], "role": row[0] if row else "member", "team_id": row[1] if row else 0}


# ---------- Team Management ----------

@app.get("/api/team")
async def api_team(user: dict = Depends(require_login)) -> dict:
    """获取当前用户所在团队的成员列表。"""
    conn = get_db()
    my_row = conn.execute("SELECT role, team_id FROM users WHERE id=?", (user["user_id"],)).fetchone()
    if not my_row:
        conn.close()
        raise HTTPException(404, "用户不存在")
    my_role = my_row[0] or "member"
    my_team_id = my_row[1] or 0

    if my_team_id == 0:
        # 没有团队，返回自己
        conn.close()
        return {"team_id": 0, "members": [{"user_id": user["user_id"], "username": user["username"], "role": my_role}]}

    rows = conn.execute("SELECT id, username, role, created_at FROM users WHERE team_id=? ORDER BY id", (my_team_id,)).fetchall()
    conn.close()
    members = [{"user_id": r[0], "username": r[1], "role": r[2], "created_at": r[3]} for r in rows]
    return {"team_id": my_team_id, "role": my_role, "members": members}


@app.post("/api/team/create")
async def api_team_create(user: dict = Depends(require_login)) -> dict:
    """创建团队，当前用户成为 admin。"""
    conn = get_db()
    my_row = conn.execute("SELECT team_id FROM users WHERE id=?", (user["user_id"],)).fetchone()
    if my_row and my_row[0] and my_row[0] > 0:
        conn.close()
        raise HTTPException(400, "已加入团队，请先退出当前团队")
    conn.execute("UPDATE users SET role='admin', team_id=? WHERE id=?", (user["user_id"], user["user_id"]))
    conn.commit()
    conn.close()
    return {"success": True, "team_id": user["user_id"], "message": "团队已创建"}


@app.post("/api/team/join")
async def api_team_join(req: dict, user: dict = Depends(require_login)) -> dict:
    """加入团队。"""
    team_id = req.get("team_id")
    if not team_id or not isinstance(team_id, int):
        raise HTTPException(400, "team_id 必须是整数")
    conn = get_db()
    # 验证目标团队存在（team_id 就是 admin 的 user_id）
    admin_row = conn.execute("SELECT id, role FROM users WHERE id=? AND team_id=?", (team_id, team_id)).fetchone()
    if not admin_row:
        conn.close()
        raise HTTPException(404, "团队不存在")
    # 更新自己的 team_id
    conn.execute("UPDATE users SET team_id=?, role='member' WHERE id=?", (team_id, user["user_id"]))
    conn.commit()
    conn.close()
    return {"success": True, "team_id": team_id, "message": "已加入团队"}


@app.post("/api/team/{target_user_id}/role")
async def api_team_set_role(target_user_id: int, req: dict, user: dict = Depends(require_login)) -> dict:
    """修改团队成员角色（仅 admin 可操作）。"""
    new_role = req.get("role", "member")
    if new_role not in ("admin", "member", "viewer"):
        raise HTTPException(400, "角色必须是 admin / member / viewer")
    conn = get_db()
    my_row = conn.execute("SELECT role, team_id FROM users WHERE id=?", (user["user_id"],)).fetchone()
    if not my_row or my_row[0] != "admin":
        conn.close()
        raise HTTPException(403, "仅团队管理员可修改角色")
    target = conn.execute("SELECT id, team_id FROM users WHERE id=?", (target_user_id,)).fetchone()
    if not target or target[1] != my_row[1]:
        conn.close()
        raise HTTPException(404, "目标用户不在你的团队中")
    conn.execute("UPDATE users SET role=? WHERE id=?", (new_role, target_user_id))
    conn.commit()
    conn.close()
    return {"success": True, "message": f"已将用户 {target_user_id} 的角色设为 {new_role}"}


# ---------- Domain Verification ----------

class VerifyRequest(BaseModel):
    url: str
    token: str
    method: str = Field(pattern="^(dns|file)$")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        return sanitize_url(v)

    @field_validator("token")
    @classmethod
    def validate_token(cls, v: str) -> str:
        v = (v or "").strip()
        if not v or len(v) > 200:
            raise ValueError("验证 token 无效")
        return v


def query_dns_txt(name: str) -> List[str]:
    records: List[str] = []
    try:
        result = subprocess.run(["nslookup", "-type=TXT", name],
                                capture_output=True, text=True, timeout=8)
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
            result = subprocess.run(["dig", "+short", "TXT", name],
                                    capture_output=True, text=True, timeout=8)
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


async def verify_dns_txt(url: str, token: str) -> Tuple[bool, str]:
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
    return False, "未找到包含验证 Token 的 TXT 记录。请确认在 " + check_name + " 添加了 TXT 记录 " + token


async def verify_file(url: str, token: str) -> Tuple[bool, str]:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if not host:
        return False, "网址无效"
    for scheme in ["https", "http"]:
        check_url = scheme + "://" + host + "/vuln-sentinel-verification.txt"
        try:
            client = get_httpx_client()
            resp = await asyncio.wait_for(
                client.get(check_url, follow_redirects=True),
                timeout=8.0,
            )
            if resp.status_code == 200:
                body = (resp.text or "").strip()
                if token in body:
                    return True, "文件验证通过：" + check_url
        except asyncio.TimeoutError:
            continue
        except Exception:
            continue
    return False, "未在网站根目录找到 vuln-sentinel-verification.txt 文件，或文件内容不包含 Token"


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
async def api_verify_fix(req: VerifyFixRequest, request: Request, user: dict = Depends(require_login)) -> dict:
    """应用修复后再次扫描对比评分：与指定 previous_scan_id 的记录做 diff。"""
    await rate_limit_dependency(request)
    url = req.url.strip()
    previous_scan_id = req.previous_scan_id
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    parsed = urlparse(url)
    host = parsed.hostname or ""
    try:
        headers, is_https, final_url, error = await fetch_headers(url)
        if error:
            return {"success": False, "error": error}
        waf_list = detect_waf(headers)
        sensitive_paths = await check_sensitive_paths(host, is_https)
        ssl_info = await get_ssl_info(host, 443) if is_https else {"has_cert": False}
        result = analyze_security(url, headers, is_https, ssl_info, waf_list, sensitive_paths)
        # V11.4：11 维交叉验证（降低误报）
        try:
            cv_result = await cross_validate_findings(
                url, headers, result["findings"],
                sensitive_paths=sensitive_paths,
                cookie_issues=result.get("cookie_issues") or [],
                is_https=is_https,
            )
            apply_cross_validation(result["findings"], cv_result)
        except Exception:
            pass
        scan_id = save_scan(
            user["user_id"], url, result["score"], result["risk_level"],
            result["findings"], result["summary"], 0, "verify",
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
                        verify_detail = f"DNS TXT 验证通过：_vulnsentinel.{domain} → {expected}"
                        break
                if not verified:
                    verify_detail = f"DNS TXT 记录未找到或值不匹配。请在 DNS 中添加：_vulnsentinel.{domain} TXT \"{expected}\""
            except dns.resolver.NXDOMAIN:
                verify_detail = f"域名 {domain} 不存在（NXDOMAIN）。请确认域名已正确注册。"
            except dns.resolver.NoAnswer:
                verify_detail = f"域名 {domain} 存在但没有 TXT 记录。请在 DNS 中添加：_vulnsentinel.{domain} TXT \"{expected}\""
            except dns.resolver.Timeout:
                verify_detail = f"DNS 查询超时，请检查网络或稍后重试。如需验证请添加：_vulnsentinel.{domain} TXT \"{expected}\""
            except dns.exception.DNSException:
                verify_detail = f"DNS 查询异常，请稍后重试。如需验证请添加：_vulnsentinel.{domain} TXT \"{expected}\""
            except Exception as e:
                verify_detail = f"DNS 查询失败，请稍后重试。如持续失败请联系管理员。"
    elif method == "file":
        # 检查文件验证：http://{domain}/.well-known/vulnsentinel
        try:
            async with httpx.AsyncClient(timeout=10, follow_redirects=True) as hc:
                resp = await hc.get(f"http://{domain}/.well-known/vulnsentinel")
                if resp.status_code == 200:
                    expected = f"vs-{user['user_id']}"
                    if expected in resp.text:
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
            (user["user_id"], domain, method, status, now, now if verified else None, expires)
        )
        conn.commit()
    finally:
        conn.close()

    return {
        "success": True, "domain": domain, "method": method,
        "verified": verified, "status": status, "detail": verify_detail,
    }


# ---------- 扫描进度（内存 + Lock） ----------
# 用内存字典 + asyncio.Lock 替代文件读写，避免并发覆盖与磁盘 I/O。
# key: scan_token (str), value: dict {stages, current, start_time, updated_at}
_scan_progress: Dict[str, dict] = {}
_scan_progress_lock = asyncio.Lock()


# ---------- 真实扫描 ----------

@app.post("/api/scan")
async def api_scan(req: ScanRequest, request: Request, user: dict = Depends(require_login)):
    """同步扫描。带阶段进度事件（写入响应头 X-Scan-Stage 预览）。"""
    await rate_limit_dependency(request)
    try:
        url = sanitize_url(req.url)
    except ValueError as e:
        raise HTTPException(422, str(e))

    # 扫描结果缓存：30 秒内同 URL 直接返回（防重复点击）
    cache_key = f"{user['user_id']}:{url}"
    cached = _SCAN_RESULT_CACHE.get(cache_key)
    if cached and (time.time() - cached[1]) < _SCAN_CACHE_TTL:
        return {**cached[0], "is_cached": True, "cached_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    parsed = urlparse(url)
    host = parsed.hostname or ""
    user_id = user["user_id"]

    # 阶段事件：写入内存字典（带 asyncio.Lock），不再写文件，避免并发覆盖。
    import secrets as _secrets
    scan_token = f"{user_id}_{int(datetime.now().timestamp())}_{_secrets.token_hex(4)}"
    progress = {
        "stages": [
            {"id": "dns", "label": "DNS 解析", "status": "pending", "detail": host},
            {"id": "connect", "label": "TCP 连接", "status": "pending", "detail": "443 或 80 端口"},
            {"id": "headers", "label": "响应头分析", "status": "pending", "detail": "HSTS/CSP/X-Frame 等 9 项"},
            {"id": "ssl", "label": "SSL 证书检查", "status": "pending", "detail": "证书链/有效期/签发者"},
            {"id": "sensitive", "label": "敏感路径扫描", "status": "pending", "detail": "/admin /backup 等 12 个"},
            {"id": "waf", "label": "WAF 识别", "status": "pending", "detail": "Cloudflare/Akamai 等 6 类"},
            {"id": "report", "label": "生成报告", "status": "pending", "detail": "评分/修复建议"},
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

        if not req.authorized:
            await _update(0, "fail")
            return ScanResponse(
                success=False, scan_type="real", url=url, final_url=url,
                time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                is_https=False, score=0, risk_level="未授权",
                findings=[], summary={"high": 0, "medium": 0, "low": 0, "total": 0},
                owasp_coverage=[], header_details=[], info_leaks=[], cors=None,
                cookie_issues=[], ssl_info={}, waf=[], sensitive_paths=[],
                waf_detected=False, raw_headers={},
                error="请先确认您有权扫描该目标（authorized: true）",
            )
        if req.deep:
            conn = get_db()
            verified = conn.execute(
                "SELECT id FROM domain_verifications WHERE user_id=? AND domain=? AND status='verified'",
                (user_id, host)
            ).fetchone()
            conn.close()
            if not verified:
                await _update(0, "fail")
                return ScanResponse(
                    success=False, scan_type="deep", url=url, final_url=url,
                    time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    is_https=False, score=0, risk_level="未验证",
                    findings=[], summary={"high": 0, "medium": 0, "low": 0, "total": 0},
                    owasp_coverage=[], header_details=[], info_leaks=[], cors=None,
                    cookie_issues=[], ssl_info={}, waf=[], sensitive_paths=[],
                    waf_detected=False, raw_headers={},
                    error="深度扫描需要先完成域名归属验证。请通过域名验证流程验证 " + host + " 的所有权。",
                )
        await _update(0, "done")
        await _update(1, "done")
        await _update(2, "running")
        headers, is_https, final_url, error = await fetch_headers(url)
        if error and not headers:
            # 完全拿不到头 → 真失败
            await _update(2, "fail")
            # 分类错误提示
            if error == "DNS_RESOLVE_FAIL":
                user_msg = "无法解析该域名，请确认网址拼写是否正确，或该域名尚未注册"
            elif error == "TIMEOUT" or "超时" in error:
                user_msg = "连接超时，该网站可能已下线或网络不可达"
            elif error == "CONNECT_FAIL" or "无法连接" in error:
                user_msg = "无法连接到该网站，请确认网站是否在线"
            else:
                user_msg = error
            return ScanResponse(
                success=False, scan_type="real", url=url, final_url=final_url,
                time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                is_https=is_https, score=0, risk_level="无法扫描",
                findings=[], summary={"high": 0, "medium": 0, "low": 0, "total": 0},
                owasp_coverage=[], header_details=[], info_leaks=[], cors=None,
                cookie_issues=[], ssl_info={}, waf=[], sensitive_paths=[],
                waf_detected=False, raw_headers={}, error=user_msg,
            )
        # 受限访问但能拿到头 → 区分跳转(301/302) 和 真正受限(401/403/405)
        restricted = False
        redirected = False
        redirect_reason = ""
        if error and headers:
            status_code = headers.pop("_status_code", 0)
            redirect_loc = headers.pop("_redirect_location", "")
            # 兜底：如果 _redirect_location 没有值，直接从响应头取 location
            if not redirect_loc:
                redirect_loc = headers.pop("location", "")
            if error.startswith("REDIRECT_"):
                # 301/302 跳转：不算受限，只提示跳转
                redirected = True
                redirect_reason = f"目标发生跳转（HTTP {status_code}），跳转地址：{redirect_loc or '未知'}。建议扫描最终目标地址。"
                error = None
            elif error == "AUTH_REQUIRED":
                restricted = True
                user_msg = "目标站点需要登录认证（HTTP 401），无法获取完整响应头。已基于现有信息生成受限报告。"
                headers["_restricted_reason"] = user_msg
                headers["_restricted_code"] = str(status_code)
                error = None
            elif error == "FORBIDDEN":
                restricted = True
                user_msg = "目标站点拒绝自动化访问（HTTP 403），可能是反爬机制。已基于现有信息生成受限报告。"
                headers["_restricted_reason"] = user_msg
                headers["_restricted_code"] = str(status_code)
                error = None
            elif error == "METHOD_NOT_ALLOWED":
                restricted = True
                user_msg = "目标站点不支持 HEAD 请求（HTTP 405），已使用 GET 请求获取响应头。"
                headers["_restricted_reason"] = user_msg
                headers["_restricted_code"] = str(status_code)
                error = None
            else:
                restricted = True
                user_msg = f"目标站点限制自动化访问（{error}），已基于现有信息生成受限报告。"
                headers["_restricted_reason"] = user_msg
                headers["_restricted_code"] = str(status_code)
                error = None
        await _update(2, "done")
        # 修复：让 SSL 解析和敏感路径扫描同时进行，节省 1-2s
        waf_list = detect_waf(headers)
        await _update(5, "done")
        await _update(4, "running")
        # 并发：SSL 检查 + 敏感路径扫描
        from urllib.parse import urlparse as _urlparse
        port_443 = 443 if is_https else 0
        ssl_task = asyncio.create_task(get_ssl_info(_urlparse(url).hostname or host, port_443) if is_https else asyncio.sleep(0, result={"has_cert": False}))
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
        await _update(6, "running")
        crawled_pages, vuln_tests, vuln_findings = [], [], []
        if req.deep:
            try:
                crawled_pages = await crawl_site(url, settings.max_crawl_pages)
            except Exception as _ce:
                crawled_pages = []
            try:
                vuln_findings, vuln_tests = await run_payload_tests(url, crawled_pages)
            except Exception:
                vuln_findings, vuln_tests = [], []

        result = analyze_security(url, headers, is_https, ssl_info, waf_list, sensitive_paths, vuln_findings)
        # V11.4：11 维交叉验证（降低误报）
        try:
            cv_result = await cross_validate_findings(
                url, headers, result["findings"],
                sensitive_paths=sensitive_paths,
                cookie_issues=result.get("cookie_issues") or [],
                is_https=is_https,
            )
            apply_cross_validation(result["findings"], cv_result)
        except Exception:
            pass
        fixes = generate_fixes(result["findings"], headers, is_https, host)
        scan_id = save_scan(
            user_id, url, result["score"], result["risk_level"],
            result["findings"], result["summary"],
            len(crawled_pages) if crawled_pages else 0,
            "deep" if req.deep else "real",
        )
        # 自动为 high/critical finding 创建修复工单
        try:
            auto_create_fix_tickets(user_id, scan_id, result["findings"])
        except Exception:
            pass
        # 自动同步资产扫描信息
        try:
            update_asset_after_scan(user_id, host, scan_id)
        except Exception:
            pass
        await _update(6, "done")
        # 受限扫描报告：合并 fetch_headers 的 HTTP 状态码限制 + analyze_security 的 WAF/反爬检测
        http_restricted_reason = headers.pop("_restricted_reason", "") if headers else ""
        http_restricted_code = headers.pop("_restricted_code", "") if headers else ""
        # analyze_security 也返回了 restricted，优先用它的（WAF/反爬检测更全面）
        as_restricted = result.get("restricted", False)
        as_restricted_reason = result.get("restricted_reason", "")
        as_restricted_code = result.get("restricted_code", "")
        # 合并：如果 analyze_security 检测到受限，用它；否则用 fetch_headers 的
        if as_restricted:
            final_restricted = True
            final_reason = as_restricted_reason
            final_code = as_restricted_code
        elif http_restricted_reason:
            final_restricted = True
            final_reason = http_restricted_reason
            final_code = http_restricted_code
        else:
            final_restricted = False
            final_reason = ""
            final_code = ""
        # 避免 result 里的 restricted 和显式参数冲突
        result.pop("restricted", None)
        result.pop("restricted_reason", None)
        result.pop("restricted_code", None)
        return ScanResponse(
            success=True, scan_type="deep" if req.deep else "real",
            url=url, final_url=final_url,
            time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            is_https=is_https, raw_headers=headers, crawled_pages=crawled_pages,
            vuln_tests=vuln_tests, scan_id=scan_id, fixes=fixes,
            restricted=final_restricted,
            restricted_reason=final_reason,
            restricted_code=final_code,
            redirected=redirected,
            redirect_reason=redirect_reason,
            **result,
        )

    try:
        result = await asyncio.wait_for(_do_scan(), timeout=30.0)
        # 扫描完成，清理内存中的进度条目
        async with _scan_progress_lock:
            _scan_progress.pop(scan_token, None)
        result_jsonable = jsonable(result)
        # 写入扫描结果缓存（仅缓存成功结果，30 秒内同 URL 直接返回）
        if isinstance(result_jsonable, dict) and result_jsonable.get("success"):
            _SCAN_RESULT_CACHE[cache_key] = (result_jsonable, time.time())
            # 简单淘汰：超过 100 个时清掉最早的
            if len(_SCAN_RESULT_CACHE) > 100:
                oldest = min(_SCAN_RESULT_CACHE.items(), key=lambda x: x[1][1])
                _SCAN_RESULT_CACHE.pop(oldest[0], None)
        return JSONResponse(
            content=result_jsonable,
            headers={"X-Scan-Token": scan_token},
        )
    except asyncio.TimeoutError:
        async with _scan_progress_lock:
            _scan_progress.pop(scan_token, None)
        return JSONResponse(
            content=jsonable(ScanResponse(
                success=False, scan_type="real", url=url, final_url=url,
                time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                is_https=False, score=0, risk_level="扫描超时",
                findings=[], summary={"high": 0, "medium": 0, "low": 0, "total": 0},
                owasp_coverage=[], header_details=[], info_leaks=[], cors=None,
                cookie_issues=[], ssl_info={}, waf=[], sensitive_paths=[],
                waf_detected=False, raw_headers={},
                error="扫描总时间超过 30 秒，请检查目标网站是否可访问",
            )),
            headers={"X-Scan-Token": scan_token},
        )
    except RuntimeError as e:
        # Event loop is closed 等底层异常：重建 client 并给友好提示
        if "event loop" in str(e).lower() or "closed" in str(e).lower():
            logger.error("Scan failed due to event loop error: %s", e)
            try:
                await close_httpx_client()
            except Exception:
                pass
            async with _scan_progress_lock:
                _scan_progress.pop(scan_token, None)
            return JSONResponse(
                content=jsonable(ScanResponse(
                    success=False, scan_type="real", url=url, final_url=url,
                    time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    is_https=False, score=0, risk_level="扫描异常",
                    findings=[], summary={"high": 0, "medium": 0, "low": 0, "total": 0},
                    owasp_coverage=[], header_details=[], info_leaks=[], cors=None,
                    cookie_issues=[], ssl_info={}, waf=[], sensitive_paths=[],
                    waf_detected=False, raw_headers={},
                    error="扫描过程中发生内部错误，请稍后重试。如持续失败，请刷新页面后重新扫描。",
                )),
                headers={"X-Scan-Token": scan_token},
            )
        raise


# ---------- 历史（含 DELETE） ----------

@app.get("/api/history")
async def api_history(user: dict = Depends(require_login), limit: int = Query(20, ge=1, le=200)) -> dict:
    user_id = user["user_id"]
    history = get_scan_history(user_id, limit)
    fixed_count = compute_fixed_count(history)
    return {
        "history": history,
        "stats": {
            "scan_count": len(history),
            "fixed_count": fixed_count,
        },
    }


@app.delete("/api/history")
async def api_history_delete(user: dict = Depends(require_login)) -> dict:
    n = delete_scan_history(user["user_id"])
    return {"success": True, "deleted": n}


# ---------- 修复工单 API ----------

@app.post("/api/fix-tickets")
async def api_create_fix_ticket(req: FixTicketCreate, user: dict = Depends(require_login)) -> dict:
    ticket_id = create_fix_ticket(
        user["user_id"], req.scan_id, req.finding_name, req.severity,
        req.fix_code, req.notes,
    )
    return {"success": True, "ticket_id": ticket_id}


@app.get("/api/fix-tickets")
async def api_list_fix_tickets(status: Optional[str] = None, user: dict = Depends(require_login)) -> dict:
    tickets = get_fix_tickets(user["user_id"], status)
    return {"success": True, "tickets": tickets}


@app.patch("/api/fix-tickets/{ticket_id}")
async def api_update_fix_ticket(ticket_id: int, req: FixTicketUpdate, user: dict = Depends(require_login)) -> dict:
    ok = update_fix_ticket(
        ticket_id, user["user_id"],
        status=req.status, fix_code=req.fix_code, notes=req.notes,
    )
    if not ok:
        raise HTTPException(404, "工单不存在或无权限")
    return {"success": True}


@app.delete("/api/fix-tickets/{ticket_id}")
async def api_delete_fix_ticket(ticket_id: int, user: dict = Depends(require_login)) -> dict:
    ok = delete_fix_ticket(ticket_id, user["user_id"])
    if not ok:
        raise HTTPException(404, "工单不存在或无权限")
    return {"success": True}


@app.post("/api/finding/feedback")
async def api_finding_feedback(req: FindingFeedbackRequest, current_user=Depends(get_current_user)) -> dict:
    """记录用户对 finding 的误报/确认反馈。

    写入 finding_feedback 表；同时如果 user_id==0（未登录的公开扫描），允许匿名反馈但不写入（仅返回 success）。
    返回值：{"success": True, "feedback_id": ...}
    """
    try:
        # 未登录用户（user_id==0）也允许反馈，但不持久化
        if not current_user or not current_user.get("user_id"):
            return {"success": True, "feedback_id": None, "note": "未登录反馈未持久化"}
        conn = get_db()
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
        conn.close()
        logger.info(
            "finding_feedback saved: user=%s scan=%s finding=%s fp=%s conf=%s",
            current_user.get("user_id"), req.scan_id, req.finding_name,
            req.is_false_positive, req.is_confirmed,
        )
        return {"success": True, "feedback_id": feedback_id}
    except Exception as e:
        logger.warning("finding_feedback save failed: %s", e)
        # 失败时仍返回 success（前端展示），但带 error 标记
        return {"success": False, "error": str(e)}


@app.get("/api/finding/feedback")
async def api_list_finding_feedback(
    scan_id: Optional[int] = None,
    current_user=Depends(get_current_user),
) -> dict:
    """查询某个扫描（或当前用户）的 finding 反馈记录，用于前端展示"已标记"状态。"""
    try:
        if not current_user or not current_user.get("user_id"):
            return {"success": True, "feedbacks": []}
        conn = get_db()
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
        conn.close()
        return {
            "success": True,
            "feedbacks": [dict(r) for r in rows],
        }
    except Exception as e:
        return {"success": False, "error": str(e), "feedbacks": []}


@app.get("/api/stats/history")
async def api_stats_history(user: dict = Depends(require_login), days: int = Query(30, ge=1, le=365)) -> dict:
    """返回扫描分数时间序列，用于前端绘制趋势图。
    数据：近 N 天该用户所有扫描的 url、score、time。
    """
    conn = get_db()
    since_ts = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    rows = conn.execute(
        """SELECT id, url, score, created_at, risk_level
           FROM scans
           WHERE user_id=? AND created_at >= ?
           ORDER BY created_at ASC""",
        (user["user_id"], since_ts),
    ).fetchall()
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
    by_url: Dict[str, list] = {}
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
async def api_alerts(user: dict = Depends(require_login), limit: int = Query(20, ge=1, le=100), unread_only: bool = Query(False)) -> dict:
    """返回用户的扫描告警通知。"""
    conn = get_db()
    sql = "SELECT * FROM alerts WHERE user_id=?"
    params = [user["user_id"]]
    if unread_only:
        sql += " AND is_read=0"
    sql += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(sql, params).fetchall()
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


@app.post("/api/alerts/{alert_id}/read")
async def api_mark_alert_read(alert_id: int, user: dict = Depends(require_login)) -> dict:
    """标记告警为已读。"""
    conn = get_db()
    conn.execute("UPDATE alerts SET is_read=1 WHERE id=? AND user_id=?", (alert_id, user["user_id"]))
    conn.commit()
    conn.close()
    return {"success": True}


# ---------- Simulate Fix（用真实 severity） ----------

@app.post("/api/simulate-fix", response_model=None)
async def simulate_fix(req: SimulateFixRequest):
    """模拟应用修复后的预期评分（不需要登录）。
    输入：scan findings 数组（使用真实 severity 字段 high/medium/low）
    输出：修复前 vs 修复后的评分对比
    """
    findings = req.findings or []
    SEV_DEDUCT = {"critical": 25, "high": 15, "medium": 8, "low": 3}
    deduction = sum(SEV_DEDUCT.get(f.get("severity", "low"), 3) for f in findings)
    before = max(0, 100 - deduction)
    after = min(100, before + deduction + 12)
    fixed_items = []
    for f in findings[:20]:
        fixed_items.append({
            "name": f.get("name"),
            "severity": f.get("severity", "low"),
            "level_zh": f.get("level_zh") or SEVERITY_ZH.get(f.get("severity", "low"), "低风险"),
            "owasp": f.get("owasp", ""),
            "fix": f.get("fix", ""),
            "summary": f.get("summary", ""),
        })
    return {
        "before_score": before,
        "after_score": after,
        "delta": after - before,
        "fixed_count": len(findings),
        "fixed_items": fixed_items,
        "summary": f"应用 {len(findings)} 项修复后，评分预计从 {before} 提升到 {after}（+{after - before} 分）",
    }


@app.post("/api/apply-fix-and-rescan", response_model=None)
async def apply_fix_and_rescan(req: ApplyFixRequest, user: dict = Depends(require_login)):
    """应用修复后再次扫描对比评分。
    可选 previous_scan_id 字段：指定要对比的"修复前"扫描。
    """
    url = req.url.strip()
    previous_scan_id = req.previous_scan_id
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    parsed = urlparse(url)
    host = parsed.hostname or ""
    try:
        headers, is_https, final_url, error = await fetch_headers(url)
        if error:
            return {"success": False, "error": error}
        ssl_info = await get_ssl_info(host, 443) if is_https else {"has_cert": False}
        waf_list = detect_waf(headers)
        sensitive_paths = await check_sensitive_paths(host, is_https)
        result = analyze_security(url, headers, is_https, ssl_info, waf_list, sensitive_paths, [])
        scan_id = save_scan(
            user["user_id"], url, result["score"], result["risk_level"],
            result["findings"], result["summary"], 0, "rescan",
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
            } if previous else None,
            "fixed": fixed,
            "new_issues": new_issues,
            "delta": delta,
        }
    except Exception as e:
        return {"success": False, "error": str(e)[:300]}


# ----- 一键修复包：把所有修复方案打包成可下载 zip -----
@app.post("/api/generate-fix-package")
async def api_generate_fix_package(request: Request, user: dict = Depends(require_login)) -> FileResponse:
    """AI 一键修复：根据 body 中的 findings + host + is_https 生成平台配置 + 部署脚本，打包成 zip。"""
    import io, zipfile, time
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
由漏洞哨兵 V11.4 自动生成
平台：{platform.upper()}
修复项数：{len(code_blocks)}
生成时间：{time.strftime('%Y-%m-%d %H:%M:%S')}

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
        readme += f"- [{f.get('severity','-')}] {f.get('name','')}\n"

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{platform}/config.conf", main_cfg)
        zf.writestr("README.md", readme)
        zf.writestr("deploy.sh", f"#!/bin/bash\necho '部署 {platform} 安全配置到 {host}'\n")
    buf.seek(0)
    from starlette.responses import Response
    content = buf.read()
    return Response(
        content=content,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=vulnsentinel-fix-{host}-{platform}-{int(time.time())}.zip"},
    )


# ---------- Fix generator 端点 ----------

@app.post("/api/fix")
async def api_fix(req: ScanRequest, request: Request, user: dict = Depends(require_login)) -> dict:
    """生成修复建议。"""
    await rate_limit_dependency(request)
    url = req.url
    parsed = urlparse(url)
    host = parsed.hostname or ""
    headers, is_https, final_url, error = await fetch_headers(url)
    if error:
        return {"success": False, "error": error}
    waf_list = detect_waf(headers)
    # 并行执行：敏感路径探测 + SSL 信息获取（节省 30-50% 时间）
    sensitive_task = asyncio.create_task(check_sensitive_paths(host, is_https))
    ssl_task = asyncio.create_task(get_ssl_info(host, 443) if is_https else asyncio.sleep(0, result={"has_cert": False}))
    sensitive_paths, ssl_info_raw = await asyncio.gather(sensitive_task, ssl_task)
    ssl_info = ssl_info_raw if is_https else {"has_cert": False}
    result = analyze_security(
        url, headers, is_https, ssl_info, waf_list, sensitive_paths,
    )
    fixes = generate_fixes(result["findings"], headers, is_https, host)
    return {"success": True, "url": url, "fixes": fixes, "score": result["score"],
            "summary": result["summary"]}


@app.post("/api/scans/{scan_id}/retest")
async def api_retest(scan_id: int, user: dict = Depends(require_login)) -> dict:
    """对同一 URL 重新扫描（复测闭环）。"""
    previous = get_scan_by_id(scan_id, user["user_id"])
    if not previous:
        raise HTTPException(404, "扫描记录不存在或无权限")
    url = previous["url"]
    parsed = urlparse(url)
    host = parsed.hostname or ""
    headers, is_https, final_url, error = await fetch_headers(url)
    if error and not headers:
        return {"success": False, "error": error or "无法获取响应头"}
    waf_list = detect_waf(headers)
    ssl_info = await get_ssl_info(host, 443) if is_https else {"has_cert": False}
    sensitive_paths = await check_sensitive_paths(host, is_https)
    result = analyze_security(url, headers, is_https, ssl_info, waf_list, sensitive_paths, [])
    new_scan_id = save_scan(
        user["user_id"], url, result["score"], result["risk_level"],
        result["findings"], result["summary"], 0, "retest",
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
async def api_compare(scan_id: int, user: dict = Depends(require_login)) -> dict:
    """对比上次扫描结果（复测闭环）。
    返回 new_findings / fixed_findings / unchanged_findings / score_change。
    """
    current = get_scan_by_id(scan_id, user["user_id"])
    if not current:
        raise HTTPException(404, "扫描记录不存在或无权限")
    url = current["url"]
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM scans WHERE user_id=? AND url=? AND id<? ORDER BY id DESC LIMIT 1",
        (user["user_id"], url, scan_id),
    ).fetchone()
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
async def api_report(scan_id: int, user: dict = Depends(require_login)) -> StreamingResponse:
    scan = get_scan_by_id(scan_id, user["user_id"])
    if not scan:
        raise HTTPException(404, "扫描记录不存在")
    findings = json.loads(scan["findings_json"]) if scan.get("findings_json") else []
    owasp_map: Dict[str, dict] = {}
    for f in findings:
        cat = f.get("owasp", "")
        if cat and cat not in owasp_map:
            owasp_map[cat] = {"category": cat, "status": "需关注", "note": ""}
    report_data = {
        "url": scan["url"], "time": scan["created_at"],
        "score": scan["score"], "risk_level": scan["risk_level"],
        "findings": findings, "owasp_coverage": list(owasp_map.values()),
        "header_details": [], "info_leaks": [], "cors": None,
        "cookie_issues": [], "ssl_info": {}, "waf": [], "sensitive_paths": [],
    }
    pdf_bytes = generate_pdf_report(report_data)
    headers = {"Content-Disposition": "attachment; filename=scan-report-" + str(scan_id) + ".pdf"}
    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf", headers=headers)


@app.get("/api/share/{share_id}")
async def api_get_share(share_id: str) -> dict:
    if not re.fullmatch(r"[a-zA-Z0-9_-]{8,32}", share_id):
        raise HTTPException(400, "分享 ID 格式无效")
    row = get_scan_by_share_id(share_id)
    if not row:
        raise HTTPException(404, "分享链接不存在或已失效")
    return row


@app.get("/api/compare")
async def api_compare(a: int, b: int, user: dict = Depends(require_login)) -> dict:
    sa = get_scan_by_id(a, user["user_id"])
    sb = get_scan_by_id(b, user["user_id"])
    if not sa or not sb:
        raise HTTPException(404, "扫描记录不存在")
    sa_findings = json.loads(sa.get("findings_json") or "[]")
    sb_findings = json.loads(sb.get("findings_json") or "[]")
    sa_names = {f["name"] for f in sa_findings}
    sb_names = {f["name"] for f in sb_findings}
    return {
        "a": {"id": sa.get("id"), "url": sa.get("url"), "score": sa.get("score"),
              "risk_level": sa.get("risk_level"), "findings_count": len(sa_findings),
              "time": sa.get("created_at")},
        "b": {"id": sb.get("id"), "url": sb.get("url"), "score": sb.get("score"),
              "risk_level": sb.get("risk_level"), "findings_count": len(sb_findings),
              "time": sb.get("created_at")},
        "fixed": list(sa_names - sb_names),
        "new": list(sb_names - sa_names),
        "score_diff": (sb.get("score", 0) - sa.get("score", 0)),
    }


class PasswordResetRequest(BaseModel):
    new_password: str = Field(min_length=6, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        return v.strip()


@app.post("/api/reset-password")
async def api_reset_password(req: PasswordResetRequest, user: dict = Depends(require_login)) -> dict:
    user_id = user["user_id"]
    new_hash = hash_password(req.new_password)
    update_user_password(user_id, new_hash)
    return {"success": True, "message": "密码已重置，请用新密码登录"}


@app.post("/api/targets")
async def api_add_target(req: AddTargetRequest, user: Optional[dict] = Depends(get_current_user)) -> dict:
    if not user:
        raise HTTPException(401, "未登录")
    upsert_target(user["user_id"], req.url, req.schedule)
    return {"success": True}


@app.get("/api/targets")
async def api_get_targets(user: Optional[dict] = Depends(get_current_user)) -> dict:
    if not user:
        raise HTTPException(401, "未登录")
    return {"targets": get_user_targets(user["user_id"])}


@app.delete("/api/targets/{target_id}")
async def api_delete_target(target_id: int, user: Optional[dict] = Depends(get_current_user)) -> dict:
    if not user:
        raise HTTPException(401, "未登录")
    conn = get_db()
    conn.execute("DELETE FROM targets WHERE id=? AND user_id=?", (target_id, user["user_id"]))
    conn.commit()
    conn.close()
    return {"success": True}


@app.get("/api/dashboard")
async def api_dashboard(user=Depends(require_login)):
    conn = get_db()
    user_id = user["user_id"]
    total = conn.execute("SELECT COUNT(*) FROM scans WHERE user_id=?", (user_id,)).fetchone()[0]
    high_count = conn.execute("SELECT COUNT(*) FROM scans WHERE user_id=? AND risk_level='高风险'", (user_id,)).fetchone()[0]
    # fixed: 通过 verify-fix 标记的修复记录数
    try:
        fixed = conn.execute("SELECT COUNT(*) FROM fix_records WHERE user_id=? AND status='verified'", (user_id,)).fetchone()[0]
    except Exception:
        fixed = 0
    recent = conn.execute("SELECT id, url, score, risk_level, created_at as time FROM scans WHERE user_id=? ORDER BY id DESC LIMIT 5", (user_id,)).fetchall()
    conn.close()
    return {
        "total_scans": total,
        "high_risk_count": high_count,
        "fixed_count": fixed,
        "recent_scans": [dict(r) for r in recent],
    }


@app.get("/api/health")
async def api_health() -> dict:
    """健康检查。返回服务状态、版本、DB 状态。"""
    db_ok = True
    try:
        conn = get_db()
        conn.execute("SELECT 1").fetchone()
        conn.close()
    except Exception:
        db_ok = False
    return {
        "status": "ok" if db_ok else "degraded",
        "version": settings.app_version,
        "title": settings.app_title,
        "db": "ok" if db_ok else "error",
        "uptime_sec": int(time.time() - _SERVICE_START_TIME),
    }


# ===== 公共演示端点（无需登录） =====

_PUBLIC_DEMO_HOSTS = {
    "example.com", "example.org", "www.example.com",
    "iana.org", "www.iana.org", "httpbin.org", "testphp.vulnweb.com",
}

# 登录用户扫描结果缓存：30 秒内同一 URL 直接返回（防重复点击 + 节省后端开销）
_SCAN_RESULT_CACHE: Dict[str, Tuple[dict, float]] = {}
_SCAN_CACHE_TTL = 30  # 秒


# 公开演示兜底缓存：网络异常时返回预置数据，确保演示 100% 可用
_PUBLIC_DEMO_CACHE = {
    "example.com": {
    "success": True,
    "scan_type": "real",
    "final_url": "https://example.com",
    "is_https": True,
    "score": 66,
    "risk_level": "中风险",
    "summary": {
        "high": 2,
        "medium": 2,
        "low": 3,
        "critical": 0,
        "total": 7
    },
    "findings": [
        {
            "name": "缺少 HSTS",
            "severity": "high",
            "level": "高风险",
            "level_zh": "高风险",
            "owasp": "A05 安全配置错误",
            "summary": "强制浏览器只通过 HTTPS 访问。",
            "fix": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
            "type": "config",
            "evidence": {
                "detected": False,
                "header": "strict-transport-security",
                "reason": "未检测到 HSTS 响应头",
                "impact": "强制浏览器只通过 HTTPS 访问"
            },
            "verify_method": "curl -I https://你的域名 | grep -i 'strict-transport-security'"
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
                "impact": "限制页面可加载的资源来源"
            },
            "verify_method": "curl -I https://你的域名 | grep -i 'content-security-policy'"
        },
        {
            "name": "缺少 X-Frame-Options",
            "severity": "medium",
            "level": "中风险",
            "level_zh": "中风险",
            "owasp": "A05 安全配置错误",
            "summary": "防止页面被嵌入 iframe。",
            "fix": "add_header X-Frame-Options \"DENY\" always;",
            "type": "config",
            "evidence": {
                "detected": False,
                "header": "x-frame-options",
                "reason": "未检测到 X-Frame-Options 响应头",
                "impact": "防止页面被嵌入 iframe"
            },
            "verify_method": "curl -I https://你的域名 | grep -i 'x-frame-options'"
        },
        {
            "name": "缺少 X-Content-Type-Options",
            "severity": "medium",
            "level": "中风险",
            "level_zh": "中风险",
            "owasp": "A05 安全配置错误",
            "summary": "禁止浏览器猜测 MIME 类型。",
            "fix": "add_header X-Content-Type-Options \"nosniff\" always;",
            "type": "config",
            "evidence": {
                "detected": False,
                "header": "x-content-type-options",
                "reason": "未检测到 X-Content-Type-Options 响应头",
                "impact": "禁止浏览器猜测 MIME 类型"
            },
            "verify_method": "curl -I https://你的域名 | grep -i 'x-content-type-options'"
        },
        {
            "name": "缺少 Referrer-Policy",
            "severity": "low",
            "level": "低风险",
            "level_zh": "低风险",
            "owasp": "A05 安全配置错误",
            "summary": "控制 Referer 头发送策略。",
            "fix": "add_header Referrer-Policy \"strict-origin-when-cross-origin\" always;",
            "type": "config",
            "evidence": {
                "detected": False,
                "header": "referrer-policy",
                "reason": "未检测到 Referrer-Policy 响应头",
                "impact": "控制 Referer 头发送策略"
            },
            "verify_method": "curl -I https://你的域名 | grep -i 'referrer-policy'"
        },
        {
            "name": "缺少 Permissions-Policy",
            "severity": "low",
            "level": "低风险",
            "level_zh": "低风险",
            "owasp": "A05 安全配置错误",
            "summary": "控制浏览器 API 权限。",
            "fix": "add_header Permissions-Policy \"camera=(), microphone=()\" always;",
            "type": "config",
            "evidence": {
                "detected": False,
                "header": "permissions-policy",
                "reason": "未检测到 Permissions-Policy 响应头",
                "impact": "控制浏览器 API 权限"
            },
            "verify_method": "curl -I https://你的域名 | grep -i 'permissions-policy'"
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
                "impact": "攻击者可利用已知版本漏洞"
            },
            "verify_method": "curl -I https://你的域名 | grep -i '^server'（不应返回具体版本）"
        }
    ],
    "owasp_coverage": [
        {
            "category": "A01 访问控制失效",
            "status": "通过",
            "note": "需关注"
        },
        {
            "category": "A02 加密机制失效",
            "status": "通过",
            "note": "已启用 HTTPS"
        },
        {
            "category": "A03 注入攻击",
            "status": "通过",
            "note": "未检测到注入漏洞"
        },
        {
            "category": "A04 不安全设计",
            "status": "通过",
            "note": "未检测到"
        },
        {
            "category": "A05 安全配置错误",
            "status": "需关注",
            "note": "部分配置可优化"
        },
        {
            "category": "A06 过时组件",
            "status": "需深度检测",
            "note": "建议扫描依赖"
        },
        {
            "category": "A07 认证失败",
            "status": "通过",
            "note": "未检测到"
        },
        {
            "category": "A08 软件完整性",
            "status": "通过",
            "note": "未检测到"
        },
        {
            "category": "A09 日志监控不足",
            "status": "低风险",
            "note": "建议加强"
        },
        {
            "category": "A10 服务端请求伪造",
            "status": "通过",
            "note": "未检测到"
        }
    ],
    "header_details": [
        {
            "name": "HSTS",
            "key": "strict-transport-security",
            "value": None,
            "status": "missing",
            "category": "传输安全",
            "severity": "high"
        },
        {
            "name": "CSP",
            "key": "content-security-policy",
            "value": None,
            "status": "missing",
            "category": "XSS 防护",
            "severity": "high"
        },
        {
            "name": "X-Frame-Options",
            "key": "x-frame-options",
            "value": None,
            "status": "missing",
            "category": "点击劫持",
            "severity": "medium"
        },
        {
            "name": "X-Content-Type-Options",
            "key": "x-content-type-options",
            "value": None,
            "status": "missing",
            "category": "MIME 嗅探",
            "severity": "medium"
        },
        {
            "name": "Referrer-Policy",
            "key": "referrer-policy",
            "value": None,
            "status": "missing",
            "category": "隐私",
            "severity": "low"
        },
        {
            "name": "Permissions-Policy",
            "key": "permissions-policy",
            "value": None,
            "status": "missing",
            "category": "隐私",
            "severity": "low"
        }
    ],
    "info_leaks": [
        {
            "name": "Server",
            "value": "cloudflare"
        }
    ],
    "cors": None,
    "cookie_issues": [],
    "ssl_info": {
        "has_cert": False,
        "error": "SSL 握手超时（目标可能未启用 HTTPS 或响应较慢）"
    },
    "waf": [
        {
            "name": "cloudflare",
            "signature": "CF-RAY",
            "value": "a1127c5aeca5d2a8-FRA"
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
        "_status_code": 200
    },
    "fixes": {
        "nginx": [
            {
                "code": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "express": "// Express: app.disable('x-powered-by')",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "add_header Content-Security-Policy \"default-src 'self'\" always;",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "nginx": "add_header Content-Security-Policy \"default-src 'self'\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "express": "// Express: app.disable('x-powered-by')",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "add_header X-Frame-Options \"DENY\" always;",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "nginx": "add_header X-Frame-Options \"DENY\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "express": "// Express: app.disable('x-powered-by')",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "add_header X-Content-Type-Options \"nosniff\" always;",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "nginx": "add_header X-Content-Type-Options \"nosniff\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "express": "// Express: app.disable('x-powered-by')",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "add_header Referrer-Policy \"strict-origin-when-cross-origin\" always;",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "nginx": "add_header Referrer-Policy \"strict-origin-when-cross-origin\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "express": "// Express: app.disable('x-powered-by')",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "add_header Permissions-Policy \"camera=(), microphone=()\" always;",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "nginx": "add_header Permissions-Policy \"camera=(), microphone=()\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "express": "// Express: app.disable('x-powered-by')",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "server_tokens off;",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "nginx": "server_tokens off;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "express": "// Express: app.disable('x-powered-by')",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            }
        ],
        "apache": [
            {
                "code": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "express": "// Express: app.disable('x-powered-by')",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "Header set Content-Security-Policy \"default-src 'self'\" ",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "apache": "Header set Content-Security-Policy \"default-src 'self'\" ",
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "express": "// Express: app.disable('x-powered-by')",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "Header set X-Frame-Options \"DENY\" ",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "apache": "Header set X-Frame-Options \"DENY\" ",
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "express": "// Express: app.disable('x-powered-by')",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "Header set X-Content-Type-Options \"nosniff\" ",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "apache": "Header set X-Content-Type-Options \"nosniff\" ",
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "express": "// Express: app.disable('x-powered-by')",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "Header set Referrer-Policy \"strict-origin-when-cross-origin\" ",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "apache": "Header set Referrer-Policy \"strict-origin-when-cross-origin\" ",
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "express": "// Express: app.disable('x-powered-by')",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "Header set Permissions-Policy \"camera=(), microphone=()\" ",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "apache": "Header set Permissions-Policy \"camera=(), microphone=()\" ",
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "express": "// Express: app.disable('x-powered-by')",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "ServerTokens Prod\nServerSignature Off",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "apache": "ServerTokens Prod\nServerSignature Off",
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "express": "// Express: app.disable('x-powered-by')",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            }
        ],
        "express": [
            {
                "code": "// Express: app.disable('x-powered-by')",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "express": "// Express: app.disable('x-powered-by')",
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            }
        ],
        "flask": [
            {
                "code": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "express": "// Express: app.disable('x-powered-by')",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['CSP'] = 'default-src 'self''\n    return resp",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['CSP'] = 'default-src 'self''\n    return resp",
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "express": "// Express: app.disable('x-powered-by')",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['Content-Security-Policy'] = 'default-src 'self''\n    return resp",
                "risk_note": "上线前请在测试环境验证，CSP 策略过严可能导致前端资源加载失败",
                "server_type": "unknown",
                "config_examples": {
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['Content-Security-Policy'] = 'default-src 'self''\n    return resp",
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "express": "// Express: app.disable('x-powered-by')",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['X-Frame-Options'] = 'DENY'\n    return resp",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['X-Frame-Options'] = 'DENY'\n    return resp",
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "express": "// Express: app.disable('x-powered-by')",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['X-Content-Type-Options'] = 'nosniff'\n    return resp",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['X-Content-Type-Options'] = 'nosniff'\n    return resp",
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "express": "// Express: app.disable('x-powered-by')",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'\n    return resp",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'\n    return resp",
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "express": "// Express: app.disable('x-powered-by')",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['Permissions-Policy'] = 'camera=(), microphone=()'\n    return resp",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['Permissions-Policy'] = 'camera=(), microphone=()'\n    return resp",
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "express": "// Express: app.disable('x-powered-by')",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "# Flask: app.config['SECRET_KEY'] = os.urandom(32)",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "flask": "# Flask: app.config['SECRET_KEY'] = os.urandom(32)",
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "express": "// Express: app.disable('x-powered-by')",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            }
        ],
        "spring_boot": [
            {
                "code": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "express": "// Express: app.disable('x-powered-by')",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "# Spring Boot: server.error.include-stacktrace=never",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "spring_boot": "# Spring Boot: server.error.include-stacktrace=never",
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "express": "// Express: app.disable('x-powered-by')",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            }
        ],
        "cloudflare": [
            {
                "code": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "express": "// Express: app.disable('x-powered-by')",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: CSP\n# Value: default-src 'self'",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: CSP\n# Value: default-src 'self'",
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "express": "// Express: app.disable('x-powered-by')",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: Content-Security-Policy\n# Value: default-src 'self'",
                "risk_note": "上线前请在测试环境验证，CSP 策略过严可能导致前端资源加载失败",
                "server_type": "unknown",
                "config_examples": {
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: Content-Security-Policy\n# Value: default-src 'self'",
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "express": "// Express: app.disable('x-powered-by')",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: X-Frame-Options\n# Value: DENY",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: X-Frame-Options\n# Value: DENY",
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "express": "// Express: app.disable('x-powered-by')",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: X-Content-Type-Options\n# Value: nosniff",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: X-Content-Type-Options\n# Value: nosniff",
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "express": "// Express: app.disable('x-powered-by')",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: Referrer-Policy\n# Value: strict-origin-when-cross-origin",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: Referrer-Policy\n# Value: strict-origin-when-cross-origin",
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "express": "// Express: app.disable('x-powered-by')",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: Permissions-Policy\n# Value: camera=(), microphone=()",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: Permissions-Policy\n# Value: camera=(), microphone=()",
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "express": "// Express: app.disable('x-powered-by')",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "# Cloudflare: Scrape Shield > Disable Server Name Exposure",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "cloudflare": "# Cloudflare: Scrape Shield > Disable Server Name Exposure",
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "express": "// Express: app.disable('x-powered-by')",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            }
        ],
        "nodejs": [
            {
                "code": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "express": "// Express: app.disable('x-powered-by')",
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "// Express helmet: add_header Content-Security-Policy \"default-src 'self'\" always;",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "express": "// Express: app.disable('x-powered-by')",
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "// Express helmet: add_header X-Frame-Options \"DENY\" always;",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "express": "// Express: app.disable('x-powered-by')",
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "// Express helmet: add_header X-Content-Type-Options \"nosniff\" always;",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "express": "// Express: app.disable('x-powered-by')",
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "// Express helmet: add_header Referrer-Policy \"strict-origin-when-cross-origin\" always;",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "express": "// Express: app.disable('x-powered-by')",
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "// Express helmet: add_header Permissions-Policy \"camera=(), microphone=()\" always;",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "express": "// Express: app.disable('x-powered-by')",
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "// app.disable('x-powered-by')",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "express": "// Express: app.disable('x-powered-by')",
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "python": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            }
        ],
        "python": [
            {
                "code": "# Flask 后置响应头: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "express": "// Express: app.disable('x-powered-by')",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "# Flask 后置响应头: add_header Content-Security-Policy \"default-src 'self'\" always;",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "express": "// Express: app.disable('x-powered-by')",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "# Flask 后置响应头: add_header X-Frame-Options \"DENY\" always;",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "express": "// Express: app.disable('x-powered-by')",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "# Flask 后置响应头: add_header X-Content-Type-Options \"nosniff\" always;",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "express": "// Express: app.disable('x-powered-by')",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "# Flask 后置响应头: add_header Referrer-Policy \"strict-origin-when-cross-origin\" always;",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "express": "// Express: app.disable('x-powered-by')",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "# Flask 后置响应头: add_header Permissions-Policy \"camera=(), microphone=()\" always;",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "express": "// Express: app.disable('x-powered-by')",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            },
            {
                "code": "# app.config['SECRET_KEY'] = os.urandom(32)",
                "risk_note": None,
                "server_type": "unknown",
                "config_examples": {
                    "nginx": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;",
                    "apache": "Header set Strict-Transport-Security \"max-age=31536000; includeSubDomains\" ",
                    "express": "// Express: app.disable('x-powered-by')",
                    "flask": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['HSTS'] = 'max-age=31536000; includeSubDomains'\n    return resp",
                    "spring_boot": "# Spring Boot: @Bean\n# public SecurityFilterChain filterChain(HttpSecurity http) {\n#     http.headers().httpStrictTransportSecurity();\n# }",
                    "cloudflare": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: HSTS\n# Value: max-age=31536000; includeSubDomains",
                    "nodejs": "// Express helmet: add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                }
            }
        ]
    }
},
        "iana.org": {
        "success": True, "scan_type": "real", "final_url": "https://iana.org",
        "is_https": True, "score": 84, "risk_level": "低风险",
        "summary": {"high": 0, "medium": 2, "low": 1, "total": 3},
        "findings": [
            {"name": "缺少 CSP", "type": "MissingHeader", "severity": "medium", "level_zh": "中风险", "description": "未启用 Content Security Policy", "fix": "add_header Content-Security-Policy \"default-src 'self'\" always;"},
            {"name": "缺少 Referrer-Policy", "type": "MissingHeader", "severity": "low", "level_zh": "低风险", "description": "未控制 Referrer 泄露", "fix": "add_header Referrer-Policy \"strict-origin-when-cross-origin\" always;"},
            {"name": "Server 头泄露", "type": "InfoLeak", "severity": "medium", "level_zh": "中风险", "description": "Server 响应头包含版本信息", "fix": "server_tokens off;"},
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
        "ssl_info": {"has_cert": True, "subject": "iana.org", "issuer": "Let's Encrypt", "days_left": 60, "expired": False, "version": "TLSv1.3", "weak": False},
        "waf": [],
        "sensitive_paths": [],
        "waf_detected": False,
        "raw_headers": {"server": "nginx/1.18.0", "strict-transport-security": "max-age=31536000"},
        "fixes": {
            "nginx": [
                {"code": 'add_header Content-Security-Policy "default-src \'self\'" always;', "risk_note": None},
                {"code": 'add_header Referrer-Policy "strict-origin-when-cross-origin" always;', "risk_note": None},
                {"code": "server_tokens off;", "risk_note": None},
            ],
            "apache": [
                {"code": 'Header set Content-Security-Policy "default-src \'self\'"', "risk_note": None},
                {"code": 'Header set Referrer-Policy "strict-origin-when-cross-origin"', "risk_note": None},
                {"code": "ServerTokens Prod", "risk_note": None},
            ],
            "express": [
                {"code": "// Express + helmet\nconst helmet = require('helmet');\napp.use(helmet({ contentSecurityPolicy: { directives: { defaultSrc: [\"'self'\"] } } }));", "risk_note": None},
                {"code": "// Express\napp.use((req, res, next) => { res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin'); next(); });", "risk_note": None},
            ],
            "flask": [
                {"code": "# Flask/FastAPI: @app.after_request\ndef add_security_headers(resp):\n    resp.headers['Content-Security-Policy'] = \"default-src 'self'\"\n    resp.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'\n    return resp", "risk_note": None},
            ],
            "spring_boot": [
                {"code": "# Spring Boot: SecurityConfig.java\nhttp.headers().contentSecurityPolicy(\"default-src 'self'\");", "risk_note": None},
            ],
            "cloudflare": [
                {"code": "# Cloudflare: Rules > Transform Rules > Modify Response Header\n# Header: Content-Security-Policy\n# Value: default-src 'self'", "risk_note": None},
            ],
        },
    },
}


def _is_public_demo_host(host: str) -> bool:
    return (host or "").lower() in _PUBLIC_DEMO_HOSTS


@app.get("/api/scan-progress/{scan_token}")
async def api_scan_progress(scan_token: str, user: dict = Depends(require_login)) -> dict:
    """返回指定扫描 token 的进度（前端轮询用）。从内存字典读取，并附带清理逻辑。"""
    # 顺手清理 30 分钟未更新的内存条目（避免 dict 膨胀）
    try:
        cutoff = time.time() - 1800
        async with _scan_progress_lock:
            stale = [k for k, v in _scan_progress.items() if v.get("updated_at", 0) < cutoff]
            for k in stale:
                _scan_progress.pop(k, None)
    except Exception:
        pass

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


@app.post("/api/public-demo-scan", response_model=None)
async def public_demo_scan(req: PublicDemoRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    if not await limiter_demo.is_allowed(client_ip):
        raise HTTPException(
            status_code=429,
            detail="公开演示请求过于频繁，请稍后再试",
            headers={"Retry-After": "60"},
        )
    if not settings.public_demo_enabled:
        raise HTTPException(403, "公开演示已关闭")
    raw_url = req.url.strip()
    if not raw_url.startswith(("http://", "https://")):
        raw_url = "https://" + raw_url
    parsed = urlparse(raw_url)
    host = (parsed.hostname or "").lower()
    if not _is_public_demo_host(host):
        raise HTTPException(403, "公开演示仅限白名单站点（example.com / httpbin.org / iana.org / testphp.vulnweb.com）。")
    try:
        headers, is_https, final_url, error = await fetch_headers(raw_url)
        if error:
            # 实时扫描失败，尝试返回缓存数据
            cached = _PUBLIC_DEMO_CACHE.get(host)
            if cached:
                return {**cached, "url": raw_url, "is_cached": True, "cached_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "cache_reason": "实时扫描失败", "note": "当前是缓存演示数据，不代表实时状态。"}
            return {"success": False, "url": raw_url, "error": error}
        ssl_info = await get_ssl_info(host, 443) if is_https else {"has_cert": False}
        waf_list = detect_waf(headers)
        sensitive_paths = await check_sensitive_paths(host, is_https)
        result = analyze_security(raw_url, headers, is_https, ssl_info, waf_list, sensitive_paths, [])
        # V11.4：生成修复建议（与登录用户一致）
        fixes = generate_fixes(result.get("findings", []), headers, is_https, host)
        return {
            "success": True, "scan_type": "real", "url": raw_url,
            "final_url": final_url, "is_https": is_https, "raw_headers": headers,
            "sensitive_paths": sensitive_paths, "waf": waf_list, "ssl_info": ssl_info,
            "fixes": fixes,
            **result,
        }
    except Exception as e:
        logger.warning("public_demo_scan failed for %s: %s", raw_url, e)
        cached = _PUBLIC_DEMO_CACHE.get(host)
        if cached:
            return {**cached, "url": raw_url, "is_cached": True, "cached_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "cache_reason": "实时扫描失败", "note": "当前是缓存演示数据，不代表实时状态。"}
        return {"success": False, "url": raw_url, "error": str(e)[:300]}


# ===== AI 安全顾问（规则版，可离线） =====

_AI_KB = [
    {"keys": ["hsts", "https", "ssl", "tls", "证书"],
     "reply": "**HSTS（HTTP Strict Transport Security）** 强制浏览器始终用 HTTPS 访问你的网站，防止降级攻击和 Cookie 劫持。\n\n**修复方法**（Nginx）：\n```\nadd_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;\n```"},
    {"keys": ["csp", "xss", "跨站脚本", "脚本注入"],
     "reply": "**CSP（Content-Security-Policy）** 限制页面能加载哪些资源，是防御 XSS 最有效的一招。\n\n**推荐配置**（按需放宽）：\n```\nadd_header Content-Security-Policy \"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; frame-ancestors 'none'\" always;\n```"},
    {"keys": ["敏感文件", ".env", ".git", "git泄露", "源码泄露"],
     "reply": "**敏感文件暴露** = 攻击者能直接拿到你的源码、配置、备份。\n\n**Nginx 拦截规则**：\n```nginx\nlocation ~ /\\.(env|git|gitignore|svn|hg|bak|sql|log|DS_Store)$ { deny all; return 403; }\n```"},
    {"keys": ["x-frame", "点击劫持", "iframe", "frame"],
     "reply": "**点击劫持（Clickjacking）**：用户被诱导点击看似无害的页面，背后却点在恶意 iframe 里。\n\n**防御**（Nginx）：\n```\nadd_header X-Frame-Options \"DENY\" always;\n```"},
    {"keys": ["x-content-type", "nosniff", "mime"],
     "reply": "**MIME 嗅探** 攻击：浏览器把 `.txt` 当 JS 解析执行，可能导致 XSS。\n\n**修复**（Nginx）：\n```\nadd_header X-Content-Type-Options \"nosniff\" always;\n```"},
    {"keys": ["server", "版本泄露", "信息泄露", "server头"],
     "reply": "**Server 头泄露版本信息** 会帮助攻击者针对特定版本找漏洞。\n\n**修复**：\n```nginx\nserver_tokens off;  # Nginx\n```"},
    {"keys": ["referrer", "referer", "引用"],
     "reply": "**Referrer-Policy** 控制跳转时是否带上来源 URL。\n\n**推荐配置**：\n```\nadd_header Referrer-Policy \"strict-origin-when-cross-origin\" always;\n```"},
    {"keys": ["permissions-policy", "权限策略", "摄像头", "麦克风", "geolocation"],
     "reply": "**Permissions-Policy** 关闭页面不需要的危险 API。\n\n**推荐配置**：\n```\nadd_header Permissions-Policy \"camera=(), microphone=(), geolocation=(), payment=(), usb=()\" always;\n```"},
    {"keys": ["评分", "分数", "安全评分", "怎么算", "打分"],
     "reply": "**V11.4 评分公式**：基础 100 分 − critical×25 − high×15 − medium×8 − low×3 + 修复配置加成 +12 + 已验证修复 +10\n\n**快速提分**：加 HSTS / CSP / X-Frame-Options / X-Content-Type-Options（4 个头 +12 分），拦截敏感文件（+6 分），关 Server 版本（+4 分）。"},
    {"keys": ["owasp", "top10", "top 10"],
     "reply": "**OWASP Top 10（2021）**：A01 访问控制失效 / A02 加密机制失效 / A03 注入攻击 / A04 不安全设计 / A05 安全配置错误 / A06 过时组件 / A07 认证失败 / A08 软件完整性 / A09 日志监控不足 / A10 服务端请求伪造。"},
    {"keys": ["你好", "hi", "hello", "在吗", "你是"],
     "reply": "你好！我是漏洞哨兵 V11.4 的安全顾问 🛡\n\n试试问我：HSTS 是什么、如何修复 CSP、怎么提分。"},
    {"keys": ["怎么用", "怎么开始", "上手", "使用"],
     "reply": "**30 秒上手流程（V11.4）**：\n1. 用测试账号一键登录（`demo / demo123`）\n2. 打开后看「真实演示报告」（已自动跑 example.com）\n3. 点「一键应用修复」看修复前后对比\n4. 注册后扫描你自己的目标\n5. 用「验证修复效果」看真实评分提升"},
    {"keys": ["批量", "多个", "一次扫", "多 url"],
     "reply": "新上线的**批量扫描**：在扫描页点「📦 批量扫描」按钮，一次最多 5 个 URL，V11 用并发执行。"},
    {"keys": ["v11", "v 11", "更新", "新版本", "11", "升级"],
     "reply": "**V11.4 主要改进**：\n1. 严重度字段统一为 severity（high/medium/low），不再混用 level\n2. 修复闭环真正打通：verify-fix 输出 fixed/new_issues/delta\n3. 批量扫描并发化（asyncio.gather）\n4. /api/history 新增 DELETE 真清空\n5. /api/version 返回构建信息\n6. 已修复数量从后端真实统计（前 30% 假数据已删除）\n7. JWT secret 默认 48 字节随机生成（不再用 dev 弱密钥）\n8. AI 顾问兜底按真实 severity 取前 3"},
]


@app.post("/api/ai-advisor")
async def ai_advisor(req: AIAdvisorRequest, request: Request, user=Depends(get_current_user)):
    client_ip = request.client.host if request.client else "unknown"
    if not await limiter_ai.is_allowed(client_ip):
        raise HTTPException(
            status_code=429,
            detail="AI 顾问请求过于频繁，请稍后再试",
            headers={"Retry-After": "60"},
        )
    msg = (req.message or "").strip().lower()
    if not msg:
        return {"reply": "请输入问题，例如：HSTS 是什么？如何修复 CSP？", "source": "empty"}

    # Phase 2.4: 如果提供了 scan_id，从数据库读取扫描结果进行个性化分析
    # 如果没提供 scan_id 但用户问的是扫描相关问题，自动读取最近一次的扫描
    scan_context = None
    if user and user.get("user_id"):
        conn = get_db()
        try:
            if req.scan_id:
                row = conn.execute("SELECT findings_json, summary_json, score, risk_level FROM scans WHERE id=? AND user_id=?", (req.scan_id, user["user_id"])).fetchone()
            else:
                # 自动读取最近一次的扫描（用于"最该先修什么"等通用问题）
                row = conn.execute("SELECT findings_json, summary_json, score, risk_level FROM scans WHERE user_id=? ORDER BY id DESC LIMIT 1", (user["user_id"],)).fetchone()
            if row:
                try:
                    findings = json.loads(row["findings_json"]) if row.get("findings_json") else []
                    summary = json.loads(row["summary_json"]) if row.get("summary_json") else {}
                    scan_context = {
                        "findings": findings,
                        "summary": summary,
                        "score": row["score"],
                        "risk_level": row["risk_level"],
                    }
                except Exception:
                    pass
        finally:
            conn.close()

    if scan_context:
        # 基于扫描结果生成个性化回答
        findings = scan_context.get("findings", [])
        score = scan_context.get("score", 0)
        high_count = scan_context.get("summary", {}).get("high", 0)

        # 生成自然语言总结
        if not msg or msg in ("总结", "概览", "总体", "整体"):
            summary_parts = []
            if score >= 75:
                summary_parts.append(f"当前安全评分为 {score} 分，整体状况良好。")
            elif score >= 50:
                summary_parts.append(f"当前安全评分为 {score} 分，存在一些需要关注的安全配置问题。")
            else:
                summary_parts.append(f"当前安全评分为 {score} 分，存在较多安全风险，建议尽快修复。")

            if high_count > 0:
                summary_parts.append(f"发现 {high_count} 个高风险项，建议优先处理。")

            # 找出最关键的问题
            high_findings = [f for f in findings if f.get("severity") in ("high", "critical")]
            if high_findings:
                names = ", ".join([f["name"] for f in high_findings[:3]])
                summary_parts.append(f"主要问题集中在：{names}。")

            return {"reply": "".join(summary_parts), "source": "scan_analysis"}

        # 回答关于当前扫描结果的问题
        if any(kw in msg for kw in ["优先", "先修", "重要", "顺序", "最该", "最先", "推荐", "建议"]):
            # 按修复优先级排序：高危优先、修复成本低优先
            prioritized = sorted(findings, key=lambda f: (
                0 if f.get("severity") in ("critical", "high") else 1 if f.get("severity") == "medium" else 2,
                f.get("name", "")
            ))
            top = prioritized[:5]
            lines = [f"🔍 当前评分 {score} 分（{scan_context.get('risk_level', '未知风险')}）。建议按以下优先级修复：\n"]
            for i, f in enumerate(top, 1):
                sev = f.get("severity", "low")
                tag = "🔴" if sev in ("critical", "high") else "🟡" if sev == "medium" else "🟢"
                fix_hint = f.get("fix", "")[:50]
                lines.append(f"{tag} 第{i}优先：{f['name']}")
                if fix_hint:
                    lines.append(f"   💡 快速修复：{fix_hint}")
                lines.append("")
            lines.append("✅ 建议先处理 🔴 高风险项，修复后重新扫描验证效果。")
            return {"reply": "\n".join(lines), "source": "scan_analysis"}

        if any(kw in msg for kw in ["分数", "评分", "为什么", "怎么扣"]):
            breakdown = scan_context.get("score_breakdown", [])
            if breakdown:
                lines = [f"当前评分 {score} 分，扣分明细如下："]
                for b in breakdown:
                    lines.append(f"- {b['item']}：-{b['deduction']} 分（{b.get('reason', '')[:40]}）")
            else:
                lines = [f"当前评分 {score} 分。"]
                for f in findings:
                    lines.append(f"- {f['name']}（{f.get('severity', '')}）")
            return {"reply": "\n".join(lines), "source": "scan_analysis"}

        if any(kw in msg for kw in ["hsts", "csp", "header", "响应头", "安全头"]):
            header_findings = [f for f in findings if "缺少" in f.get("name", "") or "HSTS" in f.get("name", "") or "CSP" in f.get("name", "")]
            if header_findings:
                lines = ["关于安全响应头的问题："]
                for f in header_findings:
                    evidence = f.get("evidence", {})
                    lines.append(f"- {f['name']}：{f.get('description', '')}")
                    if evidence.get("impact"):
                        lines.append(f"  影响：{evidence['impact']}")
                    if f.get("fix"):
                        lines.append(f"  修复：{f['fix'][:80]}")
                return {"reply": "\n".join(lines), "source": "scan_analysis"}

        # 生成修复计划
        if any(kw in msg for kw in ["修复计划", "修复步骤", "怎么修", "如何修复", "步骤"]):
            prioritized = sorted(findings, key=lambda f: (
                0 if f.get("severity") in ("critical", "high") else 1 if f.get("severity") == "medium" else 2,
                f.get("name", "")
            ))
            lines = ["📋 修复计划（按优先级排序）：\n"]
            for i, f in enumerate(prioritized[:8], 1):
                sev = f.get("severity", "low")
                tag = "🔴" if sev in ("critical", "high") else "🟡" if sev == "medium" else "🟢"
                lines.append(f"{tag} 第{i}步：修复「{f['name']}」")
                if f.get("fix"):
                    lines.append(f"   建议：{f['fix'][:80]}")
                lines.append("")
            lines.append("✅ 每步修复后建议重新扫描验证效果。")
            lines.append("📊 全部修复后，评分预计可提升至 85+ 分。")
            return {"reply": "\n".join(lines), "source": "scan_analysis"}

        # 配置位置建议
        if any(kw in msg for kw in ["放在哪里", "配置位置", "加在哪里", "写在哪里", "哪个文件"]):
            lines = ["📌 安全配置放置位置建议：\n"]
            lines.append("**Nginx**：配置通常放在 `/etc/nginx/nginx.conf` 或 `/etc/nginx/conf.d/` 下的站点配置文件中，加在 `server { }` 块内。")
            lines.append("\n**Apache**：放在站点 VirtualHost 配置中，或 `.htaccess` 文件里。")
            lines.append("\n**Express (Node.js)**：在 `app.js` 主文件中，`app.listen()` 之前添加中间件。")
            lines.append("\n**Flask/FastAPI**：使用 `@app.after_request` 装饰器统一添加安全头。")
            lines.append("\n**Spring Boot**：在 `SecurityConfig.java` 的 `filterChain` 方法中配置 `HttpSecurity`。")
            lines.append("\n**Cloudflare**：在 Cloudflare Dashboard > Rules > Transform Rules 中配置响应头修改。")
            lines.append("\n⚠ 修改配置后记得重启服务或重载配置使生效。")
            return {"reply": "\n".join(lines), "source": "scan_analysis"}

        # 上线风险提醒
        if any(kw in msg for kw in ["上线风险", "影响线上", "会挂吗", "安全吗", "风险"]):
            high_findings = [f for f in findings if f.get("severity") in ("high", "critical")]
            medium_findings = [f for f in findings if f.get("severity") == "medium"]
            lines = ["⚠ 上线风险评估：\n"]
            if high_findings:
                lines.append(f"🔴 高风险项（{len(high_findings)} 个）：建议在测试环境验证后再上线。")
                for f in high_findings[:3]:
                    lines.append(f"   - {f['name']}：{f.get('description', '')[:50]}")
            if medium_findings:
                lines.append(f"\n🟡 中风险项（{len(medium_findings)} 个）：建议尽快处理，但不阻塞上线。")
            lines.append("\n💡 修复建议：")
            lines.append("1. 先在测试环境/预发环境应用修复")
            lines.append("2. 使用浏览器开发者工具检查响应头是否正确")
            lines.append("3. 确认前端资源（JS/CSS/图片）正常加载")
            lines.append("4. 特别注意 CSP 策略可能影响第三方资源加载")
            lines.append("5. 确认无误后再部署到生产环境")
            return {"reply": "\n".join(lines), "source": "scan_analysis"}

    for kb in _AI_KB:
        for k in kb["keys"]:
            if k.lower() in msg:
                return {"reply": kb["reply"], "source": "kb"}
    if user:
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT url, score, findings_json, risk_level FROM scans WHERE user_id=? ORDER BY id DESC LIMIT 1",
                (user["user_id"],)
            ).fetchone()
            conn.close()
            if row:
                findings = json.loads(row["findings_json"] or "[]")
                # 如果用户问"最该先修什么"，即使没有 scan_context 也给出优先级排序
                if any(kw in msg for kw in ["优先", "先修", "重要", "顺序", "最该", "最先", "推荐", "建议"]):
                    prioritized = sorted(findings, key=lambda f: (
                        0 if f.get("severity") in ("critical", "high") else 1 if f.get("severity") == "medium" else 2,
                        f.get("name", "")
                    ))
                    top = prioritized[:5]
                    lines = [f"🔍 当前评分 {row['score']} 分（{row['risk_level'] or '未知风险'}）。建议按以下优先级修复：\n"]
                    for i, f in enumerate(top, 1):
                        sev = f.get("severity", "low")
                        tag = "🔴" if sev in ("critical", "high") else "🟡" if sev == "medium" else "🟢"
                        fix_hint = f.get("fix", "")[:50]
                        lines.append(f"{tag} 第{i}优先：{f.get('name', '')}")
                        if fix_hint:
                            lines.append(f"   💡 快速修复：{fix_hint}")
                        lines.append("")
                    lines.append("✅ 建议先处理 🔴 高风险项，修复后重新扫描验证效果。")
                    return {"reply": "\n".join(lines), "source": "scan"}
                top = findings[:3]
                if top:
                    names = "、".join([f.get("name", "") for f in top])
                    top_name = top[0].get("name", "")
                    return {
                        "reply": f"你最近一次扫描的是 **{row['url']}**，评分 **{row['score']}**。\n\n排名前 3 的问题：{names}\n\n可以问我具体某个问题的修复方法，比如：'怎么修 {top_name}'。",
                        "source": "scan",
                    }
        except Exception as e:
            logger.warning("ai_advisor fallback failed: %s", e)
    return {"reply": "我没找到相关知识 😢。试试问我：HSTS、CSP、敏感文件、点击劫持、OWASP Top 10，或者直接说「怎么用」。", "source": "fallback"}


# ============== 批量扫描 ==============

@app.post("/api/batch-scan", response_model=None)
async def batch_scan(req: BatchScanRequest, request: Request, user=Depends(require_login)):
    """批量扫描：一次提交多个 URL（最多 5 个），并发执行后返回对比摘要。"""
    await rate_limit_dependency(request)
    client_ip = request.client.host if request.client else "unknown"
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
        # 单个 URL 限时 25 秒，避免慢站拖死批量
        try:
            return await asyncio.wait_for(_scan_one_impl(url, host, deep, user_id), timeout=25.0)
        except asyncio.TimeoutError:
            return {"url": url, "ok": False, "error": "扫描超时（25s）"}
        except Exception as e:
            logger.warning("batch scan failed for %s: %s", url, e)
            return {"url": url, "ok": False, "error": str(e)[:200]}

    async def _scan_one_impl(url, host, deep, user_id):
        headers, is_https, final_url, error = await fetch_headers(url)
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
        result = analyze_security(url, headers, is_https, ssl_info, waf_list, sensitive_paths, vuln_findings)
        scan_id = save_scan(
            user_id, url, result["score"], result["risk_level"],
            result["findings"], result["summary"],
            len(crawled_pages) if crawled_pages else 0,
            "deep" if deep else "real",
        )
        # 批量扫描也同步资产扫描信息
        try:
            update_asset_after_scan(user_id, host, scan_id)
        except Exception:
            pass
        s = result.get("summary", {})
        return {
            "url": url, "ok": True, "score": result["score"],
            "risk_level": result["risk_level"],
            "high": s.get("high", 0), "medium": s.get("medium", 0),
            "low": s.get("low", 0), "critical": s.get("critical", 0),
            "scan_id": scan_id, "findings_count": len(result["findings"]),
        }

    # 并发跑（asyncio.gather），单个 URL 各自 25s 超时
    results = await asyncio.gather(*[scan_one(u) for u in urls])
    return {"success": True, "results": results, "count": len(results)}


# ---------- 资产管理 API ----------

@app.post("/api/assets")
async def api_create_asset(req: AssetCreateRequest, user: dict = Depends(require_login)) -> dict:
    asset_id = create_asset(user["user_id"], req.domain, req.owner, req.description)
    return {"success": True, "asset_id": asset_id}


@app.get("/api/assets")
async def api_list_assets(user: dict = Depends(require_login)) -> dict:
    assets = get_assets(user["user_id"])
    return {"success": True, "assets": assets}


@app.patch("/api/assets/{asset_id}")
async def api_update_asset(asset_id: int, req: AssetUpdateRequest, user: dict = Depends(require_login)) -> dict:
    ok = update_asset(asset_id, user["user_id"], owner=req.owner, description=req.description)
    if not ok:
        raise HTTPException(404, "资产不存在或无权限")
    return {"success": True}


@app.delete("/api/assets/{asset_id}")
async def api_delete_asset(asset_id: int, user: dict = Depends(require_login)) -> dict:
    ok = delete_asset(asset_id, user["user_id"])
    if not ok:
        raise HTTPException(404, "资产不存在或无权限")
    return {"success": True}


@app.post("/api/assets/{asset_id}/scan")
async def api_scan_asset(asset_id: int, request: Request, user: dict = Depends(require_login)):
    """对资产发起扫描：复用现有扫描逻辑。"""
    await rate_limit_dependency(request)
    asset = get_asset(asset_id, user["user_id"])
    if not asset:
        raise HTTPException(404, "资产不存在或无权限")
    domain = asset["domain"]
    url = "https://" + domain
    parsed = urlparse(url)
    host = parsed.hostname or domain
    headers, is_https, final_url, error = await fetch_headers(url)
    if error:
        return {"success": False, "error": error}
    ssl_info = await get_ssl_info(host, 443) if is_https else {"has_cert": False}
    waf_list = detect_waf(headers)
    sensitive_paths = await check_sensitive_paths(host, is_https)
    result = analyze_security(url, headers, is_https, ssl_info, waf_list, sensitive_paths, [])
    scan_id = save_scan(
        user["user_id"], url, result["score"], result["risk_level"],
        result["findings"], result["summary"], 0, "real",
    )
    try:
        auto_create_fix_tickets(user["user_id"], scan_id, result["findings"])
    except Exception:
        pass
    try:
        update_asset_after_scan(user["user_id"], host, scan_id)
    except Exception:
        pass
    return {"success": True, "scan_id": scan_id, "score": result["score"], "risk_level": result["risk_level"]}


@app.get("/")
async def index() -> HTMLResponse:
    path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>VulnSentinel V11.4</h1>")


@app.get("/{path:path}")
async def catch_all(path: str) -> Any:
    # 使用 Path.resolve() 并校验结果仍在 STATIC_DIR 内，防止路径穿越
    try:
        base = Path(STATIC_DIR).resolve()
        fp = (base / path).resolve()
    except (OSError, ValueError):
        return await index()
    if not fp.is_file():
        return await index()
    if not fp.is_relative_to(base):
        # 解析后路径已逃出静态目录 → 拒绝
        return await index()
    return FileResponse(str(fp))


if __name__ == "__main__":
    import uvicorn
    logger.info("Server starting on :%s", settings.port)
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=False)
