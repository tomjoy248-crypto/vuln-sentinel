"""Safe, read-only comparison of two authorized account contexts."""

from __future__ import annotations

import hashlib
import re
from typing import Any

import httpx

MAX_RESPONSE_BYTES = 256 * 1024


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:16]


_SECRET_PATTERN = re.compile(
    r"(?i)(authorization|cookie|set-cookie|password|passwd|secret|token|api[_-]?key|email)"
    r"(\s*[:=]\s*)([^\s,;&]+)"
)


def _redact_preview(text: str) -> str:
    """Remove common credential and personal-data values from evidence."""
    text = _SECRET_PATTERN.sub(r"\1\2[REDACTED]", text)
    return re.sub(r"(?i)([?&](?:token|key|secret|password)=)[^&\s]+", r"\1[REDACTED]", text)


def _snapshot(response: httpx.Response, body: bytes) -> dict[str, Any]:
    text = _redact_preview(body.decode("utf-8", errors="replace"))
    return {
        "status_code": response.status_code,
        "content_length": len(body),
        "body_digest": _digest(text),
        "body_preview": text[:240],
        "headers": {
            key.lower(): _redact_preview(response.headers.get(key, ""))
            for key in ("content-type", "location", "cache-control", "www-authenticate")
            if response.headers.get(key) is not None
        },
    }


async def _bounded_get(
    client: httpx.AsyncClient, url: str, headers: dict[str, str]
) -> tuple[httpx.Response, bytes]:
    """Read at most the configured evidence size from a target response."""
    async with client.stream("GET", url, headers=headers) as response:
        body = await response.aread()
        if len(body) > MAX_RESPONSE_BYTES:
            body = body[:MAX_RESPONSE_BYTES]
        return response, body


async def compare_authorized_contexts(
    url: str,
    baseline_headers: dict[str, str],
    comparison_headers: dict[str, str],
) -> dict[str, Any]:
    """Issue bounded GET requests and describe observable permission differences."""
    timeout = httpx.Timeout(10.0, connect=5.0)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=False) as client:
        baseline, baseline_body = await _bounded_get(client, url, baseline_headers)
        comparison, comparison_body = await _bounded_get(client, url, comparison_headers)

    first = _snapshot(baseline, baseline_body)
    second = _snapshot(comparison, comparison_body)
    status_diff = first["status_code"] != second["status_code"]
    body_diff = first["body_digest"] != second["body_digest"]
    both_success = 200 <= first["status_code"] < 300 and 200 <= second["status_code"] < 300
    if both_success and body_diff:
        conclusion = "两个授权身份返回内容不同，发现权限相关差异，建议人工确认数据边界"
        severity = "medium"
    elif both_success and not body_diff:
        conclusion = "两个授权身份均可访问且返回内容一致，未观察到权限差异"
        severity = "info"
    elif status_diff:
        conclusion = "两个授权身份的访问结果不同，存在访问控制差异"
        severity = "info"
    else:
        conclusion = "两个授权身份均未获得成功响应，无法判断权限差异"
        severity = "low"
    return {
        "url": url,
        "method": "GET",
        "baseline": first,
        "comparison": second,
        "status_diff": status_diff,
        "body_diff": body_diff,
        "conclusion": conclusion,
        "severity": severity,
        "evidence": "仅保留状态码、响应摘要和短预览，不保存认证请求头",
    }
