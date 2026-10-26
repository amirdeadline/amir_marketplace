# Installation engine: invokes Vercel skills CLI for Matt Pocock packages.

Set-StrictMode -Version Latest

function ConvertFrom-SkillsCliJson {
    param([Parameter(Mandatory)][string]$RawOutput)

    $clean = ($RawOutput -replace "\e\[[0-9;]*m", '').Trim()
    $starts = [regex]::Matches($clean, '\[\s*\{')
    if ($starts.Count -eq 0) {
        throw 'skills CLI did not return JSON payload'
    }

    for ($i = $starts.Count - 1; $i -ge 0; $i--) {
        $candidate = $clean.Substring($starts[$i].Index).Trim()
        try {
            return ($candidate | ConvertFrom-Json)
        }
        catch {
            continue
        }
    }

    throw 'skills CLI JSON payload could not be parsed'
}

function Invoke-SkillsCliAdd {
    param(
        [Parameter(Mandatory)][string]$ProjectRoot,
        [Parameter(Mandatory)][string[]]$SkillNames,
        [Parameter(Mandatory)][string[]]$AgentIds,
        [Parameter(Mandatory)][string]$LogPath,
        [switch]$DryRun,
        [switch]$ForceCopy
    )

    if ($DryRun) {
        Write-InstallLog -LogPath $LogPath -Message ("DRY-RUN would install skills: {0} agents: {1}" -f ($SkillNames -join ','), ($AgentIds -join ','))
        return @()
    }

    $args = @('add', $script:MattPocockSourceRepo, '--skill')
    if ($SkillNames.Count -eq 1 -and $SkillNames[0] -eq '*') {
        $args += '*'
    }
    else {
        $args += $SkillNames
    }
    $args += @('--agent') + $AgentIds + @('-y', '--json')

    if ($ForceCopy) {
        $args += '--copy'
    }

    $inv = Get-SkillsCliInvocation -ArgumentList $args
    Write-InstallLog -LogPath $LogPath -Message ("Running skills CLI: npx {0}" -f ($args -join ' '))

    Push-Location -LiteralPath $ProjectRoot
    try {
        $prevEap = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        $stdout = & npx --yes $script:SkillsCliPackage @args 2>&1 | Out-String
        $ErrorActionPreference = $prevEap
        Write-InstallLog -LogPath $LogPath -Message $stdout
        if ($LASTEXITCODE -ne 0) {
            throw "skills CLI exited with code $LASTEXITCODE"
        }

        return ConvertFrom-SkillsCliJson -RawOutput $stdout
    }
    finally {
        Pop-Location
    }
}

function Get-SelectedSkillList {
    param([Parameter(Mandatory)][string]$ConfigPath)

    if (-not (Test-Path -LiteralPath $ConfigPath)) {
        throw "Selected skills config not found: $ConfigPath"
    }
    $cfg = Get-Content -LiteralPath $ConfigPath -Raw | ConvertFrom-Json
    return @($cfg.skills)
}

