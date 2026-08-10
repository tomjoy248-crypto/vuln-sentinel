// ========== Assets Page Module ==========

import {
  escapeHtml,
  safeGetElement,
  safeSetHtml,
  safeSetDisplay,
  copyToClipboard,
  escapeAttr
} from '../utils.js';

import { showToast } from '../components/Toast.js';

import {
  authFetch,
  apiGet,
  apiPost,
  apiPatch,
  apiDelete,
  listAssets,
  createAsset,
  updateAsset,
  deleteAsset as apiDeleteAsset
} from '../api.js';

// ===== Internal helpers (originally in main.js) =====

function getToken() {
  try { return localStorage.getItem('vs_token'); } catch(e) { return null; }
}

function isLoggedIn() {
  return !!getToken();
}

function extractError(data) {
  if (!data) return '未知错误';
  if (typeof data.error === 'string' && data.error) return data.error;
  if (typeof data.detail === 'string' && data.detail) return data.detail;
  if (typeof data.message === 'string' && data.message) return data.message;
  // Pydantic 422: detail 是数组 [{type, loc, msg, input}]
  if (Array.isArray(data.detail) && data.detail.length > 0) {
    let msgs = data.detail.map(function(item) {
      if (item && typeof item.msg === 'string') return item.msg;
      if (item && typeof item === 'string') return item;
      return '';
    }).filter(Boolean);
    if (msgs.length > 0) return msgs.join('；');
  }
  return '未知错误';
}

// ===== State =====

let allAssets = [];

// ===== Assets =====

export function loadAssets() {
  if (!isLoggedIn()) {
    safeSetHtml('asset-list', '');
    safeSetDisplay('asset-empty', 'block');
    let empty = document.getElementById('asset-empty');
    if (empty) {
      empty.innerHTML = '<div class="ticket-empty-icon"></div><p>请先登录查看资产</p><p class="ticket-empty-hint">登录后管理您的域名资产</p>';
    }
    return;
  }
  authFetch('/api/assets').then(function(r) { return r.json(); }).then(function(data) {
    if (data && data.assets) {
      allAssets = data.assets;
      renderAssets(allAssets);
    } else {
      allAssets = [];
      renderAssets(allAssets);
    }
  }).catch(function(e) {
    showToast('加载资产失败: ' + e.message, 'error');
    allAssets = [];
    renderAssets(allAssets);
  });
}

export function renderAssets(assets) {
  let list = document.getElementById('asset-list');
  let empty = document.getElementById('asset-empty');
  if (!list) return;
  if (!assets || assets.length === 0) {
    list.innerHTML = '';
    if (empty) {
      empty.style.display = 'block';
      empty.innerHTML = '<div class="ticket-empty-icon"></div><p>暂无资产</p><p class="ticket-empty-hint">添加您的第一个域名资产，开始安全扫描</p>';
    }
    return;
  }
  if (empty) empty.style.display = 'none';

  let html = '<div class="asset-table-wrap"><table class="asset-table">';
  html += '<thead><tr><th>域名</th><th>负责人</th><th>验证状态</th><th>评分</th><th>操作</th></tr></thead><tbody>';
  assets.forEach(function(a) {
    let verified = a.verified || false;
    let badgeClass = verified ? 'verified' : 'pending';
    let badgeText = verified ? '已验证' : '待人工复核';
    let score = a.score;
    let scoreClass = 'high';
    if (score === null || score === undefined) {
      score = '-';
      scoreClass = '';
    } else if (score < 50) {
      scoreClass = 'low';
    } else if (score < 75) {
      scoreClass = 'medium';
    }
    html += '<tr>';
    html += '<td data-label="域名"><div class="asset-domain">' + escapeHtml(a.domain || '') + '</div><div class="asset-meta">' + escapeHtml(a.description || '') + '</div></td>';
    html += '<td data-label="负责人">' + escapeHtml(a.owner || '-') + '</td>';
    html += '<td data-label="验证状态"><span class="asset-badge ' + badgeClass + '">' + badgeText + '</span></td>';
    html += '<td data-label="评分"><div class="asset-score ' + scoreClass + '">' + score + '</div></td>';
    html += '<td data-label="操作"><div class="asset-actions">';
    html += '<button class="asset-btn primary" onclick="scanAsset(' + a.id + ', \'' + escapeAttr(a.domain || '') + '\')">扫描</button>';
    html += '<button class="asset-btn secondary" onclick="editAsset(' + a.id + ')">编辑</button>';
    html += '<button class="asset-btn danger" onclick="deleteAsset(' + a.id + ')">删除</button>';
    html += '</div></td>';
    html += '</tr>';
  });
  html += '</tbody></table></div>';
  list.innerHTML = html;
}

