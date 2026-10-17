# Shared helpers for Matt Pocock skill installers (project-local only).

Set-StrictMode -Version Latest

function Join-MultiPath {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$PathParts)
    $result = $PathParts[0]
    for ($i = 1; $i -lt $PathParts.Count; $i++) {
        $result = Join-Path -Path $result -ChildPath $PathParts[$i]
    }
    return $result
}

$script:MattPocockSourceRepo = 'mattpocock/skills'
$script:MattPocockSourceUrl = 'https://github.com/mattpocock/skills.git'
$script:SkillsCliPackage = 'skills@latest'
$script:DefaultAgentIds = @('cursor', 'claude-code', 'codex', 'hermes-agent')
$script:InstallStateDirName = '.amir/mattpocock-install'
$script:InstallerSkillNames = @('amir_install_mattpocock_all', 'amir_install_mattpocock')

function Get-MattPocockInstallStateDir {
    param([Parameter(Mandatory)][string]$ProjectRoot)
    Join-Path $ProjectRoot ($script:InstallStateDirName -replace '/', [IO.Path]::DirectorySeparatorChar)
}

function Resolve-ProjectRoot {
    param(
        [string]$ExplicitRoot,
        [string]$StartPath = (Get-Location).Path
    )

    if ($ExplicitRoot) {
        $resolved = Resolve-Path -LiteralPath $ExplicitRoot -ErrorAction Stop
        return $resolved.Path
    }

    $current = (Resolve-Path -LiteralPath $StartPath).Path
    $probe = $current
    while ($true) {
        if (Test-Path -LiteralPath (Join-Path $probe '.git') -PathType Container) {
            return $probe
        }
        $parent = Split-Path -Parent $probe
        if (-not $parent -or $parent -eq $probe) {
            return $current
        }
        $probe = $parent
    }
}

function Test-InstallDependencies {
    $result = [ordered]@{
        PowerShell = $true
        Git        = $null -ne (Get-Command git -ErrorAction SilentlyContinue)
        Node       = $null -ne (Get-Command node -ErrorAction SilentlyContinue)
        Npx        = $null -ne (Get-Command npx -ErrorAction SilentlyContinue)
    }
    return [pscustomobject]$result
}

function Get-AvailableCodingAgents {
    $agents = [ordered]@{}
    $agents['cursor'] = $true
    $agents['claude-code'] = [bool](Get-Command claude -ErrorAction SilentlyContinue)
    $agents['codex'] = [bool](Get-Command codex -ErrorAction SilentlyContinue)
    $agents['hermes-agent'] = [bool](Get-Command hermes -ErrorAction SilentlyContinue)
    return [pscustomobject]$agents
}

function Resolve-TargetAgents {
    param(
        [string[]]$RequestedAgents,
        [switch]$IncludeAllSupported
    )

    $supported = $script:DefaultAgentIds
    if ($RequestedAgents -and $RequestedAgents.Count -gt 0) {
        $invalid = $RequestedAgents | Where-Object { $_ -notin $supported }
        if ($invalid) {
            throw "Invalid agent id(s): $($invalid -join ', '). Valid: $($supported -join ', ')"
        }
        return $RequestedAgents
    }

    if ($IncludeAllSupported) {
        return $supported
    }

    $detected = Get-AvailableCodingAgents
    $selected = @()
    foreach ($id in $supported) {
        if ($detected.$id) { $selected += $id }
    }
    if (-not $selected) {
        $selected = @('cursor')
    }
    return $selected
}

function New-InstallLogPath {
    param([Parameter(Mandatory)][string]$StateDir)
    $logDir = Join-Path $StateDir 'logs'
    New-Item -ItemType Directory -Force -Path $logDir | Out-Null
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    Join-Path $logDir "install-$stamp.log"
}

function Write-InstallLog {
    param(
        [Parameter(Mandatory)][string]$LogPath,
        [Parameter(Mandatory)][string]$Message
    )
    $line = "[{0}] {1}" -f (Get-Date -Format 'o'), $Message
    Add-Content -LiteralPath $LogPath -Value $line -Encoding utf8
    if ($VerbosePreference -eq 'Continue') {
        Write-Verbose $Message
    }
}

