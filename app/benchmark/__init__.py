"""已知漏洞靶场基准对比系统。

本模块实现类似 SRC 漏洞挖掘中的验证机制：使用一组公开的已知漏洞靶场
（如 testphp.vulnweb.com、httpbin.org、example.com）作为基准，对扫描引擎
的检出能力进行量化评估。

核心概念：
    - **预期漏洞 (Expected Vulnerability)**：靶场上已知存在的漏洞，
      扫描器理应检出。
    - **负向检查 (Negative Check)**：靶场上明确不存在的漏洞类型，
      扫描器不应误报。
    - **混淆矩阵**：将扫描结果与预期对比，得到 TP/FP/TN/FN 四类计数。
    - **指标**：基于混淆矩阵计算精确率、召回率、F1、准确率与误报率。

子模块：
    - ``targets``：靶场目标与预期漏洞定义。
    - ``runner``：基准测试运行器，执行扫描并生成对比结果。
    - ``reporter``：生成自包含的 HTML 基准对比报告。

典型用法::

    import asyncio
    from app.benchmark.runner import BenchmarkRunner

    runner = BenchmarkRunner()
    report = asyncio.run(runner.run_all())
    print(report.matrix)  # 混淆矩阵
    print(report.metrics)  # 指标
"""

from __future__ import annotations

from app.benchmark.reporter import generate_html_report, generate_json_report
from app.benchmark.runner import (
    BenchmarkReport,
    BenchmarkRunner,
    ConfusionMatrix,
    Metrics,
    TargetResult,
)
from app.benchmark.targets import (
    BENCHMARK_TARGETS,
    BenchmarkTarget,
    ExpectedVulnerability,
    NegativeCheck,
)

# 兼容别名：BenchmarkReporter 指向 generate_html_report
BenchmarkReporter = generate_html_report

__all__ = [
    "BENCHMARK_TARGETS",
    "BenchmarkReport",
    "BenchmarkReporter",
    "BenchmarkRunner",
    "BenchmarkTarget",
    "ConfusionMatrix",
    "ExpectedVulnerability",
    "Metrics",
    "NegativeCheck",
    "TargetResult",
    "generate_html_report",
    "generate_json_report",
]

__version__ = "11-S"
