#Requires -Version 5.1
$packageRoot = Split-Path -Parent $PSScriptRoot
$scriptDir = Join-Path $packageRoot 'scripts'
. (Join-Path $scriptDir 'lib/MattPocockInstall.Common.ps1')
. (Join-Path $scriptDir 'lib/MattPocockInstall.Engine.ps1')

Describe 'Matt Pocock installer unit tests' {
    It 'Resolves project root from explicit path' {
        $root = Resolve-ProjectRoot -ExplicitRoot $packageRoot
        $root | Should Be (Resolve-Path $packageRoot).Path
    }

    It 'Lists 13 selected skills in config' {
        $cfg = Join-Path $packageRoot 'config/selected-skills.json'
        $skills = Get-SelectedSkillList -ConfigPath $cfg
        $skills.Count | Should Be 13
    }

    It 'Discovers upstream skills (network)' {
        $tmp = Join-Path $TestDrive 'discover'
        New-Item -ItemType Directory -Force -Path $tmp | Out-Null
        git -C $tmp init -q 2>$null
        $state = Get-MattPocockInstallStateDir -ProjectRoot $tmp
        New-Item -ItemType Directory -Force -Path $state | Out-Null
        $log = Join-Path $state 'test.log'
        Set-Content -Path $log -Value ''
        $names = Get-DiscoveredSkillNamesFromCli -ProjectRoot $tmp -LogPath $log
        ($names.Count -gt 30) | Should Be $true
        ('research' -in $names) | Should Be $true
        ('grill-with-docs' -in $names) | Should Be $true
    }
}

Describe 'Matt Pocock installer integration' {
    It 'Bootstraps and installs selected skills in empty project' {
        $empty = Join-Path $TestDrive 'empty-project'
        New-Item -ItemType Directory -Force -Path $empty | Out-Null
        git -C $empty init -q

        $bootstrap = Join-Path $packageRoot 'scripts/bootstrap.ps1'
        & powershell -NoProfile -ExecutionPolicy Bypass -File $bootstrap -ProjectRoot $empty | Out-Null
        $LASTEXITCODE | Should Be 0

        (Test-Path (Join-Path $empty '.agents/skills/amir_install_mattpocock/SKILL.md')) | Should Be $true

        $install = Join-Path $packageRoot 'scripts/install-mattpocock.ps1'
        & powershell -NoProfile -ExecutionPolicy Bypass -File $install -Mode Selected -ProjectRoot $empty | Out-Null
        $LASTEXITCODE | Should Be 0

        $cfg = Get-SelectedSkillList -ConfigPath (Join-Path $packageRoot 'config/selected-skills.json')
        $verify = Test-InstalledMattPocockSkills -ProjectRoot $empty -ExpectedSkills $cfg
        (@($verify | Where-Object { -not $_.Present }).Count -eq 0) | Should Be $true
    }

    It 'Repeated selected install remains idempotent' {
        $empty = Join-Path $TestDrive 'repeat-project'
        New-Item -ItemType Directory -Force -Path $empty | Out-Null
        git -C $empty init -q
        $install = Join-Path $packageRoot 'scripts/install-mattpocock.ps1'
        & powershell -NoProfile -ExecutionPolicy Bypass -File $install -Mode Selected -ProjectRoot $empty | Out-Null
        & powershell -NoProfile -ExecutionPolicy Bypass -File $install -Mode Selected -ProjectRoot $empty | Out-Null
        $LASTEXITCODE | Should Be 0
        $allSkills = Get-ChildItem (Join-Path $empty '.agents/skills') -Directory
        (@($allSkills | Where-Object { $_.Name -eq 'research' }).Count -eq 1) | Should Be $true
    }

    It 'Selected install after All does not remove extra skills' {
        $proj = Join-Path $TestDrive 'all-then-selected'
        New-Item -ItemType Directory -Force -Path $proj | Out-Null
        git -C $proj init -q
        $install = Join-Path $packageRoot 'scripts/install-mattpocock.ps1'
        & powershell -NoProfile -ExecutionPolicy Bypass -File $install -Mode All -ProjectRoot $proj -SkipBootstrap | Out-Null
        $before = (Get-ChildItem (Join-Path $proj '.agents/skills') -Directory).Count
        & powershell -NoProfile -ExecutionPolicy Bypass -File $install -Mode Selected -ProjectRoot $proj -SkipBootstrap | Out-Null
        $after = (Get-ChildItem (Join-Path $proj '.agents/skills') -Directory).Count
        ($after -ge $before) | Should Be $true
        (Test-Path (Join-Path $proj '.agents/skills/ask-matt/SKILL.md')) | Should Be $true
    }

    It 'Handles path with spaces' {
        $spaced = Join-Path $TestDrive 'space project'
        New-Item -ItemType Directory -Force -Path $spaced | Out-Null
        git -C $spaced init -q
        $install = Join-Path $packageRoot 'scripts/install-mattpocock.ps1'
        & powershell -NoProfile -ExecutionPolicy Bypass -File $install -Mode Selected -ProjectRoot $spaced | Out-Null
        $LASTEXITCODE | Should Be 0
    }
}
