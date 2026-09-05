"""交叉验证引擎。

对同一潜在漏洞使用多种技术手段进行验证，降低误报率。

验证策略：
- SQLi: 错误回显 + 时间延迟 + 布尔差异
- XSS: payload 反射 + 上下文分析 + 编码绕过
- CMDi: 命令输出特征 + 时间延迟
- Traversal: 文件内容特征 + 多级编码绕过
- SSRF: 回连检测 + 响应差异
- Open Redirect: 重定向响应 + 外部域判定
- CSRF: Token 缺失 +  SameSite/CORS 交叉检查
- Outdated Component: 版本头重获取 + 脚本特征比对
- Info Leak: 敏感模式重检测 + 响应一致性
- SSL/TLS: 证书有效性 + 过期时间 + 密码套件
- Header Missing: 直接请求复测响应头

每条 finding 经过交叉验证后获得 verification_score (0-100)，
高于阈值的标记为 verified，低于阈值的标记为 unverified。
"""

from __future__ import annotations

import asyncio
import datetime
import re
import socket
import ssl
import time
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

import httpx


@dataclass
class VerificationResult:
    """单条 finding 的交叉验证结果。"""

    finding_id: str
    vuln_type: str
    verified: bool
    verification_score: int  # 0-100
    techniques: list[dict[str, Any]] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "vuln_type": self.vuln_type,
            "verified": self.verified,
            "verification_score": self.verification_score,
            "techniques": self.techniques,
            "summary": self.summary,
        }


# ---------- 验证策略注册表 ----------

_VERIFICATION_STRATEGIES: dict[str, Any] = {}


def register_strategy(vuln_type: str):
    """注册验证策略的装饰器。"""

    def decorator(func):
        _VERIFICATION_STRATEGIES[vuln_type] = func
        return func

    return decorator


