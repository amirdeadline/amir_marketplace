---
description: Validate worktree discipline across the repo (registry vs git vs policy)
---

# /amir:worktree_validate

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.git_worktrees.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Validation matrix (run all; pass/fail per line)

1. Git supports worktrees here: `git worktree list` succeeds; repo is not bare-with-issues; `git --version` noted.
2. Registry integrity: `.amir/state/worktrees.json` parses; every entry's path exists and its branch matches what git reports for that path; no duplicate task ids; no two entries share a branch or a path.
3. Naming discipline: every registered worktree follows `.amir/worktrees/<task-id>-<short-name>` (or the documented sibling fallback `..\<repo>-worktrees\`); branches follow `task/<task-id>-<short-name>`. List violations.
4. Ignore rule: `.amir/worktrees/` is matched by `.gitignore` (`git check-ignore .amir/worktrees` exits 0) when in-repo placement is used.
5. Single-writer: no agent-assignment conflicts in the registry; no worktree with an active assignment whose branch also has commits from another identity since assignment (check `git log --format=%an` on the branch since `assigned_at` — informational, may be legitimate; flag for review).
6. Orphans and drift: `git worktree list --porcelain` prunable entries; on-disk trees not in the registry; registry entries not on disk.
7. Main working tree safety: the primary checkout is not itself on a `task/` branch (agents work in worktrees, not the main tree).

Verdict "disciplined" only when 1-4 pass and 5-7 have no unexplained findings. Recommend `/amir:worktree_repair` for drift and `/amir:worktree_cleanup` for finished trees. Read-only: fix nothing here.
