"""修复工单仓库：状态机 + 事件时间线"""

from datetime import datetime
from typing import Any

from app.core.exceptions import BusinessException
from app.db.session import get_db


class TicketStatus:
    PENDING = "pending"
    CONFIRMED = "confirmed"
    APPLYING = "applying"
    IN_PROGRESS = "in_progress"
    FIXED = "fixed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    IGNORED = "ignored"


# 状态机：key 为当前状态，value 为允许转移到的目标状态集合
ALLOWED_TRANSITIONS = {
    TicketStatus.PENDING: {
        TicketStatus.PENDING,
        TicketStatus.CONFIRMED,
        TicketStatus.IGNORED,
    },
    TicketStatus.CONFIRMED: {
        TicketStatus.CONFIRMED,
        TicketStatus.APPLYING,
        TicketStatus.IN_PROGRESS,
        TicketStatus.IGNORED,
    },
    TicketStatus.APPLYING: {
        TicketStatus.APPLYING,
        TicketStatus.FIXED,
        TicketStatus.FAILED,
        TicketStatus.ROLLED_BACK,
    },
    TicketStatus.IN_PROGRESS: {
        TicketStatus.IN_PROGRESS,
        TicketStatus.FIXED,
        TicketStatus.FAILED,
        TicketStatus.ROLLED_BACK,
    },
    TicketStatus.FIXED: {TicketStatus.FIXED, TicketStatus.ROLLED_BACK},
    TicketStatus.FAILED: {
        TicketStatus.FAILED,
        TicketStatus.APPLYING,
        TicketStatus.IN_PROGRESS,
        TicketStatus.ROLLED_BACK,
        TicketStatus.IGNORED,
    },
    TicketStatus.ROLLED_BACK: {
        TicketStatus.ROLLED_BACK,
        TicketStatus.APPLYING,
        TicketStatus.IN_PROGRESS,
        TicketStatus.IGNORED,
    },
    TicketStatus.IGNORED: {TicketStatus.IGNORED, TicketStatus.PENDING},
}


def _ensure_ticket_events_table(conn) -> None:
    """确保事件表存在（用于兼容尚未执行 init_db 的场景）。"""
    conn.execute(
        """CREATE TABLE IF NOT EXISTS ticket_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            from_status TEXT,
            to_status TEXT,
            note TEXT,
            created_at TEXT
        )"""
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_ticket_events_ticket_id ON ticket_events(ticket_id)"
    )


def _record_ticket_event(
    conn,
    ticket_id: int,
    user_id: int,
    from_status: str | None,
    to_status: str | None,
    note: str | None = None,
) -> None:
    """记录一次状态转移事件。"""
    _ensure_ticket_events_table(conn)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        """INSERT INTO ticket_events
           (ticket_id, user_id, from_status, to_status, note, created_at)
           VALUES (?,?,?,?,?,?)""",
        (ticket_id, user_id, from_status or "", to_status or "", note or "", now),
    )


