---
description: Run a full local Semgrep scan of the project and persist findings
argument-hint: [ruleset, default p/default]
---

# /amir:semgrep_scan

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.semgrep.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Verify `semgrep` resolves (or use the docker form); otherwise stop and point to `/amir:semgrep_setup`.
2. Run a LOCAL scan from the project root (local by default — never `semgrep ci` or `--pro` without explicit user opt-in, since those interact with the Semgrep platform):

```powershell
$env:PYTHONUTF8 = '1'
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
semgrep scan --config p/default --json --output ".amir/state/semgrep/scan-$stamp.json" .
```

   Use the ruleset from `$ARGUMENTS` if given (e.g. `p/security-audit`, `p/owasp-top-ten`, or a local `semgrep-rules/` dir). Registry rulesets (`p/...`) require network to fetch rules — that is rule download only, not code upload.
3. Preserve findings: never overwrite previous result files in `.amir/state/semgrep/`; each run gets a new timestamped file.
4. Summarize: total findings by severity (critical/high/medium/low), top rules firing, files most affected. Include file:line for every critical/high finding.
5. Honesty rules: a clean scan means "these rulesets found nothing", not "secure" — say so. If files were skipped (size, parse errors), list them from the JSON `paths.skipped` section.
6. Do not modify any source in this command; fixes go through `/amir:semgrep_fix`.
