"""审计日志路由：管理员查询审计日志。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.response import success_response
from app.schemas.responses import AuditLogListResponse
from main import require_login

router = APIRouter(tags=["审计日志"])


# ---------- 审计日志查询 ----------


@router.get("/api/admin/audit-logs", response_model=AuditLogListResponse)
async def api_admin_audit_logs(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    user_id: int | None = Query(None),
    action: str = "",
    user: dict = Depends(require_login),
) -> dict:
    """管理员查询审计日志。"""
    from main import require_admin_user
    require_admin_user(user)
    from app.audit import get_audit_logs

    logs = get_audit_logs(
        user_id=user_id,
        action=action or None,
        limit=limit,
        offset=offset,
    )
    return success_response(data={"logs": logs, "limit": limit, "offset": offset})


@router.get("/api/admin/email-logs", response_model=AuditLogListResponse)
async def api_admin_email_logs(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    email_type: str = Query("", max_length=40),
    status: str = Query("", max_length=20),
    user: dict = Depends(require_login),
) -> dict:
    """管理员查询邮件投递状态，不返回正文、令牌或完整邮箱地址。"""
    from main import require_admin_user
    require_admin_user(user)
    from app.services.email_service import get_email_delivery_logs

    logs = get_email_delivery_logs(
        email_type=email_type or None,
        status=status or None,
        limit=limit,
        offset=offset,
    )
    return success_response(
        data={
            "logs": logs,
            "limit": limit,
            "offset": offset,
        }
    )
