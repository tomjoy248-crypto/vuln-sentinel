"""插件化检测引擎。

提供基础接口和注册表，用于动态加载和管理漏洞检测插件。

使用方式:
    from app.plugins import DetectorRegistry, BaseVulnDetector

    # 注册自定义检测器
    class MyDetector(BaseVulnDetector):
        name = "my_custom"
        async def detect(self, context: ScanContext) -> list[Finding]:
            ...

    DetectorRegistry.register(MyDetector())

    # 运行所有检测器
    results = await DetectorRegistry.run_all(context)
"""

from __future__ import annotations

import asyncio
import builtins
import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("vuln_sentinel.plugins")


@dataclass
class VulnLocation:
    """漏洞位置信息，支持精准定位。"""

    url: str = ""
    method: str = "GET"
    parameter: str = ""  # 参数名
    parameter_type: str = ""  # query / body / header / cookie / path
    code_location: str = ""  # 文件名:行号（白盒场景）
    snippet: str = ""  # 触发点上下文


@dataclass
class Evidence:
    """漏洞证据，包含请求/响应片段。"""

    request_raw: str = ""  # 原始请求文本
    response_raw: str = ""  # 原始响应文本
    matched_signature: str = ""  # 命中签名
    payload: str = ""  # 测试 payload
    notes: str = ""  # 备注
    screenshot: str | None = None  # 证据截图
    extra: dict[str, Any] = field(default_factory=dict)  # 扩展字段


@dataclass
class FixSuggestion:
    """修复建议，按平台组织。"""

    generic: str = ""  # 通用修复说明
    by_platform: dict[str, str] = field(
        default_factory=dict
    )  # nginx/apache/express/flask/spring_boot/cloudflare
    risk_note: str = ""  # 风险提示


@dataclass
class ScanContext:
    """扫描上下文，传递给每个检测器。"""

    url: str
    headers: dict[str, str] = field(default_factory=dict)
    body: str = ""
    is_https: bool = False
    ssl_info: dict[str, Any] | None = None
    waf_list: list[dict[str, Any]] = field(default_factory=list)
    depth: str = "standard"
    # 证据链：检测器可从中获取最近的请求/响应片段
    evidence_store: EvidenceStore | None = None


@dataclass
class EvidenceStore:
    """轻量级证据存储，记录扫描过程中最近几次 HTTP 交互。"""

    max_entries: int = 20
    _entries: list[dict[str, Any]] = field(default_factory=list)

    def record(
        self,
        method: str,
        url: str,
        request_text: str,
        response_text: str,
        payload: str = "",
        meta: dict[str, Any] | None = None,
    ) -> None:
        """记录一次 HTTP 交互。"""
        self._entries.append(
            {
                "id": str(uuid.uuid4())[:8],
                "method": method,
                "url": url,
                "request_raw": request_text,
                "response_raw": response_text,
                "payload": payload,
                "meta": meta or {},
            }
        )
        if len(self._entries) > self.max_entries:
            self._entries.pop(0)

    def get_by_url(self, url: str) -> dict[str, Any] | None:
        """按 URL 查找最近的交互记录。"""
        for entry in reversed(self._entries):
            if entry["url"] == url:
                return entry
        return None

    def latest(self) -> dict[str, Any] | None:
        """返回最近一条记录。"""
        return self._entries[-1] if self._entries else None