function Invoke-MattPocockInstall {
    param(
        [Parameter(Mandatory)][ValidateSet('All', 'Selected', 'VerifyOnly')][string]$Mode,
        [string]$ProjectRoot,
        [string]$PackageRoot,
        [string[]]$Agents,
        [switch]$DryRun,
        [switch]$ForceUpdate,
        [switch]$ForceCopy,
        [switch]$SkipBootstrap
    )

    $deps = Test-InstallDependencies
    if (-not $deps.Git -or -not $deps.Npx -or -not $deps.Node) {
        throw 'Missing dependencies. Requires git, node, and npx on PATH.'
    }

    $resolvedRoot = Resolve-ProjectRoot -ExplicitRoot $ProjectRoot
    if (-not $PackageRoot) {
        $PackageRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
    }

    $stateDir = Get-MattPocockInstallStateDir -ProjectRoot $resolvedRoot
    New-Item -ItemType Directory -Force -Path $stateDir | Out-Null
    $logPath = New-InstallLogPath -StateDir $stateDir
    Write-InstallLog -LogPath $logPath -Message "Mode=$Mode ProjectRoot=$resolvedRoot PackageRoot=$PackageRoot"

    $agentIds = Resolve-TargetAgents -RequestedAgents $Agents -IncludeAllSupported
    Write-InstallLog -LogPath $logPath -Message "Target agents: $($agentIds -join ', ')"

    $upstreamSha = Get-UpstreamCommitSha -StateDir $stateDir -LogPath $logPath
    Write-InstallLog -LogPath $logPath -Message "Upstream commit: $upstreamSha"

    if (-not $SkipBootstrap) {
        Install-InstallerSkillsToProject -ProjectRoot $resolvedRoot -PackageRoot $PackageRoot -LogPath $logPath -DryRun:$DryRun | Out-Null
    }

    $discovered = Get-DiscoveredSkillNamesFromCli -ProjectRoot $resolvedRoot -LogPath $logPath
    Write-InstallLog -LogPath $logPath -Message ("Discovered {0} upstream skills" -f $discovered.Count)

    $skillsLockPath = Join-Path $resolvedRoot 'skills-lock.json'
    $toInstall = @()
    $skippedConflicts = @()
    $missingSelected = @()

    if ($Mode -eq 'All') {
        $toInstall = $discovered
    }
    elseif ($Mode -eq 'Selected') {
        $configPath = Join-Path $PackageRoot 'config/selected-skills.json'
        $requested = Get-SelectedSkillList -ConfigPath $configPath
        foreach ($skill in $requested) {
            if ($skill -notin $discovered) {
                $missingSelected += $skill
            }
            else {
                $toInstall += $skill
            }
        }
    }
    elseif ($Mode -eq 'VerifyOnly') {
        $configPath = Join-Path $PackageRoot 'config/selected-skills.json'
        $toInstall = Get-SelectedSkillList -ConfigPath $configPath
    }

    foreach ($skill in @($toInstall)) {
        $conflict = Test-SkillConflict -ProjectRoot $resolvedRoot -SkillName $skill -SkillsLockPath $skillsLockPath
        if ($conflict.HasConflict) {
            Write-InstallLog -LogPath $logPath -Message "CONFLICT skip $skill : $($conflict.Reason)"
            $skippedConflicts += [pscustomobject]@{ Skill = $skill; Reason = $conflict.Reason }
            $toInstall = @($toInstall | Where-Object { $_ -ne $skill })
        }
    }

    $cliResults = @()
    if ($Mode -ne 'VerifyOnly') {
        if ($toInstall.Count -eq 0 -and $Mode -ne 'Selected') {
            Write-InstallLog -LogPath $logPath -Message 'No skills to install after conflict filtering'
        }
        elseif ($Mode -eq 'All' -and $toInstall.Count -eq $discovered.Count) {
            $cliResults = Invoke-SkillsCliAdd -ProjectRoot $resolvedRoot -SkillNames @('*') -AgentIds $agentIds -LogPath $logPath -DryRun:$DryRun -ForceCopy:$ForceCopy
        }
        elseif ($toInstall.Count -gt 0) {
            $cliResults = Invoke-SkillsCliAdd -ProjectRoot $resolvedRoot -SkillNames $toInstall -AgentIds $agentIds -LogPath $logPath -DryRun:$DryRun -ForceCopy:$ForceCopy
        }
    }

    $verifySet = if ($Mode -eq 'All') { $discovered } else { $toInstall + $missingSelected }
    $verification = Test-InstalledMattPocockSkills -ProjectRoot $resolvedRoot -ExpectedSkills $verifySet

    $manifest = @{
        mode            = $Mode
        projectRoot     = $resolvedRoot
        sourceRepo      = $script:MattPocockSourceRepo
        sourceUrl       = $script:MattPocockSourceUrl
        upstreamCommit  = $upstreamSha
        agents          = $agentIds
        requestedSkills = $toInstall
        discoveredCount = $discovered.Count
        dryRun          = [bool]$DryRun
        forceUpdate     = [bool]$ForceUpdate
        skippedConflicts = $skippedConflicts
        missingUpstream  = $missingSelected
        verification     = $verification
        logPath          = $logPath
    }

    if (-not $DryRun) {
        $manifestPath = Write-InstallManifest -StateDir $stateDir -Manifest $manifest
        Write-InstallLog -LogPath $logPath -Message "Wrote manifest: $manifestPath"
    }

    $failed = @($verification | Where-Object { -not $_.Present })
    $exitCode = 0
    if ($missingSelected.Count -gt 0) { $exitCode = 2 }
    if ($failed.Count -gt 0 -and $Mode -ne 'VerifyOnly') { $exitCode = 1 }
    if ($skippedConflicts.Count -gt 0 -and $exitCode -eq 0) { $exitCode = 3 }

    return [pscustomobject]@{
        ExitCode         = $exitCode
        ProjectRoot      = $resolvedRoot
        Mode             = $Mode
        Agents           = $agentIds
        Discovered       = $discovered
        InstalledSkills  = $toInstall
        MissingUpstream  = $missingSelected
        SkippedConflicts = $skippedConflicts
        Verification     = $verification
        CliResults       = $cliResults
        LogPath          = $logPath
        ManifestDir      = $stateDir
    }
}
