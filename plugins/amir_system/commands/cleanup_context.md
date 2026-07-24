---
description: Durable context handoff before context degradation — persist facts, state, and next actions to ai/ docs
---

# /amir:cleanup_context

Load and follow the `cleanup_context` skill in this plugin (`skills/cleanup_context/SKILL.md`).

Contract:

- This is a durable context handoff, NOT fake context clearing. Never claim context was cleared
  or compacted unless a genuinely new session was started.
- Extract and persist: durable facts, completed work, pending work, decisions, risks, unresolved
  questions, modified files, validation evidence, rollback info.
- Update the project docs: `ai/status.md`, `ai/tasks.md`, `ai/decisions.md`, `ai/risks.md`, and
  write/refresh `ai/context_handoff.md`.
- The handoff document must state: project goal, current task and state, completed items, pending
  items, files changed, files to read first, commands already run, tests passed/failed, known
  risks, do-not-change list, and the next exact action.
- End by recommending a fresh session when degradation is likely, and say explicitly that the
  user must start it — you cannot clear your own context.

If this is not an Amir project (no `.amir/project.yaml` and no `ai/` directory), still perform the
handoff but write the file to `ai/context_handoff.md` after confirming the location with the user.
