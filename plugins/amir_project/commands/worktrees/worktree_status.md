---
description: Deep status of one worktree - commits, dirt, divergence, mergeability
argument-hint: <task-id or worktree path>
---

# /amir:worktree_status

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.git_worktrees.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Resolve the worktree from `$ARGUMENTS` via the registry or `git worktree list`. Default when omitted: the worktree containing the current directory, else ask.
2. Report with real command output:
   - Branch and HEAD: `git -C <path> log --oneline -5`.
   - Working state: `git -C <path> status --porcelain` — count staged / unstaged / untracked; list them when few.
   - Divergence from base: `git -C <path> rev-list --left-right --count origin/<base>...HEAD` (behind/ahead) and whether base has moved since creation.
   - Mergeability probe (non-destructive): `git -C <path> merge-tree $(git merge-base origin/<base> HEAD) origin/<base> HEAD` style check, or `git merge --no-commit --no-ff` in a scratch clone — never run a real merge here; report predicted conflicts by file.
   - Stashes on this worktree: `git -C <path> stash list`.
3. Assignment: who holds it, since when, task id (from registry).
4. Verdict: ready-to-merge / needs-rebase / has-uncommitted-work / stale, with the evidence line for each claim. Recommend the next command (`/amir:worktree_merge`, or committing/stashing first).
