"""漏洞哨兵 11-S - SRC 级扫描引擎

该模块提供符合安全应急响应中心（SRC）标准的漏洞报告格式，
包含真实检测能力：SQL 注入、XSS、敏感信息泄露、CSRF、目录遍历、过时组件等。
"""

from __future__ import annotations

import asyncio
import re
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import httpx

# 复用 main.py 的全局 HTTP 客户端和工具函数（避免重复创建）
# 通过延迟导入解决循环依赖问题
_get_httpx_client = None
_safe_read_body = None


def _init_helpers() -> None:
    global _get_httpx_client, _safe_read_body
    if _get_httpx_client is None:
        import main as _main
        _get_httpx_client = _main.get_httpx_client
        _safe_read_body = _main._safe_read_body


# ---------- 常量 ----------

SQLI_PAYLOADS: List[str] = [
    "'",
    "\"",
    "' OR '1'='1",
    "' AND SLEEP(5)--",
    "1' OR '1'='1",
    "admin'--",
]

SQLI_ERROR_PATTERNS: List[str] = [
    "sql syntax", "mysql", "postgresql", "sqlite", "oracle", "sql error",
    "unclosed quotation", "query failed", "warning: mysql", "syntax error",
    "sqlstate", "odbc", "microsoft sql", "mariadb", "pg_query", "pg_exec",
    "you have an error in your sql", "quoted string not properly terminated",
    "unterminated string", "pg_sql", "sqlite3", "database error",
]

XSS_PAYLOADS: List[Tuple[str, str]] = [
    ("<script>alert('xss')</script>", "script_tag"),
    ("<img src=x onerror=alert(1)>", "img_onerror"),
    ("'\"><svg onload=alert(1)>", "svg_onload"),
]

# 敏感信息正则
INFO_LEAK_PATTERNS: Dict[str, Dict[str, Any]] = {
    "phone": {
        "pattern": re.compile(r"(?<![\d])1[3-9]\d{9}(?![\d])"),
        "name": "手机号",
        "severity": "medium",
        "score": 5,
    },
    "id_card": {
        "pattern": re.compile(r"\b\d{17}[\dXx]\b"),
        "name": "身份证号",
        "severity": "high",
        "score": 8,
    },
    "email": {
        "pattern": re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"),
        "name": "邮箱地址",
        "severity": "low",
        "score": 3,
    },
    "internal_ip": {
        "pattern": re.compile(r"\b(127\.\d{1,3}\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3})\b"),
        "name": "内网 IP",
        "severity": "medium",
        "score": 5,
    },
    "api_key": {
        "pattern": re.compile(r"\b(?:api[_-]?key|apikey)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-]{16,})['\"]?", re.I),
        "name": "API Key",
        "severity": "high",
        "score": 8,
    },
    "aws_key": {
        "pattern": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        "name": "AWS Access Key",
        "severity": "critical",
        "score": 9,
    },
    "github_token": {
        "pattern": re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{36,}\b"),
        "name": "GitHub Token",
        "severity": "critical",
        "score": 9,
    },
}

SENSITIVE_PATHS: List[Tuple[str, str, List[str]]] = [
    ("/.git/config", "Git 配置泄露", ["[core]", "[remote"]),
    ("/.env", "环境变量文件", ["=", "DATABASE", "SECRET", "API"]),
    ("/.env.local", "本地环境变量", ["=", "DATABASE"]),
    ("/admin", "管理后台", ["login", "admin", "password", "管理"]),
    ("/phpmyadmin", "phpMyAdmin", ["phpmyadmin", "mysql", "login"]),
    ("/config.php", "PHP 配置", ["<?php", "define", "DB_"]),
    ("/wp-config.php", "WordPress 配置", ["DB_NAME", "DB_USER", "<?php"]),
    ("/backup.sql", "数据库备份", ["CREATE TABLE", "INSERT INTO"]),
    ("/dump.sql", "数据库转储", ["CREATE TABLE", "INSERT INTO"]),
    ("/server-status", "Apache 状态页", ["Apache Status", "Server Version"]),
    ("/actuator/env", "Spring Boot Actuator", ["propertySources", "server.port"]),
    ("/actuator/health", "Spring Boot Health", ["status", "UP", "DOWN"]),
    ("/debug.log", "调试日志", ["ERROR", "WARNING", "DEBUG"]),
    ("/phpinfo.php", "PHP 信息页", ["phpinfo", "PHP Version"]),
]

OUTDATED_COMPONENTS: Dict[str, Dict[str, Any]] = {
    "nginx/1.18.0": {"severity": "medium", "score": 6, "cve": "CVE-2021-23017", "safe": "1.20.1+"},
    "nginx/1.19": {"severity": "medium", "score": 6, "cve": "CVE-2021-23017", "safe": "1.20.1+"},
    "apache/2.4.49": {"severity": "critical", "score": 10, "cve": "CVE-2021-41773", "safe": "2.4.51+"},
    "apache/2.4.50": {"severity": "critical", "score": 10, "cve": "CVE-2021-42013", "safe": "2.4.51+"},
    "php/5.": {"severity": "high", "score": 8, "cve": "CVE-2019-11043", "safe": "7.4+ / 8.x"},
    "php/7.1": {"severity": "high", "score": 8, "cve": "CVE-2019-11043", "safe": "7.4+ / 8.x"},
    "php/7.2": {"severity": "high", "score": 7, "cve": "CVE-2020-7060", "safe": "7.4+ / 8.x"},
    "jquery/1.": {"severity": "medium", "score": 6, "cve": "CVE-2020-11022", "safe": "3.5.0+"},
    "jquery/2.": {"severity": "medium", "score": 6, "cve": "CVE-2020-11022", "safe": "3.5.0+"},
    "lodash/4.17.20": {"severity": "high", "score": 8, "cve": "CVE-2021-23337", "safe": "4.17.21+"},
    "spring-boot/1.": {"severity": "high", "score": 8, "cve": "CVE-2022-22965", "safe": "2.6.6+ / 2.7.x"},
    "spring-boot/2.6": {"severity": "critical", "score": 10, "cve": "CVE-2022-22965", "safe": "2.6.6+ / 2.7.x"},
}

