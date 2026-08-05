"""安全工具：JWT / 密码哈希 / 认证依赖。

本模块是 main.py 中认证逻辑的模块化封装。
main.py 仍然保留原始函数定义以保证向后兼容，
新代码应优先从 app.core.security 导入。
"""

from __future__ import annotations

import time

import bcrypt
import jwt
from fastapi import Header, HTTPException


def hash_password(pwd: str) -> str:
    """使用 bcrypt 哈希密码。

    bcrypt 限制密码最长 72 字节，超出部分截断。
    """
    return bcrypt.hashpw(pwd[:72].encode("utf-8"), bcrypt.gensalt(rounds=12)).decode(
        "utf-8"
    )


def verify_password(pwd: str, hashed: str) -> bool:
    """校验密码与 bcrypt 哈希。"""
    try:
        return bcrypt.checkpw(pwd[:72].encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def create_token(
    user_id: int,
    username: str,
    role: str = "member",
    team_id: int = 0,
    *,
    secret: str = "",
    expire_seconds: int = 86400,
) -> str:
    """生成 JWT token。

    Args:
        user_id: 用户 ID
        username: 用户名
        role: 角色
        team_id: 团队 ID
        secret: JWT 密钥（留空则由调用方从 settings 获取）
        expire_seconds: 过期时间（秒）
    """
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "team_id": team_id,
        "exp": time.time() + expire_seconds,
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def verify_token(token: str, *, secret: str = "") -> dict | None:
    """验证 JWT token。

    Args:
        token: JWT token 字符串
        secret: JWT 密钥

    Returns:
        解码后的 payload，验证失败返回 None
    """
    try:
        return jwt.decode(token, secret, algorithms=["HS256"])
    except Exception:
        return None


async def get_current_user(
    authorization: str | None = Header(None),
) -> dict | None:
    """可选认证依赖：无 token 返回 None，不报错。"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization[7:]
    # secret 由 main.py 的全局 settings 提供，此处通过延迟导入避免循环依赖
    from main import verify_token as _verify

    return _verify(token)


async def require_login(authorization: str | None = Header(None)) -> dict:
    """强制认证依赖：无 token 或 token 无效时抛 401。"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "请先登录")
    token = authorization[7:]
    from main import verify_token as _verify

    user = _verify(token)
    if not user:
        raise HTTPException(401, "请先登录")
    return user
