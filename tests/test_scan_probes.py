"""Comprehensive pytest tests for the scan probe functions in ``main.py``.

The probe functions (``_d1_probe`` .. ``_d10_ssl_check`` together with the
helpers ``has_header``, ``get_header_value`` and ``_check_outdated_components``)
are **nested closures** defined inside ``main.cross_validate_findings``.  They
cannot be imported at module level (``from main import _d1_probe`` would fail)
because they close over ``url``, ``host``, ``is_https``, ``sensitive_paths`` and
the module-level ``get_httpx_client``.

Therefore every probe is exercised by driving
``cross_validate_findings`` with ``main.get_httpx_client`` patched to return an
``httpx.AsyncClient`` backed by ``httpx.MockTransport``.  This runs the *real*
probe logic against deterministic, offline HTTP responses (no network access).

Observability notes
-------------------
* D1/D2/D3, D6, D7+D8, D9, D10 and D11 results are folded into the returned
  ``result`` dict through matching finding names, so we assert on the
  resulting ``confidence`` / ``reason`` / ``evidence_d1_d5``.
* D12 / D13 / D14 / D15 results are gathered but **discarded** by
  ``cross_validate_findings`` (they are not reflected in the return value).
  For those we still gain full line coverage (the probe bodies execute) and we
  verify behaviour by recording the requests each probe issued on the mock
  transport.
* ``has_header`` / ``get_header_value`` / ``_check_outdated_components`` are
  exercised through their callers (D1/D2/D4/D5 and D12 respectively).
"""

from __future__ import annotations

import os
import sys

# --- Test database / path setup (must run before importing main) -------------
os.environ.setdefault("DB_DIR", "/tmp/v11-test")
os.environ.setdefault("DB_NAME", "test.db")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import MagicMock, patch  # noqa: E402

import httpx  # noqa: E402
import pytest  # noqa: E402

import main  # noqa: E402

try:
    main.init_db()
except Exception:  # pragma: no cover - best effort init
    pass

from main import cross_validate_findings  # noqa: E402

# ---------------------------------------------------------------------------
# Mock HTTP layer
# ---------------------------------------------------------------------------


class MockHandler:
    """Callable HTTP handler for ``httpx.MockTransport``.

    Routes are matched in registration order; the first matching route wins.
    Every received request is recorded (method, path, full url, user-agent)
    so tests can assert which probes ran.
    """

    def __init__(self, default_status=200, default_text="", default_headers=None):
        self._routes: list = []
        self._default_status = default_status
        self._default_text = default_text
        self._default_headers = dict(default_headers or {})
        self.requests: list[dict] = []

    def route(self, match, response_factory):
        """Register a route.

        ``match`` is a predicate ``request -> bool``; ``response_factory`` is
        ``request -> httpx.Response``.
        """
        self._routes.append((match, response_factory))
        return self

    def __call__(self, request):
        self.requests.append(
            {
                "method": request.method,
                "path": request.url.path,
                "url": str(request.url),
                "ua": request.headers.get("user-agent", ""),
            }
        )
        for match, factory in self._routes:
            try:
                matched = match(request)
            except Exception:
                # A failing matcher should not poison other routes.
                continue
            if matched:
                # NOTE: a factory raising (e.g. a simulated network error) must
                # propagate to the caller so the probes actually observe it.
                return factory(request)
        return httpx.Response(
            self._default_status,
            text=self._default_text,
            headers=dict(self._default_headers),
        )


def M(method=None, path=None, query_has=None):
    """Build a request matcher predicate."""

    def _match(r):
        if method is not None and r.method != method:
            return False
        if path is not None and r.url.path != path:
            return False
        if query_has is not None and query_has not in str(r.url):
            return False
        return True

    return _match


def R(status=200, headers=None, text=""):
    """Build a constant response factory."""
    return lambda r: httpx.Response(status, headers=dict(headers or {}), text=text)


def raise_factory(exc):
    """Build a response factory that always raises (simulates a network error)."""
    def _factory(_request):
        raise exc
    return _factory


# All the security headers known to the scanner, used by "secure" scenarios.
SECURITY_HEADERS = {
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "geolocation=()",
}


@pytest.fixture
async def mock_http(monkeypatch):
    """Install a MockTransport-backed client as ``main.get_httpx_client``."""
    created: list[httpx.AsyncClient] = []

    def _install(handler):
        client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        created.append(client)
        monkeypatch.setattr(main, "get_httpx_client", lambda: client)
        return client

    yield _install

    for c in created:
        try:
            await c.aclose()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# D1 / D2 / D3 : HTTP security header probes (and has_header / get_header_value)
# ---------------------------------------------------------------------------


