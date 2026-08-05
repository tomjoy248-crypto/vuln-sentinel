"""基准对比报告生成器。

生成自包含的 HTML 基准对比报告，包含：

- 聚合检测指标（精确率、召回率、F1、准确率、误报率）。
- 混淆矩阵可视化（TP/FP/TN/FN 2x2 网格）。
- 逐靶场目标的预期与实际发现对比表。
- 每个漏洞类型的检出率统计。
- 误报率与误报明细分析。

报告内联全部 CSS，无外部依赖，可直接用浏览器打开。
"""

from __future__ import annotations

import html
from collections import defaultdict
from datetime import datetime
from typing import Any

from app.benchmark.runner import BenchmarkReport, TargetResult

# 严重级别中文名映射
_SEVERITY_CN: dict[str, str] = {
    "critical": "严重",
    "high": "高危",
    "medium": "中危",
    "low": "低危",
    "info": "信息",
    "informational": "信息",
}

# 漏洞类型中文名映射（覆盖扫描引擎常用类型）
_VULN_TYPE_CN: dict[str, str] = {
    "sqli": "SQL 注入",
    "xss": "跨站脚本 (XSS)",
    "cmdi": "命令注入",
    "traversal": "路径遍历",
    "ssrf": "服务端请求伪造 (SSRF)",
    "open_redirect": "开放重定向",
    "csrf": "跨站请求伪造 (CSRF)",
    "info_leak": "信息泄露",
    "header_missing": "安全响应头缺失",
    "cors_misconfig": "CORS 配置不当",
    "outdated_component": "过时组件",
    "ssl": "SSL/TLS 配置问题",
    "cookie": "Cookie 安全配置",
    "file_upload": "不安全文件上传",
    "idor": "不安全直接对象引用",
    "xxe": "XML 外部实体注入",
    "deserialization": "不安全反序列化",
}


def _esc(text: Any) -> str:
    """HTML 转义。"""
    return html.escape(str(text), quote=True)


def _vuln_type_cn(vuln_type: str) -> str:
    """漏洞类型中文名。"""
    return _VULN_TYPE_CN.get(vuln_type.lower(), vuln_type or "未知")


def _severity_cn(severity: str) -> str:
    """严重级别中文名。"""
    return _SEVERITY_CN.get(str(severity).lower(), str(severity) or "未知")


def _verdict_badge(verdict: str) -> str:
    """判定结果的彩色徽章 HTML。"""
    styles = {
        "TP": "background:#dcfce7;color:#166534;border-color:#86efac",
        "FP": "background:#fee2e2;color:#991b1b;border-color:#fca5a5",
        "TN": "background:#dbeafe;color:#1e40af;border-color:#93c5fd",
        "FN": "background:#fef9c3;color:#854d0e;border-color:#fde047",
    }
    style = styles.get(verdict, "background:#f3f4f6;color:#374151;border-color:#d1d5db")
    return f'<span class="badge" style="{style}">{verdict}</span>'


def _fmt_pct(value: float) -> str:
    """格式化百分比。"""
    return f"{value * 100:.2f}%"


# ---------------------------------------------------------------------------
# 统计聚合
# ---------------------------------------------------------------------------


def _vuln_type_stats(report: BenchmarkReport) -> list[dict[str, Any]]:
    """按漏洞类型聚合检出统计。

    Returns:
        列表，每项含: vuln_type, tp, fn, fp, expected_total, detection_rate。
    """
    stats: dict[str, dict[str, int]] = defaultdict(
        lambda: {"tp": 0, "fn": 0, "fp": 0}
    )

    for tr in report.targets:
        for c in tr.check_results:
            vt = c.vuln_type or "unknown"
            if c.verdict == "TP":
                stats[vt]["tp"] += 1
            elif c.verdict == "FN":
                stats[vt]["fn"] += 1
            elif c.verdict == "FP":
                stats[vt]["fp"] += 1

    rows: list[dict[str, Any]] = []
    for vt, s in stats.items():
        expected_total = s["tp"] + s["fn"]
        detection_rate = (
            s["tp"] / expected_total if expected_total > 0 else 0.0
        )
        rows.append(
            {
                "vuln_type": vt,
                "tp": s["tp"],
                "fn": s["fn"],
                "fp": s["fp"],
                "expected_total": expected_total,
                "detection_rate": detection_rate,
            }
        )

    # 按预期总数降序、检出率升序排列，突出薄弱项
    rows.sort(key=lambda r: (-r["expected_total"], r["detection_rate"]))
    return rows


