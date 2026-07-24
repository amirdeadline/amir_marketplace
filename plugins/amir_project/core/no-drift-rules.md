# amir — no-drift rules

Keep implementation aligned with approved project goal and recorded decisions. Passing tests alone is not sufficient.

## Source of truth

Authoritative state lives only in:

| Artifact | Purpose |
|----------|---------|
| `.ai/project-goal.md` | Product outcome, constraints, non-goals |
| `.ai/state/tasks.json` | Task specs, acceptance criteria, status |
| `.ai/state/decisions.json` | Human and agent decisions |
| `.ai/state/status.json` | Phase, checkpoints, gate flags |
| `.ai/state/activity.jsonl` | Append-only audit log |

Markdown under `.ai/views/` is **regenerated** from JSON — not authoritative.

**Ignored paths** (e.g. host caches, `node_modules`, build output) are never source-of-truth per `core/security-rules.md`.

## Clarification: "no cached decisions"

**"No cached decisions"** means:

- Agents **must read** current project state files at session start and before major actions.
- Decisions exist **only** in `.ai/state/decisions.json` (and goal/tasks derived from approved design).
- Conversation history, old prompts, or agent memory **do not** override project state.
- If chat contradicts JSON, **JSON wins** unless human explicitly updates state.

## Forbidden fix behavior

During fix loops, QA failures, or "make it green" pressure, agents **must not**:

1. **Remove features** to pass tests without DECISION REQUIRED and goal update
2. **Weaken acceptance criteria** in tasks or tests without human approval
3. **Change public API** (endpoints, CLI, events) without approval per `core/security-rules.md`
4. **Replace architecture** (framework, database, auth model) without architect + human gate
5. **Delete or skip failing tests** instead of fixing product code
6. **Reduce security** (disable auth, skip scan, hardcode secrets) to unblock
7. **Hide failures** (empty catch, swallow errors, false PASS)
8. **Broad rewrites** unrelated to the task spec ("while we're here")
9. **Change the goal** in code or docs to match what was built instead of fixing implementation

Any of the above → **PROBLEM**, log to activity, stop until orchestrator and human resolve.

## Allowed fix behavior

Fixes **may**:

- Correct bugs to meet **existing** acceptance criteria and `project-goal.md`
- Add tests required by QA or task spec
- Refactor **within scope** of the task when behavior unchanged and QA agrees
- Update **views** and workspace notes — not authoritative JSON except via orchestrator tools
- Apply **Minor** defaults logged to decisions per `core/question-format.md`
- Improve error messages, logging, and observability **if** specified or required for acceptance

## Expected behavior changes

If a fix **requires changing expected behavior** (semantics, UX contract, API response):

1. Stop automatic fix loop
2. Emit **DECISION REQUIRED**
3. Propose update to `tasks.json` acceptance criteria or `project-goal.md`
4. Wait for human approval recorded in `decisions.json`
5. Re-run goal-alignment review after approval

## Passing tests ≠ aligned product

A task **must not** complete when:

- Tests pass but behavior diverges from `.ai/project-goal.md`
- Features ship that contradict `decisions.json`
- Non-goals were implemented or must-haves omitted
- QA goal-alignment review **FAIL** (see `core/qa-loop.md`)

Orchestrator confirms alignment before `complete` status.

## Drift check cadence

Every **3 completed tasks** (status → `complete` in `tasks.json`), orchestrator runs a **drift check**:

1. Read `.ai/project-goal.md` and last 3 completed task records
2. Compare shipped behavior (QA reports, acceptance evidence) to goal
3. Produce **≤5 lines** summary: aligned | drift detected
4. Append entry to `.ai/state/activity.jsonl` with type `drift_check`

If drift detected → **PROBLEM**, open remediation task, pause dependent work until resolved or accepted as risk.

## Worker and QA obligations

- Workers cite task id and acceptance ids in commit/PR messages when host supports it
- QA includes **goal-alignment** section every review (`core/qa-loop.md`)
- Security drift (new endpoints, auth bypass) → immediate **FAIL** and `4-security` review

## Cross-references

| Topic | File |
|-------|------|
| QA goal alignment | `core/qa-loop.md` |
| Approval gates | `core/security-rules.md` |
| Honesty | `core/honesty-rules.md` |
| Workspace layout | `core/workspace-rules.md` |

Skills and agents must say **"Follow `core/no-drift-rules.md`"** — do not restate these rules elsewhere.
