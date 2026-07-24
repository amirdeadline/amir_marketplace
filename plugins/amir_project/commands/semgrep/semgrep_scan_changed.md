---
description: Semgrep-scan only files changed in the working tree (or vs a base ref)
argument-hint: [base ref, default HEAD]
---

# /amir:semgrep_scan_changed

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.semgrep.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Verify `semgrep` resolves; otherwise point to `/amir:semgrep_setup`.
2. Collect changed files (default: uncommitted changes; if `$ARGUMENTS` names a base ref, diff against it):

```powershell
$files = git diff --name-only --diff-filter=ACMR HEAD
```

   If `$ARGUMENTS` gives a ref: `git diff --name-only --diff-filter=ACMR <ref>...HEAD`. Include untracked source files (`git ls-files --others --exclude-standard`) when scanning the working tree.
3. If the list is empty, report "no changed files to scan" and stop — do not scan the whole repo silently.
4. Scan just those files, persisting results:

```powershell
$env:PYTHONUTF8 = '1'
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
semgrep scan --config p/default --json --output ".amir/state/semgrep/changed-$stamp.json" @files
```

5. Report findings by severity with file:line. Note the limitation honestly: scanning only changed files can miss cross-file issues (taint flows through unchanged files); recommend a periodic full `/amir:semgrep_scan`.
6. If the manifest policy sets `scan_changed_files: true`, remind the caller this command is the one hooks/workflows should invoke before commits.
