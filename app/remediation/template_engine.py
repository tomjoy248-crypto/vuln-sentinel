"""修复模板引擎。

按漏洞类型 x 服务器类型组织修复模板，支持变量注入与条件渲染。
替代 main.py 中 generate_fixes() 的硬编码 if-elif 链。
"""

from __future__ import annotations

from typing import Any


class FixTemplate:
    """单个修复模板。"""

    def __init__(
        self,
        vuln_type: str,
        platform: str,
        code: str,
        description: str = "",
        risk_note: str = "",
        prerequisites: list[str] | None = None,
        verification_steps: list[str] | None = None,
    ) -> None:
        self.vuln_type = vuln_type
        self.platform = platform
        self.code = code
        self.description = description
        self.risk_note = risk_note
        self.prerequisites = prerequisites or []
        self.verification_steps = verification_steps or []

    def render(self, ctx: dict[str, Any]) -> str:
        """使用上下文变量渲染模板代码。"""
        text = self.code
        for key, val in ctx.items():
            placeholder = f"{{{key}}}"
            text = text.replace(placeholder, str(val))
        return text


# ---------- 模板库 ----------
# 按 vuln_type -> platform -> FixTemplate 组织

_TEMPLATE_LIBRARY: dict[str, dict[str, FixTemplate]] = {}


def _register(tmpl: FixTemplate) -> None:
    _TEMPLATE_LIBRARY.setdefault(tmpl.vuln_type, {})[tmpl.platform] = tmpl


# --- Header Security ---
_register(
    FixTemplate(
        vuln_type="header_missing",
        platform="nginx",
        code='add_header {header_name} "{header_value}" always;',
        description="在 Nginx 配置中增加缺失的安全响应头",
        risk_note="上线前请在测试环境验证，CSP 策略过严可能导致前端资源加载失败",
        prerequisites=["拥有 Nginx 配置文件写权限", "可执行 nginx -s reload"],
        verification_steps=["curl -I {host} | grep -i {header_name}"],
    )
)
_register(
    FixTemplate(
        vuln_type="header_missing",
        platform="apache",
        code='Header set {header_name} "{header_value}"',
        description="在 Apache 配置中增加缺失的安全响应头",
    )
)
_register(
    FixTemplate(
        vuln_type="header_missing",
        platform="flask",
        code=(
            "@app.after_request\n"
            "def add_security_headers(resp):\n"
            "    resp.headers['{header_name}'] = '{header_value}'\n"
            "    return resp"
        ),
        description="在 Flask 应用中使用 after_request 钩子添加响应头",
    )
)
_register(
    FixTemplate(
        vuln_type="header_missing",
        platform="express",
        code="app.use(helmet({ {header_name}: '{header_value}' }));",
        description="在 Express 应用中使用 helmet 中间件添加响应头",
    )
)
_register(
    FixTemplate(
        vuln_type="header_missing",
        platform="spring_boot",
        code=(
            "@Bean\n"
            "public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {\n"
            "    http.headers().{header_method}();\n"
            "    return http.build();\n"
            "}"
        ),
        description="在 Spring Boot Security 配置中添加响应头",
    )
)
_register(
    FixTemplate(
        vuln_type="header_missing",
        platform="cloudflare",
        code=(
            "# Cloudflare: Rules > Transform Rules > Modify Response Header\n"
            "# Header: {header_name}\n"
            "# Value: {header_value}"
        ),
        description="通过 Cloudflare Transform Rules 添加响应头",
    )
)

