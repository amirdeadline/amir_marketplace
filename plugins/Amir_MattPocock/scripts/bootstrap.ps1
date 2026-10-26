#Requires -Version 5.1
<#
.SYNOPSIS
  Bootstrap Amir Matt Pocock installer skills into the current project (no prior skills required).

.EXAMPLE
  pwsh -File .\bootstrap.ps1 -ProjectRoot "C:\Projects\MyApp"
#>
[CmdletBinding()]
param(
    [string]$ProjectRoot,
    [switch]$DryRun,
    [switch]$InstallMattPocockSelected,
    [switch]$InstallMattPocockAll
)

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$packageRoot = Split-Path -Parent $scriptDir

. (Join-Path $scriptDir 'lib/MattPocockInstall.Common.ps1')
. (Join-Path $scriptDir 'lib/MattPocockInstall.Engine.ps1')

$resolvedRoot = Resolve-ProjectRoot -ExplicitRoot $ProjectRoot
$stateDir = Get-MattPocockInstallStateDir -ProjectRoot $resolvedRoot
New-Item -ItemType Directory -Force -Path $stateDir | Out-Null
$logPath = New-InstallLogPath -StateDir $stateDir

Write-Host "Bootstrapping installer skills into: $resolvedRoot" -ForegroundColor Cyan
$installed = Install-InstallerSkillsToProject -ProjectRoot $resolvedRoot -PackageRoot $packageRoot -LogPath $logPath -DryRun:$DryRun

$installed | Format-Table -AutoSize

if ($InstallMattPocockAll) {
    & (Join-Path $scriptDir 'install-mattpocock.ps1') -Mode All -ProjectRoot $resolvedRoot
    exit $LASTEXITCODE
}

if ($InstallMattPocockSelected) {
    & (Join-Path $scriptDir 'install-mattpocock.ps1') -Mode Selected -ProjectRoot $resolvedRoot
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Green
Write-Host "  Cursor / Claude / Codex / Hermes: invoke /amir_install_mattpocock or /amir_install_mattpocock_all"
Write-Host "  Or run: pwsh -File `"$($scriptDir)\install-mattpocock.ps1`" -Mode Selected"

exit 0
