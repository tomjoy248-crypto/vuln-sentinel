"""baseline: 初始化全部业务表结构

Revision ID: 001_baseline
Revises:
Create Date: 2026-08-05 00:00:00

本迁移文件将 main.py 中 init_db() 函数创建的全部业务表（含历次
ALTER TABLE 迁移追加的列）以 SQLAlchemy ``op.create_table()`` 的方式
重建为一份 baseline 迁移。表名清单：

users, scans, targets, domain_verifications, fix_tickets,
ticket_events, alerts, usage_logs, pricing_plans, recharge_records,
assets, finding_feedback, audit_logs

注意：
- 原 init_db() 使用 ``CREATE TABLE IF NOT EXISTS``，本 baseline 迁移
  面向全新数据库；对已有数据库请先执行 ``alembic stamp head`` 标记基线。
- 列定义已合并历次 ALTER TABLE ADD COLUMN 迁移，确保与运行时一致。
- 索引与原 init_db() / _create_indexes() 保持一致（仅包含本迁移涉及的表）。
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# Alembic 版本标识
revision: str = "001_baseline"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """创建全部业务表与索引。"""

    # ------------------------------------------------------------------
    # 1. users：用户表（含通知设置列）
    # ------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("username", sa.Text, nullable=False, unique=True),
        sa.Column("password", sa.Text, nullable=False),
        sa.Column("email", sa.Text, nullable=True),
        sa.Column("role", sa.Text, server_default=sa.text("'member'")),
        sa.Column("team_id", sa.Integer, server_default=sa.text("0")),
        sa.Column("credits", sa.Integer, server_default=sa.text("10")),
        sa.Column("created_at", sa.Text, nullable=True),
        sa.Column("notify_email", sa.Text, server_default=sa.text("''")),
        sa.Column("notify_webhook", sa.Text, server_default=sa.text("''")),
        sa.Column("alert_threshold", sa.Text, server_default=sa.text("'high'")),
        sqlite_autoincrement=True,
    )
    op.create_index("idx_users_username", "users", ["username"])

    # ------------------------------------------------------------------
    # 2. scans：扫描记录表
    # ------------------------------------------------------------------
    op.create_table(
        "scans",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, server_default=sa.text("0")),
        sa.Column("url", sa.Text, nullable=False),
        sa.Column("score", sa.Integer, nullable=True),
        sa.Column("risk_level", sa.Text, nullable=True),
        sa.Column("findings_count", sa.Integer, nullable=True),
        sa.Column("findings_json", sa.Text, nullable=True),
        sa.Column("summary_json", sa.Text, nullable=True),
        sa.Column("crawled_pages", sa.Integer, nullable=True),
        sa.Column("scan_type", sa.Text, server_default=sa.text("'real'")),
        sa.Column("share_id", sa.Text, nullable=True),
        sa.Column("details_json", sa.Text, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.Text, nullable=True),
        sqlite_autoincrement=True,
    )
    op.create_index("idx_scans_user_id", "scans", ["user_id"])
    op.create_index("idx_scans_url", "scans", ["url"])
    op.create_index("idx_scans_created_at", "scans", ["created_at"])
    op.create_index("idx_scans_share_id", "scans", ["share_id"])
    op.create_index(
        "idx_scans_user_created",
        "scans",
        [sa.text("user_id"), sa.text("created_at DESC")],
    )

    # ------------------------------------------------------------------
    # 3. targets：监控目标表
    # ------------------------------------------------------------------
    op.create_table(
        "targets",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column("url", sa.Text, nullable=False),
        sa.Column("schedule", sa.Text, server_default=sa.text("'daily'")),
        sa.Column("last_scan", sa.Text, nullable=True),
        sa.Column("last_score", sa.Integer, nullable=True),
        sa.Column("created_at", sa.Text, nullable=True),
        sa.UniqueConstraint("user_id", "url", name="uq_targets_user_id_url"),
        sqlite_autoincrement=True,
    )
    op.create_index("idx_targets_user_id", "targets", ["user_id"])
    op.create_index("idx_targets_schedule", "targets", ["schedule"])

    # ------------------------------------------------------------------
    # 4. domain_verifications：域名归属验证表
    # ------------------------------------------------------------------
    op.create_table(
        "domain_verifications",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column("domain", sa.Text, nullable=False),
        sa.Column("method", sa.Text, server_default=sa.text("'dns_txt'")),
        sa.Column("token", sa.Text, server_default=sa.text("''")),
        sa.Column("status", sa.Text, server_default=sa.text("'pending'")),
        sa.Column("created_at", sa.Text, nullable=True),
        sa.Column("verified_at", sa.Text, nullable=True),
        sa.Column("expires_at", sa.Text, nullable=True),
        sa.UniqueConstraint("user_id", "domain", name="uq_domain_verifications_user_id_domain"),
        sqlite_autoincrement=True,
    )

    # ------------------------------------------------------------------
    # 5. fix_tickets：修复工单表（含闭环修复字段）
    # ------------------------------------------------------------------
    op.create_table(
        "fix_tickets",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column("scan_id", sa.Integer, nullable=True),
        sa.Column("finding_name", sa.Text, nullable=False),
        sa.Column("severity", sa.Text, server_default=sa.text("'low'")),
        sa.Column("status", sa.Text, server_default=sa.text("'pending'")),
        sa.Column("fix_code", sa.Text, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.Text, nullable=True),
        sa.Column("updated_at", sa.Text, nullable=True),
        sa.Column("fixed_at", sa.Text, nullable=True),
        sa.Column("finding_id", sa.Text, server_default=sa.text("''")),
        sa.Column("finding_type", sa.Text, server_default=sa.text("''")),
        sa.Column("url", sa.Text, server_default=sa.text("''")),
        sa.Column("target_host", sa.Text, server_default=sa.text("''")),
        sa.Column("applied_at", sa.Text, nullable=True),
        sa.Column("rolled_back_at", sa.Text, nullable=True),
        sa.Column("rollback_code", sa.Text, nullable=True),
        sa.Column("verification_scan_id", sa.Integer, nullable=True),
        sa.Column("diff_summary", sa.Text, server_default=sa.text("'{}'")),
        sqlite_autoincrement=True,
    )
    op.create_index("idx_fix_tickets_user_id", "fix_tickets", ["user_id"])
    op.create_index("idx_fix_tickets_status", "fix_tickets", ["status"])
    op.create_index("idx_fix_tickets_scan_id", "fix_tickets", ["scan_id"])

    # ------------------------------------------------------------------
    # 6. ticket_events：工单状态变更事件表
    # ------------------------------------------------------------------
    op.create_table(
        "ticket_events",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("ticket_id", sa.Integer, nullable=False),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column("from_status", sa.Text, nullable=True),
        sa.Column("to_status", sa.Text, nullable=True),
        sa.Column("note", sa.Text, nullable=True),
        sa.Column("created_at", sa.Text, nullable=True),
        sqlite_autoincrement=True,
    )
    op.create_index("idx_ticket_events_ticket_id", "ticket_events", ["ticket_id"])

    # ------------------------------------------------------------------
    # 7. alerts：告警表
    # ------------------------------------------------------------------
    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column("target_id", sa.Integer, nullable=True),
        sa.Column("alert_type", sa.Text, server_default=sa.text("'score_change'")),
        sa.Column("title", sa.Text, server_default=sa.text("''")),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("details_json", sa.Text, server_default=sa.text("'{}'")),
        sa.Column("scan_id", sa.Integer, nullable=True),
        sa.Column("created_at", sa.Text, nullable=True),
        sa.Column("is_read", sa.Integer, server_default=sa.text("0")),
        sqlite_autoincrement=True,
    )
    op.create_index("idx_alerts_user_id", "alerts", ["user_id"])
    op.create_index("idx_alerts_is_read", "alerts", ["is_read"])
    op.create_index("idx_alerts_scan_id", "alerts", ["scan_id"])

    # ------------------------------------------------------------------
    # 8. usage_logs：积分使用日志表
    # ------------------------------------------------------------------
    op.create_table(
        "usage_logs",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column("action", sa.Text, nullable=False),
        sa.Column("amount", sa.Integer, nullable=False),
        sa.Column("balance_after", sa.Integer, nullable=False),
        sa.Column("scan_id", sa.Integer, nullable=True),
        sa.Column("note", sa.Text, server_default=sa.text("''")),
        sa.Column("created_at", sa.Text, nullable=True),
        sqlite_autoincrement=True,
    )
    op.create_index("idx_usage_logs_user_id", "usage_logs", ["user_id"])

    # ------------------------------------------------------------------
    # 9. pricing_plans：计费套餐表
    # ------------------------------------------------------------------
    op.create_table(
        "pricing_plans",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("description", sa.Text, server_default=sa.text("''")),
        sa.Column("credits", sa.Integer, nullable=False),
        sa.Column("price_cents", sa.Integer, nullable=False),
        sa.Column("currency", sa.Text, server_default=sa.text("'CNY'")),
        sa.Column("active", sa.Integer, server_default=sa.text("1")),
        sa.Column("created_at", sa.Text, nullable=True),
        sqlite_autoincrement=True,
    )
    op.create_index("idx_pricing_plans_active", "pricing_plans", ["active"])

    # ------------------------------------------------------------------
    # 10. recharge_records：充值记录表（含支付字段）
    # ------------------------------------------------------------------
    op.create_table(
        "recharge_records",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column("plan_id", sa.Integer, server_default=sa.text("0")),
        sa.Column("amount_cents", sa.Integer, server_default=sa.text("0")),
        sa.Column("credits_added", sa.Integer, nullable=False),
        sa.Column("status", sa.Text, server_default=sa.text("'pending'")),
        sa.Column("transaction_id", sa.Text, nullable=False, unique=True),
        sa.Column("note", sa.Text, server_default=sa.text("''")),
        sa.Column("payment_provider", sa.Text, server_default=sa.text("'mock'")),
        sa.Column("provider_order_id", sa.Text, server_default=sa.text("''")),
        sa.Column("created_at", sa.Text, nullable=True),
        sa.Column("paid_at", sa.Text, nullable=True),
        sqlite_autoincrement=True,
    )
    op.create_index("idx_recharge_records_user_id", "recharge_records", ["user_id"])
    op.create_index(
        "idx_recharge_records_transaction_id", "recharge_records", ["transaction_id"]
    )

    # ------------------------------------------------------------------
    # 11. assets：资产表
    # ------------------------------------------------------------------
    op.create_table(
        "assets",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column("domain", sa.Text, nullable=False),
        sa.Column("owner", sa.Text, server_default=sa.text("''")),
        sa.Column("description", sa.Text, server_default=sa.text("''")),
        sa.Column("verified", sa.Integer, server_default=sa.text("0")),
        sa.Column("last_scan_id", sa.Integer, nullable=True),
        sa.Column("last_scan_at", sa.Text, nullable=True),
        sa.Column("created_at", sa.Text, nullable=True),
        sa.UniqueConstraint("user_id", "domain", name="uq_assets_user_id_domain"),
        sqlite_autoincrement=True,
    )
    op.create_index("idx_assets_user_id", "assets", ["user_id"])
    op.create_index("idx_assets_domain", "assets", ["domain"])

    # ------------------------------------------------------------------
    # 12. finding_feedback：findings 误报/确认反馈表
    # ------------------------------------------------------------------
    op.create_table(
        "finding_feedback",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column("scan_id", sa.Integer, nullable=False),
        sa.Column("finding_name", sa.Text, nullable=False),
        sa.Column("finding_type", sa.Text, nullable=True),
        sa.Column("is_false_positive", sa.Integer, server_default=sa.text("0")),
        sa.Column("is_confirmed", sa.Integer, server_default=sa.text("0")),
        sa.Column(
            "created_at",
            sa.TIMESTAMP,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sqlite_autoincrement=True,
    )
    op.create_index("idx_finding_feedback_user_id", "finding_feedback", ["user_id"])
    op.create_index("idx_finding_feedback_scan_id", "finding_feedback", ["scan_id"])
    op.create_index("idx_finding_feedback_name", "finding_feedback", ["finding_name"])

    # ------------------------------------------------------------------
    # 13. audit_logs：审计日志表
    # ------------------------------------------------------------------
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, nullable=True),
        sa.Column("action", sa.Text, nullable=False),
        sa.Column("resource_type", sa.Text, nullable=False),
        sa.Column("resource_id", sa.Text, nullable=True),
        sa.Column("details_json", sa.Text, server_default=sa.text("'{}'")),
        sa.Column("client_ip", sa.Text, nullable=True),
        sa.Column("request_id", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sqlite_autoincrement=True,
    )
    op.create_index("idx_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("idx_audit_logs_action", "audit_logs", ["action"])
    op.create_index("idx_audit_logs_created_at", "audit_logs", ["created_at"])


def downgrade() -> None:
    """按 upgrade 的逆序删除所有表。

    说明：删除表时其上的索引会自动随之删除，故无需单独 drop index。
    """
    op.drop_table("audit_logs")
    op.drop_table("finding_feedback")
    op.drop_table("assets")
    op.drop_table("recharge_records")
    op.drop_table("pricing_plans")
    op.drop_table("usage_logs")
    op.drop_table("alerts")
    op.drop_table("ticket_events")
    op.drop_table("fix_tickets")
    op.drop_table("domain_verifications")
    op.drop_table("targets")
    op.drop_table("scans")
    op.drop_table("users")
