# Environment for cursor_subagent.py: per-PC venv with cursor-sdk, CURSOR_API_KEY, short agent store.
# Dot-source this; it sets $env:CURSOR_SUBAGENT_PYTHON and (if found) $env:CURSOR_API_KEY.
# Never prints the key.
$ErrorActionPreference = 'Stop'

$venv = if ($env:CURSOR_SUBAGENT_VENV) { $env:CURSOR_SUBAGENT_VENV } else { Join-Path $env:USERPROFILE '.venvs\composer' }
$python = Join-Path $venv 'Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    Write-Error "Composer venv missing at $venv. Run: python -m venv `"$venv`"; `"$venv\Scripts\pip.exe`" install cursor-sdk"
}
$env:CURSOR_SUBAGENT_PYTHON = $python

if (-not $env:CURSOR_SDK_STORE_ROOT) {
    # Short path: the SDK's default store under ~/.cursor/projects/<long-name>/... breaks Windows MAX_PATH.
    $env:CURSOR_SDK_STORE_ROOT = Join-Path $env:USERPROFILE '.amir\composer-store'
}

if (-not $env:CURSOR_API_KEY) {
    $candidates = @(
        (Join-Path $env:USERPROFILE '.amir\secrets\cursor_api_key.env'),
        'E:\PC3_Shared\workspaces\virtual_envs\ai\.env'
    )
    foreach ($envFile in $candidates) {
        if (-not (Test-Path -LiteralPath $envFile)) { continue }
        Get-Content -LiteralPath $envFile | ForEach-Object {
            $line = $_.Trim()
            if (-not $line -or $line.StartsWith('#')) { return }
            if ($line -match '^export\s+') { $line = $line.Substring(7).Trim() }
            $eq = $line.IndexOf('=')
            if ($eq -lt 1) { return }
            if ($line.Substring(0, $eq).Trim() -ne 'CURSOR_API_KEY') { return }
            $value = $line.Substring($eq + 1).Trim()
            if ($value.Length -ge 2 -and (($value.StartsWith('"') -and $value.EndsWith('"')) -or ($value.StartsWith("'") -and $value.EndsWith("'")))) {
                $value = $value.Substring(1, $value.Length - 2)
            }
            Set-Item -Path 'Env:CURSOR_API_KEY' -Value $value
        }
        if ($env:CURSOR_API_KEY) { break }
    }
}
if (-not $env:CURSOR_API_KEY) {
    Write-Error 'CURSOR_API_KEY not set. Put CURSOR_API_KEY=... in %USERPROFILE%\.amir\secrets\cursor_api_key.env (0600) or a User env var.'
}
