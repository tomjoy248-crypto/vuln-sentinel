"""异步扫描队列测试。"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from app.services.scan_queue import MemoryScanQueue, ScanTask, generate_task_id


async def _slow_runner(task: ScanTask) -> dict:
    await asyncio.sleep(0.2)
    return {"url": task.url, "done": True}


async def _fast_runner(task: ScanTask) -> dict:
    return {"url": task.url, "done": True}


@pytest.mark.asyncio
async def test_memory_queue_submit_and_status():
    queue = MemoryScanQueue(max_workers=1)
    await queue.start_worker(_fast_runner)
    try:
        task = ScanTask(
            task_id=generate_task_id(),
            user_id=1,
            url="https://example.com",
            depth="standard",
            deep=False,
            authorized=True,
        )
        task_id = await queue.submit(task)
        assert task_id == task.task_id

        # 等待任务完成
        for _ in range(50):
            result = await queue.get_status(task_id)
            if result and result.status == "completed":
                break
            await asyncio.sleep(0.05)

        result = await queue.get_status(task_id)
        assert result is not None
        assert result.status == "completed"
        assert result.result == {"url": "https://example.com", "done": True}
    finally:
        await queue.stop_worker()


@pytest.mark.asyncio
async def test_memory_queue_cancel_pending():
    queue = MemoryScanQueue(max_workers=1)
    await queue.start_worker(_slow_runner)
    try:
        task = ScanTask(
            task_id=generate_task_id(),
            user_id=1,
            url="https://example.com",
            depth="standard",
            deep=False,
            authorized=True,
        )
        task_id = await queue.submit(task)

        # 立即取消（大概率仍在 pending 或刚进入 running）
        cancelled = await queue.cancel_task(task_id)
        assert cancelled is True

        result = await queue.get_status(task_id)
        assert result is not None
        assert result.status == "cancelled"
    finally:
        await queue.stop_worker()


@pytest.mark.asyncio
async def test_memory_queue_cancel_nonexistent():
    queue = MemoryScanQueue(max_workers=1)
    assert await queue.cancel_task("SCAN-NOT-EXIST") is False


@pytest.mark.asyncio
async def test_memory_queue_cancel_already_completed():
    queue = MemoryScanQueue(max_workers=1)
    await queue.start_worker(_fast_runner)
    try:
        task = ScanTask(
            task_id=generate_task_id(),
            user_id=1,
            url="https://example.com",
            depth="standard",
            deep=False,
            authorized=True,
        )
        task_id = await queue.submit(task)
        for _ in range(50):
            result = await queue.get_status(task_id)
            if result and result.status == "completed":
                break
            await asyncio.sleep(0.05)

        assert await queue.cancel_task(task_id) is False
    finally:
        await queue.stop_worker()


@pytest.mark.asyncio
async def test_memory_queue_user_isolation():
    queue = MemoryScanQueue(max_workers=1)
    await queue.start_worker(_fast_runner)
    try:
        task1 = ScanTask(
            task_id=generate_task_id(),
            user_id=1,
            url="https://a.com",
            depth="standard",
            deep=False,
            authorized=True,
        )
        task2 = ScanTask(
            task_id=generate_task_id(),
            user_id=2,
            url="https://b.com",
            depth="standard",
            deep=False,
            authorized=True,
        )
        await queue.submit(task1)
        await queue.submit(task2)

        for _ in range(50):
            r1 = await queue.get_status(task1.task_id)
            r2 = await queue.get_status(task2.task_id)
            if r1 and r1.status == "completed" and r2 and r2.status == "completed":
                break
            await asyncio.sleep(0.05)

        assert (await queue.get_status(task1.task_id)).user_id == 1
        assert (await queue.get_status(task2.task_id)).user_id == 2
    finally:
        await queue.stop_worker()
