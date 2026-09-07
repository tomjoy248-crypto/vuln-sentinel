"""Deterministic, authorization-friendly asset inventory normalization."""

from __future__ import annotations

import hashlib
import json
import re
from urllib.parse import urljoin, urlparse
from typing import Any

MAX_INPUT = 2 * 1024 * 1024
URL_RE = re.compile(r"https?://[^\s\"'<>`]+", re.I)
PATH_RE = re.compile(r"(?:fetch|axios\.(?:get|post|put|delete)|url)\s*\(\s*[\"']?([/][^\s\"')]+)", re.I)


def _normal(value: str, base: str = "") -> str | None:
    value = str(value or "").strip()
    if not value:
        return None
    if not value.startswith(("http://", "https://")):
        if value.startswith("/") and base:
            value = urljoin(base, value)
        else:
            value = "https://" + value
    parsed = urlparse(value)
    if not parsed.hostname:
        return None
    return value.split("#", 1)[0].rstrip("/")


def _item(url: str, source: str, owner: str = "unknown", soft: bool = False) -> dict[str, Any]:
    normalized = _normal(url)
    if not normalized:
        raise ValueError("资产地址无效")
    return {"url": normalized, "host": urlparse(normalized).hostname, "source": source, "owner": owner or "unknown", "soft_page": soft, "fingerprint": hashlib.sha256(normalized.encode()).hexdigest()[:16]}


def discover_assets(content: str, source: str = "list", base_url: str = "", owner: str = "unknown") -> list[dict[str, Any]]:
    """Parse domains, URLs, OpenAPI JSON/YAML-like paths, or script contents."""
    if len(content.encode("utf-8")) > MAX_INPUT:
        raise ValueError("资产导入内容不能超过 2MB")
    found: list[dict[str, Any]] = []
    text = content.strip()
    if source == "openapi":
        try:
            doc = json.loads(text)
        except json.JSONDecodeError:
            doc = None
        if isinstance(doc, dict):
            servers = [x.get("url") for x in doc.get("servers", []) if isinstance(x, dict)]
            root = (servers[0] if servers else base_url) or base_url
            for path in (doc.get("paths") or {}):
                if isinstance(path, str):
                    url = _normal(path, root)
                    if url:
                        found.append(_item(url, "openapi", owner))
            for server in servers:
                if server:
                    found.append(_item(server, "openapi-server", owner))
        else:
            for path in re.findall(r"^\s{0,8}(/[^\s:#]+):", text, re.M):
                url = _normal(path, base_url)
                if url:
                    found.append(_item(url, "openapi", owner))
    elif source in {"script", "url"}:
        for url in URL_RE.findall(text):
            found.append(_item(url.rstrip(".,);"), source, owner))
        for path in PATH_RE.findall(text):
            url = _normal(path, base_url)
            if url:
                found.append(_item(url, "script-endpoint", owner))
    else:
        for line in text.splitlines():
            value = line.strip().split(",", 1)[0].strip()
            url = _normal(value)
            if url:
                found.append(_item(url, source, owner))
    unique: dict[str, dict[str, Any]] = {}
    for item in found:
        unique[item["url"].lower()] = item
    return sorted(unique.values(), key=lambda item: item["url"])


def mark_soft_pages(items: list[dict[str, Any]], baseline_body: str, bodies: dict[str, str]) -> list[dict[str, Any]]:
    """Mark pages whose normalized body is indistinguishable from a baseline."""
    def shape(body: str) -> str:
        return re.sub(r"\d+|[a-f0-9]{8,}", "X", (body or "").lower())[:10000]
    baseline = shape(baseline_body)
    for item in items:
        if item["url"] in bodies and baseline and shape(bodies[item["url"]]) == baseline:
            item["soft_page"] = True
            item["soft_page_reason"] = "响应内容与基线页面归一化后相同"
    return items
