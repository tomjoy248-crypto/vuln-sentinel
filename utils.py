"""漏洞哨兵 11-S - 工具函数模块"""

import ipaddress
import re
import socket
from urllib.parse import urlparse

from constants import (
    _ALLOWED_USERNAME_RE,
    _MAX_EMAIL_LEN,
    _MAX_PASSWORD_LEN,
    _MAX_URL_LEN,
    _MAX_USERNAME_LEN,
    ALLOWED_INTERNAL_HOSTS,
    BLOCKED_HOSTS,
    BLOCKED_NETWORKS,
)


# ---------- 输入验证与清理 ----------

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
        value = "https://" + value
    parsed = urlparse(value)
    if not parsed.hostname:
        raise ValueError("URL 格式无效")
    hostname = parsed.hostname.lower()
    if "." not in hostname:
        if hostname == "localhost" and "localhost" in ALLOWED_INTERNAL_HOSTS:
            pass
        else:
            raise ValueError("URL 格式无效：域名必须包含点号（如 example.com）")
    else:
        parts = hostname.rsplit(".", 1)
        tld = parts[1] if len(parts) == 2 else ""
        is_ip_like = all(c.isdigit() or c == "." for c in hostname)
        if not is_ip_like and len(tld) < 2:
            raise ValueError("URL 格式无效：域名后缀太短")
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
    if not re.match(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$", value):
        raise ValueError("邮箱格式无效")
    return value


def sanitize_password(value: str) -> str:
    if len(value) < 6 or len(value) > _MAX_PASSWORD_LEN:
        raise ValueError(f"密码长度需在 6-{_MAX_PASSWORD_LEN} 之间")
    return value


# ---------- CORS 白名单解析 ----------

def parse_cors_origins(raw: str) -> list[str]:
    """解析逗号分隔的 CORS 白名单，去空白去空项。"""
    if not raw:
        return []
    return [o.strip() for o in raw.split(",") if o.strip()]


# ---------- 通用工具 ----------

def _html_escape(text: str) -> str:
    """HTML 转义，防止 XSS。"""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )
