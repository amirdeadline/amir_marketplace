# project_cleanup

## Command

`/project_cleanup`

## Purpose

Safe workspace hygiene: verify version control, snapshot before changes, present a human-approved cleanup plan, execute only approved items, and log all actions. Never destroy authoritative amir state or checkpoint evidence.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Project root | Implicit | Current amir project root |
| Scope flags | Optional | Human may narrow to `.ai/agents/`, build artifacts, temp logs, etc. |
| Approval | Required | Explicit human approval of cleanup PLAN before execution |

## Behavior

1. Verify git repository (`git rev-parse --is-inside-work-tree`); if absent, offer `/git_setup` and stop until git exists or human waives with recorded decision.
2. Run `node tools/doctor.js <root>`; surface CRITICAL/HIGH findings before cleanup.
3. Create **pre-cleanup commit** (or stash with decision record): all tracked changes committed with message `chore: pre-cleanup snapshot` per host git workflow.
4. Scan candidates: orphan temp files, stale logs, duplicate drafts, empty dirs, unreferenced build output — **exclude protected paths** per `core/workspace-rules.md`.
5. Produce **PLAN** table: path, reason, risk tier, reversible (yes/no), requires human (yes/no). Present per `core/interaction-style.md`.
6. Wait for human approval; record approved item ids in `.ai/state/approvals.json` or `decisions.json`.
7. Execute **only** approved items; never delete:
   - `.ai/state/` (any file)
   - `.ai/project-goal.md`
   - checkpoint-tagged evidence (`qa-report.md`, alignment reviews, logs referenced by `tasks.json`)
   - `.git/`
8. Archive instead of delete when uncertain: move to `.ai/agents/1-orchestrator/archive/<timestamp>/`.
9. Append each action to `.ai/state/activity.jsonl` with event `cleanup` and details.
10. Regenerate views if state-adjacent files changed; re-run doctor if agents or tasks touched.

## Core modules referenced

- Follow `core/workspace-rules.md`
- Follow `core/interaction-style.md`
- Follow `core/message-contract.md`
- Follow `core/security-rules.md`
- Follow `core/honesty-rules.md`

## State files read/written

| File | Access |
|------|--------|
| `.ai/state/activity.jsonl` | Append |
| `.ai/state/decisions.json` | Write (waivers, approvals) |
| `.ai/state/approvals.json` | Write |
| `.ai/state/tasks.json` | Read (protect referenced evidence paths) |
| `.ai/agents/**` | Read; selective delete/archive per approved PLAN |
| Git history | Write (pre-cleanup commit) |

## Outputs

- Pre-cleanup git snapshot
- Human-approved PLAN (presented in chat and optionally saved to `.ai/agents/1-orchestrator/logs/cleanup-plan.md`)
- Executed cleanup log in `activity.jsonl`
- Post-cleanup doctor summary if requested

## Failure/abort behavior

- Abort without git and without recorded human waiver.
- Abort if human rejects PLAN; no file deletions.
- Never execute unapproved PLAN rows.
- Stop immediately if an operation would touch `.ai/state/` or `.ai/project-goal.md`; emit **PROBLEM**.
- On delete/archive error, stop remaining items, report partial completion, recommend `/rollback` if git commit was made.
