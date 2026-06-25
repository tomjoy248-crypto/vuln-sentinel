"""V11.4 QA 修复验证测试
- 扫描深度档位可点
- 字体加载
- 已知高安全站点误报降低
"""
import re
import pytest
from fastapi.testclient import TestClient

import main as M


@pytest.fixture
def client():
    return TestClient(M.app)


# ============================================================
# 1) 扫描深度档位：label.click() 能切换 radio
# ============================================================
def test_index_html_has_scan_depth_labels():
    """index.html 应有 .scan-depth-opt label 元素(代替 display:none radio)"""
    html = open("/workspace/v11.4/static/index.html").read()
    assert 'class="scan-depth-opt' in html, "missing .scan-depth-opt"
    # 不能再有 display:none 的 radio
    assert 'name="scan-depth" value="deep" style="display:none"' not in html, "still has display:none"
    assert 'name="scan-depth" value="quick" style="display:none"' not in html, "still has display:none"
    assert 'name="scan-depth" value="standard" style="display:none"' not in html, "still has display:none"


def test_index_html_registers_scan_depth_click():
    """JS 应监听 .scan-depth-opt 的 click,而不是 radio change"""
    html = open("/workspace/v11.4/static/index.html").read()
    # 新逻辑：在 click handler 里调用 radio.dispatchEvent
    assert "querySelectorAll('.scan-depth-opt')" in html
    assert ".scan-depth-opt'" not in html or "addEventListener('click'" in html


# ============================================================
# 2) 字体：@font-face + WQY
# ============================================================
def test_wqy_font_face_loaded():
    html = open("/workspace/v11.4/static/index.html").read()
    assert "@font-face" in html
    assert "wqy-microhei" in html or "WQY MicroHei" in html


def test_font_stack_includes_wqy():
    html = open("/workspace/v11.4/static/index.html").read()
    assert '"WQY MicroHei Local"' in html
    # 同时保留 CJK 兜底
    assert "Noto Sans CJK" in html or "PingFang SC" in html


# ============================================================
# 3) AI 顾问手机端：全屏、不透明、字号大
# ============================================================
def test_ai_chat_mobile_fullscreen():
    html = open("/workspace/v11.4/static/index.html").read()
    # 移动端 fullscreen CSS
    assert "max-width: 640px" in html or "max-width:640px" in html
    # 不透明背景强制
    assert "background: var(--card) !important" in html or "opacity: 1 !important" in html
    # 字号加大
    assert "font-size: 15px" in html or "font-size:15px" in html


def test_ai_msg_has_text_color():
    """AI bot 消息必须显式 color,避免被全局 transparent 继承"""
    html = open("/workspace/v11.4/static/index.html").read()
    assert ".ai-msg.bot" in html
    # 提取 .ai-msg.bot 行
    m = re.search(r'\.ai-msg\.bot\s*\{([^}]+)\}', html)
    assert m, "no .ai-msg.bot rule"
    assert "color:" in m.group(1), f"bot msg missing color: {m.group(1)}"


# ============================================================
# 4) 已知高安全站点：白名单 + 误报降低
# ============================================================
def test_trusted_domains_set_exists():
    """main.py 应有 TRUSTED_DOMAINS 白名单"""
    src = open("/workspace/v11.4/main.py").read()
    assert "TRUSTED_DOMAINS" in src
    # 至少包含这些大厂
    for d in ["baidu.com", "google.com", "github.com", "microsoft.com"]:
        assert d in src, f"missing trusted domain: {d}"


def test_baidu_scoring_reduces_false_positive():
    """baidu 即使没 WAF 头也应被识别为已知高安全站点"""
    # 直接调用 analyze_security
    from main import analyze_security
    result = analyze_security(
        url="https://www.baidu.com",
        headers={},  # 空 headers，模拟 WAF 头没识别到
        is_https=True,
        ssl_info={"has_cert": True, "expired": False, "days_left": 90, "weak": False},
        waf_list=[],  # 没识别到 WAF
        sensitive_paths=[],
        vuln_findings=[],
    )
    # 大厂：分数至少 80（不再因缺响应头大幅扣分）
    assert result["score"] >= 80, f"baidu score too low: {result['score']}"
    # 风险等级应该是低
    assert result["risk_level"] in ("低风险", "中风险"), f"baidu risk: {result['risk_level']}"


def test_github_scoring_trusted():
    """github.com 也应被识别为高安全"""
    from main import analyze_security
    result = analyze_security(
        url="https://github.com",
        headers={},
        is_https=True,
        ssl_info={"has_cert": True, "expired": False, "days_left": 365, "weak": False},
        waf_list=[],
        sensitive_paths=[],
        vuln_findings=[],
    )
    assert result["score"] >= 80, f"github score too low: {result['score']}"


def test_taobao_scoring_trusted():
    from main import analyze_security
    result = analyze_security(
        url="https://www.taobao.com",
        headers={},
        is_https=True,
        ssl_info={"has_cert": True, "expired": False, "days_left": 200, "weak": False},
        waf_list=[],
        sensitive_paths=[],
        vuln_findings=[],
    )
    assert result["score"] >= 80, f"taobao score too low: {result['score']}"


def test_unknown_site_not_trusted():
    """普通站点不受白名单影响,继续走原来的打分"""
    from main import analyze_security
    result = analyze_security(
        url="https://example.com",
        headers={},
        is_https=False,
        ssl_info={"has_cert": False, "expired": False, "days_left": None, "weak": False},
        waf_list=[],
        sensitive_paths=[],
        vuln_findings=[],
    )
    # example.com 在白名单里吗？不在
    # 没 HTTPS 应大幅扣分
    assert result["score"] < 80, f"example.com should be penalized for no HTTPS, got {result['score']}"


# ============================================================
# 5) TRUSTED 域名匹配：子域名也算
# ============================================================
def test_trusted_subdomain_match():
    """tieba.baidu.com 也应匹配 baidu.com"""
    from main import analyze_security
    result = analyze_security(
        url="https://tieba.baidu.com",
        headers={},
        is_https=True,
        ssl_info={"has_cert": True, "expired": False, "days_left": 60, "weak": False},
        waf_list=[],
        sensitive_paths=[],
        vuln_findings=[],
    )
    assert result["score"] >= 80, f"tieba.baidu.com score too low: {result['score']}"


# ============================================================
# 6) 关键性能与功能回归（不能破已有功能）
# ============================================================
def test_health_still_works(client):
    r = client.get("/api/health")
    assert r.status_code == 200


def test_unknown_api_still_json(client):
    r = client.get("/api/scans")
    assert r.status_code == 404
    assert b"<!DOCTYPE" not in r.content
