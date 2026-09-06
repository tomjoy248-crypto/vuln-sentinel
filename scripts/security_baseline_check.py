"""生产环境安全基线检查脚本。

在应用启动前或 CI 流程中运行，检查关键安全配置是否符合落地要求：
- JWT_SECRET 是否已设置且足够强
- CORS 是否显式配置（禁止通配符）
- 是否使用 HTTPS/TLS 校验
- 数据库 URL 是否使用生产级数据库（可选）
- 是否配置了 Redis（可选）
- 是否存在明显的硬编码密钥

返回非零退出码表示存在必须修复的安全问题。
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _emit(message: str) -> None:
    sys.stdout.write(f"{message}\n")
    sys.stdout.flush()


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


class CheckResult:
    """单项检查结果。"""

    def __init__(self, name: str, passed: bool, message: str, critical: bool = True) -> None:
        self.name = name
        self.passed = passed
        self.message = message
        self.critical = critical


def _is_production() -> bool:
    """判断当前是否按生产环境运行。"""
    env = os.environ.get("ENV", "development").lower()
    prod_flag = os.environ.get("PRODUCTION", "").strip().lower()
    return env == "production" or prod_flag in ("1", "true", "yes")


def check_jwt_secret() -> CheckResult:
    """检查 JWT_SECRET。"""
    is_prod = _is_production()
    secret = os.environ.get("JWT_SECRET", "")
    if not secret:
        return CheckResult(
            "JWT_SECRET",
            False,
            "未设置 JWT_SECRET 环境变量。生产环境必须设置强随机密钥（>=32 字符）。",
            critical=is_prod,
        )
    if len(secret) < 32:
        return CheckResult(
            "JWT_SECRET",
            False,
            f"JWT_SECRET 长度仅 {len(secret)} 字符，生产环境要求不少于 32 字符。",
            critical=is_prod,
        )
    if secret.lower() in {
        "change-me",
        "secret",
        "password",
        "123456",
        "your-secret-key",
    }:
        return CheckResult(
            "JWT_SECRET",
            False,
            "JWT_SECRET 使用了明显弱值，请更换为随机生成的强密钥。",
            critical=is_prod,
        )
    return CheckResult("JWT_SECRET", True, "JWT_SECRET 已设置且长度符合要求。")


def check_cors() -> CheckResult:
    """检查 CORS 配置。"""
    is_prod = _is_production()
    origins = os.environ.get("ALLOWED_ORIGINS") or os.environ.get("CORS_ORIGINS") or ""
    origins_list = [o.strip() for o in origins.split(",") if o.strip()]
    if not origins_list:
        return CheckResult(
            "CORS",
            False,
            "未设置 ALLOWED_ORIGINS / CORS_ORIGINS。生产环境必须显式列出允许的域名。",
            critical=is_prod,
        )
    if "*" in origins_list:
        return CheckResult(
            "CORS",
            False,
            "ALLOWED_ORIGINS 包含通配符 '*'，生产环境禁止此配置。",
            critical=is_prod,
        )
    return CheckResult("CORS", True, f"CORS 已显式配置 {len(origins_list)} 个来源。")


def check_tls_verify() -> CheckResult:
    """检查是否启用 TLS 证书校验。"""
    tls_verify = os.environ.get("TLS_VERIFY", "1").strip().lower()
    if tls_verify in ("0", "false", "no", "off"):
        return CheckResult(
            "TLS_VERIFY",
            False,
            "TLS_VERIFY 已禁用。生产环境必须启用 TLS 证书校验。",
        )
    return CheckResult("TLS_VERIFY", True, "TLS 证书校验已启用。")


def check_database() -> CheckResult:
    """检查数据库配置（建议生产使用 PostgreSQL）。"""
    database_url = os.environ.get("DATABASE_URL", "")
    if database_url and database_url.startswith("postgresql"):
        return CheckResult("DATABASE", True, "已配置 PostgreSQL 数据库。")
    return CheckResult(
        "DATABASE",
        True,
        "当前使用 SQLite。生产环境建议切换到 PostgreSQL 以获得更好的并发与可靠性。",
        critical=False,
    )


def check_redis() -> CheckResult:
    """检查是否配置 Redis。"""
    redis_url = os.environ.get("REDIS_URL", "")
    if redis_url:
        return CheckResult("REDIS", True, "已配置 Redis，可用于分布式限流与任务队列。")
    return CheckResult(
        "REDIS",
        True,
        "未配置 REDIS_URL。生产环境建议启用 Redis 以支持分布式限流与异步任务。",
        critical=False,
    )


def _scan_for_hardcoded_secrets(content: str) -> list[str]:
    """扫描文本中疑似硬编码密钥的模式。"""
    findings: list[str] = []
    patterns = [
        (r"['\"]sk-[A-Za-z0-9]{20,}['\"]", "API key (sk-...)"),
        (r"['\"]AK[A-Za-z0-9]{16,}['\"]", "Access key (AK...)"),
        (r"jwt_secret\s*=\s*['\"][^'\"]{8,}['\"]", "JWT secret assignment"),
        # Match standalone credential variable names only.  A word boundary
        # avoids treating harmless flags such as ``has_password`` as secrets.
        (
            r"\b(?:password|passwd|secret|token|api[_-]?key)\s*=\s*['\"][^'\"]+['\"]",
            "credential assignment",
        ),
    ]
    for pattern, desc in patterns:
        if re.search(pattern, content, re.IGNORECASE):
            findings.append(desc)
    return findings


def check_hardcoded_secrets() -> CheckResult:
    """扫描项目源码中的明显硬编码密钥。"""
    suspicious: list[str] = []
    scanned = 0
    skipped_roots = {"node_modules", "__pycache__", ".git", "static", "dist", "artifacts", ".pytest_cache"}
    skipped_names = {"test", "tests", "scripts", "benchmark_reports"}
    for pattern in ("*.py", "*.js", "*.ts", "*.yml", "*.yaml", "*.toml"):
        for path in PROJECT_ROOT.rglob(pattern):
            # 跳过依赖目录、测试与构建产物，避免把测试密码和示例配置当作真实密钥
            if any(part in skipped_roots for part in path.parts):
                continue
            if path.name.startswith("test_") or path.stem.endswith("_test"):
                continue
            if path.parent.name in skipped_names:
                continue
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            scanned += 1
            found = _scan_for_hardcoded_secrets(content)
            if found:
                suspicious.append(f"{path.relative_to(PROJECT_ROOT)}: {', '.join(found)}")
            # 仅扫描前 500 个文件，避免耗时过长
            if scanned >= 500:
                break
        if scanned >= 500:
            break

    if suspicious:
        sample = "\n  - ".join(suspicious[:5])
        return CheckResult(
            "HARDCODED_SECRETS",
            False,
            f"发现疑似硬编码密钥（共 {len(suspicious)} 处，示例）：\n  - {sample}",
        )
    return CheckResult(
        "HARDCODED_SECRETS",
        True,
        f"已扫描 {scanned} 个文件，未发现明显硬编码密钥。",
    )


def main() -> int:
    """执行所有检查并输出报告。"""
    is_prod = _is_production()
    _emit(f"Vuln Sentinel 安全基线检查 — 识别为 {'生产' if is_prod else '开发'} 环境\n")

    checks = [
        check_jwt_secret(),
        check_cors(),
        check_tls_verify(),
        check_database(),
        check_redis(),
        check_hardcoded_secrets(),
    ]

    critical_failures = 0
    warnings = 0
    for check in checks:
        status = "PASS" if check.passed else ("WARN" if not check.critical else "FAIL")
        icon = "✓" if check.passed else ("⚠" if not check.critical else "✗")
        _emit(f"{icon} [{status}] {check.name}: {check.message}")
        if not check.passed:
            if check.critical:
                critical_failures += 1
            else:
                warnings += 1

    _emit("")
    if critical_failures:
        _emit(f"结果：存在 {critical_failures} 个必须修复的严重安全问题。")
        return 1
    if warnings:
        _emit(f"结果：通过，但存在 {warnings} 项建议改进。")
        return 0
    _emit("结果：所有检查通过，安全配置符合基线要求。")
    return 0


if __name__ == "__main__":
    sys.exit(main())

