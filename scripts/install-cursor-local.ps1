# Junction all packed plugins into Cursor local plugins dir.
$ErrorActionPreference = "Stop"

$MarketplaceRoot = Split-Path -Parent $PSScriptRoot
$LocalRoot = Join-Path $env:USERPROFILE ".cursor\plugins\local"
New-Item -ItemType Directory -Force -Path $LocalRoot | Out-Null

$pluginRoot = Join-Path $MarketplaceRoot "plugins"
Get-ChildItem $pluginRoot -Directory | ForEach-Object {
  $name = $_.Name
  $path = $_.FullName
  $manifest = Join-Path $path ".cursor-plugin\plugin.json"
  if (-not (Test-Path $manifest)) {
    Write-Warning "Skip $name - no Cursor manifest"
    return
  }
  $link = Join-Path $LocalRoot $name
  if (Test-Path $link) {
    $item = Get-Item $link -Force
    if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
      cmd /c "rmdir `"$link`""
    } else {
      Remove-Item -Recurse -Force $link
    }
  }
  cmd /c "mklink /J `"$link`" `"$path`""
  if ($LASTEXITCODE -ne 0) { Write-Error "Failed junction for $name" }
  Write-Host "OK  $link"
}

Write-Host ""
Write-Host "Done. Developer: Reload Window"
Write-Host "Type /amir in chat to see marketplace slash commands."
