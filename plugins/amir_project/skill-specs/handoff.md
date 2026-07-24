# handoff

## Command

`/handoff`

## Purpose

Generate a structured pause handoff from template so a fresh orchestrator instance can resume without relying on chat history.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Project root | Implicit | Current amir project root |
| Pausing agent | Implicit | Usually `1-orchestrator` |
| Reason | Optional | Why pausing (context budget, human request, end of session) |

## Behavior

1. Read current `.ai/state/status.json`, `tasks.json`, and active task QA artifacts.
2. Build handoff block per `core/context-engineering.md` structure (≤10 lines in snippet + extended detail in file).
3. Write `.ai/agents/1-orchestrator/handoff.md` with: last VERIFIED state, open NEED items, next action, cycle counts, failing criteria ids if any.
4. Mirror concise snippet into `.ai/agents/1-orchestrator/notes.md` under `## Handoff snippet`.
5. Update `.ai/state/status.json` via `node tools/state.js <root> update-status --by 1-orchestrator` with `paused: true` and `resume_token` (uuid or timestamp slug).
6. Append `context_handoff` event to `.ai/state/activity.jsonl` per `core/budget-rules.md`.
7. Present human summary per `core/message-contract.md` with resume instructions (`/resume_build`).
8. Do not compact or delete evidence files during handoff.

## Core modules referenced

- Follow `core/context-engineering.md`
- Follow `core/workspace-rules.md`
- Follow `core/message-contract.md`
- Follow `core/budget-rules.md`
- Follow `core/no-drift-rules.md`
- Follow `core/honesty-rules.md`

## State files read/written

| File | Access |
|------|--------|
| `.ai/agents/1-orchestrator/handoff.md` | Write |
| `.ai/agents/1-orchestrator/notes.md` | Write (snippet) |
| `.ai/state/status.json` | Write (paused, resume_token) |
| `.ai/state/tasks.json` | Read |
| `.ai/state/activity.jsonl` | Append |

## Outputs

- `handoff.md` file in orchestrator workspace
- Updated `status.json` pause fields
- Human-readable handoff summary in chat

## Failure/abort behavior

- Abort if state files unreadable; do not hand off from ASSUMED state — label gaps INFERRED.
- Do not claim handoff complete without writing files and status update.
- If pause mid-fix with failing criteria, include ids explicitly; never omit open BLOCKED items.