function Invoke-ExternalCommand {
    param(
        [Parameter(Mandatory)][string]$FilePath,
        [Parameter(Mandatory)][string[]]$ArgumentList,
        [string]$LogPath,
        [string]$WorkingDirectory,
        [switch]$AllowFailure
    )

    $escaped = ($ArgumentList | ForEach-Object {
            if ($_ -match '\s') { '"{0}"' -f ($_ -replace '"', '\"') } else { $_ }
        }) -join ' '
    if ($LogPath) {
        Write-InstallLog -LogPath $LogPath -Message "EXEC: $FilePath $escaped"
    }

    Push-Location -LiteralPath $(if ($WorkingDirectory) { $WorkingDirectory } else { (Get-Location).Path })
    try {
        $prevEap = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        $output = & $FilePath @ArgumentList 2>&1 | Out-String
        $ErrorActionPreference = $prevEap
        $code = $LASTEXITCODE
        if ($null -eq $code) { $code = 0 }
        if ($LogPath -and $output) {
            Write-InstallLog -LogPath $LogPath -Message $output
        }
        if ($code -ne 0 -and -not $AllowFailure) {
            throw "Command failed ($code): $FilePath $escaped"
        }
        return [pscustomobject]@{
            ExitCode = $code
            StdOut   = $output
            StdErr   = ''
        }
    }
    finally {
        Pop-Location
    }
}

function Get-SkillsCliInvocation {
    param([string[]]$ArgumentList)
    return @{
        FilePath     = 'npx'
        ArgumentList = @('--yes', $script:SkillsCliPackage) + $ArgumentList
    }
}

function Get-UpstreamCommitSha {
    param(
        [Parameter(Mandatory)][string]$StateDir,
        [Parameter(Mandatory)][string]$LogPath
    )

    $cacheDir = Join-Path $StateDir 'upstream-cache'
    if (Test-Path -LiteralPath (Join-Path $cacheDir '.git')) {
        $rev = git -C $cacheDir rev-parse HEAD 2>$null
        if ($rev) { return $rev.Trim() }
    }

    New-Item -ItemType Directory -Force -Path $cacheDir | Out-Null
    if (-not (Test-Path -LiteralPath (Join-Path $cacheDir '.git'))) {
        Write-InstallLog -LogPath $LogPath -Message "Cloning upstream for revision pin: $($script:MattPocockSourceUrl)"
        Invoke-ExternalCommand -FilePath 'git' -ArgumentList @(
            'clone', '--depth', '1', $script:MattPocockSourceUrl, $cacheDir
        ) -LogPath $LogPath -AllowFailure:$false | Out-Null
    }
    else {
        Write-InstallLog -LogPath $LogPath -Message 'Fetching upstream HEAD (depth=1)'
        Invoke-ExternalCommand -FilePath 'git' -ArgumentList @('-C', $cacheDir, 'fetch', '--depth', '1', 'origin') -LogPath $LogPath -AllowFailure:$true | Out-Null
        Invoke-ExternalCommand -FilePath 'git' -ArgumentList @('-C', $cacheDir, 'reset', '--hard', 'origin/HEAD') -LogPath $LogPath -AllowFailure:$true | Out-Null
    }

    $sha = (git -C $cacheDir rev-parse HEAD).Trim()
    return $sha
}

