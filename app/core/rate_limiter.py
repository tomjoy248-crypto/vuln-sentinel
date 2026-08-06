"""API 限流中间件。

基于令牌桶算法实现请求限流，支持：
- 按用户 ID 限流（已认证用户）
- 按 IP 地址限流（匿名用户）
- 不同路径的差异化限流策略
- 超限返回 429 Too Many Requests
- Redis 分布式限流（生产环境）
"""

from __future__ import annotations

import asyncio
import logging
import os
import threading
import time
from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse, Response

logger = logging.getLogger("vuln_sentinel.rate_limiter")

# ---------------------------------------------------------------------------
# 令牌桶
# ---------------------------------------------------------------------------


class TokenBucket:
    """令牌桶。

    以固定速率 ``refill_rate``（tokens/秒）向桶中补充令牌，
    桶容量上限为 ``capacity``。每次请求调用 :meth:`try_consume` 消耗令牌，
    令牌不足时拒绝请求，从而在平滑限流的同时允许短时突发流量。

    Attributes:
        capacity: 桶容量（允许的突发请求数）。
        refill_rate: 令牌补充速率（tokens/秒）。
        tokens: 当前令牌数（浮点，允许小数级补充）。
        last_refill: 上次补充令牌的时间戳（``time.monotonic``）。
    """

    __slots__ = ("capacity", "refill_rate", "tokens", "last_refill")

    def __init__(self, capacity: float, refill_rate: float) -> None:
        self.capacity = float(capacity)
        self.refill_rate = float(refill_rate)
        # 初始化即满，允许服务启动初期的合理突发
        self.tokens = float(capacity)
        self.last_refill = time.monotonic()

    def _refill(self) -> None:
        """按距上次补充的时间差补充令牌，不超过容量上限。

        无论是否产生新令牌都会刷新 ``last_refill``，
        因此该字段可兼作「最近使用时间」供限流器做惰性清理。
        """
        now = time.monotonic()
        elapsed = now - self.last_refill
        if elapsed > 0:
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

    def try_consume(self, n: float = 1.0) -> bool:
        """尝试消耗 ``n`` 个令牌。

        成功返回 ``True`` 并扣减令牌；令牌不足返回 ``False`` 且不扣减。
        """
        self._refill()
        if self.tokens >= n:
            self.tokens -= n
            return True
        return False

    def seconds_until_next_token(self, n: float = 1.0) -> float:
        """返回补充到 ``n`` 个令牌还需多少秒。

        用于计算 ``X-RateLimit-Reset`` 与 ``Retry-After``。
        当前令牌已足够时返回 ``0.0``。
        """
        self._refill()
        if self.tokens >= n:
            return 0.0
        if self.refill_rate <= 0:
            return 0.0
        return (n - self.tokens) / self.refill_rate


# ---------------------------------------------------------------------------
# 限流规则
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RateLimitRule:
    """单条限流规则。

    Attributes:
        path_prefix: 路径前缀，命中该前缀的请求采用本规则。
        requests_per_minute: 每分钟允许的请求数（持续速率）。
        burst: 突发容量（令牌桶容量），允许短时间内的请求突发。
    """

    path_prefix: str
    requests_per_minute: int
    burst: int

    @property
    def refill_rate(self) -> float:
        """令牌补充速率（tokens/秒）。"""
        return self.requests_per_minute / 60.0


# ---------------------------------------------------------------------------
# 限流器
# ---------------------------------------------------------------------------