SECURITY_HEADERS = [
    "strict-transport-security",
    "content-security-policy",
    "x-frame-options",
    "x-content-type-options",
    "referrer-policy",
    "permissions-policy",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _generate_id(prefix: str = "VS") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12].upper()}"


def _mask_snippet(snippet: str, visible: int = 4) -> str:
    """对敏感片段脱敏显示。"""
    s = snippet.strip()
    if len(s) <= visible * 2 + 2:
        return s
    return s[:visible] + "****" + s[-visible:]


def _build_request_text(method: str, url: str, headers: Optional[Dict] = None, body: Optional[str] = None) -> str:
    lines = [f"{method} {urlparse(url).path or '/'}?{urlparse(url).query} HTTP/1.1"]
    host = urlparse(url).hostname or ""
    lines.append(f"Host: {host}")
    if headers:
        for k, v in headers.items():
            if k.lower() not in ("host",):
                lines.append(f"{k}: {v}")
    lines.append("")
    if body:
        lines.append(body)
    return "\n".join(lines)


def _build_response_text(resp: httpx.Response, max_len: int = 800) -> str:
    http_ver = resp.http_version
    if not http_ver.upper().startswith("HTTP/"):
        http_ver = f"HTTP/{http_ver}"
    status_line = f"{http_ver} {resp.status_code} {resp.reason_phrase}"
    header_lines = [f"{k}: {v}" for k, v in resp.headers.items()]
    body = resp.text[:max_len]
    if len(resp.text) > max_len:
        body += "\n... [截断]"
    return "\n".join([status_line] + header_lines + ["", body])


def _score_to_severity(score: int) -> str:
    if score >= 9:
        return "critical"
    if score >= 7:
        return "high"
    if score >= 4:
        return "medium"
    if score >= 1:
        return "low"
    return "info"


def _confidence_text(confidence: str) -> str:
    c = confidence.lower()
    if c in ("high", "高"):
        return "high"
    if c in ("medium", "中"):
        return "medium"
    return "low"


