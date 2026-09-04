"""持久化 HTTP 请求历史，并提供受限的安全重放能力。"""

from __future__ import annotations

import ipaddress
import json
import socket
from typing import Any
from urllib.parse import urlparse

import httpx

from app.core.sanitization import redact_sensitive_data
from app.db.session import get_db

MAX_BODY = 64 * 1024
MAX_RESPONSE = 256 * 1024
ALLOWED_METHODS = {"GET", "HEAD", "POST"}
SENSITIVE_HEADERS = {"authorization", "cookie", "set-cookie", "proxy-authorization"}


def _safe_headers(headers: dict[str, Any] | None) -> dict[str, str]:
    result: dict[str, str] = {}
    for key, value in (headers or {}).items():
        name = str(key).strip()
        if not name or len(name) > 128:
            continue
        result[name] = "***REDACTED***" if name.lower() in SENSITIVE_HEADERS else str(value)[:4096]
    return result


def _safe_url(url: str) -> str:
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("仅支持 http 或 https 地址")
    if parsed.username or parsed.password:
        raise ValueError("地址不能包含账号或密码")
    host = parsed.hostname
    try:
        addresses = [ipaddress.ip_address(host)]
    except ValueError:
        try:
            addresses = [ipaddress.ip_address(item[4][0]) for item in socket.getaddrinfo(host, None)]
        except socket.gaierror as exc:
            raise ValueError("目标域名无法解析") from exc
    if any(addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_reserved or addr.is_multicast for addr in addresses):
        raise ValueError("为防止服务端请求伪造，不允许访问内网或保留地址")
    return url.strip()


def save_request(user_id: int, method: str, url: str, headers: dict[str, Any] | None = None, body: str = "") -> int:
    method = method.upper().strip()
    if method not in ALLOWED_METHODS:
        raise ValueError("仅支持 GET、HEAD、POST 请求")
    safe_url = _safe_url(url)
    if len(body) > MAX_BODY:
        raise ValueError("请求体不能超过 64KB")
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO request_history (user_id, method, url, headers_json, body, created_at) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
        (user_id, method, safe_url, json.dumps(_safe_headers(headers), ensure_ascii=False), body),
    )
    conn.commit()
    row_id = int(cur.lastrowid)
    conn.close()
    return row_id


def list_requests(user_id: int, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
    conn = get_db()
    rows = conn.execute(
        "SELECT id, method, url, headers_json, body, response_status, response_headers_json, response_preview, created_at, replayed_at FROM request_history WHERE user_id=? ORDER BY id DESC LIMIT ? OFFSET ?",
        (user_id, limit, offset),
    ).fetchall()
    conn.close()
    return [{"id": r["id"], "method": r["method"], "url": r["url"], "headers": json.loads(r["headers_json"] or "{}"), "body": r["body"] or "", "response_status": r["response_status"], "response_headers": json.loads(r["response_headers_json"] or "{}"), "response_preview": r["response_preview"] or "", "created_at": r["created_at"], "replayed_at": r["replayed_at"]} for r in rows]


async def replay_request(user_id: int, request_id: int) -> dict[str, Any]:
    conn = get_db()
    row = conn.execute("SELECT * FROM request_history WHERE id=? AND user_id=?", (request_id, user_id)).fetchone()
    conn.close()
    if not row:
        raise LookupError("请求不存在或无权访问")
    url = _safe_url(row["url"])
    headers = json.loads(row["headers_json"] or "{}")
    headers = {k: v for k, v in headers.items() if k.lower() not in SENSITIVE_HEADERS}
    async with httpx.AsyncClient(timeout=httpx.Timeout(10.0, connect=3.0), follow_redirects=False) as client:
        response = await client.request(row["method"], url, headers=headers, content=(row["body"] or "")[:MAX_BODY])
    preview = response.content[:MAX_RESPONSE].decode(response.encoding or "utf-8", errors="replace")
    safe_response_headers = _safe_headers(dict(response.headers))
    conn = get_db()
    conn.execute("UPDATE request_history SET response_status=?, response_headers_json=?, response_preview=?, replayed_at=CURRENT_TIMESTAMP WHERE id=? AND user_id=?", (response.status_code, json.dumps(safe_response_headers, ensure_ascii=False), preview, request_id, user_id))
    conn.commit()
    conn.close()
    return {"id": request_id, "status_code": response.status_code, "headers": safe_response_headers, "body_preview": redact_sensitive_data(preview)}
