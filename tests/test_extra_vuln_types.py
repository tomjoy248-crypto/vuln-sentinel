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


@pytest.mark.asyncio
async def test_detect_directory_traversal_with_passwd_signature(monkeypatch):
    def handler(request):
        decoded = urllib.parse.unquote(str(request.url))
        if "passwd" in decoded or "hosts" in decoded:
            return httpx.Response(200, text="root:x:0:0:root:/root:/bin/bash\nwww-data:x:33:33:www-data:/var/www:/usr/sbin/nologin")
        return httpx.Response(200, text="ok")

    client = install_mock_client(monkeypatch, handler)
    try:
        findings = await main.detect_directory_traversal("https://target.test/download?file=1", ["file"])
    finally:
        await client.aclose()

    assert findings
    assert any(item["type"] == "traversal" for item in findings)
    assert any(item["name"] == "目录遍历漏洞" for item in findings)


@pytest.mark.asyncio
async def test_detect_ssrf_enhanced_with_metadata_signature(monkeypatch):
    def handler(request):
        decoded = urllib.parse.unquote(str(request.url))
        if "169.254.169.254" in decoded or "127.0.0.1" in decoded:
            return httpx.Response(200, text="instance-id\nami-id\nlocal-ipv4")
        return httpx.Response(200, text="ok")

    client = install_mock_client(monkeypatch, handler)
    try:
        findings = await main.detect_ssrf_enhanced("https://target.test/fetch?url=1", ["url"])
    finally:
        await client.aclose()

    assert findings
    assert any(item["type"] == "ssrf" for item in findings)
    assert any(item["name"] == "SSRF 漏洞（云元数据访问）" for item in findings)


@pytest.mark.asyncio
async def test_detect_csrf_forms_missing_token(monkeypatch):
    def handler(request):
        return httpx.Response(
            200,
            text="<html><body><form method='post'><input name='email'><input type='password' name='password'></form></body></html>",
        )

    client = install_mock_client(monkeypatch, handler)
    try:
        findings = await main.detect_csrf_forms("https://target.test/login")
    finally:
        await client.aclose()

    assert len(findings) == 1
    assert findings[0]["type"] == "csrf"
    assert findings[0]["name"] == "CSRF 风险"


@pytest.mark.asyncio
async def test_run_payload_tests_collects_new_types(monkeypatch):
    def handler(request):
        decoded = urllib.parse.unquote(str(request.url))
        if "etc/passwd" in decoded:
            return httpx.Response(200, text="root:x:0:0:root:/root:/bin/bash")
        if "169.254.169.254" in decoded or "127.0.0.1" in decoded:
            return httpx.Response(200, text="instance-id\nami-id\nlocal-ipv4")
        return httpx.Response(
            200,
            text="<html><body><form method='post'><input name='username'><input type='password' name='password'></form></body></html>",
        )

    client = install_mock_client(monkeypatch, handler)
    try:
        vulns, results = await main.run_payload_tests(
            "https://target.test/download?file=1",
            [{"url": "https://target.test/download?file=1"}],
        )
    finally:
        await client.aclose()

    vuln_types = {item["type"] for item in vulns}
    result_types = {item["type"] for item in results}

    assert "csrf" in vuln_types
    assert "traversal" in vuln_types
    assert "ssrf" in vuln_types
    assert "csrf" in result_types
    assert "traversal" in result_types
    assert "ssrf" in result_types


@pytest.mark.asyncio
async def test_generate_fix_patch_supports_apache_fallback():
    patch = main._generate_fix_patch([], "apache")
    assert "平台: APACHE" in patch
    assert "Header set X-Content-Type-Options" in patch
    assert "暂未实现" not in patch


@pytest.mark.asyncio
async def test_detect_sqli_and_time_based_paths(monkeypatch):
    def handler(request):
        decoded = urllib.parse.unquote(str(request.url)).lower()
        if "sleep(0.01)" in decoded or "union" in decoded or "or '1'='1" in decoded:
            return httpx.Response(200, text="SQL syntax error near 'union' on database")
        return httpx.Response(200, text="ok")

    client = install_mock_client(monkeypatch, handler)
    monkeypatch.setattr(main, "sanitize_url", lambda value: value)
    try:
        findings = await main.detect_sqli("https://target.test/search?q=1", ["q"])
        timed = await main.detect_time_based_sqli("https://target.test/search?q=1' AND SLEEP(0.01) --", threshold=0.001)
    finally:
        await client.aclose()

    assert any(item["type"] == "sqli" for item in findings)
    assert timed["vulnerable"] is True
    assert timed["method"] == "simulated"
