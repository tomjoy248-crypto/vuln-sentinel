"""内置检测插件。

将核心检测能力封装为插件，支持通过 DetectorRegistry 统一调度。
"""

from __future__ import annotations

from typing import Any, Dict, List

from app.plugins import BaseVulnDetector, Finding, ScanContext


class HeaderSecurityDetector(BaseVulnDetector):
    """安全响应头检测插件。"""

    name = "header_security"
    version = "1.0"
    supported_depths = ["quick", "standard", "deep"]

    async def detect(self, context: ScanContext) -> List[Finding]:
        """检测缺失的安全响应头。"""
        findings: List[Finding] = []
        headers = context.headers

        required_headers = {
            "Strict-Transport-Security": (
                "缺少 Strict-Transport-Security (HSTS) 响应头",
                "medium",
                "配置 HSTS 头: Strict-Transport-Security: max-age=31536000; includeSubDomains",
                "CWE-319",
                "A05 安全配置错误",
            ),
            "X-Content-Type-Options": (
                "缺少 X-Content-Type-Options 响应头",
                "low",
                "配置 X-Content-Type-Options: nosniff",
                "CWE-693",
                "A05 安全配置错误",
            ),
            "X-Frame-Options": (
                "缺少 X-Frame-Options 响应头",
                "medium",
                "配置 X-Frame-Options: DENY 或 SAMEORIGIN",
                "CWE-1021",
                "A05 安全配置错误",
            ),
            "Content-Security-Policy": (
                "缺少 Content-Security-Policy (CSP) 响应头",
                "medium",
                "配置 Content-Security-Policy: default-src 'self'",
                "CWE-693",
                "A05 安全配置错误",
            ),
        }

        for header, (title, severity, fix, cwe, owasp) in required_headers.items():
            if header not in headers:
                findings.append(
                    Finding(
                        title=title,
                        type="header_missing",
                        severity=severity,
                        description=f"响应头中未找到 {header}，攻击者可能利用此缺失执行相关攻击。",
                        url=context.url,
                        evidence={"missing_header": header, "present_headers": list(headers.keys())},
                        fix_suggestion=fix,
                        confidence="high",
                        owasp_category=owasp,
                        cwe_id=cwe,
                    )
                )

        return findings


class SSLInfoDetector(BaseVulnDetector):
    """SSL/TLS 信息检测插件。"""

    name = "ssl_info"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> List[Finding]:
        """检测 SSL/TLS 配置问题。"""
        findings: List[Finding] = []
        ssl_info = context.ssl_info or {}

        if not context.is_https:
            findings.append(
                Finding(
                    title="未启用 HTTPS",
                    type="ssl",
                    severity="high",
                    description="站点未使用 HTTPS，传输数据可能被窃听或篡改。",
                    url=context.url,
                    fix_suggestion="配置 SSL/TLS 证书并强制 HTTPS 重定向。",
                    confidence="high",
                    owasp_category="A02 加密机制失效",
                    cwe_id="CWE-319",
                )
            )
            return findings

        if ssl_info.get("expired"):
            findings.append(
                Finding(
                    title="SSL 证书已过期",
                    type="ssl",
                    severity="high",
                    description=f"SSL 证书已过期（剩余天数: {ssl_info.get('days_left', 0)}）。",
                    url=context.url,
                    evidence={"days_left": ssl_info.get("days_left")},
                    fix_suggestion="立即续期 SSL 证书。",
                    confidence="high",
                    owasp_category="A02 加密机制失效",
                    cwe_id="CWE-298",
                )
            )

        if ssl_info.get("weak"):
            findings.append(
                Finding(
                    title="弱 SSL/TLS 配置",
                    type="ssl",
                    severity="medium",
                    description="检测到弱加密套件或协议版本。",
                    url=context.url,
                    fix_suggestion="禁用 TLS 1.0/1.1，仅允许 TLS 1.2+ 和强加密套件。",
                    confidence="medium",
                    owasp_category="A02 加密机制失效",
                    cwe_id="CWE-326",
                )
            )

        return findings


def register_builtin_detectors() -> None:
    """注册所有内置检测器。"""
    from app.plugins import DetectorRegistry
    from app.plugins.detectors import (
        SQLiDetector,
        ReflectedXSSDetector,
        CommandInjectionDetector,
        DirectoryTraversalDetector,
        SSRFDetector,
        InsecureDeserializationDetector,
        TimeBasedSQLiDetector,
        SensitivePathDetectorPlugin,
    )

    DetectorRegistry.register(HeaderSecurityDetector())
    DetectorRegistry.register(SSLInfoDetector())
    DetectorRegistry.register(SQLiDetector())
    DetectorRegistry.register(ReflectedXSSDetector())
    DetectorRegistry.register(CommandInjectionDetector())
    DetectorRegistry.register(DirectoryTraversalDetector())
    DetectorRegistry.register(SSRFDetector())
    DetectorRegistry.register(InsecureDeserializationDetector())
    DetectorRegistry.register(TimeBasedSQLiDetector())
    DetectorRegistry.register(SensitivePathDetectorPlugin())
