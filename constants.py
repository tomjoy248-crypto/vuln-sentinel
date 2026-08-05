"""漏洞哨兵 11-S - 常量定义模块"""

import ipaddress
import os
import re

# ---------- URL / Network 限制 ----------

_MAX_USERNAME_LEN = 32
_MAX_URL_LEN = 2048
_MAX_EMAIL_LEN = 128
_MAX_PASSWORD_LEN = 128
_ALLOWED_USERNAME_RE = re.compile(r"^[a-zA-Z0-9_\-\u4e00-\u9fa5]+$")

# ---------- SSRF 防护 ----------

BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
]

BLOCKED_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0", "::1", "169.254.169.254"}  # nosec B104

ALLOWED_INTERNAL_HOSTS = {
    h.strip().lower()
    for h in os.environ.get("ALLOWED_INTERNAL_HOSTS", "").split(",")
    if h.strip()
}
if os.environ.get("ALLOW_LOCALHOST", "").lower() in ("1", "true", "yes"):
    ALLOWED_INTERNAL_HOSTS.add("localhost")
    ALLOWED_INTERNAL_HOSTS.add("127.0.0.1")

# ---------- 评分常量 ----------

SEVERITY_SCORE = {"critical": 25, "high": 15, "medium": 8, "low": 3}
SEVERITY_ZH = {
    "critical": "高风险",
    "high": "高风险",
    "medium": "中风险",
    "low": "低风险",
}

SCORE_DEDUCTION = {
    "exposed_path": 15,
    "high_config_missing": 8,
    "normal_config_missing": 3,
    "info_leak": 1,
    "suspect": 0,
}

# ---------- 安全头配置 ----------

SECURITY_HEADERS: dict[str, dict[str, str]] = {
    "strict-transport-security": {
        "name": "HSTS",
        "category": "传输安全",
        "severity": "high",
        "description": "强制浏览器只通过 HTTPS 访问",
        "fix": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
    },
    "content-security-policy": {
        "name": "CSP",
        "category": "XSS 防护",
        "severity": "high",
        "description": "限制页面可加载的资源来源",
        "fix": "add_header Content-Security-Policy \"default-src 'self'\" always;",
    },
    "x-frame-options": {
        "name": "X-Frame-Options",
        "category": "点击劫持",
        "severity": "medium",
        "description": "防止页面被嵌入 iframe",
        "fix": 'add_header X-Frame-Options "DENY" always;',
    },
    "x-content-type-options": {
        "name": "X-Content-Type-Options",
        "category": "MIME 嗅探",
        "severity": "medium",
        "description": "禁止浏览器猜测 MIME 类型",
        "fix": 'add_header X-Content-Type-Options "nosniff" always;',
    },
    "referrer-policy": {
        "name": "Referrer-Policy",
        "category": "隐私",
        "severity": "low",
        "description": "控制 Referer 头发送策略",
        "fix": 'add_header Referrer-Policy "strict-origin-when-cross-origin" always;',
    },
    "permissions-policy": {
        "name": "Permissions-Policy",
        "category": "隐私",
        "severity": "low",
        "description": "控制浏览器 API 权限",
        "fix": 'add_header Permissions-Policy "camera=(), microphone=()" always;',
    },
    "cache-control": {
        "name": "Cache-Control",
        "category": "缓存安全",
        "severity": "low",
        "description": "敏感页面应禁止缓存以防止信息泄露",
        "fix": 'add_header Cache-Control "no-store, no-cache, must-revalidate" always;',
    },
    "x-dns-prefetch-control": {
        "name": "X-DNS-Prefetch-Control",
        "category": "隐私",
        "severity": "low",
        "description": "控制浏览器是否自动 DNS 预取，防止隐私泄露",
        "fix": 'add_header X-DNS-Prefetch-Control "off" always;',
    },
}

# ---------- WAF 签名 ----------

