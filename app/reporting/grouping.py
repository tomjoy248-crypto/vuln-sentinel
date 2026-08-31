"""报告分组辅助函数。"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

SEVERITY_ORDER = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
    "info": 0,
    "informational": 0,
}

_GROUP_RULES: list[tuple[str, set[str], tuple[str, ...]]] = [
    (
        "公开暴露面",
        {
            "discovery_exposure",
            "well_known_exposure",
            "exposed_endpoint",
            "backup_exposure",
            "sensitive_path",
            "sensitive_config_exposure",
            "directory_listing",
            "server_exposure",
            "info_leak",
            "passive_exposure",
            "api_surface_exposure",
        },
        (
            "敏感路径",
            "敏感文件",
            "备份",
            "目录",
            "信息泄露",
            "source map",
            "调试",
            "公开",
            "well-known",
            "api 文档",
            "swagger",
            "openapi",
            "metrics",
            "actuator",
            "console",
            "phpinfo",
        ),
    ),
    (
        "配置与响应头",
        {
            "header_missing",
            "cookie_security",
            "cors_misconfig",
            "csp_weakness",
            "sri_missing",
            "trace_method",
            "ssl",
        },
        ("CSP", "Cookie", "CORS", "HSTS", "X-Frame-Options", "TRACE", "TLS", "HTTPS", "SRI", "integrity"),
    ),
    (
        "认证与授权",
        {
            "csrf",
            "auth_weakness",
            "bruteforce_protection",
            "api_auth_missing",
            "broken_access_control",
            "idor",
            "unauthorized_access",
            "logic_bypass",
            "clickjacking",
        },
        ("认证", "授权", "登录", "越权", "权限", "爆破", "CSRF", "IDOR", "劫持"),
    ),
    (
        "注入与输入验证",
        {
            "sqli",
            "ssti",
            "reflected_xss",
            "xxe",
            "cmdi",
            "traversal",
            "ssrf",
            "open_redirect",
            "deserialization",
        },
        ("注入", "XSS", "XXE", "命令", "遍历", "SSRF", "重定向", "反序列化"),
    ),
    (
        "组件与供应链",
        {"outdated_component"},
        ("组件", "框架", "版本", "CVE"),
    ),
]


def _get_value(finding: Any, *keys: str) -> str:
    """从字典或对象中提取第一个可用字符串值。"""
    if isinstance(finding, dict):
        for key in keys:
            value = finding.get(key)
            if value is not None and str(value).strip():
                return str(value)
        return ""
    for key in keys:
        value = getattr(finding, key, None)
        if value is not None and str(value).strip():
            return str(value)
    return ""


def get_group_label(finding: Any) -> str:
    """根据 finding 类型与标题返回报告分组名称。"""
    vuln_type = _get_value(finding, "type", "vulnerability_type").lower()
    title = _get_value(finding, "name", "title", "summary").lower()
    combined = f"{vuln_type} {title}"

    for label, types, keywords in _GROUP_RULES:
        if vuln_type in types:
            return label
        if any(keyword.lower() in combined for keyword in keywords):
            return label

    return "其他风险"


def group_findings(findings: Iterable[Any]) -> list[dict[str, Any]]:
    """按风险面分组 finding。"""
    grouped: dict[str, dict[str, Any]] = {}
    for finding in findings:
        label = get_group_label(finding)
        bucket = grouped.setdefault(
            label,
            {
                "label": label,
                "items": [],
                "counts": {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0},
            },
        )
        bucket["items"].append(finding)
        sev = _get_value(finding, "severity").lower() or "info"
        if sev not in bucket["counts"]:
            sev = "info"
        bucket["counts"][sev] += 1

    def _group_sort_key(item: dict[str, Any]) -> tuple[int, int, str]:
        counts = item["counts"]
        worst = max((SEVERITY_ORDER.get(k, 0) for k, v in counts.items() if v > 0), default=0)
        total = sum(counts.values())
        return (-worst, -total, item["label"])

    return sorted(grouped.values(), key=_group_sort_key)
