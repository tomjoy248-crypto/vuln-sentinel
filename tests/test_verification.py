"""Comprehensive tests for the verification modules.

Covers:
- app/verification/cross_validator.py (CrossValidator, strategies, helpers)
- app/verification/diff_engine.py (ScanDiffEngine, DiffResult, FindingSignature)

The cross validator strategies are exercised through a fake async HTTP client so
that no real network traffic is generated.
"""

from __future__ import annotations

import datetime
import os
import sys

# --- Test database / path setup (must run before importing main) -------------
os.environ.setdefault("DB_DIR", "/tmp/v11-test")
os.environ.setdefault("DB_NAME", "test.db")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import main  # noqa: E402

try:
    main.init_db()
except Exception:  # pragma: no cover - best effort init
    pass

import pytest  # noqa: E402

pytestmark = pytest.mark.asyncio

import app.verification.cross_validator as cv  # noqa: E402
from app.verification.cross_validator import (  # noqa: E402
    CrossValidator,
    VerificationResult,
    _build_test_url,
    _response_similarity,
    register_strategy,
)
from app.verification.diff_engine import (  # noqa: E402
    DiffResult,
    FindingChange,
    FindingSignature,
    ScanDiffEngine,
    _location_key,
)

# ---------------------------------------------------------------------------
# Fake HTTP layer
# ---------------------------------------------------------------------------


class FakeResponse:
    """Minimal stand-in for ``httpx.Response`` used by the strategies."""

    def __init__(self, status_code=200, text="", headers=None):
        self.status_code = status_code
        self.text = text
        self.headers = headers if headers is not None else {}


class FakeAsyncClient:
    """Fake ``httpx.AsyncClient`` that routes requests through a handler.

    ``handler`` is a callable ``(url, kwargs) -> FakeResponse | None``. Returning
    ``None`` simulates an unreachable host (mirrors ``_safe_request`` returning
    ``None`` on failure).
    """

    def __init__(self, handler=None):
        self._handler = handler
        self.calls = []

    async def get(self, url, **kwargs):
        self.calls.append(url)
        if self._handler is None:
            return FakeResponse(200, "")
        resp = self._handler(url, kwargs)
        return resp


class _RaisingTextResponse:
    status_code = 200
    headers = {}

    @property
    def text(self):
        raise UnicodeDecodeError("utf-8", b"", 0, 1, "bad")


class _RaisingClient:
    async def get(self, url, **kwargs):
        raise ValueError("network down")


# ---------------------------------------------------------------------------
# Helpers for the SSL strategy (which uses socket/ssl instead of httpx)
# ---------------------------------------------------------------------------


def _patch_ssl(monkeypatch, cert, cipher, version, *, raise_on_wrap=False, raise_cls=None):
    """Patch ``ssl``/``socket`` references inside cross_validator."""

    class _Sock:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    class _SSLSock:
        def getpeercert(self):
            return cert

        def cipher(self):
            return cipher

        def version(self):
            return version

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    class _Ctx:
        def __init__(self, *args, **kwargs):
            self.check_hostname = True
            self.verify_mode = None
            self.minimum_version = None

        def wrap_socket(self, sock, server_hostname=None):
            if raise_on_wrap:
                raise raise_cls("handshake failed")
            return _SSLSock()

    monkeypatch.setattr(cv.ssl, "create_default_context", lambda: _Ctx())
    monkeypatch.setattr(cv.ssl, "SSLContext", _Ctx)
    monkeypatch.setattr(cv.socket, "create_connection", lambda addr, timeout=None: _Sock())


# ===========================================================================
# VerificationResult dataclass
# ===========================================================================


def test_verification_result_defaults():
    result = VerificationResult(finding_id="f1", vuln_type="sqli", verified=True, verification_score=80)
    assert result.techniques == []
    assert result.summary == ""


def test_verification_result_to_dict_roundtrip():
    result = VerificationResult(
        finding_id="f1",
        vuln_type="xss",
        verified=False,
        verification_score=30,
        techniques=[{"name": "reflection", "passed": False}],
        summary="low confidence",
    )
    d = result.to_dict()
    assert d == {
        "finding_id": "f1",
        "vuln_type": "xss",
        "verified": False,
        "verification_score": 30,
        "techniques": [{"name": "reflection", "passed": False}],
        "summary": "low confidence",
    }


# ===========================================================================
# Strategy registry
# ===========================================================================


def test_all_expected_strategies_registered():
    expected = {
        "sqli",
        "xss",
        "cmdi",
        "traversal",
        "open_redirect",
        "ssrf",
        "csrf",
        "outdated_component",
        "info_leak",
        "ssl",
        "header_missing",
    }
    assert expected.issubset(cv._VERIFICATION_STRATEGIES.keys())


def test_register_strategy_decorator_returns_function_unchanged():
    @register_strategy("__test_strategy__")
    async def my_strategy(validator, finding):
        return VerificationResult(finding_id="x", vuln_type="__test_strategy__", verified=True, verification_score=99)

    assert cv._VERIFICATION_STRATEGIES["__test_strategy__"] is my_strategy
    cv._VERIFICATION_STRATEGIES.pop("__test_strategy__", None)


# ===========================================================================
# CrossValidator - low level helpers
# ===========================================================================


async def test_safe_request_returns_response_from_client():
    validator = CrossValidator(client=FakeAsyncClient(handler=lambda u, k: FakeResponse(201, "ok")))
    resp = await validator._safe_request("get", "http://x/y")
    assert resp is not None
    assert resp.status_code == 201
    assert resp.text == "ok"


async def test_safe_request_returns_none_on_exception():
    validator = CrossValidator(client=_RaisingClient())
    resp = await validator._safe_request("get", "http://x/y")
    assert resp is None


async def test_safe_read_body_none_returns_empty():
    validator = CrossValidator(client=FakeAsyncClient())
    assert await validator._safe_read_body(None) == ""


async def test_safe_read_body_returns_text():
    validator = CrossValidator(client=FakeAsyncClient())
    assert await validator._safe_read_body(FakeResponse(200, "hello")) == "hello"


async def test_safe_read_body_handles_decode_error():
    validator = CrossValidator(client=FakeAsyncClient())
    assert await validator._safe_read_body(_RaisingTextResponse()) == ""


async def test_get_client_returns_injected_client():
    fake = FakeAsyncClient()
    validator = CrossValidator(client=fake)
    assert await validator._get_client() is fake


async def test_get_client_fallback_creates_client():
    validator = CrossValidator(client=None)
    client = await validator._get_client()
    assert client is not None


# ===========================================================================
# CrossValidator - verify_finding / verify_batch
# ===========================================================================


async def test_verify_finding_no_strategy_returns_default():
    validator = CrossValidator(client=FakeAsyncClient())
    result = await validator.verify_finding({"id": "f1", "type": "totally_unknown_type"})
    assert result.finding_id == "f1"
    assert result.vuln_type == "totally_unknown_type"
    assert result.verified is True
    assert result.verification_score == 50
    assert result.techniques[0]["name"] == "no_strategy"
    assert result.techniques[0]["passed"] is True


async def test_verify_finding_dispatches_to_strategy():
    validator = CrossValidator(client=FakeAsyncClient())
    result = await validator.verify_finding(
        {"id": "s1", "type": "sqli", "url": "", "parameter": ""}
    )
    assert result.vuln_type == "sqli"
    assert result.verification_score == 70
    assert result.verified is True
    assert result.techniques[0]["name"] == "existing_evidence"


async def test_verify_finding_missing_id_uses_empty_string():
    validator = CrossValidator(client=FakeAsyncClient())
    result = await validator.verify_finding({"type": "unknown_xyz"})
    assert result.finding_id == ""


async def test_verify_batch_empty_list():
    validator = CrossValidator(client=FakeAsyncClient())
    assert await validator.verify_batch([]) == []


