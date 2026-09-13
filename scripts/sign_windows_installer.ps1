param(
  [Parameter(Mandatory=$true)][string]$InstallerPath,
  [Parameter(Mandatory=$true)][string]$CertificatePath,
  [Parameter(Mandatory=$true)][securestring]$CertificatePassword,
  [string]$TimestampUrl = 'http://timestamp.digicert.com'
)

$ErrorActionPreference = 'Stop'
$installer = (Resolve-Path -LiteralPath $InstallerPath).Path
$certificate = (Resolve-Path -LiteralPath $CertificatePath).Path
$signtool = Get-ChildItem 'C:\Program Files (x86)\Windows Kits\10\bin' -Recurse -Filter signtool.exe |
  Where-Object { $_.FullName -match '\\x64\\signtool\.exe$' } |
  Sort-Object FullName -Descending | Select-Object -First 1
if (-not $signtool) { throw 'Windows SDK signtool.exe not found.' }

$bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($CertificatePassword)
try { $plain = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr) }
finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr) }

& $signtool.FullName sign /fd SHA256 /f $certificate /p $plain /tr $TimestampUrl /td SHA256 $installer
if ($LASTEXITCODE -ne 0) { throw "signtool failed with exit code $LASTEXITCODE" }
& $signtool.FullName verify /pa /all $installer
if ($LASTEXITCODE -ne 0) { throw 'Signed installer verification failed.' }
Write-Host "Signed and verified: $installer"
