/** 后端 API 封装 */

function normalizeBase(base) {
  if (!base) return '';
  return String(base).replace(/\/+$/, '');
}

function buildApiBases() {
  const bases = [];
  const explicit = typeof __API_BASE__ !== 'undefined' ? __API_BASE__ : '';
  if (explicit) bases.push(normalizeBase(explicit));
  if (typeof window !== 'undefined' && window.__CONFIG__ && window.__CONFIG__.api_base_url) {
    bases.push(normalizeBase(window.__CONFIG__.api_base_url));
  }
  const isTauriWindow = typeof window !== 'undefined' && (
    window.location.protocol === 'tauri:' ||
    window.location.protocol === 'asset:' ||
    window.location.hostname === 'tauri.localhost'
  );
  if (typeof window !== 'undefined' &&
      (window.location.protocol === 'http:' || window.location.protocol === 'https:') &&
      !isTauriWindow) {
    bases.push('');
  }
  bases.push('http://127.0.0.1:8011');
  return [...new Set(bases)];
}

export const API_BASE = buildApiBases()[0] || '';

/**
 * Parse a JSON API response without exposing the browser's raw JSON parse error.
 * A HTML response normally means the desktop shell reached its static page
 * instead of the local backend, so report that actionable condition directly.
 */
export async function parseJsonResponse(resp) {
  const contentType = (resp.headers && resp.headers.get('content-type')) || '';
  const text = await resp.text();
  const trimmed = text.trim();
  const looksLikeHtml = /^<!doctype\s+html\b/i.test(trimmed) || /^<html[\s>]/i.test(trimmed);

  if (looksLikeHtml || (!contentType.toLowerCase().includes('json') && trimmed.startsWith('<'))) {
    throw new Error('本地后端没有正确响应，请确认安装包内本地服务已启动后重试');
  }

  if (!trimmed) return {};
  try {
    return JSON.parse(trimmed);
  } catch (error) {
    throw new Error('本地后端返回了无效数据，请重启安装包后重试');
  }
}

function delay(ms) {
  return new Promise(function(resolve) { setTimeout(resolve, ms); });
}

export function getToken() {
  try { return localStorage.getItem('vs_token'); } catch (e) { return null; }
}

export function setToken(t) {
  try { localStorage.setItem('vs_token', t); } catch (e) {}
}

export function removeToken() {
  try { localStorage.removeItem('vs_token'); } catch (e) {}
}

export function isLoggedIn() {
  return !!getToken();
}

export function getUsername() {
  try { return localStorage.getItem('vs_username') || ''; } catch (e) { return ''; }
}

export function getRole() {
  try { return localStorage.getItem('vs_role') || 'member'; } catch (e) { return 'member'; }
}

export function setRole(role) {
  try { localStorage.setItem('vs_role', role || 'member'); } catch (e) {}
}

export function authHeaders() {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = 'Bearer ' + token;
  return headers;
}

export async function authFetch(url, options = {}) {
  options.headers = Object.assign({}, authHeaders(), options.headers || {});
  const skipAuthExpiry = !!options.skipAuthExpiry;
  const baseCandidates = buildApiBases();
  const requestCandidates = [];
  for (const base of baseCandidates) {
    const normalizedBase = normalizeBase(base);
    const primaryUrl = normalizedBase ? normalizedBase + url : url;
    requestCandidates.push(primaryUrl);
    if (url.startsWith('/api/') && !url.startsWith('/api/v1/') && normalizedBase) {
      requestCandidates.push(normalizedBase + '/api/v1' + url.slice('/api'.length));
    }
  }

  let lastResponse = null;
  let lastError = null;
  for (const requestUrl of requestCandidates) {
    let attempt = 0;
    while (attempt < 2) {
      try {
        const resp = await fetch(requestUrl, options);
        lastResponse = resp;
        if (resp.status === 404 && requestCandidates.length > 1) {
          break;
        }
        if (resp.status === 401 && !skipAuthExpiry) {
          removeToken();
          try { localStorage.removeItem('vs_username'); } catch (e) {}
          throw new Error('登录状态已过期，请重新登录后再继续使用扫描功能');
        }
        return resp;
      } catch (err) {
        lastError = err;
        attempt += 1;
        if (attempt < 2) {
          await delay(250);
          continue;
        }
        break;
      }
    }
  }

  if (lastResponse) return lastResponse;
  if (lastError && lastError.message) {
    throw new Error('无法连接扫描服务，请确认本地后端已启动');
  }
  throw new Error('无法连接扫描服务，请确认本地后端已启动');
}

