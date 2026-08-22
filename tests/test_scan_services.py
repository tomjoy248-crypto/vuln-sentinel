"""Comprehensive pytest tests for the scan-related service modules.

Covers:
- app/services/scan_queue.py        (async scan task queue, memory + redis backends)
- app/services/scan_service.py      (core scan execution & post-processing pipeline)
- app/services/vuln_intel_service.py (NVD CVE aggregation with SQLite cache)
- app/services/discovery_crawler.py (lightweight same-origin endpoint discovery)
- app/services/cve_sources.py       (multi-source CVE adapters + aggregator)
- app/services/fuzz_engine.py       (parameter fuzzing engine)
- app/tasks/manager.py              (in-process async scan task manager)

All external HTTP requests are mocked via httpx.MockTransport so no real
network access is ever performed. Each test is a standalone function.
"""

from __future__ import annotations

import asyncio
import builtins
import contextlib
import json
import os
import sys
import time
import urllib.parse
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

# --- Database environment MUST be configured BEFORE importing main ---
os.environ["DB_DIR"] = "/tmp/v11-test"
os.environ["DB_NAME"] = "test.db"
os.makedirs(os.environ["DB_DIR"], exist_ok=True)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import httpx  # noqa: E402
import pytest  # noqa: E402

pytestmark = pytest.mark.asyncio

import main  # noqa: E402

main.init_db()

# Modules under test
from app.plugins._compat import old_finding_to_finding  # noqa: E402
from app.services import (
    cve_sources,  # noqa: E402
    scan_service,  # noqa: E402
    vuln_intel_service,  # noqa: E402
)
from app.services.discovery_crawler import (  # noqa: E402
    DiscoveredEndpoint,
    DiscoveryCrawler,
    _build_form_body,
    _is_interesting_path,
    _LinkExtractor,
    _normalize_url,
    _same_origin,
)
from app.services.fuzz_engine import (  # noqa: E402
    FUZZ_PAYLOADS,
    FuzzEngine,
    FuzzResult,
    _extract_params,
    fuzz_results_to_findings,
)
from app.services.scan_queue import (  # noqa: E402
    BaseScanQueue,
    MemoryScanQueue,
    RedisScanQueue,
    ScanTask,
    ScanTaskResult,
    generate_task_id,
    get_scan_queue,
    init_scan_queue,
)
from app.tasks.manager import (  # noqa: E402
    ScanTask as ManagerScanTask,
)
from app.tasks.manager import (  # noqa: E402
    ScanTaskManager,
    TaskStatus,
)

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


@contextlib.contextmanager
def _mock_httpx(handler):
    """Route every ``httpx.AsyncClient`` request through ``MockTransport(handler)``.

    The handler receives an ``httpx.Request`` and must return an
    ``httpx.Response``. This lets us exercise the real httpx code path
    (status codes, headers, json/text parsing, raise_for_status) without
    touching the network.
    """
    real_async_client = httpx.AsyncClient

    def _factory(*args, **kwargs):
        kwargs["transport"] = httpx.MockTransport(handler)
        return real_async_client(*args, **kwargs)

    with patch("httpx.AsyncClient", side_effect=_factory):
        yield


def _make_scan_task(
    task_id: str | None = None,
    user_id: int = 1,
    url: str = "https://example.com",
    deep: bool = False,
) -> ScanTask:
    return ScanTask(
        task_id=task_id or generate_task_id(),
        user_id=user_id,
        url=url,
        depth="deep" if deep else "standard",
        deep=deep,
        authorized=True,
    )


