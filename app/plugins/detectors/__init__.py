"""漏洞检测插件集合。"""

from __future__ import annotations

from app.plugins.detectors.business import (
    APIAuthMissingDetector,
    AuthWeaknessDetector,
    BruteforceProtectionDetector,
    ClickjackingDetector,
    SensitiveConfigExposureDetector,
)
from app.plugins.detectors.src_adapter import (
    BrokenAccessControlDetector,
    CommandInjectionDetector,
    CSRFDetector,
    DeserializationDetector,
    FileUploadDetector,
    IDORDetector,
    InfoLeakDetector,
    LogicBypassDetector,
    OpenRedirectDetector,
    OutdatedComponentDetector,
    PathTraversalDetector,
    ReflectedXSSDetector,
    SensitivePathDetectorPlugin,
    SQLiDetector,
    SSTIDetector,
    SSRFDetector,
    XXEDetector,
)

__all__ = [
    "SQLiDetector",
    "SSTIDetector",
    "ReflectedXSSDetector",
    "InfoLeakDetector",
    "CSRFDetector",
    "SensitivePathDetectorPlugin",
    "AuthWeaknessDetector",
    "BruteforceProtectionDetector",
    "APIAuthMissingDetector",
    "SensitiveConfigExposureDetector",
    "ClickjackingDetector",
    "OutdatedComponentDetector",
    "BrokenAccessControlDetector",
    "SSRFDetector",
    "IDORDetector",
    "FileUploadDetector",
    "LogicBypassDetector",
    "OpenRedirectDetector",
    "XXEDetector",
    "CommandInjectionDetector",
    "PathTraversalDetector",
    "DeserializationDetector",
]