async def test_verify_batch_multiple_findings():
    validator = CrossValidator(client=FakeAsyncClient())
    findings = [
        {"id": "a", "type": "unknown_a"},
        {"id": "b", "type": "unknown_b"},
    ]
    results = await validator.verify_batch(findings)
    assert len(results) == 2
    assert all(isinstance(r, VerificationResult) for r in results)
    assert {r.finding_id for r in results} == {"a", "b"}


async def test_verify_batch_handles_strategy_exception():
    async def _raising(validator, finding):
        raise RuntimeError("boom")

    cv._VERIFICATION_STRATEGIES["__test_raises__"] = _raising
    try:
        validator = CrossValidator(client=FakeAsyncClient())
        findings = [{"id": "e1", "type": "__test_raises__"}]
        results = await validator.verify_batch(findings)
        assert len(results) == 1
        r = results[0]
        assert r.verified is True
        assert r.verification_score == 50
        assert r.techniques[0]["name"] == "error"
        assert r.techniques[0]["passed"] is False
        assert "boom" in r.techniques[0]["note"]
        assert r.finding_id == "e1"
        assert r.vuln_type == "__test_raises__"
    finally:
        cv._VERIFICATION_STRATEGIES.pop("__test_raises__", None)


# ===========================================================================
# CrossValidator - enrich_findings / status helpers / validate_finding_batch
# ===========================================================================


def test_status_from_score_thresholds():
    assert CrossValidator._status_from_score(100) == "confirmed"
    assert CrossValidator._status_from_score(70) == "confirmed"
    assert CrossValidator._status_from_score(69) == "probable"
    assert CrossValidator._status_from_score(40) == "probable"
    assert CrossValidator._status_from_score(39) == "suspected"
    assert CrossValidator._status_from_score(0) == "suspected"


def test_enrich_findings_merges_verified_result():
    validator = CrossValidator(client=FakeAsyncClient())
    findings = [{"id": "f1", "type": "sqli", "severity": "high"}]
    results = [
        VerificationResult(
            finding_id="f1",
            vuln_type="sqli",
            verified=True,
            verification_score=85,
            techniques=[{"name": "bool", "passed": True}, {"name": "time", "passed": False}],
            summary="ok",
        )
    ]
    enriched = validator.enrich_findings(findings, results)
    assert len(enriched) == 1
    f = enriched[0]
    assert f["verification_score"] == 85
    assert f["verified"] is True
    assert f["verification_techniques"] == ["bool"]
    assert "adjusted_confidence" not in f


def test_enrich_findings_marks_low_confidence_when_unverified():
    validator = CrossValidator(client=FakeAsyncClient())
    findings = [{"id": "f1", "type": "sqli"}]
    results = [
        VerificationResult(
            finding_id="f1",
            vuln_type="sqli",
            verified=False,
            verification_score=20,
            techniques=[{"name": "bool", "passed": False}],
            summary="no evidence",
        )
    ]
    enriched = validator.enrich_findings(findings, results)
    f = enriched[0]
    assert f["verified"] is False
    assert f["verification_score"] == 20
    assert f["adjusted_confidence"] == "low"
    assert f["verification_note"] == "no evidence"
    assert f["verification_techniques"] == []


def test_enrich_findings_without_matching_result_keeps_original():
    validator = CrossValidator(client=FakeAsyncClient())
    findings = [{"id": "f1", "type": "sqli", "severity": "high"}]
    results = [VerificationResult(finding_id="other", vuln_type="sqli", verified=True, verification_score=90)]
    enriched = validator.enrich_findings(findings, results)
    assert enriched == [{"id": "f1", "type": "sqli", "severity": "high"}]


def test_enrich_findings_empty_inputs():
    validator = CrossValidator(client=FakeAsyncClient())
    assert validator.enrich_findings([], []) == []


def test_enrich_findings_only_passed_techniques_recorded():
    validator = CrossValidator(client=FakeAsyncClient())
    findings = [{"id": "f1", "type": "xss"}]
    results = [
        VerificationResult(
            finding_id="f1",
            vuln_type="xss",
            verified=True,
            verification_score=70,
            techniques=[
                {"name": "a", "passed": True},
                {"name": "b", "passed": False},
                {"name": "c", "passed": True},
            ],
        )
    ]
    enriched = validator.enrich_findings(findings, results)
    assert enriched[0]["verification_techniques"] == ["a", "c"]


async def test_validate_finding_batch_confirmed_status():
    # A no-strategy finding yields score 50 (probable). Use a custom strategy
    # to force a high score (>= 70) -> "confirmed".
    async def _high(validator, finding):
        return VerificationResult(
            finding_id=finding.get("id", ""),
            vuln_type="custom_high",
            verified=True,
            verification_score=95,
            techniques=[{"name": "t", "passed": True}],
            summary="high",
        )

    cv._VERIFICATION_STRATEGIES["custom_high"] = _high
    try:
        validator = CrossValidator(client=FakeAsyncClient())
        findings = [{"id": "h1", "type": "custom_high"}]
        enriched = await validator.validate_finding_batch(findings)
        f = enriched[0]
        assert f["verification_status"] == "confirmed"
        assert f["verification_score"] == 95
        assert f["verified"] is True
        assert f["verification_metadata"]["verified"] is True
        assert f["verification_metadata"]["passed_techniques"] == ["t"]
    finally:
        cv._VERIFICATION_STRATEGIES.pop("custom_high", None)


async def test_validate_finding_batch_probable_status():
    # no strategy -> score 50 -> "probable"
    validator = CrossValidator(client=FakeAsyncClient())
    findings = [{"id": "p1", "type": "no_such_strategy"}]
    enriched = await validator.validate_finding_batch(findings)
    f = enriched[0]
    assert f["verification_status"] == "probable"
    assert f["verification_score"] == 50


async def test_validate_finding_batch_suspected_when_no_result_returned(monkeypatch):
    validator = CrossValidator(client=FakeAsyncClient())

    async def _empty_batch(findings):
        return []

    monkeypatch.setattr(validator, "verify_batch", _empty_batch)
    findings = [{"id": "n1", "type": "sqli"}]
    enriched = await validator.validate_finding_batch(findings)
    f = enriched[0]
    assert f["verification_status"] == "suspected"
    assert f["verification_score"] == 0
    assert f["verification_metadata"]["verified"] is False
    assert f["verification_metadata"]["techniques"] == []


# ===========================================================================
# Module-level helper functions
# ===========================================================================


def test_build_test_url_replaces_param_value():
    url = "http://example.com/search?q=1&page=2"
    new = _build_test_url(url, "q", "PAYLOAD")
    assert "q=PAYLOAD" in new
    assert "page=2" in new
    assert new.startswith("http://example.com/search?")


def test_build_test_url_adds_param_when_missing():
    new = _build_test_url("http://example.com/path", "id", "42")
    assert "id=42" in new


def test_build_test_url_preserves_path_and_scheme():
    new = _build_test_url("https://host.local/a/b?x=1", "x", "z")
    assert new.startswith("https://host.local/a/b?")


def test_response_similarity_identical():
    text = "line1\nline2\nline3"
    assert _response_similarity(text, text) == 1.0


def test_response_similarity_no_overlap():
    assert _response_similarity("aaa\nbbb", "ccc\nddd") == 0.0


def test_response_similarity_empty_inputs():
    assert _response_similarity("", "x") == 0.0
    assert _response_similarity("x", "") == 0.0
    assert _response_similarity("", "") == 0.0


def test_response_similarity_partial_overlap():
    a = "common\nonly_a"
    b = "common\nonly_b"
    # intersection 1, union 3 -> 1/3
    assert _response_similarity(a, b) == pytest.approx(1 / 3)


