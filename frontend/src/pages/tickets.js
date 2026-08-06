// ========== Fix Tickets (store + service layer) ==========
import { escapeHtml, safeSetHtml, safeSetDisplay, copyToClipboard, isPaymentRequired, paymentRequiredMessage } from '../utils.js';
import { showToast } from '../components/Toast.js';
import { isLoggedIn, apiGet } from '../api.js';
import { appStore } from '../store.js';
import * as ticketService from '../services/ticketService.js';
import { updateUserCredits } from './profile.js';

// Label / style helpers
const TicketHelpers = {
  severityClass: function (severity) {
    if (severity === 'high' || severity === 'critical') return 'high';
    if (severity === 'medium') return 'medium';
    return 'low';
  },
  severityLabel: function (severity) {
    return { critical: '严重', high: '高危', medium: '中危', low: '低危' }[severity] || severity;
  },
  statusLabel: function (status) {
    return {
      pending: '待修复',
      confirmed: '已确认',
      applying: '应用中',
      in_progress: '修复中',
      fixed: '已修复',
      failed: '修复失败',
      rolled_back: '已回滚',
      ignored: '已忽略'
    }[status] || status;
  }
};

let ticketsPageInited = false;

export function initTicketsPage(containerSelector) {
  if (ticketsPageInited) return;
  ticketsPageInited = true;

  const container = containerSelector ? document.querySelector(containerSelector) : document.body;
  if (!container) return;

  container.addEventListener('click', handleTicketClick);
  container.addEventListener('change', handleTicketChange);
}

function handleTicketClick(e) {
  // Let checkbox interactions be handled by the change listener.
  if (e.target.closest('.ticket-checkbox') || e.target.closest('.ticket-check')) return;

  const actionEl = e.target.closest('[data-action]');
  if (!actionEl) return;

  const action = actionEl.dataset.action;
  const id = actionEl.dataset.id ? parseInt(actionEl.dataset.id, 10) : null;
  const status = actionEl.dataset.status || null;

  switch (action) {
    case 'switch-ticket-tab':
      if (status) switchTicketTab(status);
      break;
    case 'show-detail':
      if (id) showTicketDetail(id);
      break;
    case 'verify':
      if (id) verifyTicket(id);
      break;
    case 'edit-notes':
      if (id) editTicketNotes(id);
      break;
    case 'open-fixer':
      if (id) openTicketFixer(id);
      break;
    case 'open-report':
      if (id) openTicketReport(id);
      break;
    case 'copy-summary':
      if (id) copyTicketSummary(id);
      break;
    case 'delete':
      if (id) deleteTicket(id);
      break;
    case 'batch-update':
      if (status) batchUpdateTickets(status);
      break;
    case 'batch-delete':
      batchDeleteTickets();
      break;
    case 'toggle-select-all':
      toggleSelectAllTickets(actionEl);
      break;
  }
}

function handleTicketChange(e) {
  const target = e.target;

  if (target.classList.contains('ticket-checkbox')) {
    updateTicketSelection();
    return;
  }

  const actionEl = target.closest('[data-action]');
  if (!actionEl) return;

  const action = actionEl.dataset.action;
  const id = actionEl.dataset.id ? parseInt(actionEl.dataset.id, 10) : null;

  switch (action) {
    case 'change-status':
      if (id) updateTicketStatus(id, target.value);
      break;
    case 'toggle-select-all':
      toggleSelectAllTickets(target);
      break;
  }
}

export function switchTicketTab(status) {
  ticketService.setFilter(status);
  document.querySelectorAll('.ticket-tab').forEach(function (t) {
    t.classList.toggle('active', t.dataset.status === status);
  });
  renderTickets();
}

