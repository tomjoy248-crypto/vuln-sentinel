from app.plugins import ScanContext
from app.plugins.builtin import (
    BackupExposureDetector,
    ApiSurfaceExposureDetector,
    CloudStorageExposureDetector,
    CloudStorageSecretExposureDetector,
    CSPPolicyWeaknessDetector,
    DirectoryListingDetector,
    DiscoverySurfaceDetector,
    FrontendSupplyChainDetector,
    LoginSurfaceDetector,
    OAuthSurfaceDetector,
    PassiveExposureDetector,
    ProtectedRouteExposureDetector,
    SRIIntegrityDetector,
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


def test_sri_integrity_detector_flags_cross_origin_script_without_integrity():
    detector = SRIIntegrityDetector()
    context = ScanContext(
        url="https://example.com/",
        headers={},
        body='<html><script src="https://cdn.example.com/lib.js"></script></html>',
    )

    findings = __import__("asyncio").run(detector.detect(context))

    assert len(findings) == 1
    assert findings[0].type == "sri_missing"
    assert findings[0].severity == "low"
    assert findings[0].evidence.extra["missing_resources"] == [
        {"tag": "script", "url": "https://cdn.example.com/lib.js"}
    ]


def test_sri_integrity_detector_ignores_cross_origin_resource_with_integrity():
    detector = SRIIntegrityDetector()
    context = ScanContext(
        url="https://example.com/",
        headers={},
        body=(
            '<html><script src="https://cdn.example.com/lib.js" '
            'integrity="sha384-abc" crossorigin="anonymous"></script></html>'
        ),
    )

    findings = __import__("asyncio").run(detector.detect(context))

    assert findings == []


def test_sri_integrity_detector_ignores_same_origin_resources():
    detector = SRIIntegrityDetector()
    context = ScanContext(
        url="https://example.com/app/",
        headers={},
        body=(
            '<html>'
            '<script src="/static/app.js"></script>'
            '<link rel="stylesheet" href="https://example.com/assets/site.css">'
            "</html>"
        ),
    )

    findings = __import__("asyncio").run(detector.detect(context))

    assert findings == []


def test_frontend_supply_chain_detector_flags_mixed_content_and_unpinned_cdn():
    detector = FrontendSupplyChainDetector()
    context = ScanContext(
        url="https://example.com/",
        headers={},
        body=(
            '<html>'
            '<script src="http://cdn.example.com/lib.js"></script>'
            '<script src="https://unpkg.com/react/umd/react.production.min.js"></script>'
            "</html>"
        ),
    )

    findings = __import__("asyncio").run(detector.detect(context))

    assert {finding.title for finding in findings} == {
        "HTTPS 页面加载明文前端资源",
        "第三方前端资源未固定版本",
    }
    assert all(finding.type == "supply_chain_exposure" for finding in findings)


def test_frontend_supply_chain_detector_ignores_pinned_and_same_origin_resources():
    detector = FrontendSupplyChainDetector()
    context = ScanContext(
        url="https://example.com/",
        headers={},
        body=(
            '<html>'
            '<script src="/static/app.js"></script>'
            '<script src="https://unpkg.com/react@18.3.1/umd/react.production.min.js"></script>'
            "</html>"
        ),
    )

    findings = __import__("asyncio").run(detector.detect(context))

    assert findings == []


def test_login_surface_detector_flags_auth_protection_and_bruteforce_gaps(monkeypatch):
    detector = LoginSurfaceDetector()

    def handler(request):
        if request.url.path == "/login":
            return __import__("httpx").Response(
                200,
                text=(
                    '<html><form method="post">'
                    '<input type="text" name="username">'
                    '<input type="password" name="password">'
                    '<button type="submit">Login</button>'
                    "</form></html>"
                ),
                headers={"Content-Type": "text/html"},
            )
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
        "认证保护不足",
        "登录防爆破不足",
    }
    auth_finding = next(f for f in findings if f.title == "认证保护不足")
    assert "csrf_token_missing" in auth_finding.evidence.extra["issues"]


def test_login_surface_detector_ignores_protected_login_page(monkeypatch):
    detector = LoginSurfaceDetector()

    def handler(request):
        if request.url.path == "/login":
            return __import__("httpx").Response(
                200,
                text=(
                    '<html><form method="post" autocomplete="off">'
                    '<input type="hidden" name="csrf_token" value="abc123">'
                    '<input type="text" name="username">'
                    '<input type="password" name="password">'
                    '<div>captcha enabled</div>'
                    "</form></html>"
                ),
                headers={
                    "Content-Type": "text/html",
                    "X-Frame-Options": "DENY",
                },
            )
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

    assert findings == []


