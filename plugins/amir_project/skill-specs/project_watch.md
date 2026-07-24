# project_watch

## Command

`/project_watch`

## Purpose

Live operational snapshot: last N activity events, agents table with heartbeat/stale flags, and in-progress task linkage.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Project root | Implicit | Current amir project root |
| `N` | Optional | Activity lines to show (default 20) |

## Behavior

1. Read last `N` events from `ai/state/activity.jsonl` (tail, chronological).
2. Read `ai/state/agents.json` for agent registry.
3. Run `node tools/activity.js <root> heartbeat-check` to mark stale agents and obtain stale id list.
4. Cross-reference `in_progress` tasks in `ai/state/tasks.json` with `dev-<id>` and `qa-<id>` agent rows.
5. Present compact table: agent id, role, state, task_id, last heartbeat, stale flag — per `core/message-contract.md`.
6. Summarize recent actions (transitions, fix cycles, drift checks, discovery batches).
7. Read-only except heartbeat-check side effect on `agents.json` state field (stale marking).

## Core modules referenced

- Follow `core/workspace-rules.md`
- Follow `core/naming-rules.md`
- Follow `core/message-contract.md`
- Follow `core/budget-rules.md` (activity event types)

## State files read/written

| File | Access |
|------|--------|
| `ai/state/activity.jsonl` | Read |
| `ai/state/agents.json` | Read; Write (stale flags via heartbeat-check) |
| `ai/state/tasks.json` | Read |
| `ai/state/status.json` | Read |

## Outputs

- Activity tail summary (last N events)
- Agents table with stale flags
- Warnings for in_progress tasks with stale workers/QA

## Failure/abort behavior

- If activity log missing, show agents table only with **NEED** telemetry.
- If heartbeat-check fails, report error; do not guess staleness.
- Do not transition tasks or spawn agents from this command.
