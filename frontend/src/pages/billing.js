/** 计费套餐 / 充值页面 (page-billing) */

import {
  billingPlans,
  createOrder,
  getOrderStatus,
  recharges,
  isLoggedIn
} from '../api.js';

import {
  escapeHtml,
  safeSetDisplay,
  formatDate,
  renderPagination,
  extractError
} from '../utils.js';

import { showToast } from '../components/Toast.js';

const navigateTo = (...args) => typeof window.navigateTo === 'function' && window.navigateTo(...args);
const updateUserCredits = () => typeof window.updateUserCredits === 'function' && window.updateUserCredits();

function formatPrice(cents) {
  if (cents === undefined || cents === null) return '--';
  return '¥' + (cents / 100).toFixed(2);
}

function formatCredits(num) {
  if (num === undefined || num === null) return '--';
  let n = parseInt(num, 10);
  if (isNaN(n)) return String(num);
  return n.toLocaleString('zh-CN');
}

function formatValueScore(plan) {
  let credits = parseInt(plan && plan.credits, 10);
  let price = parseInt(plan && plan.price_cents, 10);
  if (!credits || !price) return '--';
  return (price / credits / 100).toFixed(2);
}

function getRecommendedPlanId(plans) {
  if (!plans || !plans.length) return null;
  let best = null;
  let bestScore = Number.POSITIVE_INFINITY;
  plans.forEach(function(plan) {
    let credits = parseInt(plan.credits, 10);
    let price = parseInt(plan.price_cents, 10);
    if (!credits || !price) return;
    let score = price / credits;
    if (score < bestScore) {
      bestScore = score;
      best = plan.id;
    }
  });
  return best;
}

function getPlanBadge(plan, recommendedPlanId) {
  if (plan.id === recommendedPlanId) return '最划算';
  if ((plan.name || '').includes('企业')) return '企业版';
  if ((plan.name || '').includes('专业')) return '专业版';
  if ((plan.name || '').includes('标准')) return '标准版';
  if ((plan.name || '').includes('体验')) return '体验版';
  return '';
}

function getPlanTarget(plan) {
  const name = (plan.name || '').toLowerCase();
  if (name.includes('企业')) return '大型团队 / 采购';
  if (name.includes('专业')) return '安全运营 / 复测';
  if (name.includes('标准')) return '日常扫描 / 验证';
  if (name.includes('体验')) return '入门试用';
  return '个人 / 轻量使用';
}

function getPlanPermission(plan) {
  const credits = parseInt(plan && plan.credits, 10) || 0;
  if (credits >= 1000) return '企业采购';
  if (credits >= 500) return '专业运营';
  if (credits >= 100) return '标准使用';
  return '入门试用';
}

function getProviderLabel(provider) {
  const map = { mock: '模拟支付', stripe: 'Stripe', alipay: '支付宝', wechat: '微信支付' };
  return map[provider] || provider;
}

function getStatusLabel(status) {
  const map = { pending: '待支付', paid: '已到账', failed: '失败', cancelled: '已取消' };
  return map[status] || status;
}

export function loadBillingPage() {
  if (!isLoggedIn()) {
    showToast('请先登录后再查看计费套餐', 'warn');
    navigateTo('profile');
    return;
  }
  loadPlans();
  loadRechargeRecords();
  checkPaymentReturn();
}

