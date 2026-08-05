"""团队管理路由：团队成员查询、创建团队、加入团队、修改角色。"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.exceptions import (
    BusinessException,
    ForbiddenException,
    NotFoundException,
)
from app.schemas.responses import TeamActionResponse, TeamListResponse
from main import get_db, require_login

router = APIRouter(tags=["团队管理"])


# ---------- Team Management ----------


@router.get("/api/team", response_model=TeamListResponse)
async def api_team(user: dict = Depends(require_login)) -> dict:
    """获取当前用户所在团队的成员列表。"""
    my_role = user.get("role", "member")
    my_team_id = user.get("team_id", 0) or 0

    if my_team_id == 0:
        # 没有团队，返回自己
        return {
            "team_id": 0,
            "members": [
                {
                    "user_id": user["user_id"],
                    "username": user["username"],
                    "role": my_role,
                }
            ],
        }

    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT id, username, role, created_at FROM users WHERE team_id=? ORDER BY id",
            (my_team_id,),
        ).fetchall()
        members = [
            {"user_id": r[0], "username": r[1], "role": r[2], "created_at": r[3]}
            for r in rows
        ]
        return {"team_id": my_team_id, "role": my_role, "members": members}
    finally:
        conn.close()


@router.post("/api/team/create", response_model=TeamActionResponse)
async def api_team_create(user: dict = Depends(require_login)) -> dict:
    """创建团队，当前用户成为 admin。"""
    conn = get_db()
    try:
        my_row = conn.execute(
            "SELECT team_id FROM users WHERE id=?", (user["user_id"],)
        ).fetchone()
        if my_row and my_row[0] and my_row[0] > 0:
            raise BusinessException("已加入团队，请先退出当前团队")
        conn.execute(
            "UPDATE users SET role='admin', team_id=? WHERE id=?",
            (user["user_id"], user["user_id"]),
        )
        conn.commit()
        return {"success": True, "team_id": user["user_id"], "message": "团队已创建"}
    finally:
        conn.close()


@router.post("/api/team/join", response_model=TeamActionResponse)
async def api_team_join(req: dict, user: dict = Depends(require_login)) -> dict:
    """加入团队。"""
    team_id = req.get("team_id")
    if not team_id or not isinstance(team_id, int):
        raise BusinessException("team_id 必须是整数")
    conn = get_db()
    try:
        # 验证目标团队存在（team_id 就是 admin 的 user_id）
        admin_row = conn.execute(
            "SELECT id, role FROM users WHERE id=? AND team_id=?", (team_id, team_id)
        ).fetchone()
        if not admin_row:
            raise NotFoundException("团队不存在")
        # 更新自己的 team_id
        conn.execute(
            "UPDATE users SET team_id=?, role='member' WHERE id=?",
            (team_id, user["user_id"]),
        )
        conn.commit()
        return {"success": True, "team_id": team_id, "message": "已加入团队"}
    finally:
        conn.close()


@router.post("/api/team/{target_user_id}/role", response_model=TeamActionResponse)
async def api_team_set_role(
    target_user_id: int, req: dict, user: dict = Depends(require_login)
) -> dict:
    """修改团队成员角色（仅 admin 可操作）。"""
    new_role = req.get("role", "member")
    if new_role not in ("admin", "member", "viewer"):
        raise BusinessException("角色必须是 admin / member / viewer")
    conn = get_db()
    try:
        my_row = conn.execute(
            "SELECT role, team_id FROM users WHERE id=?", (user["user_id"],)
        ).fetchone()
        if not my_row or my_row[0] != "admin":
            raise ForbiddenException("仅团队管理员可修改角色")
        target = conn.execute(
            "SELECT id, team_id FROM users WHERE id=?", (target_user_id,)
        ).fetchone()
        if not target or target[1] != my_row[1]:
            raise NotFoundException("目标用户不在你的团队中")
        conn.execute("UPDATE users SET role=? WHERE id=?", (new_role, target_user_id))
        conn.commit()
        return {
            "success": True,
            "message": f"已将用户 {target_user_id} 的角色设为 {new_role}",
        }
    finally:
        conn.close()
