"""Extended pytest tests for uncovered endpoints and internal helper functions in main.py.

Covers:
1. Internal helper functions (hash_password, verify_password, create_token,
   verify_token, get_db, require_login, get_current_user, sanitize_url,
   get_db_connection).
2. Extended endpoint tests (auto-fix, auto-fix-via-cloudflare, ai/chat, ai/test,
   ai-advisor, batch-scan, assets, apply-fix-and-rescan, compare, alerts,
   compliance/summary, cve/sync).
3. Additional endpoint tests for partially covered endpoints (dashboard, history,
   trend, monitors, targets, scans/comment, finding/feedback).

Patterns follow tests/test_main_endpoints.py:
- Set DB_DIR/DB_NAME to a temp path BEFORE importing main.
- Login as the "demo" user to obtain a bearer token.
- Use ``Authorization: Bearer <token>`` for protected endpoints.
"""

import asyncio
import json
import os
import sqlite3
import sys
import time
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

# --- Test DB setup (must happen before importing main) ---
os.environ["DB_DIR"] = "/tmp/v11-test"
os.environ["DB_NAME"] = "test.db"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.makedirs("/tmp/v11-test", exist_ok=True)

from fastapi.testclient import TestClient  # noqa: E402

import main  # noqa: E402

main.init_db()

client = TestClient(main.app)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _login_demo() -> str:
    """Login as the demo user (registering first if necessary). Returns token."""
    resp = client.post("/api/login", json={"username": "demo", "password": "demo123"})
    if resp.status_code != 200:
        client.post(
            "/api/register",
            json={
                "username": "demo",
                "password": "demo123",
                "email": "demo@example.com",
            },
        )
        resp = client.post(
            "/api/login", json={"username": "demo", "password": "demo123"}
        )
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return resp.json()["token"]


def _auth_headers() -> dict:
    return {"Authorization": f"Bearer {_login_demo()}"}


def _demo_user_id() -> int:
    conn = main.get_db()
    try:
        row = conn.execute("SELECT id FROM users WHERE username='demo'").fetchone()
        return row[0] if row else 1
    finally:
        conn.close()


def _ensure_credits(user_id: int, amount: int = 1000) -> None:
    """Top up the demo user's credits so credit-consuming endpoints work."""
    from app.services import credits_service

    credits_service.add_credits(user_id, amount, note="test top-up")