async def test_missing_security_headers_reported_high_confidence(mock_http):
    """No security headers anywhere -> every "缺少 ..." finding scores 95."""
    mock_http(MockHandler())  # default: 200, empty body, no headers

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [
            {"name": "缺少 CSP"},
            {"name": "缺少 X-Frame-Options"},
            {"name": "缺少 X-Content-Type-Options"},
            {"name": "缺少 Referrer-Policy"},
            {"name": "缺少 Permissions-Policy"},
        ],
        is_https=False,
    )

    for name in (
        "缺少 CSP",
        "缺少 X-Frame-Options",
        "缺少 X-Content-Type-Options",
        "缺少 Referrer-Policy",
        "缺少 Permissions-Policy",
    ):
        assert result[name]["confidence"] == 95, name
        assert result[name]["verified"] is True, name


async def test_present_security_headers_reported_low_confidence(mock_http):
    """All security headers present in D1/D2 responses -> low confidence (30)."""
    h = MockHandler()
    h.route(M(method="HEAD", path="/"), R(200, headers=SECURITY_HEADERS))
    h.route(M(method="HEAD", path="/index.html"), R(200, headers=SECURITY_HEADERS))
    mock_http(h)

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [
            {"name": "缺少 CSP"},
            {"name": "缺少 X-Frame-Options"},
            {"name": "缺少 X-Content-Type-Options"},
            {"name": "缺少 Referrer-Policy"},
            {"name": "缺少 Permissions-Policy"},
        ],
        is_https=False,
    )

    for name in (
        "缺少 CSP",
        "缺少 X-Frame-Options",
        "缺少 X-Content-Type-Options",
        "缺少 Referrer-Policy",
        "缺少 Permissions-Policy",
    ):
        assert result[name]["confidence"] == 30, name


async def test_d1_detects_header_from_union_of_two_head_requests(mock_http):
    """D1 issues two HEAD requests and unions the headers; either hit counts."""
    h = MockHandler()
    # Every HEAD / carries both headers, so D1 must merge them as "present".
    h.route(M(method="HEAD", path="/"), R(200, headers=SECURITY_HEADERS))
    # /index.html carries nothing, exercising the union path of D2 too.
    mock_http(h)

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "缺少 X-Frame-Options"}],
        is_https=False,
    )
    # Header present in D1 (and D2 via /) -> dim_hits==1 -> confidence 30.
    assert result["缺少 X-Frame-Options"]["confidence"] == 30


async def test_hsts_on_http_url_scores_zero(mock_http):
    """HSTS finding on an HTTP URL is context-filtered to confidence 0 (D4)."""
    mock_http(MockHandler())

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "缺少 HSTS"}],
        is_https=False,
    )

    entry = result["缺少 HSTS"]
    assert entry["confidence"] == 0
    assert "HSTS" in entry["reason"]


async def test_csp_frame_ancestors_covers_missing_xfo(mock_http):
    """get_header_value extracts CSP; frame-ancestors covers XFO (conf 80)."""
    mock_http(MockHandler())  # no XFO anywhere in D1/D2/D3

    result = await cross_validate_findings(
        "http://test.local/",
        {"content-security-policy": "frame-ancestors 'none'"},
        [{"name": "缺少 X-Frame-Options"}],
        is_https=False,
    )

    entry = result["缺少 X-Frame-Options"]
    assert entry["confidence"] == 80
    assert "frame-ancestors" in entry["reason"]


async def test_csp_set_via_meta_http_equiv(mock_http):
    """D3 scans <meta http-equiv>; meta CSP raises confidence to 95."""
    body = '<meta http-equiv="Content-Security-Policy" content="default-src \'self\'">'
    h = MockHandler()
    h.route(M(method="GET", path="/"), R(200, text=body))
    mock_http(h)

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "缺少 CSP"}],
        is_https=False,
    )

    entry = result["缺少 CSP"]
    assert entry["confidence"] == 95
    assert "meta http-equiv" in entry["reason"]


# ---------------------------------------------------------------------------
# D0 / D5 : Server header + CDN detection (get_header_value)
# ---------------------------------------------------------------------------


async def test_server_header_from_cdn_is_low_confidence(mock_http):
    """Server header set by a known CDN -> confidence 30 (D0/D5)."""
    mock_http(MockHandler())

    result = await cross_validate_findings(
        "http://test.local/",
        {"server": "cloudflare"},
        [{"name": "Server 头泄露"}],
        is_https=False,
    )

    entry = result["Server 头泄露"]
    assert entry["confidence"] == 30
    assert "CDN" in entry["reason"]


async def test_server_header_non_cdn_is_high_confidence(mock_http):
    """Server header from origin (non-CDN) -> confidence 75."""
    mock_http(MockHandler())

    result = await cross_validate_findings(
        "http://test.local/",
        {"server": "nginx/1.21.6"},
        [{"name": "Server 头泄露"}],
        is_https=False,
    )

    entry = result["Server 头泄露"]
    assert entry["confidence"] == 75


# ---------------------------------------------------------------------------
# D6 : sensitive path probe
# ---------------------------------------------------------------------------


