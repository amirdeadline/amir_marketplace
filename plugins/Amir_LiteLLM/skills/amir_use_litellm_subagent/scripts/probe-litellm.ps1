# Returns 0 if Palo LiteLLM proxy responds (litellm --models). Never prints API keys.
param(
    [int]$TimeoutSec = 45
)

$ErrorActionPreference = 'Stop'

function Get-LitellmLauncher {
    $cmd = Join-Path $env:USERPROFILE 'bin\litellm.cmd'
    if (Test-Path -LiteralPath $cmd) { return $cmd }
    $root = if ($env:WORKSPACES_ROOT) { $env:WORKSPACES_ROOT } else { 'E:\PC3_Shared\workspaces' }
    $py = Join-Path $root 'scripts\litellm.py'
    if (Test-Path -LiteralPath $py) { return $py }
    throw 'litellm launcher not found (expected %USERPROFILE%\bin\litellm.cmd or WORKSPACES_ROOT\scripts\litellm.py)'
}

$launcher = Get-LitellmLauncher
$paloEnv = if ($env:WORKSPACES_ROOT) {
    Join-Path $env:WORKSPACES_ROOT 'virtual_envs\palo\.env'
} else {
    'E:\PC3_Shared\workspaces\virtual_envs\palo\.env'
}

if (-not (Test-Path -LiteralPath $paloEnv)) {
    Write-Error "palo .env missing: $paloEnv"
    exit 2
}

$job = Start-Job -ScriptBlock {
    param($Launcher)
    if ($Launcher -like '*.py') {
        & python $Launcher '--models' 2>&1 | Out-Null
    } else {
        & cmd /c $Launcher '--models' 2>&1 | Out-Null
    }
    return $LASTEXITCODE
} -ArgumentList $launcher

if (-not (Wait-Job $job -Timeout $TimeoutSec)) {
    Stop-Job $job -Force | Out-Null
    Remove-Job $job -Force | Out-Null
    Write-Error "LiteLLM probe timed out after ${TimeoutSec}s (proxy not responding or VPN down)"
    exit 3
}

$code = Receive-Job $job
Remove-Job $job -Force | Out-Null
if ($code -ne 0) {
    Write-Error "litellm --models failed (exit $code). Check VPN, ANTHROPIC_API_KEY on palo, and proxy health."
    exit 4
}
exit 0
