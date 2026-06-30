"""11-S 真 LLM 接入 + 自动巡检 + AI 状态端点测试"""
import json
import os
import pytest
from fastapi.testclient import TestClient

# 必须在 import main 前配置 LLM 环境变量（某些测试覆盖）
os.environ.setdefault("LLM_ENABLED", "false")
os.environ.setdefault("LLM_API_KEY", "")

import main as M


@pytest.fixture
def client():
    return TestClient(M.app)


@pytest.fixture
def auth_headers(client):
    """注册并登录一个测试用户，返回 Authorization header"""
    uname = "llmtester"
    r = client.post("/api/register", json={"username": uname, "password": "test1234"})
    if r.status_code == 200 and r.json().get("token"):
        return {"Authorization": f"Bearer {r.json()['token']}"}
    # 已存在则登录
    r = client.post("/api/login", json={"username": uname, "password": "test1234"})
    if r.status_code == 200 and r.json().get("token"):
        return {"Authorization": f"Bearer {r.json()['token']}"}
    # 实在拿不到 token 时尝试从 cookie 拿
    if r.cookies.get("token"):
        return {"Cookie": f"token={r.cookies['token']}"}
    pytest.skip("无法获得测试用户 token")


# ============================================================
# 1) /api/ai/status 不需鉴权
# ============================================================
def test_ai_status_endpoint_returns_config(client):
    r = client.get("/api/ai/status")
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert "llm_enabled" in data
    assert "provider" in data
    assert "model" in data
    assert "api_key_configured" in data
    assert "providers_supported" in data
    # 默认未启用
    assert data["llm_enabled"] is False
    assert data["api_key_configured"] is False


# ============================================================
# 2) /api/ai/test 在未配置时降级
# ============================================================
def test_ai_test_returns_fallback_when_not_configured(client, auth_headers):
    r = client.post("/api/ai/test", json={"message": "你好"}, headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    # 未配置 LLM → 应返回 success=False, fallback=True
    assert data.get("fallback") is True
    assert data.get("success") is False


# ============================================================
# 3) _call_llm 在未配置时抛 RuntimeError（不能静默成功）
# ============================================================
def test_call_llm_raises_when_not_configured():
    import asyncio
    # 确保 settings.llm_enabled = False
    M.settings.llm_enabled = False
    M.settings.llm_api_key = ""
    with pytest.raises(RuntimeError, match="LLM"):
        asyncio.run(M._call_llm([{"role": "user", "content": "hi"}]))


# ============================================================
# 4) _build_llm_prompt 包含用户历史和反复问题
# ============================================================
def test_build_llm_prompt_includes_insights():
    insights = {
        "total_scans": 5,
        "predicted_next_score": 88,
        "persistent_issues": [
            {"name": "缺少 HSTS", "times": 3, "severity": "medium"},
        ],
    }
    history = [
        {"role": "user", "content": "什么是 HSTS"},
        {"role": "assistant", "content": "HSTS 是..."},
    ]
    msgs = M._build_llm_prompt("怎么修 HSTS", history, insights)
    # 应有 system + 2 条历史 + 1 条新问题 = 4 条
    assert len(msgs) == 4
    assert msgs[0]["role"] == "system"
    assert "HSTS" in msgs[0]["content"]  # persistent 信息
    assert "5" in msgs[0]["content"]  # total_scans
    assert "88" in msgs[0]["content"]  # predicted
    assert msgs[-1]["content"] == "怎么修 HSTS"


# ============================================================
# 5) 关键字匹配降级路径仍然工作（未启用 LLM 时）
# ============================================================
def test_ai_chat_fallback_to_keyword(client, auth_headers):
    """未配置 LLM 时，HSTS 关键字匹配应返回包含 HSTS 的回答"""
    M.settings.llm_enabled = False
    r = client.post("/api/ai/chat", json={"message": "HSTS"}, headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert "response" in data
    assert data["llm_used"] is False
    # HSTS 关键字分支的回答里应提到 Nginx
    assert "Nginx" in data["response"] or "HSTS" in data["response"]


# ============================================================
# 6) 启用 LLM 但 API Key 错误时降级
# ============================================================
def test_ai_chat_falls_back_when_llm_fails(monkeypatch, client, auth_headers):
    """模拟 LLM 抛异常，应降级到关键字匹配（HSTS 关键字）"""
    M.settings.llm_enabled = True
    M.settings.llm_api_key = "fake-key-123"

    async def fake_call_llm(messages):
        raise RuntimeError("模拟 LLM 失败")

    monkeypatch.setattr(M, "_call_llm", fake_call_llm)

    r = client.post("/api/ai/chat", json={"message": "HSTS 是什么"}, headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["llm_used"] is False
    # 降级路径走 HSTS 关键字分支
    assert "HSTS" in data["response"]


# ============================================================
# 7) 启用 LLM 且 _call_llm 成功时，llm_used 应为 True
# ============================================================
def test_ai_chat_uses_llm_when_available(monkeypatch, client, auth_headers):
    M.settings.llm_enabled = True
    M.settings.llm_api_key = "fake-key-123"

    async def fake_call_llm(messages):
        return "**测试回答** 这是 LLM 真实返回"

    monkeypatch.setattr(M, "_call_llm", fake_call_llm)

    r = client.post("/api/ai/chat", json={"message": "随便问"}, headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["llm_used"] is True
    assert data["response"] == "**测试回答** 这是 LLM 真实返回"


# ============================================================
# 8) 巡检函数：空监控时不能 crash
# ============================================================
def test_patrol_with_no_monitors_does_not_crash():
    """无任何监控项时，巡检函数应安静返回，不抛异常"""
    # 直接调用同步函数（不依赖 scheduler）
    M._patrol_all_monitors_sync()


# ============================================================
# 9) 巡检会更新 last_patrol_at
# ============================================================
def test_patrol_updates_last_patrol_at(client, auth_headers):
    """创建一个监控后，调用同步巡检函数，应更新 last_patrol_at"""
    # 创建监控
    r = client.post("/api/monitors", json={"url": "https://example.com", "frequency": 3600}, headers=auth_headers)
    assert r.status_code == 200
    mid = r.json().get("monitor_id") or r.json().get("id")
    assert mid is not None

    # 调用巡检
    M._patrol_all_monitors_sync()

    # 查询监控项
    r2 = client.get("/api/monitors", headers=auth_headers)
    assert r2.status_code == 200
    monitors = r2.json().get("monitors", [])
    target = [m for m in monitors if m["id"] == mid]
    if target:
        # 巡检应已更新 last_patrol_at
        assert target[0].get("last_patrol_at") is not None


# ============================================================
# 10) settings 中 LLM 字段默认值
# ============================================================
def test_settings_have_llm_fields():
    assert hasattr(M.settings, "llm_enabled")
    assert hasattr(M.settings, "llm_provider")
    assert hasattr(M.settings, "llm_api_key")
    assert hasattr(M.settings, "llm_model")
    assert hasattr(M.settings, "llm_base_url")
    assert hasattr(M.settings, "patrol_interval_hours")
    assert hasattr(M.settings, "patrol_score_regression_threshold")
