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

Invoke-Installer $installer
$app = Find-ProductExecutable
if (-not $app) { throw 'Installed product executable was not found in standard Windows install locations' }
$installRoot = $app.Directory.FullName

# Launch validation is intentionally time-bounded so a desktop UI cannot block CI.
$running = Start-Process -FilePath $app.FullName -PassThru
Start-Sleep -Seconds 5
if ($running.HasExited) { throw 'Installed desktop application exited during startup smoke test' }
Stop-Process -Id $running.Id -Force

# A second silent install exercises the upgrade path without changing user data.
Invoke-Installer $installer
if (-not (Find-ProductExecutable)) { throw 'Product executable disappeared after upgrade smoke test' }

$uninstaller = Join-Path $installRoot 'uninstall.exe'
if (-not (Test-Path -LiteralPath $uninstaller)) { throw "Uninstaller was not found under $installRoot" }
$uninstall = Start-Process -FilePath $uninstaller -ArgumentList '/S' -Wait -PassThru
if ($uninstall.ExitCode -ne 0) { throw "NSIS uninstaller exited with code $($uninstall.ExitCode)" }
if (Test-Path -LiteralPath $installRoot) {
  $remainingProductFiles = Get-ChildItem -LiteralPath $installRoot -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -notmatch '^(uninstall|vuln-sentinel-backend)' }
  if ($remainingProductFiles) { throw 'Product files remain after uninstall smoke test' }
}

Write-Host 'Windows install, launch, upgrade, and uninstall smoke checks passed.'
