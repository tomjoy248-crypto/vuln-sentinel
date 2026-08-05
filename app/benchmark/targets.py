"""已知漏洞靶场基准目标定义。

本模块定义了一组公开的安全测试靶场目标（ground truth），用于评估扫描引擎
的检出能力。每个目标标注了：

- **预期漏洞 (ExpectedVulnerability)**：靶场上已知存在的漏洞，扫描器理应检出。
- **负向检查 (NegativeCheck)**：靶场上明确不存在的漏洞类型，扫描器不应误报。

所用靶场均来自公开的安全测试站点：

- ``http://testphp.vulnweb.com/`` —— Acunetix 官方测试站点，包含多种已知漏洞。
- ``https://example.com/`` —— IANA 维护的示例域名，作为无注入类漏洞的基线站点。
- ``https://httpbin.org/`` —— 公开 HTTP 测试服务，用于安全头与 CORS 检测验证。

匹配规则（``ExpectedVulnerability.matches`` / ``NegativeCheck.matches``）：

1. 漏洞类型 (``type``) 大小写不敏感相等。
2. 若设置了 ``parameter``，则 finding 的 ``parameter`` 字段须相等（用于注入类漏洞）。
3. 若设置了 ``title_keywords``，则 finding 的 ``title`` 须包含任一关键词
   （用于 ``header_missing`` 等按标题区分的漏洞，如 HSTS / CSP）。

注意：真实站点的安全配置可能随时间变化，基准结果应结合时间戳解读。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

# 严重级别类型：与扫描引擎保持一致
Severity = Literal["critical", "high", "medium", "low", "info"]

# 靶场分类
TargetCategory = Literal["vuln_lab", "baseline", "test_service"]


@dataclass
class ExpectedVulnerability:
    """单个预期漏洞的定义（正例）。

    扫描器理应在对应靶场上检出此漏洞。

    Attributes:
        vuln_type: 漏洞类型，与扫描引擎 finding 的 ``type`` 字段一致
            （如 ``sqli``、``xss``、``header_missing``、``cors_misconfig``）。
        severity: 预期严重级别。
        description: 漏洞描述（用于报告展示）。
        parameter: 注入参数名（可选）。设置后仅匹配 ``parameter`` 相同的 finding，
            用于精确定位 SQL 注入、XSS 等参数级漏洞。
        title_keywords: 标题关键词列表（可选）。设置后 finding 的 ``title`` 须包含
            至少一个关键词，用于区分 ``header_missing`` 下的具体安全头
            （如 ``["hsts"]`` 匹配 "缺少 HSTS 响应头"）。
    """

    vuln_type: str
    severity: Severity
    description: str
    parameter: str = ""
    title_keywords: list[str] = field(default_factory=list)

    def matches(self, finding: dict[str, Any]) -> bool:
        """判断一条 finding 是否与本预期漏洞匹配。

        Args:
            finding: 扫描引擎产出的 finding 字典，须含 ``type`` 字段，
                可选 ``title`` 与 ``parameter`` 字段。

        Returns:
            是否匹配。
        """
        f_type = str(finding.get("type", "")).lower()
        if f_type != self.vuln_type.lower():
            return False

        # 参数级匹配（注入类漏洞）
        if self.parameter:
            f_param = str(finding.get("parameter", "")).lower()
            if f_param != self.parameter.lower():
                return False

        # 标题关键词匹配（header_missing 等按标题区分的漏洞）
        if self.title_keywords:
            title = str(finding.get("title", "")).lower()
            if not any(kw.lower() in title for kw in self.title_keywords):
                return False

        return True


@dataclass
class NegativeCheck:
    """负向检查点（负例）。

    表示靶场上明确不存在的漏洞类型，扫描器不应报告。若扫描器报告了匹配的
    finding，则计为误报 (FP)；若未报告，则计为真反例 (TN)。

    Attributes:
        vuln_type: 不应出现的漏洞类型。
        description: 检查点描述。
        title_keywords: 标题关键词列表（可选），用于更精细的匹配。
    """

    vuln_type: str
    description: str = ""
    title_keywords: list[str] = field(default_factory=list)

    def matches(self, finding: dict[str, Any]) -> bool:
        """判断一条 finding 是否命中本负向检查点。"""
        f_type = str(finding.get("type", "")).lower()
        if f_type != self.vuln_type.lower():
            return False
        if self.title_keywords:
            title = str(finding.get("title", "")).lower()
            if not any(kw.lower() in title for kw in self.title_keywords):
                return False
        return True


@dataclass
class BenchmarkTarget:
    """基准靶场目标。

    Attributes:
        id: 目标唯一标识（用于报告与日志）。
        url: 目标 URL。
        name: 目标名称（人类可读）。
        description: 目标描述。
        category: 靶场分类：``vuln_lab``（漏洞靶场）/ ``baseline``（基线）
            / ``test_service``（测试服务）。
        expected_vulns: 预期漏洞列表（正例）。
        negative_checks: 负向检查点列表（负例，用于 TN/FP 评估）。
        is_baseline: 是否为无注入类漏洞的基线站点。
        ignore_types: 范围外漏洞类型列表。匹配这些类型的 finding 在对比时
            被排除（既不计 TP 也不计 FP），用于在专项靶场（如注入端点）上
            聚焦评估特定漏洞类型，避免页面本身存在的安全头缺失等问题干扰
            注入检测的指标计算。
    """

    id: str
    url: str
    name: str
    description: str
    category: TargetCategory
    expected_vulns: list[ExpectedVulnerability] = field(default_factory=list)
    negative_checks: list[NegativeCheck] = field(default_factory=list)
    is_baseline: bool = False
    ignore_types: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# 辅助构造函数：减少重复定义
# ---------------------------------------------------------------------------

# 扫描引擎检测的标准安全头及其标题关键词
_HEADER_SPECS: list[tuple[str, list[str], Severity]] = [
    ("header_missing", ["hsts", "strict-transport-security"], "medium"),
    ("header_missing", ["csp", "content-security-policy"], "medium"),
    ("header_missing", ["x-frame-options"], "medium"),
    ("header_missing", ["x-content-type-options"], "low"),
    ("header_missing", ["referrer-policy"], "low"),
    ("header_missing", ["permissions-policy"], "low"),
]


def _header_expectations() -> list[ExpectedVulnerability]:
    """构造标准安全头缺失的预期漏洞列表。"""
    return [
        ExpectedVulnerability(
            vuln_type=vuln_type,
            severity=severity,
            description="目标未配置对应安全响应头，应被检出为缺失。",
            title_keywords=keywords,
        )
        for vuln_type, keywords, severity in _HEADER_SPECS
    ]


def _injection_negatives() -> list[NegativeCheck]:
    """构造注入类漏洞的负向检查点（不应被误报）。"""
    return [
        NegativeCheck(vuln_type="sqli", description="靶场不应存在 SQL 注入"),
        NegativeCheck(vuln_type="xss", description="靶场不应存在 XSS"),
    ]


# ---------------------------------------------------------------------------
# 基准靶场目标定义
# ---------------------------------------------------------------------------

BENCHMARK_TARGETS: list[BenchmarkTarget] = [
    BenchmarkTarget(
        id="vulnweb_home",
        url="http://testphp.vulnweb.com/",
        name="Acunetix 测试站点（首页）",
        description=(
            "Acunetix 官方公开测试站点，包含多种已知漏洞。首页本身为 HTTP 明文站点，"
            "缺少安全响应头；站点存在 SQL 注入（ListProducts.php?cat=1）与 XSS"
            "（showthread.php?id=1），但首页 URL 无注入参数。"
        ),
        category="vuln_lab",
        expected_vulns=[
            *_header_expectations(),
            # HTTP 明文站点：扫描器应额外报告"未启用 HTTPS"。
            # 注意：插件化扫描引擎将该发现归为 ssl 类型。
            ExpectedVulnerability(
                vuln_type="ssl",
                severity="critical",
                description="目标使用 HTTP 明文传输，扫描器应报告未启用 HTTPS。",
                title_keywords=["未启用 https", "未启用https", "未启用 https"],
            ),
            # 故意脆弱的测试站点，通常泄露服务器/应用信息
            ExpectedVulnerability(
                vuln_type="info_leak",
                severity="medium",
                description="测试站点响应中可能包含服务器版本、内部路径等敏感信息。",
            ),
        ],
        negative_checks=_injection_negatives(),
        is_baseline=False,
    ),
    BenchmarkTarget(
        id="example_com",
        url="https://example.com/",
        name="example.com 基线站点",
        description=(
            "IANA 维护的示例域名，作为无注入类漏洞的基线站点。该站点未配置多数"
            "安全响应头（HSTS/CSP/X-Frame-Options 等），但不存在 SQL 注入或 XSS。"
        ),
        category="baseline",
        expected_vulns=_header_expectations(),
        negative_checks=_injection_negatives(),
        is_baseline=True,
    ),
    BenchmarkTarget(
        id="httpbin_org",
        url="https://httpbin.org/",
        name="httpbin.org HTTP 测试服务",
        description=(
            "公开 HTTP 测试服务。该站点缺少部分安全响应头，且其响应中通常携带"
            "Access-Control-Allow-Origin: * 的宽松 CORS 配置。"
        ),
        category="test_service",
        expected_vulns=[
            *_header_expectations(),
            ExpectedVulnerability(
                vuln_type="cors_misconfig",
                severity="low",
                description="httpbin.org 通常返回 Access-Control-Allow-Origin: *，"
                "允许任意来源跨域访问。",
            ),
        ],
        negative_checks=_injection_negatives(),
        is_baseline=True,
    ),
    BenchmarkTarget(
        id="vulnweb_sqli",
        url="http://testphp.vulnweb.com/listproducts.php?cat=1",
        name="Acunetix 已知 SQL 注入端点",
        description=(
            "Acunetix 测试站点上已知的 SQL 注入端点。参数 ``cat`` 存在基于错误的"
            "SQL 注入漏洞，扫描器应能检出。"
        ),
        category="vuln_lab",
        expected_vulns=[
            ExpectedVulnerability(
                vuln_type="sqli",
                severity="critical",
                description="参数 cat 存在 SQL 注入漏洞（基于错误回显）。",
                parameter="cat",
            ),
        ],
        negative_checks=[],
        is_baseline=False,
        # 该端点页面同为 HTTP 且缺少安全头，这些发现属真实但非本次评估范围，
        # 排除以聚焦 SQL 注入检出能力。
        ignore_types=["header_missing", "ssl", "info_leak"],
    ),
    BenchmarkTarget(
        id="vulnweb_xss",
        url="http://testphp.vulnweb.com/showthread.php?id=1",
        name="Acunetix 已知 XSS 端点",
        description=(
            "Acunetix 测试站点上已知的 XSS 端点。参数 ``id`` 存在反射型 XSS 漏洞，"
            "扫描器应能检出。"
        ),
        category="vuln_lab",
        expected_vulns=[
            ExpectedVulnerability(
                vuln_type="xss",
                severity="high",
                description="参数 id 存在反射型 XSS 漏洞。",
                parameter="id",
            ),
        ],
        negative_checks=[],
        is_baseline=False,
        # 该端点页面同为 HTTP 且缺少安全头，排除以聚焦 XSS 检出能力。
        ignore_types=["header_missing", "ssl", "info_leak"],
    ),
]


def get_target_by_id(target_id: str) -> BenchmarkTarget | None:
    """根据 ID 获取基准靶场目标。

    Args:
        target_id: 目标 ID。

    Returns:
        对应的 ``BenchmarkTarget``，若不存在返回 ``None``。
    """
    for target in BENCHMARK_TARGETS:
        if target.id == target_id:
            return target
    return None
