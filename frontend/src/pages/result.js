/** SRC 级扫描结果页 */

import { escapeHtml, getScoreColor, getScoreGradient, getRiskColor, getRiskClass, formatDate, copyToClipboard } from '../utils.js';
import { showToast } from '../components/Toast.js';
import { exportSRCReport, verifyReproduce, findingFeedback, isLoggedIn } from '../api.js';

const SEVERITY_ORDER = { critical: 0, high: 1, medium: 2, low: 3, info: 4 };
const SEVERITY_LABEL = { critical: '严重', high: '高危', medium: '中危', low: '低危', info: '信息' };
const SEVERITY_ZH_CLASS = { critical: 'high', high: 'high', medium: 'medium', low: 'low', info: 'info' };

let _currentFindings = [];
let _selectedIndex = 0;
let _currentFixTab = 'generic';
let _currentScanId = null;
let _currentUrl = '';

/**
 * 判断数据是否符合 SRC 级报告格式
 */
export function isSRCFormat(data) {
  if (!data || !Array.isArray(data.findings)) return false;
  if (data.findings.length === 0) return false;
  const first = data.findings[0];
  return first && typeof first === 'object' &&
    'id' in first && 'severity' in first && 'evidence' in first;
}

/**
 * 渲染 SRC 级扫描结果
 */
export function renderSRCResult(data) {
  _currentFindings = sortFindings(data.findings || []);
  _selectedIndex = 0;
  _currentFixTab = 'generic';
  _currentScanId = data.scan_id || null;
  _currentUrl = data.url || '';

  const score = typeof data.score === 'number' ? data.score : (parseInt(data.score, 10) || 0);
  const summary = data.summary || { critical: 0, high: 0, medium: 0, low: 0, info: 0, total: 0 };
  const riskLevel = data.risk_level || '未知';
  const url = data.url || '';

  const container = document.getElementById('result-content') || document.getElementById('result-container');
  if (!container) {
    console.error('result-content not found');
    return;
  }

  let html = '';
  // 顶部概览
  html += renderHeader(score, riskLevel, summary, url, data);

  // 主体：左列表 + 右详情
  html += '<div class="src-result-layout">';
  html += '<div class="src-result-sidebar">' + renderFindingList(_currentFindings, _selectedIndex) + '</div>';
  html += '<div class="src-result-detail" id="src-detail-panel">' + renderFindingDetail(_currentFindings[0], 0) + '</div>';
  html += '</div>';

  container.innerHTML = html;
  bindFindingListEvents();
}

function sortFindings(findings) {
  return findings.slice().sort((a, b) => {
    const sa = SEVERITY_ORDER[(a.severity || '').toLowerCase()] ?? 99;
    const sb = SEVERITY_ORDER[(b.severity || '').toLowerCase()] ?? 99;
    if (sa !== sb) return sa - sb;
    return (b.severity_score || 0) - (a.severity_score || 0);
  });
}

function renderHeader(score, riskLevel, summary, url, data) {
  const gradient = getScoreGradient(score);
  const scoreColor = getScoreColor(score);
  const riskClass = getRiskClass(riskLevel);
  const duration = data.duration_ms ? `<span class="meta-item">耗时 ${data.duration_ms}ms</span>` : '';
  const scanId = data.scan_id ? `<span class="meta-item">扫描 #${data.scan_id}</span>` : '';
  const reportId = data.report_share_id ? `<span class="meta-item">报告 ${escapeHtml(data.report_share_id)}</span>` : '';
  const exportBtn = data.scan_id && isLoggedIn()
    ? `<button class="src-export-btn" id="src-export-markdown" title="导出 SRC 格式 Markdown 报告">导出 SRC 报告</button>`
    : '';

  return `
    <div class="src-report-header fade-in-up">
      <div class="src-score-wrap">
        <div class="src-score-ring" style="background:${gradient};color:#fff">
          <div class="src-score-value">${score}</div>
          <div class="src-score-label">安全评分</div>
        </div>
      </div>
      <div class="src-report-meta">
        <div class="src-report-title-row">
          <span class="risk-badge ${riskClass}">${escapeHtml(riskLevel)}</span>
          <span class="src-report-url">${escapeHtml(url)}</span>
        </div>
        <div class="src-report-stats">
          <div class="src-stat critical"><div class="num">${summary.critical || 0}</div><div class="label">严重</div></div>
          <div class="src-stat high"><div class="num">${summary.high || 0}</div><div class="label">高危</div></div>
          <div class="src-stat medium"><div class="num">${summary.medium || 0}</div><div class="label">中危</div></div>
          <div class="src-stat low"><div class="num">${summary.low || 0}</div><div class="label">低危</div></div>
          <div class="src-stat info"><div class="num">${summary.info || 0}</div><div class="label">信息</div></div>
          <div class="src-stat total"><div class="num">${summary.total || 0}</div><div class="label">总计</div></div>
        </div>
        <div class="src-report-submeta">
          ${scanId}${duration}${reportId}
          <span class="meta-item">发现于 ${formatDate(data.discovered_at || new Date().toISOString())}</span>
        </div>
        <div class="src-report-actions">
          ${exportBtn}
        </div>
      </div>
    </div>
  `;
}

