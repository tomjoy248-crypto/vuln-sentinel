/** Toast 通知组件 */

let _toastQueue = [];
let _toastActive = 0;
const _TOAST_MAX = 3;
const _TOAST_DURATION = 2500;

export function showToast(msg, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) {
    console.log('[' + type + ']', msg);
    return;
  }
  _toastQueue.push({ msg, type });
  _processToastQueue(container);
}

function _processToastQueue(container) {
  if (_toastActive >= _TOAST_MAX || _toastQueue.length === 0) return;
  const item = _toastQueue.shift();
  _toastActive++;

  const el = document.createElement('div');
  el.className = 'toast ' + item.type;
  el.innerHTML = '<span>' + _escapeHtml(item.msg) + '</span>';
  container.appendChild(el);

  requestAnimationFrame(function() {
    el.style.opacity = '1';
    el.style.transform = 'translateX(0)';
  });

  setTimeout(function() {
    el.style.opacity = '0';
    el.style.transform = 'translateX(20px)';
    setTimeout(function() {
      if (el.parentNode) el.parentNode.removeChild(el);
      _toastActive--;
      _processToastQueue(container);
    }, 250);
  }, _TOAST_DURATION);
}

function _escapeHtml(str) {
  if (str == null) return '';
  const div = document.createElement('div');
  div.appendChild(document.createTextNode(String(str)));
  return div.innerHTML;
}
