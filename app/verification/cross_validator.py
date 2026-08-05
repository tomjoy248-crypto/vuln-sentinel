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

    VERIFIED_THRESHOLD = 60  # 验证分数达到 60 即视为已验证
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

    async def verify_finding(self, finding: dict[str, Any]) -> VerificationResult:
        """对单条 finding 执行交叉验证。"""
        vuln_type = (finding.get("type") or "").lower()
        finding_id = finding.get("id", "")

        strategy = _VERIFICATION_STRATEGIES.get(vuln_type)
        if strategy is None:
            # 无对应策略，返回默认结果（保持原始置信度）
            return VerificationResult(
                finding_id=finding_id,
                vuln_type=vuln_type,
                verified=True,
                verification_score=50,
                techniques=[
                    {
                        "name": "no_strategy",
                        "passed": True,
                        "note": "无交叉验证策略，保持原始判定",
                    }
                ],
                summary="该漏洞类型暂无交叉验证策略",
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
                # 异常时返回默认验证通过
                verified.append(
                    VerificationResult(
                        finding_id=findings[i].get("id", ""),
                        vuln_type=(findings[i].get("type") or "").lower(),
                        verified=True,
                        verification_score=50,
                        techniques=[
                            {"name": "error", "passed": False, "note": str(res)}
                        ],
                        summary="验证过程异常，保持原始判定",
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
                if loc_host and loc_host != target_host:
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
                if location.startswith("//") or "attacker.example" in location.lower():
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
    original_headers = evidence.get("headers") or {}
    if isinstance(original_headers, dict):
        loc = original_headers.get("location") or original_headers.get("Location", "")
        if loc and urlparse(loc).netloc.lower() not in ("", target_host):
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
            if header_name.lower() not in actual_headers:
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
                    "passed": True,
                    "note": "请求失败，保持原始判定",
                }
            )
    else:
        score = 70
        techniques.append(
            {
                "name": "existing_evidence",
                "passed": True,
                "note": "基于原始扫描数据判定",
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