def _fix_code_template(vuln_type: str) -> Dict[str, Optional[str]]:
    """为常见漏洞类型提供各平台修复代码模板。"""
    templates: Dict[str, Dict[str, Optional[str]]] = {
        "sqli": {
            "nginx": """# Nginx 无法直接修复 SQL 注入，建议：
# 1. 在后端使用参数化查询
# 2. 使用 Nginx + ModSecurity 拦截常见 SQLI 模式
location / {
    modsecurity on;
    modsecurity_rules_file /etc/nginx/modsecurity.conf;
}""",
            "apache": """# Apache 建议启用 ModSecurity
SecRuleEngine On
SecRule REQUEST_COOKIES|REQUEST_COOKIES_NAMES|REQUEST_FILENAME|ARGS_NAMES|ARGS|XML:/* \
    "@rx (union|select|insert|delete|drop|--|')" \
    "id:1000,phase:2,deny,status:403,msg:'SQL Injection Detected'""",
            "express": """// Express + mysql2 参数化查询示例
const mysql = require('mysql2/promise');
const pool = mysql.createPool({ host: 'localhost', user: 'app', database: 'app' });

app.get('/user', async (req, res) => {
  const [rows] = await pool.execute(
    'SELECT * FROM users WHERE id = ?',
    [req.query.id]
  );
  res.json(rows);
});""",
            "flask": """# Flask + SQLAlchemy 参数化查询示例
from flask import request
from sqlalchemy import text

@app.route('/user')
def get_user():
    user_id = request.args.get('id')
    result = db.session.execute(
        text("SELECT * FROM users WHERE id = :id"),
        {"id": user_id}
    )
    return {"users": [dict(row) for row in result]}""",
            "spring_boot": """// Spring Boot + JdbcTemplate 参数化查询
@GetMapping("/user")
public Map<String, Object> getUser(@RequestParam Long id) {
    return jdbcTemplate.queryForMap(
        "SELECT * FROM users WHERE id = ?",
        id
    );
}""",
            "cloudflare": """# Cloudflare WAF 托管规则
# 在防火墙 > WAF > 托管规则中启用：
# - OWASP ModSecurity Core Rule Set (CRS)
# - Cloudflare Specials: SQL Injection""",
            "generic": "使用参数化查询（Prepared Statements），永远不要将用户输入拼接到 SQL 语句中。",
        },
        "xss": {
            "nginx": """# Nginx 添加安全响应头（辅助缓解 XSS）
add_header Content-Security-Policy "default-src 'self'; script-src 'self'; object-src 'none'" always;
add_header X-XSS-Protection "1; mode=block" always;""",
            "apache": """# Apache 添加 CSP 头
Header always set Content-Security-Policy "default-src 'self'; script-src 'self'; object-src 'none'"
Header always set X-XSS-Protection "1; mode=block""",
            "express": """// Express 输出编码 + CSP
const escapeHtml = require('escape-html');

app.get('/search', (req, res) => {
  res.send(`<p>搜索结果: ${escapeHtml(req.query.q)}</p>`);
});

// 全局 CSP
app.use((req, res, next) => {
  res.setHeader('Content-Security-Policy', "default-src 'self'");
  next();
});""",
            "flask": """# Flask Jinja2 自动转义 + CSP
from flask import render_template_string
from flask_talisman import Talisman

Talisman(app, content_security_policy={"default-src": "'self'"})

@app.route('/search')
def search():
    q = request.args.get('q', '')
    return render_template_string('<p>搜索结果: {{ q }}</p>', q=q)""",
            "spring_boot": """// Spring Boot 输出编码
@GetMapping("/search")
public String search(@RequestParam String q, Model model) {
    model.addAttribute("q", HtmlUtils.htmlEscape(q));
    return "search";
}""",
            "cloudflare": """# Cloudflare 内容扫描
# 防火墙 > WAF > 托管规则：启用 XSS 防护
# 页面规则：配置 CSP 响应头""",
            "generic": "对所有用户输入进行 HTML 上下文编码，配置 Content-Security-Policy，使用现代框架的自动转义功能。",
        },
        "info_leak": {
            "nginx": """# Nginx 隐藏版本号与敏感路径
server_tokens off;
location ~ /\.(env|git|svn|htaccess|bak) {
    deny all;
    return 404;
}""",
            "apache": """# Apache 隐藏版本与敏感路径
ServerTokens Prod
ServerSignature Off
<FilesMatch "^\.">
    Require all denied
</FilesMatch>""",
            "express": """// Express 禁用版本头、限制敏感路径
app.disable('x-powered-by');
app.use('/.env', (req, res) => res.status(403).end());
app.use('/.git', (req, res) => res.status(403).end());""",
            "flask": """# Flask 禁用 Server 头、保护敏感路径
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app)

@app.after_request
def remove_headers(resp):
    resp.headers.pop('Server', None)
    return resp

@app.route('/<path:sub>')
def block_sensitive(sub):
    if sub.startswith('.env') or sub.startswith('.git'):
        abort(403)""",
            "spring_boot": """// Spring Boot 关闭 Actuator 暴露
management.endpoints.web.exposure.include=health
management.endpoint.health.show-details=never
# 或完全关闭
management.server.port=-1""",
            "cloudflare": """# Cloudflare 防火墙规则
# 阻止 URI 包含 /.git、/.env、/config.php 的请求
(http.request.uri.path contains "/.git" or http.request.uri.path contains "/.env") 
-> block""",
            "generic": "移除或隐藏敏感文件，关闭详细错误信息，对响应中的敏感数据进行脱敏或删除。",
        },
        "csrf": {
            "nginx": "# CSRF 主要在应用层防护，Nginx 可配合 SameSite Cookie 与 Referer 校验策略使用。",
            "apache": "# CSRF 主要在应用层防护，Apache 可配合 mod_security CRS 的 CSRF 规则集使用。",
            "express": """// Express csurf 中间件
const csurf = require('csurf');
const csrfProtection = csurf({ cookie: { httpOnly: true, sameSite: 'strict' } });

app.get('/form', csrfProtection, (req, res) => {
  res.render('form', { csrfToken: req.csrfToken() });
});
app.post('/submit', csrfProtection, (req, res) => { ... });""",
            "flask": """# Flask-WTF CSRF 保护
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)

# 模板中
# <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">""",
            "spring_boot": """// Spring Security CSRF
@EnableWebSecurity
public class SecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http.csrf(csrf -> csrf.csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse()));
        return http.build();
    }
}""",
            "cloudflare": "# Cloudflare 无法直接阻止 CSRF，建议结合 SameSite=Strict Cookie 与自定义 Worker 校验 Referer。",
            "generic": "所有状态变更请求使用不可预测的反 CSRF Token；Cookie 设置 SameSite=Strict/Lax 与 Secure；校验 Referer/Origin。",
        },
        "sensitive_path": {
            "nginx": """location ~ /\.(git|env|svn|htaccess|bak) {
    deny all;
    return 404;
}
location /admin {
    allow 10.0.0.0/8;
    deny all;
}""",
            "apache": """<LocationMatch "^/\.(git|env|svn)">
    Require all denied
</LocationMatch>
<Location "/admin">
    Require ip 10.0.0.0/8
</Location>""",
            "express": """// 保护敏感路径
const FORBIDDEN = ['/.git', '/.env', '/admin'];
app.use((req, res, next) => {
  if (FORBIDDEN.some(p => req.path.startsWith(p))) {
    return res.status(403).end();
  }
  next();
});""",
            "flask": """# 保护敏感路径
from flask import abort

@app.before_request
def protect_sensitive():
    if request.path.startswith(('/.git', '/.env', '/admin')):
        abort(403)""",
            "spring_boot": """// Spring Security 路径授权
http.authorizeHttpRequests(auth -> auth
    .requestMatchers("/.env", "/.git/**", "/admin/**").denyAll()
    .anyRequest().permitAll()
);""",
            "cloudflare": """# Cloudflare 防火墙规则
(http.request.uri.path contains "/.git" or http.request.uri.path contains "/.env" or http.request.uri.path contains "/admin")
-> block""",
            "generic": "禁止公开访问敏感路径；对管理后台实施 IP 白名单或 MFA；定期审计 Web 根目录。",
        },
        "outdated_component": {
            "nginx": "# 升级 Nginx 到最新稳定版，并订阅官方安全通告。",
            "apache": "# 升级 Apache Httpd 到最新稳定版，并启用自动安全更新。",
            "express": "# 运行 npm audit fix 升级依赖，关注 Snyk/Dependabot 告警。",
            "flask": "# 运行 pip list --outdated，升级 Flask 及相关依赖。",
            "spring_boot": "# 升级 Spring Boot 版本，关注 Spring Security 公告。",
            "cloudflare": "# 保持 Cloudflare 托管规则与 WAF 版本为最新。",
            "generic": "升级组件到安全版本，建立依赖漏洞监控与补丁管理流程。",
        },
        "header_missing": {
            "nginx": """add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header Content-Security-Policy "default-src 'self'" always;
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;""",
            "apache": """Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
Header always set Content-Security-Policy "default-src 'self'"
Header always set X-Frame-Options "DENY"
Header always set X-Content-Type-Options "nosniff"
Header always set Referrer-Policy "strict-origin-when-cross-origin""",
            "express": """// Express 安全头中间件
const helmet = require('helmet');
app.use(helmet());""",
            "flask": """# Flask-Talisman
from flask_talisman import Talisman
Talisman(app)""",
            "spring_boot": """// Spring Security 安全头
http.headers(headers -> headers
    .httpStrictTransportSecurity(hsts -> hsts.includeSubDomains(true).maxAgeInSeconds(31536000))
    .contentSecurityPolicy(csp -> csp.policyDirectives("default-src 'self'"))
    .frameOptions(frame -> frame.deny())
);""",
            "cloudflare": """# Cloudflare 转换规则
# 在规则 > 转换规则 > 修改响应头中添加所需安全头""",
            "generic": "配置所需安全响应头（HSTS、CSP、X-Frame-Options、X-Content-Type-Options、Referrer-Policy 等）。",
        },
    }
    return templates.get(vuln_type, {k: None for k in ["nginx", "apache", "express", "flask", "spring_boot", "cloudflare", "generic"]})