function renderFindingList(findings, selectedIndex) {
  let html = '<div class="src-list-header">漏洞列表 <span class="src-list-count">' + findings.length + '</span></div>';
  html += '<div class="src-list-items">';
  if (findings.length === 0) {
    html += '<div class="src-empty">未发现漏洞</div>';
  } else {
    findings.forEach((f, i) => {
      const sev = (f.severity || 'info').toLowerCase();
      const cls = SEVERITY_ZH_CLASS[sev] || 'info';
      const active = i === selectedIndex ? 'active' : '';
      const param = f.parameter ? `<code class="src-list-param">${escapeHtml(f.parameter)}</code>` : '';
      const typeLabel = f.type ? `<span class="src-list-type">${escapeHtml(f.type.toUpperCase())}</span>` : '';
      const host = f.url ? new URL(f.url, window.location.href).hostname : '';
      const path = f.url ? new URL(f.url, window.location.href).pathname : '';
      html += `
        <div class="src-list-item ${active} ${cls}" data-index="${i}">
          <div class="src-list-row top">
            <span class="src-sev-badge ${cls}">${SEVERITY_LABEL[sev]}</span>
            <span class="src-list-title" title="${escapeAttr(f.title || '')}">${escapeHtml(f.title || '未命名漏洞')}</span>
          </div>
          <div class="src-list-row meta">
            ${typeLabel}
            ${param}
            <span class="src-list-host" title="${escapeAttr(f.url || '')}">${escapeHtml(host)}${escapeHtml(path)}</span>
            <span class="src-list-confidence">${escapeHtml(f.confidence || 'medium')}</span>
          </div>
        </div>
      `;
    });
  }
  html += '</div>';
  return html;
}

