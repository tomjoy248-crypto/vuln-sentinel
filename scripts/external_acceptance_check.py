"""Run non-destructive checks for externally supplied acceptance resources.

The checker validates reachability and configuration presence only. It never
performs active attacks, sends payment requests, or prints secret values.
"""

from __future__ import annotations

import os
import socket
import sys
from urllib.parse import urlparse


def check_url(name: str, value: str, required: bool = False) -> str:
    """Check that a URL is syntactically valid and its host resolves."""
    if not value:
        return f"BLOCKED {name}: URL not provided" if required else f"SKIP {name}: not configured"
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https", "redis", "rediss"} or not parsed.hostname:
        return f"BLOCKED {name}: invalid URL"
    try:
        socket.getaddrinfo(parsed.hostname, parsed.port or (443 if parsed.scheme == "https" else 80))
    except OSError:
        return f"BLOCKED {name}: host does not resolve"
    return f"READY {name}: host resolves (active authorization required)"


def main() -> int:
    """Print readiness for all seven external acceptance tracks."""
    results = [
        check_url("TARGET_BASE_URL", os.getenv("TARGET_BASE_URL", ""), required=True),
        check_url("REDIS_URL", os.getenv("REDIS_URL", ""), required=True),
        check_url("LLM_BASE_URL", os.getenv("LLM_BASE_URL", "")),
    ]
    required = {
        "TEST_ACCOUNT_A": "dual-account acceptance",
        "TEST_ACCOUNT_B": "dual-account acceptance",
        "LLM_API_KEY": "real LLM acceptance",
        "PAYMENT_WEBHOOK_SECRET": "payment signature acceptance",
        "WINDOWS_CERTIFICATE_BASE64": "Windows signing",
        "VAULT_ADDR": "Vault integration",
        "AWS_REGION": "AWS Secrets Manager integration",
    }
    for key, purpose in required.items():
        if os.getenv(key, "").strip():
            results.append(f"READY {purpose}: {key} supplied (value hidden)")
        else:
            results.append(f"BLOCKED {purpose}: {key} not supplied")
    blocked = 0
    for result in results:
        print(result)
        blocked += result.startswith("BLOCKED ")
    print(f"Summary: {len(results) - blocked} ready, {blocked} blocked")
    return 1 if blocked else 0


if __name__ == "__main__":
    sys.exit(main())
