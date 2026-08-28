/** SRC 级扫描结果页 */

import { escapeHtml, escapeAttr, getScoreColor, getScoreGradient, getRiskColor, getRiskClass, formatDate, copyToClipboard } from '../utils.js';
import { showToast } from '../components/Toast.js';
import { exportSRCReport, verifyReproduce, findingFeedback, createTicket, isLoggedIn } from '../api.js';

const navigateTo = (...args) => typeof window.navigateTo === 'function' && window.navigateTo(...args);

const SEVERITY_ORDER = { critical: 0, high: 1, medium: 2, low: 3, info: 4 };
const SEVERITY_LABEL = { critical: '严重', high: '高危', medium: '中危', low: '低危', info: '信息' };
const SEVERITY_ZH_CLASS = { critical: 'high', high: 'high', medium: 'medium', low: 'low', info: 'info' };
const VULN_TYPE_LABELS = {
  sqli: 'SQL 注入',
  xss: '跨站脚本',
  csrf: '跨站请求伪造',
  ssti: '模板注入',
  open_redirect: '开放重定向',
  cmdi: '命令注入',
  traversal: '路径遍历',
  deserialization: '不安全反序列化',
  ssrf: '服务端请求伪造',
  xxe: 'XML 外部实体注入',
  idor: '不安全直接对象引用',
  info_leak: '信息泄露',
  auth_weakness: '认证薄弱',
  bruteforce_protection: '防爆破不足',
  unauthorized_access: '未授权访问',
  api_auth_missing: 'API 鉴权缺失',
  sensitive_config_exposure: '敏感配置泄露',
  clickjacking: '点击劫持',
  file_upload: '不安全文件上传',
  logic_bypass: '业务逻辑绕过'
};

let _currentFindings = [];
let _selectedIndex = 0;
let _currentFixTab = 'generic';
let _currentScanId = null;
let _currentUrl = '';
let _hideLikelyFp = false;
let _currentScore = 0;
let _currentSummary = { critical: 0, high: 0, medium: 0, low: 0, info: 0, total: 0, fp_count: 0 };

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
  _hideLikelyFp = false;
  _currentScanId = data.scan_id || null;
  _currentUrl = data.url || '';
  _currentScore = typeof data.score === 'number' ? data.score : (parseInt(data.score, 10) || 0);
  _currentSummary = data.summary || { critical: 0, high: 0, medium: 0, low: 0, info: 0, total: 0, fp_count: 0 };

  const score = typeof data.score === 'number' ? data.score : (parseInt(data.score, 10) || 0);
  const summary = data.summary || { critical: 0, high: 0, medium: 0, low: 0, info: 0, total: 0 };
  const riskLevel = data.risk_level || '未知';
  const url = data.url || '';

  const container = document.getElementById('result-content') || document.getElementById('result-container');
  if (!container) {
    setTimeout(() => renderSRCResult(data), 0);
    return;
  }

  let html = '';
  // 顶部概览
  html += renderHeader(score, riskLevel, summary, url, data);

  // 扫描可信度详情面板
  if (data.quality && data.quality.overall_score !== undefined) {
    html += renderQualityPanel(data.quality, data.dedup_stats);
  }

  // 主体：左列表 + 右详情
  const firstFinding = _currentFindings.length > 0 ? _currentFindings[0] : null;
  html += '<div class="src-result-layout">';
  html += '<div class="src-result-sidebar">' + renderFindingList(_currentFindings, _selectedIndex) + '</div>';
  html += '<div class="src-result-detail" id="src-detail-panel">' + renderFindingDetail(firstFinding, 0) + '</div>';
  html += '</div>';

  container.innerHTML = html;
  bindResultPageEvents();
  bindQualityPanelEvents();
}

