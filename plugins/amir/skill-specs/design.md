# design

## Command

`/design`

## Purpose

Produce technical architecture and design document `ai/design.md` driven by the architect agent from approved `project.md`, question inventory, and `ai/project-goal.md`. The architect leads; the human approves.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Project root | Implicit | Current amir project root |
| `ai/project-goal.md` | Yes | Approved product goal |
| `project.md` | Yes | Project summary |
| `ai/state/decisions.json` | Yes | Discovery and Material answers |

## Behavior

1. Act as **`2-architect`** per `core/naming-rules.md`; messages use architect header per `core/message-contract.md`.
2. Re-read goal, project summary, and decisions — no cached decisions per `core/no-drift-rules.md`.
3. Resolve remaining Material design questions via batch per `core/question-format.md` or apply logged defaults.
4. Draft `ai/design.md` from `templates/design.md.tmpl`: vision, architecture overview, components, interfaces, data model, risks, open items.
5. Include mermaid diagram block when architecture has multiple components.
6. Present design to human in plain language per `core/interaction-style.md`; highlight tradeoffs and challenge weak requirements.
7. On human approval, record decision in `ai/state/decisions.json`; set `ai/state/status.json` phase to `design` complete / `plan` ready via orchestrator `update-status`.
8. Append `design_complete` to `ai/state/activity.jsonl`.
9. Recommend `/design_qa` next.

## Core modules referenced

- Follow `core/naming-rules.md`
- Follow `core/workspace-rules.md`
- Follow `core/question-format.md`
- Follow `core/interaction-style.md`
- Follow `core/message-contract.md`
- Follow `core/no-drift-rules.md`
- Follow `core/honesty-rules.md`
- Follow `core/security-rules.md`

## State files read/written

| File | Access |
|------|--------|
| `ai/design.md` | Write |
| `ai/project-goal.md` | Read |
| `project.md` | Read |
| `ai/state/decisions.json` | Write |
| `ai/state/status.json` | Write (phase) |
| `ai/state/activity.jsonl` | Append |
| `ai/agents/2-architect/notes.md` | Write (working) |

## Outputs

- `ai/design.md` (approved)
- Design approval decision record
- Next-step recommendation (`/design_qa`)

## Failure/abort behavior

- Abort if `ai/project-goal.md` missing or unapproved.
- Stop on unresolved Blocking design questions (security model, data residency, etc.).
- Do not write tasks to `tasks.json` — design only.
- If human rejects design, iterate; do not mark phase complete.
