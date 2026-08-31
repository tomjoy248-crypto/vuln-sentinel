"""内置检测插件。

将核心检测能力封装为插件，支持通过 DetectorRegistry 统一调度。
"""

from __future__ import annotations

import json
import re
from urllib.parse import parse_qs, unquote, urljoin, urlparse

import httpx

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


def _extract_sensitive_discovery_hits(text: str) -> list[str]:
    """从 robots / sitemap 文本中提取敏感暴露信号。"""
    lowered = text.lower()
    patterns = {
        "admin": r"(?:(?:disallow|allow|loc)\s*[:=]\s*.*(?:/admin\b|/administrator\b|/manage\b|/console\b))|(?:https?://[^ \n]+/(?:admin|administrator|manage|console)(?:[/?#\s]|$))",
        "api_admin": r"(?:/api/(?:admin|internal|private|debug)\b)",
        "login": r"(?:/login\b|/signin\b|/auth\b)",
        "debug": r"(?:/debug\b|/trace\b|/console\b)",
        "backup": r"(?:/backup\b|/dump\b|/export\b|/download\b|\.bak\b|\.old\b|\.sql\b)",
        "config": r"(?:/config\b|/settings\b|\.env\b|\.git\b|\.svn\b|\.ini\b|\.yml\b|\.yaml\b)",
        "swagger": r"(?:/swagger\b|/redoc\b|/openapi\b|/api-docs\b)",
        "internal": r"(?:/internal\b|/private\b|/staging\b|/dev\b|/test\b)",
    }
    hits: list[str] = []
    for label, pattern in patterns.items():
        if re.search(pattern, lowered, re.I):
            hits.append(label)
    return hits


def _flatten_strings(value: object) -> list[str]:
    """递归提取结构化数据中的字符串值。"""
    strings: list[str] = []
    if isinstance(value, str):
        strings.append(value)
    elif isinstance(value, dict):
        for item in value.values():
            strings.extend(_flatten_strings(item))
    elif isinstance(value, (list, tuple, set)):
        for item in value:
            strings.extend(_flatten_strings(item))
    return strings


def _score_signal_pairs(pairs: list[tuple[bool, int]]) -> int:
    """按命中信号对证据强度打分。"""
    return min(100, sum(weight for matched, weight in pairs if matched))


def _decoded_query_values(url: str) -> dict[str, list[str]]:
    """提取并解码 URL 查询参数。"""
    try:
        parsed = urlparse(url)
        values = parse_qs(parsed.query, keep_blank_values=True)
    except Exception:
        return {}
    decoded: dict[str, list[str]] = {}
    for key, items in values.items():
        decoded[key.lower()] = [unquote(str(item or "")) for item in items]
    return decoded


def _extract_well_known_hits(text: str) -> list[str]:
    """从 well-known 文本或 JSON 中提取敏感暴露信号。"""
    lowered = text.lower()
    hits: list[str] = []

    try:
        parsed = json.loads(text)
    except Exception:
        parsed = None

    strings = _flatten_strings(parsed) if parsed is not None else []
    strings.append(text)

    patterns = {
        "internal_host": r"(?:localhost|127\.0\.0\.1|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|\.internal\b|\.local\b|\.lan\b)",
        "admin_path": r"(?:/admin\b|/administrator\b|/manage\b|/console\b|/debug\b|/trace\b)",
        "backup_path": r"(?:/backup\b|/dump\b|/export\b|/download\b|\.bak\b|\.old\b|\.sql\b)",
        "config_path": r"(?:/config\b|/settings\b|\.env\b|\.git\b|\.svn\b|\.ini\b|\.yml\b|\.yaml\b)",
        "auth_endpoint": r"(?:authorization_endpoint|token_endpoint|jwks_uri|userinfo_endpoint|registration_endpoint|introspection_endpoint|revocation_endpoint|device_authorization_endpoint)",
        "internal_api": r"(?:/api/(?:internal|private|admin|debug)\b)",
        "openid": r"openid-configuration",
        "app_link": r"(?:assetlinks\.json|apple-app-site-association|mta-sts\.txt|security\.txt)",
    }

    for label, pattern in patterns.items():
        for item in strings:
            if re.search(pattern, item, re.I):
                hits.append(label)
                break

    return list(dict.fromkeys(hits))


def _parse_html_attributes(raw_attrs: str) -> dict[str, str]:
    """从 HTML 标签属性片段中提取属性名和值。"""
    attrs: dict[str, str] = {}
    for match in re.finditer(
        r"""(?P<name>[\w:-]+)(?:\s*=\s*(?:
            "(?P<dq>[^"]*)"
            |'(?P<sq>[^']*)'
            |(?P<bare>[^\s"'=<>`]+)
        ))?""",
        raw_attrs,
        re.IGNORECASE | re.VERBOSE,
    ):
        name = match.group("name").lower()
        value = match.group("dq") or match.group("sq") or match.group("bare") or ""
        attrs[name] = value.strip()
    return attrs


def _is_cross_origin_resource(page_url: str, resource_url: str) -> bool:
    """判断资源是否为跨域子资源。"""
    if not resource_url:
        return False
    resolved = urljoin(page_url, resource_url)
    parsed_page = urlparse(page_url)
    parsed_resource = urlparse(resolved)
    if parsed_resource.scheme not in {"http", "https"}:
        return False
    if not parsed_resource.netloc:
        return False
    return (
        parsed_resource.scheme.lower(),
        parsed_resource.netloc.lower(),
    ) != (
        parsed_page.scheme.lower(),
        parsed_page.netloc.lower(),
    )


def _iter_html_resource_tags(body: str) -> list[dict[str, str]]:
    """提取 HTML 中常见前端资源标签。"""
    resources: list[dict[str, str]] = []
    tag_pattern = re.compile(r"<(?P<tag>script|link|iframe)\b(?P<attrs>[^>]*)>", re.IGNORECASE)
    for match in tag_pattern.finditer(body or ""):
        tag = match.group("tag").lower()
        attrs = _parse_html_attributes(match.group("attrs"))
        if tag == "script":
            resource_url = attrs.get("src", "")
            if not resource_url:
                continue
        elif tag == "link":
            rel_value = attrs.get("rel", "").lower()
            if "stylesheet" not in {item.strip() for item in rel_value.split()}:
                continue
            resource_url = attrs.get("href", "")
            if not resource_url:
                continue
        else:
            resource_url = attrs.get("src", "")
            if not resource_url:
                continue

        resources.append(
            {
                "tag": tag,
                "url": resource_url,
                "resolved_url": urljoin("", resource_url),
                "integrity": attrs.get("integrity", ""),
                "crossorigin": attrs.get("crossorigin", ""),
                "rel": attrs.get("rel", ""),
            }
        )
    return resources


def _match_unpinned_package_cdn(resource_url: str) -> str | None:
    """识别未固定版本的第三方包 CDN 资源。"""
    parsed = urlparse(resource_url)
    host = parsed.netloc.lower()
    path = parsed.path or "/"

    if host == "unpkg.com":
        scoped_pinned = re.match(r"^/@[^/]+/[^/@]+@[^/]+(?:/|$)", path)
        package_pinned = re.match(r"^/[^/@]+@[^/]+(?:/|$)", path)
        if not scoped_pinned and not package_pinned:
            return "unpkg"

    if host == "cdn.jsdelivr.net":
        if path.startswith("/npm/"):
            rest = path[len("/npm/") :]
            scoped_pinned = re.match(r"^@[^/]+/[^/@]+@[^/]+(?:/|$)", rest)
            package_pinned = re.match(r"^[^/@]+@[^/]+(?:/|$)", rest)
            if not scoped_pinned and not package_pinned:
                return "jsdelivr-npm"
        if path.startswith("/gh/"):
            rest = path[len("/gh/") :]
            if not re.match(r"^[^/]+/[^/@]+@[^/]+(?:/|$)", rest):
                return "jsdelivr-gh"

    if host in {"raw.githubusercontent.com", "gist.githubusercontent.com"}:
        return "raw-github"

    return None


def _extract_first_form(body: str) -> str:
    """提取页面中的第一个 form 块。"""
    match = re.search(r"<form[^>]*>.*?</form>", body or "", re.IGNORECASE | re.DOTALL)
    return match.group(0) if match else ""


