<#
.SYNOPSIS
  Set Google Chrome as the Windows default browser.

.DESCRIPTION
  Opens Windows Settings to Google Chrome and clicks the official
  "Set default" button. Direct registry edits are blocked by Windows UCPD.

.PARAMETER KeepSettingsOpen
  Leave the Settings window open after the change.

.EXAMPLE
  .\Set-DefaultBrowser-Chrome.ps1
#>
[CmdletBinding()]
param(
    [switch]$KeepSettingsOpen
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$helper = Join-Path $PSScriptRoot '_DefaultBrowser.ps1'
. $helper

$exe = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
Test-BrowserInstalled -ExePath $exe -StartMenuInternetName 'Google Chrome'

Set-DefaultBrowserViaSettings `
    -RegisteredAppName 'Google Chrome' `
    -ExpectedProgId 'ChromeHTML' `
    -FriendlyNameMatch 'Google Chrome' `
    -KeepSettingsOpen:$KeepSettingsOpen
