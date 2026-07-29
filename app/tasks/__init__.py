"""异步扫描任务队列模块。

提供基于 asyncio 的扫描任务管理能力，支持后台提交、进度跟踪、
超时取消与并发数限制，无需 Redis / Celery 等外部依赖。

核心组件:
    - ScanTaskManager: 任务队列管理器（提交 / 查询 / 取消 / 统计）
    - ScanTask: 扫描任务数据结构（状态、进度、结果）
    - TaskStatus: 任务状态枚举（PENDING / RUNNING / COMPLETED ...）

使用方式::

    from app.tasks import ScanTaskManager, TaskStatus

    manager = ScanTaskManager(max_concurrent=3, task_timeout=300)
    task_id = await manager.submit(
        url="https://example.com",
        user_id=1,
        depth="standard",
        scan_func=run_plugin_scan,
    )
    status = manager.get_task_status(task_id)
"""

from app.tasks.manager import (
    ProgressCallback,
    ScanFunc,
    ScanTask,
    ScanTaskManager,
    TaskStatus,
)

__all__ = [
    "ScanTaskManager",
    "ScanTask",
    "TaskStatus",
    "ProgressCallback",
    "ScanFunc",
]