def _false_positive_details(report: BenchmarkReport) -> list[dict[str, Any]]:
    """收集所有误报（FP）明细。"""
    details: list[dict[str, Any]] = []
    for tr in report.targets:
        for c in tr.check_results:
            if c.verdict != "FP":
                continue
            details.append(
                {
                    "target_id": tr.target.id,
                    "target_name": tr.target.name,
                    "url": tr.target.url,
                    "vuln_type": c.vuln_type,
                    "kind": c.kind,
                    "finding_title": (c.finding or {}).get("title", ""),
                    "finding_severity": (c.finding or {}).get("severity", ""),
                    "note": c.note,
                }
            )
    return details


def _false_negative_details(report: BenchmarkReport) -> list[dict[str, Any]]:
    """收集所有漏报（FN）明细。"""
    details: list[dict[str, Any]] = []
    for tr in report.targets:
        for c in tr.check_results:
            if c.verdict != "FN":
                continue
            details.append(
                {
                    "target_id": tr.target.id,
                    "target_name": tr.target.name,
                    "url": tr.target.url,
                    "vuln_type": c.vuln_type,
                    "severity": c.severity,
                    "description": c.description,
                    "note": c.note,
                }
            )
    return details


# ---------------------------------------------------------------------------
# HTML 片段生成
# ---------------------------------------------------------------------------