export async function apiPost(url, body) {
  const resp = await authFetch(url, {
    skipAuthExpiry: true,
    method: 'POST',
    body: JSON.stringify(body)
  });
  const data = await parseJsonResponse(resp);
  if (data && typeof data === 'object') {
    data._status = resp.status;
    data._statusText = resp.statusText;
  }
  return data;
}

export async function apiGet(url) {
  const resp = await authFetch(url);
  const data = await parseJsonResponse(resp);
  if (data && typeof data === 'object') {
    data._status = resp.status;
    data._statusText = resp.statusText;
  }
  return data;
}

export async function apiDelete(url) {
  const resp = await authFetch(url, { method: 'DELETE' });
  const data = await parseJsonResponse(resp);
  if (data && typeof data === 'object') {
    data._status = resp.status;
    data._statusText = resp.statusText;
  }
  return data;
}

export async function apiPatch(url, body) {
  const resp = await authFetch(url, {
    method: 'PATCH',
    body: JSON.stringify(body)
  });
  const data = await parseJsonResponse(resp);
  if (data && typeof data === 'object') {
    data._status = resp.status;
    data._statusText = resp.statusText;
  }
  return data;
}

// Public config
export function publicConfig() { return apiGet('/api/config'); }

// Auth
export function register(body) { return apiPost('/api/register', body); }
export function login(body) { return apiPost('/api/login', body); }
export function resetPassword(body) { return apiPost('/api/reset-password', body); }
export function requestPasswordReset(body) { return apiPost('/api/auth/password-reset/request', body); }
export function confirmPasswordReset(body) { return apiPost('/api/auth/password-reset/confirm', body); }
export function resendVerification() { return apiPost('/api/auth/resend-verification', {}); }
export function verifyEmailToken(body) { return apiPost('/api/auth/verify-email', body); }
export function me() { return apiGet('/api/me'); }
export function credits() { return apiGet('/api/me/credits'); }
export function usage(limit = 20, offset = 0) {
  return apiGet('/api/usage?limit=' + encodeURIComponent(limit) + '&offset=' + encodeURIComponent(offset));
}

// Scan
export function scan(body) { return apiPost('/api/scan', body); }
export function history(limit = 50) { return apiGet('/api/history?limit=' + limit); }
export function deleteHistory() { return apiDelete('/api/history'); }
export function saveRequestHistory(body) { return apiPost('/api/request-history', body); }
export function listRequestHistory(limit = 50, offset = 0) { return apiGet('/api/request-history?limit=' + limit + '&offset=' + offset); }
export function replayRequestHistory(id) { return apiPost('/api/request-history/' + encodeURIComponent(id) + '/replay', {}); }
export function listScanTasks(status = '') { return apiGet('/api/scan/tasks' + (status ? '?status=' + encodeURIComponent(status) : '')); }
export function pauseScanTask(id) { return apiPost('/api/scan/tasks/' + encodeURIComponent(id) + '/pause', {}); }
export function resumeScanTask(id) { return apiPost('/api/scan/tasks/' + encodeURIComponent(id) + '/resume', {}); }
export function cancelScanTask(id) { return apiPost('/api/scan/tasks/' + encodeURIComponent(id) + '/cancel', {}); }
export function retryScanTask(id) { return apiPost('/api/scan/tasks/' + encodeURIComponent(id) + '/retry', {}); }
export function trend(url, limit = 30) {
  let q = '/api/trend?limit=' + limit;
  if (url) q += '&url=' + encodeURIComponent(url);
  return apiGet(q);
}
export function verifyFix(body) { return apiPost('/api/verify-fix', body); }

