---
description: Validate the Semgrep integration end to end with a canary finding
---

# /amir:semgrep_validate

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.semgrep.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Validation matrix (run all; pass/fail per line)

1. CLI runs: `semgrep --version` exits 0 (native or docker form). Set `$env:PYTHONUTF8 = '1'` first on native Windows (beta support).
2. Rules fetch: `semgrep scan --config p/default --help`-level check is not enough — run a real tiny scan on one project file and confirm JSON output parses.
3. Canary: write a deliberately findable snippet to the scratch area (NOT the project tree), e.g. a file in the session scratchpad containing `password = "hunter2"`, scan it with `p/secrets` (or `p/default`), and confirm at least one finding fires. Delete the canary afterwards. A scanner that cannot find a planted finding is not healthy.
4. Findings store: `.amir/state/semgrep/` exists, is writable, and is gitignored (unless the manifest opts in to committing results).
5. Mode-specific: if integration includes `guardian`/`mcp`, confirm the Semgrep MCP is connected (`claude mcp list`) and that login state matches expectations (`guardian` requires a logged-in Semgrep account — report anonymous state as a failure for that mode, clearly labeled account-dependent).
6. Policy sanity: the manifest policy parses; `block_on` values are from {critical, high, medium, low}; enforcement approval state is recorded.

Verdict "healthy" only when every applicable check passes. Report exact failures with remedies. Never let a passing validation be phrased as a security guarantee.
