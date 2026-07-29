"""输入校验工具。

提供 URL 校验、SQL 注入防护校验、XSS 输入过滤等安全校验函数。
"""

from __future__ import annotations

import ipaddress
import re
import socket
from urllib.parse import urlparse


# URL 最大长度（与项目 constants._MAX_URL_LEN 保持一致）
_MAX_URL_LENGTH = 2048

# 仅允许 http / https 协议，防 file://、gopher://、dict:// 等 SSRF 向量
_ALLOWED_SCHEMES = frozenset({"http", "https"})

# SSRF 防护：禁止访问的网段（与项目 constants.BLOCKED_NETWORKS 一致）
_SSRF_BLOCKED_NETWORKS = (
    ipaddress.ip_network("127.0.0.0/8"),       # 回环
    ipaddress.ip_network("10.0.0.0/8"),        # A 类私有
    ipaddress.ip_network("172.16.0.0/12"),     # B 类私有 (172.16 - 172.31)
    ipaddress.ip_network("192.168.0.0/16"),    # C 类私有
    ipaddress.ip_network("169.254.0.0/16"),    # 链路本地 / 云元数据
    ipaddress.ip_network("::1/128"),           # IPv6 回环
    ipaddress.ip_network("fc00::/7"),          # IPv6 唯一本地地址
)

# 常见内网/元数据主机名（字面量）
_SSRF_BLOCKED_HOSTS = frozenset({
    "localhost", "127.0.0.1", "0.0.0.0", "::1", "169.254.169.254",
})

# 本地主机名集合（用于扫描授权判断）
_LOCALHOST_HOSTS = frozenset({"localhost", "127.0.0.1", "::1"})


# ---------------------------------------------------------------------------
# 内部辅助
# ---------------------------------------------------------------------------


def _is_blocked_ip(ip_str: str) -> bool:
    """判断 IP 字面量是否落入禁用网段。"""
    # 处理 IPv6 zone，如 fe80::1%eth0
    ip_str = ip_str.split("%", 1)[0]
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return False
    return any(ip in network for network in _SSRF_BLOCKED_NETWORKS)


def _hostname_is_private(hostname: str) -> bool:
    """判断主机名是否指向内网/本地地址。

    依次检查：已知阻断主机名 -> 字面量 IP -> DNS 解析结果。
    DNS 解析失败时按「无法判定为私有」返回 ``False``，与项目既有行为一致。
    """
    hostname = hostname.lower()
    if hostname in _SSRF_BLOCKED_HOSTS:
        return True
    # 字面量 IP 直接判断
    if _is_blocked_ip(hostname):
        return True
    # 域名解析后再判断，防止域名指向内网地址（DNS rebinding 类 SSRF）
    try:
        infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        return False
    for info in infos:
        if _is_blocked_ip(info[4][0]):
            return True
    return False


def _is_localhost(hostname: str) -> bool:
    """判断主机名是否为本地回环。"""
    hostname = hostname.lower()
    if hostname in _LOCALHOST_HOSTS:
        return True
    try:
        return ipaddress.ip_address(hostname).is_loopback
    except ValueError:
        return False


def _parse_and_validate_scheme(url: str) -> tuple[bool, str, str]:
    """校验 URL 格式与协议。

    Returns:
        ``(ok, reason, hostname)``，``hostname`` 为小写主机名，失败时为空串。
    """
    url = (url or "").strip()
    if not url:
        return False, "URL 不能为空", ""
    if len(url) > _MAX_URL_LENGTH:
        return False, f"URL 长度不能超过 {_MAX_URL_LENGTH}", ""

    parsed = urlparse(url)
    scheme = (parsed.scheme or "").lower()
    if scheme not in _ALLOWED_SCHEMES:
        return False, "仅允许 http / https 协议", ""

    hostname = parsed.hostname
    if not hostname:
        return False, "URL 缺少主机名", ""
    return True, "", hostname.lower()


# ---------------------------------------------------------------------------
# 公开校验函数
# ---------------------------------------------------------------------------


def validate_url(url: str) -> tuple[bool, str]:
    """校验 URL 格式并进行 SSRF 防护检查。

    - 仅允许 ``http`` / ``https`` 协议；
    - 阻断指向内网/本地/链路本地地址的目标（127.0.0.1、10.x、172.16-31.x、
      192.168.x、169.254.x、::1、fc00::/7 等）；
    - 对域名做 DNS 解析后再判定，防止域名指向内网地址。

    Args:
        url: 待校验的 URL 字符串。

    Returns:
        ``(True, "")`` 表示通过；``(False, reason)`` 表示失败并给出原因。
    """
    ok, reason, hostname = _parse_and_validate_scheme(url)
    if not ok:
        return False, reason
    if _hostname_is_private(hostname):
        return False, f"目标地址 {hostname} 属于内网/本地地址，存在 SSRF 风险"
    return True, ""