def test_response_similarity_only_newlines():
    # splitlines on "\n" yields [''], a non-empty set -> proceeds normally
    sim = _response_similarity("\n", "\n")
    assert sim == 1.0


# ===========================================================================
# Strategy: SQLi
# ===========================================================================


async def test_sqli_no_url_param_uses_existing_evidence():
    validator = CrossValidator(client=FakeAsyncClient())
    result = await validator.verify_finding({"id": "s1", "type": "sqli"})
    assert result.verification_score == 70
    assert result.verified is True
    assert result.techniques[0]["name"] == "existing_evidence"


async def test_sqli_boolean_difference_passes():
    def handler(url, kwargs):
        if "OR" in url:  # true payload 1' OR '1'='1
            return FakeResponse(200, "A" * 1000)
        if "AND" in url:  # false payload 1' AND '1'='2
            return FakeResponse(200, "B" * 100)
        return FakeResponse(200, "")

    validator = CrossValidator(client=FakeAsyncClient(handler=handler))
    result = await validator.verify_finding(
        {"id": "s2", "type": "sqli", "url": "http://t.local/search?q=1", "parameter": "q"}
    )
    techniques = {t["name"]: t for t in result.techniques}
    assert techniques["boolean_based"]["passed"] is True
    assert techniques["time_based"]["passed"] is False
    assert techniques["error_based"]["passed"] is False
    # only boolean contributes -> 35
    assert result.verification_score == 35
    assert result.verified is False


async def test_sqli_error_based_evidence_adds_score():
    def handler(url, kwargs):
        if "OR" in url:
            return FakeResponse(200, "A" * 1000)
        if "AND" in url:
            return FakeResponse(200, "B" * 100)
        return FakeResponse(200, "")

    validator = CrossValidator(client=FakeAsyncClient(handler=handler))
    result = await validator.verify_finding(
        {
            "id": "s3",
            "type": "sqli",
            "url": "http://t.local/search?q=1",
            "parameter": "q",
            "evidence": {"response": "You have an error in your SQL syntax near 'x'"},
        }
    )
    techniques = {t["name"]: t for t in result.techniques}
    assert techniques["boolean_based"]["passed"] is True
    assert techniques["error_based"]["passed"] is True
    assert techniques["time_based"]["passed"] is False
    # boolean 35 + error 30 = 65 -> verified
    assert result.verification_score == 65
    assert result.verified is True


async def test_sqli_time_based_passes_with_faked_clock(monkeypatch):
    def handler(url, kwargs):
        if "OR" in url:
            return FakeResponse(200, "A" * 1000)
        if "AND" in url:
            return FakeResponse(200, "B" * 100)
        return FakeResponse(200, "")

    class _FakeTime:
        def __init__(self, values):
            self._it = iter(values)

        def time(self):
            return next(self._it)

    monkeypatch.setattr(cv, "time", _FakeTime([100.0, 103.6]))
    validator = CrossValidator(client=FakeAsyncClient(handler=handler))
    result = await validator.verify_finding(
        {
            "id": "s4",
            "type": "sqli",
            "url": "http://t.local/search?q=1",
            "parameter": "q",
            "evidence": {"response": "sql syntax error"},
        }
    )
    techniques = {t["name"]: t for t in result.techniques}
    assert techniques["time_based"]["passed"] is True
    # boolean 35 + time 40 + error 30 = 105 -> capped 100
    assert result.verification_score == 100
    assert result.verified is True


async def test_sqli_boolean_fails_when_responses_equal():
    validator = CrossValidator(
        client=FakeAsyncClient(handler=lambda u, k: FakeResponse(200, "same" * 50))
    )
    result = await validator.verify_finding(
        {"id": "s5", "type": "sqli", "url": "http://t.local/search?q=1", "parameter": "q"}
    )
    techniques = {t["name"]: t for t in result.techniques}
    assert techniques["boolean_based"]["passed"] is False
    assert result.verification_score == 0


# ===========================================================================
# Strategy: XSS
# ===========================================================================


async def test_xss_full_verification_passes():
    payload = "<script>alert(1)</script>"
    response_body = f"reflected {payload} here"

    def handler(url, kwargs):
        return FakeResponse(200, payload)

    validator = CrossValidator(client=FakeAsyncClient(handler=handler))
    result = await validator.verify_finding(
        {
            "id": "x1",
            "type": "xss",
            "url": "http://t.local/?q=1",
            "parameter": "q",
            "evidence": {"payload": payload, "response": response_body},
        }
    )
    techniques = {t["name"]: t for t in result.techniques}
    assert techniques["payload_reflection"]["passed"] is True
    assert techniques["event_handler"]["passed"] is True
    assert techniques["encoding_bypass"]["passed"] is True
    assert result.verification_score == 100
    assert result.verified is True


async def test_xss_no_reflection_not_verified():
    validator = CrossValidator(
        client=FakeAsyncClient(handler=lambda u, k: FakeResponse(200, "nothing here"))
    )
    result = await validator.verify_finding(
        {
            "id": "x2",
            "type": "xss",
            "url": "http://t.local/?q=1",
            "parameter": "q",
            "evidence": {"payload": "<script>", "response": "no reflection"},
        }
    )
    techniques = {t["name"]: t for t in result.techniques}
    assert techniques["payload_reflection"]["passed"] is False
    assert techniques["event_handler"]["passed"] is False
    assert techniques["encoding_bypass"]["passed"] is False
    assert result.verification_score == 0
    assert result.verified is False


async def test_xss_encoding_bypass_encoded_form():
    payload = "<script>alert(1)</script>"
    encoded = (
        payload.replace("<", "%3C").replace(">", "%3E").replace("'", "%27").replace('"', "%22")
    )

    def handler(url, kwargs):
        return FakeResponse(200, encoded)

    validator = CrossValidator(client=FakeAsyncClient(handler=handler))
    result = await validator.verify_finding(
        {
            "id": "x3",
            "type": "xss",
            "url": "http://t.local/?q=1",
            "parameter": "q",
            "evidence": {"payload": payload, "response": ""},
        }
    )
    techniques = {t["name"]: t for t in result.techniques}
    assert techniques["encoding_bypass"]["passed"] is False
    assert "编码" in techniques["encoding_bypass"]["note"]


async def test_xss_missing_params_skips_encoding():
    validator = CrossValidator(client=FakeAsyncClient())
    result = await validator.verify_finding({"id": "x4", "type": "xss"})
    techniques = {t["name"]: t for t in result.techniques}
    assert "缺少必要参数" in techniques["encoding_bypass"]["note"]
    assert result.verification_score == 0


# ===========================================================================
# Strategy: CMDi
# ===========================================================================


async def test_cmdi_no_url_param_uses_existing_evidence():
    validator = CrossValidator(client=FakeAsyncClient())
    result = await validator.verify_finding({"id": "c1", "type": "cmdi"})
    assert result.verification_score == 70
    assert result.techniques[0]["name"] == "existing_evidence"


async def test_cmdi_command_output_and_cross_command():
    def handler(url, kwargs):
        if "whoami" in url:
            return FakeResponse(200, "root\n")
        return FakeResponse(200, "")

    validator = CrossValidator(client=FakeAsyncClient(handler=handler))
    result = await validator.verify_finding(
        {
            "id": "c2",
            "type": "cmdi",
            "url": "http://t.local/?cmd=1",
            "parameter": "cmd",
            "evidence": {"response": "uid=0(root) gid=0(root) groups=0(root)"},
        }
    )
    techniques = {t["name"]: t for t in result.techniques}
    assert techniques["command_output"]["passed"] is True
    assert techniques["cross_command"]["passed"] is True
    assert techniques["time_based"]["passed"] is False
    # 50 + 20 = 70 -> verified
    assert result.verification_score == 70
    assert result.verified is True


