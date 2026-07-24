# build_goal

## Command

`/build_goal`

## Purpose

Execute the full goal delivery loop: from parsed goal through architecture, QA design, task execution, per-task worker/QA cycles, drift checks, and milestone QA — using state tools for all transitions.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Project root | Implicit | Current amir project root |
| `.ai/project-goal.md` | Yes | Approved goal |
| `.ai/state/tasks.json` | Yes | Approved task list |
| Host capabilities | Optional | `adapters/<host>/capabilities.md` for subagent availability |

## Behavior

1. **Parse goal** — re-read `.ai/project-goal.md`, `.ai/state/decisions.json`, `.ai/state/status.json`; confirm phase is `build` ready.
2. **Repo review** — snapshot current codebase; note delta from design; log `build_start` to activity.
3. **Architecture** — confirm `.ai/design.md` current; if missing or stale vs goal, run `/design` gate before build.
4. **Plan** — confirm `tasks.json` populated and human-approved; if empty, run `/plan` gate.
5. **design_qa** — confirm `.ai/qa-objectives.md` exists; if missing, run `/design_qa` gate.
6. **Tasks** — register worker/verifier agents in `agents.json` for upcoming task ids; ensure workspaces exist via `/build_agents` if needed.
7. **Per-task loop** (orchestrator `1-orchestrator` coordinates):
   1. Select next `pending` task respecting dependencies.
   2. Transition `pending` → `in_progress`: `node tools/state.js <root> transition --task <id> --to in_progress --by 1-orchestrator`.
   3. **Baseline canary** — run `./verify.sh` (or equivalent); log canary result via `node tools/activity.js <root> append --agent dev-<id> --action canary --task <id> --result <summary>`.
   4. **Worker** — render `templates/worker-prompt.md.tmpl` into `.ai/agents/dev-<id>/prompt.md`; spawn fresh `dev-<id>` (native subagent or simulated role per host).
   5. Worker implements within task scope per `core/no-drift-rules.md`; logs activity.
   6. **Fresh QA** — render verifier prompt; spawn fresh `qa-<id>` per `core/qa-loop.md`.
   7. Verifier runs acceptance + goal-alignment; writes `qa-report.md`; on PASS sets transition to `qa_passed`: `node tools/state.js <root> transition --task <id> --to qa_passed --by qa-<id> --qa-report <path>`.
   8. **Orchestrator review** — issue disposition for QA issues; goal-alignment review per `core/qa-loop.md`.
   9. On `qa_failed`, orchestrator issues fix-prompt from template; worker fix loop per `core/budget-rules.md` and `core/qa-loop.md`; increment cycles via state transitions `qa_failed` → `in_progress`.
   10. On `qa_passed`, orchestrator confirms completion checklist; transition `qa_passed` → `complete` with `--checkpoint-tag amir/T<id>-complete`.
   11. Regenerate views; log `context_rebuild` per `core/context-engineering.md`.
8. **Drift** — every 3 tasks reaching `complete`, run drift check per `core/no-drift-rules.md`; log `drift_check` to activity; pause dependents on drift detected.
9. **Milestone full QA** — at phase boundaries or orchestrator-defined milestones, run full regression per `.ai/qa-objectives.md` and `core/qa-loop.md`.
10. **Security** — invoke `4-security` review on security-touched tasks per `core/security-rules.md`.
11. If host lacks native subagents, **simulate roles sequentially** with same logical ids; disclose simulation per `core/honesty-rules.md`.
12. Continue until all tasks `complete` or orchestrator sets `blocked`/`cancelled` with note.
13. Emit progress via `core/message-contract.md` each cycle.

## Core modules referenced

- Follow `core/qa-loop.md`
- Follow `core/no-drift-rules.md`
- Follow `core/budget-rules.md`
- Follow `core/naming-rules.md`
- Follow `core/workspace-rules.md`
- Follow `core/context-engineering.md`
- Follow `core/security-rules.md`
- Follow `core/message-contract.md`
- Follow `core/interaction-style.md`
- Follow `core/honesty-rules.md`

## State files read/written

| File | Access |
|------|--------|
| `.ai/state/tasks.json` | Read/Write (transitions via tools) |
| `.ai/state/status.json` | Write (`current_task`, phase, progress) |
| `.ai/state/agents.json` | Read/Write (register workers, heartbeats) |
| `.ai/state/decisions.json` | Read |
| `.ai/state/activity.jsonl` | Append |
| `.ai/state/risks.json` | Read/Write (if risks raised) |
| `.ai/views/*.md` | Write (via render) |
| `.ai/agents/**` | Write (prompts, qa reports, notes) |
| `verify.sh` | Read/Execute |

## Outputs

- Task status progression toward `complete`
- QA artifacts per task (`qa-report.md`, alignment reviews)
- Checkpoint tags `amir/T<id>-complete` on completed tasks
- Activity audit trail of build, canary, QA, fix, drift events
- Regenerated views

## Failure/abort behavior

- Stop if pre-gates fail (no approved plan, design, or qa-objectives).
- Stop on `blocked` or budget exhaustion per `core/budget-rules.md`; require human extension decision.
- Never let worker set `qa_passed` or `complete`.
- On state transition validation error, emit **PROBLEM**, do not advance task.
- On drift detection, pause dependent tasks until remediated or risk accepted.
- Abort build loop if `./verify.sh` canary BLOCKED without documented prerequisite decision.