function renderFindingDetail(finding, index) {
  if (!finding) {
    return '<div class="src-empty-detail">请从左侧选择漏洞查看详情</div>';
  }
  const sev = (finding.severity || 'info').toLowerCase();
  const cls = SEVERITY_ZH_CLASS[sev] || 'info';
  const label = SEVERITY_LABEL[sev] || '信息';
  const evidence = finding.evidence || {};
  const locDetail = finding.location_detail || {};
  const statusMap = { open: '待处理', confirmed: '已确认', false_positive: '误报', fixed: '已修复' };
  const status = finding.status || 'open';

  let html = '<div class="src-detail-card fade-in-up">';

  // 标题行
  html += `<div class="src-detail-header">
    <div class="src-detail-title-row">
      <span class="src-detail-severity ${cls}">${label}</span>
      <h2 class="src-detail-title">${escapeHtml(finding.title || '未命名漏洞')}</h2>
      <span class="src-detail-status ${status}">${statusMap[status] || status}</span>
    </div>
    <div class="src-detail-subtitle">
      <code class="src-detail-id">${escapeHtml(finding.id || '')}</code>
      <span class="src-detail-type">${escapeHtml(finding.type || '').toUpperCase()}</span>
      ${finding.cwe_id ? `<span class="src-detail-cwe" title="Common Weakness Enumeration">${escapeHtml(finding.cwe_id)}</span>` : ''}
      ${finding.owasp_category ? `<span class="src-detail-owasp">${escapeHtml(finding.owasp_category)}</span>` : ''}
      ${finding.cvss_score ? `<span class="src-detail-cvss" title="${escapeHtml(finding.cvss_vector || '')}">CVSS ${finding.cvss_score}</span>` : ''}
      ${finding.severity_score ? `<span class="src-detail-score">评分 ${finding.severity_score}/10</span>` : ''}
      <span class="src-detail-confidence">置信度 ${escapeHtml(finding.confidence || 'medium')}</span>
    </div>
  </div>`;

  // Tab 导航
  html += `<div class="src-detail-tabs">
    <button class="src-detail-tab active" data-tab="overview">概览</button>
    <button class="src-detail-tab" data-tab="evidence">请求 / 响应</button>
    <button class="src-detail-tab" data-tab="fix">修复</button>
  </div>`;

  // 概览面板
  html += `<div class="src-detail-panel active" data-panel="overview">`;

  // 描述
  html += `<div class="src-detail-section">
    <div class="src-section-title">漏洞描述</div>
    <div class="src-section-body">${escapeHtml(finding.description || '暂无描述')}</div>
  </div>`;

  // 影响
  html += `<div class="src-detail-section">
    <div class="src-section-title">实际影响</div>
    <div class="src-section-body">${escapeHtml(finding.impact || '暂无影响说明')}</div>
  </div>`;

  // 位置
  html += `<div class="src-detail-section">
    <div class="src-section-title">精准位置</div>
    <div class="src-section-body">
      <div class="src-kv"><span class="src-k">URL</span><code class="src-v">${escapeHtml(locDetail.url || finding.url || '')}</code></div>
      ${locDetail.method ? `<div class="src-kv"><span class="src-k">方法</span><code class="src-v">${escapeHtml(locDetail.method)}</code></div>` : ''}
      ${(locDetail.parameter || finding.parameter) ? `<div class="src-kv"><span class="src-k">参数</span><code class="src-v">${escapeHtml(locDetail.parameter || finding.parameter)}</code></div>` : ''}
      ${locDetail.parameter_type ? `<div class="src-kv"><span class="src-k">参数类型</span><code class="src-v">${escapeHtml(locDetail.parameter_type)}</code></div>` : ''}
      ${locDetail.code_location ? `<div class="src-kv"><span class="src-k">代码位置</span><code class="src-v">${escapeHtml(locDetail.code_location)}</code></div>` : ''}
      ${locDetail.snippet ? `<div class="src-kv"><span class="src-k">上下文</span><span class="src-v">${escapeHtml(locDetail.snippet)}</span></div>` : ''}
      ${(!locDetail.url && finding.location) ? `<div class="src-kv"><span class="src-k">位置</span><span class="src-v">${escapeHtml(finding.location)}</span></div>` : ''}
    </div>
  </div>`;

  // 复现步骤
  if (Array.isArray(finding.reproduce_steps) && finding.reproduce_steps.length > 0) {
    html += `<div class="src-detail-section">
      <div class="src-section-title">复现步骤</div>
      <ol class="src-repro-steps">`;
    finding.reproduce_steps.forEach((step) => {
      html += `<li>${escapeHtml(step)}</li>`;
    });
    html += `</ol></div>`;
  }

  html += `</div>`;

  // 证据面板
  html += `<div class="src-detail-panel" data-panel="evidence">`;
  html += renderEvidenceSection(evidence, finding);
  html += `</div>`;

  // 修复面板
  html += `<div class="src-detail-panel" data-panel="fix">`;
  // 修复建议
  html += `<div class="src-detail-section">
    <div class="src-section-title">修复建议</div>
    <div class="src-section-body">${escapeHtml(finding.fix_suggestion || '暂无修复建议')}</div>
  </div>`;
  // 修复代码 tabs
  html += renderFixCodeSection(finding.fix_code || {});
  html += `</div>`;

  // 参考链接
  if (Array.isArray(finding.references) && finding.references.length > 0) {
    html += `<div class="src-detail-section">
      <div class="src-section-title">参考链接</div>
      <ul class="src-references">`;
    finding.references.forEach((ref) => {
      html += `<li><a href="${escapeAttr(ref)}" target="_blank" rel="noopener">${escapeHtml(ref)}</a></li>`;
    });
    html += `</ul></div>`;
  }

  // 操作按钮
  if (_currentScanId && isLoggedIn()) {
    html += `<div class="src-detail-actions">
      <button class="src-action-btn verify" data-action="verify" data-finding-id="${escapeAttr(finding.id || '')}">验证复现</button>
      <button class="src-action-btn false-positive" data-action="fp" data-finding-id="${escapeAttr(finding.id || '')}">标记误报</button>
      <button class="src-action-btn confirm" data-action="confirm" data-finding-id="${escapeAttr(finding.id || '')}">确认漏洞</button>
    </div>`;
  }

  // 元信息
  html += `<div class="src-detail-footer">
    <span>发现时间：${formatDate(finding.discovered_at || '')}</span>
  </div>`;

  html += '</div>';
  return html;
}

