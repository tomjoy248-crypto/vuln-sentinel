#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::net::{TcpListener, TcpStream};
use std::os::windows::process::CommandExt;
use std::process::Command;
use std::thread;
use std::time::Duration;

use tauri::path::BaseDirectory;
use tauri::Manager;

fn pick_free_port() -> Option<u16> {
  TcpListener::bind(("127.0.0.1", 0))
    .ok()
    .and_then(|listener| listener.local_addr().ok().map(|addr| addr.port()))
}

fn try_start_local_backend(app: &tauri::AppHandle, port: u16) {
  let backend_path = match app.path().resolve("vuln-sentinel-backend.exe", BaseDirectory::Resource) {
    Ok(path) => path,
    Err(_) => return,
  };

  if !backend_path.exists() {
    return;
  }

  let mut command = Command::new(&backend_path);
  if let Some(parent) = backend_path.parent() {
    command.current_dir(parent);
  }
  let _ = command
    .env("PORT", port.to_string())
    .creation_flags(0x08000000)
    .spawn();
}

fn wait_for_backend_ready(addr: &str, timeout_seconds: u64) -> bool {
  let mut elapsed = 0;
  while elapsed < timeout_seconds * 10 {
    if TcpStream::connect(addr).is_ok() {
      return true;
    }
    thread::sleep(Duration::from_millis(100));
    elapsed += 1;
  }
  false
}

fn escape_js_text(text: &str) -> String {
  text
    .replace('\\', "\\\\")
    .replace('`', "\\`")
    .replace('$', "\\$")
}

fn show_loading(window: &tauri::WebviewWindow, message: &str) {
  let html = format!(
    r#"<div style=\"width:100vw;height:100vh;display:flex;align-items:center;justify-content:center;background:linear-gradient(180deg,#0f172a 0%,#111827 100%);color:#e5e7eb;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Microsoft YaHei',sans-serif;\">
      <div style=\"max-width:560px;padding:28px 30px;border-radius:16px;background:rgba(15,23,42,.78);border:1px solid rgba(148,163,184,.18);box-shadow:0 20px 60px rgba(0,0,0,.38);\">
        <div style=\"font-size:22px;font-weight:700;margin-bottom:10px;\">Vuln Sentinel 正在启动</div>
        <div style=\"font-size:14px;line-height:1.8;color:#cbd5e1;\">{}</div>
        <div style=\"margin-top:18px;height:10px;border-radius:999px;overflow:hidden;background:rgba(148,163,184,.14);\">
          <div style=\"width:40%;height:100%;border-radius:inherit;background:linear-gradient(90deg,#38bdf8,#22c55e);animation:slide 1.2s ease-in-out infinite;\"></div>
        </div>
      </div>
      <style>@keyframes slide {{ 0% {{ transform: translateX(-120%); }} 100% {{ transform: translateX(260%); }} }}</style>
    </div>"#,
    escape_js_text(message)
  );
  let script = format!("document.body.innerHTML = `{}`; document.body.style.margin='0';", html);
  let _ = window.eval(&script);
}

fn main() {
  tauri::Builder::default()
    .setup(|app| {
      let port = pick_free_port().unwrap_or(8000);
      let local_web_url = format!("http://127.0.0.1:{port}/");
      let local_backend_addr = format!("127.0.0.1:{port}");
      try_start_local_backend(&app.handle().clone(), port);
      if let Some(window) = app.get_webview_window("main") {
        show_loading(&window, "正在检查本地服务并加载主界面，请稍候。");
        if wait_for_backend_ready(&local_backend_addr, 20) {
          let script = format!("window.location.replace({:?});", local_web_url);
          let _ = window.eval(&script);
        } else {
          show_loading(&window, "本地服务启动失败，请重新打开安装包或检查防火墙。");
        }
      }
      Ok(())
    })
    .run(tauri::generate_context!())
    .expect("failed to run Vuln Sentinel desktop shell");
}
