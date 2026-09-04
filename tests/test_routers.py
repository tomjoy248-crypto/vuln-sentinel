"""FastAPI 路由端点综合测试。

覆盖 app/routers/ 下全部路由模块的端点：
- auth.py    注册、登录、邮箱验证、密码重置
- user.py    当前用户信息、积分余额
- billing.py 套餐列表、购买、充值记录、订单、支付回调
- gdpr.py    数据导出、账号删除、匿名化
- team.py    团队成员查询、创建、加入、角色修改
- admin.py   审计日志查询

测试模式参考 tests/test_billing.py 与 tests/test_gdpr.py：
- 使用 TestClient
- 在导入 main 前设置 DB_DIR / DB_NAME
- 通过 _login_demo 等辅助函数获取 JWT token
- 使用 Authorization: Bearer {token} 头访问需认证端点
"""

import os
import sys
import time
import uuid

# 必须在导入 main 之前设置测试数据库路径
os.environ["DB_DIR"] = "/tmp/v11-test"
os.environ["DB_NAME"] = "test.db"
os.environ.setdefault("TESTING", "1")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import jwt  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from main import app, settings  # noqa: E402

client = TestClient(app)


# ---------- 辅助函数 ----------


def _login_demo() -> str:
    """登录 demo 账号（不存在则自动注册），返回 JWT token。"""
    login = client.post("/api/login", json={"username": "demo", "password": "demo123"})
    if login.status_code != 200:
        client.post(
            "/api/register",
            json={"username": "demo", "password": "demo123", "email": "demo@example.com"},
        )
        login = client.post("/api/login", json={"username": "demo", "password": "demo123"})
    assert login.status_code == 200, f"Login failed: {login.text}"
    return login.json()["token"]


def _register_unique(prefix: str = "u") -> tuple[str, int, str]:
    """注册一个独立用户（避免影响 demo 账号），返回 (username, user_id, token)。"""
    name = f"{prefix}_{uuid.uuid4().hex[:8]}"
    email = f"{name}@example.com"
    reg = client.post(
        "/api/register",
        json={"username": name, "password": "pass1234", "email": email},
    )
    assert reg.status_code == 200, f"Register failed: {reg.text}"
    body = reg.json()
    return name, int(body["user_id"]), body["token"]


def _login(username: str, password: str = "pass1234") -> str:
    """登录指定用户，返回 token。"""
    resp = client.post("/api/login", json={"username": username, "password": password})
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return resp.json()["token"]


def _get_first_plan_id() -> int:
    """获取第一个可用套餐 ID（测试库中套餐 ID 不固定）。"""
    resp = client.get("/api/billing/plans")
    assert resp.status_code == 200
    plans = resp.json()["data"]["plans"]
    assert len(plans) > 0, "No billing plans available"
    return plans[0]["id"]


