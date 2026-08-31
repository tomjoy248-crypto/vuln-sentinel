"""内置检测插件。

将核心检测能力封装为插件，支持通过 DetectorRegistry 统一调度。
"""

from __future__ import annotations

import re

from app.plugins import BaseVulnDetector, Evidence, Finding, ScanContext, VulnLocation


def _lower_header_map(headers: dict[str, str]) -> dict[str, str]:
    """构建大小写无关的头部映射。"""
    return {key.lower(): value for key, value in headers.items()}


def _get_header_value(headers: dict[str, str], name: str) -> str:
    """按名称获取响应头值，忽略大小写。"""
    return _lower_header_map(headers).get(name.lower(), "")


def _parse_csp(policy: str) -> dict[str, list[str]]:
    """解析 CSP 字符串为 directive -> sources 映射。"""
    directives: dict[str, list[str]] = {}
    for raw_part in policy.split(";"):
        part = raw_part.strip()
        if not part:
            continue
        tokens = part.split()
        if not tokens:
            continue
        directives[tokens[0].lower()] = tokens[1:]
    return directives


def _is_version_like(value: str) -> bool:
    """判断头部值是否带有明显版本/构建信息。"""
    if not value:
        return False
    normalized = value.lower()
    return bool(
        re.search(r"/\d", normalized)
        or re.search(r"\b\d+\.\d+(?:\.\d+)?\b", normalized)
        or "(" in normalized
        or "build" in normalized
        or "version" in normalized
    )


def _is_generic_edge_server(value: str) -> bool:
    """判断是否只是常见边缘/CDN 标识，而不是可利用的技术细节。"""
    normalized = value.lower().strip()
    if not normalized:
        return True
    generic_tokens = {
        "cloudflare",
        "cloudfront",
        "akamai",
        "fastly",
        "squid",
        "envoy",
        "varnish",
        "edge",
        "cdn",
        "nginx",
        "apache",
        "iis",
    }
    return normalized in generic_tokens


