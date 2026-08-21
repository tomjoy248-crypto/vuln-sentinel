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
async def test_extract_passive_info_leak_findings():
    findings = main._extract_passive_exposure_findings(
        "https://target.test/",
        [
            {"url": "https://target.test/app.js", "signals": ["source_map", "debug_marker"], "title": "source map + debug"},
            {"url": "https://target.test/page", "signals": ["html_comment"], "title": "html comment"},
        ],
    )

    assert any(item["type"] == "info_leak" for item in findings)
    assert any("信息泄露" in item["name"] for item in findings)


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
async def test_detect_auth_weaknesses_and_bruteforce_protection(monkeypatch):
    def handler(request):
        decoded = urllib.parse.unquote(str(request.url)).lower()
        if decoded.endswith("/login") or "/login?" in decoded:
            return httpx.Response(
                200,
                text="<html><body><form method='post'><input name='username'><input type='password' name='password'></form></body></html>",
            )
        return httpx.Response(404, text="not found")

    client = install_mock_client(monkeypatch, handler)
    try:
        findings = await main.detect_auth_weaknesses("https://target.test")
    finally:
        await client.aclose()

    types = {item["type"] for item in findings}
    assert "auth_weakness" in types
    assert "bruteforce_protection" in types


@pytest.mark.asyncio
async def test_detect_unauthorized_access_on_sensitive_routes(monkeypatch):
    def handler(request):
        decoded = urllib.parse.unquote(str(request.url)).lower()
        if decoded.endswith("/admin") or "/api/user" in decoded:
            return httpx.Response(200, text="Admin dashboard | logout | user center")
        return httpx.Response(404, text="not found")

    client = install_mock_client(monkeypatch, handler)
    try:
        findings = await main.detect_unauthorized_access("https://target.test")
    finally:
        await client.aclose()

    assert findings
    assert any(item["type"] == "unauthorized_access" for item in findings)


@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_detect_api_auth_missing_with_sensitive_json(monkeypatch):
    def handler(request):
        decoded = str(request.url).lower()
        if "/api/me" in decoded:
            return httpx.Response(200, headers={"content-type": "application/json"}, text='{"user_id": 7, "email": "owner@example.test", "role": "user"}')
        return httpx.Response(404, text="not found")

    client = install_mock_client(monkeypatch, handler)
    try:
        findings = await main.detect_api_auth_missing("https://target.test")
    finally:
        await client.aclose()

    assert findings
    assert findings[0]["type"] == "api_auth_missing"
    assert findings[0]["confidence_level"] == "高"


