"""V11.5 版本升级验证测试

确认所有面向用户的版本标识都已从 V11.4 → V11.5,
并且 V11.5 新增的能力(LLM/auto-patrol/trusted domains/AI 顾问优化)都还在。
"""
import re
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
def test_settings_app_version_is_11_5():
    """Settings.app_version 应为 11.5"""
    assert M.settings.app_version == "11.5"


def test_settings_app_title_is_v11_5():
    """Settings.app_title 应为 漏洞哨兵 V11.5"""
    assert M.settings.app_title == "漏洞哨兵 V11.5"


def test_api_version_endpoint_returns_11_5():
    """/api/version 应返回 version=11.5"""
    client = TestClient(M.app)
    r = client.get("/api/version")
    assert r.status_code == 200
    body = r.json()
    assert body.get("version") == "11.5", f"got {body.get('version')}"
    assert "V11.5" in body.get("title", "")


def test_health_endpoint_works():
    """/api/health 仍正常"""
    client = TestClient(M.app)
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


# ============================================================
# 2) index.html 用户可见标识必须都是 V11.5
# ============================================================
def test_index_html_title_is_v11_5():
    html = open(str(ROOT / "static/index.html")).read()
    assert "<title>漏洞哨兵 V11.5" in html
    # 离线 /api/version 返回的 title 也得是 V11.5
    assert '漏洞哨兵 V11.5 (离线演示模式)' in html


def test_index_html_meta_description_is_v11_5():
    html = open(str(ROOT / "static/index.html")).read()
    assert 'name="description" content="漏洞哨兵 V11.5' in html


def test_index_html_user_facing_v11_5_strings():
    """卡片/页脚中的 V11.5 字样"""
    html = open(str(ROOT / "static/index.html")).read()
    # 进化页面 h3
    assert ">漏洞哨兵 V11.5<" in html
    # 我的页面段落
    assert "<strong>漏洞哨兵 V11.5</strong>" in html
    # AI 顾问话术: "你好！我是漏洞哨兵 V11.5"
    assert "我是漏洞哨兵 V11.5" in html
    # 评分公式回复提到 V11.5
    assert "V11.5 评分公式" in html
    # 版本更新回复提到 V11.5
    assert "V11.5 主要改进" in html


def test_index_html_offline_version_11_5():
    """离线模式 /api/health, /api/version 返回 11.5"""
    html = open(str(ROOT / "static/index.html")).read()
    assert 'version: "11.5-offline"' in html
    assert 'version: "11.5"' in html
    assert 'build_time: "2026-06-25"' in html


# ============================================================
# 3) V11.5 新增能力仍然存在(没在升级过程中丢)
# ============================================================
def test_v115_has_confidence_system():
    """V11.5 置信度系统还在"""
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
    """AI 顾问手机端优化还在"""
    html = open(str(ROOT / "static/index.html")).read()
    # fullscreen CSS 还在
    assert ".ai-chat" in html
    # !important 强制 opacity
    assert "opacity: 1 !important" in html or "opacity:1 !important" in html
    # WQY 字体还在
    assert "WQY MicroHei" in html
    # 扫描深度档位修复还在
    assert "scan-depth-opt" in html
