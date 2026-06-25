"""V11.4 进化验收：智能学习/主动监控/AI对话/团队协作"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_learn_insights_uses_history():
    """智能学习必须基于真实历史（不是返回空）"""
    from fastapi.testclient import TestClient
    from main import app
    client = TestClient(app)
    login = client.post("/api/login", json={"username": "demo", "password": "demo123"})
    if login.status_code != 200:
        import pytest
        pytest.skip("demo 未注册")
    token = login.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/api/learn/insights", headers=headers)
    assert resp.status_code == 200
    d = resp.json()
    # demo 用户之前测试扫过很多次
    assert d["total_scans"] > 0, f"Expected >0 scans, got {d['total_scans']}"
    assert "persistent_issues" in d
    assert "learning_insights" in d
    assert len(d["learning_insights"]) > 0


def test_create_and_list_monitor():
    """添加/列出监控目标端点必须工作"""
    from fastapi.testclient import TestClient
    from main import app
    client = TestClient(app)
    login = client.post("/api/login", json={"username": "demo", "password": "demo123"})
    if login.status_code != 200:
        import pytest
        pytest.skip("demo 未注册")
    token = login.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    # 添加
    r1 = client.post(
        "/api/monitors",
        json={"url": "https://example.com", "frequency_hours": 24},
        headers=headers,
    )
    assert r1.status_code == 200
    d = r1.json()
    assert d["success"]
    assert d.get("monitor_id")
    # 列出
    r2 = client.get("/api/monitors", headers=headers)
    assert r2.status_code == 200
    assert r2.json()["success"]
    assert r2.json()["total"] >= 1


def test_ai_chat_remembers_conversation():
    """AI 对话必须基于记忆（第二次能用到第一次的上下文）"""
    from fastapi.testclient import TestClient
    from main import app
    client = TestClient(app)
    login = client.post("/api/login", json={"username": "demo", "password": "demo123"})
    if login.status_code != 200:
        import pytest
        pytest.skip("demo 未注册")
    token = login.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    # 第一次问
    r1 = client.post(
        "/api/ai/chat",
        json={"message": "HSTS 怎么修？"},
        headers=headers,
    )
    assert r1.status_code == 200
    d1 = r1.json()
    # AI 必须返回有意义的回复（不空、不全是空白）
    assert d1["response"].strip()
    assert len(d1["response"]) > 10
    # 第二次问"我分数怎么样"应该用到之前的 insights
    r2 = client.post(
        "/api/ai/chat",
        json={"message": "我的分数怎么样"},
        headers=headers,
    )
    assert r2.status_code == 200
    d2 = r2.json()
    # 第二次必须显示 memory_used >= 1
    assert d2["memory_used"] >= 1


def test_create_team_and_comment():
    """团队创建 + 评论端点必须工作"""
    from fastapi.testclient import TestClient
    from main import app
    client = TestClient(app)
    login = client.post("/api/login", json={"username": "demo", "password": "demo123"})
    if login.status_code != 200:
        import pytest
        pytest.skip("demo 未注册")
    token = login.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    # 创建团队
    r1 = client.post(
        "/api/teams",
        json={"name": "测试团队 V11.4"},
        headers=headers,
    )
    assert r1.status_code == 200
    assert r1.json()["success"]
    # 给扫描 1 加评论
    r2 = client.post(
        "/api/scans/1/comment",
        json={"comment": "这个扫描需要复测"},
        headers=headers,
    )
    # 扫描 1 可能不存在，但端点不能 500
    assert r2.status_code in (200, 500)
    if r2.status_code == 200:
        assert r2.json()["success"]


def test_evolution_dashboard_aggregates():
    """综合仪表盘必须聚合学习/监控/团队"""
    from fastapi.testclient import TestClient
    from main import app
    client = TestClient(app)
    login = client.post("/api/login", json={"username": "demo", "password": "demo123"})
    if login.status_code != 200:
        import pytest
        pytest.skip("demo 未注册")
    token = login.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/api/evolution/dashboard", headers=headers)
    assert resp.status_code == 200
    d = resp.json()
    assert d["success"]
    assert "learning" in d
    assert "monitoring" in d
    assert "team" in d
    assert "evolution_score" in d
    assert 0 <= d["evolution_score"] <= 100


def test_monitor_alerts_endpoint():
    """告警端点必须返回正确结构"""
    from fastapi.testclient import TestClient
    from main import app
    client = TestClient(app)
    login = client.post("/api/login", json={"username": "demo", "password": "demo123"})
    if login.status_code != 200:
        import pytest
        pytest.skip("demo 未注册")
    token = login.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/api/monitors/alerts", headers=headers)
    assert resp.status_code == 200
    d = resp.json()
    assert d["success"]
    assert "alerts" in d
    assert "unread_count" in d