function renderQualityPanel(quality, dedupStats) {
  const qScore = quality.overall_score || 0;
  const qColor = qScore >= 80 ? '#73c990' : qScore >= 60 ? '#f0a732' : '#c75450';
  const coverage = quality.coverage_score || 0;
  const reliability = quality.reliability_score || 0;
  const depth = quality.depth_score || 0;
  const recommendations = quality.recommendations || [];

  const coverageBreakdown = quality.coverage_breakdown || {};
  const reliabilityBreakdown = quality.reliability_breakdown || {};
  const typesDetected = coverageBreakdown.types_detected || [];

  // 去重统计
  const dedup = dedupStats || {};
  const dedupHtml = dedup.original_count !== undefined
    ? `<div class="src-quality-dedup">
         <span class="src-quality-label">去重统计</span>
         <span class="src-quality-stat">原始 ${dedup.original_count || 0}</span>
         <span class="src-quality-arrow">→</span>
         <span class="src-quality-stat highlight">${dedup.deduplicated_count || 0}</span>
         ${dedup.duplicate_count > 0 ? `<span class="src-quality-tag">移除重复 ${dedup.duplicate_count}</span>` : ''}
         ${dedup.correlation_groups > 0 ? `<span class="src-quality-tag">关联组 ${dedup.correlation_groups}</span>` : ''}
       </div>`
    : '';

  // 结果可信度
  const fpRate = reliabilityBreakdown.fp_rate !== undefined ? (reliabilityBreakdown.fp_rate * 100).toFixed(0) + '%' : '-';
  const highConfRate = reliabilityBreakdown.high_confidence_rate !== undefined ? (reliabilityBreakdown.high_confidence_rate * 100).toFixed(0) + '%' : '-';

  return `
    <div class="src-quality-panel" id="src-quality-panel">
      <div class="src-quality-header" id="src-quality-toggle">
        <div class="src-quality-score-wrap">
          <div class="src-quality-ring" style="border-color:${qColor}">
            <span style="color:${qColor};font-size:22px;font-weight:700">${qScore}</span>
          </div>
          <span class="src-quality-title">扫描可信度</span>
        </div>
        <div class="src-quality-bars">
          <div class="src-quality-bar-row">
            <span class="src-quality-bar-label">覆盖度</span>
            <div class="src-quality-bar"><div class="src-quality-bar-fill" style="width:${coverage}%;background:${coverage >= 80 ? '#73c990' : coverage >= 60 ? '#f0a732' : '#c75450'}"></div></div>
            <span class="src-quality-bar-val">${coverage}</span>
          </div>
          <div class="src-quality-bar-row">
            <span class="src-quality-bar-label">可靠性</span>
            <div class="src-quality-bar"><div class="src-quality-bar-fill" style="width:${reliability}%;background:${reliability >= 80 ? '#73c990' : reliability >= 60 ? '#f0a732' : '#c75450'}"></div></div>
            <span class="src-quality-bar-val">${reliability}</span>
          </div>
          <div class="src-quality-bar-row">
            <span class="src-quality-bar-label">深度</span>
            <div class="src-quality-bar"><div class="src-quality-bar-fill" style="width:${depth}%;background:${depth >= 80 ? '#73c990' : depth >= 60 ? '#f0a732' : '#c75450'}"></div></div>
            <span class="src-quality-bar-val">${depth}</span>
          </div>
        </div>
        <button class="src-quality-expand" id="src-quality-expand-btn">展开</button>
      </div>
      <div class="src-quality-detail" id="src-quality-detail" style="display:none">
        <div class="src-quality-grid">
          <div class="src-quality-section">
            <div class="src-quality-section-title">覆盖说明</div>
            <div class="src-quality-section-body">
              <div class="src-quality-kv"><span>检测漏洞类型</span><code>${typesDetected.length} 种</code></div>
              <div class="src-quality-kv"><span>类型列表</span><code>${escapeHtml(typesDetected.join(', ') || '-')}</code></div>
              <div class="src-quality-kv"><span>总发现数</span><code>${coverageBreakdown.total_findings || 0}</code></div>
            </div>
          </div>
          <div class="src-quality-section">
            <div class="src-quality-section-title">可信度与复核</div>
            <div class="src-quality-section-body">
              <div class="src-quality-kv"><span>误报率</span><code>${fpRate}</code></div>
              <div class="src-quality-kv"><span>高置信度比例</span><code>${highConfRate}</code></div>
              <div class="src-quality-kv"><span>建议复核数</span><code>${reliabilityBreakdown.fp_count || 0}</code></div>
              <div class="src-quality-kv"><span>高置信度数</span><code>${reliabilityBreakdown.high_confidence_count || 0}</code></div>
              <div class="src-quality-kv"><span>确认数</span><code>${coverageBreakdown.confirmed_count || 0}</code></div>
            </div>
          </div>
        </div>
        ${dedupHtml}
        ${recommendations.length > 0 ? `
          <div class="src-quality-recommendations">
            <div class="src-quality-section-title">建议</div>
            <ul class="src-quality-rec-list">
              ${recommendations.map(r => `<li>${escapeHtml(r)}</li>`).join('')}
            </ul>
          </div>
        ` : ''}
      </div>
    </div>
  `;
}

function bindQualityPanelEvents() {
  const toggle = document.getElementById('src-quality-toggle');
  const detail = document.getElementById('src-quality-detail');
  const btn = document.getElementById('src-quality-expand-btn');
  if (!toggle || !detail || !btn) return;
  toggle.addEventListener('click', function(e) {
    if (e.target === btn) return;
    const visible = detail.style.display !== 'none';
    detail.style.display = visible ? 'none' : 'block';
    btn.textContent = visible ? '查看明细' : '收起';
  });
  btn.addEventListener('click', function(e) {
    e.stopPropagation();
    const visible = detail.style.display !== 'none';
    detail.style.display = visible ? 'none' : 'block';
    btn.textContent = visible ? '查看明细' : '收起明细';
  });
}

function sortFindings(findings) {
  return findings.slice().sort((a, b) => {
    const av = verificationRank(a.verification_status);
    const bv = verificationRank(b.verification_status);
    if (av !== bv) return av - bv;
    const afp = a.is_likely_fp ? 1 : 0;
    const bfp = b.is_likely_fp ? 1 : 0;
    if (afp !== bfp) return afp - bfp;
    const sa = SEVERITY_ORDER[(a.severity || '').toLowerCase()] ?? 99;
    const sb = SEVERITY_ORDER[(b.severity || '').toLowerCase()] ?? 99;
    if (sa !== sb) return sa - sb;
    return (b.severity_score || 0) - (a.severity_score || 0);
  });
}

function verificationRank(status) {
  const normalized = String(status || '').toLowerCase();
  if (normalized === 'confirmed') return 0;
  if (normalized === 'probable') return 1;
  if (normalized === 'suspected') return 2;
  return 3;
}

