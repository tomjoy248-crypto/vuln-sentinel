"""审计日志路由：管理员查询审计日志。"""

from __future__ import annotations

import csv
import io

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

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


@router.get("/api/admin/audit-logs/summary")
async def api_admin_audit_summary(user: dict = Depends(require_login)) -> dict:
    """Return aggregate counts without exposing log detail."""
    from main import require_admin_user
    require_admin_user(user, "仅管理员可查看审计统计")
    from app.audit import get_audit_summary

    return success_response(data=get_audit_summary())


@router.get("/api/admin/dashboard/stats")
async def api_admin_dashboard_stats(
    days: int = Query(30, ge=1, le=365),
    user: dict = Depends(require_login),
) -> dict:
    """Return bounded scan, finding, task, and audit chart aggregates."""
    from main import require_admin_user
    require_admin_user(user, "仅管理员可查看后台统计")
    from app.audit import get_admin_dashboard_stats

    return success_response(data=get_admin_dashboard_stats(days))


@router.get("/api/admin/audit-logs/export")
async def api_admin_audit_export(
    limit: int = Query(500, ge=1, le=5000),
    action: str = Query("", max_length=80),
    resource_type: str = Query("", max_length=40),
    status: str = Query("", max_length=20),
    user: dict = Depends(require_login),
) -> StreamingResponse:
    """Export a bounded, already-redacted CSV audit report."""
    from main import require_admin_user
    require_admin_user(user, "仅管理员可导出审计日志")
    from app.audit import get_audit_logs

    logs = get_audit_logs(action=action or None, resource_type=resource_type or None,
                          status=status or None, limit=limit)
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["id", "created_at", "username", "action", "resource_type", "resource_id", "status", "client_ip", "request_id"])
    for log in logs:
        writer.writerow([log["id"], log["created_at"], log.get("username") or "", log["action"],
                         log["resource_type"], log.get("resource_id") or "", log["details"].get("status", ""),
                         log.get("client_ip") or "", log.get("request_id") or ""])
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv; charset=utf-8",
                             headers={"Content-Disposition": "attachment; filename=audit-logs.csv"})


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