export function loadTickets() {
  if (!isLoggedIn()) {
    safeSetDisplay('ticket-workbench', 'none');
    safeSetDisplay('ticket-empty', 'block');
    safeSetDisplay('ticket-batch-bar', 'none');
    safeSetHtml('ticket-empty', '<div class="ticket-empty"><div class="ticket-empty-icon"></div><p>请先登录查看工单</p></div>');
    return;
  }
  return ticketService.loadTickets().then(function () {
    renderTickets();
  }).catch(function (e) {
    showToast('加载工单失败: ' + e.message, 'error');
  });
}

export function renderTickets() {
  let list = document.getElementById('ticket-list');
  let empty = document.getElementById('ticket-empty');
  let batchBar = document.getElementById('ticket-batch-bar');
  let workbench = document.getElementById('ticket-workbench');
  let detailPanel = document.getElementById('ticket-detail-panel');
  if (!list) return;

  let tickets = ticketService.getFilteredTickets();
  if (tickets.length === 0) {
    list.innerHTML = '';
    if (empty) empty.style.display = 'block';
    if (batchBar) batchBar.style.display = 'none';
    if (workbench) workbench.style.display = 'none';
    if (detailPanel) detailPanel.innerHTML = '<div class="ticket-detail-empty">选择左侧工单查看详情</div>';
    return;
  }

  if (empty) empty.style.display = 'none';
  if (batchBar) batchBar.style.display = 'flex';
  if (workbench) workbench.style.display = 'flex';

  let html = '';
  tickets.forEach(function (t) {
    let severityClass = TicketHelpers.severityClass(t.severity);
    let severityLabel = TicketHelpers.severityLabel(t.severity);
    let statusLabel = TicketHelpers.statusLabel(t.status);
    html += '<tr class="ticket-row" data-action="show-detail" data-id="' + t.id + '">';
    html += '<td><label class="ticket-check"><input type="checkbox" class="ticket-checkbox" value="' + t.id + '"></label></td>';
    html += '<td class="ticket-title-cell">' + escapeHtml(t.finding_name) + '</td>';
    html += '<td><span class="ticket-severity ' + severityClass + '">' + severityLabel + '</span></td>';
    html += '<td><span class="ticket-status-badge">' + statusLabel + '</span></td>';
    html += '<td class="ticket-date-cell">' + (t.created_at || '') + '</td>';
    html += '</tr>';
  });
  list.innerHTML = html;
  updateTicketSelection();
}