async def test_cmdi_no_indicators_not_verified():
    validator = CrossValidator(
        client=FakeAsyncClient(handler=lambda u, k: FakeResponse(200, "normal page"))
    )
    result = await validator.verify_finding(
        {"id": "c3", "type": "cmdi", "url": "http://t.local/?cmd=1", "parameter": "cmd"}
    )
    techniques = {t["name"]: t for t in result.techniques}
    assert techniques["command_output"]["passed"] is False
    assert techniques["cross_command"]["passed"] is False
    assert result.verification_score == 0


async def test_cmdi_time_based_passes_with_faked_clock(monkeypatch):
    def handler(url, kwargs):
        if "whoami" in url:
            return FakeResponse(200, "root\n")
        return FakeResponse(200, "")

    class _FakeTime:
        def __init__(self, values):
            self._it = iter(values)

        def time(self):
            return next(self._it)

    monkeypatch.setattr(cv, "time", _FakeTime([50.0, 53.0]))
    validator = CrossValidator(client=FakeAsyncClient(handler=handler))
    result = await validator.verify_finding(
        {
            "id": "c4",
            "type": "cmdi",
            "url": "http://t.local/?cmd=1",
            "parameter": "cmd",
            "evidence": {"response": "uid=0(root)"},
        }
    )
    techniques = {t["name"]: t for t in result.techniques}
    assert techniques["time_based"]["passed"] is True
    # 50 (cmd output) + 40 (time) + 20 (cross) = 110 -> capped 100
    assert result.verification_score == 100
    assert result.verified is True


# ===========================================================================
# Strategy: Traversal
# ===========================================================================


async def test_traversal_full_verification():
    def handler(url, kwargs):
        if "passwd" in url:
            return FakeResponse(200, "root:x:0:0:root:/root:/bin/bash\n")
        if "hostname" in url:
            return FakeResponse(200, "myhost\nsecondary")
        return FakeResponse(200, "")

    validator = CrossValidator(client=FakeAsyncClient(handler=handler))
    result = await validator.verify_finding(
        {
            "id": "t1",
            "type": "traversal",
            "url": "http://t.local/?file=1",
            "parameter": "file",
            "evidence": {"response": "root:x:0:0:root:/root:/bin/bash"},
        }
    )
    techniques = {t["name"]: t for t in result.techniques}
    assert techniques["file_content"]["passed"] is True
    assert techniques["encoding_bypass"]["passed"] is True
    assert techniques["alternative_file"]["passed"] is True
    assert result.verification_score == 100
    assert result.verified is True


async def test_traversal_no_file_content():
    validator = CrossValidator(
        client=FakeAsyncClient(handler=lambda u, k: FakeResponse(200, "no file content"))
    )
    result = await validator.verify_finding(
        {"id": "t2", "type": "traversal", "url": "http://t.local/?file=1", "parameter": "file"}
    )
    techniques = {t["name"]: t for t in result.techniques}
    assert techniques["file_content"]["passed"] is False
    assert techniques["encoding_bypass"]["passed"] is False
    assert techniques["alternative_file"]["passed"] is False
    assert result.verification_score == 0


async def test_traversal_windows_indicators_in_evidence():
    validator = CrossValidator(
        client=FakeAsyncClient(handler=lambda u, k: FakeResponse(200, "nothing"))
    )
    result = await validator.verify_finding(
        {
            "id": "t3",
            "type": "traversal",
            "url": "http://t.local/?file=1",
            "parameter": "file",
            "evidence": {"response": "[fonts]\n[extensions]\n[mci extensions]"},
        }
    )
    techniques = {t["name"]: t for t in result.techniques}
    assert techniques["file_content"]["passed"] is True
    # 55 only (encoding/alternative return nothing)
    assert result.verification_score == 55


async def test_traversal_missing_params_skips_encoding_and_alternative():
    validator = CrossValidator(client=FakeAsyncClient())
    result = await validator.verify_finding({"id": "t4", "type": "traversal"})
    techniques = {t["name"]: t for t in result.techniques}
    assert "缺少必要参数" in techniques["encoding_bypass"]["note"]
    assert "缺少必要参数" in techniques["alternative_file"]["note"]
    assert result.verification_score == 0


# ===========================================================================
# Strategy: Open Redirect
# ===========================================================================


async def test_open_redirect_full_verification():
    def handler(url, kwargs):
        if "attacker.example" in url:
            return FakeResponse(302, "", headers={"location": "//attacker.example"})
        if "example.com" in url:
            return FakeResponse(302, "", headers={"location": "https://evil.com"})
        return FakeResponse(200, "")

    validator = CrossValidator(client=FakeAsyncClient(handler=handler))
    result = await validator.verify_finding(
        {
            "id": "or1",
            "type": "open_redirect",
            "url": "http://t.local/?next=1",
            "parameter": "next",
            "evidence": {"headers": {"location": "https://evil.com"}},
        }
    )
    techniques = {t["name"]: t for t in result.techniques}
    assert techniques["redirect_to_external"]["passed"] is True
    assert techniques["protocol_relative_bypass"]["passed"] is True
    assert techniques["original_evidence"]["passed"] is True
    assert result.verification_score == 100
    assert result.verified is True


async def test_open_redirect_no_redirect_response():
    validator = CrossValidator(
        client=FakeAsyncClient(handler=lambda u, k: FakeResponse(200, "ok"))
    )
    result = await validator.verify_finding(
        {
            "id": "or2",
            "type": "open_redirect",
            "url": "http://t.local/?next=1",
            "parameter": "next",
            "evidence": {},
        }
    )
    techniques = {t["name"]: t for t in result.techniques}
    assert techniques["redirect_to_external"]["passed"] is False
    assert techniques["protocol_relative_bypass"]["passed"] is False
    assert result.verification_score == 0


async def test_open_redirect_same_domain_not_scored():
    def handler(url, kwargs):
        return FakeResponse(302, "", headers={"location": "http://t.local/home"})

    validator = CrossValidator(client=FakeAsyncClient(handler=handler))
    result = await validator.verify_finding(
        {
            "id": "or3",
            "type": "open_redirect",
            "url": "http://t.local/?next=1",
            "parameter": "next",
            "evidence": {},
        }
    )
    techniques = {t["name"]: t for t in result.techniques}
    assert techniques["redirect_to_external"]["passed"] is False


async def test_open_redirect_missing_params_uses_evidence_only():
    validator = CrossValidator(client=FakeAsyncClient())
    result = await validator.verify_finding(
        {
            "id": "or4",
            "type": "open_redirect",
            "evidence": {"headers": {"location": "https://evil.com"}},
        }
    )
    techniques = {t["name"]: t for t in result.techniques}
    assert techniques["redirect_to_external"]["passed"] is False
    assert techniques["original_evidence"]["passed"] is True
    assert result.verification_score == 25


async def test_open_redirect_evidence_headers_not_dict():
    validator = CrossValidator(client=FakeAsyncClient())
    result = await validator.verify_finding(
        {"id": "or5", "type": "open_redirect", "evidence": {"headers": "not-a-dict"}}
    )
    techniques = {t["name"]: t for t in result.techniques}
    assert techniques["original_evidence"]["passed"] is False


# ===========================================================================
# Strategy: SSRF
# ===========================================================================


async def test_ssrf_internal_resource_and_differential():
    def handler(url, kwargs):
        if "192.0.2.1" in url:
            return None  # external unreachable
        if "127.0.0.1" in url or "localhost" in url or "169.254" in url:
            return FakeResponse(200, "instance-id: i-1234567890\nami-id: ami-abc123")
        return FakeResponse(200, "")

    validator = CrossValidator(client=FakeAsyncClient(handler=handler))
    result = await validator.verify_finding(
        {
            "id": "ss1",
            "type": "ssrf",
            "url": "http://t.local/?url=1",
            "parameter": "url",
            "evidence": {},
        }
    )
    techniques = {t["name"]: t for t in result.techniques}
    assert techniques["internal_resource_access"]["passed"] is True
    assert techniques["response_differential"]["passed"] is True
    assert techniques["dns_rebinding_indicator"]["passed"] is False
    # 45 + 30 = 75
    assert result.verification_score == 75
    assert result.verified is True


