"""11-S 版本升级验证测试

确认所有面向用户的版本标识都已从 V11.4 → 11-S,
并且 11-S 新增的能力(LLM/auto-patrol/trusted domains/AI 顾问优化)都还在。
"""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import main as M

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def client():
    return TestClient(M.app)


# ============================================================
# 1) Settings 中的版本号必须是 11.5
# ============================================================
def test_settings_app_version_is_11_s():
    """Settings.app_version 应为 11-S"""
    assert M.settings.app_version == "11-S"


def test_settings_app_title_is_v11_5():
    """Settings.app_title 应为 漏洞哨兵 11-S"""
    assert M.settings.app_title == "漏洞哨兵 11-S"


def test_api_version_endpoint_returns_11_s():
    """/api/version 应返回 version=11-S"""
    client = TestClient(M.app)
    r = client.get("/api/version")
    assert r.status_code == 200
    body = r.json()
    assert body.get("version") == "11-S", f"got {body.get('version')}"
    assert "11-S" in body.get("title", "")


def test_health_endpoint_works():
    """/api/health 仍正常"""
    client = TestClient(M.app)
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


# ============================================================
# 2) 前端产物用户可见标识必须都是 11-S
# ============================================================
def test_index_html_title_is_v11_5():
    """生产环境入口 static/index.html 标题保持 11-S"""
    html = open(str(ROOT / "static/index.html")).read()
    assert "<title>漏洞哨兵 11-S" in html


def test_index_html_meta_description_is_v11_5():
    html = open(str(ROOT / "static/index.html")).read()
    assert 'name="description" content="漏洞哨兵 11-S' in html


def test_frontend_source_has_11_s_strings():
    """前后端分离后，11-S 标识位于前端源码中"""
    main_js = (ROOT / "frontend/src/main.js").read_text(encoding="utf-8")
    templates_js = (ROOT / "frontend/src/templates.js").read_text(encoding="utf-8")
    # AI 顾问话术
    assert "我是漏洞哨兵 11-S" in main_js
    # 扫描深度档位还在
    assert "scan-depth-opt" in templates_js


def test_frontend_source_has_ai_chat_optimization():
    """AI 顾问手机端优化 CSS 类还在"""
    css = (ROOT / "frontend/src/style.css").read_text(encoding="utf-8")
    assert ".ai-chat" in css
    assert "opacity: 1 !important" in css or "opacity:1 !important" in css
    assert "WQY MicroHei" in css


# ============================================================
# 3) 11-S 新增能力仍然存在(没在升级过程中丢)
# ============================================================
def test_v115_has_confidence_system():
    """11-S 置信度系统还在"""
    src = open(str(ROOT / "main.py")).read()
    assert "confidence_level" in src, "confidence_level field missing"
    assert "_confidence_level_from_int" in src, "confidence mapping helper missing"


def test_v115_has_llm_integration():
    """真实 LLM 接入还在"""
    src = open(str(ROOT / "main.py")).read()
    assert "_call_llm" in src, "LLM 调用函数缺失"
    assert "_build_llm_prompt" in src, "LLM prompt 构建函数缺失"
    assert "llm_api_key" in src, "LLM 配置字段缺失"


def test_v115_has_auto_patrol():
    """auto-patrol 还在"""
    src = open(str(ROOT / "main.py")).read()
    assert "_patrol_all_monitors_sync" in src, "auto-patrol 函数缺失"
    assert "patrol_interval_hours" in src, "patrol 配置字段缺失"


def test_v115_has_ai_advisor_optimization():
    """AI 顾问手机端优化还在（前后端分离后源码在前端项目）"""
    css = (ROOT / "frontend/src/style.css").read_text(encoding="utf-8")
    templates_js = (ROOT / "frontend/src/templates.js").read_text(encoding="utf-8")
    # fullscreen CSS 还在
    assert ".ai-chat" in css
    # !important 强制 opacity
    assert "opacity: 1 !important" in css or "opacity:1 !important" in css
    # WQY 字体还在
    assert "WQY MicroHei" in css
    # 扫描深度档位修复还在
    assert "scan-depth-opt" in templates_js