export function showTicketDetail(id) {
  let ticket = ticketService.getTicketById(id);
  if (!ticket) return;
  let panel = document.getElementById('ticket-detail-panel');
  if (!panel) return;

  let severityClass = TicketHelpers.severityClass(ticket.severity);
  let severityLabel = TicketHelpers.severityLabel(ticket.severity);
  let statusLabel = TicketHelpers.statusLabel(ticket.status);

  let html = '<div class="ticket-detail-header">';
  html += '<div class="ticket-detail-title">' + escapeHtml(ticket.finding_name) + '</div>';
  html += '<div class="ticket-detail-badges"><span class="ticket-severity ' + severityClass + '">' + severityLabel + '</span><span class="ticket-status-badge">' + statusLabel + '</span></div>';
  html += '</div>';
  html += '<div class="ticket-detail-meta">工单 #' + ticket.id + (ticket.scan_id ? ' · 扫描 #' + ticket.scan_id : '') + ' · ' + (ticket.created_at || '') + '</div>';
  html += '<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px">';
  html += '<div style="background:rgba(75,110,175,0.12);color:var(--primary-light);border:1px solid rgba(75,110,175,0.28);padding:4px 10px;border-radius:999px;font-size:12px">建议：' + (ticket.status === 'fixed' ? '尽快复测确认' : ticket.status === 'failed' ? '回看失败原因并回滚' : ticket.status === 'applying' ? '等待变更生效后复测' : '推进修复并保留变更记录') + '</div>';
  html += '<div style="background:rgba(75,110,175,0.12);color:var(--primary-light);border:1px solid rgba(75,110,175,0.28);padding:4px 10px;border-radius:999px;font-size:12px">优先级：' + severityLabel + '</div>';
  if (ticket.finding_type) html += '<div style="background:rgba(75,110,175,0.12);color:var(--primary-light);border:1px solid rgba(75,110,175,0.28);padding:4px 10px;border-radius:999px;font-size:12px">类型：' + escapeHtml(ticket.finding_type) + '</div>';
  html += '</div>';

  // 闭环时间线
  html += '<div class="ticket-detail-section"><div class="ticket-detail-label">修复闭环</div>';
  html += '<div class="ticket-timeline" id="ticket-timeline-' + ticket.id + '"><div class="ticket-timeline-loading">正在读取时间线...</div></div></div>';

  if (ticket.fix_code) {
    html += '<div class="ticket-detail-section"><div class="ticket-detail-label">修复代码</div><pre class="ticket-detail-code">' + escapeHtml(ticket.fix_code) + '</pre></div>';
  }
  if (ticket.url) {
    html += '<div class="ticket-detail-section"><div class="ticket-detail-label">漏洞位置</div><code class="ticket-detail-url">' + escapeHtml(ticket.url) + '</code></div>';
  }
  if (ticket.notes) {
    html += '<div class="ticket-detail-section"><div class="ticket-detail-label">备注</div><div class="ticket-detail-notes">' + escapeHtml(ticket.notes) + '</div></div>';
  }
  // diff 摘要
  if (ticket.diff_summary && ticket.diff_summary !== '{}') {
    try {
      let diff = JSON.parse(ticket.diff_summary);
      html += '<div class="ticket-detail-section"><div class="ticket-detail-label">复测结果</div>';
      html += '<div class="ticket-diff-summary">';
      if (diff.verified_fixed) {
        html += '<div class="ticket-diff-item success">已验证修复</div>';
      }
      if (diff.summary) {
        html += '<div class="ticket-diff-stats">消除 ' + (diff.summary.eliminated_count || 0) + ' · 新增 ' + (diff.summary.new_count || 0) + ' · 保留 ' + (diff.summary.retained_count || 0) + '</div>';
        html += '<div class="ticket-diff-score">评分变化：' + (diff.before_score || 0) + ' → ' + (diff.after_score || 0) + ' (' + (diff.score_delta > 0 ? '+' : '') + diff.score_delta + ')</div>';
      }
      html += '</div></div>';
    } catch (e) {}
  }
  html += '<div class="ticket-detail-actions">';
  html += '<select class="ticket-status-select" data-action="change-status" data-id="' + ticket.id + '" title="选择当前修复进度">';
  html += '<option value="pending"' + (ticket.status === 'pending' ? ' selected' : '') + '>待修复</option>';
  html += '<option value="confirmed"' + (ticket.status === 'confirmed' ? ' selected' : '') + '>已确认</option>';
  html += '<option value="applying"' + (ticket.status === 'applying' ? ' selected' : '') + '>应用中</option>';
  html += '<option value="in_progress"' + (ticket.status === 'in_progress' ? ' selected' : '') + '>修复中</option>';
  html += '<option value="fixed"' + (ticket.status === 'fixed' ? ' selected' : '') + '>已修复</option>';
  html += '<option value="failed"' + (ticket.status === 'failed' ? ' selected' : '') + '>修复失败</option>';
  html += '<option value="rolled_back"' + (ticket.status === 'rolled_back' ? ' selected' : '') + '>已回滚</option>';
  html += '<option value="ignored"' + (ticket.status === 'ignored' ? ' selected' : '') + '>已忽略</option>';
  html += '</select>';
  html += '<button class="ticket-btn primary" data-action="verify" data-id="' + ticket.id + '">复测验证</button>';
  html += '<button class="ticket-btn secondary" data-action="open-fixer" data-id="' + ticket.id + '">去修复器</button>';
  html += '<button class="ticket-btn secondary" data-action="open-report" data-id="' + ticket.id + '">回到报告</button>';
  html += '<button class="ticket-btn secondary" data-action="copy-summary" data-id="' + ticket.id + '">复制摘要</button>';
  html += '<button class="ticket-btn secondary" data-action="edit-notes" data-id="' + ticket.id + '">备注</button>';
  html += '<button class="ticket-btn danger" data-action="delete" data-id="' + ticket.id + '">删除</button>';
  html += '</div>';
  panel.innerHTML = html;

  loadTicketTimeline(ticket.id);
  document.querySelectorAll('.ticket-row').forEach(function (r) {
    r.classList.toggle('selected', parseInt(r.dataset.id) === id);
  });
}

