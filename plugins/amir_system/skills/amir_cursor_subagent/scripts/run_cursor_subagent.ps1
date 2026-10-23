# Run cursor_subagent.py (local Cursor agent via the Cursor SDK) with the per-PC composer venv.
# Never use a parameter named Prompt: PowerShell's $Prompt collides with it and mangles the task.
#
#   run_cursor_subagent.ps1 -Cwd <repo> -TaskFile <utf8.txt> -Json                 # composer-2.5 fast
#   run_cursor_subagent.ps1 -Cwd <repo> -TaskText "..." -Model claude-opus-5-5 -Param effort=high
#   run_cursor_subagent.ps1 -Cwd <repo> -ListModels
param(
    [Parameter(Mandatory = $true)]
    [string]$Cwd,
    [string]$TaskText,
    [string]$TaskFile,
    [string]$Model,
    [string[]]$Param,
    [switch]$NoFast,
    [switch]$Json,
    [string]$Events,
    [switch]$ListModels,
    [string]$StoreRoot
)

$ErrorActionPreference = 'Stop'

$delegate = Join-Path $PSScriptRoot 'cursor_subagent.py'
$envScript = Join-Path $PSScriptRoot 'cursor_subagent_env.ps1'
if (-not (Test-Path -LiteralPath $delegate)) { Write-Error "Missing $delegate" }
if (-not (Test-Path -LiteralPath $envScript)) { Write-Error "Missing $envScript" }

. $envScript

$resolvedCwd = (Resolve-Path -LiteralPath $Cwd).Path
$pyArgs = @($delegate, '--cwd', $resolvedCwd)
if ($Model) { $pyArgs += @('--model', $Model) }
foreach ($p in ($Param | Where-Object { $_ })) { $pyArgs += @('--param', $p) }
if ($NoFast) { $pyArgs += '--no-fast' }
if ($Json) { $pyArgs += '--json' }
if ($Events) { $pyArgs += @('--events', $Events) }
if ($StoreRoot) { $pyArgs += @('--store-root', $StoreRoot) }

if ($ListModels) {
    & $env:CURSOR_SUBAGENT_PYTHON @pyArgs '--list-models'
    exit $LASTEXITCODE
}

if (-not $TaskText -and -not $TaskFile) { Write-Error 'Pass -TaskText or -TaskFile (or -ListModels).' }
if ($TaskText -and $TaskFile) { Write-Error 'Pass only one of -TaskText or -TaskFile.' }

$tmp = $null
try {
    if ($TaskFile) {
        if (-not (Test-Path -LiteralPath $TaskFile)) { Write-Error "TaskFile not found: $TaskFile" }
        $taskPath = (Resolve-Path -LiteralPath $TaskFile).Path
    }
    else {
        $tmp = [System.IO.Path]::GetTempFileName()
        [System.IO.File]::WriteAllText($tmp, $TaskText, (New-Object System.Text.UTF8Encoding $false))
        $taskPath = $tmp
    }
    & $env:CURSOR_SUBAGENT_PYTHON @pyArgs '--task-file' $taskPath
    exit $LASTEXITCODE
}
finally {
    if ($tmp) { Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue }
}
