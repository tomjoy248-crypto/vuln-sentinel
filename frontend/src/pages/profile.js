/** 个人页 / 用户设置 (page-profile) 模块 */

import {
  authFetch,
  apiPost,
  apiGet,
  apiDelete,
  register,
  login,
  resetPassword,
  me,
  credits,
  usage,
  loadAlerts as apiLoadAlerts,
  markAlertRead as apiMarkAlertRead,
  isLoggedIn,
  getToken,
  setToken,
  removeToken,
  getUsername,
  authHeaders
} from '../api.js';

import {
  escapeHtml,
  safeGetElement,
  safeSetHtml,
  safeSetText,
  safeSetValue,
  safeSetDisplay,
  copyToClipboard,
  extractError,
  formatDate,
  isPaymentRequired,
  paymentRequiredMessage,
  renderPagination
} from '../utils.js';

import { showToast } from '../components/Toast.js';

// 兼容 main.js 暴露到 window 的全局辅助函数
const navigateTo = (...args) => typeof window.navigateTo === 'function' && window.navigateTo(...args);
const updateThemeIcon = (...args) => typeof window.updateThemeIcon === 'function' && window.updateThemeIcon(...args);
const renderScanHistory = (...args) => typeof window.renderScanHistory === 'function' && window.renderScanHistory(...args);
const renderMonitorTargets = (...args) => typeof window.renderMonitorTargets === 'function' && window.renderMonitorTargets(...args);

// ========== Auth UI ==========
async function refreshLoginStatus() {
  let statusMessage = document.getElementById('auth-status-message');
  if (!statusMessage) return;
  statusMessage.textContent = '正在检查登录服务...';
  try {
    let controller = new AbortController();
    let timer = setTimeout(function() { controller.abort(); }, 2000);
    let resp = await fetch('/api/v1/', { signal: controller.signal });
    clearTimeout(timer);
    if (resp.ok) {
      statusMessage.textContent = '登录服务在线，可直接使用你的账号登录';
    } else {
      statusMessage.textContent = '登录服务可访问，但返回异常状态：' + resp.status;
    }
  } catch (e) {
    statusMessage.textContent = '登录服务暂时不可用，请先确认后端已启动';
  }
}

function toggleAuthForm(mode) {
  let guest = document.getElementById('auth-guest');
  let reg = document.getElementById('auth-register');
  let reset = document.getElementById('auth-reset');
  let logged = document.getElementById('auth-logged');
  if (mode === 'register') {
    if (guest) guest.style.display = 'none';
    if (reg) reg.style.display = 'block';
    if (reset) reset.style.display = 'none';
    if (logged) logged.style.display = 'none';
  } else if (mode === 'login') {
    if (guest) guest.style.display = 'block';
    if (reg) reg.style.display = 'none';
    if (reset) reset.style.display = 'none';
    if (logged) logged.style.display = 'none';
  } else if (mode === 'reset') {
    if (guest) guest.style.display = 'none';
    if (reg) reg.style.display = 'none';
    if (reset) reset.style.display = 'block';
    if (logged) logged.style.display = 'none';
  }
}

function updateAuthUI() {
  let guest = document.getElementById('auth-guest');
  let reg = document.getElementById('auth-register');
  let reset = document.getElementById('auth-reset');
  let logged = document.getElementById('auth-logged');
  let scanLoginTip = document.getElementById('scan-login-tip');
  let tokenInput = document.getElementById('api-token-input');
  let statusMessage = document.getElementById('auth-status-message');
  if (isLoggedIn()) {
    if (guest) guest.style.display = 'none';
    if (reg) reg.style.display = 'none';
    if (reset) reset.style.display = 'none';
    if (logged) logged.style.display = 'block';
    if (scanLoginTip) scanLoginTip.style.display = 'none';
    if (statusMessage) statusMessage.textContent = '已登录，可直接扫描或查看历史记录';
    let name = getUsername();
    let displayName = document.getElementById('auth-display-name');
    if (displayName) displayName.textContent = name || '用户';
    // 显示真实的 JWT token，不再生成假 token
    if (tokenInput) {
      let real令牌 = getToken();
      tokenInput.value = real令牌 || '令牌 不可用';
    }
  } else {
    if (guest) guest.style.display = 'block';
    if (reg) reg.style.display = 'none';
    if (reset) reset.style.display = 'none';
    if (logged) logged.style.display = 'none';
    if (scanLoginTip) scanLoginTip.style.display = 'block';
    if (statusMessage) statusMessage.textContent = '如果登录失败，请先确认后端服务已启动。';
    if (tokenInput) tokenInput.value = '登录后显示 令牌';
  }
}

