from app.plugins import ScanContext
from app.plugins.builtin import (
    BackupExposureDetector,
    ApiSurfaceExposureDetector,
    CSPPolicyWeaknessDetector,
    DirectoryListingDetector,
    DiscoverySurfaceDetector,
    PassiveExposureDetector,
    WellKnownExposureDetector,
    SensitiveEndpointDetector,
    ServerExposureDetector,
    TraceMethodDetector,
)


def test_directory_listing_detector_finds_index_pages():
    detector = DirectoryListingDetector()
    context = ScanContext(
        url="https://example.com/files/",
        headers={"Content-Type": "text/html; charset=utf-8"},
        body="<html><head><title>Index of /files/</title></head><body><h1>Index of /files/</h1><a href='../'>Parent Directory</a></body></html>",
    )

    findings = __import__("asyncio").run(detector.detect(context))

    assert len(findings) == 1
    assert findings[0].type == "directory_listing"
    assert findings[0].severity == "medium"


def test_trace_method_detector_flags_allow_trace():
    detector = TraceMethodDetector()
    context = ScanContext(
        url="https://example.com/",
        headers={"Allow": "GET, HEAD, OPTIONS, TRACE"},
        body="",
    )

    findings = __import__("asyncio").run(detector.detect(context))

    assert len(findings) == 1
    assert findings[0].type == "trace_method"
    assert findings[0].title == "HTTP TRACE 方法可用"


def test_server_exposure_detector_flags_version_headers():
    detector = ServerExposureDetector()
    context = ScanContext(
        url="https://example.com/",
        headers={
            "Server": "nginx/1.24.0 (Ubuntu)",
            "X-Powered-By": "PHP/8.2.12",
        },
        body="",
    )

    findings = __import__("asyncio").run(detector.detect(context))

    assert {finding.title for finding in findings} == {
        "Server 头泄露",
        "X-Powered-By 信息泄露",
    }
    assert all(finding.type == "server_exposure" for finding in findings)
    assert all(finding.confidence == "high" for finding in findings)


def test_server_exposure_detector_ignores_generic_cdn_headers():
    detector = ServerExposureDetector()
    context = ScanContext(
        url="https://example.com/",
        headers={"Server": "cloudflare"},
        body="",
    )

    findings = __import__("asyncio").run(detector.detect(context))

    assert findings == []


def test_csp_policy_weakness_detector_flags_unsafe_inline_and_wildcard():
    detector = CSPPolicyWeaknessDetector()
    context = ScanContext(
        url="https://example.com/",
        headers={
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.example.com; "
                "frame-ancestors *; "
                "object-src 'self'"
            )
        },
        body="",
    )

    findings = __import__("asyncio").run(detector.detect(context))

    assert len(findings) == 1
    assert findings[0].type == "csp_weakness"
    assert findings[0].severity == "medium"
    assert "unsafe-inline" in findings[0].evidence.extra["issues"][0]


def test_csp_policy_weakness_detector_ignores_strict_policy():
    detector = CSPPolicyWeaknessDetector()
    context = ScanContext(
        url="https://example.com/",
        headers={
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self'; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "frame-ancestors 'none'"
            )
        },
        body="",
    )

    findings = __import__("asyncio").run(detector.detect(context))

    assert findings == []


def test_passive_exposure_detector_flags_source_map_and_debug_markers():
    detector = PassiveExposureDetector()
    context = ScanContext(
        url="https://example.com/app.js",
        headers={},
        body=(
            "/*# sourceMappingURL=app.js.map */\n"
            "console.log('debug');\n"
            "Traceback (most recent call last): ValueError"
        ),
    )

    findings = __import__("asyncio").run(detector.detect(context))

    assert {finding.title for finding in findings} == {
        "暴露源码映射文件",
        "调试信息泄露",
    }
    assert all(finding.type == "info_leak" for finding in findings)
    assert any(finding.severity == "high" for finding in findings)


def test_api_surface_exposure_detector_flags_route_references():
    detector = ApiSurfaceExposureDetector()
    context = ScanContext(
        url="https://example.com/",
        headers={},
        body=(
            "<html><script>"
            "fetch('/api/v1/users');"
            "axios.get('/api/admin/audit');"
            "const schema='/graphql';"
            "</script></html>"
        ),
    )

    findings = __import__("asyncio").run(detector.detect(context))

    assert len(findings) == 1
    assert findings[0].type == "api_surface_exposure"
    assert findings[0].severity == "medium"
    assert "/api/v1/users" in findings[0].evidence.extra["matched_routes"]
    assert "/api/admin/audit" in findings[0].evidence.extra["matched_routes"]


