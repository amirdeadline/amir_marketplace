#Requires -Version 5.1
<#
.SYNOPSIS
  Project-local Matt Pocock skills installer (All or Selected modes).

.EXAMPLE
  .\install-mattpocock.ps1 -Mode All

.EXAMPLE
  .\install-mattpocock.ps1 -Mode Selected -ProjectRoot "C:\Projects\MyApp" -Verbose

.EXAMPLE
  .\install-mattpocock.ps1 -Mode VerifyOnly
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet('All', 'Selected', 'VerifyOnly')]
    [string]$Mode,

    [string]$ProjectRoot,
    [string[]]$Agents,
    [switch]$DryRun,
    [switch]$ForceUpdate,
    [switch]$ForceCopy,
    [switch]$SkipBootstrap
)

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $scriptDir 'lib/MattPocockInstall.Common.ps1')
. (Join-Path $scriptDir 'lib/MattPocockInstall.Engine.ps1')

$result = Invoke-MattPocockInstall -Mode $Mode `
    -ProjectRoot $ProjectRoot `
    -Agents $Agents `
    -DryRun:$DryRun `
    -ForceUpdate:$ForceUpdate `
    -ForceCopy:$ForceCopy `
    -SkipBootstrap:$SkipBootstrap

Write-Host ""
Write-Host "Matt Pocock install ($($result.Mode))" -ForegroundColor Cyan
Write-Host "  Project: $($result.ProjectRoot)"
Write-Host "  Agents:  $($result.Agents -join ', ')"
Write-Host "  Log:     $($result.LogPath)"

if ($result.MissingUpstream.Count -gt 0) {
    Write-Host ""
    Write-Host "Missing or renamed upstream skills:" -ForegroundColor Yellow
    foreach ($m in $result.MissingUpstream) {
        Write-Host "  - $m"
    }
}

if ($result.SkippedConflicts.Count -gt 0) {
    Write-Host ""
    Write-Host "Skipped due to conflicts:" -ForegroundColor Yellow
    $result.SkippedConflicts | Format-Table -AutoSize
}

$missing = @($result.Verification | Where-Object { -not $_.Present })
$present = @($result.Verification | Where-Object { $_.Present })
Write-Host ""
Write-Host "Verified present: $($present.Count)  Missing: $($missing.Count)"

if ($missing.Count -gt 0) {
    Write-Host "Missing skill files:" -ForegroundColor Red
    $missing | ForEach-Object { Write-Host "  - $($_.Skill)" }
}

exit $result.ExitCode