function Get-DiscoveredSkillNamesFromCli {
    param(
        [Parameter(Mandatory)][string]$ProjectRoot,
        [Parameter(Mandatory)][string]$LogPath
    )

    $args = @('add', $script:MattPocockSourceRepo, '--list')
    $inv = Get-SkillsCliInvocation -ArgumentList $args
    $result = Invoke-ExternalCommand -FilePath $inv.FilePath -ArgumentList $inv.ArgumentList `
        -WorkingDirectory $ProjectRoot -LogPath $LogPath -AllowFailure:$true

    if ($result.ExitCode -ne 0 -or -not $result.StdOut) {
        Write-InstallLog -LogPath $LogPath -Message 'CLI --list failed; falling back to git tree scan'
        return Get-DiscoveredSkillNamesFromGit -StateDir (Get-MattPocockInstallStateDir -ProjectRoot $ProjectRoot) -LogPath $LogPath
    }

    $names = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    foreach ($line in ($result.StdOut -split "`n")) {
        if ($line -match '^\|\s+([a-z][a-z0-9-]*)\s*\|?\s*$') {
            [void]$names.Add($Matches[1])
        }
    }

    if ($names.Count -eq 0) {
        return Get-DiscoveredSkillNamesFromGit -StateDir (Get-MattPocockInstallStateDir -ProjectRoot $ProjectRoot) -LogPath $LogPath
    }

    return @($names | Sort-Object)
}

function Get-DiscoveredSkillNamesFromGit {
    param(
        [Parameter(Mandatory)][string]$StateDir,
        [Parameter(Mandatory)][string]$LogPath
    )

    $cacheDir = Join-Path $StateDir 'upstream-cache'
    if (-not (Test-Path -LiteralPath (Join-Path $cacheDir 'skills'))) {
        Get-UpstreamCommitSha -StateDir $StateDir -LogPath $LogPath | Out-Null
    }

    $skillFiles = Get-ChildItem -LiteralPath (Join-Path $cacheDir 'skills') -Recurse -Filter 'SKILL.md' -File -ErrorAction SilentlyContinue
    $excludeDirNames = @('node_modules', '.git', 'scripts', 'docs', '.out-of-scope')
    $names = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)

    foreach ($file in $skillFiles) {
        $dir = $file.Directory
        $relative = $dir.FullName.Substring((Join-Path $cacheDir 'skills').Length).TrimStart('\', '/')
        if ($relative -match '(^|[\\/])(\.|docs|scripts|templates)([\\/]|$)') { continue }
        foreach ($part in ($relative -split '[\\/]')) {
            if ($part -in $excludeDirNames) { continue 2 }
        }
        [void]$names.Add($dir.Name)
    }

    return @($names | Sort-Object)
}

function Get-ExistingProjectSkillNames {
    param([Parameter(Mandatory)][string]$ProjectRoot)

    $names = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    $roots = @(
        (Join-Path $ProjectRoot '.agents/skills'),
        (Join-Path $ProjectRoot '.cursor/skills'),
        (Join-Path $ProjectRoot '.claude/skills'),
        (Join-Path $ProjectRoot '.hermes/skills')
    )
    foreach ($root in $roots) {
        if (-not (Test-Path -LiteralPath $root)) { continue }
        Get-ChildItem -LiteralPath $root -Directory -ErrorAction SilentlyContinue | ForEach-Object {
            [void]$names.Add($_.Name)
        }
    }
    return @($names)
}

function Test-SkillConflict {
    param(
        [Parameter(Mandatory)][string]$ProjectRoot,
        [Parameter(Mandatory)][string]$SkillName,
        [string]$SkillsLockPath
    )

    $canonical = Join-MultiPath $ProjectRoot '.agents/skills' $SkillName
    if (-not (Test-Path -LiteralPath $canonical)) {
        return [pscustomobject]@{ HasConflict = $false; Reason = $null }
    }

    if (Test-Path -LiteralPath $SkillsLockPath) {
        try {
            $lock = Get-Content -LiteralPath $SkillsLockPath -Raw | ConvertFrom-Json
            if ($lock.skills.PSObject.Properties.Name -contains $SkillName) {
                $entry = $lock.skills.$SkillName
                if ($entry.source -eq $script:MattPocockSourceRepo) {
                    return [pscustomobject]@{ HasConflict = $false; Reason = 'existing-mattpocock' }
                }
            }
        }
        catch { }
    }

    if ($SkillName -in $script:InstallerSkillNames) {
        return [pscustomobject]@{ HasConflict = $false; Reason = 'installer-skill' }
    }

    return [pscustomobject]@{
        HasConflict = $true
        Reason      = "Skill '$SkillName' exists at $canonical and is not owned by $($script:MattPocockSourceRepo)"
    }
}

