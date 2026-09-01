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
    OIDCDiscoveryConfigDetector,
    PassiveExposureDetector,
    ProtectedRouteExposureDetector,
    SRIIntegrityDetector,
    WellKnownExposureDetector,
    SensitiveEndpointDetector,
    ServerExposureDetector,
    TraceMethodDetector,
)
from app.plugins.detectors.business import SensitiveConfigExposureDetector


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


def test_sri_integrity_detector_flags_modulepreload_without_integrity():
    detector = SRIIntegrityDetector()
    context = ScanContext(
        url="https://example.com/",
        headers={},
        body='<html><link rel="modulepreload" href="https://cdn.example.com/app.mjs"></html>',
    )

    findings = __import__("asyncio").run(detector.detect(context))

    assert len(findings) == 1
    assert findings[0].type == "sri_missing"
    assert findings[0].evidence.extra["missing_resources"] == [
        {"tag": "link", "url": "https://cdn.example.com/app.mjs"}
    ]


def test_frontend_supply_chain_detector_flags_mixed_content_and_unpinned_cdn():
    detector = FrontendSupplyChainDetector()
    context = ScanContext(
        url="https://example.com/",
        headers={},
        body=(
            '<html>'
            '<script src="http://cdn.example.com/lib.js"></script>'
            '<script src="https://unpkg.com/react/umd/react.production.min.js"></script>'
            '<script src="https://cdnjs.cloudflare.com/ajax/libs/lodash/lodash.min.js"></script>'
            '<script src="https://esm.sh/react"></script>'
            "</html>"
        ),
    )

    findings = __import__("asyncio").run(detector.detect(context))

    assert {finding.title for finding in findings} == {
        "HTTPS 页面加载明文前端资源",
        "第三方前端资源未固定版本",
    }
    assert all(finding.type == "supply_chain_exposure" for finding in findings)
    unpinned = next(finding for finding in findings if finding.title == "第三方前端资源未固定版本")
    source_kinds = {item["source_kind"] for item in unpinned.evidence.extra["unpinned_resources"]}
    assert {"unpkg", "cdnjs", "esm.sh"} <= source_kinds


def test_frontend_supply_chain_detector_flags_modulepreload_and_importmap_resources():
    detector = FrontendSupplyChainDetector()
    context = ScanContext(
        url="https://example.com/",
        headers={},
        body=(
            '<html>'
            '<link rel="modulepreload" href="http://cdn.example.com/app.mjs">'
            '<script type="importmap">'
            '{"imports":{"react":"https://esm.sh/react","lit":"https://unpkg.com/lit-html/lit-html.js"}}'
            '</script>'
            "</html>"
        ),
    )

    findings = __import__("asyncio").run(detector.detect(context))

    assert {finding.title for finding in findings} == {
        "HTTPS 页面加载明文前端资源",
        "第三方前端资源未固定版本",
    }
    mixed = next(finding for finding in findings if finding.title == "HTTPS 页面加载明文前端资源")
    unpinned = next(finding for finding in findings if finding.title == "第三方前端资源未固定版本")
    mixed_tags = {item["tag"] for item in mixed.evidence.extra["mixed_resources"]}
    assert "link" in mixed_tags
    tags = {item["tag"] for item in unpinned.evidence.extra["unpinned_resources"]}
    assert "importmap" in tags


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


def test_oauth_surface_detector_flags_oidc_nonce_missing():
    detector = OAuthSurfaceDetector()
    context = ScanContext(
        url="https://example.com/login",
        headers={},
        body=(
            "<script>"
            "const auth='https://login.example.com/oauth2/authorize?client_id=web123&redirect_uri=https://app.example.com/oidc/callback&response_type=id_token&scope=openid%20profile&state=abc';"
            "</script>"
        ),
    )

    findings = __import__("asyncio").run(detector.detect(context))

    assert len(findings) == 2
    assert any(finding.title == "OIDC 授权请求未发现 nonce 参数" for finding in findings)
    nonce_finding = next(finding for finding in findings if finding.title == "OIDC 授权请求未发现 nonce 参数")
    assert nonce_finding.severity == "high"
    assert "implicit" in nonce_finding.evidence.extra["flows"]


def test_oauth_surface_detector_ignores_oidc_nonce_when_present():
    detector = OAuthSurfaceDetector()
    context = ScanContext(
        url="https://example.com/login",
        headers={},
        body=(
            "<script>"
            "const auth='https://login.example.com/oauth2/authorize?client_id=web123&redirect_uri=https://app.example.com/oidc/callback&response_type=id_token&scope=openid%20profile&state=abc&nonce=nonce-123';"
            "</script>"
        ),
    )

    findings = __import__("asyncio").run(detector.detect(context))

    assert len(findings) == 1
    assert findings[0].title == "前端暴露 OAuth 隐式流入口"


def test_oauth_surface_detector_flags_oidc_code_flow_nonce_missing():
    detector = OAuthSurfaceDetector()
    context = ScanContext(
        url="https://example.com/login",
        headers={},
        body=(
            "<script>"
            "const auth='https://login.example.com/oauth2/authorize?client_id=web123&redirect_uri=https://app.example.com/oidc/callback&response_type=code&scope=openid%20profile&state=abc';"
            "</script>"
        ),
    )

    findings = __import__("asyncio").run(detector.detect(context))

    assert len(findings) == 2
    nonce_finding = next(finding for finding in findings if finding.title == "OIDC 授权请求未发现 nonce 参数")
    assert nonce_finding.severity == "medium"
    assert nonce_finding.evidence.extra["flows"] == ["authorization_code"]


def test_oauth_surface_detector_ignores_oidc_code_nonce_when_present():
    detector = OAuthSurfaceDetector()
    context = ScanContext(
        url="https://example.com/login",
        headers={},
        body=(
            "<script>"
            "const auth='https://login.example.com/oauth2/authorize?client_id=web123&redirect_uri=https://app.example.com/oidc/callback&response_type=code&scope=openid%20profile&state=abc&nonce=nonce-123';"
            "</script>"
        ),
    )

    findings = __import__("asyncio").run(detector.detect(context))

    assert len(findings) == 1
    assert findings[0].title == "前端 OAuth 授权码流程未发现 PKCE 线索"


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


