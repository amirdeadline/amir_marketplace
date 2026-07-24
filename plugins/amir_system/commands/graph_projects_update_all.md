---
description: Update every registered portfolio project — registered-only, skips missing/disabled safely, continues past failures, per-project results, never fake overall success
---

# /amir:graph_projects_update_all

Mutating (registry + graphs). No arguments.

Engine:

```powershell
python "$env:USERPROFILE\.amir\bin\amirctl.py" portfolio-update-all
```

Engine missing → report honestly; the fallback is running the `/amir:graph_projects_update`
procedure per project, sequentially, with the same rules below. Subcommand rejected →
`--help` once, closest documented subcommand, say which.

## Rules

1. **Registered projects only** — the set comes from
   `%USERPROFILE%\.amir\registry\projects.yaml`. NEVER scan the computer for projects.
2. Announce the plan first: the list of projects that will be updated, skipped (with reason),
   and the portfolio lock that will be held for the run. Confirm before starting.
3. **Skip safely**:
   - missing directory → skip, flag as `missing-directory` (never search for the project);
   - graphify disabled in the manifest → skip the graph refresh for it (metadata refresh
     only, labeled as such — a registry-metadata change is not a project update);
   - archived lifecycle → skip unless the user explicitly includes archived.
4. **Continue past failures** — one project's failure never aborts the run. Capture the real
   error and move on.
5. The engine holds the **portfolio lock** for the whole run and backs up
   `global-graph.json` before namespace replaces. If the lock is already held, report by
   whom/when and stop — never force it.

## Report — per-project results table, then totals

| Project (id) | Result | Detail |
|---|---|---|

Result is exactly one of: **updated** (graph + metadata refreshed, evidence in the engine
output) · **metadata-only** (graphify disabled) · **skipped** (reason) · **failed** (real
error) · **blocked** (e.g. lock, missing credential).

Totals line: N updated, N metadata-only, N skipped, N failed, N blocked.

**NEVER report overall success when some projects failed.** The correct summary for a mixed
run is "partial: X of Y updated; Z failed" — with the failures listed first, not buried.
Recommend `/amir:graph_projects_update <id>` for retrying individual failures and
`/amir:graph_projects_validate` after a run with failures.