class ServerExposureDetector(BaseVulnDetector):
    """服务器与框架技术栈泄露检测插件。"""

    name = "server_exposure"
    version = "1.0"
    supported_depths = ["quick", "standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        """检测 Server / X-Powered-By 等头部中的技术栈泄露。"""
        findings: list[Finding] = []
        headers = context.headers
        normalized = _lower_header_map(headers)

        exposure_rules = {
            "server": {
                "title": "Server 头泄露",
                "parameter": "Server",
                "severity": "low",
                "cwe": "CWE-200",
                "owasp": "A05 安全配置错误",
                "fix": "关闭或最小化 Server 头输出；在 Nginx / Apache / 反向代理中禁用版本透出。",
            },
            "x-powered-by": {
                "title": "X-Powered-By 信息泄露",
                "parameter": "X-Powered-By",
                "severity": "low",
                "cwe": "CWE-200",
                "owasp": "A05 安全配置错误",
                "fix": "移除 X-Powered-By 头，避免暴露后端语言或框架信息。",
            },
            "x-aspnet-version": {
                "title": "ASP.NET 版本泄露",
                "parameter": "X-AspNet-Version",
                "severity": "medium",
                "cwe": "CWE-200",
                "owasp": "A05 安全配置错误",
                "fix": "关闭 ASP.NET 版本响应头输出。",
            },
            "x-generator": {
                "title": "X-Generator 信息泄露",
                "parameter": "X-Generator",
                "severity": "low",
                "cwe": "CWE-200",
                "owasp": "A05 安全配置错误",
                "fix": "移除 X-Generator 头，避免暴露构建工具或 CMS 版本。",
            },
        }

        for header_name, rule in exposure_rules.items():
            value = normalized.get(header_name, "").strip()
            if not value:
                continue
            if header_name == "server" and _is_generic_edge_server(value) and not _is_version_like(value):
                continue

            severity = rule["severity"]
            confidence = "medium"
            if _is_version_like(value):
                severity = "medium" if header_name == "server" else "high"
                confidence = "high"

            findings.append(
                Finding(
                    title=rule["title"],
                    type="server_exposure",
                    severity=severity,
                    description=f"响应头 {rule['parameter']} 暴露了技术栈信息：{value}。攻击者可能据此缩小攻击面。",
                    url=context.url,
                    location=VulnLocation(
                        url=context.url,
                        parameter=rule["parameter"],
                        parameter_type="header",
                        snippet=f"{rule['parameter']}: {value}",
                    ),
                    evidence=Evidence(
                        extra={
                            "header": rule["parameter"],
                            "value": value,
                        }
                    ),
                    fix_suggestion=rule["fix"],
                    confidence=confidence,
                    owasp_category=rule["owasp"],
                    cwe_id=rule["cwe"],
                )
            )

        return findings


class CSPPolicyWeaknessDetector(BaseVulnDetector):
    """CSP 策略过宽检测插件。"""

    name = "csp_policy_weakness"
    version = "1.0"
    supported_depths = ["quick", "standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        """检测可被滥用的 CSP 配置。"""
        csp = _get_header_value(context.headers, "Content-Security-Policy").strip()
        if not csp:
            return []

        directives = _parse_csp(csp)
        issues: list[str] = []
        issue_codes: list[str] = []

        def _sources(name: str) -> list[str]:
            return directives.get(name, [])

        script_sources = _sources("script-src") or _sources("default-src")
        frame_sources = _sources("frame-ancestors")
        object_sources = _sources("object-src")
        connect_sources = _sources("connect-src")

        if any(token == "*" for token in script_sources):
            issues.append("script 相关来源过宽，允许 *")
            issue_codes.append("script_wildcard")
        if any(token in {"'unsafe-inline'", "'unsafe-eval'", "'unsafe-hashes'"} for token in script_sources):
            issues.append("script 相关策略包含 unsafe-inline / unsafe-eval")
            if any(token == "'unsafe-eval'" for token in script_sources):
                issue_codes.append("unsafe_eval")
            if any(token == "'unsafe-inline'" for token in script_sources):
                issue_codes.append("unsafe_inline")
        if any(token.startswith("http:") for token in script_sources):
            issues.append("script 相关策略允许明文 HTTP 来源")
            issue_codes.append("http_source")
        if any(token == "*" for token in frame_sources):
            issues.append("frame-ancestors 允许任意站点嵌入")
            issue_codes.append("frame_ancestors_wildcard")
        if object_sources and not any(token == "'none'" for token in object_sources):
            issues.append("object-src 未收紧为 'none'")
            issue_codes.append("object_src_open")
        if any(token == "*" for token in connect_sources):
            issues.append("connect-src 允许任意出站连接")
            issue_codes.append("connect_src_wildcard")

        if not issues:
            return []

        severity = "medium"
        if any(code in {"unsafe_eval", "http_source"} for code in issue_codes):
            severity = "high"

        return [
            Finding(
                title="CSP 策略过宽",
                type="csp_weakness",
                severity=severity,
                description="Content-Security-Policy 存在可被滥用的放宽项，可能削弱对 XSS 和点击劫持的防护。",
                url=context.url,
                location=VulnLocation(
                    url=context.url,
                    parameter="Content-Security-Policy",
                    parameter_type="header",
                    snippet=csp,
                ),
                evidence=Evidence(extra={"policy": csp, "issues": issues}),
                fix_suggestion="收紧 CSP：避免使用 unsafe-inline / unsafe-eval，减少通配符和明文来源，按业务最小权限配置各 directive。",
                confidence="high",
                owasp_category="A05 安全配置错误",
                cwe_id="CWE-693",
            )
        ]


class PassiveExposureDetector(BaseVulnDetector):
    """被动泄露检测插件。"""

    name = "passive_exposure"
    version = "1.0"
    supported_depths = ["quick", "standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        """检测 source map、调试标记和堆栈信息。"""
        body = context.body or ""
        if not body:
            return []

        findings: list[Finding] = []
        lowered = body.lower()

        source_map_hits = []
        if re.search(r"sourceMappingURL\s*=", body, re.I):
            source_map_hits.append("sourceMappingURL")
        if re.search(r"\.map(?:[\s'\"?#]|$)", body, re.I):
            source_map_hits.append(".map")

        if source_map_hits:
            findings.append(
                Finding(
                    title="暴露源码映射文件",
                    type="info_leak",
                    severity="medium",
                    description="页面包含 source map 或 .map 引用，可能帮助攻击者还原前端源码结构和接口逻辑。",
                    url=context.url,
                    location=VulnLocation(
                        url=context.url,
                        parameter="",
                        parameter_type="path",
                        snippet="sourceMappingURL / .map",
                    ),
                    evidence=Evidence(
                        extra={
                            "signals": source_map_hits,
                            "excerpt": body[:300],
                        }
                    ),
                    fix_suggestion="生产环境移除 source map，或限制其访问权限并避免在公开页面引用。",
                    confidence="high",
                    owasp_category="A05 安全配置错误",
                    cwe_id="CWE-200",
                )
            )

        debug_patterns = [
            "console.log",
            "var_dump",
            "print_r",
            "debug=true",
            "stack trace",
            "traceback (most recent call last)",
            "exception in thread",
            "fatal error",
        ]
        matched_debug = [pattern for pattern in debug_patterns if pattern in lowered]
        if matched_debug:
            findings.append(
                Finding(
                    title="调试信息泄露",
                    type="info_leak",
                    severity="high" if any(item in {"stack trace", "traceback (most recent call last)", "fatal error"} for item in matched_debug) else "medium",
                    description="页面暴露了调试输出或堆栈痕迹，可能泄露框架、内部路径和异常细节。",
                    url=context.url,
                    location=VulnLocation(
                        url=context.url,
                        parameter="",
                        parameter_type="path",
                        snippet="debug marker / stack trace",
                    ),
                    evidence=Evidence(
                        extra={
                            "signals": matched_debug,
                            "excerpt": body[:300],
                        }
                    ),
                    fix_suggestion="关闭调试模式，隐藏异常堆栈，并确保生产环境不输出调试日志。",
                    confidence="high",
                    owasp_category="A05 安全配置错误",
                    cwe_id="CWE-200",
                )
            )

        return findings


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
    DetectorRegistry.register(CSPPolicyWeaknessDetector())
    DetectorRegistry.register(ServerExposureDetector())
    DetectorRegistry.register(PassiveExposureDetector())
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
