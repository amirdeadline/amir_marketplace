---
description: Repair worktree drift - prune stale entries, relink moved trees, fix registry
---

# /amir:worktree_repair

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.git_worktrees.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Diagnose first (no changes yet): run the checks from `/amir:worktree_validate` and build a findings list — prunable git entries, moved/deleted trees, registry-vs-disk drift, broken `.git` file links inside worktrees.
2. Present the findings and the planned fix for each; get one confirmation for the batch of SAFE fixes, and per-item confirmation for anything destructive.
3. Safe fixes (batch after confirmation):
   - `git worktree prune` for administratively-stale entries whose directories are gone.
   - `git worktree repair` (run from the main tree) and `git worktree repair <path>` for moved trees, which relinks `.git` file pointers in both directions.
   - Registry sync: mark registry entries whose trees are truly gone as `removed_at: <now> (pruned)`; add registry stubs for on-disk trees created outside `worktree_create` (flag them for proper naming).
4. Destructive repairs (each needs its own explicit yes): deleting a corrupt worktree directory that git no longer recognizes, or removing a registry entry that points at a tree with uncommitted changes. Always show the uncommitted diff stat first.
5. Never touch the main working tree's checkout state; repair operates on metadata and auxiliary trees only.
6. Re-run the validation matrix afterwards and report the before/after pass-fail table. "Repaired" only when the re-run is clean or every remaining failure is explicitly deferred by the user.
