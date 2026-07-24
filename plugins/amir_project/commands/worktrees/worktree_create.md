---
description: Create a task worktree with deterministic naming (one agent, one branch, one tree)
argument-hint: <task-id> <short-name> [base ref]
---

# /amir:worktree_create

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.git_worktrees.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Require `<task-id>` and `<short-name>` from `$ARGUMENTS` (kebab-case both). Base ref defaults to the repo's default branch, fetched fresh.
2. Preconditions: `git rev-parse --is-inside-work-tree` succeeds; the branch `task/<task-id>-<short-name>` does not already exist; no existing worktree already serves this task (`git worktree list`). One agent = one task branch = one worktree — refuse duplicates.
3. Placement (deterministic): primary location `.amir/worktrees/<task-id>-<short-name>` inside the project. Ensure `.amir/worktrees/` is gitignored (a worktree inside the repo tree MUST be ignored or every tool sees doubled sources). If in-repo placement breaks the project's tools (watchers, IDE indexers, build globs that cannot exclude it), use the documented fallback: sibling directory `..\<repo-name>-worktrees\<task-id>-<short-name>`. State which location was chosen and why, and record it.
4. Create:

```powershell
git fetch origin
git worktree add ".amir/worktrees/<task-id>-<short-name>" -b "task/<task-id>-<short-name>" <base-ref>
```

5. Register the assignment in `.amir/state/worktrees.json` (append entry: task id, branch, path, base ref, created_at, assigned agent = unassigned). Create the file if missing.
6. Verify: `git worktree list` shows the new tree; `git -C <path> status` is clean. Report path, branch, and base commit hash. Never claim created without the verification output.
