# project_status

## Command

`/project_status`

## Purpose

Render and present the project status dashboard. Read-only visibility into phase, progress, pending approvals, and current task.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Project root | Implicit | Current amir project root |

## Behavior

1. Run `node tools/render.js <root> status` to regenerate `ai/views/status.md` from JSON truth.
2. Read `ai/state/status.json` and `ai/state/tasks.json` for structured fields.
3. Present dashboard to human: phase, current task, progress block, pending approvals, risks summary — per `core/message-contract.md` (short lead + offer `/details` for full view).
4. Do not mutate any state files or workspaces.
5. If render output indicates missing init, recommend `/project_create` or `/project_import`.

## Core modules referenced

- Follow `core/workspace-rules.md`
- Follow `core/message-contract.md`
- Follow `core/interaction-style.md`

## State files read/written

| File | Access |
|------|--------|
| `ai/state/status.json` | Read |
| `ai/state/tasks.json` | Read |
| `ai/views/status.md` | Write (via render only) |

## Outputs

- Regenerated `ai/views/status.md`
- Human-readable status summary in chat
- Optional pointer to `ai/views/status.md` for full dashboard

## Failure/abort behavior

- If project root lacks `ai/state/status.json`, emit **NEED** project init; do not fabricate status.
- If `node tools/render.js` fails, report error verbatim; do not hand-edit views.
- Read-only: abort any incidental write attempt.
