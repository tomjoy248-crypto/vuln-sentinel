"""Comprehensive tests for utility modules and core components.

Covers:
- utils.py: SSRF protection (sanitize_url, resolve_and_validate_ip, DNS pinning),
  input sanitizers, CORS parsing, HTML escaping.
- app/sarif.py: SARIF 2.1.0 export/import.
- app/core/response.py: success_response / error_response.
- app/core/exceptions.py: BusinessException hierarchy + global handlers.
- app/core/input_validation.py: validate_url, sanitize_input, SQLi/XSS detection.
- app/core/security_headers.py: security header middleware.
- app/db/session.py: _convert_qmark, _RowProxy, _bind_params, _mask_url, get_db.
"""

import json
import os
import socket
import sqlite3
import sys

# Ensure the project root is importable and the test DB env is configured
# BEFORE importing any project modules (matches conftest conventions).
os.environ.setdefault("DB_DIR", "/tmp/v11-test")
os.environ.setdefault("DB_NAME", "test.db")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest  # noqa: E402
from fastapi import FastAPI, HTTPException  # noqa: E402
from fastapi.responses import JSONResponse, Response  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from starlette.requests import Request  # noqa: E402

import utils  # noqa: E402
from app import sarif  # noqa: E402
from app.core import exceptions, input_validation, security_headers  # noqa: E402
from app.core.response import CODE_MAP, error_response, success_response  # noqa: E402
from app.db import session  # noqa: E402

# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------


def _fake_getaddrinfo(ips):
    """Build a fake socket.getaddrinfo resolving any host to the given IP(s)."""
    if isinstance(ips, str):
        ips = [ips]

    def _fake(host, port, *args, **kwargs):
        return [
            (socket.AF_INET, socket.SOCK_STREAM, 0, "", (ip, port or 0))
            for ip in ips
        ]

    return _fake


def _gaierror_getaddrinfo(host, port, *args, **kwargs):
    raise socket.gaierror(8, "nodename nor servname provided, or not known")


def _make_request_scope(scheme="http", headers=None):
    """Build a minimal ASGI scope for a Starlette Request."""
    raw_headers = []
    for name, value in (headers or []):
        raw_headers.append((name.encode("latin-1"), value.encode("latin-1")))
    return {
        "type": "http",
        "http_version": "1.1",
        "scheme": scheme,
        "method": "GET",
        "path": "/",
        "raw_path": b"/",
        "query_string": b"",
        "headers": raw_headers,
        "server": ("testserver", 443 if scheme == "https" else 80),
        "client": ("127.0.0.1", 50000),
    }


@pytest.fixture
def sqlite_db(tmp_path):
    """Point app.db.session at a fresh SQLite file and restore afterwards."""
    db_file = str(tmp_path / "test_utils_core.db")
    old_path = session._db_path
    old_url = session._database_url
    session.init_db_path(db_file, "")
    try:
        yield db_file
    finally:
        session.init_db_path(old_path, old_url)


# ===========================================================================
# utils.py - input sanitizers
# ===========================================================================


def test_sanitize_username_valid_ascii():
    assert utils.sanitize_username("alice_123") == "alice_123"


def test_sanitize_username_valid_chinese():
    assert utils.sanitize_username("用户1") == "用户1"


def test_sanitize_username_valid_with_dash_and_underscore():
    assert utils.sanitize_username("a-b_c") == "a-b_c"


def test_sanitize_username_strips_whitespace():
    assert utils.sanitize_username("  alice  ") == "alice"


def test_sanitize_username_min_length_boundary():
    assert utils.sanitize_username("abc") == "abc"


def test_sanitize_username_max_length_boundary():
    assert utils.sanitize_username("a" * 32) == "a" * 32


def test_sanitize_username_too_short():
    with pytest.raises(ValueError, match="用户名长度"):
        utils.sanitize_username("ab")


def test_sanitize_username_too_long():
    with pytest.raises(ValueError, match="用户名长度"):
        utils.sanitize_username("a" * 33)


def test_sanitize_username_illegal_chars():
    with pytest.raises(ValueError, match="非法字符"):
        utils.sanitize_username("alice!")


def test_sanitize_username_rejects_internal_space():
    with pytest.raises(ValueError, match="非法字符"):
        utils.sanitize_username("al ice")


def test_sanitize_email_valid():
    assert utils.sanitize_email("User.Name+tag@example.co.uk") == "User.Name+tag@example.co.uk"


def test_sanitize_email_empty_returns_empty_string():
    assert utils.sanitize_email("   ") == ""


def test_sanitize_email_too_long():
    long_local = "a" * 200
    with pytest.raises(ValueError, match="邮箱长度"):
        utils.sanitize_email(f"{long_local}@example.com")


@pytest.mark.parametrize(
    "bad",
    ["notanemail", "user@", "@example.com", "user@example", "user@.com", "user example.com"],
)
def test_sanitize_email_invalid_formats(bad):
    with pytest.raises(ValueError, match="邮箱格式无效"):
        utils.sanitize_email(bad)


def test_sanitize_password_valid_min_length():
    assert utils.sanitize_password("123456") == "123456"


def test_sanitize_password_valid_max_length():
    pw = "x" * 128
    assert utils.sanitize_password(pw) == pw


def test_sanitize_password_too_short():
    with pytest.raises(ValueError, match="密码长度"):
        utils.sanitize_password("12345")


def test_sanitize_password_too_long():
    with pytest.raises(ValueError, match="密码长度"):
        utils.sanitize_password("x" * 129)


def test_parse_cors_origins_empty_string():
    assert utils.parse_cors_origins("") == []


def test_parse_cors_origins_none():
    assert utils.parse_cors_origins(None) == []


def test_parse_cors_origins_single():
    assert utils.parse_cors_origins("https://a.com") == ["https://a.com"]


def test_parse_cors_origins_multiple_with_spaces():
    result = utils.parse_cors_origins("https://a.com , https://b.com ,, https://c.com")
    assert result == ["https://a.com", "https://b.com", "https://c.com"]


