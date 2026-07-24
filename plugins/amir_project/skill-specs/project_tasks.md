# project_tasks

## Command

`/project_tasks`

## Purpose

Render and present the task board view. Read-only visibility into active and finished tasks.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Project root | Implicit | Current amir project root |

## Behavior

1. Run `node tools/render.js <root> tasks` to regenerate `ai/views/tasks.md`.
2. Read `ai/state/tasks.json` for structured task records.
3. Present task board summary: active tasks by priority, current statuses, blocked items — per `core/message-contract.md`.
4. Highlight tasks in `qa_failed`, `blocked`, or `in_progress` with stale agent flags if doctor would flag them (optional cross-check read-only).
5. Do not mutate tasks or transition statuses.

## Core modules referenced

- Follow `core/workspace-rules.md`
- Follow `core/message-contract.md`
- Follow `core/naming-rules.md`

## State files read/written

| File | Access |
|------|--------|
| `ai/state/tasks.json` | Read |
| `ai/views/tasks.md` | Write (via render only) |

## Outputs

- Regenerated `ai/views/tasks.md`
- Human-readable task board summary

## Failure/abort behavior

- If `ai/state/tasks.json` missing, recommend init; do not invent tasks.
- If render fails, stop and report error.
- Read-only: never call `node tools/state.js transition`.
