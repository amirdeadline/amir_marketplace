# Audible + desktop alert when LiteLLM / litellm session is unavailable. Never prints secrets.
param(
    [Parameter(Mandatory = $true)]
    [string]$Reason
)

$ErrorActionPreference = 'SilentlyContinue'

$soundDir = $env:CLAUDE_SOUND_DIR
if (-not $soundDir) { $soundDir = Join-Path $env:WINDIR 'Media' }
$wavs = @(Get-ChildItem -LiteralPath $soundDir -Filter '*.wav' -File -ErrorAction SilentlyContinue)
if ($wavs.Count -gt 0) {
    $pick = $wavs | Get-Random -Count 1
    try {
        $player = New-Object System.Media.SoundPlayer $pick.FullName
        $player.Play()
    } catch {
        [Console]::Beep(440, 200)
        Start-Sleep -Milliseconds 80
        [Console]::Beep(330, 200)
    }
} else {
    [Console]::Beep(440, 200)
    Start-Sleep -Milliseconds 80
    [Console]::Beep(330, 200)
}

try {
    Add-Type -AssemblyName System.Windows.Forms -ErrorAction Stop
    [System.Windows.Forms.MessageBox]::Show(
        $Reason,
        'LiteLLM session failed',
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Warning
    ) | Out-Null
} catch {
    Write-Host "LITELLM_FAILURE: $Reason"
}

exit 1
