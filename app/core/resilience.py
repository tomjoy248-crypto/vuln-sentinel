"""容错与弹性扫描工具。

提供重试、降级、超时控制、断路器等机制，确保扫描流程在面对
网络抖动、目标不稳定或子服务异常时仍能给出尽可能可靠的结果。
"""

from __future__ import annotations

import asyncio
import functools
import logging
import random
import time
from collections.abc import Callable, Coroutine
from typing import Any, TypeVar

logger = logging.getLogger("vuln_sentinel.resilience")

T = TypeVar("T")


class RetryExhausted(Exception):
    """重试耗尽异常。"""

    def __init__(self, message: str, last_error: Exception | None = None):
        super().__init__(message)
        self.last_error = last_error


async def async_retry(
    coro: Callable[[], Coroutine[Any, Any, T]],
    max_attempts: int = 3,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    base_delay: float = 0.5,
    max_delay: float = 5.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    on_retry: Callable[[Exception, int], None] | None = None,
) -> T:
    """对异步可调用对象执行带指数退避的重试。

    Args:
        coro: 无参数协程，返回目标结果
        max_attempts: 最大尝试次数
        exceptions: 需要重试的异常类型
        base_delay: 首次重试等待秒数
        max_delay: 最大重试等待秒数
        exponential_base: 退避指数底数
        jitter: 是否添加随机抖动，避免惊群
        on_retry: 每次重试时的回调，参数为 (异常, 当前尝试次数)

    Returns:
        协程返回结果

    Raises:
        RetryExhausted: 重试次数耗尽时抛出
    """
    last_err: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return await coro()
        except exceptions as exc:
            last_err = exc
            if attempt == max_attempts:
                break
            delay = min(base_delay * (exponential_base ** (attempt - 1)), max_delay)
            if jitter:
                delay = delay * (0.7 + random.random() * 0.6)
            logger.debug(
                "Retry %d/%d after %.2fs due to %s", attempt, max_attempts, delay, exc
            )
            if on_retry:
                try:
                    on_retry(exc, attempt)
                except Exception:
                    pass
            await asyncio.sleep(delay)
    raise RetryExhausted(f"重试 {max_attempts} 次后仍然失败", last_error=last_err)


def retry(
    max_attempts: int = 3,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    base_delay: float = 0.5,
    max_delay: float = 5.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
):
    """装饰器：为异步函数添加指数退避重试。"""

    def decorator(
        func: Callable[..., Coroutine[Any, Any, T]],
    ) -> Callable[..., Coroutine[Any, Any, T]]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            return await async_retry(
                coro=lambda: func(*args, **kwargs),
                max_attempts=max_attempts,
                exceptions=exceptions,
                base_delay=base_delay,
                max_delay=max_delay,
                exponential_base=exponential_base,
                jitter=jitter,
            )

        return wrapper

    return decorator


async def with_fallback(
    primary: Callable[[], Coroutine[Any, Any, T]],
    fallback: Callable[[], Coroutine[Any, Any, T]],
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> T:
    """先执行主逻辑，失败时执行降级逻辑。"""
    try:
        return await primary()
    except exceptions as exc:
        logger.warning("Primary failed, running fallback: %s", exc)
        return await fallback()


async def with_timeout(
    coro: Coroutine[Any, Any, T],
    timeout: float,
    timeout_value: T | None = None,
) -> T | None:
    """执行协程并设置超时，超时时返回 timeout_value 而非抛异常。"""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        logger.warning("Operation timed out after %.2fs, returning default", timeout)
        return timeout_value


class CircuitBreaker:
    """简易断路器，防止连续失败的调用拖垮系统。"""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        expected_exception: type[Exception] = Exception,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self._failures = 0
        self._last_failure_time: float | None = None
        self._state = "closed"  # closed / open / half_open

    async def call(self, coro: Callable[[], Coroutine[Any, Any, T]]) -> T:
        if self._state == "open":
            if (
                self._last_failure_time
                and (time.time() - self._last_failure_time) > self.recovery_timeout
            ):
                self._state = "half_open"
            else:
                raise RetryExhausted("Circuit breaker is OPEN")

        try:
            result = await coro()
            if self._state == "half_open":
                self._state = "closed"
                self._failures = 0
            return result
        except self.expected_exception as exc:
            self._failures += 1
            self._last_failure_time = time.time()
            if self._failures >= self.failure_threshold:
                self._state = "open"
            raise exc


# 全局断路器实例（按功能划分）
scan_circuit_breaker = CircuitBreaker(failure_threshold=10, recovery_timeout=60.0)
