---
description: Use the local Cursor AI agent as a subagent (Composer 2.5 fast by default, any Cursor model via --model) for one bounded task; Claude briefs, launches and verifies
argument-hint: "[--model <id>] [--param k=v] {prompt | smoke test | ping | models}"
---

# /amir:amir_cursor_subagent

Follow the skill at `skills/amir_cursor_subagent/SKILL.md` in this plugin (also installed at
user scope as `/amir_cursor_subagent` for Cursor and Claude Code).

Apply it now to `$ARGUMENTS`: parse `--model` / `--param` / `--no-fast` (default
`composer-2.5`, `fast=true`), write a standalone brief, launch
`skills/amir_cursor_subagent/scripts/run_cursor_subagent.ps1`, then verify the result with
your own tools before reporting. `smoke test`, `ping` and `models` always launch the wrapper.
