"""Comprehensive pytest unit tests for the service modules.

Covers:
- app/services/credits_service.py  (credit management)
- app/services/billing_service.py  (billing plans, purchases, transactions, payment gateways)
- app/services/gdpr_service.py     (data export, account deletion, anonymization)
- app/services/data_retention.py   (data retention policies)

All tests call the service functions directly (no HTTP layer). Each test is a
standalone function and creates its own isolated data (unique users / cleared
tables) so ordering does not affect correctness.
"""

import os
import sqlite3
import sys
import uuid
from datetime import datetime, timedelta

# --- Database environment MUST be configured BEFORE importing main ---
os.environ["DB_DIR"] = "/tmp/v11-test"
os.environ["DB_NAME"] = "test.db"
os.makedirs(os.environ["DB_DIR"], exist_ok=True)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest  # noqa: E402

import main  # noqa: E402

# Ensure all tables exist.
main.init_db()

from app.core.exceptions import BusinessException  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.services import (
    billing_service,  # noqa: E402
    credits_service,  # noqa: E402
    data_retention,  # noqa: E402
    gdpr_service,  # noqa: E402
)

_TIME_FMT = "%Y-%m-%d %H:%M:%S"

DEFAULT_PLAN_NAMES = {"体验包", "标准包", "专业包", "企业包"}


# ---------------------------------------------------------------------------
# Shared helper utilities
# ---------------------------------------------------------------------------


def _now() -> str:
    return datetime.now().strftime(_TIME_FMT)


def _days_ago(days: int) -> str:
    return (datetime.now() - timedelta(days=days)).strftime(_TIME_FMT)


def _create_user(
    *,
    username: str | None = None,
    credits: int = 10,
    role: str = "member",
    email: str | None = None,
    password: str = "hashed_pwd",
) -> tuple[int, str]:
    """Insert a user directly into the DB and return (user_id, username)."""
    uname = username or "svc_" + uuid.uuid4().hex[:12]
    conn = get_db()
    try:
        cur = conn.execute(
            "INSERT INTO users (username, password, email, role, credits, created_at) "
            "VALUES (?,?,?,?,?,?)",
            (uname, password, email or f"{uname}@example.com", role, credits, _now()),
        )
        conn.commit()
        return cur.lastrowid, uname
    finally:
        conn.close()


def _set_credits(user_id: int, credits: int) -> None:
    conn = get_db()
    try:
        conn.execute("UPDATE users SET credits=? WHERE id=?", (credits, user_id))
        conn.commit()
    finally:
        conn.close()


