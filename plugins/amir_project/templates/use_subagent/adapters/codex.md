# Codex adapter — use_subagent

## Invocation

- Skill: `amir-use-subagent` / follow `skill-specs/use_subagent.md`
- Phrases: `/use_subagent`, `/amir:use_subagent`, trailing forms

## Mode selection

Default **Mode C** — sequential isolated task execution contexts with `[AGENT <profile> T00n]` labels.

If the user opens multiple Codex sessions and returns results → **Mode D** or informal **Mode B**.

## Honesty

Per `core/honesty-rules.md`: state when roles are simulated. Do not claim parallel native subagents.