def test_parse_cors_origins_only_commas():
    assert utils.parse_cors_origins(" , , , ") == []


def test_html_escape_replaces_all_special_chars():
    assert utils._html_escape('<>"\'&') == "&lt;&gt;&quot;&#x27;&amp;"


def test_html_escape_plain_text_unchanged():
    assert utils._html_escape("hello world") == "hello world"


# ===========================================================================
# utils.py - SSRF protection
# ===========================================================================


def test_sanitize_url_prepends_https_when_missing_scheme():
    # Public IP literal so no DNS is required and result is deterministic.
    url = utils.sanitize_url("93.184.216.34")
    assert url == "https://93.184.216.34"


def test_sanitize_url_accepts_public_ip_literal_http():
    assert utils.sanitize_url("http://93.184.216.34/path") == "http://93.184.216.34/path"


def test_sanitize_url_accepts_public_domain(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", _fake_getaddrinfo("93.184.216.34"))
    assert utils.sanitize_url("https://example.com") == "https://example.com"


def test_sanitize_url_rejects_empty():
    with pytest.raises(ValueError, match="不能为空"):
        utils.sanitize_url("")


def test_sanitize_url_rejects_too_long():
    long_url = "http://example.com/" + "a" * 2100
    with pytest.raises(ValueError, match="URL 长度"):
        utils.sanitize_url(long_url)


def test_sanitize_url_rejects_missing_hostname():
    with pytest.raises(ValueError, match="URL 格式无效"):
        utils.sanitize_url("https://")


def test_sanitize_url_rejects_localhost_by_default():
    with pytest.raises(ValueError):
        utils.sanitize_url("http://localhost")


def test_sanitize_url_allows_localhost_when_in_allowed_hosts(monkeypatch):
    monkeypatch.setattr(utils, "ALLOWED_INTERNAL_HOSTS", {"localhost"})
    assert utils.sanitize_url("http://localhost") == "http://localhost"


@pytest.mark.parametrize(
    "ip",
    ["10.0.0.1", "192.168.1.1", "172.16.0.1", "172.31.0.1", "169.254.169.254", "127.0.0.1"],
)
def test_sanitize_url_rejects_private_ip_literal(ip):
    with pytest.raises(ValueError, match="内网或本地地址"):
        utils.sanitize_url(f"http://{ip}")


def test_sanitize_url_rejects_domain_resolving_to_private_ip(monkeypatch):
    # DNS rebinding scenario: public-looking domain resolves to an internal IP.
    monkeypatch.setattr(socket, "getaddrinfo", _fake_getaddrinfo("10.0.0.5"))
    with pytest.raises(ValueError, match="内网或本地地址"):
        utils.sanitize_url("https://evil.example.com")


def test_sanitize_url_rejects_short_tld():
    with pytest.raises(ValueError, match="域名后缀太短"):
        utils.sanitize_url("https://example.x")


def test_is_private_ip_blocked_hosts():
    for host in ["localhost", "127.0.0.1", "0.0.0.0", "::1", "169.254.169.254"]:
        assert utils._is_private_ip(host) is True


@pytest.mark.parametrize("ip", ["10.1.2.3", "172.16.5.5", "192.168.0.1", "169.254.1.1"])
def test_is_private_ip_private_network_literals(ip):
    assert utils._is_private_ip(ip) is True


def test_is_private_ip_public_ip_is_false():
    assert utils._is_private_ip("8.8.8.8") is False


def test_is_private_ip_unknown_host_is_false(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", _gaierror_getaddrinfo)
    assert utils._is_private_ip("nonexistent.invalid") is False


def test_resolve_and_validate_ip_returns_safe_ip(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", _fake_getaddrinfo("93.184.216.34"))
    assert utils.resolve_and_validate_ip("example.com") == "93.184.216.34"


def test_resolve_and_validate_ip_blocks_private_ip(monkeypatch):
    # 非白名单主机解析到纯内网 IP 时，所有 IP 被跳过后抛出"均被封锁"错误
    monkeypatch.setattr(socket, "getaddrinfo", _fake_getaddrinfo("10.0.0.5"))
    with pytest.raises(ValueError, match="所有解析 IP 均被封锁"):
        utils.resolve_and_validate_ip("evil.example.com")


def test_resolve_and_validate_ip_dns_failure(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", _gaierror_getaddrinfo)
    with pytest.raises(ValueError, match="DNS 解析失败"):
        utils.resolve_and_validate_ip("nonexistent.invalid")


def test_resolve_and_validate_ip_blocked_hostname():
    with pytest.raises(ValueError, match="被封锁的主机名"):
        utils.resolve_and_validate_ip("localhost")


def test_resolve_and_validate_ip_allows_internal_when_allowed(monkeypatch):
    # Allowed internal host: a private address no longer raises the
    # "internal IP" error; the first non-blocked IP is returned instead.
    monkeypatch.setattr(
        utils, "ALLOWED_INTERNAL_HOSTS", {"internal.test"}
    )
    monkeypatch.setattr(
        socket, "getaddrinfo", _fake_getaddrinfo(["10.0.0.5", "93.184.216.34"])
    )
    assert utils.resolve_and_validate_ip("internal.test") == "93.184.216.34"


def test_resolve_and_validate_ip_all_blocked_raises(monkeypatch):
    # When the host is allow-listed, the per-IP "internal IP" error is
    # bypassed; if every resolved IP is still private, the function falls
    # through to the "all blocked" error.
    monkeypatch.setattr(utils, "ALLOWED_INTERNAL_HOSTS", {"internal.test"})
    monkeypatch.setattr(socket, "getaddrinfo", _fake_getaddrinfo("10.0.0.5"))
    with pytest.raises(ValueError, match="所有解析 IP 均被封锁"):
        utils.resolve_and_validate_ip("internal.test")


def test_build_pinned_url_https_adds_default_port():
    pinned, host = utils.build_pinned_url("https://example.com/path", "93.184.216.34")
    assert pinned == "https://93.184.216.34:443/path"
    assert host == "example.com"


def test_build_pinned_url_http_adds_default_port():
    pinned, host = utils.build_pinned_url("http://example.com/", "93.184.216.34")
    assert pinned == "http://93.184.216.34:80/"
    assert host == "example.com"


def test_build_pinned_url_preserves_explicit_port():
    pinned, host = utils.build_pinned_url("https://example.com:8443/x", "10.0.0.1")
    assert pinned == "https://10.0.0.1:8443/x"
    assert host == "example.com"


def test_build_pinned_url_preserves_path_and_query():
    pinned, host = utils.build_pinned_url(
        "https://example.com/search?q=1&sort=asc", "1.2.3.4"
    )
    assert pinned == "https://1.2.3.4:443/search?q=1&sort=asc"
    assert host == "example.com"


def test_build_pinned_url_returns_original_hostname_for_sni():
    _, host = utils.build_pinned_url("https://sub.example.com/a", "1.2.3.4")
    assert host == "sub.example.com"


# ===========================================================================
# app/sarif.py
# ===========================================================================


def _sample_finding(**overrides):
    base = {
        "type": "sql_injection",
        "cwe_id": "CWE-89",
        "owasp": "A03",
        "severity": "high",
        "confidence_level": "高",
        "name": "SQL 注入",
        "summary": "存在 SQL 注入漏洞",
        "url": "https://target.example.com/search",
        "parameter": "q",
        "fix": "使用参数化查询",
        "evidence": {"payload": "' OR 1=1--", "matched": True},
    }
    base.update(overrides)
    return base


def test_make_rule_id_with_cwe():
    assert sarif._make_rule_id({"type": "xss", "cwe_id": "CWE-79"}) == "VS-79"


def test_make_rule_id_without_cwe():
    assert sarif._make_rule_id({"type": "sql_injection"}) == "VS-SQL_INJECTION"


def test_make_rule_id_uses_vuln_type_fallback():
    assert sarif._make_rule_id({"vuln_type": "csrf"}) == "VS-CSRF"


def test_make_rule_id_missing_type_defaults_unknown():
    assert sarif._make_rule_id({}) == "VS-UNKNOWN"


def test_severity_to_score_mapping():
    assert sarif._severity_to_score("critical") == "9.5"
    assert sarif._severity_to_score("high") == "8.0"
    assert sarif._severity_to_score("medium") == "5.0"
    assert sarif._severity_to_score("low") == "2.5"
    assert sarif._severity_to_score("info") == "0.0"


def test_severity_to_score_unknown_defaults_medium():
    assert sarif._severity_to_score("bogus") == "5.0"


def test_sarif_level_to_severity_mapping():
    assert sarif._sarif_level_to_severity("error") == "high"
    assert sarif._sarif_level_to_severity("warning") == "medium"
    assert sarif._sarif_level_to_severity("note") == "low"
    assert sarif._sarif_level_to_severity("none") == "info"


def test_sarif_level_to_severity_unknown_defaults_medium():
    assert sarif._sarif_level_to_severity("weird") == "medium"


def test_export_to_sarif_basic_structure():
    report = sarif.export_to_sarif({"findings": [_sample_finding()]})
    assert report["version"] == "2.1.0"
    assert report["$schema"].endswith("sarif-schema-2.1.0.json")
    assert len(report["runs"]) == 1
    run = report["runs"][0]
    assert run["tool"]["driver"]["name"] == "漏洞哨兵 11-S"
    assert run["tool"]["driver"]["version"] == "11-S"
    assert len(run["results"]) == 1
    assert run["invocations"][0]["executionSuccessful"] is True


def test_export_to_sarif_empty_findings():
    report = sarif.export_to_sarif({"findings": []})
    assert report["runs"][0]["tool"]["driver"]["rules"] == []
    assert report["runs"][0]["results"] == []
    assert report["version"] == "2.1.0"


def test_export_to_sarif_empty_findings_missing_key():
    report = sarif.export_to_sarif({})
    assert report["runs"][0]["results"] == []
    assert report["runs"][0]["properties"]["scanUrl"] == ""


def test_export_to_sarif_scan_metadata_propagated():
    scan_data = {
        "findings": [_sample_finding()],
        "url": "https://scan.example.com",
        "score": 72,
        "risk_level": "高风险",
    }
    props = sarif.export_to_sarif(scan_data)["runs"][0]["properties"]
    assert props["scanUrl"] == "https://scan.example.com"
    assert props["scanScore"] == 72
    assert props["scanRiskLevel"] == "高风险"


def test_export_to_sarif_rule_metadata():
    rules = sarif._build_sarif_rules([_sample_finding()])[0]
    assert len(rules) == 1
    rule = rules[0]
    assert rule["id"] == "VS-89"
    assert rule["name"] == "Sql Injection"
    assert rule["helpUri"] == "https://cwe.mitre.org/data/definitions/89.html"
    assert rule["properties"]["security-severity"] == "8.0"
    assert rule["properties"]["precision"] == "high"
    assert "A03" in rule["properties"]["tags"]
    assert "CWE-89" in rule["properties"]["tags"]


@pytest.mark.parametrize(
    "severity,level",
    [
        ("critical", "error"),
        ("high", "error"),
        ("medium", "warning"),
        ("low", "note"),
        ("info", "none"),
    ],
)
def test_export_to_sarif_result_level_mapping(severity, level):
    report = sarif.export_to_sarif({"findings": [_sample_finding(severity=severity)]})
    assert report["runs"][0]["results"][0]["level"] == level


def test_export_to_sarif_unknown_severity_defaults_warning():
    report = sarif.export_to_sarif({"findings": [_sample_finding(severity="bogus")]})
    assert report["runs"][0]["results"][0]["level"] == "warning"


def test_export_to_sarif_truncates_long_message():
    long_summary = "A" * 600
    report = sarif.export_to_sarif({"findings": [_sample_finding(summary=long_summary)]})
    msg = report["runs"][0]["results"][0]["message"]["text"]
    assert len(msg) == 500
    assert msg.endswith("...")


def test_export_to_sarif_includes_fixes_when_present():
    report = sarif.export_to_sarif({"findings": [_sample_finding()]})
    result = report["runs"][0]["results"][0]
    assert result["fixes"][0]["description"]["text"] == "使用参数化查询"


def test_export_to_sarif_omits_fixes_when_absent():
    finding = _sample_finding()
    finding.pop("fix")
    report = sarif.export_to_sarif({"findings": [finding]})
    assert "fixes" not in report["runs"][0]["results"][0]


def test_export_to_sarif_includes_code_flows_for_evidence():
    report = sarif.export_to_sarif({"findings": [_sample_finding()]})
    result = report["runs"][0]["results"][0]
    assert "codeFlows" in result
    flow_msg = result["codeFlows"][0]["threadFlows"][0]["locations"][0]["location"]["message"]["text"]
    assert json.loads(flow_msg) == {"payload": "' OR 1=1--", "matched": True}


def test_export_to_sarif_omits_code_flows_without_evidence():
    finding = _sample_finding()
    finding.pop("evidence")
    report = sarif.export_to_sarif({"findings": [finding]})
    assert "codeFlows" not in report["runs"][0]["results"][0]


def test_export_to_sarif_includes_locations_and_fingerprints():
    report = sarif.export_to_sarif({"findings": [_sample_finding()]})
    result = report["runs"][0]["results"][0]
    loc = result["locations"][0]
    assert loc["physicalLocation"]["artifactLocation"]["uri"] == "https://target.example.com/search"
    assert loc["logicalLocations"][0]["name"] == "q"
    assert result["partialFingerprints"]["primary"] == "VS-89:https://target.example.com/search:q"


def test_export_to_sarif_custom_tool_name_version():
    report = sarif.export_to_sarif(
        {"findings": []}, tool_name="CustomScanner", tool_version="9.9"
    )
    driver = report["runs"][0]["tool"]["driver"]
    assert driver["name"] == "CustomScanner"
    assert driver["version"] == "9.9"


def test_build_sarif_rules_dedupes_by_rule_id():
    findings = [
        _sample_finding(),
        _sample_finding(severity="low"),  # same CWE -> same rule id
        _sample_finding(cwe_id="CWE-79", type="xss"),
    ]
    rules, rule_index_map = sarif._build_sarif_rules(findings)
    assert len(rules) == 2
    assert set(rule_index_map.keys()) == {"VS-89", "VS-79"}
    assert rule_index_map["VS-89"] == 0
    assert rule_index_map["VS-79"] == 1


def test_import_from_sarif_empty_runs():
    assert sarif.import_from_sarif({"runs": []}) == []


def test_import_from_sarif_empty_results():
    sarif_data = {
        "runs": [
            {
                "tool": {"driver": {"name": "T", "rules": []}},
                "results": [],
            }
        ]
    }
    assert sarif.import_from_sarif(sarif_data) == []


def test_import_from_sarif_round_trip():
    scan_data = {"findings": [_sample_finding()]}
    report = sarif.export_to_sarif(scan_data)
    imported = sarif.import_from_sarif(report)
    assert len(imported) == 1
    finding = imported[0]
    assert finding["severity"] == "high"
    assert finding["level"] == "高风险"
    assert finding["url"] == "https://target.example.com/search"
    assert finding["parameter"] == "q"
    assert finding["summary"] == "存在 SQL 注入漏洞"
    assert finding["fix"] == "使用参数化查询"
    assert finding["cwe_id"] == "CWE-89"
    assert finding["owasp"] == "A03"
    assert finding["type"] == "sql_injection"
    assert finding["confidence_level"] == "高"
    assert finding["source"] == "sarif_import"
    assert finding["source_tool"] == "漏洞哨兵 11-S"
    assert finding["evidence"] == {"payload": "' OR 1=1--", "matched": True}


def test_import_from_sarif_extracts_severity_from_security_score():
    # level says "note" (low) but security-severity overrides to critical.
    sarif_data = {
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "T",
                        "rules": [
                            {
                                "id": "VS-X",
                                "name": "X",
                                "shortDescription": {"text": "x"},
                                "properties": {
                                    "security-severity": "9.5",
                                    "precision": "high",
                                    "tags": [],
                                },
                            }
                        ],
                    }
                },
                "results": [
                    {
                        "ruleId": "VS-X",
                        "ruleIndex": 0,
                        "level": "note",
                        "message": {"text": "msg"},
                        "locations": [],
                    }
                ],
            }
        ]
    }
    findings = sarif.import_from_sarif(sarif_data)
    assert findings[0]["severity"] == "critical"