function renderEvidenceSection(evidence, finding) {
  const hasRequest = !!evidence.request;
  const hasResponse = !!evidence.response;
  const hasPayload = !!evidence.payload;
  const hasScreenshot = !!evidence.screenshot;
  const hasNotes = !!evidence.notes;
  const hasSignature = !!evidence.matched_signature;

  let html = `<div class="src-detail-section">`;

  if (hasPayload || hasSignature || hasNotes) {
    html += `<div class="src-section-title">命中信息</div>
    <div class="src-section-body src-evidence-meta">`;
    if (hasPayload) {
      html += `<div class="src-evidence-row">
        <span class="src-evidence-label">Payload</span>
        <code class="src-payload">${escapeHtml(evidence.payload)}</code>
        <button class="src-copy-btn" data-copy="${escapeAttr(evidence.payload)}">复制</button>
      </div>`;
    }
    if (hasSignature) {
      html += `<div class="src-evidence-row">
        <span class="src-evidence-label">命中签名</span>
        <code class="src-signature">${escapeHtml(evidence.matched_signature)}</code>
      </div>`;
    }
    if (hasNotes) {
      html += `<div class="src-evidence-row">
        <span class="src-evidence-label">备注</span>
        <span>${escapeHtml(evidence.notes)}</span>
      </div>`;
    }
    html += `</div>`;
  }

  if (hasRequest || hasResponse) {
    html += `<div class="src-section-title">HTTP 流量</div>
    <div class="src-traffic-viewer">`;
    if (hasRequest) {
      html += `<div class="src-traffic-panel">
        <div class="src-traffic-header">
          <span>请求</span>
          <button class="src-copy-btn" data-copy="${escapeAttr(evidence.request)}">复制</button>
        </div>
        <pre><code>${escapeHtml(evidence.request)}</code></pre>
      </div>`;
    }
    if (hasResponse) {
      html += `<div class="src-traffic-panel">
        <div class="src-traffic-header">
          <span>响应</span>
          <button class="src-copy-btn" data-copy="${escapeAttr(evidence.response)}">复制</button>
        </div>
        <pre><code>${escapeHtml(evidence.response)}</code></pre>
      </div>`;
    }
    html += `</div>`;
  }

  if (hasScreenshot) {
    html += `<div class="src-screenshot-row">
      <span class="src-evidence-label">截图</span>
      <img src="${escapeAttr(evidence.screenshot)}" alt="证据截图" loading="lazy">
    </div>`;
  }

  if (!hasRequest && !hasResponse && !hasPayload && !hasScreenshot && !hasNotes && !hasSignature) {
    html += `<div class="src-section-title">技术证据</div>
    <div class="src-section-body"><div class="src-no-evidence">无详细技术证据</div></div>`;
  }

  html += `</div>`;
  return html;
}

function renderFixCodeSection(fixCode) {
  const platforms = [
    { key: 'nginx', label: 'Nginx' },
    { key: 'apache', label: 'Apache' },
    { key: 'express', label: 'Express' },
    { key: 'flask', label: 'Flask' },
    { key: 'spring_boot', label: 'Spring Boot' },
    { key: 'cloudflare', label: 'Cloudflare' },
    { key: 'generic', label: '通用' },
  ];
  const available = platforms.filter((p) => fixCode[p.key]);
  if (available.length === 0) {
    return '';
  }

  let html = `<div class="src-detail-section">
    <div class="src-section-title">修复代码</div>
    <div class="src-fix-tabs">`;
  available.forEach((p) => {
    const active = p.key === _currentFixTab ? 'active' : '';
    html += `<button class="src-fix-tab ${active}" data-tab="${p.key}">${p.label}</button>`;
  });
  html += `</div>`;

  available.forEach((p) => {
    const active = p.key === _currentFixTab ? 'active' : 'hidden';
    html += `<div class="src-fix-panel ${active}" data-panel="${p.key}">
      <pre><code>${escapeHtml(fixCode[p.key])}</code></pre>
      <button class="src-copy-btn" data-copy="${escapeAttr(fixCode[p.key])}">复制代码</button>
    </div>`;
  });

  html += `</div>`;
  return html;
}

