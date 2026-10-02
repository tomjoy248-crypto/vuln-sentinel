"""离线注入检测准确性基准。

这些测试只验证扫描器对可控 HTTP 响应特征的判定契约。它们使用
``httpx.MockTransport``，不发送网络请求，也不能替代真实授权靶场上的
可利用性验证、WAF/CDN 回归或浏览器执行验证。
"""

from __future__ import annotations

import html
import os
import sys
import urllib.parse

import httpx
import pytest

os.environ.setdefault("DB_DIR", "/tmp/v11-test")
os.environ.setdefault("DB_NAME", "test.db")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import main  # noqa: E402
from app.benchmark.runner import ConfusionMatrix, compute_metrics  # noqa: E402


def _install_mock_client(monkeypatch, handler):
    """将检测器的共享 HTTP 客户端替换为确定性的离线传输。"""
    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    monkeypatch.setattr(main, "get_httpx_client", lambda: client)
    return client


@pytest.mark.asyncio
async def test_injection_response_signature_baseline(monkeypatch):
    """为四类注入规则验证正例检出与安全响应不误报。

    每一类规则都运行一个已知特征响应和一个安全响应。矩阵只衡量
    规则是否按预期产生 finding，不宣称真实应用的漏洞发现准确率。
    """

    command_signature = next(iter(main.CMD_EXEC_SIGNATURES))

    def handler(request: httpx.Request) -> httpx.Response:
        decoded_url = urllib.parse.unquote(str(request.url))
        query = urllib.parse.parse_qs(request.url.query.decode())
        path = request.url.path

        if path == "/sqli":
            if "probe=positive" in decoded_url:
                return httpx.Response(200, text="SQL syntax error near query")
            return httpx.Response(200, text="Catalog search returned no matches")

        if path == "/xss":
            value = query.get("q", [""])[0]
            if "probe=positive" in decoded_url and value:
                return httpx.Response(200, text=f"<script>const result = `{value}`;</script>")
            return httpx.Response(200, text=f"<p>{html.escape(value)}</p>")

        if path == "/ssti":
            value = query.get("q", [""])[0]
            if "probe=positive" in decoded_url and value.startswith("{{"):
                return httpx.Response(200, text="rendered: vulnsentinelprobe")
            return httpx.Response(200, text="template input treated as text")

        if path == "/cmdi":
            if "probe=positive" in decoded_url:
                return httpx.Response(200, text=f"command output: {command_signature}")
            return httpx.Response(200, text="request rejected by allowlist")

        return httpx.Response(404, text="not found")

    client = _install_mock_client(monkeypatch, handler)
    cases = [
        ("sqli", main.detect_sqli, "https://target.test/sqli?probe=positive&q=1", "https://target.test/sqli?q=1", ["q"]),
        ("xss", main.detect_reflected_xss, "https://target.test/xss?probe=positive&q=1", "https://target.test/xss?q=1", ["q"]),
        ("ssti", main.detect_ssti, "https://target.test/ssti?probe=positive&q=1", "https://target.test/ssti?q=1", ["q"]),
        ("cmdi", main.detect_command_injection, "https://target.test/cmdi?probe=positive&command=1", "https://target.test/cmdi?command=1", ["command"]),
    ]
    matrix = ConfusionMatrix()

    try:
        for vuln_type, detector, positive_url, negative_url, params in cases:
            positive_findings = await detector(positive_url, params)
            negative_findings = await detector(negative_url, params)
            if any(item.get("type") == vuln_type for item in positive_findings):
                matrix.tp += 1
            else:
                matrix.fn += 1
            if any(item.get("type") == vuln_type for item in negative_findings):
                matrix.fp += 1
            else:
                matrix.tn += 1
    finally:
        await client.aclose()

    metrics = compute_metrics(matrix)
    assert matrix.to_dict() == {"tp": 4, "fp": 0, "tn": 4, "fn": 0}
    assert metrics.precision == 1.0
    assert metrics.recall == 1.0
    assert metrics.accuracy == 1.0