def test_oauth_surface_detector_flags_plain_pkce_method():
    detector = OAuthSurfaceDetector()
    context = ScanContext(
        url="https://example.com/login",
        headers={},
        body=(
            "<script>"
            "const auth='https://idp.example.com/oauth2/authorize?client_id=spa123&redirect_uri=https://app.example.com/auth/callback&response_type=code&state=abc&code_challenge=xyz&code_challenge_method=plain';"
            "</script>"
        ),
    )

    findings = __import__("asyncio").run(detector.detect(context))

    assert len(findings) == 1
    assert findings[0].title == "OAuth 授权码流程使用明文 PKCE"
    assert findings[0].severity == "high"
    assert findings[0].evidence.extra["auth_urls"]


def test_oauth_surface_detector_flags_oidc_response_mode_fragment():
    detector = OAuthSurfaceDetector()
    context = ScanContext(
        url="https://example.com/login",
        headers={},
        body=(
            "<script>"
            "const auth='https://login.example.com/oauth2/authorize?client_id=web123&redirect_uri=https://app.example.com/oidc/callback&response_type=code&response_mode=fragment&scope=openid%20profile&state=abc&nonce=nonce-123&code_challenge=xyz&code_challenge_method=S256';"
            "</script>"
        ),
    )

    findings = __import__("asyncio").run(detector.detect(context))

    assert len(findings) == 1
    assert findings[0].title == "OIDC 授权请求使用不安全的 response_mode"
    assert findings[0].severity == "high"
    assert findings[0].evidence.extra["response_modes"] == ["fragment"]


def test_oauth_surface_detector_flags_oidc_logout_without_id_token_hint():
    detector = OAuthSurfaceDetector()
    context = ScanContext(
        url="https://example.com/login",
        headers={},
        body=(
            "<script>"
            "const logout='https://login.example.com/logout?post_logout_redirect_uri=https://app.example.com/logged-out';"
            "</script>"
        ),
    )

    findings = __import__("asyncio").run(detector.detect(context))

    assert len(findings) == 1
    assert findings[0].title == "OIDC 登出请求未发现 id_token_hint"
    assert findings[0].severity == "medium"


def test_oidc_discovery_detector_flags_risky_metadata(monkeypatch):
    detector = OIDCDiscoveryConfigDetector()
    metadata = {
        "issuer": "http://idp.local",
        "authorization_endpoint": "http://idp.local/oauth2/authorize",
        "token_endpoint": "http://idp.local/oauth2/token",
        "end_session_endpoint": "http://idp.local/logout",
        "jwks_uri": "https://idp.local/.well-known/jwks.json",
        "response_types_supported": ["code", "token", "id_token"],
        "response_modes_supported": ["fragment", "query"],
        "grant_types_supported": ["authorization_code", "implicit"],
        "token_endpoint_auth_methods_supported": ["client_secret_basic", "none"],
        "frontchannel_logout_supported": False,
        "backchannel_logout_supported": False,
        "frontchannel_logout_session_supported": False,
        "id_token_signing_alg_values_supported": ["RS256", "none"],
        "userinfo_signing_alg_values_supported": ["RS256"],
        "request_object_signing_alg_values_supported": ["PS256"],
        "scopes_supported": ["profile", "email"],
        "subject_types_supported": ["public"],
    }

    def handler(request):
        if request.url.path.endswith("openid-configuration"):
            return __import__("httpx").Response(200, json=metadata)
        return __import__("httpx").Response(404, text="not found")

    client = __import__("httpx").AsyncClient(
        transport=__import__("httpx").MockTransport(handler)
    )
    monkeypatch.setattr("app.plugins.builtin.httpx.AsyncClient", lambda *args, **kwargs: client)

    try:
        findings = __import__("asyncio").run(
            detector.detect(
                ScanContext(
                    url="https://app.example.com/login",
                    headers={},
                    body='<script>const oidc="/.well-known/openid-configuration";</script>',
                )
            )
        )
    finally:
        __import__("asyncio").run(client.aclose())

    assert len(findings) == 1
    finding = findings[0]
    assert finding.type == "oidc_discovery_risk"
    assert finding.severity == "high"
    assert "implicit_grant" in finding.evidence.extra["issues"]
    assert "insecure_issuer" in finding.evidence.extra["issues"]
    assert "unsigned_id_token" in finding.evidence.extra["issues"]
    assert "risky_response_mode" in finding.evidence.extra["issues"]
    assert "insecure_logout_endpoint" in finding.evidence.extra["issues"]
    assert "logout_channel_weak" in finding.evidence.extra["issues"]
    assert finding.evidence.extra["evidence_score"] >= 70


def test_oidc_discovery_detector_ignores_hardened_metadata(monkeypatch):
    detector = OIDCDiscoveryConfigDetector()
    metadata = {
        "issuer": "https://auth.example.com",
        "authorization_endpoint": "https://auth.example.com/oauth2/authorize",
        "end_session_endpoint": "https://auth.example.com/logout",
        "token_endpoint": "https://auth.example.com/oauth2/token",
        "jwks_uri": "https://auth.example.com/.well-known/jwks.json",
        "response_types_supported": ["code"],
        "response_modes_supported": ["form_post"],
        "grant_types_supported": ["authorization_code"],
        "token_endpoint_auth_methods_supported": ["client_secret_basic"],
        "code_challenge_methods_supported": ["S256"],
        "frontchannel_logout_supported": True,
        "backchannel_logout_supported": True,
        "frontchannel_logout_session_supported": True,
        "scopes_supported": ["openid", "profile", "email"],
        "subject_types_supported": ["pairwise"],
    }

    def handler(request):
        if request.url.path.endswith("openid-configuration"):
            return __import__("httpx").Response(200, json=metadata)
        return __import__("httpx").Response(404, text="not found")

    client = __import__("httpx").AsyncClient(
        transport=__import__("httpx").MockTransport(handler)
    )
    monkeypatch.setattr("app.plugins.builtin.httpx.AsyncClient", lambda *args, **kwargs: client)

    try:
        findings = __import__("asyncio").run(
            detector.detect(
                ScanContext(
                    url="https://app.example.com/login",
                    headers={},
                    body='<script>const oidc="/.well-known/openid-configuration";</script>',
                )
            )
        )
    finally:
        __import__("asyncio").run(client.aclose())

    assert findings == []


