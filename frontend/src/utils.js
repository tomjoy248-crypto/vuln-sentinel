/** 通用工具函数 */

export function safeGetElement(id) {
  return document.getElementById(id) || null;
}

export function safeSetText(id, text) {
  const el = safeGetElement(id);
  if (el) el.textContent = text;
}

export function safeSetHtml(id, html) {
  const el = safeGetElement(id);
  if (el) el.innerHTML = html;
}

export function safeSetValue(id, value) {
  const el = safeGetElement(id);
  if (el) el.value = value;
}

export function safeSetDisplay(id, display) {
  const el = safeGetElement(id);
  if (el) el.style.display = display;
}

export function escapeHtml(str) {
  if (str == null) return '';
  const div = document.createElement('div');
  div.appendChild(document.createTextNode(String(str)));
  return div.innerHTML;
}

export function escapeAttr(str) {
  return String(str == null ? '' : str).replace(/'/g, '&#39;').replace(/"/g, '&quot;');
}

export function cssEscape(s) {
  if (!s) return '';
  return s.replace(/[^a-zA-Z0-9_-]/g, function(c) {
    return '\\' + c.charCodeAt(0).toString(16).toUpperCase() + ' ';
  });
}

export function getScoreColor(score) {
  if (score >= 75) return '#73c990';
  if (score >= 50) return '#f0a732';
  return '#c75450';
}

export function getScoreGradient(score) {
  if (score >= 75) return 'linear-gradient(90deg,#73c990,#5fa070)';
  if (score >= 50) return 'linear-gradient(90deg,#f0a732,#c48a2a)';
  return 'linear-gradient(90deg,#c75450,#a0403d)';
}

export function getRiskClass(level) {
  if (!level) return 'low';
  const l = String(level).toLowerCase();
  if (l.includes('critical') || l.includes('high')) return 'high';
  if (l.includes('medium')) return 'medium';
  if (l.includes('low')) return 'low';
  return 'info';
}

export function getRiskColor(level) {
  const cls = getRiskClass(level);
  if (cls === 'critical' || cls === 'high') return '#c75450';
  if (cls === 'medium') return '#f0a732';
  if (cls === 'low') return '#73c990';
  return '#808080';
}

export function getHost(url) {
  try {
    return new URL(url).hostname;
  } catch (e) {
    return url || '';
  }
}

export function extractError(data) {
  if (!data) return '未知错误';
  if (typeof data === 'string') return data;
  return data.error || data.detail || data.message || JSON.stringify(data);
}

export function friendlyError(err) {
  let msg = (err && (err.message || err.error || err.detail)) || String(err) || '未知错误';
  if (/timeout|timed out/i.test(msg)) {
    return '网络连接超时，请检查 URL 是否可访问';
  }
  if (/dns|getaddrinfo|Name or service not known/i.test(msg)) {
    return '域名解析失败，请检查域名是否正确';
  }
  if (/403|forbidden/i.test(msg)) {
    return '目标站点拒绝访问，可能需要授权或绕过 WAF';
  }
  if (/500|502|503|504/i.test(msg)) {
    return '目标服务器内部错误，请稍后重试';
  }
  if (/certificate|ssl|tls/i.test(msg)) {
    return 'SSL/TLS 证书验证失败，请检查 HTTPS 配置';
  }
  return msg;
}

export function setButtonLoading(btnId, loading) {
  const btn = safeGetElement(btnId);
  if (!btn) return;
  if (loading) {
    btn.dataset.originalText = btn.textContent;
    btn.textContent = '处理中...';
    btn.disabled = true;
  } else {
    btn.textContent = btn.dataset.originalText || btn.textContent;
    btn.disabled = false;
  }
}

export function renderPagination(containerId, currentPage, totalPages, onPageChange) {
  const container = safeGetElement(containerId);
  if (!container) return;
  if (totalPages <= 1) {
    container.style.display = 'none';
    return;
  }
  container.style.display = 'flex';
  let html = '';
  html += `<button ${currentPage <= 1 ? 'disabled' : ''} onclick="${onPageChange}(${currentPage - 1})">上一页</button>`;
  html += `<span style="padding:4px 10px;font-size:12px;color:var(--text-secondary)">${currentPage} / ${totalPages}</span>`;
  html += `<button ${currentPage >= totalPages ? 'disabled' : ''} onclick="${onPageChange}(${currentPage + 1})">下一页</button>`;
  container.innerHTML = html;
}

export function formatDate(iso) {
  if (!iso) return '';
  try {
    const d = new Date(iso);
    return d.toLocaleString('zh-CN');
  } catch (e) {
    return iso;
  }
}

export function copyToClipboard(text) {
  if (navigator.clipboard && window.isSecureContext) {
    return navigator.clipboard.writeText(text);
  }
  const ta = document.createElement('textarea');
  ta.value = text;
  ta.style.position = 'fixed';
  ta.style.opacity = '0';
  document.body.appendChild(ta);
  ta.select();
  try {
    document.execCommand('copy');
  } finally {
    document.body.removeChild(ta);
  }
  return Promise.resolve();
}