function buildFpTags(reasons) {
  const normalized = (reasons || []).join(' ').toLowerCase();
  const tags = [];
  if (/cloudflare|akamai|incapsula|sucuri|cdn|waf|challenge|verify you are human|security check|bot detection/.test(normalized)) {
    tags.push('CDN / WAF / 挑战页');
  }
  if (/login|log in|sign in|authentication|认证墙|password|csrf token/.test(normalized)) {
    tags.push('登录墙 / 认证页');
  }
  if (/soft 404|page not found|not found|does not exist|模板错误页|通用错误页|404/.test(normalized)) {
    tags.push('软 404 / 模板错误页');
  }
  if (tags.length === 0 && reasons && reasons.length > 0) {
    tags.push('建议复核');
  }
  return tags;
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

  const quality = data.quality || {};
  const qScore = quality.overall_score || 0;
  const qBadge = qScore > 0
    ? `<span class="meta-item" style="color:${qScore >= 80 ? '#73c990' : qScore >= 60 ? '#f0a732' : '#c75450'}">质量 ${qScore}分</span>`
    : '';

  const vStats = data.verification_stats || {};
  const vBadge = vStats.enabled
    ? `<span class="meta-item verification-badge">
        <span class="v-confirmed" title="已验证">${vStats.confirmed || 0}</span>
        <span class="v-probable" title="已验证/可信">${vStats.probable || 0}</span>
        <span class="v-suspected" title="待人工复核">${vStats.suspected || 0}</span>
       </span>`
    : '';

  const severityTotal = summary.total || 0;
  const fpCount = summary.fp_count || 0;
  const actionableCount = Math.max(0, severityTotal - fpCount);
  const criticalCount = summary.critical || 0;
  const highCount = summary.high || 0;
  const mediumCount = summary.medium || 0;
  const lowCount = summary.low || 0;
  const infoCount = summary.info || 0;
  const nextStep = criticalCount + highCount > 0
    ? '优先关闭已确认高危暴露面，再安排复测确认修复是否生效。'
    : mediumCount > 0
      ? '先处理中危项，再复扫验证修复是否生效。'
      : '当前结果偏健康，可作为客户基线留存并持续监控。';
  const reportSummary = '本次扫描共输出 ' + severityTotal + ' 项结果，其中 ' + actionableCount + ' 项建议优先处理，' + fpCount + ' 项建议复核。';
  const reportIntro = '本报告适用于授权范围内的客户交付、复测留档和修复跟踪，已优先突出已验证项与建议复核项，便于直接分配处置。';
  const actionHint = data.scan_id
    ? '<div class="src-report-action-hint src-report-action-hint-alert">优先处理已验证项，再复核建议复核项。</div>'
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
          <div class="src-stat critical"><div class="num">${criticalCount}</div><div class="label">严重</div></div>
          <div class="src-stat high"><div class="num">${highCount}</div><div class="label">高危</div></div>
          <div class="src-stat medium"><div class="num">${mediumCount}</div><div class="label">中危</div></div>
          <div class="src-stat low"><div class="num">${lowCount}</div><div class="label">低危</div></div>
          <div class="src-stat info"><div class="num">${infoCount}</div><div class="label">信息</div></div>
          <div class="src-stat total"><div class="num">${severityTotal}</div><div class="label">总计</div></div>
          <div class="src-stat" style="background:rgba(115,201,144,0.08)"><div class="num" style="color:#73c990">${actionableCount}</div><div class="label">待处理</div></div>
        </div>
        <div class="src-report-submeta">
          ${scanId}${duration}${reportId}${qBadge}${vBadge}
          <span class="meta-item">发现于 ${formatDate(data.discovered_at || new Date().toISOString())}</span>
        </div>
        <div class="src-report-actions">
          ${exportBtn}
          <button class="src-export-btn" id="src-copy-summary" title="复制当前报告摘要">复制摘要</button>
        </div>
        <div class="src-report-summary">${escapeHtml(reportSummary)}</div>
        <div class="src-report-intro">${escapeHtml(reportIntro)}</div>
        <div class="src-report-exec-summary">
          <div class="src-report-exec-title">概览</div>
          <div class="src-report-exec-text">结果已按风险、验证状态、证据完整度和可信度分层整理，建议复核项已单独标出，适合直接用于客户沟通、修复排期与验收留档。</div>
        </div>
        <div class="src-report-capability">
          <div class="src-report-capability-title">能力摘要</div>
          <div class="src-report-capability-grid">
            <div class="src-report-capability-item"><span>已验证</span><strong>${vStats.confirmed || 0}</strong></div>
            <div class="src-report-capability-item"><span>建议复核</span><strong>${fpCount}</strong></div>
            <div class="src-report-capability-item"><span>当前重点</span><strong>压误报 / 保证可用</strong></div>
          </div>
          <div class="src-report-capability-text">当前更适合做基础安全体检、证据展示、复测验证和修复跟踪；遇到登录墙、WAF/CDN、软 404 等场景会自动降权提示，优先保证结果可信与可交付。</div>
        </div>
        <div class="src-report-next-step">
          <div class="src-report-next-step-title">建议</div>
          <div class="src-report-next-step-text">${escapeHtml(nextStep)}${fpCount > 0 ? ' 已识别 ' + fpCount + ' 项建议复核结果，默认优先显示可信项，便于快速进入交付动作。' : ''}</div>
          <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px">
            <button class="src-filter-btn" onclick="navigateTo('tickets')">工单</button>
            <button class="src-filter-btn" onclick="navigateTo('fixer')">修复</button>
          </div>
          ${actionHint}
        </div>
      </div>
    </div>
  `;
}

function renderFindingList(findings, selectedIndex) {
  let visibleFindings = _hideLikelyFp ? findings.filter((item) => !item.is_likely_fp) : findings;
  let hiddenCount = findings.length - visibleFindings.length;
  let html = '<div class="src-list-header">结果列表 <span class="src-list-count">' + visibleFindings.length + '</span>';
  html += '<button class="src-filter-btn" data-action="toggle-fp-filter" title="切换建议复核项显示">' + (_hideLikelyFp ? '显示全部' : '优先可信项') + '</button>';
  if (hiddenCount > 0) html += '<span class="src-filter-note">已隐藏 ' + hiddenCount + ' 项</span>';
  html += '</div>';
  html += '<div class="src-list-items">';
  if (findings.length === 0) {
    html += '<div class="src-empty">' + (_hideLikelyFp ? '筛选下没有结果' : '暂无结果') + '</div>';
  } else {
    visibleFindings.forEach((f, i) => {
      const sev = (f.severity || 'info').toLowerCase();
      const cls = SEVERITY_ZH_CLASS[sev] || 'info';
      const active = i === selectedIndex ? 'active' : '';
      const param = f.parameter ? `<code class="src-list-param">${escapeHtml(f.parameter)}</code>` : '';
      const rawType = String(f.type || '').toLowerCase();
      const typeText = VULN_TYPE_LABELS[rawType] || (f.type ? String(f.type).toUpperCase() : '');
      const typeLabel = typeText ? `<span class="src-list-type">${escapeHtml(typeText)}</span>` : '';
      const host = f.url ? new URL(f.url, window.location.href).hostname : '';
      const path = f.url ? new URL(f.url, window.location.href).pathname : '';
      const fpTags = buildFpTags(Array.isArray(f.fp_reasons) ? f.fp_reasons : []);
      const fpTagText = fpTags.length > 0 ? fpTags[0] : '待人工复核';
      const isFp = f.is_likely_fp ? `<span class="src-list-fp-tag src-list-fp-tag-alert" title="建议复核">${escapeHtml(fpTagText)}</span>` : '';
      const corrGroup = f.correlation_group ? `<span class="src-list-corr" title="关联组 ${escapeAttr(f.correlation_group)}（${f.correlation_size || 0} 个相关）">${escapeHtml(f.correlation_group)}</span>` : '';
      const mergedCount = f.merged_count > 1 ? `<span class="src-list-merged" title="合并了 ${f.merged_count} 个重复项">×${f.merged_count}</span>` : '';
      const vStatus = f.verification_status;
      const vIcon = vStatus === 'confirmed' ? '<span class="src-list-v confirmed" title="已验证">✓ 已验证</span>' :
                    vStatus === 'probable' ? '<span class="src-list-v probable" title="可复现">? 可复现</span>' :
                    vStatus === 'suspected' ? '<span class="src-list-v suspected" title="待人工复核">! 待人工复核</span>' : '';
      const fbIcon = f.user_feedback ? (f.user_feedback.is_false_positive ? '<span class="src-list-fb fp" title="已标记误报">误报</span>' : '<span class="src-list-fb confirmed" title="已确认">确认</span>') : '';
      const rawConfidence = String(f.adjusted_confidence || f.confidence || 'medium');
      const confidenceLabel = rawConfidence === 'high' ? '高可信' : rawConfidence === 'medium' ? '中可信' : rawConfidence === 'low' ? '低可信' : rawConfidence;
      html += `
        <div class="src-list-item ${active} ${cls}" data-index="${i}">
          <div class="src-list-row top">
            <span class="src-sev-badge ${cls}">${SEVERITY_LABEL[sev]}</span>
            <span class="src-list-title" title="${escapeAttr(f.title || '')}">${escapeHtml(f.title || '未命名漏洞')}</span>
            ${vIcon}${fbIcon}${isFp}${mergedCount}
          </div>
          <div class="src-list-row meta">
            ${typeLabel}
            ${param}
            <span class="src-list-host" title="${escapeAttr(f.url || '')}">${escapeHtml(host)}${escapeHtml(path)}</span>
            <span class="src-list-confidence ${escapeHtml(rawConfidence)}">${escapeHtml(confidenceLabel)}</span>
            ${corrGroup}
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
    return '<div class="src-empty-detail">从左侧选择一项查看证据和建议</div>';
  }
  const sev = (finding.severity || 'info').toLowerCase();
  const cls = SEVERITY_ZH_CLASS[sev] || 'info';
  const label = SEVERITY_LABEL[sev] || '信息';
  const evidence = finding.evidence || {};
  const locDetail = finding.location_detail || {};
  const statusMap = { open: '待处理', confirmed: '已确认', false_positive: '误报', fixed: '已修复' };
  const status = finding.status || 'open';
  const fpReasons = Array.isArray(finding.fp_reasons) ? finding.fp_reasons : [];
  const fpTags = buildFpTags(fpReasons);
  const fpBanner = finding.is_likely_fp
    ? `<div class="src-fp-banner">
        <div class="src-fp-banner-title">疑似防护页 / 误报，建议优先复核</div>
        <div class="src-fp-banner-desc">${escapeHtml(fpTags.length > 0 ? fpTags.join(' · ') : '页面更像 CDN/WAF 拦截、登录墙、软 404 或挑战页，而不是可直接利用的漏洞。')}</div>
      </div>`
    : '';


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
      <span class="src-detail-type">${escapeHtml(VULN_TYPE_LABELS[String(finding.type || '').toLowerCase()] || String(finding.type || '').toUpperCase())}</span>
      ${finding.cwe_id ? `<span class="src-detail-cwe" title="Common Weakness Enumeration">${escapeHtml(finding.cwe_id)}</span>` : ''}
      ${finding.owasp_category ? `<span class="src-detail-owasp">${escapeHtml(finding.owasp_category)}</span>` : ''}
      ${finding.cvss_score ? `<span class="src-detail-cvss" title="${escapeHtml(finding.cvss_vector || '')}">CVSS ${finding.cvss_score}</span>` : ''}
      ${finding.severity_score ? `<span class="src-detail-score">评分 ${finding.severity_score}/10</span>` : ''}
      <span class="src-detail-confidence">置信度 ${escapeHtml((finding.adjusted_confidence || finding.confidence || 'medium').toString())}</span>
      ${finding.verification_status ? `<span class="src-detail-verify-badge ${finding.verification_status}">${finding.verification_status === 'confirmed' ? '已验证' : finding.verification_status === 'probable' ? '可复现' : '待人工复核'}</span>` : ''}
      ${finding.is_likely_fp ? '<span class="src-detail-fp-badge src-detail-fp-badge-alert">疑似防护页</span>' : ''}
      ${finding.user_feedback ? (finding.user_feedback.is_false_positive ? '<span class="src-detail-fp-badge" title="您误报">已标记误报</span>' : '<span class="src-detail-verify-badge verified" title="您已确认">客户确认</span>') : ''}
    </div>
    ${fpBanner}
  </div>`;



  // Tab 导航
  html += `<div class="src-detail-tabs">
    <button class="src-detail-tab active" data-tab="overview">概览</button>
    <button class="src-detail-tab" data-tab="evidence">请求 / 响应</button>
    <button class="src-detail-tab" data-tab="fix">修复</button>
  </div>`;

  // 概览面板
  html += `<div class="src-detail-panel active" data-panel="overview">`;

  // 误报判断与验证信息
  if (finding.fp_score !== undefined || finding.verification_score !== undefined || (finding.fp_reasons && finding.fp_reasons.length > 0)) {
    html += `<div class="src-detail-section">
      <div class="src-section-title">可信度与证据等级</div>
      <div class="src-section-body">`;
    if (finding.fp_score !== undefined) {
      const fpPct = (finding.fp_score * 100).toFixed(0);
      const fpColor = finding.fp_score >= 0.5 ? '#c75450' : finding.fp_score >= 0.3 ? '#f0a732' : '#73c990';
      html += `<div class="src-kv"><span class="src-k">误报概率</span><span class="src-v" style="color:${fpColor}">${fpPct}%</span></div>`;
    }
    if (finding.verification_score !== undefined) {
      const vColor = finding.verification_score >= 80 ? '#73c990' : finding.verification_score >= 60 ? '#f0a732' : '#c75450';
      html += `<div class="src-kv"><span class="src-k">验证得分</span><span class="src-v" style="color:${vColor}">${finding.verification_score}/100</span></div>`;
    }
    if (finding.verification_techniques && finding.verification_techniques.length > 0) {
      html += `<div class="src-kv"><span class="src-k">验证技术</span><span class="src-v">${escapeHtml(finding.verification_techniques.join(', '))}</span></div>`;
    }
    if (finding.fp_reasons && finding.fp_reasons.length > 0) {
      html += `<div class="src-fp-reasons"><ul>${finding.fp_reasons.map(r => `<li>${escapeHtml(r)}</li>`).join('')}</ul></div>`;
    }
    html += `</div></div>`;
  }

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
      <div class="src-section-title">复测步骤</div>
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
  const fixText = finding.fix_suggestion || '暂无建议';
  const fixLines = fixText.split(/\n+/).map((line) => line.trim()).filter(Boolean);
  const fixLead = fixLines[0] || '暂无建议';
  const fixSteps = fixLines.slice(1, 4);
  html += `<div class="src-detail-section">
    <div class="src-section-title">修复结论</div>
    <div class="src-section-body">
      <div style="font-weight:700;margin-bottom:6px;color:var(--text-primary)">${escapeHtml(fixLead)}</div>
      <div style="font-size:12px;color:var(--text-secondary);line-height:1.7">${escapeHtml(fixText)}</div>
    </div>
  </div>`;
  if (fixSteps.length > 0) {
    html += `<div class="src-detail-section">
      <div class="src-section-title">实施步骤</div>
      <div class="src-section-body"><ol style="margin:0;padding-left:18px;line-height:1.8;color:var(--text-secondary)">`;
    fixSteps.forEach((step) => {
      html += `<li>${escapeHtml(step)}</li>`;
    });
    html += `</ol></div></div>`;
  }
  html += `<div class="src-detail-section">
    <div class="src-section-title">修复完成后的检查</div>
    <div class="src-section-body"><ul style="margin:0;padding-left:18px;line-height:1.8;color:var(--text-secondary)">
      <li>重新扫描同一地址，确认对应漏洞已消失。</li>
      <li>核对安全头、Cookie、重定向或页面响应是否符合预期。</li>
      <li>如果为高危项，建议先在测试环境验证再发布到生产。</li>
    </ul></div>
  </div>`;
  // 修复代码 tabs
  html += renderFixCodeSection(finding.fix_code || {});
  html += `</div>`;

  // 参考链接
  if (Array.isArray(finding.references) && finding.references.length > 0) {
    html += `<div class="src-detail-section">
      <div class="src-section-title">参考资料</div>
      <ul class="src-references">`;
    finding.references.forEach((ref) => {
      html += `<li><a href="${escapeAttr(ref)}" target="_blank" rel="noopener">${escapeHtml(ref)}</a></li>`;
    });
    html += `</ul></div>`;
  }

  // 操作按钮
  if (_currentScanId && isLoggedIn()) {
    html += `<div class="src-detail-actions">
      <button class="src-action-btn verify" data-action="verify" data-finding-id="${escapeAttr(finding.id || '')}" title="重新请求目标并尝试验证是否仍可复现">复测验证</button>
      <button class="src-action-btn false-positive" data-action="fp" data-finding-id="${escapeAttr(finding.id || '')}" title="如果你判断该项不是实际漏洞，可标记为误报或观察项">标记复核</button>
      <button class="src-action-btn confirm" data-action="confirm" data-finding-id="${escapeAttr(finding.id || '')}" title="如果你确认该项真实存在，可标记为有效漏洞并进入修复流程">确认有效</button>
      <button class="src-action-btn ticket" data-action="ticket" data-finding-id="${escapeAttr(finding.id || '')}" title="将该漏洞转为修复工单并跟踪处理">转工单</button>
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
  const requestSummary = summarizeHttpMessage(evidence.request);
  const responseSummary = summarizeHttpMessage(evidence.response);

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

  html += `<div class="src-section-title">证据</div>
    <div class="src-section-body src-evidence-meta">`;
  const confidenceState = finding.verification_status || (finding.is_likely_fp ? 'suspected' : 'probable');
  const confidenceText = confidenceState === 'confirmed' ? '已验证' : confidenceState === 'probable' ? '可能存在' : '待人工复核';
  const evidenceGrade = confidenceState === 'confirmed' ? 'A级（已验证）' : confidenceState === 'probable' ? 'B级（可复现）' : 'C级（待人工复核）';
  const locationText = evidence.location || evidence.position || evidence.selector || evidence.header || evidence.parameter || evidence.path || evidence.url || "";
  html += `<div class="src-evidence-row"><span class="src-evidence-label">可信度</span><span>${escapeHtml(confidenceText)}</span></div>`;
  html += `<div class="src-evidence-row"><span class="src-evidence-label">证据等级</span><span>${escapeHtml(evidenceGrade)}</span></div>`;
  if (locationText) {
    html += `<div class="src-evidence-row"><span class="src-evidence-label">命中位置</span><span>${escapeHtml(locationText)}</span></div>`;
  }
  html += `<div class="src-evidence-row"><span class="src-evidence-label">误报概率</span><span>${finding.fp_score !== undefined ? ((finding.fp_score * 100).toFixed(0) + '%') : '—'}</span></div>`;
  if (requestSummary) {
    html += `<div class="src-evidence-row"><span class="src-evidence-label">请求摘要</span><span>${escapeHtml(requestSummary)}</span></div>`;
  }
  if (responseSummary) {
    html += `<div class="src-evidence-row"><span class="src-evidence-label">响应摘要</span><span>${escapeHtml(responseSummary)}</span></div>`;
  }
  html += `</div>`;

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
    html += `<div class="src-section-title">证据</div>
    <div class="src-section-body"><div class="src-no-evidence">无详细技术证据</div></div>`;
  }

  html += `</div>`;
  return html;
}