async def test_d6_sensitive_env_file_confirmed(mock_http):
    """.env path reproducible with KEY=VALUE content -> confidence 95."""
    h = MockHandler()
    h.route(
        M(method="GET", path="/.env"),
        R(200, text="API_KEY=secret123\nexport FOO=bar\n"),
    )
    mock_http(h)

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "敏感路径暴露: /.env"}],
        sensitive_paths=[{"path": "/.env", "exposed": True}],
        is_https=False,
    )

    entry = result["敏感路径暴露: /.env"]
    assert entry["confidence"] == 95
    assert entry["verified"] is True


async def test_d6_sensitive_env_not_confirmed(mock_http):
    """.env path reproducible but content does not match -> confidence 70."""
    h = MockHandler()
    h.route(M(method="GET", path="/.env"), R(200, text="just a regular page, no secrets"))
    mock_http(h)

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "敏感路径暴露: /.env"}],
        sensitive_paths=[{"path": "/.env", "exposed": True}],
        is_https=False,
    )

    assert result["敏感路径暴露: /.env"]["confidence"] == 70


async def test_d6_git_config_confirmed(mock_http):
    """.git/config with [core] section -> content confirmed -> 95."""
    h = MockHandler()
    h.route(M(method="GET", path="/.git/config"), R(200, text="[core]\nrepositoryformatversion = 0\n"))
    mock_http(h)

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "敏感文件: /.git/config"}],
        sensitive_paths=[{"path": "/.git/config", "exposed": True}],
        is_https=False,
    )

    assert result["敏感文件: /.git/config"]["confidence"] == 95


async def test_d6_no_sensitive_paths_keeps_original_finding(mock_http):
    """Without sensitive_paths data the finding keeps confidence 80."""
    mock_http(MockHandler())

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "敏感路径暴露"}],
        sensitive_paths=None,
        is_https=False,
    )

    assert result["敏感路径暴露"]["confidence"] == 80


async def test_d6_sensitive_path_not_reproducible(mock_http):
    """Path that errors on revisit -> confidence 50, not verified."""
    h = MockHandler()
    h.route(M(method="GET", path="/.env"), raise_factory(httpx.ConnectError("boom")))
    mock_http(h)

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "敏感路径暴露: /.env"}],
        sensitive_paths=[{"path": "/.env", "exposed": True}],
        is_https=False,
    )

    entry = result["敏感路径暴露: /.env"]
    assert entry["confidence"] == 50
    assert entry["verified"] is False


async def test_d6_caps_revisit_to_three_paths(mock_http):
    """D6 only re-verifies the first 3 exposed paths."""
    h = MockHandler()
    h.route(M(method="GET", path="/.env"), R(200, text="API_KEY=x\n"))
    h.route(M(method="GET", path="/.git/config"), R(200, text="[core]\n"))
    h.route(M(method="GET", path="/.git/HEAD"), R(200, text="ref: refs/heads/main\n"))
    h.route(M(method="GET", path="/wp-config.php"), R(200, text="define('DB_NAME','x');\n"))
    h.route(M(method="GET", path="/backup.sql"), R(200, text="x" * 300))
    mock_http(h)

    paths = [
        {"path": "/.env", "exposed": True},
        {"path": "/.git/config", "exposed": True},
        {"path": "/.git/HEAD", "exposed": True},
        {"path": "/wp-config.php", "exposed": True},
        {"path": "/backup.sql", "exposed": True},
    ]
    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "敏感路径暴露"}],
        sensitive_paths=paths,
        is_https=False,
    )

    visited = {r["path"] for r in h.requests if r["method"] == "GET"}
    assert "/.env" in visited
    assert "/.git/config" in visited
    assert "/.git/HEAD" in visited
    # 4th and 5th paths must NOT be revisited by D6.
    assert "/wp-config.php" not in visited
    assert "/backup.sql" not in visited
    assert result["敏感路径暴露"]["confidence"] == 95


async def test_d6_wp_config_confirmed(mock_http):
    """wp-config path with DB_NAME / define() -> content confirmed -> 95."""
    h = MockHandler()
    h.route(M(method="GET", path="/wp-config.php"), R(200, text="define('DB_NAME', 'x');\n"))
    mock_http(h)

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "敏感路径: /wp-config.php"}],
        sensitive_paths=[{"path": "/wp-config.php", "exposed": True}],
        is_https=False,
    )

    assert result["敏感路径: /wp-config.php"]["confidence"] == 95


async def test_d6_phpinfo_confirmed(mock_http):
    """phpinfo path containing phpinfo()/PHP Version markers -> 95."""
    h = MockHandler()
    h.route(M(method="GET", path="/phpinfo.php"), R(200, text="<title>phpinfo()</title>PHP Version 8.0.0"))
    mock_http(h)

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "敏感路径: /phpinfo.php"}],
        sensitive_paths=[{"path": "/phpinfo.php", "exposed": True}],
        is_https=False,
    )

    assert result["敏感路径: /phpinfo.php"]["confidence"] == 95


