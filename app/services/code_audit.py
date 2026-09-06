"""轻量级多语言源码审计器：输出可定位、可解释、可复核的结果。"""

from __future__ import annotations

import re

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
    ("python", re.compile(r"render_template_string\s*\(|Markup\s*\("), "模板内容可能引入服务端模板注入", "high", "不要把用户输入直接交给模板引擎，使用固定模板和自动转义。"),
    ("python", re.compile(r"@(?:app|router)\.(?:route|get|post)\([^)]*\).*csrf|csrf=False"), "Web 框架路由可能缺少 CSRF 防护", "medium", "为状态变更请求启用 CSRF 校验，并使用 SameSite Cookie。"),
    ("javascript", re.compile(r"(?:express|app)\.(?:get|post|put|delete)\([^,]+,\s*(?:async\s*)?\(?(?:req|request)\)?\s*=>"), "Express 路由需要确认认证与授权中间件", "medium", "在敏感路由前挂载认证、权限和输入校验中间件。"),
    ("javascript", re.compile(r"cors\s*\(\s*\{[^}]*origin\s*:\s*['\"]\*"), "CORS 允许任意来源", "medium", "使用受控来源白名单，禁止生产环境使用 origin: '*'."),
    ("java", re.compile(r"@(?:GetMapping|PostMapping|RequestMapping)\([^)]*\)\s*(?:public|private|protected)"), "Spring Web 接口需要确认访问控制", "medium", "为敏感接口增加 Spring Security 权限注解和输入校验。"),
    ("java", re.compile(r"setHeader\s*\(\s*['\"]Access-Control-Allow-Origin['\"]\s*,\s*['\"]\*"), "Java 接口允许任意 CORS 来源", "medium", "改为受控来源白名单，并避免凭据请求配合通配来源。"),
    ("php", re.compile(r"\$request->(?:input|query|get)\([^)]*\).*DB::raw|DB::raw\s*\("), "Laravel 原始 SQL 可能未参数化", "high", "使用查询构造器绑定参数，避免把请求参数拼接到 DB::raw。"),
    ("php", re.compile(r"header\s*\(\s*['\"]Access-Control-Allow-Origin:\s*\*"), "PHP 接口允许任意 CORS 来源", "medium", "使用受控来源白名单并限制跨域凭据。"),
    ("go", re.compile(r"\b(?:exec\.Command|os\.StartProcess)\s*\("), "Go 程序可能执行外部命令", "high", "使用固定命令白名单并分离参数，避免把请求输入传入命令执行。"),
    ("go", re.compile(r"(?:db|tx)\.(?:Query|Exec|QueryRow)\s*\([^\n]*(?:fmt\.Sprintf|\+)"), "Go SQL 查询可能由字符串拼接生成", "high", "使用 database/sql 的占位符绑定参数，避免拼接 SQL。"),
    ("csharp", re.compile(r"\b(?:Process\.Start|new\s+ProcessStartInfo)\s*\("), "C# 程序可能执行外部命令", "high", "使用固定命令白名单，关闭 shell 解释并严格校验参数。"),
    ("csharp", re.compile(r"\b(?:ExecuteSqlRaw|FromSqlRaw)\s*\("), "Entity Framework 原始 SQL 需要检查参数化", "high", "改用参数化 API 或 FromSqlInterpolated，禁止拼接用户输入。"),
    ("kotlin", re.compile(r"\bRuntime\.getRuntime\(\)\.exec|ProcessBuilder\s*\("), "Kotlin 程序可能执行外部命令", "high", "使用固定命令白名单并分离参数，避免 shell 注入。"),
    ("ruby", re.compile(r"\b(?:system|exec|`[^`]+`|Open3\.capture)\s*\(?"), "Ruby 程序可能执行外部命令", "high", "使用数组参数和固定命令白名单，禁止拼接用户输入。"),
    ("ruby", re.compile(r"(?:find_by_sql|execute)\s*\("), "Ruby 原始 SQL 需要检查参数化", "medium", "使用 ActiveRecord 参数绑定，避免拼接 SQL 字符串。"),
    ("rust", re.compile(r"Command::new\s*\(|std::process::Command"), "Rust 程序可能执行外部命令", "high", "使用固定命令白名单并分离参数，避免把用户输入传入命令执行。"),
    ("rust", re.compile(r"format!\s*\([^\n]*(?:SELECT|INSERT|UPDATE|DELETE)"), "Rust SQL 语句可能由字符串拼接生成", "high", "使用数据库驱动提供的参数绑定接口，避免拼接 SQL 字符串。"),
    ("sql", re.compile(r"(?:EXECUTE\s+IMMEDIATE|xp_cmdshell)", re.IGNORECASE), "SQL 动态执行或系统命令调用", "high", "限制动态 SQL 来源并移除数据库到操作系统的命令执行权限。"),
    ("sql", re.compile(r"SELECT\s+.*\+.*FROM|CONCAT\s*\([^\n]*SELECT", re.IGNORECASE), "SQL 语句可能由字符串拼接生成", "high", "使用预编译语句和参数绑定，不要拼接外部输入。"),
]

def _language(name: str) -> str | None:
    suffix = name.lower().rsplit(".", 1)[-1] if "." in name else ""
    return {"py": "python", "js": "javascript", "jsx": "javascript", "ts": "javascript", "tsx": "javascript", "java": "java", "php": "php", "go": "go", "cs": "csharp", "kt": "kotlin", "kts": "kotlin", "rb": "ruby", "rs": "rust", "sql": "sql"}.get(suffix)

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
