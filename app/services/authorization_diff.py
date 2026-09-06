"""Safe, read-only comparison of two authorized account contexts."""

from __future__ import annotations

import hashlib
import json
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
_SECRET_KEY_PATTERN = re.compile(
    r"(?i)^(authorization|cookie|set-cookie|password|passwd|secret|token|api[_-]?key|email)$"
)


def _redact_json(value: Any) -> Any:
    """Redact sensitive JSON values before they become evidence text."""
    if isinstance(value, dict):
        return {
            str(key): "[REDACTED]"
            if _SECRET_KEY_PATTERN.search(str(key))
            else _redact_json(child)
            for key, child in value.items()
        }
    if isinstance(value, list):
        return [_redact_json(child) for child in value[:100]]
    return value


def _redact_preview(text: str) -> str:
    """Remove common credential and personal-data values from evidence."""
    try:
        parsed = json.loads(text)
    except (TypeError, ValueError, json.JSONDecodeError):
        pass
    else:
        text = json.dumps(_redact_json(parsed), ensure_ascii=False, separators=(",", ":"))
    text = _SECRET_PATTERN.sub(r"\1\2[REDACTED]", text)
    return re.sub(r"(?i)([?&](?:token|key|secret|password)=)[^&\s]+", r"\1[REDACTED]", text)


def _json_keys(body: bytes) -> set[str]:
    """Return bounded JSON field paths without exposing field values."""
    try:
        value = json.loads(body.decode("utf-8", errors="replace"))
    except (TypeError, ValueError, json.JSONDecodeError):
        return set()

    keys: set[str] = set()

    def walk(item: Any, prefix: str = "") -> None:
        if isinstance(item, dict):
            for raw_key, child in list(item.items())[:100]:
                key = str(raw_key)[:80]
                path = f"{prefix}.{key}" if prefix else key
                keys.add(path)
                walk(child, path)
        elif isinstance(item, list):
            for child in item[:20]:
                walk(child, f"{prefix}[]" if prefix else "[]")

    walk(value)
    return keys


def _snapshot(response: httpx.Response, body: bytes, truncated: bool) -> dict[str, Any]:
    text = _redact_preview(body.decode("utf-8", errors="replace"))
    return {
        "status_code": response.status_code,
        "content_length": len(body),
        "body_truncated": truncated,
        "body_digest": _digest(text),
        "body_preview": text[:240],
        "json_keys": sorted(_json_keys(body))[:200],
        "headers": {
            key.lower(): _redact_preview(response.headers.get(key, ""))
            for key in ("content-type", "location", "cache-control", "www-authenticate")
            if response.headers.get(key) is not None
        },
    }


async def _bounded_get(
    client: httpx.AsyncClient, url: str, headers: dict[str, str]
) -> tuple[httpx.Response, bytes, bool]:
    """Read at most the configured evidence size from a target response."""
    async with client.stream("GET", url, headers=headers) as response:
        body = bytearray()
        truncated = False
        async for chunk in response.aiter_bytes():
            remaining = MAX_RESPONSE_BYTES - len(body)
            if remaining <= 0:
                truncated = True
                break
            body.extend(chunk[:remaining])
            if len(chunk) > remaining:
                truncated = True
                break
        return response, bytes(body), truncated


async def compare_authorized_contexts(
    url: str,
    baseline_headers: dict[str, str],
    comparison_headers: dict[str, str],
) -> dict[str, Any]:
    """Issue bounded GET requests and describe observable permission differences."""
    timeout = httpx.Timeout(10.0, connect=5.0)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=False) as client:
        baseline, baseline_body, baseline_truncated = await _bounded_get(
            client, url, baseline_headers
        )
        comparison, comparison_body, comparison_truncated = await _bounded_get(
            client, url, comparison_headers
        )

    first = _snapshot(baseline, baseline_body, baseline_truncated)
    second = _snapshot(comparison, comparison_body, comparison_truncated)
    status_diff = first["status_code"] != second["status_code"]
    body_diff = first["body_digest"] != second["body_digest"]
    baseline_keys = set(first["json_keys"])
    comparison_keys = set(second["json_keys"])
    json_key_diff = {
        "only_in_baseline": sorted(baseline_keys - comparison_keys)[:100],
        "only_in_comparison": sorted(comparison_keys - baseline_keys)[:100],
    }
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
        "json_key_diff": json_key_diff,
        "evidence_truncated": baseline_truncated or comparison_truncated,
        "conclusion": conclusion,
        "severity": severity,
        "evidence": "仅保留状态码、响应摘要和短预览，不保存认证请求头",
    }
