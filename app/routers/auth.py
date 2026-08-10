"""认证路由：注册、登录、邮箱验证、密码重置。"""

from __future__ import annotations

import os
import sqlite3
import time
import jwt
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from app.core.rate_limiter import get_client_ip
from pydantic import BaseModel, Field

from app.core.exceptions import (
    BusinessException,
    UnauthorizedException,
)
from app.core.response import success_response
from app.schemas.responses import (
    LoginResponse,
    MessageResponse,
    RegisterResponse,
)

# 从 main.py 导入共享依赖（main.py 在末尾导入本模块，此时所有名称已定义）
from main import (
    create_token,
    get_db,
    hash_password,
    _initial_user_credits,
    limiter_login,
    limiter_password_reset,
    limiter_password_reset_confirm,
    limiter_register,
    require_login,
    verify_password,
    _TEST_MODE,
)
from models import LoginRequest, RegisterRequest

router = APIRouter(tags=["认证"])


def _make_auth_challenge() -> dict:
    a = int(time.time()) % 9 + 1
    b = (int(time.time()) // 7) % 9 + 1
    answer = str(a + b)
    token = jwt.encode({"a": a, "b": b, "ans": answer, "exp": time.time() + 300, "purpose": "auth_challenge"}, __import__("main").settings.jwt_secret, algorithm="HS256")
    return {"token": token, "question": f"{a} + {b} = ?", "hint": "请输入验证码答案"}


def _verify_auth_challenge(token: str, answer: str) -> None:
    if _TEST_MODE or os.environ.get("AUTH_CHALLENGE_DISABLED", "").strip().lower() in {"1", "true", "yes", "on"}:
        return
    if not token or not answer:
        raise BusinessException("请完成验证码验证")
    try:
        payload = jwt.decode(token, __import__("main").settings.jwt_secret, algorithms=["HS256"])
    except Exception:
        raise BusinessException("验证码已过期，请刷新重试")
    if payload.get("purpose") != "auth_challenge" or str(payload.get("ans", "")) != str(answer).strip():
        raise BusinessException("验证码错误")


# ---------- 请求模型 ----------


class PasswordResetRequestModel(BaseModel):
    email: str


class PasswordResetConfirmModel(BaseModel):
    token: str
    new_password: str = Field(min_length=6, max_length=128)


# ---------- 端点 ----------


@router.get("/api/auth/challenge", response_model=MessageResponse)
async def api_auth_challenge() -> dict:
    return success_response(data=_make_auth_challenge())


@router.post("/api/register", response_model=RegisterResponse)
async def api_register(req: RegisterRequest, request: Request) -> dict:
    client_ip = get_client_ip(request)
    if not await limiter_register.is_allowed(client_ip):
        raise HTTPException(
            status_code=429,
            detail="注册请求过于频繁，请稍后再试",
            headers={"Retry-After": "60"},
        )
    _verify_auth_challenge(req.challenge_token, req.challenge_answer)
    conn = get_db()
    try:
        existing = conn.execute(
            "SELECT id FROM users WHERE username COLLATE NOCASE=?", (req.username,)
        ).fetchone()
        if existing:
            raise BusinessException("用户名已存在")
        conn.execute(
            "INSERT INTO users (username, password, email, role, team_id, credits, created_at) VALUES (?,?,?,?,?,?,?)",
            (
                req.username,
                hash_password(req.password),
                req.email,
                "member",
                0,
                _initial_user_credits(),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        conn.commit()
        user_row = conn.execute(
            "SELECT * FROM users WHERE username COLLATE NOCASE=?", (req.username,)
        ).fetchone()
        user = dict(user_row)
        token = create_token(
            user["id"],
            user["username"],
            user.get("role", "member"),
            user.get("team_id", 0),
        )
        user_dict = dict(user)
        return {
            "success": True,
            "token": token,
            "username": user_dict["username"],
            "user_id": user_dict["id"],
            "role": user_dict.get("role", "member"),
        }
    except sqlite3.IntegrityError:
        raise BusinessException("用户名已存在")
    finally:
        conn.close()


@router.post("/api/login", response_model=LoginResponse)
async def api_login(req: LoginRequest, request: Request) -> dict:
    client_ip = get_client_ip(request)
    if not await limiter_login.is_allowed(client_ip):
        raise HTTPException(
            status_code=429,
            detail="登录请求过于频繁，请稍后再试",
            headers={"Retry-After": "60"},
        )
    _verify_auth_challenge(req.challenge_token, req.challenge_answer)
    conn = get_db()
    try:
        user_row = conn.execute(
            "SELECT * FROM users WHERE username COLLATE NOCASE=?", (req.username,)
        ).fetchone()
        if not user_row:
            raise UnauthorizedException("用户名或密码错误")
        user = dict(user_row)
        if not verify_password(req.password, user["password"]):
            raise UnauthorizedException("用户名或密码错误")
        token = create_token(
            user["id"],
            user["username"],
            user.get("role", "member"),
            user.get("team_id", 0),
        )
        user_dict = dict(user)
        return {
            "success": True,
            "token": token,
            "username": user_dict["username"],
            "user_id": user_dict["id"],
            "role": user_dict.get("role", "member"),
        }
    finally:
        conn.close()


@router.post("/api/auth/verify-email", response_model=MessageResponse)
async def api_verify_email(token: str) -> dict:
    """验证邮箱（通过邮件中的验证链接）。"""
    from app.services.user_lifecycle import verify_email

    result = verify_email(token)
    if not result["success"]:
        raise HTTPException(400, result["message"])
    return success_response(data=result)


@router.post("/api/auth/resend-verification", response_model=MessageResponse)
async def api_resend_verification(
    user: dict = Depends(require_login),
) -> dict:
    """重新发送邮箱验证邮件。"""
    from app.services.email_service import send_verification_email
    from app.services.user_lifecycle import (
        generate_email_verification_token,
        get_user_by_email,
    )

    user_record = get_user_by_email(user.get("email", ""))
    if not user_record:
        raise HTTPException(404, "用户不存在")
    if user_record.get("email_verified"):
        return success_response(data={"message": "邮箱已验证"})

    token = generate_email_verification_token(user["user_id"])
    base_url = os.environ.get("PUBLIC_BASE_URL", "http://localhost:8000").rstrip("/")
    sent = send_verification_email(user.get("email", ""), token, base_url)
    return success_response(data={"sent": sent, "message": "验证邮件已发送" if sent else "邮件发送失败，请稍后重试"})


# ---------- 密码重置 ----------


@router.post("/api/auth/password-reset/request", response_model=MessageResponse)
async def api_password_reset_request(
    req: PasswordResetRequestModel, request: Request
) -> dict:
    """请求密码重置（发送重置邮件）。"""
    # 安全最佳实践：对密码重置请求限流，防止邮件轰炸攻击
    client_ip = get_client_ip(request)
    if not await limiter_password_reset.is_allowed(client_ip):
        raise HTTPException(
            status_code=429,
            detail="密码重置请求过于频繁，请稍后再试",
            headers={"Retry-After": "60"},
        )

    from app.services.email_service import send_password_reset_email
    from app.services.user_lifecycle import (
        generate_password_reset_token,
        get_user_by_email,
    )

    user_record = get_user_by_email(req.email)
    if not user_record:
        # 安全考虑：不透露邮箱是否存在
        return success_response(data={"message": "如果该邮箱已注册，重置邮件已发送"})

    token = generate_password_reset_token(user_record["id"])
    base_url = os.environ.get("PUBLIC_BASE_URL", "http://localhost:8000").rstrip("/")
    send_password_reset_email(req.email, token, base_url)
    return success_response(data={"message": "如果该邮箱已注册，重置邮件已发送"})


@router.post("/api/auth/password-reset/confirm", response_model=MessageResponse)
async def api_password_reset_confirm(
    req: PasswordResetConfirmModel, request: Request
) -> dict:
    """确认密码重置。"""
    # 安全最佳实践：限流防止重置令牌暴力破解
    client_ip = get_client_ip(request)
    if not await limiter_password_reset_confirm.is_allowed(client_ip):
        raise HTTPException(
            status_code=429,
            detail="密码重置确认过于频繁，请稍后再试",
            headers={"Retry-After": "60"},
        )

    from app.services.user_lifecycle import reset_password

    result = reset_password(req.token, req.new_password)
    if not result["success"]:
        raise HTTPException(400, result["message"])
    return success_response(data=result)
