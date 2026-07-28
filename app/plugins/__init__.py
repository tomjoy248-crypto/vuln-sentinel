"""插件化检测引擎。

提供基础接口和注册表，用于动态加载和管理漏洞检测插件。

使用方式:
    from app.plugins import DetectorRegistry, BaseVulnDetector

    # 注册自定义检测器
    class MyDetector(BaseVulnDetector):
        name = "my_custom"
        async def detect(self, context: ScanContext) -> List[Finding]:
            ...

    DetectorRegistry.register(MyDetector())

    # 运行所有检测器
    results = await DetectorRegistry.run_all(context)
"""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("vuln_sentinel.plugins")


@dataclass
class ScanContext:
    """扫描上下文，传递给每个检测器。"""
    url: str
    headers: Dict[str, str] = field(default_factory=dict)
    is_https: bool = False
    ssl_info: Optional[Dict[str, Any]] = None
    waf_list: List[Dict[str, Any]] = field(default_factory=list)
    depth: str = "standard"
    # 可扩展：cookies, session, auth_token 等


@dataclass
class Finding:
    """插件检测结果。"""
    title: str
    type: str
    severity: str  # critical / high / medium / low / info
    description: str = ""
    url: str = ""
    parameter: str = ""
    evidence: Dict[str, Any] = field(default_factory=dict)
    fix_suggestion: str = ""
    confidence: str = "high"
    owasp_category: str = ""
    cwe_id: str = ""


class BaseVulnDetector(ABC):
    """漏洞检测器基类。

    所有检测插件必须继承此类并实现 detect 方法。
    """

    # 检测器名称标识
    name: str = ""
    # 检测器版本
    version: str = "1.0"
    # 支持的扫描深度（quick / standard / deep）
    supported_depths: List[str] = field(default_factory=lambda: ["standard", "deep"])

    @abstractmethod
    async def detect(self, context: ScanContext) -> List[Finding]:
        """执行检测。

        Args:
            context: 扫描上下文

        Returns:
            发现的问题列表（空列表表示未发现）
        """
        ...

    async def is_applicable(self, context: ScanContext) -> bool:
        """判断当前扫描场景是否适用本检测器。

        子类可覆盖此方法实现条件检测。
        """
        return context.depth in self.supported_depths


class DetectorRegistry:
    """检测器注册表。

    管理所有已注册的检测器，提供批量运行能力。
    单例模式，模块级全局实例。
    """

    _detectors: List[BaseVulnDetector] = []
    _enabled: Dict[str, bool] = {}  # name -> enabled

    @classmethod
    def register(cls, detector: BaseVulnDetector) -> None:
        """注册检测器。"""
        if not detector.name:
            raise ValueError("Detector must have a name")
        cls._detectors.append(detector)
        cls._enabled[detector.name] = True
        logger.info("Detector registered: %s v%s", detector.name, detector.version)

    @classmethod
    def unregister(cls, name: str) -> bool:
        """注销检测器。"""
        for i, d in enumerate(cls._detectors):
            if d.name == name:
                cls._detectors.pop(i)
                cls._enabled.pop(name, None)
                logger.info("Detector unregistered: %s", name)
                return True
        return False

    @classmethod
    def get(cls, name: str) -> Optional[BaseVulnDetector]:
        """按名称获取检测器。"""
        for d in cls._detectors:
            if d.name == name:
                return d
        return None

    @classmethod
    def list(cls) -> List[BaseVulnDetector]:
        """列出所有已注册检测器。"""
        return cls._detectors.copy()

    @classmethod
    def set_enabled(cls, name: str, enabled: bool) -> None:
        """启用/禁用检测器。"""
        cls._enabled[name] = enabled

    @classmethod
    def is_enabled(cls, name: str) -> bool:
        """检测器是否启用。"""
        return cls._enabled.get(name, True)

    @classmethod
    async def run_all(cls, context: ScanContext) -> Dict[str, List[Finding]]:
        """并行运行所有启用的检测器。

        Args:
            context: 扫描上下文

        Returns:
            字典：检测器名称 -> 发现的问题列表
        """
        tasks = []
        names = []
        for detector in cls._detectors:
            if not cls.is_enabled(detector.name):
                continue
            if not await detector.is_applicable(context):
                continue
            tasks.append(detector.detect(context))
            names.append(detector.name)

        if not tasks:
            return {}

        results = await asyncio.gather(*tasks, return_exceptions=True)
        findings_map: Dict[str, List[Finding]] = {}
        for name, result in zip(names, results):
            if isinstance(result, Exception):
                logger.warning("Detector %s failed: %s", name, result)
                findings_map[name] = []
            else:
                findings_map[name] = result
        return findings_map

    @classmethod
    def reset(cls) -> None:
        """清空所有注册（主要用于测试）。"""
        cls._detectors.clear()
        cls._enabled.clear()
