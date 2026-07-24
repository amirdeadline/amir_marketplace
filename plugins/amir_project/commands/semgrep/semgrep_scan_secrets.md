---
description: Scan for hardcoded secrets - honest about free rules vs Semgrep Secrets
---

# /amir:semgrep_scan_secrets

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.semgrep.enabled` is not `true`, stop and point to `/amir:configure_project`. Check policy flag `policy.scan_secrets`.

## Honest capability statement

**Semgrep Secrets** (validated secrets detection — it checks whether a leaked credential is live) is an account-gated platform product via `semgrep ci`. The free local path is registry regex/entropy rulesets, which find PATTERNS of secrets but do not validate them and have more false positives/negatives. State which path is in use.

## Steps

1. Free/local path (default):

```powershell
$env:PYTHONUTF8 = '1'
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
semgrep scan --config p/secrets --json --output ".amir/state/semgrep/secrets-$stamp.json" .
```

   (If the `p/secrets` registry ruleset is unavailable, use `p/gitleaks` or `p/security-audit` and report the substitution.)
2. Account path (only with explicit user opt-in and login): `semgrep ci` and report validated-secret findings; findings go to the Semgrep platform.
3. CRITICAL handling: if a probable live secret is found, treat it as an incident — report file:line and secret TYPE only. NEVER print the secret value into chat, logs, or result summaries. The stored JSON already contains the matched text; keep `.amir/state/semgrep/` gitignored and say so.
4. Remediation guidance per finding: remove from source, move to the project's documented secret store (`%USERPROFILE%\.amir\secrets\` pattern or env vars), rotate the credential, and check git history (`git log -S` on the file) — rotation is required if it was ever committed.
5. Clean result phrasing: "no secret patterns matched by ruleset X on <date>" — never "no secrets in the repo".
