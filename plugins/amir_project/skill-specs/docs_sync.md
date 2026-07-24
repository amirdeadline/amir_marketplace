# docs_sync

## Command

`/docs_sync`

## Purpose

Detect drift between documentation and actual behavior; produce a fix list and apply doc updates only with human approval.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Project root | Implicit | Current amir project root |
| Doc scope | Optional | `project.md`, `ai/design.md`, README, API docs, etc. |
| Behavior sources | Implicit | `verify.sh`, tests, QA reports, codebase |

## Behavior

1. Inventory authoritative docs: `project.md`, `ai/project-goal.md`, `ai/design.md`, `ai/qa-objectives.md`, root README, generated views (read-only baseline).
2. Sample actual behavior: run `./verify.sh`, read recent `qa-report.md` files, spot-check APIs/CLI against docs.
3. Build **drift list** table: Doc location | Claimed behavior | Observed behavior | Severity | Proposed fix.
4. Classify items per `core/question-format.md` — doc wrong vs product wrong (product wrong → task or **DECISION REQUIRED**, not silent doc edit).
5. Present drift list to human per `core/interaction-style.md`.
6. Apply approved doc-only fixes; never change `ai/state/*.json` truth in this skill except logging decisions.
7. Record approval and applied fixes in `ai/state/decisions.json`.
8. Append `docs_sync` to activity with counts (drift found, fixed, deferred).
9. If product drift detected, recommend new task in `tasks.json` via `/tasks_update` or `/plan` amendment with approval.

## Core modules referenced

- Follow `core/no-drift-rules.md`
- Follow `core/question-format.md`
- Follow `core/interaction-style.md`
- Follow `core/message-contract.md`
- Follow `core/honesty-rules.md`
- Follow `core/qa-loop.md`

## State files read/written

| File | Access |
|------|--------|
| `project.md` | Read/Write (approved fixes) |
| `ai/project-goal.md` | Read (propose changes via decision only) |
| `ai/design.md` | Read/Write (approved fixes) |
| `ai/qa-objectives.md` | Read/Write (approved fixes) |
| `ai/state/decisions.json` | Write |
| `ai/state/activity.jsonl` | Append |
| QA reports / codebase | Read |

## Outputs

- Drift list table
- Applied doc patches (if approved)
- Deferred items with recommended follow-up tasks

## Failure/abort behavior

- Abort doc edits that would falsify known failing behavior — report product fix needed instead.
- Do not edit `ai/views/*.md` by hand; regenerate via render when JSON-driven.
- Stop if `./verify.sh` BLOCKED; document BLOCKED in drift list.
- No approval → no writes beyond activity log of pending drift.
