# security_scan

## Command

`/security_scan`

## Purpose

Run secrets scanning and host-native security audit tools; triage findings into `ai/state/risks.json` via `4-security` review.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Project root | Implicit | Current amir project root |
| Scan scope | Optional | Default: project root + `ai/agents/` |
| Host audit tool | Discovered | From `adapters/<host>/capabilities.md` or host docs |

## Behavior

1. Act as **`4-security`** per `core/naming-rules.md`.
2. Run `node tools/secrets_scan.js <scope>` (or documented wrapper); archive raw results to `ai/agents/4-security/logs/secrets_scan-<timestamp>.json`.
3. Discover and run **native audit tool** if host provides one (dependency audit, SAST, etc.); if unavailable, state degrade per `core/honesty-rules.md` and `adapters/<host>/capabilities.md`.
4. Triage each finding: false positive, accepted risk, must-fix — per `core/security-rules.md`.
5. Write triaged items to `ai/state/risks.json` with id, severity, source, mitigation, status.
6. Update `ai/state/status.json` `risks_summary` via orchestrator if material.
7. Append `security_scan` to activity with counts by severity.
8. Present summary table to human; **FAIL** gate if CRITICAL unmitigated secrets in tracked files.
9. Recommend remediation tasks or `/git_commit` block until clean per `core/security-rules.md`.

## Core modules referenced

- Follow `core/security-rules.md`
- Follow `core/naming-rules.md`
- Follow `core/workspace-rules.md`
- Follow `core/message-contract.md`
- Follow `core/honesty-rules.md`
- Follow `core/qa-loop.md`

## State files read/written

| File | Access |
|------|--------|
| `ai/state/risks.json` | Write |
| `ai/state/status.json` | Write (risks_summary) |
| `ai/state/activity.jsonl` | Append |
| `ai/agents/4-security/logs/*` | Write |
| `ai/agents/4-security/notes.md` | Write |

## Outputs

- Secrets scan report (archived)
- Native audit output (if run)
- Updated `risks.json` entries
- Human-facing triage summary

## Failure/abort behavior

- Abort commit-related workflows if CRITICAL secrets found in tracked paths until removed/rotated.
- Do not copy secret values into chat or notes — reference path:line only.
- If scan tool missing, report PROBLEM and list manual steps; do not claim clean.
- False positives require human approval logged in `decisions.json` before dismissing.