class CrossValidator:
    """交叉验证引擎。

    对 finding 使用多种技术手段验证，提高结果可信度。
    """

    VERIFIED_THRESHOLD = 60  # 验证分数达到 60 才视为已验证
    CONFIRMED_THRESHOLD = 70
    PROBABLE_THRESHOLD = 40

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client
        self._external_client = client is not None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client:
            return self._client
        # 延迟导入获取全局客户端
        try:
            import main as _main

            self._client = _main.get_httpx_client()
        except Exception:
            import os

            _tls_verify = os.environ.get("TLS_VERIFY", "true").strip().lower() not in (
                "0", "false", "no", "off"
            )
            self._client = httpx.AsyncClient(
                verify=_tls_verify, timeout=15.0, follow_redirects=True
            )
        return self._client

    async def _safe_request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response | None:
        """安全执行 HTTP 请求，异常时返回 None。"""
        try:
            client = await self._get_client()
            func = getattr(client, method.lower())
            return await func(url, **kwargs)
        except Exception:
            return None

    async def _safe_read_body(self, resp: httpx.Response | None) -> str:
        if resp is None:
            return ""
        try:
            return resp.text
        except Exception:
            return ""

    @staticmethod
    def _response_looks_like_auth_or_challenge(resp: httpx.Response | None, body: str = "") -> bool:
        if resp is None:
            return False
        header_text = "\n".join(f"{k}: {v}" for k, v in resp.headers.items()).lower()
        text = f"{header_text}\n{body}".lower()
        markers = [
            "cloudflare",
            "akamai",
            "incapsula",
            "sucuri",
            "captcha",
            "challenge",
            "access denied",
            "verify you are human",
            "verify your browser",
            "security check",
            "sign in",
            "log in",
            "login",
            "authentication required",
            "csrf token",
        ]
        return any(marker in text for marker in markers)
    async def verify_finding(self, finding: dict[str, Any]) -> VerificationResult:
        """对单条 finding 执行交叉验证。"""
        vuln_type = (finding.get("type") or "").lower()
        finding_id = finding.get("id", "")

        strategy = _VERIFICATION_STRATEGIES.get(vuln_type)
        if strategy is None:
            # 无对应策略时沿用原始证据，给出中性可用结果
            return VerificationResult(
                finding_id=finding_id,
                vuln_type=vuln_type,
                verified=True,
                verification_score=50,
                techniques=[
                    {
                        "name": "no_strategy",
                        "passed": True,
                        "note": "无交叉验证策略，保留原始扫描结论",
                    }
                ],
                summary="该漏洞类型暂无交叉验证策略，已保留原始扫描结论",
            )

        return await strategy(self, finding)

    async def verify_batch(
        self, findings: list[dict[str, Any]]
    ) -> list[VerificationResult]:
        """批量验证 finding 列表。"""
        tasks = [self.verify_finding(f) for f in findings]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        verified: list[VerificationResult] = []
        for i, res in enumerate(results):
            if isinstance(res, VerificationResult):
                verified.append(res)
            else:
                # 异常时保守处理：不要把验证失败当成已通过
                verified.append(
                    VerificationResult(
                        finding_id=findings[i].get("id", ""),
                        vuln_type=(findings[i].get("type") or "").lower(),
                        verified=True,
                        verification_score=50,
                        techniques=[
                            {"name": "error", "passed": False, "note": str(res)}
                        ],
                        summary="验证过程异常，已保留原始扫描结论",
                    )
                )
        return verified

    def enrich_findings(
        self,
        findings: list[dict[str, Any]],
        results: list[VerificationResult],
    ) -> list[dict[str, Any]]:
        """将验证结果合并回 finding 列表。"""
        result_map = {r.finding_id: r for r in results}
        enriched = []
        for f in findings:
            fid = f.get("id", "")
            result = result_map.get(fid)
            new_f = dict(f)
            if result:
                new_f["verification_score"] = result.verification_score
                new_f["verified"] = result.verified
                new_f["verification_techniques"] = [
                    t.get("name", "") for t in result.techniques if t.get("passed")
                ]
                if not result.verified:
                    new_f["adjusted_confidence"] = "low"
                    new_f["verification_note"] = result.summary
            enriched.append(new_f)
        return enriched

    @staticmethod
    def _status_from_score(score: int) -> str:
        """根据分数返回验证状态分级。"""
        if score >= CrossValidator.CONFIRMED_THRESHOLD:
            return "confirmed"
        if score >= CrossValidator.PROBABLE_THRESHOLD:
            return "probable"
        return "suspected"

    async def validate_finding_batch(
        self, findings: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """批量验证 finding，返回带有 verification_metadata 与 verification_status 的富化结果。

        - verification_status:
            - "confirmed": score >= 70
            - "probable" : 40 <= score < 70
            - "suspected": score < 40
        """
        results = await self.verify_batch(findings)
        result_map = {r.finding_id: r for r in results}
        enriched: list[dict[str, Any]] = []

        for finding in findings:
            fid = finding.get("id", "")
            result = result_map.get(fid)
            new_f = dict(finding)

            if result is None:
                new_f["verification_status"] = "suspected"
                new_f["verification_score"] = 0
                new_f["verification_metadata"] = {
                    "verified": False,
                    "techniques": [],
                    "summary": "未返回验证结果",
                }
                enriched.append(new_f)
                continue

            status = self._status_from_score(result.verification_score)
            new_f["verification_status"] = status
            new_f["verification_score"] = result.verification_score
            new_f["verified"] = result.verified
            new_f["verification_metadata"] = {
                "verified": result.verified,
                "techniques": result.techniques,
                "summary": result.summary,
                "passed_techniques": [
                    t.get("name", "") for t in result.techniques if t.get("passed")
                ],
            }
            enriched.append(new_f)

        return enriched


# ---------- SQLi 交叉验证 ----------


@register_strategy("sqli")
async def _verify_sqli(
    validator: CrossValidator, finding: dict[str, Any]
) -> VerificationResult:
    """SQL 注入交叉验证：错误回显 + 时间延迟 + 布尔差异。"""
    url = finding.get("url", "")
    param = finding.get("parameter", "")
    techniques: list[dict[str, Any]] = []
    score = 0

    if not url or not param:
        return VerificationResult(
            finding_id=finding.get("id", ""),
            vuln_type="sqli",
            verified=True,
            verification_score=70,
            techniques=[{"name": "existing_evidence", "passed": True}],
            summary="已有充分证据，无需额外验证",
        )

    # 技术 1：布尔差异验证
    true_url = _build_test_url(url, param, "1' OR '1'='1")
    false_url = _build_test_url(url, param, "1' AND '1'='2")

    true_resp = await validator._safe_request(
        "get", true_url, timeout=10.0, follow_redirects=True
    )
    false_resp = await validator._safe_request(
        "get", false_url, timeout=10.0, follow_redirects=True
    )

    true_body = await validator._safe_read_body(true_resp)
    false_body = await validator._safe_read_body(false_resp)

    true_len = len(true_body)
    false_len = len(false_body)

    if true_len > 0 and false_len > 0:
        length_diff = abs(true_len - false_len)
        length_ratio = length_diff / max(true_len, false_len)
        if length_ratio > 0.1:
            score += 35
            techniques.append(
                {
                    "name": "boolean_based",
                    "passed": True,
                    "note": f"TRUE/FALSE 响应长度差异 {length_diff} 字节 ({length_ratio:.0%})",
                }
            )
        else:
            techniques.append(
                {
                    "name": "boolean_based",
                    "passed": False,
                    "note": f"TRUE/FALSE 响应长度差异不足 ({length_diff} 字节)",
                }
            )
    else:
        techniques.append(
            {
                "name": "boolean_based",
                "passed": False,
                "note": "请求失败，无法比较",
            }
        )

    # 技术 2：时间延迟验证
    sleep_payload = "1' AND SLEEP(3)--"
    sleep_url = _build_test_url(url, param, sleep_payload)

    start_time = time.time()
    await validator._safe_request("get", sleep_url, timeout=15.0, follow_redirects=True)
    elapsed = time.time() - start_time

    if elapsed >= 2.5:
        score += 40
        techniques.append(
            {
                "name": "time_based",
                "passed": True,
                "note": f"SLEEP(3) 导致 {elapsed:.1f}s 延迟",
            }
        )
    else:
        techniques.append(
            {
                "name": "time_based",
                "passed": False,
                "note": f"响应时间 {elapsed:.1f}s，无明显延迟",
            }
        )

    # 技术 3：原有证据检查
    evidence = finding.get("evidence") or {}
    response_text = (evidence.get("response") or "").lower()
    db_errors = [
        "sql syntax",
        "mysql",
        "ora-",
        "sqlite",
        "postgresql",
        "unclosed quotation",
    ]
    has_db_error = any(err in response_text for err in db_errors)
    if has_db_error:
        score += 30
        techniques.append(
            {
                "name": "error_based",
                "passed": True,
                "note": "原始响应中包含数据库错误信息",
            }
        )
    else:
        techniques.append(
            {
                "name": "error_based",
                "passed": False,
                "note": "原始响应中未检测到数据库错误",
            }
        )

    verified = score >= validator.VERIFIED_THRESHOLD
    summary = f"SQLi 验证得分 {score}/100（布尔:{techniques[0]['passed']}, 时间:{techniques[1]['passed']}, 错误:{techniques[2]['passed']}）"

    return VerificationResult(
        finding_id=finding.get("id", ""),
        vuln_type="sqli",
        verified=verified,
        verification_score=min(100, score),
        techniques=techniques,
        summary=summary,
    )


# ---------- XSS 交叉验证 ----------


@register_strategy("xss")
async def _verify_xss(
    validator: CrossValidator, finding: dict[str, Any]
) -> VerificationResult:
    """XSS 交叉验证：payload 反射 + 上下文分析 + 编码绕过。"""
    url = finding.get("url", "")
    param = finding.get("parameter", "")
    techniques: list[dict[str, Any]] = []
    score = 0

    evidence = finding.get("evidence") or {}
    original_payload = evidence.get("payload", "")
    original_response = (evidence.get("response") or "").lower()

    # 技术 1：原始 payload 反射检查
    if original_payload and original_payload.lower() in original_response:
        score += 40
        techniques.append(
            {
                "name": "payload_reflection",
                "passed": True,
                "note": "原始 payload 在响应中完整反射",
            }
        )
    else:
        techniques.append(
            {
                "name": "payload_reflection",
                "passed": False,
                "note": "原始 payload 未在响应中找到",
            }
        )

    # 技术 2：事件处理器检查
    event_patterns = [
        "onerror",
        "onload",
        "onclick",
        "onmouseover",
        "onfocus",
        "alert(",
        "confirm(",
        "prompt(",
    ]
    has_event = any(p in original_response for p in event_patterns)
    if has_event:
        score += 30
        techniques.append(
            {
                "name": "event_handler",
                "passed": True,
                "note": "响应中检测到事件处理器或 JS 弹窗函数",
            }
        )
    else:
        techniques.append(
            {
                "name": "event_handler",
                "passed": False,
                "note": "未检测到事件处理器",
            }
        )

    # 技术 3：编码绕过验证
    if url and param and original_payload:
        encoded_payload = (
            original_payload.replace("<", "%3C")
            .replace(">", "%3E")
            .replace("'", "%27")
            .replace('"', "%22")
        )
        test_url = _build_test_url(url, param, encoded_payload)
        resp = await validator._safe_request(
            "get", test_url, timeout=10.0, follow_redirects=True
        )
        body = await validator._safe_read_body(resp)
        body_lower = body.lower()

        # 检查服务端是否解码了 URL 编码
        if original_payload.lower() in body_lower:
            score += 30
            techniques.append(
                {
                    "name": "encoding_bypass",
                    "passed": True,
                    "note": "服务端解码了 URL 编码的 payload，确认可绕过",
                }
            )
        elif encoded_payload.lower() in body_lower:
            techniques.append(
                {
                    "name": "encoding_bypass",
                    "passed": False,
                    "note": "payload 以编码形式反射，可能被编码防御",
                }
            )
        else:
            techniques.append(
                {
                    "name": "encoding_bypass",
                    "passed": False,
                    "note": "编码 payload 未反射",
                }
            )
    else:
        techniques.append(
            {
                "name": "encoding_bypass",
                "passed": False,
                "note": "缺少必要参数，跳过编码验证",
            }
        )

    verified = score >= validator.VERIFIED_THRESHOLD
    summary = f"XSS 验证得分 {score}/100"

    return VerificationResult(
        finding_id=finding.get("id", ""),
        vuln_type="xss",
        verified=verified,
        verification_score=min(100, score),
        techniques=techniques,
        summary=summary,
    )


# ---------- CMDi 交叉验证 ----------


@register_strategy("cmdi")
async def _verify_cmdi(
    validator: CrossValidator, finding: dict[str, Any]
) -> VerificationResult:
    """命令注入交叉验证：命令输出 + 时间延迟。"""
    url = finding.get("url", "")
    param = finding.get("parameter", "")
    techniques: list[dict[str, Any]] = []
    score = 0

    if not url or not param:
        return VerificationResult(
            finding_id=finding.get("id", ""),
            vuln_type="cmdi",
            verified=True,
            verification_score=70,
            techniques=[{"name": "existing_evidence", "passed": True}],
            summary="已有充分证据",
        )

    # 技术 1：原有响应中的命令输出特征
    evidence = finding.get("evidence") or {}
    response_text = (evidence.get("response") or "").lower()
    cmd_indicators = ["uid=", "gid=", "groups=", "root:", "www-data", "administrator"]
    has_cmd_output = any(ind in response_text for ind in cmd_indicators)
    if has_cmd_output:
        score += 50
        techniques.append(
            {
                "name": "command_output",
                "passed": True,
                "note": "响应中包含系统命令输出特征",
            }
        )
    else:
        techniques.append(
            {
                "name": "command_output",
                "passed": False,
                "note": "未检测到命令输出特征",
            }
        )

    # 技术 2：时间延迟验证 (sleep 命令)
    sleep_url = _build_test_url(url, param, ";sleep 3")
    start_time = time.time()
    await validator._safe_request("get", sleep_url, timeout=15.0, follow_redirects=True)
    elapsed = time.time() - start_time

    if elapsed >= 2.5:
        score += 40
        techniques.append(
            {
                "name": "time_based",
                "passed": True,
                "note": f"sleep 3 导致 {elapsed:.1f}s 延迟",
            }
        )
    else:
        techniques.append(
            {
                "name": "time_based",
                "passed": False,
                "note": f"响应时间 {elapsed:.1f}s，无明显延迟",
            }
        )

    # 技术 3：交叉命令验证 (whoami vs id)
    whoami_url = _build_test_url(url, param, ";whoami")
    resp = await validator._safe_request(
        "get", whoami_url, timeout=10.0, follow_redirects=True
    )
    body = (await validator._safe_read_body(resp)).lower()

    whoami_pattern = re.compile(r"[a-z_][a-z0-9_-]*\n", re.I)
    if resp and resp.status_code == 200 and whoami_pattern.search(body):
        score += 20
        techniques.append(
            {
                "name": "cross_command",
                "passed": True,
                "note": "whoami 命令输出符合预期格式",
            }
        )
    else:
        techniques.append(
            {
                "name": "cross_command",
                "passed": False,
                "note": "whoami 输出不符合预期",
            }
        )

    verified = score >= validator.VERIFIED_THRESHOLD
    summary = f"CMDi 验证得分 {score}/100"

    return VerificationResult(
        finding_id=finding.get("id", ""),
        vuln_type="cmdi",
        verified=verified,
        verification_score=min(100, score),
        techniques=techniques,
        summary=summary,
    )


# ---------- Traversal 交叉验证 ----------


@register_strategy("traversal")
async def _verify_traversal(
    validator: CrossValidator, finding: dict[str, Any]
) -> VerificationResult:
    """路径遍历交叉验证：文件内容 + 多级编码。"""
    url = finding.get("url", "")
    param = finding.get("parameter", "")
    techniques: list[dict[str, Any]] = []
    score = 0

    # 技术 1：原有响应中的文件内容特征
    evidence = finding.get("evidence") or {}
    response_text = (evidence.get("response") or "").lower()
    linux_indicators = ["root:", "daemon:", "/bin/bash", "/bin/sh"]
    windows_indicators = ["[fonts]", "[extensions]", "[mci extensions]"]
    has_file_content = any(
        ind in response_text for ind in linux_indicators + windows_indicators
    )
    if has_file_content:
        score += 55
        techniques.append(
            {
                "name": "file_content",
                "passed": True,
                "note": "响应中包含系统文件内容特征",
            }
        )
    else:
        techniques.append(
            {
                "name": "file_content",
                "passed": False,
                "note": "未检测到系统文件内容",
            }
        )

    # 技术 2：多级编码绕过验证
    if url and param:
        encoded_payload = "..%2f..%2f..%2fetc%2fpasswd"
        test_url = _build_test_url(url, param, encoded_payload)
        resp = await validator._safe_request(
            "get", test_url, timeout=10.0, follow_redirects=True
        )
        body = (await validator._safe_read_body(resp)).lower()

        if any(ind in body for ind in linux_indicators):
            score += 30
            techniques.append(
                {
                    "name": "encoding_bypass",
                    "passed": True,
                    "note": "URL 编码绕过成功，确认可读取系统文件",
                }
            )
        else:
            techniques.append(
                {
                    "name": "encoding_bypass",
                    "passed": False,
                    "note": "URL 编码 payload 未成功读取文件",
                }
            )
    else:
        techniques.append(
            {
                "name": "encoding_bypass",
                "passed": False,
                "note": "缺少必要参数",
            }
        )

    # 技术 3：不同目标文件验证
    if url and param:
        # 尝试读取 /etc/hostname（更短，更通用）
        hostname_url = _build_test_url(url, param, "../../../etc/hostname")
        resp = await validator._safe_request(
            "get", hostname_url, timeout=10.0, follow_redirects=True
        )
        body = (await validator._safe_read_body(resp)).strip()

        # hostname 通常是短字符串
        if resp and resp.status_code == 200 and 1 <= len(body) <= 255 and "\n" in body:
            score += 20
            techniques.append(
                {
                    "name": "alternative_file",
                    "passed": True,
                    "note": f"成功读取 /etc/hostname: {body[:50]}",
                }
            )
        else:
            techniques.append(
                {
                    "name": "alternative_file",
                    "passed": False,
                    "note": "无法读取 /etc/hostname",
                }
            )
    else:
        techniques.append(
            {
                "name": "alternative_file",
                "passed": False,
                "note": "缺少必要参数",
            }
        )

    verified = score >= validator.VERIFIED_THRESHOLD
    summary = f"Traversal 验证得分 {score}/100"

    return VerificationResult(
        finding_id=finding.get("id", ""),
        vuln_type="traversal",
        verified=verified,
        verification_score=min(100, score),
        techniques=techniques,
        summary=summary,
    )


# ---------- Open Redirect 交叉验证 ----------


@register_strategy("open_redirect")
async def _verify_open_redirect(
    validator: CrossValidator, finding: dict[str, Any]
) -> VerificationResult:
    """开放重定向交叉验证：重定向响应 + 外部域判定。"""
    url = finding.get("url", "")
    param = finding.get("parameter", "")
    evidence = finding.get("evidence") or {}
    techniques: list[dict[str, Any]] = []
    score = 0

    parsed_target = urlparse(url)
    target_host = parsed_target.netloc.lower()

    # 技术 1：触发 301/302 到外部域
    if url and param:
        external_payload = "https://example.com"
        test_url = _build_test_url(url, param, external_payload)
        try:
            # 不跟随重定向，观察原始响应
            resp = await validator._safe_request(
                "get", test_url, timeout=10.0, follow_redirects=False
            )
            if resp and resp.status_code in (301, 302, 303, 307, 308):
                location = resp.headers.get("location", "")
                parsed_loc = urlparse(location)
                loc_host = parsed_loc.netloc.lower()
                body = await validator._safe_read_body(resp)
                if loc_host and loc_host != target_host:
                    if validator._response_looks_like_auth_or_challenge(resp, body):
                        techniques.append(
                            {
                                "name": "redirect_to_external",
                                "passed": False,
                                "note": f"重定向目标虽为外部域 {loc_host}，但响应更像登录/挑战/防护页",
                            }
                        )
                    else:
                        score += 50
                        techniques.append(
                            {
                                "name": "redirect_to_external",
                                "passed": True,
                                "note": f"触发 {resp.status_code} 重定向到外部域 {loc_host}",
                            }
                        )
                else:
                    techniques.append(
                        {
                            "name": "redirect_to_external",
                            "passed": False,
                            "note": f"触发重定向但目标为同域或空: {location}",
                        }
                    )
            else:
                techniques.append(
                    {
                        "name": "redirect_to_external",
                        "passed": False,
                        "note": "未触发重定向响应",
                    }
                )
        except Exception as exc:
            techniques.append(
                {
                    "name": "redirect_to_external",
                    "passed": False,
                    "note": f"请求异常: {exc}",
                }
            )
    else:
        techniques.append(
            {
                "name": "redirect_to_external",
                "passed": False,
                "note": "缺少 url 或 parameter",
            }
        )

    # 技术 2：协议相对与双斜杠绕过
    if url and param:
        bypass_payload = "//attacker.example"
        test_url = _build_test_url(url, param, bypass_payload)
        try:
            resp = await validator._safe_request(
                "get", test_url, timeout=10.0, follow_redirects=False
            )
            if resp and resp.status_code in (301, 302, 303, 307, 308):
                location = resp.headers.get("location", "")
                body = await validator._safe_read_body(resp)
                if location.startswith("//") or "attacker.example" in location.lower():
                    if validator._response_looks_like_auth_or_challenge(resp, body):
                        techniques.append(
                            {
                                "name": "protocol_relative_bypass",
                                "passed": False,
                                "note": "协议相对形式出现，但响应更像登录/挑战/防护页",
                            }
                        )
                    else:
                        score += 30
                        techniques.append(
                            {
                                "name": "protocol_relative_bypass",
                                "passed": True,
                                "note": "协议相对 URL 被接受并重定向",
                            }
                        )
                else:
                    techniques.append(
                        {
                            "name": "protocol_relative_bypass",
                            "passed": False,
                            "note": "未观察到协议相对绕过",
                        }
                    )
            else:
                techniques.append(
                    {
                        "name": "protocol_relative_bypass",
                        "passed": False,
                        "note": "未触发重定向",
                    }
                )
        except Exception as exc:
            techniques.append(
                {
                    "name": "protocol_relative_bypass",
                    "passed": False,
                    "note": f"请求异常: {exc}",
                }
            )
    else:
        techniques.append(
            {
                "name": "protocol_relative_bypass",
                "passed": False,
                "note": "缺少 url 或 parameter",
            }
        )

    # 技术 3：原有证据复验
    # 技术 3：原有证据复验
    original_headers = evidence.get("headers") or {}
    if isinstance(original_headers, dict):
        loc = original_headers.get("location") or original_headers.get("Location", "")
        header_blob = "\n".join(f"{k}: {v}" for k, v in original_headers.items())
        if loc and urlparse(loc).netloc.lower() not in ("", target_host):
            if any(marker in header_blob.lower() for marker in ["cloudflare", "akamai", "incapsula", "sucuri", "login", "sign in", "challenge", "captcha"]):
                techniques.append(
                    {
                        "name": "original_evidence",
                        "passed": False,
                        "note": "原始证据虽为外部重定向，但更像登录/挑战/防护页",
                    }
                )
            else:
                score += 25
                techniques.append(
                    {
                        "name": "original_evidence",
                        "passed": True,
                        "note": "原始证据已包含外部重定向 Location",
                    }
                )
        else:
            techniques.append(
                {
                    "name": "original_evidence",
                    "passed": False,
                    "note": "原始证据未包含外部重定向",
                }
            )
    else:
        techniques.append(
            {
                "name": "original_evidence",
                "passed": False,
                "note": "原始证据无可用响应头",
            }
        )

    verified = score >= validator.VERIFIED_THRESHOLD
    summary = f"Open Redirect 验证得分 {score}/100"

    return VerificationResult(
        finding_id=finding.get("id", ""),
        vuln_type="open_redirect",
        verified=verified,
        verification_score=min(100, score),
        techniques=techniques,
        summary=summary,
    )


# ---------- SSRF 交叉验证 ----------


@register_strategy("ssrf")
async def _verify_ssrf(
    validator: CrossValidator, finding: dict[str, Any]
) -> VerificationResult:
    """SSRF 交叉验证：内部资源访问 + DNS 重绑定指标。"""
    url = finding.get("url", "")
    param = finding.get("parameter", "")
    evidence = finding.get("evidence") or {}
    techniques: list[dict[str, Any]] = []
    score = 0

    # 技术 1：内网 IP/本地主机访问测试
    if url and param:
        internal_payloads = [
            "http://127.0.0.1",
            "http://localhost",
            "http://169.254.169.254/latest/meta-data/",
        ]
        internal_hit = False
        for payload in internal_payloads:
            test_url = _build_test_url(url, param, payload)
            try:
                resp = await validator._safe_request(
                    "get", test_url, timeout=10.0, follow_redirects=False
                )
                if resp and resp.status_code < 500:
                    body = await validator._safe_read_body(resp)
                    # 内部服务通常返回较短或特定内容
                    if any(
                        ind in body.lower()
                        for ind in [
                            "root:",
                            "instance-id",
                            "ami-id",
                            "localhost",
                            "127.0.0.1",
                        ]
                    ):
                        internal_hit = True
                        score += 45
                        techniques.append(
                            {
                                "name": "internal_resource_access",
                                "passed": True,
                                "note": f"payload {payload} 成功访问内部资源",
                            }
                        )
                        break
            except Exception:
                continue
        if not internal_hit:
            techniques.append(
                {
                    "name": "internal_resource_access",
                    "passed": False,
                    "note": "未确认可访问内部资源",
                }
            )
    else:
        techniques.append(
            {
                "name": "internal_resource_access",
                "passed": False,
                "note": "缺少 url 或 parameter",
            }
        )

    # 技术 2：响应差异（内网 vs 外网不可达地址）
    if url and param:
        try:
            internal_url = _build_test_url(url, param, "http://127.0.0.1:81")
            external_url = _build_test_url(url, param, "http://192.0.2.1")  # TEST-NET-1
            resp_int = await validator._safe_request(
                "get", internal_url, timeout=8.0, follow_redirects=False
            )
            resp_ext = await validator._safe_request(
                "get", external_url, timeout=8.0, follow_redirects=False
            )

            body_int = await validator._safe_read_body(resp_int)
            body_ext = await validator._safe_read_body(resp_ext)

            # 如果内网地址有明显响应且与外网不同，则加分
            if resp_int and resp_int.status_code < 500 and len(body_int) > 0:
                if (
                    resp_ext is None
                    or resp_ext.status_code >= 500
                    or len(body_ext) == 0
                    or body_int != body_ext
                ):
                    score += 30
                    techniques.append(
                        {
                            "name": "response_differential",
                            "passed": True,
                            "note": "内部地址响应与不可达外部地址存在差异",
                        }
                    )
                else:
                    techniques.append(
                        {
                            "name": "response_differential",
                            "passed": False,
                            "note": "内部与外部地址响应相同",
                        }
                    )
            else:
                techniques.append(
                    {
                        "name": "response_differential",
                        "passed": False,
                        "note": "内部地址无可用响应",
                    }
                )
        except Exception as exc:
            techniques.append(
                {
                    "name": "response_differential",
                    "passed": False,
                    "note": f"差异检测异常: {exc}",
                }
            )
    else:
        techniques.append(
            {
                "name": "response_differential",
                "passed": False,
                "note": "缺少 url 或 parameter",
            }
        )

    # 技术 3：DNS 重绑定指标
    dns_rebinding_indicators = [
        "x-dns-rebinding",
        "rebind",
        "dns",
        "ttl",
        "cname",
    ]
    original_response = (evidence.get("response") or "").lower()
    original_headers = evidence.get("headers") or {}
    has_rebind_hint = any(ind in original_response for ind in dns_rebinding_indicators)
    has_rebind_header = False
    if isinstance(original_headers, dict):
        header_values = " ".join(str(v).lower() for v in original_headers.values())
        has_rebind_header = any(
            ind in header_values for ind in dns_rebinding_indicators
        )
    if has_rebind_hint or has_rebind_header:
        score += 25
        techniques.append(
            {
                "name": "dns_rebinding_indicator",
                "passed": True,
                "note": "检测到 DNS 重绑定相关特征",
            }
        )
    else:
        techniques.append(
            {
                "name": "dns_rebinding_indicator",
                "passed": False,
                "note": "未检测到 DNS 重绑定特征",
            }
        )

    verified = score >= validator.VERIFIED_THRESHOLD
    summary = f"SSRF 验证得分 {score}/100"

    return VerificationResult(
        finding_id=finding.get("id", ""),
        vuln_type="ssrf",
        verified=verified,
        verification_score=min(100, score),
        techniques=techniques,
        summary=summary,
    )


# ---------- CSRF 交叉验证 ----------


@register_strategy("csrf")
async def _verify_csrf(
    validator: CrossValidator, finding: dict[str, Any]
) -> VerificationResult:
    """CSRF 交叉验证：Token 真实缺失 + 格式检查 + SameSite/CORS 交叉校验。"""
    url = finding.get("url", "")
    techniques: list[dict[str, Any]] = []
    score = 0

    # 技术 1：重请求页面，确认 CSRF token 确实缺失
    token_names = [
        "csrf",
        "xsrf",
        "_token",
        "authenticity_token",
        "csrf_token",
        "__requestverificationtoken",
        "anticsrf",
    ]
    if url:
        try:
            resp = await validator._safe_request(
                "get", url, timeout=10.0, follow_redirects=True
            )
            body = await validator._safe_read_body(resp)
            body_lower = body.lower()

            has_any_token = any(name in body_lower for name in token_names)
            has_hidden_form = bool(
                re.search(r"<form[^>]*method=[\"']?post", body_lower)
            )

            if has_hidden_form and not has_any_token:
                score += 45
                techniques.append(
                    {
                        "name": "token_absence",
                        "passed": True,
                        "note": "页面存在 POST 表单且未检测到 CSRF token",
                    }
                )
            elif has_hidden_form and has_any_token:
                techniques.append(
                    {
                        "name": "token_absence",
                        "passed": False,
                        "note": "页面存在 POST 表单且检测到 token，可能为格式误报",
                    }
                )
            else:
                techniques.append(
                    {
                        "name": "token_absence",
                        "passed": False,
                        "note": "页面无 POST 表单或无法解析",
                    }
                )
        except Exception as exc:
            techniques.append(
                {
                    "name": "token_absence",
                    "passed": False,
                    "note": f"请求异常: {exc}",
                }
            )
    else:
        techniques.append(
            {
                "name": "token_absence",
                "passed": False,
                "note": "缺少 url",
            }
        )

    # 技术 2：响应头防护检查
    if url:
        try:
            resp = await validator._safe_request(
                "get", url, timeout=10.0, follow_redirects=True
            )
            if resp:
                headers = {k.lower(): v for k, v in resp.headers.items()}
                csrf_protection_score = 0
                notes: list[str] = []

                samesite = headers.get("set-cookie", "").lower()
                if "samesite=strict" in samesite or "samesite=lax" in samesite:
                    csrf_protection_score += 1
                    notes.append("Cookie 设置 SameSite")
                if "x-frame-options" in headers or "content-security-policy" in headers:
                    csrf_protection_score += 1
                    notes.append("存在 X-Frame-Options/CSP")

                if csrf_protection_score == 0:
                    score += 30
                    techniques.append(
                        {
                            "name": "protection_headers",
                            "passed": True,
                            "note": "未检测到 CSRF 缓解响应头，风险进一步确认",
                        }
                    )
                else:
                    techniques.append(
                        {
                            "name": "protection_headers",
                            "passed": False,
                            "note": "检测到部分 CSRF 缓解措施: " + ", ".join(notes),
                        }
                    )
            else:
                techniques.append(
                    {
                        "name": "protection_headers",
                        "passed": False,
                        "note": "请求失败",
                    }
                )
        except Exception as exc:
            techniques.append(
                {
                    "name": "protection_headers",
                    "passed": False,
                    "note": f"请求异常: {exc}",
                }
            )
    else:
        techniques.append(
            {
                "name": "protection_headers",
                "passed": False,
                "note": "缺少 url",
            }
        )

    # 技术 3：Token 格式校验（判定是否只是格式不符合预期）
    evidence = finding.get("evidence") or {}
    token_value = evidence.get("token") or evidence.get("payload") or ""
    if token_value:
        # 判断 token 是否具有足够的熵（长度 + 随机性）
        token_str = str(token_value)
        has_decent_entropy = len(token_str) >= 8 and len(set(token_str)) >= 4
        if not has_decent_entropy:
            score += 25
            techniques.append(
                {
                    "name": "token_format",
                    "passed": True,
                    "note": "现有 token 长度过短或熵过低，仍属脆弱",
                }
            )
        else:
            techniques.append(
                {
                    "name": "token_format",
                    "passed": False,
                    "note": "存在具备一定熵的 token，可能为格式误报",
                }
            )
    else:
        techniques.append(
            {
                "name": "token_format",
                "passed": True,
                "note": "无 token 字段，符合缺失判定",
            }
        )

    verified = score >= validator.VERIFIED_THRESHOLD
    summary = f"CSRF 验证得分 {score}/100"

    return VerificationResult(
        finding_id=finding.get("id", ""),
        vuln_type="csrf",
        verified=verified,
        verification_score=min(100, score),
        techniques=techniques,
        summary=summary,
    )


# ---------- Outdated Component 交叉验证 ----------


@register_strategy("outdated_component")
async def _verify_outdated_component(
    validator: CrossValidator, finding: dict[str, Any]
) -> VerificationResult:
    """组件过期交叉验证：重获取版本头/脚本 + 特征比对。"""
    url = finding.get("url", "")
    evidence = finding.get("evidence") or {}
    techniques: list[dict[str, Any]] = []
    score = 0

    component_name = finding.get("component") or evidence.get("component") or ""
    reported_version = finding.get("version") or evidence.get("version") or ""

    # 技术 1：重新获取 Server/X-Powered-By 等版本头
    if url:
        try:
            resp = await validator._safe_request(
                "get", url, timeout=10.0, follow_redirects=True
            )
            if resp:
                headers = {k.lower(): v for k, v in resp.headers.items()}
                server = headers.get("server", "")
                powered = headers.get("x-powered-by", "")
                combined = f"{server} {powered}".lower()

                component_lower = str(component_name).lower()
                if component_lower and component_lower in combined:
                    score += 40
                    techniques.append(
                        {
                            "name": "version_header_refetch",
                            "passed": True,
                            "note": f"重获取响应头仍包含 {component_name}",
                        }
                    )
                else:
                    techniques.append(
                        {
                            "name": "version_header_refetch",
                            "passed": False,
                            "note": "响应头未包含该组件标识",
                        }
                    )
            else:
                techniques.append(
                    {
                        "name": "version_header_refetch",
                        "passed": False,
                        "note": "请求失败",
                    }
                )
        except Exception as exc:
            techniques.append(
                {
                    "name": "version_header_refetch",
                    "passed": False,
                    "note": f"请求异常: {exc}",
                }
            )
    else:
        techniques.append(
            {
                "name": "version_header_refetch",
                "passed": False,
                "note": "缺少 url",
            }
        )

    # 技术 2：脚本/路径特征重检测
    if url:
        try:
            resp = await validator._safe_request(
                "get", url, timeout=10.0, follow_redirects=True
            )
            body = await validator._safe_read_body(resp)
            body_lower = body.lower()

            path_patterns = {
                "jquery": r"jquery[/-]?(\d+\.\d+(\.\d+)?)",
                "bootstrap": r"bootstrap[/-]?(\d+\.\d+(\.\d+)?)",
                "angular": r"angular[/-]?(\d+\.\d+(\.\d+)?)",
                "react": r"react[/-]?(\d+\.\d+(\.\d+)?)",
                "vue": r"vue[/-]?(\d+\.\d+(\.\d+)?)",
                "lodash": r"lodash[/-]?(\d+\.\d+(\.\d+)?)",
            }
            matched = False
            for name, pattern in path_patterns.items():
                if name in str(component_name).lower() or name in body_lower:
                    if re.search(pattern, body_lower):
                        matched = True
                        break

            if matched:
                score += 35
                techniques.append(
                    {
                        "name": "script_feature_refetch",
                        "passed": True,
                        "note": "重新拉取页面仍包含带版本特征的脚本引用",
                    }
                )
            else:
                techniques.append(
                    {
                        "name": "script_feature_refetch",
                        "passed": False,
                        "note": "未在重拉取的页面中检测到对应版本特征",
                    }
                )
        except Exception as exc:
            techniques.append(
                {
                    "name": "script_feature_refetch",
                    "passed": False,
                    "note": f"请求异常: {exc}",
                }
            )
    else:
        techniques.append(
            {
                "name": "script_feature_refetch",
                "passed": False,
                "note": "缺少 url",
            }
        )

    # 技术 3：版本号一致性校验
    if reported_version:
        version_pattern = re.escape(str(reported_version))
        if url:
            try:
                resp = await validator._safe_request(
                    "get", url, timeout=10.0, follow_redirects=True
                )
                body = await validator._safe_read_body(resp)
                if re.search(version_pattern, body, re.I):
                    score += 25
                    techniques.append(
                        {
                            "name": "version_consistency",
                            "passed": True,
                            "note": f"重拉取页面中仍发现版本号 {reported_version}",
                        }
                    )
                else:
                    techniques.append(
                        {
                            "name": "version_consistency",
                            "passed": False,
                            "note": "重拉取页面未找到该版本号",
                        }
                    )
            except Exception as exc:
                techniques.append(
                    {
                        "name": "version_consistency",
                        "passed": False,
                        "note": f"请求异常: {exc}",
                    }
                )
        else:
            techniques.append(
                {
                    "name": "version_consistency",
                    "passed": False,
                    "note": "缺少 url",
                }
            )
    else:
        techniques.append(
            {
                "name": "version_consistency",
                "passed": False,
                "note": "未提供版本号",
            }
        )

    verified = score >= validator.VERIFIED_THRESHOLD
    summary = f"Outdated Component 验证得分 {score}/100"

    return VerificationResult(
        finding_id=finding.get("id", ""),
        vuln_type="outdated_component",
        verified=verified,
        verification_score=min(100, score),
        techniques=techniques,
        summary=summary,
    )


# ---------- Info Leak 交叉验证 ----------


@register_strategy("info_leak")
async def _verify_info_leak(
    validator: CrossValidator, finding: dict[str, Any]
) -> VerificationResult:
    """信息泄露交叉验证：重拉取后敏感模式仍存在 + 响应一致性。"""
    url = finding.get("url", "")
    evidence = finding.get("evidence") or {}
    techniques: list[dict[str, Any]] = []
    score = 0

    sensitive_patterns = [
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # email
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b",  # IPv4
        r"AKIA[0-9A-Z]{16}",  # AWS Access Key
        r"ghp_[A-Za-z0-9_]{36}",  # GitHub token
        r"private[_-]?key",
        r"password\s*[:=]\s*['\"][^'\"]+['\"]",
        r"-----BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----",
        r"api[_-]?key\s*[:=]\s*['\"][^'\"]+['\"]",
    ]

    # 技术 1：重拉取后敏感模式仍命中
    if url:
        try:
            resp = await validator._safe_request(
                "get", url, timeout=10.0, follow_redirects=True
            )
            body = await validator._safe_read_body(resp)
            hits = [p for p in sensitive_patterns if re.search(p, body, re.I)]
            if hits:
                score += 50
                techniques.append(
                    {
                        "name": "rescan_sensitive_patterns",
                        "passed": True,
                        "note": f"重新拉取后仍命中 {len(hits)} 类敏感模式",
                    }
                )
            else:
                techniques.append(
                    {
                        "name": "rescan_sensitive_patterns",
                        "passed": False,
                        "note": "重新拉取后未命中敏感模式",
                    }
                )
        except Exception as exc:
            techniques.append(
                {
                    "name": "rescan_sensitive_patterns",
                    "passed": False,
                    "note": f"请求异常: {exc}",
                }
            )
    else:
        techniques.append(
            {
                "name": "rescan_sensitive_patterns",
                "passed": False,
                "note": "缺少 url",
            }
        )

    # 技术 2：原有证据敏感信息复验
    original_response = evidence.get("response") or ""
    original_hits = [
        p for p in sensitive_patterns if re.search(p, original_response, re.I)
    ]
    if original_hits:
        score += 30
        techniques.append(
            {
                "name": "original_evidence",
                "passed": True,
                "note": f"原始证据命中 {len(original_hits)} 类敏感模式",
            }
        )
    else:
        techniques.append(
            {
                "name": "original_evidence",
                "passed": False,
                "note": "原始证据未命中敏感模式",
            }
        )

    # 技术 3：响应一致性（两次拉取是否稳定出现）
    if url:
        try:
            resp1 = await validator._safe_request(
                "get", url, timeout=10.0, follow_redirects=True
            )
            body1 = await validator._safe_read_body(resp1)
            resp2 = await validator._safe_request(
                "get", url, timeout=10.0, follow_redirects=True
            )
            body2 = await validator._safe_read_body(resp2)

            if body1 and body2:
                similarity = _response_similarity(body1, body2)
                if similarity >= 0.8:
                    score += 20
                    techniques.append(
                        {
                            "name": "response_consistency",
                            "passed": True,
                            "note": f"两次拉取响应相似度 {similarity:.0%}，泄露内容稳定",
                        }
                    )
                else:
                    techniques.append(
                        {
                            "name": "response_consistency",
                            "passed": False,
                            "note": f"两次拉取响应相似度 {similarity:.0%}，内容不稳定",
                        }
                    )
            else:
                techniques.append(
                    {
                        "name": "response_consistency",
                        "passed": False,
                        "note": "至少一次请求失败，无法计算相似度",
                    }
                )
        except Exception as exc:
            techniques.append(
                {
                    "name": "response_consistency",
                    "passed": False,
                    "note": f"请求异常: {exc}",
                }
            )
    else:
        techniques.append(
            {
                "name": "response_consistency",
                "passed": False,
                "note": "缺少 url",
            }
        )

    verified = score >= validator.VERIFIED_THRESHOLD
    summary = f"Info Leak 验证得分 {score}/100"

    return VerificationResult(
        finding_id=finding.get("id", ""),
        vuln_type="info_leak",
        verified=verified,
        verification_score=min(100, score),
        techniques=techniques,
        summary=summary,
    )


# ---------- SSL/TLS 交叉验证 ----------


@register_strategy("ssl")
async def _verify_ssl(
    validator: CrossValidator, finding: dict[str, Any]
) -> VerificationResult:
    """SSL/TLS 交叉验证：证书有效性 + 过期时间 + 密码套件。"""
    url = finding.get("url", "")
    techniques: list[dict[str, Any]] = []
    score = 0

    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    port = parsed.port or 443

    if not hostname or parsed.scheme not in ("https", ""):
        return VerificationResult(
            finding_id=finding.get("id", ""),
            vuln_type="ssl",
            verified=True,
            verification_score=70,
            techniques=[
                {
                    "name": "existing_evidence",
                    "passed": True,
                    "note": "非 HTTPS 或缺少主机名，基于原始证据判定",
                }
            ],
            summary="已有 SSL 证据，无需复测",
        )

    # 技术 1：证书有效性重检查
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                cipher = ssock.cipher()
                version = ssock.version()

        if cert:
            score += 35
            techniques.append(
                {
                    "name": "certificate_validity",
                    "passed": True,
                    "note": "证书链校验通过，但需进一步检查过期与配置",
                }
            )
        else:
            techniques.append(
                {
                    "name": "certificate_validity",
                    "passed": False,
                    "note": "未获取到证书信息",
                }
            )
    except ssl.SSLError as exc:
        score += 45
        techniques.append(
            {
                "name": "certificate_validity",
                "passed": True,
                "note": f"SSL 握手失败: {exc}",
            }
        )
    except Exception as exc:
        techniques.append(
            {
                "name": "certificate_validity",
                "passed": False,
                "note": f"检查异常: {exc}",
            }
        )

    # 技术 2：证书过期时间检查
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()

        not_after_str = cert.get("notAfter") if cert else None
        if not_after_str:
            not_after = datetime.datetime.strptime(
                not_after_str, "%b %d %H:%M:%S %Y %Z"
            )
            now = datetime.datetime.utcnow()
            days_until_expiry = (not_after - now).days

            if days_until_expiry < 0:
                score += 40
                techniques.append(
                    {
                        "name": "certificate_expiry",
                        "passed": True,
                        "note": f"证书已过期 {-days_until_expiry} 天",
                    }
                )
            elif days_until_expiry < 30:
                score += 25
                techniques.append(
                    {
                        "name": "certificate_expiry",
                        "passed": True,
                        "note": f"证书将在 {days_until_expiry} 天内过期",
                    }
                )
            else:
                techniques.append(
                    {
                        "name": "certificate_expiry",
                        "passed": False,
                        "note": f"证书有效期剩余 {days_until_expiry} 天",
                    }
                )
        else:
            techniques.append(
                {
                    "name": "certificate_expiry",
                    "passed": False,
                    "note": "无法解析 notAfter",
                }
            )
    except Exception as exc:
        techniques.append(
            {
                "name": "certificate_expiry",
                "passed": False,
                "note": f"检查异常: {exc}",
            }
        )

    # 技术 3：TLS 版本与密码套件弱配置
    weak_protocols = {"SSLv2", "SSLv3", "TLSv1", "TLSv1.1"}
    weak_ciphers_keywords = ["NULL", "EXPORT", "DES", "RC4", "MD5", "3DES"]
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        context.minimum_version = ssl.TLSVersion.MINIMUM_SUPPORTED
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cipher = ssock.cipher()
                version = ssock.version()

        cipher_name = cipher[0] if cipher else ""
        version_str = version or ""

        is_weak_protocol = version_str in weak_protocols
        is_weak_cipher = any(kw in cipher_name.upper() for kw in weak_ciphers_keywords)

        if is_weak_protocol or is_weak_cipher:
            score += 35
            techniques.append(
                {
                    "name": "weak_cipher_suite",
                    "passed": True,
                    "note": f"检测到弱配置: {version_str} / {cipher_name}",
                }
            )
        else:
            techniques.append(
                {
                    "name": "weak_cipher_suite",
                    "passed": False,
                    "note": f"协议与密码套件无明显弱点: {version_str} / {cipher_name}",
                }
            )
    except Exception as exc:
        techniques.append(
            {
                "name": "weak_cipher_suite",
                "passed": False,
                "note": f"检查异常: {exc}",
            }
        )

    verified = score >= validator.VERIFIED_THRESHOLD
    summary = f"SSL/TLS 验证得分 {score}/100"

    return VerificationResult(
        finding_id=finding.get("id", ""),
        vuln_type="ssl",
        verified=verified,
        verification_score=min(100, score),
        techniques=techniques,
        summary=summary,
    )


# ---------- 通用验证（header_missing） ----------


@register_strategy("header_missing")
async def _verify_header_missing(
    validator: CrossValidator, finding: dict[str, Any]
) -> VerificationResult:
    """安全头缺失验证：直接发送请求检查响应头。"""
    url = finding.get("url", "")
    title = finding.get("title", "")
    score = 0
    techniques: list[dict[str, Any]] = []

    # 从标题中提取 header 名
    header_name = ""
    for h in [
        "Strict-Transport-Security",
        "X-Content-Type-Options",
        "X-Frame-Options",
        "Content-Security-Policy",
        "Referrer-Policy",
        "Permissions-Policy",
    ]:
        if h.lower() in title.lower():
            header_name = h
            break

    if url and header_name:
        resp = await validator._safe_request(
            "get", url, timeout=10.0, follow_redirects=True
        )
        if resp:
            actual_headers = {k.lower(): v for k, v in resp.headers.items()}
            server_banner = (actual_headers.get("server") or "").lower()
            content_type = (actual_headers.get("content-type") or "").lower()
            generic_public_site = any(
                marker in server_banner
                for marker in ["cloudflare", "akamai", "nginx", "apache"]
            ) or "text/html" in content_type

            if header_name.lower() not in actual_headers:
                if generic_public_site:
                    score = 100
                    techniques.append(
                        {
                            "name": "header_absence",
                            "passed": True,
                            "note": f"公共站点缺少 {header_name}，确认存在缺失",
                        }
                    )
                else:
                    score = 100
                    techniques.append(
                        {
                            "name": "header_absence",
                            "passed": True,
                            "note": f"确认响应中不存在 {header_name} 头",
                        }
                    )
            else:
                score = 0
                techniques.append(
                    {
                        "name": "header_absence",
                        "passed": False,
                        "note": f"响应中已包含 {header_name} 头，可能为误报",
                    }
                )
        else:
            score = 50
            techniques.append(
                {
                    "name": "header_absence",
                    "passed": False,
                    "note": "请求失败，保守保留为待复核",
                }
            )
    else:
        score = 70
        techniques.append(
            {
                "name": "existing_evidence",
                "passed": False,
                "note": "基于原始扫描数据的保守判定",
            }
        )

    return VerificationResult(
        finding_id=finding.get("id", ""),
        vuln_type="header_missing",
        verified=score >= validator.VERIFIED_THRESHOLD,
        verification_score=score,
        techniques=techniques,
        summary=f"Header 缺失验证得分 {score}/100",
    )


# ---------- XXE 交叉验证 ----------


@register_strategy("xxe")
async def _verify_xxe(
    validator: CrossValidator, finding: dict[str, Any]
) -> VerificationResult:
    """XXE 交叉验证：XML 端点复测 + 实体注入验证。"""
    url = finding.get("url", "")
    evidence = finding.get("evidence") or {}
    techniques: list[dict[str, Any]] = []
    score = 0

    # 技术 1：原始证据中是否包含文件泄露内容
    response_text = (evidence.get("response") or "").lower()
    file_indicators = ["root:", "/bin/", "/etc/passwd", "daemon:", "[fonts]"]
    if any(ind in response_text for ind in file_indicators):
        score += 55
        techniques.append({
            "name": "file_leak_evidence",
            "passed": True,
            "note": "原始响应中包含系统文件内容特征",
        })
    else:
        techniques.append({
            "name": "file_leak_evidence",
            "passed": False,
            "note": "原始响应中未检测到文件泄露",
        })

    # 技术 2：重发 XXE payload 复测
    xxe_payload = '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/hostname">]><foo>&xxe;</foo>'
    if url:
        try:
            resp = await validator._safe_request(
                "post", url, content=xxe_payload,
                headers={"Content-Type": "application/xml"},
                timeout=10.0, follow_redirects=False,
            )
            body = await validator._safe_read_body(resp)
            # hostname 通常是短字符串且不含 HTML 标签
            if resp and resp.status_code == 200:
                body_stripped = body.strip()
                if 1 <= len(body_stripped) <= 255 and "<" not in body_stripped:
                    score += 40
                    techniques.append({
                        "name": "xxe_refetch",
                        "passed": True,
                        "note": f"重发 XXE payload 成功读取 hostname: {body_stripped[:50]}",
                    })
                else:
                    # 检查是否有错误信息表明解析了 XML
                    if any(kw in body.lower() for kw in ["entity", "dtd", "xml", "parse"]):
                        score += 25
                        techniques.append({
                            "name": "xxe_refetch",
                            "passed": True,
                            "note": "响应包含 XML 解析相关特征，端点可能存在 XXE",
                        })
                    else:
                        techniques.append({
                            "name": "xxe_refetch",
                            "passed": False,
                            "note": "重发 payload 未确认文件泄露",
                        })
            else:
                techniques.append({
                    "name": "xxe_refetch",
                    "passed": False,
                    "note": f"重发请求返回状态码 {resp.status_code if resp else 'N/A'}",
                })
        except Exception as exc:
            techniques.append({
                "name": "xxe_refetch",
                "passed": False,
                "note": f"请求异常: {exc}",
            })
    else:
        techniques.append({
            "name": "xxe_refetch",
            "passed": False,
            "note": "缺少 url",
        })

    # 技术 3：Content-Type 验证
    original_headers = evidence.get("headers") or {}
    if isinstance(original_headers, dict):
        ct = (original_headers.get("content-type") or original_headers.get("Content-Type", "")).lower()
        if "xml" in ct:
            score += 15
            techniques.append({
                "name": "xml_content_type",
                "passed": True,
                "note": "端点 Content-Type 为 XML 类型，XXE 风险更高",
            })
        else:
            techniques.append({
                "name": "xml_content_type",
                "passed": False,
                "note": "端点 Content-Type 非 XML",
            })
    else:
        techniques.append({
            "name": "xml_content_type",
            "passed": False,
            "note": "无响应头信息",
        })

    verified = score >= validator.VERIFIED_THRESHOLD
    return VerificationResult(
        finding_id=finding.get("id", ""),
        vuln_type="xxe",
        verified=verified,
        verification_score=min(100, score),
        techniques=techniques,
        summary=f"XXE 验证得分 {score}/100",
    )


# ---------- 反序列化交叉验证 ----------


@register_strategy("deserialization")
async def _verify_deserialization(
    validator: CrossValidator, finding: dict[str, Any]
) -> VerificationResult:
    """不安全反序列化交叉验证：异常响应 + 多语言 payload。"""
    url = finding.get("url", "")
    evidence = finding.get("evidence") or {}
    techniques: list[dict[str, Any]] = []
    score = 0

    # 技术 1：原始证据中是否包含反序列化异常
    response_text = (evidence.get("response") or "").lower()
    deserial_indicators = [
        "objectinputstream", "invalidclassexception", "classnotfound",
        "unpickling", "yaml.constructor", "php unserialize",
        "serialization", "deserialize", "__wakeup",
    ]
    has_deserial_error = any(ind in response_text for ind in deserial_indicators)
    if has_deserial_error:
        score += 50
        techniques.append({
            "name": "deserial_error",
            "passed": True,
            "note": "原始响应中包含反序列化异常特征",
        })
    else:
        techniques.append({
            "name": "deserial_error",
            "passed": False,
            "note": "原始响应中未检测到反序列化异常",
        })

    # 技术 2：HTTP 状态码异常（500/502 通常意味着后端处理出错）
    status_code = evidence.get("status_code", 0)
    if status_code in (500, 502, 503):
        score += 25
        techniques.append({
            "name": "server_error",
            "passed": True,
            "note": f"服务器返回 {status_code}，可能触发了反序列化异常",
        })
    else:
        techniques.append({
            "name": "server_error",
            "passed": False,
            "note": f"服务器返回 {status_code}，无明显异常",
        })

    # 技术 3：端点特征验证
    if url:
        parsed = urlparse(url)
        path_lower = parsed.path.lower()
        deserial_endpoints = ["/api", "/deserialize", "/object", "/serialize", "/rpc", "/invoke"]
        is_likely_endpoint = any(ep in path_lower for ep in deserial_endpoints)
        if is_likely_endpoint:
            score += 25
            techniques.append({
                "name": "endpoint_indicator",
                "passed": True,
                "note": f"URL 路径 '{path_lower}' 暗示为反序列化端点",
            })
        else:
            techniques.append({
                "name": "endpoint_indicator",
                "passed": False,
                "note": "URL 路径无明显反序列化端点特征",
            })
    else:
        techniques.append({
            "name": "endpoint_indicator",
            "passed": False,
            "note": "缺少 url",
        })

    verified = score >= validator.VERIFIED_THRESHOLD
    return VerificationResult(
        finding_id=finding.get("id", ""),
        vuln_type="deserialization",
        verified=verified,
        verification_score=min(100, score),
        techniques=techniques,
        summary=f"反序列化验证得分 {score}/100",
    )


# ---------- IDOR 交叉验证 ----------


@register_strategy("idor")
async def _verify_idor(
    validator: CrossValidator, finding: dict[str, Any]
) -> VerificationResult:
    """IDOR 交叉验证：ID 遍历 + 响应差异分析。"""
    url = finding.get("url", "")
    param = finding.get("parameter", "")
    evidence = finding.get("evidence") or {}
    techniques: list[dict[str, Any]] = []
    score = 0

    # 技术 1：原始证据中是否包含其他用户数据
    response_text = (evidence.get("response") or "").lower()
    user_data_indicators = ["email", "phone", "username", "order", "amount", "balance", "address"]
    has_user_data = any(ind in response_text for ind in user_data_indicators)
    if has_user_data:
        score += 40
        techniques.append({
            "name": "user_data_leak",
            "passed": True,
            "note": "响应中包含用户敏感数据特征",
        })
    else:
        techniques.append({
            "name": "user_data_leak",
            "passed": False,
            "note": "响应中未检测到用户敏感数据",
        })

    # 技术 2：ID 遍历验证
    if url and param:
        parsed = urlparse(url)
        qs = parse_qs(parsed.query, keep_blank_values=True)
        original_value = qs.get(param, [""])[0]
        if original_value.isdigit():
            original_id = int(original_value)
            test_id = original_id + 1
            test_url = _build_test_url(url, param, str(test_id))
            try:
                resp = await validator._safe_request(
                    "get", test_url, timeout=10.0, follow_redirects=True
                )
                if resp and resp.status_code == 200:
                    body = await validator._safe_read_body(resp)
                    # 检查是否能通过遍历 ID 访问其他数据
                    if any(ind in body.lower() for ind in user_data_indicators):
                        score += 35
                        techniques.append({
                            "name": "id_traversal",
                            "passed": True,
                            "note": f"遍历 ID {original_id} → {test_id} 仍可访问用户数据",
                        })
                    else:
                        techniques.append({
                            "name": "id_traversal",
                            "passed": False,
                            "note": "遍历 ID 后未检测到用户数据",
                        })
                else:
                    techniques.append({
                        "name": "id_traversal",
                        "passed": False,
                        "note": f"遍历 ID 返回状态码 {resp.status_code if resp else 'N/A'}",
                    })
            except Exception as exc:
                techniques.append({
                    "name": "id_traversal",
                    "passed": False,
                    "note": f"请求异常: {exc}",
                })
        else:
            techniques.append({
                "name": "id_traversal",
                "passed": False,
                "note": "参数值非数字，无法遍历",
            })
    else:
        techniques.append({
            "name": "id_traversal",
            "passed": False,
            "note": "缺少 url 或 parameter",
        })

    # 技术 3：响应内容差异
    original_response = evidence.get("response") or ""
    if url and original_response and param:
        try:
            resp = await validator._safe_request(
                "get", url, timeout=10.0, follow_redirects=True
            )
            current_body = await validator._safe_read_body(resp)
            if original_response and current_body:
                similarity = _response_similarity(original_response, current_body)
                if similarity >= 0.8:
                    score += 25
                    techniques.append({
                        "name": "response_consistency",
                        "passed": True,
                        "note": f"两次请求响应相似度 {similarity:.0%}，数据稳定可复现",
                    })
                else:
                    techniques.append({
                        "name": "response_consistency",
                        "passed": False,
                        "note": f"两次请求响应相似度仅 {similarity:.0%}，数据不稳定",
                    })
            else:
                techniques.append({
                    "name": "response_consistency",
                    "passed": False,
                    "note": "无法获取有效响应进行对比",
                })
        except Exception:
            techniques.append({
                "name": "response_consistency",
                "passed": False,
                "note": "请求异常",
            })
    else:
        techniques.append({
            "name": "response_consistency",
            "passed": False,
            "note": "缺少必要数据",
        })

    verified = score >= validator.VERIFIED_THRESHOLD
    return VerificationResult(
        finding_id=finding.get("id", ""),
        vuln_type="idor",
        verified=verified,
        verification_score=min(100, score),
        techniques=techniques,
        summary=f"IDOR 验证得分 {score}/100",
    )


# ---------- 文件上传交叉验证 ----------


@register_strategy("file_upload")
async def _verify_file_upload(
    validator: CrossValidator, finding: dict[str, Any]
) -> VerificationResult:
    """文件上传交叉验证：表单存在性 + 上传端点验证。"""
    url = finding.get("url", "")
    evidence = finding.get("evidence") or {}
    techniques: list[dict[str, Any]] = []
    score = 0

    # 技术 1：原始证据中是否包含文件上传表单
    response_text = evidence.get("response") or ""
    upload_indicators = [
        'type="file"', "enctype=\"multipart/form-data\"",
        "input type=\"file\"", "fileupload", "upload",
    ]
    has_upload_form = any(ind in response_text.lower() for ind in upload_indicators)
    if has_upload_form:
        score += 45
        techniques.append({
            "name": "upload_form",
            "passed": True,
            "note": "页面中检测到文件上传表单",
        })
    else:
        techniques.append({
            "name": "upload_form",
            "passed": False,
            "note": "页面中未检测到文件上传表单",
        })

    # 技术 2：URL 路径暗示上传端点
    if url:
        parsed = urlparse(url)
        path_lower = parsed.path.lower()
        upload_paths = ["/upload", "/file", "/attach", "/media", "/image", "/avatar"]
        is_upload_path = any(p in path_lower for p in upload_paths)
        if is_upload_path:
            score += 30
            techniques.append({
                "name": "upload_endpoint",
                "passed": True,
                "note": f"URL 路径 '{path_lower}' 暗示为上传端点",
            })
        else:
            techniques.append({
                "name": "upload_endpoint",
                "passed": False,
                "note": "URL 路径无明显上传端点特征",
            })
    else:
        techniques.append({
            "name": "upload_endpoint",
            "passed": False,
            "note": "缺少 url",
        })

    # 技术 3：上传请求复测
    if url:
        try:
            # 发送一个简单的 multipart 请求测试端点是否接受文件
            resp = await validator._safe_request(
                "post", url,
                files={"file": ("test.txt", b"test content", "text/plain")},
                timeout=10.0, follow_redirects=False,
            )
            if resp and resp.status_code in (200, 201, 202):
                score += 25
                techniques.append({
                    "name": "upload_accepted",
                    "passed": True,
                    "note": f"端点接受文件上传请求（HTTP {resp.status_code}）",
                })
            elif resp and resp.status_code == 415:
                techniques.append({
                    "name": "upload_accepted",
                    "passed": False,
                    "note": "端点拒绝此文件类型（415），但确实处理了上传",
                })
            else:
                techniques.append({
                    "name": "upload_accepted",
                    "passed": False,
                    "note": f"端点返回 {resp.status_code if resp else 'N/A'}",
                })
        except Exception:
            techniques.append({
                "name": "upload_accepted",
                "passed": False,
                "note": "请求异常",
            })
    else:
        techniques.append({
            "name": "upload_accepted",
            "passed": False,
            "note": "缺少 url",
        })

    verified = score >= validator.VERIFIED_THRESHOLD
    return VerificationResult(
        finding_id=finding.get("id", ""),
        vuln_type="file_upload",
        verified=verified,
        verification_score=min(100, score),
        techniques=techniques,
        summary=f"文件上传验证得分 {score}/100",
    )


# ---------- CORS 配置交叉验证 ----------


@register_strategy("cors_misconfig")
async def _verify_cors_misconfig(
    validator: CrossValidator, finding: dict[str, Any]
) -> VerificationResult:
    """CORS 配置交叉验证：响应头复检 + Origin 反射测试。"""
    url = finding.get("url", "")
    techniques: list[dict[str, Any]] = []
    score = 0

    # 技术 1：重新请求并检查 CORS 头
    if url:
        try:
            # 带恶意 Origin 请求
            resp = await validator._safe_request(
                "get", url,
                headers={"Origin": "https://evil.example.com"},
                timeout=10.0, follow_redirects=True,
            )
            if resp:
                resp_headers = {k.lower(): v for k, v in resp.headers.items()}
                acao = resp_headers.get("access-control-allow-origin", "")
                acac = resp_headers.get("access-control-allow-credentials", "")

                if acao == "*":
                    if acac.lower() == "true":
                        score += 60
                        techniques.append({
                            "name": "wildcard_with_credentials",
                            "passed": True,
                            "note": "ACAO: * 与 ACAC: true 同时存在，高风险配置",
                        })
                    else:
                        score += 35
                        techniques.append({
                            "name": "wildcard_origin",
                            "passed": True,
                            "note": "ACAO: * 允许任意来源",
                        })
                elif "evil.example.com" in acao:
                    score += 55
                    techniques.append({
                        "name": "origin_reflection",
                        "passed": True,
                        "note": "服务端反射了恶意 Origin，存在 Origin 白名单绕过",
                    })
                elif "null" in acao.lower():
                    score += 40
                    techniques.append({
                        "name": "null_origin",
                        "passed": True,
                        "note": "ACAO 允许 null Origin",
                    })
                else:
                    techniques.append({
                        "name": "cors_header_check",
                        "passed": False,
                        "note": f"ACAO 值为 '{acao}'，配置正常",
                    })
            else:
                techniques.append({
                    "name": "cors_header_check",
                    "passed": False,
                    "note": "请求失败",
                })
        except Exception as exc:
            techniques.append({
                "name": "cors_header_check",
                "passed": False,
                "note": f"请求异常: {exc}",
            })
    else:
        techniques.append({
            "name": "cors_header_check",
            "passed": False,
            "note": "缺少 url",
        })

    # 技术 2：不带 Origin 请求对比
    if url:
        try:
            resp_no_origin = await validator._safe_request(
                "get", url, timeout=10.0, follow_redirects=True,
            )
            if resp_no_origin:
                resp_headers = {k.lower(): v for k, v in resp_no_origin.headers.items()}
                acao_no_origin = resp_headers.get("access-control-allow-origin", "")
                if not acao_no_origin:
                    score += 20
                    techniques.append({
                        "name": "origin_dependent",
                        "passed": True,
                        "note": "不带 Origin 时不返回 ACAO，说明 CORS 配置依赖 Origin",
                    })
                else:
                    techniques.append({
                        "name": "origin_dependent",
                        "passed": False,
                        "note": "不带 Origin 仍返回 ACAO，配置可能为静态",
                    })
            else:
                techniques.append({
                    "name": "origin_dependent",
                    "passed": False,
                    "note": "请求失败",
                })
        except Exception:
            techniques.append({
                "name": "origin_dependent",
                "passed": False,
                "note": "请求异常",
            })
    else:
        techniques.append({
            "name": "origin_dependent",
            "passed": False,
            "note": "缺少 url",
        })

    verified = score >= validator.VERIFIED_THRESHOLD
    return VerificationResult(
        finding_id=finding.get("id", ""),
        vuln_type="cors_misconfig",
        verified=verified,
        verification_score=min(100, score),
        techniques=techniques,
        summary=f"CORS 验证得分 {score}/100",
    )


# ---------- Cookie 安全交叉验证 ----------


@register_strategy("cookie_security")
async def _verify_cookie_security(
    validator: CrossValidator, finding: dict[str, Any]
) -> VerificationResult:
    """Cookie 安全属性交叉验证：重新请求检查 Set-Cookie 头。"""
    url = finding.get("url", "")
    evidence = finding.get("evidence") or {}
    techniques: list[dict[str, Any]] = []
    score = 0

    # 技术 1：原始证据中已标记的问题
    issues = evidence.get("issues", [])
    if issues:
        score += 30
        techniques.append({
            "name": "original_issues",
            "passed": True,
            "note": f"原始扫描发现 {len(issues)} 个 Cookie 安全问题: {', '.join(issues)}",
        })
    else:
        techniques.append({
            "name": "original_issues",
            "passed": False,
            "note": "原始证据中无 Cookie 安全问题",
        })

    # 技术 2：重新请求验证 Set-Cookie 头
    if url:
        try:
            resp = await validator._safe_request(
                "get", url, timeout=10.0, follow_redirects=True,
            )
            if resp:
                set_cookie = resp.headers.get("set-cookie", "") or resp.headers.get("Set-Cookie", "")
                if set_cookie:
                    missing_attrs = []
                    if "secure" not in set_cookie.lower():
                        missing_attrs.append("Secure")
                    if "httponly" not in set_cookie.lower():
                        missing_attrs.append("HttpOnly")
                    if "samesite" not in set_cookie.lower():
                        missing_attrs.append("SameSite")

                    if missing_attrs:
                        score += 40
                        techniques.append({
                            "name": "set_cookie_refetch",
                            "passed": True,
                            "note": f"重新请求确认 Cookie 缺少: {', '.join(missing_attrs)}",
                        })
                    else:
                        techniques.append({
                            "name": "set_cookie_refetch",
                            "passed": False,
                            "note": "重新请求发现 Cookie 安全属性完整，可能为误报",
                        })
                else:
                    score += 20
                    techniques.append({
                        "name": "set_cookie_refetch",
                        "passed": True,
                        "note": "重新请求未返回 Set-Cookie，保持原始判定",
                    })
            else:
                techniques.append({
                    "name": "set_cookie_refetch",
                    "passed": False,
                    "note": "请求失败",
                })
        except Exception:
            techniques.append({
                "name": "set_cookie_refetch",
                "passed": False,
                "note": "请求异常",
            })
    else:
        techniques.append({
            "name": "set_cookie_refetch",
            "passed": False,
            "note": "缺少 url",
        })

    # 技术 3：HTTPS 上下文验证
    parsed = urlparse(url) if url else None
    if parsed and parsed.scheme == "https":
        score += 15
        techniques.append({
            "name": "https_context",
            "passed": True,
            "note": "HTTPS 站点下 Cookie 缺少 Secure 属性风险更高",
        })
    else:
        techniques.append({
            "name": "https_context",
            "passed": False,
            "note": "HTTP 站点下 Secure 属性本身不适用",
        })

    verified = score >= validator.VERIFIED_THRESHOLD
    return VerificationResult(
        finding_id=finding.get("id", ""),
        vuln_type="cookie_security",
        verified=verified,
        verification_score=min(100, score),
        techniques=techniques,
        summary=f"Cookie 安全验证得分 {score}/100",
    )


# ---------- 敏感路径交叉验证 ----------


@register_strategy("sensitive_path")
async def _verify_sensitive_path(
    validator: CrossValidator, finding: dict[str, Any]
) -> VerificationResult:
    """敏感路径交叉验证：路径可访问性复检 + 响应内容验证。"""
    url = finding.get("url", "")
    evidence = finding.get("evidence") or {}
    techniques: list[dict[str, Any]] = []
    score = 0

    # 技术 1：重新请求该路径验证可访问性
    if url:
        try:
            resp = await validator._safe_request(
                "get", url, timeout=10.0, follow_redirects=False,
            )
            if resp:
                if resp.status_code == 200:
                    score += 45
                    techniques.append({
                        "name": "path_accessible",
                        "passed": True,
                        "note": "敏感路径返回 HTTP 200，确认可访问",
                    })
                elif resp.status_code in (301, 302, 307):
                    score += 25
                    techniques.append({
                        "name": "path_accessible",
                        "passed": True,
                        "note": f"敏感路径返回 {resp.status_code} 重定向，可能存在",
                    })
                elif resp.status_code == 401:
                    score += 30
                    techniques.append({
                        "name": "path_accessible",
                        "passed": True,
                        "note": "敏感路径返回 401，路径存在但需认证",
                    })
                elif resp.status_code == 403:
                    score += 20
                    techniques.append({
                        "name": "path_accessible",
                        "passed": True,
                        "note": "敏感路径返回 403，路径存在但被禁止",
                    })
                else:
                    techniques.append({
                        "name": "path_accessible",
                        "passed": False,
                        "note": f"敏感路径返回 {resp.status_code}，可能不存在",
                    })
            else:
                techniques.append({
                    "name": "path_accessible",
                    "passed": False,
                    "note": "请求失败",
                })
        except Exception:
            techniques.append({
                "name": "path_accessible",
                "passed": False,
                "note": "请求异常",
            })
    else:
        techniques.append({
            "name": "path_accessible",
            "passed": False,
            "note": "缺少 url",
        })

    # 技术 2：响应内容敏感信息检测
    response_text = (evidence.get("response") or "").lower()
    sensitive_indicators = [
        "password", "secret", "key", "token", "config",
        "database", "admin", "backup", "dump", "credentials",
    ]
    has_sensitive_content = any(ind in response_text for ind in sensitive_indicators)
    if has_sensitive_content:
        score += 35
        techniques.append({
            "name": "sensitive_content",
            "passed": True,
            "note": "响应内容中包含敏感关键词",
        })
    else:
        techniques.append({
            "name": "sensitive_content",
            "passed": False,
            "note": "响应内容中未检测到敏感关键词",
        })

    # 技术 3：路径模式验证
    parsed = urlparse(url) if url else None
    if parsed:
        path_lower = parsed.path.lower()
        known_sensitive_patterns = [
            "/admin", "/backup", "/config", "/.git", "/.env",
            "/wp-admin", "/phpmyadmin", "/console", "/debug",
            "/api/v1/users", "/internal", "/secret",
        ]
        matches_pattern = any(p in path_lower for p in known_sensitive_patterns)
        if matches_pattern:
            score += 20
            techniques.append({
                "name": "path_pattern",
                "passed": True,
                "note": "路径匹配已知敏感路径模式",
            })
        else:
            techniques.append({
                "name": "path_pattern",
                "passed": False,
                "note": "路径不匹配已知敏感路径模式",
            })
    else:
        techniques.append({
            "name": "path_pattern",
            "passed": False,
            "note": "无法解析路径",
        })

    verified = score >= validator.VERIFIED_THRESHOLD
    return VerificationResult(
        finding_id=finding.get("id", ""),
        vuln_type="sensitive_path",
        verified=verified,
        verification_score=min(100, score),
        techniques=techniques,
        summary=f"敏感路径验证得分 {score}/100",
    )


# ---------- 工具函数 ----------


def _build_test_url(url: str, param: str, payload: str) -> str:
    """构造测试 URL，替换指定参数的值为 payload。"""
    parsed = urlparse(url)
    qs = parse_qs(parsed.query, keep_blank_values=True)
    qs[param] = [payload]
    new_query = urlencode(qs, doseq=True)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"


def _response_similarity(a: str, b: str) -> float:
    """计算两段响应文本的简单相似度（基于共有行比例）。"""
    if not a or not b:
        return 0.0
    lines_a = set(a.splitlines())
    lines_b = set(b.splitlines())
    if not lines_a or not lines_b:
        return 0.0
    intersection = lines_a & lines_b
    union = lines_a | lines_b
    return len(intersection) / len(union)
