# design_agents

## Command

`/design_agents`

## Purpose

Populate `ai/state/agents.json` with the project agent registry using canonical naming, and render the human-readable `ai/views/agents.md` view.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Project root | Implicit | Current amir project root |
| `ai/design.md` | Yes | Approved design (component owners) |
| `ai/qa-objectives.md` | Yes | QA org requirements |
| Planned task list | Optional | Draft task ids if known pre-plan |

## Behavior

1. Act as **`1-orchestrator`** writer for `agents.json` per `core/workspace-rules.md`.
2. Register fixed top-level agents per `core/naming-rules.md`: `1-orchestrator`, `2-architect`, `3-qa`, `4-security`.
3. Add planned worker/verifier slots (`dev-T00x`, `qa-T00x`) if task ids are known from draft plan; otherwise register org agents only and note workers spawn at build.
4. Set initial `state: active` for orchestrator/architect/qa/security; workers `inactive` until task assignment.
5. Validate against `schemas/agents.schema.json` before write.
6. Write `ai/state/agents.json` via orchestrator path (direct write only if host lacks state tooling — prefer consistency with init structure).
7. Render `ai/views/agents.md`: table of id, role, state, task_id, workspace path — regenerate from JSON (hand-render if no tool subcommand; view is non-authoritative).
8. Present registry summary per `core/message-contract.md`.
9. Append `design_agents_complete` to activity; recommend `/build_agents`.

## Core modules referenced

- Follow `core/naming-rules.md`
- Follow `core/workspace-rules.md`
- Follow `core/message-contract.md`
- Follow `core/honesty-rules.md`

## State files read/written

| File | Access |
|------|--------|
| `ai/state/agents.json` | Write |
| `ai/views/agents.md` | Write |
| `ai/design.md` | Read |
| `ai/qa-objectives.md` | Read |
| `ai/state/activity.jsonl` | Append |

## Outputs

- Populated `ai/state/agents.json`
- `ai/views/agents.md`
- Registry summary in chat

## Failure/abort behavior

- Abort if schema validation fails; do not write invalid JSON.
- Abort if duplicate agent ids detected.
- Do not create workspace folders — `/build_agents` does that.
- If naming conflicts with existing workspaces, emit **PROBLEM** and list orphans for doctor.
