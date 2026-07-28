"""漏洞检测插件集合。"""

from __future__ import annotations

from app.plugins.detectors.src_adapter import (
    BrokenAccessControlDetector,
    CSRFDetector,
    FileUploadDetector,
    IDORDetector,
    InfoLeakDetector,
    LogicBypassDetector,
    OpenRedirectDetector,
    OutdatedComponentDetector,
    ReflectedXSSDetector,
    SQLiDetector,
    SSRFDetector,
    SensitivePathDetectorPlugin,
    XXEDetector,
)

__all__ = [
    "SQLiDetector",
    "ReflectedXSSDetector",
    "InfoLeakDetector",
    "CSRFDetector",
    "SensitivePathDetectorPlugin",
    "OutdatedComponentDetector",
    "BrokenAccessControlDetector",
    "SSRFDetector",
    "IDORDetector",
    "FileUploadDetector",
    "LogicBypassDetector",
    "OpenRedirectDetector",
    "XXEDetector",
]
