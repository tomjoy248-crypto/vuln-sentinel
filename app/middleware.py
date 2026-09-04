"""自定义中间件。

request_id 中间件：为每个请求生成唯一 ID，
注入到 structlog 上下文和响应头中，
支持全链路日志追踪。

audit_logging_middleware：自动记录所有写操作 API 的审计日志。
"""

from __future__ import annotations

import time
from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import Request
from app.core.rate_limiter import get_client_ip
from fastapi.responses import Response

from app.core.logging import (
    generate_request_id,
    get_request_id,
    set_request_id,
)


async def request_id_middleware(
    request: Request,
    call_next: Callable[[Request], Coroutine[Any, Any, Any]],
) -> Response:
    """request_id 中间件。

    - 优先使用客户端传入的 X-Request-ID 头
    - 否则生成新的 request_id
    - 将 request_id 注入到 structlog 上下文
    - 在响应头中返回 X-Request-ID
    """
    # 获取或生成 request_id
    request_id = request.headers.get("X-Request-ID") or generate_request_id()
    set_request_id(request_id)

    # 处理请求
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start

    # 注入响应头
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time"] = f"{duration:.3f}s"

    return response


async def structured_request_logging_middleware(
    request: Request,
    call_next: Callable[[Request], Coroutine[Any, Any, Any]],
) -> Response:
    """结构化请求日志中间件。

    替代原有的 request_logging_middleware，
    输出 JSON 格式的请求日志，包含 request_id。
    """
    import structlog

    logger = structlog.get_logger("vuln_sentinel.http")
    start = time.time()
    client_ip = get_client_ip(request)
    method = request.method
    path = request.url.path

    try:
        response = await call_next(request)
    except Exception as e:
        duration = time.time() - start
        logger.error(
            "request_error",
            method=method,
            path=path,
            client_ip=client_ip,
            duration_ms=round(duration * 1000, 2),
            error=str(e),
            request_id=get_request_id(),
        )
        raise

    duration = time.time() - start
    status_code = response.status_code

    # 慢请求标记（> 3 秒）
    log_level = "warning" if duration > 3 else "info"
    log_method = getattr(logger, log_level)

    log_method(
        "request_completed",
        method=method,
        path=path,
        status_code=status_code,
        client_ip=client_ip,
        duration_ms=round(duration * 1000, 2),
        request_id=get_request_id(),
    )

    return response


# ---------- 审计日志中间件 ----------

# 无需审计的路径前缀
_AUDIT_SKIP_PATHS: tuple[str, ...] = (
    "/api/login",
    "/api/register",
    "/api/health",
    "/api/version",
    "/metrics",
    "/api/public-demo-scan",
    "/api/ai/chat",
)

# 路径 -> 资源类型映射（优先匹配前缀）
_AUDIT_PATH_RESOURCE_MAP: dict[str, str] = {
    "/api/scan": "scan",
    "/api/verify": "scan",
    "/api/verify-fix": "scan",
    "/api/verify-domain": "scan",
    "/api/batch-scan": "scan",
    "/api/history": "scan",
    "/api/fix-tickets": "ticket",
    "/api/finding": "finding",
    "/api/monitors": "monitor",
    "/api/assets": "asset",
    "/api/targets": "target",
    "/api/teams": "team",
    "/api/team": "team",
    "/api/report": "report",
    "/api/share": "report",
    "/api/reset-password": "user",
    "/api/me": "user",
    "/api/stats": "stats",
    "/api/alerts": "alert",
    "/api/simulate-fix": "ticket",
    "/api/apply-fix-and-rescan": "scan",
    "/api/generate-fix-package": "report",
    "/api/auto-fix": "ticket",
    "/api/auto-fix-via-cloudflare": "ticket",
    "/api/fix": "ticket",
    "/api/demo-fix": "demo",
    "/api/demo-full-cycle": "demo",
    "/api/ai-advisor": "ai",
    "/api/scans": "scan",
}


def _extract_resource_id(path: str) -> str | None:
    """从 RESTful 路径中提取资源 ID，如 /api/scans/123/retest -> 123。"""
    parts = path.strip("/").split("/")
    # 模式：/api/{resource}/{id}/... 或 /api/{resource}/{id}
    if len(parts) >= 3 and parts[0] == "api":
        # 检查第三个部分是否是数字或 UUID
        candidate = parts[2]
        if candidate.isdigit() or (len(candidate) > 8 and "-" in candidate):
            return candidate
    return None


def _infer_resource_type(path: str) -> str:
    """根据路径推断资源类型。"""
    for prefix, rtype in _AUDIT_PATH_RESOURCE_MAP.items():
        if path.startswith(prefix):
            return rtype
    return "api"


def _parse_user_id_from_request(request: Request) -> int | None:
    """从请求 Authorization header 中解析 user_id。"""
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return None
    token = auth[7:]
    try:
        import jwt

        try:
            from main import settings as main_settings

            secret = getattr(main_settings, "jwt_secret", "") or ""
        except Exception:
            secret = ""
        if not secret:
            from app.core.config import settings as config_settings

            secret = getattr(config_settings, "jwt_secret", "") or ""
        if not secret:
            return None
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload.get("user_id")
    except Exception:
        return None


async def audit_logging_middleware(
    request: Request,
    call_next: Callable[[Request], Coroutine[Any, Any, Any]],
) -> Response:
    """审计日志中间件。

    自动为所有写操作 API（POST/PUT/PATCH/DELETE）记录审计日志。
    解析 JWT 获取 user_id，失败时以匿名身份记录。
    不阻塞主流程，异常静默丢弃。
    """
    method = request.method

    # 只审计写操作
    if method not in ("POST", "PUT", "PATCH", "DELETE"):
        return await call_next(request)

    path = request.url.path

    # 跳过白名单路径
    if path.startswith(_AUDIT_SKIP_PATHS):
        return await call_next(request)

    # 只审计 API 路径
    if not path.startswith("/api/"):
        return await call_next(request)

    user_id = _parse_user_id_from_request(request)
    client_ip = get_client_ip(request)
    resource_type = _infer_resource_type(path)
    resource_id = _extract_resource_id(path)
    action = f"{method.lower()}_{resource_type}"

    started = time.time()
    try:
        response = await call_next(request)
    except Exception:
        try:
            from app.audit import save_audit_log
            save_audit_log(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details={
                    "path": path,
                    "method": method,
                    "status": "error",
                    "status_code": 500,
                    "duration_ms": round((time.time() - started) * 1000, 2),
                },
                client_ip=client_ip,
            )
        except Exception:
            pass
        raise

    # 请求完成后记录审计日志（不阻塞、不抛异常）
    try:
        from app.audit import save_audit_log

        details = {
            "path": path,
            "method": method,
            "status_code": response.status_code,
            "status": "success" if response.status_code < 400 else "failure",
            "duration_ms": round((time.time() - started) * 1000, 2),
        }
        save_audit_log(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            client_ip=client_ip,
        )
    except Exception:
        # 审计日志失败不得影响业务
        pass

    return response