def test_import_from_sarif_handles_invalid_evidence_json():
    sarif_data = {
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "T",
                        "rules": [
                            {
                                "id": "VS-X",
                                "name": "X",
                                "shortDescription": {"text": "x"},
                                "properties": {"tags": []},
                            }
                        ],
                    }
                },
                "results": [
                    {
                        "ruleId": "VS-X",
                        "ruleIndex": 0,
                        "level": "warning",
                        "message": {"text": "msg"},
                        "locations": [],
                        "codeFlows": [
                            {
                                "threadFlows": [
                                    {
                                        "locations": [
                                            {
                                                "location": {
                                                    "physicalLocation": {
                                                        "artifactLocation": {"uri": "u"},
                                                        "region": {"startLine": 1},
                                                    },
                                                    "message": {"text": "not-json"},
                                                }
                                            }
                                        ]
                                    }
                                ]
                            }
                        ],
                    }
                ],
            }
        ]
    }
    findings = sarif.import_from_sarif(sarif_data)
    assert findings[0]["evidence"] == {"raw": "not-json"}


def test_export_to_sarif_skips_finding_that_raises(monkeypatch):
    # Force a conversion error to exercise the try/except guard in export.
    def _boom(finding, rule_index_map):
        raise RuntimeError("boom")

    monkeypatch.setattr(sarif, "_finding_to_sarif_result", _boom)
    report = sarif.export_to_sarif({"findings": [_sample_finding()]})
    assert report["runs"][0]["results"] == []