def _references(vuln_type: str) -> List[str]:
    refs = {
        "sqli": [
            "https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html",
            "https://portswigger.net/web-security/sql-injection",
        ],
        "xss": [
            "https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html",
            "https://portswigger.net/web-security/cross-site-scripting",
        ],
        "info_leak": [
            "https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html",
            "https://owasp.org/www-project-top-ten/2017/A3_2017-Sensitive_Data_Exposure",
        ],
        "csrf": [
            "https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html",
            "https://portswigger.net/web-security/csrf",
        ],
        "sensitive_path": [
            "https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/02-Configuration_and_Deployment_Management_Testing/05-Enumerate_Infrastructure_and_Application_Admin_Interfaces",
        ],
        "outdated_component": [
            "https://owasp.org/www-project-top-ten/2017/A9_2017-Using_Components_with_Known_Vulnerabilities",
            "https://nvd.nist.gov/",
        ],
        "header_missing": [
            "https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html",
            "https://owasp.org/www-project-secure-headers/",
        ],
    }
    return refs.get(vuln_type, [])


def _owasp_category(vuln_type: str) -> str:
    mapping = {
        "sqli": "A03:2021 - Injection",
        "xss": "A03:2021 - Injection",
        "info_leak": "A02:2021 - Cryptographic Failures / A05 - Security Misconfiguration",
        "csrf": "A01:2021 - Broken Access Control",
        "sensitive_path": "A01:2021 - Broken Access Control",
        "outdated_component": "A06:2021 - Vulnerable and Outdated Components",
        "header_missing": "A05:2021 - Security Misconfiguration",
        "ssl": "A02:2021 - Cryptographic Failures",
        "cors": "A01:2021 - Broken Access Control",
        "cookie": "A07:2021 - Identification and Authentication Failures",
    }
    return mapping.get(vuln_type, "A05:2021 - Security Misconfiguration")


def build_finding(
    vuln_type: str,
    title: str,
    severity: str,
    severity_score: int,
    url: str,
    parameter: str,
    location: str,
    description: str,
    evidence_request: str,
    evidence_response: str,
    evidence_payload: Optional[str] = None,
    impact: str = "",
    reproduce_steps: Optional[List[str]] = None,
    fix_suggestion: str = "",
    confidence: str = "high",
    screenshot: Optional[str] = None,
) -> Dict[str, Any]:
    """构建 SRC 标准 finding。"""
    fix_code = _fix_code_template(vuln_type)
    return {
        "id": _generate_id(),
        "title": title,
        "type": vuln_type,
        "severity": severity,
        "severity_score": severity_score,
        "url": url,
        "parameter": parameter,
        "location": location,
        "description": description,
        "evidence": {
            "request": evidence_request,
            "response": evidence_response,
            "payload": evidence_payload,
            "screenshot": screenshot,
        },
        "impact": impact or description,
        "reproduce_steps": reproduce_steps or [],
        "fix_suggestion": fix_suggestion or _fix_code_template(vuln_type).get("generic", ""),
        "fix_code": fix_code,
        "references": _references(vuln_type),
        "confidence": _confidence_text(confidence),
        "owasp_category": _owasp_category(vuln_type),
        "discovered_at": _now_iso(),
    }


# ---------- 真实检测能力 ----------

def _build_test_url(url: str, param: str, payload: str) -> str:
    parsed = urlparse(url)
    qs = parse_qs(parsed.query, keep_blank_values=True)
    qs[param] = [payload]
    new_query = urlencode(qs, doseq=True)
    return urlunparse(parsed._replace(query=new_query))