def test_oidc_discovery_detector_flags_missing_pkce_support(monkeypatch):
    detector = OIDCDiscoveryConfigDetector()
    metadata = {
        "issuer": "https://auth.example.com",
        "authorization_endpoint": "https://auth.example.com/oauth2/authorize",
        "token_endpoint": "https://auth.example.com/oauth2/token",
        "jwks_uri": "https://auth.example.com/.well-known/jwks.json",
        "response_types_supported": ["code"],
        "response_modes_supported": ["form_post"],
        "grant_types_supported": ["authorization_code"],
        "token_endpoint_auth_methods_supported": ["client_secret_basic"],
        "frontchannel_logout_supported": True,
        "backchannel_logout_supported": True,
        "frontchannel_logout_session_supported": True,
        "scopes_supported": ["openid", "profile", "email"],
        "subject_types_supported": ["pairwise"],
    }

    def handler(request):
        if request.url.path.endswith("openid-configuration"):
            return __import__("httpx").Response(200, json=metadata)
        return __import__("httpx").Response(404, text="not found")

    client = __import__("httpx").AsyncClient(
        transport=__import__("httpx").MockTransport(handler)
    )
    monkeypatch.setattr("app.plugins.builtin.httpx.AsyncClient", lambda *args, **kwargs: client)

    try:
        findings = __import__("asyncio").run(
            detector.detect(
                ScanContext(
                    url="https://app.example.com/login",
                    headers={},
                    body='<script>const oidc="/.well-known/openid-configuration";</script>',
                )
            )
        )
    finally:
        __import__("asyncio").run(client.aclose())

    assert len(findings) == 1
    finding = findings[0]
    assert finding.type == "oidc_discovery_risk"
    assert "missing_pkce_support" in finding.evidence.extra["issues"]
    assert finding.evidence.extra["code_challenge_methods_supported"] == []


def test_oidc_discovery_detector_flags_weak_pkce_support(monkeypatch):
    detector = OIDCDiscoveryConfigDetector()
    metadata = {
        "issuer": "https://auth.example.com",
        "authorization_endpoint": "https://auth.example.com/oauth2/authorize",
        "token_endpoint": "https://auth.example.com/oauth2/token",
        "jwks_uri": "https://auth.example.com/.well-known/jwks.json",
        "response_types_supported": ["code"],
        "response_modes_supported": ["form_post"],
        "grant_types_supported": ["authorization_code"],
        "token_endpoint_auth_methods_supported": ["client_secret_basic"],
        "code_challenge_methods_supported": ["plain"],
        "frontchannel_logout_supported": True,
        "backchannel_logout_supported": True,
        "frontchannel_logout_session_supported": True,
        "scopes_supported": ["openid", "profile", "email"],
        "subject_types_supported": ["pairwise"],
    }

    def handler(request):
        if request.url.path.endswith("openid-configuration"):
            return __import__("httpx").Response(200, json=metadata)
        return __import__("httpx").Response(404, text="not found")

    client = __import__("httpx").AsyncClient(
        transport=__import__("httpx").MockTransport(handler)
    )
    monkeypatch.setattr("app.plugins.builtin.httpx.AsyncClient", lambda *args, **kwargs: client)

    try:
        findings = __import__("asyncio").run(
            detector.detect(
                ScanContext(
                    url="https://app.example.com/login",
                    headers={},
                    body='<script>const oidc="/.well-known/openid-configuration";</script>',
                )
            )
        )
    finally:
        __import__("asyncio").run(client.aclose())

    assert len(findings) == 1
    finding = findings[0]
    assert finding.type == "oidc_discovery_risk"
    assert "weak_pkce_support" in finding.evidence.extra["issues"]
    assert finding.evidence.extra["code_challenge_methods_supported"] == ["plain"]


def test_oidc_discovery_detector_flags_insecure_oauth_endpoints(monkeypatch):
    detector = OIDCDiscoveryConfigDetector()
    metadata = {
        "issuer": "https://auth.example.com",
        "authorization_endpoint": "https://auth.example.com/oauth2/authorize",
        "token_endpoint": "http://idp.local/oauth2/token",
        "userinfo_endpoint": "http://127.0.0.1:8080/oauth2/userinfo",
        "revocation_endpoint": "http://idp.local/oauth2/revoke",
        "introspection_endpoint": "http://idp.local/oauth2/introspect",
        "device_authorization_endpoint": "http://idp.local/oauth2/device",
        "jwks_uri": "https://auth.example.com/.well-known/jwks.json",
        "response_types_supported": ["code"],
        "response_modes_supported": ["form_post"],
        "grant_types_supported": ["authorization_code"],
        "token_endpoint_auth_methods_supported": ["client_secret_basic"],
        "frontchannel_logout_supported": True,
        "backchannel_logout_supported": True,
        "frontchannel_logout_session_supported": True,
        "scopes_supported": ["openid", "profile", "email"],
        "subject_types_supported": ["pairwise"],
    }

    def handler(request):
        if request.url.path.endswith("openid-configuration"):
            return __import__("httpx").Response(200, json=metadata)
        return __import__("httpx").Response(404, text="not found")

    client = __import__("httpx").AsyncClient(
        transport=__import__("httpx").MockTransport(handler)
    )
    monkeypatch.setattr("app.plugins.builtin.httpx.AsyncClient", lambda *args, **kwargs: client)

    try:
        findings = __import__("asyncio").run(
            detector.detect(
                ScanContext(
                    url="https://app.example.com/login",
                    headers={},
                    body='<script>const oidc="/.well-known/openid-configuration";</script>',
                )
            )
        )
    finally:
        __import__("asyncio").run(client.aclose())

    assert len(findings) == 1
    finding = findings[0]
    assert finding.type == "oidc_discovery_risk"
    assert "insecure_oauth_endpoint" in finding.evidence.extra["issues"]
    assert finding.evidence.extra["token_endpoint"] == "http://idp.local/oauth2/token"
    assert finding.evidence.extra["userinfo_endpoint"] == "http://127.0.0.1:8080/oauth2/userinfo"


