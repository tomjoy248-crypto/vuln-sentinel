"""用户生命周期服务测试。

测试 app/services/user_lifecycle.py 和 email_service.py 的核心功能：
- 邮箱验证 token 生成与验证流程
- 密码重置 token 生成与重置流程
- token 过期 / 重复使用场景

直接调用服务函数（不通过 HTTP）。
"""

import os
import sys
import uuid
from datetime import datetime, timedelta

import bcrypt

os.environ["DB_DIR"] = "/tmp/v11-test"
os.environ["DB_NAME"] = "test.db"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import main  # noqa: E402,F401  -- 导入 main 以初始化数据库路径与表结构
from app.db.session import get_db  # noqa: E402
from app.services import email_service, user_lifecycle  # noqa: E402

_TIME_FMT = "%Y-%m-%d %H:%M:%S"


def _create_test_user() -> int:
    """直接在数据库中创建测试用户，返回 user_id。"""
    name = "life_" + uuid.uuid4().hex[:8]
    hashed = bcrypt.hashpw(b"pass1234", bcrypt.gensalt(rounds=12)).decode("utf-8")
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (username, password, email, role, team_id, credits, created_at) "
            "VALUES (?, ?, ?, 'member', 0, 10, ?)",
            (name, hashed, f"{name}@example.com", datetime.now().strftime(_TIME_FMT)),
        )
        conn.commit()
        row = conn.execute("SELECT id FROM users WHERE username = ?", (name,)).fetchone()
        return row["id"]
    finally:
        conn.close()


# ---------- 邮箱验证 ----------


def test_email_verification_flow():
    """邮箱验证 token 生成后可成功验证，并标记 email_verified=1。"""
    user_id = _create_test_user()
    token = user_lifecycle.generate_email_verification_token(user_id)
    assert token

    result = user_lifecycle.verify_email(token)
    assert result["success"] is True

    conn = get_db()
    try:
        row = conn.execute("SELECT email_verified FROM users WHERE id = ?", (user_id,)).fetchone()
        assert row["email_verified"] == 1
    finally:
        conn.close()


def test_email_verification_token_reuse():
    """已使用的验证 token 不能重复验证。"""
    user_id = _create_test_user()
    token = user_lifecycle.generate_email_verification_token(user_id)

    first = user_lifecycle.verify_email(token)
    assert first["success"] is True

    second = user_lifecycle.verify_email(token)
    assert second["success"] is False
    assert "已使用" in second["message"] or "重复" in second["message"]


def test_email_verification_invalid_token():
    """无效的验证 token 返回失败。"""
    result = user_lifecycle.verify_email("invalid-" + uuid.uuid4().hex)
    assert result["success"] is False
    assert "无效" in result["message"] or "不存在" in result["message"]


def test_email_verification_expired_token():
    """超过 24 小时有效期的验证 token 返回失败。"""
    user_id = _create_test_user()
    token = user_lifecycle.generate_email_verification_token(user_id)
    # 手动将 created_at 改为 25 小时前（超过 24h TTL）
    expired = (datetime.now() - timedelta(hours=25)).strftime(_TIME_FMT)
    conn = get_db()
    try:
        conn.execute(
            "UPDATE user_email_verifications SET created_at = ? WHERE token = ?",
            (expired, token),
        )
        conn.commit()
    finally:
        conn.close()

    result = user_lifecycle.verify_email(token)
    assert result["success"] is False
    assert "过期" in result["message"]


# ---------- 密码重置 ----------


def test_password_reset_flow():
    """密码重置 token 生成后可成功重置密码（bcrypt 哈希后可校验）。"""
    user_id = _create_test_user()
    token = user_lifecycle.generate_password_reset_token(user_id)
    assert token

    new_password = "newpass456"
    result = user_lifecycle.reset_password(token, new_password)
    assert result["success"] is True

    conn = get_db()
    try:
        row = conn.execute("SELECT password FROM users WHERE id = ?", (user_id,)).fetchone()
        assert bcrypt.checkpw(new_password.encode("utf-8"), row["password"].encode("utf-8"))
    finally:
        conn.close()


def test_password_reset_token_reuse():
    """已使用的密码重置 token 不能重复使用。"""
    user_id = _create_test_user()
    token = user_lifecycle.generate_password_reset_token(user_id)

    first = user_lifecycle.reset_password(token, "newpass1")
    assert first["success"] is True

    second = user_lifecycle.reset_password(token, "newpass2")
    assert second["success"] is False
    assert "使用" in second["message"]


def test_password_reset_expired_token():
    """超过 30 分钟有效期的密码重置 token 返回失败。"""
    user_id = _create_test_user()
    token = user_lifecycle.generate_password_reset_token(user_id)
    # 手动将 expires_at 改为 31 分钟前（超过 30min TTL）
    expired = (datetime.now() - timedelta(minutes=31)).strftime(_TIME_FMT)
    conn = get_db()
    try:
        conn.execute(
            "UPDATE user_password_resets SET expires_at = ? WHERE token = ?",
            (expired, token),
        )
        conn.commit()
    finally:
        conn.close()

    result = user_lifecycle.reset_password(token, "newpass456")
    assert result["success"] is False
    assert "过期" in result["message"]


def test_password_reset_empty_password():
    """空密码重置返回失败。"""
    user_id = _create_test_user()
    token = user_lifecycle.generate_password_reset_token(user_id)
    result = user_lifecycle.reset_password(token, "")
    assert result["success"] is False
    assert "空" in result["message"]


def test_password_reset_invalid_token():
    """无效的密码重置 token 返回失败。"""
    result = user_lifecycle.reset_password("invalid-" + uuid.uuid4().hex, "newpass456")
    assert result["success"] is False
    assert "无效" in result["message"] or "不存在" in result["message"]


# ---------- 用户查询 ----------


def test_get_user_by_email():
    """按邮箱查找用户，不存在或空邮箱返回 None。"""
    user_id = _create_test_user()
    conn = get_db()
    try:
        email = conn.execute("SELECT email FROM users WHERE id = ?", (user_id,)).fetchone()["email"]
    finally:
        conn.close()

    found = user_lifecycle.get_user_by_email(email)
    assert found is not None
    assert found["id"] == user_id

    # 不存在的邮箱返回 None
    assert user_lifecycle.get_user_by_email("none-" + uuid.uuid4().hex + "@example.com") is None
    # 空邮箱返回 None
    assert user_lifecycle.get_user_by_email("") is None


# ---------- 邮件服务 ----------


def test_email_service_smtp_not_configured():
    """SMTP 未配置时发送验证/重置邮件返回 False 且不抛异常。"""
    assert email_service.send_verification_email("test@example.com", "tok", "http://localhost:8000") is False
    assert email_service.send_password_reset_email("test@example.com", "tok", "http://localhost:8000") is False


def test_email_service_is_smtp_configured():
    """SMTP 配置检测：未配置返回 False，三项齐备时返回 True。"""
    assert email_service.is_smtp_configured() is False

    keys = ("SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD")
    backup = {k: os.environ.get(k) for k in keys}
    try:
        os.environ["SMTP_HOST"] = "smtp.example.com"
        os.environ["SMTP_USER"] = "user@example.com"
        os.environ["SMTP_PASSWORD"] = "secret"
        assert email_service.is_smtp_configured() is True
    finally:
        for k, v in backup.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