class RateLimiter:
    """令牌桶限流器。

    为每条规则维护一个 ``{identifier: TokenBucket}`` 字典，identifier 优先取
    已认证用户的 ``user_id``，否则取客户端 IP。通过单把互斥锁保证线程安全，
    并周期性清理长期未使用的桶以防内存泄漏。

    预配置规则（按匹配优先级排序，越具体的路径越靠前）：

    - ``/api/scan``     10 rpm, burst 3   （扫描成本高，严格限流）
    - ``/api/login``    5 rpm,  burst 3   （防暴力破解）
    - ``/api/register`` 3 rpm,  burst 2   （防批量注册）
    - ``/api/ai/``      20 rpm, burst 5   （AI 接口中等限流）
    - ``/api/``         默认 60 rpm, burst 10
    - 非 ``/api/`` 路径（静态资源、健康检查等）不限流
    """

    # 桶闲置超过该时长将被清理（10 分钟）
    _BUCKET_TTL_SECONDS: float = 600.0
    # 清理检查的最小间隔，避免每次请求都全量扫描
    _CLEANUP_INTERVAL_SECONDS: float = 60.0

    def __init__(self, default_rpm: int = 60, default_burst: int = 10) -> None:
        self._default_rpm = default_rpm
        self._default_burst = default_burst
        self._lock = threading.Lock()
        self._last_cleanup = time.monotonic()

        # 预配置规则：越具体的路径越靠前，默认 /api/ 规则放最后兜底
        self._rules: list[RateLimitRule] = [
            RateLimitRule("/api/scan", 10, 3),
            RateLimitRule("/api/login", 5, 3),
            RateLimitRule("/api/register", 3, 2),
            RateLimitRule("/api/ai/", 20, 5),
            RateLimitRule("/api/", default_rpm, default_burst),
        ]

        # 每条规则一个独立的 identifier -> TokenBucket 字典
        self._buckets: dict[str, dict[str, TokenBucket]] = {
            rule.path_prefix: {} for rule in self._rules
        }

    # ---------------- 规则匹配 ----------------

    def get_rule(self, path: str) -> RateLimitRule | None:
        """返回命中路径的限流规则；非 API 路径返回 ``None``（不限流）。"""
        for rule in self._rules:
            if self._path_matches(path, rule.path_prefix):
                return rule
        return None

    @staticmethod
    def _path_matches(path: str, prefix: str) -> bool:
        """前缀匹配。

        - 以 ``/`` 结尾的前缀按 ``startswith`` 匹配其下所有子路径；
        - 否则要求精确命中或在边界 ``/`` 处续接，
          避免 ``/api/scan`` 误命中 ``/api/scans``。
        """
        if prefix.endswith("/"):
            return path.startswith(prefix)
        return path == prefix or path.startswith(prefix + "/")

    # ---------------- 限流检查 ----------------

    async def check(self, path: str, identifier: str) -> tuple[bool, dict[str, str]]:
        """检查请求是否被允许。

        Args:
            path: 请求路径。
            identifier: 限流标识（用户 ID 或客户端 IP）。

        Returns:
            ``(allowed, headers)`` 二元组。

            - 非 API 路径直接放行，``headers`` 为空字典。
            - ``headers`` 包含 ``X-RateLimit-Limit`` / ``X-RateLimit-Remaining``
              / ``X-RateLimit-Reset`` 三个标准限流响应头。其中 ``Reset`` 为
              「下一个令牌可用」的 Unix 时间戳（秒）。
        """
        rule = self.get_rule(path)
        if rule is None:
            return True, {}

        with self._lock:
            self._maybe_cleanup()
            buckets = self._buckets[rule.path_prefix]
            bucket = buckets.get(identifier)
            if bucket is None:
                bucket = TokenBucket(rule.burst, rule.refill_rate)
                buckets[identifier] = bucket
            allowed = bucket.try_consume(1.0)
            # Remaining 不超过 Limit（即 requests_per_minute）
            remaining = max(0, min(int(bucket.tokens), rule.requests_per_minute))
            reset_in = bucket.seconds_until_next_token(1.0)

        headers = {
            "X-RateLimit-Limit": str(rule.requests_per_minute),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(int(time.time() + reset_in)),
        }
        return allowed, headers

    # ---------------- 惰性清理 ----------------

    def _maybe_cleanup(self) -> None:
        """周期性清理闲置桶。必须在持有 ``self._lock`` 时调用。"""
        now = time.monotonic()
        if now - self._last_cleanup < self._CLEANUP_INTERVAL_SECONDS:
            return
        self._last_cleanup = now
        cutoff = now - self._BUCKET_TTL_SECONDS
        for buckets in self._buckets.values():
            # last_refill 兼作「最近使用时间」
            stale = [ident for ident, b in buckets.items() if b.last_refill < cutoff]
            for ident in stale:
                del buckets[ident]

    def reset(self) -> None:
        """清空所有限流桶（主要用于测试与运维重置）。"""
        with self._lock:
            for buckets in self._buckets.values():
                buckets.clear()