async def test_ssrf_no_internal_response():
    def handler(url, kwargs):
        if "192.0.2.1" in url:
            return None
        return FakeResponse(200, "")

    validator = CrossValidator(client=FakeAsyncClient(handler=handler))
    result = await validator.verify_finding(
        {"id": "ss2", "type": "ssrf", "url": "http://t.local/?url=1", "parameter": "url"}
    )
    techniques = {t["name"]: t for t in result.techniques}
    assert techniques["internal_resource_access"]["passed"] is False
    assert techniques["response_differential"]["passed"] is False
    assert result.verification_score == 0


async def test_ssrf_dns_rebinding_indicator_from_evidence():
    validator = CrossValidator(
        client=FakeAsyncClient(handler=lambda u, k: FakeResponse(200, ""))
    )
    result = await validator.verify_finding(
        {
            "id": "ss3",
            "type": "ssrf",
            "url": "http://t.local/?url=1",
            "parameter": "url",
            "evidence": {"response": "x-dns-rebinding detected, low ttl"},
        }
    )
    techniques = {t["name"]: t for t in result.techniques}
    assert techniques["dns_rebinding_indicator"]["passed"] is True
    assert result.verification_score == 25


async def test_ssrf_missing_params():
    validator = CrossValidator(client=FakeAsyncClient())
    result = await validator.verify_finding({"id": "ss4", "type": "ssrf"})
    techniques = {t["name"]: t for t in result.techniques}
    assert "缺少" in techniques["internal_resource_access"]["note"]
    assert "缺少" in techniques["response_differential"]["note"]
    assert result.verification_score == 0


# ===========================================================================
# Strategy: CSRF
# ===========================================================================


async def test_csrf_full_verification():
    # POST form without CSRF token + no protection headers. The token_format
    # technique is marked passed (consistent with absence) but does not add
    # score on its own, so the total is 45 + 30 = 75.
    def handler(url, kwargs):
        return FakeResponse(200, '<form method="post" action="/x"><input name="q"></form>', headers={})

    validator = CrossValidator(client=FakeAsyncClient(handler=handler))
    result = await validator.verify_finding(
        {"id": "cf1", "type": "csrf", "url": "http://t.local/form", "evidence": {}}
    )
    techniques = {t["name"]: t for t in result.techniques}
    assert techniques["token_absence"]["passed"] is True
    assert techniques["protection_headers"]["passed"] is True
    assert techniques["token_format"]["passed"] is True
    assert result.verification_score == 75
    assert result.verified is True


async def test_csrf_low_entropy_token_adds_score():
    def handler(url, kwargs):
        return FakeResponse(200, '<form method="post"><input name="q"></form>', headers={})

    validator = CrossValidator(client=FakeAsyncClient(handler=handler))
    result = await validator.verify_finding(
        {"id": "cf1b", "type": "csrf", "url": "http://t.local/form", "evidence": {"token": "ab"}}
    )
    techniques = {t["name"]: t for t in result.techniques}
    assert techniques["token_format"]["passed"] is True
    # 45 (token_absence) + 30 (protection) + 25 (low-entropy token) = 100
    assert result.verification_score == 100
    assert result.verified is True


async def test_csrf_token_present_and_protection_headers():
    def handler(url, kwargs):
        return FakeResponse(
            200,
            '<form method="post"><input name="csrf_token" value="abc"></form>',
            headers={"set-cookie": "s=1; SameSite=Strict", "x-frame-options": "DENY"},
        )

    validator = CrossValidator(client=FakeAsyncClient(handler=handler))
    result = await validator.verify_finding(
        {"id": "cf2", "type": "csrf", "url": "http://t.local/form", "evidence": {"token": "abcdefgh1234"}}
    )
    techniques = {t["name"]: t for t in result.techniques}
    assert techniques["token_absence"]["passed"] is False
    assert techniques["protection_headers"]["passed"] is False
    assert techniques["token_format"]["passed"] is False
    assert result.verification_score == 0


async def test_csrf_no_url_only_token_format():
    # Without a url the request-based techniques fail, but a low-entropy token
    # in evidence still contributes +25 from the token_format technique.
    validator = CrossValidator(client=FakeAsyncClient())
    result = await validator.verify_finding({"id": "cf4", "type": "csrf", "evidence": {"token": "ab"}})
    techniques = {t["name"]: t for t in result.techniques}
    assert "缺少 url" in techniques["token_absence"]["note"]
    assert techniques["token_format"]["passed"] is True
    assert result.verification_score == 25


# ===========================================================================
# Strategy: Outdated Component
# ===========================================================================


async def test_outdated_component_full_verification():
    def handler(url, kwargs):
        return FakeResponse(
            200,
            '<script src="/js/jquery-1.12.4.min.js"></script>',
            headers={"server": "jQuery/1.12.4", "x-powered-by": "Express"},
        )

    validator = CrossValidator(client=FakeAsyncClient(handler=handler))
    result = await validator.verify_finding(
        {
            "id": "oc1",
            "type": "outdated_component",
            "url": "http://t.local/",
            "component": "jquery",
            "version": "1.12.4",
        }
    )
    techniques = {t["name"]: t for t in result.techniques}
    assert techniques["version_header_refetch"]["passed"] is True
    assert techniques["script_feature_refetch"]["passed"] is True
    assert techniques["version_consistency"]["passed"] is True
    assert result.verification_score == 100
    assert result.verified is True


async def test_outdated_component_no_match():
    def handler(url, kwargs):
        return FakeResponse(200, "no scripts here", headers={"server": "nginx"})

    validator = CrossValidator(client=FakeAsyncClient(handler=handler))
    result = await validator.verify_finding(
        {
            "id": "oc2",
            "type": "outdated_component",
            "url": "http://t.local/",
            "component": "angular",
            "version": "5.0.0",
        }
    )
    techniques = {t["name"]: t for t in result.techniques}
    assert techniques["version_header_refetch"]["passed"] is False
    assert techniques["script_feature_refetch"]["passed"] is False
    assert techniques["version_consistency"]["passed"] is False
    assert result.verification_score == 0


async def test_outdated_component_no_url():
    validator = CrossValidator(client=FakeAsyncClient())
    result = await validator.verify_finding(
        {"id": "oc3", "type": "outdated_component", "component": "jquery", "version": "1.12.4"}
    )
    techniques = {t["name"]: t for t in result.techniques}
    assert "缺少 url" in techniques["version_header_refetch"]["note"]
    assert "缺少 url" in techniques["script_feature_refetch"]["note"]
    assert "缺少 url" in techniques["version_consistency"]["note"]
    assert result.verification_score == 0


async def test_outdated_component_no_version_skips_consistency():
    def handler(url, kwargs):
        return FakeResponse(200, '<script src="jquery-1.12.4.min.js"></script>', headers={"server": "jquery"})

    validator = CrossValidator(client=FakeAsyncClient(handler=handler))
    result = await validator.verify_finding(
        {"id": "oc4", "type": "outdated_component", "url": "http://t.local/", "component": "jquery"}
    )
    techniques = {t["name"]: t for t in result.techniques}
    assert techniques["version_consistency"]["passed"] is False
    assert "未提供版本号" in techniques["version_consistency"]["note"]


# ===========================================================================
# Strategy: Info Leak
# ===========================================================================


