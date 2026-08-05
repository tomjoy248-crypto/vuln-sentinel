"""签名库。

管理漏洞检测中用于匹配响应内容的签名规则，
包括数据库错误特征、命令输出特征、框架指纹等。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from re import Pattern


@dataclass
class Signature:
    """检测签名。"""

    name: str
    vuln_type: str
    pattern: str
    pattern_type: str = "substring"  # substring / regex
    description: str = ""
    compiled: Pattern[str] | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if self.pattern_type == "regex" and self.pattern:
            self.compiled = re.compile(self.pattern, re.IGNORECASE)

    def match(self, text: str) -> bool:
        """检查文本是否匹配签名。"""
        if not text:
            return False
        if self.pattern_type == "regex" and self.compiled:
            return bool(self.compiled.search(text))
        return self.pattern.lower() in text.lower()


class SignatureLibrary:
    """签名库。

    按漏洞类型组织检测签名，支持快速匹配响应内容。
    """

    def __init__(self) -> None:
        self._signatures: dict[str, list[Signature]] = {}
        self._init_builtin()

    def _init_builtin(self) -> None:
        """初始化内置签名集。"""
        # --- SQL Injection Error Signatures ---
        sqli_sigs = [
            Signature(
                "mysql_syntax_error",
                "sqli",
                "sql syntax",
                "substring",
                "MySQL 语法错误",
            ),
            Signature(
                "mysql_fetch",
                "sqli",
                "mysql_fetch",
                "substring",
                "MySQL fetch 函数错误",
            ),
            Signature(
                "mysql_warning",
                "sqli",
                "mysql_query",
                "substring",
                "MySQL 查询函数错误",
            ),
            Signature(
                "postgresql_error",
                "sqli",
                "pg_query",
                "substring",
                "PostgreSQL 查询错误",
            ),
            Signature(
                "postgresql_syntax",
                "sqli",
                "psql error",
                "substring",
                "PostgreSQL 语法错误",
            ),
            Signature("oracle_error", "sqli", "ora-", "substring", "Oracle 数据库错误"),
            Signature(
                "sqlite_error", "sqli", "sqlite_warning", "substring", "SQLite 错误"
            ),
            Signature(
                "sqlite_query",
                "sqli",
                "sqlite3.operationalerror",
                "substring",
                "SQLite 操作错误",
            ),
            Signature(
                "mssql_error", "sqli", "microsoft sql server", "substring", "MSSQL 错误"
            ),
            Signature(
                "unclosed_quotation",
                "sqli",
                "unclosed quotation",
                "substring",
                "未闭合引号",
            ),
            Signature(
                "odbc_error", "sqli", "odbc sql server driver", "substring", "ODBC 错误"
            ),
            Signature("db2_error", "sqli", "db2 sql error", "substring", "DB2 错误"),
            Signature(
                "syntax_error_generic",
                "sqli",
                r"you have an error in your sql syntax",
                "regex",
                "通用 SQL 语法错误",
            ),
            Signature(
                "column_mismatch",
                "sqli",
                r"column (?:count|number) doesn't match",
                "regex",
                "列数不匹配",
            ),
        ]
        for s in sqli_sigs:
            self.register(s)

        # --- Command Injection Output Signatures ---
        cmdi_sigs = [
            Signature("linux_uid", "cmdi", "uid=", "substring", "Linux id 命令输出"),
            Signature("linux_gid", "cmdi", "gid=", "substring", "Linux gid 输出"),
            Signature(
                "linux_groups", "cmdi", "groups=", "substring", "Linux groups 输出"
            ),
            Signature(
                "linux_passwd_root", "cmdi", "root:", "substring", "passwd 文件 root 行"
            ),
            Signature(
                "linux_passwd_daemon",
                "cmdi",
                "daemon:",
                "substring",
                "passwd 文件 daemon 行",
            ),
            Signature(
                "www_data_user", "cmdi", "www-data", "substring", "www-data 用户"
            ),
            Signature(
                "windows_admin",
                "cmdi",
                "administrator",
                "substring",
                "Windows administrator",
            ),
            Signature(
                "nt_authority",
                "cmdi",
                "nt authority",
                "substring",
                "Windows NT AUTHORITY",
            ),
            Signature(
                "windows_dir_output",
                "cmdi",
                r"<DIR>\s+",
                "regex",
                "Windows dir 命令输出",
            ),
            Signature(
                "linux_hostname_pattern",
                "cmdi",
                r"[a-z_][a-z0-9_-]*\n",
                "regex",
                "whoami 输出格式",
            ),
        ]
        for s in cmdi_sigs:
            self.register(s)

        # --- Path Traversal File Content Signatures ---
        traversal_sigs = [
            Signature(
                "passwd_root", "traversal", "root:", "substring", "/etc/passwd root 行"
            ),
            Signature(
                "passwd_daemon",
                "traversal",
                "daemon:",
                "substring",
                "/etc/passwd daemon 行",
            ),
            Signature(
                "passwd_bin", "traversal", "/bin/bash", "substring", "passwd shell 路径"
            ),
            Signature(
                "passwd_bin_sh", "traversal", "/bin/sh", "substring", "passwd sh 路径"
            ),
            Signature(
                "win_ini_fonts", "traversal", "[fonts]", "substring", "win.ini fonts 段"
            ),
            Signature(
                "win_ini_extensions",
                "traversal",
                "[extensions]",
                "substring",
                "win.ini extensions 段",
            ),
            Signature(
                "win_ini_mci",
                "traversal",
                "[mci extensions]",
                "substring",
                "win.ini MCI 段",
            ),
            Signature(
                "win_ini_files", "traversal", "[files]", "substring", "win.ini files 段"
            ),
        ]
        for s in traversal_sigs:
            self.register(s)

        # --- XSS Reflection Signatures ---
        xss_sigs = [
            Signature("script_tag", "xss", "<script", "substring", "script 标签反射"),
            Signature("onerror_event", "xss", "onerror=", "substring", "onerror 事件"),
            Signature("onload_event", "xss", "onload=", "substring", "onload 事件"),
            Signature("svg_tag", "xss", "<svg", "substring", "SVG 标签"),
            Signature("img_tag", "xss", "<img", "substring", "IMG 标签"),
            Signature("iframe_tag", "xss", "<iframe", "substring", "IFRAME 标签"),
            Signature(
                "javascript_protocol",
                "xss",
                "javascript:",
                "substring",
                "javascript 协议",
            ),
            Signature("alert_function", "xss", "alert(", "substring", "alert 函数"),
            Signature(
                "document_cookie", "xss", "document.cookie", "substring", "Cookie 窃取"
            ),
        ]
        for s in xss_sigs:
            self.register(s)

        # --- XXE Indicators ---
        xxe_sigs = [
            Signature(
                "passwd_content", "xxe", "root:", "substring", "读取到 /etc/passwd"
            ),
            Signature("bin_path", "xxe", "/bin/", "substring", "passwd 文件 bin 路径"),
            Signature(
                "xml_error_entity", "xxe", "entity", "substring", "XML 实体相关错误"
            ),
            Signature("xml_error_dtd", "xxe", "dtd", "substring", "DTD 相关错误"),
        ]
        for s in xxe_sigs:
            self.register(s)

        # --- Info Leak Signatures ---
        info_sigs = [
            Signature(
                "php_info", "info_leak", "phpinfo()", "substring", "PHP info 页面"
            ),
            Signature(
                "php_version_header",
                "info_leak",
                "x-powered-by: php",
                "substring",
                "PHP 版本头",
            ),
            Signature(
                "aspnet_header",
                "info_leak",
                "x-aspnet-version",
                "substring",
                "ASP.NET 版本头",
            ),
            Signature(
                "server_header_nginx",
                "info_leak",
                "server: nginx",
                "substring",
                "Nginx 版本头",
            ),
            Signature(
                "server_header_apache",
                "info_leak",
                "server: apache",
                "substring",
                "Apache 版本头",
            ),
            Signature(
                "stack_trace",
                "info_leak",
                r"traceback \(most recent call last\)",
                "regex",
                "Python 堆栈跟踪",
            ),
            Signature(
                "java_stack_trace",
                "info_leak",
                "at java.",
                "substring",
                "Java 堆栈跟踪",
            ),
            Signature(
                "debug_info", "info_leak", "debug=true", "substring", "调试信息暴露"
            ),
        ]
        for s in info_sigs:
            self.register(s)

        # --- WAF / Protection Signatures ---
        waf_sigs = [
            Signature("cloudflare", "waf", "cloudflare", "substring", "Cloudflare WAF"),
            Signature("incapsula", "waf", "incapsula", "substring", "Incapsula WAF"),
            Signature("sucuri", "waf", "sucuri", "substring", "Sucuri WAF"),
            Signature("akamai", "waf", "akamai", "substring", "Akamai WAF"),
            Signature("f5_bigip", "waf", "bigipserver", "substring", "F5 BIG-IP"),
            Signature(
                "mod_security", "waf", "mod_security", "substring", "ModSecurity WAF"
            ),
            Signature(
                "blocked_message", "waf", "access denied", "substring", "访问被拒绝"
            ),
            Signature(
                "rate_limit", "waf", "too many requests", "substring", "频率限制"
            ),
        ]
        for s in waf_sigs:
            self.register(s)

    def register(self, sig: Signature) -> None:
        """注册一个签名。"""
        self._signatures.setdefault(sig.vuln_type, []).append(sig)

    def match_any(self, vuln_type: str, text: str) -> list[Signature]:
        """检查文本是否匹配指定漏洞类型的任何签名。"""
        matched = []
        for sig in self._signatures.get(vuln_type, []):
            if sig.match(text):
                matched.append(sig)
        return matched

    def has_match(self, vuln_type: str, text: str) -> bool:
        """快速检查是否有匹配。"""
        return len(self.match_any(vuln_type, text)) > 0

    def get_signatures(self, vuln_type: str) -> list[Signature]:
        """获取指定漏洞类型的所有签名。"""
        return list(self._signatures.get(vuln_type, []))

    def list_types(self) -> list[str]:
        """列出所有已注册的漏洞类型。"""
        return sorted(self._signatures.keys())

    def stats(self) -> dict[str, int]:
        """返回各漏洞类型的签名数量统计。"""
        return {vt: len(sigs) for vt, sigs in self._signatures.items()}
