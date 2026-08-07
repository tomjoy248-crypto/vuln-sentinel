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

$versionMatch = [regex]::Match($installer.Name, '_([0-9]+(?:\.[0-9]+)+)_x64-setup\.exe$')
$version = if ($versionMatch.Success) { $versionMatch.Groups[1].Value } else { 'unknown' }
$targetName = "Vuln-Sentinel-$version-win64-setup.exe"
$targetPath = Join-Path $outDir $targetName
Copy-Item $installer.FullName $targetPath -Force

$hash = Get-FileHash $targetPath -Algorithm SHA256
$manifest = [ordered]@{
  product = 'Vuln Sentinel'
  version = $version
  generated_at = (Get-Date).ToString('o')
  installer = $targetName
  sha256 = $hash.Hash
  source = $installer.FullName
}
$manifestPath = Join-Path $outDir 'release-manifest.json'
$manifest | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 $manifestPath

Write-Host "Output: $targetPath"
Write-Host "Manifest: $manifestPath"
Write-Host "SHA256: $($hash.Hash)"