# --- HTTPS / SSL ---
_register(
    FixTemplate(
        vuln_type="ssl",
        platform="nginx",
        code=(
            "server {{\n"
            "    listen 80;\n"
            "    server_name {host};\n"
            "    return 301 https://$host$request_uri;\n"
            "}}"
        ),
        description="Nginx 强制 HTTPS 重定向",
    )
)
_register(
    FixTemplate(
        vuln_type="ssl",
        platform="apache",
        code=(
            "<VirtualHost *:80>\n"
            "    ServerName {host}\n"
            "    Redirect permanent / https://$host/\n"
            "</VirtualHost>"
        ),
        description="Apache 强制 HTTPS 重定向",
    )
)
_register(
    FixTemplate(
        vuln_type="ssl",
        platform="cloudflare",
        code="# Cloudflare: SSL/TLS > Full (Strict)",
        description="在 Cloudflare 面板开启 Full (Strict) SSL 模式",
    )
)
_register(
    FixTemplate(
        vuln_type="weak_ssl",
        platform="nginx",
        code=(
            "ssl_protocols TLSv1.2 TLSv1.3;\n"
            "ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;\n"
            "ssl_prefer_server_ciphers on;"
        ),
        description="禁用弱 TLS 版本和弱加密套件",
    )
)
_register(
    FixTemplate(
        vuln_type="weak_ssl",
        platform="apache",
        code=(
            "SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1\n"
            "SSLCipherSuite ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256\n"
            "SSLHonorCipherOrder on"
        ),
        description="Apache 禁用弱 TLS 版本",
    )
)

# --- SQL Injection ---
_register(
    FixTemplate(
        vuln_type="sqli",
        platform="flask",
        code=(
            "# 使用参数化查询\n"
            "cursor.execute('SELECT * FROM users WHERE id=%s', (user_id,))"
        ),
        description="将字符串拼接 SQL 改为参数化查询",
        risk_note="确保所有查询路径都使用参数化，避免遗漏",
    )
)
_register(
    FixTemplate(
        vuln_type="sqli",
        platform="express",
        code="// db.query('SELECT * FROM users WHERE id=$1', [userId])",
        description="使用预处理语句替代字符串拼接",
    )
)
_register(
    FixTemplate(
        vuln_type="sqli",
        platform="spring_boot",
        code="# Java: JdbcTemplate.query('SELECT * FROM users WHERE id=?', new Object[]{userId})",
        description="Spring Boot 使用 JdbcTemplate 参数化查询",
    )
)
_register(
    FixTemplate(
        vuln_type="sqli",
        platform="nginx",
        code='# ModSecurity: SecRule ARGS "(OR|UNION)" "deny,status:403"',
        description="Nginx + ModSecurity WAF 规则拦截 SQLi 特征",
    )
)
_register(
    FixTemplate(
        vuln_type="sqli",
        platform="cloudflare",
        code="# Cloudflare: WAF > SQL Injection Rules > Enable",
        description="开启 Cloudflare SQL 注入防护规则",
    )
)

# --- XSS ---
_register(
    FixTemplate(
        vuln_type="xss",
        platform="flask",
        code=(
            "# 使用 Jinja2 自动转义\n"
            "{{ user_input | e }}\n"
            "# 或 Markup.escape(user_input)"
        ),
        description="对用户输入进行 HTML 实体编码",
        risk_note="上线前请在测试环境验证，CSP 策略过严可能导致前端资源加载失败",
    )
)
_register(
    FixTemplate(
        vuln_type="xss",
        platform="express",
        code="// DOMPurify.sanitize(userInput)",
        description="使用 DOMPurify 清理用户输入",
    )
)
_register(
    FixTemplate(
        vuln_type="xss",
        platform="nginx",
        code="add_header Content-Security-Policy \"default-src 'self'; script-src 'self'\" always;",
        description="通过 CSP 限制脚本执行来源",
    )
)
_register(
    FixTemplate(
        vuln_type="xss",
        platform="cloudflare",
        code="# Cloudflare: WAF > XSS Rules > Enable",
        description="开启 Cloudflare XSS 防护规则",
    )
)

# --- SSRF ---
_register(
    FixTemplate(
        vuln_type="ssrf",
        platform="flask",
        code=(
            "# 使用白名单 + ipaddress 校验\n"
            "import ipaddress\n"
            "addr = ipaddress.ip_address(hostname)\n"
            "if addr.is_private or addr.is_loopback:\n"
            "    raise ValueError('禁止访问内网地址')"
        ),
        description="拦截对内网/回环地址的请求",
    )
)
_register(
    FixTemplate(
        vuln_type="ssrf",
        platform="express",
        code=(
            "// 使用代理 + 禁止请求 169.254.169.254\n"
            "const blocked = ['169.254.169.254', '127.0.0.1', 'localhost'];"
        ),
        description="Express 层拦截敏感内网地址",
    )
)