def sanitize_input(text: str, max_length: int = 10000) -> str:
    """基础输入清理。

    - 去除 NULL 字节与控制字符（保留制表符 ``\\t``、换行 ``\\n``、回车 ``\\r``）；
    - 按指定长度截断；
    - 去除首尾空白。

    Args:
        text: 原始输入。
        max_length: 允许的最大字符数，默认 10000。

    Returns:
        清理后的字符串。
    """
    if text is None:
        return ""
    text = str(text)
    # 去除控制字符（保留 \t \n \r）与 DEL
    text = _CONTROL_CHAR_RE.sub("", text)
    # 截断
    if len(text) > max_length:
        text = text[:max_length]
    return text.strip()


# 控制字符：\x00-\x08, \x0b, \x0c, \x0e-\x1f, \x7f（排除 \t=\x09 \n=\x0a \r=\x0d）
_CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def validate_scan_target(url: str, authorized: bool = False) -> tuple[bool, str]:
    """校验扫描目标。

    在 URL 格式与协议校验的基础上，执行扫描授权策略：

    - 本地回环目标（localhost / 127.0.0.1 / ::1）允许直接扫描；
    - 非本地目标必须 ``authorized=True`` 才允许扫描。

    注意：本函数不应用 :func:`validate_url` 的 SSRF 内网阻断逻辑——
    授权场景下允许扫描内网靶场（与项目 ``ALLOWED_INTERNAL_HOSTS`` 行为一致），
    未授权的非本地请求一律拒绝，从而同样起到 SSRF 防护作用。

    Args:
        url: 待校验的扫描目标 URL。
        authorized: 调用方是否已获得授权。

    Returns:
        ``(True, "")`` 表示通过；``(False, reason)`` 表示失败并给出原因。
    """
    ok, reason, hostname = _parse_and_validate_scheme(url)
    if not ok:
        return False, reason

    if _is_localhost(hostname):
        return True, ""
    if not authorized:
        return False, "扫描非本地目标需要授权"
    return True, ""


# ---------------------------------------------------------------------------
# 纵深防御：SQL 注入检测 / XSS 过滤
# ---------------------------------------------------------------------------

# 常见 SQL 注入特征（粗粒度，仅作输入层提示，不能替代参数化查询）
_SQLI_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bunion\b\s+\bselect\b", re.I),                       # UNION SELECT
    re.compile(r"'\s*(?:or|and)\s+'?\w+'?\s*=\s*'?\w+", re.I),         # ' OR '1'='1
    re.compile(r"\b(?:or|and)\s+\d+\s*=\s*\d+\b", re.I),               # OR 1=1
    re.compile(r"--\s*$", re.I),                                       # 行尾注释
    re.compile(r"/\*.*?\*/", re.I | re.S),                             # 块注释
    re.compile(r";\s*(?:drop|update|insert|delete|truncate|alter|exec)\b", re.I),
    re.compile(r"\bexec(?:ute)?\s*\(", re.I),
    re.compile(r"\bxp_cmdshell\b", re.I),
)


def detect_sql_injection(text: str) -> bool:
    """粗粒度检测输入是否包含常见 SQL 注入特征。

    仅作为输入层的纵深防御提示，**不能替代参数化查询**。
    可能存在误报，建议结合业务上下文使用。
    """
    if not text:
        return False
    lowered = text.lower()
    return any(pattern.search(lowered) for pattern in _SQLI_PATTERNS)


# 危险 HTML/脚本特征
_SCRIPT_TAG_RE = re.compile(
    r"<\s*/?\s*(script|iframe|object|embed|svg)\b[^>]*>", re.I | re.S
)
_EVENT_HANDLER_RE = re.compile(
    r"\bon\w+\s*=\s*(?:'[^']*'|\"[^\"]*\"|[^\s>]+)", re.I
)
_JS_URI_RE = re.compile(r"(?:javascript|vbscript|data)\s*:", re.I)


def strip_xss(text: str) -> str:
    """移除输入中常见的 XSS 载荷。

    包括：``<script>`` 等危险标签、``on*`` 事件处理器、
    ``javascript:`` / ``vbscript:`` / ``data:`` 伪协议。

    用于对自由输入做输入侧过滤；输出侧仍应做 HTML 转义以彻底防范 XSS。
    """
    if not text:
        return ""
    text = _SCRIPT_TAG_RE.sub("", text)
    text = _EVENT_HANDLER_RE.sub("", text)
    text = _JS_URI_RE.sub("", text)
    return text