@pytest.mark.asyncio
async def test_run_payload_tests_collects_new_types(monkeypatch):
    deser_sig = next(iter(main.DESER_SIGNATURES))
    cmd_sig = next(iter(main.CMD_EXEC_SIGNATURES))

    def handler(request):
        decoded = urllib.parse.unquote(str(request.url)).lower()
        if "etc/passwd" in decoded:
            return httpx.Response(200, text="root:x:0:0:root:/root:/bin/bash")
        if "169.254.169.254" in decoded or "127.0.0.1" in decoded:
            return httpx.Response(200, text="instance-id\nami-id\nlocal-ipv4")
        if "command" in decoded:
            return httpx.Response(200, text=f"output {cmd_sig}")
        if decoded.endswith('/login'):
            return httpx.Response(200, text="<html><body><form method='post'><input name='username'><input type='password' name='password'></form></body></html>")
        if decoded.endswith('/admin') or '/api/user' in decoded:
            return httpx.Response(200, text='Admin dashboard | logout | user center')
        if decoded.endswith('.xml') or 'application/xml' in str(request.headers.get('content-type', '')).lower():
            return httpx.Response(200, text='xml parser error: DOCTYPE not allowed')
        if 'id=1' in decoded:
            return httpx.Response(200, text='Account profile: Alice | status: active | permissions: read-write | notes: standard user account')
        if 'id=2' in decoded:
            return httpx.Response(200, text='Account profile: Bob | status: active | permissions: read-write | notes: standard user account')
        return httpx.Response(
            200,
            text="<html><body><form method='post'><input name='username'><input type='password' name='password'></form></body></html>",
            headers={"Set-Cookie": f"session={deser_sig}; Path=/"},
        )

    client = install_mock_client(monkeypatch, handler)
    try:
        vulns, results = await main.run_payload_tests(
            "https://target.test/download?file=1",
            [
                {"url": "https://target.test/download?file=1"},
                {"url": "https://target.test/service.xml?id=1"},
                {"url": "https://target.test/app.js", "signals": ["source_map", "debug_marker"], "title": "source map + debug"},
            ],
        )
    finally:
        await client.aclose()

    vuln_types = {item["type"] for item in vulns}
    result_types = {item["type"] for item in results}

    assert "csrf" in vuln_types
    assert "traversal" in vuln_types
    assert "ssrf" in vuln_types
    assert "cmdi" in vuln_types or any(item["type"] == "cmdi" for item in vulns)
    assert "deserialization" in vuln_types or any(item["type"] == "deserialization" for item in vulns)
    assert "xxe" in vuln_types or any(item["type"] == "xxe" for item in vulns)
    assert "idor" in vuln_types or any(item["type"] == "idor" for item in vulns)
    assert "auth_weakness" in vuln_types or any(item["type"] == "auth_weakness" for item in vulns)
    assert "bruteforce_protection" in vuln_types or any(item["type"] == "bruteforce_protection" for item in vulns)
    assert "unauthorized_access" in vuln_types or any(item["type"] == "unauthorized_access" for item in vulns)
    assert "csrf" in result_types
    assert "traversal" in result_types
    assert "ssrf" in result_types
    assert "cmdi" in result_types
    assert "deserialization" in result_types
    assert "xxe" in result_types
    assert "idor" in result_types
    assert "info_leak" in result_types
    assert "auth_weakness" in result_types
    assert "bruteforce_protection" in result_types
    assert "unauthorized_access" in result_types


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


@pytest.mark.asyncio
async def test_detect_command_injection_with_exec_signature(monkeypatch):
    sig = next(iter(main.CMD_EXEC_SIGNATURES))

    def handler(request):
        return httpx.Response(200, text=f"command output {sig}")

    client = install_mock_client(monkeypatch, handler)
    try:
        findings = await main.detect_command_injection("https://target.test/run?command=1", ["command"])
    finally:
        await client.aclose()

    assert findings
    assert any(item["type"] == "cmdi" for item in findings)
    assert any(item["name"] == "命令注入漏洞" for item in findings)


@pytest.mark.asyncio
async def test_detect_deserialization_with_cookie_signature(monkeypatch):
    sig = next(iter(main.DESER_SIGNATURES))

    findings = await main.detect_insecure_deserialization({"Set-Cookie": f"session={sig}; Path=/"}, "https://target.test/")

    assert findings
    assert any(item["type"] == "deserialization" for item in findings)
    assert any("反序列化" in item["name"] for item in findings)


@pytest.mark.asyncio
async def test_detect_xxe_with_xml_probe(monkeypatch):
    def handler(request):
        if request.method == 'POST':
            return httpx.Response(200, text='xml parser error: DOCTYPE not allowed')
        return httpx.Response(200, text='ok')

    client = install_mock_client(monkeypatch, handler)
    try:
        findings = await main.detect_xxe('https://target.test/service.xml?id=1', ['id'])
    finally:
        await client.aclose()

    assert findings
    assert any(item['type'] == 'xxe' for item in findings)
    assert any('XXE' in item['name'] for item in findings)


@pytest.mark.asyncio
async def test_detect_idor_risk_with_adjacent_ids(monkeypatch):
    def handler(request):
        decoded = urllib.parse.unquote(str(request.url)).lower()
        if 'id=1' in decoded:
            return httpx.Response(200, text='Account profile: Alice | status: active | permissions: read-write | notes: standard user account')
        if 'id=2' in decoded:
            return httpx.Response(200, text='Account profile: Bob | status: active | permissions: read-write | notes: standard user account')
        return httpx.Response(200, text='ok')

    client = install_mock_client(monkeypatch, handler)
    try:
        findings = await main.detect_idor_risk('https://target.test/profile?id=1', ['id'])
    finally:
        await client.aclose()

    assert findings
    assert any(item['type'] == 'idor' for item in findings)
    assert any('IDOR' in item['name'] for item in findings)