function loadPlans() {
  let container = document.getElementById('billing-plans-list');
  if (!container) return;
  container.innerHTML = '<div style="text-align:center;padding:20px;color:var(--text-secondary)">正在加载套餐...</div>';

  billingPlans().then(function(data) {
    let plans = (data && data.data && data.data.plans) || (data && data.plans) || [];
    if (!plans.length) {
      container.innerHTML = '<div style="text-align:center;padding:20px;color:var(--text-secondary)">暂无可用套餐</div>';
      return;
    }
    let recommendedPlanId = getRecommendedPlanId(plans);
    let html = '<div style="display:flex;flex-direction:column;gap:12px">';
    html += '<div style="display:flex;flex-wrap:wrap;gap:10px;padding:12px 14px;background:var(--bg);border:1px solid var(--border);border-radius:2px;font-size:12px;color:var(--text-secondary)">';
    html += '<div>• 所有订单都会进入充值记录，便于财务对账与追踪</div>';
    html += '<div>• 充值后可立即用于扫描、复测、修复验证、报告导出和审计留痕</div>';
    html += '<div>• 支持模拟支付、Stripe，以及支付宝/微信测试回调与骨架通道</div>';
    html += '</div>';
    html += '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px">';
    plans.forEach(function(plan) {
      let isRecommended = plan.id === recommendedPlanId;
      let badge = getPlanBadge(plan, recommendedPlanId);
      let borderColor = isRecommended ? 'var(--warning)' : 'var(--border)';
      let shadow = isRecommended ? '0 0 0 1px rgba(240,167,50,0.35)' : 'none';
      html += '<div style="background:var(--bg);border:1px solid ' + borderColor + ';box-shadow:' + shadow + ';border-radius:2px;padding:14px;display:flex;flex-direction:column;gap:8px;position:relative">';
      if (badge) {
        html += '<div style="position:absolute;top:10px;right:10px;background:' + (isRecommended ? 'var(--warning)' : 'var(--primary)') + ';color:#fff;font-size:11px;font-weight:700;padding:3px 8px;border-radius:999px">' + escapeHtml(badge) + '</div>';
      }
      html += '<div style="font-size:15px;font-weight:700">' + escapeHtml(plan.name) + '</div>';
      html += '<div style="font-size:12px;color:var(--text-secondary);min-height:34px">' + escapeHtml(plan.description || '') + '</div>';
      html += '<div style="font-size:22px;font-weight:700;color:var(--warning)">' + formatPrice(plan.price_cents) + '</div>';
      html += '<div style="font-size:13px;color:var(--text-secondary)">含 <strong style="color:var(--text)">' + formatCredits(plan.credits) + '</strong> 积分</div>';
      html += '<div style="font-size:12px;color:var(--text-secondary)">约 <strong style="color:var(--text)">' + formatValueScore(plan) + ' 元/积分</strong></div>';
      html += '<div style="font-size:12px;color:var(--text-secondary)">适合：' + escapeHtml(getPlanTarget(plan)) + '</div>';
      html += '<div style="font-size:12px;color:var(--text-secondary)">可用于：扫描 / 复扫 / 报告 / 工单 / 审计</div>';
      html += '<div style="font-size:12px;color:var(--text-secondary)">权限：' + escapeHtml(getPlanPermission(plan)) + '</div>';
      html += '<button class="fixer-btn primary" style="width:100%;margin-top:auto" onclick="buyPlan(' + plan.id + ', event)">立即购买</button>';
      html += '</div>';
    });
    html += '</div>';
    html += '<div style="padding:12px 14px;background:var(--bg);border:1px solid var(--border);border-radius:2px;font-size:12px;color:var(--text-secondary);line-height:1.7">';
    html += '<div style="font-weight:700;color:var(--text);margin-bottom:4px">购买后流程</div>';
    html += '<div>1. 选择套餐并完成支付 → 2. 积分立即到账 → 3. 直接进入扫描或复扫 → 4. 结果会进入报告、工单和审计 → 5. 可按项目或团队需求继续升级。</div>';
    html += '</div>';
    html += '<div style="margin-top:12px;padding:12px 14px;background:rgba(75,110,175,0.08);border:1px solid rgba(75,110,175,0.2);border-radius:2px;font-size:12px;color:var(--text-secondary);line-height:1.7">';
    html += '<div style="font-weight:700;color:var(--primary);margin-bottom:4px">交付前确认</div>';
    html += '<div>建议上线前重点确认：支付回调签名、积分扣减日志、权限分层、导出权限、审计日志留存，以及客户能否看懂套餐价值与结果证据。</div>';
    html += '</div>';
    container.innerHTML = html;
  }).catch(function(e) {
    container.innerHTML = '<div style="text-align:center;padding:20px;color:var(--danger)">加载套餐失败</div>';
  });
}

function buyPlan(planId, ev) {
  if (ev) ev.stopPropagation();
  if (!isLoggedIn()) { showToast('请先登录', 'warn'); navigateTo('profile'); return; }

  let provider = 'mock';
  let stripeKey = '';
  // 若后端配置了 Stripe 公钥，优先使用真实支付
  if (window.__STRIPE_PUBLISHABLE_KEY__) {
    provider = 'stripe';
    stripeKey = window.__STRIPE_PUBLISHABLE_KEY__;
  }

  let base = (window.__PUBLIC_BASE_URL__ || window.location.origin).replace(/\/$/, '');
  createOrder({
    plan_id: planId,
    provider: provider,
    success_url: base + '/billing?status=success',
    cancel_url: base + '/billing?status=cancel'
  }).then(function(data) {
    if (!data || !data.success) {
      showToast(extractError(data) || '创建订单失败', 'error');
      return;
    }
    if (data.data && data.data.checkout_url) {
      // Stripe 跳转
      window.location.href = data.data.checkout_url;
    } else if (data.data && data.data.transaction_id) {
      // mock / 直接到账
      showToast('支付成功，积分已到账', 'success');
      updateUserCredits();
      loadRechargeRecords();
    } else {
      showToast('订单状态异常', 'error');
    }
  }).catch(function(e) {
    showToast('购买失败：' + (e.message || '网络错误'), 'error');
  });
}

