#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::menu::{AboutMetadataBuilder, MenuBuilder};
use tauri::Manager;

const FALLBACK_WEB_URL: &str = "https://vuln-sentinel-v11-s.onrender.com/";

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
      if let Some(window) = app.get_webview_window("main") {
        let _ = window.set_title("Vuln Sentinel - 安全扫描与交付平台");
        let _ = window.set_focus();
        let _ = window.eval(&format!("window.location.replace('{}')", FALLBACK_WEB_URL));
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
