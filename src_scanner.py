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


# 证据存储（由插件化扫描入口注入）
_evidence_store = None


def set_evidence_store(store: Any) -> None:
    """设置全局证据存储，供检测函数记录 HTTP 交互。"""
    global _evidence_store
    _evidence_store = store


def clear_evidence_store() -> None:
    """清除全局证据存储。"""
    global _evidence_store
    _evidence_store = None


async def _recorded_request(method: str, url: str, **kwargs: Any) -> Any:
    """执行 HTTP 请求并将请求/响应记录到证据存储。"""
    _init_helpers()
    client = _get_httpx_client()
    payload = kwargs.pop("_payload", "")
    func = getattr(client, method.lower())
    resp = await func(url, **kwargs)

    if _evidence_store is not None:
        try:
            headers = kwargs.get("headers") or {}
            body = kwargs.get("content") or kwargs.get("data") or ""
            request_text = _build_request_text(method.upper(), url, headers, body if isinstance(body, str) else "")
            response_text = _build_response_text(resp, 800)
            _evidence_store.record(
                method=method.upper(),
                url=url,
                request_text=request_text,
                response_text=response_text,
                payload=payload,
                meta={"status_code": resp.status_code},
            )
        except Exception:
            pass
    return resp


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
Header always set Referrer-Policy "strict-origin-when-cross-origin" """,
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
        "broken_access_control": {
            "nginx": """# Nginx 对管理接口加 IP 白名单
location /admin {
    allow 10.0.0.0/8;
    deny all;
    # 同时建议后端执行二次会话校验
}""",
            "apache": """<Location "/admin">
    Require ip 10.0.0.0/8
</Location>""",
            "express": """// Express 路由级权限校验
const isAuthenticated = require('./auth');
app.use('/admin', isAuthenticated, require('./admin'));""",
            "flask": """# Flask 装饰器校验
from flask_login import login_required

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        abort(403)
    return render_template('admin.html')""",
            "spring_boot": """// Spring Security 方法级授权
@PreAuthorize("hasRole('ADMIN')")
@GetMapping("/admin/users")
public List<User> listUsers() { ... }""",
            "cloudflare": "# 使用 Cloudflare Access / Zero Trust 对 /admin 等路径实施身份校验。",
            "generic": "所有管理/敏感接口必须校验用户身份与权限；默认拒绝访问，明确授权放行。",
        },
        "idor": {
            "nginx": "# IDOR 属于应用层逻辑漏洞，Nginx 无法直接修复，建议后端实施授权校验。",
            "apache": "# IDOR 属于应用层逻辑漏洞，Apache 无法直接修复，建议后端实施授权校验。",
            "express": """// 资源访问前校验所有权
app.get('/api/orders/:id', async (req, res) => {
  const order = await Order.findById(req.params.id);
  if (!order || order.userId !== req.user.id) return res.sendStatus(403);
  res.json(order);
});""",
            "flask": """# 查询资源时加入用户 ID 过滤