async def detect_sqli_src(url: str) -> List[Dict[str, Any]]:
    """SQL 注入检测（SRC 格式）。"""
    _init_helpers()
    client = _get_httpx_client()
    findings: List[Dict[str, Any]] = []

    parsed = urlparse(url)
    params = list(parse_qs(parsed.query, keep_blank_values=True).keys()) if parsed.query else []
    if not params:
        return findings

    baseline_body = ""
    baseline_time = 0.0
    try:
        resp = await client.get(url, timeout=10.0, follow_redirects=True)
        baseline_body = _safe_read_body(resp).lower()
        baseline_time = resp.elapsed.total_seconds() if resp.elapsed else 0.0
    except Exception:
        pass

    for param in params[:6]:
        for payload in SQLI_PAYLOADS:
            test_url = _build_test_url(url, param, payload)
            try:
                start = time.time()
                resp = await client.get(test_url, timeout=12.0, follow_redirects=True)
                elapsed = time.time() - start
                body = _safe_read_body(resp)
                body_lower = body.lower()

                matched_pattern = None
                for pattern in SQLI_ERROR_PATTERNS:
                    if pattern in body_lower:
                        matched_pattern = pattern
                        break

                if matched_pattern:
                    findings.append(build_finding(
                        vuln_type="sqli",
                        title=f"SQL 注入漏洞（参数 {param}）",
                        severity="critical",
                        severity_score=10,
                        url=test_url,
                        parameter=param,
                        location=f"URL 参数 {param}",
                        description=f"参数 '{param}' 存在 SQL 注入漏洞，响应中包含数据库错误信息，攻击者可构造恶意 SQL 语句读取、修改或删除数据库数据。",
                        evidence_request=_build_request_text("GET", test_url),
                        evidence_response=_build_response_text(resp, 600),
                        evidence_payload=payload,
                        impact="攻击者可利用该漏洞绕过认证、读取敏感数据、篡改数据库内容，甚至获取服务器权限。",
                        reproduce_steps=[
                            f"访问目标页面：{url}",
                            f"在参数 {param} 中注入 payload：{payload}",
                            "提交请求并观察响应是否包含数据库错误信息或异常数据",
                            "使用 sqlmap 或手工 union select 进一步验证数据读取能力",
                        ],
                        fix_suggestion="在所有数据库操作中使用参数化查询（Prepared Statements），禁止字符串拼接 SQL；对 ORM 禁用原生 SQL 拼接。",
                        confidence="high",
                    ))
                    break

                elif "sleep" in payload.lower() or "delay" in payload.lower():
                    if elapsed > baseline_time + 4 and elapsed > 5:
                        findings.append(build_finding(
                            vuln_type="sqli",
                            title=f"SQL 注入漏洞 - 时间盲注（参数 {param}）",
                            severity="high",
                            severity_score=8,
                            url=test_url,
                            parameter=param,
                            location=f"URL 参数 {param}",
                            description=f"参数 '{param}' 疑似存在 SQL 时间盲注，注入延时 payload 后响应时间显著增加（{elapsed:.1f}s）。",
                            evidence_request=_build_request_text("GET", test_url),
                            evidence_response=_build_response_text(resp, 400) + f"\n\n[响应时间] {elapsed:.2f}s",
                            evidence_payload=payload,
                            impact="即使无错误回显，攻击者仍可通过逐位猜测的方式抽取数据库内容。",
                            reproduce_steps=[
                                f"记录正常请求响应时间（约 {baseline_time:.2f}s）",
                                f"在参数 {param} 注入：{payload}",
                                f"观察响应时间是否显著增加（实测 {elapsed:.1f}s）",
                            ],
                            fix_suggestion="使用参数化查询；为数据库查询设置最大执行时间（statement_timeout）；统一错误处理避免信息泄露。",
                            confidence="medium",
                        ))
                        break

                elif _response_differs_significantly(baseline_body, body_lower):
                    findings.append(build_finding(
                        vuln_type="sqli",
                        title=f"SQL 注入漏洞 - 疑似布尔盲注（参数 {param}）",
                        severity="high",
                        severity_score=7,
                        url=test_url,
                        parameter=param,
                        location=f"URL 参数 {param}",
                        description=f"参数 '{param}' 注入后响应内容显著变化，疑似存在布尔盲注。",
                        evidence_request=_build_request_text("GET", test_url),
                        evidence_response=_build_response_text(resp, 600),
                        evidence_payload=payload,
                        impact="攻击者可通过构造布尔条件逐位推断数据库内容。",
                        reproduce_steps=[
                            "记录正常页面响应内容",
                            f"注入永真条件：{payload}",
                            "对比响应内容差异，确认是否存在布尔盲注",
                        ],
                        fix_suggestion="使用参数化查询；统一错误页面与正常页面的响应长度和内容。",
                        confidence="medium",
                    ))
                    break

            except Exception as e:
                continue
    return findings


def _response_differs_significantly(baseline: str, current: str, threshold: float = 0.3) -> bool:
    if not baseline or not current:
        return False
    if abs(len(baseline) - len(current)) > max(len(baseline), 1) * threshold:
        return True
    return False


async def detect_xss_src(url: str) -> List[Dict[str, Any]]:
    """反射型 XSS 检测（SRC 格式）。"""
    _init_helpers()
    client = _get_httpx_client()
    findings: List[Dict[str, Any]] = []

    parsed = urlparse(url)
    params = list(parse_qs(parsed.query, keep_blank_values=True).keys()) if parsed.query else []
    if not params:
        return findings

    for param in params[:6]:
        for payload, tag in XSS_PAYLOADS:
            test_url = _build_test_url(url, param, payload)
            try:
                resp = await client.get(test_url, timeout=10.0, follow_redirects=True)
                body = _safe_read_body(resp)

                if payload in body:
                    script_pattern = re.compile(r"<script[^>]*>.*" + re.escape(payload) + r".*</script>", re.I | re.S)
                    event_pattern = re.compile(r"(on\w+)=[\"'].*" + re.escape(payload) + r".*[\"']", re.I)
                    attr_pattern = re.compile(r"<[^>]*" + re.escape(payload) + r"[^>]*>", re.I)

                    dangerous = bool(script_pattern.search(body) or event_pattern.search(body))
                    reflected_context = "script/event" if dangerous else "html_attribute" if attr_pattern.search(body) else "html_body"

                    severity = "high" if dangerous else "medium"
                    score = 8 if dangerous else 5

                    findings.append(build_finding(
                        vuln_type="xss",
                        title=f"反射型 XSS 漏洞（参数 {param}）",
                        severity=severity,
                        severity_score=score,
                        url=test_url,
                        parameter=param,
                        location=f"URL 参数 {param}，反射位置：{reflected_context}",
                        description=f"参数 '{param}' 的输入未经过滤即反射到响应中，payload 在 {reflected_context} 上下文中执行，可触发任意 JavaScript 代码。",
                        evidence_request=_build_request_text("GET", test_url),
                        evidence_response=_build_response_text(resp, 800),
                        evidence_payload=payload,
                        impact="攻击者可构造恶意链接，诱导用户点击后窃取 Cookie、会话令牌或执行钓鱼攻击。",
                        reproduce_steps=[
                            f"访问：{test_url}",
                            "查看页面源代码，确认 payload 是否原样反射",
                            f"在浏览器开发者工具中观察 payload 所在上下文（{reflected_context}）",
                            "尝试替换为 document.cookie 窃取脚本验证",
                        ],
                        fix_suggestion="在输出到 HTML 前进行上下文相关编码；配置 CSP；优先使用框架自动转义机制。",
                        confidence="high" if dangerous else "medium",
                    ))
                    break
            except Exception:
                continue
    return findings


