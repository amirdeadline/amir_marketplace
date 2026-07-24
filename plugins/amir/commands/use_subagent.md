---
name: "amir:use_subagent"
description: "Orchestrate via plan, atomic tasks, dedicated subagents or isolated contexts, validation, and verification. Does not code before planning."
---

# /amir:use_subagent

Orchestrate via plan, atomic tasks, dedicated subagents or isolated contexts, validation, and verification. Does not code before planning.

User request: `$ARGUMENTS`

Also accept `/use_subagent {prompt}` and trailing `{prompt} /amir:use_subagent`.

## Instructions

Read and follow `skill-specs/use_subagent.md` in this packed amir plugin (`skill-specs/<name>.md`).

- Resolve amir root: this plugin directory (marketplace-packed; contains `core/`, `skill-specs/`, `tools/`).
- Templates: `templates/use_subagent/`
- Schemas: `schemas/use_subagent-*.yaml`
- Host notes: `templates/use_subagent/adapters/cursor.md`
- Clarifications: `core/question-format.md` (A–E)
- Honesty: `core/honesty-rules.md`
- Secrets: `core/security-rules.md`

### Orchestration (non-negotiable)

- Do **not** implement before Stages 1–3 (understanding, clarify if needed, final plan).
- Inspect the repository before asking questions.
- Decompose into atomic tasks with measurable acceptance criteria.
- One fresh specialized subagent **or** isolated task execution context per executable task.
- Use Cursor `Task` when available (Mode A); otherwise Mode C and say so — never fake native subagents.
- Validate every result with evidence; independent review for medium/high risk.
- No project-tree scratch; prefer chat; TEMP under `%TEMP%\subagent-work\<session-id>\` only if needed.

Execute the skill **Behavior** section exactly.
