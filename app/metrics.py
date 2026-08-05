"""Metrics helpers with optional Prometheus dependencies.

The project can run in lightweight environments without prometheus_client or
prometheus-fastapi-instrumentator installed. In that case the helpers become
no-ops so the application and tests can still import the package tree.
"""

from __future__ import annotations

import time
from typing import Any

try:  # pragma: no cover - optional dependency
    from fastapi import FastAPI
    from prometheus_client import Counter, Gauge, Histogram
    from prometheus_fastapi_instrumentator import Instrumentator
except Exception:  # pragma: no cover - graceful fallback
    FastAPI = Any  # type: ignore[assignment]
    Counter = Gauge = Histogram = None  # type: ignore[assignment]
    Instrumentator = None  # type: ignore[assignment]


class _NullMetric:
    def inc(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def dec(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def observe(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def labels(self, *_args: Any, **_kwargs: Any) -> "_NullMetric":
        return self


class _NullTimer:
    def __init__(self, start: float) -> None:
        self.start = start

    def __float__(self) -> float:
        return self.start


if Counter is None:
    scans_total = _NullMetric()
    scan_duration_seconds = _NullMetric()
    scan_cache_hits_total = _NullMetric()
    scan_cache_misses_total = _NullMetric()
    active_scans = _NullMetric()
    findings_total = _NullMetric()
    api_requests_total = _NullMetric()
else:
    scans_total = Counter(
        "vuln_sentinel_scans_total",
        "Total number of scans",
        ["status", "depth"],
    )
    scan_duration_seconds = Histogram(
        "vuln_sentinel_scan_duration_seconds",
        "Scan execution duration in seconds",
        buckets=(1, 5, 10, 30, 60, 120, 300, 600),
    )
    scan_cache_hits_total = Counter("vuln_sentinel_scan_cache_hits_total", "Total scan cache hits")
    scan_cache_misses_total = Counter("vuln_sentinel_scan_cache_misses_total", "Total scan cache misses")
    active_scans = Gauge("vuln_sentinel_active_scans", "Number of currently active scans")
    findings_total = Counter("vuln_sentinel_findings_total", "Total findings discovered", ["severity"])
    api_requests_total = Counter(
        "vuln_sentinel_api_requests_total",
        "Total API requests",
        ["method", "endpoint", "status_code"],
    )


def setup_metrics(app: Any) -> None:
    """Register metrics middleware when the optional package exists."""
    if Instrumentator is None:
        return None
    Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        should_respect_env_var=False,
        excluded_handlers=["/metrics", "/health/*", "/favicon.ico", "/robots.txt"],
    ).instrument(app).expose(
        app,
        endpoint="/metrics",
        include_in_schema=False,
        tags=["monitoring"],
    )


def record_scan_start() -> float:
    active_scans.inc()
    return time.time()


def record_scan_end(start_time: float, status: str = "success", depth: str = "standard") -> None:
    active_scans.dec()
    duration = time.time() - start_time
    scan_duration_seconds.observe(duration)
    scans_total.labels(status=status, depth=depth).inc()


def record_cache_hit() -> None:
    scan_cache_hits_total.inc()


def record_cache_miss() -> None:
    scan_cache_misses_total.inc()


def record_findings(findings: list[dict[str, Any]]) -> None:
    for finding in findings:
        severity = str(finding.get("severity") or "unknown")
        findings_total.labels(severity=severity).inc()


def record_api_request(method: str, endpoint: str, status_code: int) -> None:
    api_requests_total.labels(method=method, endpoint=endpoint, status_code=str(status_code)).inc()
