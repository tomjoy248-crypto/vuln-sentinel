"""YAML 自定义规则引擎。

支持从 YAML 文件加载自定义检测规则，并将其作为插件注册到 DetectorRegistry。
企业用户可以编写 YAML 规则文件来扩展检测能力，无需修改代码。

YAML 规则格式示例:
    rules:
      - id: custom-xss-param
        name: 自定义 XSS 参数检测
        severity: high
        type: xss
        cwe_id: CWE-79
        owasp_category: A03 注入攻击
        description: 检测可能存在 XSS 的参数
        match:
          param_names: ["search", "q", "query", "keyword"]
          response_patterns:
            - "<script"
            - "onerror="
          response_status: [200]
        fix_suggestion: 对用户输入进行 HTML 编码
        confidence: high
        supported_depths: [standard, deep]
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from app.plugins import BaseVulnDetector, Finding, ScanContext

logger = logging.getLogger("vuln_sentinel.rule_engine")


@dataclass
class MatchConfig:
    """规则匹配配置。"""
    param_names: List[str] = field(default_factory=list)
    param_patterns: List[str] = field(default_factory=list)
    response_patterns: List[str] = field(default_factory=list)
    response_status: List[int] = field(default_factory=list)
    header_patterns: Dict[str, str] = field(default_factory=dict)
    body_regex: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "MatchConfig":
        return cls(
            param_names=data.get("param_names", []),
            param_patterns=data.get("param_patterns", []),
            response_patterns=data.get("response_patterns", []),
            response_status=data.get("response_status", []),
            header_patterns=data.get("header_patterns", {}),
            body_regex=data.get("body_regex", []),
        )


@dataclass
class CustomRule:
    """自定义检测规则。"""
    id: str
    name: str
    severity: str
    type: str
    cwe_id: str = ""
    owasp_category: str = ""
    description: str = ""
    fix_suggestion: str = ""
    confidence: str = "medium"
    supported_depths: List[str] = field(default_factory=lambda: ["standard", "deep"])
    match: MatchConfig = field(default_factory=MatchConfig)
    payload: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "CustomRule":
        match_data = data.get("match", {})
        return cls(
            id=data.get("id", "unknown"),
            name=data.get("name", "自定义规则"),
            severity=data.get("severity", "medium"),
            type=data.get("type", "custom"),
            cwe_id=data.get("cwe_id", ""),
            owasp_category=data.get("owasp_category", ""),
            description=data.get("description", ""),
            fix_suggestion=data.get("fix_suggestion", ""),
            confidence=data.get("confidence", "medium"),
            supported_depths=data.get("supported_depths", ["standard", "deep"]),
            match=MatchConfig.from_dict(match_data),
            payload=data.get("payload", ""),
        )


def load_rules_from_yaml(file_path: str) -> List[CustomRule]:
    """从 YAML 文件加载规则列表。

    Args:
        file_path: YAML 文件路径

    Returns:
        解析后的 CustomRule 列表
    """
    try:
        import yaml
    except ImportError:
        logger.warning("PyYAML not installed, custom rule loading disabled")
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not data or not isinstance(data, dict):
            return []
        rules_data = data.get("rules", [])
        return [CustomRule.from_dict(r) for r in rules_data if isinstance(r, dict)]
    except Exception as e:
        logger.error("Failed to load rules from %s: %s", file_path, e)
        return []


def load_rules_from_directory(dir_path: str) -> List[CustomRule]:
    """从目录加载所有 YAML 规则文件。

    Args:
        dir_path: 规则目录路径

    Returns:
        合并后的 CustomRule 列表
    """
    all_rules: List[CustomRule] = []
    if not os.path.isdir(dir_path):
        return all_rules

    for filename in sorted(os.listdir(dir_path)):
        if not filename.endswith((".yaml", ".yml")):
            continue
        file_path = os.path.join(dir_path, filename)
        rules = load_rules_from_yaml(file_path)
        all_rules.extend(rules)
        if rules:
            logger.info("Loaded %d rules from %s", len(rules), filename)

    return all_rules


class YAMLRuleDetector(BaseVulnDetector):
    """基于 YAML 自定义规则的检测器。

    将一组 CustomRule 包装为单个检测器插件。
    每条规则独立匹配，命中即生成 Finding。
    """

    name = "yaml_custom_rules"
    version = "1.0"
    supported_depths = ["quick", "standard", "deep"]

    def __init__(self, rules: List[CustomRule]):
        self._rules = rules
        # 动态设置 supported_depths
        depths = set()
        for r in rules:
            depths.update(r.supported_depths)
        if depths:
            self.supported_depths = list(depths)

    async def detect(self, context: ScanContext) -> List[Finding]:
        findings: List[Finding] = []
        parsed = urlparse(context.url)
        params = [p.split("=")[0] for p in parsed.query.split("&") if "=" in p] if parsed.query else []

        for rule in self._rules:
            if context.depth not in rule.supported_depths:
                continue
            try:
                finding = await self._match_rule(rule, context, params)
                if finding:
                    findings.append(finding)
            except Exception as e:
                logger.warning("Rule %s execution failed: %s", rule.id, e)

        return findings

    async def _match_rule(self, rule: CustomRule, context: ScanContext, params: List[str]) -> Optional[Finding]:
        """匹配单条规则。"""
        match = rule.match

        # 1. 参数名匹配
        if match.param_names or match.param_patterns:
            param_matched = False
            for param in params:
                if param.lower() in [n.lower() for n in match.param_names]:
                    param_matched = True
                    break
                for pattern in match.param_patterns:
                    if re.search(pattern, param, re.IGNORECASE):
                        param_matched = True
                        break
            if not param_matched:
                return None

        # 2. 响应头匹配
        if match.header_patterns:
            header_matched = False
            for header_name, pattern in match.header_patterns.items():
                header_value = context.headers.get(header_name, context.headers.get(header_name.title(), ""))
                if header_value and re.search(pattern, header_value, re.IGNORECASE):
                    header_matched = True
                    break
            if not header_matched:
                return None

        # 3. 如果需要检查响应体或状态码，需要发起 HTTP 请求
        if match.response_patterns or match.response_status or match.body_regex:
            finding = await self._check_response(rule, context, match)
            return finding

        # 4. 如果只有参数名/头部匹配，直接报告
        return self._build_finding(rule, context, params)

    async def _check_response(
        self, rule: CustomRule, context: ScanContext, match: MatchConfig
    ) -> Optional[Finding]:
        """检查响应内容和状态码。"""
        try:
            from main import get_httpx_client
            client = get_httpx_client()
            resp = await client.get(context.url, timeout=10.0, follow_redirects=True)

            # 状态码匹配
            if match.response_status and resp.status_code not in match.response_status:
                return None

            body = resp.text.lower()

            # 响应模式匹配
            for pattern in match.response_patterns:
                if pattern.lower() in body:
                    return self._build_finding(rule, context, evidence={
                        "matched_pattern": pattern,
                        "status_code": resp.status_code,
                        "url": context.url,
                    })

            # 正则匹配
            for regex in match.body_regex:
                if re.search(regex, body, re.IGNORECASE):
                    return self._build_finding(rule, context, evidence={
                        "matched_regex": regex,
                        "status_code": resp.status_code,
                        "url": context.url,
                    })

        except Exception as e:
            logger.debug("Rule %s response check failed: %s", rule.id, e)

        return None

    def _build_finding(
        self, rule: CustomRule, context: ScanContext, evidence: Optional[dict] = None
    ) -> Finding:
        """构建 Finding 对象。"""
        return Finding(
            title=rule.name,
            type=rule.type,
            severity=rule.severity,
            description=rule.description or f"自定义规则 {rule.id} 命中",
            url=context.url,
            evidence=evidence or {"rule_id": rule.id},
            fix_suggestion=rule.fix_suggestion or "请根据业务场景手动修复",
            confidence=rule.confidence,
            owasp_category=rule.owasp_category,
            cwe_id=rule.cwe_id,
        )


def register_yaml_rules(rules_dir: str = "rules/") -> int:
    """加载并注册 YAML 自定义规则。

    Args:
        rules_dir: 规则文件目录

    Returns:
        注册的规则数量
    """
    from app.plugins import DetectorRegistry

    rules = load_rules_from_directory(rules_dir)
    if not rules:
        logger.info("No custom YAML rules found in %s", rules_dir)
        return 0

    detector = YAMLRuleDetector(rules)
    DetectorRegistry.register(detector)
    logger.info("Registered %d custom YAML rules as detector '%s'", len(rules), detector.name)
    return len(rules)
