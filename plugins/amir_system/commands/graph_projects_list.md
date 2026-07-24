---
description: Portfolio table of all registered projects with graph health, freshness, progress, and git state (registry only — never scans the computer)
argument-hint: [filter]
---

# /amir:graph_projects_list

Read-only. Works anywhere. Source of truth is the shared registry
`%USERPROFILE%\.amir\registry\projects.yaml` — the SAME registry `/amir:list_projects` uses.
**NEVER scan the filesystem for projects. Registry entries only.** The only paths you may touch
are the registered project directories themselves (to check reachability/freshness) and the
portfolio store `%USERPROFILE%\.amir\portfolio\`.

## Engine

```powershell
python "$env:USERPROFILE\.amir\bin\amirctl.py" portfolio-list
python "$env:USERPROFILE\.amir\bin\amirctl.py" portfolio-list <filter>
```

If `amirctl.py` is missing, report honestly: "The amirctl engine is not installed at
`%USERPROFILE%\.amir\bin\amirctl.py`." Then fall back to reading `projects.yaml` and each
project's `.amir\portfolio.yaml` / `.ai\status.md` directly (read-only), and label the output
as manually assembled. If the subcommand name is rejected, run the script with `--help` once,
use the closest documented subcommand, and say which one you used.

## Filters (`$ARGUMENTS`)

`all` (default) · `active` · `paused` · `archived` · `at-risk` · `stale` · `graph-stale` ·
`missing-directory` · `needs-attention`. An unknown filter → show this list and ask; do not
guess from fuzzy text.

## Output table — ALL of these columns, per project

| Column | Source |
|---|---|
| Name | registry / `.amir\portfolio.yaml` |
| Id | stable `project.id` from `.amir\project.yaml` (never folder name) |
| Directory | registry |
| Lifecycle | portfolio.yaml (`active`/`paused`/`archived`) |
| Priority | portfolio.yaml (blank = unset — show blank, never invent) |
| Health | engine health flag / blockers evaluation |
| Current phase | portfolio.yaml `phase.current` |
| Confirmed progress | ONLY milestone/acceptance-criteria evidence; blank = unknown |
| Estimated progress | labeled estimate; blank allowed |
| Last project update | newest of `.ai\status.md` mtime / portfolio.yaml timestamps |
| Last graph update | project `graphify-out\graph.json` + global namespace timestamp |
| Graph freshness | current / stale / missing (see detections) |
| Git branch | `git -C <dir> rev-parse --abbrev-ref HEAD` (skip silently-failing repos: mark `n/a`) |
| Git dirty | `git -C <dir> status --porcelain` non-empty → yes |
| Blockers | portfolio.yaml `health.blockers` |
| Next action | portfolio.yaml `next_action` |
| Graphify enabled | manifest `project_tools.graphify.enabled` |
| Cursor enabled | registry/manifest |
| Claude enabled | registry/manifest |
| Asana ref | portfolio.yaml `integrations.asana.project_gid` — ONLY when configured, else blank |

Wide table: if the host renders poorly, split into two stacked tables (identity+PM columns,
then graph+git columns) — never drop columns.

## Detections (flag, never repair from this command)

- **Missing directory** — registered root no longer exists. Flag only; never search for it.
- **Invalid manifest** — `.amir\project.yaml` unreadable/unparseable.
- **Stale graph** — local graph mtime older than latest source change, or global namespace
  built from an older commit than the project HEAD.
- **Missing `.ai\status.md`**.
- **Status older than threshold** — `.ai\status.md` older than the project's
  `reporting.status_stale_after_days` (default 14).
- **Source changed after graph** — commits/file changes newer than the last graph build.

## The 5 per-project states — always distinguish explicitly

1. **Registered** — entry exists in `projects.yaml`.
2. **Project reachable** — directory exists and manifest parses.
3. **Graph available** — a namespace for this id exists in the global graph.
4. **Graph current** — that namespace is not stale versus the project source.
5. **Project status current** — `.ai\status.md` exists and is within the staleness threshold.

A project can be Registered without being reachable, and Graph-available without being
Graph-current — never collapse these into one "OK/broken" flag.

After the table: one line per detection group with the affected projects and the fix command
(`/amir:graph_projects_update <dir|id>`, `/amir:graph_projects_remove`, `/amir:onboard_project`).
For the concise PM view without graph columns, cross-reference `/amir:list_projects`.

## Constraints

- Registry holds non-secret metadata only; if anything secret-like appears, warn — never print it.
- Empty/missing registry → say so plainly; do not invent projects.
- Honest reporting: values you could not determine are shown as blank/`unknown`, never guessed.
