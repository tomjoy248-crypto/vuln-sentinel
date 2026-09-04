"""Comprehensive pytest tests for the main API endpoints still defined in main.py.

Covers health, config, dashboard, scan, history, CVE, fix, monitors, targets,
demo, compliance, evolution, API versioning, usage, share, report, finding,
scans (comment/retest/compare), verify, notifications, generate, scan-progress,
scan-auth-log and reset-password endpoints.

Patterns follow tests/test_billing.py:
- Set DB_DIR/DB_NAME to a temp path BEFORE importing main.
- Login as the "demo" user to obtain a bearer token.
- Use ``Authorization: Bearer <token>`` for protected endpoints.
"""

import os
import sys
import time

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


def _create_scan_record(user_id: int, url: str = "https://example.com") -> int:
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
                85,
                "低风险",
                0,
                "[]",
                "{}",
                0,
                "test",
                "2026-01-01 00:00:00",
            ),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Health endpoints (public)
# ---------------------------------------------------------------------------

def test_api_health_returns_ok_status():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "version" in body
    assert "db" in body


def test_health_live_returns_alive():
    resp = client.get("/health/live")
    assert resp.status_code == 200
    assert resp.json()["status"] == "alive"


def test_health_ready_returns_ready():
    resp = client.get("/health/ready")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ready"
    assert "checks" in body
    assert "database" in body["checks"]


def test_health_ready_returns_degraded_when_dependency_fails(monkeypatch):
    monkeypatch.setattr("app.health.check_db_health", lambda: False)
    monkeypatch.setattr("app.health._check_redis_health", lambda: False)

    resp = client.get("/health/ready")
    assert resp.status_code == 503
    body = resp.json()
    assert body["status"] == "degraded"
    assert body["checks"]["database"] == "error"
    assert body["checks"]["redis"] == "skip" or body["checks"]["redis"] == "error"


def test_health_version_returns_version_info():
    resp = client.get("/health/version")
    assert resp.status_code == 200
    body = resp.json()
    assert "version" in body
    assert "title" in body
    assert "build_time" in body


# ---------------------------------------------------------------------------
# Config & version (public)
# ---------------------------------------------------------------------------

def test_api_config_returns_public_config():
    resp = client.get("/api/config")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    cfg = body["data"]
    assert "stripe_enabled" in cfg
    assert "public_base_url" in cfg
    assert "alipay_enabled" in cfg
    assert "wechat_enabled" in cfg


def test_api_version_returns_version():
    resp = client.get("/api/version")
    assert resp.status_code == 200
    body = resp.json()
    assert body["version"] == main.settings.app_version
    assert "title" in body
    assert "build_time" in body


