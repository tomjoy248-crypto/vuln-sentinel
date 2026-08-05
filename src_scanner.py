"""Legacy SRC scanner compatibility layer.

This project has moved to the plugin-based scan pipeline, but a number of
modules and tests still import `src_scanner` directly. This module keeps the
old entry points available so the application can start cleanly while the rest
of the code continues to use the modern pipeline.
"""

from __future__ import annotations

from typing import Any

_evidence_store: Any = None


def set_evidence_store(store: Any) -> None:
    """Attach a shared evidence store used by legacy adapters."""
    global _evidence_store
    _evidence_store = store


def clear_evidence_store() -> None:
    """Detach the shared evidence store."""
    global _evidence_store
    _evidence_store = None


def get_evidence_store() -> Any:
    """Return the currently configured evidence store, if any."""
    return _evidence_store


def build_finding(**kwargs: Any) -> dict[str, Any]:
    """Build a legacy finding dictionary."""
    return dict(kwargs)


async def _empty(*_args: Any, **_kwargs: Any) -> list[dict[str, Any]]:
    return []


run_src_scan = _empty
detect_sqli_src = _empty
detect_xss_src = _empty
detect_info_leak_src = _empty
detect_csrf_src = _empty
detect_sensitive_paths_src = _empty
detect_outdated_components_src = _empty
detect_broken_access_control_src = _empty
detect_ssrf_src = _empty
detect_idor_src = _empty
detect_file_upload_src = _empty
detect_logic_bypass_src = _empty
detect_open_redirect_src = _empty
detect_xxe_src = _empty
detect_command_injection_src = _empty
detect_path_traversal_src = _empty
detect_rce_src = _empty
detect_clickjacking_src = _empty
detect_cors_src = _empty
detect_rate_limit_src = _empty
detect_security_headers_src = _empty
