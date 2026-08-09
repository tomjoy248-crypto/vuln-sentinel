#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::net::TcpStream;
use std::os::windows::process::CommandExt;
use std::process::Command;
use std::thread;
use std::time::Duration;

use tauri::menu::{AboutMetadataBuilder, MenuBuilder};
use tauri::path::BaseDirectory;
use tauri::Manager;

const LOCAL_WEB_URL: &str = "http://127.0.0.1:8000/";
const LOCAL_BACKEND_ADDR: &str = "127.0.0.1:8000";

const STARTUP_HTML: &str = r#"<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Vuln Sentinel</title>
  <style>
    html, body { width: 100%; height: 100%; margin: 0; }
    body {
      display: flex; align-items: center; justify-content: center;
      background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
      color: #e5e7eb;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif;
    }
    .panel {
      width: min(520px, calc(100vw - 48px));
      padding: 28px 30px;
      border-radius: 16px;
      background: rgba(15, 23, 42, 0.78);
      border: 1px solid rgba(148, 163, 184, 0.18);
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.38);
    }
    .title { font-size: 22px; font-weight: 700; margin: 0 0 10px; }
    .desc { margin: 0; font-size: 14px; line-height: 1.7; color: #cbd5e1; }
    .bar {
      margin-top: 18px; height: 10px; border-radius: 999px; overflow: hidden;
      background: rgba(148, 163, 184, 0.14);
    }
    .bar > span {
      display: block; width: 40%; height: 100%; border-radius: inherit;
      background: linear-gradient(90deg, #38bdf8, #22c55e);
      animation: slide 1.2s ease-in-out infinite;
    }
    @keyframes slide { 0% { transform: translateX(-120%); } 100% { transform: translateX(260%); } }
  </style>
</head>
<body>
  <div class="panel">
    <div class="title">Vuln Sentinel 正在启动</div>
    <p class="desc">正在检查本地服务并加载主界面，请稍候。</p>
    <div class="bar"><span></span></div>
  </div>
</body>
</html>"#;

fn try_start_local_backend(app: &tauri::AppHandle) {
  let backend_path = match app.path().resolve("vuln-sentinel-backend.exe", BaseDirectory::Resource) {
    Ok(path) => path,
    Err(_) => return,
  };

  if !backend_path.exists() {
    return;
  }

  let _ = Command::new(backend_path)
    .creation_flags(0x08000000)
    .spawn();
}

fn wait_for_backend_ready(timeout_seconds: u64) -> bool {
  let mut elapsed = 0;
  while elapsed < timeout_seconds * 10 {
    if TcpStream::connect(LOCAL_BACKEND_ADDR).is_ok() {
      return true;
    }
    thread::sleep(Duration::from_millis(100));
    elapsed += 1;
  }
  false
}

fn show_bootstrap_message(window: &tauri::WebviewWindow, message: &str) {
  let escaped = message
    .replace('\\', "\\\\")
    .replace('`', "\\`");
  let script = format!(
    "document.body.innerHTML = `<div style=\"padding:24px;font-size:18px;line-height:1.8;display:flex;align-items:center;justify-content:center;height:100vh;background:#0f172a;color:#e5e7eb;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Microsoft YaHei',sans-serif;\"><div style=\"max-width:560px\">{}</div></div>`;",
    escaped
  );
  let _ = window.eval(&script);
}

fn show_startup_page(window: &tauri::WebviewWindow) {
  let escaped = STARTUP_HTML
    .replace('\\', "\\\\")
    .replace('`', "\\`");
  let script = format!(
    "document.open();document.write(`{}`);document.close();",
    escaped
  );
  let _ = window.eval(&script);
}

fn main() {
  tauri::Builder::default()
    .menu(|app_handle| {
      MenuBuilder::new(app_handle)
        .about(Some(
          AboutMetadataBuilder::new()
            .name(Some("Vuln Sentinel"))
            .version(Some(env!("CARGO_PKG_VERSION")))
            .comments(Some("安全扫描与交付平台"))
            .website(Some("https://github.com/tomjoy248-crypto/vuln-sentinel"))
            .build(),
        ))
        .separator()
        .close_window_with_text("关闭窗口")
        .quit_with_text("退出 Vuln Sentinel")
        .build()
    })
    .setup(|app| {
      try_start_local_backend(&app.handle().clone());
      if let Some(window) = app.get_webview_window("main") {
        let window_for_wait = window.clone();
        show_startup_page(&window);
        thread::spawn(move || {
          if !wait_for_backend_ready(20) {
            show_bootstrap_message(&window_for_wait, "本地服务启动失败，请重新打开安装包或检查防火墙。");
            return;
          }
          let script = format!("window.location.replace({:?});", LOCAL_WEB_URL);
          let _ = window_for_wait.eval(&script);
        });
      }
      Ok(())
    })
    .on_menu_event(|app, event| {
      if event.id().as_ref() == "about" {
        if let Some(window) = app.get_webview_window("main") {
          let _ = window.set_focus();
        }
      }
    })
    .run(tauri::generate_context!())
    .expect("failed to run Vuln Sentinel desktop shell");
}
