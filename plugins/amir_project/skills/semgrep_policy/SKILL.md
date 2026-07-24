---
name: semgrep_policy
description: >-
  Semgrep policy for amir projects: local-first scanning, honest free-vs-account
  boundaries, severity gating, findings preservation, fix discipline.
---

# semgrep_policy

Semgrep provides static analysis (SAST), plus account-gated secrets validation and supply-chain analysis. In amir projects it is gated on `project_tools.semgrep.enabled` with `integration: guardian | mcp | both`.

## Product boundaries — state them honestly, always

- **semgrep CLI (`semgrep scan`)**: free, local, no account. Registry rulesets (`p/default`, `p/security-audit`, `p/owasp-top-ten`, `p/secrets`) are fetched over the network; code is scanned locally and not uploaded.
- **Semgrep Guardian** (https://github.com/semgrep/guardian): the official Claude Code plugin (MCP server + write-hooks). ACCOUNT REQUIRED (`semgrep login`); in Claude Code it uses Semgrep's hosted remote MCP, and findings flow through the Semgrep platform. Never install it without telling the user both facts.
- **`semgrep ci` / Semgrep Secrets / Semgrep Supply Chain**: platform products, account-gated; findings (not code) are sent to Semgrep's AppSec Platform. `--pro` engine features are opt-in only.
- Windows: native CLI support is beta (Python 3.10+, set `PYTHONUTF8=1`); docker (`semgrep/semgrep`) is the reliable fallback.

## Policy block (manifest, SPEC §8.3)

```yaml
project_tools:
  semgrep:
    enabled: true
    integration: mcp          # guardian | mcp | both
    policy:
      scan_changed_files: true
      scan_before_commit: true
      block_on: [critical, high]   # advisory until the project approves enforcement
      scan_secrets: true
      scan_dependencies: false     # honest default: full SCA needs an account
```

`block_on` is NOT enforced until project approval is recorded; until then gates report ADVISORY.

## Non-negotiable rules

1. A clean scan is never "secure" — it is "no findings from these rulesets on this date". Say it that way.
2. Findings are preserved in `.amir/state/semgrep/` (timestamped JSON, gate log, remediations, waivers), gitignored by default, never overwritten.
3. No automatic fix without source-level verification first, and no "fixed" claim without a rescan of the touched files AND a test run after.
4. False positives get narrow `# nosemgrep: <rule-id>` suppressions with a justification comment — never rule-wide disables to make output quiet.
5. Never silently upload proprietary code: local scans are the default; anything platform-bound (login, ci, Guardian, --pro) requires explicit user opt-in with the data flow stated.

## Fallbacks

CLI missing → docker image. Guardian unavailable/anonymous → local CLI scans still work; report the mode honestly. Registry unreachable → local rules dir if the project has one, else report "cannot scan", never fake a result.