# --- CSRF ---
_register(
    FixTemplate(
        vuln_type="csrf",
        platform="flask",
        code=(
            "# Flask-WTF 自动处理 CSRF Token\n"
            "from flask_wtf.csrf import CSRFProtect\n"
            "csrf = CSRFProtect(app)"
        ),
        description="启用 Flask-WTF CSRF 保护",
    )
)
_register(
    FixTemplate(
        vuln_type="csrf",
        platform="express",
        code="// csurf 中间件\napp.use(csurf({ cookie: true }));",
        description="Express 使用 csurf 中间件",
    )
)

# --- Open Redirect ---
_register(
    FixTemplate(
        vuln_type="open_redirect",
        platform="flask",
        code=(
            "# 白名单校验跳转目标\n"
            "ALLOWED_HOSTS = ['example.com', 'www.example.com']\n"
            "from urllib.parse import urlparse\n"
            "if urlparse(url).hostname not in ALLOWED_HOSTS:\n"
            "    abort(403)"
        ),
        description="对跳转目标 URL 进行白名单校验",
    )
)

# --- Info Leak ---
_register(
    FixTemplate(
        vuln_type="info_leak",
        platform="nginx",
        code="server_tokens off;",
        description="隐藏 Nginx 版本号",
    )
)
_register(
    FixTemplate(
        vuln_type="info_leak",
        platform="apache",
        code="ServerTokens Prod\nServerSignature Off",
        description="隐藏 Apache 版本号和签名",
    )
)
_register(
    FixTemplate(
        vuln_type="info_leak",
        platform="express",
        code="app.disable('x-powered-by');",
        description="隐藏 Express 框架标识",
    )
)

# --- Sensitive Path ---
_register(
    FixTemplate(
        vuln_type="sensitive_path",
        platform="nginx",
        code=(
            "location ~ /(\\.env|\\.git|\\.svn|backup\\.sql|\\.bak) {\n"
            "    deny all;\n"
            "    return 403;\n"
            "}"
        ),
        description="禁止访问敏感路径",
    )
)
_register(
    FixTemplate(
        vuln_type="sensitive_path",
        platform="apache",
        code=(
            '<LocationMatch "/(\\.env|\\.git|\\.svn|backup\\.sql|\\.bak)">\n'
            "    Require all denied\n"
            "</LocationMatch>"
        ),
        description="Apache 禁止访问敏感路径",
    )
)

# --- File Upload ---
_register(
    FixTemplate(
        vuln_type="file_upload",
        platform="flask",
        code=(
            "# 限制文件类型 + 重命名 + 隔离存储\n"
            "ALLOWED = {'png', 'jpg', 'pdf'}\n"
            "ext = secure_filename(file.filename).rsplit('.', 1)[-1].lower()\n"
            "if ext not in ALLOWED:\n"
            "    abort(400)\n"
            "uuid_name = f'{uuid.uuid4()}.{ext}'\n"
            "file.save(os.path.join('/var/uploads', uuid_name))"
        ),
        description="限制上传文件扩展名、重命名并隔离存储",
    )
)

# --- IDOR ---
_register(
    FixTemplate(
        vuln_type="idor",
        platform="flask",
        code=(
            "# 每次访问资源时校验所有权\n"
            "if resource.owner_id != current_user.id:\n"
            "    abort(403)"
        ),
        description="在资源访问点增加所有权校验",
    )
)

# --- Broken Access Control ---
_register(
    FixTemplate(
        vuln_type="broken_access_control",
        platform="flask",
        code=(
            "# 使用装饰器统一鉴权\n@require_role('admin')\ndef admin_panel():\n    ..."
        ),
        description="统一使用装饰器进行角色鉴权",
    )
)

