"""轻量级多语言源码审计器：输出可定位、可解释、可复核的结果。"""

from __future__ import annotations

import re
import json

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

_CONFIG_RULES = [
    (".env", re.compile(r"(?i)^(?:[A-Z0-9_]*(?:PASSWORD|SECRET|TOKEN|API_KEY|PRIVATE_KEY)[A-Z0-9_]*)\s*=\s*[^$#\s]+"), "配置文件包含可能的明文凭证", "high", "使用密钥管理服务或环境注入，不要把真实凭证提交到仓库。"),
    ("dockerfile", re.compile(r"(?i)^\s*USER\s+root\s*$|^\s*ADD\s+https?://"), "容器配置存在高风险指令", "high", "使用非 root 用户运行，并对远程构建输入做固定版本校验。"),
    ("compose", re.compile(r"(?i)(?:password|token|secret)\s*:\s*[^$\{\s]+"), "容器编排文件可能包含明文密钥", "high", "通过 secrets 或环境注入凭证，避免写入 compose 文件。"),
    ("config", re.compile(r"(?i)(?:debug\s*[=:]\s*true|allow.?origin\s*[=:]\s*[\"']?\*)"), "配置可能启用调试或任意跨域", "medium", "生产环境关闭 debug，并使用受控来源白名单。"),
]

_DEPENDENCY_FILES = {"requirements.txt", "package.json", "pom.xml", "build.gradle", "composer.json", "go.mod"}
_KNOWN_DEPENDENCY_RISKS = {
    "pyyaml": ("high", "PyYAML 旧版本可能存在不安全反序列化风险"),
    "lodash": ("high", "lodash 旧版本存在原型污染风险"),
    "log4j": ("critical", "Log4j 旧版本存在高风险远程代码执行风险"),
    "requests": ("medium", "requests 版本需要结合版本范围进行安全更新"),
}

def _language(name: str) -> str | None:
    suffix = name.lower().rsplit(".", 1)[-1] if "." in name else ""
    return {"py": "python", "js": "javascript", "jsx": "javascript", "ts": "javascript", "tsx": "javascript", "java": "java", "php": "php", "go": "go", "cs": "csharp", "kt": "kotlin", "kts": "kotlin", "rb": "ruby", "rs": "rust", "sql": "sql"}.get(suffix)


def _config_kind(name: str) -> str | None:
    lower = name.lower().replace("\\", "/").rsplit("/", 1)[-1]
    if lower == ".env" or lower.startswith(".env."):
        return ".env"
    if lower == "dockerfile":
        return "dockerfile"
    if lower in {"docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"}:
        return "compose"
    if lower.endswith((".yml", ".yaml", ".json", ".ini", ".conf", ".properties", ".xml")):
        return "config"
    return None


def _dependency_findings(name: str, text: str, audit_id: str) -> list[dict]:
    lower = name.lower().replace("\\", "/").rsplit("/", 1)[-1]
    if lower not in _DEPENDENCY_FILES:
        return []
    results = []
    for number, line in enumerate(text.splitlines(), 1):
        for package, (severity, title) in _KNOWN_DEPENDENCY_RISKS.items():
            if re.search(rf"(?i)(^|[\"'\s:=]){re.escape(package)}([\"'\s<>=~^]|$)", line):
                results.append({"audit_id": audit_id, "file": name, "line": number, "snippet": line.strip()[:300], "rule": "dependency_advisory", "title": title, "severity": severity, "confidence": "low", "fix": f"锁定 {package} 到供应商已修复版本，并结合 SBOM/CVE 数据源复核。", "status": "open", "dependency": package})
    return results


def _cross_file_findings(files: dict[str, str], audit_id: str) -> list[dict]:
    """Conservative cross-file source-to-sink hints; no execution or code evaluation."""
    sources = []
    sinks = []
    for name, text in files.items():
        for line_no, line in enumerate(text.splitlines(), 1):
            if re.search(r"(?i)(request\.(args|form|query|body)|req\.(query|body|params)|getParameter\(|input\()", line):
                sources.append((name, line_no, line.strip()[:240]))
            if re.search(r"(?i)(execute\(|query\(|innerHTML\s*=|subprocess\.|Runtime\.getRuntime|shell_exec\()", line):
                sinks.append((name, line_no, line.strip()[:240]))
    if not sources or not sinks:
        return []
    source = sources[0]
    sink = next((item for item in sinks if item[0] != source[0]), sinks[0])
    return [{"audit_id": audit_id, "file": sink[0], "line": sink[1], "snippet": sink[2], "rule": "cross_file_data_flow", "title": "跨文件输入到危险调用的数据流线索", "severity": "high", "confidence": "low", "fix": "沿调用链对输入执行白名单校验、上下文编码或参数化，并在人工复核后确认可达性。", "status": "open", "code_flow": [{"file": source[0], "line": source[1], "snippet": source[2], "role": "source"}, {"file": sink[0], "line": sink[1], "snippet": sink[2], "role": "sink"}]}]


def audit_sources(files: dict[str, bytes], audit_id: str) -> list[dict]:
    """Audit a file set with language, config, dependency, and flow checks."""
    decoded = {name: content.decode("utf-8", errors="replace") for name, content in files.items()}
    findings = []
    for name, content in files.items():
        findings.extend(audit_source(name, content, audit_id))
        text = decoded[name]
        findings.extend(_dependency_findings(name, text, audit_id))
        kind = _config_kind(name)
        if kind:
            for number, line in enumerate(text.splitlines(), 1):
                for rule_kind, pattern, title, severity, fix in _CONFIG_RULES:
                    if rule_kind == kind and pattern.search(line):
                        findings.append({"audit_id": audit_id, "file": name, "line": number, "snippet": line.strip()[:300], "rule": "config_security", "title": title, "severity": severity, "confidence": "medium", "fix": fix, "status": "open"})
    findings.extend(_cross_file_findings(decoded, audit_id))
    return findings

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
