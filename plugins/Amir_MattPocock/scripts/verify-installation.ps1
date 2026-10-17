#Requires -Version 5.1
[CmdletBinding()]
param(
    [string]$ProjectRoot,
    [ValidateSet('All', 'Selected')]
    [string]$Scope = 'Selected'
)

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$packageRoot = Split-Path -Parent $scriptDir

. (Join-Path $scriptDir 'lib/MattPocockInstall.Common.ps1')
. (Join-Path $scriptDir 'lib/MattPocockInstall.Engine.ps1')

$result = Invoke-MattPocockInstall -Mode VerifyOnly -ProjectRoot $ProjectRoot -SkipBootstrap

$expected = if ($Scope -eq 'All') {
    $result.Discovered
}
else {
    Get-SelectedSkillList -ConfigPath (Join-Path $packageRoot 'config/selected-skills.json')
}

$verification = Test-InstalledMattPocockSkills -ProjectRoot $result.ProjectRoot -ExpectedSkills $expected
$verification | Format-Table Skill, Present, SkillPath -AutoSize

$missing = @($verification | Where-Object { -not $_.Present })
if ($missing.Count -gt 0) {
    exit 1
}
exit 0
