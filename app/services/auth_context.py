"""Ephemeral parsing of authorized authentication material.

This module deliberately returns request headers only for the current call.
Callers must not persist the returned context or include it in audit details.
"""

from __future__ import annotations

import json
import re
from typing import Any

MAX_IMPORT_BYTES = 256 * 1024
MAX_HEADERS = 20
SENSITIVE = {"authorization", "cookie", "set-cookie", "proxy-authorization"}
ALLOWED = {
    "accept", "content-type", "authorization", "cookie", "x-access-token",
    "x-api-key", "x-auth-token", "x-csrf-token", "x-session-id", "x-tenant-id",
    "x-user-id", "origin", "referer",
}


def _redacted(name: str, value: str) -> str:
    if name.lower() in SENSITIVE:
        return "[REDACTED]"
    return value[:80]


def _headers(raw: dict[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for key, value in raw.items():
        name = str(key).strip()
        if not name or name.lower() not in ALLOWED:
            continue
        text = str(value).strip()
        if len(name) > 128 or len(text) > 4096:
            raise ValueError("认证请求头长度超出限制")
        result[name] = text
    if len(result) > MAX_HEADERS:
        raise ValueError("认证请求头不能超过 20 个")
    return result


def _parse_http(text: str) -> tuple[str | None, dict[str, str]]:
    lines = text.replace("\r\n", "\n").split("\n")
    headers: dict[str, str] = {}
    for line in lines[1:]:
        if not line.strip():
            break
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        headers[key.strip()] = value.strip()
    first = lines[0].split()
    url = first[1] if len(first) >= 2 and first[0].upper() in {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"} else None
    return url, _headers(headers)


def parse_auth_context(content: str, kind: str = "auto") -> dict[str, Any]:
    """Parse a cookie/token/header/HAR import without retaining raw content."""
    if not isinstance(content, str) or len(content.encode("utf-8")) > MAX_IMPORT_BYTES:
        raise ValueError("认证导入内容不能超过 256KB")
    text = content.strip()
    if not text:
        raise ValueError("认证导入内容不能为空")
    headers: dict[str, str] = {}
    url: str | None = None
    detected = kind.lower().strip()
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        obj = None
    if isinstance(obj, dict):
        if isinstance(obj.get("log"), dict):
            entries = obj["log"].get("entries") or []
            if not entries:
                raise ValueError("HAR 文件没有请求记录")
            request = entries[0].get("request") or {}
        else:
            request = obj.get("request") if isinstance(obj.get("request"), dict) else obj
        if isinstance(request, dict):
            url = str(request.get("url") or "") or None
            raw_headers = request.get("headers") or request.get("header") or {}
            if isinstance(raw_headers, list):
                raw_headers = {item.get("name"): item.get("value", "") for item in raw_headers if isinstance(item, dict) and item.get("name")}
            if isinstance(raw_headers, dict):
                headers.update(_headers(raw_headers))
            detected = "har" if obj.get("log") else (detected if detected != "auto" else "request-json")
    elif "\n" in text and re.match(r"^(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s", text, re.I):
        url, headers = _parse_http(text)
        detected = "http" if detected == "auto" else detected
    elif ":" in text and text.split(":", 1)[0].lower() in {"cookie", "authorization", "x-api-key", "x-access-token", "x-auth-token"}:
        key, value = text.split(":", 1)
        headers = _headers({key: value.strip()})
        detected = "header" if detected == "auto" else detected
    else:
        headers = {"Authorization": text if text.lower().startswith("bearer ") else f"Bearer {text}"}
        headers = _headers(headers)
        detected = "token" if detected == "auto" else detected
    if not headers:
        raise ValueError("未找到可用的认证头")
    return {
        "headers": headers,
        "url": url,
        "kind": detected,
        "header_summary": {key: _redacted(key, value) for key, value in headers.items()},
        "in_memory_only": True,
    }
