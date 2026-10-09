# Link amir_system skills into the user skill folders of Claude Code and Cursor.
# Uses directory junctions (one real copy, no drift). Never overwrites or deletes an existing folder.
#   powershell -File scripts\install-user-skills.ps1                  # create missing links
#   powershell -File scripts\install-user-skills.ps1 -Verify          # report only
#   powershell -File scripts\install-user-skills.ps1 -Skills amir_critical,amir_handoff
param(
  [string[]]$Skills = @("amir_prisma_sdwan", "amir_prisma_sdwan_sme", "amir_prisma_sdwan_training", "amir_official_doc",
                      "amir_md_artifact", "amir_md_to_words"),
  [switch]$Verify
)
$ErrorActionPreference = "Stop"

$SkillsRoot = Join-Path (Split-Path -Parent $PSScriptRoot) "plugins\amir_system\skills"
$UserRoots = @(
  (Join-Path $env:USERPROFILE ".claude\skills"),
  (Join-Path $env:USERPROFILE ".cursor\skills")
)
$problems = 0

function Get-LinkTarget([string]$Path) {
  $item = Get-Item -LiteralPath $Path -Force
  if (-not ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) { return $null }
  return ([string](@($item.Target)[0])).TrimEnd('\')
}

foreach ($skill in $Skills) {
  $source = Join-Path $SkillsRoot $skill
  if (-not (Test-Path -LiteralPath (Join-Path $source "SKILL.md"))) {
    Write-Warning "NO SKILL  $source has no SKILL.md"
    $problems++
    continue
  }
  foreach ($root in $UserRoots) {
    $link = Join-Path $root $skill
    if (Test-Path -LiteralPath $link) {
      $target = Get-LinkTarget $link
      if ($target -and ($target -ieq $source.TrimEnd('\'))) {
        Write-Output "OK        $link -> $source"
      } else {
        Write-Warning "CONFLICT  $link exists and is not a junction to $source; left untouched"
        $problems++
      }
      continue
    }
    if ($Verify) {
      Write-Warning "MISSING   $link"
      $problems++
      continue
    }
    New-Item -ItemType Directory -Force -Path $root | Out-Null
    New-Item -ItemType Junction -Path $link -Target $source | Out-Null
    Write-Output "CREATED   $link -> $source"
  }
}

if ($problems -gt 0) { Write-Output "$problems problem(s)"; exit 1 }
Write-Output "All links in place. Start a new Claude Code session or reload the Cursor window to pick up new skills."
exit 0
