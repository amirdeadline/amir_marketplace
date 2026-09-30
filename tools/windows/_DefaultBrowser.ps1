# Shared helpers for Set-DefaultBrowser-*.ps1
# Windows 11 blocks registry writes to UserChoice (UCPD). These helpers open
# Settings to the app page and invoke the official "Set default" button.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-HttpHttpsProgId {
    $result = [ordered]@{}
    foreach ($proto in @('http', 'https')) {
        $latest = "HKCU:\Software\Microsoft\Windows\Shell\Associations\UrlAssociations\$proto\UserChoiceLatest\ProgId"
        $legacy = "HKCU:\Software\Microsoft\Windows\Shell\Associations\UrlAssociations\$proto\UserChoice"
        if (Test-Path $latest) {
            $result[$proto] = (Get-ItemProperty -Path $latest).ProgId
        }
        elseif (Test-Path $legacy) {
            $result[$proto] = (Get-ItemProperty -Path $legacy).ProgId
        }
        else {
            $result[$proto] = $null
        }
    }
    return [pscustomobject]$result
}

function Get-AssocFriendlyApp {
    param([Parameter(Mandatory)][string]$Association)

    if (-not ('DefaultBrowser.Assoc' -as [type])) {
        Add-Type -Namespace DefaultBrowser -Name Assoc -MemberDefinition @'
[System.Runtime.InteropServices.DllImport("Shlwapi.dll", CharSet = System.Runtime.InteropServices.CharSet.Unicode)]
public static extern uint AssocQueryString(
    int flags, int str, string pszAssoc, string pszExtra,
    System.Text.StringBuilder pszOut, ref uint pcchOut);
'@
    }

    $sb = New-Object System.Text.StringBuilder 1024
    $len = [uint32]$sb.Capacity
    # ASSOCSTR_FRIENDLYAPPNAME = 4
    [void][DefaultBrowser.Assoc]::AssocQueryString(0, 4, $Association, $null, $sb, [ref]$len)
    return $sb.ToString()
}

function Test-BrowserInstalled {
    param(
        [Parameter(Mandatory)][string]$ExePath,
        [Parameter(Mandatory)][string]$StartMenuInternetName
    )

    if (-not (Test-Path -LiteralPath $ExePath)) {
        throw "Browser executable not found: $ExePath"
    }

    $key = "HKLM:\SOFTWARE\Clients\StartMenuInternet\$StartMenuInternetName"
    if (-not (Test-Path -LiteralPath $key)) {
        throw "Browser is not registered under StartMenuInternet as '$StartMenuInternetName'."
    }
}

function Set-DefaultBrowserViaSettings {
    param(
        [Parameter(Mandatory)][string]$RegisteredAppName,
        [Parameter(Mandatory)][string]$ExpectedProgId,
        [Parameter(Mandatory)][string]$FriendlyNameMatch,
        [int]$TimeoutSeconds = 30,
        [switch]$KeepSettingsOpen
    )

    Add-Type -AssemblyName UIAutomationClient
    Add-Type -AssemblyName UIAutomationTypes

    $before = Get-HttpHttpsProgId
    Write-Host "Current default ProgId: http=$($before.http) https=$($before.https)"

    Get-Process -Name 'SystemSettings' -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep -Milliseconds 600

    $encoded = [uri]::EscapeDataString($RegisteredAppName)
    $uri = "ms-settings:defaultapps?registeredAppMachine=$encoded"
    Write-Host "Opening Settings: $RegisteredAppName"
    Start-Process $uri | Out-Null

    $buttonId = 'SystemSettings_DefaultApps_DefaultBrowserWithPinToStartAndTaskbarAction_Button'
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    $button = $null

    while ((Get-Date) -lt $deadline) {
        $root = [System.Windows.Automation.AutomationElement]::RootElement
        $settingsCond = New-Object System.Windows.Automation.PropertyCondition (
            [System.Windows.Automation.AutomationElement]::NameProperty), 'Settings'
        $settings = $root.FindFirst([System.Windows.Automation.TreeScope]::Children, $settingsCond)
        if ($settings) {
            $idCond = New-Object System.Windows.Automation.PropertyCondition (
                [System.Windows.Automation.AutomationElement]::AutomationIdProperty), $buttonId
            $candidate = $settings.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $idCond)
            if ($candidate -and $candidate.Current.Name -match [regex]::Escape($FriendlyNameMatch)) {
                $button = $candidate
                break
            }
        }
        Start-Sleep -Milliseconds 350
    }

    if (-not $button) {
        throw "Timed out waiting for the 'Set default' button for '$RegisteredAppName'. Is Settings usable on this desktop session?"
    }

    if (-not $button.Current.IsEnabled) {
        throw "The 'Set default' button for '$RegisteredAppName' is disabled."
    }

    Write-Host "Clicking: $($button.Current.Name)"
    $invoke = $button.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
    $invoke.Invoke()

    $verifyDeadline = (Get-Date).AddSeconds($TimeoutSeconds)
    $after = $null
    do {
        Start-Sleep -Milliseconds 400
        $after = Get-HttpHttpsProgId
        if ($after.http -eq $ExpectedProgId -and $after.https -eq $ExpectedProgId) {
            break
        }
    } while ((Get-Date) -lt $verifyDeadline)

    $httpFriendly = Get-AssocFriendlyApp -Association 'http'
    $httpsFriendly = Get-AssocFriendlyApp -Association 'https'

    $ok = ($after.http -eq $ExpectedProgId -and $after.https -eq $ExpectedProgId)

    if (-not $KeepSettingsOpen) {
        Get-Process -Name 'SystemSettings' -ErrorAction SilentlyContinue | Stop-Process -Force
    }

    $summary = [pscustomobject]@{
        RegisteredApp   = $RegisteredAppName
        ExpectedProgId  = $ExpectedProgId
        HttpProgId      = $after.http
        HttpsProgId     = $after.https
        HttpFriendlyApp = $httpFriendly
        HttpsFriendlyApp= $httpsFriendly
        Success         = $ok
    }

    if (-not $ok) {
        Write-Error ("Failed to set default browser to '{0}'. http={1} https={2} (friendly: {3} / {4})" -f `
            $RegisteredAppName, $after.http, $after.https, $httpFriendly, $httpsFriendly)
    }

    Write-Host "Default browser is now: $httpFriendly (ProgId $($after.http))"
    return $summary
}
