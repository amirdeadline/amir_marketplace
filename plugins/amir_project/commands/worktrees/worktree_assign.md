---
description: Assign a worktree to exactly one writing agent (enforces single-writer rule)
argument-hint: <task-id> <agent name>
---

# /amir:worktree_assign

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.git_worktrees.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Resolve the worktree for `<task-id>` from `.amir/state/worktrees.json`; verify it still exists in `git worktree list`. Missing → point to `/amir:worktree_create` or `/amir:worktree_repair`.
2. Enforce the single-writer rule: if the entry already has a different assigned agent, REFUSE unless the user explicitly reassigns (and then record the handoff: old agent, new agent, timestamp, reason). Never allow two write-agents on one tree — parallel writers corrupt each other's staged state.
3. An agent may hold multiple read-only checkouts, but write assignment is 1:1 both ways where the project runs one-task-per-agent: warn if this agent already holds another write assignment.
4. Update the registry entry: `assigned: <agent>`, `assigned_at`. Write the file atomically (write temp, then move).
5. Tell the assigned agent's session (via the project's messaging convention) the worktree path and branch, and the rule: commit early and often on the task branch, never switch branches inside the worktree, never touch other worktrees.
6. Report the final assignment table for this task.
