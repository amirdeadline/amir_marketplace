# resume_build

## Command

`/resume_build`

## Purpose

Safely resume an interrupted build: diagnose health, repair or flag issues, consume handoff context, regenerate orchestrator prompt, and continue the next orchestrator action.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Project root | Implicit | Current amir project root |
| Handoff artifacts | Optional | `ai/agents/1-orchestrator/notes.md`, `handoff.md`, `ai/state/status.json` resume fields |

## Behavior

1. Run `node tools/doctor.js <root>` first; present CRITICAL/HIGH findings table.
2. Auto-repair safe items only: regenerate stale views via `node tools/render.js <root> all`; run `node tools/activity.js <root> heartbeat-check`.
3. Flag non-repairable findings for human (illegal status, secrets, budget overrun, missing QA reports).
4. Read handoff: `ai/agents/1-orchestrator/handoff.md` or handoff snippet in `notes.md` per `core/context-engineering.md`.
5. Read `ai/state/status.json` (`current_task`, `phase`, `resume_token`, pending approvals).
6. Re-read JSON truth per `core/no-drift-rules.md` — no cached decisions from prior chat.
7. Regenerate orchestrator `prompt.md` from current state + templates; trim stale chat context.
8. Determine **next action**: continue `in_progress` task, resume fix loop, start next `pending` task, or escalate `blocked`.
9. If `status.json` indicates `paused`, clear pause only after human ACK or valid `resume_token`.
10. Append `resume_build` to activity with doctor summary and next action id.
11. Invoke `/build_goal` continuation or single-task step per status; message per `core/message-contract.md`.

## Core modules referenced

- Follow `core/context-engineering.md`
- Follow `core/no-drift-rules.md`
- Follow `core/workspace-rules.md`
- Follow `core/message-contract.md`
- Follow `core/honesty-rules.md`
- Follow `core/qa-loop.md`
- Follow `core/budget-rules.md`

## State files read/written

| File | Access |
|------|--------|
| `ai/state/status.json` | Read/Write (clear pause, set current_task) |
| `ai/state/tasks.json` | Read |
| `ai/state/agents.json` | Read/Write (stale repair) |
| `ai/state/activity.jsonl` | Append |
| `ai/views/*.md` | Write (via render) |
| `ai/agents/1-orchestrator/prompt.md` | Write (regenerate) |
| `ai/agents/1-orchestrator/notes.md` | Read |
| `ai/agents/1-orchestrator/handoff.md` | Read |

## Outputs

- Doctor findings table (pre-resume)
- Repaired flags list (views, heartbeats)
- Regenerated orchestrator prompt
- Explicit next action started or queued

## Failure/abort behavior

- Do not resume if CRITICAL doctor findings unresolved (secrets, illegal status) without human override recorded in decisions.
- Abort if handoff contradicts JSON truth — JSON wins; emit **PROBLEM**.
- Do not auto-transition tasks; use `node tools/state.js transition` with validation.
- If no resumable task and all complete, report done; recommend `/milestone_retro` or `/docs_sync`.
