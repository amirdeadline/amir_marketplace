---
name: "amir:troubleshoot"
description: "Interactive troubleshooting for: `$ARGUMENTS`"
---

# /amir:troubleshoot

Interactive troubleshooting for: `$ARGUMENTS`

## Instructions

Read and follow `skill-specs/troubleshoot.md` in this packed amir plugin (`skill-specs/<name>.md`).

- Resolve amir root: this plugin directory (marketplace-packed; contains `core/`, `skill-specs/`, `tools/`).
- Use templates under `templates/troubleshoot/` for step, root-cause, options, plan, approval, execution, and validation formats.
- Classify every command with `templates/troubleshoot/command-classifier.md` before running it.
- Clarifications (if needed): follow `core/question-format.md` (A–E).
- Honesty labels: Fact / Hypothesis / Inference / Unknown per `core/honesty-rules.md`.
- Secrets: redact; follow `core/security-rules.md`.

### Safety (non-negotiable)

- **Mode A — Read-only:** may run without approval only when confidently `READ_ONLY`.
- **Mode B — State-changing / UNCERTAIN:** never run before exact plan + explicit approval (`Approve plan` / `Approve actions N-M`).
- One diagnostic step at a time; next step derived from evidence.
- Never skip from root cause to execution.
- Never write scratch/diagnostic files into the project tree.
- Prefer in-chat evidence; TEMP under `%TEMP%\troubleshoot\<session-id>\` only if approved (or host-authorized).

Execute the skill **Behavior** section exactly. Do not invent steps not in the skill definition.