def _looks_like_login_or_challenge(body: str, headers: dict[str, str]) -> bool:
    """判断响应是否更像登录页、认证页或挑战页。"""
    text = f"{body}\n" + "\n".join(f"{k}: {v}" for k, v in headers.items())
    lowered = text.lower()
    markers = (
        "login",
        "sign in",
        "signin",
        "authentication required",
        "please sign in",
        "please log in",
        "请登录",
        "请先登录",
        "验证码",
        "challenge",
        "verify you are human",
        "turnstile",
        "captcha",
    )
    return any(marker in lowered for marker in markers)


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


class SRIIntegrityDetector(BaseVulnDetector):
    """跨域脚本与样式缺少 SRI 保护检测插件。"""

    name = "sri_integrity"
    version = "1.0"
    supported_depths = ["quick", "standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        """检测跨域 script / stylesheet 是否缺少 integrity 属性。"""
        body = context.body or ""
        if not body:
            return []

        missing_resources: list[dict[str, str]] = []
        for resource in _iter_html_resource_tags(body):
            if resource["tag"] not in {"script", "link"}:
                continue
            resource_url = resource["url"]
            if not _is_cross_origin_resource(context.url, resource_url):
                continue
            if resource["integrity"].strip():
                continue

            missing_resources.append(
                {
                    "tag": resource["tag"],
                    "url": urljoin(context.url, resource_url),
                }
            )

        if not missing_resources:
            return []

        snippet = ", ".join(item["url"] for item in missing_resources[:3])
        resource_kinds = sorted({item["tag"] for item in missing_resources})
        return [
            Finding(
                title="跨域子资源缺少 SRI 完整性保护",
                type="sri_missing",
                severity="low",
                description="页面引用了跨域脚本或样式资源，但未配置 integrity 属性，供应链资源被篡改时浏览器无法进行完整性校验。",
                url=context.url,
                location=VulnLocation(
                    url=context.url,
                    parameter="integrity",
                    parameter_type="html",
                    snippet=snippet,
                ),
                evidence=Evidence(
                    extra={
                        "missing_resources": missing_resources,
                        "resource_types": resource_kinds,
                    }
                ),
                fix_suggestion="为跨域 script 和 stylesheet 增加 SRI integrity 属性，并配合固定版本资源或可信发布流程统一维护哈希值。",
                confidence="high",
                owasp_category="A05 安全配置错误",
                cwe_id="CWE-353",
            )
        ]


class FrontendSupplyChainDetector(BaseVulnDetector):
    """前端供应链与明文资源风险检测插件。"""

    name = "frontend_supply_chain"
    version = "1.0"
    supported_depths = ["quick", "standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        """检测 HTTPS 页面明文资源与未固定版本的第三方前端依赖。"""
        body = context.body or ""
        if not body:
            return []

        resources = _iter_html_resource_tags(body)
        if not resources:
            return []

        findings: list[Finding] = []
        parsed_page = urlparse(context.url)
        mixed_resources: list[dict[str, str]] = []
        unpinned_resources: list[dict[str, str]] = []

        for resource in resources:
            resolved_url = urljoin(context.url, resource["url"])
            parsed_resource = urlparse(resolved_url)
            if parsed_page.scheme.lower() == "https" and parsed_resource.scheme.lower() == "http":
                mixed_resources.append(
                    {
                        "tag": resource["tag"],
                        "url": resolved_url,
                    }
                )

            if not _is_cross_origin_resource(context.url, resource["url"]):
                continue
            source_kind = _match_unpinned_package_cdn(resolved_url)
            if source_kind:
                unpinned_resources.append(
                    {
                        "tag": resource["tag"],
                        "url": resolved_url,
                        "source_kind": source_kind,
                    }
                )

        if mixed_resources:
            findings.append(
                Finding(
                    title="HTTPS 页面加载明文前端资源",
                    type="supply_chain_exposure",
                    severity="medium",
                    description="HTTPS 页面中存在通过 HTTP 加载的脚本、样式或 iframe 资源，链路可被中间人篡改，影响前端代码与页面完整性。",
                    url=context.url,
                    location=VulnLocation(
                        url=context.url,
                        parameter="src/href",
                        parameter_type="html",
                        snippet=", ".join(item["url"] for item in mixed_resources[:3]),
                    ),
                    evidence=Evidence(
                        extra={
                            "mixed_resources": mixed_resources,
                            "resource_count": len(mixed_resources),
                        }
                    ),
                    fix_suggestion="将所有前端活动资源统一切换为 HTTPS，并检查 CDN、第三方组件和嵌入页面是否仍引用明文地址。",
                    confidence="high",
                    owasp_category="A05 安全配置错误",
                    cwe_id="CWE-319",
                )
            )

        if unpinned_resources:
            findings.append(
                Finding(
                    title="第三方前端资源未固定版本",
                    type="supply_chain_exposure",
                    severity="low",
                    description="页面直接引用了未固定版本或直接来自代码仓库的第三方前端资源，发布内容变化时可能引入供应链不确定性。",
                    url=context.url,
                    location=VulnLocation(
                        url=context.url,
                        parameter="src/href",
                        parameter_type="html",
                        snippet=", ".join(item["url"] for item in unpinned_resources[:3]),
                    ),
                    evidence=Evidence(
                        extra={
                            "unpinned_resources": unpinned_resources,
                            "resource_count": len(unpinned_resources),
                        }
                    ),
                    fix_suggestion="优先使用固定版本的发布地址，并结合 SRI、私有镜像或发布白名单控制第三方前端依赖的变更面。",
                    confidence="high",
                    owasp_category="A06 易受攻击和过时的组件",
                    cwe_id="CWE-494",
                )
            )

        return findings


class LoginSurfaceDetector(BaseVulnDetector):
    """登录面安全配置检测插件。"""

    name = "login_surface"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    _login_path_hints = [
        "/login",
        "/signin",
        "/sign-in",
        "/user/login",
        "/admin/login",
        "/auth/login",
        "/account/login",
        "/member/login",
        "/wp-login.php",
    ]
    _anti_bot_hints = (
        "captcha",
        "验证码",
        "二次验证",
        "双重验证",
        "mfa",
        "2fa",
        "otp",
        "短信验证码",
        "邮箱验证码",
        "security code",
        "authenticator",
        "turnstile",
        "recaptcha",
    )

    async def detect(self, context: ScanContext) -> list[Finding]:
        """检测登录表单防护和基础防爆破信号。"""
        origin = f"{urlparse(context.url).scheme}://{urlparse(context.url).netloc}"
        findings: list[Finding] = []

        try:
            async with httpx.AsyncClient(
                follow_redirects=True,
                headers=context.headers or None,
            ) as client:
                for rel_path in self._login_path_hints:
                    login_url = urljoin(origin, rel_path)
                    try:
                        resp = await client.get(login_url, timeout=8.0)
                    except Exception:
                        continue
                    if resp.status_code != 200:
                        continue

                    body = resp.text or ""
                    if not re.search(
                        r'<input[^>]*type=["\']password["\']',
                        body,
                        re.IGNORECASE,
                    ):
                        continue

                    form_html = _extract_first_form(body)
                    form_lower = form_html.lower()
                    body_lower = body.lower()
                    issues: list[str] = []

                    if form_html:
                        if (
                            'autocomplete="off"' not in form_lower
                            and "autocomplete='off'" not in form_lower
                        ):
                            issues.append("login_page_no_autocomplete_off")

                        csrf_found = False
                        for input_tag in re.findall(r"<input[^>]*>", form_html, re.IGNORECASE):
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
                            if not any(token in name for token in ("csrf", "token", "nonce")):
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

                    response_headers = _lower_header_map(dict(resp.headers))
                    if not (
                        response_headers.get("x-frame-options")
                        or "frame-ancestors" in response_headers.get("content-security-policy", "").lower()
                    ):
                        issues.append("login_page_no_xfo")

                    if not any(hint in body_lower for hint in self._anti_bot_hints):
                        issues.append("bruteforce_protection_missing")

                    evidence = {
                        "login_path": rel_path,
                        "issues": issues,
                        "status_code": resp.status_code,
                    }

                    auth_issues: list[str] = []
                    if "csrf_token_missing" in issues:
                        auth_issues.append("登录表单缺少 CSRF token")
                    if "login_page_no_xfo" in issues:
                        auth_issues.append("登录页缺少 X-Frame-Options 或 frame-ancestors")
                    if "login_page_no_autocomplete_off" in issues:
                        auth_issues.append("登录表单未关闭自动补全")

                    if auth_issues:
                        severity = "high" if "csrf_token_missing" in issues else "medium"
                        findings.append(
                            Finding(
                                title="认证保护不足",
                                type="auth_weakness",
                                severity=severity,
                                description="登录页面存在基础认证防护缺口，攻击者可能借此增加点击劫持、跨站请求或凭据暴露风险。",
                                url=login_url,
                                location=VulnLocation(
                                    url=login_url,
                                    parameter="login form",
                                    parameter_type="html",
                                    snippet=rel_path,
                                ),
                                evidence=Evidence(
                                    extra={
                                        **evidence,
                                        "auth_issues": auth_issues,
                                    },
                                    response_raw=body[:4000],
                                ),
                                fix_suggestion="为登录表单补充 CSRF token、autocomplete=\"off\"、X-Frame-Options 或 CSP frame-ancestors，并统一加固会话 Cookie 与 Origin/Referer 校验。",
                                confidence="high" if severity == "high" else "medium",
                                owasp_category="A07 身份识别与认证失败",
                                cwe_id="CWE-306",
                            )
                        )

                    if "bruteforce_protection_missing" in issues:
                        findings.append(
                            Finding(
                                title="登录防爆破不足",
                                type="bruteforce_protection",
                                severity="medium",
                                description="登录页面未发现明显的验证码、二次验证或其他防爆破提示，自动化撞库与口令尝试成本较低。",
                                url=login_url,
                                location=VulnLocation(
                                    url=login_url,
                                    parameter="login form",
                                    parameter_type="html",
                                    snippet=rel_path,
                                ),
                                evidence=Evidence(
                                    extra=evidence,
                                    response_raw=body[:4000],
                                ),
                                fix_suggestion="为登录与找回密码流程增加验证码、二次验证、失败锁定、账号/IP 维度限流和审计日志。",
                                confidence="medium",
                                owasp_category="A07 身份识别与认证失败",
                                cwe_id="CWE-307",
                            )
                        )

                    break
        except Exception:
            return findings

        return findings


class ProtectedRouteExposureDetector(BaseVulnDetector):
    """后台/敏感路由匿名访问检测插件。"""

    name = "protected_route_exposure"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    _protected_path_hints = [
        "/admin",
        "/admin/dashboard",
        "/admin/users",
        "/dashboard",
        "/account",
        "/profile",
        "/settings",
        "/management",
        "/user",
        "/user/profile",
        "/api/me",
        "/api/user",
        "/api/account",
        "/api/profile",
        "/api/admin",
        "/api/admin/audit",
        "/api/admin/users",
        "/api/users",
        "/api/settings",
    ]
    _protected_keywords = (
        "dashboard",
        "admin",
        "account",
        "profile",
        "settings",
        "logout",
        "user center",
        "管理",
        "权限",
        "role",
        "permission",
        "email",
        "username",
    )
    _sensitive_json_keys = (
        "email",
        "username",
        "user_id",
        "userid",
        "role",
        "permission",
        "token",
        "secret",
        "admin",
        "settings",
    )
    _admin_json_keys = ("role", "permission", "admin", "settings", "token", "secret")
    _profile_keywords = ("account", "profile", "email", "username", "user center")

    def _classify_page_exposure(self, rel_path: str, body_lower: str) -> tuple[str, str, str, str, str]:
        is_admin_surface = any(token in rel_path for token in ("/admin", "/management", "/settings", "/dashboard"))
        if is_admin_surface or "admin" in body_lower or "permission" in body_lower:
            return (
                "后台管理页面匿名可访问",
                "admin_page_exposure",
                "high",
                "high",
                "management_page",
            )
        return (
            "用户账户页面匿名可访问",
            "user_profile_exposure",
            "medium",
            "medium",
            "profile_page",
        )

    def _classify_api_exposure(self, rel_path: str, matched_keys: list[str]) -> tuple[str, str, str, str, str]:
        admin_keys = [key for key in matched_keys if key in self._admin_json_keys]
        if admin_keys or "/api/admin" in rel_path or "/api/settings" in rel_path:
            return (
                "管理接口匿名可访问",
                "admin_api_exposure",
                "critical",
                "high",
                "admin_api_data",
            )
        return (
            "用户数据接口匿名可访问",
            "user_data_api_exposure",
            "high",
            "high" if matched_keys else "medium",
            "user_api_data",
        )

    async def detect(self, context: ScanContext) -> list[Finding]:
        """检测匿名请求是否能直接访问后台页面或敏感接口。"""
        origin = f"{urlparse(context.url).scheme}://{urlparse(context.url).netloc}"
        findings: list[Finding] = []

        try:
            async with httpx.AsyncClient(
                follow_redirects=False,
                headers=context.headers or None,
            ) as client:
                for rel_path in self._protected_path_hints:
                    target_url = urljoin(origin, rel_path)
                    try:
                        resp = await client.get(
                            target_url,
                            timeout=8.0,
                            headers={
                                "User-Agent": "Mozilla/5.0",
                                "Accept": "application/json, text/html;q=0.9, */*;q=0.8",
                            },
                        )
                    except Exception:
                        continue

                    if resp.status_code in {401, 403}:
                        continue
                    if resp.status_code in {301, 302, 303, 307, 308}:
                        location = resp.headers.get("location", "")
                        if _looks_like_login_or_challenge(location, {}):
                            continue
                    if resp.status_code != 200:
                        continue

                    body = resp.text or ""
                    header_map = dict(resp.headers)
                    if _looks_like_login_or_challenge(body, header_map):
                        continue

                    body_lower = body.lower()
                    content_type = (resp.headers.get("content-type") or "").lower()
                    is_api = rel_path.startswith("/api/")
                    has_sensitive_json = False
                    matched_keys: list[str] = []
                    if is_api and ("json" in content_type or body.lstrip().startswith(("{", "["))):
                        matched_keys = [
                            key for key in self._sensitive_json_keys if f'"{key.lower()}"' in body_lower
                        ]
                        has_sensitive_json = len(matched_keys) >= 1

                    matched_keywords = [
                        term for term in self._protected_keywords if term in body_lower
                    ]
                    page_exposure_candidate = self._classify_page_exposure(
                        rel_path, body_lower
                    )[4]
                    has_sensitive_text = len(matched_keywords) >= (
                        1 if page_exposure_candidate == "management_page" else 2
                    )
                    if not has_sensitive_json and not has_sensitive_text:
                        continue

                    if is_api:
                        title, finding_type, severity, confidence, exposure_kind = self._classify_api_exposure(rel_path, matched_keys)
                        description = (
                            "未登录请求即可访问管理类接口并返回权限、配置或后台管理数据。"
                            if exposure_kind == "admin_api_data"
                            else "未登录请求即可访问用户数据接口并返回账号、身份或资料信息。"
                        )
                        fix = "为相关 API 统一增加会话或 Bearer 鉴权，并补充对象级授权，匿名请求应返回 401/403。"
                    else:
                        title, finding_type, severity, confidence, exposure_kind = self._classify_page_exposure(rel_path, body_lower)
                        description = (
                            "未登录请求即可访问后台管理页面，管理面暴露在匿名访问边界之外。"
                            if exposure_kind == "management_page"
                            else "未登录请求即可访问账户或个人资料页面，访问控制边界可能不足。"
                        )
                        fix = "对后台页面统一挂载认证中间件和角色校验，未登录访问应跳转登录页或返回 401/403。"

                    evidence_score = _score_signal_pairs(
                        [
                            (resp.status_code == 200, 30),
                            (is_api, 15),
                            ("/admin" in rel_path or "/management" in rel_path, 20),
                            ("/profile" in rel_path or "/account" in rel_path or "/user" in rel_path, 15),
                            (len(matched_keys) >= 1, 20),
                            (len(matched_keys) >= 2, 10),
                            (len(matched_keywords) >= 2, 10),
                        ]
                    )
                    if evidence_score < (55 if is_api else 40):
                        continue

                    findings.append(
                        Finding(
                            title=title,
                            type=finding_type,
                            severity=severity,
                            description=description,
                            url=target_url,
                            location=VulnLocation(
                                url=target_url,
                                parameter="",
                                parameter_type="path",
                                snippet=rel_path,
                            ),
                            evidence=Evidence(
                                extra={
                                    "path": rel_path,
                                    "status_code": resp.status_code,
                                    "content_type": content_type,
                                    "matched_keys": matched_keys[:8],
                                    "matched_keywords": matched_keywords[:8],
                                    "exposure_kind": exposure_kind,
                                    "evidence_score": evidence_score,
                                    "data_classification": (
                                        "admin"
                                        if exposure_kind in {"admin_api_data", "management_page"}
                                        else "user"
                                    ),
                                    "is_api": is_api,
                                },
                                response_raw=body[:4000],
                            ),
                            fix_suggestion=fix,
                            confidence=confidence,
                            owasp_category="A01 访问控制失效",
                            cwe_id="CWE-284",
                        )
                    )
        except Exception:
            return findings

        return findings


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


class ApiSurfaceExposureDetector(BaseVulnDetector):
    """API 入口面暴露检测插件。"""

    name = "api_surface_exposure"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        """检测页面源码是否显式暴露 API 路径。"""
        body = context.body or ""
        if not body:
            return []

        lowered = body.lower()
        route_pattern = re.compile(
            r"""(?:
                ['"`]
                (?P<path>/(?:api|v\d+)(?:/[^\s"'`<>()]+)+)
                ['"`]
            )""",
            re.IGNORECASE | re.VERBOSE,
        )
        routes = sorted({match.group("path") for match in route_pattern.finditer(body)})

        graphql_refs = []
        if "/graphql" in lowered:
            graphql_refs.append("/graphql")
        if "graphql" in lowered and ("fetch(" in lowered or "axios" in lowered or "query" in lowered):
            graphql_refs.append("graphql")

        if not routes and not graphql_refs:
            return []

        route_hints = [
            route
            for route in routes
            if any(token in route.lower() for token in ("/admin", "/internal", "/debug", "/private"))
        ]
        severity = "low"
        if route_hints or len(routes) >= 5:
            severity = "medium"

        excerpt = body[:400]
        return [
            Finding(
                title="API 入口面暴露",
                type="api_surface_exposure",
                severity=severity,
                description="页面源码或前端脚本中直接暴露了 API 路径与入口线索，攻击者可据此缩小枚举范围并定位业务接口。",
                url=context.url,
                location=VulnLocation(
                    url=context.url,
                    parameter="",
                    parameter_type="path",
                    snippet="API 路径引用",
                ),
                evidence=Evidence(
                    extra={
                        "matched_routes": routes,
                        "graphql_refs": graphql_refs,
                        "excerpt": excerpt,
                    }
                ),
                fix_suggestion="尽量避免在公开页面中直接暴露完整 API 路径、内部命名空间和调试入口；对管理类接口使用鉴权与最小权限控制。",
                confidence="high",
                owasp_category="A05 安全配置错误",
                cwe_id="CWE-200",
            )
        ]


class OAuthSurfaceDetector(BaseVulnDetector):
    """前端 OAuth / SSO 授权面暴露检测插件。"""

    name = "oauth_surface"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        body = context.body or ""
        if not body:
            return []

        lowered = body.lower()
        auth_urls = sorted(
            {
                match.group(1)
                for match in re.finditer(
                    r"""['"](https?://[^'"<>]+/(?:oauth|oidc|openid-connect|sso)[^'"<>]*)['"]""",
                    body,
                    re.I,
                )
            }
        )
        callback_paths = sorted(
            {
                match.group(1)
                for match in re.finditer(
                    r"""['"]((?:/|https?://[^'"<>]+/)(?:oauth|auth|sso)[^'"<>]*(?:callback|redirect)[^'"<>]*)['"]""",
                    body,
                    re.I,
                )
            }
        )
        has_client_id = bool(
            re.search(r"(client[_-]?id\s*[:=]\s*['\"][^'\"]+['\"]|client_id=)", body, re.I)
        )
        implicit_flow = bool(
            re.search(r"response_type=(?:token|id_token|token%20id_token|id_token%20token)", lowered)
        )
        auth_code_flow = "response_type=code" in lowered or "authorization_code" in lowered
        has_pkce = "code_challenge" in lowered or "pkce" in lowered
        has_state = "state=" in lowered or re.search(r"state\s*[:=]\s*['\"]", body, re.I)
        redirect_targets: list[str] = []
        insecure_redirects: list[str] = []
        wildcard_redirects: list[str] = []
        state_missing_urls: list[str] = []
        nonce_missing_entries: list[tuple[str, str, str]] = []
        for auth_url in auth_urls:
            query = _decoded_query_values(auth_url)
            scope_values = " ".join(query.get("scope", [])).lower()
            response_type_values = " ".join(query.get("response_type", [])).lower()
            scope_tokens = {token for token in re.split(r"\s+", scope_values) if token}
            response_type_tokens = {token for token in re.split(r"[\s+]+", response_type_values) if token}
            has_oidc_scope = "openid" in scope_tokens
            has_oidc_implicit = bool(response_type_tokens & {"token", "id_token"})
            has_oidc_code = "code" in response_type_tokens
            has_nonce = bool(query.get("nonce"))
            redirect_values = (
                query.get("redirect_uri", [])
                + query.get("post_logout_redirect_uri", [])
                + query.get("returnto", [])
                + query.get("relaystate", [])
            )
            for target in redirect_values:
                if target not in redirect_targets:
                    redirect_targets.append(target)
                normalized = target.lower().strip()
                if (
                    normalized.startswith("http://")
                    or "localhost" in normalized
                    or "127.0.0.1" in normalized
                    or "0.0.0.0" in normalized
                ) and target not in insecure_redirects:
                    insecure_redirects.append(target)
                if "*" in normalized and target not in wildcard_redirects:
                    wildcard_redirects.append(target)
                if "state" not in query and auth_url not in state_missing_urls:
                    state_missing_urls.append(auth_url)
            if has_oidc_scope and not has_nonce:
                flow_label = "implicit" if has_oidc_implicit else "authorization_code" if has_oidc_code else "unknown"
                severity_label = "high" if has_oidc_implicit else "medium" if has_oidc_code else "low"
                entry = (auth_url, severity_label, flow_label)
                if entry not in nonce_missing_entries:
                    nonce_missing_entries.append(entry)

        findings: list[Finding] = []
        if implicit_flow and auth_urls:
            evidence_score = _score_signal_pairs(
                [
                    (True, 40),
                    (len(auth_urls) >= 1, 20),
                    (has_client_id, 15),
                    (len(callback_paths) >= 1, 15),
                    (not has_state, 10),
                ]
            )
            findings.append(
                Finding(
                    title="前端暴露 OAuth 隐式流入口",
                    type="oauth_surface_exposure",
                    severity="high",
                    description="页面脚本中直接暴露了 OAuth 隐式流授权入口，令牌可能经前端跳转或片段回传，泄露面相对更大。",
                    url=context.url,
                    location=VulnLocation(
                        url=context.url,
                        parameter="oauth authorize url",
                        parameter_type="html",
                        snippet="response_type=token / id_token",
                    ),
                    evidence=Evidence(
                        extra={
                            "auth_urls": auth_urls[:6],
                            "callback_paths": callback_paths[:6],
                            "has_client_id": has_client_id,
                            "has_state": bool(has_state),
                            "flow": "implicit",
                            "evidence_score": evidence_score,
                        },
                        response_raw=body[:4000],
                    ),
                    fix_suggestion="优先改用授权码 + PKCE，避免在前端使用隐式流；同时确保 state 校验、最小化回调暴露并限制 redirect URI。",
                    confidence="high",
                    owasp_category="A07 身份识别与认证失败",
                    cwe_id="CWE-287",
                )
            )

        if auth_urls and callback_paths and has_client_id and auth_code_flow and not has_pkce:
            evidence_score = _score_signal_pairs(
                [
                    (True, 30),
                    (len(auth_urls) >= 1, 20),
                    (len(callback_paths) >= 1, 20),
                    (has_client_id, 15),
                    (auth_code_flow, 10),
                    (not has_pkce, 15),
                ]
            )
            findings.append(
                Finding(
                    title="前端 OAuth 授权码流程未发现 PKCE 线索",
                    type="oauth_surface_exposure",
                    severity="medium",
                    description="页面中可见 OAuth 授权码流程入口、回调地址与 client_id，但未发现 PKCE 线索，移动端或 SPA 场景下抗拦截能力偏弱。",
                    url=context.url,
                    location=VulnLocation(
                        url=context.url,
                        parameter="oauth config",
                        parameter_type="html",
                        snippet="response_type=code",
                    ),
                    evidence=Evidence(
                        extra={
                            "auth_urls": auth_urls[:6],
                            "callback_paths": callback_paths[:6],
                            "has_client_id": has_client_id,
                            "has_state": bool(has_state),
                            "flow": "authorization_code",
                            "pkce_detected": False,
                            "evidence_score": evidence_score,
                        },
                        response_raw=body[:4000],
                    ),
                    fix_suggestion="对前端或移动端 OAuth 授权码流程启用 PKCE，并校验 state、限制 redirect URI 与登出回跳地址。",
                    confidence="medium",
                    owasp_category="A07 身份识别与认证失败",
                    cwe_id="CWE-287",
                )
            )

        if state_missing_urls:
            evidence_score = _score_signal_pairs(
                [
                    (True, 30),
                    (len(state_missing_urls) >= 1, 25),
                    (len(auth_urls) >= 1, 15),
                    (has_client_id, 10),
                    (len(callback_paths) >= 1, 10),
                    (implicit_flow or auth_code_flow, 10),
                ]
            )
            findings.append(
                Finding(
                    title="OAuth 授权请求未发现 state 参数",
                    type="oauth_config_risk",
                    severity="medium",
                    description="页面中暴露的 OAuth / SSO 授权请求未发现 state 参数，回跳流程抗 CSRF 与登录串联能力不足。",
                    url=context.url,
                    location=VulnLocation(
                        url=context.url,
                        parameter="state",
                        parameter_type="html",
                        snippet="OAuth authorize URL",
                    ),
                    evidence=Evidence(
                        extra={
                            "auth_urls": state_missing_urls[:6],
                            "callback_paths": callback_paths[:6],
                            "has_client_id": has_client_id,
                            "flow": "implicit" if implicit_flow else "authorization_code",
                            "evidence_score": evidence_score,
                        },
                        response_raw=body[:4000],
                    ),
                    fix_suggestion="为所有 OAuth / OIDC 授权请求加入强随机 state，并在回调端严格校验来源、会话与一次性使用。对 OIDC 同时校验 nonce。",
                    confidence="medium",
                    owasp_category="A07 身份识别与认证失败",
                    cwe_id="CWE-352",
                )
            )

        if nonce_missing_entries:
            nonce_missing_urls = [item[0] for item in nonce_missing_entries]
            nonce_severities = {item[1] for item in nonce_missing_entries}
            nonce_flows = {item[2] for item in nonce_missing_entries}
            evidence_score = _score_signal_pairs(
                [
                    (True, 35),
                    (len(nonce_missing_urls) >= 1, 20),
                    (len(auth_urls) >= 1, 15),
                    (has_client_id, 10),
                    (len(callback_paths) >= 1, 10),
                    (implicit_flow or auth_code_flow, 10),
                ]
            )
            findings.append(
                Finding(
                    title="OIDC 授权请求未发现 nonce 参数",
                    type="oauth_config_risk",
                    severity="high" if "high" in nonce_severities else "medium",
                    description="页面中暴露的 OIDC 授权请求包含 openid scope，但未发现 nonce 参数，可能放大重放和令牌注入风险。",
                    url=context.url,
                    location=VulnLocation(
                        url=context.url,
                        parameter="nonce",
                        parameter_type="html",
                        snippet="OIDC authorize URL",
                    ),
                    evidence=Evidence(
                        extra={
                            "auth_urls": nonce_missing_urls[:6],
                            "callback_paths": callback_paths[:6],
                            "has_client_id": has_client_id,
                            "flows": sorted(nonce_flows),
                            "evidence_score": evidence_score,
                        },
                        response_raw=body[:4000],
                    ),
                    fix_suggestion="为所有 OIDC 授权请求加入强随机 nonce，并在 ID Token 校验阶段严格验证 nonce 与会话绑定关系。",
                    confidence="high",
                    owasp_category="A07 身份识别与认证失败",
                    cwe_id="CWE-287",
                )
            )

        if insecure_redirects or wildcard_redirects:
            evidence_score = _score_signal_pairs(
                [
                    (len(insecure_redirects) >= 1, 35),
                    (len(wildcard_redirects) >= 1, 30),
                    (len(redirect_targets) >= 1, 15),
                    (len(auth_urls) >= 1, 10),
                    (has_client_id, 10),
                ]
            )
            findings.append(
                Finding(
                    title="OAuth 回调地址配置暴露高风险线索",
                    type="oauth_config_risk",
                    severity="high" if insecure_redirects else "medium",
                    description="页面中可见的 OAuth / SSO 授权配置包含非 HTTPS、本地调试或通配回调地址线索，若 IdP 放行，可能扩大令牌回跳与钓鱼利用面。",
                    url=context.url,
                    location=VulnLocation(
                        url=context.url,
                        parameter="redirect_uri",
                        parameter_type="html",
                        snippet="redirect_uri / post_logout_redirect_uri",
                    ),
                    evidence=Evidence(
                        extra={
                            "auth_urls": auth_urls[:6],
                            "redirect_targets": redirect_targets[:8],
                            "insecure_redirects": insecure_redirects[:8],
                            "wildcard_redirects": wildcard_redirects[:8],
                            "evidence_score": evidence_score,
                        },
                        response_raw=body[:4000],
                    ),
                    fix_suggestion="在 IdP 侧仅允许精确匹配的 HTTPS redirect URI，移除 localhost、测试域名和通配配置，并同步限制 post_logout_redirect_uri / RelayState 落点。",
                    confidence="high" if insecure_redirects else "medium",
                    owasp_category="A07 身份识别与认证失败",
                    cwe_id="CWE-601",
                )
            )

        return findings


class CloudStorageExposureDetector(BaseVulnDetector):
    """对象存储公开列目录检测插件。"""

    name = "cloud_storage_exposure"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    def _extract_targets(self, body: str) -> list[tuple[str, str, str]]:
        targets: dict[tuple[str, str], tuple[str, str, str]] = {}

        for match in re.finditer(r"https://([a-z0-9.\-_]+)\.s3\.amazonaws\.com(?:/[^'\"<>\s]*)?", body, re.I):
            bucket = match.group(1)
            targets[("s3", bucket)] = (
                "s3",
                f"https://{bucket}.s3.amazonaws.com/?list-type=2",
                bucket,
            )
        for match in re.finditer(r"https://storage\.googleapis\.com/([a-z0-9.\-_]+)(?:/[^'\"<>\s]*)?", body, re.I):
            bucket = match.group(1)
            targets[("gcs", bucket)] = (
                "gcs",
                f"https://storage.googleapis.com/{bucket}/",
                bucket,
            )
        for match in re.finditer(r"https://([a-z0-9\-]+)\.blob\.core\.windows\.net/([a-z0-9.\-_]+)(?:/[^'\"<>\s]*)?", body, re.I):
            account = match.group(1)
            container = match.group(2)
            label = f"{account}/{container}"
            targets[("azure", label)] = (
                "azure",
                f"https://{account}.blob.core.windows.net/{container}?restype=container&comp=list",
                label,
            )

        return list(targets.values())

    async def detect(self, context: ScanContext) -> list[Finding]:
        body = context.body or ""
        if not body:
            return []

        targets = self._extract_targets(body)
        if not targets:
            return []

        findings: list[Finding] = []
        try:
            async with httpx.AsyncClient(
                follow_redirects=True,
                headers=context.headers or None,
            ) as client:
                for provider, probe_url, label in targets:
                    try:
                        resp = await client.get(probe_url, timeout=8.0)
                    except Exception:
                        continue
                    if resp.status_code != 200:
                        continue
                    content = (resp.text or "")[:4000]
                    lowered = content.lower()
                    listing_markers = {
                        "s3": ["listbucketresult", "<key>", "<name>"],
                        "gcs": ["<listbucketresult", "<contents>", "<key>"],
                        "azure": ["enumerationresults", "<blobs>", "<blob>"],
                    }.get(provider, [])
                    matched = [marker for marker in listing_markers if marker in lowered]
                    if len(matched) < 2:
                        continue
                    evidence_score = _score_signal_pairs(
                        [
                            (resp.status_code == 200, 30),
                            (len(matched) >= 2, 35),
                            (provider == "azure", 10),
                            (provider in {"s3", "gcs"}, 15),
                        ]
                    )
                    findings.append(
                        Finding(
                            title="对象存储公开列目录",
                            type="cloud_storage_exposure",
                            severity="high",
                            description="前端引用的对象存储桶/容器可被匿名列目录，攻击者可能枚举文件、备份、日志或内部资源路径。",
                            url=probe_url,
                            location=VulnLocation(
                                url=probe_url,
                                parameter="bucket/container listing",
                                parameter_type="path",
                                snippet=label,
                            ),
                            evidence=Evidence(
                                extra={
                                    "provider": provider,
                                    "bucket_or_container": label,
                                    "matched_markers": matched,
                                    "evidence_score": evidence_score,
                                },
                                response_raw=content,
                            ),
                            fix_suggestion="关闭对象存储公开列目录，仅开放最小读权限；对公开资源使用专用静态分发策略，并将敏感对象迁移到私有桶或签名访问。",
                            confidence="high",
                            owasp_category="A05 安全配置错误",
                            cwe_id="CWE-200",
                        )
                    )
        except Exception:
            return findings

        return findings


class CloudStorageSecretExposureDetector(BaseVulnDetector):
    """对象存储签名访问链接暴露检测插件。"""

    name = "cloud_storage_secret_exposure"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        body = context.body or ""
        if not body:
            return []

        patterns = [
            (
                "aws_s3",
                r"(https://[a-z0-9.\-_]+\.s3(?:[.-][a-z0-9-]+)?\.amazonaws\.com/[^'\"<>\s]+\?[^'\"<>\s]*X-Amz-Signature=[^'\"<>\s]+)",
                ["x-amz-signature", "x-amz-credential", "x-amz-expires"],
            ),
            (
                "gcs",
                r"(https://storage\.googleapis\.com/[^'\"<>\s]+\?[^'\"<>\s]*X-Goog-Signature=[^'\"<>\s]+)",
                ["x-goog-signature", "x-goog-credential", "x-goog-expires"],
            ),
            (
                "azure_blob",
                r"(https://[a-z0-9\-]+\.blob\.core\.windows\.net/[^'\"<>\s]+\?[^'\"<>\s]*sig=[^'\"<>\s]+)",
                ["sig=", "se=", "sp="],
            ),
        ]

        findings: list[Finding] = []
        lowered = body.lower()
        for provider, pattern, markers in patterns:
            urls = sorted({match.group(1) for match in re.finditer(pattern, body, re.I)})
            if not urls:
                continue
            matched_markers = [marker for marker in markers if marker in lowered]
            evidence_score = _score_signal_pairs(
                [
                    (len(urls) >= 1, 40),
                    (len(matched_markers) >= 2, 25),
                    (len(urls) >= 2, 10),
                    (provider == "azure_blob", 10),
                    (provider in {"aws_s3", "gcs"}, 15),
                ]
            )
            findings.append(
                Finding(
                    title="前端暴露对象存储签名访问链接",
                    type="cloud_storage_secret_exposure",
                    severity="high",
                    description="页面源码中直接出现对象存储签名访问链接或 SAS 参数，可能被他人复用以读取受限资源、枚举文件或绕过预期访问边界。",
                    url=context.url,
                    location=VulnLocation(
                        url=context.url,
                        parameter="signed storage url",
                        parameter_type="html",
                        snippet=provider,
                    ),
                    evidence=Evidence(
                        extra={
                            "provider": provider,
                            "signed_urls": urls[:5],
                            "matched_markers": matched_markers,
                            "evidence_score": evidence_score,
                        },
                        response_raw=body[:4000],
                    ),
                    fix_suggestion="避免在前端源码中硬编码签名对象存储链接；改为后端按需短时签发，并限制权限、路径范围、来源与过期时间。",
                    confidence="high",
                    owasp_category="A05 安全配置错误",
                    cwe_id="CWE-200",
                )
            )

        return findings


class OIDCDiscoveryConfigDetector(BaseVulnDetector):
    """OIDC discovery 配置审计插件。"""

    name = "oidc_discovery_config"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    _discovery_patterns = (
        r"https?://[^'\"<>\s]+/\.well-known/openid-configuration",
        r"['\"]/(?:\.well-known/)?openid-configuration['\"]",
        r"['\"]/(?:oauth2|oauth|oidc)/\.well-known/openid-configuration['\"]",
    )

    def _candidate_urls(self, context: ScanContext) -> list[str]:
        origin = f"{urlparse(context.url).scheme}://{urlparse(context.url).netloc}"
        body = context.body or ""
        urls: list[str] = []
        for pattern in self._discovery_patterns:
            for match in re.finditer(pattern, body, re.I):
                value = match.group(0).strip("'\"")
                if value.startswith("http"):
                    candidate = value
                else:
                    candidate = urljoin(origin, value)
                if candidate not in urls:
                    urls.append(candidate)
        for fallback in (
            f"{origin}/.well-known/openid-configuration",
            f"{origin}/oauth2/.well-known/openid-configuration",
        ):
            if fallback not in urls:
                urls.append(fallback)
        return urls

    async def detect(self, context: ScanContext) -> list[Finding]:
        body = context.body or ""
        urls = self._candidate_urls(context)
        if not urls:
            return []

        findings: list[Finding] = []
        seen_fingerprints: set[tuple[str, str, str]] = set()
        try:
            async with httpx.AsyncClient(
                follow_redirects=True,
                headers=context.headers or None,
            ) as client:
                for discovery_url in urls:
                    try:
                        resp = await client.get(discovery_url, timeout=8.0)
                    except Exception:
                        continue
                    if resp.status_code != 200:
                        continue
                    try:
                        config = resp.json()
                    except Exception:
                        continue
                    if not isinstance(config, dict):
                        continue

                    response_types = {str(item).lower() for item in config.get("response_types_supported", [])}
                    grant_types = {str(item).lower() for item in config.get("grant_types_supported", [])}
                    token_methods = {str(item).lower() for item in config.get("token_endpoint_auth_methods_supported", [])}
                    subject_types = {str(item).lower() for item in config.get("subject_types_supported", [])}
                    scopes = {str(item).lower() for item in config.get("scopes_supported", [])}
                    id_token_algs = {str(item).lower() for item in config.get("id_token_signing_alg_values_supported", [])}
                    userinfo_algs = {str(item).lower() for item in config.get("userinfo_signing_alg_values_supported", [])}
                    request_object_algs = {
                        str(item).lower() for item in config.get("request_object_signing_alg_values_supported", [])
                    }
                    jwks_uri = str(config.get("jwks_uri") or "")
                    issuer = str(config.get("issuer") or "")
                    auth_endpoint = str(config.get("authorization_endpoint") or "")

                    issues: list[str] = []
                    if "token" in response_types or "id_token" in response_types:
                        issues.append("implicit_response")
                    if "implicit" in grant_types:
                        issues.append("implicit_grant")
                    if "none" in token_methods:
                        issues.append("none_client_auth")
                    if jwks_uri.startswith("http://") or "localhost" in jwks_uri or "127.0.0.1" in jwks_uri:
                        issues.append("insecure_jwks_uri")
                    if issuer.startswith("http://") or "localhost" in issuer or "127.0.0.1" in issuer:
                        issues.append("insecure_issuer")
                    if "public" in subject_types:
                        issues.append("public_subject")
                    if "openid" not in scopes and scopes:
                        issues.append("openid_scope_missing")
                    if auth_endpoint.startswith("http://") or "localhost" in auth_endpoint:
                        issues.append("insecure_auth_endpoint")
                    if "none" in id_token_algs:
                        issues.append("unsigned_id_token")
                    if "none" in userinfo_algs:
                        issues.append("unsigned_userinfo")
                    if "none" in request_object_algs:
                        issues.append("unsigned_request_object")

                    if not issues:
                        continue

                    fingerprint = (
                        issuer,
                        jwks_uri,
                        ",".join(sorted(issues)),
                    )
                    if fingerprint in seen_fingerprints:
                        continue
                    seen_fingerprints.add(fingerprint)

                    evidence_score = _score_signal_pairs(
                        [
                            ("implicit_response" in issues, 25),
                            ("implicit_grant" in issues, 25),
                            ("none_client_auth" in issues, 20),
                            ("insecure_jwks_uri" in issues, 20),
                            ("insecure_issuer" in issues, 15),
                            ("insecure_auth_endpoint" in issues, 15),
                            ("openid_scope_missing" in issues, 10),
                            ("public_subject" in issues, 10),
                        ]
                    )
                    severity = "high" if any(item in issues for item in ("implicit_response", "implicit_grant", "none_client_auth", "insecure_jwks_uri", "insecure_issuer")) else "medium"
                    findings.append(
                        Finding(
                            title="OIDC Discovery 配置存在高风险线索",
                            type="oidc_discovery_risk",
                            severity=severity,
                            description="OIDC discovery 文档中暴露了可能影响登录安全的配置线索，例如隐式流、none 客户端认证、非 HTTPS issuer 或 jwks_uri。",
                            url=discovery_url,
                            location=VulnLocation(
                                url=discovery_url,
                                parameter="openid-configuration",
                                parameter_type="path",
                                snippet="OIDC discovery",
                            ),
                            evidence=Evidence(
                                extra={
                                    "issues": issues,
                                    "issuer": issuer,
                                    "jwks_uri": jwks_uri,
                                    "authorization_endpoint": auth_endpoint,
                                    "response_types_supported": sorted(response_types),
                            "grant_types_supported": sorted(grant_types),
                            "token_endpoint_auth_methods_supported": sorted(token_methods),
                            "id_token_signing_alg_values_supported": sorted(id_token_algs),
                            "userinfo_signing_alg_values_supported": sorted(userinfo_algs),
                            "request_object_signing_alg_values_supported": sorted(request_object_algs),
                            "evidence_score": evidence_score,
                        },
                                response_raw=resp.text[:4000],
                            ),
                            fix_suggestion="在 IdP discovery 配置中关闭隐式流与 none 客户端认证，确保 issuer、jwks_uri 与授权端点均为 HTTPS，并限制到正式环境域名。",
                            confidence="high" if severity == "high" else "medium",
                            owasp_category="A07 身份识别与认证失败",
                            cwe_id="CWE-20",
                        )
                    )
        except Exception:
            return findings

        return findings


class SensitiveEndpointDetector(BaseVulnDetector):
    """敏感管理/调试端点暴露检测插件。"""

    name = "sensitive_endpoint"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        """探测常见管理、指标、调试与文档端点是否公开。"""
        origin = f"{urlparse(context.url).scheme}://{urlparse(context.url).netloc}"
        candidates = [
            ("/metrics", "暴露 Prometheus 指标端点", "high", ["# HELP", "# TYPE", "process_cpu_seconds_total"], 2, "CWE-200"),
            ("/actuator/prometheus", "暴露 Spring Boot Prometheus 指标端点", "high", ["# HELP", "# TYPE", "jvm_"], 2, "CWE-200"),
            ("/actuator/health", "暴露 Spring Boot Actuator 健康端点", "medium", ['"status":"UP"', '"components"', '"details"'], 1, "CWE-200"),
            ("/actuator/env", "暴露 Spring Boot Actuator 环境端点", "high", ['"propertySources"', '"activeProfiles"', '"environment"'], 1, "CWE-200"),
            ("/openapi.json", "暴露 OpenAPI 描述文件", "medium", ['"openapi"', '"paths"', '"components"'], 2, "CWE-200"),
            ("/v3/api-docs", "暴露 OpenAPI 描述文件", "medium", ['"openapi"', '"paths"', '"components"'], 2, "CWE-200"),
            ("/swagger-ui", "暴露 Swagger UI 文档", "medium", ["swagger-ui", "openapi"], 1, "CWE-200"),
            ("/swagger-ui.html", "暴露 Swagger UI 文档", "medium", ["swagger-ui", "openapi"], 1, "CWE-200"),
            ("/redoc", "暴露 API 文档页面", "low", ["redoc", "openapi"], 1, "CWE-200"),
            ("/graphiql", "暴露 GraphiQL 调试界面", "medium", ["graphiql", "graphql"], 1, "CWE-200"),
            ("/graphql/playground", "暴露 GraphQL Playground 调试界面", "medium", ["graphql playground", "subscriptions endpoint"], 1, "CWE-200"),
            ("/phpinfo.php", "暴露 PHP 信息页面", "high", ["php version", "phpinfo()"], 1, "CWE-200"),
            ("/server-status", "暴露服务器状态页面", "medium", ["apache server status", "server uptime"], 1, "CWE-200"),
            ("/debug", "暴露调试端点", "high", ["traceback", "stack trace", "exception in thread", "debug toolbar"], 1, "CWE-489"),
            ("/h2-console", "暴露 H2 控制台", "high", ["h2 console", "welcome to h2"], 1, "CWE-200"),
        ]

        findings: list[Finding] = []
        try:
            async with httpx.AsyncClient(
                follow_redirects=True,
                headers=context.headers or None,
            ) as client:
                for rel_path, title, severity, markers, min_markers, cwe in candidates:
                    endpoint_url = urljoin(origin, rel_path)
                    try:
                        resp = await client.get(endpoint_url, timeout=8.0)
                    except Exception:
                        continue

                    if resp.status_code != 200:
                        continue
                    body = (resp.text or "").lower()
                    matched_markers = [
                        marker for marker in markers if marker.lower() in body
                    ]
                    if len(matched_markers) < min_markers:
                        continue

                    findings.append(
                        Finding(
                            title=title,
                            type="exposed_endpoint",
                            severity=severity,
                            description=f"端点 {rel_path} 可直接访问并返回可识别的管理/调试内容，攻击面已暴露到公网边界。",
                            url=endpoint_url,
                            location=VulnLocation(
                                url=endpoint_url,
                                parameter="",
                                parameter_type="path",
                                snippet=rel_path,
                            ),
                            evidence=Evidence(
                                extra={
                                    "endpoint": rel_path,
                                    "matched_markers": matched_markers,
                                    "status_code": resp.status_code,
                                    "content_type": resp.headers.get("content-type", ""),
                                },
                                response_raw=resp.text[:4000],
                            ),
                            fix_suggestion="将这些端点限制到内网、管理员白名单或鉴权后访问，生产环境避免公开调试和运维接口。",
                            confidence="high",
                            owasp_category="A05 安全配置错误",
                            cwe_id=cwe,
                        )
                    )
        except Exception:
            return findings

        return findings


class BackupExposureDetector(BaseVulnDetector):
    """备份与导出文件暴露检测插件。"""

    name = "backup_exposure"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        """探测常见备份、导出与旧版本文件是否公开。"""
        origin = f"{urlparse(context.url).scheme}://{urlparse(context.url).netloc}"
        candidates = [
            ("/backup.sql", "数据库备份文件暴露", "high", ["create table", "insert into", "drop table", "mysql dump", "postgresql database dump"], "CWE-200"),
            ("/dump.sql", "数据库导出文件暴露", "high", ["create table", "insert into", "drop table", "mysqldump", "dump completed"], "CWE-200"),
            ("/db.sql", "数据库文件暴露", "high", ["create table", "insert into", "drop table", "pragma", "sqlite"], "CWE-200"),
            ("/backup.bak", "备份文件暴露", "medium", ["password", "secret", "token", "api_key", "database"], "CWE-200"),
            ("/config.bak", "配置备份文件暴露", "high", ["password", "secret", "token", "api_key", "database_url"], "CWE-200"),
            ("/config.old", "旧配置文件暴露", "high", ["password", "secret", "token", "api_key", "database_url"], "CWE-200"),
            ("/settings.old", "旧配置文件暴露", "high", ["password", "secret", "token", "api_key", "database_url"], "CWE-200"),
            ("/.env.bak", "环境变量备份暴露", "high", ["password", "secret", "token", "api_key", "jwt_secret"], "CWE-200"),
            ("/application.yml.bak", "应用配置备份暴露", "high", ["password:", "secret:", "token:", "api_key:", "spring:"], "CWE-200"),
            ("/web.config.bak", "Web 配置备份暴露", "high", ["connectionstrings", "appsettings", "password", "secret"], "CWE-200"),
        ]

        findings: list[Finding] = []
        try:
            async with httpx.AsyncClient(
                follow_redirects=True,
                headers=context.headers or None,
            ) as client:
                for rel_path, title, severity, markers, cwe in candidates:
                    target_url = urljoin(origin, rel_path)
                    try:
                        resp = await client.get(target_url, timeout=8.0)
                    except Exception:
                        continue

                    body = (resp.text or "").lower()
                    if resp.status_code != 200 or not body:
                        continue
                    if len(body) < 20 and not any(marker in body for marker in markers):
                        continue

                    matched = [marker for marker in markers if marker.lower() in body]
                    if not matched:
                        continue

                    findings.append(
                        Finding(
                            title=title,
                            type="backup_exposure",
                            severity=severity,
                            description=f"公开可访问的 {rel_path} 暴露了备份或导出内容，攻击者可能直接获得配置、凭据或数据库结构。",
                            url=target_url,
                            location=VulnLocation(
                                url=target_url,
                                parameter="",
                                parameter_type="path",
                                snippet=rel_path,
                            ),
                            evidence=Evidence(
                                extra={
                                    "endpoint": rel_path,
                                    "matched_markers": matched,
                                    "status_code": resp.status_code,
                                    "content_type": resp.headers.get("content-type", ""),
                                },
                                response_raw=resp.text[:4000],
                            ),
                            fix_suggestion="将备份、导出和旧版本文件移出 Web 根目录，并在服务器层显式禁止访问这些后缀。",
                            confidence="high",
                            owasp_category="A05 安全配置错误",
                            cwe_id=cwe,
                        )
                    )
        except Exception:
            return findings

        return findings


class DiscoverySurfaceDetector(BaseVulnDetector):
    """公开发现面泄露检测插件。"""

    name = "discovery_surface"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        """检测 robots.txt / sitemap.xml 是否暴露敏感入口。"""
        origin = f"{urlparse(context.url).scheme}://{urlparse(context.url).netloc}"
        targets = [
            ("/robots.txt", "robots.txt 暴露敏感路径", "medium", "robots"),
            ("/sitemap.xml", "sitemap.xml 暴露敏感页面", "medium", "sitemap"),
            ("/sitemap_index.xml", "sitemap.xml 暴露敏感页面", "low", "sitemap"),
        ]

        findings: list[Finding] = []
        try:
            async with httpx.AsyncClient(
                follow_redirects=True,
                headers=context.headers or None,
            ) as client:
                for rel_path, title, base_severity, source_name in targets:
                    target_url = urljoin(origin, rel_path)
                    try:
                        resp = await client.get(target_url, timeout=8.0)
                    except Exception:
                        continue

                    if resp.status_code != 200:
                        continue

                    text = resp.text or ""
                    if not text.strip():
                        continue

                    hits = _extract_sensitive_discovery_hits(text)
                    if not hits:
                        continue

                    severity = base_severity
                    if len(hits) >= 3 or "backup" in hits or "config" in hits:
                        severity = "high"

                    findings.append(
                        Finding(
                            title=title,
                            type="discovery_exposure",
                            severity=severity,
                            description=f"公开的 {rel_path} 暴露了敏感发现信息，攻击者可从中直接枚举管理入口、调试面或备份路径。",
                            url=target_url,
                            location=VulnLocation(
                                url=target_url,
                                parameter="",
                                parameter_type="path",
                                snippet=rel_path,
                            ),
                            evidence=Evidence(
                                extra={
                                    "source": source_name,
                                    "matched_signals": hits,
                                    "status_code": resp.status_code,
                                },
                                response_raw=text[:4000],
                            ),
                            fix_suggestion="将 robots.txt / sitemap.xml 中的敏感路径移除，避免在公开发现文件里列出管理、备份、调试与内部入口。",
                            confidence="high",
                            owasp_category="A05 安全配置错误",
                            cwe_id="CWE-200",
                        )
                    )
        except Exception:
            return findings

        return findings


class WellKnownExposureDetector(BaseVulnDetector):
    """well-known 公开元数据泄露检测插件。"""

    name = "well_known_exposure"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        """检测 well-known 文件是否泄露内部地址、管理入口或调试元数据。"""
        origin = f"{urlparse(context.url).scheme}://{urlparse(context.url).netloc}"
        targets = [
            "/.well-known/openid-configuration",
            "/.well-known/security.txt",
            "/.well-known/assetlinks.json",
            "/.well-known/apple-app-site-association",
            "/.well-known/mta-sts.txt",
        ]

        findings: list[Finding] = []
        try:
            async with httpx.AsyncClient(
                follow_redirects=True,
                headers=context.headers or None,
            ) as client:
                for rel_path in targets:
                    target_url = urljoin(origin, rel_path)
                    try:
                        resp = await client.get(target_url, timeout=8.0)
                    except Exception:
                        continue

                    if resp.status_code != 200:
                        continue

                    text = resp.text or ""
                    if not text.strip():
                        continue

                    hits = _extract_well_known_hits(text)
                    if not hits:
                        continue

                    severity = "low"
                    if "internal_host" in hits or "admin_path" in hits or "backup_path" in hits:
                        severity = "high"
                    elif "auth_endpoint" in hits or "internal_api" in hits:
                        severity = "medium"
                    elif "config_path" in hits:
                        severity = "medium"

                    findings.append(
                        Finding(
                            title="well-known 公开元数据泄露",
                            type="well_known_exposure",
                            severity=severity,
                            description=f"{rel_path} 公开暴露了服务发现或站点关联元数据，且其中包含敏感入口或内部地址线索。",
                            url=target_url,
                            location=VulnLocation(
                                url=target_url,
                                parameter="",
                                parameter_type="path",
                                snippet=rel_path,
                            ),
                            evidence=Evidence(
                                extra={
                                    "path": rel_path,
                                    "matched_signals": hits,
                                    "status_code": resp.status_code,
                                },
                                response_raw=text[:4000],
                            ),
                            fix_suggestion="检查 well-known 配置内容，移除内部地址、管理入口和调试接口，仅保留业务必须公开的元数据。",
                            confidence="high",
                            owasp_category="A05 安全配置错误",
                            cwe_id="CWE-200",
                        )
                    )
        except Exception:
            return findings

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
    DetectorRegistry.register(SRIIntegrityDetector())
    DetectorRegistry.register(FrontendSupplyChainDetector())
    DetectorRegistry.register(LoginSurfaceDetector())
    DetectorRegistry.register(ProtectedRouteExposureDetector())
    DetectorRegistry.register(ServerExposureDetector())
    DetectorRegistry.register(PassiveExposureDetector())
    DetectorRegistry.register(ApiSurfaceExposureDetector())
    DetectorRegistry.register(OAuthSurfaceDetector())
    DetectorRegistry.register(OIDCDiscoveryConfigDetector())
    DetectorRegistry.register(CloudStorageExposureDetector())
    DetectorRegistry.register(CloudStorageSecretExposureDetector())
    DetectorRegistry.register(SensitiveEndpointDetector())
    DetectorRegistry.register(BackupExposureDetector())
    DetectorRegistry.register(DiscoverySurfaceDetector())
    DetectorRegistry.register(WellKnownExposureDetector())
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