def test_protected_route_exposure_detector_flags_admin_page_and_api(monkeypatch):
    detector = ProtectedRouteExposureDetector()

    def handler(request):
        path = request.url.path
        if path == "/admin":
            return __import__("httpx").Response(
                200,
                text="<html><title>Admin Dashboard</title><body>dashboard admin logout users</body></html>",
                headers={"Content-Type": "text/html"},
            )
        if path == "/api/me":
            return __import__("httpx").Response(
                200,
                text='{"username":"alice","email":"alice@example.com","role":"admin"}',
                headers={"Content-Type": "application/json"},
            )
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
        "后台管理页面匿名可访问",
        "管理接口匿名可访问",
    }
    assert any(finding.type == "admin_page_exposure" for finding in findings)
    assert any(finding.type == "admin_api_exposure" for finding in findings)
    assert any(finding.severity == "critical" for finding in findings)
    assert any(finding.evidence.extra.get("exposure_kind") == "admin_api_data" for finding in findings)
    assert all(finding.evidence.extra.get("evidence_score", 0) >= 55 for finding in findings)


def test_protected_route_exposure_detector_flags_profile_page(monkeypatch):
    detector = ProtectedRouteExposureDetector()

    def handler(request):
        if request.url.path == "/profile":
            return __import__("httpx").Response(
                200,
                text="<html><body>profile username email account</body></html>",
                headers={"Content-Type": "text/html"},
            )
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
    assert findings[0].title == "用户账户页面匿名可访问"
    assert findings[0].type == "user_profile_exposure"
    assert findings[0].severity == "medium"
    assert findings[0].evidence.extra["evidence_score"] >= 50


def test_protected_route_exposure_detector_ignores_login_redirect_and_challenge(monkeypatch):
    detector = ProtectedRouteExposureDetector()

    def handler(request):
        path = request.url.path
        if path == "/admin":
            return __import__("httpx").Response(
                302,
                headers={"Location": "/login"},
            )
        if path == "/dashboard":
            return __import__("httpx").Response(
                200,
                text="<html><body>Please verify you are human challenge</body></html>",
                headers={"Content-Type": "text/html"},
            )
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


def test_oauth_surface_detector_flags_implicit_flow():
    detector = OAuthSurfaceDetector()
    context = ScanContext(
        url="https://example.com/login",
        headers={},
        body=(
            "<script>"
            "const auth='https://login.example.com/oauth2/authorize?client_id=web123&redirect_uri=https://app.example.com/oauth/callback&response_type=token';"
            "</script>"
        ),
    )

    findings = __import__("asyncio").run(detector.detect(context))

    assert len(findings) == 2
    assert any(finding.type == "oauth_surface_exposure" and finding.severity == "high" for finding in findings)
    implicit = next(finding for finding in findings if finding.type == "oauth_surface_exposure")
    assert implicit.evidence.extra["flow"] == "implicit"
    assert implicit.evidence.extra["evidence_score"] >= 70
    assert any(finding.title == "OAuth 授权请求未发现 state 参数" for finding in findings)


def test_oauth_surface_detector_flags_auth_code_without_pkce():
    detector = OAuthSurfaceDetector()
    context = ScanContext(
        url="https://example.com/login",
        headers={},
        body=(
            "<script>"
            "const auth='https://sso.example.com/oauth2/authorize?client_id=spa123&redirect_uri=https://app.example.com/auth/callback&response_type=code&state=abc';"
            "</script>"
        ),
    )

    findings = __import__("asyncio").run(detector.detect(context))

    assert len(findings) == 1
    assert findings[0].type == "oauth_surface_exposure"
    assert findings[0].severity == "medium"
    assert findings[0].evidence.extra["pkce_detected"] is False


def test_oauth_surface_detector_flags_missing_state_and_insecure_redirect():
    detector = OAuthSurfaceDetector()
    context = ScanContext(
        url="https://example.com/login",
        headers={},
        body=(
            "<script>"
            "const auth='https://idp.example.com/oauth2/authorize?client_id=spa123&redirect_uri=http://localhost:3000/callback&response_type=code';"
            "</script>"
        ),
    )

    findings = __import__("asyncio").run(detector.detect(context))

    assert {finding.title for finding in findings} == {
        "OAuth 授权请求未发现 state 参数",
        "OAuth 回调地址配置暴露高风险线索",
        "前端 OAuth 授权码流程未发现 PKCE 线索",
    }
    redirect_finding = next(finding for finding in findings if finding.title == "OAuth 回调地址配置暴露高风险线索")
    assert "http://localhost:3000/callback" in redirect_finding.evidence.extra["insecure_redirects"]


