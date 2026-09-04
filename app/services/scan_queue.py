"""异步扫描任务队列。

支持两种后端：
- 内存队列（默认，单进程/开发环境）
- Redis 队列（生产环境，通过 REDIS_URL 启用）

提供统一的 submit / status / result 接口，
让 deep 扫描等耗时任务可以异步执行并轮询进度。
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
import uuid
from abc import ABC, abstractmethod
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("vuln_sentinel.scan_queue")


@dataclass
class ScanTask:
    """扫描任务定义。"""

    task_id: str
    user_id: int
    url: str
    depth: str
    deep: bool
    authorized: bool
    auth_headers: dict[str, str] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "user_id": self.user_id,
            "url": self.url,
            "depth": self.depth,
            "deep": self.deep,
            "authorized": self.authorized,
            # Never expose session tokens through task status APIs or logs.
            "auth_headers": {key: "***REDACTED***" for key in self.auth_headers},
            "created_at": self.created_at,
        }


@dataclass
class ScanTaskResult:
    """扫描任务结果。"""

    task_id: str
    status: str  # pending / running / completed / failed / cancelled
    progress: int = 0  # 0-100
    stage: str = "queued"
    result: dict[str, Any] | None = None
    error: str | None = None
    user_id: int = 0
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "status": self.status,
            "progress": self.progress,
            "stage": self.stage,
            "result": self.result,
            "error": self.error,
            "user_id": self.user_id,
            "updated_at": self.updated_at,
        }


TaskRunner = Callable[[ScanTask], Coroutine[Any, Any, dict[str, Any]]]


class BaseScanQueue(ABC):
    """扫描队列基类。"""

    @abstractmethod
    async def submit(self, task: ScanTask) -> str:
        """提交任务，返回 task_id。"""
        ...

    @abstractmethod
    async def get_status(self, task_id: str) -> ScanTaskResult | None:
        """查询任务状态。"""
        ...

    @abstractmethod
    async def cancel_task(self, task_id: str) -> bool:
        """取消任务，返回是否成功。"""
        ...

    @abstractmethod
    async def start_worker(self, runner: TaskRunner) -> None:
        """启动后台工作线程。"""
        ...

    @abstractmethod
    async def stop_worker(self) -> None:
        """停止后台工作线程。"""
        ...


class MemoryScanQueue(BaseScanQueue):
    """内存版扫描队列。"""

    def __init__(self, max_workers: int = 2) -> None:
        self._queue: asyncio.Queue[ScanTask] = asyncio.Queue()
        self._results: dict[str, ScanTaskResult] = {}
        self._handles: dict[str, asyncio.Task] = {}
        self._max_workers = max_workers
        self._worker_tasks: list[asyncio.Task] = []
        self._runner: TaskRunner | None = None
        self._running = False

    async def submit(self, task: ScanTask) -> str:
        self._results[task.task_id] = ScanTaskResult(
            task_id=task.task_id,
            status="pending",
            stage="queued",
            user_id=task.user_id,
        )
        await self._queue.put(task)
        logger.info("Scan task queued: %s", task.task_id)
        return task.task_id

    async def get_status(self, task_id: str) -> ScanTaskResult | None:
        return self._results.get(task_id)

    async def cancel_task(self, task_id: str) -> bool:
        """取消任务。

        仅 pending / running 状态可取消；已完成或失败返回 False。
        """
        result = self._results.get(task_id)
        if result is None:
            return False
        if result.status not in ("pending", "running"):
            return False

        result.status = "cancelled"
        result.stage = "cancelled"
        result.progress = 0
        result.updated_at = time.time()

        handle = self._handles.pop(task_id, None)
        if handle and not handle.done():
            handle.cancel()
        logger.info("Scan task cancelled: %s", task_id)
        return True

    async def start_worker(self, runner: TaskRunner) -> None:
        if self._running:
            return
        self._runner = runner
        self._running = True
        for i in range(self._max_workers):
            self._worker_tasks.append(asyncio.create_task(self._worker_loop(i)))
        logger.info("Memory scan queue worker started (%d workers)", self._max_workers)

    async def stop_worker(self) -> None:
        self._running = False
        for t in self._worker_tasks:
            t.cancel()
        self._worker_tasks = []
        logger.info("Memory scan queue worker stopped")

    async def _worker_loop(self, worker_id: int) -> None:
        while self._running:
            try:
                task = await asyncio.wait_for(self._queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue

            result = self._results.get(task.task_id)
            if result and result.status == "cancelled":
                self._queue.task_done()
                continue
            if result:
                result.status = "running"
                result.stage = "scanning"
                result.updated_at = time.time()

            exec_task = asyncio.create_task(self._run_single_task(task))
            self._handles[task.task_id] = exec_task
            try:
                await exec_task
            except asyncio.CancelledError:
                logger.info("Scan task cancelled in worker: %s", task.task_id)
            finally:
                self._handles.pop(task.task_id, None)
                self._queue.task_done()

    async def _run_single_task(self, task: ScanTask) -> None:
        """执行单个扫描任务并更新结果状态。"""
        result = self._results.get(task.task_id)
        try:
            if self._runner is None:
                raise RuntimeError("Task runner not configured")
            data = await self._runner(task)
            if result and result.status not in ("cancelled",):
                result.status = "completed"
                result.progress = 100
                result.stage = "done"
                result.result = data
                result.updated_at = time.time()
            logger.info("Scan task completed: %s", task.task_id)
        except asyncio.CancelledError:
            if result:
                result.status = "cancelled"
                result.stage = "cancelled"
                result.error = "任务已取消"
                result.updated_at = time.time()
            logger.info("Scan task cancelled: %s", task.task_id)
            raise
        except Exception as e:
            logger.warning("Scan task failed: %s - %s", task.task_id, e)
            if result and result.status not in ("cancelled",):
                result.status = "failed"
                result.error = str(e)
                result.updated_at = time.time()


class RedisScanQueue(BaseScanQueue):
    """Redis 版扫描队列（生产环境）。

    需要安装 redis 包并通过 REDIS_URL 启用。
    """

    def __init__(self, redis_url: str, max_workers: int = 2) -> None:
        self._redis_url = redis_url
        self._max_workers = max_workers
        self._worker_tasks: list[asyncio.Task] = []
        self._runner: TaskRunner | None = None
        self._running = False
        self._redis: Any = None

    def _get_redis(self) -> Any:
        if self._redis is None:
            try:
                import redis.asyncio as aioredis
            except ImportError as e:
                raise RuntimeError("Redis queue requires 'redis' package") from e
            self._redis = aioredis.from_url(self._redis_url, decode_responses=True)
        return self._redis

    async def submit(self, task: ScanTask) -> str:
        r = self._get_redis()
        await r.lpush("scan_queue:pending", json.dumps(task.to_dict()))
        await self._set_result(
            task.task_id,
            ScanTaskResult(task.task_id, "pending", stage="queued", user_id=task.user_id),
        )
        return task.task_id

    async def get_status(self, task_id: str) -> ScanTaskResult | None:
        r = self._get_redis()
        data = await r.get(f"scan_queue:result:{task_id}")
        if not data:
            return None
        try:
            d = json.loads(data)
            return ScanTaskResult(**d)
        except Exception:
            return None

    async def cancel_task(self, task_id: str) -> bool:
        """取消任务。

        将 task_id 写入 Redis 取消集合，worker 在执行前/执行后会检查该集合。
        仅当任务结果仍存在且处于 pending / running 状态时才允许取消。
        """
        r = self._get_redis()
        result = await self.get_status(task_id)
        if result is None:
            return False
        if result.status not in ("pending", "running"):
            return False

        await r.sadd("scan_queue:cancelled", task_id)
        await r.expire("scan_queue:cancelled", 86400)
        result.status = "cancelled"
        result.stage = "cancelled"
        result.error = "任务已取消"
        result.updated_at = time.time()
        await self._set_result(task_id, result)
        logger.info("Redis scan task cancelled: %s", task_id)
        return True

    async def _is_cancelled(self, task_id: str) -> bool:
        r = self._get_redis()
        return bool(await r.sismember("scan_queue:cancelled", task_id))

    async def start_worker(self, runner: TaskRunner) -> None:
        if self._running:
            return
        self._runner = runner
        self._running = True
        for i in range(self._max_workers):
            self._worker_tasks.append(asyncio.create_task(self._worker_loop(i)))
        logger.info("Redis scan queue worker started (%d workers)", self._max_workers)

    async def stop_worker(self) -> None:
        self._running = False
        for t in self._worker_tasks:
            t.cancel()
        self._worker_tasks = []
        if self._redis:
            await self._redis.close()
        logger.info("Redis scan queue worker stopped")

    async def _worker_loop(self, worker_id: int) -> None:
        r = self._get_redis()
        while self._running:
            try:
                item = await r.brpop("scan_queue:pending", timeout=1)
                if not item:
                    continue
                task_data = json.loads(item[1])
                task = ScanTask(**task_data)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.warning("Redis queue pop failed: %s", e)
                await asyncio.sleep(1)
                continue

            if await self._is_cancelled(task.task_id):
                await self._set_result(
                    task.task_id,
                    ScanTaskResult(
                        task.task_id,
                        "cancelled",
                        stage="cancelled",
                        error="任务已取消",
                        user_id=task.user_id,
                    ),
                )
                continue

            await self._set_result(
                task.task_id,
                ScanTaskResult(task.task_id, "running", stage="scanning", user_id=task.user_id),
            )
            try:
                if self._runner is None:
                    raise RuntimeError("Task runner not configured")
                data = await self._runner(task)
                if await self._is_cancelled(task.task_id):
                    await self._set_result(
                        task.task_id,
                        ScanTaskResult(
                            task.task_id,
                            "cancelled",
                            stage="cancelled",
                            error="任务已取消",
                            user_id=task.user_id,
                        ),
                    )
                else:
                    await self._set_result(
                        task.task_id,
                        ScanTaskResult(
                            task.task_id, "completed", 100, "done", result=data, user_id=task.user_id
                        ),
                    )
                    logger.info("Redis scan task completed: %s", task.task_id)
            except asyncio.CancelledError:
                logger.info("Redis scan task cancelled in worker: %s", task.task_id)
                raise
            except Exception as e:
                logger.warning("Redis scan task failed: %s - %s", task.task_id, e)
                await self._set_result(
                    task.task_id,
                    ScanTaskResult(task.task_id, "failed", error=str(e), user_id=task.user_id),
                )

    async def list_user_tasks(self, user_id: int, limit: int = 50) -> list[ScanTaskResult]:
        """列出指定用户的任务结果（按更新时间倒序）。"""
        r = self._get_redis()
        results: list[ScanTaskResult] = []
        cursor: int = 0
        while True:
            cursor, keys = await r.scan(cursor, match="scan_queue:result:*", count=100)
            if keys:
                values = await r.mget(keys)
                for data in values:
                    if not data:
                        continue
                    try:
                        d = json.loads(data)
                        if d.get("user_id") == user_id:
                            results.append(ScanTaskResult(**d))
                    except Exception:
                        continue
            if cursor == 0:
                break
        results.sort(key=lambda x: x.updated_at, reverse=True)
        return results[:limit]

    async def _set_result(self, task_id: str, result: ScanTaskResult) -> None:
        r = self._get_redis()
        await r.setex(
            f"scan_queue:result:{task_id}",
            86400,  # 结果保留 24 小时
            json.dumps(result.to_dict()),
        )


_scan_queue: BaseScanQueue | None = None


def init_scan_queue(
    redis_url: str | None = None, max_workers: int = 2
) -> BaseScanQueue:
    """初始化扫描队列。"""
    global _scan_queue
    redis_url = redis_url or os.environ.get("REDIS_URL", "")
    if redis_url:
        _scan_queue = RedisScanQueue(redis_url, max_workers=max_workers)
        logger.info("Using Redis scan queue: %s", redis_url)
    else:
        _scan_queue = MemoryScanQueue(max_workers=max_workers)
        logger.info("Using memory scan queue")
    return _scan_queue


def get_scan_queue() -> BaseScanQueue:
    """获取当前扫描队列实例。"""
    if _scan_queue is None:
        return init_scan_queue()
    return _scan_queue


def generate_task_id() -> str:
    """生成任务 ID。"""
    return f"SCAN-{uuid.uuid4().hex[:12].upper()}"
