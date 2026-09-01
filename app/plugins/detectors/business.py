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
        probes: list[tuple[str, str, str, re.Pattern[str]]] = [
            ("/.env", "环境变量文件暴露", "high", re.compile(r"(secret|password|passwd|jwt|api[_-]?key|token|credentials|database_url|private[_-]?key|begin private key)", re.I)),
            ("/.env.local", "本地环境变量文件暴露", "high", re.compile(r"(secret|password|passwd|jwt|api[_-]?key|token|credentials|database_url|private[_-]?key|begin private key)", re.I)),
            ("/.env.production", "生产环境变量文件暴露", "high", re.compile(r"(secret|password|passwd|jwt|api[_-]?key|token|credentials|database_url|private[_-]?key|begin private key)", re.I)),
            ("/.git/config", "Git 仓库配置暴露", "high", re.compile(r"(url\s*=|remote\s+\"origin\"|fetch\s*=)", re.I)),
            ("/.git-credentials", "Git 凭据文件暴露", "high", re.compile(r"(https?://[^\s:]+:[^\s@]+@|password=|username=|token=)", re.I)),
            ("/.netrc", "Netrc 凭据文件暴露", "high", re.compile(r"(machine\s+\S+\s+login\s+\S+\s+password\s+\S+|default\s+login\s+\S+\s+password\s+\S+)", re.I)),
            ("/.pgpass", "PostgreSQL 凭据文件暴露", "high", re.compile(r"^[^:\n]+:[^:\n]*:[^:\n]*:[^:\n]+:[^:\n]+", re.I | re.M)),
            ("/.docker/config.json", "Docker 凭据文件暴露", "high", re.compile(r"(auths|credsstore|identitytoken|auth)", re.I)),
            ("/.htpasswd", "HTTP Basic 认证口令文件暴露", "high", re.compile(r"(\$apr1\$|\$2[aby]\$|\{ssha\}|^[^:\n]+:[A-Za-z0-9./$]{20,})", re.I | re.M)),
            ("/.aws/credentials", "AWS 凭据文件暴露", "high", re.compile(r"(aws_access_key_id|aws_secret_access_key|aws_session_token)", re.I)),
            ("/service-account.json", "云服务账号文件暴露", "high", re.compile(r"(\"type\"\s*:\s*\"service_account\"|private_key|client_email|token_uri)", re.I)),
            ("/firebase-service-account.json", "Firebase 服务账号文件暴露", "high", re.compile(r"(\"type\"\s*:\s*\"service_account\"|private_key|client_email|token_uri)", re.I)),
            ("/config.php", "PHP 配置文件暴露", "high", re.compile(r"(secret|password|passwd|api[_-]?key|token|database|mysqli|pdo|ldap)", re.I)),
            ("/wp-config.php", "WordPress 配置文件暴露", "high", re.compile(r"(DB_NAME|DB_USER|DB_PASSWORD|AUTH_KEY|SECURE_AUTH_KEY|LOGGED_IN_KEY|NONCE_KEY)", re.I)),
            ("/application.yml", "Spring 配置文件暴露", "high", re.compile(r"(spring:|datasource:|password:|secret:|jwt|oauth|redis|mongodb)", re.I)),
            ("/application.yaml", "Spring 配置文件暴露", "high", re.compile(r"(spring:|datasource:|password:|secret:|jwt|oauth|redis|mongodb)", re.I)),
            ("/application.properties", "Spring 配置文件暴露", "high", re.compile(r"(spring\.|datasource\.|password=|secret=|jwt|oauth|redis|mongodb)", re.I)),
            ("/application-prod.yml", "生产 Spring 配置文件暴露", "high", re.compile(r"(spring:|datasource:|password:|secret:|jwt|oauth|redis|mongodb)", re.I)),
            ("/docker-compose.yml", "Docker Compose 配置暴露", "high", re.compile(r"(services:|environment:|password|secret|token|db_|redis|postgres|mysql)", re.I)),
            ("/docker-compose.override.yml", "Docker Compose 覆盖配置暴露", "high", re.compile(r"(services:|environment:|password|secret|token|db_|redis|postgres|mysql)", re.I)),
            ("/nginx.conf", "Nginx 配置文件暴露", "high", re.compile(r"(proxy_pass|server_name|ssl_certificate|auth_basic|upstream|location\s+/)", re.I)),
            ("/apache2.conf", "Apache 配置文件暴露", "high", re.compile(r"(documentroot|proxy_pass|servername|sslcertificatefile|authuserfile)", re.I)),
            ("/httpd.conf", "Apache 配置文件暴露", "high", re.compile(r"(documentroot|proxy_pass|servername|sslcertificatefile|authuserfile)", re.I)),
            ("/haproxy.cfg", "HAProxy 配置文件暴露", "high", re.compile(r"(frontend|backend|bind\s+|server\s+|secret|password|auth)", re.I)),
            ("/Caddyfile", "Caddy 配置文件暴露", "medium", re.compile(r"(reverse_proxy|tls\s+|basic_auth|file_server|header\s+)", re.I)),
            ("/traefik.yml", "Traefik 配置文件暴露", "medium", re.compile(r"(entrypoints:|certificatesresolvers:|dashboard:|providers:|password|secret)", re.I)),
            ("/web.config", "Web 配置文件暴露", "high", re.compile(r"(connectionstrings|appsettings|password|secret|token)", re.I)),
            ("/settings.py", "应用配置文件暴露", "high", re.compile(r"(secret|password|jwt|api[_-]?key|token|database|redis|celery)", re.I)),
            ("/settings.json", "应用 JSON 配置暴露", "medium", re.compile(r"(secret|password|jwt|api[_-]?key|token|database|redis|client_id|client_secret)", re.I)),
            ("/config.json", "应用 JSON 配置暴露", "medium", re.compile(r"(secret|password|jwt|api[_-]?key|token|database|redis|client_id|client_secret)", re.I)),
            ("/secrets.json", "密钥 JSON 文件暴露", "high", re.compile(r"(secret|private_key|client_secret|refresh_token|api_key|access_token)", re.I)),
            ("/kubeconfig", "Kubernetes 配置文件暴露", "high", re.compile(r"(clusters:|users:|contexts:|client-certificate|client-key|token:)", re.I)),
            ("/terraform.tfvars", "Terraform 变量文件暴露", "high", re.compile(r"(password|secret|token|access_key|secret_key|client_secret)", re.I)),
            ("/values.yaml", "Helm Values 配置暴露", "medium", re.compile(r"(password:|secret:|token:|apiKey:|clientSecret:|database)", re.I)),
            ("/.gitlab-ci.yml", "CI 配置文件暴露", "medium", re.compile(r"(password|secret|token|api_key|docker_login|aws_access_key_id)", re.I)),
            ("/.github/workflows/ci.yml", "GitHub Actions 工作流暴露", "medium", re.compile(r"(secrets\.|password|token|aws_access_key_id|client_secret)", re.I)),
            ("/.github/workflows/deploy.yml", "GitHub Actions 工作流暴露", "medium", re.compile(r"(secrets\.|password|token|aws_access_key_id|client_secret)", re.I)),
            ("/Jenkinsfile", "Jenkins 流水线文件暴露", "medium", re.compile(r"(environment|credentials\(|password|secret|token)", re.I)),
            ("/.npmrc", "包管理配置暴露", "medium", re.compile(r"(//.*:_authToken=|registry=|always-auth=)", re.I)),
            ("/.pypirc", "PyPI 配置暴露", "medium", re.compile(r"(username=|password=|token=|index-servers)", re.I)),
            ("/access.log", "访问日志暴露", "medium", re.compile(r"(authorization:|cookie:|set-cookie:|bearer\s+[a-z0-9\.\-_]+|sessionid=|token=)", re.I)),
            ("/app.log", "应用日志暴露", "medium", re.compile(r"(traceback|exception|stack trace|password=|secret=|token=|authorization:)", re.I)),
            ("/debug.log", "调试日志暴露", "high", re.compile(r"(traceback|exception|stack trace|password=|secret=|token=|authorization:|debug)", re.I)),
            ("/error.log", "错误日志暴露", "medium", re.compile(r"(traceback|exception|stack trace|password=|secret=|token=)", re.I)),
            ("/server.log", "服务器日志暴露", "medium", re.compile(r"(traceback|exception|stack trace|password=|secret=|token=)", re.I)),
            ("/audit.log", "审计日志暴露", "medium", re.compile(r"(user\s+login|role=|permission=|authorization:|token=|secret=)", re.I)),
        ]
        findings: list[Finding] = []
        try:
            async with httpx.AsyncClient(follow_redirects=True, headers=context.headers or None) as client:
                for rel_path, title, severity, markers in probes:
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
                            title=title,
                            type="sensitive_config_exposure",
                            severity=severity,
                            description=f"可直接访问敏感文件 {rel_path}，可能泄露密钥、数据库、日志或部署信息。",
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
                                "matched_category": "log" if rel_path.endswith(".log") else "config",
                            }, response_raw=body[:4000]),
                            fix_suggestion="限制这些敏感文件的访问权限，移出 Web 根目录，并确保仓库中不包含明文密钥、日志和部署配置。",
                            confidence="high",
                            owasp_category="A01 访问控制失效",
                            cwe_id="CWE-200",
                            fix=FixSuggestion(generic="禁止 Web 直接暴露配置文件、日志文件和密钥文件。"),
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