# --- Command Injection ---
_register(
    FixTemplate(
        vuln_type="cmdi",
        platform="flask",
        code="# subprocess.run(['ls', user_input], shell=False)",
        description="使用列表传参替代 shell=True",
    )
)
_register(
    FixTemplate(
        vuln_type="cmdi",
        platform="express",
        code="// child_process.execFile('ls', [arg], callback)",
        description="使用 execFile 替代 exec，避免 shell 注入",
    )
)

# --- Path Traversal ---
_register(
    FixTemplate(
        vuln_type="traversal",
        platform="flask",
        code="# os.path.commonpath([base_dir, target]) == base_dir",
        description="校验目标路径是否在允许的基础目录内",
    )
)

# --- Deserialization ---
_register(
    FixTemplate(
        vuln_type="deserialization",
        platform="flask",
        code="# 使用 json + itsdangerous 代替 pickle",
        description="避免使用不安全的反序列化库",
    )
)

# --- XXE ---
_register(
    FixTemplate(
        vuln_type="xxe",
        platform="flask",
        code=(
            "# Python xml.etree: 禁用外部实体\n"
            "from xml.etree import ElementTree as ET\n"
            "parser = ET.XMLParser(resolve_entities=False)"
        ),
        description="禁用 XML 外部实体解析",
    )
)

# --- Logic Bypass ---
_register(
    FixTemplate(
        vuln_type="logic_bypass",
        platform="generic",
        code=(
            "# 在关键业务逻辑处增加服务端校验\n"
            "# 不要仅依赖前端隐藏字段或 JS 校验\n"
            "if not validate_business_rule(data):\n"
            "    abort(403)"
        ),
        description="关键业务逻辑必须在服务端二次校验",
    )
)


# ---------- 引擎 ----------


class RemediationTemplateEngine:
    """修复模板引擎。

    根据漏洞类型、服务器类型和上下文生成结构化修复方案。
    """

    # 默认平台列表（按优先级）
    PLATFORM_PRIORITY = [
        "nginx",
        "apache",
        "cloudflare",
        "flask",
        "express",
        "spring_boot",
        "generic",
    ]

    @classmethod
    def list_templates(cls, vuln_type: str) -> dict[str, FixTemplate]:
        """获取某漏洞类型的所有平台模板。"""
        return dict(_TEMPLATE_LIBRARY.get(vuln_type, {}))

    @classmethod
    def render(
        cls,
        vuln_type: str,
        platform: str,
        ctx: dict[str, Any],
    ) -> FixTemplate | None:
        """渲染指定漏洞类型和平台的修复模板。"""
        tmpl = _TEMPLATE_LIBRARY.get(vuln_type, {}).get(platform)
        if not tmpl:
            return None
        # 返回一个带有渲染后代码的副本
        return FixTemplate(
            vuln_type=tmpl.vuln_type,
            platform=tmpl.platform,
            code=tmpl.render(ctx),
            description=tmpl.description,
            risk_note=tmpl.risk_note,
            prerequisites=tmpl.prerequisites,
            verification_steps=[s.format(**ctx) for s in tmpl.verification_steps],
        )

    @classmethod
    def render_all_platforms(
        cls,
        vuln_type: str,
        ctx: dict[str, Any],
    ) -> dict[str, FixTemplate]:
        """为某漏洞类型渲染所有可用平台的模板。"""
        result: dict[str, FixTemplate] = {}
        for platform, tmpl in _TEMPLATE_LIBRARY.get(vuln_type, {}).items():
            result[platform] = cls.render(vuln_type, platform, ctx)
        return result

    @classmethod
    def suggest_platforms(
        cls,
        detected_server: str,
        vuln_type: str,
    ) -> list[str]:
        """根据检测到的服务器类型推荐修复平台顺序。"""
        available = list(_TEMPLATE_LIBRARY.get(vuln_type, {}).keys())
        if detected_server in available:
            # 检测到的平台放最前
            ordered = [detected_server]
            ordered += [p for p in available if p != detected_server]
            return ordered
        return available