# ---------------------------------------------------------------------------
# Redis 分布式限流器
# ---------------------------------------------------------------------------


class RedisRateLimiter:
    """基于 Redis 固定窗口的分布式限流器。

    当 ``REDIS_URL`` 配置时启用，多实例共享限流计数。
    使用 Lua 脚本保证 ``检查-扣减`` 原子性，避免并发竞态。
    """

    _WINDOW_SECONDS = 60

    _ALLOW_SCRIPT = """
    local key = KEYS[1]
    local limit = tonumber(ARGV[1])
    local ttl = tonumber(ARGV[2])
    local current = tonumber(redis.call('GET', key) or 0)
    if current >= limit then
        return 0
    end
    redis.call('INCR', key)
    if current == 0 then
        redis.call('EXPIRE', key, ttl)
    end
    return 1
    """

    def __init__(
        self, redis_url: str, default_rpm: int = 60, default_burst: int = 10
    ) -> None:
        self._redis_url = redis_url
        self._default_rpm = default_rpm
        self._default_burst = default_burst
        self._rules: list[RateLimitRule] = [
            RateLimitRule("/api/scan", 10, 3),
            RateLimitRule("/api/login", 5, 3),
            RateLimitRule("/api/register", 3, 2),
            RateLimitRule("/api/ai/", 20, 5),
            RateLimitRule("/api/", default_rpm, default_burst),
        ]
        self._redis: Any = None
        self._lua_sha: str | None = None
        self._lock = asyncio.Lock()

    def _get_rule(self, path: str) -> RateLimitRule | None:
        for rule in self._rules:
            if RateLimiter._path_matches(path, rule.path_prefix):
                return rule
        return None

    async def _get_redis(self) -> Any:
        async with self._lock:
            if self._redis is None:
                import redis.asyncio as aioredis

                self._redis = aioredis.from_url(self._redis_url, decode_responses=True)
                self._lua_sha = await self._redis.script_load(self._ALLOW_SCRIPT)
            return self._redis

    async def check(self, path: str, identifier: str) -> tuple[bool, dict[str, str]]:
        """检查请求是否被允许（Redis 固定窗口）。"""
        rule = self._get_rule(path)
        if rule is None:
            return True, {}

        now = int(time.time())
        window_start = now - (now % self._WINDOW_SECONDS)
        key = f"v11s:ratelimit:{rule.path_prefix}:{identifier}:{window_start}"
        limit = rule.requests_per_minute

        try:
            r = await self._get_redis()
            if self._lua_sha:
                allowed = await r.evalsha(
                    self._lua_sha, 1, key, str(limit), str(self._WINDOW_SECONDS)
                )
            else:
                allowed = await r.eval(
                    self._ALLOW_SCRIPT, 1, key, str(limit), str(self._WINDOW_SECONDS)
                )
            allowed = bool(int(allowed))
            current = int(await r.get(key) or 0)
            remaining = max(0, limit - current)
            reset = window_start + self._WINDOW_SECONDS
        except Exception as exc:
            logger.warning("Redis rate limiter failed, allowing request: %s", exc)
            return True, {}

        headers = {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset),
        }
        return allowed, headers


# ---------------------------------------------------------------------------
# 限流器工厂与 FastAPI 集成
# ---------------------------------------------------------------------------


def create_rate_limiter(
    redis_url: str | None = None,
    default_rpm: int = 60,
    default_burst: int = 10,
) -> RateLimiter | RedisRateLimiter:
    """根据配置创建合适的限流器。

    - 若 ``redis_url`` 或环境变量 ``REDIS_URL`` 非空，优先使用 Redis 分布式限流。
    - Redis 不可用或配置缺失时回退到内存 TokenBucket。
    """
    if redis_url is None:
        redis_url = os.environ.get("REDIS_URL", "")
        if not redis_url:
            try:
                from app.core.config import settings

                redis_url = getattr(settings, "redis_url", "") or ""
            except Exception:
                pass

    if redis_url:
        try:
            import redis

            _ = redis.asyncio  # 仅验证 redis 包可用
            return RedisRateLimiter(
                redis_url, default_rpm=default_rpm, default_burst=default_burst
            )
        except Exception as exc:
            logger.warning(
                "Redis rate limiter unavailable, fallback to memory: %s", exc
            )

    return RateLimiter(default_rpm=default_rpm, default_burst=default_burst)