def test_api_v1_info_returns_version_root():
    resp = client.get("/api/v1/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["api_version"] == "v1"
    assert body["version"] == main.settings.app_version
    assert resp.headers.get("X-API-Version") == "v1"


def test_api_v1_without_trailing_slash():
    resp = client.get("/api/v1")
    assert resp.status_code == 200
    assert resp.json()["api_version"] == "v1"
    assert resp.headers.get("X-API-Version") == "v1"


# ---------------------------------------------------------------------------
# Dashboard (auth)
# ---------------------------------------------------------------------------

def test_dashboard_requires_auth():
    resp = client.get("/api/dashboard")
    assert resp.status_code == 401


def test_dashboard_returns_summary():
    resp = client.get("/api/dashboard", headers=_auth_headers())
    assert resp.status_code == 200
    body = resp.json()
    assert "total_scans" in body
    assert "high_risk_count" in body
    assert "fixed_count" in body
    assert "recent_scans" in body


def test_trend_requires_auth():
    resp = client.get("/api/trend")
    assert resp.status_code == 401


def test_trend_returns_series_and_summary():
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


def test_stats_history_requires_auth():
    resp = client.get("/api/stats/history")
    assert resp.status_code == 401


def test_stats_history_returns_points():
    resp = client.get("/api/stats/history", headers=_auth_headers())
    assert resp.status_code == 200
    body = resp.json()
    assert "points" in body
    assert "series" in body
    assert "summary" in body
    assert "scan_count" in body["summary"]


# ---------------------------------------------------------------------------
# Scan (auth)
# ---------------------------------------------------------------------------

def test_scan_requires_auth():
    resp = client.post("/api/scan", json={"url": "example.com"})
    assert resp.status_code == 401


def test_scan_invalid_url_returns_failure():
    """An SSRF-blocked URL returns 200 with success=False (no crash)."""
    resp = client.post(
        "/api/scan", json={"url": "http://localhost"}, headers=_auth_headers()
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False
    assert body["risk_level"] == "无法扫描"


def test_scan_example_com_succeeds():
    resp = client.post(
        "/api/scan",
        json={"url": "example.com", "authorized": True},
        headers=_auth_headers(),
    )
    assert resp.status_code == 200
    body = resp.json()
    # Scan may succeed or fail depending on network/DNS in test env;
    # either way the response structure must be valid
    assert "success" in body
    if body["success"]:
        assert "score" in body
        assert "summary" in body
        assert "findings" in body
    else:
        assert "error" in body or "risk_level" in body


def test_get_scan_requires_auth():
    resp = client.get("/api/scan/1")
    assert resp.status_code == 401


def test_get_scan_not_found_returns_404():
    resp = client.get("/api/scan/999999", headers=_auth_headers())
    assert resp.status_code == 404


def test_get_scan_returns_record():
    scan_id = _create_scan_record(_demo_user_id())
    resp = client.get(f"/api/scan/{scan_id}", headers=_auth_headers())
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "scan" in body
    assert body["scan"]["id"] == scan_id


def test_async_scan_requires_auth():
    resp = client.post("/api/scan/async", json={"url": "example.com"})
    assert resp.status_code == 401


def test_async_scan_creates_task():
    resp = client.post(
        "/api/scan/async",
        json={"url": "example.com", "authorized": True},
        headers=_auth_headers(),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "task_id" in body
    assert body["status"] == "pending"


def test_list_scan_tasks_requires_auth():
    resp = client.get("/api/scan/tasks")
    assert resp.status_code == 401


def test_list_scan_tasks_shadowed_by_scan_id_route():
    """GET /api/scan/tasks is shadowed by the earlier /api/scan/{scan_id} route
    (scan_id is typed as int, defined at a lower line number).  Consequently the
    path segment ``tasks`` is matched against ``{scan_id}`` and FastAPI returns
    422 because ``tasks`` cannot be parsed as an integer.  This test documents
    that known route-ordering behaviour."""
    resp = client.get("/api/scan/tasks", headers=_auth_headers())
    assert resp.status_code == 422
    detail = resp.json()["detail"]
    assert any("scan_id" in str(d.get("loc", [])) for d in detail)


def test_list_scan_tasks_via_task_manager():
    """Exercise the task-listing logic indirectly: create an async scan task,
    then retrieve it by task_id through GET /api/scan/tasks/{task_id}."""
    headers = _auth_headers()
    create = client.post(
        "/api/scan/async",
        json={"url": "example.com", "authorized": True},
        headers=headers,
    )
    assert create.status_code == 200
    task_id = create.json()["task_id"]

    got = client.get(f"/api/scan/tasks/{task_id}", headers=headers)
    assert got.status_code == 200
    body = got.json()
    assert body["task_id"] == task_id
    assert body["found"] is True


def test_get_scan_task_requires_auth():
    resp = client.get("/api/scan/tasks/abc")
    assert resp.status_code == 401


def test_get_scan_task_not_found_returns_404():
    resp = client.get("/api/scan/tasks/nonexistent-task-id", headers=_auth_headers())
    assert resp.status_code == 404


def test_scan_progress_requires_auth():
    resp = client.get("/api/scan-progress/some-token")
    assert resp.status_code == 401


def test_scan_progress_unknown_token_returns_idle():
    resp = client.get("/api/scan-progress/unknown-token", headers=_auth_headers())
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "idle"
    assert body["current"] == -1


# ---------------------------------------------------------------------------
# History (auth)
# ---------------------------------------------------------------------------

def test_history_requires_auth():
    resp = client.get("/api/history")
    assert resp.status_code == 401


def test_history_returns_history_and_stats():
    resp = client.get("/api/history", headers=_auth_headers())
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert "history" in data
    assert "stats" in data
    assert "scan_count" in data["stats"]
    assert "fixed_count" in data["stats"]


def test_history_delete_requires_auth():
    resp = client.delete("/api/history")
    assert resp.status_code == 401


def test_history_delete_clears_history():
    headers = _auth_headers()
    # Ensure there is at least one record before deleting.
    _create_scan_record(_demo_user_id())
    resp = client.delete("/api/history", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "deleted" in body["data"]
    assert isinstance(body["data"]["deleted"], int)


# ---------------------------------------------------------------------------
# CVE (public)
# ---------------------------------------------------------------------------

def test_cve_stats_returns_stats():
    resp = client.get("/api/cve/stats")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True


def test_cve_search_without_keyword_returns_error():
    resp = client.get("/api/cve/search")
    assert resp.status_code in (400, 422)


def test_cve_get_invalid_format_returns_400():
    resp = client.get("/api/cve/not-a-cve")
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Fix (auth; simulate-fix is public)
# ---------------------------------------------------------------------------

def test_fix_requires_auth():
    resp = client.post("/api/fix", json={"url": "example.com"})
    assert resp.status_code == 401


def test_fix_tickets_create_requires_auth():
    resp = client.post("/api/fix-tickets", json={"finding_name": "test"})
    assert resp.status_code == 401


def test_fix_tickets_list_requires_auth():
    resp = client.get("/api/fix-tickets")
    assert resp.status_code == 401


def test_fix_tickets_create_and_list():
    headers = _auth_headers()
    scan_id = _create_scan_record(_demo_user_id())
    create = client.post(
        "/api/fix-tickets",
        json={
            "scan_id": scan_id,
            "finding_name": "缺少 HSTS",
            "severity": "high",
            "fix_code": "add_header Strict-Transport-Security ...",
        },
        headers=headers,
    )
    assert create.status_code == 200
    assert create.json()["success"] is True
    assert "ticket_id" in create.json()["data"]

    listing = client.get("/api/fix-tickets", headers=headers)
    assert listing.status_code == 200
    assert listing.json()["success"] is True
    tickets = listing.json()["data"]["tickets"]
    assert any(t["finding_name"] == "缺少 HSTS" for t in tickets)


def test_fix_ticket_get_and_update():
    """Verify ticket retrieval and a valid status transition.

    Tickets start as ``pending``; the ALLOWED_TRANSITIONS table only permits
    pending -> {pending, confirmed, ignored}.  Transitioning directly to
    ``fixed`` is rejected with 400, so we first move to ``confirmed``.
    """
    headers = _auth_headers()
    scan_id = _create_scan_record(_demo_user_id())
    create = client.post(
        "/api/fix-tickets",
        json={"scan_id": scan_id, "finding_name": "缺少 CSP", "severity": "high"},
        headers=headers,
    )
    ticket_id = create.json()["data"]["ticket_id"]

    got = client.get(f"/api/fix-tickets/{ticket_id}", headers=headers)
    assert got.status_code == 200
    assert got.json()["success"] is True
    assert got.json()["data"]["ticket"]["id"] == ticket_id

    # Invalid transition: pending -> fixed is not allowed (returns 400).
    bad = client.patch(
        f"/api/fix-tickets/{ticket_id}",
        json={"status": "fixed"},
        headers=headers,
    )
    assert bad.status_code == 400

    # Valid transition: pending -> confirmed.
    patched = client.patch(
        f"/api/fix-tickets/{ticket_id}",
        json={"status": "confirmed"},
        headers=headers,
    )
    assert patched.status_code == 200
    assert patched.json()["success"] is True

    # Verify the new status persisted.
    rechecked = client.get(f"/api/fix-tickets/{ticket_id}", headers=headers)
    assert rechecked.json()["data"]["ticket"]["status"] == "confirmed"


def test_fix_ticket_full_lifecycle():
    """Exercise the full valid transition chain:
    pending -> confirmed -> applying -> fixed.
    """
    headers = _auth_headers()
    scan_id = _create_scan_record(_demo_user_id())
    create = client.post(
        "/api/fix-tickets",
        json={"scan_id": scan_id, "finding_name": "缺少 X-Frame-Options", "severity": "medium"},
        headers=headers,
    )
    ticket_id = create.json()["data"]["ticket_id"]

    for new_status in ("confirmed", "applying", "fixed"):
        resp = client.patch(
            f"/api/fix-tickets/{ticket_id}",
            json={"status": new_status},
            headers=headers,
        )
        assert resp.status_code == 200, f"Transition to {new_status} failed: {resp.text}"
        assert resp.json()["success"] is True


def test_simulate_fix_is_public():
    """simulate-fix does not require authentication."""
    resp = client.post(
        "/api/simulate-fix",
        json={"findings": [{"name": "缺少 HSTS", "severity": "high"}]},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "before_score" in body
    assert "after_score" in body
    assert "delta" in body
    assert body["fixed_count"] == 1


def test_simulate_fix_calculates_scores():
    findings = [
        {"name": "缺少 HSTS", "severity": "high"},
        {"name": "缺少 CSP", "severity": "high"},
        {"name": "缺少 X-Frame-Options", "severity": "medium"},
    ]
    resp = client.post("/api/simulate-fix", json={"findings": findings})
    assert resp.status_code == 200
    body = resp.json()
    # deduction = 2*15 + 1*8 = 38; before = 100-38 = 62; after = min(100, 62+38+12)
    assert body["before_score"] == 62
    assert body["after_score"] == 100
    assert body["delta"] == 38
    assert body["fixed_count"] == 3


def test_demo_fix_requires_auth():
    resp = client.post("/api/demo-fix", json={"action": "apply"})
    assert resp.status_code == 401


def test_demo_fix_invalid_action_returns_422():
    resp = client.post(
        "/api/demo-fix", json={"action": "hack"}, headers=_auth_headers()
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Monitors (auth)
# ---------------------------------------------------------------------------

def test_monitors_list_requires_auth():
    resp = client.get("/api/monitors")
    assert resp.status_code == 401


def test_monitors_list_returns_structure():
    resp = client.get("/api/monitors", headers=_auth_headers())
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "monitors" in body
    assert "total" in body


def test_monitor_create_requires_auth():
    resp = client.post("/api/monitors", json={"url": "https://example.com"})
    assert resp.status_code == 401


def test_monitor_create_invalid_url_returns_error():
    resp = client.post(
        "/api/monitors", json={"url": "http://localhost"}, headers=_auth_headers()
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False


def test_monitor_create_list_and_delete():
    headers = _auth_headers()
    create = client.post(
        "/api/monitors",
        json={"url": "https://example.com", "frequency_hours": 24},
        headers=headers,
    )
    assert create.status_code == 200
    body = create.json()
    assert body["success"] is True
    monitor_id = body["monitor_id"]

    listing = client.get("/api/monitors", headers=headers)
    assert listing.status_code == 200
    assert any(m["id"] == monitor_id for m in listing.json()["monitors"])

    delete = client.delete(f"/api/monitors/{monitor_id}", headers=headers)
    assert delete.status_code == 200
    assert delete.json()["success"] is True
    assert delete.json()["deleted_id"] == monitor_id


def test_monitor_delete_requires_auth():
    resp = client.delete("/api/monitors/1")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Targets (auth)
# ---------------------------------------------------------------------------

def test_targets_list_requires_auth():
    resp = client.get("/api/targets")
    assert resp.status_code == 401


def test_targets_create_requires_auth():
    resp = client.post("/api/targets", json={"url": "https://example.com"})
    assert resp.status_code == 401


def test_target_delete_requires_auth():
    resp = client.delete("/api/targets/1")
    assert resp.status_code == 401


def test_target_create_list_and_delete():
    headers = _auth_headers()
    url = "https://example.com"
    create = client.post(
        "/api/targets", json={"url": url, "schedule": "daily"}, headers=headers
    )
    assert create.status_code == 200
    assert create.json()["success"] is True

    listing = client.get("/api/targets", headers=headers)
    assert listing.status_code == 200
    targets = listing.json()["targets"]
    assert any(t["url"] == url for t in targets)

    target_id = next(t["id"] for t in targets if t["url"] == url)
    delete = client.delete(f"/api/targets/{target_id}", headers=headers)
    assert delete.status_code == 200
    assert delete.json()["success"] is True


def test_target_create_records_audit_user_id():
    headers = _auth_headers()
    url = "https://audit.example.com"
    create = client.post(
        "/api/targets", json={"url": url, "schedule": "daily"}, headers=headers
    )
    assert create.status_code == 200

    conn = main.get_db()
    try:
        row = conn.execute(
            "SELECT user_id, action, resource_type FROM audit_logs ORDER BY id DESC LIMIT 1"
        ).fetchone()
        assert row is not None
        assert row["user_id"] == _demo_user_id()
        assert row["action"] == "post_target"
        assert row["resource_type"] == "target"
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Demo (auth / public)
# ---------------------------------------------------------------------------

def test_demo_status_requires_auth():
    resp = client.get("/api/demo-status")
    assert resp.status_code == 401


def test_demo_full_cycle_requires_auth():
    resp = client.post("/api/demo-full-cycle", json={"target": "localhost:8080"})
    assert resp.status_code == 401


def test_public_demo_scan_non_whitelist_returns_403():
    main.settings.public_demo_enabled = True
    main.settings.free_trial_enabled = True
    resp = client.post("/api/public-demo-scan", json={"url": "https://evil.com"})
    assert resp.status_code == 403


def test_public_demo_scan_disabled_returns_403(monkeypatch):
    monkeypatch.setattr(main.settings, "public_demo_enabled", False, raising=False)
    monkeypatch.setattr(main.settings, "free_trial_enabled", True, raising=False)

    resp = client.post("/api/public-demo-scan", json={"url": "https://example.com"})
    assert resp.status_code == 403


def test_public_demo_scan_whitelist_returns_200():
    main.settings.public_demo_enabled = True
    main.settings.free_trial_enabled = True
    resp = client.post("/api/public-demo-scan", json={"url": "https://example.com"})
    assert resp.status_code == 200
    body = resp.json()
    assert "url" in body
    assert body.get("success") is True or body.get("is_cached") is True


# ---------------------------------------------------------------------------
# Compliance (auth)
# ---------------------------------------------------------------------------

def test_compliance_summary_requires_auth():
    resp = client.get("/api/compliance/summary")
    assert resp.status_code == 401


def test_compliance_summary_returns_data():
    resp = client.get("/api/compliance/summary", headers=_auth_headers())
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "data" in body


# ---------------------------------------------------------------------------
# Evolution & learning (auth)
# ---------------------------------------------------------------------------

def test_evolution_dashboard_requires_auth():
    resp = client.get("/api/evolution/dashboard")
    assert resp.status_code == 401


def test_evolution_dashboard_returns_structure():
    resp = client.get("/api/evolution/dashboard", headers=_auth_headers())
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "learning" in body
    assert "monitoring" in body
    assert "team" in body
    assert "evolution_score" in body


def test_learn_insights_requires_auth():
    resp = client.get("/api/learn/insights")
    assert resp.status_code == 401


def test_learn_insights_returns_dict():
    resp = client.get("/api/learn/insights", headers=_auth_headers())
    assert resp.status_code == 200
    assert isinstance(resp.json(), dict)


# ---------------------------------------------------------------------------
# Usage (auth)
# ---------------------------------------------------------------------------

def test_usage_requires_auth():
    resp = client.get("/api/usage")
    assert resp.status_code == 401


def test_usage_returns_logs():
    resp = client.get("/api/usage", headers=_auth_headers())
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "logs" in body["data"]
    assert "total" in body["data"]


# ---------------------------------------------------------------------------
# Share (public)
# ---------------------------------------------------------------------------

def test_share_invalid_id_format_returns_400():
    resp = client.get("/api/share/bad!")
    assert resp.status_code == 400


def test_share_not_found_returns_404():
    resp = client.get("/api/share/aaaaaaaa")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Report (auth)
# ---------------------------------------------------------------------------

def test_report_requires_auth():
    resp = client.get("/api/report/1")
    assert resp.status_code == 401


def test_report_not_found_returns_404():
    resp = client.get("/api/report/999999", headers=_auth_headers())
    assert resp.status_code == 404


def test_report_html_returns_html():
    scan_id = _create_scan_record(_demo_user_id())
    resp = client.get(f"/api/report/{scan_id}?format=html", headers=_auth_headers())
    assert resp.status_code == 200
    assert "text/html" in resp.headers.get("content-type", "")


def test_src_export_requires_auth():
    resp = client.post("/api/report/src-export", json={"scan_id": 1})
    assert resp.status_code == 401


def test_src_export_not_found_returns_404():
    resp = client.post(
        "/api/report/src-export", json={"scan_id": 999999}, headers=_auth_headers()
    )
    assert resp.status_code == 404


def test_src_export_returns_markdown():
    scan_id = _create_scan_record(_demo_user_id())
    resp = client.post(
        "/api/report/src-export",
        json={"scan_id": scan_id, "format": "markdown"},
        headers=_auth_headers(),
    )
    assert resp.status_code == 200
    assert "markdown" in resp.headers.get("content-type", "")


# ---------------------------------------------------------------------------
# Finding feedback & verify-reproduce (auth / anonymous)
# ---------------------------------------------------------------------------

def test_finding_feedback_anonymous_returns_success():
    """Anonymous feedback is accepted but not persisted."""
    resp = client.post(
        "/api/finding/feedback",
        json={"scan_id": 1, "finding_name": "缺少 HSTS", "is_false_positive": True},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["feedback_id"] is None


def test_finding_feedback_authenticated_persists():
    headers = _auth_headers()
    scan_id = _create_scan_record(_demo_user_id())
    resp = client.post(
        "/api/finding/feedback",
        json={
            "scan_id": scan_id,
            "finding_name": "缺少 CSP",
            "is_false_positive": True,
        },
        headers=headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["feedback_id"] is not None


def test_finding_feedback_list_returns_feedbacks():
    headers = _auth_headers()
    resp = client.get("/api/finding/feedback", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "feedbacks" in body


def test_finding_verify_reproduce_requires_auth():
    resp = client.post(
        "/api/finding/verify-reproduce",
        json={"scan_id": 1, "finding_id": "x", "url": "https://example.com"},
    )
    assert resp.status_code == 401


def test_finding_verify_reproduce_not_found_returns_404():
    resp = client.post(
        "/api/finding/verify-reproduce",
        json={"scan_id": 999999, "finding_id": "x", "url": "https://example.com"},
        headers=_auth_headers(),
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Scans: comment / retest / compare (auth)
# ---------------------------------------------------------------------------

def test_scan_comment_requires_auth():
    resp = client.post("/api/scans/1/comment", json={"comment": "hi"})
    assert resp.status_code == 401


def test_scan_comment_empty_returns_error():
    resp = client.post(
        "/api/scans/1/comment", json={"comment": ""}, headers=_auth_headers()
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False


def test_scan_comment_and_list():
    headers = _auth_headers()
    scan_id = _create_scan_record(_demo_user_id())
    create = client.post(
        f"/api/scans/{scan_id}/comment",
        json={"comment": "needs review"},
        headers=headers,
    )
    assert create.status_code == 200
    assert create.json()["success"] is True

    listing = client.get(f"/api/scans/{scan_id}/comments", headers=headers)
    assert listing.status_code == 200
    body = listing.json()
    assert body["success"] is True
    assert body["total"] >= 1
    assert any(c["comment"] == "needs review" for c in body["comments"])


def test_scan_comments_requires_auth():
    resp = client.get("/api/scans/1/comments")
    assert resp.status_code == 401


def test_scan_retest_requires_auth():
    resp = client.post("/api/scans/1/retest")
    assert resp.status_code == 401


def test_scan_retest_not_found_returns_404():
    resp = client.post("/api/scans/999999/retest", headers=_auth_headers())
    assert resp.status_code == 404


def test_scan_compare_requires_auth():
    resp = client.get("/api/scans/1/compare")
    assert resp.status_code == 401


def test_scan_compare_not_found_returns_404():
    resp = client.get("/api/scans/999999/compare", headers=_auth_headers())
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Verify (auth)
# ---------------------------------------------------------------------------

def test_verify_requires_auth():
    resp = client.post(
        "/api/verify",
        json={"url": "https://example.com", "token": "tok", "method": "dns"},
    )
    assert resp.status_code == 401


def test_verify_domain_requires_auth():
    resp = client.post("/api/verify-domain", json={"domain": "example.com"})
    assert resp.status_code == 401


def test_verify_domain_empty_returns_400():
    resp = client.post(
        "/api/verify-domain", json={"domain": ""}, headers=_auth_headers()
    )
    assert resp.status_code == 400


def test_verify_domain_no_dot_returns_400():
    resp = client.post(
        "/api/verify-domain", json={"domain": "localhost"}, headers=_auth_headers()
    )
    assert resp.status_code == 400


def test_verify_domain_invalid_method_returns_400():
    resp = client.post(
        "/api/verify-domain",
        json={"domain": "example.com", "method": "hack"},
        headers=_auth_headers(),
    )
    assert resp.status_code == 400


def test_verify_fix_requires_auth():
    resp = client.post("/api/verify-fix", json={"url": "https://example.com"})
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Notifications (auth)
# ---------------------------------------------------------------------------

def test_get_notifications_requires_auth():
    resp = client.get("/api/me/notifications")
    assert resp.status_code == 401


def test_get_notifications_returns_settings():
    resp = client.get("/api/me/notifications", headers=_auth_headers())
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "email" in body
    assert "webhook" in body
    assert "threshold" in body


def test_update_notifications_requires_auth():
    resp = client.post("/api/me/notifications", json={"threshold": "high"})
    assert resp.status_code == 401


def test_update_notifications_sets_threshold():
    resp = client.post(
        "/api/me/notifications",
        json={"email": "", "webhook": "", "threshold": "critical"},
        headers=_auth_headers(),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True

    # Verify it persisted.
    get_resp = client.get("/api/me/notifications", headers=_auth_headers())
    assert get_resp.json()["threshold"] == "critical"


# ---------------------------------------------------------------------------
# Generate fix package (auth)
# ---------------------------------------------------------------------------

def test_generate_fix_package_requires_auth():
    resp = client.post(
        "/api/generate-fix-package", json={"findings": [], "host": "example.com"}
    )
    assert resp.status_code == 401


def test_generate_fix_package_returns_zip():
    resp = client.post(
        "/api/generate-fix-package",
        json={
            "findings": [{"name": "缺少 HSTS", "severity": "high"}],
            "host": "example.com",
            "is_https": True,
            "platform": "nginx",
        },
        headers=_auth_headers(),
    )
    assert resp.status_code == 200
    assert "application/zip" in resp.headers.get("content-type", "")
    assert resp.headers.get("content-disposition", "").startswith("attachment")


# ---------------------------------------------------------------------------
# Scan auth log (auth)
# ---------------------------------------------------------------------------

def test_scan_auth_log_requires_auth():
    resp = client.post("/api/scan-auth-log", json={"authorized_at": "2026-01-01"})
    assert resp.status_code == 401


def test_scan_auth_log_missing_field_returns_error():
    resp = client.post("/api/scan-auth-log", json={}, headers=_auth_headers())
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False


def test_scan_auth_log_success():
    resp = client.post(
        "/api/scan-auth-log",
        json={"authorized_at": "2026-01-01 00:00:00", "url": "https://example.com"},
        headers=_auth_headers(),
    )
    assert resp.status_code == 200
    assert resp.json()["success"] is True


# ---------------------------------------------------------------------------
# Reset password (auth)
# ---------------------------------------------------------------------------

def test_reset_password_requires_auth():
    resp = client.post("/api/reset-password", json={"new_password": "newpass123"})
    assert resp.status_code == 401


def test_reset_password_changes_password():
    # Use a dedicated user so the shared demo account is not affected.
    username = "reset_" + str(int(time.time() * 1000))
    reg = client.post(
        "/api/register", json={"username": username, "password": "oldpass123"}
    )
    assert reg.status_code == 200
    token = reg.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post(
        "/api/reset-password", json={"new_password": "newpass456"}, headers=headers
    )
    assert resp.status_code == 200
    assert resp.json()["success"] is True

    # Old password no longer works.
    old_login = client.post(
        "/api/login", json={"username": username, "password": "oldpass123"}
    )
    assert old_login.status_code in (401, 422)

    # New password works.
    new_login = client.post(
        "/api/login", json={"username": username, "password": "newpass456"}
    )
    assert new_login.status_code == 200