function bindFindingListEvents() {
  document.querySelectorAll('.src-list-item').forEach((el) => {
    el.addEventListener('click', function() {
      const idx = parseInt(this.dataset.index, 10);
      selectFinding(idx);
    });
  });

  document.querySelectorAll('.src-detail-tab').forEach((el) => {
    el.addEventListener('click', function() {
      const tab = this.dataset.tab;
      const card = this.closest('.src-detail-card');
      if (!card) return;
      card.querySelectorAll('.src-detail-tab').forEach((t) => t.classList.remove('active'));
      this.classList.add('active');
      card.querySelectorAll('.src-detail-panel').forEach((p) => {
        p.classList.toggle('active', p.dataset.panel === tab);
      });
    });
  });

  document.querySelectorAll('.src-fix-tab').forEach((el) => {
    el.addEventListener('click', function() {
      _currentFixTab = this.dataset.tab;
      document.querySelectorAll('.src-fix-tab').forEach((t) => t.classList.remove('active'));
      this.classList.add('active');
      document.querySelectorAll('.src-fix-panel').forEach((p) => {
        p.classList.toggle('active', p.dataset.panel === _currentFixTab);
        p.classList.toggle('hidden', p.dataset.panel !== _currentFixTab);
      });
    });
  });

  document.querySelectorAll('.src-copy-btn').forEach((btn) => {
    btn.addEventListener('click', function(e) {
      e.stopPropagation();
      const text = this.dataset.copy || '';
      copyToClipboard(text).then(() => showToast('已复制到剪贴板'));
    });
  });

  document.querySelectorAll('.src-export-btn').forEach((btn) => {
    btn.addEventListener('click', onExportSRCReport);
  });

  document.querySelectorAll('.src-action-btn').forEach((btn) => {
    btn.addEventListener('click', onFindingAction);
  });
}

