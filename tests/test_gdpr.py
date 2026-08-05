"""GDPR 数据合规服务测试。

测试 app/services/gdpr_service.py 的核心功能：
- 数据导出需要登录
- 账号删除需要确认参数
- 匿名化功能

参考 tests/test_billing.py 的测试模式（_login_demo 函数等）。
"""

import os
import sys
import uuid

from fastapi.testclient import TestClient

os.environ["DB_DIR"] = "/tmp/v11-test"
os.environ["DB_NAME"] = "test.db"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import app  # noqa: E402

client = TestClient(app)


def _login_demo() -> str:
    """登录 demo 账号（不存在则自动注册），返回 JWT token。"""
    login = client.post("/api/login", json={"username": "demo", "password": "demo123"})
    if login.status_code != 200:
        reg = client.post(
            "/api/register",
            json={"username": "demo", "password": "demo123", "email": "demo@example.com"},
        )
        assert reg.status_code == 200, f"Register failed: {reg.text}"
        login = client.post("/api/login", json={"username": "demo", "password": "demo123"})
    assert login.status_code == 200, f"Login failed: {login.text}"
    return login.json()["token"]


def _register_unique_user() -> tuple[str, int]:
    """注册一个独立用户（避免影响 demo 账号），返回 (token, user_id)。"""
    name = "gdpr_" + uuid.uuid4().hex[:8]
    reg = client.post(
        "/api/register",
        json={"username": name, "password": "pass1234", "email": f"{name}@example.com"},
    )
    assert reg.status_code == 200, f"Register failed: {reg.text}"
    body = reg.json()
    return body["token"], int(body["user_id"])


def test_export_requires_login():
    """数据导出必须登录，未登录返回 401。"""
    resp = client.get("/api/me/export")
    assert resp.status_code == 401


def test_export_returns_user_data():
    """登录后导出数据包含用户基本信息（排除密码）及各数据类别。"""
    token = _login_demo()
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/api/me/export", headers=headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()["data"]
    # 用户基本信息存在且不含密码字段
    assert data["user"] is not None
    assert "password" not in data["user"]
    # 包含全部数据类别
    for key in ("scans", "recharge_records", "usage_logs", "audit_logs", "fix_tickets", "finding_feedback"):
        assert key in data


def test_delete_account_requires_confirm():
    """删除账号必须传入 confirm=DELETE 确认参数。"""
    token, _ = _register_unique_user()
    headers = {"Authorization": f"Bearer {token}"}
    # 不传 confirm 参数
    resp = client.delete("/api/me/account", headers=headers)
    assert resp.status_code == 400
    err = resp.json().get("error", "")
    assert "DELETE" in err or "确认" in err


def test_delete_account_with_confirm():
    """传入 confirm=DELETE 后账号及关联数据被删除，无法再次登录。"""
    name = "del_" + uuid.uuid4().hex[:8]
    reg = client.post(
        "/api/register",
        json={"username": name, "password": "pass1234", "email": f"{name}@example.com"},
    )
    assert reg.status_code == 200, reg.text
    token = reg.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.delete("/api/me/account?confirm=DELETE", headers=headers)
    assert resp.status_code == 200, resp.text
    result = resp.json()["data"]
    assert result["success"] is True
    assert "users" in result["deleted_tables"]

    # 删除后无法再登录
    login = client.post("/api/login", json={"username": name, "password": "pass1234"})
    assert login.status_code != 200


def test_anonymize_requires_login():
    """匿名化必须登录，未登录返回 401。"""
    resp = client.post("/api/me/anonymize")
    assert resp.status_code == 401


def test_anonymize_user_data():
    """匿名化后用户名变为 deleted_user_{id}，邮箱与密码清空。"""
    from app.db.session import get_db

    token, user_id = _register_unique_user()
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.post("/api/me/anonymize", headers=headers)
    assert resp.status_code == 200, resp.text
    result = resp.json()["data"]
    assert result["success"] is True

    # 直接查库验证匿名化效果
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT username, email, password FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        assert row is not None
        assert row["username"] == f"deleted_user_{user_id}"
        assert row["email"] == ""
        assert row["password"] == ""
    finally:
        conn.close()