def test_oidc_discovery_detector_flags_insecure_auxiliary_endpoints(monkeypatch):
    detector = OIDCDiscoveryConfigDetector()
    metadata = {
        "issuer": "https://auth.example.com",
        "authorization_endpoint": "https://auth.example.com/oauth2/authorize",
        "token_endpoint": "https://auth.example.com/oauth2/token",
        "jwks_uri": "https://auth.example.com/.well-known/jwks.json",
        "registration_endpoint": "http://idp.local/oauth2/register",
        "pushed_authorization_request_endpoint": "http://idp.local/oauth2/par",
        "backchannel_authentication_endpoint": "http://127.0.0.1:9000/oauth2/backchannel",
        "response_types_supported": ["code"],
        "response_modes_supported": ["form_post"],
        "grant_types_supported": ["authorization_code"],
        "token_endpoint_auth_methods_supported": ["client_secret_basic"],
        "frontchannel_logout_supported": True,
        "backchannel_logout_supported": True,
        "frontchannel_logout_session_supported": True,
        "scopes_supported": ["openid", "profile", "email"],
        "subject_types_supported": ["pairwise"],
        "code_challenge_methods_supported": ["S256"],
    }

    def handler(request):
        if request.url.path.endswith("openid-configuration"):
            return __import__("httpx").Response(200, json=metadata)
        return __import__("httpx").Response(404, text="not found")

    client = __import__("httpx").AsyncClient(
        transport=__import__("httpx").MockTransport(handler)
    )
    monkeypatch.setattr("app.plugins.builtin.httpx.AsyncClient", lambda *args, **kwargs: client)

    try:
        findings = __import__("asyncio").run(
            detector.detect(
                ScanContext(
                    url="https://app.example.com/login",
                    headers={},
                    body='<script>const oidc="/.well-known/openid-configuration";</script>',
                )
            )
        )
    finally:
        __import__("asyncio").run(client.aclose())

    assert len(findings) == 1
    finding = findings[0]
    assert finding.type == "oidc_discovery_risk"
    assert "insecure_oauth_endpoint" in finding.evidence.extra["issues"]
    assert finding.evidence.extra["registration_endpoint"] == "http://idp.local/oauth2/register"
    assert finding.evidence.extra["pushed_authorization_request_endpoint"] == "http://idp.local/oauth2/par"
    assert finding.evidence.extra["backchannel_authentication_endpoint"] == "http://127.0.0.1:9000/oauth2/backchannel"


def test_oidc_discovery_detector_flags_insecure_metadata_uris(monkeypatch):
    detector = OIDCDiscoveryConfigDetector()
    metadata = {
        "issuer": "https://auth.example.com",
        "authorization_endpoint": "https://auth.example.com/oauth2/authorize",
        "token_endpoint": "https://auth.example.com/oauth2/token",
        "jwks_uri": "https://auth.example.com/.well-known/jwks.json",
        "op_policy_uri": "http://idp.local/policy",
        "op_tos_uri": "http://idp.local/tos",
        "service_documentation": "http://127.0.0.1:8080/docs",
        "check_session_iframe": "http://idp.local/session/check",
        "response_types_supported": ["code"],
        "response_modes_supported": ["form_post"],
        "grant_types_supported": ["authorization_code"],
        "token_endpoint_auth_methods_supported": ["client_secret_basic"],
        "frontchannel_logout_supported": True,
        "backchannel_logout_supported": True,
        "frontchannel_logout_session_supported": True,
        "scopes_supported": ["openid", "profile", "email"],
        "subject_types_supported": ["pairwise"],
        "code_challenge_methods_supported": ["S256"],
    }

    def handler(request):
        if request.url.path.endswith("openid-configuration"):
            return __import__("httpx").Response(200, json=metadata)
        return __import__("httpx").Response(404, text="not found")

    client = __import__("httpx").AsyncClient(
        transport=__import__("httpx").MockTransport(handler)
    )
    monkeypatch.setattr("app.plugins.builtin.httpx.AsyncClient", lambda *args, **kwargs: client)

    try:
        findings = __import__("asyncio").run(
            detector.detect(
                ScanContext(
                    url="https://app.example.com/login",
                    headers={},
                    body='<script>const oidc="/.well-known/openid-configuration";</script>',
                )
            )
        )
    finally:
        __import__("asyncio").run(client.aclose())

    assert len(findings) == 1
    finding = findings[0]
    assert finding.type == "oidc_discovery_risk"
    assert "insecure_oauth_endpoint" in finding.evidence.extra["issues"]
    assert finding.evidence.extra["op_policy_uri"] == "http://idp.local/policy"
    assert finding.evidence.extra["service_documentation"] == "http://127.0.0.1:8080/docs"
    assert finding.evidence.extra["check_session_iframe"] == "http://idp.local/session/check"


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


def test_cloud_storage_exposure_detector_flags_spaces_listing(monkeypatch):
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
                    body='<img src="https://public-assets.nyc3.digitaloceanspaces.com/logo.png">',
                )
            )
        )
    finally:
        __import__("asyncio").run(client.aclose())

    assert len(findings) == 1
    assert findings[0].evidence.extra["provider"] == "spaces"


def test_cloud_storage_exposure_detector_flags_wasabi_listing(monkeypatch):
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
                    body='<img src="https://public-assets.s3.us-east-1.wasabisys.com/logo.png">',
                )
            )
        )
    finally:
        __import__("asyncio").run(client.aclose())

    assert len(findings) == 1
    assert findings[0].evidence.extra["provider"] == "wasabi"


def test_cloud_storage_exposure_detector_flags_backblaze_listing(monkeypatch):
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
                    body='<img src="https://s3.us-west-004.backblazeb2.com/public-assets/logo.png">',
                )
            )
        )
    finally:
        __import__("asyncio").run(client.aclose())

    assert len(findings) == 1
    assert findings[0].evidence.extra["provider"] == "backblaze"


def test_cloud_storage_exposure_detector_flags_minio_listing(monkeypatch):
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
                    body='<img src="http://minio.local:9000/public-assets/logo.png">',
                )
            )
        )
    finally:
        __import__("asyncio").run(client.aclose())

    assert len(findings) == 1
    assert findings[0].evidence.extra["provider"] == "minio"


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


def test_cloud_storage_secret_exposure_detector_flags_spaces_signed_urls():
    detector = CloudStorageSecretExposureDetector()
    context = ScanContext(
        url="https://example.com/assets",
        headers={},
        body=(
            '<script>'
            'const a="https://public-assets.nyc3.digitaloceanspaces.com/private/report.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=abc&X-Amz-Expires=3600&X-Amz-Signature=deadbeef";'
            '</script>'
        ),
    )

    findings = __import__("asyncio").run(detector.detect(context))

    assert len(findings) == 1
    assert findings[0].evidence.extra["provider"] == "digitalocean_spaces"


def test_cloud_storage_secret_exposure_detector_flags_ibm_cos_signed_urls():
    detector = CloudStorageSecretExposureDetector()
    context = ScanContext(
        url="https://example.com/assets",
        headers={},
        body=(
            '<script>'
            'const a="https://s3.us-south.cloud-object-storage.appdomain.cloud/backups/dump.sql?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=abc&X-Amz-Expires=3600&X-Amz-Signature=deadbeef";'
            '</script>'
        ),
    )

    findings = __import__("asyncio").run(detector.detect(context))

    assert len(findings) == 1
    assert findings[0].evidence.extra["provider"] == "ibm_cos"