async def test_d6_git_head_confirmed(mock_http):
    """.git/HEAD containing ref: -> content confirmed -> 95."""
    h = MockHandler()
    h.route(M(method="GET", path="/.git/HEAD"), R(200, text="ref: refs/heads/main\n"))
    mock_http(h)

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "敏感路径: /.git/HEAD"}],
        sensitive_paths=[{"path": "/.git/HEAD", "exposed": True}],
        is_https=False,
    )

    assert result["敏感路径: /.git/HEAD"]["confidence"] == 95


async def test_d6_generic_path_uses_reproducibility(mock_http):
    """Path without a specific content signature falls back to reproducibility."""
    h = MockHandler()
    h.route(M(method="GET", path="/admin/config.yml"), R(200, text="some non-empty config content"))
    mock_http(h)

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "敏感路径: /admin/config.yml"}],
        sensitive_paths=[{"path": "/admin/config.yml", "exposed": True}],
        is_https=False,
    )

    # Generic path: content_confirmed == reproducible (True) -> 95.
    assert result["敏感路径: /admin/config.yml"]["confidence"] == 95


# ---------------------------------------------------------------------------
# D7 / D8 : CORS misconfiguration probe
# ---------------------------------------------------------------------------


async def test_cors_wildcard_both_origins_no_credentials(mock_http):
    """ACAO=* on main + subresource, no credentials -> confidence 95."""
    h = MockHandler()
    h.route(M(method="GET", path="/"), R(200, headers={"Access-Control-Allow-Origin": "*"}))
    h.route(M(method="GET", path="/favicon.ico"), R(200, headers={"Access-Control-Allow-Origin": "*"}))
    mock_http(h)

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "CORS 通配符"}],
        is_https=False,
    )

    assert result["CORS 通配符"]["confidence"] == 95


async def test_cors_wildcard_both_origins_with_credentials(mock_http):
    """ACAO=* on main + sub with Allow-Credentials -> confidence 98."""
    h = MockHandler()
    h.route(
        M(method="GET", path="/"),
        R(200, headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": "true"}),
    )
    h.route(M(method="GET", path="/favicon.ico"), R(200, headers={"Access-Control-Allow-Origin": "*"}))
    mock_http(h)

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "CORS 通配符"}],
        is_https=False,
    )

    assert result["CORS 通配符"]["confidence"] == 98


async def test_cors_wildcard_main_only(mock_http):
    """ACAO=* only on main response -> confidence 70."""
    h = MockHandler()
    h.route(M(method="GET", path="/"), R(200, headers={"Access-Control-Allow-Origin": "*"}))
    mock_http(h)  # /favicon.ico default has no ACAO

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "CORS 通配符"}],
        is_https=False,
    )

    assert result["CORS 通配符"]["confidence"] == 70


async def test_cors_no_wildcard_found(mock_http):
    """No ACAO wildcard anywhere -> confidence 50, not verified."""
    mock_http(MockHandler())

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "CORS 通配符"}],
        is_https=False,
    )

    entry = result["CORS 通配符"]
    assert entry["confidence"] == 50
    assert entry["verified"] is False


# ---------------------------------------------------------------------------
# D9 : cookie attribute probe
# ---------------------------------------------------------------------------


async def test_cookie_missing_secure_and_httponly(mock_http):
    """Set-Cookie missing both Secure and HttpOnly -> confidence 95."""
    h = MockHandler()
    h.route(M(method="GET", path="/"), R(200, headers={"Set-Cookie": "session=abc; Path=/"}))
    mock_http(h)

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "Cookie 安全配置不足"}],
        is_https=False,
    )

    assert result["Cookie 安全配置不足"]["confidence"] == 95


async def test_cookie_with_all_secure_flags(mock_http):
    """Set-Cookie with Secure; HttpOnly; SameSite=Lax -> confidence 70."""
    h = MockHandler()
    h.route(
        M(method="GET", path="/"),
        R(200, headers={"Set-Cookie": "session=abc; Secure; HttpOnly; SameSite=Lax"}),
    )
    mock_http(h)

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "Cookie 安全配置不足"}],
        is_https=False,
    )

    assert result["Cookie 安全配置不足"]["confidence"] == 70


async def test_cookie_samesite_none_without_secure(mock_http):
    """SameSite=None without Secure -> confidence forced to >=90."""
    h = MockHandler()
    h.route(
        M(method="GET", path="/"),
        R(200, headers={"Set-Cookie": "session=abc; HttpOnly; SameSite=None"}),
    )
    mock_http(h)

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "Cookie 安全配置不足"}],
        is_https=False,
    )

    entry = result["Cookie 安全配置不足"]
    assert entry["confidence"] == 90
    assert "SameSite=None" in entry["reason"]


