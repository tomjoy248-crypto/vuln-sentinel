/** 后端 API 封装 */

export const API_BASE = '';

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

export function authHeaders() {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = 'Bearer ' + token;
  return headers;
}

export async function authFetch(url, options = {}) {
  options.headers = Object.assign({}, authHeaders(), options.headers || {});
  const resp = await fetch(API_BASE + url, options);
  return resp;
}

export async function apiPost(url, body) {
  const resp = await authFetch(url, {
    method: 'POST',
    body: JSON.stringify(body)
  });
  return resp.json();
}

export async function apiGet(url) {
  const resp = await authFetch(url);
  return resp.json();
}

export async function apiDelete(url) {
  const resp = await authFetch(url, { method: 'DELETE' });
  return resp.json();
}

export async function apiPatch(url, body) {
  const resp = await authFetch(url, {
    method: 'PATCH',
    body: JSON.stringify(body)
  });
  return resp.json();
}

// Auth
export function register(body) { return apiPost('/api/register', body); }
export function login(body) { return apiPost('/api/login', body); }
export function resetPassword(body) { return apiPost('/api/reset-password', body); }
export function me() { return apiGet('/api/me'); }

// Scan
export function scan(body) { return apiPost('/api/scan', body); }
export function history(limit = 50) { return apiGet('/api/history?limit=' + limit); }
export function deleteHistory() { return apiDelete('/api/history'); }
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

// Team
export function team() { return apiGet('/api/team'); }
export function createTeam() { return apiPost('/api/team/create', {}); }
export function joinTeam(body) { return apiPost('/api/team/join', body); }
