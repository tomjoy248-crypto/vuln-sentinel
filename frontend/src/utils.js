/** 通用工具函数 */

export function safeGetElement(id) { let el = document.getElementById(id); return el || null; }
export function safeSetText(id, text) { let el = safeGetElement(id); if (el) el.textContent = text; }
export function safeSetHtml(id, html) { let el = safeGetElement(id); if (el) el.innerHTML = html; }
export function safeSetValue(id, value) { let el = safeGetElement(id); if (el) el.value = value; }
export function safeSetDisplay(id, display) { let el = safeGetElement(id); if (el) el.style.display = display; }

export function escapeHtml(str) {
  if (str == null) return '';
  let div = document.createElement('div');
  div.appendChild(document.createTextNode(String(str)));
  return div.innerHTML;
}

export function escapeAttr(str) {
  return String(str == null ? '' : str).replace(/'/g, "&#39;").replace(/"/g, "&quot;");
}

export function getHost(url) {
  try {
    if (!/^https?:\/\//i.test(url)) url = 'http://' + url;
    let u = new URL(url);
    return u.hostname;
  } catch(e) {
    return url.replace(/^https?:\/\//i, '').split('/')[0];
  }
}

export function getScoreColor(score) {
  score = parseInt(score, 10);
  if (isNaN(score)) score = 0;
  if (score >= 75) return '#73c990';
  if (score >= 50) return '#f0a732';
  return '#c75450';
}

export function getScoreGradient(score) {
  score = parseInt(score, 10);
  if (isNaN(score)) score = 0;
  score = Math.max(0, Math.min(100, score));
  if (score >= 75) return 'conic-gradient(#73c990 0% ' + score + '%, #334155 ' + score + '% 100%)';
  if (score >= 50) return 'conic-gradient(#f0a732 0% ' + score + '%, #334155 ' + score + '% 100%)';
  return 'conic-gradient(#c75450 0% ' + score + '%, #334155 ' + score + '% 100%)';
}

export function getRiskClass(level) {
  if (level === '严重' || level === 'critical' || level === '高风险' || level === 'high') return 'high';
  if (level === '中风险' || level === 'medium') return 'medium';
  return 'low';
}

export function getRiskColor(level) {
  if (!level) return 'var(--text-secondary)';
  if (level.indexOf('严重') >= 0 || level.indexOf('高') >= 0 || level.indexOf('critical') >= 0) return '#c75450';
  if (level.indexOf('中') >= 0 || level.indexOf('medium') >= 0) return '#f0a732';
  if (level.indexOf('低') >= 0 || level.indexOf('low') >= 0) return '#16a34a';
  return 'var(--text-secondary)';
}

export function copyToClipboard(text) {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    return navigator.clipboard.writeText(text);
  }
  return new Promise((resolve, reject) => {
    try {
      let ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.left = '-9999px';
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      resolve();
    } catch (e) {
      reject(e);
    }
  });
}

export function formatDate(iso) {
  if (!iso) return '-';
  try {
    const d = new Date(iso);
    if (isNaN(d.getTime())) return iso;
    const pad = (n) => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
  } catch (e) {
    return iso;
  }
}

export function cssEscape(s) {
  if (window.CSS && window.CSS.escape) return window.CSS.escape(s);
  return String(s).replace(/[^a-zA-Z0-9_-]/g, function(c) { return '\\' + c; });
}

export function extractError(data) {
  if (!data) return '未知错误';
  let msg = '';
  if (typeof data.error === 'string' && data.error) msg = data.error;
  else if (typeof data.detail === 'string' && data.detail) msg = data.detail;
  else if (Array.isArray(data.detail) && data.detail.length > 0) {
    msg = data.detail
      .map(function(item) {
        if (!item) return '';
        if (typeof item === 'string') return item;
        if (typeof item.msg === 'string' && item.msg) return item.msg;
        if (Array.isArray(item.loc) && item.loc.length) return String(item.loc[item.loc.length - 1]);
        return '';
      })
      .filter(Boolean)
      .join('；');
  }
  else if (typeof data.message === 'string' && data.message) msg = data.message;
  else msg = '请求失败';

  if (typeof data.code === 'string' && !msg.includes(data.code) && data.code !== 'ERROR') {
    msg += '（' + data.code + '）';
  }

  // 合规/授权错误附加更明确的引导
  if (data.restricted_code === 'restricted') {
    msg += '（该目标类型受限，请确认您拥有合法授权后再扫描）';
  } else if (data.restricted_code === 'ownership_required') {
    msg += '，请先完成域名归属验证。';
  } else if (data.restricted_code === 'unauthorized') {
    msg += '（请先确认您有权扫描该目标）';
  }
  return msg;
}

export function isPaymentRequired(data) {
  return data && data._status === 402 && data.code === 'PAYMENT_REQUIRED';
}

export function paymentRequiredMessage(data) {
  if (isPaymentRequired(data)) {
    return (typeof data.message === 'string' && data.message) || '额度不足，请充值后再试';
  }
  return '';
}

export function friendlyError(err) {
  let msg = (err && (err.message || err.error || err.detail)) || String(err) || '未知错误';
  if (/timeout|timed out/i.test(msg)) {
    return '请求超时，请检查网络连接或稍后重试';
  }
  if (/network|fetch|internet|offline/i.test(msg)) {
    return '网络连接异常，请检查网络设置';
  }
  if (/403|forbidden/i.test(msg)) {
    return '请求被拒绝，请检查权限或联系管理员';
  }
  if (/404|not found/i.test(msg)) {
    return '请求的资源不存在';
  }
  if (/500|502|503|504|server error/i.test(msg)) {
    return '服务器暂时不可用，请稍后重试';
  }
  if (/unauthorized|401|未登录|登录|token|jwt/i.test(msg)) {
    return '登录状态已过期，请重新登录';
  }
  return msg;
}

export function setButtonLoading(btnId, loading) {
  let btn = safeGetElement(btnId);
  if (!btn) return;
  if (loading) {
    btn._originalText = btn.textContent;
    btn.textContent = '处理中...';
    btn.disabled = true;
  } else {
    btn.textContent = btn._originalText || btn.textContent;
    btn.disabled = false;
  }
}

export function renderPagination(containerId, currentPage, totalPages, onPageChange) {
  let container = safeGetElement(containerId);
  if (!container) return;
  if (totalPages <= 1) { container.innerHTML = ''; return; }
  let html = '';
  let maxButtons = 5;
  let startPage = Math.max(1, currentPage - Math.floor(maxButtons / 2));
  let endPage = Math.min(totalPages, startPage + maxButtons - 1);
  if (endPage - startPage < maxButtons - 1) startPage = Math.max(1, endPage - maxButtons + 1);

  if (currentPage > 1) {
    html += '<button class="page-btn" data-page="' + (currentPage - 1) + '">上一页</button>';
  }
  for (let i = startPage; i <= endPage; i++) {
    html += '<button class="page-btn ' + (i === currentPage ? 'active' : '') + '" data-page="' + i + '">' + i + '</button>';
  }
  if (currentPage < totalPages) {
    html += '<button class="page-btn" data-page="' + (currentPage + 1) + '">下一页</button>';
  }
  container.innerHTML = html;
  container.querySelectorAll('.page-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      let p = parseInt(this.dataset.page, 10);
      if (onPageChange) onPageChange(p);
    });
  });
}

