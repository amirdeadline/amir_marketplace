#Requires -Version 5.1
<#
.SYNOPSIS
  Remove Matt Pocock skills recorded in skills-lock.json (project-local).
#>
[CmdletBinding()]
param(
    [string]$ProjectRoot,
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $scriptDir 'lib/MattPocockInstall.Common.ps1')

$resolvedRoot = Resolve-ProjectRoot -ExplicitRoot $ProjectRoot
$lockPath = Join-Path $resolvedRoot 'skills-lock.json'
if (-not (Test-Path -LiteralPath $lockPath)) {
    Write-Error "No skills-lock.json at $lockPath"
}

$lock = Get-Content -LiteralPath $lockPath -Raw | ConvertFrom-Json
$names = @($lock.skills.PSObject.Properties.Name)
if ($names.Count -eq 0) {
    Write-Host 'No skills listed in skills-lock.json'
    exit 0
}

Write-Host "Removing $($names.Count) skill(s) via skills CLI..."
$args = @('remove') + $names + @('-y')
if ($DryRun) {
    Write-Host "DRY-RUN: npx skills@latest $($args -join ' ')"
    exit 0
}

$prevEap = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
Push-Location -LiteralPath $resolvedRoot
try {
    & npx --yes skills@latest @args 2>&1 | Out-String | Write-Host
}
finally {
    Pop-Location
    $ErrorActionPreference = $prevEap
}

exit $LASTEXITCODE
