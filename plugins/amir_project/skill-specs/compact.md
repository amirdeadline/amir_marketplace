# compact

## Command

`/compact`

## Purpose

Manually compact working context per context-engineering thresholds without losing authoritative criteria or security constraints.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Project root | Implicit | Current amir project root |
| Agent id | Optional | Workspace to compact (default active agent) |
| Trigger | Implicit | Human request or >50% context threshold per `core/budget-rules.md` |

## Behavior

1. Identify agent workspace `.ai/agents/<agent-id>/notes.md` and active prompt files.
2. Follow compaction rules in `core/context-engineering.md`: summarize completed steps; drop redundant file pastes; retain acceptance criteria ids, failing QA ids, open DECISION REQUIRED, security constraints.
3. Do not remove references to `.ai/state/*.json` paths — convert blobs to pointers.
4. Archive verbose superseded sections to `.ai/agents/<agent-id>/logs/compact-<timestamp>.md` before trimming `notes.md`.
5. Regenerate worker/verifier prompt from JSON if task active — stale prompts forbidden per `core/context-engineering.md`.
6. Append `context_compact` event to `.ai/state/activity.jsonl` per `core/budget-rules.md` with agent id and estimated savings note.
7. If usage still >75% after compact, recommend `/handoff` for fresh instance.
8. Message human per `core/message-contract.md` with what was retained vs archived.

## Core modules referenced

- Follow `core/context-engineering.md`
- Follow `core/budget-rules.md`
- Follow `core/message-contract.md`
- Follow `core/no-drift-rules.md`
- Follow `core/honesty-rules.md`

## State files read/written

| File | Access |
|------|--------|
| `.ai/agents/<agent-id>/notes.md` | Write (trim) |
| `.ai/agents/<agent-id>/prompt.md` | Write (regenerate if needed) |
| `.ai/agents/<agent-id>/logs/*` | Write (archive) |
| `.ai/state/activity.jsonl` | Append |
| `.ai/state/tasks.json` | Read |
| `.ai/state/decisions.json` | Read |

## Outputs

- Compacted `notes.md`
- Optional archive log file
- `context_compact` activity event
- Recommendation for handoff if still over threshold

## Failure/abort behavior

- Abort if compaction would remove active acceptance criteria or open BLOCKED items — emit **PROBLEM**.
- Do not compact `.ai/state/` JSON or `.ai/project-goal.md`.
- Never treat compacted notes as new decisions — promote separately via orchestrator.
