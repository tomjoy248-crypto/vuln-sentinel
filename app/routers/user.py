"""用户信息路由：当前用户信息、积分余额、使用日志。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.core.exceptions import UnauthorizedException
from app.core.response import success_response
from app.schemas.responses import ApiResponse, CreditsResponse, MeResponse
from app.services import credits_service
from main import get_current_user, get_db, require_login

router = APIRouter(tags=["用户信息"])


# ---------- 端点 ----------


@router.get("/api/me", response_model=MeResponse)
async def api_me(user: dict | None = Depends(get_current_user)) -> dict:
    if not user:
        raise UnauthorizedException("未登录")

    # 从数据库读取最新 role/team_id/credits，确保和数据库一致
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT id, username, role, team_id, credits FROM users WHERE id=?",
            (user["user_id"],),
        ).fetchone()
        if not row:
            raise UnauthorizedException("用户不存在")
        user_dict = dict(row)
        return {
            "user_id": user_dict["id"],
            "username": user_dict["username"],
            "role": user_dict.get("role", "member"),
            "team_id": user_dict.get("team_id", 0),
            "credits": user_dict.get("credits", 10),
        }
    finally:
        conn.close()


@router.get("/api/me/credits", response_model=CreditsResponse)
async def api_me_credits(user: dict = Depends(require_login)) -> dict:
    """获取当前用户积分余额。"""
    credits = credits_service.get_credits(user["user_id"])
    return success_response(data={"credits": credits})


@router.get("/api/usage", response_model=ApiResponse)
async def api_usage(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user: dict = Depends(require_login),
) -> dict:
    """获取当前用户的积分使用日志。"""
    logs, total = credits_service.get_usage_logs(
        user["user_id"], limit=limit, offset=offset
    )
    return success_response(
        data={"logs": logs, "total": total},
        meta={"limit": limit, "offset": offset},
    )
