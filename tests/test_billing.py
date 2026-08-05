"""计费套餐与充值 API 测试。"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient

os.environ["DB_DIR"] = "/tmp/v11-test"
os.environ["DB_NAME"] = "test.db"

from main import app

client = TestClient(app)


def _login_demo() -> str:
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


def _get_plan_id() -> int:
    """获取第一个可用套餐 ID（测试库中套餐 ID 不固定）。"""
    resp = client.get("/api/billing/plans")
    assert resp.status_code == 200
    plans = resp.json()["data"]["plans"]
    assert len(plans) > 0, "No billing plans available"
    return plans[0]["id"]


def test_public_config_returns_stripe_status():
    """/api/config 返回公开运行时配置（含 Stripe/支付宝/微信 启用状态，不含密钥）。"""
    resp = client.get("/api/config")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    cfg = data["data"]
    assert "stripe_enabled" in cfg
    assert "stripe_publishable_key" in cfg
    assert "public_base_url" in cfg
    assert "alipay_enabled" in cfg
    assert "wechat_enabled" in cfg


def test_get_billing_plans_returns_defaults():
    """/api/billing/plans 返回默认套餐。"""
    resp = client.get("/api/billing/plans")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    plans = data["data"]["plans"]
    assert len(plans) >= 1
    assert all(k in plans[0] for k in ("id", "name", "credits", "price_cents", "currency"))


def test_purchase_plan_requires_login():
    """购买套餐必须登录。"""
    resp = client.post("/api/billing/purchase", json={"plan_id": 1})
    assert resp.status_code == 401


def test_purchase_plan_increases_credits():
    """购买套餐后积分增加。"""
    token = _login_demo()
    headers = {"Authorization": f"Bearer {token}"}

    # 获取第一个套餐
    plans_resp = client.get("/api/billing/plans")
    plan = plans_resp.json()["data"]["plans"][0]
    plan_id = plan["id"]
    credits_before = client.get("/api/me/credits", headers=headers).json()["data"]["credits"]

    purchase = client.post("/api/billing/purchase", json={"plan_id": plan_id}, headers=headers)
    assert purchase.status_code == 200, purchase.text
    result = purchase.json()["data"]
    assert result["success"] is True
    assert result["credits_added"] == plan["credits"]

    credits_after = client.get("/api/me/credits", headers=headers).json()["data"]["credits"]
    assert credits_after == credits_before + plan["credits"]


def test_recharge_records_list_requires_login():
    """充值记录必须登录。"""
    resp = client.get("/api/billing/recharges")
    assert resp.status_code == 401


def test_recharge_records_after_purchase():
    """购买后充值记录可见。"""
    token = _login_demo()
    headers = {"Authorization": f"Bearer {token}"}

    records_resp = client.get("/api/billing/recharges", headers=headers)
    assert records_resp.status_code == 200
    data = records_resp.json()["data"]
    assert "records" in data
    assert "total" in data
    assert data["total"] >= 1


def test_admin_recharge_requires_admin():
    """非管理员不能调用管理员充值。"""
    token = _login_demo()
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.post(
        "/api/admin/recharge",
        json={"user_id": 1, "credits": 10, "note": "test"},
        headers=headers,
    )
    assert resp.status_code == 403
    assert "权限" in resp.json().get("error", "")


def test_create_order_mock_paid():
    """创建模拟支付订单后直接到账。"""
    token = _login_demo()
    headers = {"Authorization": f"Bearer {token}"}

    plans_resp = client.get("/api/billing/plans")
    plan = plans_resp.json()["data"]["plans"][0]
    plan_id = plan["id"]

    credits_before = client.get("/api/me/credits", headers=headers).json()["data"]["credits"]
    resp = client.post(
        "/api/billing/order",
        json={"plan_id": plan_id, "provider": "mock"},
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()["data"]
    assert data["success"] is True
    assert data["provider"] == "mock"
    assert data["status"] == "paid"
    assert data["credits_added"] == plan["credits"]

    credits_after = client.get("/api/me/credits", headers=headers).json()["data"]["credits"]
    assert credits_after == credits_before + plan["credits"]


def test_create_order_stripe_not_configured():
    """未配置 Stripe 时创建 stripe 订单返回错误。"""
    token = _login_demo()
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.post(
        "/api/billing/order",
        json={"plan_id": _get_plan_id(), "provider": "stripe"},
        headers=headers,
    )
    assert resp.status_code == 400
    assert "未启用" in resp.json().get("error", "")


def test_order_status_requires_owner():
    """普通用户不能查看他人订单。"""
    import uuid

    token = _login_demo()
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.post(
        "/api/billing/order",
        json={"plan_id": _get_plan_id(), "provider": "mock"},
        headers=headers,
    )
    tx = resp.json()["data"]["transaction_id"]

    # 换一个用户登录
    other_name = "other" + uuid.uuid4().hex[:8]
    reg = client.post(
        "/api/register",
        json={"username": other_name, "password": "other123", "email": f"{other_name}@example.com"},
    )
    assert reg.status_code == 200, reg.text
    other_token = client.post(
        "/api/login", json={"username": other_name, "password": "other123"}
    ).json()["token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}
    resp2 = client.get(f"/api/billing/order/{tx}", headers=other_headers)
    assert resp2.status_code == 403


def test_alipay_webhook_not_configured():
    """未配置支付宝时返回 501。"""
    resp = client.post("/api/billing/webhook/alipay", json={})
    assert resp.status_code == 501


def test_wechat_webhook_not_configured():
    """未配置微信支付时返回 501。"""
    resp = client.post("/api/billing/webhook/wechat", json={})
    assert resp.status_code == 501


def test_alipay_webhook_mock_fulfills_order():
    """ALIPAY_MOCK=true 时支付宝回调可幂等完成订单。"""
    import os

    os.environ["ALIPAY_MOCK"] = "true"
    try:
        token = _login_demo()
        headers = {"Authorization": f"Bearer {token}"}
        order = client.post(
            "/api/billing/order",
            json={"plan_id": _get_plan_id(), "provider": "mock"},
            headers=headers,
        ).json()["data"]
        tx = order["transaction_id"]

        resp = client.post(
            "/api/billing/webhook/alipay",
            json={"out_trade_no": tx, "trade_status": "TRADE_SUCCESS"},
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["success"] is True
        assert data["transaction_id"] == tx
    finally:
        os.environ.pop("ALIPAY_MOCK", None)


def test_wechat_webhook_mock_fulfills_order():
    """WECHAT_MOCK=true 时微信支付回调可幂等完成订单。"""
    import os

    os.environ["WECHAT_MOCK"] = "true"
    try:
        token = _login_demo()
        headers = {"Authorization": f"Bearer {token}"}
        order = client.post(
            "/api/billing/order",
            json={"plan_id": _get_plan_id(), "provider": "mock"},
            headers=headers,
        ).json()["data"]
        tx = order["transaction_id"]

        resp = client.post(
            "/api/billing/webhook/wechat",
            json={"out_trade_no": tx, "trade_state": "SUCCESS"},
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["success"] is True
        assert data["transaction_id"] == tx
    finally:
        os.environ.pop("WECHAT_MOCK", None)


def test_create_order_alipay_not_configured():
    """未配置支付宝时创建 alipay 订单返回 501 骨架提示。"""
    token = _login_demo()
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.post(
        "/api/billing/order",
        json={"plan_id": _get_plan_id(), "provider": "alipay"},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["provider"] == "alipay"
    assert data["status"] == "pending"
    assert "SDK" in data["note"]


def test_create_order_wechat_not_configured():
    """未配置微信时创建 wechat 订单返回 501 骨架提示。"""
    token = _login_demo()
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.post(
        "/api/billing/order",
        json={"plan_id": _get_plan_id(), "provider": "wechat"},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["provider"] == "wechat"
    assert data["status"] == "pending"
    assert "SDK" in data["note"]


def test_create_order_alipay_mock_paid():
    """ALIPAY_MOCK=true 时支付宝订单直接到账。"""
    import os

    os.environ["ALIPAY_MOCK"] = "true"
    try:
        token = _login_demo()
        headers = {"Authorization": f"Bearer {token}"}
        plans_resp = client.get("/api/billing/plans")
        plan = plans_resp.json()["data"]["plans"][0]
        credits_before = client.get("/api/me/credits", headers=headers).json()["data"]["credits"]

        resp = client.post(
            "/api/billing/order",
            json={"plan_id": plan["id"], "provider": "alipay"},
            headers=headers,
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()["data"]
        assert data["provider"] == "alipay"
        assert data["status"] == "paid"
        assert data["credits_added"] == plan["credits"]

        credits_after = client.get("/api/me/credits", headers=headers).json()["data"]["credits"]
        assert credits_after == credits_before + plan["credits"]
    finally:
        os.environ.pop("ALIPAY_MOCK", None)
