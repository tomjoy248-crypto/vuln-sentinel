"""邮件服务。

用于发送邮箱验证邮件、密码重置邮件等通知邮件。
复用 main.py 中已有的 SMTP 配置（从 os.environ 读取 SMTP_HOST/PORT/USER/PASSWORD/FROM），
当 SMTP 未配置时记录日志并返回 False。

邮件正文使用 HTML 格式，文案为中文。底层基于标准库 smtplib + email.mime 实现。
"""

from __future__ import annotations

import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.logging import get_request_id
from app.db.session import get_db

logger = logging.getLogger("vuln_sentinel.email")


def _mask_email(email: str) -> str:
    """仅保留收件人邮箱的最少可识别信息，避免日志泄露完整地址。"""
    value = (email or "").strip()
    if "@" not in value:
        return "***"
    local, domain = value.split("@", 1)
    if len(local) <= 2:
        masked_local = "*" * len(local)
    else:
        masked_local = local[:1] + "***" + local[-1:]
    return f"{masked_local}@{domain}"


def _save_delivery_log(
    email_type: str,
    recipient: str,
    subject: str,
    status: str,
    error_message: str = "",
) -> None:
    """记录邮件投递结果，但不保存正文、令牌或完整邮箱地址。"""
    try:
        conn = get_db()
        conn.execute(
            """INSERT INTO email_delivery_logs
               (email_type, recipient_masked, subject, status, error_message, request_id)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                email_type,
                _mask_email(recipient),
                subject[:200],
                status,
                (error_message or "")[:500],
                get_request_id(),
            ),
        )
        conn.commit()
        conn.close()
    except Exception as exc:  # logging must never break email delivery
        logger.warning("邮件投递日志写入失败: %s", exc)


def get_email_delivery_logs(
    email_type: str | None = None,
    status: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[dict]:
    """查询邮件投递记录，供管理员审计使用。"""
    conn = get_db()
    try:
        conditions = []
        params: list = []
        if email_type:
            conditions.append("email_type = ?")
            params.append(email_type)
        if status:
            conditions.append("status = ?")
            params.append(status)
        where = "WHERE " + " AND ".join(conditions) if conditions else ""
        params.extend([limit, offset])
        rows = conn.execute(
            f"""SELECT id, email_type, recipient_masked, subject, status,
                       error_message, request_id, created_at
                FROM email_delivery_logs {where}
                ORDER BY created_at DESC LIMIT ? OFFSET ?""",
            params,
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def _get_smtp_config() -> dict[str, str | int]:
    """从环境变量读取 SMTP 配置（与 main.py 保持一致）。"""
    return {
        "host": os.getenv("SMTP_HOST", ""),
        "port": int(os.getenv("SMTP_PORT", "587")),
        "user": os.getenv("SMTP_USER", ""),
        "password": os.getenv("SMTP_PASSWORD", ""),
        "from": os.getenv("SMTP_FROM", "vuln-sentinel@example.com"),
    }


def is_smtp_configured() -> bool:
    """检查 SMTP 是否已配置。

    与 main.py 中 SMTP_ENABLED 判断逻辑一致：
    需要 SMTP_HOST、SMTP_USER、SMTP_PASSWORD 同时配置。
    """
    cfg = _get_smtp_config()
    return bool(cfg["host"] and cfg["user"] and cfg["password"])


def _send_email(
    to_email: str,
    subject: str,
    html_body: str,
    *,
    email_type: str = "unknown",
) -> bool:
    """发送 HTML 邮件的内部实现。

    Args:
        to_email: 收件人邮箱地址
        subject: 邮件主题
        html_body: HTML 格式的邮件正文

    Returns:
        True 表示发送成功，False 表示发送失败或 SMTP 未配置
    """
    if not is_smtp_configured():
        logger.warning("SMTP 未配置，跳过发送邮件（subject=%s）", subject)
        _save_delivery_log(email_type, to_email, subject, "skipped", "SMTP 未配置")
        return False
    if not to_email:
        logger.warning("收件人邮箱为空，跳过发送邮件（subject=%s）", subject)
        _save_delivery_log(email_type, to_email, subject, "skipped", "收件人邮箱为空")
        return False

    cfg = _get_smtp_config()
    host = str(cfg["host"])
    port = int(cfg["port"])
    user = str(cfg["user"])
    password = str(cfg["password"])
    sender = str(cfg["from"])

    msg = MIMEMultipart("alternative")
    msg["From"] = sender
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        # 465 端口使用 SSL 直连，587 等端口使用 STARTTLS 升级
        if port == 465:
            with smtplib.SMTP_SSL(host, port, timeout=15) as server:
                server.login(user, password)
                server.sendmail(sender, [to_email], msg.as_string())
        else:
            with smtplib.SMTP(host, port, timeout=15) as server:
                if port == 587:
                    server.starttls()
                server.login(user, password)
                server.sendmail(sender, [to_email], msg.as_string())
        logger.info("邮件发送成功: to=%s subject=%s", to_email, subject)
        _save_delivery_log(email_type, to_email, subject, "sent")
        return True
    except Exception as exc:  # noqa: BLE001 - 邮件发送失败需吞掉异常并返回 False
        logger.warning("邮件发送失败: to=%s subject=%s error=%s", to_email, subject, exc)
        _save_delivery_log(email_type, to_email, subject, "failed", str(exc))
        return False


def _verification_html(verify_link: str) -> str:
    """生成邮箱验证邮件的 HTML 正文。"""
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"></head>
<body style="font-family:-apple-system,'Segoe UI','Microsoft YaHei',sans-serif;color:#333;max-width:560px;margin:0 auto;padding:24px;">
  <h2 style="color:#1a73e8;">验证你的邮箱地址</h2>
  <p>你好！</p>
  <p>你正在为<strong>Vuln Sentinel（Vuln Sentinel）</strong>账号绑定邮箱，请点击下方按钮完成邮箱验证：</p>
  <p style="margin:24px 0;">
    <a href="{verify_link}" style="display:inline-block;background:#1a73e8;color:#fff;text-decoration:none;padding:12px 28px;border-radius:6px;font-weight:600;">立即验证邮箱</a>
  </p>
  <p>或复制以下链接到浏览器打开：</p>
  <p style="word-break:break-all;color:#1a73e8;">{verify_link}</p>
  <p style="color:#999;font-size:13px;">该验证链接有效期为 24 小时。如果你没有发起此操作，请忽略本邮件。</p>
  <hr style="border:none;border-top:1px solid #eee;margin:24px 0;">
  <p style="color:#999;font-size:12px;">Vuln Sentinel Vuln Sentinel · 安全扫描平台</p>
</body>
</html>"""


def _password_reset_html(reset_link: str) -> str:
    """生成密码重置邮件的 HTML 正文。"""
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"></head>
<body style="font-family:-apple-system,'Segoe UI','Microsoft YaHei',sans-serif;color:#333;max-width:560px;margin:0 auto;padding:24px;">
  <h2 style="color:#d93025;">重置你的密码</h2>
  <p>你好！</p>
  <p>我们收到了你在<strong>Vuln Sentinel（Vuln Sentinel）</strong>重置密码的请求，请点击下方按钮设置新密码：</p>
  <p style="margin:24px 0;">
    <a href="{reset_link}" style="display:inline-block;background:#d93025;color:#fff;text-decoration:none;padding:12px 28px;border-radius:6px;font-weight:600;">重置密码</a>
  </p>
  <p>或复制以下链接到浏览器打开：</p>
  <p style="word-break:break-all;color:#d93025;">{reset_link}</p>
  <p style="color:#999;font-size:13px;">该重置链接有效期为 30 分钟，过期后需重新申请。如果你没有发起此操作，请忽略本邮件，你的密码不会被修改。</p>
  <hr style="border:none;border-top:1px solid #eee;margin:24px 0;">
  <p style="color:#999;font-size:12px;">Vuln Sentinel Vuln Sentinel · 安全扫描平台</p>
</body>
</html>"""


def send_verification_email(user_email: str, token: str, base_url: str) -> bool:
    """发送邮箱验证邮件。

    邮件中包含验证链接 ``{base_url}/verify-email?token={token}``。

    Args:
        user_email: 用户邮箱地址
        token: 邮箱验证 token
        base_url: 服务对外基础地址，用于拼接验证链接

    Returns:
        True 表示发送成功，False 表示发送失败或 SMTP 未配置
    """
    base = (base_url or "").rstrip("/")
    verify_link = f"{base}/verify-email?token={token}"
    html = _verification_html(verify_link)
    return _send_email(user_email, "【Vuln Sentinel】邮箱验证", html, email_type="verification")


def send_password_reset_email(user_email: str, token: str, base_url: str) -> bool:
    """发送密码重置邮件。

    邮件中包含重置链接 ``{base_url}/reset-password?token={token}``。

    Args:
        user_email: 用户邮箱地址
        token: 密码重置 token
        base_url: 服务对外基础地址，用于拼接重置链接

    Returns:
        True 表示发送成功，False 表示发送失败或 SMTP 未配置
    """
    base = (base_url or "").rstrip("/")
    reset_link = f"{base}/reset-password?token={token}"
    html = _password_reset_html(reset_link)
    return _send_email(user_email, "【Vuln Sentinel】密码重置", html, email_type="password_reset")