export function createTeam() {
  let name = document.getElementById('team-name').value.trim();
  if (!name) { showToast('请输入团队名', 'error'); return; }
  authFetch('/api/teams', { method: 'POST', body: JSON.stringify({ name: name }) })
    .then(function(r) { return r.json(); }).then(function(data) {
      if (data.id || data.team_id) {
        showToast('团队已创建', 'success');
        if (window.loadEvolution) window.loadEvolution();
      } else {
        showToast('创建失败: ' + JSON.stringify(data), 'error');
      }
    }).catch(function(e) { showToast('创建失败: ' + e.message, 'error'); });
}

export function addAsset() {
  let domain = document.getElementById('asset-domain').value.trim();
  let owner = document.getElementById('asset-owner').value.trim();
  let description = document.getElementById('asset-description').value.trim();
  let errEl = document.getElementById('asset-form-error');
  if (!domain) {
    if (errEl) { errEl.textContent = '请输入域名'; errEl.style.display = 'block'; }
    return;
  }
  if (errEl) errEl.style.display = 'none';
  authFetch('/api/assets', {
    method: 'POST',
    body: JSON.stringify({ domain: domain, owner: owner, description: description })
  }).then(function(r) { return r.json(); }).then(function(data) {
    if (data.id || data.asset_id) {
      showToast('资产添加成功', 'success');
      document.getElementById('asset-domain').value = '';
      document.getElementById('asset-owner').value = '';
      document.getElementById('asset-description').value = '';
      loadAssets();
    } else {
      let msg = extractError(data) || '添加失败';
      if (errEl) { errEl.textContent = msg; errEl.style.display = 'block'; }
    }
  }).catch(function(e) {
    if (errEl) { errEl.textContent = '添加失败: ' + e.message; errEl.style.display = 'block'; }
  });
}

export function editAsset(assetId) {
  let asset = allAssets.find(function(a) { return a.id === assetId; });
  if (!asset) return;
  let newDomain = prompt('修改域名:', asset.domain || '');
  if (newDomain === null) return;
  let newOwner = prompt('修改负责人:', asset.owner || '');
  if (newOwner === null) return;
  let newDesc = prompt('修改描述:', asset.description || '');
  if (newDesc === null) return;
  authFetch('/api/assets/' + assetId, {
    method: 'PATCH',
    body: JSON.stringify({ domain: newDomain.trim(), owner: newOwner.trim(), description: newDesc.trim() })
  }).then(function(r) { return r.json(); }).then(function(data) {
    if (data.id || data.success) {
      showToast('资产更新成功', 'success');
      loadAssets();
    } else {
      showToast(extractError(data) || '更新失败', 'error');
    }
  }).catch(function(e) {
    showToast('更新失败: ' + e.message, 'error');
  });
}

export function deleteAsset(assetId) {
  if (!confirm('确定要删除此资产吗？')) return;
  authFetch('/api/assets/' + assetId, { method: 'DELETE' }).then(function(r) {
    if (r.ok || r.status === 204) {
      showToast('资产已删除', 'success');
      loadAssets();
    } else {
      return r.json().then(function(data) { throw new Error(extractError(data) || '删除失败'); });
    }
  }).catch(function(e) {
    showToast('删除失败: ' + e.message, 'error');
  });
}

export function scanAsset(assetId, domain) {
  if (!domain) return;
  let url = domain;
  if (!/^https?:\/\//i.test(url)) url = 'https://' + url;
  document.getElementById('scan-url').value = url;
  if (window.navigateTo) window.navigateTo('scan');
  if (window.startScanDirect) window.startScanDirect();
}