def _detect_server_type(headers: dict[str, str]) -> str:
    """根据响应头推测服务器类型（兼容 main.py 原逻辑）。"""
    server = headers.get("server", "").lower()
    if "nginx" in server:
        return "nginx"
    if "apache" in server:
        return "apache"
    if "cloudflare" in server:
        return "cloudflare"
    powered = headers.get("x-powered-by", "").lower()
    if "express" in powered:
        return "express"
    if "flask" in powered or "python" in powered or "wsgi" in powered:
        return "flask"
    if "spring" in powered or "java" in powered:
        return "spring_boot"
    return "unknown"


# Header 名映射（别名 -> 标准名）
_HEADER_NAME_MAP = {
    "hsts": "Strict-Transport-Security",
    "csp": "Content-Security-Policy",
    "xcto": "X-Content-Type-Options",
    "xfo": "X-Frame-Options",
}


def _parse_header_fix(name: str, fix_text: str) -> tuple[str, str]:
    """从修复文本中解析 header 名和值。"""
    header_name = name[3:] if name.startswith("缺少 ") else name
    # 映射别名到标准 header 名
    header_name = _HEADER_NAME_MAP.get(header_name.lower(), header_name)
    header_value = ""
    if '"' in fix_text:
        parts = fix_text.split('"')
        if len(parts) >= 2:
            header_value = parts[1]
    return header_name, header_value


def _infer_vuln_type(name: str, ftype: str) -> str:
    """根据 finding name 和 type 推断漏洞类型（兼容大小写和别名）。"""
    ftype_norm = (ftype or "").lower()
    name_norm = (name or "").lower()

    # 优先使用 type 字段
    type_aliases = {
        "xss": "xss",
        "reflected_xss": "xss",
        "sqli": "sqli",
        "sql_injection": "sqli",
        "ssrf": "ssrf",
        "csrf": "csrf",
        "cmdi": "cmdi",
        "command_injection": "cmdi",
        "traversal": "traversal",
        "path_traversal": "traversal",
        "deserialization": "deserialization",
        "idor": "idor",
        "open_redirect": "open_redirect",
        "file_upload": "file_upload",
        "info_leak": "info_leak",
        "sensitive_path": "sensitive_path",
        "broken_access_control": "broken_access_control",
        "logic_bypass": "logic_bypass",
        "xxe": "xxe",
        "ssl": "ssl",
        "weak_ssl": "weak_ssl",
    }
    if ftype_norm in type_aliases:
        return type_aliases[ftype_norm]

    # 根据 name 推断
    if "sql" in name_norm or "sqli" in name_norm:
        return "sqli"
    if "xss" in name_norm:
        return "xss"
    if "csrf" in name_norm:
        return "csrf"
    if "ssrf" in name_norm:
        return "ssrf"
    if "cmd" in name_norm or "command" in name_norm:
        return "cmdi"
    if "traversal" in name_norm or "路径遍历" in name:
        return "traversal"
    if "反序列化" in name or "deserialization" in name_norm:
        return "deserialization"
    if "idor" in name_norm or "越权" in name:
        return "idor"
    if "重定向" in name or "redirect" in name_norm:
        return "open_redirect"
    if "上传" in name or "upload" in name_norm:
        return "file_upload"
    if "信息泄露" in name or "info leak" in name_norm:
        return "info_leak"
    if "敏感路径" in name or "sensitive path" in name_norm:
        return "sensitive_path"
    if "越权访问" in name or "access control" in name_norm:
        return "broken_access_control"
    if "逻辑绕过" in name or "logic" in name_norm:
        return "logic_bypass"
    if "xxe" in name_norm:
        return "xxe"
    if "弱 ssl" in name_norm or "弱 tls" in name_norm or "weak ssl" in name_norm:
        return "weak_ssl"
    if "ssl" in name_norm or "https" in name_norm:
        return "ssl"
    if "cookie" in name_norm:
        return "header_missing"
    if "cors" in name_norm:
        return "header_missing"

    return ftype_norm or "unknown"


