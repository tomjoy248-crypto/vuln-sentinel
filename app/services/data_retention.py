"""数据保留策略服务。

按可配置保留期定时清理过期数据，避免数据库无限膨胀：
- 扫描记录及相关 findings（默认 90 天）
- 审计日志（默认 180 天）
- 积分使用日志（默认 60 天）
- 扫描进度记录（默认 7 天）

设计要点：
- 统一通过 app.db.session.get_db() 获取连接，与业务层一致
- 所有 SQL 使用参数化查询（? 占位符）防止 SQL 注入
- 每个清理函数返回 dict，至少包含 deleted_count 字段
- run_retention_policy() 作为统一入口，供 APScheduler 定时调用

说明：当前项目使用 SQLite（原生 SQL），created_at 以 "YYYY-MM-DD HH:MM:SS" 文本
存储，故按字符串字面量比较即可正确过滤时间范围。切换到 PostgreSQL 时，仅需将
比较表达式调整为 created_at < %s::timestamp（psycopg2 占位符）。
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from app.db.session import get_db

logger = logging.getLogger("vuln_sentinel.retention")


def _cutoff(days: int) -> str:
    """计算 N 天前的时间戳字符串。

    与入库格式保持一致（YYYY-MM-DD HH:MM:SS），便于直接与 created_at 文本列比较。

    Args:
        days: 保留天数

    Returns:
        截止时间字符串
    """
    return (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")


def _table_exists(conn: Any, table_name: str) -> bool:
    """检查表是否存在（SQLite 专用，用于可选表的防御性清理）。

    Args:
        conn: 数据库连接
        table_name: 表名

    Returns:
        表存在返回 True
    """
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    ).fetchone()
    return row is not None


def cleanup_old_scans(days: int = 90) -> dict[str, Any]:
    """清理指定天数之前的扫描记录及相关 findings。

    扫描结果（findings）以 JSON 形式存储在 scans.findings_json 中，
    删除 scans 行即同步删除其 findings；同时清理 finding_feedback 表中
    关联到这些扫描的反馈记录，避免产生孤儿数据。

    Args:
        days: 保留天数，早于该天数的记录将被删除

    Returns:
        包含 deleted_count 等统计信息的字典
    """
    cutoff = _cutoff(days)
    deleted_feedback = 0
    deleted_scans = 0
    conn = get_db()
    try:
        # 先清理关联的 finding 反馈（依赖待删除的 scan id）
        if _table_exists(conn, "finding_feedback"):
            cur_fb = conn.execute(
                "DELETE FROM finding_feedback WHERE scan_id IN "
                "(SELECT id FROM scans WHERE created_at < ?)",
                (cutoff,),
            )
            deleted_feedback = cur_fb.rowcount or 0
        # 再清理扫描记录本身（含 findings_json）
        cur_scans = conn.execute(
            "DELETE FROM scans WHERE created_at < ?",
            (cutoff,),
        )
        deleted_scans = cur_scans.rowcount or 0
        conn.commit()
    except Exception:
        conn.rollback()
        logger.exception("清理扫描记录失败 (days=%d)", days)
        return {
            "deleted_count": 0,
            "scans": 0,
            "finding_feedback": 0,
            "days": days,
            "error": True,
        }
    finally:
        conn.close()

    total = deleted_scans + deleted_feedback
    logger.info(
        "清理扫描记录完成: scans=%d, finding_feedback=%d, total=%d (cutoff=%s)",
        deleted_scans,
        deleted_feedback,
        total,
        cutoff,
    )
    return {
        "deleted_count": total,
        "scans": deleted_scans,
        "finding_feedback": deleted_feedback,
        "days": days,
        "cutoff": cutoff,
    }


def cleanup_old_audit_logs(days: int = 180) -> dict[str, Any]:
    """清理指定天数之前的审计日志。

    Args:
        days: 保留天数

    Returns:
        包含 deleted_count 等统计信息的字典
    """
    cutoff = _cutoff(days)
    conn = get_db()
    try:
        cur = conn.execute(
            "DELETE FROM audit_logs WHERE created_at < ?",
            (cutoff,),
        )
        deleted = cur.rowcount or 0
        conn.commit()
    except Exception:
        conn.rollback()
        logger.exception("清理审计日志失败 (days=%d)", days)
        return {"deleted_count": 0, "days": days, "error": True}
    finally:
        conn.close()

    logger.info("清理审计日志完成: deleted=%d (cutoff=%s)", deleted, cutoff)
    return {"deleted_count": deleted, "days": days, "cutoff": cutoff}


def cleanup_old_usage_logs(days: int = 60) -> dict[str, Any]:
    """清理指定天数之前的积分使用日志。

    Args:
        days: 保留天数

    Returns:
        包含 deleted_count 等统计信息的字典
    """
    cutoff = _cutoff(days)
    conn = get_db()
    try:
        cur = conn.execute(
            "DELETE FROM usage_logs WHERE created_at < ?",
            (cutoff,),
        )
        deleted = cur.rowcount or 0
        conn.commit()
    except Exception:
        conn.rollback()
        logger.exception("清理使用日志失败 (days=%d)", days)
        return {"deleted_count": 0, "days": days, "error": True}
    finally:
        conn.close()

    logger.info("清理使用日志完成: deleted=%d (cutoff=%s)", deleted, cutoff)
    return {"deleted_count": deleted, "days": days, "cutoff": cutoff}


def cleanup_old_scan_progress(days: int = 7) -> dict[str, Any]:
    """清理指定天数之前的扫描进度记录。

    当前扫描进度（_scan_progress）以内存结构保存并自带 TTL 清理；
    此函数面向未来：当扫描进度持久化为 scan_progress 表后自动生效。
    若表尚未存在则跳过清理，返回 deleted_count=0。

    Args:
        days: 保留天数

    Returns:
        包含 deleted_count 等统计信息的字典
    """
    cutoff = _cutoff(days)
    conn = get_db()
    try:
        # scan_progress 当前为内存结构；若未来持久化为表则在此清理
        if not _table_exists(conn, "scan_progress"):
            logger.debug("scan_progress 表不存在，跳过清理（当前为内存进度）")
            return {
                "deleted_count": 0,
                "days": days,
                "cutoff": cutoff,
                "skipped": True,
            }
        cur = conn.execute(
            "DELETE FROM scan_progress WHERE created_at < ?",
            (cutoff,),
        )
        deleted = cur.rowcount or 0
        conn.commit()
    except Exception:
        conn.rollback()
        logger.exception("清理扫描进度记录失败 (days=%d)", days)
        return {"deleted_count": 0, "days": days, "error": True}
    finally:
        conn.close()

    logger.info("清理扫描进度记录完成: deleted=%d (cutoff=%s)", deleted, cutoff)
    return {"deleted_count": deleted, "days": days, "cutoff": cutoff}


def run_retention_policy() -> dict[str, Any]:
    """统一执行数据保留策略。

    依次调用各清理函数，汇总删除统计。可作为定时任务（APScheduler）入口。

    Returns:
        包含 total_deleted 与各分项 details 的字典
    """
    logger.info("开始执行数据保留策略清理...")
    results = {
        "scans": cleanup_old_scans(),
        "audit_logs": cleanup_old_audit_logs(),
        "usage_logs": cleanup_old_usage_logs(),
        "scan_progress": cleanup_old_scan_progress(),
    }
    total = sum(r.get("deleted_count", 0) for r in results.values())
    logger.info("数据保留策略清理完成，共删除 %d 条记录", total)
    return {"total_deleted": total, "details": results}
