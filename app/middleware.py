"""自定义中间件。

request_id 中间件：为每个请求生成唯一 ID，
注入到 structlog 上下文和响应头中，
支持全链路日志追踪。
"""

from __future__ import annotations

import time
import uuid
from typing import Callable, Coroutine, Any

from fastapi import Request
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
    client_ip = request.client.host if request.client else "unknown"
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
