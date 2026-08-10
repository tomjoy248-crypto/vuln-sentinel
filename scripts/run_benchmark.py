#!/usr/bin/env python3
"""已知漏洞靶场基准对比系统 —— 独立运行脚本。

命令行入口，对一组公开安全测试靶场执行完整基准测试，生成 HTML 与 JSON
报告到 ``benchmark_reports/`` 目录。

用法::

    python scripts/run_benchmark.py                 # 标准模式
    python scripts/run_benchmark.py --deep          # 深度扫描模式
    python scripts/run_benchmark.py --output-dir ./reports  # 自定义输出目录
    python scripts/run_benchmark.py --target vulnweb_sqli   # 仅运行指定目标

输出文件：
    - ``benchmark_report_<timestamp>.html``  自包含 HTML 报告
    - ``benchmark_report_<timestamp>.json``  机器可读 JSON 报告
    - ``benchmark_report_latest.html``       最新 HTML 软链接（复制）
    - ``benchmark_report_latest.json``       最新 JSON 软链接（复制）
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path

# 确保项目根目录在 sys.path 中，以便 ``import app.benchmark`` 与 ``import main`` 可用
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# 默认输出目录
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "benchmark_reports"


def _fmt_pct(value: float) -> str:
    """格式化百分比（本地辅助函数，避免依赖 reporter 私有函数）。"""
    return f"{value * 100:.2f}%"


def _setup_logging(verbose: bool = False) -> None:
    """配置日志。"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def _print_console_summary(report: object) -> None:
    """在控制台打印基准测试摘要。"""

    matrix = report.matrix  # type: ignore[attr-defined]
    metrics = report.metrics  # type: ignore[attr-defined]
    print("\n" + "=" * 64)
    print("Vuln Sentinel · 已知漏洞靶场基准测试结果")
    print("=" * 64)
    print(f"目标总数:   {report.total_targets}")  # type: ignore[attr-defined]
    print(f"成功扫描:   {report.successful_targets}")  # type: ignore[attr-defined]
    print("-" * 64)
    print("混淆矩阵:")
    print(f"  TP (真正例 / 正确检出): {matrix.tp}")
    print(f"  FP (假正例 / 误报):    {matrix.fp}")
    print(f"  TN (真反例 / 正确排除): {matrix.tn}")
    print(f"  FN (假反例 / 漏报):    {matrix.fn}")
    print("-" * 64)
    print("检测指标:")
    print(f"  精确率 Precision : {_fmt_pct(metrics.precision)}")
    print(f"  召回率 Recall    : {_fmt_pct(metrics.recall)}")
    print(f"  F1 Score         : {_fmt_pct(metrics.f1)}")
    print(f"  准确率 Accuracy  : {_fmt_pct(metrics.accuracy)}")
    print(f"  误报率 FPR       : {_fmt_pct(metrics.fpr)}")
    print("-" * 64)
    print("逐目标结果:")
    for tr in report.targets:  # type: ignore[attr-defined]
        status = "OK" if tr.error is None else f"ERR({tr.error[:40]})"
        print(
            f"  [{tr.target.id:<16}] {tr.target.name:<28} "
            f"TP={tr.matrix.tp} FP={tr.matrix.fp} "
            f"TN={tr.matrix.tn} FN={tr.matrix.fn}  {status}"
        )
    print("=" * 64 + "\n")


async def _run(args: argparse.Namespace) -> object:
    """执行基准测试并返回报告。"""
    from app.benchmark.runner import BenchmarkRunner
    from app.benchmark.targets import BENCHMARK_TARGETS, get_target_by_id

    # 选择目标子集
    targets = list(BENCHMARK_TARGETS)
    if args.target:
        selected = [get_target_by_id(args.target)]
        if selected[0] is None:
            print(f"错误：未找到目标 ID '{args.target}'")
            print("可用目标 ID：" + ", ".join(t.id for t in BENCHMARK_TARGETS))
            sys.exit(2)
        targets = [t for t in selected if t is not None]

    runner = BenchmarkRunner(
        deep=args.deep,
        scan_timeout=args.scan_timeout,
        max_concurrency=args.concurrency,
        targets=targets,
    )
    return await runner.run_all()


def main() -> int:
    """命令行入口。"""
    parser = argparse.ArgumentParser(
        description="已知漏洞靶场基准对比系统：评估扫描引擎对已知漏洞的检出能力。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--deep",
        action="store_true",
        help="启用深度扫描模式（端点发现 + 参数 fuzz，耗时更长）。",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"报告输出目录（默认：{DEFAULT_OUTPUT_DIR}）。",
    )
    parser.add_argument(
        "--target",
        type=str,
        default="",
        help="仅运行指定目标 ID（如 vulnweb_sqli）。留空则运行全部目标。",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=2,
        help="并发扫描目标数（默认 2）。",
    )
    parser.add_argument(
        "--scan-timeout",
        type=float,
        default=90.0,
        help="单目标扫描总超时秒数（默认 90）。",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="启用 DEBUG 日志。",
    )
    args = parser.parse_args()

    _setup_logging(verbose=args.verbose)

    # 执行基准测试
    report = asyncio.run(_run(args))

    # 控制台摘要
    _print_console_summary(report)

    # 写出报告文件
    from app.benchmark.reporter import generate_html_report, generate_json_report

    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_path = output_dir / f"benchmark_report_{timestamp}.html"
    json_path = output_dir / f"benchmark_report_{timestamp}.json"
    latest_html = output_dir / "benchmark_report_latest.html"
    latest_json = output_dir / "benchmark_report_latest.json"

    html_path.write_text(
        generate_html_report(report), encoding="utf-8"
    )
    json_path.write_text(
        generate_json_report(report), encoding="utf-8"
    )
    # 覆盖 latest 副本
    latest_html.write_text(
        generate_html_report(report), encoding="utf-8"
    )
    latest_json.write_text(
        generate_json_report(report), encoding="utf-8"
    )

    print(f"HTML 报告已生成: {html_path}")
    print(f"JSON 报告已生成: {json_path}")
    print(f"最新 HTML 副本:  {latest_html}")
    print(f"最新 JSON 副本:  {latest_json}")

    # 若召回率或精确率过低，返回非零退出码以便 CI 检测
    metrics = report.metrics  # type: ignore[attr-defined]
    if metrics.recall < 0.5 and report.successful_targets > 0:  # type: ignore[attr-defined]
        print(
            f"\n警告：召回率仅 {_fmt_pct(metrics.recall)}（低于 50%），"
            "扫描引擎漏报较多预期漏洞。",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

