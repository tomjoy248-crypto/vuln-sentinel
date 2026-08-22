"""业务型漏洞检测插件。

这部分覆盖认证、API 鉴权、敏感配置暴露、点击劫持等更偏产品化的扫描类型。
"""

from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse

import httpx

from app.plugins import BaseVulnDetector, Evidence, Finding, FixSuggestion, ScanContext, VulnLocation
from app.plugins._compat import old_finding_to_finding


async def _get_text(client: httpx.AsyncClient, url: str) -> tuple[int, str, dict[str, str]]:
    resp = await client.get(url, timeout=8.0, follow_redirects=True)
    return resp.status_code, resp.text, {k.lower(): v for k, v in resp.headers.items()}


class AuthWeaknessDetector(BaseVulnDetector):
    """登录页认证防护不足检测。"""

    name = "auth_weakness"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        from main import detect_auth_weaknesses

        raw = await detect_auth_weaknesses(context.url)
        return [old_finding_to_finding(item) for item in raw]


class BruteforceProtectionDetector(BaseVulnDetector):
    """登录防爆破不足检测。"""

    name = "bruteforce_protection"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        from main import detect_auth_weaknesses

        raw = await detect_auth_weaknesses(context.url)
        return [
            old_finding_to_finding(item)
            for item in raw
            if item.get("type") == "bruteforce_protection"
        ]


class APIAuthMissingDetector(BaseVulnDetector):
    """API 接口鉴权缺失检测。"""

    name = "api_auth_missing"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        from main import detect_api_auth_missing

        raw = await detect_api_auth_missing(context.url)
        return [old_finding_to_finding(item) for item in raw]


