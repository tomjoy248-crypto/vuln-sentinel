param(
  [Parameter(Mandatory = $true)]
  [string]$InstallerPath
)

$ErrorActionPreference = 'Stop'
$installer = (Resolve-Path -LiteralPath $InstallerPath).Path
$installRoot = Join-Path $env:LOCALAPPDATA 'Vuln Sentinel'

if (Test-Path -LiteralPath $installRoot) {
  Remove-Item -LiteralPath $installRoot -Recurse -Force
}

function Invoke-Installer([string]$path) {
  $process = Start-Process -FilePath $path -ArgumentList '/S' -Wait -PassThru
  if ($process.ExitCode -ne 0) {
    throw "NSIS installer exited with code $($process.ExitCode)"
  }
}

function Find-ProductExecutable() {
  if (-not (Test-Path -LiteralPath $installRoot)) { return $null }
  Get-ChildItem -LiteralPath $installRoot -Recurse -File -Filter '*.exe' |
    Where-Object { $_.Name -notmatch '^(uninstall|vuln-sentinel-backend)' } |
    Select-Object -First 1
}

Invoke-Installer $installer
$app = Find-ProductExecutable
if (-not $app) { throw "Installed product executable was not found under $installRoot" }

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
if (Test-Path -LiteralPath $installRoot) { throw 'Install directory remains after uninstall smoke test' }

Write-Host 'Windows install, launch, upgrade, and uninstall smoke checks passed.'
