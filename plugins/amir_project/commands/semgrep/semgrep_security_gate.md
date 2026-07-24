---
description: Evaluate scan results against the project's block_on policy (advisory until approved)
---

# /amir:semgrep_security_gate

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.semgrep.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Policy source

Read `project_tools.semgrep.policy`. Defaults when absent: `block_on: [critical, high]`, scan changed files before commit. CRITICAL RULE: the gate is ADVISORY until the project has explicitly approved enforcement (approval recorded in the manifest / project notes). Without recorded approval, report violations but do not block or claim to block.

## Steps

1. Obtain a current result set: prefer a fresh `/amir:semgrep_scan_changed` run (or full scan if requested). Do not gate on stale results — if the newest file in `.amir/state/semgrep/` predates the latest source change, rescan.
2. Parse the JSON findings; bucket by severity.
3. Apply `block_on`: any finding at a listed severity is a gate violation. List each violating finding with file:line, rule id, and a one-line risk statement.
4. Verdict:
   - Enforcement approved + violations → verdict FAIL: instruct the caller not to commit/merge until resolved or explicitly waived by the user (record waivers in `.amir/state/semgrep/waivers.md` with reason and date).
   - Enforcement not approved → verdict ADVISORY with the same list, plus a note on how to approve enforcement via `/amir:configure_project`.
   - No violations → verdict PASS, phrased as "no findings at gated severities from the rulesets used" — never "code is secure".
5. Persist the gate decision (timestamp, scan file used, verdict, waivers applied) to `.amir/state/semgrep/gate-log.jsonl` (append, never rewrite history).