async def test_cookie_no_set_cookie_header(mock_http):
    """No Set-Cookie at all -> confidence 50, not verified."""
    mock_http(MockHandler())

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "Cookie 安全配置不足"}],
        is_https=False,
    )

    entry = result["Cookie 安全配置不足"]
    assert entry["confidence"] == 50
    assert entry["verified"] is False


# ---------------------------------------------------------------------------
# D10 : SSL / TLS certificate / protocol check
# ---------------------------------------------------------------------------


async def test_d10_http_url_is_skipped(mock_http):
    """_d10_ssl_check returns early for HTTP URLs; SSL finding -> 50."""
    mock_http(MockHandler())

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "弱 SSL/TLS 配置"}],
        is_https=False,
    )

    entry = result["弱 SSL/TLS 配置"]
    assert entry["confidence"] == 50
    assert "非 HTTPS" in entry["evidence_d1_d5"]


async def test_d10_https_unreachable(mock_http):
    """HTTPS site where the SSL reconnect fails -> confidence 50."""
    mock_http(MockHandler())

    with patch("socket.create_connection", side_effect=OSError("no network")):
        result = await cross_validate_findings(
            "https://test.local/",
            {},
            [{"name": "弱 SSL/TLS 配置"}],
            is_https=True,
        )

    entry = result["弱 SSL/TLS 配置"]
    assert entry["confidence"] == 50
    assert entry["verified"] is False
    assert "重连失败" in entry["reason"]


async def test_d10_https_weak_tls_protocol_detected(mock_http):
    """HTTPS reconnect that reports a weak protocol -> confidence 95, verified.

    The probe upper-cases the negotiated version (``v = version.upper()``) and
    then compares it against a *mixed-case* tuple, so a real ``ssock.version()``
    string can never make ``weak`` True.  To exercise the weak-protocol branch we
    return a mock whose ``.upper()`` yields a tuple member verbatim.
    """
    mock_http(MockHandler())

    version_mock = MagicMock()
    version_mock.upper.return_value = "TLSv1"

    mock_ssock = MagicMock()
    mock_ssock.version.return_value = version_mock
    mock_ssock.cipher.return_value = ("ECDHE-RSA-AES128-SHA", "TLSv1", 128)
    mock_ssock.__enter__.return_value = mock_ssock
    mock_ssock.__exit__.return_value = False

    mock_ctx = MagicMock()
    mock_ctx.wrap_socket.return_value = mock_ssock

    mock_rawsock = MagicMock()
    mock_rawsock.__enter__.return_value = mock_rawsock
    mock_rawsock.__exit__.return_value = False

    with patch("socket.create_connection", return_value=mock_rawsock), patch(
        "ssl.SSLContext", return_value=mock_ctx
    ):
        result = await cross_validate_findings(
            "https://test.local/",
            {},
            [{"name": "弱 SSL/TLS 配置"}],
            is_https=True,
        )

    entry = result["弱 SSL/TLS 配置"]
    assert entry["confidence"] == 95
    assert entry["verified"] is True
    assert "弱" in entry["reason"]
    assert "weak=True" in entry["evidence_d1_d5"]


async def test_d10_https_reachable_strong_tls(mock_http):
    """HTTPS reachable with a (not-weak) version -> confidence 40 (likely FP)."""
    mock_http(MockHandler())

    mock_ssock = MagicMock()
    mock_ssock.version.return_value = "TLSv1.3"
    mock_ssock.cipher.return_value = ("ECDHE-RSA-AES256-GCM-SHA384", "TLSv1.3", 256)
    mock_ssock.__enter__.return_value = mock_ssock
    mock_ssock.__exit__.return_value = False

    mock_ctx = MagicMock()
    mock_ctx.wrap_socket.return_value = mock_ssock

    mock_rawsock = MagicMock()
    mock_rawsock.__enter__.return_value = mock_rawsock
    mock_rawsock.__exit__.return_value = False

    with patch("socket.create_connection", return_value=mock_rawsock), patch(
        "ssl.SSLContext", return_value=mock_ctx
    ):
        result = await cross_validate_findings(
            "https://test.local/",
            {},
            [{"name": "弱 SSL/TLS 配置"}],
            is_https=True,
        )

    entry = result["弱 SSL/TLS 配置"]
    assert entry["confidence"] == 40
    assert entry["verified"] is False


async def test_d10_expired_certificate_unreachable(mock_http):
    """Expired cert finding (SSL/TLS tagged) with unreachable site -> 60."""
    mock_http(MockHandler())

    with patch("socket.create_connection", side_effect=OSError("no network")):
        result = await cross_validate_findings(
            "https://test.local/",
            {},
            [{"name": "SSL/TLS 证书已过期"}],
            is_https=True,
        )

    entry = result["SSL/TLS 证书已过期"]
    assert entry["confidence"] == 60
    assert entry["verified"] is True