def _create_scan_record(
    user_id: int,
    url: str = "https://example.com",
    findings_json: str = "[]",
    score: int = 85,
    risk_level: str = "低风险",
) -> int:
    """Insert a scan record directly into the DB (no network). Returns scan id."""
    conn = main.get_db()
    try:
        cur = conn.execute(
            "INSERT INTO scans (user_id, url, score, risk_level, findings_count, "
            "findings_json, summary_json, crawled_pages, scan_type, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                user_id,
                url,
                score,
                risk_level,
                len(json.loads(findings_json)),
                findings_json,
                "{}",
                0,
                "test",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


# ===========================================================================
# 1. INTERNAL HELPER FUNCTIONS
# ===========================================================================

# --- hash_password / verify_password ---

def test_hash_password_returns_bcrypt_hash():
    """hash_password should return a bcrypt hash with the $2b$ prefix."""
    h = main.hash_password("mypassword")
    assert isinstance(h, str)
    assert h.startswith("$2b$")


def test_hash_password_different_each_time():
    """Each call produces a different hash due to random salt."""
    h1 = main.hash_password("secret")
    h2 = main.hash_password("secret")
    assert h1 != h2


def test_verify_password_correct():
    """verify_password returns True for the correct password."""
    h = main.hash_password("correct-pwd")
    assert main.verify_password("correct-pwd", h) is True


def test_verify_password_wrong():
    """verify_password returns False for a wrong password."""
    h = main.hash_password("correct-pwd")
    assert main.verify_password("wrong-pwd", h) is False


def test_hash_password_truncates_long_input():
    """Passwords longer than 72 bytes are truncated but still verify."""
    long_pwd = "a" * 100
    h = main.hash_password(long_pwd)
    # The truncated version (first 72 bytes) should verify
    assert main.verify_password(long_pwd, h) is True
    # A password that shares the first 72 bytes also verifies (truncation)
    assert main.verify_password("a" * 72, h) is True


def test_verify_password_empty_string():
    """verify_password handles empty strings without crashing."""
    h = main.hash_password("")
    assert main.verify_password("", h) is True
    assert main.verify_password("x", h) is False


# --- create_token / verify_token ---

def test_create_token_returns_nonempty_string():
    """create_token returns a non-empty JWT string."""
    tok = main.create_token(1, "testuser")
    assert isinstance(tok, str)
    assert len(tok) > 20


def test_create_token_contains_payload():
    """The decoded token contains user_id, username, role, team_id and exp."""
    tok = main.create_token(42, "alice", role="admin", team_id=7)
    payload = main.jwt.decode(tok, main.settings.jwt_secret, algorithms=["HS256"])
    assert payload["user_id"] == 42
    assert payload["username"] == "alice"
    assert payload["role"] == "admin"
    assert payload["team_id"] == 7
    assert "exp" in payload


def test_create_token_default_role_and_team():
    """create_token defaults role to 'member' and team_id to 0."""
    tok = main.create_token(1, "bob")
    payload = main.jwt.decode(tok, main.settings.jwt_secret, algorithms=["HS256"])
    assert payload["role"] == "member"
    assert payload["team_id"] == 0


def test_verify_token_valid():
    """verify_token decodes a valid token and returns the payload dict."""
    tok = main.create_token(99, "charlie")
    payload = main.verify_token(tok)
    assert payload is not None
    assert payload["user_id"] == 99
    assert payload["username"] == "charlie"


def test_verify_token_invalid_returns_none():
    """verify_token returns None for a garbage token."""
    assert main.verify_token("not.a.real.token") is None


def test_verify_token_empty_returns_none():
    """verify_token returns None for an empty string."""
    assert main.verify_token("") is None


def test_verify_token_wrong_secret_returns_none():
    """verify_token returns None for a token signed with a different secret."""
    tok = main.jwt.encode(
        {"user_id": 1, "username": "x", "exp": time.time() + 3600},
        "wrong-secret",
        algorithm="HS256",
    )
    assert main.verify_token(tok) is None


def test_verify_token_expired_returns_none():
    """verify_token returns None for an expired token."""
    tok = main.jwt.encode(
        {"user_id": 1, "username": "x", "exp": time.time() - 3600},
        main.settings.jwt_secret,
        algorithm="HS256",
    )
    assert main.verify_token(tok) is None


# --- get_db / get_db_connection ---

def test_get_db_returns_sqlite_connection():
    """get_db returns a sqlite3.Connection with Row factory."""
    conn = main.get_db()
    try:
        assert isinstance(conn, sqlite3.Connection)
        assert conn.row_factory is sqlite3.Row
    finally:
        conn.close()


def test_get_db_executes_query():
    """get_db returns a connection that can execute queries."""
    conn = main.get_db()
    try:
        row = conn.execute("SELECT 1 as val").fetchone()
        assert row["val"] == 1
    finally:
        conn.close()


def test_get_db_connection_context_manager():
    """get_db_connection works as a context manager and auto-closes."""
    from app.db.session import get_db_connection

    with get_db_connection() as conn:
        row = conn.execute("SELECT 42 as answer").fetchone()
        assert row["answer"] == 42
    # After the context, the connection is closed; using it raises an error
    with pytest.raises(Exception):
        conn.execute("SELECT 1")


# --- require_login / get_current_user ---

def test_require_login_no_header_raises():
    """require_login raises UnauthorizedException when no Authorization header."""
    from app.core.exceptions import UnauthorizedException

    with pytest.raises(UnauthorizedException):
        asyncio.run(main.require_login(authorization=None))


def test_require_login_malformed_header_raises():
    """require_login raises when the header does not start with 'Bearer '."""
    from app.core.exceptions import UnauthorizedException

    with pytest.raises(UnauthorizedException):
        asyncio.run(main.require_login(authorization="Token abc"))


def test_require_login_invalid_token_raises():
    """require_login raises for an invalid bearer token."""
    from app.core.exceptions import UnauthorizedException

    with pytest.raises(UnauthorizedException):
        asyncio.run(main.require_login(authorization="Bearer invalid.token.here"))


def test_require_login_valid_token_returns_user():
    """require_login returns the user dict for a valid token."""
    tok = main.create_token(5, "valid_user", role="member")
    user = asyncio.run(main.require_login(authorization=f"Bearer {tok}"))
    assert user is not None
    assert user["user_id"] == 5
    assert user["username"] == "valid_user"


def test_get_current_user_no_header_returns_none():
    """get_current_user returns None when no Authorization header is provided."""
    result = asyncio.run(main.get_current_user(authorization=None))
    assert result is None


def test_get_current_user_malformed_header_returns_none():
    """get_current_user returns None for a non-Bearer header."""
    result = asyncio.run(main.get_current_user(authorization="Basic abc"))
    assert result is None


def test_get_current_user_invalid_token_returns_none():
    """get_current_user returns None for an invalid token."""
    result = asyncio.run(
        main.get_current_user(authorization="Bearer garbage.token.value")
    )
    assert result is None


def test_get_current_user_valid_token_returns_user():
    """get_current_user returns the user dict for a valid token."""
    tok = main.create_token(77, "ghost")
    user = asyncio.run(main.get_current_user(authorization=f"Bearer {tok}"))
    assert user is not None
    assert user["user_id"] == 77
    assert user["username"] == "ghost"


# --- sanitize_url ---

def test_sanitize_url_allows_public_domain():
    """sanitize_url accepts a public domain and prepends https://."""
    result = main.sanitize_url("example.com")
    assert "example.com" in result
    assert result.startswith("https://")


def test_sanitize_url_allows_https_url():
    """sanitize_url accepts a full https URL."""
    result = main.sanitize_url("https://example.com/path")
    assert result == "https://example.com/path"


def test_sanitize_url_allows_http_url():
    """sanitize_url accepts a full http URL."""
    result = main.sanitize_url("http://example.com")
    assert result == "http://example.com"


def test_sanitize_url_blocks_empty():
    """sanitize_url raises ValueError for an empty string."""
    with pytest.raises(ValueError, match="不能为空"):
        main.sanitize_url("")


def test_sanitize_url_blocks_whitespace_only():
    """sanitize_url raises ValueError for whitespace-only input."""
    with pytest.raises(ValueError, match="不能为空"):
        main.sanitize_url("   ")


def test_sanitize_url_blocks_private_ip():
    """sanitize_url blocks the cloud metadata IP (SSRF protection)."""
    with pytest.raises(ValueError, match="内网或本地地址"):
        main.sanitize_url("http://169.254.169.254")


def test_sanitize_url_blocks_localhost():
    """sanitize_url blocks localhost (no dot in hostname)."""
    with pytest.raises(ValueError, match="域名"):
        main.sanitize_url("http://localhost")


def test_sanitize_url_blocks_loopback_ip():
    """sanitize_url blocks 127.0.0.1 (SSRF protection)."""
    with pytest.raises(ValueError, match="内网"):
        main.sanitize_url("http://127.0.0.1")


def test_sanitize_url_blocks_short_tld():
    """sanitize_url blocks domains with a TLD shorter than 2 characters."""
    with pytest.raises(ValueError, match="后缀太短|域名"):
        main.sanitize_url("http://example.x")


# ===========================================================================
# 2. EXTENDED ENDPOINT TESTS
# ===========================================================================

# --- POST /api/auto-fix ---

def test_auto_fix_requires_auth():
    """POST /api/auto-fix without a token returns 401."""
    resp = client.post("/api/auto-fix", json={"scan_id": 1})
    assert resp.status_code == 401


def test_auto_fix_missing_scan_id():
    """Missing scan_id returns success=False."""
    resp = client.post(
        "/api/auto-fix",
        json={"credentials": {"host": "1.2.3.4", "password": "pwd"}},
        headers=_auth_headers(),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False
    assert "scan_id" in body["error"]


def test_auto_fix_missing_credentials():
    """Missing host or password returns success=False."""
    scan_id = _create_scan_record(_demo_user_id())
    resp = client.post(
        "/api/auto-fix",
        json={"scan_id": scan_id, "credentials": {}},
        headers=_auth_headers(),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False
    assert "host" in body["error"] or "password" in body["error"]


def test_auto_fix_nonexistent_scan():
    """A non-existent scan_id returns success=False."""
    resp = client.post(
        "/api/auto-fix",
        json={
            "scan_id": 999999,
            "credentials": {"host": "10.0.0.1", "password": "pwd"},
        },
        headers=_auth_headers(),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False
    assert "不存在" in body["error"] or "权限" in body["error"]


def test_auto_fix_invalid_json_body():
    """A non-JSON body returns success=False."""
    resp = client.post(
        "/api/auto-fix",
        content="not json",
        headers={**_auth_headers(), "Content-Type": "application/json"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False


# --- POST /api/auto-fix-via-cloudflare ---

def test_auto_fix_cloudflare_requires_auth():
    """POST /api/auto-fix-via-cloudflare without a token returns 401."""
    resp = client.post(
        "/api/auto-fix-via-cloudflare",
        json={"scan_id": 1, "cf_token": "t", "cf_zone": "z"},
    )
    assert resp.status_code == 401


def test_auto_fix_cloudflare_missing_params():
    """Missing cf_token or cf_zone returns success=False."""
    resp = client.post(
        "/api/auto-fix-via-cloudflare",
        json={"scan_id": 1},
        headers=_auth_headers(),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False
    assert "cf_token" in body["error"] or "cf_zone" in body["error"]


def test_auto_fix_cloudflare_nonexistent_scan():
    """A non-existent scan returns success=False."""
    resp = client.post(
        "/api/auto-fix-via-cloudflare",
        json={"scan_id": 999999, "cf_token": "tok", "cf_zone": "example.com"},
        headers=_auth_headers(),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False
    assert "不存在" in body["error"]


def test_auto_fix_cloudflare_no_findings_returns_zero():
    """A scan with no fixable findings returns applied=0 without API calls."""
    scan_id = _create_scan_record(_demo_user_id(), findings_json="[]")
    resp = client.post(
        "/api/auto-fix-via-cloudflare",
        json={"scan_id": scan_id, "cf_token": "tok", "cf_zone": "example.com"},
        headers=_auth_headers(),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["applied"] == 0


def test_auto_fix_cloudflare_invalid_json_body():
    """A non-JSON body returns success=False."""
    resp = client.post(
        "/api/auto-fix-via-cloudflare",
        content="not json",
        headers={**_auth_headers(), "Content-Type": "application/json"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False


# --- POST /api/ai/chat ---

def test_ai_chat_requires_auth():
    """POST /api/ai/chat without a token returns 401."""
    resp = client.post("/api/ai/chat", json={"message": "hello"})
    assert resp.status_code == 401


def test_ai_chat_empty_message():
    """An empty message returns success=False."""
    resp = client.post(
        "/api/ai/chat", json={"message": ""}, headers=_auth_headers()
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False
    assert "空" in body["error"]


def test_ai_chat_invalid_json_body():
    """A non-JSON body returns success=False."""
    resp = client.post(
        "/api/ai/chat",
        content="not json",
        headers={**_auth_headers(), "Content-Type": "application/json"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False


def test_ai_chat_keyword_hsts():
    """Asking about HSTS returns a non-empty response (keyword fallback)."""
    resp = client.post(
        "/api/ai/chat",
        json={"message": "HSTS 是什么？"},
        headers=_auth_headers(),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert len(body["response"]) > 0
    assert "memory_used" in body
    assert "llm_used" in body
    assert "insights_summary" in body


def test_ai_chat_greeting_keyword():
    """A greeting message returns a non-empty response."""
    resp = client.post(
        "/api/ai/chat",
        json={"message": "你好"},
        headers=_auth_headers(),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert len(body["response"]) > 0


def test_ai_chat_response_structure():
    """The response has the expected keys."""
    resp = client.post(
        "/api/ai/chat",
        json={"message": "怎么修 HSTS"},
        headers=_auth_headers(),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "response" in body
    assert "memory_used" in body
    assert "llm_used" in body
    assert "llm_provider" in body
    assert "insights_summary" in body
    summary = body["insights_summary"]
    assert "total_scans" in summary
    assert "persistent_count" in summary
    assert "predicted_score" in summary


# --- POST /api/ai/test ---

def test_ai_test_requires_auth():
    """POST /api/ai/test without a token returns 401."""
    resp = client.post("/api/ai/test", json={"message": "hi"})
    assert resp.status_code == 401


def test_ai_test_without_llm_config_returns_fallback():
    """When LLM is not configured, returns success=False with fallback=True."""
    resp = client.post(
        "/api/ai/test", json={"message": "hello"}, headers=_auth_headers()
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False
    assert body.get("fallback") is True
    assert "LLM" in body["error"] or "API Key" in body["error"]


def test_ai_test_no_body_does_not_crash():
    """POST /api/ai/test with no JSON body still returns a response."""
    resp = client.post("/api/ai/test", headers=_auth_headers())
    assert resp.status_code == 200
    body = resp.json()
    # LLM not configured -> fallback
    assert body.get("fallback") is True or body.get("success") is True


# --- POST /api/ai-advisor ---

def test_ai_advisor_empty_message_returns_guidance():
    """An empty message returns a guidance reply from the rule engine."""
    resp = client.post(
        "/api/ai-advisor", json={"message": ""}, headers=_auth_headers()
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "reply" in body
    assert body["source"] == "rule_engine"


def test_ai_advisor_invalid_scan_id_graceful():
    """An invalid scan_id does not crash; falls back to rule engine."""
    resp = client.post(
        "/api/ai-advisor",
        json={"scan_id": 999999, "message": "总结一下"},
        headers=_auth_headers(),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "reply" in body or "answer" in body


def test_ai_advisor_keyword_csp():
    """Asking about CSP returns a reply mentioning Content-Security-Policy."""
    resp = client.post(
        "/api/ai-advisor",
        json={"message": "怎么修 CSP"},
        headers=_auth_headers(),
    )
    assert resp.status_code == 200
    body = resp.json()
    reply = body.get("reply") or body.get("answer", "")
    assert "Content-Security-Policy" in reply or "CSP" in reply


# --- POST /api/batch-scan ---

def test_batch_scan_requires_auth():
    """POST /api/batch-scan without a token returns 401."""
    resp = client.post(
        "/api/batch-scan", json={"urls": ["https://example.com"]}
    )
    assert resp.status_code == 401


def test_batch_scan_empty_list_returns_400():
    """An empty URL list returns 400."""
    resp = client.post(
        "/api/batch-scan", json={"urls": []}, headers=_auth_headers()
    )
    assert resp.status_code == 400


def test_batch_scan_too_many_urls_returns_422():
    """More than 5 URLs returns 422 (validator rejects)."""
    resp = client.post(
        "/api/batch-scan",
        json={"urls": ["example.com"] * 6},
        headers=_auth_headers(),
    )
    assert resp.status_code in (400, 422)


def test_batch_scan_not_authorized():
    """authorized=False returns success=False with an authorization error."""
    resp = client.post(
        "/api/batch-scan",
        json={"urls": ["https://example.com"], "authorized": False},
        headers=_auth_headers(),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False
    assert "authorized" in body.get("error", "").lower() or "授权" in body.get(
        "error", ""
    )


def test_batch_scan_invalid_url_returns_422():
    """An SSRF-blocked URL in the list causes a 422 validation error."""
    resp = client.post(
        "/api/batch-scan",
        json={"urls": ["http://localhost"], "authorized": True},
        headers=_auth_headers(),
    )
    assert resp.status_code == 422


# --- POST /api/assets ---

def test_assets_create_requires_auth():
    """POST /api/assets without a token returns 401."""
    resp = client.post("/api/assets", json={"domain": "example.com"})
    assert resp.status_code == 401


def test_assets_list_requires_auth():
    """GET /api/assets without a token returns 401."""
    resp = client.get("/api/assets")
    assert resp.status_code == 401


def test_assets_create_and_list():
    """Creating an asset returns an asset_id; listing shows it."""
    headers = _auth_headers()
    domain = f"asset-test-{int(time.time() * 1000)}.com"
    resp = client.post(
        "/api/assets",
        json={"domain": domain, "owner": "team-a", "description": "test asset"},
        headers=headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "asset_id" in body
    asset_id = body["asset_id"]

    listing = client.get("/api/assets", headers=headers)
    assert listing.status_code == 200
    assets = listing.json()["assets"]
    assert any(a["id"] == asset_id for a in assets)


def test_assets_create_strips_protocol():
    """Creating an asset with a full URL strips the protocol."""
    headers = _auth_headers()
    domain = f"strip-test-{int(time.time() * 1000)}.com"
    resp = client.post(
        "/api/assets",
        json={"domain": "https://" + domain},
        headers=headers,
    )
    assert resp.status_code == 200
    listing = client.get("/api/assets", headers=headers)
    assets = listing.json()["assets"]
    matched = [a for a in assets if a["domain"] == domain]
    assert len(matched) >= 1


def test_assets_create_empty_domain_returns_422():
    """An empty domain returns 422 (validation error)."""
    resp = client.post(
        "/api/assets", json={"domain": ""}, headers=_auth_headers()
    )
    assert resp.status_code == 422


def test_asset_delete_requires_auth():
    """DELETE /api/assets/{id} without a token returns 401."""
    resp = client.delete("/api/assets/1")
    assert resp.status_code == 401


def test_asset_delete_nonexistent_returns_404():
    """Deleting a non-existent asset returns 404."""
    resp = client.delete("/api/assets/999999", headers=_auth_headers())
    assert resp.status_code == 404


# --- POST /api/assets/{asset_id}/scan ---

def test_asset_scan_requires_auth():
    """POST /api/assets/{id}/scan without a token returns 401."""
    resp = client.post("/api/assets/1/scan")
    assert resp.status_code == 401


def test_asset_scan_nonexistent_returns_404():
    """Scanning a non-existent asset returns 404."""
    resp = client.post("/api/assets/999999/scan", headers=_auth_headers())
    assert resp.status_code == 404


def test_asset_scan_creates_scan_record():
    """Scanning an existing asset with mocked network produces a scan."""
    headers = _auth_headers()
    # Create an asset
    domain = f"scan-asset-{int(time.time() * 1000)}.com"
    create = client.post(
        "/api/assets",
        json={"domain": domain, "owner": "", "description": ""},
        headers=headers,
    )
    asset_id = create.json()["asset_id"]

    # Mock network-dependent functions to avoid real HTTP calls
    fake_headers = {"content-type": "text/html", "server": "nginx"}
    with patch.object(
        main, "fetch_headers", new_callable=AsyncMock,
        return_value=(fake_headers, True, "https://" + domain, None),
    ), patch.object(
        main, "get_ssl_info", new_callable=AsyncMock,
        return_value={"has_cert": True, "days_left": 90, "expired": False, "weak": False},
    ), patch.object(
        main, "check_sensitive_paths", new_callable=AsyncMock,
        return_value=[],
    ):
        resp = client.post(f"/api/assets/{asset_id}/scan", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "scan_id" in body
    assert body["scan_id"] > 0


def test_asset_scan_detects_source_map_assets():
    """Asset scans should surface exposed source maps as scan findings."""
    headers = _auth_headers()
    domain = f"sourcemap-asset-{int(time.time() * 1000)}.com"
    create = client.post(
        "/api/assets",
        json={"domain": domain, "owner": "", "description": ""},
        headers=headers,
    )
    assert create.status_code == 200
    asset_id = create.json()["asset_id"]

    fake_headers = {"content-type": "text/html", "server": "nginx"}

    def handler(request):
        if request.url.path == "/_next/build-manifest.json":
            return __import__("httpx").Response(
                200,
                text='{"devFiles":["static/chunks/react-refresh.js"],"polyfillFiles":["static/chunks/polyfills.js"],"pages":{"/":["static/chunks/pages/index.js"]}}',
                headers={"Content-Type": "application/json"},
            )
        return __import__("httpx").Response(404, text="not found")

    http_client = __import__("httpx").AsyncClient(
        transport=__import__("httpx").MockTransport(handler)
    )

    try:
        with patch.object(
            main,
            "fetch_headers",
            new_callable=AsyncMock,
            return_value=(fake_headers, True, "https://" + domain, None),
        ), patch.object(
            main,
            "get_ssl_info",
            new_callable=AsyncMock,
            return_value={"has_cert": True, "days_left": 90, "expired": False, "weak": False},
        ), patch.object(
            main,
            "get_httpx_client",
            return_value=http_client,
        ):
            resp = client.post(f"/api/assets/{asset_id}/scan", headers=headers)
    finally:
        asyncio.run(http_client.aclose())

    assert resp.status_code == 200
    body = resp.json()
    scan_id = body["scan_id"]
    conn = main.get_db()
    try:
        row = conn.execute(
            "SELECT findings_json FROM scans WHERE id=?", (scan_id,)
        ).fetchone()
    finally:
        conn.close()

    assert row is not None
    assert "/_next/build-manifest.json" in row[0]


def test_asset_scan_detects_docker_compose_assets():
    """Asset scans should surface exposed deployment configs as scan findings."""
    headers = _auth_headers()
    domain = f"compose-asset-{int(time.time() * 1000)}.com"
    create = client.post(
        "/api/assets",
        json={"domain": domain, "owner": "", "description": ""},
        headers=headers,
    )
    assert create.status_code == 200
    asset_id = create.json()["asset_id"]

    fake_headers = {"content-type": "text/html", "server": "nginx"}

    def handler(request):
        if request.url.path == "/docker-compose.yml":
            return __import__("httpx").Response(
                200,
                text=(
                    "version: '3.8'\n"
                    "services:\n"
                    "  web:\n"
                    "    image: vuln-sentinel:latest\n"
                    "    environment:\n"
                    "      - DATABASE_URL=postgres://user:pass@db:5432/app\n"
                    "    ports:\n"
                    "      - '8080:8080'\n"
                ),
                headers={"Content-Type": "text/yaml"},
            )
        return __import__("httpx").Response(404, text="not found")

    http_client = __import__("httpx").AsyncClient(
        transport=__import__("httpx").MockTransport(handler)
    )

    try:
        with patch.object(
            main,
            "fetch_headers",
            new_callable=AsyncMock,
            return_value=(fake_headers, True, "https://" + domain, None),
        ), patch.object(
            main,
            "get_ssl_info",
            new_callable=AsyncMock,
            return_value={"has_cert": True, "days_left": 90, "expired": False, "weak": False},
        ), patch.object(
            main,
            "get_httpx_client",
            return_value=http_client,
        ):
            resp = client.post(f"/api/assets/{asset_id}/scan", headers=headers)
    finally:
        asyncio.run(http_client.aclose())

    assert resp.status_code == 200
    body = resp.json()
    scan_id = body["scan_id"]
    conn = main.get_db()
    try:
        row = conn.execute(
            "SELECT findings_json FROM scans WHERE id=?", (scan_id,)
        ).fetchone()
    finally:
        conn.close()

    assert row is not None
    assert "/docker-compose.yml" in row[0]


# --- POST /api/apply-fix-and-rescan ---

def test_apply_fix_and_rescan_requires_auth():
    """POST /api/apply-fix-and-rescan without a token returns 401."""
    resp = client.post(
        "/api/apply-fix-and-rescan", json={"url": "example.com"}
    )
    assert resp.status_code == 401


def test_apply_fix_and_rescan_invalid_url_422():
    """An SSRF-blocked URL causes a 422 validation error."""
    resp = client.post(
        "/api/apply-fix-and-rescan",
        json={"url": "http://localhost"},
        headers=_auth_headers(),
    )
    assert resp.status_code == 422


def test_apply_fix_and_rescan_fetch_error():
    """When fetch_headers returns an error, the endpoint returns success=False."""
    _ensure_credits(_demo_user_id())
    with patch.object(
        main, "fetch_headers", new_callable=AsyncMock,
        return_value=({}, False, "", "CONNECTION_ERROR"),
    ):
        resp = client.post(
            "/api/apply-fix-and-rescan",
            json={"url": "example.com"},
            headers=_auth_headers(),
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False
    assert "error" in body


def test_apply_fix_and_rescan_success_with_mock():
    """With mocked network, the endpoint returns a comparison result."""
    _ensure_credits(_demo_user_id())
    url = "example.com"
    fake_headers = {"content-type": "text/html", "server": "nginx"}
    with patch.object(
        main, "fetch_headers", new_callable=AsyncMock,
        return_value=(fake_headers, True, "https://" + url, None),
    ), patch.object(
        main, "get_ssl_info", new_callable=AsyncMock,
        return_value={"has_cert": True, "days_left": 90, "expired": False, "weak": False},
    ), patch.object(
        main, "check_sensitive_paths", new_callable=AsyncMock,
        return_value=[],
    ):
        resp = client.post(
            "/api/apply-fix-and-rescan",
            json={"url": url},
            headers=_auth_headers(),
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "scan_id" in body
    assert "score" in body
    assert "findings" in body
    assert "delta" in body


# --- POST /api/compare ---

def test_compare_requires_auth():
    """POST /api/compare without a token returns 401."""
    resp = client.post("/api/compare?a=1&b=2")
    assert resp.status_code == 401


def test_compare_missing_params_422():
    """Missing query params a and b returns 422."""
    resp = client.post("/api/compare", headers=_auth_headers())
    assert resp.status_code == 422


def test_compare_nonexistent_scans_404():
    """Comparing non-existent scan IDs returns 404."""
    resp = client.post(
        "/api/compare?a=999999&b=999998", headers=_auth_headers()
    )
    assert resp.status_code == 404


def test_compare_two_scans():
    """Comparing two existing scans returns the diff structure."""
    user_id = _demo_user_id()
    scan_a = _create_scan_record(
        user_id,
        findings_json=json.dumps(
            [{"name": "缺少 HSTS", "severity": "high"}]
        ),
        score=70,
    )
    scan_b = _create_scan_record(
        user_id,
        findings_json=json.dumps(
            [{"name": "缺少 HSTS", "severity": "high"},
             {"name": "缺少 CSP", "severity": "high"}]
        ),
        score=80,
    )
    resp = client.post(
        f"/api/compare?a={scan_a}&b={scan_b}", headers=_auth_headers()
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["a"]["id"] == scan_a
    assert body["b"]["id"] == scan_b
    assert "fixed" in body
    assert "new" in body
    assert "score_diff" in body
    assert isinstance(body["fixed"], list)
    assert isinstance(body["new"], list)
    assert body["score_diff"] == 80 - 70


def test_compare_same_scan():
    """Comparing a scan with itself returns empty fixed/new lists."""
    user_id = _demo_user_id()
    scan_id = _create_scan_record(
        user_id,
        findings_json=json.dumps([{"name": "X", "severity": "low"}]),
    )
    resp = client.post(
        f"/api/compare?a={scan_id}&b={scan_id}", headers=_auth_headers()
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["fixed"] == []
    assert body["new"] == []
    assert body["score_diff"] == 0


# --- GET /api/alerts ---

def test_alerts_requires_auth():
    """GET /api/alerts without a token returns 401."""
    resp = client.get("/api/alerts")
    assert resp.status_code == 401


def test_alerts_returns_structure():
    """GET /api/alerts returns alerts list and count."""
    headers = _auth_headers()
    resp = client.get("/api/alerts", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "alerts" in body
    assert "count" in body
    assert body["count"] == len(body["alerts"])


def test_alerts_limit_param():
    """The limit query param caps the number of returned alerts."""
    headers = _auth_headers()
    resp = client.get("/api/alerts?limit=5", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["alerts"]) <= 5


def test_alerts_unread_only_param():
    """unread_only=True filters to unread alerts."""
    headers = _auth_headers()
    resp = client.get("/api/alerts?unread_only=true", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    for a in body["alerts"]:
        assert a.get("is_read") == 0


def test_alerts_unread_count_requires_auth():
    """GET /api/alerts/unread-count without a token returns 401."""
    resp = client.get("/api/alerts/unread-count")
    assert resp.status_code == 401


def test_alerts_unread_count_returns_int():
    """GET /api/alerts/unread-count returns an integer count."""
    resp = client.get("/api/alerts/unread-count", headers=_auth_headers())
    assert resp.status_code == 200
    body = resp.json()
    assert "unread_count" in body
    assert isinstance(body["unread_count"], int)


# --- POST /api/alerts/{alert_id}/read ---

def test_alerts_mark_read_requires_auth():
    """POST /api/alerts/{id}/read without a token returns 401."""
    resp = client.post("/api/alerts/1/read")
    assert resp.status_code == 401


def test_alerts_mark_read_nonexistent_returns_success():
    """Marking a non-existent alert as read is idempotent (success=True)."""
    resp = client.post("/api/alerts/999999/read", headers=_auth_headers())
    assert resp.status_code == 200
    assert resp.json()["success"] is True


def test_alerts_mark_read_and_verify():
    """Mark an alert as read and verify is_read flips to 1."""
    user_id = _demo_user_id()
    conn = main.get_db()
    try:
        conn.execute(
            "INSERT INTO alerts (user_id, target_id, alert_type, message, "
            "details_json, created_at, is_read) VALUES (?,?,?,?,?,?,?)",
            (user_id, 1, "score_drop", "test mark read", "{}",
             datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0),
        )
        conn.commit()
        alert_id = conn.execute(
            "SELECT id FROM alerts WHERE user_id=? ORDER BY id DESC LIMIT 1",
            (user_id,),
        ).fetchone()["id"]
    finally:
        conn.close()

    resp = client.post(f"/api/alerts/{alert_id}/read", headers=_auth_headers())
    assert resp.status_code == 200
    assert resp.json()["success"] is True

    conn = main.get_db()
    try:
        row = conn.execute(
            "SELECT is_read FROM alerts WHERE id=?", (alert_id,)
        ).fetchone()
    finally:
        conn.close()
    assert row["is_read"] == 1


# --- GET /api/compliance/summary ---

def test_compliance_summary_requires_auth():
    """GET /api/compliance/summary without a token returns 401."""
    resp = client.get("/api/compliance/summary")
    assert resp.status_code == 401


def test_compliance_summary_returns_data():
    """GET /api/compliance/summary returns the compliance rules summary."""
    resp = client.get("/api/compliance/summary", headers=_auth_headers())
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert "restricted_tlds" in data
    assert "blocked_networks" in data
    assert "requires_authorization" in data
    assert data["requires_authorization"] is True


# --- POST /api/cve/sync ---

def test_cve_sync_requires_auth():
    """POST /api/cve/sync without a token returns 401."""
    resp = client.post("/api/cve/sync")
    assert resp.status_code == 401


def test_cve_sync_invalid_days_zero_422():
    """days=0 is below the minimum (ge=1) and returns 422."""
    resp = client.post("/api/cve/sync?days=0", headers=_auth_headers())
    assert resp.status_code == 422


def test_cve_sync_invalid_days_too_large_422():
    """days=121 exceeds the maximum (le=120) and returns 422."""
    resp = client.post("/api/cve/sync?days=121", headers=_auth_headers())
    assert resp.status_code == 422


def test_cve_sync_success_with_mock():
    """With a mocked NVD sync, the endpoint returns saved/fetched counts."""
    with patch.object(
        main.vuln_intel_service,
        "sync_recent_nvd_cves",
        new_callable=AsyncMock,
        return_value=(5, 10),
    ):
        resp = client.post(
            "/api/cve/sync?days=7", headers=_auth_headers()
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert data["saved"] == 5
    assert data["fetched"] == 10
    assert data["days"] == 7


# ===========================================================================
# 3. ADDITIONAL ENDPOINT TESTS (partially covered)
# ===========================================================================

# --- GET /api/dashboard ---

def test_dashboard_requires_auth():
    """GET /api/dashboard without a token returns 401."""
    resp = client.get("/api/dashboard")
    assert resp.status_code == 401


def test_dashboard_data_types():
    """Dashboard returns correct data types for each field."""
    resp = client.get("/api/dashboard", headers=_auth_headers())
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body["total_scans"], int)
    assert isinstance(body["high_risk_count"], int)
    assert isinstance(body["fixed_count"], int)
    assert isinstance(body["recent_scans"], list)


def test_dashboard_recent_scans_structure():
    """Each item in recent_scans has id, url, score, risk_level, time."""
    user_id = _demo_user_id()
    _create_scan_record(user_id, url="https://dash-test.com")
    resp = client.get("/api/dashboard", headers=_auth_headers())
    assert resp.status_code == 200
    body = resp.json()
    if body["recent_scans"]:
        scan = body["recent_scans"][0]
        assert "id" in scan
        assert "url" in scan
        assert "score" in scan
        assert "risk_level" in scan
        assert "time" in scan


# --- GET /api/history ---

def test_history_requires_auth():
    """GET /api/history without a token returns 401."""
    resp = client.get("/api/history")
    assert resp.status_code == 401


def test_history_pagination():
    """History respects limit and offset params."""
    user_id = _demo_user_id()
    for _ in range(3):
        _create_scan_record(user_id, url="https://pag-test.com")
    resp = client.get(
        "/api/history?limit=2&offset=0", headers=_auth_headers()
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert len(data["history"]) <= 2
    assert body["meta"]["limit"] == 2
    assert body["meta"]["offset"] == 0


def test_history_offset_param():
    """History with offset skips the first N records."""
    user_id = _demo_user_id()
    for _ in range(3):
        _create_scan_record(user_id, url="https://offset-test.com")
    resp_first = client.get(
        "/api/history?limit=10&offset=0", headers=_auth_headers()
    )
    resp_offset = client.get(
        "/api/history?limit=10&offset=2", headers=_auth_headers()
    )
    total_first = resp_first.json()["meta"]["total"]
    total_offset = resp_offset.json()["meta"]["total"]
    # total should be the same regardless of offset
    assert total_first == total_offset
    # offset result should have fewer or equal items
    assert len(resp_offset.json()["data"]["history"]) <= len(
        resp_first.json()["data"]["history"]
    )


def test_history_url_filter():
    """History with url filter returns only matching records."""
    user_id = _demo_user_id()
    target_url = f"https://filter-test-{int(time.time())}.com"
    _create_scan_record(user_id, url=target_url)
    resp = client.get(
        f"/api/history?url={target_url}", headers=_auth_headers()
    )
    assert resp.status_code == 200
    body = resp.json()
    for item in body["data"]["history"]:
        assert item["url"] == target_url


def test_history_stats_structure():
    """History stats contain scan_count and fixed_count."""
    resp = client.get("/api/history", headers=_auth_headers())
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "stats" in data
    assert "scan_count" in data["stats"]
    assert "fixed_count" in data["stats"]


# --- GET /api/trend ---

def test_trend_requires_auth():
    """GET /api/trend without a token returns 401."""
    resp = client.get("/api/trend")
    assert resp.status_code == 401


def test_trend_response_structure():
    """Trend returns urls, series, and summary with all expected keys."""
    resp = client.get("/api/trend", headers=_auth_headers())
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert "urls" in data
    assert "series" in data
    assert "summary" in data
    summary = data["summary"]
    assert "total_scans" in summary
    assert "avg_score" in summary
    assert "max_score" in summary
    assert "min_score" in summary
    assert "latest_score" in summary
    assert "improved" in summary


def test_trend_limit_param():
    """Trend respects the limit param."""
    resp = client.get("/api/trend?limit=5", headers=_auth_headers())
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True


def test_trend_with_data():
    """After creating scan records, trend returns the URL in urls."""
    user_id = _demo_user_id()
    target_url = f"https://trend-test-{int(time.time())}.com"
    _create_scan_record(user_id, url=target_url, score=90)
    _create_scan_record(user_id, url=target_url, score=95)
    resp = client.get("/api/trend", headers=_auth_headers())
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert target_url in data["urls"]


# --- POST /api/monitors ---

def test_monitor_create_requires_auth():
    """POST /api/monitors without a token returns 401."""
    resp = client.post("/api/monitors", json={"url": "https://example.com"})
    assert resp.status_code == 401


def test_monitor_create_valid():
    """Creating a monitor with valid data returns monitor_id."""
    resp = client.post(
        "/api/monitors",
        json={"url": "https://example.com", "frequency_hours": 24},
        headers=_auth_headers(),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "monitor_id" in body
    assert body["url"] == "https://example.com"
    assert body["frequency_hours"] == 24


def test_monitor_create_empty_url():
    """An empty URL returns success=False."""
    resp = client.post(
        "/api/monitors", json={"url": ""}, headers=_auth_headers()
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False


def test_monitor_create_invalid_url_ssrf():
    """An SSRF-blocked URL returns success=False."""
    resp = client.post(
        "/api/monitors",
        json={"url": "http://localhost"},
        headers=_auth_headers(),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False


def test_monitor_create_invalid_frequency():
    """A frequency outside 1-168 returns success=False."""
    resp = client.post(
        "/api/monitors",
        json={"url": "https://example.com", "frequency_hours": 0},
        headers=_auth_headers(),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False

    resp2 = client.post(
        "/api/monitors",
        json={"url": "https://example.com", "frequency_hours": 200},
        headers=_auth_headers(),
    )
    assert resp2.status_code == 200
    assert resp2.json()["success"] is False


# --- POST /api/targets ---

def test_targets_create_requires_auth():
    """POST /api/targets without a token returns 401."""
    resp = client.post("/api/targets", json={"url": "https://example.com"})
    assert resp.status_code == 401


def test_targets_create_valid():
    """Creating a target with valid data returns success=True."""
    url = f"https://target-test-{int(time.time())}.com"
    resp = client.post(
        "/api/targets",
        json={"url": url, "schedule": "daily"},
        headers=_auth_headers(),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True

    listing = client.get("/api/targets", headers=_auth_headers())
    assert listing.status_code == 200
    targets = listing.json()["targets"]
    assert any(t["url"] == url for t in targets)


def test_targets_create_invalid_schedule_422():
    """An invalid schedule value returns 422."""
    resp = client.post(
        "/api/targets",
        json={"url": "https://example.com", "schedule": "hourly"},
        headers=_auth_headers(),
    )
    assert resp.status_code == 422


def test_targets_create_ssrf_url_422():
    """An SSRF-blocked URL returns 422."""
    resp = client.post(
        "/api/targets",
        json={"url": "http://localhost", "schedule": "daily"},
        headers=_auth_headers(),
    )
    assert resp.status_code == 422


def test_targets_create_default_schedule():
    """Creating a target without schedule defaults to 'daily'."""
    url = f"https://default-sched-{int(time.time())}.com"
    resp = client.post(
        "/api/targets", json={"url": url}, headers=_auth_headers()
    )
    assert resp.status_code == 200
    listing = client.get("/api/targets", headers=_auth_headers())
    targets = listing.json()["targets"]
    matched = [t for t in targets if t["url"] == url]
    assert len(matched) >= 1
    assert matched[0]["schedule"] == "daily"


# --- POST /api/scans/{scan_id}/comment ---

def test_scan_comment_requires_auth():
    """POST /api/scans/{id}/comment without a token returns 401."""
    resp = client.post("/api/scans/1/comment", json={"comment": "hi"})
    assert resp.status_code == 401


def test_scan_comment_empty_returns_error():
    """An empty comment returns success=False."""
    scan_id = _create_scan_record(_demo_user_id())
    resp = client.post(
        f"/api/scans/{scan_id}/comment",
        json={"comment": ""},
        headers=_auth_headers(),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False


def test_scan_comment_add_and_list():
    """Adding a comment succeeds and it appears in the listing."""
    headers = _auth_headers()
    scan_id = _create_scan_record(_demo_user_id())
    resp = client.post(
        f"/api/scans/{scan_id}/comment",
        json={"comment": "needs urgent review"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["success"] is True

    listing = client.get(
        f"/api/scans/{scan_id}/comments", headers=headers
    )
    assert listing.status_code == 200
    body = listing.json()
    assert body["success"] is True
    assert body["total"] >= 1
    assert any(c["comment"] == "needs urgent review" for c in body["comments"])


def test_scan_comments_requires_auth():
    """GET /api/scans/{id}/comments without a token returns 401."""
    resp = client.get("/api/scans/1/comments")
    assert resp.status_code == 401


def test_scan_comment_invalid_json():
    """A non-JSON body returns success=False."""
    scan_id = _create_scan_record(_demo_user_id())
    resp = client.post(
        f"/api/scans/{scan_id}/comment",
        content="not json",
        headers={**_auth_headers(), "Content-Type": "application/json"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False


# --- POST /api/finding/feedback ---

def test_finding_feedback_requires_auth_not_enforced():
    """Anonymous feedback is accepted (returns success=True, feedback_id=None)."""
    resp = client.post(
        "/api/finding/feedback",
        json={"scan_id": 1, "finding_name": "test", "is_false_positive": True},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["feedback_id"] is None


def test_finding_feedback_authenticated_persists():
    """Authenticated feedback is persisted and returns a feedback_id."""
    headers = _auth_headers()
    scan_id = _create_scan_record(_demo_user_id())
    resp = client.post(
        "/api/finding/feedback",
        json={
            "scan_id": scan_id,
            "finding_name": "缺少 HSTS",
            "finding_type": "config",
            "is_false_positive": True,
            "is_confirmed": False,
        },
        headers=headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["feedback_id"] is not None


def test_finding_feedback_confirmed_flag():
    """Submitting is_confirmed=True persists correctly."""
    headers = _auth_headers()
    scan_id = _create_scan_record(_demo_user_id())
    resp = client.post(
        "/api/finding/feedback",
        json={
            "scan_id": scan_id,
            "finding_name": "缺少 CSP",
            "is_false_positive": False,
            "is_confirmed": True,
        },
        headers=headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["feedback_id"] is not None

    # Verify via the list endpoint
    listing = client.get(
        f"/api/finding/feedback?scan_id={scan_id}", headers=headers
    )
    assert listing.status_code == 200
    feedbacks = listing.json().get("feedbacks", [])
    assert any(f.get("is_confirmed") for f in feedbacks)


def test_finding_feedback_list_filter_by_scan():
    """The feedback list can be filtered by scan_id."""
    headers = _auth_headers()
    scan_id = _create_scan_record(_demo_user_id())
    client.post(
        "/api/finding/feedback",
        json={
            "scan_id": scan_id,
            "finding_name": "test finding",
            "is_false_positive": True,
        },
        headers=headers,
    )
    resp = client.get(
        f"/api/finding/feedback?scan_id={scan_id}", headers=headers
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "feedbacks" in body
    for fb in body["feedbacks"]:
        assert fb["scan_id"] == scan_id


def test_finding_feedback_with_note():
    """Feedback with a note is accepted."""
    headers = _auth_headers()
    scan_id = _create_scan_record(_demo_user_id())
    resp = client.post(
        "/api/finding/feedback",
        json={
            "scan_id": scan_id,
            "finding_name": "X-Frame-Options missing",
            "is_false_positive": False,
            "is_confirmed": True,
            "note": "Confirmed during manual testing",
        },
        headers=headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