def test_cloud_storage_secret_exposure_detector_flags_backblaze_signed_urls():
    detector = CloudStorageSecretExposureDetector()
    context = ScanContext(
        url="https://example.com/assets",
        headers={},
        body=(
            '<script>'
            'const a="https://s3.us-west-004.backblazeb2.com/public-assets/report.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=abc&X-Amz-Expires=3600&X-Amz-Signature=deadbeef";'
            '</script>'
        ),
    )

    findings = __import__("asyncio").run(detector.detect(context))

    assert len(findings) == 1
    assert findings[0].evidence.extra["provider"] == "backblaze"


def test_cloud_storage_secret_exposure_detector_flags_oci_signed_urls():
    detector = CloudStorageSecretExposureDetector()
    context = ScanContext(
        url="https://example.com/assets",
        headers={},
        body=(
            '<script>'
            'const a="https://mynamespace.compat.objectstorage.us-ashburn-1.oraclecloud.com/backups/report.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=abc&X-Amz-Expires=3600&X-Amz-Signature=deadbeef";'
            '</script>'
        ),
    )

    findings = __import__("asyncio").run(detector.detect(context))

    assert len(findings) == 1
    assert findings[0].evidence.extra["provider"] == "oci"


def test_cloud_storage_secret_exposure_detector_flags_minio_signed_urls():
    detector = CloudStorageSecretExposureDetector()
    context = ScanContext(
        url="https://example.com/assets",
        headers={},
        body=(
            '<script>'
            'const a="http://minio.local:9000/public-assets/report.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=abc&X-Amz-Expires=3600&X-Amz-Signature=deadbeef";'
            '</script>'
        ),
    )

    findings = __import__("asyncio").run(detector.detect(context))

    assert len(findings) == 1
    assert findings[0].evidence.extra["provider"] == "minio"


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


def test_sensitive_endpoint_detector_flags_spring_actuator_management_endpoints(monkeypatch):
    detector = SensitiveEndpointDetector()

    def handler(request):
        path = request.url.path
        if path == "/actuator/configprops":
            return __import__("httpx").Response(
                200,
                text='{"contexts":{"app":{"beans":{"serverProperties":{"prefix":"server","properties":{"port":8080}}}}}}',
                headers={"Content-Type": "application/json"},
            )
        if path == "/actuator/beans":
            return __import__("httpx").Response(
                200,
                text='{"contexts":{"app":{"beans":{"dataSource":{"scope":"singleton"}}}}}',
                headers={"Content-Type": "application/json"},
            )
        if path == "/actuator/mappings":
            return __import__("httpx").Response(
                200,
                text='{"contexts":{"app":{"dispatcherServlets":{"dispatcherServlet":{"handlerMappings":[{"predicate":"GET /admin"}]}}}}}',
                headers={"Content-Type": "application/json"},
            )
        if path == "/actuator/heapdump":
            return __import__("httpx").Response(
                200,
                text="JAVA HEAP DUMP\nclass histogram\n",
                headers={"Content-Type": "application/octet-stream"},
            )
        if path == "/actuator/threaddump":
            return __import__("httpx").Response(
                200,
                text="Full thread dump Java HotSpot(TM)\n\"main\" #1 prio=5 os_prio=0 tid=0x0000 nid=0x1 waiting",
                headers={"Content-Type": "text/plain"},
            )
        if path == "/actuator/logfile":
            return __import__("httpx").Response(
                200,
                text="2026-09-01 ERROR Authorization: Bearer token\n2026-09-01 password=secret\n",
                headers={"Content-Type": "text/plain"},
            )
        if path == "/actuator/shutdown":
            return __import__("httpx").Response(
                200,
                text='{"message":"shutdown"}',
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
        "暴露 Spring Boot Actuator 配置属性端点",
        "暴露 Spring Boot Actuator Beans 端点",
        "暴露 Spring Boot Actuator 路由映射端点",
        "暴露 Spring Boot HeapDump 端点",
        "暴露 Spring Boot ThreadDump 端点",
        "暴露 Spring Boot 日志文件端点",
        "暴露 Spring Boot 关停端点",
    }
    assert all(finding.type == "exposed_endpoint" for finding in findings)