// Evidence 通用渲染器
export var EVIDENCE_LABELS = {
  header: '相关响应头',
  detected: '检测结果',
  reason: '判断依据',
  impact: '影响说明',
  value: '当前值',
  check_scope: '检测范围',
  limitation: '检测局限',
  param: '问题参数',
  payload: '测试 Payload',
  url: '问题 URL',
  path: '暴露路径',
  status: '响应状态',
  snippet: '内容片段',
  library: '组件名称',
  version: '当前版本',
  detected_version: '当前版本',
  min_safe_version: '安全版本',
  cve: '关联 CVE',
  missing_flags: '缺失安全标志',
  redirect_to: '重定向目标',
  os: '操作系统',
  body_hint: '响应特征',
  days_left: '证书剩余天数',
  method: '检测方法'
};

export var EVIDENCE_ORDER = [
  'detected', 'header', 'reason', 'impact', 'value', 'check_scope', 'limitation',
  'param', 'payload', 'url', 'path', 'status', 'snippet',
  'library', 'version', 'detected_version', 'min_safe_version', 'cve',
  'missing_flags', 'redirect_to', 'os', 'body_hint', 'days_left', 'method'
];

export function renderEvidence(evi) {
  if (!evi || typeof evi !== 'object') return '';
  let keys = Object.keys(evi).filter(function(k) { return evi[k] !== undefined && evi[k] !== null && evi[k] !== ''; });
  if (keys.length === 0) return '';
  let ordered = [];
  EVIDENCE_ORDER.forEach(function(k) { if (keys.indexOf(k) >= 0) ordered.push(k); });
  keys.forEach(function(k) { if (ordered.indexOf(k) < 0) ordered.push(k); });

  let rows = ordered.map(function(k) {
    let label = EVIDENCE_LABELS[k] || k;
    let raw = evi[k];
    let valHtml = '';

    if (k === 'detected') {
      let detColor = raw ? '#c75450' : '#73c990';
      let detText = raw ? '已检测到' : '未检测到';
      valHtml = '<span style="color:' + detColor + ';font-weight:600;font-size:12px">' + detText + '</span>';
    } else if (k === 'payload') {
      valHtml = '<code style="background:#3b0d0d;color:#fecaca;padding:2px 8px;border-radius:2px;font-size:12px;word-break:break-all;border:1px solid rgba(199,84,80,0.35)">' + escapeHtml(raw) + '</code>';
    } else if (k === 'url' || k === 'path') {
      valHtml = '<code style="background:#2b2b2b;padding:2px 8px;border-radius:2px;font-size:12px;word-break:break-all">' + escapeHtml(raw) + '</code>';
    } else if (k === 'cve') {
      let cveText = String(raw);
      let cveMatches = cveText.match(/CVE-\d{4}-\d{4,7}/gi) || [];
      if (cveMatches.length > 0) {
        valHtml = cveMatches.map(function(id) {
          return '<span style="display:inline-block;background:#c75450;color:#fff;padding:2px 8px;border-radius:2px;font-size:11px;font-weight:700;letter-spacing:0.3px">' + escapeHtml(id) + '</span>';
        }).join(' ');
        let extra = cveText.replace(/CVE-\d{4}-\d{4,7}/gi, '').replace(/[,\s、，；;]+/g, ' ').trim();
        if (extra) valHtml += ' <span style="font-size:12px;color:var(--text-secondary)">' + escapeHtml(extra) + '</span>';
      } else {
        valHtml = '<span style="display:inline-block;background:#c75450;color:#fff;padding:2px 8px;border-radius:2px;font-size:11px;font-weight:700">' + escapeHtml(cveText) + '</span>';
      }
    } else if (k === 'missing_flags') {
      let arr = Array.isArray(raw) ? raw : [raw];
      valHtml = arr.map(function(item) {
        return '<code style="background:rgba(240,167,50,0.1);color:#f0a732;padding:2px 8px;border-radius:2px;font-size:12px">' + escapeHtml(item) + '</code>';
      }).join(' ');
    } else if (k === 'status' || k === 'days_left') {
      valHtml = '<span style="font-weight:600;color:var(--text-primary);font-size:12px">' + escapeHtml(raw) + '</span>';
    } else if (k === 'snippet') {
      valHtml = '<code style="background:#1e293b;color:#e2e8f0;padding:6px 8px;border-radius:2px;font-size:11px;word-break:break-all;display:block;white-space:pre-wrap;max-height:160px;overflow:auto">' + escapeHtml(raw) + '</code>';
    } else {
      valHtml = '<span style="font-size:12px;color:var(--text)">' + escapeHtml(raw) + '</span>';
    }
    return '<div style="margin-bottom:8px"><span style="display:inline-block;min-width:80px;color:var(--text-secondary);font-size:12px;font-weight:600">' + label + '</span> ' + valHtml + '</div>';
  });
  return '<div style="margin-top:10px">' + rows.join('') + '</div>';
}
