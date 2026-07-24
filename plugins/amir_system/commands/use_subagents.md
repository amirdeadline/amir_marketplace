---
description: Decompose the current project goal into bounded, verifiable subagent tasks and orchestrate them safely
argument-hint: [goal or task description]
---

# /amir:use_subagents

Load and follow the `use_subagents` skill in this plugin (`skills/use_subagents/SKILL.md`).

Contract (the skill elaborates):

- Read the project goal, `.amir/project.yaml`, and the system rules BEFORE decomposing anything.
  If there is no `.amir/project.yaml`, say so and ask whether to proceed in ad-hoc mode
  (reduced guarantees, no manifest-gated tools).
- Decompose into ordered, independently verifiable tasks. Each subagent gets ONE bounded context
  package — never the whole repository.
- Every task package must state: acceptance criteria, allowed paths, prohibited paths, required
  tests, required evidence.
- Use separate git worktrees for parallel code modification ONLY if worktrees are enabled in the
  manifest; otherwise serialize code-writing tasks.
- Graphify/Serena are usable by subagents only when enabled in the manifest (tool-scope rule).
- Subagents must not change the project end goal (goal-preservation rule).
- Merge only validated work; record decisions and results in the project's `ai/` docs.
- Report honestly which tasks completed, failed, were skipped, or are blocked — with evidence.

`$ARGUMENTS`, if present, is the goal to decompose; otherwise derive it from the project docs and
confirm it with the user first.
