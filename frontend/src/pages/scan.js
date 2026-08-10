/** 扫描页 / 扫描流程模块 * * 当前 的扫描入口内嵌在首页（page-home）的 scan-section 中， * 完整扫描逻辑（startScanDirect / startScan / startRealScan）位于 main.js。 * 本模块保留为扫描相关逻辑的挂载点，方便后续拆出独立扫描页时迁移。 */ export function init() {
  // 扫描输入框 Enter 快捷键已在 main.js 中绑定， // 授权 checkbox 联动、按钮状态等也在 main.js 初始化。 // 若未来添加独立 /scan 路由页面，可在此渲染页面级 UI。
} /** * 供独立扫描页使用的入口占位。 * @param {string} url */
export function startScanFromPage(url) {
  if (
    typeof window !== "undefined" &&
    typeof window.startScanDirect === "function"
  ) {
    const input = document.getElementById("scan-url");
    if (input) input.value = url || "";
    window.startScanDirect();
  }
}