def test_sensitive_endpoint_detector_flags_cloud_native_operations_endpoints(monkeypatch):
    detector = SensitiveEndpointDetector()

    def handler(request):
        path = request.url.path
        if path == "/v1/sys/health":
            return __import__("httpx").Response(
                200,
                text='{"initialized":true,"sealed":false,"version":"1.15.0","cluster_name":"vault-cluster"}',
                headers={"Content-Type": "application/json"},
            )
        if path == "/v1/sys/mounts":
            return __import__("httpx").Response(
                200,
                text='{"auth/token/":{"type":"token"},"kv/":{"type":"kv"},"transit/":{"type":"transit"}}',
                headers={"Content-Type": "application/json"},
            )
        if path == "/v1/status/leader":
            return __import__("httpx").Response(
                200,
                text='"127.0.0.1:8300" "127.0.0.1:8300"',
                headers={"Content-Type": "text/plain"},
            )
        if path == "/v1/agent/self":
            return __import__("httpx").Response(
                200,
                text='{"Config":{"NodeName":"consul-1"},"Member":{"Name":"consul-1"},"Checks":[{"CheckID":"service:api"}]}',
                headers={"Content-Type": "application/json"},
            )
        if path == "/ui/":
            return __import__("httpx").Response(
                200,
                text="<html><title>Consul</title><body>datacenter services kv</body></html>",
                headers={"Content-Type": "text/html"},
            )
        if path == "/v2/keys/":
            return __import__("httpx").Response(
                200,
                text='{"action":"get","node":{"key":"/","dir":true,"nodes":[{"key":"/config"}]}}',
                headers={"Content-Type": "application/json"},
            )
        if path == "/v2/members":
            return __import__("httpx").Response(
                200,
                text='{"members":[{"name":"etcd-1","peerURLs":["http://127.0.0.1:2380"],"clientURLs":["http://127.0.0.1:2379"]}]}',
                headers={"Content-Type": "application/json"},
            )
        if path == "/v2/stats/self":
            return __import__("httpx").Response(
                200,
                text='{"dbSize":1234,"leaderInfo":{"leader":"etcd-1"},"recvAppendRequestCnt":5}',
                headers={"Content-Type": "application/json"},
            )
        if path == "/api/v1/nodes":
            return __import__("httpx").Response(
                200,
                text='{"kind":"NodeList","items":[{"metadata":{"name":"node-1"}}]}',
                headers={"Content-Type": "application/json"},
            )
        if path == "/api/v1/pods":
            return __import__("httpx").Response(
                200,
                text='{"kind":"PodList","items":[{"metadata":{"name":"pod-1"},"status":{"phase":"Running"}}]}',
                headers={"Content-Type": "application/json"},
            )
        if path == "/api/v1/namespaces/kube-system/services/https:kubernetes-dashboard:/proxy/":
            return __import__("httpx").Response(
                200,
                text="<html><title>Kubernetes Dashboard</title><body>overview namespace</body></html>",
                headers={"Content-Type": "text/html"},
            )
        if path == "/api/v2/status":
            return __import__("httpx").Response(
                200,
                text='{"status":"success","data":{"cluster":"main","version":"0.25.0"}}',
                headers={"Content-Type": "application/json"},
            )
        if path == "/-/ready":
            return __import__("httpx").Response(
                200,
                text="Prometheus Server is Ready.",
                headers={"Content-Type": "text/plain"},
            )
        if path == "/-/healthy":
            return __import__("httpx").Response(
                200,
                text="Prometheus Server is Healthy.",
                headers={"Content-Type": "text/plain"},
            )
        if path == "/api/v1/status/config":
            return __import__("httpx").Response(
                200,
                text='{"status":"success","data":{"yaml":"global:\\n  scrape_interval: 15s\\n  query_timeout: 2m"}}',
                headers={"Content-Type": "application/json"},
            )
        if path == "/api/v1/status/flags":
            return __import__("httpx").Response(
                200,
                text='{"status":"success","data":{"web.enable-lifecycle":"true","storage.tsdb.retention.time":"15d","query.max-concurrency":"20"}}',
                headers={"Content-Type": "application/json"},
            )
        if path == "/api/v1/targets":
            return __import__("httpx").Response(
                200,
                text='{"status":"success","data":{"activeTargets":[{"scrapePool":"node","discoveredLabels":{"job":"node"},"labels":{"instance":"node-1"}}]}}',
                headers={"Content-Type": "application/json"},
            )
        if path == "/api/v2/silences":
            return __import__("httpx").Response(
                200,
                text='{"status":"success","data":[{"id":"silence-1","createdBy":"admin"}]}',
                headers={"Content-Type": "application/json"},
            )
        if path == "/api/v2/alerts":
            return __import__("httpx").Response(
                200,
                text='{"status":"success","data":[{"labels":{"alertname":"HighCPU"},"annotations":{"summary":"cpu"}}]}',
                headers={"Content-Type": "application/json"},
            )
        if path == "/api/v2/receivers":
            return __import__("httpx").Response(
                200,
                text='{"status":"success","data":[{"name":"default","routes":[{"receiver":"team-a"}],"matchers":[{"name":"severity","value":"critical"}]}]}',
                headers={"Content-Type": "application/json"},
            )
        if path == "/api/v2.0/configurations":
            return __import__("httpx").Response(
                200,
                text='{"auth_mode":"db_auth","project_creation_restriction":"adminonly"}',
                headers={"Content-Type": "application/json"},
            )
        if path == "/api/v2.0/projects":
            return __import__("httpx").Response(
                200,
                text='[{"project_id":1,"metadata":{"name":"library"}}]',
                headers={"Content-Type": "application/json"},
            )
        if path == "/api/v2.0/users/current":
            return __import__("httpx").Response(
                200,
                text='{"user_id":1,"username":"admin","has_admin_role":true}',
                headers={"Content-Type": "application/json"},
            )
        if path == "/api/version":
            return __import__("httpx").Response(
                200,
                text='{"Version":"v2.14.0","GitCommit":"deadbeef"}',
                headers={"Content-Type": "application/json"},
            )
        if path == "/api/v1/applications":
            return __import__("httpx").Response(
                200,
                text='{"items":[{"metadata":{"name":"demo"},"status":{"health":{"status":"Healthy"}}}]}',
                headers={"Content-Type": "application/json"},
            )
        if path == "/settings":
            return __import__("httpx").Response(
                200,
                text="<html><title>Argo CD Settings</title><body>settings repository</body></html>",
                headers={"Content-Type": "text/html"},
            )
        if path == "/api/search":
            return __import__("httpx").Response(
                200,
                text='[{"title":"Main Dashboard","uid":"abc123","type":"dash-db","uri":"db/main"}]',
                headers={"Content-Type": "application/json"},
            )
        if path == "/v2/_catalog":
            return __import__("httpx").Response(
                200,
                text='{"repositories":["app/backend","app/frontend"]}',
                headers={"Content-Type": "application/json"},
            )
        if path == "/version":
            return __import__("httpx").Response(
                200,
                text='{"ApiVersion":"1.45","Version":"24.0.7","GitCommit":"deadbeef"}',
                headers={"Content-Type": "application/json"},
            )
        if path == "/info":
            return __import__("httpx").Response(
                200,
                text='{"Containers":2,"Images":5,"OperatingSystem":"Ubuntu","NCPU":4}',
                headers={"Content-Type": "application/json"},
            )
        if path == "/containers/json":
            return __import__("httpx").Response(
                200,
                text='[{"Id":"abc123","Image":"nginx:latest","Names":["/web"],"State":"running"}]',
                headers={"Content-Type": "application/json"},
            )
        if path == "/images/json":
            return __import__("httpx").Response(
                200,
                text='[{"Id":"img123","RepoTags":["app/backend:latest"],"Size":123456}]',
                headers={"Content-Type": "application/json"},
            )
        if path == "/debug/pprof/":
            return __import__("httpx").Response(
                200,
                text="profiles\ngoroutine\nheap\n",
                headers={"Content-Type": "text/plain"},
            )
        if path == "/debug/vars":
            return __import__("httpx").Response(
                200,
                text='{"cmdline":["app"],"memstats":{"Alloc":1234},"goroutines":5}',
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
        "暴露 Prometheus 就绪检查端点",
        "暴露 Prometheus 健康检查端点",
        "暴露 Prometheus 配置状态端点",
        "暴露 Prometheus 启动参数端点",
        "暴露 Prometheus 抓取目标端点",
        "暴露 Vault 健康检查端点",
        "暴露 Vault 挂载配置端点",
        "暴露 Consul 集群领导者信息",
        "暴露 Consul Agent 自检端点",
        "暴露 Consul UI 管理面板",
        "暴露 etcd v2 Key API",
        "暴露 etcd 成员信息",
        "暴露 etcd 自身状态",
        "暴露 Kubernetes 节点 API",
        "暴露 Kubernetes Pod API",
        "暴露 Kubernetes Dashboard",
        "暴露 Alertmanager 状态端点",
        "暴露 Alertmanager 静音端点",
        "暴露 Alertmanager 告警端点",
        "暴露 Alertmanager 接收器配置",
        "暴露 Harbor 配置端点",
        "暴露 Harbor 项目端点",
        "暴露 Harbor 当前用户信息",
        "暴露 Argo CD 版本信息",
        "暴露 Argo CD 应用列表",
        "暴露 Argo CD 设置页面",
        "暴露 Grafana 搜索接口",
        "暴露 Docker Registry 目录",
        "暴露 Docker Remote API 版本信息",
        "暴露 Docker Remote API 详细信息",
        "暴露 Docker 容器列表接口",
        "暴露 Docker 镜像列表接口",
        "暴露 Go pprof 调试端点",
        "暴露 Go expvar 调试端点",
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


def test_sensitive_endpoint_detector_flags_prometheus_control_plane(monkeypatch):
    detector = SensitiveEndpointDetector()

    def handler(request):
        path = request.url.path
        if path == "/-/ready":
            return __import__("httpx").Response(200, text="Prometheus Server is Ready.")
        if path == "/api/v1/status/config":
            return __import__("httpx").Response(
                200,
                text='{"status":"success","data":{"yaml":"global:\\n  scrape_interval: 15s\\n  query_timeout: 2m"}}',
                headers={"Content-Type": "application/json"},
            )
        if path == "/api/v1/status/flags":
            return __import__("httpx").Response(
                200,
                text='{"status":"success","data":{"web.enable-lifecycle":"true","storage.tsdb.retention.time":"15d","query.max-concurrency":"20"}}',
                headers={"Content-Type": "application/json"},
            )
        if path == "/api/v1/targets":
            return __import__("httpx").Response(
                200,
                text='{"status":"success","data":{"activeTargets":[{"scrapePool":"node","discoveredLabels":{"job":"node"},"labels":{"instance":"node-1"}}]}}',
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
        "暴露 Prometheus 就绪检查端点",
        "暴露 Prometheus 配置状态端点",
        "暴露 Prometheus 启动参数端点",
        "暴露 Prometheus 抓取目标端点",
    }


def test_sensitive_endpoint_detector_flags_common_admin_panels(monkeypatch):
    detector = SensitiveEndpointDetector()

    def handler(request):
        path = request.url.path
        if path == "/jenkins":
            return __import__("httpx").Response(
                200,
                text="<html><title>Dashboard [Jenkins]</title><body>build history</body></html>",
                headers={"Content-Type": "text/html"},
            )
        if path == "/grafana":
            return __import__("httpx").Response(
                200,
                text="<html><title>Grafana</title><body>dashboard login</body></html>",
                headers={"Content-Type": "text/html"},
            )
        if path == "/api/search":
            return __import__("httpx").Response(
                200,
                text='[{"title":"Main Dashboard","uid":"abc123","type":"dash-db","uri":"db/main"}]',
                headers={"Content-Type": "application/json"},
            )
        if path == "/api/health":
            return __import__("httpx").Response(
                200,
                text='{"database":"ok","version":"10.4.1","commit":"abc123"}',
                headers={"Content-Type": "application/json"},
            )
        if path == "/kibana":
            return __import__("httpx").Response(
                200,
                text="<html><title>Kibana</title><body>elastic dashboard login</body></html>",
                headers={"Content-Type": "text/html"},
            )
        if path == "/api/status":
            return __import__("httpx").Response(
                200,
                text='{"name":"kibana","overall":{"state":"green"},"version":{"number":"8.12.0"}}',
                headers={"Content-Type": "application/json"},
            )
        if path == "/phpmyadmin":
            return __import__("httpx").Response(
                200,
                text="<html><title>phpMyAdmin</title><body>server version login</body></html>",
                headers={"Content-Type": "text/html"},
            )
        if path == "/manager/html":
            return __import__("httpx").Response(
                200,
                text="<html><title>Tomcat Manager Application</title><body>application manager deploy undeploy</body></html>",
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
        "暴露 Jenkins 管理面板",
        "暴露 Grafana 管理面板",
        "暴露 Grafana 搜索接口",
        "暴露 Grafana 健康状态端点",
        "暴露 Kibana 管理面板",
        "暴露 Kibana 状态端点",
        "暴露 phpMyAdmin 管理面板",
        "暴露 Tomcat Manager 管理面板",
    }
    assert all(finding.type == "exposed_endpoint" for finding in findings)


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


def test_backup_exposure_detector_flags_compressed_backup_files(monkeypatch):
    detector = BackupExposureDetector()

    def handler(request):
        path = request.url.path
        if path == "/backup.zip":
            return __import__("httpx").Response(
                200,
                text="PK\x03\x04 mysql dump backup archive contains DB_PASSWORD and secrets",
            )
        if path == "/backup.tar.gz":
            return __import__("httpx").Response(
                200,
                text="postgresql database dump archive with database and backup manifests",
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
        "压缩备份文件暴露",
    }
    assert all(finding.type == "backup_exposure" for finding in findings)


def test_backup_exposure_detector_flags_sqlite_database_files(monkeypatch):
    detector = BackupExposureDetector()

    def handler(request):
        path = request.url.path
        if path == "/backup.sqlite3":
            return __import__("httpx").Response(
                200,
                text="SQLite format 3\nCREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT);\nPRAGMA user_version=1;",
            )
        if path == "/database.db":
            return __import__("httpx").Response(
                200,
                text="sqlite database schema with table accounts and pragma settings",
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
        "SQLite 备份文件暴露",
        "数据库文件暴露",
    }
    assert all(finding.type == "backup_exposure" for finding in findings)


def test_backup_exposure_detector_flags_legacy_and_compressed_variants(monkeypatch):
    detector = BackupExposureDetector()

    def handler(request):
        path = request.url.path
        if path == "/backup.sql.bak":
            return __import__("httpx").Response(
                200,
                text="-- MySQL dump\nCREATE TABLE users (id INT);\nINSERT INTO users VALUES (1);",
            )
        if path == "/database.db.bak":
            return __import__("httpx").Response(
                200,
                text="SQLite format 3\nCREATE TABLE accounts (id INTEGER PRIMARY KEY);\nPRAGMA user_version=1;",
            )
        if path == "/backup.tar.bz2":
            return __import__("httpx").Response(
                200,
                text="postgresql database dump archive with database and backup manifests",
            )
        if path == "/backup.sql.zst":
            return __import__("httpx").Response(
                200,
                text="mysql dump archive compressed with zstd and backup metadata",
            )
        if path == "/backup.db.gz":
            return __import__("httpx").Response(
                200,
                text="sqlite database archive with create table schema pragma",
            )
        if path == "/application.yaml.bak":
            return __import__("httpx").Response(
                200,
                text="spring:\n  datasource:\n    password: secret\n    url: jdbc:postgresql://db/app",
            )
        if path == "/config.yaml.gz":
            return __import__("httpx").Response(
                200,
                text="spring:\n  datasource:\n    password: secret\n    url: jdbc:postgresql://db/app",
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
        "数据库备份旧版本暴露",
        "数据库旧备份文件暴露",
        "压缩备份文件暴露",
        "压缩数据库备份文件暴露",
        "应用配置备份暴露",
        "YAML 配置压缩备份暴露",
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


def test_sensitive_config_exposure_detector_flags_config_and_log_files(monkeypatch):
    detector = SensitiveConfigExposureDetector()

    def handler(request):
        path = request.url.path
        if path == "/.env":
            return __import__("httpx").Response(
                200,
                text="DATABASE_URL=postgres://user:pass@db.local/app\nJWT_SECRET=supersecret\nPRIVATE_KEY=-----BEGIN PRIVATE KEY-----",
            )
        if path == "/debug.log":
            return __import__("httpx").Response(
                200,
                text="2026-09-01T10:00:00Z ERROR Traceback (most recent call last)\nAuthorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\n",
            )
        return __import__("httpx").Response(404, text="not found")

    client = __import__("httpx").AsyncClient(
        transport=__import__("httpx").MockTransport(handler)
    )
    monkeypatch.setattr("app.plugins.detectors.business.httpx.AsyncClient", lambda *args, **kwargs: client)

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
        "环境变量文件暴露",
        "调试日志暴露",
    }
    assert all(finding.type == "sensitive_config_exposure" for finding in findings)


def test_sensitive_config_exposure_detector_flags_infra_and_ci_files(monkeypatch):
    detector = SensitiveConfigExposureDetector()

    def handler(request):
        path = request.url.path
        if path == "/nginx.conf":
            return __import__("httpx").Response(
                200,
                text=(
                    "server {\n"
                    "    server_name app.example.com;\n"
                    "    ssl_certificate /etc/ssl/cert.pem;\n"
                    "    proxy_pass http://10.0.0.8:8080;\n"
                    "}\n"
                ),
            )
        if path == "/.aws/credentials":
            return __import__("httpx").Response(
                200,
                text="[default]\naws_access_key_id=AKIAFAKE\naws_secret_access_key=FAKESECRET\n",
            )
        if path == "/.github/workflows/ci.yml":
            return __import__("httpx").Response(
                200,
                text=(
                    "name: ci\n"
                    "jobs:\n"
                    "  build:\n"
                    "    steps:\n"
                    "      - run: echo ${{ secrets.DEPLOY_TOKEN }}\n"
                ),
            )
        return __import__("httpx").Response(404, text="not found")

    client = __import__("httpx").AsyncClient(
        transport=__import__("httpx").MockTransport(handler)
    )
    monkeypatch.setattr("app.plugins.detectors.business.httpx.AsyncClient", lambda *args, **kwargs: client)

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
        "Nginx 配置文件暴露",
        "AWS 凭据文件暴露",
        "GitHub Actions 工作流暴露",
    }
    assert all(finding.type == "sensitive_config_exposure" for finding in findings)


