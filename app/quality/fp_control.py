"""误报控制模块。

基于启发式规则分析 finding 的可信度，标记或过滤可能的误报。
"""

from __future__ import annotations

import re
from typing import Any


class FalsePositiveControl:
    """误报控制器。

    规则设计原则：
    1. 保守策略：宁可漏报也不误报（安全场景要求）
    2. 可解释性：每条规则都有明确的判定理由
    3. 可配置性：规则权重和阈值支持外部调整
    """

    # 误报风险关键词（出现在响应中时，finding 可信度下降）
    FP_RESPONSE_KEYWORDS: list[str] = [
        "waf",
        "firewall",
        "blocked",
        "blocked by",
        "cloudflare",
        "access denied",
        "forbidden",
        "unauthorized",
        "authentication required",
        "captcha",
        "challenge",
        "rate limit",
        "too many requests",
        "incapsula",
        "sucuri",
        "akamai",
        "f5",
    ]

    # 高置信度响应特征（出现时保持或提升可信度）
    HIGH_CONFIDENCE_INDICATORS: dict[str, list[str]] = {
        "sqli": ["sql syntax", "mysql_fetch", "ora-", "pl/sql", "unclosed quotation"],
        "xss": ["<script>alert", "onerror=alert", "svg onload"],
        "cmdi": ["uid=", "gid=", "groups=", "root:", "www-data"],
        "traversal": ["root:", "daemon:", "[fonts]", "[extensions]"],
        "xxe": ["root:", "/bin/bash", "/bin/sh"],
    }

    # 低置信度上下文模式
    LOW_CONFIDENCE_PATTERNS: list[re.Pattern] = [
        re.compile(r"\b404\b.*not found", re.I),
        re.compile(r"\b500\b.*internal server error", re.I),
        re.compile(r"\b503\b.*service unavailable", re.I),
    ]

    def __init__(self, threshold: float = 0.38) -> None:
        """
        Args:
            threshold: 误报概率阈值，超过此值则标记为低置信度
        """
        self.threshold = threshold

    def analyze(self, finding: dict[str, Any]) -> dict[str, Any]:
        """分析单个 finding，返回带误报评估的结果。

        Returns:
            在原 finding 上增加以下字段：
            - fp_score: 误报概率 (0.0-1.0)
            - fp_reasons: 触发规则列表
            - adjusted_confidence: 调整后的置信度
            - is_likely_fp: 是否可能为误报
        """
        fp_score = 0.0
        reasons: list[str] = []

        vuln_type = (finding.get("type") or "").lower()
        response = self._get_response_text(finding)
        request_text = self._get_request_text(finding)
        response_headers = self._get_response_headers(finding)

        # 规则 1：WAF/防火墙拦截响应
        if self._contains_fp_keywords(response) and not self._has_strong_evidence(finding, vuln_type):
            fp_score += 0.28
            reasons.append("响应包含 WAF/拦截关键词，可能是防护设备触发的误报")

        # 规则 2：HTTP 错误状态码且无利用证据
        status_code = self._extract_status_code(response)
        if status_code in (403, 429, 503) and not self._has_exploit_evidence(
            finding, vuln_type
        ):
            fp_score += 0.18
            reasons.append(f"HTTP {status_code} 响应且无明确利用证据")
            if self._looks_like_challenge_response(response, response_headers):
                fp_score += 0.12
                reasons.append("响应更像登录/挑战/限流页面，降低直接判为漏洞的概率")

        # 规则 3：响应长度异常短（可能为通用错误页）
        resp_len = len(response)
        if resp_len < 100 and status_code != 200:
            fp_score += 0.15
            reasons.append("响应长度过短，可能是通用错误页面")

        # 规则 4：高置信度验证（如果存在强利用证据，降低误报分）
        if self._has_strong_evidence(finding, vuln_type):
            fp_score -= 0.3
            reasons.append("存在强利用证据，降低误报概率")

        # 规则 5：请求参数为常见静态资源后缀
        if request_text and self._is_static_resource(request_text) and not self._has_strong_evidence(finding, vuln_type):
            fp_score += 0.2
            reasons.append("请求目标为静态资源，动态漏洞利用概率低")

        # 规则 6：响应中包含页面框架/模板代码（可能为反射而非注入）
        if vuln_type in ("xss", "sqli") and self._contains_framework_markup(response) and not self._has_strong_evidence(finding, vuln_type):
            fp_score += 0.15
            reasons.append("响应包含框架/模板代码，可能是正常页面反射")

        # 边界处理
        fp_score = max(0.0, min(1.0, fp_score))

        original_confidence = finding.get("confidence", "high")
        adjusted = self._adjust_confidence(original_confidence, fp_score)

        result = dict(finding)
        result["fp_score"] = round(fp_score, 2)
        result["fp_reasons"] = reasons
        result["adjusted_confidence"] = adjusted
        result["is_likely_fp"] = fp_score >= self.threshold
        return result

    def analyze_batch(self, findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """批量分析 finding 列表。"""
        return [self.analyze(f) for f in findings]

    def _get_response_text(self, finding: dict[str, Any]) -> str:
        """提取响应文本。"""
        evidence = finding.get("evidence") or {}
        if isinstance(evidence, dict):
            return (evidence.get("response") or "").lower()
        return ""

    def _get_request_text(self, finding: dict[str, Any]) -> str:
        """提取请求文本。"""
        evidence = finding.get("evidence") or {}
        if isinstance(evidence, dict):
            return (evidence.get("request") or "").lower()
        return ""

    def _get_response_headers(self, finding: dict[str, Any]) -> str:
        """提取响应头文本。"""
        evidence = finding.get("evidence") or {}
        if isinstance(evidence, dict):
            headers = evidence.get("response_headers") or evidence.get("headers") or ""
            return str(headers).lower()
        return ""

    def _contains_fp_keywords(self, text: str) -> bool:
        text_lower = text.lower()
        return any(kw in text_lower for kw in self.FP_RESPONSE_KEYWORDS)

    def _extract_status_code(self, response_text: str) -> int | None:
        m = re.search(r"http/\d\.\d\s+(\d{3})", response_text, re.I)
        if m:
            return int(m.group(1))
        return None

    def _has_exploit_evidence(self, finding: dict[str, Any], vuln_type: str) -> bool:
        """检查是否有明确的利用证据。"""
        response = self._get_response_text(finding)
        indicators = self.HIGH_CONFIDENCE_INDICATORS.get(vuln_type, [])
        return any(ind in response for ind in indicators)

    def _has_strong_evidence(self, finding: dict[str, Any], vuln_type: str) -> bool:
        """检查是否有强利用证据（高可信度）。"""
        response = self._get_response_text(finding)
        payload = finding.get("evidence", {}).get("payload", "")

        # XSS：payload 完整反射且包含事件处理器
        if vuln_type == "xss" and payload and payload.lower() in response:
            if any(
                evt in response for evt in ["onerror", "onload", "alert(", "confirm("]
            ):
                return True

        # SQLi：明确的数据库错误信息
        if vuln_type == "sqli":
            db_errors = ["sql syntax", "unclosed quotation", "incorrect syntax", "ora-"]
            if any(err in response for err in db_errors):
                return True

        # CMDi：系统命令输出
        if vuln_type == "cmdi" and any(
            ind in response for ind in ["uid=", "gid=", "groups="]
        ):
            return True

        # Traversal：系统文件内容
        if vuln_type == "traversal" and any(
            ind in response for ind in ["root:", "daemon:", "[fonts]"]
        ):
            return True

        return False

    def _is_static_resource(self, request_text: str) -> bool:
        static_exts = [
            ".css",
            ".js",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".svg",
            ".ico",
            ".woff",
            ".ttf",
        ]
        first_line = request_text.splitlines()[0] if request_text else ""
        return any(ext in first_line for ext in static_exts)

    def _contains_framework_markup(self, response: str) -> bool:
        framework_patterns = [
            "<!doctype html>",
            "<html",
            "<head",
            "<body",
            "<div",
            "<script",
            "react",
            "vue",
            "angular",
            "next.js",
            "nuxt",
        ]
        return any(p in response for p in framework_patterns)

    def _looks_like_challenge_response(self, response: str, headers: str) -> bool:
        text = f"{response}\n{headers}".lower()
        challenge_markers = [
            "captcha",
            "cloudflare",
            "access denied",
            "verify you are human",
            "challenge",
            "csrf token",
            "sign in",
            "log in",
            "too many requests",
            "rate limit",
            "bot detection",
            "security check",
            "verify your browser",
        ]
        return any(marker in text for marker in challenge_markers)

    def _adjust_confidence(self, original: str, fp_score: float) -> str:
        confidence_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        rev_order = {v: k for k, v in confidence_order.items()}
        current = confidence_order.get(original.lower(), 1)

        if fp_score >= 0.7:
            delta = 3
        elif fp_score >= 0.5:
            delta = 2
        elif fp_score >= 0.3:
            delta = 1
        else:
            delta = 0

        new_idx = min(4, current + delta)
        return rev_order.get(new_idx, "low")


def filter_findings(
    findings: list[dict[str, Any]],
    threshold: float = 0.5,
    drop_fp: bool = False,
) -> list[dict[str, Any]]:
    """对 finding 列表进行误报过滤。

    Args:
        findings: 原始 finding 列表
        threshold: 误报概率阈值
        drop_fp: 是否直接删除可能的误报（False 则仅标记并保留）

    Returns:
        处理后的 finding 列表
    """
    controller = FalsePositiveControl(threshold=threshold)
    analyzed = controller.analyze_batch(findings)

    if drop_fp:
        return [f for f in analyzed if not f.get("is_likely_fp")]

    return analyzed
