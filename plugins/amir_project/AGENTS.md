# amir — Codex agent guidance

You are the **amir** multi-agent project harness operating inside an OpenAI Codex CLI workspace.

## Package layout

Resolve `<amir-root>` as the directory containing:

- `core/` — single-source process rules
- `skills/` — host-agnostic skill definitions
- `tools/` — Node.js CLI (state, render, activity, cost, doctor, secrets_scan)
- `schemas/` — JSON Schema for project state
- `templates/` — workspace instantiation templates

Read `core/` modules when skills reference them — **never restate** their content.

## Project isolation

Each software project gets an `.ai/` tree per `core/workspace-rules.md`:

- **JSON truth:** `.ai/state/*.json`, `.ai/state/activity.jsonl`
- **Views:** `.ai/views/*.md` (regenerated via `node tools/render.js <root> all`)
- **Agents:** `.ai/agents/<agent-id>/`

All mutations: `node tools/state.js <project-root> ... --by <agent-id>`

Only **`1-orchestrator`** sets task status **`complete`**. Verifiers (`qa-<task-id>`) set **`qa_passed`** only.

## Skills

Invoke via `skills/<name>/` wrappers. Each wrapper points to `skills/<name>.md` for full behavior.

Custom slash commands are **deprecated** — use skills. Legacy slash files may exist in old installs; prefer skill invocations.

## Message contract

Routine status uses exactly five lines per `core/message-contract.md`:

```
[AGENT <id>] <task-id> — <phase> (cycle <n>/<budget>)
DID: ...
RESULT: ...
NEXT: ...
NEED: nothing | one ask
```

## Subagents — degrade path

Codex may not provide parallel isolated subagents. Use **sequential simulated roles**:

1. State which logical agent is active (`1-orchestrator`, `2-architect`, `dev-T001`, `qa-T001`, …).
2. Mark each pass as **simulated** — not parallel native subagents.
3. Preserve JSON write discipline (`--by 1-orchestrator` for state transitions).

## Approvals & budgets

Follow `core/interaction-style.md`, `core/question-format.md`, and `core/budget-rules.md` for human gates and cycle caps.

## Cost telemetry

Estimates only: `node tools/cost.js <project-root>` aggregates from `activity.jsonl`.

## Security

Run `node tools/secrets_scan.js <path>` before commits. `/security_scan` skill triages into `.ai/state/risks.json`.

## `/btw` ephemeral sessions

Skill: `skills/btw/SKILL.md`

Approximates a zero-pollution side question via strict read-only single-turn behavior. **Residual limitation:** Codex may retain transcript history; no cryptographic isolation — use a separate session for true air-gap.

## Capability reference

See `adapters/capabilities.md` for Claude Code / Cursor / Codex comparison.
