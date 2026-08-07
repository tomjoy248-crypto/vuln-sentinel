"""Metrics helpers with optional Prometheus dependencies.

The project can run in lightweight environments without prometheus_client or
prometheus-fastapi-instrumentator installed. In that case the helpers become
no-ops so the application and tests can still import the package tree.
"""

from __future__ import annotations

import os
import time
from typing import Any

try:  # pragma: no cover - optional dependency
    from fastapi import FastAPI, Header, HTTPException, Request
    from fastapi.responses import PlainTextResponse
    from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
except Exception:  # pragma: no cover - graceful fallback
    FastAPI = Any  # type: ignore[assignment]
    Counter = Gauge = Histogram = None  # type: ignore[assignment]
    generate_latest = None  # type: ignore[assignment]
    CONTENT_TYPE_LATEST = "text/plain; version=0.0.4"  # type: ignore[assignment]
    PlainTextResponse = Any  # type: ignore[assignment]


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


def _client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For", "").strip()
    if forwarded_for:
        candidate = forwarded_for.split(",", 1)[0].strip()
        if candidate:
            return candidate
    forwarded = request.headers.get("X-Real-IP", "").strip()
    if forwarded:
        return forwarded
    return request.client.host if request.client else "unknown"


def _metrics_allowed(request: Request, auth_header: str | None) -> bool:
    public_flag = os.environ.get("METRICS_PUBLIC", "0").strip().lower() in ("1", "true", "yes", "on")
    if public_flag:
        return True
    if _client_ip(request) in {"127.0.0.1", "::1", "localhost"}:
        return True
    token = os.environ.get("METRICS_AUTH_TOKEN", "").strip()
    if not token:
        return False
    if not auth_header:
        return False
    header = auth_header.strip()
    if header == token:
        return True
    if header.startswith("Bearer ") and header[7:].strip() == token:
        return True
    if header.startswith("Token ") and header[6:].strip() == token:
        return True
    return False


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
    """Register metrics endpoint with lightweight auth."""
    if generate_latest is None:
        return None

    @app.get("/metrics", include_in_schema=False)
    async def metrics_endpoint(request: Request, authorization: str | None = Header(None)) -> Any:
        if not _metrics_allowed(request, authorization):
            raise HTTPException(status_code=403, detail="metrics access denied")
        return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    return None


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



def record_findings(severity: str, count: int = 1) -> None:
    findings_total.labels(severity=severity).inc(count)