class ClickjackingDetector(BaseVulnDetector):
    """点击劫持风险检测。"""

    name = "clickjacking"
    version = "1.0"
    supported_depths = ["quick", "standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        from main import _probe_login_page_security

        probe = await _probe_login_page_security(context.url)
        if not probe.get("login_page_found"):
            return []
        issues = set(probe.get("issues") or [])
        if "login_page_no_xfo" not in issues:
            return []
        login_path = probe.get("login_path") or "/login"
        return [
            Finding(
                title="登录页存在点击劫持风险",
                type="clickjacking",
                severity="medium",
                description="登录页缺少 X-Frame-Options，可能被嵌入到第三方 iframe 中诱导点击。",
                url=urljoin(_origin(context.url), login_path),
                location=VulnLocation(
                    url=urljoin(_origin(context.url), login_path),
                    parameter="",
                    parameter_type="header",
                    snippet="登录页响应头",
                ),
                evidence=Evidence(extra={
                    "login_path": login_path,
                    "issues": sorted(issues),
                }),
                fix_suggestion="为登录页配置 X-Frame-Options: DENY 或 CSP frame-ancestors 'none'。",
                confidence="high",
                owasp_category="A05 安全配置错误",
                cwe_id="CWE-1021",
                fix=FixSuggestion(generic="为登录页添加 X-Frame-Options 或 CSP frame-ancestors。"),
            )
        ]


class SensitiveConfigExposureDetector(BaseVulnDetector):
    """敏感配置暴露检测。"""

    name = "sensitive_config_exposure"
    version = "1.0"
    supported_depths = ["quick", "standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        origin = _origin(context.url)
        probes = [
            '/.env',
            '/.env.local',
            '/.git/config',
            '/config.php',
            '/wp-config.php',
            '/application.yml',
            '/application.yaml',
            '/docker-compose.yml',
            '/web.config',
            '/settings.py',
        ]
        markers = re.compile(r"(secret|password|passwd|jwt|api[_-]?key|token|credentials|database|db_|mysql|postgres|redis)", re.I)
        findings: list[Finding] = []
        try:
            async with httpx.AsyncClient(follow_redirects=True, headers=context.headers or None) as client:
                for rel_path in probes:
                    try:
                        status, body, headers = await _get_text(client, urljoin(origin, rel_path))
                    except Exception:
                        continue
                    if status != 200:
                        continue
                    if not body or len(body) < 8:
                        continue
                    if not markers.search(body):
                        continue
                    findings.append(
                        Finding(
                            title="敏感配置暴露",
                            type="sensitive_config_exposure",
                            severity="high",
                            description=f"可直接访问敏感配置文件 {rel_path}，可能泄露密钥、数据库或部署信息。",
                            url=urljoin(origin, rel_path),
                            location=VulnLocation(
                                url=urljoin(origin, rel_path),
                                parameter=rel_path,
                                parameter_type="path",
                                snippet=rel_path,
                            ),
                            evidence=Evidence(extra={
                                "path": rel_path,
                                "status_code": status,
                                "present_headers": headers,
                            }, response_raw=body[:4000]),
                            fix_suggestion="限制这些配置文件的访问权限，移出 Web 根目录，并确保仓库中不包含明文密钥。",
                            confidence="high",
                            owasp_category="A01 访问控制失效",
                            cwe_id="CWE-200",
                            fix=FixSuggestion(generic="禁止 Web 直接暴露配置文件和密钥文件。"),
                        )
                    )
        except Exception:
            return findings
        return findings


class FileUploadDetector(BaseVulnDetector):
    """文件上传风险检测。"""

    name = "file_upload"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        url = context.url
        path_lower = urlparse(url).path.lower()
        upload_paths = ["/upload", "/file", "/attach", "/media", "/image", "/avatar"]
        indicators = ["type=\"file\"", "enctype=\"multipart/form-data\"", "fileupload", "upload"]
        findings: list[Finding] = []
        try:
            async with httpx.AsyncClient(follow_redirects=True, headers=context.headers or None) as client:
                status, body, _ = await _get_text(client, url)
                body_lower = body.lower()
                score = 0
                evidence_bits: list[str] = []
                if any(token in path_lower for token in upload_paths):
                    score += 30
                    evidence_bits.append("url_path_looks_like_upload_endpoint")
                if any(ind in body_lower for ind in indicators):
                    score += 45
                    evidence_bits.append("upload_form_detected")
                if any(token in body_lower for token in ("multipart/form-data", "accept=\"image/", "accept=\"video/", "accept=\"audio/")):
                    score += 10
                    evidence_bits.append("upload_restriction_hint")
                if evidence_bits:
                    # 轻量复测：如果当前 URL 支持 multipart POST，进一步提高置信度
                    try:
                        resp = await client.post(
                            url,
                            files={"file": ("test.txt", b"test content", "text/plain")},
                            follow_redirects=False,
                            timeout=8.0,
                        )
                        if resp.status_code in (200, 201, 202):
                            score += 25
                            evidence_bits.append("upload_accepted")
                    except Exception:
                        pass
                    findings.append(
                        Finding(
                            title="文件上传风险",
                            type="file_upload",
                            severity="medium" if score < 60 else "high",
                            description="页面或路径显示存在文件上传入口，需检查文件类型、大小、存储位置和执行权限。",
                            url=url,
                            location=VulnLocation(url=url, parameter="file", parameter_type="body", snippet="上传表单或上传端点"),
                            evidence=Evidence(extra={
                                "path": path_lower,
                                "signals": evidence_bits,
                                "status_code": status,
                            }, response_raw=body[:4000]),
                            fix_suggestion="限制可上传文件类型、重命名文件、隔离存储目录并禁止可执行文件访问。",
                            confidence="medium" if score < 60 else "high",
                            owasp_category="A01 访问控制失效",
                            cwe_id="CWE-434",
                            fix=FixSuggestion(generic="对上传文件做类型白名单、重命名与隔离存储。"),
                        )
                    )
        except Exception:
            return findings
        return findings


class LogicBypassDetector(BaseVulnDetector):
    """逻辑绕过风险检测。"""

    name = "logic_bypass"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> list[Finding]:
        url = context.url
        path_lower = urlparse(url).path.lower()
        body_lower = (context.body or "").lower()
        signals = [
            "admin", "role", "vip", "coupon", "discount", "unlock", "bypass", "limit", "permission", "privilege",
        ]
        evidence_bits = [token for token in signals if token in path_lower or token in body_lower]
        if not evidence_bits:
            return []
        severity = "medium" if len(evidence_bits) < 2 else "high"
        return [
            Finding(
                title="逻辑绕过风险",
                type="logic_bypass",
                severity=severity,
                description="页面或路径暴露出角色切换、权限控制、优惠码或解锁类逻辑，建议补齐服务端校验。",
                url=url,
                location=VulnLocation(url=url, parameter="", parameter_type="path", snippet=path_lower or "page"),
                evidence=Evidence(extra={"signals": evidence_bits}),
                fix_suggestion="所有关键状态变更都必须在服务端重新校验权限与业务约束。",
                confidence="medium",
                owasp_category="A04 不安全设计",
                cwe_id="CWE-693",
                fix=FixSuggestion(generic="把关键业务校验放在服务端，避免仅靠前端控制。"),
            )
        ]


def _origin(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"