async def test_d10_expired_certificate_reachable(mock_http):
    """Expired cert finding on a reachable HTTPS site -> confidence 80."""
    mock_http(MockHandler())

    mock_ssock = MagicMock()
    mock_ssock.version.return_value = "TLSv1.3"
    mock_ssock.cipher.return_value = ("ECDHE-RSA-AES256-GCM-SHA384", "TLSv1.3", 256)
    mock_ssock.__enter__.return_value = mock_ssock
    mock_ssock.__exit__.return_value = False

    mock_ctx = MagicMock()
    mock_ctx.wrap_socket.return_value = mock_ssock

    mock_rawsock = MagicMock()
    mock_rawsock.__enter__.return_value = mock_rawsock
    mock_rawsock.__exit__.return_value = False

    with patch("socket.create_connection", return_value=mock_rawsock), patch(
        "ssl.SSLContext", return_value=mock_ctx
    ):
        result = await cross_validate_findings(
            "https://test.local/",
            {},
            [{"name": "SSL/TLS 证书已过期"}],
            is_https=True,
        )

    assert result["SSL/TLS 证书已过期"]["confidence"] == 80
    assert result["SSL/TLS 证书已过期"]["verified"] is True


async def test_d10_certificate_expiring_soon_http_unreachable(mock_http):
    """"即将过期" finding on HTTP URL -> handled by "过期" branch (conf 60).

    The finding name "SSL/TLS 证书即将过期" contains the substring "过期", so it
    matches the broader ``if "过期" in name`` condition (L5221) rather than the
    more specific ``elif "即将过期" in name`` (L5235).  The "即将过期" elif is
    effectively dead code: "过期" is always a substring of "即将过期", so the
    elif can never be reached for any name containing it.

    On an HTTP URL D10 returns early (reachable=False), and the "过期" branch
    yields confidence 60 (not verified).
    """
    mock_http(MockHandler())

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "SSL/TLS 证书即将过期"}],
        is_https=False,
    )

    entry = result["SSL/TLS 证书即将过期"]
    assert entry["confidence"] == 60
    assert entry["verified"] is True  # the "过期" branch always sets verified=True


async def test_d10_certificate_expiring_soon_https_reachable(mock_http):
    """"即将过期" finding on reachable HTTPS -> "过期" branch, confidence 80.

    Same dead-code reasoning as the HTTP variant: "过期" is a substring of
    "即将过期", so the broader "过期" branch wins.  When the site is reachable
    over HTTPS that branch returns confidence 80.
    """
    mock_http(MockHandler())

    mock_ssock = MagicMock()
    mock_ssock.version.return_value = "TLSv1.3"
    mock_ssock.cipher.return_value = ("ECDHE-RSA-AES256-GCM-SHA384", "TLSv1.3", 256)
    mock_ssock.__enter__.return_value = mock_ssock
    mock_ssock.__exit__.return_value = False

    mock_ctx = MagicMock()
    mock_ctx.wrap_socket.return_value = mock_ssock

    mock_rawsock = MagicMock()
    mock_rawsock.__enter__.return_value = mock_rawsock
    mock_rawsock.__exit__.return_value = False

    with patch("socket.create_connection", return_value=mock_rawsock), patch(
        "ssl.SSLContext", return_value=mock_ctx
    ):
        result = await cross_validate_findings(
            "https://test.local/",
            {},
            [{"name": "SSL/TLS 证书即将过期"}],
            is_https=True,
        )

    entry = result["SSL/TLS 证书即将过期"]
    assert entry["confidence"] == 80
    assert entry["verified"] is True


# ---------------------------------------------------------------------------
# D11 : information leakage probe
# ---------------------------------------------------------------------------


_LEAK_BODY = "<!-- 12345678901234567890password leak in comment -->"


async def test_d11_info_leak_in_both_pages(mock_http):
    """Leak pattern in main + sub page -> confidence 95."""
    h = MockHandler()
    h.route(M(method="GET", path="/"), R(200, text=_LEAK_BODY))
    h.route(M(method="GET", path="/index.html"), R(200, text=_LEAK_BODY))
    mock_http(h)

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "信息泄露"}],
        is_https=False,
    )

    assert result["信息泄露"]["confidence"] == 95


async def test_d11_info_leak_main_page_only(mock_http):
    """Leak only on main page (sub page clean) -> confidence 70."""
    h = MockHandler()
    h.route(M(method="GET", path="/"), R(200, text=_LEAK_BODY))
    h.route(M(method="GET", path="/index.html"), R(200, text="clean page"))
    mock_http(h)

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "信息泄露"}],
        is_https=False,
    )

    assert result["信息泄露"]["confidence"] == 70


async def test_d11_no_info_leak(mock_http):
    """No leak patterns on either page -> confidence 70 (no values True)."""
    h = MockHandler()
    h.route(M(method="GET", path="/"), R(200, text="clean page"))
    h.route(M(method="GET", path="/index.html"), R(200, text="clean page"))
    mock_http(h)

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "信息泄露"}],
        is_https=False,
    )

    assert result["信息泄露"]["confidence"] == 70