@app.route('/order/<int:order_id>')
@login_required
def order(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    return jsonify(order.to_dict())""",
            "spring_boot": """// 方法级资源授权
@PostAuthorize("returnObject.owner == authentication.name")
@GetMapping("/orders/{id}")
public Order getOrder(@PathVariable Long id) { ... }""",
            "cloudflare": "# Cloudflare 无法识别业务 ID 归属，必须在应用层校验。",
            "generic": "使用间接引用映射（UUID/令牌）替代连续数字 ID；每次访问资源时校验当前用户是否为资源所有者。",
        },
        "ssrf": {
            "nginx": "# Nginx 可限制对内部地址的访问，但无法完全替代应用层校验。",
            "apache": "# Apache 可配合 mod_security 拦截部分内网请求，但无法完全替代应用层校验。",
            "express": """// Node.js SSRF 防护：校验与解析 URL
const { URL } = require('url');
function isPrivateIp(ip) { ... }

app.post('/fetch', (req, res) => {
  const u = new URL(req.body.url);
  if (isPrivateIp(u.hostname)) return res.status(400).send('Forbidden target');
  // 使用禁用重定向的受限 HTTP 客户端
});""",
            "flask": """# Python SSRF 防护
import socket
from urllib.parse import urlparse

def is_internal(host):
    try:
        ip = socket.getaddrinfo(host, None)[0][4][0]
        return ipaddress.ip_address(ip).is_private
    except Exception:
        return True

@app.route('/fetch')
def fetch():
    url = request.args.get('url')
    if is_internal(urlparse(url).hostname):
        abort(400)
    ...""",
            "spring_boot": """// Java SSRF 防护：禁止重定向到私有地址
HttpClient client = HttpClient.newBuilder()
    .followRedirects(Redirect.NEVER).build();""",
            "cloudflare": "# 使用 Cloudflare Gateway / WAF 规则限制出站目标。",
            "generic": "校验用户提供的 URL：禁用重定向、解析并拒绝内网/元数据地址、使用白名单域名、最小化请求权限。",
        },
        "file_upload": {
            "nginx": """# Nginx 禁止上传目录执行脚本
location /uploads {
    location ~* \\.(php|jsp|asp|aspx|sh|py)$ {
        deny all;
    }
}""",
            "apache": """<Directory /var/www/uploads>
    <FilesMatch "\\.(php|jsp|asp|aspx|sh|py)$">
        Require all denied
    </FilesMatch>
</Directory>""",
            "express": """// Express：校验 MIME 类型与扩展名，重命名文件
const multer = require('multer');
const upload = multer({
  fileFilter: (req, file, cb) => {
    if (!['image/jpeg','image/png'].includes(file.mimetype)) return cb(new Error('Invalid type'));
    cb(null, true);
  }
});""",
            "flask": """# Flask：限制扩展名与 MIME
from werkzeug.utils import secure_filename
ALLOWED = {'png', 'jpg', 'pdf'}

@app.route('/upload', methods=['POST'])
def upload():
    f = request.files['file']
    ext = secure_filename(f.filename).rsplit('.', 1)[-1].lower()
    if ext not in ALLOWED:
        abort(400)
    ...""",
            "spring_boot": """// Spring Boot：校验扩展名与 Magic Number
String ext = FilenameUtils.getExtension(file.getOriginalFilename());
if (!Set.of("png","jpg","pdf").contains(ext)) throw new IllegalArgumentException();""",
            "cloudflare": "# Cloudflare WAF 可拦截常见 WebShell 上传扩展名。",
            "generic": "限制允许的文件类型（白名单扩展名 + MIME + Magic Number）；上传目录禁止脚本执行；文件重命名并隔离存储。",
        },
        "logic_bypass": {
            "nginx": "# 业务逻辑绕过需在应用层修复，Nginx 仅能做速率限制等辅助防护。",
            "apache": "# 业务逻辑绕过需在应用层修复，Apache 仅能做速率限制等辅助防护。",
            "express": """// 服务端必须校验所有状态转换
app.post('/checkout', authenticate, async (req, res) => {
  const order = await Order.findById(req.body.orderId);
  if (order.status !== 'pending') return res.status(400).send('Invalid status');
  // 重新计算价格，不信任客户端传入
});""",
            "flask": """# 服务端重新校验业务状态与权限
@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    order = Order.query.get_or_404(request.json['order_id'])
    if order.user_id != current_user.id or order.status != 'pending':
        abort(403)
    ...""",
            "spring_boot": """// Spring Boot：服务端校验业务规则
@PostMapping("/checkout")
public ResponseEntity<?> checkout(@RequestBody CheckoutReq req, @AuthenticationPrincipal User user) {
    Order order = orderRepo.findById(req.getOrderId()).orElseThrow();
    if (!order.getUserId().equals(user.getId()) || !"pending".equals(order.getStatus())) {
        return ResponseEntity.status(403).build();
    }
    ...
}""",
            "cloudflare": "# Cloudflare 无法识别业务逻辑，建议应用层修复并配合 Bot Management 降低自动化攻击。",
            "generic": "所有业务关键状态转换在服务端重新校验；不信任客户端传入的价格、状态、权限字段；实施幂等与并发控制。",
        },
        "open_redirect": {
            "nginx": "# Nginx 不处理业务重定向，在应用层校验跳转目标。",
            "apache": "# Apache 不处理业务重定向，在应用层校验跳转目标。",
            "express": """// Express：白名单校验重定向 URL
const ALLOWED_REDIRECTS = ['/dashboard', '/profile', '/'];
app.get('/redirect', (req, res) => {
  const target = req.query.url;
  if (!ALLOWED_REDIRECTS.includes(target)) {
    return res.status(400).send('Invalid redirect');
  }
  res.redirect(target);
});""",
            "flask": """# Flask：白名单校验重定向 URL
from flask import redirect, abort, request
ALLOWED_REDIRECTS = {'/dashboard', '/profile', '/'}
@app.route('/redirect')
def safe_redirect():
    target = request.args.get('url', '/')
    if target not in ALLOWED_REDIRECTS:
        abort(400)
    return redirect(target)""",
            "spring_boot": """// Spring Boot：白名单校验
@GetMapping("/redirect")
public ResponseEntity<Void> redirect(@RequestParam String url) {
    if (!ALLOWED_REDIRECTS.contains(url)) {
        return ResponseEntity.badRequest().build();
    }
    return ResponseEntity.status(302).header("Location", url).build();
}""",
            "cloudflare": "# Cloudflare WAF 规则可拦截含外部 URL 的重定向参数。",
            "generic": "对用户提供的 URL 参数进行白名单校验；禁止重定向到外部域名；使用相对路径跳转。",
        },
        "xxe": {
            "nginx": "# Nginx 不解析 XML，在应用层禁用 DTD。",
            "apache": "# Apache 不解析 XML，在应用层禁用 DTD。",
            "express": """// Node.js：使用 libxmljs2 并禁用 DTD
const libxmljs2 = require('libxmljs2');
const doc = libxmljs2.parseXml(xml, {
  dtdload: false,
  dtdattr: false,
  noent: false,
});""",
            "flask": """# Python：使用 defusedxml 替代标准库
from defusedxml import ElementTree
tree = ElementTree.fromstring(xml_data)  # 自动禁用外部实体""",
            "spring_boot": """// Java：禁用 DTD 和外部实体
DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
dbf.setFeature("http://xml.org/sax/features/external-general-entities", false);
dbf.setFeature("http://xml.org/sax/features/external-parameter-entities", false);""",
            "cloudflare": "# Cloudflare WAF 可拦截包含 XML 实体定义的请求体。",
            "generic": "禁用 XML DTD 处理和外部实体；使用安全的 XML 解析库（如 defusedxml）；对 XML 输入进行白名单校验。",
        },
        "cmdi": {
            "nginx": "# Nginx 无法直接修复命令注入，建议在后端使用参数化 API 并配合 WAF 拦截常见注入字符。",
            "apache": "# Apache + ModSecurity 可拦截常见命令注入模式：SecRule ARGS '@rx [;&|`]' 'id:2000,deny,status:403'",
            "express": """// Node.js：使用 execFile 替代 exec，避免 shell 解析
const { execFile } = require('child_process');
execFile('ls', [userInput], (err, stdout) => { ... });""",
            "flask": """# Python：使用列表传参替代 shell=True
import subprocess
subprocess.run(['ls', user_input], shell=False, capture_output=True)""",
            "spring_boot": """// Java：使用 ProcessBuilder 并校验参数
List<String> cmd = Arrays.asList("ls", userInput);
new ProcessBuilder(cmd).start();""",
            "cloudflare": "# Cloudflare WAF 可拦截包含命令分隔符的请求参数。",
            "generic": "永远不要将用户输入拼接到系统命令字符串中；使用参数化 API（列表传参）并严格校验输入字符白名单。",
        },
        "traversal": {
            "nginx": "# Nginx 限制访问范围：location /files { alias /var/www/files; } 确保无法通过 ../ 跳出目录。",
            "apache": "# Apache 限制访问范围并校验路径。",
            "express": """// Node.js：校验路径在允许的基础目录内
const path = require('path');
const safePath = path.join(BASE_DIR, path.normalize(userInput));
if (!safePath.startsWith(BASE_DIR)) throw new Error('非法路径');""",
            "flask": """# Python：校验路径在允许的基础目录内
import os
base = '/var/www/files'
requested = os.path.realpath(os.path.join(base, user_input))
if not requested.startswith(base):
    abort(403)""",
            "spring_boot": """// Java：校验规范路径
Path base = Paths.get("/var/www/files").toRealPath();
Path target = base.resolve(userInput).toRealPath();
if (!target.startsWith(base)) throw new SecurityException();""",
            "cloudflare": "# Cloudflare WAF 可拦截包含 '../' 序列的请求参数。",
            "generic": "对用户输入的文件路径进行标准化处理（realpath / getCanonicalPath），限制在允许的基础目录内；禁止直接使用用户输入拼接文件路径。",
        },
        "deserialization": {
            "nginx": "# Nginx 无法直接修复反序列化漏洞，建议在应用层禁用原生反序列化。",
            "apache": "# Apache 无法直接修复反序列化漏洞，建议在应用层禁用原生反序列化。",
            "express": """// Node.js：使用 JSON 替代原生序列化
const data = JSON.parse(userInput);  // 安全
// 避免：eval(userInput) 或 require('vm').runInNewContext""",
            "flask": """# Python：使用 JSON 替代 pickle
import json
data = json.loads(user_input)  # 安全
# 避免：pickle.loads(user_input) 或 yaml.unsafe_load""",
            "spring_boot": """// Java：使用 JSON 替代 ObjectInputStream
ObjectMapper mapper = new ObjectMapper();
MyClass obj = mapper.readValue(json, MyClass.class);  // 安全
// 避免：new ObjectInputStream(in).readObject()""",
            "cloudflare": "# Cloudflare WAF 可拦截包含序列化对象特征的请求体。",
            "generic": "永远不要反序列化不可信数据；使用 JSON 等安全格式替代原生序列化；如需使用，实施签名验证和类型白名单。",
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
        "broken_access_control": [
            "https://cheatsheetseries.owasp.org/cheatsheets/Access_Control_Cheat_Sheet.html",
            "https://owasp.org/Top10/A01_2021-Broken_Access_Control/",
        ],
        "idor": [
            "https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html",
            "https://portswigger.net/web-security/access-control/idor",
        ],
        "ssrf": [
            "https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html",
            "https://portswigger.net/web-security/ssrf",
        ],
        "file_upload": [
            "https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html",
            "https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload",
        ],
        "logic_bypass": [
            "https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html",
            "https://owasp.org/Top10/A04_2021-Insecure_Design/",
        ],
        "open_redirect": [
            "https://owasp.org/www-community/attacks/Unvalidated_Redirects_and_Forwards_Cheat_Sheet",
            "https://portswigger.net/kb/issues/00500100/unvalidated-redirection",
        ],
        "xxe": [
            "https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html",
            "https://portswigger.net/web-security/xxe",
        ],
        "cmdi": [
            "https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html",
            "https://portswigger.net/web-security/os-command-injection",
        ],
        "traversal": [
            "https://cheatsheetseries.owasp.org/cheatsheets/Path_Traversal_Prevention_Cheat_Sheet.html",
            "https://portswigger.net/web-security/file-path-traversal",
        ],
        "deserialization": [
            "https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html",
            "https://owasp.org/www-project-top-ten/2017/A8_2017-Insecure_Deserialization",
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
        "broken_access_control": "A01:2021 - Broken Access Control",
        "idor": "A01:2021 - Broken Access Control",
        "ssrf": "A10:2021 - Server-Side Request Forgery",
        "file_upload": "A04:2021 - Insecure Design",
        "logic_bypass": "A04:2021 - Insecure Design / A07 - Authentication Failures",
        "open_redirect": "A01:2021 - Broken Access Control",
        "xxe": "A05:2021 - Security Misconfiguration",
        "cmdi": "A03:2021 - Injection",
        "traversal": "A01:2021 - Broken Access Control",
        "deserialization": "A08:2021 - Software and Data Integrity Failures",
    }
    return mapping.get(vuln_type, "A05:2021 - Security Misconfiguration")


def _cwe_id(vuln_type: str) -> str:
    """返回漏洞类型对应的首选 CWE 编号。"""
    mapping = {
        "sqli": "CWE-89",
        "xss": "CWE-79",
        "info_leak": "CWE-200",
        "csrf": "CWE-352",
        "sensitive_path": "CWE-548",
        "outdated_component": "CWE-1104",
        "header_missing": "CWE-693",
        "ssl": "CWE-319",
        "cors": "CWE-942",
        "cookie": "CWE-614",
        "broken_access_control": "CWE-284",
        "idor": "CWE-639",
        "ssrf": "CWE-918",
        "file_upload": "CWE-434",
        "logic_bypass": "CWE-287",
        "open_redirect": "CWE-601",
        "xxe": "CWE-611",
        "cmdi": "CWE-78",
        "traversal": "CWE-22",
        "deserialization": "CWE-502",
    }
    return mapping.get(vuln_type, "CWE-693")


def _cvss_vector(severity_score: int, vuln_type: str = "") -> str:
    """根据严重度评分与漏洞类型生成近似的 CVSS v3.1 向量字符串。

    这里采用简化映射，确保每条 finding 都有可读的 CVSS 向量；
    真实 SRC 提交建议由安全工程师根据实际利用条件微调。
    """
    # 攻击向量：默认网络可达
    av = "AV:N"
    # 攻击复杂度
    ac = "AC:L" if severity_score >= 6 else "AC:H"
    # 权限要求
    pr = "PR:N"
    if vuln_type in ("idor", "broken_access_control"):
        pr = "PR:L"
    if vuln_type in ("sqli", "xss", "ssrf"):
        pr = "PR:N"
    # 用户交互
    ui = "UI:N" if vuln_type in ("sqli", "ssrf", "idor", "info_leak", "sensitive_path", "outdated_component") else "UI:R"
    # 作用范围
    s = "S:U"
    # 机密性 / 完整性 / 可用性
    if severity_score >= 9:
        c, i, a = "C:H", "I:H", "A:H"
    elif severity_score >= 7:
        c, i = "C:H", "I:H"
        a = "A:L" if vuln_type in ("ssrf", "logic_bypass") else "A:N"
    elif severity_score >= 4:
        c, i, a = "C:L", "I:L", "A:N"
    else:
        c, i, a = "C:N", "I:N", "A:N"
    # 部分类型微调
    if vuln_type == "xss":
        c, i, a = "C:L", "I:L", "A:N"
    if vuln_type == "info_leak":
        c = "C:H" if severity_score >= 8 else "C:L"
        i, a = "I:N", "A:N"
    if vuln_type == "header_missing":
        c, i, a = "C:N", "I:N", "A:N"
    return f"CVSS:3.1/{av}/{ac}/{pr}/{ui}/{s}/{c}/{i}/{a}"


def _cvss_score_from_vector(vector: str) -> float:
    """从 CVSS v3.1 向量计算近似的 Base Score（简化版，用于排序）。"""
    # 简化公式：参考 CVSS v3.1 线性近似，保留一位小数
    scores = {
        "AV:N": 0.85, "AV:A": 0.62, "AV:L": 0.55, "AV:P": 0.2,
        "AC:L": 0.77, "AC:H": 0.44,
        "PR:N": 0.85, "PR:L": 0.62, "PR:H": 0.27,
        "UI:N": 0.85, "UI:R": 0.62,
        "S:U": 6.42, "S:C": 7.52,
        "C:H": 0.56, "C:L": 0.22, "C:N": 0.0,
        "I:H": 0.56, "I:L": 0.22, "I:N": 0.0,
        "A:H": 0.56, "A:L": 0.22, "A:N": 0.0,
    }
    parts = [p.strip() for p in vector.replace("CVSS:3.1/", "").split("/")]
    vals = {}
    for p in parts:
        if ":" in p:
            k, v = p.split(":", 1)
            vals[k + ":" + v] = scores.get(k + ":" + v, 0.0)
    iss = 1 - ((1 - vals.get("C:H", vals.get("C:L", 0))) *
               (1 - vals.get("I:H", vals.get("I:L", 0))) *
               (1 - vals.get("A:H", vals.get("A:L", 0))))
    impact = vals.get("S:U", 6.42) * iss
    exploitability = (8.22 * vals.get("AV:N", 0.85) *
                      vals.get("AC:L", 0.77) *
                      vals.get("PR:N", 0.85) *
                      vals.get("UI:N", 0.85))
    if impact <= 0:
        return 0.0
    base = min(impact + exploitability, 10)
    return round(base, 1)


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
    cvss_vector = _cvss_vector(severity_score, vuln_type)
    cvss_score = _cvss_score_from_vector(cvss_vector)
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
        "fix": fix_suggestion or _fix_code_template(vuln_type).get("generic", ""),
        "fix_suggestion": fix_suggestion or _fix_code_template(vuln_type).get("generic", ""),
        "fix_code": fix_code,
        "references": _references(vuln_type),
        "confidence": _confidence_text(confidence),
        "owasp_category": _owasp_category(vuln_type),
        "cwe_id": _cwe_id(vuln_type),
        "cvss_score": cvss_score,
        "cvss_vector": cvss_vector,
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
        resp = await _recorded_request("get", url, timeout=10.0, follow_redirects=True)
        baseline_body = _safe_read_body(resp).lower()
        baseline_time = resp.elapsed.total_seconds() if resp.elapsed else 0.0
    except Exception:
        pass

    for param in params[:6]:
        for payload in SQLI_PAYLOADS:
            test_url = _build_test_url(url, param, payload)
            try:
                start = time.time()
                resp = await _recorded_request("get", test_url, timeout=12.0, follow_redirects=True)
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
                resp = await _recorded_request("get", test_url, timeout=10.0, follow_redirects=True)
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
            resp = await _recorded_request("get", url, timeout=10.0, follow_redirects=True)
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
            resp = await _recorded_request("get", url, timeout=10.0, follow_redirects=True)
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
            resp = await _recorded_request("get", test_url, timeout=10.0, follow_redirects=True)
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
            resp = await _recorded_request("get", url, timeout=10.0, follow_redirects=True)
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


# ---------- SRC 扩展检测：越权、SSRF、IDOR、文件上传、逻辑绕过 ----------

ADMIN_PATHS: List[Tuple[str, str]] = [
    ("/admin", "管理后台入口"),
    ("/api/admin", "API 管理接口"),
    ("/manage", "管理后台"),
    ("/dashboard/admin", "仪表盘管理"),
    ("/console", "控制台"),
]

SSRF_PAYLOADS: List[Tuple[str, str, str]] = [
    ("http://127.0.0.1", "本地回环", "127.0.0.1"),
    ("http://169.254.169.254/latest/meta-data/", "AWS 元数据", "169.254.169.254"),
    ("http://metadata.google.internal/", "GCP 元数据", "metadata.google.internal"),
    ("http://192.168.1.1", "内网地址", "192.168.1.1"),
    ("file:///etc/passwd", "文件协议", "file://"),
]

IDOR_ID_PATTERNS: List[Tuple[str, re.Pattern]] = [
    ("id", re.compile(r"\b(id|user_id|order_id|pid|sid)=\d+", re.I)),
    ("page", re.compile(r"\b(page|offset|limit)=\d+", re.I)),
]

FILE_UPLOAD_FORM_PATTERNS: List[re.Pattern] = [
    re.compile(r"<input[^>]*type=[\"']file[\"']", re.I),
    re.compile(r"<form[^>]*enctype=[\"']multipart/form-data[\"']", re.I),
]

LOGIN_BYPASS_PATTERNS: Dict[str, re.Pattern] = {
    "no_csrf_login": re.compile(r"<form[^>]*>.*?<input[^>]*type=[\"']password[\"'].*?</form>", re.I | re.S),
    "json_login": re.compile(r"['\"]/api/(login|auth|signin)['\"]", re.I),
}


async def detect_broken_access_control_src(base_url: str) -> List[Dict[str, Any]]:
    """检测未授权访问管理接口（越权）。"""
    _init_helpers()
    client = _get_httpx_client()
    findings: List[Dict[str, Any]] = []

    parsed = urlparse(base_url)
    origin = f"{parsed.scheme}://{parsed.netloc}"

    for path, name in ADMIN_PATHS:
        test_url = origin + path
        try:
            resp = await _recorded_request("get", test_url, timeout=10.0, follow_redirects=False)
            # 200 且无登录特征，判定为未授权访问
            if resp.status_code != 200:
                continue
            body = _safe_read_body(resp).lower()
            login_markers = ["login", "sign in", "登录", "用户名", "password", "密码", "otp", "mfa", "sso"]
            if any(m in body for m in login_markers):
                continue
            findings.append(build_finding(
                vuln_type="broken_access_control",
                title=f"未授权访问：{name}",
                severity="high",
                severity_score=8,
                url=test_url,
                parameter="",
                location=f"路径 {path}",
                description=f"{name}（{path}）可直接访问，响应中未出现登录入口，疑似缺少身份认证。",
                evidence_request=_build_request_text("GET", test_url),
                evidence_response=_build_response_text(resp, 700),
                impact="攻击者可能无需登录即可访问管理功能，导致数据泄露、权限滥用或系统被接管。",
                reproduce_steps=[
                    f"在无痕模式下访问 {test_url}",
                    "确认未跳转至登录页",
                    "尝试访问下级功能路径验证权限边界",
                ],
                fix_suggestion="对管理接口实施强制认证与授权；默认拒绝匿名访问；结合 IP 白名单与 MFA。",
                confidence="medium",
            ))
        except Exception:
            continue
    return findings


async def detect_ssrf_src(url: str) -> List[Dict[str, Any]]:
    """检测 SSRF 入口点：URL 参数、表单 action 等可接受外部地址的位置。"""
    _init_helpers()
    client = _get_httpx_client()
    findings: List[Dict[str, Any]] = []

    parsed = urlparse(url)
    params = list(parse_qs(parsed.query, keep_blank_values=True).keys()) if parsed.query else []

    # 只检测名字像 URL 的参数
    url_like_params = [p for p in params if any(k in p.lower() for k in ("url", "link", "path", "src", "redirect", "callback", "uri", "site"))]

    for param in url_like_params[:4]:
        for payload, target_name, indicator in SSRF_PAYLOADS:
            test_url = _build_test_url(url, param, payload)
            try:
                resp = await _recorded_request("get", test_url, timeout=8.0, follow_redirects=False)
                body = _safe_read_body(resp).lower()
                elapsed = resp.elapsed.total_seconds() if resp.elapsed else 0.0

                # 判定：返回 200 且包含内网/元数据特征，或响应时间明显较快（说明本地可达）
                detected = False
                if resp.status_code == 200 and indicator in body:
                    detected = True
                elif resp.status_code in (301, 302, 307, 308) and indicator in (resp.headers.get("location") or "").lower():
                    detected = True
                elif elapsed < 0.5 and any(x in body for x in ["root:", "meta-data", "iam", "instance-id"]):
                    detected = True

                if detected:
                    findings.append(build_finding(
                        vuln_type="ssrf",
                        title=f"服务端请求伪造（参数 {param}）",
                        severity="critical" if "metadata" in target_name.lower() or "file://" in payload else "high",
                        severity_score=9 if "metadata" in target_name.lower() or "file://" in payload else 8,
                        url=test_url,
                        parameter=param,
                        location=f"URL 参数 {param}",
                        description=f"参数 '{param}' 接受外部地址并可能由服务端发起请求，测试 payload 命中 {target_name}，存在 SSRF 风险。",
                        evidence_request=_build_request_text("GET", test_url),
                        evidence_response=_build_response_text(resp, 600),
                        evidence_payload=payload,
                        impact="攻击者可利用服务端访问内网、云服务元数据接口或本地文件，导致敏感信息泄露甚至云环境接管。",
                        reproduce_steps=[
                            f"访问 {test_url}",
                            f"观察响应是否包含 {target_name} 内容或重定向到内部地址",
                            "尝试访问 169.254.169.254 等元数据地址进一步验证",
                        ],
                        fix_suggestion="严格校验用户输入的 URL；禁用重定向；解析并拒绝私有 IP、元数据域名与 file:// 协议；使用白名单。",
                        confidence="medium",
                    ))
                    break
            except Exception:
                continue
    return findings


async def detect_idor_src(url: str) -> List[Dict[str, Any]]:
    """检测不安全的直接对象引用（IDOR）：尝试替换连续数字 ID。"""
    _init_helpers()
    client = _get_httpx_client()
    findings: List[Dict[str, Any]] = []

    parsed = urlparse(url)
    qs = parse_qs(parsed.query, keep_blank_values=True)
    if not qs:
        return findings

    for param, values in qs.items():
        for value in values[:1]:
            if not re.fullmatch(r"\d+", value):
                continue
            original_id = int(value)
            test_ids = [original_id + 1, original_id - 1, original_id + 10]
            for test_id in test_ids:
                new_qs = {k: ([str(test_id)] if k == param else v) for k, v in qs.items()}
                test_url = urlunparse(parsed._replace(query=urlencode(new_qs, doseq=True)))
                try:
                    resp = await _recorded_request("get", test_url, timeout=10.0, follow_redirects=True)
                    if resp.status_code != 200:
                        continue
                    body = _safe_read_body(resp)
                    # 简单启发：响应长度相近且包含常见资源字段，认为存在 IDOR
                    if any(k in body.lower() for k in ["email", "phone", "username", "order", "user", "amount", "balance"]):
                        findings.append(build_finding(
                            vuln_type="idor",
                            title=f"不安全的直接对象引用（参数 {param}）",
                            severity="high",
                            severity_score=8,
                            url=test_url,
                            parameter=param,
                            location=f"URL 参数 {param}",
                            description=f"参数 '{param}' 为连续数字 ID，通过将其从 {original_id} 改为 {test_id} 仍可访问资源，说明未校验资源归属。",
                            evidence_request=_build_request_text("GET", test_url),
                            evidence_response=_build_response_text(resp, 700),
                            impact="攻击者可通过遍历 ID 访问其他用户的订单、资料、账单等敏感数据。",
                            reproduce_steps=[
                                f"访问原始链接：{url}",
                                f"将参数 {param} 依次替换为相邻 ID（如 {test_ids}）",
                                "观察是否返回其他用户数据",
                            ],
                            fix_suggestion="使用 UUID/间接引用；每次访问资源时校验当前用户是否为资源所有者；限制批量遍历。",
                            confidence="medium",
                        ))
                        return findings
                except Exception:
                    continue
    return findings


async def detect_file_upload_src(url: str, body: Optional[str] = None) -> List[Dict[str, Any]]:
    """检测页面中是否存在文件上传入口。"""
    _init_helpers()
    client = _get_httpx_client()
    findings: List[Dict[str, Any]] = []

    if body is None:
        try:
            resp = await _recorded_request("get", url, timeout=10.0, follow_redirects=True)
            body = _safe_read_body(resp)
        except Exception:
            body = ""

    for pattern in FILE_UPLOAD_FORM_PATTERNS:
        matches = list(pattern.finditer(body))
        if matches:
            first = matches[0].group(0)
            action_match = re.search(r'<form[^>]*action=["\']([^"\']*)["\']', body, re.I)
            action = action_match.group(1) if action_match else ""
            findings.append(build_finding(
                vuln_type="file_upload",
                title="发现文件上传入口",
                severity="medium",
                severity_score=6,
                url=url,
                parameter="",
                location=f"页面表单（action={action}）",
                description="页面中存在文件上传表单，若后端未对文件类型、内容、扩展名进行严格校验，可能被上传 WebShell 或恶意文件。",
                evidence_request=_build_request_text("GET", url),
                evidence_response=first[:500],
                impact="攻击者可能上传并执行服务器端脚本，导致服务器被控制、数据泄露或横向移动。",
                reproduce_steps=[
                    f"访问 {url}",
                    "定位文件上传表单",
                    "尝试上传带有脚本扩展名的文件（如 .php/.jsp/.aspx）",
                    "确认是否被拦截或可直接访问执行",
                ],
                fix_suggestion="使用白名单扩展名与 MIME 类型；校验文件 Magic Number；上传目录禁止脚本执行；重命名并隔离存储。",
                confidence="low",
            ))
            break
    return findings


async def detect_logic_bypass_src(url: str, headers: Dict[str, str], body: Optional[str] = None) -> List[Dict[str, Any]]:
    """检测登录/认证相关页面的逻辑绕过风险点。"""
    _init_helpers()
    client = _get_httpx_client()
    findings: List[Dict[str, Any]] = []

    if body is None:
        try:
            resp = await _recorded_request("get", url, timeout=10.0, follow_redirects=True)
            body = _safe_read_body(resp)
        except Exception:
            body = ""

    body_lower = body.lower()

    # 登录表单缺少 CSRF 与验证码
    if LOGIN_BYPASS_PATTERNS["no_csrf_login"].search(body):
        has_csrf = bool(re.search(r"csrf|xsrf|captcha|recaptcha", body_lower))
        if not has_csrf:
            findings.append(build_finding(
                vuln_type="logic_bypass",
                title="登录接口缺少 CSRF / 验证码保护",
                severity="medium",
                severity_score=5,
                url=url,
                parameter="",
                location="登录表单",
                description="登录表单未包含 CSRF Token 或验证码，攻击者可构造自动化的凭证喷洒、暴力破解或钓鱼登录请求。",
                evidence_request=_build_request_text("GET", url),
                evidence_response=LOGIN_BYPASS_PATTERNS["no_csrf_login"].search(body).group(0)[:500],
                impact="弱口令与自动化撞库攻击风险提升；钓鱼页面可跨站提交登录请求。",
                reproduce_steps=[
                    f"访问 {url}",
                    "查看登录表单源码",
                    "确认是否缺少 csrf_token / captcha",
                    "使用 Burp Intruder 测试登录接口对高频请求的拦截策略",
                ],
                fix_suggestion="登录接口添加 CSRF Token；实施速率限制、账户锁定与验证码（推荐行为验证码）；监控异常登录。",
                confidence="medium",
            ))

    # API 登录端点暴露
    if LOGIN_BYPASS_PATTERNS["json_login"].search(body):
        findings.append(build_finding(
            vuln_type="logic_bypass",
            title="前端暴露 API 登录端点",
            severity="low",
            severity_score=3,
            url=url,
            parameter="",
            location="前端 JS/HTML",
            description="前端代码中可直接定位到登录 API 端点，便于攻击者进行自动化认证测试。",
            evidence_request=_build_request_text("GET", url),
            evidence_response="匹配内容：" + LOGIN_BYPASS_PATTERNS["json_login"].search(body).group(0),
            impact="攻击者可绕过前端限制，直接调用登录 API 进行暴力破解。",
            reproduce_steps=[
                f"查看 {url} 前端源码",
                "搜索 /api/login、/api/auth 等端点",
                "使用脚本直接 POST 测试",
            ],
            fix_suggestion="服务端实施统一认证策略、速率限制、设备指纹与异常检测；不要依赖前端隐藏端点。",
            confidence="low",
        ))

    return findings


# ---------- 开放重定向检测 ----------

OPEN_REDIRECT_PARAM_NAMES = [
    "url", "redirect", "redirect_url", "redirect_to", "return_url",
    "returnurl", "next", "target", "to", "goto", "dest", "destination",
    "continue", "callback_url", "rurl", "u", "link",
]

OPEN_REDIRECT_PAYLOADS = [
    ("https://evil.example.com", "https://evil.example.com"),
    ("//evil.example.com", "//evil.example.com"),
    ("/\\evil.example.com", "evil.example.com"),
    ("https:evil.example.com", "evil.example.com"),
]


async def detect_open_redirect_src(url: str) -> List[Dict[str, Any]]:
    """检测开放重定向漏洞。

    通过在重定向相关参数中注入外部 URL，检查 HTTP 响应的 Location 头
    是否指向外部域名。
    """
    _init_helpers()
    client = _get_httpx_client()
    findings: List[Dict[str, Any]] = []

    parsed = urlparse(url)
    if not parsed.query:
        return findings

    params = [p.split("=")[0] for p in parsed.query.split("&") if "=" in p]
    redirect_params = [
        p for p in params
        if p.lower() in OPEN_REDIRECT_PARAM_NAMES
    ]

    for param in redirect_params[:3]:
        for payload, indicator in OPEN_REDIRECT_PAYLOADS:
            test_url = _build_test_url(url, param, payload)
            try:
                resp = await _recorded_request("get", test_url, timeout=8.0, follow_redirects=False)

                # 检查 3xx 重定向的 Location 头
                if resp.status_code in (301, 302, 303, 307, 308):
                    location = resp.headers.get("location", "")
                    if indicator in location:
                        findings.append(build_finding(
                            vuln_type="open_redirect",
                            title="开放重定向漏洞",
                            severity="medium",
                            severity_score=6,
                            url=test_url,
                            parameter=param,
                            location="URL 参数",
                            description=f"参数 '{param}' 存在开放重定向漏洞，可将用户重定向到外部恶意站点（{indicator}）。",
                            evidence_request=_build_request_text("GET", test_url),
                            evidence_response=f"HTTP {resp.status_code}\\nLocation: {location}",
                            impact="攻击者可利用此漏洞进行钓鱼攻击、恶意软件分发，或窃取用户凭证。",
                            reproduce_steps=[
                                f"访问: {test_url}",
                                f"观察浏览器被重定向到: {location}",
                            ],
                            fix_suggestion="对重定向参数进行白名单校验，仅允许站内相对路径。",
                            confidence="high",
                        ))
                        break  # 一个参数命中即可
            except Exception:
                pass

    return findings


# ---------- XXE 检测 ----------

XXE_CONTENT_TYPE_PATTERNS = [
    re.compile(r"application/xml", re.I),
    re.compile(r"text/xml", re.I),
    re.compile(r"application/atom\+xml", re.I),
    re.compile(r"application/rss\+xml", re.I),
]

XXE_BODY_INDICATORS = [
    re.compile(r"<\?xml", re.I),
    re.compile(r"<!DOCTYPE", re.I),
    re.compile(r"<\w+.*xmlns=", re.I),
]

XXE_PAYLOAD = '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>'

# ---------- 命令注入检测常量 ----------
CMDI_PAYLOADS: List[str] = [
    ";id",
    "|id",
    "`id`",
    "$(id)",
    ";whoami",
    "|whoami",
    ";cat /etc/passwd",
    "|cat /etc/passwd",
]

CMDI_INDICATORS: List[str] = [
    "uid=", "gid=", "groups=", "root:", "daemon:", "bin:",
    "www-data", "administrator", "nt authority",
]

# ---------- 路径遍历检测常量 ----------
TRAVERSAL_PAYLOADS: List[Tuple[str, str]] = [
    ("../../../etc/passwd", "linux_passwd"),
    ("....//....//....//etc/passwd", "linux_passwd_alt"),
    ("..%2f..%2f..%2fetc/passwd", "url_encoded"),
    ("..\\..\\..\\windows\\win.ini", "windows_ini"),
    ("....\\\\....\\\\....\\\\windows\\\\win.ini", "windows_ini_alt"),
]

TRAVERSAL_INDICATORS: Dict[str, List[str]] = {
    "linux_passwd": ["root:", "daemon:", "bin:", "/bin/bash", "/bin/sh"],
    "linux_passwd_alt": ["root:", "daemon:", "bin:", "/bin/bash", "/bin/sh"],
    "url_encoded": ["root:", "daemon:", "bin:", "/bin/bash", "/bin/sh"],
    "windows_ini": ["[fonts]", "[extensions]", "[mci extensions]", "[files]"],
    "windows_ini_alt": ["[fonts]", "[extensions]", "[mci extensions]", "[files]"],
}

# ---------- 不安全的反序列化检测常量 ----------
DESERIAL_ENDPOINTS: List[str] = [
    "/api/deserialize", "/deserialize", "/object", "/rpc",
    "/api/object", "/api/rpc", "/api/invoke", "/invoke",
    "/api/batch", "/batch", "/api/process", "/process",
]

DESERIAL_CONTENT_TYPES: List[str] = [
    "application/java-serialized-object",
    "application/x-java-serialized-object",
    "application/x-yaml",
    "application/octet-stream",
    "application/x-www-form-urlencoded",
]

DESERIAL_BODY_INDICATORS: List[re.Pattern] = [
    re.compile(r"rO0[AB]"),  # Java serialized object base64
    re.compile(r"aced00"),    # Java serialized object hex
    re.compile(r"!!python/object"),  # PyYAML unsafe
    re.compile(r"__reduce__"),       # Python pickle
    re.compile(r"O:\d+:\""),         # PHP serialized
]


async def detect_xxe_src(url: str, headers: Dict[str, str], body: str = "") -> List[Dict[str, Any]]:
    """检测 XML 外部实体（XXE）注入漏洞。

    检测策略：
    1. 检查响应头 Content-Type 是否为 XML 类型
    2. 检查响应体是否包含 XML 声明或 DOCTYPE
    3. 向疑似 XML 端点发送 XXE payload，检查是否泄露文件内容
    """
    _init_helpers()
    client = _get_httpx_client()
    findings: List[Dict[str, Any]] = []

    # 1. 静态检测：响应头或响应体暗示 XML 处理
    content_type = headers.get("content-type", headers.get("Content-Type", ""))
    is_xml_endpoint = any(p.search(content_type) for p in XXE_CONTENT_TYPE_PATTERNS) if content_type else False

    has_xml_body = False
    if body:
        has_xml_body = any(p.search(body[:2000]) for p in XXE_BODY_INDICATORS)

    if not is_xml_endpoint and not has_xml_body:
        # 检查 URL 是否暗示 XML 端点
        if not any(kw in url.lower() for kw in ["/api/xml", "/xml", "/rss", "/atom", "/feed", "/soap"]):
            return findings

    # 2. 动态检测：发送 XXE payload
    try:
        resp = await _recorded_request("post", 
            url,
            content=XXE_PAYLOAD,
            headers={"Content-Type": "application/xml"},
            timeout=10.0,
            follow_redirects=False,
        )

        if resp.status_code == 200:
            resp_body = resp.text.lower()
            # 检查是否泄露了 /etc/passwd 内容
            if "root:" in resp_body and "/bin/" in resp_body:
                findings.append(build_finding(
                    vuln_type="xxe",
                    title="XML 外部实体注入（XXE）",
                    severity="critical",
                    severity_score=10,
                    url=url,
                    parameter="XML Body",
                    location="HTTP 请求体",
                    description="目标端点在解析 XML 时未禁用外部实体，可读取服务器本地文件（已通过 file:// 协议读取 /etc/passwd）。",
                    evidence_request=f"POST {url}\\nContent-Type: application/xml\\n\\n{XXE_PAYLOAD}",
                    evidence_response=f"HTTP {resp.status_code}\\n{resp.text[:500]}",
                    impact="攻击者可读取任意文件、执行 SSRF、导致拒绝服务，甚至在某些配置下实现远程代码执行。",
                    reproduce_steps=[
                        f"POST {url}",
                        "Content-Type: application/xml",
                        f"Body: {XXE_PAYLOAD}",
                        "检查响应中是否包含文件内容",
                    ],
                    fix_suggestion="禁用 XML DTD 和外部实体处理；使用 defusedxml 等安全解析库。",
                    confidence="high",
                ))
            elif resp.status_code == 200 and ("error" not in resp_body or "parse" in resp_body):
                # 响应正常但未泄露文件，可能是端点接受 XML 但未泄露内容
                if is_xml_endpoint or has_xml_body:
                    findings.append(build_finding(
                        vuln_type="xxe",
                        title="潜在 XML 外部实体注入",
                        severity="medium",
                        severity_score=5,
                        url=url,
                        parameter="XML Body",
                        location="HTTP 请求体",
                        description="目标端点接受 XML 输入，但未验证是否禁用了外部实体处理。需人工确认是否可利用。",
                        evidence_request=f"POST {url}\\nContent-Type: application/xml\\n\\n{XXE_PAYLOAD}",
                        evidence_response=f"HTTP {resp.status_code} (响应长度: {len(resp.text)})",
                        impact="如果 XML 解析器未禁用外部实体，攻击者可能读取文件或执行 SSRF。",
                        reproduce_steps=[
                            "发送包含外部实体定义的 XML 请求",
                            "检查响应中是否泄露系统文件内容",
                        ],
                        fix_suggestion="确保 XML 解析器禁用 DTD 和外部实体；使用 defusedxml 库。",
                        confidence="medium",
                    ))
    except Exception:
        pass

    return findings


async def detect_command_injection_src(url: str) -> List[Dict[str, Any]]:
    """检测命令注入漏洞。

    检测策略：
    1. 提取 URL 参数
    2. 注入命令执行 payload（;id, |whoami 等）
    3. 检查响应中是否包含系统命令输出特征
    """
    _init_helpers()
    findings: List[Dict[str, Any]] = []

    parsed = urlparse(url)
    params = list(parse_qs(parsed.query, keep_blank_values=True).keys()) if parsed.query else []
    if not params:
        return findings

    for param in params[:4]:
        for payload in CMDI_PAYLOADS:
            test_url = _build_test_url(url, param, payload)
            try:
                resp = await _recorded_request("get", test_url, timeout=10.0, follow_redirects=True)
                body = _safe_read_body(resp)
                body_lower = body.lower()

                matched = False
                for indicator in CMDI_INDICATORS:
                    if indicator.lower() in body_lower:
                        matched = True
                        break

                if matched:
                    findings.append(build_finding(
                        vuln_type="cmdi",
                        title=f"命令注入漏洞（参数 {param}）",
                        severity="critical",
                        severity_score=10,
                        url=test_url,
                        parameter=param,
                        location=f"URL 参数 {param}",
                        description=f"参数 '{param}' 存在命令注入漏洞，服务器执行了用户输入中的系统命令并返回了命令输出。",
                        evidence_request=_build_request_text("GET", test_url),
                        evidence_response=_build_response_text(resp, 600),
                        evidence_payload=payload,
                        impact="攻击者可利用该漏洞执行任意系统命令，完全控制服务器、窃取数据或植入后门。",
                        reproduce_steps=[
                            f"访问目标页面：{url}",
                            f"在参数 {param} 中注入命令：{payload}",
                            "提交请求并观察响应是否包含系统命令输出（如 uid、whoami 结果）",
                        ],
                        fix_suggestion="永远不要将用户输入拼接到系统命令中；使用参数化 API（如 Python subprocess.run(list, shell=False)）。",
                        confidence="high",
                    ))
                    break
            except Exception:
                pass
        if findings:
            break

    return findings


async def detect_path_traversal_src(url: str) -> List[Dict[str, Any]]:
    """检测路径遍历/目录穿越漏洞。

    检测策略：
    1. 提取 URL 参数
    2. 注入路径遍历 payload（../../../etc/passwd 等）
    3. 检查响应中是否包含系统文件内容特征
    """
    _init_helpers()
    findings: List[Dict[str, Any]] = []

    parsed = urlparse(url)
    params = list(parse_qs(parsed.query, keep_blank_values=True).keys()) if parsed.query else []
    if not params:
        return findings

    for param in params[:4]:
        for payload, tag in TRAVERSAL_PAYLOADS:
            test_url = _build_test_url(url, param, payload)
            try:
                resp = await _recorded_request("get", test_url, timeout=10.0, follow_redirects=True)
                body = _safe_read_body(resp)
                body_lower = body.lower()

                indicators = TRAVERSAL_INDICATORS.get(tag, [])
                matched = False
                for indicator in indicators:
                    if indicator.lower() in body_lower:
                        matched = True
                        break

                if matched:
                    findings.append(build_finding(
                        vuln_type="traversal",
                        title=f"路径遍历漏洞（参数 {param}）",
                        severity="high",
                        severity_score=8,
                        url=test_url,
                        parameter=param,
                        location=f"URL 参数 {param}",
                        description=f"参数 '{param}' 存在路径遍历漏洞，攻击者可通过构造 '../' 序列读取服务器上的任意文件。",
                        evidence_request=_build_request_text("GET", test_url),
                        evidence_response=_build_response_text(resp, 600),
                        evidence_payload=payload,
                        impact="攻击者可读取系统配置文件、源代码、数据库凭证，甚至通过日志包含等方式实现远程代码执行。",
                        reproduce_steps=[
                            f"访问目标页面：{url}",
                            f"在参数 {param} 中注入路径遍历 payload：{payload}",
                            "提交请求并观察响应是否包含系统文件内容",
                        ],
                        fix_suggestion="对用户输入的文件路径进行标准化处理（如 os.path.realpath），限制在允许的基础目录内；禁止直接使用用户输入拼接文件路径。",
                        confidence="high",
                    ))
                    break
            except Exception:
                pass
        if findings:
            break

    return findings


async def detect_deserialization_src(url: str, headers: Dict[str, str], body: str = "") -> List[Dict[str, Any]]:
    """检测不安全的反序列化漏洞。

    检测策略：
    1. 检查 URL 路径或 Content-Type 是否暗示反序列化端点
    2. 检查响应体中是否包含序列化对象特征
    3. 向疑似端点发送序列化 payload，观察异常响应
    """
    _init_helpers()
    findings: List[Dict[str, Any]] = []

    parsed = urlparse(url)
    path_lower = parsed.path.lower()

    # 1. 端点识别
    is_deserial_endpoint = any(path_lower.endswith(ep) or ep in path_lower for ep in DESERIAL_ENDPOINTS)

    content_type = headers.get("content-type", headers.get("Content-Type", "")).lower()
    is_deserial_content_type = any(ct in content_type for ct in DESERIAL_CONTENT_TYPES)

    has_deserial_body = False
    if body:
        for pattern in DESERIAL_BODY_INDICATORS:
            if pattern.search(body[:2000]):
                has_deserial_body = True
                break

    if not is_deserial_endpoint and not is_deserial_content_type and not has_deserial_body:
        return findings

    # 2. 动态检测：发送常见反序列化 payload
    deserial_payloads = [
        ("rO0ABXNyABFqYXZhLnV0aWwuSGFzaE1hcAUH2sHDFmDRwAIAA0kACmxvYWRGYWN0b3JJAAl0aHJlc2hvbGR4cA==", "java"),
        ("O:8:\"stdClass\":0:{}", "php"),
        ("!!python/object:__main__.Test {}", "python"),
    ]

    for payload, ptype in deserial_payloads:
        try:
            resp = await _recorded_request(
                "post",
                url,
                content=payload,
                headers={"Content-Type": "application/octet-stream"},
                timeout=10.0,
                follow_redirects=False,
            )

            body_text = _safe_read_body(resp)
            body_lower = body_text.lower()

            # 检查是否触发反序列化异常
            error_indicators = [
                "serialization", "deserialize", "objectinputstream",
                "invalidclassexception", "classnotfound", "unpickling",
                "yaml.constructor", "php unserialize",
            ]
            has_error = any(ind in body_lower for ind in error_indicators)

            if has_error or resp.status_code in (500, 502, 503):
                findings.append(build_finding(
                    vuln_type="deserialization",
                    title="不安全的反序列化漏洞",
                    severity="critical",
                    severity_score=10,
                    url=url,
                    parameter="HTTP Body",
                    location="反序列化端点",
                    description=f"目标端点 ({parsed.path}) 接受用户输入并进行反序列化操作，检测到类型为 {ptype} 的反序列化异常响应。",
                    evidence_request=f"POST {url}\nContent-Type: application/octet-stream\n\n{payload[:80]}...",
                    evidence_response=_build_response_text(resp, 600),
                    evidence_payload=payload,
                    impact="攻击者可构造恶意序列化对象实现远程代码执行（RCE），完全控制服务器。",
                    reproduce_steps=[
                        f"向 {url} 发送包含 {ptype} 序列化对象的请求",
                        "观察响应是否包含反序列化异常或服务器错误",
                        "使用 ysoserial、PHPGGC 等工具生成利用链进一步验证",
                    ],
                    fix_suggestion="永远不要反序列化不可信数据；使用 JSON 等安全格式替代原生序列化；如需使用，实施签名验证和类型白名单。",
                    confidence="high" if has_error else "medium",
                ))
                break
        except Exception:
            pass

    # 3. 静态检测：如果端点或内容类型匹配但动态检测未触发，报告潜在风险
    if not findings and (is_deserial_endpoint or is_deserial_content_type):
        findings.append(build_finding(
            vuln_type="deserialization",
            title="潜在不安全的反序列化端点",
            severity="medium",
            severity_score=5,
            url=url,
            parameter="",
            location=parsed.path,
            description=f"目标端点 ({parsed.path}) 的 URL 路径或 Content-Type 暗示其可能执行反序列化操作，需人工确认安全性。",
            evidence_request=_build_request_text("GET", url),
            evidence_response="",
            impact="如果该端点确实执行反序列化且未做安全限制，攻击者可能通过恶意对象实现远程代码执行。",
            reproduce_steps=[
                f"确认端点 {parsed.path} 是否接受序列化对象输入",
                "尝试发送不同格式的序列化 payload 观察响应",
            ],
            fix_suggestion="对所有反序列化操作实施严格的类型白名单和签名验证；优先使用 JSON 等安全数据交换格式。",
            confidence="low",
        ))

    return findings


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
    bac_task = detect_broken_access_control_src(url)
    ssrf_task = detect_ssrf_src(url)
    idor_task = detect_idor_src(url)
    upload_task = detect_file_upload_src(url)
    logic_task = detect_logic_bypass_src(url, headers)
    open_redirect_task = detect_open_redirect_src(url)
    xxe_task = detect_xxe_src(url, headers, "")
    cmdi_task = detect_command_injection_src(url)
    traversal_task = detect_path_traversal_src(url)
    deserial_task = detect_deserialization_src(url, headers, "")

    tasks = [
        sqli_task, xss_task, info_leak_task, csrf_task, paths_task, components_task,
        bac_task, ssrf_task, idor_task, upload_task, logic_task, open_redirect_task, xxe_task,
        cmdi_task, traversal_task, deserial_task,
    ]
    if deep:
        # 深度模式：暂不增加额外任务，保留扩展位
        pass

    results = await asyncio.gather(*tasks, return_exceptions=True)
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
