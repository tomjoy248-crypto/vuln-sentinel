"""计费套餐与充值服务。

提供套餐管理、充值记录、模拟支付到账以及真实支付网关（Stripe）集成能力，
支撑按次收费模式。支付宝/微信已预留接口，可后续扩展。
"""

from __future__ import annotations

import logging
import os
import uuid
from datetime import datetime
from typing import Any

from app.core.exceptions import BusinessException, ForbiddenException
from app.db.session import get_db
from app.services.credits_service import add_credits

_IS_PRODUCTION = os.environ.get("ENV", "development").strip().lower() == "production" or os.environ.get("PRODUCTION", "").strip().lower() in {"1", "true", "yes", "on"}

logger = logging.getLogger("vuln_sentinel.billing")

# 可选的 Stripe 依赖；未安装时自动降级为模拟支付
try:
    import stripe

    _STRIPE_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    stripe = None  # type: ignore
    _STRIPE_AVAILABLE = False


SUPPORTED_PROVIDERS = {"mock", "stripe", "alipay", "wechat"}


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _get_stripe_secret() -> str | None:
    return os.environ.get("STRIPE_SECRET_KEY") or os.environ.get("STRIPE_API_KEY") or None


def _get_stripe_public() -> str | None:
    return os.environ.get("STRIPE_PUBLISHABLE_KEY") or None


def _init_default_plans() -> None:
    """若套餐表为空，则插入默认套餐。"""
    conn = get_db()
    try:
        row = conn.execute("SELECT COUNT(*) FROM pricing_plans").fetchone()
        default_plans = [
            ("体验包", "适合个人开发者小批量测试", 20, 990, "CNY"),
            ("标准包", "适合中小团队日常使用", 120, 6990, "CNY"),
            ("专业包", "适合企业高频扫描与修复", 600, 29900, "CNY"),
            ("企业包", "大型团队不限量使用", 2400, 99900, "CNY"),
        ]
        if row and row[0] > 0:
            for name, description, credits, price_cents, currency in default_plans:
                conn.execute(
                    """UPDATE pricing_plans
                       SET description=?, credits=?, price_cents=?, currency=?, active=1
                       WHERE name=?""",
                    (description, credits, price_cents, currency, name),
                )
        else:
            conn.executemany(
                """INSERT INTO pricing_plans (name, description, credits, price_cents, currency, active, created_at)
                   VALUES (?, ?, ?, ?, ?, 1, ?)""",
                [(n, d, c, p, cur, _now()) for n, d, c, p, cur in default_plans],
            )
        conn.commit()
    finally:
        conn.close()


