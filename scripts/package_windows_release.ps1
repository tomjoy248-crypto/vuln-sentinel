$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$bundleDir = Join-Path $repoRoot 'src-tauri\target\release\bundle\nsis'
$outDir = Join-Path $repoRoot 'artifacts\windows'

if (!(Test-Path $bundleDir)) {
  throw "Bundle directory not found: $bundleDir"
}

$installer = Get-ChildItem $bundleDir -Filter '*_x64-setup.exe' | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $installer) {
  throw 'Windows installer not found.'
}

New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$targetName = 'Vuln-Sentinel-11.0.0-win64-setup.exe'
$targetPath = Join-Path $outDir $targetName
Copy-Item $installer.FullName $targetPath -Force
Write-Host "Output: $targetPath"
