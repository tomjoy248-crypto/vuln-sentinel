"""Vuln Sentinel - 工具函数模块"""

import ipaddress
import logging
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

logger = logging.getLogger("vuln_sentinel.utils")

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


def resolve_and_validate_ip(hostname: str) -> str:
    """解析主机名并验证 IP 安全性，返回第一个安全 IP。

    安全最佳实践（SSRF 防护 - DNS Pinning）：
    在校验阶段解析 DNS 得到 IP 后，将此 IP 固定传递给后续 HTTP 请求，
    消除 check-then-use 时间窗口（DNS 重绑定攻击）。

    Args:
        hostname: 要解析的主机名

    Returns:
        解析到的第一个安全 IP 地址字符串

    Raises:
        ValueError: 如果主机名解析失败或解析到被封锁的内网 IP
    """
    if hostname.lower() in BLOCKED_HOSTS and hostname.lower() not in ALLOWED_INTERNAL_HOSTS:
        raise ValueError(f"被封锁的主机名: {hostname}")

    try:
        infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror as exc:
        raise ValueError(f"DNS 解析失败: {hostname}") from exc

    for info in infos:
        ip_str = info[4][0]
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            continue
        # 检查是否落入被封锁网段
        is_blocked = False
        for network in BLOCKED_NETWORKS:
            if ip in network:
                is_blocked = True
                break
        if is_blocked and hostname.lower() not in ALLOWED_INTERNAL_HOSTS:
            # 跳过被封 IP，继续尝试下一个解析结果
            continue
        if not is_blocked:
            return ip_str

    raise ValueError(f"所有解析 IP 均被封锁: {hostname}")


def build_pinned_url(original_url: str, pinned_ip: str) -> tuple[str, str]:
    """构建使用固定 IP 的请求 URL，同时返回原始主机名用于 Host 头和 SNI。

    安全最佳实践（SSRF 防护 - DNS Pinning）：
    将 URL 中的域名替换为已验证的 IP，防止 httpx 再次解析 DNS 时遭受重绑定攻击。
    对于 HTTPS，通过保留原始主机名用于 SNI/TLS 验证。

    Args:
        original_url: 原始 URL（如 https://example.com/path）
        pinned_ip: 已验证的 IP 地址（如 93.184.216.34）

    Returns:
        (pinned_url, original_hostname) 元组
        pinned_url: 使用 IP 的 URL（如 https://93.184.216.34/path）
        original_hostname: 原始主机名（如 example.com，用于 Host 头和 SNI）
    """
    parsed = urlparse(original_url)
    original_hostname = parsed.hostname or ""
    # 用 IP 替换主机名构建新 URL
    netloc = pinned_ip
    if parsed.port:
        netloc = f"{pinned_ip}:{parsed.port}"
    elif parsed.scheme == "https":
        netloc = f"{pinned_ip}:443"
    elif parsed.scheme == "http":
        netloc = f"{pinned_ip}:80"
    pinned_url = f"{parsed.scheme}://{netloc}{parsed.path}"
    if parsed.query:
        pinned_url += f"?{parsed.query}"
    return pinned_url, original_hostname


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

