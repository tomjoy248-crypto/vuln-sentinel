/** Toast 通知组件 */

let _toastQueue = [];
let _toastActive = 0;
const _TOAST_MAX = 3;
const _TOAST_DURATION = 2500;

export function showToast(msg, type) {
  _toastQueue.push({ msg: msg, type: type });
  _processToastQueue();
}

function _processToastQueue() {
  if (_toastActive >= _TOAST_MAX || _toastQueue.length === 0) return;
  let item = _toastQueue.shift();
  _toastActive++;

  let container = document.getElementById('toast-container');
  if (!container) { _toastActive--; return; }
  let t = document.createElement('div');
  t.className = 'toast';

  let icon = 'ℹ️';
  if (item.type === 'error') icon = '[错误]';
  else if (item.type === 'success') icon = '[成功]';
  else if (item.type === 'warn') icon = '[警告]';
  let iconSpan = document.createElement('span');
  iconSpan.textContent = icon + ' ';
  iconSpan.style.marginRight = '6px';
  t.appendChild(iconSpan);
  t.appendChild(document.createTextNode(item.msg));

  if (item.type === 'error') t.classList.add('error');
  else if (item.type === 'success') t.classList.add('success');

  container.appendChild(t);

  requestAnimationFrame(function() {
    requestAnimationFrame(function() {
      t.classList.add('show');
    });
  });

  setTimeout(function() {
    t.classList.add('hiding');
    t.classList.remove('show');
    setTimeout(function() {
      if (t.parentNode) t.parentNode.removeChild(t);
      _toastActive--;
      _processToastQueue();
    }, 300);
  }, _TOAST_DURATION);
}
