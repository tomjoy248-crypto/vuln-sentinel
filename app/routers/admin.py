"""审计日志路由：管理员查询审计日志。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

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
    action: str = Query("", max_length=80),
    resource_type: str = Query("", max_length=40),
    resource_id: str = Query("", max_length=120),
    username: str = Query("", max_length=80),
    status: str = Query("", max_length=20),
    start_at: str = Query("", max_length=30),
    end_at: str = Query("", max_length=30),
    user: dict = Depends(require_login),
) -> dict:
    """管理员查询审计日志。"""
    from main import require_admin_user
    require_admin_user(user, "仅管理员可查询审计日志")
    from app.audit import get_audit_logs

    logs = get_audit_logs(
        user_id=user_id,
        action=action or None,
        resource_type=resource_type or None,
        resource_id=resource_id or None,
        username=username or None,
        status=status or None,
        start_at=start_at or None,
        end_at=end_at or None,
        limit=limit,
        offset=offset,
    )
    return success_response(data={"logs": logs, "limit": limit, "offset": offset,
                                  "has_more": len(logs) == limit})


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
    require_admin_user(user, "仅管理员可查询邮件日志")
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
