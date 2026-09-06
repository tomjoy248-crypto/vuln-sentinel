"""合规与目标授权检查。

产品级扫描工具必须具备基本合规能力：
- 禁止扫描未授权或受保护目标
- 识别并拦截高风险目标（政府、金融、内网等）
- 要求用户明确声明扫描授权
- 深度扫描要求域名所有权验证
"""

from __future__ import annotations

import ipaddress
import logging
from datetime import datetime
from urllib.parse import urlparse

from app.db.session import get_db
from constants import BLOCKED_HOSTS, BLOCKED_NETWORKS

logger = logging.getLogger("vuln_sentinel.compliance")


# 高风险 / 受限域名后缀与关键词
RESTRICTED_TLDS = {
    ".gov",
    ".gov.cn",
    ".gov.hk",
    ".gov.mo",
    ".gov.tw",
    ".mil",
    ".edu.cn",
    ".ac.cn",
}
RESTRICTED_KEYWORDS = {
    "bank",
    "ccb",
    "icbc",
    "abc",
    "boc",
    "cmb",
    "bankcomm",
    "unionpay",
    "alipay",
    "wechatpay",
    "tenpay",
    "police",
    "gongan",
    "ga",
    "gov",
}

# 默认允许用于测试的公开靶场/演示域名
ALLOWED_DEMO_HOSTS = {
    "example.com",
    "www.example.com",
    "example.org",
    "iana.org",
    "www.iana.org",
    "httpbin.org",
    "www.httpbin.org",
    "testphp.vulnweb.com",
    "testaspnet.vulnweb.com",
    "webscantest.com",
    "www.webscantest.com",
}


class ComplianceError(Exception):
    """合规检查失败异常。"""

    def __init__(self, reason: str, code: str = "restricted") -> None:
        self.reason = reason
        self.code = code
        super().__init__(reason)


def _extract_host(url: str) -> tuple[str, int | None]:
    """从 URL 提取主机名与端口。"""
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower().strip()
    return host, parsed.port


def _is_ip_address(host: str) -> bool:
    """判断主机名是否为 IP 地址。"""
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def _is_blocked_ip(host: str) -> bool:
    """检查主机 IP 是否属于禁止网段。"""
    if host in BLOCKED_HOSTS:
        return True
    try:
        ip = ipaddress.ip_address(host)
        for network in BLOCKED_NETWORKS:
            if ip in network:
                return True
    except ValueError:
        pass
    return False


def _is_restricted_domain(host: str) -> bool:
    """检查域名是否属于受限类型。"""
    if not host:
        return True

    # 允许公开演示目标
    if host in ALLOWED_DEMO_HOSTS:
        return False

    # 检查受限后缀
    for tld in RESTRICTED_TLDS:
        if host.endswith(tld):
            return True

    # 检查敏感关键词
    host_parts = set(host.replace("-", "").replace("_", "").split("."))
    if host_parts & RESTRICTED_KEYWORDS:
        return True

    return False


def validate_scan_target(
    url: str,
    authorized: bool = False,
    allowed_demo: bool = True,
) -> tuple[bool, str]:
    """校验扫描目标是否合规。

    Args:
        url: 目标 URL
        authorized: 用户是否声明已获授权
        allowed_demo: 是否允许公开演示目标

    Returns:
        (是否通过, 原因)
    """
    host, port = _extract_host(url)
    if not host:
        return False, "无法解析目标 URL"

    # 1. 必须声明授权（演示目标除外）
    if not authorized and (not allowed_demo or host not in ALLOWED_DEMO_HOSTS):
        return False, "扫描前必须确认您已获得目标所有者授权"

    # 2. 禁止内网 / 本地地址。主机名也要先检查，不能只拦截直接写出的 IP；
    #    否则 localhost 等本地别名会绕过 SSRF 防护。
    if _is_blocked_ip(host):
        return False, "禁止扫描内网、本地或链路本地地址"
    if _is_ip_address(host):
        return True, ""

    # 3. 禁止受限域名
    if _is_restricted_domain(host):
        return False, "该目标属于政府、金融、教育或其他受限类型，请勿在未获明确授权时扫描"

    # 4. 禁止常见非 Web 端口
    if port and port not in {80, 443, 8080, 8443, 3000, 5000, 8000, 9000}:
        return False, f"端口 {port} 不在允许扫描范围内"

    return True, ""


