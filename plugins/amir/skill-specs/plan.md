# plan

## Command

`/plan`

## Purpose

Produce a phased implementation plan, run context-engineering quality review, obtain human approval, and populate `ai/state/tasks.json`.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Project root | Implicit | Current amir project root |
| `ai/design.md` | Yes | Approved design |
| `ai/qa-objectives.md` | Yes | QA criteria mapping |
| `ai/project-goal.md` | Yes | Goal constraints |

## Behavior

1. Act as **`2-architect`** proposing tasks; orchestrator owns JSON writes.
2. Decompose work into phases (foundation, core features, hardening, docs) aligned with design components.
3. Size each task per `core/context-engineering.md`: max ~5 files, ~300 LOC, **one behavior** per task; split oversized items.
4. Assign task ids per `core/naming-rules.md` (`T001`… sequential); include priority, dependencies, `approval_required`, initial `cycles` budget.
5. Invoke **review sub-agent** (native Task if available) to audit plan for context-engineering quality, dependency order, acceptance testability, and sizing violations.
6. If sub-agent unavailable, simulate review sequentially and state degrade per `core/honesty-rules.md` and host `adapters/<host>/capabilities.md`.
7. Present plan table to human per `core/interaction-style.md`; batch Material questions if scope forks remain.
8. On human approval, write tasks to `ai/state/tasks.json` (orchestrator via `set-task-field` / bulk JSON update + schema validation).
9. Update `ai/state/status.json` phase to `plan` complete; append `plan_approved` to activity.
10. Run `node tools/render.js <root> tasks`; recommend `/build_goal`.

## Core modules referenced

- Follow `core/context-engineering.md`
- Follow `core/naming-rules.md`
- Follow `core/workspace-rules.md`
- Follow `core/question-format.md`
- Follow `core/interaction-style.md`
- Follow `core/message-contract.md`
- Follow `core/budget-rules.md`
- Follow `core/no-drift-rules.md`
- Follow `core/honesty-rules.md`
- Follow `core/qa-loop.md`

## State files read/written

| File | Access |
|------|--------|
| `ai/state/tasks.json` | Write |
| `ai/state/status.json` | Write |
| `ai/state/decisions.json` | Write (plan approval) |
| `ai/state/activity.jsonl` | Append |
| `ai/views/tasks.md` | Write (via render) |
| `ai/design.md` | Read |
| `ai/qa-objectives.md` | Read |
| `ai/project-goal.md` | Read |

## Outputs

- Populated `ai/state/tasks.json` with phased tasks
- Regenerated `ai/views/tasks.md`
- Plan approval decision
- Review sub-agent findings (if run)

## Failure/abort behavior

- Abort if design or qa-objectives not approved.
- Do not write tasks without explicit human approval.
- Abort if `tasks.json` schema validation fails.
- Stop if review sub-agent flags Blocking sizing or missing acceptance criteria — fix plan first.
- Never set task status beyond `pending` in this skill.
