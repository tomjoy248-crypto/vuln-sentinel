"""计费路由：套餐列表、购买、充值记录、订单与支付回调。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.core.response import success_response
from app.schemas.responses import (
    ApiResponse,
    BillingPlanListResponse,
    OrderStatusResponse,
    PurchaseResponse,
    RechargeListResponse,
)
from main import require_login
from models import (
    AdminRechargeRequest,
    CreateOrderRequest,
    PurchasePlanRequest,
)

router = APIRouter(tags=["计费"])


# ---------- Billing / 计费套餐 ----------


@router.get("/api/billing/plans", response_model=BillingPlanListResponse)
async def api_billing_plans() -> dict:
    """获取可用计费套餐列表。"""
    from app.services.billing_service import get_plans

    plans = get_plans(active_only=True)
    return success_response(data={"plans": plans})


@router.post("/api/billing/purchase", response_model=PurchaseResponse)
async def api_billing_purchase(
    req: PurchasePlanRequest, user: dict = Depends(require_login)
) -> dict:
    """购买套餐（模拟支付，积分立即到账）。"""
    from app.services.billing_service import purchase_plan

    result = purchase_plan(user["user_id"], req.plan_id)
    return success_response(data=result)


@router.get("/api/billing/recharges", response_model=RechargeListResponse)
async def api_billing_recharges(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user: dict = Depends(require_login),
) -> dict:
    """获取当前用户的充值记录。"""
    from app.services.billing_service import get_user_recharge_records

    records, total = get_user_recharge_records(
        user["user_id"], limit=limit, offset=offset
    )
    return success_response(
        data={"records": records, "total": total},
        meta={"limit": limit, "offset": offset},
    )


@router.post("/api/admin/recharge", response_model=PurchaseResponse)
async def api_admin_recharge(
    req: AdminRechargeRequest, user: dict = Depends(require_login)
) -> dict:
    """管理员直接给用户充值积分。"""
    from app.services.billing_service import admin_recharge_user

    result = admin_recharge_user(user, req.user_id, req.credits, req.note)
    return success_response(data=result)


@router.post("/api/billing/order", response_model=OrderStatusResponse)
async def api_billing_create_order(
    req: CreateOrderRequest, user: dict = Depends(require_login)
) -> dict:
    """创建支付订单（支持 mock/stripe，支付宝/微信预留）。"""
    from app.services.billing_service import create_payment_order

    result = create_payment_order(
        user_id=user["user_id"],
        plan_id=req.plan_id,
        provider=req.provider,
        success_url=req.success_url,
        cancel_url=req.cancel_url,
    )
    return success_response(data=result)


@router.get("/api/billing/order/{transaction_id}", response_model=OrderStatusResponse)
async def api_billing_order_status(
    transaction_id: str, user: dict = Depends(require_login)
) -> dict:
    """查询订单状态。"""
    from app.services.billing_service import (
        get_order_status,
        get_recharge_record_by_transaction,
    )

    record = get_recharge_record_by_transaction(transaction_id)
    if not record:
        raise HTTPException(status_code=404, detail="订单不存在")
    # 用户只能查看自己的订单
    if record.get("user_id") != user["user_id"] and user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="无权查看该订单")
    status = get_order_status(transaction_id)
    return success_response(data=status)


@router.post("/api/billing/webhook/{provider}", response_model=ApiResponse)
async def api_billing_webhook(provider: str, request: Request) -> dict:
    """支付网关异步通知回调（Stripe / 支付宝 / 微信）。"""
    import os

    from app.core.exceptions import BusinessException
    from app.services.billing_service import (
        handle_alipay_notify,
        handle_stripe_webhook,
        handle_wechat_notify,
    )

    if provider == "stripe":
        payload = await request.body()
        sig = request.headers.get("stripe-signature", "")
        secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
        if not secret:
            raise HTTPException(status_code=400, detail="STRIPE_WEBHOOK_SECRET 未配置")
        try:
            result = handle_stripe_webhook(payload, sig, secret)
        except BusinessException as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
        return success_response(data=result)

    if provider == "alipay":
        payload = await request.json()
        try:
            result = handle_alipay_notify(payload)
        except BusinessException as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
        return success_response(data=result)

    if provider == "wechat":
        payload = await request.json()
        try:
            result = handle_wechat_notify(payload)
        except BusinessException as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
        return success_response(data=result)

    raise HTTPException(status_code=400, detail=f"不支持的支付渠道：{provider}")