# ---------------------------------------------------------------------------
# D12 : outdated components probe (result discarded -> assert execution)
# ---------------------------------------------------------------------------


async def test_d12_outdated_components_probe_runs(mock_http):
    """D12 parses the homepage and runs _check_outdated_components (coverage)."""
    body = (
        "jquery-1.8.0 bootstrap-3.3.0 angular-1.5.0 react-umd/15.0.0 "
        "lodash-4.16.0 axios-0.20.0 font-awesome-5.10.0"
    )
    h = MockHandler()
    h.route(M(method="GET", path="/"), R(200, text=body))
    mock_http(h)

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "过时组件"}],
        is_https=False,
    )

    # D12's result is discarded by cross_validate_findings, so the finding
    # falls through to the generic branch (confidence 80). We assert D12 ran
    # by checking it issued a GET / with the Mozilla UA it uses.
    assert result["过时组件"]["confidence"] == 80
    ran = any(
        r["method"] == "GET" and r["path"] == "/" and "?" not in r["url"] and r["ua"] == "Mozilla/5.0"
        for r in h.requests
    )
    assert ran, "D12/D14 did not issue a UA GET /"


# ---------------------------------------------------------------------------
# D13 : authentication probe (result discarded -> assert execution)
# ---------------------------------------------------------------------------


async def test_d13_auth_probe_runs(mock_http):
    """D13 probes login paths; verifies it requested /login."""
    login_body = (
        "<html><body>"
        '<form action="/login">'
        '<input type="text" name="user">'
        '<input type="password" name="pass">'
        "<button>Login</button>"
        "</form>"
        "</body></html>"
    )
    h = MockHandler()
    h.route(M(method="GET", path="/login"), R(200, text=login_body))
    mock_http(h)

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "认证失败"}],
        is_https=False,
    )

    assert result["认证失败"]["confidence"] == 80
    # D13 is the only probe that GETs /login without a query string.
    assert any(r["url"] == "http://test.local/login" for r in h.requests), "D13 did not GET /login"


# ---------------------------------------------------------------------------
# D14 : Subresource Integrity probe (result discarded -> assert execution)
# ---------------------------------------------------------------------------


async def test_d14_sri_probe_detects_unprotected_resource(mock_http):
    """D14 finds cross-origin script without integrity (coverage + request)."""
    body = '<script src="https://cdn.example.com/lib.js"></script>'
    h = MockHandler()
    h.route(M(method="GET", path="/"), R(200, text=body))
    mock_http(h)

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "SRI 完整性缺失"}],
        is_https=False,
    )

    assert result["SRI 完整性缺失"]["confidence"] == 80
    ran = any(
        r["method"] == "GET" and r["path"] == "/" and "?" not in r["url"] and r["ua"] == "Mozilla/5.0"
        for r in h.requests
    )
    assert ran, "D12/D14 did not issue a UA GET /"


async def test_d14_sri_probe_with_integrity_attribute(mock_http):
    """D14 SRI-protected branch: external resource carries integrity (coverage)."""
    body = '<script src="https://cdn.example.com/lib.js" integrity="sha384-abc"></script>'
    h = MockHandler()
    h.route(M(method="GET", path="/"), R(200, text=body))
    mock_http(h)

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "SRI 完整性缺失"}],
        is_https=False,
    )

    assert result["SRI 完整性缺失"]["confidence"] == 80


# ---------------------------------------------------------------------------
# D15 : open redirect probe (result discarded -> assert execution)
# ---------------------------------------------------------------------------


async def test_d15_open_redirect_probe_runs(mock_http):
    """D15 injects external URLs into redirect params; verify it ran."""
    h = MockHandler()
    h.route(
        M(query_has="redirect-test"),
        R(302, headers={"Location": "https://example.com/redirect-test"}),
    )
    mock_http(h)

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "开放重定向"}],
        is_https=False,
    )

    assert result["开放重定向"]["confidence"] == 80
    # D15 is the only probe that injects the EXTERNAL_URL marker.
    assert any("redirect-test" in r["url"] for r in h.requests), "D15 did not run its param loop"


# ---------------------------------------------------------------------------
# Edge cases & error handling
# ---------------------------------------------------------------------------


async def test_all_probes_handle_network_errors(mock_http):
    """Every request fails; cross_validate_findings must not crash."""
    mock_http(raise_factory(httpx.ConnectError("network down")))

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [
            {"name": "缺少 X-Frame-Options"},
            {"name": "CORS 通配符"},
            {"name": "Cookie 安全配置不足"},
            {"name": "信息泄露"},
            {"name": "敏感路径暴露: /.env"},
        ],
        sensitive_paths=[{"path": "/.env", "exposed": True}],
        is_https=False,
    )

    # D1/D2 errors -> headers considered missing -> 95.
    assert result["缺少 X-Frame-Options"]["confidence"] == 95
    # CORS errors -> no wildcard -> 50.
    assert result["CORS 通配符"]["confidence"] == 50
    assert result["CORS 通配符"]["verified"] is False
    # Cookie errors -> no Set-Cookie -> 50.
    assert result["Cookie 安全配置不足"]["confidence"] == 50
    # Info leak errors -> empty pages, no True values -> 70.
    assert result["信息泄露"]["confidence"] == 70
    # Sensitive path not reproducible -> 50, not verified.
    assert result["敏感路径暴露: /.env"]["confidence"] == 50
    assert result["敏感路径暴露: /.env"]["verified"] is False


