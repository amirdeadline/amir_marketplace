# Generic / third-party adapter — use_subagent

## Detect

1. Can the host spawn an isolated agent with a custom prompt? → Mode A
2. Can multiple agents run concurrently without shared mutable chat? → Mode B
3. Otherwise → Mode C (isolated task execution context)
4. If only the user can create agents → Mode D

## Mode C procedure

For each READY task:

1. Build prompt from `subagent-prompt.md` only (no prior task reasoning).
2. Execute solely that task.
3. Capture structured result (`schemas/use_subagent-result.schema.yaml`).
4. Orchestrator validates.
5. Discard task-local chain-of-thought before the next task.

Announce: `Using isolated task execution context (Mode C) — not a native subagent.`

## Mode D procedure

Emit for each task: prompt body, dependencies, parallel group id, expected return format. Integrate when the user pastes results. Validate as usual.
