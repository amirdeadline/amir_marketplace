---
description: Report Semgrep CLI/MCP/Guardian state and findings summary for this project
---

# /amir:semgrep_status

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.semgrep.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Checks (report each separately)

1. Manifest: integration mode (guardian | mcp | both) and the configured policy block, including whether `block_on` gating has project approval.
2. CLI: `semgrep --version` (or docker fallback availability). Note Windows-beta status if running natively.
3. Login state: `semgrep whoami` if available in this version, else check `semgrep login --help` guidance; report logged-in vs anonymous. Anonymous = local OSS scans only; logged-in = platform features (ci, secrets, supply chain).
4. Guardian/MCP: is the Semgrep plugin/MCP registered and connected (`claude mcp list`, `/plugin` inventory).
5. Findings store: does `.amir/state/semgrep/` exist; how many stored scan result files; date of the latest; count of open findings by severity from the latest JSON.
6. Never equate "no findings" with "secure" — if the latest scan is clean, phrase it as "no findings from the rulesets used on that date".

Suggest `/amir:semgrep_setup` or `/amir:semgrep_validate` for anything failing.