def generate_remediation_plan(
    findings: list[dict[str, Any]],
    headers: dict[str, str],
    host: str,
) -> dict[str, Any]:
    """生成完整的修复计划。

    返回结构与 generate_fixes() 兼容，但增加了结构化字段：
    - plans: 按 finding 组织的修复方案列表
    - by_platform: 按平台聚合的修复配置
    - summary: 统计信息
    """
    engine = RemediationTemplateEngine()
    detected = _detect_server_type(headers)

    plans: list[dict[str, Any]] = []
    by_platform: dict[str, list[dict[str, Any]]] = {
        p: [] for p in engine.PLATFORM_PRIORITY
    }
    seen: set = set()

    for f in findings:
        name = (f.get("name") or f.get("title") or "").strip()
        severity = f.get("severity") or "low"
        raw_type = f.get("type", "unknown")
        url = f.get("url", "")
        parameter = f.get("parameter", "")

        # 推断漏洞类型（兼容大小写和别名）
        ftype = _infer_vuln_type(name, raw_type)

        # 构建上下文
        ctx: dict[str, Any] = {
            "host": host,
            "url": url,
            "parameter": parameter,
            "finding_name": name,
        }

        # 处理 header_missing 类型：从 name 解析 header 名
        if name.startswith("缺少 "):
            ftype = "header_missing"
            fix_text = (
                f.get("fix", "")
                or f.get("fix_suggestion", "")
                or (f.get("fix_code") or {}).get("generic", "")
            )
            header_name, header_value = _parse_header_fix(name, fix_text)
            ctx["header_name"] = header_name
            ctx["header_value"] = header_value
            ctx["header_method"] = header_name.lower().replace("-", "_")

        # 特殊映射
        if ftype == "ssl" and "弱" in name:
            ftype = "weak_ssl"

        templates = engine.render_all_platforms(ftype, ctx)
        if not templates:
            # 兜底：如果有 fix_text，作为 generic 平台
            fix_text = (
                f.get("fix", "")
                or f.get("fix_suggestion", "")
                or (f.get("fix_code") or {}).get("generic", "")
            )
            if fix_text:
                templates["generic"] = FixTemplate(
                    vuln_type=ftype,
                    platform="generic",
                    code=fix_text,
                    description="通用修复建议",
                )

        # 去重键
        dedup_key = f"{ftype}:{name}"
        if dedup_key in seen:
            continue
        seen.add(dedup_key)

        platform_fixes: dict[str, dict[str, Any]] = {}
        for platform, tmpl in templates.items():
            if not tmpl:
                continue
            entry = {
                "code": tmpl.code,
                "description": tmpl.description,
                "risk_note": tmpl.risk_note,
                "prerequisites": tmpl.prerequisites,
                "verification_steps": tmpl.verification_steps,
            }
            platform_fixes[platform] = entry
            by_platform.setdefault(platform, []).append(entry)

        plans.append(
            {
                "finding_name": name,
                "finding_type": ftype,
                "severity": severity,
                "url": url,
                "parameter": parameter,
                "recommended_platforms": engine.suggest_platforms(detected, ftype),
                "detected_platform": detected,
                "fixes": platform_fixes,
            }
        )

    # 兼容旧格式：生成 fixes 字典
    legacy_fixes: dict[str, list[dict[str, Any]]] = {
        "nginx": [],
        "apache": [],
        "express": [],
        "flask": [],
        "spring_boot": [],
        "cloudflare": [],
        "nodejs": [],
        "python": [],
    }
    for platform, entries in by_platform.items():
        target_key = platform
        if platform == "generic" and entries:
            target_key = "nginx"  # 兜底放到 nginx
        for e in entries:
            legacy_fixes.setdefault(target_key, []).append(
                {
                    "code": e["code"],
                    "risk_note": e.get("risk_note"),
                    "server_type": detected,
                    "config_examples": {platform: e["code"]},
                }
            )

    return {
        "plans": plans,
        "by_platform": by_platform,
        "legacy_fixes": legacy_fixes,
        "summary": {
            "total_findings": len(plans),
            "platforms_available": list(
                {p for plan in plans for p in plan["fixes"].keys()}
            ),
            "detected_platform": detected,
        },
    }