async def test_info_leak_full_verification():
    body = "admin@example.com AKIAIOSFODNN7EXAMPLE password=\"s3cr3t\""

    validator = CrossValidator(client=FakeAsyncClient(handler=lambda u, k: FakeResponse(200, body)))
    result = await validator.verify_finding(
        {
            "id": "il1",
            "type": "info_leak",
            "url": "http://t.local/",
            "evidence": {"response": body},
        }
    )
    techniques = {t["name"]: t for t in result.techniques}
    assert techniques["rescan_sensitive_patterns"]["passed"] is True
    assert techniques["original_evidence"]["passed"] is True
    assert techniques["response_consistency"]["passed"] is True
    assert result.verification_score == 100
    assert result.verified is True


async def test_info_leak_no_sensitive_content():
    validator = CrossValidator(
        client=FakeAsyncClient(handler=lambda u, k: FakeResponse(200, "nothing sensitive here"))
    )
    result = await validator.verify_finding(
        {"id": "il2", "type": "info_leak", "url": "http://t.local/", "evidence": {}}
    )
    techniques = {t["name"]: t for t in result.techniques}
    assert techniques["rescan_sensitive_patterns"]["passed"] is False
    assert techniques["original_evidence"]["passed"] is False
    # consistency passes (identical bodies) -> +20
    assert techniques["response_consistency"]["passed"] is True
    assert result.verification_score == 20


async def test_info_leak_inconsistent_responses():
    state = {"calls": 0}

    def handler(url, kwargs):
        state["calls"] += 1
        return FakeResponse(200, f"body-{state['calls']}")

    validator = CrossValidator(client=FakeAsyncClient(handler=handler))
    result = await validator.verify_finding(
        {"id": "il3", "type": "info_leak", "url": "http://t.local/", "evidence": {}}
    )
    techniques = {t["name"]: t for t in result.techniques}
    assert techniques["response_consistency"]["passed"] is False
    assert result.verification_score == 0


async def test_info_leak_no_url_uses_evidence():
    validator = CrossValidator(client=FakeAsyncClient())
    result = await validator.verify_finding(
        {
            "id": "il4",
            "type": "info_leak",
            "evidence": {"response": "leaked admin@example.com"},
        }
    )
    techniques = {t["name"]: t for t in result.techniques}
    assert "缺少 url" in techniques["rescan_sensitive_patterns"]["note"]
    assert "缺少 url" in techniques["response_consistency"]["note"]
    assert techniques["original_evidence"]["passed"] is True
    assert result.verification_score == 30


# ===========================================================================
# Strategy: SSL/TLS
# ===========================================================================


async def test_ssl_non_https_returns_existing_evidence():
    validator = CrossValidator(client=FakeAsyncClient())
    result = await validator.verify_finding({"id": "ssl1", "type": "ssl", "url": "http://example.com"})
    assert result.verification_score == 70
    assert result.verified is True
    assert result.techniques[0]["name"] == "existing_evidence"


async def test_ssl_no_hostname_returns_existing_evidence():
    validator = CrossValidator(client=FakeAsyncClient())
    result = await validator.verify_finding({"id": "ssl2", "type": "ssl", "url": ""})
    assert result.verification_score == 70
    assert result.techniques[0]["name"] == "existing_evidence"


async def test_ssl_valid_cert_future_strong(monkeypatch):
    cert = {"notAfter": "Jan 01 00:00:00 2030 GMT"}
    _patch_ssl(monkeypatch, cert, ("ECDHE-RSA-AES256-GCM-SHA384", "TLSv1.2", 256), "TLSv1.2")
    validator = CrossValidator(client=FakeAsyncClient())
    result = await validator.verify_finding({"id": "ssl3", "type": "ssl", "url": "https://example.com"})
    techniques = {t["name"]: t for t in result.techniques}
    assert techniques["certificate_validity"]["passed"] is True
    assert techniques["certificate_expiry"]["passed"] is False
    assert techniques["weak_cipher_suite"]["passed"] is False
    # only cert validity 35
    assert result.verification_score == 35
    assert result.verified is False


async def test_ssl_expired_cert(monkeypatch):
    cert = {"notAfter": "Jan 01 00:00:00 2020 GMT"}
    _patch_ssl(monkeypatch, cert, ("ECDHE-RSA-AES256-GCM-SHA384", "TLSv1.2", 256), "TLSv1.2")
    validator = CrossValidator(client=FakeAsyncClient())
    result = await validator.verify_finding({"id": "ssl4", "type": "ssl", "url": "https://example.com"})
    techniques = {t["name"]: t for t in result.techniques}
    assert techniques["certificate_validity"]["passed"] is True
    assert techniques["certificate_expiry"]["passed"] is True
    assert techniques["weak_cipher_suite"]["passed"] is False
    # 35 + 40 = 75
    assert result.verification_score == 75
    assert result.verified is True


async def test_ssl_near_expiry(monkeypatch):
    near = (datetime.datetime.utcnow() + datetime.timedelta(days=10)).strftime("%b %d %H:%M:%S %Y GMT")
    cert = {"notAfter": near}
    _patch_ssl(monkeypatch, cert, ("ECDHE-RSA-AES256-GCM-SHA384", "TLSv1.2", 256), "TLSv1.2")
    validator = CrossValidator(client=FakeAsyncClient())
    result = await validator.verify_finding({"id": "ssl5", "type": "ssl", "url": "https://example.com"})
    techniques = {t["name"]: t for t in result.techniques}
    assert techniques["certificate_expiry"]["passed"] is True
    # 35 (validity) + 25 (near expiry) = 60 -> verified
    assert result.verification_score == 60
    assert result.verified is True


async def test_ssl_weak_cipher_suite(monkeypatch):
    cert = {"notAfter": "Jan 01 00:00:00 2030 GMT"}
    _patch_ssl(monkeypatch, cert, ("RC4-MD5", "SSLv3", 128), "SSLv3")
    validator = CrossValidator(client=FakeAsyncClient())
    result = await validator.verify_finding({"id": "ssl6", "type": "ssl", "url": "https://example.com"})
    techniques = {t["name"]: t for t in result.techniques}
    assert techniques["weak_cipher_suite"]["passed"] is True
    # 35 (validity) + 35 (weak) = 70
    assert result.verification_score == 70
    assert result.verified is True


async def test_ssl_handshake_error_scores(monkeypatch):
    cert = {"notAfter": "Jan 01 00:00:00 2030 GMT"}
    _patch_ssl(
        monkeypatch,
        cert,
        ("ECDHE-RSA-AES256-GCM-SHA384", "TLSv1.2", 256),
        "TLSv1.2",
        raise_on_wrap=True,
        raise_cls=cv.ssl.SSLError,
    )
    validator = CrossValidator(client=FakeAsyncClient())
    result = await validator.verify_finding({"id": "ssl7", "type": "ssl", "url": "https://example.com"})
    techniques = {t["name"]: t for t in result.techniques}
    assert techniques["certificate_validity"]["passed"] is True
    assert "SSL 握手失败" in techniques["certificate_validity"]["note"]
    assert techniques["certificate_expiry"]["passed"] is False
    assert techniques["weak_cipher_suite"]["passed"] is False
    # only 45 from the ssl error
    assert result.verification_score == 45
    assert result.verified is False


# ===========================================================================
# Strategy: Header Missing
# ===========================================================================


async def test_header_missing_confirmed_absent():
    validator = CrossValidator(
        client=FakeAsyncClient(handler=lambda u, k: FakeResponse(200, "ok", headers={"content-type": "text/html"}))
    )
    result = await validator.verify_finding(
        {"id": "hm1", "type": "header_missing", "url": "http://t.local/", "title": "Missing X-Frame-Options"}
    )
    assert result.verification_score == 100
    assert result.verified is True
    assert result.techniques[0]["name"] == "header_absence"
    assert result.techniques[0]["passed"] is True


