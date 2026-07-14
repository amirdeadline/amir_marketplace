# Install amir-marketplace plugins into Cursor's local plugin directory.
# Usage (from marketplace root or anywhere):
#   powershell -ExecutionPolicy Bypass -File scripts/install-cursor-local.ps1

$ErrorActionPreference = "Stop"

$MarketplaceRoot = Split-Path -Parent $PSScriptRoot
$LocalRoot = Join-Path $env:USERPROFILE ".cursor\plugins\local"
New-Item -ItemType Directory -Force -Path $LocalRoot | Out-Null

$plugins = @(
  @{ Name = "amir"; Path = Join-Path $MarketplaceRoot "plugins\amir" },
  @{ Name = "amir-asana"; Path = Join-Path $MarketplaceRoot "plugins\amir-asana" }
)

foreach ($p in $plugins) {
  if (-not (Test-Path $p.Path)) {
    Write-Error "Missing $($p.Path). Run the matching pack script first."
  }
  $manifest = Join-Path $p.Path ".cursor-plugin\plugin.json"
  if (-not (Test-Path $manifest)) {
    Write-Error "Missing Cursor manifest: $manifest"
  }

  $link = Join-Path $LocalRoot $p.Name
  if (Test-Path $link) {
    $item = Get-Item $link -Force
    if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
      cmd /c "rmdir `"$link`""
    } else {
      Remove-Item -Recurse -Force $link
    }
  }

  cmd /c "mklink /J `"$link`" `"$($p.Path)`""
  if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to create junction for $($p.Name)"
  }
  Write-Host "OK  $link -> $($p.Path)"
}

Write-Host ""
Write-Host "Done. In Cursor: Developer: Reload Window"
Write-Host "Then open Customize -> Plugins and confirm amir + amir-asana."
