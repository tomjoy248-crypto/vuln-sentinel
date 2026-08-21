from __future__ import annotations

import os
import sys
import urllib.parse

import httpx
import pytest

os.environ.setdefault("DB_DIR", "/tmp/v11-test")
os.environ.setdefault("DB_NAME", "test.db")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import main  # noqa: E402


def install_mock_client(monkeypatch, handler):
    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    monkeypatch.setattr(main, "get_httpx_client", lambda: client)
    return client


@pytest.mark.asyncio
async def test_detect_ssti_with_rendered_marker(monkeypatch):
    def handler(request):
        decoded = urllib.parse.unquote(str(request.url))
        if "?" in decoded:
            return httpx.Response(200, text="hello vulnsentinelprobe")
        return httpx.Response(200, text="baseline page")

    client = install_mock_client(monkeypatch, handler)
    try:
        findings = await main.detect_ssti("https://target.test/search", ["q"])
    finally:
        await client.aclose()

    assert len(findings) == 1
    assert findings[0]["type"] == "ssti"
    assert findings[0]["name"] == "模板注入漏洞（SSTI）"


@pytest.mark.asyncio
async def test_detect_open_redirect_with_location_header(monkeypatch):
    def handler(request):
        decoded = urllib.parse.unquote(str(request.url))
        if "redirect-check" in decoded:
            return httpx.Response(302, headers={"Location": "https://example.com/redirect-check"})
        return httpx.Response(200, text="ok")

    client = install_mock_client(monkeypatch, handler)
    try:
        findings = await main.detect_open_redirect("https://target.test/login", ["next"])
    finally:
        await client.aclose()

    assert len(findings) == 1
    assert findings[0]["type"] == "open_redirect"
    assert findings[0]["name"] == "开放重定向漏洞"