def test_sensitive_endpoint_detector_flags_public_ops_endpoints(monkeypatch):
    detector = SensitiveEndpointDetector()

    def handler(request):
        path = request.url.path
        if path == "/metrics":
            return __import__("httpx").Response(200, text="# HELP app_requests_total\n# TYPE app_requests_total counter\n")
        if path == "/actuator/health":
            return __import__("httpx").Response(200, text='{"status":"UP","components":{"db":{"status":"UP"}}}')
        return __import__("httpx").Response(403, text="forbidden")

    client = __import__("httpx").AsyncClient(
        transport=__import__("httpx").MockTransport(handler)
    )
    monkeypatch.setattr("app.plugins.builtin.httpx.AsyncClient", lambda *args, **kwargs: client)

    try:
        findings = __import__("asyncio").run(
            detector.detect(
                ScanContext(
                    url="https://example.com/",
                    headers={},
                    body="",
                )
            )
        )
    finally:
        __import__("asyncio").run(client.aclose())

    assert {finding.title for finding in findings} == {
        "暴露 Prometheus 指标端点",
        "暴露 Spring Boot Actuator 健康端点",
    }
    assert all(finding.type == "exposed_endpoint" for finding in findings)


def test_sensitive_endpoint_detector_ignores_protected_endpoints(monkeypatch):
    detector = SensitiveEndpointDetector()

    def handler(_request):
        return __import__("httpx").Response(403, text="forbidden")

    client = __import__("httpx").AsyncClient(
        transport=__import__("httpx").MockTransport(handler)
    )
    monkeypatch.setattr("app.plugins.builtin.httpx.AsyncClient", lambda *args, **kwargs: client)

    try:
        findings = __import__("asyncio").run(
            detector.detect(
                ScanContext(
                    url="https://example.com/",
                    headers={},
                    body="",
                )
            )
        )
    finally:
        __import__("asyncio").run(client.aclose())

    assert findings == []


def test_backup_exposure_detector_flags_dump_and_backup_files(monkeypatch):
    detector = BackupExposureDetector()

    def handler(request):
        path = request.url.path
        if path == "/backup.sql":
            return __import__("httpx").Response(
                200,
                text="-- MySQL dump\nCREATE TABLE users (id INT);\nINSERT INTO users VALUES (1);",
            )
        if path == "/config.bak":
            return __import__("httpx").Response(
                200,
                text="DATABASE_URL=postgres://user:pass@db.local/app\nJWT_SECRET=supersecret",
            )
        return __import__("httpx").Response(403, text="forbidden")

    client = __import__("httpx").AsyncClient(
        transport=__import__("httpx").MockTransport(handler)
    )
    monkeypatch.setattr("app.plugins.builtin.httpx.AsyncClient", lambda *args, **kwargs: client)

    try:
        findings = __import__("asyncio").run(
            detector.detect(
                ScanContext(
                    url="https://example.com/",
                    headers={},
                    body="",
                )
            )
        )
    finally:
        __import__("asyncio").run(client.aclose())

    assert {finding.title for finding in findings} == {
        "数据库备份文件暴露",
        "配置备份文件暴露",
    }
    assert all(finding.type == "backup_exposure" for finding in findings)


def test_backup_exposure_detector_ignores_forbidden_files(monkeypatch):
    detector = BackupExposureDetector()

    def handler(_request):
        return __import__("httpx").Response(403, text="forbidden")

    client = __import__("httpx").AsyncClient(
        transport=__import__("httpx").MockTransport(handler)
    )
    monkeypatch.setattr("app.plugins.builtin.httpx.AsyncClient", lambda *args, **kwargs: client)

    try:
        findings = __import__("asyncio").run(
            detector.detect(
                ScanContext(
                    url="https://example.com/",
                    headers={},
                    body="",
                )
            )
        )
    finally:
        __import__("asyncio").run(client.aclose())

    assert findings == []


