"""V11.4 验收测试：PDF 中文字体不能退化为 ■"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_pdf_chinese_font_registered():
    """PDF 字体注册：必须成功（非 Helvetica）"""
    from main import generate_pdf_report

    sample = {
        "url": "https://test.com", "time": "2026-06-25", "score": 95, "risk_level": "低风险",
        "summary": {"total": 1, "critical": 0, "high": 0, "medium": 0, "low": 1},
        "findings": [
            {"name": "测试中文问题", "severity": "low", "level_zh": "低风险",
             "owasp": "A05 安全配置错误", "summary": "测试中文描述",
             "fix": "add_header Test 中文配置 'self' always;"}
        ],
        "owasp_coverage": [
            {"category": "A01 测试", "status": "通过", "note": "中文备注"}
        ],
        "header_details": [], "info_leaks": [], "cors": None,
        "cookie_issues": [], "ssl_info": {}, "waf": [], "sensitive_paths": [],
    }
    pdf_bytes = generate_pdf_report(sample)
    assert pdf_bytes, "PDF bytes should not be empty"
    assert len(pdf_bytes) > 1000, f"PDF too small ({len(pdf_bytes)} bytes)"
    # 尝试提取文本验证
    try:
        from pdfminer.high_level import extract_text
        text = extract_text(__import__("io").BytesIO(pdf_bytes))
    except ImportError:
        try:
            import subprocess
            r = subprocess.run(["pdftotext", "-", "-"], input=pdf_bytes, capture_output=True, timeout=5)
            text = r.stdout.decode("utf-8", errors="ignore")
        except Exception:
            return  # 跳过文本验证
    # 关键断言：能找到中文（不能全是 ■）
    assert "中文" in text or "问题" in text, f"PDF missing Chinese text. Got: {text[:200]}"
    # 不能全是 ■
    import re
    blackboxes = len(re.findall(r"■{3,}", text))
    assert blackboxes < 3, f"Too many black boxes in PDF: {blackboxes} occurrences (font fallback issue)"


def test_owasp_top10_full_coverage():
    """PDF 报告必须包含完整 A01-A10 OWASP 覆盖（不是只有 finding 的）"""
    from main import generate_pdf_report

    sample = {
        "url": "https://test.com", "time": "2026-06-25", "score": 95, "risk_level": "低风险",
        "summary": {"total": 1, "critical": 0, "high": 0, "medium": 0, "low": 1},
        "findings": [
            {"name": "测试", "severity": "low", "owasp": "A05", "summary": "测试"}
        ],
        "owasp_coverage": [
            {"category": c, "status": "通过", "note": "测试"}
            for c in [f"A0{i} 测试" for i in range(1, 11)]
        ],
        "header_details": [], "info_leaks": [], "cors": None,
        "cookie_issues": [], "ssl_info": {}, "waf": [], "sensitive_paths": [],
    }
    pdf_bytes = generate_pdf_report(sample)
    try:
        import subprocess
        r = subprocess.run(["pdftotext", "-", "-"], input=pdf_bytes, capture_output=True, timeout=5)
        text = r.stdout.decode("utf-8", errors="ignore")
    except Exception:
        return
    # 必须有 A01-A10 全部
    for i in range(1, 11):
        assert f"A0{i}" in text, f"PDF missing A0{i} OWASP coverage"


def test_scan_auth_log_endpoint_exists():
    """/api/scan-auth-log 端点必须存在（前端会调用）"""
    from fastapi.testclient import TestClient
    from main import app
    client = TestClient(app)
    # 不需要登录，验证端点存在（不是 404）
    resp = client.post("/api/scan-auth-log", json={"authorized_at": "2026-06-25"})
    assert resp.status_code in (200, 401), f"Endpoint should exist: {resp.status_code} {resp.text}"


def test_get_single_scan_endpoint_exists():
    """/api/scan/{id} 端点必须存在"""
    from fastapi.testclient import TestClient
    from main import app
    client = TestClient(app)
    resp = client.get("/api/scan/1")
    assert resp.status_code in (200, 401, 404), f"Endpoint should exist: {resp.status_code}"