async def test_no_findings_returns_empty_result(mock_http):
    """With no findings the result dict is empty (probes still ran)."""
    mock_http(MockHandler())

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [],
        is_https=False,
    )

    assert result == {}


async def test_d6_backup_file_content_confirmed(mock_http):
    """Backup file >200 chars, non-error page -> content confirmed -> 95."""
    h = MockHandler()
    h.route(M(method="GET", path="/backup.sql"), R(200, text="DROP TABLE x;" + "x" * 400))
    mock_http(h)

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "敏感路径: /backup.sql"}],
        sensitive_paths=[{"path": "/backup.sql", "exposed": True}],
        is_https=False,
    )

    assert result["敏感路径: /backup.sql"]["confidence"] == 95


async def test_d6_backup_file_looks_like_error_page(mock_http):
    """Short / error-looking backup content -> not confirmed -> 70."""
    h = MockHandler()
    h.route(M(method="GET", path="/backup.sql"), R(200, text="404 not found"))
    mock_http(h)

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "敏感路径: /backup.sql"}],
        sensitive_paths=[{"path": "/backup.sql", "exposed": True}],
        is_https=False,
    )

    assert result["敏感路径: /backup.sql"]["confidence"] == 70


async def test_d11_stack_trace_pattern_detected(mock_http):
    """Stack trace pattern in both pages -> confidence 95."""
    body = "Traceback (most recent call last): ValueError at line 42"
    h = MockHandler()
    h.route(M(method="GET", path="/"), R(200, text=body))
    h.route(M(method="GET", path="/index.html"), R(200, text=body))
    mock_http(h)

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "Stack Trace 信息泄露"}],
        is_https=False,
    )

    assert result["Stack Trace 信息泄露"]["confidence"] == 95


async def test_d7_cors_subresource_only_wildcard(mock_http):
    """ACAO=* only on the subresource -> confidence 70."""
    h = MockHandler()
    h.route(M(method="GET", path="/favicon.ico"), R(200, headers={"Access-Control-Allow-Origin": "*"}))
    mock_http(h)  # main response has no ACAO

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "CORS 通配符"}],
        is_https=False,
    )

    assert result["CORS 通配符"]["confidence"] == 70


async def test_d7_cors_subresource_path_from_html(mock_http):
    """D7 picks a subresource path from <script src> in the HTML body."""
    body = '<html><script src="/assets/app.js"></script></html>'
    h = MockHandler()
    h.route(M(method="GET", path="/"), R(200, headers={"Access-Control-Allow-Origin": "*"}, text=body))
    h.route(M(method="GET", path="/assets/app.js"), R(200, headers={"Access-Control-Allow-Origin": "*"}))
    mock_http(h)

    result = await cross_validate_findings(
        "http://test.local/",
        {},
        [{"name": "CORS 通配符"}],
        is_https=False,
    )

    # Both main and the discovered subresource carry ACAO=* -> 95.
    assert result["CORS 通配符"]["confidence"] == 95
    assert any(r["path"] == "/assets/app.js" for r in h.requests)


async def test_d2_skips_index_html_when_url_is_index(mock_http):
    """D2 skips /index.html when the scanned URL is already /index.html."""
    h = MockHandler()
    # XFO present on both the URL (D1 HEADs the URL) and "/" (D2 scans only "/").
    h.route(M(method="HEAD", path="/"), R(200, headers={"X-Frame-Options": "DENY"}))
    h.route(M(method="HEAD", path="/index.html"), R(200, headers={"X-Frame-Options": "DENY"}))
    mock_http(h)

    result = await cross_validate_findings(
        "http://test.local/index.html",
        {},
        [{"name": "缺少 X-Frame-Options"}],
        is_https=False,
    )

    # XFO present in D1 (url=/index.html) and D2 (/) -> confidence 30.
    assert result["缺少 X-Frame-Options"]["confidence"] == 30
    # D1 issues exactly 2 HEAD requests to the URL (/index.html).  Because the URL
    # *is* /index.html, D2 must skip it; otherwise there would be a 3rd HEAD to
    # /index.html from D2.
    head_index_count = sum(
        1 for r in h.requests if r["method"] == "HEAD" and r["path"] == "/index.html"
    )
    assert head_index_count == 2, "D2 did not skip /index.html"