_INLINE_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
    "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial,
    sans-serif;
  background: #f8fafc; color: #1e293b; line-height: 1.6; padding: 24px;
}
.container { max-width: 1200px; margin: 0 auto; }
h1 { font-size: 28px; color: #0f172a; margin-bottom: 8px; }
h2 { font-size: 22px; color: #1e293b; margin: 32px 0 16px; padding-bottom: 8px;
     border-bottom: 2px solid #e2e8f0; }
h3 { font-size: 18px; color: #334155; margin: 20px 0 12px; }
.subtitle { color: #64748b; font-size: 14px; margin-bottom: 24px; }
.card { background: #fff; border-radius: 12px; padding: 24px; margin-bottom: 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08); border: 1px solid #e2e8f0; }
.metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                gap: 16px; }
.metric { text-align: center; padding: 20px 12px; border-radius: 10px;
          background: #f8fafc; border: 1px solid #e2e8f0; }
.metric .value { font-size: 32px; font-weight: 700; color: #0f172a; }
.metric .label { font-size: 13px; color: #64748b; margin-top: 4px; }
.metric.good .value { color: #16a34a; }
.metric.warn .value { color: #d97706; }
.metric.bad .value { color: #dc2626; }
.matrix { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; max-width: 520px; }
.matrix-cell { padding: 28px 20px; border-radius: 10px; text-align: center;
               border: 2px solid; }
.matrix-cell .count { font-size: 40px; font-weight: 700; }
.matrix-cell .name { font-size: 14px; margin-top: 6px; font-weight: 600; }
.matrix-cell .desc { font-size: 12px; margin-top: 4px; opacity: 0.85; }
.matrix-cell.tp { background: #dcfce7; border-color: #86efac; color: #166534; }
.matrix-cell.fp { background: #fee2e2; border-color: #fca5a5; color: #991b1b; }
.matrix-cell.tn { background: #dbeafe; border-color: #93c5fd; color: #1e40af; }
.matrix-cell.fn { background: #fef9c3; border-color: #fde047; color: #854d0e; }
table { width: 100%; border-collapse: collapse; font-size: 14px; }
th { background: #f1f5f9; text-align: left; padding: 10px 12px; font-weight: 600;
     color: #475569; border-bottom: 2px solid #e2e8f0; white-space: nowrap; }
td { padding: 10px 12px; border-bottom: 1px solid #e2e8f0; vertical-align: top; }
tr:hover td { background: #f8fafc; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px;
         font-weight: 600; border: 1px solid; }
.sev { display: inline-block; padding: 1px 7px; border-radius: 4px; font-size: 12px;
       font-weight: 600; }
.sev-critical { background: #fef2f2; color: #991b1b; }
.sev-high { background: #fff7ed; color: #9a3412; }
.sev-medium { background: #fffbeb; color: #92400e; }
.sev-low { background: #f0fdf4; color: #166534; }
.sev-info { background: #f1f5f9; color: #475569; }
.bar-container { background: #e2e8f0; border-radius: 4px; height: 18px; width: 100%;
                min-width: 80px; overflow: hidden; position: relative; }
.bar-fill { height: 100%; border-radius: 4px; }
.bar-label { position: absolute; right: 6px; top: 0; font-size: 11px; line-height: 18px;
             color: #1e293b; font-weight: 600; }
.code { font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
        font-size: 13px; color: #be185d; word-break: break-all; }
.muted { color: #94a3b8; }
.error-box { background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px;
             padding: 10px 14px; color: #991b1b; font-size: 13px; margin-top: 8px; }
.tag { display: inline-block; padding: 1px 6px; border-radius: 4px; font-size: 11px;
       background: #e0e7ff; color: #3730a3; }
.summary-line { font-size: 15px; color: #475569; margin-bottom: 16px; }
"""


def _severity_class(severity: str) -> str:
    """严重级别对应的 CSS 类名。"""
    return f"sev-{str(severity).lower()}"


def _render_header(report: BenchmarkReport) -> str:
    """渲染报告头部与摘要指标。"""
    m = report.metrics
    generated = datetime.fromisoformat(report.generated_at).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    ) if report.generated_at else "未知"

    def _metric_class(name: str, value: float) -> str:
        if name in ("precision", "recall", "f1", "accuracy"):
            if value >= 0.9:
                return "good"
            if value >= 0.7:
                return "warn"
            return "bad"
        # fpr: 越低越好
        if value <= 0.05:
            return "good"
        if value <= 0.2:
            return "warn"
        return "bad"

    return f"""
    <div class="card">
      <h1>漏洞哨兵 11-S · 已知漏洞靶场基准对比报告</h1>
      <div class="subtitle">生成时间：{_esc(generated)} ｜
        目标数：{report.total_targets} ｜ 成功扫描：{report.successful_targets} ｜
        扫描模式：{'深度' if False else '标准'}（见各目标详情）</div>
      <div class="summary-line">
        本报告基于公开安全测试靶场，评估扫描引擎对已知漏洞的检出能力。
        下方指标聚合所有靶场的混淆矩阵得出。
      </div>
      <div class="metrics-grid">
        <div class="metric {_metric_class('precision', m.precision)}">
          <div class="value">{_fmt_pct(m.precision)}</div>
          <div class="label">精确率 Precision</div>
        </div>
        <div class="metric {_metric_class('recall', m.recall)}">
          <div class="value">{_fmt_pct(m.recall)}</div>
          <div class="label">召回率 Recall</div>
        </div>
        <div class="metric {_metric_class('f1', m.f1)}">
          <div class="value">{_fmt_pct(m.f1)}</div>
          <div class="label">F1 Score</div>
        </div>
        <div class="metric {_metric_class('accuracy', m.accuracy)}">
          <div class="value">{_fmt_pct(m.accuracy)}</div>
          <div class="label">准确率 Accuracy</div>
        </div>
        <div class="metric {_metric_class('fpr', m.fpr)}">
          <div class="value">{_fmt_pct(m.fpr)}</div>
          <div class="label">误报率 FPR</div>
        </div>
      </div>
    </div>
    """


def _render_confusion_matrix(report: BenchmarkReport) -> str:
    """渲染混淆矩阵可视化。"""
    mx = report.matrix
    return f"""
    <div class="card">
      <h2>混淆矩阵</h2>
      <div class="summary-line">
        TP+FN = 预期漏洞总数（正例）；FP+TN = 负向检查 + 未预期发现总数（负例）。
      </div>
      <div class="matrix">
        <div class="matrix-cell tp">
          <div class="count">{mx.tp}</div>
          <div class="name">TP 真正例</div>
          <div class="desc">正确检出预期漏洞</div>
        </div>
        <div class="matrix-cell fp">
          <div class="count">{mx.fp}</div>
          <div class="name">FP 假正例</div>
          <div class="desc">报告了不存在的漏洞（误报）</div>
        </div>
        <div class="matrix-cell fn">
          <div class="count">{mx.fn}</div>
          <div class="name">FN 假反例</div>
          <div class="desc">漏报了预期漏洞</div>
        </div>
        <div class="matrix-cell tn">
          <div class="count">{mx.tn}</div>
          <div class="name">TN 真反例</div>
          <div class="desc">正确判定无该漏洞</div>
        </div>
      </div>
    </div>
    """


def _render_vuln_type_stats(report: BenchmarkReport) -> str:
    """渲染每个漏洞类型的检出率统计。"""
    rows = _vuln_type_stats(report)
    if not rows:
        return '<div class="card"><h2>漏洞类型检出率</h2><p class="muted">无数据</p></div>'

    body = []
    for r in rows:
        rate = r["detection_rate"]
        color = "#16a34a" if rate >= 0.9 else ("#d97706" if rate >= 0.5 else "#dc2626")
        body.append(f"""
        <tr>
          <td>{_esc(_vuln_type_cn(r['vuln_type']))}<br><span class="muted code">{_esc(r['vuln_type'])}</span></td>
          <td>{r['tp']}</td>
          <td>{r['fn']}</td>
          <td>{r['fp']}</td>
          <td>{r['expected_total']}</td>
          <td>
            <div class="bar-container">
              <div class="bar-fill" style="width:{rate*100:.1f}%;background:{color}"></div>
              <span class="bar-label">{_fmt_pct(rate)}</span>
            </div>
          </td>
        </tr>""")

    return f"""
    <div class="card">
      <h2>漏洞类型检出率统计</h2>
      <table>
        <thead><tr>
          <th>漏洞类型</th><th>检出 TP</th><th>漏报 FN</th><th>误报 FP</th>
          <th>预期总数</th><th>检出率</th>
        </tr></thead>
        <tbody>{''.join(body)}
        </tbody>
      </table>
    </div>
    """


def _render_target_detail(tr: TargetResult) -> str:
    """渲染单个靶场目标的详细对比表。"""
    t = tr.target
    mx = tr.matrix
    m = tr.metrics

    error_html = ""
    if tr.error:
        error_html = f'<div class="error-box">扫描失败：{_esc(tr.error)}（所有预期漏洞计为漏报）</div>'

    # 检查点对比表
    check_rows = []
    for c in tr.check_results:
        finding_title = (c.finding or {}).get("title", "—")
        finding_sev = (c.finding or {}).get("severity", "")
        sev_html = (
            f'<span class="sev {_severity_class(finding_sev)}">{_esc(_severity_cn(finding_sev))}</span>'
            if finding_sev
            else '<span class="muted">—</span>'
        )
        kind_tag = {
            "expected": '<span class="tag">预期</span>',
            "negative": '<span class="tag">负向</span>',
            "unexpected": '<span class="tag" style="background:#ffe4e6;color:#9f1239">未预期</span>',
        }.get(c.kind, "")
        check_rows.append(f"""
        <tr>
          <td>{_verdict_badge(c.verdict)}</td>
          <td>{kind_tag} {_esc(_vuln_type_cn(c.vuln_type))}<br><span class="muted code">{_esc(c.vuln_type)}</span></td>
          <td>{sev_html}</td>
          <td>{_esc(finding_title)}</td>
          <td>{_esc(c.note)}</td>
        </tr>""")

    checks_html = (
        f'<table><thead><tr>'
        f'<th>判定</th><th>检查点</th><th>严重级别</th><th>实际发现</th><th>说明</th>'
        f'</tr></thead><tbody>{"".join(check_rows)}</tbody></table>'
        if check_rows
        else '<p class="muted">无检查点数据</p>'
    )

    return f"""
    <div class="card">
      <h3>{_esc(t.name)} <span class="muted" style="font-size:14px;font-weight:400">（{t.id}）</span></h3>
      <div class="summary-line">
        <span class="code">{_esc(t.url)}</span><br>
        分类：{_esc(t.category)} ｜ 类别：{'基线站点' if t.is_baseline else '漏洞靶场'}<br>
        {_esc(t.description)}
      </div>
      {error_html}
      <div class="metrics-grid" style="margin:12px 0">
        <div class="metric"><div class="value">{mx.tp}</div><div class="label">TP</div></div>
        <div class="metric"><div class="value">{mx.fp}</div><div class="label">FP</div></div>
        <div class="metric"><div class="value">{mx.tn}</div><div class="label">TN</div></div>
        <div class="metric"><div class="value">{mx.fn}</div><div class="label">FN</div></div>
        <div class="metric"><div class="value">{_fmt_pct(m.recall)}</div><div class="label">召回率</div></div>
        <div class="metric"><div class="value">{_fmt_pct(m.precision)}</div><div class="label">精确率</div></div>
      </div>
      <p class="muted" style="font-size:13px">实际发现 {len(tr.findings)} 项{f'（其中 {tr.ignored_count} 项属范围外已排除）' if tr.ignored_count else ''} ｜ 耗时 {tr.duration_ms} ms ｜ 扫描时间 {_esc(tr.scanned_at[:19] if tr.scanned_at else '—')}</p>
      <div style="margin-top:12px">{checks_html}</div>
    </div>
    """


def _render_targets(report: BenchmarkReport) -> str:
    """渲染所有靶场目标的详细对比。"""
    parts = ['<h2>逐靶场目标对比详情</h2>']
    # 汇总表
    summary_rows = []
    for tr in report.targets:
        mx = tr.matrix
        m = tr.metrics
        status = '<span class="sev sev-low">成功</span>' if tr.error is None else '<span class="sev sev-critical">失败</span>'
        summary_rows.append(f"""
        <tr>
          <td>{_esc(tr.target.id)}</td>
          <td>{_esc(tr.target.name)}</td>
          <td class="code">{_esc(tr.target.url)}</td>
          <td>{status}</td>
          <td>{mx.tp}</td><td>{mx.fp}</td><td>{mx.tn}</td><td>{mx.fn}</td>
          <td>{_fmt_pct(m.precision)}</td>
          <td>{_fmt_pct(m.recall)}</td>
          <td>{_fmt_pct(m.f1)}</td>
        </tr>""")
    summary_table = f"""
    <div class="card">
      <h3>目标汇总</h3>
      <table>
        <thead><tr>
          <th>ID</th><th>名称</th><th>URL</th><th>状态</th>
          <th>TP</th><th>FP</th><th>TN</th><th>FN</th>
          <th>精确率</th><th>召回率</th><th>F1</th>
        </tr></thead>
        <tbody>{"".join(summary_rows)}</tbody>
      </table>
    </div>
    """
    parts.append(summary_table)
    for tr in report.targets:
        parts.append(_render_target_detail(tr))
    return "\n".join(parts)


def _render_false_positive_analysis(report: BenchmarkReport) -> str:
    """渲染误报率与误报明细分析。"""
    details = _false_positive_details(report)
    if not details:
        return (
            '<div class="card"><h2>误报分析</h2>'
            '<p class="sev sev-low">本次基准测试未产生误报 (FP=0)。</p></div>'
        )

    rows = []
    for d in details:
        sev = d.get("finding_severity", "")
        sev_html = (
            f'<span class="sev {_severity_class(sev)}">{_esc(_severity_cn(sev))}</span>'
            if sev
            else '<span class="muted">—</span>'
        )
        rows.append(f"""
        <tr>
          <td>{_esc(d['target_name'])}</td>
          <td>{_esc(_vuln_type_cn(d['vuln_type']))}</td>
          <td>{sev_html}</td>
          <td>{_esc(d['finding_title'])}</td>
          <td>{_esc(d['note'])}</td>
        </tr>""")

    return f"""
    <div class="card">
      <h2>误报分析</h2>
      <div class="summary-line">
        共 {len(details)} 项误报。误报率 FPR = {_fmt_pct(report.metrics.fpr)}
        （FP / (FP + TN)）。下表列出全部误报明细，用于定位扫描引擎的误报来源。
      </div>
      <table>
        <thead><tr>
          <th>靶场目标</th><th>漏洞类型</th><th>严重级别</th><th>误报标题</th><th>说明</th>
        </tr></thead>
        <tbody>{"".join(rows)}</tbody>
      </table>
    </div>
    """


def _render_false_negative_analysis(report: BenchmarkReport) -> str:
    """渲染漏报明细分析。"""
    details = _false_negative_details(report)
    if not details:
        return (
            '<div class="card"><h2>漏报分析</h2>'
            '<p class="sev sev-low">本次基准测试无漏报 (FN=0)，召回率 100%。</p></div>'
        )

    rows = []
    for d in details:
        severity = d.get("severity", "")
        if severity:
            sev_html = (
                f'<span class="sev {_severity_class(severity)}">'
                f"{_esc(_severity_cn(severity))}</span>"
            )
        else:
            sev_html = '<span class="muted">—</span>'
        target_name = d["target_name"]
        vuln_type = d["vuln_type"]
        description = d["description"]
        rows.append(f"""
        <tr>
          <td>{_esc(target_name)}</td>
          <td>{_esc(_vuln_type_cn(vuln_type))}</td>
          <td>{sev_html}</td>
          <td>{_esc(description)}</td>
        </tr>""")

    return f"""
    <div class="card">
      <h2>漏报分析</h2>
      <div class="summary-line">
        共 {len(details)} 项漏报。召回率 Recall = {_fmt_pct(report.metrics.recall)}
        （TP / (TP + FN)）。下表列出所有未检出的预期漏洞。
      </div>
      <table>
        <thead><tr>
          <th>靶场目标</th><th>漏洞类型</th><th>预期级别</th><th>预期漏洞描述</th>
        </tr></thead>
        <tbody>{"".join(rows)}</tbody>
      </table>
    </div>
    """


def generate_html_report(report: BenchmarkReport) -> str:
    """生成自包含的 HTML 基准对比报告。

    报告内联全部 CSS，无外部依赖，可直接用浏览器打开。

    Args:
        report: 完整的基准测试报告。

    Returns:
        HTML 字符串。
    """
    generated = datetime.fromisoformat(report.generated_at).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    ) if report.generated_at else datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    body = [
        _render_header(report),
        _render_confusion_matrix(report),
        _render_vuln_type_stats(report),
        _render_targets(report),
        _render_false_positive_analysis(report),
        _render_false_negative_analysis(report),
    ]

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>漏洞哨兵 11-S · 已知漏洞靶场基准对比报告</title>
<style>{_INLINE_CSS}</style>
</head>
<body>
<div class="container">
{''.join(body)}
<div class="card" style="text-align:center;color:#94a3b8;font-size:12px">
  漏洞哨兵 11-S 基准对比系统 ｜ 生成于 {_esc(generated)}<br>
  注：真实靶场的安全配置可能随时间变化，结果应结合时间戳解读。
</div>
</div>
</body>
</html>"""


def generate_json_report(report: BenchmarkReport) -> str:
    """生成 JSON 格式的基准对比报告（便于程序化消费）。"""
    import json

    return json.dumps(report.to_dict(), ensure_ascii=False, indent=2)
