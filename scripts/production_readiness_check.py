"""Validate production prerequisites without exposing secret values.

Run this in a deployment environment after injecting secrets and before
starting the service. It deliberately checks presence and safe modes only;
it never prints credential contents.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


TRUE_VALUES = {"1", "true", "yes", "on"}


def enabled(name: str) -> bool:
    """Return whether an environment flag is explicitly enabled."""
    return os.environ.get(name, "").strip().lower() in TRUE_VALUES


def main() -> int:
    """Report production configuration gaps and return a CI-friendly status."""
    errors: list[str] = []
    warnings: list[str] = []

    if len(os.environ.get("JWT_SECRET", "").strip()) < 32:
        errors.append("JWT_SECRET must contain at least 32 characters")
    if not os.environ.get("CREDENTIAL_ENCRYPT_KEY", "").strip():
        errors.append("CREDENTIAL_ENCRYPT_KEY is required")
    if os.environ.get("ALLOWED_ORIGINS", "").strip() in {"", "*"}:
        errors.append("ALLOWED_ORIGINS must list explicit production origins")
    if not os.environ.get("REDIS_URL", "").strip():
        warnings.append("REDIS_URL is not configured; queue and rate limits use local fallback")
    if enabled("ALIPAY_MOCK") or enabled("WECHAT_MOCK"):
        errors.append("payment mock mode must be disabled in production")

    llm_enabled = enabled("LLM_ENABLED")
    if llm_enabled and not os.environ.get("LLM_API_KEY", "").strip():
        errors.append("LLM_ENABLED requires LLM_API_KEY")
    if not llm_enabled:
        warnings.append("AI advisor will use keyword fallback until LLM_ENABLED and LLM_API_KEY are configured")

    certificate_path = os.environ.get("WINDOWS_SIGNING_CERT_PATH", "").strip()
    if certificate_path and not Path(certificate_path).is_file():
        errors.append("WINDOWS_SIGNING_CERT_PATH does not point to a readable certificate")
    if not certificate_path:
        warnings.append("Windows installer will be unsigned until WINDOWS_SIGNING_CERT_PATH is configured")

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    print("Production readiness configuration passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
