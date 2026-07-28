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
from typing import Any, Dict

from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse

from app.core.logging import get_request_id
from app.db.session import check_db_health

router = APIRouter(prefix="/health", tags=["health"])

# 服务启动时间
_SERVICE_START_TIME = time.time()


@router.get("/live")
async def health_live() -> Dict[str, Any]:
    """存活探针：只要进程在跑就返回 200。

    用于 K8s livenessProbe：失败则重启容器。
    """
    return {"status": "alive"}


@router.get("/ready")
async def health_ready(response: Response) -> JSONResponse:
    """就绪探针：检查数据库等依赖是否就绪。

    用于 K8s readinessProbe：失败则不接入流量。
    """
    db_ok = check_db_health()
    status_code = 200 if db_ok else 503
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if db_ok else "not_ready",
            "checks": {
                "database": "ok" if db_ok else "error",
            },
            "uptime_sec": int(time.time() - _SERVICE_START_TIME),
        },
    )


@router.get("/version")
async def health_version() -> Dict[str, Any]:
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


def get_health_summary() -> Dict[str, Any]:
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
