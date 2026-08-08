#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::net::TcpStream;
use std::process::Command;
use std::thread;
use std::time::Duration;
use tauri::menu::{AboutMetadataBuilder, MenuBuilder};
use tauri::Manager;
use tauri::path::BaseDirectory;

const LOCAL_WEB_URL: &str = "http://127.0.0.1:8000/";
const LOCAL_BACKEND_ADDR: &str = "127.0.0.1:8000";

fn try_start_local_backend(app: &tauri::AppHandle) {
  let backend_path = match app.path().resolve("vuln-sentinel-backend.exe", BaseDirectory::Resource) {
    Ok(path) => path,
    Err(_) => return,
  };

  if !backend_path.exists() {
    return;
  }

  let _ = Command::new(backend_path).spawn();
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
        let window = window.clone();
        let _ = window.eval(r#"document.body.innerHTML='<div style="padding:24px;font-size:18px;font-family:sans-serif">Vuln Sentinel 正在启动本地服务，请稍候...</div>';"#);
        thread::spawn(move || {
          if !wait_for_backend_ready(20) {
            let _ = window.eval(r#"document.body.innerHTML='<div style="padding:24px;font-size:18px;font-family:sans-serif">本地服务启动失败，请重新打开安装包或检查防火墙。</div>';"#);
            return;
          }
          let _ = window.eval(&format!("window.location.replace('{}');", LOCAL_WEB_URL));
        });
      }
      Ok(())
    })
    .on_menu_event(|app, event| {
      let id = event.id().as_ref();
      if id == "about" {
        if let Some(window) = app.get_webview_window("main") {
          let _ = window.set_focus();
        }
      }
    })
    .run(tauri::generate_context!())
    .expect("failed to run Vuln Sentinel desktop shell");
}
