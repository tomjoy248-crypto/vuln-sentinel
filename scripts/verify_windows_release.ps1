param(
  [string]$ManifestPath = (Join-Path (Join-Path (Split-Path -Parent $PSScriptRoot) 'artifacts\windows') 'release-manifest.json')
)

$ErrorActionPreference = 'Stop'

if (!(Test-Path $ManifestPath)) {
  throw "Manifest not found: $ManifestPath"
}

$manifest = Get-Content $ManifestPath -Raw | ConvertFrom-Json
$installerPath = Join-Path (Split-Path -Parent $ManifestPath) $manifest.installer

if (!(Test-Path $installerPath)) {
  throw "Installer not found: $installerPath"
}

$hash = Get-FileHash $installerPath -Algorithm SHA256
$ok = $hash.Hash -eq $manifest.sha256

[pscustomobject]@{
  product = $manifest.product
  version = $manifest.version
  installer = $manifest.installer
  expected_sha256 = $manifest.sha256
  actual_sha256 = $hash.Hash
  verified = $ok
  source = $manifest.source
} | Format-List

if (-not $ok) {
  throw 'SHA256 mismatch.'
}