WAF_SIGNATURES: dict[str, list[str]] = {
    "cloudflare": ["CF-RAY", "__cfduid", "cf-browser-verification", "cloudflare"],
    "aliyun": ["X-Alibaba-WAF", "X-Alibaba-WAF-Action", "aliyun"],
    "aws": ["X-AMZ-CF-ID", "X-Cache", "awselb", "aws"],
    "baidu": ["X-Bd-WAF", "X-Bd-Id", "bfe"],
    "qcloud": ["X-Qcloud-Edge", "X-Tencent-Ua", "qcloud"],
    "imperva": ["X-Iinfo", "incap_ses", "imperva"],
    "akamai": ["X-Akamai-Request-BC", "Akamai-Origin-Hop", "akamai"],
}

# ---------- 敏感路径 ----------

SENSITIVE_PATHS: list[str] = [
    "/.env",
    "/.git/config",
    "/.svn/entries",
    "/.htaccess",
    "/admin",
    "/phpmyadmin",
    "/.DS_Store",
    "/config.php",
    "/wp-config.php",
    "/.env.local",
    "/backup.sql",
    "/dump.sql",
    "/.bak",
    "/config/database.yml",
    "/.git/HEAD",
    "/.git/COMMIT_EDITMSG",
    "/debug.log",
    "/error.log",
    "/phpinfo.php",
    "/server-status",
    "/server-info",
    "/actuator",
    "/actuator/env",
    "/actuator/health",
]

PATH_WHITELIST: list[str] = [
    "/sitemap.xml",
    "/robots.txt",
    "/api",
    "/swagger",
    "/login",
    "/health",
    "/favicon.ico",
    "/",
]

INFO_PATHS: list[str] = ["/robots.txt"]

# ---------- 攻击载荷 ----------

XSS_PAYLOADS: list[str] = [
    '<script>alert("XSS")</script>',
    '"><img src=x onerror=alert(1)>',
    "'-alert(1)-'",
    "{{7*7}}",
    "<svg onload=alert(1)>",
    "javascript:alert(1)",
]

SQLI_PAYLOADS: list[str] = [
    "' OR 1=1--",
    "1' OR '1'='1",
    "admin'--",
    "' UNION SELECT NULL--",
    "1; DROP TABLE users--",
    "' OR 1=1 /*",
]

SQLI_PAYLOADS_V2: list[str] = [
    "' OR '1'='1",
    "'; DROP TABLE users; --",
    "' UNION SELECT null,null--",
    "' OR 1=1--",
    "1' OR '1'='1",
    "admin'--",
]

XSS_PAYLOADS_V2: list[str] = [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert(1)>",
    '" onmouseover=alert(1) "',
    '"><svg onload=alert(1)>',
    "javascript:alert(1)",
]

CMDI_PAYLOADS: list[str] = [
    "; cat /etc/passwd",
    "| whoami",
    "`id`",
    "$(id)",
    "&& echo vuln_sentinel_cmdi",
]

TRAVERSAL_PAYLOADS: list[str] = [
    "../../../etc/passwd",
    "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
    "....//....//....//etc/passwd",
    "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
]

# ---------- 检测签名 ----------

SQLI_ERROR_PATTERNS: list[str] = [
    "sql syntax",
    "mysql",
    "postgresql",
    "sqlite",
    "oracle",
    "sql error",
    "unclosed quotation",
    "query failed",
    "warning: mysql",
    "syntax error",
    "sqlstate",
    "odbc",
    "microsoft sql",
    "mariadb",
    "pg_query",
    "pg_exec",
    "you have an error in your sql",
    "quoted string not properly terminated",
    "unterminated string",
    "pg_sql",
    "sqlite3",
]

PASSWD_SIGNATURES: list[str] = ["root:x:0:0", "bin:x:1:1", "daemon:x:2:2"]
WINDOWS_HOSTS_SIGNATURES: list[str] = [
    "# Copyright (c) 1993-2000 Microsoft Corp",
    "localhost name resolution",
]
CMD_EXEC_SIGNATURES: list[str] = [
    "uid=",
    "gid=",
    "groups=",
    "root:",
    "www-data",
    "vuln_sentinel_cmdi",
]
DESER_SIGNATURES: list[str] = ["rO0AB", "H4sIAAAAAAAA", "aced", "aced00", "ro0"]
