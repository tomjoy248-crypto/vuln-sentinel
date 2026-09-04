"""Legacy SRC scanner compatibility layer.

This project has moved to the plugin-based scan pipeline, but a number of
modules and tests still import `src_scanner` directly. This module keeps the
old entry points available so the application can start cleanly while the rest
of the code continues to use the modern pipeline.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import parse_qs, urlparse

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


def _query_params(url: str) -> list[str]:
    """Return bounded query parameter names for legacy detector adapters."""
    return list(parse_qs(urlparse(url).query, keep_blank_values=True).keys())[:10]


async def detect_sqli_src(url: str, *_args: Any, **_kwargs: Any) -> list[dict[str, Any]]:
    """Delegate SQLi detection to the maintained implementation."""
    from main import detect_sqli
    return await detect_sqli(url, _query_params(url))


async def detect_xss_src(url: str, *_args: Any, **_kwargs: Any) -> list[dict[str, Any]]:
    """Delegate reflected XSS detection to the maintained implementation."""
    from main import detect_reflected_xss
    return await detect_reflected_xss(url, _query_params(url))


async def run_src_scan(url: str, headers: dict | None = None, is_https: bool = False, ssl_info: dict | None = None) -> list[dict[str, Any]]:
    """Compatibility entry point using the maintained safe probes."""
    findings: list[dict[str, Any]] = []
    findings.extend(await detect_sqli_src(url))
    findings.extend(await detect_xss_src(url))
    return findings


detect_info_leak_src = _empty
detect_csrf_src = _empty
detect_sensitive_paths_src = _empty
detect_outdated_components_src = _empty
detect_broken_access_control_src = _empty
async def detect_ssrf_src(url: str, *_args: Any, **_kwargs: Any) -> list[dict[str, Any]]:
    from main import detect_ssrf_enhanced
    return await detect_ssrf_enhanced(url, _query_params(url))


async def detect_idor_src(url: str, *_args: Any, **_kwargs: Any) -> list[dict[str, Any]]:
    from main import detect_idor_risk
    return await detect_idor_risk(url, _query_params(url))
detect_file_upload_src = _empty
detect_logic_bypass_src = _empty
async def detect_open_redirect_src(url: str, *_args: Any, **_kwargs: Any) -> list[dict[str, Any]]:
    from main import detect_open_redirect
    return await detect_open_redirect(url, _query_params(url))


async def detect_xxe_src(url: str, headers: dict | None = None, body: str = "", **_kwargs: Any) -> list[dict[str, Any]]:
    from main import detect_xxe
    return await detect_xxe(url, _query_params(url))


async def detect_command_injection_src(url: str, *_args: Any, **_kwargs: Any) -> list[dict[str, Any]]:
    from main import detect_command_injection
    return await detect_command_injection(url, _query_params(url))
detect_path_traversal_src = _empty
detect_rce_src = _empty
detect_clickjacking_src = _empty
detect_cors_src = _empty
detect_rate_limit_src = _empty
detect_security_headers_src = _empty
detect_deserialization_src = _empty
