"""V11.6 QA 修复验证测试
- 扫描深度档位可点
- 字体加载
- 置信度系统
"""
import re
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

import main as M
import asyncio  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def _run_analyze_security(*args, **kwargs):
    return asyncio.run(M.analyze_security(*args, **kwargs))


@pytest.fixture
def client():
    return TestClient(M.app)


# ============================================================
# 1) 扫描深度档位：label.click() 能切换 radio
# ============================================================
def test_index_html_has_scan_depth_labels():
    """index.html 应有 .scan-depth-opt label 元素(代替 display:none radio)"""
    html = open(str(ROOT / "static/index.html")).read()
    assert 'class="scan-depth-opt' in html, "missing .scan-depth-opt"
    # 不能再有 display:none 的 radio
    assert 'name="scan-depth" value="deep" style="display:none"' not in html, "still has display:none"
    assert 'name="scan-depth" value="quick" style="display:none"' not in html, "still has display:none"
    assert 'name="scan-depth" value="standard" style="display:none"' not in html, "still has display:none"


def test_index_html_registers_scan_depth_click():
    """JS 应监听 .scan-depth-opt 的 click,而不是 radio change"""
    html = open(str(ROOT / "static/index.html")).read()
    # 新逻辑：在 click handler 里调用 radio.dispatchEvent
    assert "querySelectorAll('.scan-depth-opt')" in html
    assert ".scan-depth-opt'" not in html or "addEventListener('click'" in html


# ============================================================
# 2) 字体：@font-face + WQY
# ============================================================
def test_wqy_font_face_loaded():
    html = open(str(ROOT / "static/index.html")).read()
    assert "@font-face" in html
    assert "wqy-microhei" in html or "WQY MicroHei" in html


def test_font_stack_includes_wqy():
    html = open(str(ROOT / "static/index.html")).read()
    assert '"WQY MicroHei Local"' in html
    # 同时保留 CJK 兜底
    assert "Noto Sans CJK" in html or "PingFang SC" in html


# ============================================================
# 3) AI 顾问手机端：全屏、不透明、字号大
# ============================================================
def test_ai_chat_mobile_fullscreen():
    html = open(str(ROOT / "static/index.html")).read()
    # 移动端 fullscreen CSS
    assert "max-width: 640px" in html or "max-width:640px" in html
    # 不透明背景强制
    assert "background: var(--card) !important" in html or "opacity: 1 !important" in html
    # 字号加大
    assert "font-size: 15px" in html or "font-size:15px" in html


def test_ai_msg_has_text_color():
    """AI bot 消息必须显式 color,避免被全局 transparent 继承"""
    html = open(str(ROOT / "static/index.html")).read()
    assert ".ai-msg.bot" in html
    # 提取 .ai-msg.bot 行
    m = re.search(r'\.ai-msg\.bot\s*\{([^}]+)\}', html)
    assert m, "no .ai-msg.bot rule"
    assert "color:" in m.group(1), f"bot msg missing color: {m.group(1)}"


# ============================================================
# 4) V11.6：置信度系统 + WAF 不消除漏洞
# ============================================================
def test_trusted_domains_removed():
    """V11.6 已移除 TRUSTED_DOMAINS 白名单，不能以"知名"为由自动判定安全"""
    src = open(str(ROOT / "main.py")).read()
    # TRUSTED_DOMAINS 局部定义应已删除
    assert "TRUSTED_DOMAINS = {" not in src, "TRUSTED_DOMAINS should be removed"


def test_waf_does_not_erase_findings():
    """WAF 站点仍应报告 missing header finding，只是置信度为中"""
    from main import analyze_security
    result = _run_analyze_security(
        url="https://example.com",
        headers={},  # 空 headers
        is_https=True,
        ssl_info={"has_cert": True, "expired": False, "days_left": 90, "weak": False},
        waf_list=[{"name": "Cloudflare", "value": "cloudflare"}],
        sensitive_paths=[],
        vuln_findings=[],
    )
    # 必须有 finding（WAF 不消除）
    assert len(result["findings"]) > 0, "WAF should not erase findings"
    # 至少有一个 finding 的置信度为"中"（WAF 站点）
    conf_levels = [f.get("confidence_level", "") for f in result["findings"]]
    assert "中" in conf_levels, f"WAF site should have medium confidence, got {conf_levels}"


def test_confidence_levels_present():
    """所有 finding 必须包含 confidence_level 字段"""
    from main import analyze_security
    result = _run_analyze_security(
        url="https://example.com",
        headers={},
        is_https=True,
        ssl_info={"has_cert": True, "expired": False, "days_left": 90, "weak": False},
        waf_list=[],
        sensitive_paths=[],
        vuln_findings=[],
    )
    for f in result["findings"]:
        assert "confidence_level" in f, f"finding missing confidence_level: {f['name']}"
        assert f["confidence_level"] in ("高", "中", "低")


def test_waf_bonus_capped_at_3():
    """WAF 最多 +3 分，不能覆盖真实缺失项"""
    from main import analyze_security
    # 无 WAF 的站点
    result_no_waf = _run_analyze_security(
        url="https://example.com",
        headers={},
        is_https=True,
        ssl_info={"has_cert": True, "expired": False, "days_left": 90, "weak": False},
        waf_list=[],
        sensitive_paths=[],
        vuln_findings=[],
    )
    # 有 WAF 的站点
    result_waf = _run_analyze_security(
        url="https://example.com",
        headers={},
        is_https=True,
        ssl_info={"has_cert": True, "expired": False, "days_left": 90, "weak": False},
        waf_list=[{"name": "Cloudflare", "value": "cloudflare"}],
        sensitive_paths=[],
        vuln_findings=[],
    )
    # WAF bonus 最多 3 分
    assert result_waf["score"] - result_no_waf["score"] <= 3, \
        f"WAF bonus too large: {result_waf['score']} vs {result_no_waf['score']}"
    # 两者分数差距应很小（WAF 不能覆盖缺失项）
    assert result_waf["score"] - result_no_waf["score"] >= 0, \
        f"WAF should not reduce score: {result_waf['score']} vs {result_no_waf['score']}"


def test_restricted_scan_low_confidence():
    """受限扫描的所有 finding 置信度应为低"""
    from main import analyze_security
    result = _run_analyze_security(
        url="https://example.com",
        headers={"x-waf-check": "captcha"},  # 触发受限扫描
        is_https=True,
        ssl_info={"has_cert": True, "expired": False, "days_left": 90, "weak": False},
        waf_list=[],
        sensitive_paths=[{"suspect": True, "reason": "疑似登录页"}],
        vuln_findings=[],
    )
    assert result["restricted"] is True
    for f in result["findings"]:
        assert f["confidence_level"] == "低", f"restricted scan finding should be low confidence: {f['name']}"


# ============================================================
# 5) 关键性能与功能回归（不能破已有功能）
# ============================================================
def test_health_still_works(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_unknown_api_still_json(client):
    r = client.get("/api/unknown-endpoint")
    assert r.status_code in (404,)
    assert r.headers.get("content-type", "").startswith("application/json")
