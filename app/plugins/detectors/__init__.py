"""漏洞检测器插件集合。

将 main.py 中的核心检测函数包装为 BaseVulnDetector 插件，
支持通过 DetectorRegistry 统一调度。

设计原则：
- 延迟导入 main.py 中的检测函数，避免循环导入
- 返回标准的 Finding 对象列表
- 插件失败不阻塞其他检测器
"""

from __future__ import annotations

from typing import List, Any, Dict
from urllib.parse import urlparse

from app.plugins import BaseVulnDetector, ScanContext, Finding


# ---------- 辅助函数 ----------

def _extract_url_params(url: str) -> List[str]:
    """从 URL 查询字符串中提取参数名列表。"""
    parsed = urlparse(url)
    if not parsed.query:
        return []
    return [p.split("=")[0] for p in parsed.query.split("&") if "=" in p]


def _dict_to_finding(data: dict) -> Finding:
    """将 main.py 返回的漏洞字典转换为 Finding 对象。"""
    evidence = data.get("evidence", {}) or {}
    location = data.get("location", {}) or {}
    return Finding(
        title=data.get("name", "未知漏洞"),
        type=data.get("type", "unknown"),
        severity=data.get("severity", "medium"),
        description=data.get("summary", data.get("description", "")),
        url=evidence.get("url", location.get("url", "")),
        parameter=evidence.get("param", location.get("target", "")),
        evidence=evidence,
        fix_suggestion=data.get("fix", ""),
        confidence=data.get("confidence_level", "高"),
        owasp_category=data.get("owasp", ""),
        cwe_id=data.get("cwe_id", ""),
    )


# ---------- 检测器插件 ----------

class SQLiDetector(BaseVulnDetector):
    """SQL 注入检测插件。"""

    name = "sqli"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> List[Finding]:
        params = _extract_url_params(context.url)
        if not params:
            return []
        # 延迟导入避免循环依赖
        from main import detect_sqli
        results = await detect_sqli(context.url, params)
        return [_dict_to_finding(r) for r in results if isinstance(r, dict)]


class ReflectedXSSDetector(BaseVulnDetector):
    """反射型 XSS 检测插件。"""

    name = "reflected_xss"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> List[Finding]:
        params = _extract_url_params(context.url)
        if not params:
            return []
        from main import detect_reflected_xss
        results = await detect_reflected_xss(context.url, params)
        return [_dict_to_finding(r) for r in results if isinstance(r, dict)]


class CommandInjectionDetector(BaseVulnDetector):
    """命令注入检测插件。"""

    name = "command_injection"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> List[Finding]:
        params = _extract_url_params(context.url)
        if not params:
            return []
        from main import detect_command_injection
        results = await detect_command_injection(context.url, params)
        return [_dict_to_finding(r) for r in results if isinstance(r, dict)]


class DirectoryTraversalDetector(BaseVulnDetector):
    """目录遍历检测插件。"""

    name = "directory_traversal"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> List[Finding]:
        params = _extract_url_params(context.url)
        if not params:
            return []
        from main import detect_directory_traversal
        results = await detect_directory_traversal(context.url, params)
        return [_dict_to_finding(r) for r in results if isinstance(r, dict)]


class SSRFDetector(BaseVulnDetector):
    """SSRF 检测插件。"""

    name = "ssrf"
    version = "1.0"
    supported_depths = ["standard", "deep"]

    async def detect(self, context: ScanContext) -> List[Finding]:
        params = _extract_url_params(context.url)
        if not params:
            return []
        from main import detect_ssrf_enhanced
        results = await detect_ssrf_enhanced(context.url, params)
        return [_dict_to_finding(r) for r in results if isinstance(r, dict)]


class InsecureDeserializationDetector(BaseVulnDetector):
    """不安全反序列化检测插件。"""

    name = "insecure_deserialization"
    version = "1.0"
    supported_depths = ["quick", "standard", "deep"]

    async def detect(self, context: ScanContext) -> List[Finding]:
        from main import detect_insecure_deserialization
        results = await detect_insecure_deserialization(context.headers, context.url)
        return [_dict_to_finding(r) for r in results if isinstance(r, dict)]


class TimeBasedSQLiDetector(BaseVulnDetector):
    """时间盲注 SQLi 检测插件（深度扫描专用）。"""

    name = "time_based_sqli"
    version = "1.0"
    supported_depths = ["deep"]

    async def detect(self, context: ScanContext) -> List[Finding]:
        from main import detect_time_based_sqli
        result = await detect_time_based_sqli(context.url)
        if isinstance(result, dict) and result.get("vulnerable"):
            return [_dict_to_finding(result)]
        return []


class SensitivePathDetectorPlugin(BaseVulnDetector):
    """敏感路径检测插件。"""

    name = "sensitive_paths"
    version = "1.0"
    supported_depths = ["quick", "standard", "deep"]

    async def detect(self, context: ScanContext) -> List[Finding]:
        from main import check_sensitive_paths
        parsed = urlparse(context.url)
        host = parsed.hostname or parsed.path
        if not host:
            return []
        results = await check_sensitive_paths(host, context.is_https)
        findings: List[Finding] = []
        for r in results:
            if not isinstance(r, dict):
                continue
            severity = "high" if r.get("exposed") else ("low" if r.get("suspect") else "info")
            findings.append(Finding(
                title=f"敏感路径暴露: {r.get('path', '')}" if r.get("exposed") else f"敏感路径信息: {r.get('path', '')}",
                type="sensitive_path",
                severity=severity,
                description=r.get("reason", ""),
                url=context.url,
                evidence=r,
                fix_suggestion="限制敏感路径访问或移除。",
                confidence="高" if r.get("exposed") else "中",
                owasp_category="A01 访问控制失效",
                cwe_id="CWE-548",
            ))
        return findings