def _make_admin() -> tuple[str, int]:
    """注册用户并创建团队（成为 admin），重新登录获取含 admin 角色的 token。

    返回 (admin_token, user_id)。
    """
    name, user_id, _ = _register_unique(prefix="adm")
    token = _login(name)
    resp = client.post("/api/team/create", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200, f"Team create failed: {resp.text}"
    # 重新登录：login 从数据库读取最新 role=admin，新 token 携带 admin 角色
    admin_token = _login(name)
    return admin_token, user_id


def _make_team_with_member() -> tuple[str, int, str, int]:
    """创建一个 admin 团队并让一个新成员加入。

    返回 (admin_token, admin_id, member_token, member_id)。
    """
    admin_token, admin_id = _make_admin()
    mname, member_id, _ = _register_unique(prefix="mem")
    member_token = _login(mname)
    resp = client.post(
        "/api/team/join",
        json={"team_id": admin_id},
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert resp.status_code == 200, f"Team join failed: {resp.text}"
    return admin_token, admin_id, member_token, member_id


def _token_with_email(user_id: int, username: str, email: str, role: str = "member") -> str:
    """构造包含 email 字段的 JWT。

    默认 login/register 返回的 token 不含 email，而 /api/auth/resend-verification
    依赖 token 中的 email 查找用户，故此处手动构造含 email 的 token 以测试正常路径。
    """
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "team_id": 0,
        "email": email,
        "exp": time.time() + settings.jwt_expire_seconds,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


# ===========================================================================
# auth.py —— 注册、登录、邮箱验证、密码重置
# ===========================================================================


def test_register_creates_user_and_returns_token():
    """注册新用户成功，返回 token 与用户信息。"""
    name = f"reg_{uuid.uuid4().hex[:8]}"
    resp = client.post(
        "/api/register",
        json={"username": name, "password": "pass1234", "email": f"{name}@example.com"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["success"] is True
    assert body["token"]
    assert body["username"] == name
    assert body["user_id"]
    assert body["role"] == "member"


def test_register_duplicate_username_returns_400():
    """重复用户名注册返回 400 业务错误。"""
    name = f"dup_{uuid.uuid4().hex[:8]}"
    client.post(
        "/api/register",
        json={"username": name, "password": "pass1234", "email": f"{name}@example.com"},
    )
    resp = client.post(
        "/api/register",
        json={"username": name, "password": "pass1234", "email": f"{name}@example.com"},
    )
    assert resp.status_code == 400
    assert resp.json()["error"] == "用户名已存在"


def test_register_short_password_returns_422():
    """密码过短返回 422 校验错误。"""
    name = f"sp_{uuid.uuid4().hex[:8]}"
    resp = client.post(
        "/api/register",
        json={"username": name, "password": "123", "email": f"{name}@example.com"},
    )
    assert resp.status_code == 422


def test_register_short_username_returns_422():
    """用户名过短返回 422 校验错误。"""
    resp = client.post(
        "/api/register",
        json={"username": "ab", "password": "pass1234", "email": "ab@example.com"},
    )
    assert resp.status_code == 422


def test_register_missing_password_returns_422():
    """缺少必填字段 password 返回 422。"""
    resp = client.post("/api/register", json={"username": f"miss_{uuid.uuid4().hex[:8]}"})
    assert resp.status_code == 422


def test_login_returns_token():
    """登录成功返回 token。"""
    name, _, _ = _register_unique(prefix="login")
    resp = client.post("/api/login", json={"username": name, "password": "pass1234"})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["success"] is True
    assert body["token"]
    assert body["username"] == name


def test_auth_challenge_returns_question_and_token():
    """验证码接口返回题目和一次性令牌。"""
    resp = client.get("/api/auth/challenge")
    assert resp.status_code == 200, resp.text
    data = resp.json()["data"]
    assert data["question"]
    assert data["token"]
    payload = jwt.decode(data["token"], settings.jwt_secret, algorithms=["HS256"])
    assert 0 < payload["exp"] - time.time() <= 30


def test_login_wrong_password_returns_401():
    """密码错误返回 401。"""
    name, _, _ = _register_unique(prefix="wp")
    resp = client.post("/api/login", json={"username": name, "password": "wrongpassword"})
    assert resp.status_code == 401
    assert resp.json()["error"] == "用户名或密码错误"


def test_login_nonexistent_user_returns_401():
    """不存在的用户登录返回 401。"""
    resp = client.post(
        "/api/login",
        json={"username": f"noexist_{uuid.uuid4().hex[:8]}", "password": "pass1234"},
    )
    assert resp.status_code == 401
    assert resp.json()["error"] == "用户名或密码错误"


def test_login_missing_fields_returns_422():
    """登录缺少必填字段返回 422。"""
    resp = client.post("/api/login", json={"username": "someone"})
    assert resp.status_code == 422


def test_verify_email_success():
    """使用有效 token 验证邮箱成功。"""
    from app.services.user_lifecycle import generate_email_verification_token

    _, user_id, _ = _register_unique(prefix="ve")
    token = generate_email_verification_token(user_id)
    resp = client.post(f"/api/auth/verify-email?token={token}")
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"]["success"] is True


def test_verify_email_invalid_token_returns_400():
    """无效的验证 token 返回 400。"""
    resp = client.post("/api/auth/verify-email?token=invalid-token-xxx")
    assert resp.status_code == 400
    assert resp.json()["error"] == "验证链接无效或不存在"


def test_verify_email_reuse_token_returns_400():
    """重复使用验证 token 返回 400。"""
    from app.services.user_lifecycle import generate_email_verification_token

    _, user_id, _ = _register_unique(prefix="vr")
    token = generate_email_verification_token(user_id)
    first = client.post(f"/api/auth/verify-email?token={token}")
    assert first.status_code == 200
    second = client.post(f"/api/auth/verify-email?token={token}")
    assert second.status_code == 400


def test_resend_verification_requires_login():
    """未登录调用重发验证邮件返回 401。"""
    resp = client.post("/api/auth/resend-verification")
    assert resp.status_code == 401


def test_resend_verification_sends_email():
    """登录后（token 含 email）重发验证邮件返回 200。

    JWT 默认不含 email 字段，此处构造含 email 的 token 以测试正常路径。
    SMTP 未配置时 sent=False，但仍返回 200。
    """
    name, user_id, _ = _register_unique(prefix="rv")
    email = f"{name}@example.com"
    token = _token_with_email(user_id, name, email)
    resp = client.post(
        "/api/auth/resend-verification", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()["data"]
    assert "sent" in data


def test_password_reset_request_returns_generic_message():
    """密码重置请求对未知邮箱也返回通用成功消息（不泄露邮箱是否存在）。"""
    resp = client.post(
        "/api/auth/password-reset/request",
        json={"email": f"nobody_{uuid.uuid4().hex[:8]}@example.com"},
    )
    assert resp.status_code == 200
    assert resp.json()["success"] is True


def test_password_reset_request_missing_email_returns_422():
    """密码重置请求缺少 email 字段返回 422。"""
    resp = client.post("/api/auth/password-reset/request", json={})
    assert resp.status_code == 422


def test_password_reset_confirm_success():
    """使用有效 token 重置密码成功，之后可用新密码登录。"""
    from app.services.user_lifecycle import generate_password_reset_token

    name, user_id, _ = _register_unique(prefix="pr")
    token = generate_password_reset_token(user_id)
    resp = client.post(
        "/api/auth/password-reset/confirm",
        json={"token": token, "new_password": "brandnew123"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"]["success"] is True
    # 用新密码登录验证
    login = client.post("/api/login", json={"username": name, "password": "brandnew123"})
    assert login.status_code == 200


def test_password_reset_confirm_invalid_token_returns_400():
    """无效的重置 token 返回 400。"""
    resp = client.post(
        "/api/auth/password-reset/confirm",
        json={"token": "bad-token", "new_password": "newpass123"},
    )
    assert resp.status_code == 400
    assert resp.json()["error"] == "密码重置链接无效或不存在"


def test_password_reset_confirm_short_password_returns_422():
    """新密码过短返回 422 校验错误。"""
    resp = client.post(
        "/api/auth/password-reset/confirm",
        json={"token": "some-token", "new_password": "123"},
    )
    assert resp.status_code == 422


# ===========================================================================
# user.py —— 当前用户信息、积分余额
# ===========================================================================


def test_get_me_returns_current_user():
    """GET /api/me 返回当前登录用户信息。"""
    name, user_id, token = _register_unique(prefix="me")
    resp = client.get("/api/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["user_id"] == user_id
    assert body["username"] == name
    assert body["role"] == "member"
    assert "credits" in body


def test_get_me_requires_login():
    """未登录访问 /api/me 返回 401。"""
    resp = client.get("/api/me")
    assert resp.status_code == 401


def test_get_me_invalid_token_returns_401():
    """无效 token 访问 /api/me 返回 401。"""
    resp = client.get("/api/me", headers={"Authorization": "Bearer invalidtoken"})
    assert resp.status_code == 401


def test_get_me_credits_returns_balance():
    """GET /api/me/credits 返回积分余额。"""
    _, _, token = _register_unique(prefix="cr")
    resp = client.get("/api/me/credits", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"]["credits"] >= 0


def test_get_me_credits_requires_login():
    """未登录访问 /api/me/credits 返回 401。"""
    resp = client.get("/api/me/credits")
    assert resp.status_code == 401


def test_get_me_credits_invalid_token_returns_401():
    """无效 token 访问 /api/me/credits 返回 401。"""
    resp = client.get("/api/me/credits", headers={"Authorization": "Bearer bad"})
    assert resp.status_code == 401


# ===========================================================================
# billing.py —— 套餐、购买、充值记录、订单、支付回调
# ===========================================================================


def test_get_billing_plans_returns_list():
    """GET /api/billing/plans 返回套餐列表。"""
    resp = client.get("/api/billing/plans")
    assert resp.status_code == 200
    plans = resp.json()["data"]["plans"]
    assert len(plans) >= 1
    assert all(
        k in plans[0] for k in ("id", "name", "credits", "price_cents", "currency")
    )


def test_purchase_plan_increases_credits():
    """购买套餐后积分增加。"""
    _, _, token = _register_unique(prefix="buy")
    headers = {"Authorization": f"Bearer {token}"}
    plan = client.get("/api/billing/plans").json()["data"]["plans"][0]
    before = client.get("/api/me/credits", headers=headers).json()["data"]["credits"]
    resp = client.post(
        "/api/billing/purchase", json={"plan_id": plan["id"]}, headers=headers
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"]["credits_added"] == plan["credits"]
    after = client.get("/api/me/credits", headers=headers).json()["data"]["credits"]
    assert after == before + plan["credits"]


def test_purchase_plan_requires_login():
    """未登录购买套餐返回 401。"""
    resp = client.post("/api/billing/purchase", json={"plan_id": 1})
    assert resp.status_code == 401


def test_purchase_nonexistent_plan_returns_404():
    """购买不存在的套餐返回 404。"""
    _, _, token = _register_unique(prefix="pnp")
    resp = client.post(
        "/api/billing/purchase",
        json={"plan_id": 99999},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404
    assert resp.json()["error"] == "套餐不存在或已下架"


def test_purchase_invalid_plan_id_returns_422():
    """plan_id 非整数返回 422。"""
    token = _login_demo()
    resp = client.post(
        "/api/billing/purchase",
        json={"plan_id": "abc"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422


def test_get_recharges_requires_login():
    """未登录获取充值记录返回 401。"""
    resp = client.get("/api/billing/recharges")
    assert resp.status_code == 401


def test_get_recharges_returns_records():
    """购买后充值记录可见。"""
    _, _, token = _register_unique(prefix="rc")
    headers = {"Authorization": f"Bearer {token}"}
    plan = client.get("/api/billing/plans").json()["data"]["plans"][0]
    client.post("/api/billing/purchase", json={"plan_id": plan["id"]}, headers=headers)
    resp = client.get("/api/billing/recharges", headers=headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total"] >= 1
    assert len(data["records"]) >= 1


def test_admin_recharge_requires_login():
    """未登录调用管理员充值返回 401。"""
    resp = client.post(
        "/api/admin/recharge", json={"user_id": 1, "credits": 10, "note": "x"}
    )
    assert resp.status_code == 401


def test_admin_recharge_requires_admin():
    """非管理员调用管理员充值返回 403。"""
    _, _, token = _register_unique(prefix="na")
    resp = client.post(
        "/api/admin/recharge",
        json={"user_id": 1, "credits": 10, "note": "x"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403
    assert resp.json()["error"] == "权限不足"


def test_admin_recharge_success():
    """管理员充值成功，目标用户积分增加。"""
    admin_token, _ = _make_admin()
    _, target_id, target_token = _register_unique(prefix="tg")
    before = client.get(
        "/api/me/credits", headers={"Authorization": f"Bearer {target_token}"}
    ).json()["data"]["credits"]
    resp = client.post(
        "/api/admin/recharge",
        json={"user_id": target_id, "credits": 20, "note": "test recharge"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"]["credits_added"] == 20
    after = client.get(
        "/api/me/credits", headers={"Authorization": f"Bearer {target_token}"}
    ).json()["data"]["credits"]
    assert after == before + 20


def test_create_order_mock_paid():
    """创建 mock 订单直接到账。"""
    _, _, token = _register_unique(prefix="ord")
    headers = {"Authorization": f"Bearer {token}"}
    plan = client.get("/api/billing/plans").json()["data"]["plans"][0]
    before = client.get("/api/me/credits", headers=headers).json()["data"]["credits"]
    resp = client.post(
        "/api/billing/order",
        json={"plan_id": plan["id"], "provider": "mock"},
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()["data"]
    assert data["provider"] == "mock"
    assert data["status"] == "paid"
    assert data["credits_added"] == plan["credits"]
    after = client.get("/api/me/credits", headers=headers).json()["data"]["credits"]
    assert after == before + plan["credits"]


def test_create_order_requires_login():
    """未登录创建订单返回 401。"""
    resp = client.post("/api/billing/order", json={"plan_id": 1, "provider": "mock"})
    assert resp.status_code == 401


def test_create_order_invalid_provider_returns_422():
    """不支持的支付渠道返回 422 校验错误。"""
    token = _login_demo()
    resp = client.post(
        "/api/billing/order",
        json={"plan_id": 1, "provider": "paypal"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422


def test_get_order_status_success():
    """查询自己的订单状态成功。"""
    _, _, token = _register_unique(prefix="os")
    headers = {"Authorization": f"Bearer {token}"}
    plan_id = _get_first_plan_id()
    order = client.post(
        "/api/billing/order", json={"plan_id": plan_id, "provider": "mock"}, headers=headers
    ).json()["data"]
    tx = order["transaction_id"]
    resp = client.get(f"/api/billing/order/{tx}", headers=headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()["data"]
    assert data["transaction_id"] == tx
    assert data["status"] == "paid"


def test_get_order_status_not_found_returns_404():
    """查询不存在的订单返回 404。"""
    token = _login_demo()
    resp = client.get(
        "/api/billing/order/NOTEXIST", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 404
    assert resp.json()["error"] == "订单不存在"


def test_get_order_status_requires_login():
    """未登录查询订单返回 401。"""
    resp = client.get("/api/billing/order/some-tx")
    assert resp.status_code == 401


def test_get_order_status_requires_owner():
    """普通用户不能查看他人订单，返回 403。"""
    _, _, owner_token = _register_unique(prefix="ow")
    headers = {"Authorization": f"Bearer {owner_token}"}
    plan_id = _get_first_plan_id()
    order = client.post(
        "/api/billing/order", json={"plan_id": plan_id, "provider": "mock"}, headers=headers
    ).json()["data"]
    tx = order["transaction_id"]
    _, _, other_token = _register_unique(prefix="oo")
    resp = client.get(
        f"/api/billing/order/{tx}",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert resp.status_code == 403


def test_alipay_webhook_not_configured_returns_501():
    """未配置支付宝时回调返回 501。"""
    resp = client.post("/api/billing/webhook/alipay", json={})
    assert resp.status_code == 501


def test_wechat_webhook_not_configured_returns_501():
    """未配置微信支付时回调返回 501。"""
    resp = client.post("/api/billing/webhook/wechat", json={})
    assert resp.status_code == 501


def test_stripe_webhook_no_secret_returns_400():
    """未配置 STRIPE_WEBHOOK_SECRET 时 stripe 回调返回 400。"""
    resp = client.post("/api/billing/webhook/stripe", json={})
    assert resp.status_code == 400
    assert "STRIPE_WEBHOOK_SECRET" in resp.json()["error"]


def test_webhook_unknown_provider_returns_400():
    """不支持的支付渠道回调返回 400。"""
    resp = client.post("/api/billing/webhook/paypal", json={})
    assert resp.status_code == 400
    assert "paypal" in resp.json()["error"]


def test_alipay_webhook_mock_fulfills_order():
    """ALIPAY_MOCK=true 时支付宝回调可幂等完成订单。"""
    os.environ["ALIPAY_MOCK"] = "true"
    try:
        _, _, token = _register_unique(prefix="wh")
        headers = {"Authorization": f"Bearer {token}"}
        plan_id = _get_first_plan_id()
        order = client.post(
            "/api/billing/order",
            json={"plan_id": plan_id, "provider": "mock"},
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


# ===========================================================================
# gdpr.py —— 数据导出、账号删除、匿名化
# ===========================================================================


def test_export_requires_login():
    """未登录导出数据返回 401。"""
    resp = client.get("/api/me/export")
    assert resp.status_code == 401


def test_export_returns_user_data():
    """导出数据包含用户基本信息（排除密码）及各数据类别。"""
    token = _login_demo()
    resp = client.get("/api/me/export", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200, resp.text
    data = resp.json()["data"]
    assert data["user"] is not None
    assert "password" not in data["user"]
    for key in (
        "scans",
        "recharge_records",
        "usage_logs",
        "audit_logs",
        "fix_tickets",
        "finding_feedback",
    ):
        assert key in data


def test_delete_account_requires_login():
    """未登录删除账号返回 401。"""
    resp = client.delete("/api/me/account?confirm=DELETE")
    assert resp.status_code == 401


def test_delete_account_requires_confirm():
    """删除账号必须传 confirm=DELETE 确认参数。"""
    _, _, token = _register_unique(prefix="del")
    resp = client.delete("/api/me/account", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 400
    err = resp.json().get("error", "")
    assert "DELETE" in err or "确认" in err


def test_delete_account_with_confirm():
    """确认后删除账号及关联数据，无法再登录。"""
    name, _, token = _register_unique(prefix="gone")
    resp = client.delete(
        "/api/me/account?confirm=DELETE", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200, resp.text
    result = resp.json()["data"]
    assert result["success"] is True
    assert "users" in result["deleted_tables"]
    # 删除后无法再登录
    login = client.post("/api/login", json={"username": name, "password": "pass1234"})
    assert login.status_code != 200


def test_anonymize_requires_login():
    """未登录匿名化返回 401。"""
    resp = client.post("/api/me/anonymize")
    assert resp.status_code == 401


def test_anonymize_user_data():
    """匿名化后用户名变为 deleted_user_{id}，邮箱与密码清空。"""
    from app.db.session import get_db

    _, user_id, token = _register_unique(prefix="an")
    resp = client.post("/api/me/anonymize", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"]["success"] is True
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


# ===========================================================================
# team.py —— 团队成员查询、创建、加入、角色修改
# ===========================================================================


def test_get_team_requires_login():
    """未登录获取团队成员返回 401。"""
    resp = client.get("/api/team")
    assert resp.status_code == 401


def test_get_team_without_team_returns_self():
    """无团队时返回自己作为唯一成员。"""
    _, _, token = _register_unique(prefix="nt")
    resp = client.get("/api/team", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["team_id"] == 0
    assert len(body["members"]) == 1


def test_get_team_with_team_returns_members():
    """有团队时返回全部成员列表。"""
    admin_token, admin_id, _, member_id = _make_team_with_member()
    resp = client.get("/api/team", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["team_id"] == admin_id
    member_ids = [m["user_id"] for m in body["members"]]
    assert admin_id in member_ids
    assert member_id in member_ids


def test_team_create_success():
    """创建团队成功，当前用户成为 admin。"""
    name, user_id, token = _register_unique(prefix="tc")
    resp = client.post("/api/team/create", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["success"] is True
    assert body["team_id"] == user_id
    # 重新登录后 role 应为 admin
    new_token = _login(name)
    me = client.get("/api/me", headers={"Authorization": f"Bearer {new_token}"})
    assert me.json()["role"] == "admin"


def test_team_create_requires_login():
    """未登录创建团队返回 401。"""
    resp = client.post("/api/team/create")
    assert resp.status_code == 401


def test_team_create_already_in_team_returns_400():
    """已加入团队再次创建返回 400。"""
    admin_token, _ = _make_admin()  # 该用户已创建团队
    resp = client.post(
        "/api/team/create", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 400
    assert "团队" in resp.json()["error"]


def test_team_join_success():
    """加入团队成功。"""
    admin_token, admin_id = _make_admin()
    _, _, member_token = _register_unique(prefix="jn")
    resp = client.post(
        "/api/team/join",
        json={"team_id": admin_id},
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["success"] is True
    assert body["team_id"] == admin_id


def test_team_join_requires_login():
    """未登录加入团队返回 401。"""
    resp = client.post("/api/team/join", json={"team_id": 1})
    assert resp.status_code == 401


def test_team_join_nonexistent_team_returns_404():
    """加入不存在的团队返回 404。"""
    _, _, token = _register_unique(prefix="nj")
    resp = client.post(
        "/api/team/join",
        json={"team_id": 999999},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404
    assert resp.json()["error"] == "团队不存在"


def test_team_join_invalid_team_id_returns_400():
    """team_id 非整数返回 400 业务错误。"""
    _, _, token = _register_unique(prefix="ij")
    resp = client.post(
        "/api/team/join",
        json={"team_id": "abc"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400
    assert resp.json()["error"] == "team_id 必须是整数"


def test_team_set_role_success():
    """管理员修改团队成员角色成功。"""
    admin_token, _, _, member_id = _make_team_with_member()
    resp = client.post(
        f"/api/team/{member_id}/role",
        json={"role": "viewer"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["success"] is True


def test_team_set_role_requires_login():
    """未登录修改角色返回 401。"""
    resp = client.post("/api/team/1/role", json={"role": "member"})
    assert resp.status_code == 401


def test_team_set_role_non_admin_returns_403():
    """非管理员修改角色返回 403。"""
    _, _, member_token = _register_unique(prefix="nr")
    resp = client.post(
        "/api/team/1/role",
        json={"role": "member"},
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert resp.status_code == 403
    assert resp.json()["error"] == "仅团队管理员可修改角色"


def test_team_set_role_invalid_role_returns_400():
    """无效角色返回 400 业务错误。"""
    admin_token, _, _, member_id = _make_team_with_member()
    resp = client.post(
        f"/api/team/{member_id}/role",
        json={"role": "superadmin"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 400
    assert resp.json()["error"] == "角色必须是 admin / member / viewer"


def test_team_set_role_target_not_in_team_returns_404():
    """目标用户不在团队中返回 404。"""
    admin_token, _, _, _ = _make_team_with_member()
    _, outsider_id, _ = _register_unique(prefix="out")
    resp = client.post(
        f"/api/team/{outsider_id}/role",
        json={"role": "member"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 404
    assert resp.json()["error"] == "目标用户不在你的团队中"


# ===========================================================================
# admin.py —— 审计日志查询
# ===========================================================================


def test_admin_audit_logs_requires_login():
    """未登录查询审计日志返回 401。"""
    resp = client.get("/api/admin/audit-logs")
    assert resp.status_code == 401


def test_admin_audit_logs_requires_admin():
    """非管理员查询审计日志返回 403。"""
    _, _, token = _register_unique(prefix="al")
    resp = client.get(
        "/api/admin/audit-logs", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 403
    assert resp.json()["error"] == "仅管理员可查询审计日志"


def test_admin_audit_logs_returns_logs():
    """管理员查询审计日志成功，返回日志列表。"""
    admin_token, _ = _make_admin()
    resp = client.get(
        "/api/admin/audit-logs", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()["data"]
    assert "logs" in data
    assert isinstance(data["logs"], list)


def test_admin_audit_logs_with_filters():
    """管理员可使用 limit/offset/action 过滤参数。"""
    admin_token, _ = _make_admin()
    resp = client.get(
        "/api/admin/audit-logs?limit=5&offset=0&action=post_team",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()["data"]
    assert data["limit"] == 5
    assert data["offset"] == 0


def test_admin_audit_logs_invalid_limit_returns_422():
    """limit 超出范围返回 422 校验错误。"""
    admin_token, _ = _make_admin()
    resp = client.get(
        "/api/admin/audit-logs?limit=99999",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 422


def test_admin_email_logs_requires_admin():
    """非管理员不能查看邮件投递日志。"""
    _, _, token = _register_unique(prefix="el")
    resp = client.get(
        "/api/admin/email-logs", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 403


def test_admin_email_logs_returns_logs():
    """管理员可以查看邮件投递状态，且接口返回日志列表。"""
    admin_token, _ = _make_admin()
    resp = client.get(
        "/api/admin/email-logs", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()["data"]
    assert "logs" in data
    assert isinstance(data["logs"], list)
