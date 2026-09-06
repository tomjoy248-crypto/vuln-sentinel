"""Regression tests for persisted tasks, authorization comparison and flow analysis."""

import asyncio
import os
import sys

import pytest

os.environ.setdefault("DB_DIR", "/tmp/v11-test")
os.environ.setdefault("DB_NAME", "test.db")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient  # noqa: E402

import main  # noqa: E402
from app.plugins import BaseVulnDetector, DetectorRegistry, Finding, ScanContext  # noqa: E402
from app.services.authorization_diff import _redact_preview  # noqa: E402
from app.services.business_flow import analyze_business_flow  # noqa: E402
from app.tasks import ScanTaskManager, TaskStatus  # noqa: E402

main.init_db()
client = TestClient(main.app)


def _auth_headers() -> dict[str, str]:
    """Return a self-contained token that does not depend on a test database path."""
    return {"Authorization": f"Bearer {main.create_token(1, 'demo', 'member')}"}


def test_business_flow_detects_jump_duplicate_and_parameter_boundary() -> None:
    """The offline analyzer reports all three core business-flow signals."""
    result = analyze_business_flow(
        [
            {"name": "create", "state": "created", "action": "create", "request_key": "a"},
            {
                "name": "pay",
                "state": "paid",
                "action": "pay",
                "request_key": "a",
                "parameters": {"amount": -1},
            },
        ]
    )
    types = {finding["type"] for finding in result["findings"]}
    assert {"state_jump", "duplicate_submission", "boundary_value"} <= types


def test_business_flow_endpoint_requires_authorization() -> None:
    response = client.post(
        "/api/business-flow/analyze",
        json={"authorized": False, "steps": [{"state": "created"}]},
        headers=_auth_headers(),
    )
    assert response.status_code == 403


def test_business_flow_endpoint_returns_retest_status() -> None:
    payload = {
        "authorized": True,
        "steps": [{"name": "pay", "state": "paid", "action": "pay", "request_key": "a"}],
        "baseline_steps": [
            {"name": "pay", "state": "paid", "action": "pay", "request_key": ""}
        ],
    }
    response = client.post("/api/business-flow/analyze", json=payload, headers=_auth_headers())
    assert response.status_code == 200
    assert response.json()["result"]["retest"]["available"] is True


def test_authorization_diff_json_evidence_redacts_secrets() -> None:
    """Structured response evidence must not expose credential values."""
    preview = _redact_preview('{"user":"alice","token":"do-not-store","profile":{"email":"a@example.com"}}')
    assert "do-not-store" not in preview
    assert "a@example.com" not in preview
    assert "[REDACTED]" in preview


def test_authorization_diff_endpoint_is_read_only(monkeypatch: pytest.MonkeyPatch) -> None:
    """The endpoint validates authorization and delegates only to the comparator."""
    async def fake_compare(url, baseline_headers, comparison_headers):
        assert url == "https://example.com"
        assert baseline_headers == {"Authorization": "Bearer one"}
        assert comparison_headers == {"Authorization": "Bearer two"}
        return {"status_diff": True, "body_diff": False, "severity": "info"}

    monkeypatch.setattr(main, "validate_scan_target_full", lambda *args, **kwargs: (True, "", ""))
    monkeypatch.setattr("app.services.authorization_diff.compare_authorized_contexts", fake_compare)
    response = client.post(
        "/api/authorization-diff",
        json={
            "url": "example.com",
            "authorized": True,
            "baseline_headers": {"Authorization": "Bearer one"},
            "comparison_headers": {"Authorization": "Bearer two"},
        },
        headers=_auth_headers(),
    )
    assert response.status_code == 200
    assert response.json()["result"]["status_diff"] is True


@pytest.mark.asyncio
async def test_persisted_task_state_and_restart_recovery(monkeypatch: pytest.MonkeyPatch) -> None:
    """Task snapshots are saved and sensitive active tasks are not resumed."""
    saved = []
    monkeypatch.setattr("app.services.task_persistence.save_task", lambda task: saved.append(task.to_dict()))
    manager = ScanTaskManager(persist=True)

    async def scan_func(url, *, progress_cb, **kwargs):
        progress_cb(100)
        return {"ok": True}

    task_id = await manager.submit("https://example.com", 1, "standard", scan_func)
    for _ in range(50):
        if manager.get_task(task_id).status == TaskStatus.COMPLETED:
            break
        await asyncio.sleep(0.01)
    assert manager.get_task(task_id).status == TaskStatus.COMPLETED
    assert any(item["status"] == "completed" for item in saved)

    monkeypatch.setattr(
        "app.services.task_persistence.load_tasks",
        lambda: [{
            "task_id": "SCAN-AUTH-RESTART",
            "user_id": "1",
            "url": "https://example.com",
            "depth": "standard",
            "status": "running",
            "has_sensitive_context": 1,
        }],
    )
    restored = ScanTaskManager(persist=True)
    assert restored.restore_tasks(scan_func) == 1
    assert restored.get_task("SCAN-AUTH-RESTART").status == TaskStatus.FAILED
    assert "认证任务" in restored.get_task("SCAN-AUTH-RESTART").error