# ===========================================================================
# app/core/response.py
# ===========================================================================


def test_success_response_default():
    resp = success_response()
    assert resp.status_code == 200
    payload = json.loads(resp.body)
    assert payload == {"success": True, "message": "ok"}


def test_success_response_with_data_and_meta():
    resp = success_response(data={"a": 1}, meta={"page": 2}, message="done")
    payload = json.loads(resp.body)
    assert payload == {
        "success": True,
        "message": "done",
        "data": {"a": 1},
        "meta": {"page": 2},
    }


def test_success_response_omits_data_when_none():
    resp = success_response(data=None, message="hi")
    payload = json.loads(resp.body)
    assert "data" not in payload
    assert payload["message"] == "hi"


def test_success_response_omits_meta_when_none():
    resp = success_response(data=1, meta=None)
    payload = json.loads(resp.body)
    assert "meta" not in payload


def test_success_response_custom_status_code():
    resp = success_response(status_code=201)
    assert resp.status_code == 201


def test_success_response_returns_jsonresponse():
    assert isinstance(success_response(), JSONResponse)


def test_error_response_default():
    resp = error_response("bad input")
    assert resp.status_code == 400
    payload = json.loads(resp.body)
    assert payload == {"success": False, "error": "bad input", "code": "ERROR"}