def test_sensitive_config_exposure_detector_flags_credentials_files(monkeypatch):
    detector = SensitiveConfigExposureDetector()

    def handler(request):
        path = request.url.path
        if path == "/.git-credentials":
            return __import__("httpx").Response(
                200,
                text="https://alice:supersecret@example.com\n",
            )
        if path == "/.netrc":
            return __import__("httpx").Response(
                200,
                text="machine api.example.com login alice password supersecret\n",
            )
        if path == "/.pgpass":
            return __import__("httpx").Response(
                200,
                text="db.example.com:5432:appdb:appuser:pgsecret\n",
            )
        if path == "/.docker/config.json":
            return __import__("httpx").Response(
                200,
                text='{"auths":{"registry.example.com":{"auth":"YWxpY2U6c3VwZXJzZWNyZXQ="}}}',
            )
        if path == "/.htpasswd":
            return __import__("httpx").Response(
                200,
                text="admin:$apr1$abcdefghijklmnop$qwertyuiopasdfghjklz\n",
            )
        if path == "/service-account.json":
            return __import__("httpx").Response(
                200,
                text='{"type":"service_account","project_id":"demo","client_email":"svc@example.iam.gserviceaccount.com","private_key":"-----BEGIN PRIVATE KEY-----"}',
            )
        if path == "/firebase-service-account.json":
            return __import__("httpx").Response(
                200,
                text='{"type":"service_account","project_id":"demo","client_email":"firebase@example.iam.gserviceaccount.com","private_key":"-----BEGIN PRIVATE KEY-----"}',
            )
        return __import__("httpx").Response(404, text="not found")

    client = __import__("httpx").AsyncClient(
        transport=__import__("httpx").MockTransport(handler)
    )
    monkeypatch.setattr("app.plugins.detectors.business.httpx.AsyncClient", lambda *args, **kwargs: client)

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
        "Git 凭据文件暴露",
        "Netrc 凭据文件暴露",
        "PostgreSQL 凭据文件暴露",
        "Docker 凭据文件暴露",
        "HTTP Basic 认证口令文件暴露",
        "云服务账号文件暴露",
        "Firebase 服务账号文件暴露",
    }
    assert all(finding.type == "sensitive_config_exposure" for finding in findings)


def test_sensitive_config_exposure_detector_ignores_forbidden_files(monkeypatch):
    detector = SensitiveConfigExposureDetector()

    def handler(_request):
        return __import__("httpx").Response(403, text="forbidden")

    client = __import__("httpx").AsyncClient(
        transport=__import__("httpx").MockTransport(handler)
    )
    monkeypatch.setattr("app.plugins.detectors.business.httpx.AsyncClient", lambda *args, **kwargs: client)

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