def _ticket_events(ticket_id: int) -> list[dict[str, Any]]:
    """获取指定工单的所有事件，按时间升序排列。"""
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT * FROM ticket_events WHERE ticket_id=? ORDER BY id ASC",
            (ticket_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def create_fix_ticket(
    user_id: int,
    scan_id: int | None,
    finding_name: str,
    severity: str,
    fix_code: str | None = None,
    notes: str | None = None,
    finding_id: str | None = None,
    finding_type: str | None = None,
    url: str | None = None,
    target_host: str | None = None,
) -> int:
    conn = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cur = conn.execute(
            """INSERT INTO fix_tickets (
                user_id, scan_id, finding_name, severity, status,
                fix_code, notes, finding_id, finding_type, url, target_host,
                created_at, updated_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                user_id,
                scan_id,
                finding_name,
                severity,
                TicketStatus.PENDING,
                fix_code,
                notes,
                finding_id or "",
                finding_type or "",
                url or "",
                target_host or "",
                now,
                now,
            ),
        )
        ticket_id = cur.lastrowid
        _record_ticket_event(
            conn, ticket_id, user_id, "", TicketStatus.PENDING, "创建工单"
        )
        conn.commit()
        return ticket_id
    finally:
        conn.close()


def get_fix_tickets(user_id: int, status: str | None = None) -> list[dict[str, Any]]:
    conn = get_db()
    try:
        if status:
            rows = conn.execute(
                "SELECT * FROM fix_tickets WHERE user_id=? AND status=? ORDER BY id DESC",
                (user_id, status),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM fix_tickets WHERE user_id=? ORDER BY id DESC",
                (user_id,),
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_fix_ticket(ticket_id: int, user_id: int) -> dict[str, Any] | None:
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT * FROM fix_tickets WHERE id=? AND user_id=?",
            (ticket_id, user_id),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def update_fix_ticket(
    ticket_id: int,
    user_id: int,
    status: str | None = None,
    fix_code: str | None = None,
    notes: str | None = None,
    applied_at: str | None = None,
    rolled_back_at: str | None = None,
    rollback_code: str | None = None,
    verification_scan_id: int | None = None,
    diff_summary: str | None = None,
) -> bool:
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT status FROM fix_tickets WHERE id=? AND user_id=?",
            (ticket_id, user_id),
        ).fetchone()
        if not row:
            return False

        current_status = row["status"]
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fields: list[str] = []
        params: list[Any] = []

        if status is not None and status != current_status:
            allowed = ALLOWED_TRANSITIONS.get(current_status, set())
            if status not in allowed:
                raise BusinessException(
                    f"无效的状态转换: {current_status} -> {status}",
                    code="INVALID_TRANSITION",
                )
            fields.append("status=?")
            params.append(status)
            _record_ticket_event(conn, ticket_id, user_id, current_status, status)
            if status == TicketStatus.FIXED:
                fields.append("fixed_at=?")
                params.append(now)
            if status == TicketStatus.APPLYING:
                fields.append("applied_at=?")
                params.append(now)
            if status == TicketStatus.ROLLED_BACK:
                fields.append("rolled_back_at=?")
                params.append(now)

        if fix_code is not None:
            fields.append("fix_code=?")
            params.append(fix_code)
        if notes is not None:
            fields.append("notes=?")
            params.append(notes)
        if applied_at is not None:
            fields.append("applied_at=?")
            params.append(applied_at)
        if rolled_back_at is not None:
            fields.append("rolled_back_at=?")
            params.append(rolled_back_at)
        if rollback_code is not None:
            fields.append("rollback_code=?")
            params.append(rollback_code)
        if verification_scan_id is not None:
            fields.append("verification_scan_id=?")
            params.append(verification_scan_id)
        if diff_summary is not None:
            fields.append("diff_summary=?")
            params.append(diff_summary)

        if not fields:
            return True

        fields.append("updated_at=?")
        params.append(now)
        params.extend([ticket_id, user_id])

        conn.execute(
            f"UPDATE fix_tickets SET {', '.join(fields)} WHERE id=? AND user_id=?",  # nosec B608 - fields 列表由硬编码字段名构建，值通过参数化查询传递
            params,
        )
        conn.commit()
        n = conn.total_changes
        return n > 0
    finally:
        conn.close()


def delete_fix_ticket(ticket_id: int, user_id: int) -> bool:
    conn = get_db()
    try:
        cur = conn.execute(
            "DELETE FROM fix_tickets WHERE id=? AND user_id=?", (ticket_id, user_id)
        )
        conn.commit()
        n = cur.rowcount
        return n > 0
    finally:
        conn.close()


def auto_create_fix_tickets(
    user_id: int, scan_id: int, findings: list, target_host: str = ""
) -> int:
    """为 high/critical finding 自动创建工单，跳过已存在的同名待处理工单。

    优化：先一次性查出当前用户所有 pending 工单的 finding_name（set 缓存），
    避免对每条 finding 单独查询（消除 N+1）。
    """
    candidates: list[tuple[str, str, str, str, str, str, str]] = []
    for f in findings:
        severity = (f.get("severity") or "low").lower()
        if severity not in ("high", "critical"):
            continue
        name = (f.get("name") or f.get("title") or "").strip()
        if not name:
            continue
        fix_code = (
            f.get("fix", "")
            or f.get("fix_suggestion", "")
            or (f.get("fix_code") or {}).get("generic", "")
        )
        fid = f.get("id") or ""
        ftype = f.get("type") or ""
        url = f.get("url") or ""
        candidates.append((name, severity, fix_code, fid, ftype, url, target_host))

    if not candidates:
        return 0

    conn = get_db()
    try:
        existing_rows = conn.execute(
            "SELECT finding_name FROM fix_tickets WHERE user_id=? AND status=?",
            (user_id, TicketStatus.PENDING),
        ).fetchall()
        existing = {row["finding_name"] for row in existing_rows}
    finally:
        conn.close()

    created = 0
    for name, severity, fix_code, fid, ftype, url, host in candidates:
        if name in existing:
            continue
        create_fix_ticket(
            user_id,
            scan_id,
            name,
            severity,
            fix_code,
            finding_id=fid,
            finding_type=ftype,
            url=url,
            target_host=host,
        )
        existing.add(name)
        created += 1
    return created


def build_ticket_timeline(ticket: dict[str, Any]) -> list[dict[str, Any]]:
    """基于工单时间戳与事件表构建闭环时间线。

    返回与旧版 api_fix_ticket_timeline 相同 shape 的列表。
    """
    events = _ticket_events(ticket["id"])
    status_events: dict[str, dict[str, Any]] = {}
    for e in events:
        to_status = e.get("to_status")
        if not to_status:
            continue
        ts = e.get("created_at") or ""
        if (
            to_status not in status_events
            or (status_events[to_status].get("created_at") or "") < ts
        ):
            status_events[to_status] = e

    def event_time(status: str) -> str:
        ev = status_events.get(status)
        return ev.get("created_at", "") if ev else ""

    timeline: list[dict[str, Any]] = []

    if ticket.get("created_at"):
        timeline.append(
            {
                "stage": "discovered",
                "label": "发现漏洞",
                "time": ticket["created_at"],
                "status": "done",
            }
        )

    if ticket.get("status") in (
        "confirmed",
        "applying",
        "fixed",
        "failed",
        "rolled_back",
    ):
        timeline.append(
            {
                "stage": "confirmed",
                "label": "确认修复",
                "time": event_time("confirmed") or ticket.get("updated_at", ""),
                "status": "done",
            }
        )
    else:
        timeline.append(
            {
                "stage": "confirmed",
                "label": "确认修复",
                "time": "",
                "status": "pending",
            }
        )

    if ticket.get("applied_at"):
        timeline.append(
            {
                "stage": "applying",
                "label": "应用修复",
                "time": ticket["applied_at"],
                "status": "done",
            }
        )
    elif ticket.get("status") in ("applying", "fixed", "failed"):
        timeline.append(
            {
                "stage": "applying",
                "label": "应用修复",
                "time": event_time("applying") or ticket.get("updated_at", ""),
                "status": "doing",
            }
        )
    else:
        timeline.append(
            {
                "stage": "applying",
                "label": "应用修复",
                "time": "",
                "status": "pending",
            }
        )

    if ticket.get("verification_scan_id"):
        timeline.append(
            {
                "stage": "verified",
                "label": "复测验证",
                "time": event_time("fixed")
                or event_time("failed")
                or ticket.get("updated_at", ""),
                "status": "done",
            }
        )
    elif ticket.get("status") in ("fixed", "failed"):
        timeline.append(
            {
                "stage": "verified",
                "label": "复测验证",
                "time": "",
                "status": "doing",
            }
        )
    else:
        timeline.append(
            {
                "stage": "verified",
                "label": "复测验证",
                "time": "",
                "status": "pending",
            }
        )

    if ticket.get("status") == "fixed":
        timeline.append(
            {
                "stage": "closed",
                "label": "闭环完成",
                "time": ticket.get("fixed_at", ""),
                "status": "done",
            }
        )
    elif ticket.get("status") == "failed":
        timeline.append(
            {
                "stage": "closed",
                "label": "修复失败",
                "time": event_time("failed") or ticket.get("updated_at", ""),
                "status": "failed",
            }
        )
    elif ticket.get("status") == "rolled_back":
        timeline.append(
            {
                "stage": "closed",
                "label": "已回滚",
                "time": ticket.get("rolled_back_at", ""),
                "status": "rolled_back",
            }
        )
    else:
        timeline.append(
            {
                "stage": "closed",
                "label": "闭环完成",
                "time": "",
                "status": "pending",
            }
        )

    return timeline
