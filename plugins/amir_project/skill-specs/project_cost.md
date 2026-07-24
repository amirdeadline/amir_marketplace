# project_cost

## Command

`/project_cost`

## Purpose

Aggregate and present cost telemetry from activity events. All USD figures are estimates unless explicitly logged.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Project root | Implicit | Current amir project root |

## Behavior

1. Run `node tools/cost.js <root>` to produce the cost report markdown.
2. Present summary tables: project total, by task, by agent, by model, rising fix-cycle flags.
3. Label every USD value as **(est)** in chat per tool output disclaimer.
4. If `.ai/state/activity.jsonl` is empty, state no telemetry yet; suggest ensuring agents log via `node tools/activity.js append`.
5. Read-only — do not modify cost or activity files.

## Core modules referenced

- Follow `core/message-contract.md`
- Follow `core/budget-rules.md`
- Follow `core/honesty-rules.md`

## State files read/written

| File | Access |
|------|--------|
| `.ai/state/activity.jsonl` | Read |
| `.ai/state/tasks.json` | Read |
| `tools/pricing.json` | Read (via cost tool) |

## Outputs

- Cost report (stdout from `node tools/cost.js`)
- Chat summary with explicit estimate labeling
- Rising fix-cycle warnings when detected

## Failure/abort behavior

- If activity log missing, report zero data; do not estimate from chat length.
- If cost tool throws, report error; do not fabricate numbers.
- Read-only command.
