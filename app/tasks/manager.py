"""异步扫描任务队列。

提供基于 asyncio 的扫描任务管理，支持：
- 提交异步扫描任务
- 查询任务状态与进度
- 任务超时与取消
- 并发数限制

设计目标：
- 零外部依赖：不依赖 Redis / Celery，任务存储于进程内存字典，
  适合单实例 FastAPI 部署；后续如需横向扩展可替换为分布式后端。
- 非阻塞提交：submit() 立即返回 task_id，扫描在后台协程执行。
- 可控并发：通过 asyncio.Semaphore 限制同时在跑的扫描数量，
  避免单实例资源被打满。
- 进度可观测：scan_func 通过 progress_cb 回调上报 0-100 进度，
  前端可轮询 get_task_status() 渲染进度条。

使用方式::

    from app.tasks import ScanTaskManager

    manager = ScanTaskManager(max_concurrent=3, task_timeout=300)
    task_id = await manager.submit(
        url="https://example.com",
        user_id=1,
        depth="standard",
        scan_func=run_plugin_scan,
        headers={...},
        is_https=True,
    )
    # 轮询状态
    status = manager.get_task_status(task_id)
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional

logger = logging.getLogger("vuln_sentinel.tasks")

# 进度回调类型：接收 0-100 的进度值
ProgressCallback = Callable[[int], None]

# 扫描函数类型：async (url, *, progress_cb, **kwargs) -> dict
ScanFunc = Callable[..., Awaitable[Dict[str, Any]]]

# 终态集合：进入这些状态后任务不再流转
_TERMINAL_STATUSES = frozenset(
    {
        "completed",
        "failed",
        "cancelled",
        "timeout",
    }
)


class TaskStatus(str, Enum):
    """任务状态枚举。

    继承 ``str`` 以便直接 JSON 序列化与日志输出：
    - PENDING: 已提交，等待获取并发槽位
    - RUNNING: 已获取槽位，scan_func 执行中
    - COMPLETED: scan_func 正常返回，结果已存储
    - FAILED: scan_func 抛出异常
    - CANCELLED: 被显式取消
    - TIMEOUT: 执行超过 task_timeout 被中止
    """

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass
class ScanTask:
    """扫描任务描述。

    字段说明:
        task_id: 任务唯一标识（SCAN-XXXXXXXXXXXX）
        url: 扫描目标 URL
        user_id: 提交用户 ID（用于权限隔离与列表过滤）
        status: 当前任务状态
        depth: 扫描深度 quick / standard / deep
        progress: 进度百分比 0-100
        created_at: 提交时间（UTC ISO8601）
        started_at: 开始执行时间（UTC ISO8601）
        completed_at: 结束时间（UTC ISO8601），终态时填充
        result: 扫描结果字典，COMPLETED 时填充
        error: 错误信息，FAILED / TIMEOUT 时填充
    """

    task_id: str
    url: str
    user_id: Any
    status: TaskStatus = TaskStatus.PENDING
    depth: str = "standard"
    progress: int = 0
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，便于 API 序列化与日志输出。"""
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "url": self.url,
            "user_id": self.user_id,
            "depth": self.depth,
            "progress": self.progress,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "result": self.result,
            "error": self.error,
        }


def _now_iso() -> str:
    """返回当前 UTC 时间的 ISO8601 字符串。"""
    return datetime.now(timezone.utc).isoformat()