def test_error_response_with_extra():
    resp = error_response("conflict", code="CONFLICT", status_code=409, extra={"id": 7})
    payload = json.loads(resp.body)
    assert payload == {
        "success": False,
        "error": "conflict",
        "code": "CONFLICT",
        "id": 7,
    }
    assert resp.status_code == 409


def test_error_response_custom_status_code():
    assert error_response("nope", status_code=422).status_code == 422


def test_error_response_returns_jsonresponse():
    assert isinstance(error_response("x"), JSONResponse)


def test_code_map_contains_expected_codes():
    assert CODE_MAP[400] == "BAD_REQUEST"
    assert CODE_MAP[401] == "UNAUTHORIZED"
    assert CODE_MAP[403] == "FORBIDDEN"
    assert CODE_MAP[404] == "NOT_FOUND"
    assert CODE_MAP[409] == "CONFLICT"
    assert CODE_MAP[422] == "VALIDATION_ERROR"
    assert CODE_MAP[429] == "TOO_MANY_REQUESTS"
    assert CODE_MAP[500] == "INTERNAL_ERROR"


# ===========================================================================
# app/core/exceptions.py
# ===========================================================================


def test_business_exception_defaults():
    exc = exceptions.BusinessException("something broke")
    assert exc.detail == "something broke"
    assert exc.code == "BUSINESS_ERROR"
    assert exc.status_code == 400
    assert str(exc) == "something broke"


def test_business_exception_custom_args():
    exc = exceptions.BusinessException("boom", code="CUSTOM", status_code=418)
    assert exc.code == "CUSTOM"
    assert exc.status_code == 418


def test_not_found_exception():
    exc = exceptions.NotFoundException()
    assert exc.status_code == 404
    assert exc.code == "NOT_FOUND"
    assert exc.detail == "资源不存在"


def test_not_found_exception_custom_detail():
    exc = exceptions.NotFoundException("user missing")
    assert exc.detail == "user missing"
    assert exc.status_code == 404


def test_unauthorized_exception():
    exc = exceptions.UnauthorizedException()
    assert exc.status_code == 401
    assert exc.code == "UNAUTHORIZED"


def test_forbidden_exception():
    exc = exceptions.ForbiddenException()
    assert exc.status_code == 403
    assert exc.code == "FORBIDDEN"


def test_rate_limit_exception():
    exc = exceptions.RateLimitException()
    assert exc.status_code == 429
    assert exc.code == "TOO_MANY_REQUESTS"


def test_payment_required_exception():
    exc = exceptions.PaymentRequiredException()
    assert exc.status_code == 402
    assert exc.code == "PAYMENT_REQUIRED"


def test_all_business_exceptions_are_subclasses():
    for cls in (
        exceptions.NotFoundException,
        exceptions.UnauthorizedException,
        exceptions.ForbiddenException,
        exceptions.RateLimitException,
        exceptions.PaymentRequiredException,
    ):
        assert issubclass(cls, exceptions.BusinessException)


def _build_exception_app():
    app = FastAPI()
    exceptions.register_exception_handlers(app)

    @app.get("/biz")
    def biz():
        raise exceptions.BusinessException("custom biz error", code="BIZ_CODE", status_code=418)

    @app.get("/notfound")
    def notfound():
        raise exceptions.NotFoundException("widget missing")

    @app.get("/http")
    def http_exc():
        raise HTTPException(
            status_code=429, detail="slow down", headers={"Retry-After": "60"}
        )

    @app.get("/boom")
    def boom():
        raise RuntimeError("kaboom")

    return app


def test_register_exception_handlers_handles_business_exception():
    client = TestClient(_build_exception_app(), raise_server_exceptions=False)
    resp = client.get("/biz")
    assert resp.status_code == 418
    data = resp.json()
    assert data["success"] is False
    assert data["error"] == "custom biz error"
    assert data["code"] == "BIZ_CODE"


def test_register_exception_handlers_handles_not_found_exception():
    client = TestClient(_build_exception_app(), raise_server_exceptions=False)
    resp = client.get("/notfound")
    assert resp.status_code == 404
    data = resp.json()
    assert data["code"] == "NOT_FOUND"
    assert data["error"] == "widget missing"


def test_register_exception_handlers_handles_http_exception():
    client = TestClient(_build_exception_app(), raise_server_exceptions=False)
    resp = client.get("/http")
    assert resp.status_code == 429
    data = resp.json()
    assert data["code"] == "TOO_MANY_REQUESTS"
    assert data["error"] == "slow down"
    assert data["headers"] == {"Retry-After": "60"}