function New-DirectoryLink {
    param(
        [Parameter(Mandatory)][string]$LinkPath,
        [Parameter(Mandatory)][string]$TargetPath
    )

    $parent = Split-Path -Parent $LinkPath
    if (-not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }
    if (Test-Path -LiteralPath $LinkPath) {
        $item = Get-Item -LiteralPath $LinkPath -Force
        if ($item.LinkType -and $item.Target -eq $TargetPath) { return 'unchanged' }
        throw "Refusing to overwrite existing path: $LinkPath"
    }

    try {
        New-Item -ItemType SymbolicLink -Path $LinkPath -Target $TargetPath | Out-Null
        return 'symlink'
    }
    catch {
        try {
            New-Item -ItemType Junction -Path $LinkPath -Target $TargetPath | Out-Null
            return 'junction'
        }
        catch {
            Copy-Item -LiteralPath $TargetPath -Destination $LinkPath -Recurse -Force
            return 'copy'
        }
    }
}

function Install-InstallerSkillsToProject {
    param(
        [Parameter(Mandatory)][string]$ProjectRoot,
        [Parameter(Mandatory)][string]$PackageRoot,
        [Parameter(Mandatory)][string]$LogPath,
        [switch]$DryRun
    )

    $results = @()
    $canonicalRoot = Join-Path $ProjectRoot '.agents/skills'
    $sourceRoot = Join-Path $PackageRoot 'skills'

    foreach ($skillName in $script:InstallerSkillNames) {
        $src = Join-Path $sourceRoot $skillName
        if (-not (Test-Path -LiteralPath (Join-Path $src 'SKILL.md'))) {
            throw "Missing installer skill source: $src"
        }
        $dest = Join-Path $canonicalRoot $skillName
        if ($DryRun) {
            $results += [pscustomobject]@{ Skill = $skillName; Action = 'dry-run'; Path = $dest }
            continue
        }

        New-Item -ItemType Directory -Force -Path $canonicalRoot | Out-Null
        if (Test-Path -LiteralPath $dest) {
            Write-InstallLog -LogPath $LogPath -Message "Refreshing installer skill: $skillName"
            Remove-Item -LiteralPath $dest -Recurse -Force
        }
        Copy-Item -LiteralPath $src -Destination $dest -Recurse -Force
        Write-InstallLog -LogPath $LogPath -Message "Copied installer skill to $dest"

        foreach ($agentRoot in @('.claude/skills', '.hermes/skills')) {
            $linkPath = Join-MultiPath $ProjectRoot ($agentRoot.Replace('/', [IO.Path]::DirectorySeparatorChar)) $skillName
            $mode = New-DirectoryLink -LinkPath $linkPath -TargetPath $dest
            Write-InstallLog -LogPath $LogPath -Message "Linked $skillName -> $agentRoot ($mode)"
        }

        $results += [pscustomobject]@{ Skill = $skillName; Action = 'installed'; Path = $dest }
    }

    return $results
}

function Write-InstallManifest {
    param(
        [Parameter(Mandatory)][string]$StateDir,
        [Parameter(Mandatory)][hashtable]$Manifest
    )

    New-Item -ItemType Directory -Force -Path $StateDir | Out-Null
    $path = Join-Path $StateDir 'manifest.json'
    $Manifest['updatedAt'] = (Get-Date).ToUniversalTime().ToString('o')
    $Manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $path -Encoding utf8
    return $path
}

function Test-InstalledMattPocockSkills {
    param(
        [Parameter(Mandatory)][string]$ProjectRoot,
        [Parameter(Mandatory)][string[]]$ExpectedSkills
    )

    $canonicalRoot = Join-Path $ProjectRoot '.agents/skills'
    $report = @()
    foreach ($name in $ExpectedSkills) {
        $skillMd = Join-MultiPath $canonicalRoot $name 'SKILL.md'
        $report += [pscustomobject]@{
            Skill     = $name
            Present   = Test-Path -LiteralPath $skillMd
            SkillPath = $skillMd
        }
    }
    return $report
}
