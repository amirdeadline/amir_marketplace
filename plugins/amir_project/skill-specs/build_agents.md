# build_agents

## Command

`/build_agents`

## Purpose

Materialize agent workspace folders and seed `prompt.md` / `notes.md` for every registered agent in `agents.json`.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Project root | Implicit | Current amir project root |
| `.ai/state/agents.json` | Yes | Agent registry from `/design_agents` |

## Behavior

1. Read `.ai/state/agents.json`; fail if empty or missing orchestrator.
2. For each agent id, create `.ai/agents/<agent-id>/` per `core/workspace-rules.md` and `core/naming-rules.md`.
3. Create `notes.md` with header structure per `core/context-engineering.md` (agent id, task id placeholder, empty sections).
4. Create `prompt.md` — role-specific seed:
   - Orchestrator: coordination charter + pointers to state tools
   - Architect: design maintenance charter
   - QA org: verifier policy per `core/qa-loop.md`
   - Security: review charter per `core/security-rules.md`
   - Workers/verifiers: defer full prompt to `templates/worker-prompt.md.tmpl` at task start (stub with "await task assignment")
5. Create `logs/` subdirectory; add `.gitkeep` if needed.
6. For `qa-<task-id>` agents, use consistent path convention chosen at project create (flat or under `3-qa/`).
7. Do not overwrite non-empty `notes.md` or `qa-report.md` without orchestrator note in decisions.
8. Append `build_agents_complete` to activity; run `node tools/doctor.js <root>` orphan check.
9. Recommend `/plan`.

## Core modules referenced

- Follow `core/workspace-rules.md`
- Follow `core/naming-rules.md`
- Follow `core/context-engineering.md`
- Follow `core/qa-loop.md`
- Follow `core/security-rules.md`
- Follow `core/message-contract.md`

## State files read/written

| File | Access |
|------|--------|
| `.ai/state/agents.json` | Read |
| `.ai/agents/**/notes.md` | Write |
| `.ai/agents/**/prompt.md` | Write |
| `.ai/agents/**/logs/` | Create |
| `.ai/state/activity.jsonl` | Append |

## Outputs

- Workspace folder per agent id
- Seeded `prompt.md` and `notes.md` files
- Doctor orphan check result

## Failure/abort behavior

- Abort if `agents.json` missing.
- Stop on path collision with non-agent directories; report paths.
- Never delete existing workspace content; archive via `/agent_reset` if respawn needed.
- If disk write fails, stop and report partial creation list.
