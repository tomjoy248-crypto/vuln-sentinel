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
        from src_scanner import detect_csrf_src

        raw = await detect_csrf_src(context.url, context.headers, context.body or None)
        return [old_finding_to_finding(r) for r in raw]


class SensitivePathDetectorPlugin(BaseVulnDetector):
    """敏感路径检测插件。"""

    name = "sensitive_path"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        from src_scanner import detect_sensitive_paths_src

        raw = await detect_sensitive_paths_src(context.url)
        return [old_finding_to_finding(r) for r in raw]


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
        from src_scanner import detect_idor_src

        raw = await detect_idor_src(context.url)
        return [old_finding_to_finding(r) for r in raw]


class FileUploadDetector(BaseVulnDetector):
    """文件上传检测插件。"""

    name = "file_upload"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        from src_scanner import detect_file_upload_src

        raw = await detect_file_upload_src(context.url, context.body or None)
        return [old_finding_to_finding(r) for r in raw]


class LogicBypassDetector(BaseVulnDetector):
    """逻辑绕过检测插件。"""

    name = "logic_bypass"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        from src_scanner import detect_logic_bypass_src

        raw = await detect_logic_bypass_src(
            context.url, context.headers, context.body or None
        )
        return [old_finding_to_finding(r) for r in raw]


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
        from src_scanner import detect_deserialization_src

        raw = await detect_deserialization_src(
            context.url, context.headers, context.body or ""
        )
        return [old_finding_to_finding(r) for r in raw]
