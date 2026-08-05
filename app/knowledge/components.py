"""CVE 组件库。

管理已知漏洞组件（框架、库、服务器）的版本指纹与关联 CVE，
支持版本比对和已知漏洞查询。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CVEEntry:
    """单个 CVE 条目。"""

    cve_id: str
    severity: str  # critical / high / medium / low
    cvss_score: float = 0.0
    description: str = ""
    affected_versions: str = ""  # e.g. "<1.2.3" or ">=1.0,<2.0"
    fixed_version: str = ""  # 修复版本


@dataclass
class KnownComponent:
    """已知漏洞组件。"""

    name: str
    category: str  # framework / library / server / cms / language
    fingerprint_patterns: list[str] = field(
        default_factory=list
    )  # 响应中用于识别的模式
    header_patterns: dict[str, str] = field(default_factory=dict)  # 响应头匹配
    cves: list[CVEEntry] = field(default_factory=list)
    latest_safe_version: str = ""

    def match_response(self, body: str, headers: dict[str, str]) -> bool:
        """检查响应是否匹配该组件指纹。"""
        body_lower = body.lower()
        for pattern in self.fingerprint_patterns:
            if pattern.lower() in body_lower:
                return True
        headers_lower = {k.lower(): v.lower() for k, v in headers.items()}
        for header_name, pattern in self.header_patterns.items():
            actual = headers_lower.get(header_name.lower(), "")
            if pattern.lower() in actual:
                return True
        return False

    def extract_version(self, body: str, headers: dict[str, str]) -> str | None:
        """从响应中提取组件版本号。"""
        headers_lower = {k.lower(): v for k, v in headers.items()}
        # 从 header 提取版本
        for header_name, _ in self.header_patterns.items():
            actual = headers_lower.get(header_name.lower(), "")
            version_match = re.search(r"(\d+\.\d+(?:\.\d+)*)", actual)
            if version_match:
                return version_match.group(1)
        # 从 body 提取版本
        for pattern in self.fingerprint_patterns:
            idx = body.lower().find(pattern.lower())
            if idx >= 0:
                after = body[idx + len(pattern) : idx + len(pattern) + 50]
                version_match = re.search(r"(\d+\.\d+(?:\.\d+)*)", after)
                if version_match:
                    return version_match.group(1)
        return None


class ComponentDatabase:
    """CVE 组件库。

    管理已知漏洞组件的指纹和 CVE 数据，
    支持从 HTTP 响应中识别组件并查询关联漏洞。
    """

    def __init__(self) -> None:
        self._components: dict[str, KnownComponent] = {}
        self._init_builtin()

    def _init_builtin(self) -> None:
        """初始化内置组件库。"""
        # --- Web 服务器 ---
        nginx = KnownComponent(
            name="nginx",
            category="server",
            header_patterns={"server": "nginx"},
            latest_safe_version="1.25.3",
            cves=[
                CVEEntry(
                    "CVE-2021-23017",
                    "high",
                    7.7,
                    "nginx DNS 解析器堆缓冲区溢出",
                    "<1.20.1",
                    "1.20.1",
                ),
                CVEEntry(
                    "CVE-2019-20372",
                    "high",
                    7.5,
                    "HTTP 请求走私导致拒绝服务",
                    "<1.17.7",
                    "1.17.7",
                ),
                CVEEntry(
                    "CVE-2018-16843",
                    "medium",
                    5.3,
                    "HTTP/2 内存泄漏",
                    "<1.15.6",
                    "1.15.6",
                ),
            ],
        )
        self.register(nginx)

        apache = KnownComponent(
            name="apache-httpd",
            category="server",
            header_patterns={"server": "apache"},
            latest_safe_version="2.4.58",
            cves=[
                CVEEntry(
                    "CVE-2021-41773",
                    "high",
                    7.5,
                    "Apache 路径遍历和文件泄露",
                    "<2.4.50",
                    "2.4.50",
                ),
                CVEEntry(
                    "CVE-2021-42013",
                    "high",
                    7.5,
                    "Apache 路径遍历（41773 补丁绕过）",
                    "<2.4.51",
                    "2.4.51",
                ),
                CVEEntry(
                    "CVE-2020-9484",
                    "high",
                    7.5,
                    "Apache 反序列化 RCE",
                    "<2.4.43",
                    "2.4.43",
                ),
            ],
        )
        self.register(apache)

        iis = KnownComponent(
            name="iis",
            category="server",
            header_patterns={"server": "microsoft-iis"},
            latest_safe_version="10.0",
            cves=[
                CVEEntry(
                    "CVE-2015-1635", "high", 7.3, "IIS HTTP 协议栈 RCE", "<6.0", "6.0"
                ),
                CVEEntry(
                    "CVE-2015-8111",
                    "medium",
                    4.3,
                    "IIS FTP 身份验证绕过",
                    "<7.0",
                    "7.0",
                ),
            ],
        )
        self.register(iis)

        # --- 编程语言/运行时 ---
        php = KnownComponent(
            name="php",
            category="language",
            header_patterns={"x-powered-by": "php"},
            latest_safe_version="8.3.0",
            cves=[
                CVEEntry(
                    "CVE-2021-21703",
                    "high",
                    7.8,
                    "PHP-FPM 堆缓冲区溢出",
                    "<8.0.13",
                    "8.0.13",
                ),
                CVEEntry(
                    "CVE-2021-21708",
                    "high",
                    7.8,
                    "PHP LDAP 堆缓冲区溢出",
                    "<8.0.15",
                    "8.0.15",
                ),
                CVEEntry(
                    "CVE-2024-4577",
                    "critical",
                    9.8,
                    "PHP CGI 参数注入 RCE",
                    "<8.3.8",
                    "8.3.8",
                ),
            ],
        )
        self.register(php)

        # --- Web 框架 ---
        django = KnownComponent(
            name="django",
            category="framework",
            fingerprint_patterns=["django", "csrfmiddlewaretoken"],
            header_patterns={"x-frame-options": "deny"},
            latest_safe_version="4.2.8",
            cves=[
                CVEEntry(
                    "CVE-2023-46695",
                    "high",
                    7.5,
                    "Django DoS via IPv6",
                    "<4.2.7",
                    "4.2.7",
                ),
                CVEEntry(
                    "CVE-2023-41164",
                    "medium",
                    5.3,
                    "Django django.utils.encoding.uri_to_iri",
                    "<4.2.5",
                    "4.2.5",
                ),
                CVEEntry(
                    "CVE-2023-36053",
                    "high",
                    7.5,
                    "Django EmailValidator/URLValidator ReDoS",
                    "<4.2.4",
                    "4.2.4",
                ),
            ],
        )
        self.register(django)

        flask = KnownComponent(
            name="flask",
            category="framework",
            fingerprint_patterns=["flask", "werkzeug"],
            header_patterns={"server": "werkzeug"},
            latest_safe_version="3.0.0",
            cves=[
                CVEEntry(
                    "CVE-2023-30861",
                    "medium",
                    5.3,
                    "Flask Cookie 会话固定",
                    "<2.2.5",
                    "2.2.5",
                ),
            ],
        )
        self.register(flask)

        express = KnownComponent(
            name="express",
            category="framework",
            header_patterns={"x-powered-by": "express"},
            latest_safe_version="4.18.2",
            cves=[
                CVEEntry(
                    "CVE-2022-24999",
                    "high",
                    7.5,
                    "Express qs 解析原型污染",
                    "<4.17.3",
                    "4.17.3",
                ),
            ],
        )
        self.register(express)

        spring_boot = KnownComponent(
            name="spring-boot",
            category="framework",
            fingerprint_patterns=["whitelabel error page", "spring"],
            header_patterns={"x-application-context": "application"},
            latest_safe_version="3.2.0",
            cves=[
                CVEEntry(
                    "CVE-2022-22965",
                    "critical",
                    9.8,
                    "Spring4Shell RCE",
                    "<2.6.6",
                    "2.6.6",
                ),
                CVEEntry(
                    "CVE-2022-22963",
                    "critical",
                    9.8,
                    "Spring Cloud Function SpEL RCE",
                    "<3.2.3",
                    "3.2.3",
                ),
                CVEEntry(
                    "CVE-2022-22950",
                    "medium",
                    5.4,
                    "Spring Framework SpEL DoS",
                    "<5.3.18",
                    "5.3.18",
                ),
            ],
        )
        self.register(spring_boot)

        # --- CMS ---
        wordpress = KnownComponent(
            name="wordpress",
            category="cms",
            fingerprint_patterns=["wp-content", "wp-includes", "wp-json"],
            header_patterns={"link": "wp-json"},
            latest_safe_version="6.4.2",
            cves=[
                CVEEntry(
                    "CVE-2023-2745",
                    "high",
                    7.5,
                    "WordPress 目录遍历",
                    "<6.2.1",
                    "6.2.1",
                ),
                CVEEntry(
                    "CVE-2022-21661",
                    "high",
                    7.5,
                    "WP_Query SQL 注入",
                    "<5.8.3",
                    "5.8.3",
                ),
                CVEEntry(
                    "CVE-2021-39200",
                    "medium",
                    5.3,
                    "WordPress SSRF via REST API",
                    "<5.8",
                    "5.8",
                ),
            ],
        )
        self.register(wordpress)

        joomla = KnownComponent(
            name="joomla",
            category="cms",
            fingerprint_patterns=["joomla", "com_content"],
            latest_safe_version="4.4.1",
            cves=[
                CVEEntry(
                    "CVE-2023-23752",
                    "high",
                    7.5,
                    "Joomla 未授权信息泄露",
                    "<4.2.7",
                    "4.2.7",
                ),
                CVEEntry(
                    "CVE-2023-22602", "high", 7.5, "Joomla SQL 注入", "<4.2.6", "4.2.6"
                ),
            ],
        )
        self.register(joomla)

        # --- JavaScript 库 ---
        jquery = KnownComponent(
            name="jquery",
            category="library",
            fingerprint_patterns=["jquery"],
            latest_safe_version="3.7.1",
            cves=[
                CVEEntry(
                    "CVE-2020-11023",
                    "medium",
                    5.3,
                    "jQuery XSS via htmlPrefilter",
                    "<3.5.0",
                    "3.5.0",
                ),
                CVEEntry(
                    "CVE-2015-9251",
                    "medium",
                    5.3,
                    "jQuery XSS via cross-domain ajax",
                    "<3.0.0",
                    "3.0.0",
                ),
            ],
        )
        self.register(jquery)

        # --- 反向代理/CDN ---
        cloudflare = KnownComponent(
            name="cloudflare",
            category="server",
            header_patterns={"server": "cloudflare", "cf-ray": "cf-ray"},
            latest_safe_version="",
            cves=[],
        )
        self.register(cloudflare)

    def register(self, component: KnownComponent) -> None:
        """注册一个组件。"""
        self._components[component.name] = component

    def identify(
        self, body: str, headers: dict[str, str]
    ) -> list[tuple[KnownComponent, str | None]]:
        """从 HTTP 响应中识别组件。

        Returns:
            匹配的组件列表，每项包含组件和提取到的版本（可能为 None）
        """
        matched: list[tuple[KnownComponent, str | None]] = []
        for comp in self._components.values():
            if comp.match_response(body, headers):
                version = comp.extract_version(body, headers)
                matched.append((comp, version))
        return matched

    def get_cves(
        self, component_name: str, version: str | None = None
    ) -> list[CVEEntry]:
        """查询组件的 CVE 列表。

        如果提供了版本号，则仅返回该版本受影响的 CVE。
        """
        comp = self._components.get(component_name)
        if not comp:
            return []
        if version is None:
            return list(comp.cves)
        # 简化版本比较：检查 affected_versions 中的约束
        result: list[CVEEntry] = []
        for cve in comp.cves:
            if self._is_affected(version, cve.affected_versions):
                result.append(cve)
        return result

    def _is_affected(self, version: str, constraint: str) -> bool:
        """简化的版本受影响判断。"""
        if not constraint:
            return True
        # 解析约束：支持 "<1.2.3", ">=1.0,<2.0" 等格式
        parts = constraint.split(",")
        for part in parts:
            part = part.strip()
            if part.startswith("<"):
                target = part[1:].strip()
                if not target.startswith("="):
                    if self._compare_versions(version, target) >= 0:
                        return False
                else:
                    if self._compare_versions(version, target[1:].strip()) > 0:
                        return False
            elif part.startswith(">="):
                target = part[2:].strip()
                if self._compare_versions(version, target) < 0:
                    return False
            elif part.startswith(">"):
                target = part[1:].strip()
                if not target.startswith("="):
                    if self._compare_versions(version, target) <= 0:
                        return False
                else:
                    if self._compare_versions(version, target[1:].strip()) < 0:
                        return False
        return True

    def _compare_versions(self, v1: str, v2: str) -> int:
        """比较两个版本号。返回 -1, 0, 1。"""
        parts1 = [int(x) for x in re.findall(r"\d+", v1)]
        parts2 = [int(x) for x in re.findall(r"\d+", v2)]
        max_len = max(len(parts1), len(parts2))
        parts1 += [0] * (max_len - len(parts1))
        parts2 += [0] * (max_len - len(parts2))
        for a, b in zip(parts1, parts2):
            if a < b:
                return -1
            if a > b:
                return 1
        return 0

    def list_components(self) -> list[str]:
        """列出所有已注册的组件名称。"""
        return sorted(self._components.keys())

    def get_component(self, name: str) -> KnownComponent | None:
        """获取指定组件。"""
        return self._components.get(name)

    def stats(self) -> dict[str, Any]:
        """返回组件库统计信息。"""
        return {
            "total_components": len(self._components),
            "total_cves": sum(len(c.cves) for c in self._components.values()),
            "by_category": {
                cat: sum(1 for c in self._components.values() if c.category == cat)
                for cat in set(c.category for c in self._components.values())
            },
        }
