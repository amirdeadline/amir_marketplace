---
name: worktree_discipline
description: >-
  Git worktree discipline for parallel agents: one agent per tree, deterministic
  naming, merge gates, cleanup safety.
---

# worktree_discipline

Native git worktrees give each parallel task an isolated checkout sharing one repository. Gated on `project_tools.git_worktrees.enabled`. No external tool is involved — plain git.

## The core invariant

**One agent = one task branch = one worktree.** Never two write-agents in one tree (they trash each other's index and working state); never one agent writing across multiple trees at once (untraceable changes). Read-only peeks into other trees are fine.

## Deterministic layout

- Worktree path: `.amir/worktrees/<task-id>-<short-name>` (kebab-case), with `.amir/worktrees/` gitignored — an unignored in-repo worktree doubles every source file for tools.
- Documented fallback when in-repo placement breaks the project's tooling (watchers, indexers, undisciplined build globs): sibling directory `..\<repo-name>-worktrees\<task-id>-<short-name>`. The choice is recorded per project; do not mix locations casually.
- Branch: `task/<task-id>-<short-name>`, cut from the fresh default branch.
- Registry: `.amir/state/worktrees.json` mirrors assignments (task, path, branch, agent, timestamps). Git is ground truth; the registry is the assignment ledger — `/amir:worktree_repair` reconciles drift.

## Inside a worktree

Commit early and often on the task branch; never switch branches inside a worktree; never touch sibling trees; rebase/merge the base INTO the task branch in the worktree when the base moves.

## Merge gate (order is mandatory)

Clean tree → commits validated (on-task, message convention, no secrets in the diff) → tests pass IN the worktree → base freshness handled → merge `--no-ff` from the main tree → integration tests on the target AFTER the merge. A merge without post-merge integration tests is unfinished; failed integration → revert or fix forward, user decides.

## Cleanup safety

Uncommitted work is never force-deleted without per-tree explicit approval; unmerged (failed/abandoned) worktrees are PRESERVED unless explicitly removed — they are the record of what was attempted. Branch deletion uses `-d` (git refuses unmerged), remote deletion only on request. `git worktree prune` and registry updates close the loop.

## Fallback

If worktrees are unusable in a context (exotic filesystem, tooling that chokes), fall back to sequential single-branch work with the same branch naming and the same merge gate — discipline survives the mechanism.
