"""敏感数据脱敏模块测试。"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.sanitization import redact_sensitive_data, safe_log_message


def test_redact_password_field():
    data = {"username": "alice", "password": "SuperSecret123!"}
    result = redact_sensitive_data(data)
    assert result["username"] == "alice"
    assert result["password"] == "***REDACTED***"


def test_redact_nested_sensitive_data():
    data = {
        "user": {"name": "bob"},
        "credentials": {"api_key": "sk-1234567890abcdef"},
    }
    result = redact_sensitive_data(data)
    assert result["user"]["name"] == "bob"
    assert result["credentials"] == "***REDACTED***"


def test_redact_bearer_token_value():
    data = {"note": "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"}
    result = redact_sensitive_data(data)
    assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in result["note"]
    assert "***REDACTED***" in result["note"]


def test_redact_list_with_sensitive_items():
    data = [
        {"name": "item1"},
        {"token": "abc123"},
    ]
    result = redact_sensitive_data(data)
    assert result[0]["name"] == "item1"
    assert result[1]["token"] == "***REDACTED***"


def test_redact_leaves_normal_data_unchanged():
    data = {"url": "https://example.com", "count": 42, "enabled": True}
    result = redact_sensitive_data(data)
    assert result == data


def test_safe_log_message_redacts_bearer():
    msg = "Request failed with Authorization: Bearer abcdef1234567890"
    result = safe_log_message(msg)
    assert "abcdef1234567890" not in result
    assert "Bearer ***REDACTED***" in result


def test_safe_log_message_redacts_password_like_pairs():
    msg = "login failed for user=x password=MyP@ssw0rd"
    result = safe_log_message(msg)
    assert "MyP@ssw0rd" not in result
    assert "password=***REDACTED***" in result


def test_safe_log_message_ignores_normal_text():
    msg = "scan completed for https://example.com"
    assert safe_log_message(msg) == msg