def test_discovery_surface_detector_flags_robots_and_sitemap_leaks(monkeypatch):
    detector = DiscoverySurfaceDetector()

    robots = (
        "User-agent: *\n"
        "Disallow: /admin\n"
        "Disallow: /backup.sql\n"
        "Disallow: /internal/console\n"
        "Sitemap: https://example.com/sitemap.xml\n"
    )
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        "<urlset>"
        "<url><loc>https://example.com/admin</loc></url>"
        "<url><loc>https://example.com/debug</loc></url>"
        "<url><loc>https://example.com/internal/report</loc></url>"
        "</urlset>"
    )

    def handler(request):
        path = request.url.path
        if path == "/robots.txt":
            return __import__("httpx").Response(200, text=robots)
        if path == "/sitemap.xml":
            return __import__("httpx").Response(200, text=sitemap)
        return __import__("httpx").Response(404, text="not found")

    client = __import__("httpx").AsyncClient(
        transport=__import__("httpx").MockTransport(handler)
    )
    monkeypatch.setattr("app.plugins.builtin.httpx.AsyncClient", lambda *args, **kwargs: client)

    try:
        findings = __import__("asyncio").run(
            detector.detect(
                ScanContext(
                    url="https://example.com/",
                    headers={},
                    body="",
                )
            )
        )
    finally:
        __import__("asyncio").run(client.aclose())

    assert {finding.title for finding in findings} == {
        "robots.txt 暴露敏感路径",
        "sitemap.xml 暴露敏感页面",
    }
    assert all(finding.type == "discovery_exposure" for finding in findings)


def test_discovery_surface_detector_ignores_empty_or_blocked_files(monkeypatch):
    detector = DiscoverySurfaceDetector()

    def handler(_request):
        return __import__("httpx").Response(403, text="forbidden")

    client = __import__("httpx").AsyncClient(
        transport=__import__("httpx").MockTransport(handler)
    )
    monkeypatch.setattr("app.plugins.builtin.httpx.AsyncClient", lambda *args, **kwargs: client)

    try:
        findings = __import__("asyncio").run(
            detector.detect(
                ScanContext(
                    url="https://example.com/",
                    headers={},
                    body="",
                )
            )
        )
    finally:
        __import__("asyncio").run(client.aclose())

    assert findings == []


def test_well_known_detector_flags_internal_openid_metadata(monkeypatch):
    detector = WellKnownExposureDetector()

    openid = {
        "issuer": "https://auth.example.com",
        "authorization_endpoint": "https://auth.example.com/admin/login",
        "token_endpoint": "https://10.0.0.8/token",
        "jwks_uri": "https://auth.example.com/.well-known/jwks.json",
    }

    def handler(request):
        if request.url.path == "/.well-known/openid-configuration":
            return __import__("httpx").Response(200, json=openid)
        if request.url.path == "/.well-known/security.txt":
            return __import__("httpx").Response(404, text="not found")
        return __import__("httpx").Response(404, text="not found")

    client = __import__("httpx").AsyncClient(
        transport=__import__("httpx").MockTransport(handler)
    )
    monkeypatch.setattr("app.plugins.builtin.httpx.AsyncClient", lambda *args, **kwargs: client)

    try:
        findings = __import__("asyncio").run(
            detector.detect(
                ScanContext(
                    url="https://example.com/",
                    headers={},
                    body="",
                )
            )
        )
    finally:
        __import__("asyncio").run(client.aclose())

    assert len(findings) == 1
    assert findings[0].type == "well_known_exposure"
    assert findings[0].severity == "high"
    assert "internal_host" in findings[0].evidence.extra["matched_signals"]


def test_well_known_detector_ignores_blocked_endpoints(monkeypatch):
    detector = WellKnownExposureDetector()

    def handler(_request):
        return __import__("httpx").Response(403, text="forbidden")

    client = __import__("httpx").AsyncClient(
        transport=__import__("httpx").MockTransport(handler)
    )
    monkeypatch.setattr("app.plugins.builtin.httpx.AsyncClient", lambda *args, **kwargs: client)

    try:
        findings = __import__("asyncio").run(
            detector.detect(
                ScanContext(
                    url="https://example.com/",
                    headers={},
                    body="",
                )
            )
        )
    finally:
        __import__("asyncio").run(client.aclose())

    assert findings == []