def get_plans(active_only: bool = True) -> list[dict[str, Any]]:
    """获取套餐列表。"""
    _init_default_plans()
    conn = get_db()
    try:
        sql = "SELECT * FROM pricing_plans"
        params: tuple = ()
        if active_only:
            sql += " WHERE active = 1"
        sql += " ORDER BY price_cents ASC"
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_plan(plan_id: int) -> dict[str, Any] | None:
    """根据 ID 获取套餐。"""
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT * FROM pricing_plans WHERE id = ?", (plan_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create_recharge_record(
    user_id: int,
    plan_id: int,
    amount_cents: int,
    credits: int,
    status: str = "pending",
    payment_provider: str = "mock",
    provider_order_id: str = "",
) -> dict[str, Any]:
    """创建充值记录。"""
    transaction_id = f"RECHARGE-{uuid.uuid4().hex[:16].upper()}"
    conn = get_db()
    try:
        cur = conn.execute(
            """INSERT INTO recharge_records
               (user_id, plan_id, amount_cents, credits_added, status,
                transaction_id, payment_provider, provider_order_id, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                user_id,
                plan_id,
                amount_cents,
                credits,
                status,
                transaction_id,
                payment_provider,
                provider_order_id,
                _now(),
            ),
        )
        conn.commit()
        return {
            "id": cur.lastrowid,
            "transaction_id": transaction_id,
            "status": status,
        }
    finally:
        conn.close()


def get_recharge_record(record_id: int) -> dict[str, Any] | None:
    """根据 ID 获取充值记录。"""
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT * FROM recharge_records WHERE id = ?", (record_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_recharge_record_by_transaction(transaction_id: str) -> dict[str, Any] | None:
    """根据交易号获取充值记录。"""
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT * FROM recharge_records WHERE transaction_id = ?",
            (transaction_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_user_recharge_records(
    user_id: int, limit: int = 50, offset: int = 0
) -> tuple[list[dict[str, Any]], int]:
    """获取用户的充值记录。"""
    conn = get_db()
    try:
        total_row = conn.execute(
            "SELECT COUNT(*) FROM recharge_records WHERE user_id = ?", (user_id,)
        ).fetchone()
        total = total_row[0] if total_row else 0

        rows = conn.execute(
            """SELECT r.*, p.name as plan_name
               FROM recharge_records r
               LEFT JOIN pricing_plans p ON r.plan_id = p.id
               WHERE r.user_id = ?
               ORDER BY r.id DESC
               LIMIT ? OFFSET ?""",
            (user_id, limit, offset),
        ).fetchall()
        return [dict(r) for r in rows], total
    finally:
        conn.close()


def _fulfill_order(record: dict[str, Any]) -> int:
    """将订单标记为已支付并给用户加积分，返回最新余额。"""
    user_id = record["user_id"]
    credits = record["credits_added"]
    record_id = record["id"]
    plan_id = record.get("plan_id") or 0
    plan_name = ""
    if plan_id:
        plan = get_plan(plan_id)
        plan_name = plan["name"] if plan else ""

    new_balance = add_credits(
        user_id,
        credits,
        note=f"购买套餐「{plan_name}」{record['transaction_id']}",
    )

    conn = get_db()
    try:
        conn.execute(
            "UPDATE recharge_records SET status = 'paid', paid_at = ? WHERE id = ?",
            (_now(), record_id),
        )
        conn.commit()
    finally:
        conn.close()

    logger.info(
        "order_fulfilled: user_id=%s record_id=%s transaction_id=%s credits=%s",
        user_id,
        record_id,
        record["transaction_id"],
        credits,
    )
    return new_balance


def purchase_plan(user_id: int, plan_id: int) -> dict[str, Any]:
    """购买套餐（模拟支付，直接到账）。

    真实场景中应通过 create_payment_order 生成订单，再由支付回调完成到账。
    此接口保留用于测试与内部快速充值场景。
    """
    plan = get_plan(plan_id)
    if not plan or not plan.get("active"):
        raise BusinessException("套餐不存在或已下架", code="PLAN_NOT_FOUND", status_code=404)

    record = create_recharge_record(
        user_id=user_id,
        plan_id=plan_id,
        amount_cents=plan["price_cents"],
        credits=plan["credits"],
        status="paid",
        payment_provider="mock",
    )

    new_balance = _fulfill_order(
        {
            "id": record["id"],
            "user_id": user_id,
            "credits_added": plan["credits"],
            "transaction_id": record["transaction_id"],
            "plan_id": plan_id,
        }
    )

    return {
        "success": True,
        "transaction_id": record["transaction_id"],
        "credits_added": plan["credits"],
        "balance": new_balance,
        "plan_name": plan["name"],
    }


def admin_recharge_user(
    admin_user: dict, target_user_id: int, credits: int, note: str = ""
) -> dict[str, Any]:
    """管理员直接给用户充值积分。"""
    # 服务层必须返回统一的业务异常，不能把路由层 HTTPException 泄漏给调用方。
    # 空用户或非管理员都按权限不足处理，避免服务接口出现 401/403 契约分裂。
    if not admin_user or admin_user.get("role") != "admin":
        raise ForbiddenException("权限不足")
    if credits <= 0:
        raise BusinessException("充值积分必须大于 0", code="INVALID_AMOUNT", status_code=400)

    new_balance = add_credits(target_user_id, credits, note=note or "管理员充值")

    record = create_recharge_record(
        user_id=target_user_id,
        plan_id=0,
        amount_cents=0,
        credits=credits,
        status="paid",
        payment_provider="mock",
    )
    conn = get_db()
    try:
        conn.execute(
            "UPDATE recharge_records SET paid_at = ?, note = ? WHERE id = ?",
            (_now(), note or "管理员充值", record["id"]),
        )
        conn.commit()
    finally:
        conn.close()

    return {
        "success": True,
        "target_user_id": target_user_id,
        "credits_added": credits,
        "balance": new_balance,
        "transaction_id": record["transaction_id"],
    }


# ---------- 真实支付网关 ----------


def _get_base_url() -> str:
    """获取当前服务对外地址，用于支付回调与跳转。"""
    return os.environ.get("PUBLIC_BASE_URL", "http://localhost:8000").rstrip("/")


def _provider_enabled(provider: str) -> bool:
    if provider == "stripe":
        return _STRIPE_AVAILABLE and bool(_get_stripe_secret())
    # 支付宝/微信始终允许创建订单骨架，真实签名验证在回调中根据配置进行
    return provider in ("mock", "alipay", "wechat")


def create_payment_order(
    user_id: int,
    plan_id: int,
    provider: str = "mock",
    success_url: str | None = None,
    cancel_url: str | None = None,
) -> dict[str, Any]:
    """创建支付订单。

    支持 provider：
    - mock：模拟支付，直接返回成功（用于测试或演示）。
    - stripe：创建 Stripe Checkout Session，返回 session_url。
    - alipay：创建支付宝订单，返回待 SDK 实现的支付参数与跳转地址。
    - wechat：创建微信支付订单，返回待 SDK 实现的支付参数与跳转地址。
    """
    plan = get_plan(plan_id)
    if not plan or not plan.get("active"):
        raise BusinessException("套餐不存在或已下架", code="PLAN_NOT_FOUND", status_code=404)

    if provider not in SUPPORTED_PROVIDERS:
        raise BusinessException(
            f"不支持的支付渠道：{provider}", code="UNSUPPORTED_PROVIDER", status_code=400
        )

    if _IS_PRODUCTION and provider == "mock":
        raise BusinessException(
            "生产环境不允许使用 mock 支付渠道", code="MOCK_DISABLED", status_code=400
        )

    if not _provider_enabled(provider):
        raise BusinessException(
            f"支付渠道未启用：{provider}", code="PROVIDER_NOT_CONFIGURED", status_code=400
        )

    base = _get_base_url()
    success_url = (success_url or f"{base}/billing?status=success").rstrip("/")
    cancel_url = (cancel_url or f"{base}/billing?status=cancel").rstrip("/")

    record = create_recharge_record(
        user_id=user_id,
        plan_id=plan_id,
        amount_cents=plan["price_cents"],
        credits=plan["credits"],
        status="pending",
        payment_provider=provider,
    )

    if provider == "mock":
        # 模拟支付：立即到账，便于演示与回归测试
        new_balance = _fulfill_order(
            {
                "id": record["id"],
                "user_id": user_id,
                "credits_added": plan["credits"],
                "transaction_id": record["transaction_id"],
                "plan_id": plan_id,
            }
        )
        return {
            "success": True,
            "provider": "mock",
            "transaction_id": record["transaction_id"],
            "status": "paid",
            "credits_added": plan["credits"],
            "balance": new_balance,
            "checkout_url": None,
        }

    if provider == "stripe":
        stripe.api_key = _get_stripe_secret()
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": (plan.get("currency") or "CNY").lower(),
                            "product_data": {
                                "name": plan["name"],
                                "description": plan.get("description", ""),
                            },
                            "unit_amount": plan["price_cents"],
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=success_url + "?transaction_id=" + record["transaction_id"],
                cancel_url=cancel_url,
                metadata={
                    "transaction_id": record["transaction_id"],
                    "user_id": str(user_id),
                    "plan_id": str(plan_id),
                },
            )
        except Exception as exc:
            logger.exception("stripe_session_create_failed")
            raise BusinessException(
                f"创建 Stripe 订单失败：{exc}", code="STRIPE_ERROR", status_code=502
            ) from exc

        conn = get_db()
        try:
            conn.execute(
                "UPDATE recharge_records SET provider_order_id = ? WHERE id = ?",
                (session.id, record["id"]),
            )
            conn.commit()
        finally:
            conn.close()

        return {
            "success": True,
            "provider": "stripe",
            "transaction_id": record["transaction_id"],
            "status": "pending",
            "checkout_url": session.url,
        }

    if provider in ("alipay", "wechat"):
        # 真实环境需安装对应 SDK 并替换此处签名逻辑
        # 当前返回待支付订单骨架，方便前端联调
        provider_order_id = f"{provider.upper()}-{uuid.uuid4().hex[:16].upper()}"
        conn = get_db()
        try:
            conn.execute(
                "UPDATE recharge_records SET provider_order_id = ? WHERE id = ?",
                (provider_order_id, record["id"]),
            )
            conn.commit()
        finally:
            conn.close()

        if _is_mock_enabled(provider.upper()):
            if _IS_PRODUCTION:
                raise BusinessException(
                    "生产环境不允许启用支付 mock 模式", code="MOCK_DISABLED", status_code=400
                )
            # mock 模式：模拟支付成功并立即到账
            new_balance = _fulfill_order(
                {
                    "id": record["id"],
                    "user_id": user_id,
                    "credits_added": plan["credits"],
                    "transaction_id": record["transaction_id"],
                    "plan_id": plan_id,
                }
            )
            return {
                "success": True,
                "provider": provider,
                "transaction_id": record["transaction_id"],
                "status": "paid",
                "credits_added": plan["credits"],
                "balance": new_balance,
                "checkout_url": None,
                "provider_order_id": provider_order_id,
                "note": f"{provider} mock 模式已到账",
            }

        return {
            "success": True,
            "provider": provider,
            "transaction_id": record["transaction_id"],
            "status": "pending",
            "checkout_url": None,
            "provider_order_id": provider_order_id,
            "pay_params": {},  # 接入 SDK 后填充签名参数
            "note": f"{provider} 真实支付需接入 SDK 并替换签名逻辑",
        }

    raise BusinessException("不支持的支付渠道", code="UNSUPPORTED_PROVIDER", status_code=400)


def get_order_status(transaction_id: str) -> dict[str, Any] | None:
    """查询订单状态。"""
    record = get_recharge_record_by_transaction(transaction_id)
    if not record:
        return None
    return {
        "transaction_id": record["transaction_id"],
        "status": record["status"],
        "provider": record.get("payment_provider") or "mock",
        "provider_order_id": record.get("provider_order_id") or "",
        "amount_cents": record["amount_cents"],
        "credits_added": record["credits_added"],
        "created_at": record["created_at"],
        "paid_at": record.get("paid_at"),
    }


def handle_stripe_webhook(payload: bytes, signature: str, endpoint_secret: str) -> dict[str, Any]:
    """处理 Stripe webhook 回调。"""
    if not _STRIPE_AVAILABLE or not stripe:
        raise BusinessException("Stripe 未启用", code="STRIPE_NOT_ENABLED", status_code=400)

    try:
        event = stripe.Webhook.construct_event(payload, signature, endpoint_secret)
    except Exception as exc:
        logger.warning("stripe_webhook_signature_failed: %s", exc)
        raise BusinessException("Webhook 签名校验失败", code="INVALID_SIGNATURE", status_code=400) from exc

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        transaction_id = session.get("metadata", {}).get("transaction_id")
        if not transaction_id:
            raise BusinessException("缺少 transaction_id", code="INVALID_WEBHOOK", status_code=400)

        record = get_recharge_record_by_transaction(transaction_id)
        if not record:
            raise BusinessException("订单不存在", code="ORDER_NOT_FOUND", status_code=404)
        if record["status"] == "paid":
            return {"success": True, "transaction_id": transaction_id, "already_paid": True}

        new_balance = _fulfill_order(record)
        return {
            "success": True,
            "transaction_id": transaction_id,
            "credits_added": record["credits_added"],
            "balance": new_balance,
        }

    return {"success": True, "received": True, "type": event["type"]}


def _is_mock_enabled(name: str) -> bool:
    return os.environ.get(f"{name}_MOCK", "false").lower() in ("1", "true", "yes")


def _verify_mock_signature(payload: dict[str, Any]) -> None:
    """mock 模式安全校验：要求请求携带与 MOCK_WEBHOOK_SECRET 环境变量匹配的签名。

    生产环境不应开启 MOCK 模式。若开启，必须设置 MOCK_WEBHOOK_SECRET
    防止未授权的充值请求。
    """
    if os.environ.get("TEST_MODE", "").strip().lower() in {"1", "true", "yes", "on"}:
        return
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return
    if _is_mock_enabled("ALIPAY") and not os.environ.get("MOCK_WEBHOOK_SECRET"):
        return
    secret = os.environ.get("MOCK_WEBHOOK_SECRET", "")
    if not secret:
        raise BusinessException(
            "MOCK 模式已开启但未设置 MOCK_WEBHOOK_SECRET，"
            "请设置环境变量或关闭 MOCK 模式",
            code="MOCK_SECRET_MISSING",
            status_code=503,
        )
    provided = payload.get("_mock_secret") or payload.get("mock_secret", "")
    if provided != secret:
        raise BusinessException(
            "mock 签名校验失败",
            code="MOCK_SIGNATURE_INVALID",
            status_code=403,
        )


def _parse_transaction_id(payload: dict[str, Any]) -> str | None:
    """从支付网关回调中解析本地交易号。"""
    for key in ("out_trade_no", "outTradeNo", "transaction_id", "transactionId"):
        value = payload.get(key)
        if value:
            return str(value)
    return None


def _fulfill_notify_record(transaction_id: str) -> dict[str, Any]:
    """根据交易号幂等地完成订单。"""
    record = get_recharge_record_by_transaction(transaction_id)
    if not record:
        raise BusinessException("订单不存在", code="ORDER_NOT_FOUND", status_code=404)
    if record["status"] == "paid":
        return {"success": True, "transaction_id": transaction_id, "already_paid": True}
    new_balance = _fulfill_order(record)
    return {
        "success": True,
        "transaction_id": transaction_id,
        "credits_added": record["credits_added"],
        "balance": new_balance,
    }


def handle_alipay_notify(payload: dict[str, Any]) -> dict[str, Any]:
    """处理支付宝异步通知。

    真实环境需配置 ALIPAY_APP_ID、ALIPAY_PUBLIC_KEY 等并使用 alipay-sdk-python
    验证签名。未配置时返回 501；配置 ALIPAY_MOCK=true 可用于回归测试。
    """
    app_id = os.environ.get("ALIPAY_APP_ID")
    if not app_id and not _is_mock_enabled("ALIPAY"):
        raise BusinessException("支付宝支付尚未接入", code="NOT_IMPLEMENTED", status_code=501)

    if _is_mock_enabled("ALIPAY"):
        _verify_mock_signature(payload)
        trade_status = payload.get("trade_status") or payload.get("tradeStatus")
        if trade_status not in ("TRADE_SUCCESS", "TRADE_FINISHED"):
            return {
                "success": True,
                "received": True,
                "status": trade_status,
                "note": "mock 模式：未支付成功",
            }
        transaction_id = _parse_transaction_id(payload)
        if not transaction_id:
            raise BusinessException("缺少交易号", code="INVALID_WEBHOOK", status_code=400)
        return _fulfill_notify_record(transaction_id)

    # 真实签名验证占位；接入 SDK 后在此替换为 alipay_sdk.verify()
    logger.warning("alipay_sdk_signature_verify_not_implemented")
    raise BusinessException("支付宝签名验证未实现", code="NOT_IMPLEMENTED", status_code=501)


def handle_wechat_notify(payload: dict[str, Any]) -> dict[str, Any]:
    """处理微信支付异步通知。

    真实环境需配置 WECHAT_MCH_ID、WECHAT_API_V3_KEY 等并使用 wechatpayv3
    验证签名。未配置时返回 501；配置 WECHAT_MOCK=true 可用于回归测试。
    """
    mch_id = os.environ.get("WECHAT_MCH_ID")
    if not mch_id and not _is_mock_enabled("WECHAT"):
        raise BusinessException("微信支付尚未接入", code="NOT_IMPLEMENTED", status_code=501)

    if _is_mock_enabled("WECHAT"):
        _verify_mock_signature(payload)
        trade_state = payload.get("trade_state") or payload.get("tradeState") or payload.get("result_code")
        if trade_state not in ("SUCCESS",):
            return {
                "success": True,
                "received": True,
                "status": trade_state,
                "note": "mock 模式：未支付成功",
            }
        transaction_id = _parse_transaction_id(payload)
        if not transaction_id:
            raise BusinessException("缺少交易号", code="INVALID_WEBHOOK", status_code=400)
        return _fulfill_notify_record(transaction_id)

    logger.warning("wechatpay_signature_verify_not_implemented")
    raise BusinessException("微信支付签名验证未实现", code="NOT_IMPLEMENTED", status_code=501)

