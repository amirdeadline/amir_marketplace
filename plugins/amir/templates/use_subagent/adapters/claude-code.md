# Claude Code adapter — use_subagent

## Invocation

- `/amir:use_subagent {prompt}` via packed skill `skills/use_subagent/SKILL.md`
- Aliases when the host recognizes `/use_subagent` or trailing trigger

## Mode selection

Prefer **Mode A** — native Task / agent definitions under `agents/` (`1-orchestrator` stays as parent; workers are fresh Task agents).

Map logical profiles to Claude agents or Task roles. One Task per atomic task. Do not reuse the same worker session for unrelated tasks.

## Mode C fallback

If Task is unavailable, use isolated task execution contexts and label them — never claim native isolation.

## Notes

- Clarifications: `core/question-format.md` A–E
- Do not write scratch into the project tree; use `%TEMP%\subagent-work\<id>\` only if needed
- Independent of `ai/state` unless user asks to persist