function doResetPassword() {
  if (!isLoggedIn()) { showToast('请先登录后再修改密码'); toggleAuthForm('login'); return; }
  let pw1El = document.getElementById('reset-new-password');
  let pw2El = document.getElementById('reset-new-password2');
  let errEl = document.getElementById('reset-error');
  if (!pw1El || !pw2El) { showToast('密码重置表单加载失败'); return; }
  let pw1 = pw1El.value;
  let pw2 = pw2El.value;
  if (errEl) errEl.textContent = '';
  if (!pw1 || pw1.length < 6) { if (errEl) errEl.textContent = '新密码至少 6 个字符'; return; }
  if (pw1 !== pw2) { if (errEl) errEl.textContent = '两次密码不一致'; return; }
  authFetch('/api/reset-password', {
    method: 'POST',
    body: JSON.stringify({ new_password: pw1 })
  }).then(function(r) { return r.json(); }).then(function(data) {
    if (data.success) {
      showToast('密码已修改，请用新密码登录');
      doLogout();
    } else {
      errEl.textContent = extractError(data) || '修改失败';
    }
  }).catch(function(e) {
    if (errEl) errEl.textContent = '修改失败: ' + e.message;
  });
}

function doLogin() {
  let usernameEl = document.getElementById('login-username');
  let passwordEl = document.getElementById('login-password');
  let errEl = document.getElementById('login-error');
  if (!usernameEl || !passwordEl) { showToast('登录表单加载失败'); return; }
  let username = usernameEl.value.trim();
  let password = passwordEl.value.trim();
  if (errEl) errEl.textContent = '';
  if (!username || !password) { if (errEl) errEl.textContent = '请输入用户名和密码'; return; }

  authFetch('/api/login', {
    skipAuthExpiry: true,
    method: 'POST',
    body: JSON.stringify({ username: username, password: password })
  }).then(function(resp) { return resp.json(); }).then(function(data) {
    let token = data.token || (data.data && data.data.token);
    let resolvedUsername = data.username || (data.data && data.data.username) || username;
    if (token) {
      setToken(token);
      try { localStorage.setItem('vs_username', resolvedUsername); } catch(e) {}
      updateAuthUI();
      updateAlertBadge();
      updateUserCredits();
      if (typeof window.updateScanCreditsHint === 'function') window.updateScanCreditsHint();
      showToast('登录成功，欢迎 ' + resolvedUsername);
      navigateTo('scan');
    } else {
      if (errEl) errEl.textContent = extractError(data) || '登录失败';
    }
  }).catch(function(e) {
    if (errEl) errEl.textContent = '登录失败: ' + e.message;
  });
}

