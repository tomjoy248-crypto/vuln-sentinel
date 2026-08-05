"""
积分 / 按量计费模块测试。
覆盖：余额查询、扫描扣费、额度不足 402 响应。
"""
import os
import sys
import time

from fastapi.testclient import TestClient

# 强制使用与 test_main.py 一致的临时 DB
os.environ["DB_DIR"] = "/tmp/v11-test"
os.environ["DB_NAME"] = "test.db"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import main  # noqa: E402
from app.services import credits_service  # noqa: E402

client = TestClient(main.app)


def _login_demo():
    r = client.post("/api/login", json={"username": "demo", "password": "demo123"})
    assert r.status_code == 200, f"demo login failed: {r.text}"
    return {"Authorization": f"Bearer {r.json()['token']}"}


def _register_user():
    u = "credit_u_" + str(int(time.time() * 1000000))
    r = client.post("/api/register", json={"username": u, "password": "pass1234"})
    assert r.status_code == 200, f"register failed: {r.text}"
    body = r.json()
    return {"Authorization": f"Bearer {body['token']}"}, body["user_id"]


def test_me_returns_credits():
    h = _login_demo()
    r = client.get("/api/me", headers=h)
    assert r.status_code == 200, r.text
    body = r.json()
    assert "credits" in body
    assert isinstance(body["credits"], int)
    assert body["credits"] >= 0


def test_me_credits_endpoint():
    h, user_id = _register_user()
    r = client.get("/api/me/credits", headers=h)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("success") is True
    assert body["data"]["credits"] == 10


def test_usage_endpoint_shape():
    h, user_id = _register_user()
    r = client.get("/api/usage", headers=h)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("success") is True
    assert "logs" in body["data"]
    assert "total" in body["data"]
    assert "meta" in body


def test_scan_consumes_credits():
    h, user_id = _register_user()
    before = credits_service.get_credits(user_id)
    assert before >= 1

    r = client.post("/api/scan", json={"url": "example.com", "authorized": True}, headers=h)
    assert r.status_code == 200, r.text
    body = r.json()
    # 扫描可能成功也可能因网络失败返回 success=False 的 ScanResponse；无论哪种都扣费
    assert "success" in body

    after = credits_service.get_credits(user_id)
    assert after == before - credits_service.SCAN_STANDARD_COST


def test_scan_insufficient_credits_returns_402():
    h, user_id = _register_user()
    # 把用户积分清零
    conn = main.get_db()
    try:
        conn.execute("UPDATE users SET credits=0 WHERE id=?", (user_id,))
        conn.commit()
    finally:
        conn.close()

    r = client.post("/api/scan", json={"url": "example.com", "authorized": True}, headers=h)
    assert r.status_code == 402, f"expected 402, got {r.status_code}: {r.text}"
    body = r.json()
    assert body.get("code") == "PAYMENT_REQUIRED"
    assert body.get("success") is False
