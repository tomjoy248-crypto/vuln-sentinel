"""数据保留策略服务测试。

测试 app/services/data_retention.py 的核心功能：
- 按保留期清理过期扫描记录及关联 finding_feedback（级联删除）
- 清理审计日志、积分使用日志
- scan_progress 表不存在时跳过（skipped=True）
- run_retention_policy 汇总各清理任务并返回 total_deleted
- 自定义 days 参数控制清理阈值
- 空表场景不报错

直接调用服务函数（不通过 HTTP），参考 tests/test_user_lifecycle.py 的测试模式。
"""

import os
import sys
import uuid
from datetime import datetime, timedelta

os.environ["DB_DIR"] = "/tmp/v11-test"
os.environ["DB_NAME"] = "test.db"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import main  # noqa: E402,F401  -- 导入 main 以初始化数据库路径与表结构
from app.db.session import get_db  # noqa: E402
from app.services import data_retention  # noqa: E402

_TIME_FMT = "%Y-%m-%d %H:%M:%S"


# ---------- 工具函数 ----------


def _now() -> str:
    """当前时间戳字符串。"""
    return datetime.now().strftime(_TIME_FMT)


def _days_ago(days: int) -> str:
    """N 天前的时间戳字符串。"""
    return (datetime.now() - timedelta(days=days)).strftime(_TIME_FMT)


def _clear_tables(*tables: str) -> None:
    """清空指定表的所有行，确保 deleted_count 断言确定论。"""
    conn = get_db()
    try:
        for table in tables:
            conn.execute(f"DELETE FROM {table}")
        conn.commit()
    finally:
        conn.close()


def _count(table: str, where: str = "", args: tuple = ()) -> int:
    """统计表中满足条件的行数。"""
    sql = f"SELECT COUNT(*) AS c FROM {table}"
    if where:
        sql += f" WHERE {where}"
    conn = get_db()
    try:
        return conn.execute(sql, args).fetchone()["c"]
    finally:
        conn.close()


