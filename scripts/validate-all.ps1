# Windows-first validator for the whole marketplace
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
  Write-Error "claude CLI not on PATH"
}

Write-Host "== marketplace =="
claude plugin validate $Root
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$fail = 0
Get-ChildItem (Join-Path $Root "plugins") -Directory | ForEach-Object {
  Write-Host "== plugin: $($_.Name) =="
  claude plugin validate $_.FullName
  if ($LASTEXITCODE -ne 0) { $fail = 1 }
}

node (Join-Path $Root "scripts\verify-marketplace.js")
if ($LASTEXITCODE -ne 0) { $fail = 1 }

if ($fail -ne 0) {
  Write-Error "validate-all: FAILED"
}
Write-Host "validate-all: OK"
