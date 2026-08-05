"""统一 API 响应封装"""

from typing import Any

from fastapi.responses import JSONResponse


def success_response(
    data: Any = None,
    message: str = "ok",
    meta: dict[str, Any] | None = None,
    status_code: int = 200,
) -> JSONResponse:
    """统一成功响应"""
    payload: dict[str, Any] = {"success": True, "message": message}
    if data is not None:
        payload["data"] = data
    if meta:
        payload["meta"] = meta
    return JSONResponse(status_code=status_code, content=payload)


def error_response(
    detail: str,
    code: str = "ERROR",
    status_code: int = 400,
    extra: dict[str, Any] | None = None,
) -> JSONResponse:
    """统一错误响应"""
    payload: dict[str, Any] = {"success": False, "error": detail, "code": code}
    if extra:
        payload.update(extra)
    return JSONResponse(status_code=status_code, content=payload)


CODE_MAP = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    409: "CONFLICT",
    422: "VALIDATION_ERROR",
    429: "TOO_MANY_REQUESTS",
    500: "INTERNAL_ERROR",
}