async def test_header_missing_present_is_false_positive():
    def handler(url, kwargs):
        return FakeResponse(200, "ok", headers={"content-security-policy": "default-src 'self'"})

    validator = CrossValidator(client=FakeAsyncClient(handler=handler))
    result = await validator.verify_finding(
        {"id": "hm2", "type": "header_missing", "url": "http://t.local/", "title": "Missing Content-Security-Policy"}
    )
    assert result.verification_score == 0
    assert result.verified is False
    assert result.techniques[0]["passed"] is False


async def test_header_missing_request_failure_keeps_original():
    validator = CrossValidator(client=FakeAsyncClient(handler=lambda u, k: None))
    result = await validator.verify_finding(
        {"id": "hm3", "type": "header_missing", "url": "http://t.local/", "title": "Missing X-Frame-Options"}
    )
    assert result.verification_score == 50
    assert result.verified is False


async def test_header_missing_no_recognized_header_uses_evidence():
    validator = CrossValidator(client=FakeAsyncClient())
    result = await validator.verify_finding(
        {"id": "hm4", "type": "header_missing", "url": "http://t.local/", "title": "Something else"}
    )
    assert result.verification_score == 70
    assert result.techniques[0]["name"] == "existing_evidence"


async def test_header_missing_no_url_uses_evidence():
    validator = CrossValidator(client=FakeAsyncClient())
    result = await validator.verify_finding(
        {"id": "hm5", "type": "header_missing", "title": "Missing Referrer-Policy"}
    )
    assert result.verification_score == 70
    assert result.techniques[0]["name"] == "existing_evidence"


# ===========================================================================
# diff_engine: FindingSignature & _location_key
# ===========================================================================


def test_location_key_url_param_location():
    data = {"url": "http://x/a", "parameter": "q", "location": "body"}
    assert _location_key(data) == "http://x/a|q|body"


def test_location_key_only_url():
    assert _location_key({"url": "http://x/a"}) == "http://x/a"


def test_location_key_empty_returns_unknown():
    assert _location_key({}) == "unknown"


def test_location_key_location_detail_overrides():
    data = {
        "url": "http://x/old",
        "parameter": "old",
        "location_detail": {"url": "http://x/new", "parameter": "new"},
    }
    assert _location_key(data) == "http://x/new|new"


def test_location_key_location_detail_not_dict_ignored():
    data = {"url": "http://x/a", "location_detail": "not-a-dict"}
    assert _location_key(data) == "http://x/a"


def test_finding_signature_from_dict_type_key():
    sig = FindingSignature.from_dict(
        {"type": "SQLI", "url": "http://x/a", "parameter": "q", "severity": "HIGH"}
    )
    assert sig.vuln_type == "sqli"
    assert sig.severity == "high"
    assert sig.location_key == "http://x/a|q"


def test_finding_signature_from_dict_vuln_type_key():
    sig = FindingSignature.from_dict({"vuln_type": "XSS", "severity": "Medium"})
    assert sig.vuln_type == "xss"
    assert sig.severity == "medium"


def test_finding_signature_defaults():
    sig = FindingSignature.from_dict({})
    assert sig.vuln_type == "unknown"
    assert sig.severity == "low"
    assert sig.location_key == "unknown"


def test_finding_signature_hash_and_equality():
    a = FindingSignature("sqli", "loc|q", "high")
    b = FindingSignature("sqli", "loc|q", "high")
    c = FindingSignature("sqli", "loc|q", "medium")
    assert a == b
    assert hash(a) == hash(b)
    assert a != c
    assert hash(a) != hash(c)
    # usable as dict key
    d = {a: 1}
    assert d[b] == 1


# ===========================================================================
# diff_engine: DiffResult
# ===========================================================================


def test_diff_result_defaults():
    r = DiffResult()
    assert r.eliminated == []
    assert r.new_findings == []
    assert r.retained == []
    assert r.severity_changed == []
    assert r.summary == {}
    assert r.score_delta == 0


def test_is_verified_fixed_default_requires_score_and_eliminated():
    r = DiffResult(score_delta=25)
    r.eliminated.append(FindingChange(change_type="eliminated", before={"name": "v1"}))
    assert r.is_verified_fixed() is True


def test_is_verified_fixed_default_no_eliminated():
    r = DiffResult(score_delta=25)
    assert r.is_verified_fixed() is False


def test_is_verified_fixed_default_low_delta():
    r = DiffResult(score_delta=10)
    r.eliminated.append(FindingChange(change_type="eliminated", before={"name": "v1"}))
    assert r.is_verified_fixed() is False


def test_is_verified_fixed_with_target_names_all_eliminated():
    r = DiffResult()
    r.eliminated.append(FindingChange(change_type="eliminated", before={"name": "SQLi-1"}))
    r.eliminated.append(FindingChange(change_type="eliminated", before={"title": "XSS-1"}))
    assert r.is_verified_fixed(target_finding_names=["SQLi-1", "XSS-1"]) is True


def test_is_verified_fixed_with_target_names_not_all_eliminated():
    r = DiffResult()
    r.eliminated.append(FindingChange(change_type="eliminated", before={"name": "SQLi-1"}))
    assert r.is_verified_fixed(target_finding_names=["SQLi-1", "XSS-1"]) is False


def test_diff_result_to_dict_structure():
    # score_delta is a plain field (not derived from before/after scores).
    r = DiffResult(
        before_scan_id=1,
        after_scan_id=2,
        before_score=40,
        after_score=70,
        score_delta=30,
    )
    r.eliminated.append(FindingChange(change_type="eliminated", before={"id": "a"}, notes="gone"))
    r.new_findings.append(FindingChange(change_type="new", after={"id": "b"}, notes="new"))
    r.retained.append(FindingChange(change_type="retained", before={"id": "c"}, after={"id": "c"}))
    r.severity_changed.append(
        FindingChange(change_type="severity_changed", before={"id": "d"}, after={"id": "d"}, severity_delta="high -> medium")
    )
    d = r.to_dict()
    assert d["before_scan_id"] == 1
    assert d["after_scan_id"] == 2
    assert d["score_delta"] == 30
    assert d["eliminated"][0]["finding"] == {"id": "a"}
    assert d["new_findings"][0]["finding"] == {"id": "b"}
    assert d["retained"][0]["finding"] == {"id": "c"}
    assert d["severity_changed"][0]["severity_delta"] == "high -> medium"
    # score_delta 30 with at least one eliminated finding -> verified fixed
    assert d["verified_fixed"] is True


# ===========================================================================
# diff_engine: ScanDiffEngine.compare
# ===========================================================================


def test_compare_empty_inputs():
    result = ScanDiffEngine.compare([], [])
    assert result.eliminated == []
    assert result.new_findings == []
    assert result.retained == []
    assert result.severity_changed == []
    assert result.summary["total_before"] == 0
    assert result.summary["total_after"] == 0


def test_compare_all_eliminated():
    before = [
        {"id": "1", "type": "sqli", "url": "http://x/a", "parameter": "q", "severity": "high"},
    ]
    result = ScanDiffEngine.compare(before, [], before_score=30, after_score=90)
    assert len(result.eliminated) == 1
    assert result.eliminated[0].before["id"] == "1"
    assert result.new_findings == []
    assert result.retained == []
    assert result.score_delta == 60
    assert result.summary["eliminated_count"] == 1
    assert result.summary["high_critical_before"] == 1
    assert result.summary["high_critical_after"] == 0
    assert result.summary["high_critical_delta"] == -1
    assert result.summary["score_improved"] is True


