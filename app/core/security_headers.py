"""安全响应头中间件。

为所有响应自动注入安全相关的 HTTP 头。
"""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import Request
from fastapi.responses import Response

# 默认注入到所有响应的安全头
SECURITY_HEADERS: dict[str, str] = {
    "X-Content-Type-Options": "nosniff",
    "X-XSS-Protection": "1; mode=block",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    # NOTE: 'unsafe-inline' 保留在 script-src 中是因为当前前端代码中存在
    # 内联脚本（非 Vite 注入的部分），直接移除会导致功能损坏。
    # TODO（未来改进）: 将所有内联脚本迁移至外部文件后，改用基于 nonce 或 hash
    # 的 CSP（Vite 已为构建产物生成哈希文件名，具备实施条件），
    # 届时可移除 'unsafe-inline' 以显著增强 XSS 防护。
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self' data:; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    ),
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
}

# 仅在 HTTPS 下注入的头（HSTS 在明文 HTTP 上会被浏览器忽略，且可能锁定后续 HTTPS）
HTTPS_ONLY_HEADERS: dict[str, str] = {
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
}


def apply_security_headers(response: Response, *, is_https: bool = False) -> Response:
    """向响应注入安全头。

    Args:
        response: 待处理的响应对象。
        is_https: 请求是否经 HTTPS 到达；为 ``True`` 时额外注入 HSTS 头。
    """
    for key, value in SECURITY_HEADERS.items():
        response.headers[key] = value
    if is_https:
        for key, value in HTTPS_ONLY_HEADERS.items():
            response.headers[key] = value
    return response


def _is_https(request: Request) -> bool:
    """判断请求是否通过 HTTPS 到达。

    优先使用 Starlette 的 ``url.is_secure``；在反向代理后则信任
    ``X-Forwarded-Proto`` 头（需确保代理已正确设置该头）。
    """
    try:
        if request.url.is_secure:
            return True
    except Exception:
        pass
    forwarded_proto = request.headers.get("x-forwarded-proto", "")
    return forwarded_proto.split(",")[0].strip().lower() == "https"


async def security_headers_middleware(
    request: Request,
    call_next: Callable[[Request], Coroutine[Any, Any, Any]],
) -> Response:
    """安全响应头中间件。

    对所有响应注入统一的安全头；HTTPS 请求额外附加
    ``Strict-Transport-Security``。
    """
    response = await call_next(request)
    return apply_security_headers(response, is_https=_is_https(request))