async def detect_info_leak_src(url: str, headers: Dict[str, str], body: Optional[str] = None) -> List[Dict[str, Any]]:
    """敏感信息泄露检测（SRC 格式）。"""
    _init_helpers()
    client = _get_httpx_client()
    findings: List[Dict[str, Any]] = []

    if body is None:
        try:
            resp = await client.get(url, timeout=10.0, follow_redirects=True)
            body = _safe_read_body(resp)
        except Exception:
            body = ""

    text = body[:500 * 1024]  # 限制扫描长度

    for leak_type, config in INFO_LEAK_PATTERNS.items():
        matches = list(config["pattern"].finditer(text))
        if not matches:
            continue

        # 去重并限制数量
        seen = set()
        snippets = []
        for m in matches:
            key = m.group(0).strip()
            if key in seen or len(key) < 4:
                continue
            seen.add(key)
            snippets.append(_mask_snippet(key))
            if len(snippets) >= 5:
                break

        if not snippets:
            continue

        first = next(iter(matches))
        snippet_text = "; ".join(snippets)
        findings.append(build_finding(
            vuln_type="info_leak",
            title=f"敏感信息泄露：{config['name']}",
            severity=config["severity"],
            severity_score=config["score"],
            url=url,
            parameter="",
            location="响应体",
            description=f"响应中检测到 {config['name']} 信息泄露，可能暴露用户隐私或内部凭证。",
            evidence_request=_build_request_text("GET", url),
            evidence_response=f"[匹配片段（已脱敏）]\n{snippet_text}\n\n[匹配位置] 响应体偏移 {first.start()}",
            impact=f"泄露 {config['name']} 可用于社会工程、横向渗透或进一步利用。",
            reproduce_steps=[
                f"访问 {url}",
                f"在响应中搜索 {config['name']} 特征",
                "使用 Burp/正则提取完整内容并评估影响范围",
            ],
            fix_suggestion="对响应中的敏感数据进行脱敏、删除或加密；加强日志与错误处理；定期使用 DLP 工具扫描。",
            confidence="high",
        ))

    # Server / X-Powered-By 头泄露
    for header_name in ["server", "x-powered-by"]:
        value = headers.get(header_name, headers.get(header_name.title(), ""))
        if value and re.search(r"\d+\.\d+", value):
            findings.append(build_finding(
                vuln_type="info_leak",
                title=f"服务器信息泄露：{header_name.title()}",
                severity="low",
                severity_score=2,
                url=url,
                parameter="",
                location=f"响应头 {header_name.title()}",
                description=f"响应头 {header_name.title()} 暴露了服务器软件及版本信息，便于攻击者筛选已知 CVE。",
                evidence_request=_build_request_text("GET", url),
                evidence_response=f"{header_name.title()}: {value}",
                impact="攻击者可结合版本信息快速定位已知漏洞利用代码。",
                reproduce_steps=[
                    f"curl -I {url}",
                    f"观察 {header_name.title()} 头是否包含版本号",
                ],
                fix_suggestion="隐藏或修改 Server / X-Powered-By 头；保持组件及时更新。",
                confidence="high",
            ))

    return findings


async def detect_csrf_src(url: str, headers: Dict[str, str], body: Optional[str] = None) -> List[Dict[str, Any]]:
    """CSRF 防护缺失检测（SRC 格式）。"""
    _init_helpers()
    client = _get_httpx_client()
    findings: List[Dict[str, Any]] = []

    if body is None:
        try:
            resp = await client.get(url, timeout=10.0, follow_redirects=True)
            body = _safe_read_body(resp)
        except Exception:
            body = ""

    # 检测表单是否缺少 CSRF Token
    form_pattern = re.compile(r"<form[^>]*>(.*?)</form>", re.I | re.S)
    token_pattern = re.compile(r"csrf|xsrf|anti.?token", re.I)
    for match in form_pattern.finditer(body):
        form_html = match.group(1)
        action_match = re.search(r'action=["\']([^"\']*)["\']', match.group(0), re.I)
        method_match = re.search(r'method=["\']([^"\']*)["\']', match.group(0), re.I)
        method = (method_match.group(1).upper() if method_match else "GET")
        if method != "POST":
            continue
        if not token_pattern.search(form_html):
            findings.append(build_finding(
                vuln_type="csrf",
                title="表单缺少 CSRF Token 防护",
                severity="medium",
                severity_score=6,
                url=url,
                parameter="",
                location=f"页面表单 (action={action_match.group(1) if action_match else ''})",
                description="页面中存在 POST 表单，但未包含 CSRF Token，攻击者可构造跨站请求伪造攻击。",
                evidence_request=_build_request_text("GET", url),
                evidence_response=form_html[:600],
                impact="攻击者可诱导已登录用户提交非预期请求，导致数据修改、权限变更等操作。",
                reproduce_steps=[
                    f"访问 {url}",
                    "定位页面中的 POST 表单",
                    "检查表单字段是否包含 csrf_token / _csrf 等",
                    "构造恶意 HTML 页面，使用自动提交的 form 进行验证",
                ],
                fix_suggestion="为所有状态变更表单添加不可预测且与用户会话绑定的 CSRF Token；同时校验 Referer/Origin。",
                confidence="medium",
            ))
            break

    # Cookie SameSite=None 且无 Secure
    set_cookie = headers.get("set-cookie", headers.get("Set-Cookie", ""))
    if set_cookie:
        cookie_lower = set_cookie.lower()
        if "samesite=none" in cookie_lower and "secure" not in cookie_lower:
            findings.append(build_finding(
                vuln_type="csrf",
                title="Cookie SameSite=None 未配合 Secure 标志",
                severity="medium",
                severity_score=5,
                url=url,
                parameter="",
                location="Set-Cookie 响应头",
                description="Cookie 设置为 SameSite=None 但未标记 Secure，浏览器将拒绝发送该 Cookie，且存在 CSRF 风险。",
                evidence_request=_build_request_text("GET", url),
                evidence_response=f"Set-Cookie: {set_cookie}",
                impact="跨站请求可携带会话 Cookie，增加 CSRF 攻击面。",
                reproduce_steps=[
                    f"curl -I {url}",
                    "检查 Set-Cookie 头是否包含 SameSite=None 且缺少 Secure",
                ],
                fix_suggestion="为 SameSite=None 的 Cookie 同时设置 Secure 标志；或改用 SameSite=Strict/Lax。",
                confidence="high",
            ))

    return findings