function doRegister() {
  let usernameEl = document.getElementById('reg-username');
  let emailEl = document.getElementById('reg-email');
  let passwordEl = document.getElementById('reg-password');
  let password2El = document.getElementById('reg-password2');
  let errEl = document.getElementById('register-error');
  if (!usernameEl || !passwordEl || !password2El) { showToast('注册表单加载失败'); return; }
  let username = usernameEl.value.trim();
  let email = emailEl ? emailEl.value.trim() : '';
  let password = passwordEl.value.trim();
  let password2 = password2El.value.trim();
  if (errEl) errEl.textContent = '';
  if (!username || !password) { if (errEl) errEl.textContent = '请输入用户名和密码'; return; }
  if (password !== password2) { if (errEl) errEl.textContent = '两次密码不一致'; return; }
  if (password.length < 6) { if (errEl) errEl.textContent = '密码至少 6 个字符'; return; }

  let payload = { username: username, password: password };
  if (email) { payload.email = email; }

  authFetch('/api/register', {
    skipAuthExpiry: true,
    method: 'POST',
    body: JSON.stringify(payload)
  }).then(function(resp) { return resp.json(); }).then(function(data) {
    let token = data.token || (data.data && data.data.token);
    let resolvedUsername = data.username || (data.data && data.data.username) || username;
    if (token) {
      setToken(token);
      try { localStorage.setItem('vs_username', resolvedUsername); } catch(e) {}
      updateAuthUI();
      updateAlertBadge();
      updateUserCredits();
      if (typeof window.updateScanCreditsHint === 'function') window.updateScanCreditsHint();
      showToast('注册成功，欢迎 ' + resolvedUsername);
      navigateTo('scan');
    } else {
      if (errEl) errEl.textContent = extractError(data) || '注册失败';
    }
  }).catch(function(e) {
    if (errEl) errEl.textContent = '注册失败: ' + e.message;
  });
}

function doLogout() {
  removeToken();
  try { localStorage.removeItem('vs_username'); } catch(e) {}
  updateAuthUI();
  let badge = document.getElementById('nav-alert-badge');
  if (badge) badge.style.display = 'none';
  showToast('已退出登录');
  navigateTo('home');
}

// ========== Credits ==========
function formatCredits(num) {
  if (num === undefined || num === null) return '--';
  let n = parseInt(num, 10);
  if (isNaN(n)) return String(num);
  return n.toLocaleString('zh-CN');
}

export function updateUserCredits() {
  if (!isLoggedIn()) {
    safeSetText('user-credits', '额度：--');
    return Promise.resolve(null);
  }
  return credits().then(function(data) {
    let balance = data && data.success && data.data && typeof data.data.credits === 'number'
      ? data.data.credits
      : (data && typeof data.credits === 'number' ? data.credits : null);
    safeSetText('user-credits', '额度：' + formatCredits(balance));
    let creditsBalance = document.getElementById('credits-balance');
    if (creditsBalance) creditsBalance.textContent = formatCredits(balance);
    return balance;
  }).catch(function() {
    safeSetText('user-credits', '额度：--');
  });
}

export function loadCreditsUsage(page) {
  page = parseInt(page, 10) || 1;
  let limit = 10;
  let offset = (page - 1) * limit;
  let listEl = document.getElementById('credits-usage-list');
  if (listEl) listEl.innerHTML = '<div style="text-align:center;padding:20px;color:var(--text-secondary)">正在读取使用记录...</div>';
  updateUserCredits();
  usage(limit, offset).then(function(data) {
    let logs = (data && data.data && data.data.logs) || (data && data.logs) || [];
    let total = (data && data.data && data.data.total) || (data && data.total) || logs.length;
    let meta = (data && data.meta) || {};
    let metaLimit = meta.limit || limit;
    let metaOffset = meta.offset || offset;
    let currentPage = Math.floor(metaOffset / metaLimit) + 1;
    let totalPages = Math.max(1, Math.ceil(total / metaLimit));
    renderUsageList(logs);
    renderPagination('credits-pagination', currentPage, totalPages, function(p) { loadCreditsUsage(p); });
    safeSetDisplay('credits-pagination', totalPages > 1 ? 'flex' : 'none');
  }).catch(function(e) {
    if (listEl) listEl.innerHTML = '<div style="text-align:center;padding:20px;color:var(--danger)">读取使用记录失败</div>';
  });
}