function loadRechargeRecords(page) {
  page = parseInt(page, 10) || 1;
  let limit = 10;
  let offset = (page - 1) * limit;
  let listEl = document.getElementById('billing-records-list');
  if (!listEl) return;
  listEl.innerHTML = '<div style="text-align:center;padding:20px;color:var(--text-secondary)">正在读取充值记录...</div>';

  recharges(limit, offset).then(function(data) {
    let records = (data && data.data && data.data.records) || (data && data.records) || [];
    let total = (data && data.data && data.data.total) || (data && data.total) || records.length;
    let meta = (data && data.meta) || {};
    let metaLimit = meta.limit || limit;
    let metaOffset = meta.offset || offset;
    let currentPage = Math.floor(metaOffset / metaLimit) + 1;
    let totalPages = Math.max(1, Math.ceil(total / metaLimit));

    renderRecords(records);
    renderPagination('billing-records-pagination', currentPage, totalPages, function(p) { loadRechargeRecords(p); });
    safeSetDisplay('billing-records-pagination', totalPages > 1 ? 'flex' : 'none');
  }).catch(function(e) {
    listEl.innerHTML = '<div style="text-align:center;padding:20px;color:var(--danger)">读取充值记录失败</div>';
  });
}

function renderRecords(records) {
  let listEl = document.getElementById('billing-records-list');
  if (!listEl) return;
  if (!records || !records.length) {
    listEl.innerHTML = '<div style="text-align:center;padding:24px;color:var(--text-secondary)">暂无充值记录</div>';
    return;
  }
  let html = '<div style="display:flex;flex-direction:column;gap:8px">';
  records.forEach(function(r) {
    let amountText = r.amount_cents ? formatPrice(r.amount_cents) : '免费';
    let statusColor = r.status === 'paid' ? 'var(--success)' : (r.status === 'pending' ? 'var(--warning)' : 'var(--danger)');
    html += '<div style="display:flex;align-items:center;justify-content:space-between;padding:10px;background:var(--bg);border:1px solid var(--border);border-radius:2px">';
    html += '<div>';
    html += '<div style="font-size:13px;font-weight:600">' + escapeHtml(r.plan_name || '充值') + '</div>';
    html += '<div style="font-size:11px;color:var(--text-secondary);margin-top:2px">' + formatDate(r.created_at) + ' · ' + getProviderLabel(r.payment_provider) + '</div>';
    html += '</div>';
    html += '<div style="text-align:right">';
    html += '<div style="font-size:13px;font-weight:700">' + amountText + '</div>';
    html += '<div style="font-size:11px;color:' + statusColor + ';margin-top:2px">' + getStatusLabel(r.status) + '</div>';
    html += '</div></div>';
  });
  html += '</div>';
  listEl.innerHTML = html;
}

function checkPaymentReturn() {
  let params = new URLSearchParams(window.location.search);
  let status = params.get('status');
  let tx = params.get('transaction_id');
  if (!status && !tx) return;

  if (status === 'cancel') {
    showToast('支付已取消', 'warn');
    cleanReturnParams();
    return;
  }

  if (tx) {
    showToast('正在确认支付结果...', 'success');
    pollOrderStatus(tx);
  } else if (status === 'success') {
    showToast('支付成功', 'success');
    updateUserCredits();
    loadRechargeRecords();
  }
  cleanReturnParams();
}

function cleanReturnParams() {
  try {
    let url = new URL(window.location.href);
    url.searchParams.delete('status');
    url.searchParams.delete('transaction_id');
    window.history.replaceState({}, '', url.toString());
  } catch (e) {}
}

function pollOrderStatus(transactionId) {
  let attempts = 0;
  let max = 10;
  let timer = setInterval(function() {
    attempts++;
    getOrderStatus(transactionId).then(function(data) {
      let order = (data && data.data) || data;
      if (order && order.status === 'paid') {
        clearInterval(timer);
        showToast('支付成功，积分已到账', 'success');
        updateUserCredits();
        loadRechargeRecords();
        return;
      }
      if (attempts >= max) {
        clearInterval(timer);
        showToast('支付结果确认超时，请稍后刷新查看', 'warn');
      }
    }).catch(function() {
      if (attempts >= max) clearInterval(timer);
    });
  }, 2000);
}

export function init() {
  if (typeof window !== 'undefined') {
    window.buyPlan = buyPlan;
    window.loadBillingPage = loadBillingPage;
  }
}

