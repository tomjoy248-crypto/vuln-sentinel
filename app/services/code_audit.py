"""轻量级多语言源码审计器：输出可定位、可解释、可复核的结果。"""

from __future__ import annotations

import re
from dataclasses import dataclass

MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_FILES = 200

_RULES = [
    ("python", re.compile(r"\b(eval|exec)\s*\(|subprocess\.(run|Popen|call)\s*\("), "命令执行或动态代码执行", "high", "使用参数化 API，禁止将用户输入传入 eval、exec 或 shell 命令。"),
    ("python", re.compile(r"execute\s*\(\s*f[\"']|format\s*\([^)]*\).*execute"), "SQL 语句可能由字符串拼接生成", "high", "使用参数化查询，不要拼接 SQL 字符串。"),
    ("javascript", re.compile(r"\b(innerHTML|outerHTML|document\.write)\s*="), "危险 DOM 写入", "medium", "使用 textContent 或安全模板，并对用户输入进行上下文编码。"),
    ("javascript", re.compile(r"\beval\s*\(|new\s+Function\s*\("), "动态代码执行", "high", "移除动态执行，改用白名单映射和安全解析。"),
    ("java", re.compile(r"Runtime\.getRuntime\(\)\.exec|new\s+ProcessBuilder\s*\("), "系统命令执行", "high", "使用固定命令白名单，参数与命令分离并避免 shell 解释。"),
    ("java", re.compile(r"Statement\s+\w+\s*=|createStatement\s*\(\)"), "可能使用未参数化 SQL", "medium", "改用 PreparedStatement 并绑定参数。"),
    ("php", re.compile(r"\b(eval|system|shell_exec|passthru|exec)\s*\("), "危险 PHP 执行函数", "high", "移除动态执行，使用白名单业务操作。"),
    ("php", re.compile(r"mysql_query\s*\(|\$wpdb->query\s*\("), "数据库查询需要检查参数化", "medium", "使用 PDO 预处理或框架参数绑定。"),
]

def _language(name: str) -> str | None:
    suffix = name.lower().rsplit(".", 1)[-1] if "." in name else ""
    return {"py": "python", "js": "javascript", "jsx": "javascript", "ts": "javascript", "tsx": "javascript", "java": "java", "php": "php"}.get(suffix)

def audit_source(name: str, content: bytes, audit_id: str) -> list[dict]:
    """扫描单个源码文件，保留有限上下文，避免把整份源码写入结果。"""
    if len(content) > MAX_FILE_BYTES:
        return [{"audit_id": audit_id, "file": name, "line": 1, "snippet": "", "rule": "file_size", "title": "文件超过审计大小限制", "severity": "info", "confidence": "high", "fix": "拆分文件或使用离线审计流程。"}]
    language = _language(name)
    if not language:
        return []
    text = content.decode("utf-8", errors="replace")
    findings: list[dict] = []
    for number, line in enumerate(text.splitlines(), 1):
        for rule_language, pattern, title, severity, fix in _RULES:
            if rule_language != language or not pattern.search(line):
                continue
            findings.append({"audit_id": audit_id, "file": name, "line": number, "snippet": line.strip()[:300], "rule": pattern.pattern[:120], "title": title, "severity": severity, "confidence": "medium", "fix": fix, "status": "open"})
    return findings