def test_compare_new_findings():
    after = [
        {"id": "2", "type": "xss", "url": "http://x/b", "parameter": "q", "severity": "medium"},
    ]
    result = ScanDiffEngine.compare([], after, before_score=80, after_score=50)
    assert len(result.new_findings) == 1
    assert result.new_findings[0].after["id"] == "2"
    assert result.eliminated == []
    assert result.score_delta == -30
    assert result.summary["score_improved"] is False


def test_compare_retained_unchanged():
    finding = {"id": "1", "type": "sqli", "url": "http://x/a", "parameter": "q", "severity": "high"}
    result = ScanDiffEngine.compare([finding], [finding])
    assert len(result.retained) == 1
    assert result.eliminated == []
    assert result.new_findings == []
    assert result.severity_changed == []


def test_compare_severity_difference_treated_as_eliminated_and_new():
    # ``severity`` is part of FindingSignature, so a severity change makes the
    # before/after signatures differ: the old severity is "eliminated" and the
    # new severity is reported as a "new" finding.
    before = [{"id": "1", "type": "sqli", "url": "http://x/a", "parameter": "q", "severity": "high"}]
    after = [{"id": "1", "type": "sqli", "url": "http://x/a", "parameter": "q", "severity": "medium"}]
    result = ScanDiffEngine.compare(before, after)
    assert len(result.eliminated) == 1
    assert result.eliminated[0].before["severity"] == "high"
    assert len(result.new_findings) == 1
    assert result.new_findings[0].after["severity"] == "medium"
    assert result.severity_changed == []
    assert result.retained == []


def test_compare_severity_change_worsening_is_eliminated_and_new():
    before = [{"id": "1", "type": "sqli", "url": "http://x/a", "parameter": "q", "severity": "low"}]
    after = [{"id": "1", "type": "sqli", "url": "http://x/a", "parameter": "q", "severity": "high"}]
    result = ScanDiffEngine.compare(before, after)
    assert len(result.eliminated) == 1
    assert result.eliminated[0].before["severity"] == "low"
    assert len(result.new_findings) == 1
    assert result.new_findings[0].after["severity"] == "high"
    assert result.severity_changed == []
    # high/critical count goes from 0 to 1
    assert result.summary["high_critical_delta"] == 1


def test_diff_result_severity_changed_serialization():
    # The severity_changed bucket (populated by external callers / future logic)
    # is serialized faithfully by to_dict.
    r = DiffResult(score_delta=10)
    r.severity_changed.append(
        FindingChange(
            change_type="severity_changed",
            before={"id": "d", "severity": "high"},
            after={"id": "d", "severity": "medium"},
            severity_delta="high -> medium",
            notes="改善",
        )
    )
    d = r.to_dict()
    entry = d["severity_changed"][0]
    assert entry["change_type"] == "severity_changed"
    assert entry["before"]["severity"] == "high"
    assert entry["after"]["severity"] == "medium"
    assert entry["severity_delta"] == "high -> medium"


def test_compare_dedup_identical_signatures():
    """Findings with identical signatures collapse into a single map entry."""
    dup = {"id": "1", "type": "sqli", "url": "http://x/a", "parameter": "q", "severity": "high"}
    before = [dup, dict(dup)]
    result = ScanDiffEngine.compare(before, [])
    # dedup: only one eliminated signature
    assert len(result.eliminated) == 1
    # but raw counts reflect input length
    assert result.summary["total_before"] == 2


def test_compare_mixed_scenario():
    before = [
        {"id": "1", "type": "sqli", "url": "http://x/a", "parameter": "q", "severity": "high"},
        {"id": "2", "type": "xss", "url": "http://x/b", "parameter": "q", "severity": "medium"},
        {"id": "3", "type": "csrf", "url": "http://x/c", "severity": "low"},
    ]
    after = [
        # 1 retained unchanged
        {"id": "1", "type": "sqli", "url": "http://x/a", "parameter": "q", "severity": "high"},
        # 2 severity changed medium -> high: because severity is part of the
        # signature this surfaces as eliminated(medium) + new(high)
        {"id": "2", "type": "xss", "url": "http://x/b", "parameter": "q", "severity": "high"},
        # 4 is new
        {"id": "4", "type": "ssrf", "url": "http://x/d", "parameter": "url", "severity": "critical"},
    ]
    result = ScanDiffEngine.compare(
        before, after, before_scan_id=10, after_scan_id=11, before_score=45, after_score=55
    )
    assert result.before_scan_id == 10
    assert result.after_scan_id == 11
    assert len(result.eliminated) == 2  # xss(medium) + csrf(low)
    assert len(result.new_findings) == 2  # ssrf(critical) + xss(high)
    assert len(result.retained) == 1  # sqli unchanged
    assert result.severity_changed == []
    assert result.summary["eliminated_count"] == 2
    assert result.summary["new_count"] == 2
    assert result.summary["retained_count"] == 1
    assert result.summary["severity_changed_count"] == 0
    assert result.summary["high_critical_before"] == 1  # only sqli high
    assert result.summary["high_critical_after"] == 3  # sqli + xss + ssrf
    assert result.summary["high_critical_delta"] == 2


def test_compare_risk_level_changed():
    before = [{"id": "1", "type": "sqli", "url": "http://x/a", "parameter": "q", "severity": "high"}]
    after = []  # all fixed
    result = ScanDiffEngine.compare(before, after, before_score=30, after_score=85)
    # before 30 -> critical, after 85 -> low -> changed
    assert result.summary["risk_level_changed"] is True


def test_compare_risk_level_unchanged():
    before = [{"id": "1", "type": "sqli", "url": "http://x/a", "parameter": "q", "severity": "high"}]
    after = [{"id": "1", "type": "sqli", "url": "http://x/a", "parameter": "q", "severity": "high"}]
    result = ScanDiffEngine.compare(before, after, before_score=50, after_score=55)
    # both high -> unchanged
    assert result.summary["risk_level_changed"] is False


def test_risk_level_boundaries():
    rl = ScanDiffEngine._risk_level
    assert rl(0) == "critical"
    assert rl(39) == "critical"
    assert rl(40) == "high"
    assert rl(59) == "high"
    assert rl(60) == "medium"
    assert rl(79) == "medium"
    assert rl(80) == "low"
    assert rl(100) == "low"


# ===========================================================================
# diff_engine: ScanDiffEngine.compare_scans
# ===========================================================================


def test_compare_scans_with_full_scan_dicts():
    before_scan = {
        "scan_id": 7,
        "score": 40,
        "findings": [
            {"id": "1", "type": "sqli", "url": "http://x/a", "parameter": "q", "severity": "high"},
            {"id": "2", "type": "xss", "url": "http://x/b", "parameter": "q", "severity": "medium"},
        ],
    }
    after_scan = {
        "scan_id": 8,
        "score": 80,
        "findings": [
            {"id": "2", "type": "xss", "url": "http://x/b", "parameter": "q", "severity": "medium"},
        ],
    }
    result = ScanDiffEngine.compare_scans(before_scan, after_scan)
    assert result.before_scan_id == 7
    assert result.after_scan_id == 8
    assert result.before_score == 40
    assert result.after_score == 80
    assert result.score_delta == 40
    assert len(result.eliminated) == 1  # sqli gone
    assert len(result.retained) == 1  # xss retained


def test_compare_scans_missing_fields_defaults():
    result = ScanDiffEngine.compare_scans({}, {})
    assert result.before_scan_id is None
    assert result.after_scan_id is None
    assert result.before_score == 0
    assert result.after_score == 0
    assert result.eliminated == []
    assert result.new_findings == []


def test_compare_scans_score_none_treated_as_zero():
    before = {"scan_id": 1, "score": None, "findings": []}
    after = {"scan_id": 2, "score": None, "findings": []}
    result = ScanDiffEngine.compare_scans(before, after)
    assert result.before_score == 0
    assert result.after_score == 0
    assert result.score_delta == 0