async def _wait_for_status(
    queue: MemoryScanQueue, task_id: str, status: str, timeout: float = 3.0
) -> ScanTaskResult | None:
    """Poll a memory queue until the task reaches ``status`` or timeout."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        result = await queue.get_status(task_id)
        if result and result.status == status:
            return result
        await asyncio.sleep(0.02)
    return await queue.get_status(task_id)


def _sample_nvd_item(cve_id: str = "CVE-2021-44228") -> dict[str, Any]:
    """Build a minimal but realistic NVD ``vulnerabilities[].cve`` item."""
    return {
        "cve": {
            "id": cve_id,
            "descriptions": [
                {"lang": "en", "value": "Critical remote code execution in log4j."},
                {"lang": "zh", "value": "log4j 严重远程代码执行漏洞。"},
            ],
            "metrics": {
                "cvssMetricV31": [
                    {
                        "cvssData": {
                            "baseScore": 9.8,
                            "vectorString": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
                            "baseSeverity": "CRITICAL",
                        },
                        "baseSeverity": "CRITICAL",
                    }
                ]
            },
            "references": [
                {"url": "https://example.com/advisory", "source": "vendor", "tags": ["patch"]},
            ],
            "configurations": [
                {
                    "nodes": [
                        {
                            "cpeMatch": [
                                {
                                    "criteria": "cpe:2.3:a:apache:log4j:2.14.0:*:*:*:*:*:*:*",
                                    "vulnerable": True,
                                    "versionStartIncluding": "2.0",
                                    "versionEndExcluding": "2.15.1",
                                }
                            ]
                        }
                    ]
                }
            ],
            "published": "2021-12-10T00:00:00.000",
            "lastModified": "2022-01-10T00:00:00.000",
        }
    }


# ===========================================================================
# scan_queue.py tests
# ===========================================================================


def test_generate_task_id_format():
    tid = generate_task_id()
    assert tid.startswith("SCAN-")
    assert len(tid) == len("SCAN-") + 12
    # hex chars uppercase
    assert tid[5:].isupper() or all(c in "0123456789ABCDEF" for c in tid[5:])


def test_generate_task_id_uniqueness():
    ids = {generate_task_id() for _ in range(200)}
    assert len(ids) == 200


def test_scan_task_to_dict_roundtrip():
    task = _make_scan_task(task_id="SCAN-ABC123")
    d = task.to_dict()
    assert d["task_id"] == "SCAN-ABC123"
    assert d["user_id"] == 1
    assert d["url"] == "https://example.com"
    assert d["depth"] == "standard"
    assert d["deep"] is False
    assert d["authorized"] is True
    assert "created_at" in d


def test_scan_task_result_to_dict_defaults():
    result = ScanTaskResult(task_id="SCAN-1", status="pending")
    d = result.to_dict()
    assert d["task_id"] == "SCAN-1"
    assert d["status"] == "pending"
    assert d["progress"] == 0
    assert d["stage"] == "queued"
    assert d["result"] is None
    assert d["error"] is None
    assert d["user_id"] == 0
    assert "updated_at" in d


def test_base_scan_queue_is_abstract():
    with pytest.raises(TypeError):
        BaseScanQueue()  # type: ignore[abstract]


async def test_memory_queue_submit_creates_pending_result():
    queue = MemoryScanQueue(max_workers=1)
    task = _make_scan_task()
    task_id = await queue.submit(task)
    assert task_id == task.task_id
    result = await queue.get_status(task_id)
    assert result is not None
    assert result.status == "pending"
    assert result.stage == "queued"
    assert result.user_id == task.user_id


async def test_memory_queue_get_status_unknown_returns_none():
    queue = MemoryScanQueue()
    assert await queue.get_status("SCAN-DOES-NOT-EXIST") is None


async def test_memory_queue_worker_completes_task():
    queue = MemoryScanQueue(max_workers=1)

    async def runner(t: ScanTask) -> dict:
        return {"url": t.url, "ok": True}

    await queue.start_worker(runner)
    try:
        task = _make_scan_task()
        task_id = await queue.submit(task)
        result = await _wait_for_status(queue, task_id, "completed")
        assert result is not None
        assert result.status == "completed"
        assert result.progress == 100
        assert result.stage == "done"
        assert result.result == {"url": "https://example.com", "ok": True}
    finally:
        await queue.stop_worker()


async def test_memory_queue_worker_failed_task_records_error():
    queue = MemoryScanQueue(max_workers=1)

    async def runner(t: ScanTask) -> dict:
        raise RuntimeError("boom")

    await queue.start_worker(runner)
    try:
        task = _make_scan_task()
        task_id = await queue.submit(task)
        result = await _wait_for_status(queue, task_id, "failed")
        assert result is not None
        assert result.status == "failed"
        assert "boom" in (result.error or "")
    finally:
        await queue.stop_worker()


async def test_memory_queue_cancel_pending_task():
    queue = MemoryScanQueue(max_workers=1)
    # slow runner keeps the worker busy so the second task stays pending
    async def runner(t: ScanTask) -> dict:
        await asyncio.sleep(0.5)
        return {"done": True}

    await queue.start_worker(runner)
    try:
        first = _make_scan_task(task_id="SCAN-FIRST")
        second = _make_scan_task(task_id="SCAN-SECOND")
        await queue.submit(first)
        await queue.submit(second)

        cancelled = await queue.cancel_task(second.task_id)
        assert cancelled is True
        result = await queue.get_status(second.task_id)
        assert result is not None
        assert result.status == "cancelled"
        assert result.stage == "cancelled"
    finally:
        await queue.stop_worker()


async def test_memory_queue_cancel_already_completed_returns_false():
    queue = MemoryScanQueue(max_workers=1)

    async def runner(t: ScanTask) -> dict:
        return {"ok": True}

    await queue.start_worker(runner)
    try:
        task = _make_scan_task()
        task_id = await queue.submit(task)
        await _wait_for_status(queue, task_id, "completed")
        assert await queue.cancel_task(task_id) is False
    finally:
        await queue.stop_worker()


async def test_memory_queue_cancel_nonexistent_returns_false():
    queue = MemoryScanQueue()
    assert await queue.cancel_task("SCAN-NOPE") is False


async def test_memory_queue_cancel_failed_returns_false():
    queue = MemoryScanQueue(max_workers=1)

    async def runner(t: ScanTask) -> dict:
        raise ValueError("nope")

    await queue.start_worker(runner)
    try:
        task = _make_scan_task()
        task_id = await queue.submit(task)
        await _wait_for_status(queue, task_id, "failed")
        assert await queue.cancel_task(task_id) is False
    finally:
        await queue.stop_worker()


async def test_memory_queue_start_worker_idempotent():
    queue = MemoryScanQueue(max_workers=2)
    async def runner(t: ScanTask) -> dict:
        return {"ok": True}

    await queue.start_worker(runner)
    assert len(queue._worker_tasks) == 2
    await queue.start_worker(runner)  # second call should be a no-op
    assert len(queue._worker_tasks) == 2
    await queue.stop_worker()
    assert queue._worker_tasks == []
    assert queue._running is False


async def test_memory_queue_worker_skips_cancelled_before_run():
    queue = MemoryScanQueue(max_workers=1)

    started = asyncio.Event()

    async def runner(t: ScanTask) -> dict:
        started.set()
        await asyncio.sleep(0.3)
        return {"ok": True}

    await queue.start_worker(runner)
    try:
        block = _make_scan_task(task_id="SCAN-BLOCK")
        target = _make_scan_task(task_id="SCAN-TARGET")
        await queue.submit(block)
        await queue.submit(target)
        # cancel the second while it is still queued behind the blocker
        await started.wait()
        await queue.cancel_task(target.task_id)
        # The blocker should still complete normally.
        blocker_result = await _wait_for_status(queue, block.task_id, "completed")
        assert blocker_result is not None
        assert blocker_result.status == "completed"
        target_result = await queue.get_status(target.task_id)
        assert target_result is not None
        assert target_result.status == "cancelled"
    finally:
        await queue.stop_worker()


async def test_memory_queue_runner_not_configured_marks_failed():
    queue = MemoryScanQueue(max_workers=1)
    # start_worker sets the runner; we clear it to exercise the RuntimeError path
    await queue.start_worker(lambda t: None)  # type: ignore[arg-type]
    queue._runner = None  # type: ignore[assignment]
    try:
        task = _make_scan_task()
        task_id = await queue.submit(task)
        result = await _wait_for_status(queue, task_id, "failed")
        assert result is not None
        assert result.status == "failed"
        assert "not configured" in (result.error or "").lower()
    finally:
        await queue.stop_worker()


async def test_memory_queue_stop_worker_without_start_is_safe():
    queue = MemoryScanQueue()
    await queue.stop_worker()  # should not raise
    assert queue._running is False


def test_init_scan_queue_defaults_to_memory():
    q = init_scan_queue()
    assert isinstance(q, MemoryScanQueue)


def test_init_scan_queue_with_redis_url_creates_redis_queue():
    q = init_scan_queue(redis_url="redis://localhost:6379/0")
    assert isinstance(q, RedisScanQueue)
    # restore to memory for other tests
    init_scan_queue()


def test_get_scan_queue_returns_singleton():
    init_scan_queue()
    a = get_scan_queue()
    b = get_scan_queue()
    assert a is b


# --- RedisScanQueue (no real redis; use AsyncMock) ---


def _redis_queue_with_mock() -> tuple[RedisScanQueue, AsyncMock]:
    queue = RedisScanQueue("redis://localhost:6379/0", max_workers=1)
    mock_redis = AsyncMock()
    queue._redis = mock_redis  # type: ignore[assignment]
    return queue, mock_redis


async def test_redis_queue_submit_pushes_and_stores_result():
    queue, r = _redis_queue_with_mock()
    task = _make_scan_task()
    task_id = await queue.submit(task)
    assert task_id == task.task_id
    r.lpush.assert_awaited_once()
    args, _ = r.lpush.call_args
    assert args[0] == "scan_queue:pending"
    assert json.loads(args[1])["task_id"] == task.task_id
    r.setex.assert_awaited_once()
    key, ttl, payload = r.setex.call_args.args
    assert key == f"scan_queue:result:{task.task_id}"
    assert ttl == 86400
    assert json.loads(payload)["status"] == "pending"


async def test_redis_queue_get_status_returns_parsed_result():
    queue, r = _redis_queue_with_mock()
    stored = ScanTaskResult("SCAN-X", "running", progress=42, stage="scanning", user_id=7)
    r.get.return_value = json.dumps(stored.to_dict())
    result = await queue.get_status("SCAN-X")
    assert result is not None
    assert result.task_id == "SCAN-X"
    assert result.status == "running"
    assert result.progress == 42
    assert result.user_id == 7


async def test_redis_queue_get_status_missing_returns_none():
    queue, r = _redis_queue_with_mock()
    r.get.return_value = None
    assert await queue.get_status("SCAN-MISSING") is None


async def test_redis_queue_get_status_invalid_json_returns_none():
    queue, r = _redis_queue_with_mock()
    r.get.return_value = "not-json"
    assert await queue.get_status("SCAN-BAD") is None


async def test_redis_queue_cancel_pending_marks_cancelled():
    queue, r = _redis_queue_with_mock()
    pending = ScanTaskResult("SCAN-P", "pending", stage="queued", user_id=1)
    r.get.return_value = json.dumps(pending.to_dict())
    assert await queue.cancel_task("SCAN-P") is True
    r.sadd.assert_awaited_once()
    assert r.sadd.call_args.args == ("scan_queue:cancelled", "SCAN-P")
    r.expire.assert_awaited_once()
    # final stored result should be cancelled
    _, _, payload = r.setex.call_args.args
    assert json.loads(payload)["status"] == "cancelled"


async def test_redis_queue_cancel_completed_returns_false():
    queue, r = _redis_queue_with_mock()
    completed = ScanTaskResult("SCAN-C", "completed", progress=100, stage="done")
    r.get.return_value = json.dumps(completed.to_dict())
    assert await queue.cancel_task("SCAN-C") is False
    r.sadd.assert_not_awaited()


async def test_redis_queue_cancel_missing_returns_false():
    queue, r = _redis_queue_with_mock()
    r.get.return_value = None
    assert await queue.cancel_task("SCAN-NOPE") is False


async def test_redis_queue_is_cancelled_reads_set():
    queue, r = _redis_queue_with_mock()
    r.sismember.return_value = True
    assert await queue._is_cancelled("SCAN-Z") is True
    r.sismember.assert_awaited_once_with("scan_queue:cancelled", "SCAN-Z")


async def test_redis_queue_list_user_tasks_filters_and_sorts():
    queue, r = _redis_queue_with_mock()
    # two results for user 1, one for user 2
    r1 = ScanTaskResult("SCAN-1", "completed", user_id=1, updated_at=100.0)
    r2 = ScanTaskResult("SCAN-2", "completed", user_id=1, updated_at=200.0)
    r3 = ScanTaskResult("SCAN-3", "completed", user_id=2, updated_at=300.0)
    keys = [f"scan_queue:result:{r.task_id}" for r in (r1, r2, r3)]
    values = [json.dumps(r.to_dict()) for r in (r1, r2, r3)]
    # scan returns (next_cursor, keys); after first call cursor is 0 to stop
    r.scan.side_effect = [(0, keys)]
    r.mget.return_value = values

    results = await queue.list_user_tasks(user_id=1, limit=10)
    assert [res.task_id for res in results] == ["SCAN-2", "SCAN-1"]  # sorted by updated_at desc


async def test_redis_queue_list_user_tasks_empty():
    queue, r = _redis_queue_with_mock()
    r.scan.side_effect = [(0, [])]
    assert await queue.list_user_tasks(user_id=1) == []


async def test_redis_queue_start_stop_worker_idempotent():
    queue, _ = _redis_queue_with_mock()
    async def runner(t: ScanTask) -> dict:
        return {"ok": True}

    await queue.start_worker(runner)
    n = len(queue._worker_tasks)
    await queue.start_worker(runner)  # idempotent
    assert len(queue._worker_tasks) == n
    await queue.stop_worker()
    assert queue._worker_tasks == []
    assert queue._running is False


def test_redis_get_redis_raises_when_redis_not_installed(monkeypatch):
    real_import = builtins.__import__

    def _import(name, *args, **kwargs):
        if name == "redis.asyncio":
            raise ImportError("simulated: redis not available")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _import)
    monkeypatch.delitem(sys.modules, "redis.asyncio", raising=False)
    queue = RedisScanQueue("redis://localhost:6379/0")
    with pytest.raises(RuntimeError, match="redis"):
        queue._get_redis()


# ===========================================================================
# scan_service.py tests
# ===========================================================================


def test_calculate_score_empty_findings_is_perfect():
    stats = scan_service._calculate_score([])
    assert stats["score"] == 100
    assert stats["risk_level"] == "low"
    assert stats["summary"]["total"] == 0


def test_calculate_score_critical_drops_to_critical_risk():
    findings = [{"severity": "critical"} for _ in range(5)]
    stats = scan_service._calculate_score(findings)
    # 5 * 25 = 125 deducted, clamped to 10
    assert stats["score"] == 10
    assert stats["risk_level"] == "critical"
    assert stats["summary"]["critical"] == 5
    assert stats["summary"]["total"] == 5


def test_calculate_score_mixed_severities_and_unknown():
    findings = [
        {"severity": "high"},
        {"severity": "medium"},
        {"severity": "low"},
        {"severity": "info"},
        {"severity": "unknown"},  # not in weights -> 0 deduction but counted
    ]
    stats = scan_service._calculate_score(findings)
    # 100 - 15 - 8 - 3 - 0 - 0 = 74
    assert stats["score"] == 74
    assert stats["risk_level"] == "medium"
    assert stats["summary"]["high"] == 1
    assert stats["summary"]["medium"] == 1
    assert stats["summary"]["low"] == 1
    assert stats["summary"]["info"] == 1
    assert stats["summary"]["total"] == 5


def test_calculate_score_score_never_below_ten():
    findings = [{"severity": "critical"}] * 100
    stats = scan_service._calculate_score(findings)
    assert stats["score"] == 10


def test_calculate_score_risk_level_boundaries():
    # risk_level: critical (<40), high (40..<60), medium (60..<80), low (80..100)
    # 3 high = 45 deducted -> 55 -> high
    assert scan_service._calculate_score([{"severity": "high"}] * 3)["risk_level"] == "high"
    # 2 high = 30 deducted -> 70 -> medium
    assert scan_service._calculate_score([{"severity": "high"}] * 2)["risk_level"] == "medium"
    # 1 low = 3 deducted -> 97 -> low
    assert scan_service._calculate_score([{"severity": "low"}])["risk_level"] == "low"
    # 3 critical = 75 deducted -> 25 -> critical
    assert scan_service._calculate_score([{"severity": "critical"}] * 3)["risk_level"] == "critical"


def test_ensure_plugins_registered_is_idempotent():
    scan_service._ensure_plugins_registered()
    scan_service._ensure_plugins_registered()  # second call is a no-op
    from app.plugins import DetectorRegistry

    assert len(DetectorRegistry.list()) > 0


async def test_run_cross_validation_enriches_findings():
    findings = [{"id": "F1", "type": "sqli", "severity": "high"}]
    enriched = [{"id": "F1", "verification_status": "confirmed"}]

    with patch.object(scan_service, "CrossValidator") as MockValidator:
        instance = MockValidator.return_value
        instance.validate_finding_batch = AsyncMock(return_value=enriched)
        result = await scan_service._run_cross_validation(findings)

    assert result is enriched


async def test_run_cross_validation_returns_original_on_exception():
    findings = [{"id": "F1", "type": "sqli"}]
    with patch.object(scan_service, "CrossValidator") as MockValidator:
        instance = MockValidator.return_value
        instance.validate_finding_batch = AsyncMock(side_effect=RuntimeError("validator down"))
        result = await scan_service._run_cross_validation(findings)

    # original findings returned unchanged when validator raises
    assert result is findings


async def test_run_plugin_scan_standard_no_findings():
    with patch.object(scan_service, "DetectorRegistry") as MockRegistry, \
         patch.object(scan_service, "_run_cross_validation", new=AsyncMock(side_effect=lambda f: f)), \
         patch.object(scan_service, "src_scanner", create=True) if False else patch("src_scanner.set_evidence_store"), \
         patch("src_scanner.clear_evidence_store"):
        MockRegistry.list.return_value = [MagicMock()]  # ensure _ensure_plugins_registered no-ops
        MockRegistry.run_all = AsyncMock(return_value={})

        result = await scan_service.run_plugin_scan(
            url="https://example.com",
            headers={"User-Agent": "test"},
            is_https=True,
            ssl_info={"issuer": "TestCA"},
            waf=None,
            deep=False,
        )

    assert result["success"] is True
    assert result["url"] == "https://example.com"
    assert result["scan_engine"] == "plugin"
    assert result["score"] == 100
    assert result["risk_level"] == "low"
    assert result["summary"]["total"] == 0
    assert result["findings"] == []
    assert result["waf"] is None
    assert result["ssl"] == {"issuer": "TestCA"}
    assert result["report_share_id"].startswith("RPT-")
    assert "quality" in result
    assert "dedup_stats" in result
    assert result["verification_stats"]["enabled"] is True


async def test_run_plugin_scan_with_findings_lowers_score():
    finding = old_finding_to_finding(
        {"id": "F1", "title": "Missing HSTS", "type": "header_missing", "severity": "high"}
    )
    with patch.object(scan_service, "DetectorRegistry") as MockRegistry, \
         patch.object(scan_service, "_run_cross_validation", new=AsyncMock(side_effect=lambda f: f)), \
         patch("src_scanner.set_evidence_store"), \
         patch("src_scanner.clear_evidence_store"):
        MockRegistry.list.return_value = [MagicMock()]
        MockRegistry.run_all = AsyncMock(return_value={"header_detector": [finding]})

        result = await scan_service.run_plugin_scan(
            url="https://example.com",
            headers={},
            is_https=True,
            ssl_info={},
            deep=False,
        )

    assert result["success"] is True
    assert result["score"] == 85  # 100 - 15 (one high)
    assert result["summary"]["high"] == 1
    assert result["summary"]["total"] == 1
    assert len(result["findings"]) == 1


async def test_run_plugin_scan_verification_disabled():
    with patch.object(scan_service, "DetectorRegistry") as MockRegistry, \
         patch.object(scan_service, "_run_cross_validation", new=AsyncMock(return_value=[])) as mock_cv, \
         patch("src_scanner.set_evidence_store"), \
         patch("src_scanner.clear_evidence_store"):
        MockRegistry.list.return_value = [MagicMock()]
        MockRegistry.run_all = AsyncMock(return_value={})

        result = await scan_service.run_plugin_scan(
            url="https://example.com",
            headers={},
            is_https=False,
            ssl_info={},
            deep=False,
            enable_verification=False,
        )

    assert result["success"] is True
    assert result["verification_stats"]["enabled"] is False
    # cross validation should NOT have been called
    mock_cv.assert_not_awaited()


async def test_run_plugin_scan_deep_mode_invokes_discovery_and_fuzz():
    with patch.object(scan_service, "DetectorRegistry") as MockRegistry, \
         patch.object(scan_service, "DiscoveryCrawler") as MockCrawler, \
         patch.object(scan_service, "FuzzEngine") as MockFuzzer, \
         patch.object(scan_service, "_run_cross_validation", new=AsyncMock(side_effect=lambda f: f)), \
         patch("src_scanner.set_evidence_store"), \
         patch("src_scanner.clear_evidence_store"):
        MockRegistry.list.return_value = [MagicMock()]
        MockRegistry.run_all = AsyncMock(return_value={})
        crawler_inst = MockCrawler.return_value
        crawler_inst.discover = AsyncMock(return_value=[])  # no endpoints discovered
        fuzzer_inst = MockFuzzer.return_value
        fuzzer_inst.fuzz_multiple = AsyncMock(return_value={})

        result = await scan_service.run_plugin_scan(
            url="https://example.com",
            headers={},
            is_https=True,
            ssl_info={},
            deep=True,
        )

    assert result["success"] is True
    MockCrawler.assert_called_once()
    crawler_inst.discover.assert_awaited_once()
    MockFuzzer.assert_called_once()
    fuzzer_inst.fuzz_multiple.assert_awaited_once()


async def test_run_plugin_scan_deep_mode_with_discovered_endpoints():
    ep = DiscoveredEndpoint(url="https://example.com/page?id=1", method="GET")
    finding = old_finding_to_finding(
        {"id": "F2", "title": "Reflected XSS", "type": "xss", "severity": "medium"}
    )
    with patch.object(scan_service, "DetectorRegistry") as MockRegistry, \
         patch.object(scan_service, "DiscoveryCrawler") as MockCrawler, \
         patch.object(scan_service, "FuzzEngine") as MockFuzzer, \
         patch.object(scan_service, "_run_cross_validation", new=AsyncMock(side_effect=lambda f: f)), \
         patch("src_scanner.set_evidence_store"), \
         patch("src_scanner.clear_evidence_store"):
        MockRegistry.list.return_value = [MagicMock()]
        # run_all returns findings on the home page + on the discovered endpoint
        MockRegistry.run_all = AsyncMock(return_value={"det": [finding]})
        crawler_inst = MockCrawler.return_value
        crawler_inst.discover = AsyncMock(return_value=[ep])
        fuzzer_inst = MockFuzzer.return_value
        fuzzer_inst.fuzz_multiple = AsyncMock(return_value={})

        result = await scan_service.run_plugin_scan(
            url="https://example.com",
            headers={},
            is_https=True,
            ssl_info={},
            deep=True,
        )

    assert result["success"] is True
    assert result["summary"]["total"] >= 1


async def test_run_plugin_scan_discovery_failure_does_not_break_scan():
    with patch.object(scan_service, "DetectorRegistry") as MockRegistry, \
         patch.object(scan_service, "DiscoveryCrawler") as MockCrawler, \
         patch.object(scan_service, "FuzzEngine") as MockFuzzer, \
         patch.object(scan_service, "_run_cross_validation", new=AsyncMock(side_effect=lambda f: f)), \
         patch("src_scanner.set_evidence_store"), \
         patch("src_scanner.clear_evidence_store"):
        MockRegistry.list.return_value = [MagicMock()]
        MockRegistry.run_all = AsyncMock(return_value={})
        crawler_inst = MockCrawler.return_value
        crawler_inst.discover = AsyncMock(side_effect=RuntimeError("crawl failed"))
        fuzzer_inst = MockFuzzer.return_value
        fuzzer_inst.fuzz_multiple = AsyncMock(return_value={})

        result = await scan_service.run_plugin_scan(
            url="https://example.com",
            headers={},
            is_https=True,
            ssl_info={},
            deep=True,
        )

    # discovery failure is swallowed; scan still succeeds
    assert result["success"] is True


# ===========================================================================
# vuln_intel_service.py tests
# ===========================================================================


@pytest.fixture(autouse=True)
def _reset_nvd_rate_limiter(monkeypatch):
    """Disable NVD rate-limit sleeping and reset the throttle timestamp."""
    monkeypatch.setattr(vuln_intel_service, "NVD_REQUEST_INTERVAL_SECONDS", 0.0)
    monkeypatch.setattr(vuln_intel_service, "_last_nvd_request_at", 0.0)


def test_ensure_cve_table_creates_tables():
    vuln_intel_service.ensure_cve_table()
    from app.db.session import get_db_connection

    with get_db_connection() as conn:
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
    assert "cve_records" in tables
    assert "cve_components" in tables


def test_parse_cve_item_full_record():
    record = vuln_intel_service._parse_cve_item(_sample_nvd_item())
    assert record is not None
    assert record["cve_id"] == "CVE-2021-44228"
    assert "log4j" in record["description"]
    assert record["severity"] == "critical"
    assert record["cvss_score"] == 9.8
    assert "CVSS:3.1" in record["cvss_vector"]
    refs = json.loads(record["references_json"])
    assert refs[0]["url"] == "https://example.com/advisory"
    cpes = json.loads(record["cpe_matches_json"])
    assert cpes[0]["criteria"].startswith("cpe:2.3:a:apache:log4j")
    assert record["published_date"] == "2021-12-10T00:00:00.000"


def test_parse_cve_item_missing_id_returns_none():
    item = {"cve": {"id": "", "descriptions": []}}
    assert vuln_intel_service._parse_cve_item(item) is None


def test_parse_cve_item_non_cve_prefix_returns_none():
    item = {"cve": {"id": "GHSA-xxxx-yyyy-zzzz"}}
    assert vuln_intel_service._parse_cve_item(item) is None


def test_parse_cve_item_uses_fallback_description_when_no_english():
    item = {
        "cve": {
            "id": "CVE-2020-0001",
            "descriptions": [{"lang": "zh", "value": "中文描述"}],
            "metrics": {},
            "references": [],
            "configurations": [],
            "published": "",
            "lastModified": "",
        }
    }
    record = vuln_intel_service._parse_cve_item(item)
    assert record is not None
    assert record["description"] == "中文描述"
    assert record["severity"] == "unknown"
    assert record["cvss_score"] == 0.0


def test_parse_cve_item_accepts_bare_cve_dict():
    # When item already is the cve dict (no "cve" wrapper)
    bare = {
        "id": "CVE-2022-0002",
        "descriptions": [{"lang": "en", "value": "desc"}],
        "metrics": {},
        "references": [],
        "configurations": [],
        "published": "p",
        "lastModified": "m",
    }
    record = vuln_intel_service._parse_cve_item(bare)
    assert record is not None
    assert record["cve_id"] == "CVE-2022-0002"


def test_parse_cve_item_falls_back_to_cvss_v2():
    item = {
        "cve": {
            "id": "CVE-2019-0003",
            "descriptions": [{"lang": "en", "value": "v2 only"}],
            "metrics": {
                "cvssMetricV2": [
                    {
                        "cvssData": {
                            "baseScore": 7.5,
                            "vectorString": "CVSS:2.0/AV:N/AC:L/Au:N/C:P/I:P/A:P",
                        },
                        "baseSeverity": "HIGH",
                    }
                ]
            },
            "references": [],
            "configurations": [],
            "published": "",
            "lastModified": "",
        }
    }
    record = vuln_intel_service._parse_cve_item(item)
    assert record is not None
    assert record["severity"] == "high"
    assert record["cvss_score"] == 7.5


def test_parse_cpe_product_valid():
    vendor, product = vuln_intel_service._parse_cpe_product(
        "cpe:2.3:a:apache:log4j:2.14.0:*:*:*:*:*:*:*"
    )
    assert vendor == "apache"
    assert product == "log4j"


def test_parse_cpe_product_invalid_returns_empty():
    assert vuln_intel_service._parse_cpe_product("not-a-cpe") == ("", "")
    assert vuln_intel_service._parse_cpe_product("") == ("", "")


def test_save_cve_records_empty_returns_zero():
    assert vuln_intel_service._save_cve_records([]) == 0


def test_save_cve_records_persists_and_indexes_components():
    record = vuln_intel_service._parse_cve_item(_sample_nvd_item())
    inserted = vuln_intel_service._save_cve_records([record])
    assert inserted == 1

    cached = vuln_intel_service.get_cve_from_cache("CVE-2021-44228")
    assert cached is not None
    assert cached["cve_id"] == "CVE-2021-44228"
    assert cached["severity"] == "critical"

    comps = vuln_intel_service.get_cves_for_component("log4j")
    assert any(c["cve_id"] == "CVE-2021-44228" for c in comps)


def test_save_cve_records_upserts_on_conflict():
    record = vuln_intel_service._parse_cve_item(_sample_nvd_item())
    vuln_intel_service._save_cve_records([record])
    # mutate description and save again
    record["description"] = "Updated description text"
    vuln_intel_service._save_cve_records([record])
    cached = vuln_intel_service.get_cve_from_cache("CVE-2021-44228")
    assert cached is not None
    assert cached["description"] == "Updated description text"


async def test_fetch_nvd_cve_invalid_id_returns_none():
    assert await vuln_intel_service.fetch_nvd_cve("not-a-cve") is None
    assert await vuln_intel_service.fetch_nvd_cve("") is None


async def test_fetch_nvd_cve_normalizes_and_caches():
    payload = {"vulnerabilities": [_sample_nvd_item("CVE-2021-9999")]}

    def handler(request: httpx.Request) -> httpx.Response:
        assert "cveId=CVE-2021-9999" in str(request.url)
        return httpx.Response(200, json=payload)

    with _mock_httpx(handler):
        record = await vuln_intel_service.fetch_nvd_cve("cve-2021-9999")

    assert record is not None
    assert record["cve_id"] == "CVE-2021-9999"
    # cached locally
    assert vuln_intel_service.get_cve_from_cache("CVE-2021-9999") is not None


async def test_fetch_nvd_cve_no_vulnerabilities_returns_none():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"vulnerabilities": []})

    with _mock_httpx(handler):
        assert await vuln_intel_service.fetch_nvd_cve("CVE-2020-1234") is None


async def test_fetch_nvd_cve_http_error_returns_none():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="server error")

    with _mock_httpx(handler):
        assert await vuln_intel_service.fetch_nvd_cve("CVE-2020-4321") is None


async def test_search_nvd_cves_empty_keyword_returns_empty():
    records, total = await vuln_intel_service.search_nvd_cves("")
    assert records == []
    assert total == 0


async def test_search_nvd_cves_returns_and_caches_records():
    payload = {
        "vulnerabilities": [_sample_nvd_item("CVE-2023-1111"), _sample_nvd_item("CVE-2023-2222")],
        "totalResults": 2,
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert "keywordSearch=log4j" in str(request.url)
        return httpx.Response(200, json=payload)

    with _mock_httpx(handler):
        records, total = await vuln_intel_service.search_nvd_cves("log4j")

    assert len(records) == 2
    assert total == 2
    assert {r["cve_id"] for r in records} == {"CVE-2023-1111", "CVE-2023-2222"}
    # cached
    assert vuln_intel_service.get_cve_from_cache("CVE-2023-1111") is not None


async def test_search_nvd_cves_error_returns_empty():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, text="forbidden")

    with _mock_httpx(handler):
        records, total = await vuln_intel_service.search_nvd_cves("denied")
    assert records == []
    assert total == 0


async def test_sync_recent_nvd_cves_single_page():
    payload = {
        "vulnerabilities": [_sample_nvd_item("CVE-2024-0001")],
        "totalResults": 1,
    }

    def handler(request: httpx.Request) -> httpx.Request | httpx.Response:
        return httpx.Response(200, json=payload)

    with _mock_httpx(handler):
        saved, fetched = await vuln_intel_service.sync_recent_nvd_cves(days=7)

    assert fetched == 1
    assert saved == 1
    assert vuln_intel_service.get_cve_from_cache("CVE-2024-0001") is not None


async def test_sync_recent_nvd_cves_multiple_pages():
    page1 = {
        "vulnerabilities": [_sample_nvd_item("CVE-2024-0010"), _sample_nvd_item("CVE-2024-0011")],
        "totalResults": 3,
    }
    page2 = {
        "vulnerabilities": [_sample_nvd_item("CVE-2024-0012")],
        "totalResults": 3,
    }
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(200, json=page1 if calls["n"] == 1 else page2)

    with _mock_httpx(handler):
        saved, fetched = await vuln_intel_service.sync_recent_nvd_cves(days=1)

    assert fetched == 3
    assert saved == 3
    assert calls["n"] == 2


async def test_sync_recent_nvd_cves_stops_on_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="down")

    with _mock_httpx(handler):
        saved, fetched = await vuln_intel_service.sync_recent_nvd_cves(days=1)

    assert saved == 0
    assert fetched == 0


def test_get_cve_from_cache_empty_id_returns_none():
    assert vuln_intel_service.get_cve_from_cache("") is None
    assert vuln_intel_service.get_cve_from_cache("   ") is None


def test_get_cve_from_cache_nonexistent_returns_none():
    assert vuln_intel_service.get_cve_from_cache("CVE-1900-0000") is None


def test_search_cve_cache_empty_keyword_returns_empty():
    assert vuln_intel_service.search_cve_cache("") == []


def test_search_cve_cache_matches_keyword():
    record = vuln_intel_service._parse_cve_item(_sample_nvd_item("CVE-2099-SEARCH"))
    vuln_intel_service._save_cve_records([record])
    results = vuln_intel_service.search_cve_cache("log4j")
    assert any(r["cve_id"] == "CVE-2099-SEARCH" for r in results)


def test_get_cves_for_component_nonexistent_returns_empty():
    results = vuln_intel_service.get_cves_for_component("definitely-not-a-product-xyz")
    assert results == []


def test_get_cve_stats_returns_dict_shape():
    stats = vuln_intel_service.get_cve_stats()
    assert "total_cached" in stats
    assert "by_severity" in stats
    assert "latest_cached" in stats
    assert isinstance(stats["by_severity"], dict)
    # at least the records we inserted above exist
    assert stats["total_cached"] >= 1


# ===========================================================================
# discovery_crawler.py tests
# ===========================================================================


def test_same_origin_true():
    assert _same_origin("https://example.com/a", "https://example.com/b") is True


def test_same_origin_different_scheme():
    assert _same_origin("https://example.com", "http://example.com") is False


def test_same_origin_different_host():
    assert _same_origin("https://example.com", "https://evil.com") is False


def test_same_origin_case_insensitive_host():
    assert _same_origin("https://Example.com", "https://example.com") is True


def test_normalize_url_strips_fragment():
    assert _normalize_url("https://example.com/a?b=1#frag") == "https://example.com/a?b=1"


def test_normalize_url_preserves_query():
    assert _normalize_url("https://example.com/p?x=1&y=2") == "https://example.com/p?x=1&y=2"


def test_is_interesting_path_skips_static_assets():
    for path in ["/style.css", "/app.js", "/logo.png", "/data.json", "/font.woff2"]:
        assert _is_interesting_path(path) is False


def test_is_interesting_path_skips_logout():
    assert _is_interesting_path("/logout") is False
    assert _is_interesting_path("/signout") is False
    assert _is_interesting_path("/unsubscribe") is False


def test_is_interesting_path_keeps_dynamic_paths():
    assert _is_interesting_path("/users/profile") is True
    assert _is_interesting_path("/search?q=1") is True


def test_build_form_body_encodes_inputs():
    body = _build_form_body([{"name": "q", "value": "x"}, {"name": "page", "value": ""}])
    assert "q=x" in body
    assert "page=test" in body  # blank value falls back to "test"


def test_link_extractor_extracts_links_and_forms():
    html = """
    <html><body>
      <a href="/about">About</a>
      <a href="https://other.com/x">Other</a>
      <form action="/login" method="POST">
        <input type="text" name="user" value="admin">
        <input type="password" name="pass">
      </form>
    </body></html>
    """
    extractor = _LinkExtractor("https://example.com/")
    extractor.feed(html)
    assert "https://example.com/about" in extractor.links
    assert "https://other.com/x" in extractor.links
    assert len(extractor.forms) == 1
    form = extractor.forms[0]
    assert form["action"] == "https://example.com/login"
    assert form["method"] == "POST"
    assert {i["name"] for i in form["inputs"]} == {"user", "pass"}


def test_link_extractor_form_without_action_uses_base():
    html = '<form><input name="q"></form>'
    extractor = _LinkExtractor("https://example.com/page")
    extractor.feed(html)
    assert extractor.forms[0]["action"] == "https://example.com/page"
    assert extractor.forms[0]["method"] == "GET"


def test_discovered_endpoint_defaults():
    ep = DiscoveredEndpoint(url="https://example.com/x")
    assert ep.method == "GET"
    assert ep.body == ""
    assert ep.parameter_names == []
    assert ep.source == "homepage"


async def test_discover_invalid_url_returns_empty():
    crawler = DiscoveryCrawler()
    assert await crawler.discover("not-a-url") == []
    assert await crawler.discover("https://") == []


async def test_discover_extracts_homepage_links_and_forms():
    html = """
    <html><body>
      <a href="/dashboard">Dashboard</a>
      <a href="https://example.com/profile">Profile</a>
      <a href="https://evil.com/x">Evil</a>
      <form action="/search" method="GET">
        <input name="q" value="test">
      </form>
    </body></html>
    """
    pages = {
        "https://example.com/": httpx.Response(200, text=html, headers={"content-type": "text/html"}),
        "https://example.com/dashboard": httpx.Response(
            200, text="<html><body>dashboard</body></html>", headers={"content-type": "text/html"}
        ),
        "https://example.com/profile": httpx.Response(
            200, text="<html><body>profile</body></html>", headers={"content-type": "text/html"}
        ),
        "https://example.com/robots.txt": httpx.Response(404, text=""),
        "https://example.com/sitemap.xml": httpx.Response(404, text=""),
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return pages.get(str(request.url), httpx.Response(404))

    crawler = DiscoveryCrawler(max_pages=5)
    with _mock_httpx(handler):
        endpoints = await crawler.discover("https://example.com/")

    urls = {ep.url for ep in endpoints}
    assert "https://example.com/" in urls
    assert "https://example.com/dashboard" in urls
    assert "https://example.com/profile" in urls
    assert "https://evil.com/x" not in urls  # cross-origin filtered
    # the form is captured
    form_eps = [ep for ep in endpoints if ep.source == "form"]
    assert len(form_eps) == 1
    assert form_eps[0].url == "https://example.com/search"
    assert form_eps[0].method == "GET"
    assert "q" in form_eps[0].parameter_names


async def test_discover_respects_max_pages():
    pages = {}
    for i in range(5):
        pages[f"https://example.com/p{i}"] = httpx.Response(
            200,
            text=f'<a href="/p{i + 1}">next</a>',
            headers={"content-type": "text/html"},
        )
    pages["https://example.com/robots.txt"] = httpx.Response(404)
    pages["https://example.com/sitemap.xml"] = httpx.Response(404)

    def handler(request: httpx.Request) -> httpx.Response:
        return pages.get(str(request.url), httpx.Response(404))

    crawler = DiscoveryCrawler(max_pages=2, total_timeout=10.0)
    with _mock_httpx(handler):
        endpoints = await crawler.discover("https://example.com/p0")

    visited = {ep.url for ep in endpoints if ep.source == "homepage"}
    assert len(visited) <= 2


async def test_discover_parses_sitemap():
    sitemap_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset><url><loc>https://example.com/from-sitemap</loc></url></urlset>'
    )
    homepage = httpx.Response(
        200, text="<html><body>home</body></html>", headers={"content-type": "text/html"}
    )
    pages = {
        "https://example.com/": homepage,
        "https://example.com/robots.txt": httpx.Response(200, text=""),
        "https://example.com/sitemap.xml": httpx.Response(200, text=sitemap_xml),
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return pages.get(str(request.url), httpx.Response(404))

    crawler = DiscoveryCrawler(max_pages=5)
    with _mock_httpx(handler):
        endpoints = await crawler.discover("https://example.com/")

    sources = {ep.source for ep in endpoints}
    assert "sitemap" in sources
    assert any(ep.url == "https://example.com/from-sitemap" for ep in endpoints)


async def test_discover_robots_sitemap_directive():
    robots = "Sitemap: https://example.com/robots_sitemap.xml\nUser-agent: *\n"
    sitemap_xml = (
        '<urlset><url><loc>https://example.com/from-robots</loc></url></urlset>'
    )
    pages = {
        "https://example.com/": httpx.Response(
            200, text="<html></html>", headers={"content-type": "text/html"}
        ),
        "https://example.com/robots.txt": httpx.Response(200, text=robots),
        "https://example.com/sitemap.xml": httpx.Response(404),
        "https://example.com/robots_sitemap.xml": httpx.Response(200, text=sitemap_xml),
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return pages.get(str(request.url), httpx.Response(404))

    crawler = DiscoveryCrawler(max_pages=5)
    with _mock_httpx(handler):
        endpoints = await crawler.discover("https://example.com/")

    assert any(ep.url == "https://example.com/from-robots" for ep in endpoints)


async def test_discover_handles_request_errors_gracefully():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    crawler = DiscoveryCrawler(max_pages=3, total_timeout=5.0)
    with _mock_httpx(handler):
        endpoints = await crawler.discover("https://example.com/")

    assert endpoints == []


async def test_discover_skips_non_html_responses():
    pages = {
        "https://example.com/": httpx.Response(200, text="plain", headers={"content-type": "text/plain"}),
        "https://example.com/robots.txt": httpx.Response(404),
        "https://example.com/sitemap.xml": httpx.Response(404),
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return pages.get(str(request.url), httpx.Response(404))

    crawler = DiscoveryCrawler(max_pages=3)
    with _mock_httpx(handler):
        endpoints = await crawler.discover("https://example.com/")

    # non-html content-type is skipped, so no homepage endpoint recorded
    assert all(ep.source != "homepage" for ep in endpoints) or endpoints == []


async def test_discover_dedupes_same_url_method():
    html = '<a href="/">home</a><a href="/.">dot</a>'
    pages = {
        "https://example.com/": httpx.Response(200, text=html, headers={"content-type": "text/html"}),
        "https://example.com/robots.txt": httpx.Response(404),
        "https://example.com/sitemap.xml": httpx.Response(404),
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return pages.get(str(request.url), httpx.Response(404))

    crawler = DiscoveryCrawler(max_pages=5)
    with _mock_httpx(handler):
        endpoints = await crawler.discover("https://example.com/")

    # homepage url should appear only once
    homepage_urls = [ep.url for ep in endpoints if ep.url == "https://example.com/"]
    assert len(homepage_urls) == 1


# ===========================================================================
# cve_sources.py tests
# ===========================================================================


async def test_nvd_source_delegates_to_vuln_intel():
    record = {"cve_id": "CVE-2021-1", "severity": "high"}
    with patch.object(vuln_intel_service, "fetch_nvd_cve", new=AsyncMock(return_value=record)):
        src = cve_sources.NVDSource()
        assert await src.fetch_cve("CVE-2021-1") == record
    assert src.name == "nvd"


async def test_nvd_source_search_delegates():
    with patch.object(
        vuln_intel_service,
        "search_nvd_cves",
        new=AsyncMock(return_value=([{"cve_id": "CVE-1"}], 1)),
    ):
        src = cve_sources.NVDSource()
        records, total = await src.search("keyword", limit=5)
    assert records == [{"cve_id": "CVE-1"}]
    assert total == 1


async def test_local_cache_source_fetch_uses_cache():
    record = vuln_intel_service._parse_cve_item(_sample_nvd_item("CVE-2022-LOCAL"))
    vuln_intel_service._save_cve_records([record])
    src = cve_sources.LocalCacheSource()
    fetched = await src.fetch_cve("CVE-2022-LOCAL")
    assert fetched is not None
    assert fetched["cve_id"] == "CVE-2022-LOCAL"
    assert src.name == "local_cache"


async def test_local_cache_source_search_uses_cache():
    record = vuln_intel_service._parse_cve_item(_sample_nvd_item("CVE-2022-LOCSEARCH"))
    vuln_intel_service._save_cve_records([record])
    src = cve_sources.LocalCacheSource()
    records, total = await src.search("log4j")
    assert total >= 1
    assert any(r["cve_id"] == "CVE-2022-LOCSEARCH" for r in records)


async def test_circl_source_normalize_valid():
    src = cve_sources.CIRCLSource()
    normalized = src._normalize(
        {
            "id": "CVE-2020-1234",
            "summary": "A vulnerability",
            "severity": "HIGH",
            "cvss": 7.5,
            "Published": "2020-01-01",
            "Modified": "2020-02-01",
            "references": ["https://ref"],
        }
    )
    assert normalized is not None
    assert normalized["cve_id"] == "CVE-2020-1234"
    assert normalized["description"] == "A vulnerability"
    assert normalized["severity"] == "high"
    assert normalized["cvss_score"] == 7.5
    assert normalized["source"] == "circl"


def test_circl_source_normalize_non_cve_returns_none():
    src = cve_sources.CIRCLSource()
    assert src._normalize({"id": "GHSA-xxxx"}) is None


async def test_circl_source_fetch_cve_invalid_id_returns_none():
    src = cve_sources.CIRCLSource()
    assert await src.fetch_cve("not-cve") is None


async def test_circl_source_fetch_cve_mocked():
    data = {
        "id": "CVE-2020-CIRCL",
        "summary": "circl desc",
        "severity": "MEDIUM",
        "cvss": 5.0,
        "Published": "p",
        "Modified": "m",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url).endswith("/cve/CVE-2020-CIRCL")
        return httpx.Response(200, json=data)

    with _mock_httpx(handler):
        src = cve_sources.CIRCLSource()
        record = await src.fetch_cve("CVE-2020-CIRCL")

    assert record is not None
    assert record["cve_id"] == "CVE-2020-CIRCL"
    assert record["severity"] == "medium"


async def test_circl_source_fetch_cve_404_returns_none():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404)

    with _mock_httpx(handler):
        src = cve_sources.CIRCLSource()
        assert await src.fetch_cve("CVE-2020-NOTFOUND") is None


async def test_circl_source_search_mocked_list():
    data = [
        {"id": "CVE-2020-A", "summary": "a", "cvss": 1.0},
        {"id": "CVE-2020-B", "summary": "b", "cvss": 2.0},
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=data)

    with _mock_httpx(handler):
        src = cve_sources.CIRCLSource()
        records, total = await src.search("keyword", limit=10)

    assert total == 2
    assert {r["cve_id"] for r in records} == {"CVE-2020-A", "CVE-2020-B"}


async def test_circl_source_search_empty_keyword():
    src = cve_sources.CIRCLSource()
    records, total = await src.search("")
    assert records == []
    assert total == 0


async def test_circl_source_search_error_returns_empty():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("boom")

    with _mock_httpx(handler):
        src = cve_sources.CIRCLSource()
        records, total = await src.search("keyword")
    assert records == []
    assert total == 0


async def test_aggregator_fetch_cve_prefers_local_cache():
    record = vuln_intel_service._parse_cve_item(_sample_nvd_item("CVE-2022-AGG"))
    vuln_intel_service._save_cve_records([record])

    agg = cve_sources.CVEAggregator()
    with patch.object(vuln_intel_service, "fetch_nvd_cve", new=AsyncMock(return_value=None)):
        result = await agg.fetch_cve("CVE-2022-AGG")
    assert result is not None
    assert result["cve_id"] == "CVE-2022-AGG"
    assert result["source"] == "local_cache"


async def test_aggregator_fetch_cve_falls_back_to_nvd():
    nvd_record = {"cve_id": "CVE-2022-AGG2", "severity": "high", "description": "x"}
    agg = cve_sources.CVEAggregator()
    with patch.object(vuln_intel_service, "get_cve_from_cache", return_value=None), \
         patch.object(vuln_intel_service, "fetch_nvd_cve", new=AsyncMock(return_value=nvd_record)):
        result = await agg.fetch_cve("CVE-2022-AGG2")
    assert result is not None
    assert result["source"] == "nvd"


async def test_aggregator_fetch_cve_returns_none_when_all_sources_empty():
    agg = cve_sources.CVEAggregator()
    with patch.object(vuln_intel_service, "get_cve_from_cache", return_value=None), \
         patch.object(vuln_intel_service, "fetch_nvd_cve", new=AsyncMock(return_value=None)):
        result = await agg.fetch_cve("CVE-2999-NOPE")
    assert result is None


async def test_aggregator_fetch_cve_source_exception_does_not_break():
    agg = cve_sources.CVEAggregator()
    with patch.object(vuln_intel_service, "get_cve_from_cache", return_value=None), \
         patch.object(vuln_intel_service, "fetch_nvd_cve", new=AsyncMock(side_effect=RuntimeError("err"))), \
         patch.object(cve_sources.CIRCLSource, "fetch_cve", new=AsyncMock(return_value=None)):
        result = await agg.fetch_cve("CVE-2999-ERR")
    assert result is None


async def test_aggregator_search_local_hit_avoids_external():
    record = vuln_intel_service._parse_cve_item(_sample_nvd_item("CVE-2022-AGGSEARCH"))
    vuln_intel_service._save_cve_records([record])

    agg = cve_sources.CVEAggregator()
    with patch.object(vuln_intel_service, "search_nvd_cves", new=AsyncMock(return_value=([], 0))):
        records, total = await agg.search("log4j")
    assert any(r["cve_id"] == "CVE-2022-AGGSEARCH" for r in records)
    assert all(r["source"] == "local_cache" for r in records)


async def test_aggregator_search_local_miss_uses_external_sources():
    agg = cve_sources.CVEAggregator()
    nvd_records = [{"cve_id": "CVE-EXT-1", "description": "a"}]
    circl_records = [
        {"cve_id": "CVE-EXT-2", "description": "b"},
        {"cve_id": "CVE-EXT-1", "description": "dup"},  # duplicate id, deduped
    ]
    with patch.object(vuln_intel_service, "search_cve_cache", return_value=[]), \
         patch.object(vuln_intel_service, "search_nvd_cves", new=AsyncMock(return_value=(nvd_records, 1))):
        # CIRCL uses its own httpx; mock it out
        with patch.object(cve_sources.CIRCLSource, "search", new=AsyncMock(return_value=(circl_records, 2))):
            records, total = await agg.search("keyword", limit=10)
    ids = {r["cve_id"] for r in records}
    assert ids == {"CVE-EXT-1", "CVE-EXT-2"}
    assert total == 2


async def test_aggregator_search_external_failure_is_ignored():
    agg = cve_sources.CVEAggregator()
    with patch.object(vuln_intel_service, "search_cve_cache", return_value=[]), \
         patch.object(vuln_intel_service, "search_nvd_cves", new=AsyncMock(side_effect=RuntimeError("nvd down"))), \
         patch.object(cve_sources.CIRCLSource, "search", new=AsyncMock(return_value=([{"cve_id": "CVE-OK"}], 1))):
        records, total = await agg.search("keyword")
    assert any(r["cve_id"] == "CVE-OK" for r in records)
    assert total == 1


def test_get_aggregator_returns_singleton():
    a = cve_sources.get_aggregator()
    b = cve_sources.get_aggregator()
    assert a is b
    assert len(a.sources) == 3


def test_cve_source_abstract_cannot_instantiate():
    with pytest.raises(TypeError):
        cve_sources.CVESource()  # type: ignore[abstract]


# ===========================================================================
# fuzz_engine.py tests
# ===========================================================================


def test_extract_params_from_url_query():
    params = _extract_params("https://example.com/p?id=1&name=abc")
    assert params["id"] == ["1"]
    assert params["name"] == ["abc"]


def test_extract_params_no_query_returns_empty():
    assert _extract_params("https://example.com/p") == {}


def test_extract_params_from_form_body():
    params = _extract_params(
        "https://example.com/p",
        body="user=admin&pass=secret",
        content_type="application/x-www-form-urlencoded",
    )
    assert params["user"] == ["admin"]
    assert params["pass"] == ["secret"]


def test_extract_params_ignores_body_without_form_content_type():
    params = _extract_params("https://example.com/p?id=1", body="user=admin", content_type="application/json")
    assert "user" not in params
    assert params["id"] == ["1"]


def test_fuzz_engine_defaults():
    engine = FuzzEngine()
    assert engine.techniques == ["sqli", "xss", "cmdi", "traversal", "ssrf", "open_redirect", "xxe", "crlf"]
    assert engine.max_params == 15


def test_fuzz_engine_custom_techniques():
    engine = FuzzEngine(techniques=["sqli"], max_params=2)
    assert engine.techniques == ["sqli"]
    assert engine.max_params == 2


def test_build_fuzz_url_replaces_target_param():
    engine = FuzzEngine()
    url = engine._build_fuzz_url(
        "https://example.com/p",
        {"id": ["1"], "name": ["abc"]},
        "id",
        "' OR 1=1",
    )
    assert "id=%27+OR+1%3D1" in url
    assert "name=abc" in url


def test_detect_evidence_sqli_error():
    engine = FuzzEngine()
    ev = engine._detect_evidence("sqli", "'", "you have an error in your sql syntax near")
    assert ev == "sql_error"


def test_detect_evidence_command_output():
    engine = FuzzEngine()
    ev = engine._detect_evidence("cmdi", ";id", "uid=0(root) gid=0(root)")
    assert ev == "cmd_output"


def test_detect_evidence_xss_requires_reflection():
    engine = FuzzEngine()
    # payload reflected -> detected
    payload = "<script>alert(1)</script>"
    assert engine._detect_evidence("xss", payload, payload.lower()) == "xss_reflected"
    # pattern present but payload not reflected -> not detected
    assert engine._detect_evidence("xss", payload, "<script>alert(1)</script>".lower()) == "xss_reflected"
    assert engine._detect_evidence("xss", payload, "no reflection here") == ""


def test_detect_evidence_traversal_passwd():
    engine = FuzzEngine()
    assert engine._detect_evidence("traversal", "../etc/passwd", "root:x:0:0:root:/root:/bin/bash") == "passwd_content"


def test_detect_evidence_no_match_returns_empty():
    engine = FuzzEngine()
    assert engine._detect_evidence("sqli", "'", "normal response with no error") == ""


def test_fuzz_payloads_contain_all_techniques():
    for tech in ["sqli", "xss", "cmdi", "traversal", "ssrf", "open_redirect", "xxe", "crlf"]:
        assert tech in FUZZ_PAYLOADS
        assert len(FUZZ_PAYLOADS[tech]) > 0


async def test_fuzz_url_no_params_returns_empty():
    engine = FuzzEngine()
    client = AsyncMock()
    result = await engine.fuzz_url(client, "https://example.com/p")
    assert result == []
    client.get.assert_not_awaited()


async def test_fuzz_url_detects_sqli_evidence():
    engine = FuzzEngine(techniques=["sqli"], max_params=5)
    client = AsyncMock()
    client.get.return_value = httpx.Response(
        500, text="error in your SQL syntax near ' OR '1'='1", request=httpx.Request("GET", "https://x")
    )
    results = await engine.fuzz_url(client, "https://example.com/p?id=1")
    assert len(results) >= 1
    assert all(r.technique == "sqli" for r in results)
    assert any(r.evidence_type == "sql_error" for r in results)
    assert all(r.confidence == "high" for r in results if r.evidence_type == "sql_error")


async def test_fuzz_url_no_evidence_returns_empty():
    engine = FuzzEngine(techniques=["sqli"], max_params=5)
    client = AsyncMock()
    client.get.return_value = httpx.Response(200, text="ok", request=httpx.Request("GET", "https://x"))
    results = await engine.fuzz_url(client, "https://example.com/p?id=1")
    assert results == []


async def test_fuzz_url_can_probe_form_posts_and_detect_xxe():
    engine = FuzzEngine(techniques=["xxe"], max_params=5)

    async def handler(request):
        assert request.method == "POST"
        body = request.content.decode(errors="ignore")
        form = urllib.parse.parse_qs(body, keep_blank_values=True)
        decoded_values = " ".join(urllib.parse.unquote(v) for values in form.values() for v in values)
        if "DOCTYPE" in decoded_values or "entity" in decoded_values:
            return httpx.Response(200, text="xml parsing error: DOCTYPE not allowed", request=request)
        return httpx.Response(200, text="ok", request=request)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    try:
        results = await engine.fuzz_url(
            client,
            "https://example.com/upload",
            body="xml=1",
            content_type="application/x-www-form-urlencoded",
            method="POST",
        )
    finally:
        await client.aclose()

    assert results
    assert all(r.technique == "xxe" for r in results)
    assert any(r.evidence_type == "doctype" for r in results)


async def test_fuzz_url_swallows_request_exceptions():
    engine = FuzzEngine(techniques=["sqli"], max_params=5)
    client = AsyncMock()
    client.get.side_effect = httpx.ConnectError("boom")
    results = await engine.fuzz_url(client, "https://example.com/p?id=1")
    assert results == []


async def test_fuzz_multiple_aggregates_results():
    # both urls have a param; the /a path returns sql_error evidence, /b does not.
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/a":
            return httpx.Response(200, text="error in your sql syntax", request=request)
        return httpx.Response(200, text="ok", request=request)

    engine = FuzzEngine(techniques=["sqli"], max_params=3, request_timeout=2.0)
    with _mock_httpx(handler):
        results = await engine.fuzz_multiple(
            ["https://example.com/a?id=1", "https://example.com/b?name=x"],
            max_concurrency=2,
        )

    assert "https://example.com/a?id=1" in results
    assert "https://example.com/b?name=x" not in results  # no evidence -> omitted
    assert all(r.technique == "sqli" for r in results["https://example.com/a?id=1"])


async def test_fuzz_multiple_empty_urls():
    engine = FuzzEngine()
    with _mock_httpx(lambda r: httpx.Response(200, text="ok")):
        assert await engine.fuzz_multiple([]) == {}


def test_fuzz_results_to_findings_maps_fields():
    results = [
        FuzzResult(
            parameter="id",
            payload="' OR '1'='1",
            technique="sqli",
            response_snippet="sql syntax error",
            status_code=500,
            response_length=42,
            evidence_type="sql_error",
            confidence="high",
        )
    ]
    findings = fuzz_results_to_findings(results, "https://example.com/p?id=1")
    assert len(findings) == 1
    f = findings[0]
    assert f["type"] == "sqli"
    assert f["severity"] == "high"
    assert f["url"] == "https://example.com/p?id=1"
    assert f["parameter"] == "id"
    assert f["confidence"] == "high"
    assert f["id"].startswith("FUZZ-")
    assert "evidence" in f
    assert f["evidence"]["payload"] == "' OR '1'='1"


def test_fuzz_results_to_findings_empty():
    assert fuzz_results_to_findings([], "https://example.com") == []


def test_fuzz_results_to_findings_severity_map():
    for tech, sev in [
        ("sqli", "high"),
        ("xss", "medium"),
        ("cmdi", "high"),
        ("traversal", "high"),
        ("ssrf", "high"),
        ("open_redirect", "medium"),
        ("xxe", "high"),
        ("crlf", "medium"),
    ]:
        findings = fuzz_results_to_findings(
            [FuzzResult(parameter="p", payload="x", technique=tech)], "https://x"
        )
        assert findings[0]["severity"] == sev


# ===========================================================================
# tasks/manager.py tests
# ===========================================================================


def test_manager_init_validates_max_concurrent():
    with pytest.raises(ValueError):
        ScanTaskManager(max_concurrent=0)


def test_manager_init_validates_task_timeout():
    with pytest.raises(ValueError):
        ScanTaskManager(task_timeout=0)
    with pytest.raises(ValueError):
        ScanTaskManager(task_timeout=-1)


def test_manager_init_validates_max_retained():
    with pytest.raises(ValueError):
        ScanTaskManager(max_retained=-1)


def test_manager_scan_task_to_dict():
    task = ManagerScanTask(task_id="SCAN-1", url="https://x", user_id=1)
    d = task.to_dict()
    assert d["task_id"] == "SCAN-1"
    assert d["status"] == "pending"
    assert d["url"] == "https://x"
    assert d["progress"] == 0
    assert d["result"] is None
    assert d["error"] is None


def test_task_status_enum_values():
    assert TaskStatus.PENDING.value == "pending"
    assert TaskStatus.COMPLETED.value == "completed"
    assert TaskStatus.TIMEOUT.value == "timeout"
    assert TaskStatus.CANCELLED.value == "cancelled"


async def test_manager_submit_and_complete():
    async def scan_func(url, *, progress_cb, **kwargs):
        progress_cb(50)
        return {"url": url, "ok": True}

    mgr = ScanTaskManager(max_concurrent=2, task_timeout=10)
    tid = await mgr.submit("https://example.com", 1, "standard", scan_func)

    for _ in range(100):
        if mgr.get_task(tid).status == TaskStatus.COMPLETED:
            break
        await asyncio.sleep(0.02)

    task = mgr.get_task(tid)
    assert task.status == TaskStatus.COMPLETED
    assert task.progress == 100
    assert task.result == {"url": "https://example.com", "ok": True}
    assert task.started_at is not None
    assert task.completed_at is not None

    status = mgr.get_task_status(tid)
    assert status["found"] is True
    assert status["status"] == "completed"
    assert status["progress"] == 100


async def test_manager_submit_non_dict_result_wrapped():
    async def scan_func(url, *, progress_cb, **kwargs):
        return "plain-string-result"

    mgr = ScanTaskManager()
    tid = await mgr.submit("https://x", 1, "standard", scan_func)
    for _ in range(100):
        if mgr.get_task(tid).status == TaskStatus.COMPLETED:
            break
        await asyncio.sleep(0.02)

    task = mgr.get_task(tid)
    assert task.status == TaskStatus.COMPLETED
    assert task.result == {"result": "plain-string-result"}


async def test_manager_failed_task_records_error():
    async def scan_func(url, *, progress_cb, **kwargs):
        raise ValueError("scan broke")

    mgr = ScanTaskManager()
    tid = await mgr.submit("https://x", 1, "standard", scan_func)
    for _ in range(100):
        if mgr.get_task(tid).status == TaskStatus.FAILED:
            break
        await asyncio.sleep(0.02)

    task = mgr.get_task(tid)
    assert task.status == TaskStatus.FAILED
    assert "ValueError" in (task.error or "")
    assert "scan broke" in (task.error or "")


async def test_manager_timeout_task():
    async def scan_func(url, *, progress_cb, **kwargs):
        await asyncio.sleep(5)
        return {"ok": True}

    mgr = ScanTaskManager(task_timeout=0.2)
    tid = await mgr.submit("https://x", 1, "standard", scan_func)
    for _ in range(200):
        if mgr.get_task(tid).status == TaskStatus.TIMEOUT:
            break
        await asyncio.sleep(0.02)

    task = mgr.get_task(tid)
    assert task.status == TaskStatus.TIMEOUT
    assert "超时" in (task.error or "")


async def test_manager_progress_callback_forwards_to_user_cb():
    seen = []

    async def scan_func(url, *, progress_cb, **kwargs):
        progress_cb(10)
        progress_cb(60)
        progress_cb(100)
        return {"ok": True}

    mgr = ScanTaskManager()

    def user_cb(value):
        seen.append(value)

    tid = await mgr.submit(
        "https://x", 1, "standard", scan_func, progress_cb=user_cb
    )
    for _ in range(100):
        if mgr.get_task(tid).status == TaskStatus.COMPLETED:
            break
        await asyncio.sleep(0.02)

    assert seen == [10, 60, 100]
    assert mgr.get_task(tid).progress == 100


async def test_manager_progress_callback_user_error_ignored():
    async def scan_func(url, *, progress_cb, **kwargs):
        progress_cb(50)
        return {"ok": True}

    mgr = ScanTaskManager()

    def bad_cb(value):
        raise RuntimeError("user cb failed")

    tid = await mgr.submit("https://x", 1, "standard", scan_func, progress_cb=bad_cb)
    for _ in range(100):
        if mgr.get_task(tid).status == TaskStatus.COMPLETED:
            break
        await asyncio.sleep(0.02)

    # scan completes despite the user callback raising
    assert mgr.get_task(tid).status == TaskStatus.COMPLETED


async def test_manager_progress_clamped_and_monotonic():
    async def scan_func(url, *, progress_cb, **kwargs):
        progress_cb(150)  # out of range -> clamped to 100
        progress_cb(20)  # lower than current -> ignored (monotonic)
        return {"ok": True}

    mgr = ScanTaskManager()
    tid = await mgr.submit("https://x", 1, "standard", scan_func)
    for _ in range(100):
        if mgr.get_task(tid).status == TaskStatus.COMPLETED:
            break
        await asyncio.sleep(0.02)

    task = mgr.get_task(tid)
    assert task.status == TaskStatus.COMPLETED
    assert task.progress == 100


async def test_manager_cancel_pending_task():
    hold = asyncio.Event()

    async def blocking_scan(url, *, progress_cb, **kwargs):
        await hold.wait()
        return {"ok": True}

    mgr = ScanTaskManager(max_concurrent=1, task_timeout=30)
    t1 = await mgr.submit("https://a", 1, "standard", blocking_scan)
    # wait until t1 occupies the single slot
    for _ in range(100):
        if mgr.get_task(t1).status == TaskStatus.RUNNING:
            break
        await asyncio.sleep(0.02)
    assert mgr.get_task(t1).status == TaskStatus.RUNNING

    t2 = await mgr.submit("https://b", 1, "standard", blocking_scan)
    assert mgr.get_task(t2).status == TaskStatus.PENDING

    assert await mgr.cancel_task(t2) is True
    assert mgr.get_task(t2).status == TaskStatus.CANCELLED

    # release the blocker so the test can finish cleanly
    hold.set()
    for _ in range(100):
        if mgr.get_task(t1).status == TaskStatus.COMPLETED:
            break
        await asyncio.sleep(0.02)
    assert mgr.get_task(t1).status == TaskStatus.COMPLETED


async def test_manager_cancel_running_task():
    started = asyncio.Event()

    async def slow_scan(url, *, progress_cb, **kwargs):
        started.set()
        await asyncio.sleep(10)
        return {"ok": True}

    mgr = ScanTaskManager(max_concurrent=1, task_timeout=60)
    tid = await mgr.submit("https://x", 1, "standard", slow_scan)
    await started.wait()
    for _ in range(100):
        if mgr.get_task(tid).status == TaskStatus.RUNNING:
            break
        await asyncio.sleep(0.02)
    assert mgr.get_task(tid).status == TaskStatus.RUNNING

    assert await mgr.cancel_task(tid) is True
    for _ in range(200):
        if mgr.get_task(tid).status == TaskStatus.CANCELLED:
            break
        await asyncio.sleep(0.02)
    assert mgr.get_task(tid).status == TaskStatus.CANCELLED


async def test_manager_cancel_nonexistent_returns_false():
    mgr = ScanTaskManager()
    assert await mgr.cancel_task("SCAN-NOPE") is False


async def test_manager_cancel_already_completed_returns_false():
    async def scan_func(url, *, progress_cb, **kwargs):
        return {"ok": True}

    mgr = ScanTaskManager()
    tid = await mgr.submit("https://x", 1, "standard", scan_func)
    for _ in range(100):
        if mgr.get_task(tid).status == TaskStatus.COMPLETED:
            break
        await asyncio.sleep(0.02)

    assert await mgr.cancel_task(tid) is False


def test_manager_get_task_status_not_found():
    mgr = ScanTaskManager()
    status = mgr.get_task_status("SCAN-MISSING")
    assert status["found"] is False
    assert status["status"] == "not_found"
    assert status["progress"] == 0


def test_manager_get_task_nonexistent_returns_none():
    mgr = ScanTaskManager()
    assert mgr.get_task("SCAN-MISSING") is None


def test_manager_list_tasks_filtering_and_ordering():
    mgr = ScanTaskManager()
    t1 = ManagerScanTask(task_id="SCAN-1", url="https://a", user_id=1, created_at="2024-01-01T00:00:00")
    t2 = ManagerScanTask(task_id="SCAN-2", url="https://b", user_id=2, created_at="2024-01-02T00:00:00")
    t3 = ManagerScanTask(
        task_id="SCAN-3", url="https://c", user_id=1, status=TaskStatus.COMPLETED, created_at="2024-01-03T00:00:00"
    )
    mgr._tasks = {t1.task_id: t1, t2.task_id: t2, t3.task_id: t3}

    all_tasks = mgr.list_tasks()
    assert [t.task_id for t in all_tasks] == ["SCAN-3", "SCAN-2", "SCAN-1"]  # newest first

    user1 = mgr.list_tasks(user_id=1)
    assert {t.task_id for t in user1} == {"SCAN-1", "SCAN-3"}

    completed = mgr.list_tasks(status=TaskStatus.COMPLETED)
    assert [t.task_id for t in completed] == ["SCAN-3"]

    # status filter accepts a string value too
    completed_str = mgr.list_tasks(status="completed")
    assert [t.task_id for t in completed_str] == ["SCAN-3"]


def test_manager_list_tasks_invalid_status_string_raises():
    mgr = ScanTaskManager()
    with pytest.raises(ValueError):
        mgr.list_tasks(status="not-a-real-status")


def test_manager_get_stats_counts_by_status():
    mgr = ScanTaskManager(max_concurrent=3, task_timeout=120)
    mgr._tasks = {
        "1": ManagerScanTask(task_id="1", url="u", user_id=1, status=TaskStatus.PENDING),
        "2": ManagerScanTask(task_id="2", url="u", user_id=1, status=TaskStatus.RUNNING),
        "3": ManagerScanTask(task_id="3", url="u", user_id=1, status=TaskStatus.COMPLETED),
        "4": ManagerScanTask(task_id="4", url="u", user_id=1, status=TaskStatus.FAILED),
        "5": ManagerScanTask(task_id="5", url="u", user_id=1, status=TaskStatus.CANCELLED),
        "6": ManagerScanTask(task_id="6", url="u", user_id=1, status=TaskStatus.TIMEOUT),
    }
    stats = mgr.get_stats()
    assert stats["total"] == 6
    assert stats["pending"] == 1
    assert stats["running"] == 1
    assert stats["completed"] == 1
    assert stats["failed"] == 1
    assert stats["cancelled"] == 1
    assert stats["timeout"] == 1
    assert stats["max_concurrent"] == 3
    assert stats["task_timeout"] == 120


async def test_manager_cleanup_retains_only_recent_terminal():
    async def scan_func(url, *, progress_cb, **kwargs):
        return {"ok": True}

    mgr = ScanTaskManager(max_concurrent=5, task_timeout=10, max_retained=2)
    ids = []
    for i in range(5):
        tid = await mgr.submit(f"https://x{i}", 1, "standard", scan_func)
        ids.append(tid)
        # ensure each completes before the next to differentiate completed_at
        for _ in range(100):
            if mgr.get_task(tid).status == TaskStatus.COMPLETED:
                break
            await asyncio.sleep(0.01)

    # only the 2 most-recently completed terminal tasks should remain
    remaining = mgr.list_tasks(status=TaskStatus.COMPLETED)
    assert len(remaining) <= 2
    assert {t.task_id for t in remaining} <= set(ids)


async def test_manager_max_retained_zero_disables_cleanup():
    async def scan_func(url, *, progress_cb, **kwargs):
        return {"ok": True}

    mgr = ScanTaskManager(max_concurrent=3, task_timeout=10, max_retained=0)
    ids = []
    for i in range(6):
        tid = await mgr.submit(f"https://y{i}", 1, "standard", scan_func)
        ids.append(tid)
        for _ in range(100):
            if mgr.get_task(tid).status == TaskStatus.COMPLETED:
                break
            await asyncio.sleep(0.01)

    # max_retained=0 means cleanup is a no-op; all tasks retained
    assert len(mgr.list_tasks()) == 6


async def test_manager_kwargs_passed_to_scan_func():
    received = {}
    progress_seen = []

    async def scan_func(url, *, progress_cb, **kwargs):
        received.update(kwargs)
        received["__progress_cb_callable"] = callable(progress_cb)
        progress_cb(100)
        progress_seen.append(True)
        return {"ok": True}

    mgr = ScanTaskManager()
    tid = await mgr.submit(
        "https://x", 7, "deep", scan_func, headers={"X": "1"}, is_https=True
    )
    for _ in range(100):
        if mgr.get_task(tid).status == TaskStatus.COMPLETED:
            break
        await asyncio.sleep(0.02)

    # user-supplied kwargs are forwarded; progress_cb is injected as a callable
    assert received["headers"] == {"X": "1"}
    assert received["is_https"] is True
    assert received["__progress_cb_callable"] is True
    assert progress_seen == [True]
    # progress_cb is consumed by the named parameter, so it is not in **kwargs
    assert "progress_cb" not in received
