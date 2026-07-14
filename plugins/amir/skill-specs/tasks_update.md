# tasks_update

## Command

`/tasks_update`

## Purpose

Reconcile reported task or scope changes through state tools and regenerate task views.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Project root | Implicit | Current amir project root |
| Change report | Yes | Human or agent report of task status, fields, or scope changes |
| Writer identity | Yes | `--by 1-orchestrator` for JSON writes |

## Behavior

1. Read current `ai/state/tasks.json` and `ai/state/status.json` — establish baseline.
2. Parse change report: task id, field updates, proposed transitions, new tasks, cancellations.
3. Validate all changes against `schemas/tasks.schema.json` and transition rules in `tools/state.js`.
4. Apply status changes only via `node tools/state.js <root> transition --task <id> --to <status> --by <agent> [--note ...] [--qa-report ...] [--checkpoint-tag ...]`.
5. Apply non-status field updates via `node tools/state.js <root> set-task-field --task <id> --field <name> --value <value> --by 1-orchestrator`.
6. Update `ai/state/status.json` if `current_task` or phase changes: `update-status --by 1-orchestrator`.
7. Record Material scope changes in `ai/state/decisions.json` when acceptance criteria shift per `core/no-drift-rules.md`.
8. Run `node tools/render.js <root> tasks` and optionally `status`.
9. Append `tasks_update` to activity with changed task ids.
10. Present diff summary per `core/message-contract.md`.

## Core modules referenced

- Follow `core/workspace-rules.md`
- Follow `core/no-drift-rules.md`
- Follow `core/naming-rules.md`
- Follow `core/message-contract.md`
- Follow `core/qa-loop.md`
- Follow `core/honesty-rules.md`

## State files read/written

| File | Access |
|------|--------|
| `ai/state/tasks.json` | Write (via state tools) |
| `ai/state/status.json` | Write |
| `ai/state/decisions.json` | Write (if scope changed) |
| `ai/state/activity.jsonl` | Append |
| `ai/views/tasks.md` | Write (via render) |
| `ai/views/status.md` | Write (optional via render) |

## Outputs

- Updated `tasks.json` and related status fields
- Regenerated task board view
- Change diff summary in chat

## Failure/abort behavior

- Reject illegal transitions with tool error message — do not hand-edit JSON.
- Reject worker/verifier attempts to set `complete` or unauthorized `qa_passed`.
- Abort if change report lacks task id or approval for `cancelled`/`blocked`.
- On validation failure, leave prior state untouched.