// Tickets
export function createTicket(body) { return apiPost('/api/fix-tickets', body); }
export function listTickets(status) {
  let q = '/api/fix-tickets';
  if (status) q += '?status=' + encodeURIComponent(status);
  return apiGet(q);
}
export function getTicket(id) { return apiGet('/api/fix-tickets/' + id); }
export function updateTicket(id, body) { return apiPatch('/api/fix-tickets/' + id, body); }
export function deleteTicket(id) { return apiDelete('/api/fix-tickets/' + id); }
export function exportTicket(id, format = 'markdown') {
  return authFetch('/api/fix-tickets/' + id + '/export?format=' + encodeURIComponent(format), {
    method: 'GET'
  });
}
export function listTicketCollaborators() { return apiGet('/api/fix-tickets/meta/collaborators'); }

// Assets
export function listAssets() { return apiGet('/api/assets'); }
export function createAsset(body) { return apiPost('/api/assets', body); }
export function updateAsset(id, body) { return apiPatch('/api/assets/' + id, body); }
export function deleteAsset(id) { return apiDelete('/api/assets/' + id); }

// Alerts
export function loadAlerts(page = 1, limit = 20, unreadOnly = false) {
  return apiGet('/api/alerts?page=' + page + '&limit=' + limit + '&unread_only=' + unreadOnly);
}
export function markAlertRead(id) { return apiPost('/api/alerts/' + id + '/read', {}); }

// AI Advisor
export function aiAdvisor(body) { return apiPost('/api/ai-advisor', body); }
export function aiStatus() { return apiGet('/api/ai-status'); }

export function adminAuditLogs(limit = 50, offset = 0, action = '', filters = {}) {
  let q = '/api/admin/audit-logs?limit=' + encodeURIComponent(limit) + '&offset=' + encodeURIComponent(offset);
  if (action) q += '&action=' + encodeURIComponent(action);
  ['user_id', 'username', 'resource_type', 'resource_id', 'status', 'start_at', 'end_at'].forEach(function(key) {
    if (filters[key]) q += '&' + key + '=' + encodeURIComponent(filters[key]);
  });
  return apiGet(q);
}
export function adminAuditSummary() { return apiGet('/api/admin/audit-logs/summary'); }
export function adminAuditExport(filters = {}) {
  const q = new URLSearchParams(filters).toString();
  return apiGet('/api/admin/audit-logs/export' + (q ? '?' + q : ''));
}

export function adminEmailLogs(limit = 50, offset = 0, emailType = '', status = '') {
  let q = '/api/admin/email-logs?limit=' + encodeURIComponent(limit) + '&offset=' + encodeURIComponent(offset);
  if (emailType) q += '&email_type=' + encodeURIComponent(emailType);
  if (status) q += '&status=' + encodeURIComponent(status);
  return apiGet(q);
}

// SRC 报告导出 / 验证复现 / 反馈
export function exportSRCReport(body) {
  return authFetch('/api/report/src-export', {
    method: 'POST',
    body: JSON.stringify(body)
  });
}
export function verifyReproduce(body) { return apiPost('/api/finding/verify-reproduce', body); }
export function findingFeedback(body) { return apiPost('/api/finding/feedback', body); }
export function listFindingFeedback(scanId) {
  return apiGet('/api/finding/feedback?scan_id=' + encodeURIComponent(scanId));
}

// Team
export function team() { return apiGet('/api/team'); }
export function createTeam() { return apiPost('/api/team/create', {}); }
export function joinTeam(body) { return apiPost('/api/team/join', body); }

// Billing
export function billingPlans() { return apiGet('/api/billing/plans'); }
export function createOrder(body) { return apiPost('/api/billing/order', body); }
export function getOrderStatus(transactionId) { return apiGet('/api/billing/order/' + encodeURIComponent(transactionId)); }
export function purchasePlan(body) { return apiPost('/api/billing/purchase', body); }
export function recharges(limit = 50, offset = 0) {
  return apiGet('/api/billing/recharges?limit=' + encodeURIComponent(limit) + '&offset=' + encodeURIComponent(offset));
}
