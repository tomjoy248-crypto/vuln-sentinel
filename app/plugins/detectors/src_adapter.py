"""SRC 扫描器插件适配器。

将 src_scanner.py 中已有的检测函数包装为 BaseVulnDetector 插件，
使旧检测能力接入新的插件化调度体系，同时保留原有逻辑与测试兼容性。
"""

from __future__ import annotations

from urllib.parse import parse_qs, urlencode, urlparse

import httpx

from app.plugins import (
    BaseVulnDetector,
    Evidence,
    Finding,
    FixSuggestion,
    ScanContext,
    VulnLocation,
)
from app.plugins._compat import old_finding_to_finding

_SSTI_PAYLOADS: list[tuple[str, str]] = [
    ("{{'vuln' ~ '-' ~ 'sentinel' ~ '-' ~ 'probe'}}", "vuln-sentinel-probe"),
    ("{{'vuln' + '-' + 'sentinel' + '-' + 'probe'}}", "vuln-sentinel-probe"),
    ("<%= 'vuln' + '-' + 'sentinel' + '-' + 'probe' %>", "vuln-sentinel-probe"),
    ("${7*7}", "49"),
]


def _extract_params(url: str, body: str = "") -> dict[str, list[str]]:
    params: dict[str, list[str]] = {}
    parsed = urlparse(url)
    for key, values in parse_qs(parsed.query, keep_blank_values=True).items():
        params.setdefault(key, []).extend(values)
    if body and "=" in body and not body.lstrip().startswith("{"):
        for key, values in parse_qs(body, keep_blank_values=True).items():
            params.setdefault(key, []).extend(values)
    return params


def _build_test_url(
    base_url: str,
    params: dict[str, list[str]],
    target_param: str,
    payload: str,
) -> str:
    merged = {key: (values[0] if values else "") for key, values in params.items()}
    merged[target_param] = payload
    return f"{base_url}?{urlencode(merged, safe='')}" if merged else base_url


class SSTIDetector(BaseVulnDetector):
    """模板注入检测插件。"""

    name = "ssti"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        params = _extract_params(context.url, context.body or "")
        if not params:
            return []

        findings: list[Finding] = []
        try:
            async with httpx.AsyncClient(
                timeout=8.0,
                follow_redirects=True,
                headers=context.headers or None,
            ) as client:
                baseline_body = ""
                try:
                    baseline_resp = await client.get(context.url)
                    baseline_body = baseline_resp.text.lower()
                except Exception:
                    pass

                for param in list(params)[:3]:
                    for payload, marker in _SSTI_PAYLOADS:
                        test_url = _build_test_url(context.url, params, param, payload)
                        try:
                            resp = await client.get(test_url)
                        except Exception:
                            continue
                        body = resp.text.lower()
                        if (
                            marker.lower() in body
                            and payload.lower() not in body
                            and body != baseline_body
                        ):
                            findings.append(
                                Finding(
                                    title="模板注入漏洞（SSTI）",
                                    type="ssti",
                                    severity="high",
                                    description=f"参数 '{param}' 的模板表达式被渲染，疑似存在模板注入。",
                                    url=test_url,
                                    location=VulnLocation(
                                        url=test_url,
                                        parameter=param,
                                        parameter_type="query",
                                        snippet="模板表达式渲染结果",
                                    ),
                                    evidence=Evidence(
                                        extra={
                                            "payload": payload,
                                            "rendered_marker": marker,
                                            "baseline_present": bool(baseline_body),
                                        },
                                        payload=payload,
                                        response_raw=body[:4000],
                                    ),
                                    fix_suggestion="不要将用户输入拼接进模板表达式；所有显示内容都应作为纯文本输出并启用默认转义。",
                                    confidence="high",
                                    owasp_category="A03 注入攻击",
                                    cwe_id="CWE-94",
                                    fix=FixSuggestion(
                                        generic="禁止将用户输入拼接进模板表达式，并对输出做默认转义。",
                                    ),
                                )
                            )
        except Exception:
            return findings
        return findings


class SQLiDetector(BaseVulnDetector):
    """SQL 注入检测插件。"""

    name = "sqli"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        from src_scanner import detect_sqli_src

        raw = await detect_sqli_src(context.url)
        return [old_finding_to_finding(r) for r in raw]


class ReflectedXSSDetector(BaseVulnDetector):
    """反射型 XSS 检测插件。"""

    name = "reflected_xss"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        from src_scanner import detect_xss_src

        raw = await detect_xss_src(context.url)
        return [old_finding_to_finding(r) for r in raw]


