---
description: Remove finished worktrees safely - uncommitted work is never force-deleted
argument-hint: [task-id | --merged-only]
---

# /amir:worktree_cleanup

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.git_worktrees.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Scope from `$ARGUMENTS`: one task id, or `--merged-only` (all registry entries with `merged_at` set), or interactive selection from `/amir:worktree_list` output.
2. For EACH candidate, check before touching anything:
   - Uncommitted changes: `git -C <path> status --porcelain`. Non-empty → SKIP this tree and surface the changes; never force-delete uncommitted work without the user explicitly approving loss, per finding.
   - Unmerged commits: `git log <target> ^task/<branch> --oneline`. Non-empty and not marked merged → treat as a FAILED/unfinished worktree: PRESERVE it by default (the spec requires preserving failed worktrees unless explicitly removed); only remove on an explicit per-tree user yes.
   - Stashes: `git -C <path> stash list` — surface before removal.
3. Removal, per approved tree:

```powershell
git worktree remove ".amir/worktrees/<task-id>-<short-name>"
```

   Use `git worktree remove --force` ONLY when the user explicitly approved discarding that tree's dirt (destructive-action rule: named confirmation per tree, no blanket approval).
4. Branch: ask separately whether to delete the merged task branch (`git branch -d task/<...>` — `-d` not `-D`, so git itself protects unmerged branches). Remote branches are deleted only on explicit request.
5. Finish with `git worktree prune` and update `.amir/state/worktrees.json` (mark removed entries with `removed_at`; keep the history rows).
6. Report per tree: removed / preserved (and why) / branch kept or deleted. No blanket "cleaned up".
