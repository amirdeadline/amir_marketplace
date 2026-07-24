---
description: Dependency/supply-chain scan - honest about what needs a Semgrep account
---

# /amir:semgrep_scan_dependencies

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.semgrep.enabled` is not `true`, stop and point to `/amir:configure_project`. Also check the policy flag `project_tools.semgrep.policy.scan_dependencies` and note if it is false.

## Honest capability statement (say this up front)

Semgrep's full dependency scanning is **Semgrep Supply Chain**, an account-gated platform product driven by `semgrep ci` after `semgrep login` — reachability-aware SCA findings are NOT part of the free local `semgrep scan`. Do not pretend otherwise.

## Steps

1. If the user has a Semgrep account and explicitly opts in to platform interaction: run `semgrep login` (browser flow, user completes it), then from the project root `semgrep ci` and report the Supply Chain findings it returns. Findings (not code) are sent to the Semgrep platform — state this before running.
2. Without an account (free/local path), provide the best local alternative and label it as such:
   - Ecosystem-native audits, e.g. `npm audit --json`, `pip-audit` (if installed), `cargo audit`, `dotnet list package --vulnerable` — run the ones matching this project's lockfiles.
   - Semgrep registry rules that flag known-bad usage patterns of libraries (`semgrep scan --config p/supply-chain` if the registry exposes it; if the ruleset does not exist or is empty for this ecosystem, report that plainly).
3. Persist whatever results were produced to `.amir/state/semgrep/deps-<timestamp>.json` (or `.txt` for non-JSON tools).
4. Summarize: vulnerable packages, advisory ids, fixed versions, and whether each result came from Semgrep Supply Chain (account) or a local fallback tool.
5. Never auto-upgrade dependencies here; propose upgrades and let the project's normal change process apply them (tests must run after any bump).