def test_oauth_surface_detector_ignores_strong_auth_code_flow():
    detector = OAuthSurfaceDetector()
    context = ScanContext(
        url="https://example.com/login",
        headers={},
        body=(
            "<script>"
            "const auth='https://idp.example.com/oauth2/authorize?client_id=spa123&redirect_uri=https://app.example.com/auth/callback&response_type=code&state=abc&code_challenge=xyz&code_challenge_method=S256';"
            "</script>"
        ),
    )

    findings = __import__("asyncio").run(detector.detect(context))

    assert findings == []


def test_cloud_storage_exposure_detector_flags_public_bucket_listing(monkeypatch):
    detector = CloudStorageExposureDetector()

    def handler(request):
        if "list-type=2" in str(request.url):
            return __import__("httpx").Response(
                200,
                text="<?xml version='1.0'?><ListBucketResult><Name>public-assets</Name><Contents><Key>backup.zip</Key></Contents></ListBucketResult>",
                headers={"Content-Type": "application/xml"},
            )
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
                    body='<img src="https://public-assets.s3.amazonaws.com/logo.png">',
                )
            )
        )
    finally:
        __import__("asyncio").run(client.aclose())

    assert len(findings) == 1
    assert findings[0].type == "cloud_storage_exposure"
    assert findings[0].evidence.extra["provider"] == "s3"
    assert findings[0].evidence.extra["evidence_score"] >= 75


def test_cloud_storage_exposure_detector_flags_azure_listing(monkeypatch):
    detector = CloudStorageExposureDetector()

    def handler(request):
        if "comp=list" in str(request.url):
            return __import__("httpx").Response(
                200,
                text="<?xml version='1.0'?><EnumerationResults><Blobs><Blob><Name>dump.sql</Name></Blob></Blobs></EnumerationResults>",
                headers={"Content-Type": "application/xml"},
            )
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
                    body='<a href="https://corpstore.blob.core.windows.net/backups/dump.sql">download</a>',
                )
            )
        )
    finally:
        __import__("asyncio").run(client.aclose())

    assert len(findings) == 1
    assert findings[0].evidence.extra["provider"] == "azure"


def test_cloud_storage_secret_exposure_detector_flags_signed_urls():
    detector = CloudStorageSecretExposureDetector()
    context = ScanContext(
        url="https://example.com/assets",
        headers={},
        body=(
            '<script>'
            'const a="https://public-assets.s3.amazonaws.com/private/report.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=abc&X-Amz-Expires=3600&X-Amz-Signature=deadbeef";'
            'const b="https://corpstore.blob.core.windows.net/backups/dump.sql?sp=r&se=2026-09-01T00:00:00Z&sig=abcdef";'
            '</script>'
        ),
    )

    findings = __import__("asyncio").run(detector.detect(context))

    assert len(findings) == 2
    assert {finding.evidence.extra["provider"] for finding in findings} == {
        "aws_s3",
        "azure_blob",
    }
    assert all(finding.type == "cloud_storage_secret_exposure" for finding in findings)


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


def test_sensitive_endpoint_detector_flags_swagger_and_prometheus_variants(monkeypatch):
    detector = SensitiveEndpointDetector()

    def handler(request):
        path = request.url.path
        if path == "/swagger-ui.html":
            return __import__("httpx").Response(
                200,
                text="<html><title>swagger-ui</title><div>openapi</div></html>",
                headers={"Content-Type": "text/html"},
            )
        if path == "/actuator/prometheus":
            return __import__("httpx").Response(
                200,
                text="# HELP jvm_memory_used_bytes\n# TYPE jvm_memory_used_bytes gauge\njvm_memory_used_bytes 1",
                headers={"Content-Type": "text/plain"},
            )
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
        "暴露 Swagger UI 文档",
        "暴露 Spring Boot Prometheus 指标端点",
    }


def test_sensitive_endpoint_detector_ignores_generic_debug_page(monkeypatch):
    detector = SensitiveEndpointDetector()

    def handler(request):
        if request.url.path == "/debug":
            return __import__("httpx").Response(
                200,
                text="<html><body>debug login</body></html>",
                headers={"Content-Type": "text/html"},
            )
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
