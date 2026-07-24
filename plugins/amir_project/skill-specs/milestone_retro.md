# milestone_retro

## Command

`/milestone_retro`

## Purpose

Aggregate reflections at a milestone into durable decisions, risks, and prompt-template improvements for subsequent phases.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Project root | Implicit | Current amir project root |
| Milestone id | Optional | Phase name, task range, or tag |
| Reflection sources | Implicit | QA reports, activity tail, agent notes, human feedback |

## Behavior

1. Define milestone boundary (last N complete tasks, phase end, or human-specified range).
2. Collect evidence: `ai/state/activity.jsonl` filtered events, completed task `qa-report.md` paths, orchestrator/architect notes.
3. Synthesize reflections: what worked, what failed, budget/cycle outliers, drift events, two-strike incidents per `core/budget-rules.md`.
4. Produce **decisions** candidates → append to `ai/state/decisions.json` after human approval (process changes, defaults, scope adjustments).
5. Produce **risks** candidates → append to `ai/state/risks.json` with severity and mitigation.
6. Propose **prompt template** tweaks (file paths in `templates/` only — do not paste full core rules); record as decisions with template version note.
7. Present retro summary per `core/interaction-style.md`; obtain human approval before writing JSON.
8. Append `milestone_retro` to activity with milestone id and counts.
9. Update `ai/state/status.json` risks_summary if material risks added.

## Core modules referenced

- Follow `core/interaction-style.md`
- Follow `core/message-contract.md`
- Follow `core/budget-rules.md`
- Follow `core/no-drift-rules.md`
- Follow `core/qa-loop.md`
- Follow `core/honesty-rules.md`
- Follow `core/workspace-rules.md`

## State files read/written

| File | Access |
|------|--------|
| `ai/state/decisions.json` | Write (approved) |
| `ai/state/risks.json` | Write (approved) |
| `ai/state/status.json` | Write (risks_summary) |
| `ai/state/activity.jsonl` | Append / Read |
| `ai/state/tasks.json` | Read |
| `ai/agents/**/qa-report.md` | Read |
| `ai/agents/**/notes.md` | Read |

## Outputs

- Retro summary document (optional `ai/agents/1-orchestrator/logs/retro-<milestone>.md`)
- New/updated decisions and risks in JSON
- Template change tickets as decision records

## Failure/abort behavior

- Do not write decisions/risks without human approval.
- Abort if milestone has zero complete tasks and no human-defined boundary.
- Do not restate `core/*` rule text into retro — reference paths only.
- Label unverified reflections INFERRED per `core/honesty-rules.md`.
