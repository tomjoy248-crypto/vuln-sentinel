from app.plugins import ScanContext
from app.plugins.builtin import (
    CSPPolicyWeaknessDetector,
    DirectoryListingDetector,
    PassiveExposureDetector,
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
