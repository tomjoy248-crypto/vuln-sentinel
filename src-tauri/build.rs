use std::fs;
use std::path::PathBuf;

fn main() {
  println!("cargo:rerun-if-changed=tauri.conf.json");
  println!("cargo:rerun-if-changed=capabilities.json");
  println!("cargo:rerun-if-changed=../runtime/backend-dist/vuln-sentinel-backend.exe");

  let manifest_dir = PathBuf::from(std::env::var("CARGO_MANIFEST_DIR").expect("CARGO_MANIFEST_DIR missing"));
  let source = manifest_dir.join("../runtime/backend-dist/vuln-sentinel-backend.exe");
  let target = manifest_dir.join("target/release/resources/backend-dist/vuln-sentinel-backend.exe");
  if let Some(parent) = target.parent() {
    let _ = fs::create_dir_all(parent);
  }
  if source.exists() {
    let _ = fs::copy(&source, &target);
  }

  tauri_build::build();
}
