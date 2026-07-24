# agent_reset

## Command

`/agent_reset {agent-id}`

## Purpose

Archive an agent workspace and respawn a fresh prompt/notes shell without deleting history. Mark agent reset in registry for audit.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `{agent-id}` | Yes | Canonical agent id per `core/naming-rules.md` |
| Project root | Implicit | Current amir project root |
| Reason | Optional | Stale context, corrupted notes, role respawn |

## Behavior

1. Validate `{agent-id}` exists in `ai/state/agents.json`.
2. Confirm agent is not mid-critical transition without orchestrator approval (check task `in_progress` linkage).
3. **Archive** workspace: move `ai/agents/<agent-id>/` to `ai/agents/<agent-id>/archive/<timestamp>/` or copy-all-then-truncate — **never delete** workspace files.
4. Recreate fresh `ai/agents/<agent-id>/` with empty `notes.md` and regenerated `prompt.md` per role (same rules as `/build_agents`).
5. Preserve registry row; set `state: active`, clear `last_heartbeat_ts`, update `task_id` if respawning for new assignment.
6. Append `agent_reset` to `ai/state/activity.jsonl` with agent id, archive path, reason.
7. Log reset decision to `ai/state/decisions.json` if human requested or task-scoped respawn.
8. If resetting `qa-<task-id>` or `dev-<task-id>` during active task, coordinate with orchestrator — may require task note `agent_reset` without status change.
9. Message per `core/message-contract.md` with archive location.

## Core modules referenced

- Follow `core/naming-rules.md`
- Follow `core/workspace-rules.md`
- Follow `core/context-engineering.md`
- Follow `core/message-contract.md`
- Follow `core/honesty-rules.md`

## State files read/written

| File | Access |
|------|--------|
| `ai/agents/<agent-id>/**` | Archive + recreate |
| `ai/state/agents.json` | Write (state, heartbeat, task_id) |
| `ai/state/decisions.json` | Write (optional) |
| `ai/state/activity.jsonl` | Append |
| `ai/state/tasks.json` | Read |

## Outputs

- Archived workspace at timestamped path
- Fresh `prompt.md` and `notes.md`
- Updated agent registry row
- Activity and decision audit entries

## Failure/abort behavior

- Abort if `{agent-id}` not in registry — run `/design_agents` first.
- Never delete workspace directories or QA evidence — archive only.
- Abort if human denies reset on active `in_progress` task without orchestrator note.
- Do not reset `1-orchestrator` during unpaused build without `/handoff` first unless emergency with decision record.