def _insert_plan(
    *, name: str, credits: int = 1, price_cents: int = 100, active: int = 1,
    currency: str = "CNY", description: str = "test plan",
) -> int:
    conn = get_db()
    try:
        cur = conn.execute(
            "INSERT INTO pricing_plans (name, description, credits, price_cents, currency, active, created_at) "
            "VALUES (?,?,?,?,?,?,?)",
            (name, description, credits, price_cents, currency, active, _now()),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def _delete_plan(plan_id: int) -> None:
    conn = get_db()
    try:
        conn.execute("DELETE FROM pricing_plans WHERE id=?", (plan_id,))
        conn.commit()
    finally:
        conn.close()


def _insert_scan(user_id: int = 1, created_at: str | None = None) -> int:
    conn = get_db()
    try:
        cur = conn.execute(
            "INSERT INTO scans (user_id, url, score, risk_level, findings_count, findings_json, "
            "summary_json, crawled_pages, scan_type, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                user_id,
                f"https://scan-{uuid.uuid4().hex[:8]}.example.com",
                80,
                "low",
                0,
                "[]",
                "{}",
                0,
                "test",
                created_at or _now(),
            ),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def _insert_audit_log(user_id: int = 1, created_at: str | None = None) -> int:
    conn = get_db()
    try:
        cur = conn.execute(
            "INSERT INTO audit_logs (user_id, action, resource_type, resource_id, details_json, "
            "client_ip, request_id, created_at) VALUES (?,?,?,?,?,?,?,?)",
            (user_id, "login", "auth", str(user_id), "{}", "127.0.0.1", uuid.uuid4().hex, created_at or _now()),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def _insert_usage_log(
    user_id: int = 1,
    created_at: str | None = None,
    *,
    amount: int = -1,
    balance_after: int = 9,
    action: str = "scan_cost",
    note: str = "retention",
) -> int:
    conn = get_db()
    try:
        cur = conn.execute(
            "INSERT INTO usage_logs (user_id, action, amount, balance_after, scan_id, note, created_at) "
            "VALUES (?,?,?,?,?,?,?)",
            (user_id, action, amount, balance_after, None, note, created_at or _now()),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def _insert_fix_ticket(user_id: int = 1, created_at: str | None = None) -> int:
    conn = get_db()
    try:
        cur = conn.execute(
            "INSERT INTO fix_tickets (user_id, scan_id, finding_name, severity, status, created_at) "
            "VALUES (?,?,?,?,?,?)",
            (user_id, None, "缺少 HSTS", "high", "pending", created_at or _now()),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def _insert_finding_feedback(
    user_id: int = 1, scan_id: int = 1, created_at: str | None = None
) -> int:
    conn = get_db()
    try:
        cur = conn.execute(
            "INSERT INTO finding_feedback (user_id, scan_id, finding_name, finding_type, "
            "is_false_positive, is_confirmed, created_at) VALUES (?,?,?,?,?,?,?)",
            (user_id, scan_id, "缺少 HSTS", "config", 0, 1, created_at or _now()),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def _clear_tables(*tables: str) -> None:
    conn = get_db()
    try:
        for table in tables:
            conn.execute(f"DELETE FROM {table}")
        conn.commit()
    finally:
        conn.close()


def _count_rows(table: str, where: str = "", args: tuple = ()) -> int:
    sql = f"SELECT COUNT(*) FROM {table}"
    if where:
        sql += f" WHERE {where}"
    conn = get_db()
    try:
        return conn.execute(sql, args).fetchone()[0]
    finally:
        conn.close()


def _drop_scan_progress() -> None:
    conn = get_db()
    try:
        conn.execute("DROP TABLE IF EXISTS scan_progress")
        conn.commit()
    finally:
        conn.close()


class _BadConn:
    """A fake connection whose execute() always fails, used to exercise error paths."""

    def execute(self, *args, **kwargs):
        raise sqlite3.OperationalError("simulated failure")

    def executemany(self, *args, **kwargs):
        raise sqlite3.OperationalError("simulated failure")

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass


# ===========================================================================
# credits_service tests
# ===========================================================================


def test_get_credits_returns_default_balance_for_new_user():
    user_id, _ = _create_user(credits=10)
    assert credits_service.get_credits(user_id) == 10


def test_get_credits_returns_zero_for_nonexistent_user():
    assert credits_service.get_credits(999999999) == 0


def test_has_credits_sufficient_and_insufficient():
    user_id, _ = _create_user(credits=10)
    assert credits_service.has_credits(user_id, 10) is True
    assert credits_service.has_credits(user_id, 1) is True
    assert credits_service.has_credits(user_id, 11) is False
    assert credits_service.has_credits(user_id, 0) is True


def test_has_credits_for_nonexistent_user_is_false_for_positive_amount():
    assert credits_service.has_credits(999999999, 1) is False


def test_add_credits_increases_balance_and_logs_recharge():
    user_id, _ = _create_user(credits=10)
    new_balance = credits_service.add_credits(user_id, 5, note="recharge test")
    assert new_balance == 15
    assert credits_service.get_credits(user_id) == 15

    logs, total = credits_service.get_usage_logs(user_id)
    assert total == 1
    assert logs[0]["action"] == "recharge"
    assert logs[0]["amount"] == 5
    assert logs[0]["balance_after"] == 15
    assert logs[0]["note"] == "recharge test"


def test_add_credits_accumulates_across_calls():
    user_id, _ = _create_user(credits=0)
    assert credits_service.add_credits(user_id, 5) == 5
    assert credits_service.add_credits(user_id, 3) == 8
    assert credits_service.get_credits(user_id) == 8


def test_add_credits_nonexistent_user_returns_amount_without_creating_user():
    # No row -> current balance treated as 0; UPDATE affects 0 rows.
    result = credits_service.add_credits(999999998, 7, note="ghost")
    assert result == 7
    assert credits_service.get_credits(999999998) == 0


def test_deduct_credits_happy_path_records_usage_log():
    user_id, _ = _create_user(credits=10)
    new_balance = credits_service.deduct_credits(
        user_id, 3, "scan_cost", scan_id=99, note="test scan"
    )
    assert new_balance == 7
    assert credits_service.get_credits(user_id) == 7

    logs, total = credits_service.get_usage_logs(user_id)
    assert total == 1
    assert logs[0]["action"] == "scan_cost"
    assert logs[0]["amount"] == 3
    assert logs[0]["balance_after"] == 7
    assert logs[0]["scan_id"] == 99
    assert logs[0]["note"] == "test scan"


def test_deduct_credits_insufficient_raises_payment_required():
    user_id, _ = _create_user(credits=2)
    with pytest.raises(BusinessException) as exc:
        credits_service.deduct_credits(user_id, 5, "scan_cost")
    assert exc.value.code == "PAYMENT_REQUIRED"
    assert exc.value.status_code == 402
    # Balance unchanged and no usage log written.
    assert credits_service.get_credits(user_id) == 2
    _, total = credits_service.get_usage_logs(user_id)
    assert total == 0


def test_deduct_credits_nonexistent_user_raises_payment_required():
    with pytest.raises(BusinessException) as exc:
        credits_service.deduct_credits(999999997, 1, "scan_cost")
    assert exc.value.code == "PAYMENT_REQUIRED"
    assert exc.value.status_code == 402


def test_deduct_credits_exact_balance_to_zero():
    user_id, _ = _create_user(credits=4)
    assert credits_service.deduct_credits(user_id, 4, "scan_cost") == 0
    assert credits_service.get_credits(user_id) == 0


def test_log_usage_returns_log_id_and_is_retrievable():
    user_id, _ = _create_user(credits=10)
    log_id = credits_service.log_usage(
        user_id, 1, 9, "scan_cost", scan_id=5, note="manual log"
    )
    assert log_id > 0
    logs, total = credits_service.get_usage_logs(user_id)
    assert total == 1
    assert logs[0]["id"] == log_id
    assert logs[0]["scan_id"] == 5
    assert logs[0]["note"] == "manual log"


def test_get_usage_logs_pagination_and_ordering():
    user_id, _ = _create_user(credits=100)
    ids = []
    for _ in range(5):
        ids.append(credits_service.log_usage(user_id, 1, 100, "scan_cost"))

    logs, total = credits_service.get_usage_logs(user_id, limit=2, offset=0)
    assert total == 5
    assert len(logs) == 2
    # Ordered by id DESC.
    assert [lg["id"] for lg in logs] == sorted(ids, reverse=True)[:2]

    logs2, _ = credits_service.get_usage_logs(user_id, limit=2, offset=2)
    assert len(logs2) == 2
    assert {lg["id"] for lg in logs}.isdisjoint({lg["id"] for lg in logs2})

    logs3, _ = credits_service.get_usage_logs(user_id, limit=2, offset=4)
    assert len(logs3) == 1


def test_get_usage_logs_empty_for_new_user():
    user_id, _ = _create_user(credits=10)
    logs, total = credits_service.get_usage_logs(user_id)
    assert logs == []
    assert total == 0


def test_get_usage_logs_empty_for_nonexistent_user():
    logs, total = credits_service.get_usage_logs(999999996)
    assert logs == []
    assert total == 0


# ===========================================================================
# billing_service tests
# ===========================================================================


# --- plans ---


def test_get_plans_returns_default_plans_sorted_by_price():
    plans = billing_service.get_plans(active_only=True)
    assert len(plans) >= 4
    names = {p["name"] for p in plans}
    assert DEFAULT_PLAN_NAMES.issubset(names)
    prices = [p["price_cents"] for p in plans]
    assert prices == sorted(prices)
    assert all(p["active"] == 1 for p in plans)
    for plan in plans:
        for key in ("id", "name", "credits", "price_cents", "currency", "active"):
            assert key in plan


def test_get_plans_active_only_excludes_inactive():
    plan_id = _insert_plan(name="inactive_plan_test", active=0)
    try:
        active_plans = billing_service.get_plans(active_only=True)
        all_plans = billing_service.get_plans(active_only=False)
        assert all(p["id"] != plan_id for p in active_plans)
        assert any(p["id"] == plan_id for p in all_plans)
    finally:
        _delete_plan(plan_id)


def test_get_plan_by_id_returns_plan():
    plans = billing_service.get_plans(active_only=True)
    pid = plans[0]["id"]
    plan = billing_service.get_plan(pid)
    assert plan is not None
    assert plan["id"] == pid


def test_get_plan_nonexistent_returns_none():
    assert billing_service.get_plan(99999999) is None


# --- recharge records ---


def test_create_recharge_record_returns_id_and_transaction_id():
    user_id, _ = _create_user(credits=10)
    result = billing_service.create_recharge_record(
        user_id, plan_id=1, amount_cents=990, credits=10,
        status="pending", payment_provider="mock",
    )
    assert "id" in result and "transaction_id" in result
    assert result["status"] == "pending"
    assert result["transaction_id"].startswith("RECHARGE-")

    record = billing_service.get_recharge_record(result["id"])
    assert record is not None
    assert record["user_id"] == user_id
    assert record["plan_id"] == 1
    assert record["amount_cents"] == 990
    assert record["credits_added"] == 10
    assert record["status"] == "pending"
    assert record["payment_provider"] == "mock"


def test_get_recharge_record_nonexistent_returns_none():
    assert billing_service.get_recharge_record(99999999) is None


def test_get_recharge_record_by_transaction():
    user_id, _ = _create_user(credits=10)
    result = billing_service.create_recharge_record(
        user_id, plan_id=0, amount_cents=0, credits=5, status="pending",
    )
    record = billing_service.get_recharge_record_by_transaction(result["transaction_id"])
    assert record is not None
    assert record["transaction_id"] == result["transaction_id"]


def test_get_recharge_record_by_transaction_nonexistent_returns_none():
    assert billing_service.get_recharge_record_by_transaction("NONEXISTENT-TX") is None


def test_get_user_recharge_records_returns_records_and_total():
    user_id, _ = _create_user(credits=10)
    ids = []
    for _ in range(3):
        r = billing_service.create_recharge_record(
            user_id, plan_id=0, amount_cents=0, credits=1, status="pending",
        )
        ids.append(r["id"])

    records, total = billing_service.get_user_recharge_records(user_id)
    assert total == 3
    assert len(records) == 3
    # Ordered by id DESC.
    assert [r["id"] for r in records] == sorted(ids, reverse=True)
    # LEFT JOIN with pricing_plans provides plan_name column.
    assert "plan_name" in records[0]


def test_get_user_recharge_records_pagination():
    user_id, _ = _create_user(credits=10)
    for _ in range(5):
        billing_service.create_recharge_record(
            user_id, plan_id=0, amount_cents=0, credits=1, status="pending",
        )
    records, total = billing_service.get_user_recharge_records(user_id, limit=2, offset=0)
    assert total == 5
    assert len(records) == 2
    records2, _ = billing_service.get_user_recharge_records(user_id, limit=2, offset=4)
    assert len(records2) == 1


def test_get_user_recharge_records_empty():
    user_id, _ = _create_user(credits=10)
    records, total = billing_service.get_user_recharge_records(user_id)
    assert records == []
    assert total == 0


# --- purchase_plan ---


def test_purchase_plan_happy_path_increases_credits():
    user_id, _ = _create_user(credits=10)
    plans = billing_service.get_plans(active_only=True)
    plan = plans[0]

    result = billing_service.purchase_plan(user_id, plan["id"])
    assert result["success"] is True
    assert result["credits_added"] == plan["credits"]
    assert result["balance"] == 10 + plan["credits"]
    assert result["plan_name"] == plan["name"]
    assert "transaction_id" in result

    assert credits_service.get_credits(user_id) == 10 + plan["credits"]

    record = billing_service.get_recharge_record_by_transaction(result["transaction_id"])
    assert record["status"] == "paid"
    assert record["paid_at"] is not None


def test_purchase_plan_invalid_id_raises_plan_not_found():
    user_id, _ = _create_user(credits=10)
    with pytest.raises(BusinessException) as exc:
        billing_service.purchase_plan(user_id, 99999999)
    assert exc.value.code == "PLAN_NOT_FOUND"
    assert exc.value.status_code == 404


def test_purchase_plan_inactive_raises_plan_not_found():
    user_id, _ = _create_user(credits=10)
    plan_id = _insert_plan(name="inactive_purchase_test", active=0)
    try:
        with pytest.raises(BusinessException) as exc:
            billing_service.purchase_plan(user_id, plan_id)
        assert exc.value.code == "PLAN_NOT_FOUND"
    finally:
        _delete_plan(plan_id)


# --- admin_recharge_user ---


def test_admin_recharge_requires_admin_role():
    user_id, _ = _create_user(credits=10, role="member")
    with pytest.raises(BusinessException) as exc:
        billing_service.admin_recharge_user({"role": "member"}, user_id, 10)
    assert exc.value.code == "FORBIDDEN"
    assert exc.value.status_code == 403


def test_admin_recharge_missing_role_raises_forbidden():
    user_id, _ = _create_user(credits=10)
    with pytest.raises(BusinessException) as exc:
        billing_service.admin_recharge_user({}, user_id, 10)
    assert exc.value.code == "FORBIDDEN"


def test_admin_recharge_invalid_amount_raises():
    user_id, _ = _create_user(credits=10)
    with pytest.raises(BusinessException) as exc:
        billing_service.admin_recharge_user({"role": "admin"}, user_id, 0)
    assert exc.value.code == "INVALID_AMOUNT"
    assert exc.value.status_code == 400

    with pytest.raises(BusinessException):
        billing_service.admin_recharge_user({"role": "admin"}, user_id, -5)


def test_admin_recharge_happy_path_with_note():
    target_id, _ = _create_user(credits=10)
    result = billing_service.admin_recharge_user(
        {"role": "admin"}, target_id, 50, note="admin grant"
    )
    assert result["success"] is True
    assert result["credits_added"] == 50
    assert result["balance"] == 60
    assert result["target_user_id"] == target_id
    assert "transaction_id" in result
    assert credits_service.get_credits(target_id) == 60

    record = billing_service.get_recharge_record_by_transaction(result["transaction_id"])
    assert record["status"] == "paid"
    assert record["credits_added"] == 50
    assert record["note"] == "admin grant"


def test_admin_recharge_uses_default_note_when_blank():
    target_id, _ = _create_user(credits=0)
    result = billing_service.admin_recharge_user({"role": "admin"}, target_id, 5)
    assert result["balance"] == 5
    record = billing_service.get_recharge_record_by_transaction(result["transaction_id"])
    assert record["note"] == "管理员充值"


# --- create_payment_order ---


def test_create_payment_order_mock_paid_immediately():
    user_id, _ = _create_user(credits=10)
    plans = billing_service.get_plans(active_only=True)
    plan = plans[0]

    result = billing_service.create_payment_order(user_id, plan["id"], provider="mock")
    assert result["success"] is True
    assert result["provider"] == "mock"
    assert result["status"] == "paid"
    assert result["credits_added"] == plan["credits"]
    assert result["balance"] == 10 + plan["credits"]
    assert result["checkout_url"] is None
    assert credits_service.get_credits(user_id) == 10 + plan["credits"]


def test_create_payment_order_invalid_provider_raises():
    user_id, _ = _create_user(credits=10)
    plans = billing_service.get_plans(active_only=True)
    with pytest.raises(BusinessException) as exc:
        billing_service.create_payment_order(user_id, plans[0]["id"], provider="bitcoin")
    assert exc.value.code == "UNSUPPORTED_PROVIDER"


def test_create_payment_order_plan_not_found_raises():
    user_id, _ = _create_user(credits=10)
    with pytest.raises(BusinessException) as exc:
        billing_service.create_payment_order(user_id, 99999999, provider="mock")
    assert exc.value.code == "PLAN_NOT_FOUND"


def test_create_payment_order_stripe_not_configured_raises(monkeypatch):
    # No STRIPE_SECRET_KEY configured -> provider not enabled.
    monkeypatch.delenv("STRIPE_SECRET_KEY", raising=False)
    monkeypatch.delenv("STRIPE_API_KEY", raising=False)
    user_id, _ = _create_user(credits=10)
    plans = billing_service.get_plans(active_only=True)
    with pytest.raises(BusinessException) as exc:
        billing_service.create_payment_order(user_id, plans[0]["id"], provider="stripe")
    assert exc.value.code == "PROVIDER_NOT_CONFIGURED"


def test_create_payment_order_alipay_pending(monkeypatch):
    monkeypatch.delenv("ALIPAY_MOCK", raising=False)
    user_id, _ = _create_user(credits=10)
    plans = billing_service.get_plans(active_only=True)
    plan = plans[0]

    result = billing_service.create_payment_order(user_id, plan["id"], provider="alipay")
    assert result["success"] is True
    assert result["provider"] == "alipay"
    assert result["status"] == "pending"
    assert result["checkout_url"] is None
    assert result["provider_order_id"].startswith("ALIPAY-")
    assert "SDK" in result["note"]
    # Credits not added while pending.
    assert credits_service.get_credits(user_id) == 10


def test_create_payment_order_wechat_pending(monkeypatch):
    monkeypatch.delenv("WECHAT_MOCK", raising=False)
    user_id, _ = _create_user(credits=10)
    plans = billing_service.get_plans(active_only=True)

    result = billing_service.create_payment_order(user_id, plans[0]["id"], provider="wechat")
    assert result["success"] is True
    assert result["provider"] == "wechat"
    assert result["status"] == "pending"
    assert result["provider_order_id"].startswith("WECHAT-")
    assert "SDK" in result["note"]


def test_create_payment_order_alipay_mock_paid(monkeypatch):
    monkeypatch.setenv("ALIPAY_MOCK", "true")
    user_id, _ = _create_user(credits=10)
    plans = billing_service.get_plans(active_only=True)
    plan = plans[0]

    result = billing_service.create_payment_order(user_id, plan["id"], provider="alipay")
    assert result["status"] == "paid"
    assert result["provider"] == "alipay"
    assert result["credits_added"] == plan["credits"]
    assert result["balance"] == 10 + plan["credits"]
    assert result["provider_order_id"].startswith("ALIPAY-")
    assert "到账" in result["note"]


def test_create_payment_order_wechat_mock_paid(monkeypatch):
    monkeypatch.setenv("WECHAT_MOCK", "true")
    user_id, _ = _create_user(credits=10)
    plans = billing_service.get_plans(active_only=True)
    plan = plans[0]

    result = billing_service.create_payment_order(user_id, plan["id"], provider="wechat")
    assert result["status"] == "paid"
    assert result["provider"] == "wechat"
    assert result["credits_added"] == plan["credits"]
    assert result["balance"] == 10 + plan["credits"]
    assert result["provider_order_id"].startswith("WECHAT-")


# --- get_order_status ---


def test_get_order_status_existing_paid_order():
    user_id, _ = _create_user(credits=10)
    plans = billing_service.get_plans(active_only=True)
    plan = plans[0]
    order = billing_service.create_payment_order(user_id, plan["id"], provider="mock")

    status = billing_service.get_order_status(order["transaction_id"])
    assert status is not None
    assert status["transaction_id"] == order["transaction_id"]
    assert status["status"] == "paid"
    assert status["provider"] == "mock"
    assert status["amount_cents"] == plan["price_cents"]
    assert status["credits_added"] == plan["credits"]


def test_get_order_status_pending_record():
    user_id, _ = _create_user(credits=10)
    r = billing_service.create_recharge_record(
        user_id, plan_id=1, amount_cents=990, credits=10,
        status="pending", payment_provider="alipay", provider_order_id="ALIPAY-XYZ",
    )
    status = billing_service.get_order_status(r["transaction_id"])
    assert status["status"] == "pending"
    assert status["provider"] == "alipay"
    assert status["provider_order_id"] == "ALIPAY-XYZ"
    assert status["paid_at"] is None


def test_get_order_status_nonexistent_returns_none():
    assert billing_service.get_order_status("NONEXISTENT-TX-123") is None


# --- webhook / notify handlers ---


def test_handle_stripe_webhook_not_enabled(monkeypatch):
    # Force Stripe to be considered unavailable regardless of environment.
    monkeypatch.setattr(billing_service, "_STRIPE_AVAILABLE", False)
    monkeypatch.setattr(billing_service, "stripe", None)
    with pytest.raises(BusinessException) as exc:
        billing_service.handle_stripe_webhook(b"payload", "sig", "secret")
    assert exc.value.code == "STRIPE_NOT_ENABLED"


def test_handle_alipay_notify_not_configured_raises(monkeypatch):
    monkeypatch.delenv("ALIPAY_APP_ID", raising=False)
    monkeypatch.delenv("ALIPAY_MOCK", raising=False)
    with pytest.raises(BusinessException) as exc:
        billing_service.handle_alipay_notify({})
    assert exc.value.code == "NOT_IMPLEMENTED"
    assert exc.value.status_code == 501


def test_handle_alipay_notify_mock_fulfills_order(monkeypatch):
    monkeypatch.setenv("ALIPAY_MOCK", "true")
    user_id, _ = _create_user(credits=10)
    rec = billing_service.create_recharge_record(
        user_id, plan_id=0, amount_cents=0, credits=7, status="pending",
        payment_provider="alipay",
    )

    result = billing_service.handle_alipay_notify(
        {"out_trade_no": rec["transaction_id"], "trade_status": "TRADE_SUCCESS"}
    )
    assert result["success"] is True
    assert result["transaction_id"] == rec["transaction_id"]
    assert result["credits_added"] == 7
    assert result["balance"] == 17
    assert credits_service.get_credits(user_id) == 17

    record = billing_service.get_recharge_record_by_transaction(rec["transaction_id"])
    assert record["status"] == "paid"


def test_handle_alipay_notify_mock_trade_finished_fulfills(monkeypatch):
    monkeypatch.setenv("ALIPAY_MOCK", "true")
    user_id, _ = _create_user(credits=5)
    rec = billing_service.create_recharge_record(
        user_id, plan_id=0, amount_cents=0, credits=3, status="pending",
    )
    result = billing_service.handle_alipay_notify(
        {"out_trade_no": rec["transaction_id"], "trade_status": "TRADE_FINISHED"}
    )
    assert result["success"] is True
    assert result["balance"] == 8


def test_handle_alipay_notify_mock_idempotent_already_paid(monkeypatch):
    monkeypatch.setenv("ALIPAY_MOCK", "true")
    user_id, _ = _create_user(credits=10)
    rec = billing_service.create_recharge_record(
        user_id, plan_id=0, amount_cents=0, credits=5, status="pending",
    )

    first = billing_service.handle_alipay_notify(
        {"out_trade_no": rec["transaction_id"], "trade_status": "TRADE_SUCCESS"}
    )
    assert first["success"] is True
    assert "already_paid" not in first

    second = billing_service.handle_alipay_notify(
        {"out_trade_no": rec["transaction_id"], "trade_status": "TRADE_SUCCESS"}
    )
    assert second["success"] is True
    assert second.get("already_paid") is True
    # Balance unchanged after the second (idempotent) call.
    assert credits_service.get_credits(user_id) == 15


def test_handle_alipay_notify_mock_invalid_status_received(monkeypatch):
    monkeypatch.setenv("ALIPAY_MOCK", "true")
    result = billing_service.handle_alipay_notify(
        {"out_trade_no": "RECHARGE-XYZ", "trade_status": "WAIT_BUYER_PAY"}
    )
    assert result["success"] is True
    assert result["received"] is True
    assert "未支付成功" in result["note"]


def test_handle_alipay_notify_mock_missing_transaction_id_raises(monkeypatch):
    monkeypatch.setenv("ALIPAY_MOCK", "true")
    with pytest.raises(BusinessException) as exc:
        billing_service.handle_alipay_notify({"trade_status": "TRADE_SUCCESS"})
    assert exc.value.code == "INVALID_WEBHOOK"


def test_handle_alipay_notify_mock_order_not_found_raises(monkeypatch):
    monkeypatch.setenv("ALIPAY_MOCK", "true")
    with pytest.raises(BusinessException) as exc:
        billing_service.handle_alipay_notify(
            {"out_trade_no": "RECHARGE-NOTEXIST", "trade_status": "TRADE_SUCCESS"}
        )
    assert exc.value.code == "ORDER_NOT_FOUND"


def test_handle_wechat_notify_not_configured_raises(monkeypatch):
    monkeypatch.delenv("WECHAT_MCH_ID", raising=False)
    monkeypatch.delenv("WECHAT_MOCK", raising=False)
    with pytest.raises(BusinessException) as exc:
        billing_service.handle_wechat_notify({})
    assert exc.value.code == "NOT_IMPLEMENTED"
    assert exc.value.status_code == 501


def test_handle_wechat_notify_mock_fulfills_order(monkeypatch):
    monkeypatch.setenv("WECHAT_MOCK", "true")
    user_id, _ = _create_user(credits=10)
    rec = billing_service.create_recharge_record(
        user_id, plan_id=0, amount_cents=0, credits=8, status="pending",
    )
    result = billing_service.handle_wechat_notify(
        {"out_trade_no": rec["transaction_id"], "trade_state": "SUCCESS"}
    )
    assert result["success"] is True
    assert result["balance"] == 18
    assert credits_service.get_credits(user_id) == 18


def test_handle_wechat_notify_mock_idempotent(monkeypatch):
    monkeypatch.setenv("WECHAT_MOCK", "true")
    user_id, _ = _create_user(credits=10)
    rec = billing_service.create_recharge_record(
        user_id, plan_id=0, amount_cents=0, credits=5, status="pending",
    )
    billing_service.handle_wechat_notify(
        {"out_trade_no": rec["transaction_id"], "trade_state": "SUCCESS"}
    )
    second = billing_service.handle_wechat_notify(
        {"out_trade_no": rec["transaction_id"], "trade_state": "SUCCESS"}
    )
    assert second.get("already_paid") is True
    assert credits_service.get_credits(user_id) == 15


def test_handle_wechat_notify_mock_invalid_state_received(monkeypatch):
    monkeypatch.setenv("WECHAT_MOCK", "true")
    result = billing_service.handle_wechat_notify(
        {"out_trade_no": "RECHARGE-XYZ", "trade_state": "NOTPAY"}
    )
    assert result["success"] is True
    assert result["received"] is True
    assert "未支付成功" in result["note"]


def test_handle_wechat_notify_mock_missing_transaction_id_raises(monkeypatch):
    monkeypatch.setenv("WECHAT_MOCK", "true")
    with pytest.raises(BusinessException) as exc:
        billing_service.handle_wechat_notify({"trade_state": "SUCCESS"})
    assert exc.value.code == "INVALID_WEBHOOK"


# --- internal helpers (still part of the public surface of the module) ---


def test_parse_transaction_id_supports_all_key_variants():
    assert billing_service._parse_transaction_id({"out_trade_no": "TX1"}) == "TX1"
    assert billing_service._parse_transaction_id({"outTradeNo": "TX2"}) == "TX2"
    assert billing_service._parse_transaction_id({"transaction_id": "TX3"}) == "TX3"
    assert billing_service._parse_transaction_id({"transactionId": "TX4"}) == "TX4"
    assert billing_service._parse_transaction_id({}) is None
    assert billing_service._parse_transaction_id({"out_trade_no": ""}) is None


def test_is_mock_enabled_reads_env(monkeypatch):
    monkeypatch.setenv("FOO_MOCK", "true")
    assert billing_service._is_mock_enabled("FOO") is True
    monkeypatch.setenv("FOO_MOCK", "1")
    assert billing_service._is_mock_enabled("FOO") is True
    monkeypatch.setenv("FOO_MOCK", "yes")
    assert billing_service._is_mock_enabled("FOO") is True
    monkeypatch.setenv("FOO_MOCK", "false")
    assert billing_service._is_mock_enabled("FOO") is False
    monkeypatch.delenv("FOO_MOCK", raising=False)
    assert billing_service._is_mock_enabled("FOO") is False


def test_get_base_url_default_and_custom(monkeypatch):
    monkeypatch.delenv("PUBLIC_BASE_URL", raising=False)
    assert billing_service._get_base_url() == "http://localhost:8000"
    monkeypatch.setenv("PUBLIC_BASE_URL", "https://example.com/")
    assert billing_service._get_base_url() == "https://example.com"


def test_get_stripe_secret_and_public_default_none(monkeypatch):
    monkeypatch.delenv("STRIPE_SECRET_KEY", raising=False)
    monkeypatch.delenv("STRIPE_API_KEY", raising=False)
    monkeypatch.delenv("STRIPE_PUBLISHABLE_KEY", raising=False)
    assert billing_service._get_stripe_secret() is None
    assert billing_service._get_stripe_public() is None
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_123")
    monkeypatch.setenv("STRIPE_PUBLISHABLE_KEY", "pk_test_123")
    assert billing_service._get_stripe_secret() == "sk_test_123"
    assert billing_service._get_stripe_public() == "pk_test_123"


def test_provider_enabled_variants(monkeypatch):
    monkeypatch.delenv("STRIPE_SECRET_KEY", raising=False)
    monkeypatch.delenv("STRIPE_API_KEY", raising=False)
    assert billing_service._provider_enabled("mock") is True
    assert billing_service._provider_enabled("alipay") is True
    assert billing_service._provider_enabled("wechat") is True
    assert billing_service._provider_enabled("stripe") is False
    assert billing_service._provider_enabled("bitcoin") is False


# ===========================================================================
# gdpr_service tests
# ===========================================================================


def test_export_user_data_existing_user_excludes_password():
    user_id, uname = _create_user(credits=10, email="export@example.com")
    data = gdpr_service.export_user_data(user_id)
    assert data["user"] is not None
    assert data["user"]["id"] == user_id
    assert data["user"]["username"] == uname
    assert "password" not in data["user"]
    for key in ("scans", "recharge_records", "usage_logs", "audit_logs", "fix_tickets", "finding_feedback"):
        assert key in data
        assert isinstance(data[key], list)


def test_export_user_data_nonexistent_user():
    data = gdpr_service.export_user_data(99999999)
    assert data["user"] is None
    for key in ("scans", "recharge_records", "usage_logs", "audit_logs", "fix_tickets", "finding_feedback"):
        assert data[key] == []


def test_export_user_data_includes_related_records():
    user_id, _ = _create_user(credits=10)
    scan_id = _insert_scan(user_id)
    _insert_finding_feedback(user_id, scan_id)
    credits_service.add_credits(user_id, 5, note="export test")  # creates a usage log
    billing_service.create_recharge_record(
        user_id, plan_id=0, amount_cents=0, credits=5, status="paid"
    )
    _insert_audit_log(user_id)
    _insert_fix_ticket(user_id)

    data = gdpr_service.export_user_data(user_id)
    assert len(data["scans"]) >= 1
    assert len(data["finding_feedback"]) >= 1
    assert len(data["usage_logs"]) >= 1
    assert len(data["recharge_records"]) >= 1
    assert len(data["audit_logs"]) >= 1
    assert len(data["fix_tickets"]) >= 1
    # All exported rows belong to this user.
    for row in data["scans"]:
        assert row["user_id"] == user_id
    for row in data["audit_logs"]:
        assert row["user_id"] == user_id
    assert "password" not in data["user"]


def test_delete_user_account_removes_user_and_related_data():
    user_id, _ = _create_user(credits=10)
    _insert_scan(user_id)
    _insert_finding_feedback(user_id, _insert_scan(user_id))
    credits_service.add_credits(user_id, 5)
    billing_service.create_recharge_record(
        user_id, plan_id=0, amount_cents=0, credits=5, status="paid"
    )
    _insert_audit_log(user_id)
    _insert_fix_ticket(user_id)

    result = gdpr_service.delete_user_account(user_id)
    assert result["success"] is True
    assert "users" in result["deleted_tables"]

    conn = get_db()
    try:
        assert conn.execute("SELECT id FROM users WHERE id=?", (user_id,)).fetchone() is None
        assert conn.execute("SELECT COUNT(*) FROM scans WHERE user_id=?", (user_id,)).fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM finding_feedback WHERE user_id=?", (user_id,)).fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM usage_logs WHERE user_id=?", (user_id,)).fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM recharge_records WHERE user_id=?", (user_id,)).fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM audit_logs WHERE user_id=?", (user_id,)).fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM fix_tickets WHERE user_id=?", (user_id,)).fetchone()[0] == 0
    finally:
        conn.close()


def test_delete_user_account_nonexistent_returns_success():
    # DELETE on a missing id is a no-op; the transaction still succeeds.
    result = gdpr_service.delete_user_account(99999999)
    assert result["success"] is True
    assert "users" in result["deleted_tables"]
    conn = get_db()
    try:
        assert conn.execute("SELECT id FROM users WHERE id=99999999").fetchone() is None
    finally:
        conn.close()


def test_export_after_delete_returns_none_user():
    user_id, _ = _create_user(credits=10)
    gdpr_service.delete_user_account(user_id)
    data = gdpr_service.export_user_data(user_id)
    assert data["user"] is None


def test_anonymize_user_data_happy_path():
    user_id, _ = _create_user(credits=10, email="anon@example.com")
    result = gdpr_service.anonymize_user_data(user_id)
    assert result["success"] is True
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT username, email, password FROM users WHERE id=?", (user_id,)
        ).fetchone()
        assert row["username"] == f"deleted_user_{user_id}"
        assert row["email"] == ""
        assert row["password"] == ""
    finally:
        conn.close()


def test_anonymize_user_data_nonexistent_returns_failure():
    result = gdpr_service.anonymize_user_data(99999999)
    assert result["success"] is False
    assert "不存在" in result["message"]


# ===========================================================================
# data_retention tests
# ===========================================================================


def test_cutoff_returns_past_timestamp_in_correct_format():
    s = data_retention._cutoff(30)
    parsed = datetime.strptime(s, _TIME_FMT)
    assert parsed < datetime.now()


def test_table_exists_helper():
    conn = get_db()
    try:
        assert data_retention._table_exists(conn, "users") is True
        assert data_retention._table_exists(conn, "definitely_not_a_table_xyz") is False
    finally:
        conn.close()


def test_cleanup_old_scans_deletes_old_keeps_new():
    _clear_tables("scans", "finding_feedback")
    old_ids = [_insert_scan(1, _days_ago(100)) for _ in range(3)]
    new_ids = [_insert_scan(1, _now()) for _ in range(2)]
    assert _count_rows("scans") == 5

    result = data_retention.cleanup_old_scans(days=90)

    assert result["deleted_count"] == 3
    assert result["scans"] == 3
    assert result["finding_feedback"] == 0
    assert result["days"] == 90
    assert "cutoff" in result
    assert result.get("error") is not True
    for sid in old_ids:
        assert _count_rows("scans", "id = ?", (sid,)) == 0
    for sid in new_ids:
        assert _count_rows("scans", "id = ?", (sid,)) == 1
    assert _count_rows("scans") == 2


def test_cleanup_old_scans_cascades_finding_feedback():
    _clear_tables("scans", "finding_feedback")
    old_scan = _insert_scan(1, _days_ago(100))
    _insert_finding_feedback(1, old_scan, _now())
    _insert_finding_feedback(1, old_scan, _now())
    new_scan = _insert_scan(1, _now())
    new_fb = _insert_finding_feedback(1, new_scan, _now())

    result = data_retention.cleanup_old_scans(days=90)

    assert result["scans"] == 1
    assert result["finding_feedback"] == 2
    assert result["deleted_count"] == 3
    assert _count_rows("scans", "id = ?", (old_scan,)) == 0
    assert _count_rows("finding_feedback", "scan_id = ?", (old_scan,)) == 0
    assert _count_rows("scans", "id = ?", (new_scan,)) == 1
    assert _count_rows("finding_feedback", "id = ?", (new_fb,)) == 1


def test_cleanup_old_scans_empty_table():
    _clear_tables("scans", "finding_feedback")
    result = data_retention.cleanup_old_scans(days=90)
    assert result["deleted_count"] == 0
    assert result["scans"] == 0
    assert result["finding_feedback"] == 0
    assert result.get("error") is not True


def test_cleanup_old_scans_custom_days_threshold():
    _clear_tables("scans", "finding_feedback")
    scan_20 = _insert_scan(1, _days_ago(20))
    scan_50 = _insert_scan(1, _days_ago(50))
    scan_100 = _insert_scan(1, _days_ago(100))

    # days=40: deletes scans older than 40 days (50d, 100d), keeps the 20d scan.
    r1 = data_retention.cleanup_old_scans(days=40)
    assert r1["scans"] == 2
    assert r1["days"] == 40
    assert _count_rows("scans", "id = ?", (scan_20,)) == 1
    assert _count_rows("scans", "id = ?", (scan_50,)) == 0
    assert _count_rows("scans", "id = ?", (scan_100,)) == 0

    # days=10: deletes the remaining 20d scan.
    r2 = data_retention.cleanup_old_scans(days=10)
    assert r2["scans"] == 1
    assert _count_rows("scans", "id = ?", (scan_20,)) == 0


def test_cleanup_old_audit_logs():
    _clear_tables("audit_logs")
    old_ids = [_insert_audit_log(1, _days_ago(200)) for _ in range(2)]
    new_ids = [_insert_audit_log(1, _days_ago(10)) for _ in range(3)]
    assert _count_rows("audit_logs") == 5

    result = data_retention.cleanup_old_audit_logs(days=180)

    assert result["deleted_count"] == 2
    assert result["days"] == 180
    assert "cutoff" in result
    assert result.get("error") is not True
    for lid in old_ids:
        assert _count_rows("audit_logs", "id = ?", (lid,)) == 0
    for lid in new_ids:
        assert _count_rows("audit_logs", "id = ?", (lid,)) == 1


def test_cleanup_old_audit_logs_empty_table():
    _clear_tables("audit_logs")
    result = data_retention.cleanup_old_audit_logs(days=180)
    assert result["deleted_count"] == 0
    assert result.get("error") is not True


def test_cleanup_old_usage_logs():
    _clear_tables("usage_logs")
    old_ids = [_insert_usage_log(1, _days_ago(70)) for _ in range(4)]
    new_ids = [_insert_usage_log(1, _days_ago(5)) for _ in range(2)]
    assert _count_rows("usage_logs") == 6

    result = data_retention.cleanup_old_usage_logs(days=60)

    assert result["deleted_count"] == 4
    assert result["days"] == 60
    assert result.get("error") is not True
    for lid in old_ids:
        assert _count_rows("usage_logs", "id = ?", (lid,)) == 0
    for lid in new_ids:
        assert _count_rows("usage_logs", "id = ?", (lid,)) == 1


def test_cleanup_old_usage_logs_empty_table():
    _clear_tables("usage_logs")
    result = data_retention.cleanup_old_usage_logs(days=60)
    assert result["deleted_count"] == 0
    assert result.get("error") is not True


def test_cleanup_old_scan_progress_table_missing_skipped():
    _drop_scan_progress()
    result = data_retention.cleanup_old_scan_progress(days=7)
    assert result["skipped"] is True
    assert result["deleted_count"] == 0
    assert result["days"] == 7
    assert "cutoff" in result
    assert result.get("error") is not True


def test_cleanup_old_scan_progress_table_exists_deletes_old():
    _drop_scan_progress()
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
        result = data_retention.cleanup_old_scan_progress(days=7)
        assert result.get("skipped") is not True
        assert result["deleted_count"] == 1
        assert _count_rows("scan_progress") == 1
    finally:
        _drop_scan_progress()


def test_run_retention_policy_aggregates_all_tasks():
    _drop_scan_progress()
    _clear_tables("scans", "finding_feedback", "audit_logs", "usage_logs")

    old_scan = _insert_scan(1, _days_ago(100))
    _insert_finding_feedback(1, old_scan, _days_ago(100))
    for _ in range(3):
        _insert_audit_log(1, _days_ago(200))
    for _ in range(2):
        _insert_usage_log(1, _days_ago(70))
    new_scan = _insert_scan(1, _now())
    _insert_audit_log(1, _days_ago(5))
    _insert_usage_log(1, _days_ago(3))

    expected_scans = 1 + 1  # 1 scan + 1 feedback
    expected_audit = 3
    expected_usage = 2

    result = data_retention.run_retention_policy()

    assert result["total_deleted"] == expected_scans + expected_audit + expected_usage
    details = result["details"]
    assert set(details.keys()) == {"scans", "audit_logs", "usage_logs", "scan_progress"}
    assert details["scans"]["deleted_count"] == expected_scans
    assert details["scans"]["scans"] == 1
    assert details["scans"]["finding_feedback"] == 1
    assert details["audit_logs"]["deleted_count"] == expected_audit
    assert details["usage_logs"]["deleted_count"] == expected_usage
    assert details["scan_progress"]["skipped"] is True
    assert details["scan_progress"]["deleted_count"] == 0
    # New data retained.
    assert _count_rows("scans", "id = ?", (new_scan,)) == 1


def test_cleanup_old_scans_error_path_returns_error_dict(monkeypatch):
    monkeypatch.setattr(data_retention, "get_db", lambda: _BadConn())
    result = data_retention.cleanup_old_scans(days=90)
    assert result["deleted_count"] == 0
    assert result["scans"] == 0
    assert result["finding_feedback"] == 0
    assert result["error"] is True


def test_cleanup_old_audit_logs_error_path_returns_error_dict(monkeypatch):
    monkeypatch.setattr(data_retention, "get_db", lambda: _BadConn())
    result = data_retention.cleanup_old_audit_logs(days=180)
    assert result["deleted_count"] == 0
    assert result["error"] is True


def test_cleanup_old_usage_logs_error_path_returns_error_dict(monkeypatch):
    monkeypatch.setattr(data_retention, "get_db", lambda: _BadConn())
    result = data_retention.cleanup_old_usage_logs(days=60)
    assert result["deleted_count"] == 0
    assert result["error"] is True


def test_cleanup_old_scan_progress_error_path_returns_error_dict(monkeypatch):
    monkeypatch.setattr(data_retention, "get_db", lambda: _BadConn())
    result = data_retention.cleanup_old_scan_progress(days=7)
    assert result["deleted_count"] == 0
    assert result["error"] is True


# ---------------------------------------------------------------------------
# Additional edge-case coverage for remaining reachable branches
# ---------------------------------------------------------------------------


def test_get_plans_seeds_defaults_when_plans_table_empty():
    """_init_default_plans re-seeds the four default plans when the table is empty."""
    conn = get_db()
    try:
        conn.execute("DELETE FROM pricing_plans")
        conn.commit()
    finally:
        conn.close()

    plans = billing_service.get_plans(active_only=True)
    names = {p["name"] for p in plans}
    assert DEFAULT_PLAN_NAMES.issubset(names)
    assert len(plans) >= 4
    assert all(p["active"] == 1 for p in plans)


def test_handle_alipay_notify_real_gateway_not_implemented(monkeypatch):
    """With ALIPAY_APP_ID set but mock disabled, signature verification is not implemented -> 501."""
    monkeypatch.setenv("ALIPAY_APP_ID", "test_app_id")
    monkeypatch.delenv("ALIPAY_MOCK", raising=False)
    with pytest.raises(BusinessException) as exc:
        billing_service.handle_alipay_notify(
            {"out_trade_no": "RECHARGE-X", "trade_status": "TRADE_SUCCESS"}
        )
    assert exc.value.code == "NOT_IMPLEMENTED"
    assert exc.value.status_code == 501


def test_handle_wechat_notify_real_gateway_not_implemented(monkeypatch):
    """With WECHAT_MCH_ID set but mock disabled, signature verification is not implemented -> 501."""
    monkeypatch.setenv("WECHAT_MCH_ID", "test_mch_id")
    monkeypatch.delenv("WECHAT_MOCK", raising=False)
    with pytest.raises(BusinessException) as exc:
        billing_service.handle_wechat_notify(
            {"out_trade_no": "RECHARGE-X", "trade_state": "SUCCESS"}
        )
    assert exc.value.code == "NOT_IMPLEMENTED"
    assert exc.value.status_code == 501


def test_fetch_user_rows_handles_invalid_and_missing_tables():
    """_fetch_user_rows returns [] for invalid table names and valid-but-missing tables."""
    user_id, _ = _create_user(credits=10)
    conn = get_db()
    try:
        # Invalid table name (not in whitelist) -> [] without querying.
        assert gdpr_service._fetch_user_rows(conn, "users_evil_table", user_id) == []
        # Valid whitelist name but the table does not exist (e.g. 'findings') -> [].
        assert gdpr_service._fetch_user_rows(conn, "findings", user_id) == []
        # Existing table returns a list (possibly empty).
        assert isinstance(gdpr_service._fetch_user_rows(conn, "scans", user_id), list)
    finally:
        conn.close()


def test_table_exists_helper_in_gdpr():
    """gdpr_service._table_exists reports existence correctly."""
    conn = get_db()
    try:
        assert gdpr_service._table_exists(conn, "users") is True
        assert gdpr_service._table_exists(conn, "definitely_not_a_table_gdpr") is False
    finally:
        conn.close()
