"""审计日志路由：管理员查询审计日志。"""

from __future__ import annotations

import csv
import io
import secrets

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse

from app.core.exceptions import BusinessException, NotFoundException
from app.core.response import success_response
from app.schemas.responses import AuditLogListResponse
from main import require_login

router = APIRouter(tags=["审计日志"])


def _mask_email(value: str) -> str:
    if not value or "@" not in value:
        return ""
    name, domain = value.split("@", 1)
    return (name[:2] + "***@" + domain) if name else "***@" + domain


def _mask_phone(value: str) -> str:
    return value[:3] + "****" + value[-4:] if len(value or "") == 11 else ""


@router.post("/api/admin/setup")
async def api_admin_setup(req: dict, user: dict = Depends(require_login)) -> dict:
    """Promote the first administrator using an out-of-band setup token."""
    from app.audit import save_audit_log
    from main import get_db, settings

    configured = settings.admin_setup_token.strip()
    supplied = str(req.get("setup_token") or "").strip()
    if not configured:
        raise BusinessException("未配置 ADMIN_SETUP_TOKEN")
    if not secrets.compare_digest(configured, supplied):
        save_audit_log(user["user_id"], "admin_setup_failed", "user", str(user["user_id"]))
        raise BusinessException("管理员初始化令牌错误", status_code=403)
    conn = get_db()
    try:
        if conn.execute("SELECT id FROM users WHERE system_role='admin' LIMIT 1").fetchone():
            raise BusinessException("管理员已经存在", status_code=409)
        conn.execute("UPDATE users SET system_role='admin' WHERE id=?", (user["user_id"],))
        conn.commit()
    finally:
        conn.close()
    save_audit_log(user["user_id"], "admin_setup_success", "user", str(user["user_id"]))
    return {"success": True, "message": "管理员初始化成功"}


@router.get("/api/admin/users")
async def api_admin_users(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    query: str = Query("", max_length=80),
    role: str = Query("", max_length=20),
    active: str = Query("", max_length=10),
    user: dict = Depends(require_login),
) -> dict:
    from main import get_db, require_admin_user

    require_admin_user(user, "仅管理员可查看用户")
    clauses, params = [], []
    if query:
        clauses.append("(username LIKE ? OR email LIKE ? OR phone LIKE ?)")
        term = f"%{query}%"
        params.extend([term, term, term])
    if role:
        clauses.append("role=?")
        params.append(role)
    if active in {"0", "1"}:
        clauses.append("is_active=?")
        params.append(int(active))
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    conn = get_db()
    try:
        total = conn.execute("SELECT COUNT(*) FROM users" + where, params).fetchone()[0]
        rows = conn.execute(
            "SELECT id, username, email, phone, phone_verified, role, system_role, team_id, credits, is_active, created_at "
            + "FROM users" + where + " ORDER BY id DESC LIMIT ? OFFSET ?",
            [*params, limit, offset],
        ).fetchall()
    finally:
        conn.close()
    users = []
    for row in rows:
        item = dict(row)
        item["email"] = _mask_email(item.get("email") or "")
        item["phone"] = _mask_phone(item.get("phone") or "")
        item["is_active"] = bool(item.get("is_active", 1))
        item["phone_verified"] = bool(item.get("phone_verified", 0))
        users.append(item)
    return {"success": True, "data": {"users": users, "total": total, "limit": limit, "offset": offset}}


@router.patch("/api/admin/users/{target_user_id}")
async def api_admin_update_user(
    target_user_id: int,
    req: dict,
    request: Request,
    user: dict = Depends(require_login),
) -> dict:
    from app.audit import save_audit_log
    from main import get_db, require_admin_confirmation, require_admin_user

    require_admin_user(user, "仅管理员可管理用户")
    require_admin_confirmation(request)
    system_role = req.get("system_role")
    is_active = req.get("is_active")
    if system_role is not None and system_role not in {"admin", "user"}:
        raise BusinessException("系统角色不合法")
    if is_active is not None and not isinstance(is_active, bool):
        raise BusinessException("账号状态不合法")
    if target_user_id == user["user_id"] and (system_role not in {None, "admin"} or is_active is False):
        raise BusinessException("不能降低或停用当前管理员账号")
    conn = get_db()
    try:
        target = conn.execute("SELECT id, system_role, is_active FROM users WHERE id=?", (target_user_id,)).fetchone()
        if not target:
            raise NotFoundException("用户不存在")
        if target["system_role"] == "admin" and system_role not in {None, "admin"}:
            if conn.execute("SELECT COUNT(*) FROM users WHERE system_role='admin' AND is_active=1").fetchone()[0] <= 1:
                raise BusinessException("不能移除最后一个管理员")
        if system_role is not None:
            conn.execute("UPDATE users SET system_role=? WHERE id=?", (system_role, target_user_id))
        if is_active is not None:
            conn.execute("UPDATE users SET is_active=? WHERE id=?", (int(is_active), target_user_id))
        conn.commit()
    finally:
        conn.close()
    save_audit_log(user["user_id"], "admin_user_update", "user", str(target_user_id), {"system_role": system_role, "is_active": is_active}, request.client.host if request.client else "")
    return {"success": True, "message": "用户信息已更新"}


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