@dataclass
class Finding:
    """插件检测结果。

    字段说明：
    - id: 唯一标识
    - title: 漏洞标题
    - type: 漏洞类型
    - severity: 严重度 critical/high/medium/low/info
    - confidence: 置信度 high/medium/low
    - cvss_score: CVSS v3.1 分数（可选）
    - cwe_id: CWE 编号
    - owasp_category: OWASP 分类
    - description: 漏洞描述
    - url: 漏洞 URL（兼容旧字段）
    - parameter: 漏洞参数（兼容旧字段）
    - location: 精准位置信息
    - evidence: 证据对象
    - raw_evidence: 原始证据字典（兼容旧数据）
    - fix_suggestion: 修复建议文本（兼容旧字段）
    - fix: 结构化修复建议
    - status: 状态 open/confirmed/false_positive/fixed
    """

    # 基础信息
    title: str
    type: str
    severity: str  # critical / high / medium / low / info
    id: str = field(default_factory=lambda: f"VS-{str(uuid.uuid4())[:8].upper()}")

    # 分类与评分
    confidence: str = "high"
    cvss_score: float | None = None
    severity_score: int | None = None
    cvss_vector: str = ""
    cwe_id: str = ""
    owasp_category: str = ""

    # 描述与影响
    description: str = ""
    impact: str = ""

    # 位置（兼容旧字段 + 新结构化字段）
    url: str = ""
    parameter: str = ""
    location: VulnLocation = field(default_factory=VulnLocation)

    # 证据
    evidence: Evidence = field(default_factory=Evidence)
    raw_evidence: dict[str, Any] = field(default_factory=dict)

    # 修复建议
    fix_suggestion: str = ""
    fix: FixSuggestion = field(default_factory=FixSuggestion)
    fix_code: dict[str, str] = field(default_factory=dict)

    # 复现与参考
    reproduce_steps: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)

    # 元信息
    discovered_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    # 状态
    status: str = "open"

    def to_dict(self) -> dict[str, Any]:
        """转换为兼容旧系统的字典格式。"""
        evidence = {
            "request": self.evidence.request_raw,
            "response": self.evidence.response_raw,
            "request_raw": self.evidence.request_raw,
            "response_raw": self.evidence.response_raw,
            "matched_signature": self.evidence.matched_signature,
            "payload": self.evidence.payload,
            "notes": self.evidence.notes,
            "screenshot": self.evidence.screenshot,
            **self.raw_evidence,
            **self.evidence.extra,
        }
        # 保持旧版 key 的别名兼容
        if self.evidence.request_raw and "request" not in self.raw_evidence:
            evidence["request"] = self.evidence.request_raw
        if self.evidence.response_raw and "response" not in self.raw_evidence:
            evidence["response"] = self.evidence.response_raw

        result = {
            "id": self.id,
            "name": self.title,
            "title": self.title,
            "type": self.type,
            "severity": self.severity,
            "severity_score": self.severity_score,
            "level": {
                "critical": "严重",
                "high": "高风险",
                "medium": "中风险",
                "low": "低风险",
                "info": "信息",
            }.get(self.severity, "中风险"),
            "level_zh": {
                "critical": "严重",
                "high": "高风险",
                "medium": "中风险",
                "low": "低风险",
                "info": "信息",
            }.get(self.severity, "中风险"),
            "confidence_level": self.confidence,
            "confidence": self.confidence,
            "cvss_score": self.cvss_score,
            "cvss_vector": self.cvss_vector,
            "cwe_id": self.cwe_id,
            "owasp": self.owasp_category,
            "owasp_category": self.owasp_category,
            "summary": self.description,
            "description": self.description,
            "impact": self.impact or self.description,
            "url": self.url or self.location.url,
            "parameter": self.parameter or self.location.parameter,
            "location": self.location.snippet
            or self.location.parameter
            or self.location.code_location
            or self.location.url
            or "",
            "location_detail": {
                "url": self.location.url or self.url,
                "method": self.location.method,
                "parameter": self.location.parameter or self.parameter,
                "parameter_type": self.location.parameter_type,
                "code_location": self.location.code_location,
                "snippet": self.location.snippet,
            },
            "evidence": evidence,
            "reproduce_steps": self.reproduce_steps,
            "references": self.references,
            "fix": self.fix_suggestion or self.fix.generic,
            "fix_suggestion": self.fix_suggestion or self.fix.generic,
            "fix_code": self.fix_code or self.fix.by_platform,
            "fixes_by_platform": self.fix.by_platform or self.fix_code,
            "risk_note": self.fix.risk_note,
            "status": self.status,
            "discovered_at": self.discovered_at,
            "ai_advice": f"**漏洞**：{self.title}\n**影响**：{self.impact or self.description}\n**修复**：{self.fix_suggestion or self.fix.generic}",
        }
        return result


class BaseVulnDetector(ABC):
    """漏洞检测器基类。

    所有检测插件必须继承此类并实现 detect 方法。
    """

    # 检测器名称标识
    name: str = ""
    # 检测器版本
    version: str = "1.0"
    # 支持的扫描深度（quick / standard / deep）
    supported_depths: list[str] = field(default_factory=lambda: ["standard", "deep"])

    @abstractmethod
    async def detect(self, context: ScanContext) -> list[Finding]:
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

    _detectors: builtins.list[BaseVulnDetector] = []
    _enabled: dict[str, bool] = {}  # name -> enabled

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
    def get(cls, name: str) -> BaseVulnDetector | None:
        """按名称获取检测器。"""
        for d in cls._detectors:
            if d.name == name:
                return d
        return None

    @classmethod
    def list(cls) -> builtins.list[BaseVulnDetector]:
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
    async def run_all(cls, context: ScanContext) -> dict[str, builtins.list[Finding]]:
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
        findings_map: dict[str, list[Finding]] = {}
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
