/** 通用 Modal 组件 */

export function openModal(title, content, options = {}) {
  let modal = document.getElementById('global-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'global-modal';
    modal.className = 'modal';
    modal.innerHTML = `
      <div class="modal-backdrop"></div>
      <div class="modal-dialog">
        <div class="modal-header">
          <h3 class="modal-title"></h3>
          <button class="modal-close" aria-label="关闭">&times;</button>
        </div>
        <div class="modal-body"></div>
      </div>
    `;
    document.body.appendChild(modal);
    modal.querySelector('.modal-close').addEventListener('click', () => closeModal());
    modal.querySelector('.modal-backdrop').addEventListener('click', () => closeModal());
  }
  modal.querySelector('.modal-title').textContent = title || '';
  modal.querySelector('.modal-body').innerHTML = content || '';
  modal.classList.add('show');
  modal.style.display = 'flex';
  if (options.onOpen) options.onOpen(modal);
  return modal;
}

export function closeModal() {
  const modal = document.getElementById('global-modal');
  if (!modal) return;
  modal.classList.remove('show');
  modal.style.display = 'none';
}
