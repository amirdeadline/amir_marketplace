---
description: Merge a task worktree's branch after commit validation; integration tests after
argument-hint: <task-id> [target branch]
---

# /amir:worktree_merge

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.git_worktrees.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Pre-merge validation (all mandatory; refuse the merge on failure)

1. Resolve the worktree and branch for `<task-id>` from the registry. Target defaults to the repo's default branch.
2. Clean tree: `git -C <path> status --porcelain` is empty — uncommitted work must be committed or explicitly stashed by the user first.
3. Commit validation: review `git log <target>..task/<...> --oneline`; commits are on-task (spot-check diffs for scope creep), messages follow the project's convention, no merge-commits from random branches, and the branch contains no obvious secrets (`git diff <target>...HEAD` scanned for credential patterns — if the semgrep group is enabled, run `/amir:semgrep_scan_changed <target>`).
4. Task-branch tests pass: run the project's test suite INSIDE the worktree and record real results. Failing tests → no merge.
5. Freshness: if the target has advanced, rebase or merge target into the task branch in the worktree first, resolve conflicts there, re-run tests.

## Merge

6. From the MAIN working tree (never from inside the task worktree):

```powershell
git checkout <target>
git pull --ff-only origin <target>
git merge --no-ff "task/<task-id>-<short-name>"
```

   Use `--no-ff` so the task remains visible as a unit. Do not push unless the user asks.

## Post-merge (mandatory)

7. Integration tests on the target branch after the merge; report real results. If they fail, offer to revert the merge (`git revert -m 1 <merge-commit>`) or fix forward — user decides.
8. On success: update the registry entry (`merged_at`, merge commit), and offer `/amir:worktree_cleanup <task-id>` — do not auto-delete the worktree.
9. Report: merge commit hash, test results before and after, and the cleanup recommendation. "Merged" is claimable only after step 7 output exists.