async def detect_sensitive_paths_src(base_url: str) -> List[Dict[str, Any]]:
    """目录遍历 / 未授权访问检测（SRC 格式）。"""
    _init_helpers()
    client = _get_httpx_client()
    findings: List[Dict[str, Any]] = []

    parsed = urlparse(base_url)
    origin = f"{parsed.scheme}://{parsed.netloc}"

    async def check(path: str, name: str, indicators: List[str]) -> None:
        test_url = origin + path
        try:
            resp = await client.get(test_url, timeout=10.0, follow_redirects=True)
            if resp.status_code != 200:
                return
            body = _safe_read_body(resp)
            body_lower = body.lower()

            # 软 404 过滤
            soft_404 = ["page not found", "not found", "404 not found", "找不到页面", "页面不存在"]
            if any(p in body_lower for p in soft_404):
                return

            matched = [i for i in indicators if i.lower() in body_lower]
            if matched or len(body) > 10:
                snippet = body[:500]
                findings.append(build_finding(
                    vuln_type="sensitive_path",
                    title=f"敏感路径可访问：{path}",
                    severity="high" if path in ("/.git/config", "/.env", "/wp-config.php") else "medium",
                    severity_score=8 if path in ("/.git/config", "/.env", "/wp-config.php") else 5,
                    url=test_url,
                    parameter="",
                    location=f"路径 {path}",
                    description=f"{name} 路径可直接访问，可能暴露源代码、配置信息或管理接口。",
                    evidence_request=_build_request_text("GET", test_url),
                    evidence_response=_build_response_text(resp, 700),
                    impact="攻击者可获取数据库凭证、源代码、系统配置，进而控制服务器或横向移动。",
                    reproduce_steps=[
                        f"直接访问：{test_url}",
                        "确认返回状态码为 200 且包含敏感内容",
                        "尝试访问父目录或相关文件",
                    ],
                    fix_suggestion="禁止公开访问敏感路径；对管理后台加 IP 白名单/MFA；Web 服务器配置拒绝访问 .git/.env 等目录。",
                    confidence="high" if matched else "medium",
                ))
        except Exception:
            return

    tasks = [check(path, name, indicators) for path, name, indicators in SENSITIVE_PATHS]
    await asyncio.gather(*tasks, return_exceptions=True)
    return findings


async def detect_outdated_components_src(url: str, headers: Dict[str, str], body: Optional[str] = None) -> List[Dict[str, Any]]:
    """过时组件 / CVE 检测（SRC 格式）。"""
    _init_helpers()
    client = _get_httpx_client()
    findings: List[Dict[str, Any]] = []

    if body is None:
        try:
            resp = await client.get(url, timeout=10.0, follow_redirects=True)
            body = _safe_read_body(resp)
        except Exception:
            body = ""

    detected: List[Tuple[str, str]] = []

    # 从响应头识别
    for header in ["server", "x-powered-by"]:
        value = headers.get(header, headers.get(header.title(), ""))
        if value:
            detected.append((header, value.lower()))

    # 从响应体识别常见 JS 库
    js_patterns = {
        r"jquery[/-](\d+\.\d+\.?\d*)": "jquery",
        r"lodash[/-](\d+\.\d+\.?\d*)": "lodash",
        r"vue[/-](\d+\.\d+\.?\d*)": "vue",
        r"react[/-](\d+\.\d+\.?\d*)": "react",
    }
    for pattern, name in js_patterns.items():
        for match in re.finditer(pattern, body.lower()):
            version = match.group(1)
            detected.append((name, f"{name}/{version}"))

    checked = set()
    for source, signature in detected:
        for prefix, info in OUTDATED_COMPONENTS.items():
            if signature.startswith(prefix) and prefix not in checked:
                checked.add(prefix)
                findings.append(build_finding(
                    vuln_type="outdated_component",
                    title=f"过时组件：{signature}",
                    severity=info["severity"],
                    severity_score=info["score"],
                    url=url,
                    parameter="",
                    location=f"{source} 识别",
                    description=f"检测到组件 {signature}，该版本存在已知漏洞 {info['cve']}，建议升级至 {info['safe']}。",
                    evidence_request=_build_request_text("GET", url),
                    evidence_response=f"{source}: {signature}",
                    impact="攻击者可利用已知 CVE 执行远程代码、读取敏感数据或提升权限。",
                    reproduce_steps=[
                        f"curl -I {url}",
                        f"确认 {source} 头或 JS 资源包含 {signature}",
                        f"查询 {info['cve']} 利用条件与 PoC",
                    ],
                    fix_suggestion=f"升级 {signature.split('/')[0]} 至安全版本 {info['safe']}，并建立组件漏洞监控流程。",
                    confidence="high",
                ))

    return findings


