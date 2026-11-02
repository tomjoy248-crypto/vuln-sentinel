"""XXE、反序列化和上传入口的离线准确性契约。

仅使用本地受控响应，不发送网络请求；不能替代真实授权靶场验证。
"""

from __future__ import annotations

import os
import sys

import httpx
import pytest

os.environ.setdefault("DB_DIR", "/tmp/v12-accuracy-test")
os.environ.setdefault("DB_NAME", "test.db")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import main  # noqa: E402
from app.benchmark.runner import ConfusionMatrix, compute_metrics  # noqa: E402
from app.plugins import ScanContext  # noqa: E402
from app.plugins.detectors.business import FileUploadDetector  # noqa: E402


@pytest.mark.asyncio
async def test_xxe_positive_negative_matrix(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/soap.xml" and request.method == "POST":
            if "probe=positive" in str(request.url):
                return httpx.Response(200, text="vuln-sentinel-xxe-probe")
            return httpx.Response(200, text="XML parsed as text")
        return httpx.Response(404, text="not found")

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    monkeypatch.setattr(main, "get_httpx_client", lambda: client)
    try:
        positive = await main.detect_xxe("https://target.test/soap.xml?probe=positive", ["xml"])
        negative = await main.detect_xxe("https://target.test/soap.xml", ["xml"])
    finally:
        await client.aclose()

    matrix = ConfusionMatrix(tp=int(bool(positive)), fn=int(not positive), fp=int(bool(negative)), tn=int(not negative))
    assert matrix.to_dict() == {"tp": 1, "fp": 0, "tn": 1, "fn": 0}
    assert compute_metrics(matrix).precision == 1.0


@pytest.mark.asyncio
async def test_deserialization_positive_negative_matrix(monkeypatch):
    signature = next(iter(main.DESER_SIGNATURES))
    client = httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(200, text="safe response")))
    monkeypatch.setattr(main, "get_httpx_client", lambda: client)
    try:
        positive = await main.detect_insecure_deserialization({"Set-Cookie": f"session={signature}"}, "https://target.test")
        negative = await main.detect_insecure_deserialization({"Set-Cookie": "session=opaque-random-token"}, "https://target.test")
    finally:
        await client.aclose()

    assert any(item.get("type") == "deserialization" for item in positive)
    assert not any(item.get("type") == "deserialization" for item in negative)


@pytest.mark.asyncio
async def test_upload_entry_signal_does_not_claim_executable_upload(monkeypatch):
    async def scan(url: str, response_text: str, post_status: int):
        def handler(request: httpx.Request) -> httpx.Response:
            if request.method == "POST":
                return httpx.Response(post_status, text="stored")
            return httpx.Response(200, text=response_text)

        client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        monkeypatch.setattr("app.plugins.detectors.business.httpx.AsyncClient", lambda **kwargs: client)
        return await FileUploadDetector().detect(ScanContext(url=url))

    positive = await scan(
        "https://target.test/profile",
        '<form enctype="multipart/form-data"><input type="file" name="avatar"></form>',
        201,
    )
    negative = await scan("https://target.test/catalog", "<p>Catalog search</p>", 404)

    assert len(positive) == 1
    assert positive[0].type == "file_upload"
    assert "upload_accepted" in positive[0].evidence.extra["signals"]
    assert not negative
    assert "需检查文件类型" in positive[0].description
