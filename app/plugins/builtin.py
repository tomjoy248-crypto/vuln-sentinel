"""内置检测插件。

将核心检测能力封装为插件，支持通过 DetectorRegistry 统一调度。
"""

from __future__ import annotations

from app.plugins import BaseVulnDetector, Evidence, Finding, ScanContext, VulnLocation


class HeaderSecurityDetector(BaseVulnDetector):
    """安全响应头检测插件。"""

    name = "header_security"
    version = "1.0"
    supported_depths = ["quick", "standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        """检测缺失的安全响应头。"""
        findings: list[Finding] = []
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
                        location=VulnLocation(
                            url=context.url,
                            parameter=header,
                            parameter_type="header",
                            snippet="HTTP 响应头",
                        ),
                        evidence=Evidence(
                            extra={
                                "missing_header": header,
                                "present_headers": list(headers.keys()),
                            },
                        ),
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

    async def detect(self, context: ScanContext) -> list[Finding]:
        """检测 SSL/TLS 配置问题。"""
        findings: list[Finding] = []
        ssl_info = context.ssl_info or {}

        if not context.is_https:
            findings.append(
                Finding(
                    title="未启用 HTTPS",
                    type="ssl",
                    severity="high",
                    description="站点未使用 HTTPS，传输数据可能被窃听或篡改。",
                    url=context.url,
                    location=VulnLocation(
                        url=context.url,
                        parameter="",
                        parameter_type="protocol",
                        snippet="协议层",
                    ),
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
                    location=VulnLocation(
                        url=context.url,
                        parameter="",
                        parameter_type="protocol",
                        snippet="TLS 证书",
                    ),
                    evidence=Evidence(
                        extra={"days_left": ssl_info.get("days_left")},
                    ),
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
                    location=VulnLocation(
                        url=context.url,
                        parameter="",
                        parameter_type="protocol",
                        snippet="TLS 配置",
                    ),
                    fix_suggestion="禁用 TLS 1.0/1.1，仅允许 TLS 1.2+ 和强加密套件。",
                    confidence="medium",
                    owasp_category="A02 加密机制失效",
                    cwe_id="CWE-326",
                )
            )

        return findings


class CookieSecurityDetector(BaseVulnDetector):
    """Cookie 安全属性检测插件。"""

    name = "cookie_security"
    version = "1.0"
    supported_depths = ["quick", "standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        """检测 Set-Cookie 头中缺失的安全属性。"""
        findings: list[Finding] = []
        headers = context.headers
        set_cookie = headers.get("set-cookie") or headers.get("Set-Cookie", "")
        if not set_cookie:
            return findings

        cookies = [c.strip() for c in str(set_cookie).split(",") if c.strip()]
        for cookie in cookies:
            name = cookie.split("=")[0] if "=" in cookie else ""
            issues = []
            if "secure" not in cookie.lower() and context.is_https:
                issues.append("缺少 Secure 属性")
            if "httponly" not in cookie.lower():
                issues.append("缺少 HttpOnly 属性")
            if "samesite" not in cookie.lower():
                issues.append("缺少 SameSite 属性")
            if issues:
                findings.append(
                    Finding(
                        title=f"Cookie '{name}' 安全属性不足",
                        type="cookie_security",
                        severity="medium" if "httponly" in issues else "low",
                        description=f"Set-Cookie 头中的 {name} 存在以下问题：{', '.join(issues)}。",
                        url=context.url,
                        location=VulnLocation(
                            url=context.url,
                            parameter=name,
                            parameter_type="cookie",
                            snippet=cookie,
                        ),
                        evidence=Evidence(extra={"cookie": cookie, "issues": issues}),
                        fix_suggestion="为敏感 Cookie 添加 Secure、HttpOnly 和 SameSite=Lax/Strict 属性。",
                        confidence="high",
                        owasp_category="A05 安全配置错误",
                        cwe_id="CWE-1004",
                    )
                )
        return findings


class CORSSecurityDetector(BaseVulnDetector):
    """CORS 配置安全检测插件。"""

    name = "cors_security"
    version = "1.0"
    supported_depths = ["quick", "standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        """检测不安全的 CORS 配置。"""
        findings: list[Finding] = []
        headers = context.headers
        acao = headers.get("access-control-allow-origin") or headers.get(
            "Access-Control-Allow-Origin", ""
        )
        acac = headers.get("access-control-allow-credentials") or headers.get(
            "Access-Control-Allow-Credentials", ""
        )
        if not acao:
            return findings

        if acao == "*":
            if acac and acac.lower() == "true":
                findings.append(
                    Finding(
                        title="CORS 配置存在高风险：允许任意来源且携带凭证",
                        type="cors_misconfig",
                        severity="high",
                        description="Access-Control-Allow-Origin: * 与 Access-Control-Allow-Credentials: true 同时存在，任意恶意网站可发起带凭证的跨域请求。",
                        url=context.url,
                        location=VulnLocation(
                            url=context.url,
                            parameter="Access-Control-Allow-Origin",
                            parameter_type="header",
                            snippet=f"Access-Control-Allow-Origin: {acao}",
                        ),
                        evidence=Evidence(extra={"acao": acao, "acac": acac}),
                        fix_suggestion="禁止同时设置 Access-Control-Allow-Origin: * 与 Access-Control-Allow-Credentials: true；应使用白名单动态校验 Origin。",
                        confidence="high",
                        owasp_category="A05 安全配置错误",
                        cwe_id="CWE-942",
                    )
                )
            else:
                findings.append(
                    Finding(
                        title="CORS 允许任意来源",
                        type="cors_misconfig",
                        severity="low",
                        description="Access-Control-Allow-Origin: * 允许任意域访问资源，可能泄露敏感信息。",
                        url=context.url,
                        location=VulnLocation(
                            url=context.url,
                            parameter="Access-Control-Allow-Origin",
                            parameter_type="header",
                            snippet=f"Access-Control-Allow-Origin: {acao}",
                        ),
                        evidence=Evidence(extra={"acao": acao}),
                        fix_suggestion="根据业务需要，将 Access-Control-Allow-Origin 设置为可信域名白名单。",
                        confidence="high",
                        owasp_category="A05 安全配置错误",
                        cwe_id="CWE-942",
                    )
                )
        elif "null" in acao.lower():
            findings.append(
                Finding(
                    title="CORS 允许 null Origin",
                    type="cors_misconfig",
                    severity="medium",
                    description="Access-Control-Allow-Origin 设置为 null，攻击者可利用 sandboxed iframe 绕过同源策略。",
                    url=context.url,
                    location=VulnLocation(
                        url=context.url,
                        parameter="Access-Control-Allow-Origin",
                        parameter_type="header",
                        snippet=f"Access-Control-Allow-Origin: {acao}",
                    ),
                    evidence=Evidence(extra={"acao": acao}),
                    fix_suggestion="移除 null 来源，仅允许可信域名。",
                    confidence="high",
                    owasp_category="A05 安全配置错误",
                    cwe_id="CWE-942",
                )
            )
        return findings


class EnhancedHeaderSecurityDetector(BaseVulnDetector):
    """增强安全响应头检测插件（Permissions-Policy / Referrer-Policy）。"""

    name = "enhanced_header_security"
    version = "1.0"
    supported_depths = ["quick", "standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        """检测缺失的 Permissions-Policy 和 Referrer-Policy 响应头。"""
        findings: list[Finding] = []
        headers = context.headers
        required = {
            "Referrer-Policy": (
                "缺少 Referrer-Policy 响应头",
                "low",
                "配置 Referrer-Policy: strict-origin-when-cross-origin 或 no-referrer",
                "CWE-200",
                "A05 安全配置错误",
            ),
            "Permissions-Policy": (
                "缺少 Permissions-Policy 响应头",
                "low",
                "配置 Permissions-Policy 以限制浏览器敏感 API 的使用",
                "CWE-693",
                "A05 安全配置错误",
            ),
        }
        for header, (title, severity, fix, cwe, owasp) in required.items():
            if header.lower() not in {k.lower(): v for k, v in headers.items()}:
                findings.append(
                    Finding(
                        title=title,
                        type="header_missing",
                        severity=severity,
                        description=f"响应头中未找到 {header}，可能导致信息泄露或敏感 API 被滥用。",
                        url=context.url,
                        location=VulnLocation(
                            url=context.url,
                            parameter=header,
                            parameter_type="header",
                            snippet="HTTP 响应头",
                        ),
                        evidence=Evidence(
                            extra={
                                "missing_header": header,
                                "present_headers": list(headers.keys()),
                            }
                        ),
                        fix_suggestion=fix,
                        confidence="high",
                        owasp_category=owasp,
                        cwe_id=cwe,
                    )
                )
        return findings


class DirectoryListingDetector(BaseVulnDetector):
    """目录浏览检测插件。"""

    name = "directory_listing"
    version = "1.0"
    supported_depths = ["quick", "standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        body = (context.body or "").lower()
        headers = context.headers
        content_type = " ".join(f"{k}: {v}" for k, v in headers.items()).lower()
        if not body:
            return []
        indicators = (
            "index of /",
            "directory listing for",
            "parent directory",
            "last modified",
        )
        if not any(indicator in body for indicator in indicators):
            return []
        if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
            return []

        return [
            Finding(
                title="目录浏览开启",
                type="directory_listing",
                severity="medium",
                description="目标页面呈现目录列表，攻击者可能枚举敏感文件、备份或隐藏资源。",
                url=context.url,
                location=VulnLocation(
                    url=context.url,
                    parameter="",
                    parameter_type="path",
                    snippet="Directory listing",
                ),
                evidence=Evidence(extra={"content_type": headers.get("content-type", "")}),
                fix_suggestion="关闭目录浏览，确保站点目录返回索引页或 403/404。",
                confidence="high",
                owasp_category="A05 安全配置错误",
                cwe_id="CWE-548",
            )
        ]


class TraceMethodDetector(BaseVulnDetector):
    """危险 HTTP 方法检测插件。"""

    name = "trace_method"
    version = "1.0"
    supported_depths = ["quick", "standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        allow_header = " ".join(
            f"{k}: {v}" for k, v in context.headers.items()
        ).lower()
        if "trace" not in allow_header and "options" not in allow_header:
            return []

        findings: list[Finding] = []
        if "trace" in allow_header:
            findings.append(
                Finding(
                    title="HTTP TRACE 方法可用",
                    type="trace_method",
                    severity="low",
                    description="服务器暴露了 TRACE 方法，可能放大 XST 或调试类风险。",
                    url=context.url,
                    location=VulnLocation(
                        url=context.url,
                        parameter="Allow",
                        parameter_type="header",
                        snippet="Allow: TRACE",
                    ),
                    evidence=Evidence(extra={"allow": allow_header}),
                    fix_suggestion="关闭 TRACE 方法，仅保留业务必需的 HTTP 方法。",
                    confidence="medium",
                    owasp_category="A05 安全配置错误",
                    cwe_id="CWE-749",
                )
            )
        return findings


def register_builtin_detectors() -> None:
    """注册所有内置检测器。"""
    from app.plugins import DetectorRegistry
    from app.plugins.detectors import (
        BrokenAccessControlDetector,
        APIAuthMissingDetector,
        AuthWeaknessDetector,
        BruteforceProtectionDetector,
        ClickjackingDetector,
        CommandInjectionDetector,
        CSRFDetector,
        DeserializationDetector,
        FileUploadDetector,
        IDORDetector,
        InfoLeakDetector,
        LogicBypassDetector,
        OpenRedirectDetector,
        OutdatedComponentDetector,
        PathTraversalDetector,
        ReflectedXSSDetector,
        SensitiveConfigExposureDetector,
        SensitivePathDetectorPlugin,
        SQLiDetector,
        SSTIDetector,
        SSRFDetector,
        XXEDetector,
    )

    DetectorRegistry.register(HeaderSecurityDetector())
    DetectorRegistry.register(EnhancedHeaderSecurityDetector())
    DetectorRegistry.register(DirectoryListingDetector())
    DetectorRegistry.register(TraceMethodDetector())
    DetectorRegistry.register(SSLInfoDetector())
    DetectorRegistry.register(CookieSecurityDetector())
    DetectorRegistry.register(CORSSecurityDetector())
    DetectorRegistry.register(SQLiDetector())
    DetectorRegistry.register(SSTIDetector())
    DetectorRegistry.register(ReflectedXSSDetector())
    DetectorRegistry.register(InfoLeakDetector())
    DetectorRegistry.register(CSRFDetector())
    DetectorRegistry.register(SensitivePathDetectorPlugin())
    DetectorRegistry.register(AuthWeaknessDetector())
    DetectorRegistry.register(BruteforceProtectionDetector())
    DetectorRegistry.register(APIAuthMissingDetector())
    DetectorRegistry.register(SensitiveConfigExposureDetector())
    DetectorRegistry.register(ClickjackingDetector())
    DetectorRegistry.register(OutdatedComponentDetector())
    DetectorRegistry.register(BrokenAccessControlDetector())
    DetectorRegistry.register(SSRFDetector())
    DetectorRegistry.register(IDORDetector())
    DetectorRegistry.register(FileUploadDetector())
    DetectorRegistry.register(LogicBypassDetector())
    DetectorRegistry.register(OpenRedirectDetector())
    DetectorRegistry.register(XXEDetector())
    DetectorRegistry.register(CommandInjectionDetector())
    DetectorRegistry.register(PathTraversalDetector())
    DetectorRegistry.register(DeserializationDetector())
