<#
.SYNOPSIS
  Set Prisma Access Browser as the Windows default browser.

.DESCRIPTION
  Opens Windows Settings to Prisma Access Browser and clicks the official
  "Set default" button. Direct registry edits are blocked by Windows UCPD.

.PARAMETER KeepSettingsOpen
  Leave the Settings window open after the change.

.EXAMPLE
  .\Set-DefaultBrowser-PrismaAccess.ps1
#>
[CmdletBinding()]
param(
    [switch]$KeepSettingsOpen
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$helper = Join-Path $PSScriptRoot '_DefaultBrowser.ps1'
. $helper

$exe = 'C:\Program Files\Palo Alto Networks\PrismaAccessBrowser\Application\PrismaAccessBrowser.exe'
Test-BrowserInstalled -ExePath $exe -StartMenuInternetName 'Prisma Access Browser'

Set-DefaultBrowserViaSettings `
    -RegisteredAppName 'Prisma Access Browser' `
    -ExpectedProgId 'PABHTML' `
    -FriendlyNameMatch 'Prisma Browser' `
    -KeepSettingsOpen:$KeepSettingsOpen
