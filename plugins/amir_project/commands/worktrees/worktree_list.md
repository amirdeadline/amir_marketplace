---
description: List all worktrees with task assignment and cleanliness state
---

# /amir:worktree_list

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.git_worktrees.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Ground truth from git:

```powershell
git worktree list --porcelain
```

2. Cross-reference with `.amir/state/worktrees.json` (assignments). For each worktree report: path, branch, HEAD commit, assigned task/agent (or "untracked — not created via worktree_create"), dirty/clean (`git -C <path> status --porcelain`), ahead/behind its base (`git rev-list --left-right --count <base>...HEAD`), and age.
3. Flag anomalies explicitly: worktrees in the registry but missing on disk (prunable — point to `/amir:worktree_repair`), worktrees on disk but not in the registry, two registry entries claiming the same branch (violates one-task-one-tree), locked or prunable entries from the porcelain output.
4. Read-only command: change nothing; recommend `/amir:worktree_cleanup` or `/amir:worktree_repair` where applicable.
