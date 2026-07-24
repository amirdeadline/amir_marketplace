# project_create

## Command

`/project_create {prompt}`

## Purpose

Bootstrap a new amir project from a human goal: create the project folder and workspace skeleton, run structured discovery, produce approved goal documents, and initialize JSON state.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `{prompt}` | Yes | Human goal text describing what to build |
| Project root | Implicit | Current working directory or path chosen during create |
| Host capabilities | Optional | Read `adapters/<host>/capabilities.md` when present for degrade paths |

## Behavior

1. Resolve project root and project name from `{prompt}` and host context; create project folder if needed.
2. Instantiate workspace skeleton from plugin `templates/` per `core/workspace-rules.md` (including `.ai/` tree, `verify.sh` from `templates/verify.sh.tmpl`, and agent workspace stubs).
3. Build a **question inventory** from `{prompt}`: list unknowns, ambiguities, and missing acceptance criteria.
4. Triage every inventory item per `core/question-format.md` (Blocking / Material / Minor).
5. Ask the human in batches per `core/question-format.md` and `core/interaction-style.md`; apply Minor defaults to `.ai/state/decisions.json` without asking.
6. After discovery resolves Blocking items and Material batches are answered (or defaulted with approval), draft `.ai/project-goal.md` from `templates/project-goal.md.tmpl` and root `project.md` (human-readable project summary).
7. Present goal documents for human approval; on approval, record decision in `.ai/state/decisions.json`.
8. Initialize state: `node tools/state.js <root> init`.
9. Append `project_create` event to `.ai/state/activity.jsonl` via `node tools/activity.js <root> append`.
10. Regenerate views: `node tools/render.js <root> all`.
11. Emit short status per `core/message-contract.md` with next recommended command (`/design`).

## Core modules referenced

- Follow `core/workspace-rules.md`
- Follow `core/question-format.md`
- Follow `core/interaction-style.md`
- Follow `core/message-contract.md`
- Follow `core/budget-rules.md` (discovery batch caps)
- Follow `core/honesty-rules.md`

## State files read/written

| File | Access |
|------|--------|
| `.ai/project-goal.md` | Write (after approval) |
| `project.md` | Write |
| `.ai/state/tasks.json` | Write (init defaults) |
| `.ai/state/status.json` | Write (init; set phase `discovery` → `design`) |
| `.ai/state/agents.json` | Write (init) |
| `.ai/state/decisions.json` | Write (Minor defaults, approvals) |
| `.ai/state/risks.json` | Write (init) |
| `.ai/state/approvals.json` | Write (init) |
| `.ai/state/activity.jsonl` | Append |
| `.ai/views/*.md` | Write (via render) |
| `verify.sh` | Write (from template) |

## Outputs

- New project folder with full `.ai/` skeleton
- Approved `.ai/project-goal.md` and `project.md`
- Initialized `.ai/state/*.json` and empty `activity.jsonl`
- Regenerated `.ai/views/status.md` and `.ai/views/tasks.md`
- Human-facing summary message with phase and next step

## Failure/abort behavior

- Abort if `{prompt}` is empty; ask for goal text.
- Stop discovery on unresolved **Blocking** questions; do not init state or write goal until resolved.
- If `node tools/state.js init` fails schema validation, emit **PROBLEM**, do not claim project ready.
- If human rejects goal draft, revise and re-present; do not overwrite approved goal without new decision.
- On host missing write access, emit **PROBLEM** with path and stop.
