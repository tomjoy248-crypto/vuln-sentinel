param(
  [Parameter(Mandatory = $true)]
  [string]$InstallerPath
)

$ErrorActionPreference = 'Stop'
$installer = (Resolve-Path -LiteralPath $InstallerPath).Path
$candidateRoots = @(
  (Join-Path $env:LOCALAPPDATA 'Programs'),
  (Join-Path $env:LOCALAPPDATA 'Vuln Sentinel'),
  (Join-Path $env:ProgramFiles 'Vuln Sentinel')
)

foreach ($root in $candidateRoots) {
  if (Test-Path -LiteralPath $root -PathType Leaf) { continue }
  if (Test-Path -LiteralPath $root) {
    Get-ChildItem -LiteralPath $root -Directory -ErrorAction SilentlyContinue |
      Where-Object { $_.Name -match 'vuln.?sentinel' } |
      Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
  }
}

function Invoke-Installer([string]$path) {
  $process = Start-Process -FilePath $path -ArgumentList '/S' -Wait -PassThru
  if ($process.ExitCode -ne 0) {
    throw "NSIS installer exited with code $($process.ExitCode)"
  }
}

function Find-ProductExecutable() {
  $roots = $candidateRoots | Where-Object { Test-Path -LiteralPath $_ }
  Get-ChildItem -LiteralPath $roots -Recurse -File -Filter '*.exe' -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -notmatch '^(uninstall|vuln-sentinel-backend)' } |
    Select-Object -First 1
}

function Stop-ProductBackend() {
  Get-Process -Name 'vuln-sentinel-backend' -ErrorAction SilentlyContinue |
    Stop-Process -Force -ErrorAction SilentlyContinue
  Start-Sleep -Milliseconds 500
}

Invoke-Installer $installer
$app = Find-ProductExecutable
if (-not $app) { throw 'Installed product executable was not found in standard Windows install locations' }
$installRoot = $app.Directory.FullName
$backend = Get-ChildItem -LiteralPath $installRoot -Recurse -File -Filter 'vuln-sentinel-backend.exe' -ErrorAction SilentlyContinue |
  Select-Object -First 1
if (-not $backend) { throw 'Bundled backend executable was not found after installation' }

# Launch validation is intentionally time-bounded so a desktop UI cannot block CI.
$running = Start-Process -FilePath $app.FullName -PassThru
Start-Sleep -Seconds 5
if ($running.HasExited) { throw 'Installed desktop application exited during startup smoke test' }

$backendReady = $false
for ($attempt = 0; $attempt -lt 20; $attempt++) {
  try {
    $health = Invoke-RestMethod -Uri 'http://127.0.0.1:8011/health/live' -TimeoutSec 2
    if ($health) { $backendReady = $true; break }
  } catch {
    Start-Sleep -Milliseconds 500
  }
}
if (-not $backendReady) { throw 'Bundled backend did not become reachable on 127.0.0.1:8011' }

$testUsername = "ci_install_$([Guid]::NewGuid().ToString('N').Substring(0, 10))"
$testPassword = "VsTest-$([Guid]::NewGuid().ToString('N').Substring(0, 12))!"
$registerBody = @{
  username = $testUsername
  password = $testPassword
  email = "$testUsername@example.invalid"
} | ConvertTo-Json
$registered = Invoke-RestMethod -Uri 'http://127.0.0.1:8011/api/register' -Method Post -ContentType 'application/json' -Body $registerBody -TimeoutSec 10
if (-not $registered.success -or -not $registered.token) { throw 'Bundled backend registration smoke test failed' }

$loginBody = @{ username = $testUsername; password = $testPassword } | ConvertTo-Json
$loggedIn = Invoke-RestMethod -Uri 'http://127.0.0.1:8011/api/login' -Method Post -ContentType 'application/json' -Body $loginBody -TimeoutSec 10
if (-not $loggedIn.success -or -not $loggedIn.token) { throw 'Bundled backend login smoke test failed' }
Stop-Process -Id $running.Id -Force
Stop-ProductBackend

# A second silent install exercises the upgrade path without changing user data.
Invoke-Installer $installer
if (-not (Find-ProductExecutable)) { throw 'Product executable disappeared after upgrade smoke test' }

$runningAfterUpgrade = Start-Process -FilePath $app.FullName -PassThru
$loginAfterUpgrade = $null
for ($attempt = 0; $attempt -lt 30; $attempt++) {
  try {
    $loginAfterUpgrade = Invoke-RestMethod -Uri 'http://127.0.0.1:8011/api/login' -Method Post -ContentType 'application/json' -Body $loginBody -TimeoutSec 2
    if ($loginAfterUpgrade.success -and $loginAfterUpgrade.token) { break }
  } catch {
    Start-Sleep -Milliseconds 500
  }
}
if (-not $loginAfterUpgrade -or -not $loginAfterUpgrade.success -or -not $loginAfterUpgrade.token) {
  throw 'Account data or login capability was not preserved after upgrade'
}
if (-not $runningAfterUpgrade.HasExited) { Stop-Process -Id $runningAfterUpgrade.Id -Force }
Stop-ProductBackend

# The desktop shell may still hold files open after the backend exits.  Close it
# before invoking NSIS so the uninstall check measures installer cleanup rather
# than Windows file-lock timing.
Get-Process -Name 'vuln-sentinel-desktop' -ErrorAction SilentlyContinue |
  Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 750

$uninstaller = Join-Path $installRoot 'uninstall.exe'
if (-not (Test-Path -LiteralPath $uninstaller)) { throw "Uninstaller was not found under $installRoot" }
$uninstall = Start-Process -FilePath $uninstaller -ArgumentList '/S' -Wait -PassThru
if ($uninstall.ExitCode -ne 0) { throw "NSIS uninstaller exited with code $($uninstall.ExitCode)" }
if (Test-Path -LiteralPath $installRoot) {
  $remainingProductFiles = Get-ChildItem -LiteralPath $installRoot -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -notmatch '^(uninstall|vuln-sentinel-backend)' }
  if ($remainingProductFiles) {
    # Retry once after a short delay to avoid transient Windows AV/indexer locks.
    Start-Sleep -Seconds 2
    $remainingProductFiles = Get-ChildItem -LiteralPath $installRoot -Recurse -File -ErrorAction SilentlyContinue |
      Where-Object { $_.Name -notmatch '^(uninstall|vuln-sentinel-backend)' }
  }
  if ($remainingProductFiles) { throw 'Product files remain after uninstall smoke test' }
}

Write-Host 'Windows install, launch, upgrade, and uninstall smoke checks passed.'
