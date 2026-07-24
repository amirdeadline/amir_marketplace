---
description: Fix a Semgrep finding with source verification before and tests after
argument-hint: <rule id or finding reference> [--all-of-rule]
---

# /amir:semgrep_fix

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.semgrep.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Hard rules

- Source-level verification BEFORE any automatic fix: read the code, confirm the finding is real and the fix preserves behavior. Never apply Semgrep autofix output blindly.
- Tests MUST run after fixes. No passing test run → report "fix applied, unverified", never "fixed".
- One rule / one finding at a time unless the user passes `--all-of-rule` and confirms the batch.

## Steps

1. Identify the finding(s) from `$ARGUMENTS` against the latest scan JSON in `.amir/state/semgrep/`.
2. For each: run the analysis of `/amir:semgrep_explain` (read source, confirm exploitability or at least rule correctness). Skip and report anything assessed as a false positive — offer a narrow `# nosemgrep: <rule-id>` suppression with justification instead.
3. Apply the minimal fix. If the rule ships an autofix (`semgrep scan --config <rule> --autofix --dryrun` shows the patch), review the dry-run diff first and only then apply; hand-write the fix when the autofix is too coarse.
4. Re-scan just the touched files with the same rule to confirm the finding is gone:

```powershell
semgrep scan --config <ruleset-or-rule> <changed files> --json
```

5. Run the project's test suite (or nearest relevant subset) and report real results. On failure, revert or fix forward with user agreement.
6. Record the remediation (finding id, fix summary, rescan result, test result) by appending to `.amir/state/semgrep/remediations.jsonl`. Preserve the original finding files untouched.
