"""健康检查路由。

提供三个标准健康检查端点：
- /health/live: 存活探针（K8s livenessProbe），始终返回 200
- /health/ready: 就绪探针（K8s readinessProbe），检查 DB 等依赖
- /health/version: 版本信息

同时保持原有 /api/health 端点不变以兼容旧客户端。
"""

from __future__ import annotations

import os
import time
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.logging import get_request_id
from app.db.session import check_db_health

router = APIRouter(prefix="/health", tags=["health"])

# 服务启动时间
_SERVICE_START_TIME = time.time()


def _check_redis_health() -> bool:
    """检查 Redis 连通性。未配置 Redis 时返回 True（跳过检查）。"""
    redis_url = os.environ.get("REDIS_URL", "")
    if not redis_url:
        return True
    try:
        import redis

        r = redis.from_url(redis_url, socket_timeout=2, socket_connect_timeout=2)
        r.ping()
        return True
    except ImportError:
        # redis 库未安装，跳过检查
        return True
    except Exception:
        return False


@router.get("/live")
async def health_live() -> dict[str, Any]:
    """存活探针：只要进程在跑就返回 200。

    用于 K8s livenessProbe：失败则重启容器。
    """
    return {"status": "alive"}


@router.get("/ready")
async def health_ready() -> JSONResponse:
    """就绪探针：依赖健康时返回 200，退化时返回 503。"""
    db_ok = check_db_health()
    redis_ok = _check_redis_health()
    all_ok = db_ok and redis_ok
    return JSONResponse(
        status_code=200 if all_ok else 503,
        content={
            "status": "ready" if all_ok else "degraded",
            "checks": {
                "database": "ok" if db_ok else "error",
                "redis": "ok" if redis_ok else "skip",
            },
            "uptime_sec": int(time.time() - _SERVICE_START_TIME),
        },
    )


@router.get("/version")
async def health_version() -> dict[str, Any]:
    """版本信息端点。"""
    # 延迟导入避免循环依赖
    from main import settings

    return {
        "version": settings.app_version,
        "title": settings.app_title,
        "build_time": settings.build_time,
        "env": settings.env,
        "python": os.sys.version.split()[0],
    }


def get_health_summary() -> dict[str, Any]:
    """获取健康摘要（供 /api/health 兼容端点使用）。"""
    db_ok = check_db_health()
    from main import settings

    return {
        "status": "ok" if db_ok else "degraded",
        "version": settings.app_version,
        "title": settings.app_title,
        "db": "ok" if db_ok else "error",
        "uptime_sec": int(time.time() - _SERVICE_START_TIME),
        "request_id": get_request_id() or None,
    }