@pytest.mark.asyncio
async def test_pause_resume_does_not_finish_queued_task() -> None:
    """A paused task stays queued and resumes after the running task releases the slot."""
    manager = ScanTaskManager(max_concurrent=1, task_timeout=2)
    started = asyncio.Event()
    release = asyncio.Event()

    async def scan_func(url, *, progress_cb, **kwargs):
        started.set()
        await release.wait()
        return {"url": url}

    first = await manager.submit("https://one.example", 1, "standard", scan_func)
    await started.wait()
    second = await manager.submit("https://two.example", 1, "standard", scan_func)
    await asyncio.sleep(0)
    assert await manager.pause_task(second) is True
    paused = manager.get_task(second)
    assert paused.status == TaskStatus.PAUSED
    assert paused.completed_at is None
    assert await manager.resume_task(second) is True
    release.set()
    for _ in range(100):
        if manager.get_task(second).status == TaskStatus.COMPLETED:
            break
        await asyncio.sleep(0.01)
    assert manager.get_task(first).status == TaskStatus.COMPLETED
    assert manager.get_task(second).status == TaskStatus.COMPLETED


@pytest.mark.asyncio
async def test_restart_keeps_paused_state_and_allows_safe_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    """Paused anonymous work stays paused; failed anonymous work can be retried."""
    monkeypatch.setattr("app.services.task_persistence.save_task", lambda task: None)
    monkeypatch.setattr(
        "app.services.task_persistence.load_tasks",
        lambda: [
            {
                "task_id": "SCAN-PAUSED-RESTART",
                "user_id": "1",
                "url": "https://example.com",
                "depth": "standard",
                "status": "paused",
                "progress": 20,
            },
            {
                "task_id": "SCAN-FAILED-RESTART",
                "user_id": "1",
                "url": "https://example.org",
                "depth": "standard",
                "status": "failed",
                "error": "network error",
            },
        ],
    )
    manager = ScanTaskManager(persist=True, task_timeout=2)

    async def scan_func(url, *, progress_cb, **kwargs):
        return {"url": url, "recovered": True}

    assert manager.restore_tasks(scan_func) == 2
    assert manager.get_task("SCAN-PAUSED-RESTART").status == TaskStatus.PAUSED
    assert await manager.resume_task("SCAN-PAUSED-RESTART") is True
    retry_id = await manager.retry_task("SCAN-FAILED-RESTART")
    assert retry_id is not None
    for _ in range(100):
        states = {
            manager.get_task("SCAN-PAUSED-RESTART").status,
            manager.get_task(retry_id).status,
        }
        if states == {TaskStatus.COMPLETED}:
            break
        await asyncio.sleep(0.01)
    assert manager.get_task("SCAN-PAUSED-RESTART").status == TaskStatus.COMPLETED
    assert manager.get_task(retry_id).status == TaskStatus.COMPLETED


def test_admin_dashboard_stats_shape() -> None:
    """The administrator aggregate endpoint exposes chart-safe bounded fields."""
    from app.audit import get_admin_dashboard_stats

    stats = get_admin_dashboard_stats(7)
    assert stats["period_days"] == 7
    assert set(stats["scans"]) == {"total", "by_day", "by_risk"}
    assert set(stats["tasks"]) == {"total", "by_status", "failed"}
    assert len(stats["scans"]["by_day"]) == 7
    assert "by_type" in stats["findings"]


@pytest.mark.asyncio
async def test_slow_detector_isolated_without_dropping_fast_results(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A detector timeout must not discard findings from other detectors."""

    class FastDetector(BaseVulnDetector):
        name = "test_fast_detector"
        supported_depths = ["standard"]

        async def detect(self, context: ScanContext) -> list[Finding]:
            return [Finding(title="快速检测结果", type="test", severity="low")]

    class SlowDetector(BaseVulnDetector):
        name = "test_slow_detector"
        supported_depths = ["standard"]

        async def detect(self, context: ScanContext) -> list[Finding]:
            await asyncio.sleep(0.05)
            return [Finding(title="不应返回", type="test", severity="low")]

    original_detectors = DetectorRegistry._detectors.copy()
    original_enabled = DetectorRegistry._enabled.copy()
    try:
        DetectorRegistry.reset()
        DetectorRegistry.register(FastDetector())
        DetectorRegistry.register(SlowDetector())
        monkeypatch.setattr(
            DetectorRegistry,
            "_DETECTOR_TIMEOUT_SECONDS",
            {"standard": 0.01},
        )
        results = await DetectorRegistry.run_all(
            ScanContext(url="https://example.com", depth="standard")
        )
        assert len(results["test_fast_detector"]) == 1
        assert results["test_slow_detector"] == []
    finally:
        DetectorRegistry._detectors[:] = original_detectors
        DetectorRegistry._enabled.clear()
        DetectorRegistry._enabled.update(original_enabled)
