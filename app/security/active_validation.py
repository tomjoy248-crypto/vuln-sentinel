"""扫描模式策略，确保主动验证默认是无害、可回滚的。"""

from __future__ import annotations


def validate_mode(mode: str, authorized: bool, confirmed: bool) -> str:
    """校验扫描模式；隔离模式需要授权和管理员确认。"""
    normalized = (mode or "safe").strip().lower()
    if normalized not in {"safe", "isolated"}:
        raise ValueError("验证模式仅支持 safe 或 isolated")
    if normalized == "isolated" and (not authorized or not confirmed):
        raise ValueError("隔离验证需要明确授权并完成高风险确认")
    return normalized