export function updateTicketSelection() {
  let checked = document.querySelectorAll('.ticket-checkbox:checked');
  let countEl = document.getElementById('ticket-selected-count');
  if (countEl) countEl.textContent = '已选 ' + checked.length + ' 项';
}

export function toggleSelectAllTickets(source) {
  let checked = source ? source.checked : false;
  document.querySelectorAll('.ticket-checkbox').forEach(function (b) { b.checked = checked; });
  document.querySelectorAll('[data-action="toggle-select-all"]').forEach(function (cb) { cb.checked = checked; });
  updateTicketSelection();
}

export function getSelectedTicketIds() {
  let ids = [];
  document.querySelectorAll('.ticket-checkbox:checked').forEach(function (b) { ids.push(parseInt(b.value, 10)); });
  return ids;
}

export function batchUpdateTickets(status) {
  let ids = getSelectedTicketIds();
  if (ids.length === 0) { showToast('请先选择工单', 'error'); return; }
  ticketService.batchUpdate(ids, status).then(function () {
    showToast('已批量更新 ' + ids.length + ' 个工单', 'success');
    return loadTickets();
  }).catch(function (e) {
    showToast('批量更新失败: ' + e.message, 'error');
  });
}

export function batchDeleteTickets() {
  let ids = getSelectedTicketIds();
  if (ids.length === 0) { showToast('请先选择工单', 'error'); return; }
  if (!confirm('确定删除选中的 ' + ids.length + ' 个工单？')) return;
  ticketService.batchDelete(ids).then(function () {
    showToast('已批量删除 ' + ids.length + ' 个工单', 'success');
    return loadTickets();
  }).catch(function (e) {
    showToast('批量删除失败: ' + e.message, 'error');
  });
}

export function updateTicketStatus(id, status) {
  ticketService.updateTicketStatus(id, status).then(function () {
    showToast('状态已更新', 'success');
    return loadTickets().then(function () { showTicketDetail(id); });
  }).catch(function (e) {
    showToast('更新失败: ' + e.message, 'error');
  });
}

export function deleteTicket(id) {
  if (!confirm('确定删除该工单？')) return;
  ticketService.deleteTicket(id).then(function () {
    showToast('工单已删除', 'success');
    let panel = document.getElementById('ticket-detail-panel');
    if (panel) panel.innerHTML = '<div class="ticket-detail-empty">选择左侧工单查看详情</div>';
    return loadTickets();
  }).catch(function (e) {
    showToast('删除失败: ' + e.message, 'error');
  });
}

export function editTicketNotes(id) {
  let ticket = ticketService.getTicketById(id);
  let note = prompt('编辑备注:', ticket && ticket.notes ? ticket.notes : '');
  if (note === null) return;
  ticketService.updateTicketNotes(id, note).then(function () {
    showToast('备注已保存', 'success');
    return loadTickets().then(function () { showTicketDetail(id); });
  }).catch(function (e) {
    showToast('保存失败: ' + e.message, 'error');
  });
}

export function openTicketFixer(id) {
  let ticket = ticketService.getTicketById(id);
  if (!ticket) return;
  try {
    if (ticket.url && window.localStorage) {
      localStorage.setItem('vs_fixer_ticket', JSON.stringify({
        ticket_id: ticket.id,
        scan_id: ticket.scan_id || null,
        url: ticket.url,
        finding_name: ticket.finding_name || '',
        finding_type: ticket.finding_type || '',
        severity: ticket.severity || 'low'
      }));
    }
  } catch (e) {}
  if (typeof window.navigateTo === 'function') {
    window.navigateTo('fixer');
  } else {
    window.location.hash = '#page-fixer';
  }
}

