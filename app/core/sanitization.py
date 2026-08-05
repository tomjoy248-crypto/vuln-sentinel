"""敏感数据脱敏工具。

用于日志、审计、错误响应等场景，避免密码、Token、密钥等敏感信息泄漏。
"""

from __future__ import annotations

import copy
import re
from typing import Any

# 需要脱敏的敏感字段名（不区分大小写）
_SENSITIVE_KEYS: frozenset[str] = frozenset(
    {
        "password",
        "pwd",
        "passwd",
        "secret",
        "jwt_secret",
        "api_key",
        "apikey",
        "access_key",
        "secret_key",
        "private_key",
        "ssh_key",
        "token",
        "refresh_token",
        "authorization",
        "credentials",
        "credential",
        "cookie",
        "session",
        "credit_card",
        "cvv",
        "ssn",
    }
)

# 常见密钥/Token 值模式：用于对字符串值进行模糊匹配
_SECRET_VALUE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^Bearer\s+[A-Za-z0-9_\-\.]+$"),  # JWT / Bearer token
    re.compile(r"^Basic\s+[A-Za-z0-9+/=]+$"),  # Basic auth
    re.compile(r"^sk-[A-Za-z0-9]{20,}$"),  # OpenAI style API key
    re.compile(r"^AK[A-Za-z0-9]{16,}$"),  # Cloud access key style
    re.compile(r"^[A-Za-z0-9/+=]{40,}$"),  # Long base64-like secret
)

_REDACTED = "***REDACTED***"


def _is_sensitive_key(key: str) -> bool:
    """判断字段名是否为敏感字段。"""
    normalized = key.lower().strip().replace("-", "_")
    return normalized in _SENSITIVE_KEYS or any(
        sensitive in normalized for sensitive in _SENSITIVE_KEYS
    )


def _looks_like_secret_value(value: str) -> bool:
    """判断字符串值是否像密钥/Token。"""
    return any(pattern.match(value) for pattern in _SECRET_VALUE_PATTERNS)


def redact_sensitive_data(
    data: Any,
    *,
    depth: int = 0,
    max_depth: int = 10,
) -> Any:
    """递归脱敏敏感数据。

    支持 dict、list、tuple、set 以及基本类型。对 dict 中敏感 key 的值、
    以及看起来像密钥/Token 的字符串值进行脱敏。

    Args:
        data: 待脱敏的数据。
        depth: 当前递归深度（内部使用）。
        max_depth: 最大递归深度，防止循环/过深结构。

    Returns:
        脱敏后的数据副本（尽量不修改原始对象）。
    """
    if depth > max_depth:
        return data

    if isinstance(data, dict):
        result: dict[str, Any] = {}
        for key, value in data.items():
            if not isinstance(key, str):
                key = str(key)
            if _is_sensitive_key(key):
                result[key] = _REDACTED
            else:
                result[key] = redact_sensitive_data(value, depth=depth + 1, max_depth=max_depth)
        return result

    if isinstance(data, list):
        return [redact_sensitive_data(item, depth=depth + 1, max_depth=max_depth) for item in data]

    if isinstance(data, tuple):
        return tuple(
            redact_sensitive_data(item, depth=depth + 1, max_depth=max_depth) for item in data
        )

    if isinstance(data, set):
        return {
            redact_sensitive_data(item, depth=depth + 1, max_depth=max_depth) for item in data
        }

    if isinstance(data, str):
        if _looks_like_secret_value(data):
            return _REDACTED
        # 对可能包含 Authorization header 的长文本做部分脱敏
        if "authorization" in data.lower() and len(data) > 30:
            return re.sub(
                r"([Aa]uthorization[\"']?\s*[:=]\s*[\"']?)(Bearer\s+[A-Za-z0-9_\-\.]+)",
                r"\1***REDACTED***",
                data,
            )
        return data

    return copy.copy(data) if hasattr(data, "__copy__") else data


def safe_log_message(message: str) -> str:
    """对日志消息中的常见敏感信息进行脱敏。

    主要用于不可控的异常消息或第三方返回内容，避免将密钥/密码写入日志。
    """
    if not isinstance(message, str):
        message = str(message)

    # 脱敏 Bearer token
    message = re.sub(
        r"Bearer\s+[A-Za-z0-9_\-\.]{10,}",
        "Bearer ***REDACTED***",
        message,
    )
    # 脱敏 password=xxx
    message = re.sub(
        r"(password|pwd|secret|token|api_key|apikey)[\"']?\s*[:=]\s*[\"']?[^\s&\"']+",
        r"\1=***REDACTED***",
        message,
        flags=re.IGNORECASE,
    )
    return message
