# Run Claude Code once via litellm (palo tokens) as a delegated subagent. Stdout = report.
param(
    [Parameter(Mandatory = $true)]
    [string]$Task,
    [string]$ProjectDir = (Get-Location).Path,
    [string]$SubagentType = 'generalPurpose',
    [string]$Model = ''
)

$ErrorActionPreference = 'Stop'
$probe = Join-Path $PSScriptRoot 'probe-litellm.ps1'
$notify = Join-Path $PSScriptRoot 'notify-litellm-failure.ps1'

function Get-UsageLoggerPath {
    if ($env:WORKSPACES_ROOT) {
        $ws = Join-Path $env:WORKSPACES_ROOT 'scripts\log_litellm_usage.py'
        if (Test-Path -LiteralPath $ws) { return $ws }
    }
    return Join-Path $PSScriptRoot 'log_litellm_usage.py'
}

function Get-UsageLogPath {
    if ($env:LITELLM_USAGE_LOG) { return $env:LITELLM_USAGE_LOG }
    $root = if ($env:WORKSPACES_ROOT) { $env:WORKSPACES_ROOT } else { 'E:\PC3_Shared\workspaces' }
    return Join-Path $root 'logs\litellm-usage.jsonl'
}

& $probe
if ($LASTEXITCODE -ne 0) {
    $msg = 'LiteLLM is not responding. Subagent was not started. Fix palo/VPN/proxy, then retry /amir_use_litellm_subagent.'
    & $notify -Reason $msg
    exit $LASTEXITCODE
}

$launcher = Join-Path $env:USERPROFILE 'bin\litellm.cmd'
if (-not (Test-Path -LiteralPath $launcher)) {
    $root = if ($env:WORKSPACES_ROOT) { $env:WORKSPACES_ROOT } else { 'E:\PC3_Shared\workspaces' }
    $launcher = Join-Path $root 'scripts\litellm.py'
}

$delegation = @"
You are a delegated subagent invoked from Cursor via Palo LiteLLM (corporate proxy).

Rules:
- Complete the task below using tools as needed.
- Prefer the Task tool with subagent_type ``$SubagentType`` for large exploration.
- Return a concise final report only (findings, paths, blockers). No filler.
- Never print secrets or full API tokens.

Task:
$Task
"@

$projectDir = (Resolve-Path -LiteralPath $ProjectDir).Path
$since = (Get-Date).ToUniversalTime().ToString('o')
$usagePy = Get-UsageLoggerPath
$paloPy = if ($env:WORKSPACES_ROOT) {
    Join-Path $env:WORKSPACES_ROOT 'virtual_envs\palo\.venv\Scripts\python.exe'
} else {
    'E:\PC3_Shared\workspaces\virtual_envs\palo\.venv\Scripts\python.exe'
}
if (-not (Test-Path -LiteralPath $paloPy)) { $paloPy = 'python' }
$spendBefore = (& $paloPy $usagePy get-spend 2>$null | Select-Object -Last 1)

$launchArgs = @()
if ($Model -and $Model.Trim()) {
    $launchArgs += @('--model', $Model.Trim())
}
$launchArgs += @($projectDir, '--', '-p', $delegation, '--print')

if ($launcher -like '*.py') {
    & python $launcher @launchArgs
} else {
    & $launcher @launchArgs
}
$code = $LASTEXITCODE

if ($code -ne 0) {
    & $notify -Reason "LiteLLM Claude subagent failed (exit $code). See terminal output above."
    exit $code
}

$logArgs = @(
    $usagePy, 'record',
    '--source', 'amir_use_litellm_subagent',
    '--project-dir', $projectDir,
    '--since', $since
)
if ($spendBefore -match '^[\d.]+$') {
    $logArgs += @('--spend-before', $spendBefore)
}
Write-Host ''
Write-Host '--- LiteLLM usage ---'
& $paloPy @logArgs
Write-Host "Log file: $(Get-UsageLogPath)"
if ($Model -and $Model.Trim()) {
    Write-Host "Model override: $($Model.Trim()) (palo default unchanged)"
}
Write-Host ''

exit 0