class InfoLeakDetector(BaseVulnDetector):
    """敏感信息泄露检测插件。"""

    name = "info_leak"
    version = "1.0"
    supported_depths = ["quick", "standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        from src_scanner import detect_info_leak_src

        raw = await detect_info_leak_src(
            context.url, context.headers, context.body or None
        )
        return [old_finding_to_finding(r) for r in raw]


class CSRFDetector(BaseVulnDetector):
    """CSRF 检测插件。"""

    name = "csrf"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        from main import detect_csrf_forms

        raw = await detect_csrf_forms(context.url)
        return [old_finding_to_finding(r) for r in raw]


class SensitivePathDetectorPlugin(BaseVulnDetector):
    """敏感路径检测插件。"""

    name = "sensitive_path"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        sensitive_paths = [
            "/.env",
            "/.env.local",
            "/.git/config",
            "/.svn/entries",
            "/config.php",
            "/wp-config.php",
            "/application.yml",
            "/application.yaml",
            "/docker-compose.yml",
            "/web.config",
            "/settings.py",
            "/.npmrc",
        ]
        config_suffixes = (".env", ".env.local", ".git/config", ".svn/entries", ".php", ".yml", ".yaml", ".py", ".config", ".ini", ".json", ".toml")
        markers = ("secret", "password", "passwd", "token", "jwt", "api_key", "apikey", "credentials", "database", "mysql", "postgres", "redis")
        findings: list[Finding] = []
        origin = f"{urlparse(context.url).scheme}://{urlparse(context.url).netloc}"
        try:
            async with httpx.AsyncClient(follow_redirects=True, headers=context.headers or None) as client:
                for rel_path in sensitive_paths:
                    try:
                        resp = await client.get(urljoin(origin, rel_path), timeout=8.0)
                    except Exception:
                        continue
                    body = resp.text.lower()
                    if resp.status_code != 200 or not body:
                        continue
                    if not any(marker in body for marker in markers):
                        continue
                    finding_type = "sensitive_config_exposure" if rel_path.lower().endswith(config_suffixes) else "sensitive_path"
                    title = "敏感配置暴露" if finding_type == "sensitive_config_exposure" else "敏感路径暴露"
                    severity = "high" if finding_type == "sensitive_config_exposure" else "medium"
                    findings.append(
                        Finding(
                            title=title,
                            type=finding_type,
                            severity=severity,
                            description=f"可直接访问敏感路径 {rel_path}，可能泄露配置、密钥或源码信息。",
                            url=urljoin(origin, rel_path),
                            location=VulnLocation(
                                url=urljoin(origin, rel_path),
                                parameter=rel_path,
                                parameter_type="path",
                                snippet=rel_path,
                            ),
                            evidence=Evidence(extra={"path": rel_path, "status_code": resp.status_code}, response_raw=body[:4000]),
                            fix_suggestion="限制这些文件的 Web 访问权限，并确保仓库中不包含明文密钥或配置。",
                            confidence="high",
                            owasp_category="A01 访问控制失效",
                            cwe_id="CWE-200",
                            fix=FixSuggestion(generic="不要让配置文件、密钥文件和源码备份暴露在 Web 根目录。"),
                        )
                    )
        except Exception:
            return findings
        return findings


class OutdatedComponentDetector(BaseVulnDetector):
    """过时组件检测插件。"""

    name = "outdated_component"
    version = "1.0"
    supported_depths = ["quick", "standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        from src_scanner import detect_outdated_components_src

        raw = await detect_outdated_components_src(
            context.url, context.headers, context.body or None
        )
        return [old_finding_to_finding(r) for r in raw]


class BrokenAccessControlDetector(BaseVulnDetector):
    """越权访问检测插件。"""

    name = "broken_access_control"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        from src_scanner import detect_broken_access_control_src

        raw = await detect_broken_access_control_src(context.url)
        return [old_finding_to_finding(r) for r in raw]


class SSRFDetector(BaseVulnDetector):
    """SSRF 检测插件。"""

    name = "ssrf"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        from src_scanner import detect_ssrf_src

        raw = await detect_ssrf_src(context.url)
        return [old_finding_to_finding(r) for r in raw]


class IDORDetector(BaseVulnDetector):
    """IDOR 检测插件。"""

    name = "idor"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        from main import detect_idor_risk

        params = list(parse_qs(urlparse(context.url).query, keep_blank_values=True).keys())
        raw = await detect_idor_risk(context.url, params)
        return [old_finding_to_finding(r) for r in raw]


class FileUploadDetector(BaseVulnDetector):
    """文件上传检测插件。"""

    name = "file_upload"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        upload_paths = ("/upload", "/file", "/attach", "/media", "/image", "/avatar")
        upload_indicators = ("type=\"file\"", "enctype=\"multipart/form-data\"", "fileupload", "upload")
        path_lower = urlparse(context.url).path.lower()
        findings: list[Finding] = []
        try:
            async with httpx.AsyncClient(follow_redirects=True, headers=context.headers or None) as client:
                try:
                    resp = await client.get(context.url, timeout=8.0)
                except Exception:
                    return findings
                body = resp.text.lower()
                evidence_bits = []
                if any(token in path_lower for token in upload_paths):
                    evidence_bits.append("url_path_looks_like_upload_endpoint")
                if any(ind in body for ind in upload_indicators):
                    evidence_bits.append("upload_form_detected")
                if not evidence_bits:
                    return findings
                try:
                    post_resp = await client.post(
                        context.url,
                        files={"file": ("test.txt", b"test content", "text/plain")},
                        follow_redirects=False,
                        timeout=8.0,
                    )
                    if post_resp.status_code in (200, 201, 202):
                        evidence_bits.append("upload_accepted")
                except Exception:
                    pass
                findings.append(
                    Finding(
                        title="文件上传风险",
                        type="file_upload",
                        severity="medium" if "upload_accepted" not in evidence_bits else "high",
                        description="页面或路径显示存在文件上传入口，需检查文件类型、大小、存储位置和执行权限。",
                        url=context.url,
                        location=VulnLocation(url=context.url, parameter="file", parameter_type="body", snippet="上传表单或上传端点"),
                        evidence=Evidence(extra={"signals": evidence_bits, "status_code": resp.status_code}, response_raw=resp.text[:4000]),
                        fix_suggestion="限制可上传文件类型、重命名文件、隔离存储目录并禁止可执行文件访问。",
                        confidence="medium" if "upload_accepted" not in evidence_bits else "high",
                        owasp_category="A01 访问控制失效",
                        cwe_id="CWE-434",
                        fix=FixSuggestion(generic="对上传文件做类型白名单、重命名与隔离存储。"),
                    )
                )
        except Exception:
            return findings
        return findings


class LogicBypassDetector(BaseVulnDetector):
    """逻辑绕过检测插件。"""

    name = "logic_bypass"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        path_lower = urlparse(context.url).path.lower()
        body_lower = (context.body or "").lower()
        signals = ["admin", "role", "vip", "coupon", "discount", "unlock", "bypass", "limit", "permission", "privilege"]
        matched = [token for token in signals if token in path_lower or token in body_lower]
        if not matched:
            return []
        severity = "medium" if len(matched) < 2 else "high"
        return [
            Finding(
                title="逻辑绕过风险",
                type="logic_bypass",
                severity=severity,
                description="页面或路径暴露出角色切换、权限控制、优惠码或解锁类逻辑，建议补齐服务端校验。",
                url=context.url,
                location=VulnLocation(url=context.url, parameter="", parameter_type="path", snippet=path_lower or "page"),
                evidence=Evidence(extra={"signals": matched}),
                fix_suggestion="所有关键状态变更都必须在服务端重新校验权限与业务约束。",
                confidence="medium",
                owasp_category="A04 不安全设计",
                cwe_id="CWE-693",
                fix=FixSuggestion(generic="把关键业务校验放在服务端，避免仅靠前端控制。"),
            )
        ]


class OpenRedirectDetector(BaseVulnDetector):
    """开放重定向检测插件。"""

    name = "open_redirect"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        from src_scanner import detect_open_redirect_src

        raw = await detect_open_redirect_src(context.url)
        return [old_finding_to_finding(r) for r in raw]


class XXEDetector(BaseVulnDetector):
    """XXE 检测插件。"""

    name = "xxe"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        from src_scanner import detect_xxe_src

        raw = await detect_xxe_src(context.url, context.headers, context.body or "")
        return [old_finding_to_finding(r) for r in raw]


class CommandInjectionDetector(BaseVulnDetector):
    """命令注入检测插件。"""

    name = "cmdi"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        from src_scanner import detect_command_injection_src

        raw = await detect_command_injection_src(context.url)
        return [old_finding_to_finding(r) for r in raw]


class PathTraversalDetector(BaseVulnDetector):
    """路径遍历检测插件。"""

    name = "traversal"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        from src_scanner import detect_path_traversal_src

        raw = await detect_path_traversal_src(context.url)
        return [old_finding_to_finding(r) for r in raw]


class DeserializationDetector(BaseVulnDetector):
    """不安全反序列化检测插件。"""

    name = "deserialization"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        from main import detect_insecure_deserialization

        raw = await detect_insecure_deserialization(context.headers, context.url)
        return [old_finding_to_finding(r) for r in raw]
