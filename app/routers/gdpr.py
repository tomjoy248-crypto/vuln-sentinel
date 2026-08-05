"""GDPR 数据合规路由：数据导出、账号删除、数据匿名化、数据保留策略。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.core.response import success_response
from app.schemas.responses import ApiResponse, DataExportResponse
from main import require_login

router = APIRouter(tags=["GDPR 数据合规"])


# ---------- GDPR 数据合规 ----------


@router.get("/api/me/export", response_model=DataExportResponse)
async def api_export_my_data(user: dict = Depends(require_login)) -> dict:
    """导出当前用户的所有数据（GDPR 数据可携带权）。"""
    from app.services.gdpr_service import export_user_data

    data = export_user_data(user["user_id"])
    return success_response(data=data, meta={"note": "数据导出完成"})


@router.delete("/api/me/account", response_model=ApiResponse)
async def api_delete_my_account(
    user: dict = Depends(require_login),
    confirm: str = "",
) -> dict:
    """删除当前用户账号及所有关联数据（GDPR 被遗忘权）。

    需要传入 confirm=DELETE 确认操作。
    """
    if confirm != "DELETE":
        raise HTTPException(400, "请传入 confirm=DELETE 确认删除操作")
    from app.services.gdpr_service import delete_user_account

    result = delete_user_account(user["user_id"])
    if not result["success"]:
        raise HTTPException(500, result["message"])
    return success_response(data=result)


@router.post("/api/me/anonymize", response_model=ApiResponse)
async def api_anonymize_my_data(user: dict = Depends(require_login)) -> dict:
    """匿名化用户个人数据（保留扫描记录用于统计）。"""
    from app.services.gdpr_service import anonymize_user_data

    result = anonymize_user_data(user["user_id"])
    return success_response(data=result)


# ---------- 数据保留策略手动触发 ----------


@router.post("/api/admin/data-retention/run", response_model=ApiResponse)
async def api_admin_run_retention(
    user: dict = Depends(require_login),
) -> dict:
    """管理员手动触发数据保留策略清理。"""
    if user.get("role") != "admin":
        raise HTTPException(403, "仅管理员可执行此操作")
    from app.services.data_retention import run_retention_policy

    stats = run_retention_policy()
    return success_response(data=stats)