export function openTicketReport(id) {
  let ticket = ticketService.getTicketById(id);
  if (!ticket) return;
  if (typeof window.navigateTo === 'function') {
    window.navigateTo('home');
  } else {
    window.location.hash = '#page-home';
  }
}

export function copyTicketSummary(id) {
  let ticket = ticketService.getTicketById(id);
  if (!ticket) return;
  let summary = [
    '工单 #' + ticket.id,
    '名称: ' + (ticket.finding_name || ''),
    '等级: ' + (TicketHelpers.severityLabel(ticket.severity) || ticket.severity || ''),
    '状态: ' + (TicketHelpers.statusLabel(ticket.status) || ticket.status || ''),
    '来源 URL: ' + (ticket.url || ''),
    '备注: ' + (ticket.notes || '')
  ].join('\n');
  copyToClipboard(summary).then(function () {
    showToast('工单摘要已复制');
  });
}

export function loadTicketTimeline(id) {
  let container = document.getElementById('ticket-timeline-' + id);
  if (!container) return;
  apiGet('/api/fix-tickets/' + id + '/timeline').then(function (data) {
    if (!data || !data.timeline) {
      container.innerHTML = '<div class="ticket-timeline-empty">暂无时间线数据</div>';
      return;
    }
    let html = '<div class="ticket-timeline-steps">';
    data.timeline.forEach(function (step, idx) {
      let cls = 'step-' + step.status;
      let icon = { done: '✓', doing: '●', pending: '○', failed: '✗', rolled_back: '↩' }[step.status] || '○';
      html += '<div class="ticket-timeline-step ' + cls + '">';
      html += '<div class="ticket-timeline-icon">' + icon + '</div>';
      html += '<div class="ticket-timeline-content">';
      html += '<div class="ticket-timeline-label">' + escapeHtml(step.label) + '</div>';
      if (step.time) {
        html += '<div class="ticket-timeline-time">' + escapeHtml(step.time) + '</div>';
      }
      html += '</div></div>';
      if (idx < data.timeline.length - 1) {
        html += '<div class="ticket-timeline-line"></div>';
      }
    });
    html += '</div>';
    container.innerHTML = html;
  }).catch(function () {
    container.innerHTML = '<div class="ticket-timeline-empty">加载失败</div>';
  });
}

export function verifyTicket(id) {
  if (!confirm('确定对工单 #' + id + ' 复测验证？系统会重新扫描并对比修复效果。')) return;
  let btn = document.querySelector('.ticket-detail-actions [data-action="verify"][data-id="' + id + '"]');
  if (btn) {
    btn.textContent = '验证中...';
    btn.disabled = true;
  }
  ticketService.verifyTicket(id).then(function (data) {
    if (isPaymentRequired(data)) {
      showToast(paymentRequiredMessage(data), 'error');
      updateUserCredits();
      return;
    }
    if (data && data.success) {
      let msg = data.status === 'fixed' ? '复测通过：漏洞已修复！' : '复测完成：漏洞仍存在';
      showToast(msg, data.status === 'fixed' ? 'success' : 'warning');
      updateUserCredits();
      if (data.status === 'fixed') {
        setTimeout(function () {
          openTicketFixer(id);
        }, 300);
      }
      return loadTickets().then(function () { showTicketDetail(id); });
    } else {
      showToast('验证失败：' + (data && data.error ? data.error : '未知错误'), 'error');
    }
  }).catch(function (e) {
    showToast('验证请求失败', 'error');
  }).finally(function () {
    if (btn) {
      btn.textContent = '复测验证';
      btn.disabled = false;
    }
  });
}
