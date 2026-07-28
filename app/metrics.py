"""Prometheus 指标暴露。

使用 prometheus-fastapi-instrumentator 自动收集 HTTP 指标，
并注册自定义业务指标：

自定义指标：
- scans_total: 扫描总数（labels: status, depth）
- scan_duration_seconds: 扫描耗时直方图
- scan_cache_hits_total: 缓存命中次数
- scan_cache_misses_total: 缓存未命中次数
- active_scans: 当前活跃扫描数（Gauge）
- findings_total: 发现的漏洞总数（labels: severity）
"""

from __future__ import annotations

import time
from typing import Any, Optional

from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI, Response


# ---------- 自定义业务指标 ----------

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

scan_cache_hits_total = Counter(
    "vuln_sentinel_scan_cache_hits_total",
    "Total scan cache hits",
)

scan_cache_misses_total = Counter(
    "vuln_sentinel_scan_cache_misses_total",
    "Total scan cache misses",
)

active_scans = Gauge(
    "vuln_sentinel_active_scans",
    "Number of currently active scans",
)

findings_total = Counter(
    "vuln_sentinel_findings_total",
    "Total findings discovered",
    ["severity"],
)

api_requests_total = Counter(
    "vuln_sentinel_api_requests_total",
    "Total API requests",
    ["method", "endpoint", "status_code"],
)


def setup_metrics(app: FastAPI) -> None:
    """在 FastAPI 应用上注册 Prometheus 指标。

    Args:
        app: FastAPI 应用实例
    """
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


def record_scan_start() -> Any:
    """记录扫描开始，返回计时器。"""
    active_scans.inc()
    return time.time()


def record_scan_end(start_time: float, status: str = "success", depth: str = "standard") -> None:
    """记录扫描结束。"""
    active_scans.dec()
    duration = time.time() - start_time
    scan_duration_seconds.observe(duration)
    scans_total.labels(status=status, depth=depth).inc()


def record_cache_hit() -> None:
    """记录缓存命中。"""
    scan_cache_hits_total.inc()


def record_cache_miss() -> None:
    """记录缓存未命中。"""
    scan_cache_misses_total.inc()


def record_findings(findings: list) -> None:
    """记录发现的漏洞。"""
    for f in findings:
        severity = f.get("severity", "unknown") if isinstance(f, dict) else "unknown"
        findings_total.labels(severity=severity).inc()
