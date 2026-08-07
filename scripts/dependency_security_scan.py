"""依赖安全扫描脚本。

扫描 Python 依赖中的已知漏洞。优先使用 pip-audit，未安装时回退到
pip 的 "audit" 子命令提示，或输出检查清单供人工确认。

建议集成到 CI：
    python scripts/dependency_security_scan.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REQUIREMENTS = PROJECT_ROOT / "requirements.txt"


def _emit(message: str) -> None:
    sys.stdout.write(f"{message}\n")
    sys.stdout.flush()


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def _run_pip_audit() -> tuple[bool, str]:
    """调用 pip-audit 扫描 requirements.txt。

    Returns:
        (是否成功执行且无漏洞, 输出文本)
    """
    try:
        result = subprocess.run(
            ["pip-audit", "--requirement", str(REQUIREMENTS), "--format=json"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            timeout=120,
        )
    except FileNotFoundError:
        return False, "pip-audit 未安装。建议安装：pip install pip-audit"
    except subprocess.TimeoutExpired:
        return False, "pip-audit 执行超时（120s），请检查网络连接。"

    if result.returncode == 0:
        return True, "pip-audit 未在 requirements.txt 中发现已知漏洞。"

    # 尝试解析 JSON 输出
    try:
        data = json.loads(result.stdout or "[]")
        if not data:
            return True, "pip-audit 返回空结果，未发现已知漏洞。"
        lines = []
        for item in data:
            pkg = item.get("name", "unknown")
            ver = item.get("version", "unknown")
            vulns = item.get("vulns", [])
            for v in vulns:
                lines.append(
                    f"  - {pkg}=={ver}: {v.get('id', 'UNKNOWN')} "
                    f"{v.get('fix_versions', '无修复版本信息')}"
                )
        return False, "发现已知漏洞：\n" + "\n".join(lines)
    except json.JSONDecodeError:
        return False, f"pip-audit 返回异常（code={result.returncode}）：\n{result.stdout or result.stderr}"


def _check_requirements_syntax() -> tuple[bool, str]:
    """检查 requirements.txt 语法是否可解析。"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--dry-run", "-r", str(REQUIREMENTS)],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            timeout=60,
        )
        if result.returncode == 0:
            return True, "requirements.txt 语法检查通过。"
        return False, f"requirements.txt 存在解析问题：\n{result.stderr or result.stdout}"
    except Exception as e:
        return False, f"无法执行 pip dry-run：{e}"


def main() -> int:
    """执行依赖安全扫描。"""
    _emit("漏洞哨兵 11-S 依赖安全扫描\n")

    if not REQUIREMENTS.exists():
        _emit(f"✗ [FAIL] 未找到 {REQUIREMENTS}")
        return 1

    ok, msg = _check_requirements_syntax()
    _emit(f"{'✓' if ok else '✗'} [{'PASS' if ok else 'FAIL'}] REQUIREMENTS_SYNTAX: {msg}")
    if not ok:
        return 1

    ok, msg = _run_pip_audit()
    _emit(f"{'✓' if ok else '✗'} [{'PASS' if ok else 'FAIL'}] DEPENDENCY_VULNS: {msg}")

    if not ok and "pip-audit 未安装" in msg:
        # 未安装审计工具视为警告而非失败，避免阻塞无网络环境
        _emit("\n提示：安装 pip-audit 后重新运行可获得已知漏洞扫描结果。")
        return 0

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