def check_target_ownership(
    url: str,
    user_id: int,
    verification_token: str | None = None,
) -> tuple[bool, str]:
    """目标所有权验证（DNS / 文件验证 / 数据库已验证记录）。

    验证逻辑：
    1. 若提供了 verification_token，直接视为通过（简化场景 / 测试）。
    2. 否则查询 domain_verifications 表，检查该用户是否已完成对应域名的验证。

    Args:
        url: 目标 URL
        user_id: 用户 ID
        verification_token: 可选的验证凭证

    Returns:
        (是否通过, 原因)
    """
    host, _ = _extract_host(url)
    if not host:
        return False, "无法解析目标 URL"

    if verification_token and verification_token.strip():
        return True, ""

    try:
        conn = get_db()
        try:
            row = conn.execute(
                """SELECT id, status, expires_at FROM domain_verifications
                   WHERE user_id = ? AND domain = ? AND status = 'verified'
                   ORDER BY verified_at DESC LIMIT 1""",
                (user_id, host),
            ).fetchone()
            if not row:
                return False, f"域名 {host} 尚未完成所有权验证，请先验证域名归属"
            # 简单检查是否过期（如果字段存在）
            expires_at = row.get("expires_at")
            if expires_at:
                try:
                    if datetime.fromisoformat(expires_at) < datetime.now():
                        return False, f"域名 {host} 的所有权验证已过期，请重新验证"
                except Exception:
                    pass
            return True, ""
        finally:
            conn.close()
    except Exception as e:
        logger.warning("Check target ownership failed: %s", e)
        return False, "所有权验证服务暂不可用，请稍后重试"


def validate_scan_target_full(
    url: str,
    user_id: int,
    authorized: bool = False,
    deep: bool = False,
    verification_token: str | None = None,
    allowed_demo: bool = True,
) -> tuple[bool, str, str]:
    """完整扫描目标校验（合规 + 所有权）。

    Args:
        url: 目标 URL
        user_id: 用户 ID
        authorized: 用户是否声明已获授权
        deep: 是否为深度扫描
        verification_token: 可选域名验证凭证
        allowed_demo: 是否允许公开演示目标

    Returns:
        (是否通过, 原因, code)
        code 取值：ok / unauthorized / restricted / ownership_required / error
    """
    # 1. 基础合规校验
    ok, reason = validate_scan_target(
        url, authorized=authorized, allowed_demo=allowed_demo
    )
    if not ok:
        return False, reason, "restricted" if "受限" in reason else "unauthorized"

    # 2. 深度扫描必须完成域名所有权验证（演示目标除外）
    host, _ = _extract_host(url)
    if deep and allowed_demo and host in ALLOWED_DEMO_HOSTS:
        return True, "", "ok"

    if deep:
        owned, own_reason = check_target_ownership(
            url, user_id, verification_token=verification_token
        )
        if not owned:
            return False, own_reason, "ownership_required"

    return True, "", "ok"


def get_compliance_summary() -> dict:
    """返回当前合规规则摘要（供前端展示）。"""
    return {
        "restricted_tlds": sorted(RESTRICTED_TLDS),
        "restricted_keywords_count": len(RESTRICTED_KEYWORDS),
        "allowed_demo_hosts": sorted(ALLOWED_DEMO_HOSTS),
        "blocked_networks": [str(n) for n in BLOCKED_NETWORKS],
        "requires_authorization": True,
    }

