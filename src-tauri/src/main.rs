#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::Manager;

fn main() {
  tauri::Builder::default()
    .setup(|app| {
      if let Some(window) = app.get_webview_window("main") {
        let _ = window.set_title("Vuln Sentinel - 安全扫描与交付平台");
      }
      Ok(())
    })
    .run(tauri::generate_context!())
    .expect("failed to run Vuln Sentinel desktop shell");
}