# ---------- 扫描编排 ----------

async def run_src_scan(
    url: str,
    headers: Dict[str, str],
    is_https: bool,
    ssl_info: Dict[str, Any],
    waf: Optional[str] = None,
    deep: bool = False,
) -> Dict[str, Any]:
    """执行 SRC 级扫描并返回标准化响应。"""
    _init_helpers()
    start_ts = time.time()
    findings: List[Dict[str, Any]] = []

    # 并行执行动态检测
    sqli_task = detect_sqli_src(url)
    xss_task = detect_xss_src(url)
    info_leak_task = detect_info_leak_src(url, headers)
    csrf_task = detect_csrf_src(url, headers)
    paths_task = detect_sensitive_paths_src(url)
    components_task = detect_outdated_components_src(url, headers)

    results = await asyncio.gather(
        sqli_task, xss_task, info_leak_task, csrf_task, paths_task, components_task,
        return_exceptions=True,
    )
    for res in results:
        if isinstance(res, list):
            findings.extend(res)
        elif isinstance(res, Exception):
            import logging
            logging.getLogger("src_scanner").warning("Detection error: %s", res)

    # 安全头缺失
    missing_headers = []
    for h in SECURITY_HEADERS:
        if not headers.get(h, headers.get(h.title())):
            missing_headers.append(h)
            title = {
                "strict-transport-security": "缺少 HSTS 响应头",
                "content-security-policy": "缺少 CSP 响应头",
                "x-frame-options": "缺少 X-Frame-Options 响应头",
                "x-content-type-options": "缺少 X-Content-Type-Options 响应头",
                "referrer-policy": "缺少 Referrer-Policy 响应头",
                "permissions-policy": "缺少 Permissions-Policy 响应头",
            }.get(h, f"缺少 {h} 响应头")
            findings.append(build_finding(
                vuln_type="header_missing",
                title=title,
                severity="medium" if h in ("strict-transport-security", "content-security-policy", "x-frame-options") else "low",
                severity_score=5 if h in ("strict-transport-security", "content-security-policy", "x-frame-options") else 2,
                url=url,
                parameter="",
                location="HTTP 响应头",
                description=f"目标未配置 {h} 安全响应头，降低了浏览器端的安全防护能力。",
                evidence_request=_build_request_text("GET", url),
                evidence_response="\n".join([f"{k}: {v}" for k, v in headers.items()]) or "（无响应头）",
                impact="缺少安全头可导致点击劫持、MIME 嗅探、信息泄露等风险。",
                reproduce_steps=[
                    f"curl -I {url}",
                    f"确认响应头中不存在 {h}",
                ],
                fix_suggestion="在 Web 服务器或应用框架中配置对应安全响应头。",
                confidence="high",
            ))

    # HTTPS / SSL
    ssl_finding = None
    if not is_https:
        findings.append(build_finding(
            vuln_type="header_missing",
            title="未启用 HTTPS",
            severity="critical",
            severity_score=10,
            url=url,
            parameter="",
            location="协议层",
            description="目标使用 HTTP 明文传输，数据可被中间人窃听或篡改。",
            evidence_request=_build_request_text("GET", url),
            evidence_response="URL 协议为 http://",
            impact="用户凭证、Cookie、业务数据在传输过程中完全暴露。",
            reproduce_steps=[
                f"使用 curl 访问 {url}",
                "确认未发生 301 跳转到 HTTPS",
            ],
            fix_suggestion="申请 SSL/TLS 证书，强制 80 端口 301 跳转至 HTTPS，并配置 HSTS。",
            confidence="high",
        ))
    elif ssl_info.get("expired"):
        findings.append(build_finding(
            vuln_type="ssl",
            title="SSL 证书已过期",
            severity="high",
            severity_score=8,
            url=url,
            parameter="",
            location="TLS 证书",
            description=f"SSL 证书已过期 {ssl_info.get('days_left')} 天，浏览器会显示安全警告。",
            evidence_request=_build_request_text("GET", url),
            evidence_response=str(ssl_info),
            impact="用户无法正常访问，数据传输不受信任。",
            reproduce_steps=["使用 openssl s_client 连接目标", "检查证书有效期"],
            fix_suggestion="立即续期 SSL 证书并部署。",
            confidence="high",
        ))
    elif isinstance(ssl_info.get("days_left"), (int, float)) and ssl_info["days_left"] < 30:
        findings.append(build_finding(
            vuln_type="ssl",
            title="SSL 证书即将过期",
            severity="medium",
            severity_score=4,
            url=url,
            parameter="",
            location="TLS 证书",
            description=f"SSL 证书将在 {ssl_info['days_left']} 天后过期。",
            evidence_request=_build_request_text("GET", url),
            evidence_response=str(ssl_info),
            impact="证书过期后将导致服务不可用。",
            reproduce_steps=["检查证书有效期"],
            fix_suggestion="提前续期 SSL 证书。",
            confidence="high",
        ))

    # 评分
    score = 100
    summary = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0, "total": 0}
    severity_weights = {"critical": 25, "high": 15, "medium": 8, "low": 3, "info": 0}
    for f in findings:
        sev = f.get("severity", "info")
        summary[sev] = summary.get(sev, 0) + 1
        summary["total"] += 1
        score -= severity_weights.get(sev, 0)
    score = max(10, min(100, score))

    risk_level = "critical" if score < 40 else "high" if score < 60 else "medium" if score < 80 else "low"

    duration_ms = int((time.time() - start_ts) * 1000)

    return {
        "success": True,
        "scan_id": int(time.time()),
        "url": url,
        "score": score,
        "risk_level": risk_level,
        "summary": summary,
        "findings": findings,
        "headers": headers,
        "waf": waf,
        "ssl": ssl_info,
        "duration_ms": duration_ms,
        "report_share_id": _generate_id("RPT"),
    }
