---
description: Update one registered project in the portfolio — refresh state, determine freshness, evidence-based progress, local graph refresh, global namespace replace, honest report
argument-hint: project_directory | project_id
---

# /amir:graph_projects_update

Mutating (registry + graphs). Argument: directory or registered id. If `$ARGUMENTS` is empty,
show `portfolio-list` and ASK which project — never fuzzy-match a name from conversation.

Engine:

```powershell
python "$env:USERPROFILE\.amir\bin\amirctl.py" portfolio-update <dir|id>
```

Engine missing → say so; offer only the supervised manual path below with a shown plan per
write. Subcommand rejected → `--help` once, closest documented subcommand, report which.

## Phase 1 — Read current state (read-only)

From the project: `.amir\project.yaml` (stable id, enabled tools), `.amir\portfolio.yaml`
(lifecycle, priority, phase, milestones, blockers, next action), the `.ai\` docs
(status.md, tasks.md, decisions.md, risks.md, changelog.md), and git state
(`git -C <dir> rev-parse --abbrev-ref HEAD`, `git status --porcelain`, HEAD commit + date).
Directory missing or manifest unreadable → STOP and report; this command never repairs.

## Phase 2 — Freshness determination

Compare, and record which is newer:

- last local graph build (graphify-out\graph.json time + the source commit it was built from)
  vs. project HEAD / latest file changes → local graph **current** or **stale**;
- global namespace timestamp vs. local graph → namespace **current** or **stale**;
- `.ai\status.md` age vs. the staleness threshold → project status **current** or **stale**.

Label every stale item as stale in the final report — a failed or skipped refresh keeps the
PREVIOUS graph in place and it must be reported as stale, never as updated.

## Phase 3 — Progress (evidence only — NEVER invent)

Progress values may come ONLY from:

- milestone data in `.amir\portfolio.yaml` (done/total, with evidence fields);
- acceptance criteria marked complete in project docs;
- `.ai\tasks.md` completion state;
- Asana (when `integrations.asana` is configured) via the asana capability;
- explicitly labeled estimates written by a human.

Classify the result as **Confirmed** (milestone/criteria evidence), **Estimated** (labeled
estimate, shown as an estimate), or **Unknown** (blank — a perfectly valid answer). Commit
count, graph size, file count, and vibes are NOT progress sources (global-graph rule: never
infer business completion from technical activity).

## Phase 4 — Refresh

1. Local graph: if graphify is enabled in the manifest and the graph is stale → refresh,
   incremental (`graphify update`) when possible, full rebuild when the CLI reports it cannot
   update incrementally. Graphify disabled → SKIP the graph work and say so; never enable it.
2. Global namespace: the engine replaces the namespace keyed by the SAME stable `project.id`
   — replace, never append; **no duplicate namespaces may ever result**. The engine holds the
   portfolio lock and backs up `global-graph.json` before the replace; confirm the backup from
   its output. Held lock → report and stop.
3. Registry entry: refresh timestamps/metadata. Note: a registry-metadata-only change is NOT
   a project update — do not present it as one.

## Phase 5 — Report (chat + file)

Write `<project>\.amir\reports\global-graph-update.md` and summarize in chat. The report block
contains ALL of these items:

1. project id, name, directory
2. lifecycle, priority, current phase
3. freshness determination results (local graph / global namespace / project status, each
   current|stale|missing, with the timestamps compared)
4. progress: Confirmed / Estimated / Unknown — with the evidence source for any number shown
5. git state: branch, dirty yes/no, HEAD commit and date
6. blockers and next action (from portfolio.yaml — blank if unset)
7. local graph refresh result: incremental | full | skipped (reason) | failed (real error)
8. global namespace replace result: replaced | skipped | failed — with the backup path
9. registry entry changes (fields touched)
10. errors and warnings, verbatim where short
11. overall status line separating **completed / failed / skipped / blocked**

Never report overall success when any sub-step failed; a failed update keeps the previous
graph and the report must say so.