def test_register_exception_handlers_handles_generic_exception():
    client = TestClient(_build_exception_app(), raise_server_exceptions=False)
    resp = client.get("/boom")
    assert resp.status_code == 500
    data = resp.json()
    assert data["success"] is False
    assert data["error"] == "服务器内部错误"
    assert data["code"] == "INTERNAL_ERROR"


# ===========================================================================
# app/core/input_validation.py
# ===========================================================================


def test_validate_url_accepts_public_url(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", _fake_getaddrinfo("93.184.216.34"))
    ok, reason = input_validation.validate_url("https://example.com")
    assert ok is True
    assert reason == ""


def test_validate_url_accepts_public_ip_literal():
    ok, reason = input_validation.validate_url("http://93.184.216.34/path")
    assert ok is True
    assert reason == ""


def test_validate_url_rejects_empty():
    ok, reason = input_validation.validate_url("")
    assert ok is False
    assert "不能为空" in reason


def test_validate_url_rejects_none():
    ok, reason = input_validation.validate_url(None)
    assert ok is False
    assert "不能为空" in reason


@pytest.mark.parametrize("scheme", ["file:///etc/passwd", "gopher://x", "ftp://x", "dict://x"])
def test_validate_url_rejects_non_http_scheme(scheme):
    ok, reason = input_validation.validate_url(scheme)
    assert ok is False
    assert "http" in reason


def test_validate_url_rejects_missing_hostname():
    ok, reason = input_validation.validate_url("https://")
    assert ok is False
    assert "主机名" in reason


def test_validate_url_rejects_too_long():
    ok, reason = input_validation.validate_url("https://example.com/" + "a" * 2100)
    assert ok is False
    assert "长度" in reason


@pytest.mark.parametrize(
    "ip",
    ["127.0.0.1", "10.0.0.1", "192.168.1.1", "172.16.0.1", "169.254.169.254", "0.0.0.0", "::1"],
)
def test_validate_url_rejects_private_ip_literal(ip):
    url = f"http://[{ip}]" if ":" in ip else f"http://{ip}"
    ok, reason = input_validation.validate_url(url)
    assert ok is False
    assert "SSRF" in reason


def test_validate_url_rejects_domain_resolving_to_private_ip(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", _fake_getaddrinfo("10.0.0.5"))
    ok, reason = input_validation.validate_url("https://rebind.example.com")
    assert ok is False
    assert "SSRF" in reason


def test_is_blocked_ip_private_ipv4():
    assert input_validation._is_blocked_ip("10.1.2.3") is True


def test_is_blocked_ip_public_ipv4():
    assert input_validation._is_blocked_ip("8.8.8.8") is False


def test_is_blocked_ip_invalid_returns_false():
    assert input_validation._is_blocked_ip("not-an-ip") is False


def test_is_blocked_ip_strips_ipv6_zone():
    # "::1%eth0" should be split on '%' and the "::1" portion is loopback.
    assert input_validation._is_blocked_ip("::1%eth0") is True


def test_is_localhost_recognizes_loopback():
    for host in ["localhost", "127.0.0.1", "::1"]:
        assert input_validation._is_localhost(host) is True


def test_is_localhost_rejects_non_loopback():
    assert input_validation._is_localhost("8.8.8.8") is False
    assert input_validation._is_localhost("example.com") is False


def test_sanitize_input_none_returns_empty():
    assert input_validation.sanitize_input(None) == ""


def test_sanitize_input_strips_control_chars():
    text = "hello\x00\x07world\x1f"
    assert input_validation.sanitize_input(text) == "helloworld"


def test_sanitize_input_preserves_newlines_tabs():
    text = "line1\ttab\nline2\r"
    assert input_validation.sanitize_input(text) == "line1\ttab\nline2"


def test_sanitize_input_truncates_to_max_length():
    text = "abcdefghij"
    assert input_validation.sanitize_input(text, max_length=5) == "abcde"


def test_sanitize_input_strips_whitespace():
    assert input_validation.sanitize_input("  hello  ") == "hello"


def test_sanitize_input_non_string_input():
    assert input_validation.sanitize_input(12345) == "12345"


def test_validate_scan_target_localhost_allowed_without_auth():
    ok, reason = input_validation.validate_scan_target("http://localhost", authorized=False)
    assert ok is True
    assert reason == ""


def test_validate_scan_target_loopback_ip_allowed_without_auth():
    ok, _ = input_validation.validate_scan_target("http://127.0.0.1", authorized=False)
    assert ok is True


def test_validate_scan_target_nonlocal_requires_auth():
    ok, reason = input_validation.validate_scan_target(
        "https://example.com", authorized=False
    )
    assert ok is False
    assert "授权" in reason


def test_validate_scan_target_nonlocal_with_auth():
    ok, reason = input_validation.validate_scan_target(
        "https://example.com", authorized=True
    )
    assert ok is True
    assert reason == ""


def test_validate_scan_target_rejects_bad_scheme():
    ok, reason = input_validation.validate_scan_target("file:///etc/passwd")
    assert ok is False
    assert "http" in reason


def test_validate_scan_target_rejects_empty():
    ok, reason = input_validation.validate_scan_target("")
    assert ok is False


@pytest.mark.parametrize(
    "payload",
    [
        "1 UNION SELECT password FROM users",
        "' OR '1'='1",
        "admin' OR 1=1--",
        "1; DROP TABLE users",
        "1; UPDATE users SET role='admin'",
        "EXEC('sp')",
        "xp_cmdshell 'dir'",
        "/* block comment */",
    ],
)
def test_detect_sql_injection_detects_payloads(payload):
    assert input_validation.detect_sql_injection(payload) is True


def test_detect_sql_injection_empty_returns_false():
    assert input_validation.detect_sql_injection("") is False
    assert input_validation.detect_sql_injection(None) is False


def test_detect_sql_injection_benign_text_returns_false():
    assert input_validation.detect_sql_injection("hello world 12345") is False


def test_strip_xss_removes_script_tag():
    # strip_xss removes the <script> tags but leaves the inner text content.
    assert input_validation.strip_xss("<script>alert(1)</script>hello") == "alert(1)hello"


def test_strip_xss_removes_iframe_and_svg():
    out = input_validation.strip_xss("<iframe src='x'></iframe><svg onload=alert(1)>")
    assert "<iframe" not in out
    assert "<svg" not in out


def test_strip_xss_removes_event_handlers():
    out = input_validation.strip_xss('<img src=x onerror=alert(1)>')
    assert "onerror" not in out


def test_strip_xss_removes_javascript_uri():
    out = input_validation.strip_xss('<a href="javascript:alert(1)">x</a>')
    assert "javascript:" not in out


def test_strip_xss_empty_returns_empty():
    assert input_validation.strip_xss("") == ""
    assert input_validation.strip_xss(None) == ""


def test_strip_xss_benign_text_unchanged():
    assert input_validation.strip_xss("plain text 123") == "plain text 123"


# ===========================================================================
# app/core/security_headers.py
# ===========================================================================


def test_security_headers_contain_expected_keys():
    for key in [
        "X-Content-Type-Options",
        "X-XSS-Protection",
        "X-Frame-Options",
        "Referrer-Policy",
        "Content-Security-Policy",
        "Permissions-Policy",
    ]:
        assert key in security_headers.SECURITY_HEADERS


def test_https_only_headers_contains_hsts():
    assert "Strict-Transport-Security" in security_headers.HTTPS_ONLY_HEADERS


def test_apply_security_headers_adds_defaults():
    resp = Response(content="hi")
    security_headers.apply_security_headers(resp)
    assert resp.headers["X-Content-Type-Options"] == "nosniff"
    assert resp.headers["X-Frame-Options"] == "DENY"
    assert resp.headers["X-XSS-Protection"] == "1; mode=block"
    assert "default-src 'self'" in resp.headers["Content-Security-Policy"]


def test_apply_security_headers_no_hsts_over_http():
    resp = Response(content="hi")
    security_headers.apply_security_headers(resp, is_https=False)
    assert "Strict-Transport-Security" not in resp.headers


def test_apply_security_headers_adds_hsts_over_https():
    resp = Response(content="hi")
    security_headers.apply_security_headers(resp, is_https=True)
    assert resp.headers["Strict-Transport-Security"] == "max-age=31536000; includeSubDomains"


def test_apply_security_headers_returns_same_response():
    resp = Response(content="hi")
    assert security_headers.apply_security_headers(resp) is resp


def test_is_https_secure_scheme():
    request = Request(_make_request_scope(scheme="https"))
    assert security_headers._is_https(request) is True


def test_is_https_forwarded_proto():
    request = Request(
        _make_request_scope(scheme="http", headers=[("x-forwarded-proto", "https")])
    )
    assert security_headers._is_https(request) is True


def test_is_https_plain_http_returns_false():
    request = Request(_make_request_scope(scheme="http"))
    assert security_headers._is_https(request) is False


def test_is_https_forwarded_proto_with_multiple_values():
    request = Request(
        _make_request_scope(scheme="http", headers=[("x-forwarded-proto", "https, http")])
    )
    assert security_headers._is_https(request) is True


def _build_security_headers_app():
    app = FastAPI()
    app.middleware("http")(security_headers.security_headers_middleware)

    @app.get("/")
    def root():
        return {"ok": True}

    return app


def test_security_headers_middleware_adds_headers():
    client = TestClient(_build_security_headers_app())
    resp = client.get("/")
    assert resp.headers["X-Content-Type-Options"] == "nosniff"
    assert resp.headers["X-Frame-Options"] == "DENY"


def test_security_headers_middleware_no_hsts_over_http():
    client = TestClient(_build_security_headers_app())
    resp = client.get("/")
    assert "strict-transport-security" not in {k.lower() for k in resp.headers.keys()}


def test_security_headers_middleware_adds_hsts_via_forwarded_proto():
    client = TestClient(_build_security_headers_app())
    resp = client.get("/", headers={"x-forwarded-proto": "https"})
    assert resp.headers["Strict-Transport-Security"] == "max-age=31536000; includeSubDomains"


# ===========================================================================
# app/db/session.py
# ===========================================================================


def test_convert_qmark_simple():
    sql, had = session._convert_qmark("SELECT * FROM users WHERE id = ?")
    assert sql == "SELECT * FROM users WHERE id = :p0"
    assert had is True


def test_convert_qmark_no_placeholders():
    sql, had = session._convert_qmark("SELECT 1")
    assert sql == "SELECT 1"
    assert had is False


def test_convert_qmark_multiple_placeholders():
    sql, had = session._convert_qmark("INSERT INTO t (a, b, c) VALUES (?, ?, ?)")
    assert sql == "INSERT INTO t (a, b, c) VALUES (:p0, :p1, :p2)"
    assert had is True


def test_convert_qmark_ignores_qmark_in_single_quoted_string():
    sql, had = session._convert_qmark("SELECT '?' FROM t WHERE x = ?")
    assert sql == "SELECT '?' FROM t WHERE x = :p0"
    assert had is True


def test_convert_qmark_preserves_escaped_single_quotes():
    sql, _ = session._convert_qmark("SELECT 'O''Brien' WHERE x = ?")
    assert sql == "SELECT 'O''Brien' WHERE x = :p0"


def test_convert_qmark_ignores_qmark_in_double_quoted_identifier():
    sql, had = session._convert_qmark('SELECT "col?weird" FROM t WHERE x = ?')
    assert sql == 'SELECT "col?weird" FROM t WHERE x = :p0'
    assert had is True


def test_convert_qmark_ignores_qmark_in_line_comment():
    sql, had = session._convert_qmark("SELECT 1 -- ignore this ?\nFROM t WHERE x = ?")
    assert "-- ignore this ?" in sql
    assert sql.endswith("WHERE x = :p0")
    assert had is True


def test_convert_qmark_ignores_qmark_in_block_comment():
    sql, had = session._convert_qmark("SELECT /* ? */ a FROM t WHERE b = ?")
    assert "/* ? */" in sql
    assert sql == "SELECT /* ? */ a FROM t WHERE b = :p0"
    assert had is True


def test_convert_qmark_continues_indexing_after_comment():
    sql, _ = session._convert_qmark("SELECT /* ? */ a FROM t WHERE b = ? AND c = ?")
    assert sql == "SELECT /* ? */ a FROM t WHERE b = :p0 AND c = :p1"


def test_convert_qmark_empty_string():
    sql, had = session._convert_qmark("")
    assert sql == ""
    assert had is False


def test_bind_params_none():
    assert session._bind_params(None) == {}


def test_bind_params_dict_is_copied():
    original = {"a": 1, "b": 2}
    bound = session._bind_params(original)
    assert bound == original
    bound["a"] = 99
    assert original["a"] == 1


def test_bind_params_sequence():
    assert session._bind_params((10, 20, 30)) == {"p0": 10, "p1": 20, "p2": 30}


def test_row_proxy_string_key_access():
    row = session._RowProxy({"id": 1, "name": "alice"})
    assert row["id"] == 1
    assert row["name"] == "alice"


def test_row_proxy_int_index_access():
    row = session._RowProxy({"id": 1, "name": "alice"})
    assert row[0] == 1
    assert row[1] == "alice"


def test_row_proxy_int_index_with_explicit_keys():
    row = session._RowProxy({"a": "x", "b": "y"}, keys=["b", "a"])
    assert row[0] == "y"
    assert row[1] == "x"


def test_row_proxy_attribute_access():
    row = session._RowProxy({"username": "bob"})
    assert row.username == "bob"


def test_row_proxy_missing_attribute_raises():
    row = session._RowProxy({"username": "bob"})
    with pytest.raises(AttributeError):
        row.nonexistent


def test_row_proxy_private_name_raises():
    row = session._RowProxy({"username": "bob"})
    with pytest.raises(AttributeError):
        row._secret


def test_row_proxy_dict_conversion():
    row = session._RowProxy({"id": 1, "name": "alice"})
    assert dict(row) == {"id": 1, "name": "alice"}


def test_row_proxy_keys_values_items():
    row = session._RowProxy({"id": 1, "name": "alice"})
    assert row.keys() == ["id", "name"]
    assert row.values() == [1, "alice"]
    assert row.items() == [("id", 1), ("name", "alice")]


def test_row_proxy_len_and_contains():
    row = session._RowProxy({"id": 1, "name": "alice"})
    assert len(row) == 2
    assert "id" in row
    assert "missing" not in row


def test_row_proxy_get_with_default():
    row = session._RowProxy({"id": 1})
    assert row.get("id") == 1
    assert row.get("missing") is None
    assert row.get("missing", "default") == "default"


def test_row_proxy_iteration_yields_values():
    row = session._RowProxy({"id": 1, "name": "alice"})
    assert list(row) == [1, "alice"]


def test_row_proxy_repr():
    row = session._RowProxy({"id": 1})
    assert "_RowProxy" in repr(row)


def test_mask_url_with_password():
    url = "postgresql://user:secret@host:5432/db"
    assert session._mask_url(url) == "postgresql://user:****@host:5432/db"


def test_mask_url_without_credentials():
    url = "postgresql://host:5432/db"
    assert session._mask_url(url) == "postgresql://host:5432/db"


def test_mask_url_without_scheme_unchanged():
    url = "user:secret@host"
    assert session._mask_url(url) == "user:secret@host"


def test_mask_url_no_at_sign_unchanged():
    assert session._mask_url("sqlite:///path/to.db") == "sqlite:///path/to.db"


def test_init_db_path_sets_globals():
    old_path = session._db_path
    old_url = session._database_url
    try:
        session.init_db_path("/tmp/foobar.db", "")
        assert session._db_path == "/tmp/foobar.db"
        assert session._database_url == ""
    finally:
        session.init_db_path(old_path, old_url)


def test_get_db_returns_sqlite_connection(sqlite_db):
    conn = session.get_db()
    try:
        assert isinstance(conn, sqlite3.Connection)
        assert conn.row_factory is sqlite3.Row
    finally:
        conn.close()


def test_get_db_applies_wal_pragma(sqlite_db):
    conn = session.get_db()
    try:
        mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        assert mode.lower() == "wal"
        foreign_keys = conn.execute("PRAGMA foreign_keys").fetchone()[0]
        assert foreign_keys == 1
    finally:
        conn.close()


def test_get_db_connection_context_manager(sqlite_db):
    with session.get_db_connection() as conn:
        row = conn.execute("SELECT 1 AS v").fetchone()
        assert row["v"] == 1
    # Connection should be closed after leaving the context.
    with pytest.raises(sqlite3.ProgrammingError):
        conn.execute("SELECT 1")


def test_get_db_connection_row_access(sqlite_db):
    with session.get_db_connection() as conn:
        conn.execute("CREATE TABLE t (id INTEGER, name TEXT)")
        conn.execute("INSERT INTO t VALUES (?, ?)", (1, "alice"))
        conn.commit()
        row = conn.execute("SELECT id, name FROM t WHERE id = ?", (1,)).fetchone()
        assert row["name"] == "alice"
        assert row[0] == 1
        assert dict(row) == {"id": 1, "name": "alice"}


def test_check_db_health_true_when_connected(sqlite_db):
    assert session.check_db_health() is True


def test_check_db_health_false_on_error(monkeypatch):
    monkeypatch.setattr(session, "_db_path", "/nonexistent_dir_xyz/test.db")
    monkeypatch.setattr(session, "_database_url", "")
    assert session.check_db_health() is False
