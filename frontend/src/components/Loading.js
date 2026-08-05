/** Loading 组件 */

export function setLoading(selectorOrElement, loading) {
  const el = typeof selectorOrElement === 'string'
    ? document.querySelector(selectorOrElement)
    : selectorOrElement;
  if (!el) return;
  if (loading) {
    el.dataset.loading = 'true';
    el.classList.add('loading');
  } else {
    el.dataset.loading = 'false';
    el.classList.remove('loading');
  }
}

export function showGlobalLoading(text = '加载中...') {
  let el = document.getElementById('global-loading');
  if (!el) {
    el = document.createElement('div');
    el.id = 'global-loading';
    el.className = 'global-loading';
    el.innerHTML = '<div class="spinner"></div><div class="loading-text"></div>';
    document.body.appendChild(el);
  }
  el.querySelector('.loading-text').textContent = text;
  el.style.display = 'flex';
}

export function hideGlobalLoading() {
  const el = document.getElementById('global-loading');
  if (el) el.style.display = 'none';
}