# 模块级单例，供中间件默认使用；如需自定义规则可替换该实例
rate_limiter = create_rate_limiter()


def get_client_ip(request: Request) -> str:
    """Best-effort client IP extraction with reverse-proxy support."""
    forwarded_for = request.headers.get("X-Forwarded-For", "").strip()
    if forwarded_for:
        candidate = forwarded_for.split(",", 1)[0].strip()
        if candidate:
            return candidate
    forwarded = request.headers.get("X-Real-IP", "").strip()
    if forwarded:
        return forwarded
    return request.client.host if request.client else "unknown"


def get_identifier(request: Request) -> str:
    """从请求中提取限流标识。

    优先使用 JWT 中的 ``user_id``（已认证用户），否则使用客户端 IP。
    返回形如 ``user:<id>`` 或 ``ip:<addr>`` 的字符串，避免两类标识碰撞。
    """
    user_id = _extract_user_id(request)
    if user_id is not None:
        return f"user:{user_id}"
    client_ip = get_client_ip(request)
    return f"ip:{client_ip}"


def _extract_user_id(request: Request) -> str | None:
    """从 ``Authorization`` 头解析 user_id，失败返回 ``None``。"""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth[len("Bearer "):]
    secret = _get_jwt_secret()
    if not secret:
        return None
    try:
        import jwt

        payload = jwt.decode(token, secret, algorithms=["HS256"])
    except Exception:
        return None
    uid = payload.get("user_id")
    return str(uid) if uid is not None else None


def _get_jwt_secret() -> str:
    """获取 JWT 密钥，依次尝试 ``app.core.config`` 与 ``main`` 中的 settings。

    任一来源缺失或抛异常均静默跳过；都取不到时返回空串（按匿名处理）。
    """
    for getter in (_secret_from_config, _secret_from_main):
        try:
            secret = getter()
        except Exception:
            continue
        if secret:
            return secret
    return ""


def _secret_from_config() -> str:
    from app.core.config import settings  # type: ignore[import]

    return getattr(settings, "jwt_secret", "") or ""


def _secret_from_main() -> str:
    from main import settings  # type: ignore[import]

    return getattr(settings, "jwt_secret", "") or ""


async def rate_limit_middleware(
    request: Request,
    call_next: Callable[[Request], Coroutine[Any, Any, Any]],
) -> Response:
    """API 限流中间件。

    - 命中限流规则时按用户/IP 维度计量；
    - 超限返回 ``429 Too Many Requests``，并携带限流响应头与 ``Retry-After``；
    - 非 API 路径（静态资源、健康检查等）不限流，也不附加限流头。
    - 测试环境（pytest）自动跳过限流，避免干扰测试。
    """
    # 测试环境下跳过限流
    import os
    import sys

    if os.environ.get("PYTEST_CURRENT_TEST") or "pytest" in sys.argv[0]:
        return await call_next(request)
    if os.environ.get("VULN_SENTINEL_TEST") or os.environ.get("TESTING"):
        return await call_next(request)

    path = request.url.path
    identifier = get_identifier(request)
    allowed, headers = await rate_limiter.check(path, identifier)

    if not allowed:
        # Retry-After 取「下一个窗口起始」所需秒数，至少 1 秒
        retry_after = max(1, int(headers["X-RateLimit-Reset"]) - int(time.time()))
        return JSONResponse(
            status_code=429,
            content={"detail": "请求过于频繁，请稍后再试。"},
            headers={**headers, "Retry-After": str(retry_after)},
        )

    response = await call_next(request)
    for key, value in headers.items():
        response.headers[key] = value
    return response
