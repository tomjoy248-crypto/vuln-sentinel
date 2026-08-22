#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::fs::OpenOptions;
use std::net::TcpStream;
use std::process::Stdio;
use std::os::windows::process::CommandExt;
use std::path::{Path, PathBuf};
use std::process::Command;
use std::thread;
use std::time::Duration;

use tauri::path::BaseDirectory;
use tauri::Manager;

fn candidate_backend_paths(app: &tauri::AppHandle) -> Vec<PathBuf> {
  let mut candidates = vec![
    app.path().resolve("vuln-sentinel-backend.exe", BaseDirectory::Resource),
    app.path().resolve("backend-dist/vuln-sentinel-backend.exe", BaseDirectory::Resource),
    app.path().resolve("backend/vuln-sentinel-backend.exe", BaseDirectory::Resource),
  ];

  if let Ok(resource_dir) = app.path().resource_dir() {
    candidates.push(Ok(resource_dir.join("vuln-sentinel-backend.exe")));
    candidates.push(Ok(resource_dir.join("backend-dist").join("vuln-sentinel-backend.exe")));
    candidates.push(Ok(resource_dir.join("resources").join("backend-dist").join("vuln-sentinel-backend.exe")));
  }

  if let Ok(exe) = std::env::current_exe() {
    if let Some(dir) = exe.parent() {
      candidates.push(Ok(dir.join("vuln-sentinel-backend.exe")));
      candidates.push(Ok(dir.join("backend-dist").join("vuln-sentinel-backend.exe")));
    }
  }

  candidates
    .into_iter()
    .filter_map(Result::ok)
    .filter(|path| Path::new(path).exists())
    .collect()
}

fn walk_for_backend(dir: &Path, depth: usize, found: &mut Vec<PathBuf>) {
  if depth == 0 {
    return;
  }
  let entries = match std::fs::read_dir(dir) {
    Ok(entries) => entries,
    Err(_) => return,
  };
  for entry in entries.flatten() {
    let path = entry.path();
    if path.is_dir() {
      walk_for_backend(&path, depth - 1, found);
    } else if let Some(name) = path.file_name().and_then(|n| n.to_str()) {
      let lower = name.to_ascii_lowercase();
      if lower == "vuln-sentinel-backend.exe" || lower.starts_with("vuln-sentinel-backend") && lower.ends_with(".exe") {
        found.push(path);
      }
    }
  }
}

fn try_start_local_backend(app: &tauri::AppHandle, port: u16) -> Option<PathBuf> {
  let mut found = candidate_backend_paths(app);
  if found.is_empty() {
    if let Ok(exe) = std::env::current_exe() {
      if let Some(dir) = exe.parent() {
        walk_for_backend(dir, 4, &mut found);
      }
    }
  }
  let backend_path = found.into_iter().next()?;

  let log_path = std::env::temp_dir().join("vuln-sentinel-backend-startup.log");
  let log_file = OpenOptions::new().create(true).append(true).open(&log_path).ok();

  let mut command = Command::new(&backend_path);
  if let Some(parent) = backend_path.parent() {
    command.current_dir(parent);
  }
  if let Some(file) = log_file {
    if let Ok(stderr_file) = file.try_clone() {
      command.stdout(Stdio::from(file));
      command.stderr(Stdio::from(stderr_file));
    }
  }
  match command
    .env("PORT", port.to_string())
    .env("AUTH_CHALLENGE_DISABLED", "1")
    .env("ENV", "development")
    .creation_flags(0x08000000)
    .spawn()
  {
    Ok(_) => Some(backend_path),
    Err(_) => None,
  }
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
    r#"<div style="width:100vw;height:100vh;display:flex;align-items:center;justify-content:center;background:linear-gradient(180deg,#0f172a 0%,#111827 100%);color:#e5e7eb;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Microsoft YaHei',sans-serif;">
      <div style="max-width:560px;padding:28px 30px;border-radius:16px;background:rgba(15,23,42,.78);border:1px solid rgba(148,163,184,.18);box-shadow:0 20px 60px rgba(0,0,0,.38);">
        <div style="font-size:22px;font-weight:700;margin-bottom:10px;">Vuln Sentinel 正在启动</div>
        <div style="font-size:14px;line-height:1.8;color:#cbd5e1;">{}</div>
        <div style="margin-top:18px;height:10px;border-radius:999px;overflow:hidden;background:rgba(148,163,184,.14);">
          <div style="width:40%;height:100%;border-radius:inherit;background:linear-gradient(90deg,#38bdf8,#22c55e);animation:slide 1.2s ease-in-out infinite;"></div>
        </div>
      </div>
      <style>@keyframes slide {{ 0% {{ transform: translateX(-120%); }} 100% {{ transform: translateX(260%); }} }}</style>
    </div>"#,
    escape_js_text(message)
  );
  let script = format!("document.body.innerHTML = `{}`; document.body.style.margin='0';", html);
  let _ = window.eval(&script);
}

fn show_backend_fallback(window: &tauri::WebviewWindow, backend_hint: &str) {
  let banner_text = format!(
    "本地服务暂未启动，界面已打开。请检查防火墙或重新启动安装包。后端路径：{}",
    backend_hint
  );
  let escaped = escape_js_text(&banner_text);
  let script = format!(
    r#"(function() {{
      var boot = document.getElementById('boot-screen');
      if (boot && boot.parentNode) boot.parentNode.removeChild(boot);
      var banner = document.createElement('div');
      banner.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:99999;background:#7c2d12;color:#fff;padding:10px 16px;font-size:13px;line-height:1.5;font-family:system-ui,-apple-system,Segoe UI,Microsoft YaHei,sans-serif';
      banner.textContent = `{}`;
      document.body.appendChild(banner);
    }})();"#,
    escaped
  );
  let _ = window.eval(&script);
}

fn main() {
  tauri::Builder::default()
    .setup(|app| {
      let port = 8011;
      let address = format!("127.0.0.1:{}", port);
      let backend_path = if TcpStream::connect(&address).is_ok() {
        None
      } else {
        try_start_local_backend(&app.handle().clone(), port)
      };

      if let Some(window) = app.get_webview_window("main") {
        show_loading(&window, "正在启动本地安全扫描服务，请稍候。");
        thread::spawn(move || {
          if wait_for_backend_ready(&address, 30) {
            if let Ok(url) = url::Url::parse(&format!("http://127.0.0.1:{}/", port)) {
              let _ = window.navigate(url);
            }
          } else {
            let hint = backend_path
              .as_ref()
              .map(|path| path.display().to_string())
              .unwrap_or_else(|| "未找到后端可执行文件".to_string());
            show_backend_fallback(&window, &hint);
          }
        });
      }
      Ok(())
    })
    .run(tauri::generate_context!())
    .expect("failed to run Vuln Sentinel desktop shell");
}