function renderUsageList(logs) {
  let listEl = document.getElementById('credits-usage-list');
  if (!listEl) return;
  if (!logs || logs.length === 0) {
    listEl.innerHTML = '<div style="text-align:center;padding:24px;color:var(--text-secondary)">近 30 天内没有额度变动记录</div>';
    return;
  }
  let html = '<div style="display:flex;flex-direction:column;gap:8px">';
  logs.forEach(function(log) {
    let amount = log.amount || 0;
    let amountClass = amount < 0 ? 'var(--danger)' : 'var(--success)';
    let amountText = (amount > 0 ? '+' : '') + amount;
    html += '<div style="display:flex;align-items:center;justify-content:space-between;padding:10px;background:var(--bg);border:1px solid var(--border);border-radius:2px">';
    html += '<div>';
    html += '<div style="font-size:13px;font-weight:600">' + escapeHtml(log.action || '额度变动') + '</div>';
    html += '<div style="font-size:11px;color:var(--text-secondary);margin-top:2px">' + formatDate(log.created_at) + '</div>';
    html += '</div>';
    html += '<div style="text-align:right">';
    html += '<div style="font-size:13px;font-weight:700;color:' + amountClass + '">' + amountText + '</div>';
    html += '<div style="font-size:11px;color:var(--text-secondary);margin-top:2px">余额 ' + formatCredits(log.balance_after) + '</div>';
    html += '</div></div>';
  });
  html += '</div>';
  listEl.innerHTML = html;
}

// ========== 账号 Stats ==========
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
    let avgScore = document.getElementById('stat-avg-score');
    let fixedCount = document.getElementById('stat-fixed-count');
    if (scanCount) scanCount.textContent = stats.scan_count || history.length;
    if (avgScore) {
      if (history.length === 0) {
        avgScore.textContent = '-';
      } else {
        let sum = history.reduce(function(a, b) { return a + (b.score || 0); }, 0);
        avgScore.textContent = Math.round(sum / history.length);
      }
    }
    // 已修复数：取后端真实统计（同 URL 的相邻两次扫描 diff 累计）
    if (fixedCount) fixedCount.textContent = stats.fixed_count || 0;
  }).catch(function() {});
}

