"""业务异常与全局异常处理"""

from fastapi import HTTPException, Request

from app.core.response import CODE_MAP, error_response


class BusinessException(Exception):
    """可预见的业务异常"""

    def __init__(
        self, detail: str, code: str = "BUSINESS_ERROR", status_code: int = 400
    ):
        self.detail = detail
        self.code = code
        self.status_code = status_code
        super().__init__(detail)


class NotFoundException(BusinessException):
    def __init__(self, detail: str = "资源不存在"):
        super().__init__(detail, code="NOT_FOUND", status_code=404)


class UnauthorizedException(BusinessException):
    def __init__(self, detail: str = "请先登录"):
        super().__init__(detail, code="UNAUTHORIZED", status_code=401)


class ForbiddenException(BusinessException):
    def __init__(self, detail: str = "权限不足"):
        super().__init__(detail, code="FORBIDDEN", status_code=403)


class RateLimitException(BusinessException):
    def __init__(self, detail: str = "请求过于频繁，请稍后再试"):
        super().__init__(detail, code="TOO_MANY_REQUESTS", status_code=429)


class PaymentRequiredException(BusinessException):
    def __init__(self, detail: str = "额度不足，请充值后继续使用"):
        super().__init__(detail, code="PAYMENT_REQUIRED", status_code=402)


def register_exception_handlers(app):
    """注册全局异常处理器"""

    @app.exception_handler(BusinessException)
    async def business_exception_handler(request: Request, exc: BusinessException):
        return error_response(exc.detail, exc.code, exc.status_code)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return error_response(
            exc.detail,
            CODE_MAP.get(exc.status_code, "ERROR"),
            exc.status_code,
            {"headers": dict(exc.headers)} if exc.headers else None,
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        import logging

        logger = logging.getLogger("vuln_sentinel")
        logger.exception(
            "Unhandled exception at %s %s", request.method, request.url.path
        )
        return error_response("服务器内部错误", "INTERNAL_ERROR", 500)