async function onExportSRCReport() {
  if (!_currentScanId) return;
  try {
    const resp = await exportSRCReport({ scan_id: _currentScanId, format: 'markdown' });
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `src-report-${_currentScanId}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast('SRC 报告已开始下载');
  } catch (e) {
    showToast('导出失败：' + (e && e.message ? e.message : '未知错误'));
  }
}

async function onFindingAction(e) {
  const btn = e.currentTarget;
  const action = btn.dataset.action;
  const findingId = btn.dataset.findingId;
  const finding = _currentFindings.find((f) => f.id === findingId);
  if (!_currentScanId || !finding) return;

  if (action === 'verify') {
    btn.textContent = '验证中...';
    btn.disabled = true;
    try {
      const res = await verifyReproduce({ scan_id: _currentScanId, finding_id: findingId, url: finding.url || _currentUrl });
      if (res && res.success) {
        const status = res.reproducible === true ? '仍可复现' : (res.reproducible === false ? '已无法复现' : '需人工复核');
        showToast(`验证结果：${status}`);
      } else {
        showToast('验证失败：' + (res && res.error ? res.error : '未知错误'));
      }
    } catch (e) {
      showToast('验证请求失败');
    } finally {
      btn.textContent = '验证复现';
      btn.disabled = false;
    }
    return;
  }

  try {
    const res = await findingFeedback({
      scan_id: _currentScanId,
      finding_name: finding.title || findingId,
      finding_type: finding.type || '',
      is_false_positive: action === 'fp',
      is_confirmed: action === 'confirm',
    });
    if (res && res.success) {
      showToast(action === 'fp' ? '已标记为误报' : '已确认漏洞');
    } else {
      showToast('反馈提交失败：' + (res && res.error ? res.error : '未知错误'));
    }
  } catch (e) {
    showToast('反馈请求失败');
  }
}

function selectFinding(index) {
  _selectedIndex = index;
  document.querySelectorAll('.src-list-item').forEach((el, i) => {
    el.classList.toggle('active', i === index);
  });
  const detail = document.getElementById('src-detail-panel');
  if (detail) {
    detail.innerHTML = renderFindingDetail(_currentFindings[index], index);
    bindFindingListEvents();
  }
}

/**
 * 注入 SRC 结果页专用样式（仅当页面渲染时插入一次）
 */
export function injectSRCStyles() {
  if (document.getElementById('src-result-styles')) return;
  const style = document.createElement('style');
  style.id = 'src-result-styles';
  style.textContent = `
    .src-report-header { display:flex; gap:20px; align-items:center; background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius); padding:20px; margin-bottom:16px; }
    .src-score-wrap { flex:0 0 auto; }
    .src-score-ring { width:110px; height:110px; border-radius:50%; display:flex; flex-direction:column; align-items:center; justify-content:center; border:3px solid rgba(255,255,255,0.1); }
    .src-score-value { font-size:34px; font-weight:800; line-height:1; }
    .src-score-label { font-size:11px; opacity:0.85; margin-top:4px; }
    .src-report-meta { flex:1; min-width:0; }
    .src-report-title-row { display:flex; align-items:center; gap:12px; flex-wrap:wrap; margin-bottom:10px; }
    .src-report-url { font-family:var(--font); font-size:13px; color:var(--text-secondary); word-break:break-all; }
    .src-report-stats { display:flex; gap:10px; flex-wrap:wrap; margin-bottom:12px; }
    .src-stat { min-width:64px; text-align:center; padding:8px 10px; border-radius:var(--radius-sm); background:var(--bg-secondary); border:1px solid var(--border-light); }
    .src-stat .num { font-size:18px; font-weight:700; }
    .src-stat .label { font-size:11px; color:var(--text-secondary); }
    .src-stat.critical .num { color:#c75450; }
    .src-stat.high .num { color:#f0a732; }
    .src-stat.medium .num { color:#f0a732; }
    .src-stat.low .num { color:#73c990; }
    .src-stat.info .num { color:#808080; }
    .src-stat.total .num { color:var(--primary-light); }
    .src-report-submeta { display:flex; gap:12px; flex-wrap:wrap; font-size:12px; color:var(--text-secondary); }
    .meta-item { background:var(--token-bg); padding:3px 8px; border-radius:var(--radius-xs); }
    .src-report-actions { margin-top:12px; }
    .src-export-btn { background:var(--primary); color:#fff; border:none; padding:6px 14px; border-radius:var(--radius-xs); font-size:12px; cursor:pointer; }
    .src-export-btn:hover { background:var(--primary-light); }

    .src-result-layout { display:grid; grid-template-columns:380px 1fr; gap:16px; }
    @media (max-width:900px) { .src-result-layout { grid-template-columns:1fr; } }

    .src-result-sidebar { background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius); overflow:hidden; max-height:calc(100vh - 220px); display:flex; flex-direction:column; }
    .src-list-header { padding:12px 14px; border-bottom:1px solid var(--border-light); font-weight:700; font-size:13px; display:flex; align-items:center; justify-content:space-between; }
    .src-list-count { background:var(--primary); color:#fff; font-size:11px; padding:2px 8px; border-radius:10px; }
    .src-list-items { overflow-y:auto; flex:1; padding:6px; }
    .src-list-item { padding:10px 12px; border-radius:var(--radius-sm); cursor:pointer; border-left:3px solid transparent; margin-bottom:4px; transition:background .12s; }
    .src-list-item:hover { background:var(--bg-secondary); }
    .src-list-item.active { background:var(--verify-selected); border-left-color:var(--primary); }
    .src-list-item.critical { border-left-color:#c75450; }
    .src-list-item.high { border-left-color:#c75450; }
    .src-list-item.medium { border-left-color:#f0a732; }
    .src-list-item.low { border-left-color:#73c990; }
    .src-list-item.info { border-left-color:#808080; }
    .src-list-row { display:flex; align-items:center; gap:8px; }
    .src-list-row.top { align-items:flex-start; }
    .src-list-row.meta { margin-top:6px; flex-wrap:wrap; font-size:11px; }
    .src-sev-badge { font-size:10px; font-weight:700; padding:2px 7px; border-radius:var(--radius-xs); color:#fff; white-space:nowrap; flex:0 0 auto; }
    .src-sev-badge.critical { background:#c75450; }
    .src-sev-badge.high { background:#c75450; }
    .src-sev-badge.medium { background:#f0a732; color:#000; }
    .src-sev-badge.low { background:#73c990; color:#000; }
    .src-sev-badge.info { background:#808080; }
    .src-list-title { font-size:13px; font-weight:600; color:var(--text-primary); flex:1; word-break:break-word; line-height:1.4; }
    .src-list-type { font-size:10px; background:var(--token-bg); padding:2px 6px; border-radius:var(--radius-xs); color:var(--text-secondary); }
    .src-list-param { font-size:10px; background:rgba(75,110,175,0.15); color:var(--primary-light); padding:2px 6px; border-radius:var(--radius-xs); }
    .src-list-host { color:var(--text-secondary); font-family:var(--font); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:180px; }
    .src-list-confidence { font-size:11px; color:var(--text-secondary); margin-left:auto; text-transform:uppercase; }

    .src-result-detail { max-height:calc(100vh - 220px); overflow-y:auto; }
    .src-detail-card { background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius); padding:0; display:flex; flex-direction:column; }
    .src-detail-header { border-bottom:1px solid var(--border-light); padding:16px 18px 14px; }
    .src-detail-title-row { display:flex; align-items:flex-start; gap:10px; margin-bottom:10px; }
    .src-detail-severity { font-size:11px; font-weight:700; padding:3px 10px; border-radius:var(--radius-xs); color:#fff; white-space:nowrap; }
    .src-detail-severity.critical { background:#c75450; }
    .src-detail-severity.high { background:#c75450; }
    .src-detail-severity.medium { background:#f0a732; color:#000; }
    .src-detail-severity.low { background:#73c990; color:#000; }
    .src-detail-severity.info { background:#808080; }
    .src-detail-title { font-size:17px; font-weight:700; margin:0; color:var(--text-primary); flex:1; line-height:1.4; }
    .src-detail-status { font-size:11px; padding:2px 8px; border-radius:var(--radius-xs); margin-left:auto; border:1px solid var(--border-light); }
    .src-detail-status.open { background:rgba(240,167,50,0.12); color:#f0a732; border-color:rgba(240,167,50,0.3); }
    .src-detail-status.confirmed { background:rgba(199,84,80,0.15); color:#c75450; border-color:rgba(199,84,80,0.3); }
    .src-detail-status.false_positive { background:rgba(128,128,128,0.15); color:#808080; border-color:rgba(128,128,128,0.3); }
    .src-detail-status.fixed { background:rgba(115,201,144,0.15); color:#73c990; border-color:rgba(115,201,144,0.3); }
    .src-detail-subtitle { display:flex; gap:10px; flex-wrap:wrap; align-items:center; font-size:12px; color:var(--text-secondary); }
    .src-detail-id { background:var(--token-bg); padding:2px 6px; border-radius:var(--radius-xs); }
    .src-detail-type { color:var(--primary-light); font-weight:600; }
    .src-detail-cwe { background:rgba(199,84,80,0.12); color:#e08e8a; padding:2px 8px; border-radius:var(--radius-xs); }
    .src-detail-owasp { background:rgba(75,110,175,0.12); color:var(--primary-light); padding:2px 8px; border-radius:var(--radius-xs); }
    .src-detail-cvss { background:rgba(240,167,50,0.12); color:#f0a732; padding:2px 8px; border-radius:var(--radius-xs); }
    .src-detail-score { background:rgba(115,201,144,0.12); color:#73c990; padding:2px 8px; border-radius:var(--radius-xs); }

    .src-detail-tabs { display:flex; border-bottom:1px solid var(--border-light); background:var(--bg-secondary); }
    .src-detail-tab { background:transparent; border:none; border-bottom:2px solid transparent; color:var(--text-secondary); padding:10px 16px; font-size:12px; font-weight:600; cursor:pointer; }
    .src-detail-tab:hover { color:var(--text-primary); }
    .src-detail-tab.active { color:var(--primary-light); border-bottom-color:var(--primary); background:rgba(75,110,175,0.08); }
    .src-detail-panel { display:none; padding:18px; }
    .src-detail-panel.active { display:block; }

    .src-detail-section { margin-bottom:18px; }
    .src-section-title { font-size:12px; font-weight:700; color:var(--text-primary); margin-bottom:8px; display:flex; align-items:center; gap:6px; text-transform:uppercase; letter-spacing:0.3px; }
    .src-section-body { font-size:13px; color:var(--text); line-height:1.7; }
    .src-kv { display:flex; gap:10px; margin-bottom:6px; align-items:flex-start; }
    .src-k { min-width:60px; color:var(--text-secondary); font-size:12px; }
    .src-v { flex:1; word-break:break-all; }
    .src-repro-steps { padding-left:18px; margin:0; }
    .src-repro-steps li { margin-bottom:6px; }

    .src-evidence-row { display:flex; align-items:center; gap:10px; margin-bottom:10px; flex-wrap:wrap; }
    .src-evidence-label { font-size:12px; color:var(--text-secondary); min-width:60px; }
    .src-payload { background:#3b0d0d; color:#fecaca; padding:6px 10px; border-radius:var(--radius-xs); border:1px solid rgba(199,84,80,0.35); font-size:12px; word-break:break-all; flex:1; }
    .src-signature { background:#2b2b2b; color:#bbbbbb; padding:6px 10px; border-radius:var(--radius-xs); border:1px solid var(--border-light); font-size:12px; word-break:break-all; flex:1; font-family:var(--font); }
    .src-traffic-viewer { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
    @media (max-width:1100px) { .src-traffic-viewer { grid-template-columns:1fr; } }
    .src-traffic-panel { background:var(--code-bg); border:1px solid var(--border-light); border-radius:var(--radius-sm); overflow:hidden; display:flex; flex-direction:column; min-height:180px; }
    .src-traffic-header { display:flex; align-items:center; justify-content:space-between; padding:8px 12px; background:var(--bg-secondary); border-bottom:1px solid var(--border-light); font-size:12px; font-weight:600; color:var(--text-secondary); }
    .src-traffic-header .src-copy-btn { margin:0; }
    .src-traffic-panel pre { margin:0; padding:12px; overflow:auto; max-height:420px; flex:1; }
    .src-traffic-panel code { font-family:var(--font); font-size:12px; color:var(--code-color); white-space:pre-wrap; word-break:break-all; }
    .src-screenshot-row img { max-width:100%; border:1px solid var(--border-light); border-radius:var(--radius-sm); margin-top:6px; }
    .src-no-evidence { color:var(--text-secondary); font-size:12px; }

    .src-fix-tabs { display:flex; gap:6px; flex-wrap:wrap; margin-bottom:10px; }
    .src-fix-tab { background:var(--bg-secondary); border:1px solid var(--border-light); color:var(--text-secondary); padding:5px 12px; border-radius:var(--radius-xs); cursor:pointer; font-size:12px; }
    .src-fix-tab.active { background:var(--primary); color:#fff; border-color:var(--primary); }
    .src-fix-panel { background:var(--code-bg); border:1px solid var(--border-light); border-radius:var(--radius-sm); padding:12px; position:relative; }
    .src-fix-panel.hidden { display:none; }
    .src-fix-panel pre { margin:0; overflow:auto; max-height:360px; }
    .src-fix-panel code { font-family:var(--font); font-size:12px; color:var(--code-color); white-space:pre-wrap; word-break:break-all; }

    .src-copy-btn { background:rgba(75,110,175,0.15); border:1px solid rgba(75,110,175,0.3); color:var(--primary-light); padding:4px 10px; border-radius:var(--radius-xs); cursor:pointer; font-size:11px; }
    .src-copy-btn:hover { background:var(--primary); color:#fff; }
    .src-references { padding-left:18px; margin:0; }
    .src-references li { margin-bottom:6px; word-break:break-all; }
    .src-detail-actions { display:flex; gap:10px; flex-wrap:wrap; padding:0 18px 18px; }
    .src-action-btn { background:var(--bg-secondary); border:1px solid var(--border-light); color:var(--text-secondary); padding:6px 14px; border-radius:var(--radius-xs); cursor:pointer; font-size:12px; }
    .src-action-btn:hover { border-color:var(--primary); color:var(--primary-light); }
    .src-action-btn.verify { background:rgba(75,110,175,0.12); color:var(--primary-light); border-color:rgba(75,110,175,0.3); }
    .src-action-btn.false-positive { background:rgba(115,201,144,0.12); color:#73c990; border-color:rgba(115,201,144,0.3); }
    .src-action-btn.confirm { background:rgba(199,84,80,0.12); color:#c75450; border-color:rgba(199,84,80,0.3); }
    .src-detail-footer { font-size:12px; color:var(--text-secondary); border-top:1px solid var(--border-light); padding:12px 18px; }
    .src-empty { padding:30px; text-align:center; color:var(--text-secondary); }
    .src-empty-detail { padding:40px; text-align:center; color:var(--text-secondary); background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius); }
  `;
  document.head.appendChild(style);
}

export function init() {
  injectSRCStyles();
}