def _insert_scan(created_at: str, user_id: int = 1) -> int:
    """插入一条扫描记录，返回 scan id。"""
    url = f"https://retention-test-{uuid.uuid4().hex[:8]}.example.com"
    conn = get_db()
    try:
        cur = conn.execute(
            "INSERT INTO scans (user_id, url, score, risk_level, findings_count, "
            "findings_json, summary_json, crawled_pages, scan_type, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (user_id, url, 80, "中风险", 1, "[]", "{}", 0, "test", created_at),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def _insert_audit_log(created_at: str, user_id: int = 1) -> int:
    """插入一条审计日志，返回 id。"""
    conn = get_db()
    try:
        cur = conn.execute(
            "INSERT INTO audit_logs (user_id, action, resource_type, resource_id, "
            "details_json, client_ip, request_id, created_at) VALUES (?,?,?,?,?,?,?,?)",
            (user_id, "login", "auth", str(user_id), "{}", "127.0.0.1", uuid.uuid4().hex, created_at),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def _insert_usage_log(created_at: str, user_id: int = 1) -> int:
    """插入一条积分使用日志，返回 id。"""
    conn = get_db()
    try:
        cur = conn.execute(
            "INSERT INTO usage_logs (user_id, action, amount, balance_after, scan_id, note, created_at) "
            "VALUES (?,?,?,?,?,?,?)",
            (user_id, "scan_cost", -1, 9, None, "retention-test", created_at),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def _insert_finding_feedback(scan_id: int, created_at: str, user_id: int = 1) -> int:
    """插入一条 finding 反馈，返回 id。"""
    conn = get_db()
    try:
        cur = conn.execute(
            "INSERT INTO finding_feedback (user_id, scan_id, finding_name, finding_type, "
            "is_false_positive, is_confirmed, created_at) VALUES (?,?,?,?,?,?,?)",
            (user_id, scan_id, "缺少 HSTS", "config", 1, 0, created_at),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def _drop_scan_progress() -> None:
    """确保 scan_progress 表不存在（恢复默认状态）。"""
    conn = get_db()
    try:
        conn.execute("DROP TABLE IF EXISTS scan_progress")
        conn.commit()
    finally:
        conn.close()


# ---------- cleanup_old_scans ----------


def test_cleanup_old_scans():
    """清理超过 90 天的扫描记录，保留新记录。"""
    _clear_tables("scans", "finding_feedback")
    old_ids = [_insert_scan(_days_ago(100)) for _ in range(3)]
    new_ids = [_insert_scan(_now()) for _ in range(2)]
    assert _count("scans") == 5

    result = data_retention.cleanup_old_scans(days=90)

    assert result["deleted_count"] == 3
    assert result["scans"] == 3
    assert result["finding_feedback"] == 0
    assert result["days"] == 90
    assert "cutoff" in result
    assert result.get("error") is not True
    # 旧记录已删除
    for scan_id in old_ids:
        assert _count("scans", "id = ?", (scan_id,)) == 0
    # 新记录保留
    for scan_id in new_ids:
        assert _count("scans", "id = ?", (scan_id,)) == 1
    assert _count("scans") == 2


# ---------- cleanup_old_audit_logs ----------


def test_cleanup_old_audit_logs():
    """清理超过 180 天的审计日志，保留新记录。"""
    _clear_tables("audit_logs")
    old_ids = [_insert_audit_log(_days_ago(200)) for _ in range(2)]
    new_ids = [_insert_audit_log(_days_ago(10)) for _ in range(3)]
    assert _count("audit_logs") == 5

    result = data_retention.cleanup_old_audit_logs(days=180)

    assert result["deleted_count"] == 2
    assert result["days"] == 180
    assert "cutoff" in result
    assert result.get("error") is not True
    for log_id in old_ids:
        assert _count("audit_logs", "id = ?", (log_id,)) == 0
    for log_id in new_ids:
        assert _count("audit_logs", "id = ?", (log_id,)) == 1
    assert _count("audit_logs") == 3


# ---------- cleanup_old_usage_logs ----------


def test_cleanup_old_usage_logs():
    """清理超过 60 天的积分使用日志，保留新记录。"""
    _clear_tables("usage_logs")
    old_ids = [_insert_usage_log(_days_ago(70)) for _ in range(4)]
    new_ids = [_insert_usage_log(_days_ago(5)) for _ in range(2)]
    assert _count("usage_logs") == 6

    result = data_retention.cleanup_old_usage_logs(days=60)

    assert result["deleted_count"] == 4
    assert result["days"] == 60
    assert "cutoff" in result
    assert result.get("error") is not True
    for log_id in old_ids:
        assert _count("usage_logs", "id = ?", (log_id,)) == 0
    for log_id in new_ids:
        assert _count("usage_logs", "id = ?", (log_id,)) == 1
    assert _count("usage_logs") == 2


# ---------- cleanup_old_scan_progress ----------


def test_cleanup_old_scan_progress():
    """scan_progress 表不存在时返回 skipped=True；存在时按保留期清理。"""
    _drop_scan_progress()

    # 表不存在：跳过清理
    result = data_retention.cleanup_old_scan_progress(days=7)
    assert result["skipped"] is True
    assert result["deleted_count"] == 0
    assert result["days"] == 7
    assert "cutoff" in result
    assert result.get("error") is not True

    # 表存在：按 created_at 清理过期记录
    conn = get_db()
    try:
        conn.execute(
            "CREATE TABLE scan_progress (id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "created_at TEXT, status TEXT)"
        )
        conn.execute("INSERT INTO scan_progress (created_at, status) VALUES (?, 'done')", (_days_ago(30),))
        conn.execute("INSERT INTO scan_progress (created_at, status) VALUES (?, 'running')", (_now(),))
        conn.commit()
    finally:
        conn.close()

    try:
        result2 = data_retention.cleanup_old_scan_progress(days=7)
        assert result2.get("skipped") is not True
        assert result2["deleted_count"] == 1
        assert _count("scan_progress") == 1
    finally:
        _drop_scan_progress()


# ---------- run_retention_policy ----------


def test_run_retention_policy():
    """run_retention_policy 汇总各清理任务并返回 total_deleted。"""
    _drop_scan_progress()
    _clear_tables("scans", "finding_feedback", "audit_logs", "usage_logs")

    # 过期数据
    old_scan = _insert_scan(_days_ago(100))
    _insert_finding_feedback(old_scan, _days_ago(100))
    _insert_finding_feedback(old_scan, _days_ago(100))
    for _ in range(3):
        _insert_audit_log(_days_ago(200))
    for _ in range(2):
        _insert_usage_log(_days_ago(70))
    # 新数据（不应被删除）
    new_scan = _insert_scan(_now())
    _insert_audit_log(_days_ago(5))
    _insert_usage_log(_days_ago(3))

    expected_scans = 1 + 2  # 1 scan + 2 finding_feedback
    expected_audit = 3
    expected_usage = 2
    expected_total = expected_scans + expected_audit + expected_usage

    result = data_retention.run_retention_policy()

    assert result["total_deleted"] == expected_total
    details = result["details"]
    assert set(details.keys()) == {"scans", "audit_logs", "usage_logs", "scan_progress"}
    assert details["scans"]["deleted_count"] == expected_scans
    assert details["scans"]["scans"] == 1
    assert details["scans"]["finding_feedback"] == 2
    assert details["audit_logs"]["deleted_count"] == expected_audit
    assert details["usage_logs"]["deleted_count"] == expected_usage
    assert details["scan_progress"]["skipped"] is True
    assert details["scan_progress"]["deleted_count"] == 0
    # 新数据保留
    assert _count("scans", "id = ?", (new_scan,)) == 1
    assert _count("audit_logs") == 1
    assert _count("usage_logs") == 1


# ---------- 级联删除 finding_feedback ----------


def test_cleanup_scans_with_finding_feedback():
    """清理旧扫描时级联删除关联的 finding_feedback（依据 scan 的 created_at）。"""
    _clear_tables("scans", "finding_feedback")
    # 旧扫描 + 关联反馈（反馈本身时间戳为"现在"，但应随旧扫描一起删除）
    old_scan = _insert_scan(_days_ago(100))
    _insert_finding_feedback(old_scan, _now())
    _insert_finding_feedback(old_scan, _now())
    # 新扫描 + 关联反馈
    new_scan = _insert_scan(_now())
    new_fb = _insert_finding_feedback(new_scan, _now())
    assert _count("scans") == 2
    assert _count("finding_feedback") == 3

    result = data_retention.cleanup_old_scans(days=90)

    assert result["scans"] == 1
    assert result["finding_feedback"] == 2
    assert result["deleted_count"] == 3  # 1 scan + 2 feedback
    # 旧扫描及其反馈被删除
    assert _count("scans", "id = ?", (old_scan,)) == 0
    assert _count("finding_feedback", "scan_id = ?", (old_scan,)) == 0
    # 新扫描及其反馈保留
    assert _count("scans", "id = ?", (new_scan,)) == 1
    assert _count("finding_feedback", "id = ?", (new_fb,)) == 1
    assert _count("finding_feedback") == 1


# ---------- 自定义 days 参数 ----------


def test_custom_days_parameter():
    """自定义 days 参数控制清理阈值。"""
    _clear_tables("scans", "finding_feedback")
    scan_20 = _insert_scan(_days_ago(20))
    scan_50 = _insert_scan(_days_ago(50))
    scan_100 = _insert_scan(_days_ago(100))
    assert _count("scans") == 3

    # days=40：删除超过 40 天的（50天、100天），保留 20天
    r1 = data_retention.cleanup_old_scans(days=40)
    assert r1["scans"] == 2
    assert r1["days"] == 40
    assert _count("scans", "id = ?", (scan_20,)) == 1
    assert _count("scans", "id = ?", (scan_50,)) == 0
    assert _count("scans", "id = ?", (scan_100,)) == 0
    assert _count("scans") == 1

    # days=10：再删除超过 10 天的（20天）
    r2 = data_retention.cleanup_old_scans(days=10)
    assert r2["scans"] == 1
    assert r2["days"] == 10
    assert _count("scans", "id = ?", (scan_20,)) == 0
    assert _count("scans") == 0


# ---------- 空表场景 ----------


def test_cleanup_no_data():
    """空表时清理函数不报错且 deleted_count=0。"""
    _clear_tables("scans", "finding_feedback", "audit_logs", "usage_logs")

    r_scans = data_retention.cleanup_old_scans(days=90)
    assert r_scans["deleted_count"] == 0
    assert r_scans["scans"] == 0
    assert r_scans["finding_feedback"] == 0
    assert r_scans.get("error") is not True

    r_audit = data_retention.cleanup_old_audit_logs(days=180)
    assert r_audit["deleted_count"] == 0
    assert r_audit.get("error") is not True

    r_usage = data_retention.cleanup_old_usage_logs(days=60)
    assert r_usage["deleted_count"] == 0
    assert r_usage.get("error") is not True