class ScanTaskManager:
    """异步扫描任务队列管理器。

    基于 asyncio 实现轻量级任务队列，无需 Redis / Celery 等外部依赖：

      1. submit() 提交任务 -> 创建 PENDING 任务记录 -> 调度后台协程
      2. 后台协程通过 Semaphore 限制并发数，获取槽位后置为 RUNNING
      3. 使用 asyncio.wait_for 包装 scan_func，超时置为 TIMEOUT
      4. scan_func 通过 progress_cb 回调上报 0-100 的进度
      5. 成功置为 COMPLETED 并存储结果；异常置为 FAILED
      6. cancel_task() 取消运行中的任务
      7. 自动清理历史终态任务，仅保留最近 max_retained 条

    线程安全：所有跨协程的字典变更通过 asyncio.Lock 串行化。
    由于 asyncio 单线程事件模型，同步读方法（get_task / list_tasks /
    get_stats）直接读取内存字典，无需加锁即可保证一致性。

    使用方式::

        manager = ScanTaskManager(max_concurrent=3, task_timeout=300)
        task_id = await manager.submit(url, user_id, depth, scan_func)
    """

    def __init__(
        self,
        max_concurrent: int = 3,
        task_timeout: float = 300,
        max_retained: int = 100,
    ) -> None:
        """初始化任务管理器。

        Args:
            max_concurrent: 最大并发扫描数，超过则排队等待
            task_timeout: 单任务超时时间（秒），超时置为 TIMEOUT
            max_retained: 终态任务最大保留数量，超出按完成时间清理最早的
        """
        if max_concurrent < 1:
            raise ValueError("max_concurrent 必须 >= 1")
        if task_timeout <= 0:
            raise ValueError("task_timeout 必须 > 0")
        if max_retained < 0:
            raise ValueError("max_retained 必须 >= 0")

        self._max_concurrent = max_concurrent
        self._task_timeout = task_timeout
        self._max_retained = max_retained

        # task_id -> ScanTask
        self._tasks: Dict[str, ScanTask] = {}
        # task_id -> asyncio.Task（后台协程句柄，用于取消）
        self._handles: Dict[str, asyncio.Task] = {}

        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # 提交任务
    # ------------------------------------------------------------------
    async def submit(
        self,
        url: str,
        user_id: Any,
        depth: str,
        scan_func: ScanFunc,
        **kwargs: Any,
    ) -> str:
        """提交一个异步扫描任务。

        创建 PENDING 任务记录并立即调度后台协程执行，不阻塞调用方。
        scan_func 将以 ``scan_func(url, progress_cb=<cb>, **kwargs)`` 形式调用，
        通过 progress_cb 上报 0-100 的进度。

        若 kwargs 中已包含 ``progress_cb``，管理器会将其与内部进度回调串联：
        内部回调更新任务进度后，再调用用户传入的回调。

        Args:
            url: 扫描目标 URL
            user_id: 提交用户 ID（用于过滤与权限隔离）
            depth: 扫描深度 quick / standard / deep
            scan_func: 异步扫描可调用对象，接收 url 与 progress_cb 等关键字参数，
                返回 dict 结果
            **kwargs: 透传给 scan_func 的额外参数（如 headers / is_https）

        Returns:
            新建任务的 task_id
        """
        task_id = f"SCAN-{uuid.uuid4().hex[:12].upper()}"
        task = ScanTask(
            task_id=task_id,
            url=url,
            user_id=user_id,
            depth=depth,
            status=TaskStatus.PENDING,
            progress=0,
            created_at=_now_iso(),
        )

        async with self._lock:
            self._tasks[task_id] = task

        # 调度后台协程：fire-and-forget，异常在 _run_task 内部消化
        handle = asyncio.create_task(self._run_task(task, scan_func, kwargs))
        self._handles[task_id] = handle

        logger.info(
            "Task submitted: id=%s url=%s depth=%s user=%s",
            task_id,
            url,
            depth,
            user_id,
        )
        return task_id

    # ------------------------------------------------------------------
    # 内部执行生命周期
    # ------------------------------------------------------------------
    async def _run_task(
        self,
        task: ScanTask,
        scan_func: ScanFunc,
        kwargs: Dict[str, Any],
    ) -> None:
        """单任务执行生命周期管理。

        流程:
            1. 获取并发槽位（Semaphore），排队期间状态保持 PENDING
            2. 置为 RUNNING，记录 started_at
            3. 注入 progress_cb 后用 asyncio.wait_for 包装 scan_func
            4. 按结果设置终态：COMPLETED / FAILED / TIMEOUT / CANCELLED
            5. 释放槽位（async with 自动释放）并触发历史任务清理
        """
        # 取出用户传入的进度回调（如有），与内部回调串联
        user_progress_cb = kwargs.pop("progress_cb", None)

        def _progress_cb(value: int) -> None:
            """内部进度回调：更新任务进度，再转发给用户回调。"""
            self._update_progress(task, value)
            if user_progress_cb is not None:
                try:
                    user_progress_cb(value)
                except Exception:
                    logger.warning(
                        "progress_cb: user callback raised, ignored",
                        exc_info=True,
                    )

        call_kwargs = dict(kwargs)
        call_kwargs["progress_cb"] = _progress_cb

        try:
            async with self._semaphore:
                # 排队期间若已被取消，直接退出，不占用执行槽位
                if task.status == TaskStatus.CANCELLED:
                    return

                task.status = TaskStatus.RUNNING
                task.started_at = _now_iso()
                task.progress = 0
                logger.info("Task running: id=%s", task.task_id)

                result = await asyncio.wait_for(
                    scan_func(task.url, **call_kwargs),
                    timeout=self._task_timeout,
                )

                # 兼容非 dict 返回值，统一存储为 dict
                task.result = (
                    result if isinstance(result, dict) else {"result": result}
                )
                task.progress = 100
                task.status = TaskStatus.COMPLETED
                logger.info("Task completed: id=%s", task.task_id)
        except asyncio.TimeoutError:
            task.status = TaskStatus.TIMEOUT
            task.error = f"任务执行超时（{self._task_timeout} 秒）"
            logger.warning("Task timeout: id=%s", task.task_id)
        except asyncio.CancelledError:
            task.status = TaskStatus.CANCELLED
            logger.info("Task cancelled: id=%s", task.task_id)
            raise
        except Exception as exc:
            task.status = TaskStatus.FAILED
            task.error = f"{type(exc).__name__}: {exc}"
            logger.exception("Task failed: id=%s", task.task_id)
        finally:
            task.completed_at = _now_iso()
            await self._cleanup()

    def _update_progress(self, task: ScanTask, value: int) -> None:
        """更新任务进度（0-100，越界自动钳制）。

        仅在 RUNNING 期间生效，避免终态任务被旧回调意外回退。
        """
        if task.status != TaskStatus.RUNNING:
            return
        try:
            clamped = max(0, min(100, int(value)))
        except (TypeError, ValueError):
            return
        # 进度单调不回退，避免乱序回调导致进度条倒退
        if clamped > task.progress:
            task.progress = clamped

    # ------------------------------------------------------------------
    # 查询
    # ------------------------------------------------------------------
    def get_task(self, task_id: str) -> Optional[ScanTask]:
        """按 task_id 获取任务对象。

        Args:
            task_id: 任务 ID

        Returns:
            ScanTask 实例，不存在则返回 None
        """
        return self._tasks.get(task_id)

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态字典（供 API 响应直接返回）。

        Args:
            task_id: 任务 ID

        Returns:
            状态字典。任务不存在时返回 ``{"found": False, ...}``。
        """
        task = self._tasks.get(task_id)
        if task is None:
            return {
                "task_id": task_id,
                "status": "not_found",
                "found": False,
                "progress": 0,
            }
        data = task.to_dict()
        data["found"] = True
        return data

    def list_tasks(
        self,
        user_id: Optional[Any] = None,
        status: Optional[TaskStatus] = None,
    ) -> List[ScanTask]:
        """列出任务，支持按用户与状态过滤。

        Args:
            user_id: 仅返回该用户的任务，None 表示不限制
            status: 仅返回该状态的任务，None 表示不限制。
                可传入 TaskStatus 枚举或字符串值（如 "running"）。

        Returns:
            匹配的任务列表，按提交时间倒序排列（最新在前）
        """
        normalized_status: Optional[TaskStatus] = None
        if status is not None:
            normalized_status = (
                status if isinstance(status, TaskStatus) else TaskStatus(status)
            )

        tasks = list(self._tasks.values())
        if user_id is not None:
            tasks = [t for t in tasks if t.user_id == user_id]
        if normalized_status is not None:
            tasks = [t for t in tasks if t.status == normalized_status]

        tasks.sort(key=lambda t: t.created_at or "", reverse=True)
        return tasks

    def get_stats(self) -> Dict[str, Any]:
        """返回队列统计信息。

        Returns:
            包含各状态计数与队列配置的字典
        """
        counts: Dict[str, int] = {s.value: 0 for s in TaskStatus}
        for task in self._tasks.values():
            counts[task.status.value] += 1

        return {
            "total": len(self._tasks),
            "pending": counts[TaskStatus.PENDING.value],
            "running": counts[TaskStatus.RUNNING.value],
            "completed": counts[TaskStatus.COMPLETED.value],
            "failed": counts[TaskStatus.FAILED.value],
            "cancelled": counts[TaskStatus.CANCELLED.value],
            "timeout": counts[TaskStatus.TIMEOUT.value],
            "max_concurrent": self._max_concurrent,
            "task_timeout": self._task_timeout,
        }

    # ------------------------------------------------------------------
    # 取消
    # ------------------------------------------------------------------
    async def cancel_task(self, task_id: str) -> bool:
        """取消运行中的任务。

        仅 PENDING / RUNNING 状态可取消。取消通过中断后台协程实现：

        - 若协程已启动（RUNNING），CancelledError 在 scan_func 执行处抛出，
          由 _run_task 的异常处理置为 CANCELLED；
        - 若协程尚未启动（PENDING，仍在排队等待信号量），asyncio 会将
          CancelledError 抛在协程入口，此时协程体（含异常处理与 finally）
          不会执行，因此这里显式将状态置为 CANCELLED 以保证状态一致。

        Args:
            task_id: 任务 ID

        Returns:
            True 表示已发起取消；False 表示任务不存在或已处于终态无法取消
        """
        async with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return False
            if task.status not in (TaskStatus.PENDING, TaskStatus.RUNNING):
                return False
            handle = self._handles.get(task_id)

        # 句柄已结束（刚完成）则无法取消
        if handle is None or handle.done():
            return False

        cancelled = handle.cancel()
        if not cancelled:
            return False

        # 防御性置态：覆盖「协程未启动即被取消」的场景。
        # 若协程已运行，_run_task 的 CancelledError 处理会幂等覆盖，无副作用。
        if task.status in (TaskStatus.PENDING, TaskStatus.RUNNING):
            task.status = TaskStatus.CANCELLED
            task.completed_at = _now_iso()

        logger.info("Task cancel requested: id=%s", task_id)
        return True

    # ------------------------------------------------------------------
    # 清理
    # ------------------------------------------------------------------
    async def _cleanup(self) -> None:
        """清理历史终态任务，仅保留最近 max_retained 条。

        策略:
            - 仅清理终态任务（COMPLETED / FAILED / CANCELLED / TIMEOUT），
              永不清理 PENDING / RUNNING 任务
            - 按完成时间（completed_at）升序删除最早的，直到数量降至 max_retained
            - 同步移除对应的 asyncio.Task 句柄引用
        """
        if self._max_retained == 0:
            return

        terminal = [
            t
            for t in self._tasks.values()
            if t.status.value in _TERMINAL_STATUSES
        ]
        if len(terminal) <= self._max_retained:
            return

        # 按完成时间排序，删除最早的一批
        terminal.sort(key=lambda t: t.completed_at or t.created_at or "")
        to_remove = terminal[: len(terminal) - self._max_retained]

        async with self._lock:
            for t in to_remove:
                self._tasks.pop(t.task_id, None)
                self._handles.pop(t.task_id, None)

        if to_remove:
            logger.debug(
                "Cleaned up %d terminal tasks (retained=%d)",
                len(to_remove),
                self._max_retained,
            )
