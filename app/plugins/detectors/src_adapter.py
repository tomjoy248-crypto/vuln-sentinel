"""SRC 扫描器插件适配器。

将 src_scanner.py 中已有的检测函数包装为 BaseVulnDetector 插件，
使旧检测能力接入新的插件化调度体系，同时保留原有逻辑与测试兼容性。
"""

from __future__ import annotations

from typing import List

from app.plugins import BaseVulnDetector, Finding, ScanContext
from app.plugins._compat import old_finding_to_finding


class SQLiDetector(BaseVulnDetector):
    """SQL 注入检测插件。"""

    name = "sqli"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> List[Finding]:
        from src_scanner import detect_sqli_src

        raw = await detect_sqli_src(context.url)
        return [old_finding_to_finding(r) for r in raw]


class ReflectedXSSDetector(BaseVulnDetector):
    """反射型 XSS 检测插件。"""

    name = "reflected_xss"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> List[Finding]:
        from src_scanner import detect_xss_src

        raw = await detect_xss_src(context.url)
        return [old_finding_to_finding(r) for r in raw]


class InfoLeakDetector(BaseVulnDetector):
    """敏感信息泄露检测插件。"""

    name = "info_leak"
    version = "1.0"
    supported_depths = ["quick", "standard", "deep"]

    async def detect(self, context: ScanContext) -> List[Finding]:
        from src_scanner import detect_info_leak_src

        raw = await detect_info_leak_src(context.url, context.headers, context.body or None)
        return [old_finding_to_finding(r) for r in raw]


class CSRFDetector(BaseVulnDetector):
    """CSRF 检测插件。"""

    name = "csrf"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> List[Finding]:
        from src_scanner import detect_csrf_src

        raw = await detect_csrf_src(context.url, context.headers, context.body or None)
        return [old_finding_to_finding(r) for r in raw]


class SensitivePathDetectorPlugin(BaseVulnDetector):
    """敏感路径检测插件。"""

    name = "sensitive_path"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> List[Finding]:
        from src_scanner import detect_sensitive_paths_src

        raw = await detect_sensitive_paths_src(context.url)
        return [old_finding_to_finding(r) for r in raw]


class OutdatedComponentDetector(BaseVulnDetector):
    """过时组件检测插件。"""

    name = "outdated_component"
    version = "1.0"
    supported_depths = ["quick", "standard", "deep"]

    async def detect(self, context: ScanContext) -> List[Finding]:
        from src_scanner import detect_outdated_components_src

        raw = await detect_outdated_components_src(context.url, context.headers, context.body or None)
        return [old_finding_to_finding(r) for r in raw]


class BrokenAccessControlDetector(BaseVulnDetector):
    """越权访问检测插件。"""

    name = "broken_access_control"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> List[Finding]:
        from src_scanner import detect_broken_access_control_src

        raw = await detect_broken_access_control_src(context.url)
        return [old_finding_to_finding(r) for r in raw]


class SSRFDetector(BaseVulnDetector):
    """SSRF 检测插件。"""

    name = "ssrf"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> List[Finding]:
        from src_scanner import detect_ssrf_src

        raw = await detect_ssrf_src(context.url)
        return [old_finding_to_finding(r) for r in raw]


class IDORDetector(BaseVulnDetector):
    """IDOR 检测插件。"""

    name = "idor"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> List[Finding]:
        from src_scanner import detect_idor_src

        raw = await detect_idor_src(context.url)
        return [old_finding_to_finding(r) for r in raw]


class FileUploadDetector(BaseVulnDetector):
    """文件上传检测插件。"""

    name = "file_upload"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> List[Finding]:
        from src_scanner import detect_file_upload_src

        raw = await detect_file_upload_src(context.url, context.body or None)
        return [old_finding_to_finding(r) for r in raw]


class LogicBypassDetector(BaseVulnDetector):
    """逻辑绕过检测插件。"""

    name = "logic_bypass"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> List[Finding]:
        from src_scanner import detect_logic_bypass_src

        raw = await detect_logic_bypass_src(context.url, context.headers, context.body or None)
        return [old_finding_to_finding(r) for r in raw]


class OpenRedirectDetector(BaseVulnDetector):
    """开放重定向检测插件。"""

    name = "open_redirect"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> List[Finding]:
        from src_scanner import detect_open_redirect_src

        raw = await detect_open_redirect_src(context.url)
        return [old_finding_to_finding(r) for r in raw]


class XXEDetector(BaseVulnDetector):
    """XXE 检测插件。"""

    name = "xxe"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> List[Finding]:
        from src_scanner import detect_xxe_src

        raw = await detect_xxe_src(context.url, context.headers, context.body or "")
        return [old_finding_to_finding(r) for r in raw]