// ========== 账号 Tab Navigation ==========
function showProfileTab(tab) {
  document.querySelectorAll('.profile-tab').forEach(function(el) { el.style.display = 'none'; });
  let target = document.getElementById('profile-tab-' + tab);
  if (target) {
    target.style.display = 'block';
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  if (tab === 'history') renderScanHistory();
  if (tab === 'monitor') renderMonitorTargets();
  if (tab === 'ai-config') renderAIConfig();
  if (tab === 'alerts') loadAlerts();
  if (tab === 'notifications') loadNotificationSettings();
  if (tab === 'credits') loadCreditsUsage();
}

function toggleSetting(el, key) {
  let span = document.getElementById('setting-' + key);
  if (!span) return;
  let isOn = span.dataset.enabled === 'true';
  span.dataset.enabled = isOn ? 'false' : 'true';
  span.classList.toggle('on', !isOn);
  let newState = !isOn;
  // Real dark mode toggle
  if (key === 'darkMode') {
    if (newState) {
      document.documentElement.setAttribute('data-theme', 'dark');
      (function(){try{localStorage.setItem('vs_dark','1');}catch(e){}})();
    } else {
      document.documentElement.removeAttribute('data-theme');
      (function(){try{localStorage.removeItem('vs_dark');}catch(e){}})();
    }
    updateThemeIcon(newState);
  }
  // Real auto-save toggle
  if (key === 'auto保存') {
    (function(){try{localStorage.setItem('vs_autosave',newState?'1':'0');}catch(e){}})();
  }
  showToast('设置已更新');
}

// ========== AI Config ==========
function getAIConfig() {
  try {
    let raw = localStorage.getItem('vs_ai_config');
    if (raw) return JSON.parse(raw);
  } catch (e) {}
  return { api_key: '', provider: 'openai', model: '', use_llm: true };
}

function saveAIConfig() {
  let apiKey = document.getElementById('ai-config-apikey').value.trim();
  let provider = document.getElementById('ai-config-provider').value;
  let model = document.getElementById('ai-config-model').value.trim();
  let useLLM = document.getElementById('setting-useLLM').dataset.enabled === 'true';
  let config = { api_key: apiKey, provider: provider, model: model, use_llm: useLLM };
  try {
    localStorage.setItem('vs_ai_config', JSON.stringify(config));
    showToast('安全顾问配置已保存');
  } catch (e) {
    showToast('保存失败：' + (e.message || '浏览器存储受限'), 'error');
  }
}

function clearAIConfig() {
  try {
    localStorage.removeItem('vs_ai_config');
    document.getElementById('ai-config-apikey').value = '';
    document.getElementById('ai-config-provider').value = 'openai';
    document.getElementById('ai-config-model').value = '';
    let span = document.getElementById('setting-useLLM');
    if (span) { span.dataset.enabled = 'true'; span.textContent = '已开启'; span.style.color = 'var(--success)'; }
    showToast('安全顾问配置已清除');
  } catch (e) {}
}

function toggleAISetting(key) {
  let span = document.getElementById('setting-' + (key === 'useLLM' ? 'useLLM' : key));
  if (!span) return;
  let isOn = span.dataset.enabled === 'true';
  span.dataset.enabled = isOn ? 'false' : 'true';
  span.classList.toggle('on', !isOn);
}

function renderAIConfig() {
  let config = getAIConfig();
  let apiKeyEl = document.getElementById('ai-config-apikey');
  let providerEl = document.getElementById('ai-config-provider');
  let modelEl = document.getElementById('ai-config-model');
  let useLLMEl = document.getElementById('setting-useLLM');
  if (apiKeyEl) apiKeyEl.value = config.api_key || '';
  if (providerEl) providerEl.value = config.provider || 'openai';
  if (modelEl) modelEl.value = config.model || '';
  if (useLLMEl) {
    let on = config.use_llm !== false;
    useLLMEl.dataset.enabled = on ? 'true' : 'false';
    useLLMEl.classList.toggle('on', on);
  }
}

// ========== Notification / 告警 Functions ==========
function loadAlerts(page) {
  page = page || 1;
  let listEl = document.getElementById('alerts-list');
  if (!listEl) return;
  listEl.innerHTML = '<div style="text-align:center;padding:20px;color:var(--text-secondary)">正在读取告警...</div>';
  fetch('/api/alerts?limit=20&unread_only=false', { headers: authHeaders() })
    .then(function(r) { return r.json(); })
    .then(function(data) {
      let alerts = data.alerts || [];
      if (alerts.length === 0) {
        listEl.innerHTML = '<div style="text-align:center;padding:20px;color:var(--text-secondary)">暂无告警记录</div>';
        document.getElementById('alerts-pagination').style.display = 'none';
        return;
      }
      let html = '';
      alerts.forEach(function(a) {
        let isRead = a.is_read ? true : false;
        let badge = '';
        if (a.alert_type === 'high_risk_found' || a.alert_type === 'monitor_down') badge = '<span style="background:var(--danger);color:#fff;font-size:11px;padding:2px 6px;border-radius:2px;margin-left:6px">高危</span>';
        else if (a.alert_type === 'score_drop') badge = '<span style="background:var(--warning);color:#fff;font-size:11px;padding:2px 6px;border-radius:2px;margin-left:6px">评分下降</span>';
        else if (a.alert_type === 'scan_complete') badge = '<span style="background:var(--success);color:#fff;font-size:11px;padding:2px 6px;border-radius:2px;margin-left:6px">完成</span>';
        html += '<div class="menu-item" style="margin-bottom:8px;opacity:' + (isRead ? '0.7' : '1') + '">';
        html += '<div style="flex:1">';
        html += '<div style="font-weight:600;font-size:14px">' + escapeHtml(a.title || a.message || '告警') + badge + '</div>';
        html += '<div style="font-size:12px;color:var(--text-secondary);margin-top:4px">' + escapeHtml(a.created_at || '') + '</div>';
        html += '<div style="font-size:13px;color:var(--text);margin-top:4px">' + escapeHtml(a.message || '') + '</div>';
        html += '</div>';
        if (!isRead) {
          html += '<button class="fixer-btn secondary" style="height:32px;padding:0 12px;font-size:12px;margin-left:8px;white-space:nowrap" onclick="markAlertRead(' + a.id + ', event)">标记已读</button>';
        }
        html += '</div>';
      });
      listEl.innerHTML = html;
      document.getElementById('alerts-pagination').style.display = 'none';
      updateAlertBadge();
    })
    .catch(function(e) {
      listEl.innerHTML = '<div style="text-align:center;padding:20px;color:var(--text-secondary)">加载失败</div>';
    });
}

function markAlertRead(alertId, ev) {
  if (ev) ev.stopPropagation();
  fetch('/api/alerts/' + alertId + '/read', { method: 'POST', headers: authHeaders() })
    .then(function(r) { return r.json(); })
    .then(function(data) {
      if (data.success) { loadAlerts(); updateAlertBadge(); }
    });
}

function markAllAlertsRead() {
  fetch('/api/alerts?limit=100', { headers: authHeaders() })
    .then(function(r) { return r.json(); })
    .then(function(data) {
      let alerts = data.alerts || [];
      let unread = alerts.filter(function(a) { return !a.is_read; });
      if (unread.length === 0) { showToast('没有未读告警'); return; }
      let done = 0;
      unread.forEach(function(a) {
        fetch('/api/alerts/' + a.id + '/read', { method: 'POST', headers: authHeaders() })
          .then(function() { done++; if (done >= unread.length) { loadAlerts(); updateAlertBadge(); showToast('已全部标记为已读'); } });
      });
    });
}

function updateAlertBadge() {
  if (!isLoggedIn()) {
    let badge = document.getElementById('nav-alert-badge');
    if (badge) badge.style.display = 'none';
    return;
  }
  fetch('/api/alerts/unread-count', { headers: authHeaders() })
    .then(function(r) { return r.json(); })
    .then(function(data) {
      let badge = document.getElementById('nav-alert-badge');
      if (!badge) return;
      let count = data.unread_count || 0;
      if (count > 0) {
        badge.textContent = count > 99 ? '99+' : count;
        badge.style.display = 'inline-block';
      } else {
        badge.style.display = 'none';
      }
    });
}

function loadNotificationSettings() {
  fetch('/api/me/notifications', { headers: authHeaders() })
    .then(function(r) { return r.json(); })
    .then(function(data) {
      if (data.success) {
        let emailEl = document.getElementById('notify-email-input');
        let webhookEl = document.getElementById('notify-webhook-input');
        let thresholdEl = document.getElementById('notify-threshold-select');
        if (emailEl) emailEl.value = data.email || '';
        if (webhookEl) webhookEl.value = data.webhook || '';
        if (thresholdEl) thresholdEl.value = data.threshold || 'high';
      }
    });
}

function saveNotificationSettings() {
  let email = document.getElementById('notify-email-input').value.trim();
  let webhook = document.getElementById('notify-webhook-input').value.trim();
  let threshold = document.getElementById('notify-threshold-select').value;
  fetch('/api/me/notifications', {
    method: 'POST',
    headers: Object.assign({'Content-Type': 'application/json'}, authHeaders()),
    body: JSON.stringify({ email: email, webhook: webhook, threshold: threshold }),
  })
    .then(function(r) { return r.json(); })
    .then(function(data) {
      if (data.success) { showToast('通知设置已保存', 'success'); }
      else { showToast(data.error || '保存失败', 'error'); }
    });
}

function toggleApiKeyVisibility() {
  let input = document.getElementById('ai-config-apikey');
  let btn = document.getElementById('ai-config-eye');
  if (!input || !btn) return;
  if (input.type === 'password') {
    input.type = 'text';
    btn.textContent = '隐藏';
  } else {
    input.type = 'password';
    btn.textContent = '显示';
  }
}

// ========== Module Init ==========
export function init() {
  let loginPass = safeGetElement('login-password');
  if (loginPass) { loginPass.addEventListener('keydown', function(e) { if (e.key === 'Enter') doLogin(); }); }
  let regEmail = safeGetElement('reg-email');
  let regPass = safeGetElement('reg-password');
  let regConfirm = safeGetElement('reg-password2');
  if (regEmail) { regEmail.addEventListener('keydown', function(e) { if (e.key === 'Enter') doRegister(); }); }
  if (regPass) { regPass.addEventListener('keydown', function(e) { if (e.key === 'Enter') doRegister(); }); }
  if (regConfirm) { regConfirm.addEventListener('keydown', function(e) { if (e.key === 'Enter') doRegister(); }); }

  try { updateProfileStats(); } catch(e) { console.warn('updateProfileStats error:', e); }
  try { updateAuthUI(); } catch(e) { console.warn('updateAuthUI error:', e); }
  try { refreshLoginStatus(); } catch(e) { console.warn('refreshLoginStatus error:', e); }
  try { updateUserCredits(); } catch(e) { console.warn('updateUserCredits error:', e); }
  try { renderAIConfig(); } catch(e) { console.warn('renderAIConfig error:', e); }

  if (typeof window !== 'undefined') {
    window.updateUserCredits = updateUserCredits;
    window.loadCreditsUsage = loadCreditsUsage;
  }
}

// ========== Exports ==========
export {
  toggleAuthForm,
  updateAuthUI,
  refreshLoginStatus,
  doResetPassword,
  doLogin,
  doRegister,
  doLogout,
  updateProfileStats,
  showProfileTab,
  toggleSetting,
  getAIConfig,
  saveAIConfig,
  clearAIConfig,
  toggleAISetting,
  loadAlerts,
  markAlertRead,
  markAllAlertsRead,
  updateAlertBadge,
  loadNotificationSettings,
  saveNotificationSettings,
  toggleApiKeyVisibility,
  renderAIConfig
};


if (typeof window !== 'undefined') {
  window.doResetPassword = function() {
    let passwordEl = document.getElementById('reset-password-token');
    let newPasswordEl = document.getElementById('reset-new-password');
    let confirmEl = document.getElementById('reset-new-password2');
    let token = passwordEl ? passwordEl.value.trim() : '';
    let newPassword = newPasswordEl ? newPasswordEl.value.trim() : '';
    let confirmPassword = confirmEl ? confirmEl.value.trim() : '';
    if (!token) { showToast('请输入重置 令牌'); return; }
    if (!newPassword || newPassword.length < 6) { showToast('新密码至少 6 个字符'); return; }
    if (newPassword !== confirmPassword) { showToast('两次密码不一致'); return; }
    apiPost('/api/auth/password-reset/confirm', { token: token, new_password: newPassword }).then(function(data) {
      if (data && data.success) {
        showToast('密码重置成功，请重新登录');
        toggleAuthForm('login');
      } else {
        showToast(extractError(data) || '密码重置失败');
      }
    }).catch(function(e) { showToast('密码重置失败：' + e.message); });
  };
  window.doResendVerification = function() {
    resendVerification().then(function(data) {
      showToast((data && data.message) || '验证邮件已重新发送');
    }).catch(function(e) { showToast('重新发送失败：' + e.message); });
  };
  window.doVerifyEmailFromToken = function() {
    let tokenEl = document.getElementById('verify-email-token');
    let token = tokenEl ? tokenEl.value.trim() : '';
    if (!token) { showToast('请输入邮箱验证 令牌'); return; }
    apiPost('/api/auth/verify-email', { token: token }).then(function(data) {
      if (data && data.success) {
        showToast('邮箱验证成功');
      } else {
        showToast(extractError(data) || '邮箱验证失败');
      }
    }).catch(function(e) { showToast('邮箱验证失败：' + e.message); });
  };
}


if (typeof window !== 'undefined') {
  window.refreshAuthChallenge = window.refreshAuthChallenge || function(){};
}
