#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::Manager;

fn main() {
  tauri::Builder::default()
    .setup(|app| {
      let _window = app
        .get_webview_window("main")
        .ok_or_else(|| tauri::Error::Setup("main window not found".into()))?;
      Ok(())
    })
    .run(tauri::generate_context!())
    .expect("failed to run Vuln Sentinel desktop shell");
}
