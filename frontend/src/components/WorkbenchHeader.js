/** 工作台头部组件 */

export function WorkbenchHeader(title, subtitle) {
  return `
    <div class="workbench-header">
      <h1 class="workbench-title">${title}</h1>
      <span class="workbench-subtitle">${subtitle}</span>
    </div>
  `;
}

export function renderWorkbenchHeader(containerId, title, subtitle) {
  const container = document.getElementById(containerId);
  if (container) container.innerHTML = WorkbenchHeader(title, subtitle);
}