function summarizeHttpMessage(text) {
  if (!text) return '';
  const lines = String(text).split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
  if (!lines.length) return '';
  const statusLine = lines.find((line) => /^HTTP\/\d/i.test(line));
  const methodLine = lines.find((line) => /^(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+/i.test(line));
  const targetLine = methodLine ? methodLine.split(/\s+/).slice(0, 2).join(' ') : '';
  const headerLines = lines.filter((line) => /^[A-Za-z0-9\-]+:\s*/.test(line)).slice(0, 3);
  const parts = [];
  if (statusLine) parts.push(statusLine.replace(/^HTTP\/\d\.\d\s*/i, 'HTTP '));
  if (targetLine) parts.push(targetLine);
  if (headerLines.length) parts.push(headerLines.join(' | '));
  return parts.join(' · ').slice(0, 220);
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

function bindResultPageEvents() {
  const container = document.getElementById('result-content') || document.getElementById('result-container');
  if (!container || container.dataset.srcResultBound === '1') return;
  container.dataset.srcResultBound = '1';
  container.addEventListener('click', function(e) {
    const listItem = e.target.closest('.src-list-item');
    if (listItem) {
      const idx = parseInt(listItem.dataset.index, 10);
      selectFinding(idx);
      return;
    }
    const detailTab = e.target.closest('.src-detail-tab');
    if (detailTab) {
      const tab = detailTab.dataset.tab;
      const card = detailTab.closest('.src-detail-card');
      if (!card) return;
      card.querySelectorAll('.src-detail-tab').forEach((t) => t.classList.remove('active'));
      detailTab.classList.add('active');
      card.querySelectorAll('.src-detail-panel').forEach((p) => {
        p.classList.toggle('active', p.dataset.panel === tab);
      });
      return;
    }
    const fixTab = e.target.closest('.src-fix-tab');
    if (fixTab) {
      _currentFixTab = fixTab.dataset.tab;
      document.querySelectorAll('.src-fix-tab').forEach((t) => t.classList.remove('active'));
      fixTab.classList.add('active');
      document.querySelectorAll('.src-fix-panel').forEach((p) => {
        p.classList.toggle('active', p.dataset.panel === _currentFixTab);
        p.classList.toggle('hidden', p.dataset.panel !== _currentFixTab);
      });
      return;
    }
    const copyBtn = e.target.closest('.src-copy-btn');
    if (copyBtn) {
      const text = copyBtn.dataset.copy || '';
      copyToClipboard(text).then(() => showToast('已复制到剪贴板'));
      return;
    }
    const exportBtn = e.target.closest('.src-export-btn');
    if (exportBtn) {
      if (exportBtn.id === 'src-copy-summary') {
        onCopyReportSummary();
      } else {
        onExportSRCReport();
      }
      return;
    }
    const filterBtn = e.target.closest('.src-filter-btn');
    if (filterBtn && filterBtn.dataset.action === 'toggle-fp-filter') {
      _hideLikelyFp = !_hideLikelyFp;
      const visibleFindings = _hideLikelyFp ? _currentFindings.filter((item) => !item.is_likely_fp) : _currentFindings;
      _selectedIndex = 0;
      const detail = document.getElementById('src-detail-panel');
      if (detail) {
        detail.innerHTML = renderFindingDetail(visibleFindings[0], 0);
      }
      return;
    }
    const actionBtn = e.target.closest('.src-action-btn');
    if (actionBtn) {
      onFindingAction(e);
    }
  });
}

function bindFindingListEvents() {
  // 保留旧调用点的兼容性；实际事件已由 bindResultPageEvents 统一托管。
}



async function onCopyReportSummary() {
  if (!_currentScanId) return;
  const findingCards = Array.from(document.querySelectorAll('.finding-card'));
  const topFindings = findingCards
    .slice(0, 3)
    .map((card, index) => {
      const title = card.querySelector('.finding-title');
      const severity = card.querySelector('.finding-severity');
      return `${index + 1}. ${title ? title.textContent.trim() : '未命名项'}${severity ? `（${severity.textContent.trim()}）` : ''}`;
    })
    .filter(Boolean);
  const actionableCount = Math.max(0, (_currentSummary.total || 0) - (_currentSummary.fp_count || 0));
  const summaryText = [
    '报告摘要',
    '扫描 ID: ' + _currentScanId,
    'URL: ' + _currentUrl,
    '安全评分: ' + _currentScore,
    '总计: ' + (_currentSummary.total || 0),
    '待处理: ' + actionableCount,
    topFindings.length ? '重点项:\n' + topFindings.join('\n') : '重点项: 无',
    '建议: 优先处理高危和严重项，修复后复测。'
  ].join(String.fromCharCode(10));
  await copyToClipboard(summaryText);
  showToast('报告摘要已复制');
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
        const status = res.reproducible === true ? '仍可复现' : (res.reproducible === false ? '已无法复现' : '需人工复测');
        showToast(`验证完成：${status}`);
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

  const loadingText = action === 'fp' ? '标记中...' : action === 'ticket' ? '创建中...' : '提交中...';
  const idleText = action === 'fp' ? '标记误报' : action === 'ticket' ? '工单' : '确认有效';
  btn.textContent = loadingText;
  btn.disabled = true;
  try {
    if (action === 'ticket') {
      const res = await createTicket({
        scan_id: _currentScanId,
        finding_name: finding.title || findingId,
        severity: finding.severity || 'low',
        fix_code: finding.fix_code && finding.fix_code.generic ? finding.fix_code.generic : '',
        notes: finding.fix_suggestion || finding.description || '',
      });
      if (res && res.success) {
        showToast('工单已创建');
        setTimeout(function () { navigateTo('tickets'); }, 300);
      } else {
        showToast('工单失败：' + (res && res.error ? res.error : '未知错误'));
      }
    } else {
      const res = await findingFeedback({
        scan_id: _currentScanId,
        finding_name: finding.title || findingId,
        finding_type: finding.type || '',
        is_false_positive: action === 'fp',
        is_confirmed: action === 'confirm',
      });
      if (res && res.success) {
        showToast(action === 'fp' ? '误报，后续会用于优化检测' : '已确认漏洞，已记录到反馈闭环');
      } else {
        showToast('反馈提交失败：' + (res && res.error ? res.error : '未知错误'));
      }
    }
  } catch (e) {
    showToast(action === 'ticket' ? '工单创建失败' : '反馈请求失败');
  } finally {
    btn.textContent = idleText;
    btn.disabled = false;
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
    .src-report-capability { margin-top:12px; padding:12px 14px; border-radius:var(--radius-sm); background:rgba(115,201,144,0.08); border:1px solid rgba(115,201,144,0.18); }
    .src-report-capability-title { font-size:12px; font-weight:700; margin-bottom:8px; color:#73c990; }
    .src-report-capability-grid { display:grid; grid-template-columns:repeat(3, minmax(0, 1fr)); gap:10px; }
    .src-report-capability-item { background:rgba(255,255,255,0.03); border:1px solid var(--border-light); border-radius:var(--radius-xs); padding:8px 10px; display:flex; flex-direction:column; gap:4px; }
    .src-report-capability-item span { font-size:11px; color:var(--text-secondary); }
    .src-report-capability-item strong { font-size:13px; color:var(--text-primary); }
    .src-report-capability-text { margin-top:8px; font-size:12px; color:var(--text-secondary); line-height:1.7; }
    @media (max-width: 900px) { .src-report-capability-grid { grid-template-columns:1fr; } }

    .src-quality-panel { background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius); margin-bottom:16px; overflow:hidden; }
    .src-quality-header { display:flex; align-items:center; gap:20px; padding:14px 18px; cursor:pointer; }
    .src-quality-score-wrap { display:flex; flex-direction:column; align-items:center; gap:4px; }
    .src-quality-ring { width:48px; height:48px; border-radius:50%; border:3px solid; display:flex; align-items:center; justify-content:center; }
    .src-quality-title { font-size:11px; color:var(--text-secondary); }
    .src-quality-bars { flex:1; display:flex; flex-direction:column; gap:6px; }
    .src-quality-bar-row { display:flex; align-items:center; gap:10px; }
    .src-quality-bar-label { width:50px; font-size:12px; color:var(--text-secondary); text-align:right; }
    .src-quality-bar { flex:1; height:8px; background:var(--bg-secondary); border-radius:4px; overflow:hidden; }
    .src-quality-bar-fill { height:100%; border-radius:4px; transition:width 0.6s ease; }
    .src-quality-bar-val { width:28px; font-size:12px; font-weight:600; text-align:right; }
    .src-quality-expand { background:var(--bg-secondary); border:1px solid var(--border); color:var(--text-secondary); padding:4px 10px; border-radius:var(--radius-xs); font-size:11px; cursor:pointer; white-space:nowrap; }
    .src-quality-expand:hover { border-color:var(--primary); color:var(--primary-light); }
    .src-quality-detail { padding:0 18px 14px; border-top:1px solid var(--border-light); }
    .src-quality-grid { display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-top:12px; }
    @media (max-width:700px) { .src-quality-grid { grid-template-columns:1fr; } }
    .src-quality-section { }
    .src-quality-section-title { font-size:12px; font-weight:700; color:var(--text-secondary); margin-bottom:8px; }
    .src-quality-section-body { display:flex; flex-direction:column; gap:4px; }
    .src-quality-kv { display:flex; justify-content:space-between; align-items:center; font-size:12px; }
    .src-quality-kv span { color:var(--text-secondary); }
    .src-quality-kv code { background:var(--token-bg); padding:2px 6px; border-radius:var(--radius-xs); font-size:11px; }
    .src-quality-dedup { display:flex; align-items:center; gap:8px; margin-top:12px; padding:10px; background:var(--bg-secondary); border-radius:var(--radius-sm); flex-wrap:wrap; }
    .src-quality-label { font-size:12px; font-weight:700; color:var(--text-secondary); }
    .src-quality-stat { font-size:13px; font-weight:600; }
    .src-quality-stat.highlight { color:var(--primary-light); }
    .src-quality-arrow { color:var(--text-secondary); }
    .src-quality-tag { background:var(--token-bg); padding:2px 8px; border-radius:10px; font-size:11px; color:var(--text-secondary); }
    .src-quality-recommendations { margin-top:12px; }
    .src-quality-rec-list { margin:0; padding-left:18px; font-size:12px; color:var(--text-secondary); }
    .src-quality-rec-list li { margin-bottom:4px; line-height:1.5; }

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
    .src-list-fp-tag { background:#c7545022; color:#c75450; font-size:10px; padding:1px 5px; border-radius:3px; font-weight:700; }
    .src-list-fp-tag-alert { background:rgba(240,167,50,0.18); color:#f0a732; }
    .src-list-fp-tag-alert.fp { background:rgba(199,84,80,0.18); color:#c75450; }
    .src-list-fp-tag-alert.info { background:rgba(128,128,128,0.18); color:#808080; }
    .src-list-merged { background:var(--primary); color:#fff; font-size:10px; padding:1px 5px; border-radius:3px; font-weight:600; }
    .src-list-corr { background:var(--token-bg); color:var(--text-secondary); font-size:10px; padding:1px 5px; border-radius:3px; font-family:var(--font); }
    .src-list-v { font-size:10px; padding:1px 5px; border-radius:3px; font-weight:700; margin-left:4px; }
    .src-list-v.confirmed { background:rgba(115,201,144,0.2); color:#73c990; }
    .src-list-v.probable { background:rgba(240,167,50,0.2); color:#f0a732; }
    .src-list-v.suspected { background:rgba(199,84,80,0.2); color:#c75450; }
    .src-list-fb { font-size:10px; padding:1px 5px; border-radius:3px; font-weight:700; margin-left:4px; }
    .src-list-fb.confirmed { background:rgba(115,201,144,0.2); color:#73c990; }
    .src-list-fb.fp { background:rgba(128,128,128,0.2); color:#808080; }
    .src-list-confidence.high { color:#73c990; }
    .src-list-confidence.medium { color:#f0a732; }
    .src-list-confidence.low { color:#c75450; }
    .verification-badge { display:flex; gap:4px; align-items:center; }
    .verification-badge span { font-size:10px; padding:1px 5px; border-radius:3px; font-weight:600; }
    .v-confirmed { background:rgba(115,201,144,0.2); color:#73c990; }
    .v-probable { background:rgba(240,167,50,0.2); color:#f0a732; }
    .v-suspected { background:rgba(199,84,80,0.2); color:#c75450; }

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
    .src-detail-confidence { background:var(--token-bg); color:var(--text-secondary); padding:2px 8px; border-radius:var(--radius-xs); }
    .src-detail-fp-badge { background:rgba(199,84,80,0.15); color:#c75450; padding:2px 8px; border-radius:var(--radius-xs); font-weight:600; }
    .src-detail-verify-badge { padding:2px 8px; border-radius:var(--radius-xs); font-weight:600; }
    .src-detail-verify-badge.verified { background:rgba(115,201,144,0.15); color:#73c990; }
    .src-detail-verify-badge.unverified { background:rgba(240,167,50,0.15); color:#f0a732; }
    .src-detail-verify-badge.confirmed { background:rgba(115,201,144,0.15); color:#73c990; }
    .src-detail-verify-badge.probable { background:rgba(240,167,50,0.15); color:#f0a732; }
    .src-detail-verify-badge.suspected { background:rgba(199,84,80,0.15); color:#c75450; }
    .src-fp-banner { margin:12px 0 4px; padding:12px 14px; border:1px solid rgba(240,167,50,0.35); border-radius:var(--radius-sm); background:linear-gradient(135deg, rgba(240,167,50,0.12), rgba(199,84,80,0.08)); }
    .src-fp-banner-title { font-size:13px; font-weight:700; color:#f0a732; margin-bottom:4px; }
    .src-fp-banner-desc { font-size:12px; color:var(--text-secondary); line-height:1.6; }

    .src-fp-reasons { margin-top:8px; }
    .src-fp-reasons ul { margin:0; padding-left:18px; }
    .src-fp-reasons li { font-size:12px; color:var(--text-secondary); margin-bottom:3px; }

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
    .src-action-btn.ticket { background:rgba(75,110,175,0.12); color:var(--primary-light); border-color:rgba(75,110,175,0.3); }
    .src-detail-footer { font-size:12px; color:var(--text-secondary); border-top:1px solid var(--border-light); padding:12px 18px; }
    .src-empty { padding:30px; text-align:center; color:var(--text-secondary); }
    .src-empty-detail { padding:40px; text-align:center; color:var(--text-secondary); background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius); }
  `;
  document.head.appendChild(style);
}

export function init() {
  injectSRCStyles();
}




