---
description: Health check of the portfolio system itself — engine, registry, global graph, locks, backups, per-project state counts
---

# /amir:graph_projects_status

Read-only. Works anywhere.

Engine:

```powershell
python "$env:USERPROFILE\.amir\bin\amirctl.py" portfolio-status
```

Engine missing → report that first (it is itself a health finding), then assemble what you
can read-only from `%USERPROFILE%\.amir\registry\projects.yaml` and
`%USERPROFILE%\.amir\portfolio\`, clearly labeled as manually assembled. Subcommand rejected
→ `--help` once, closest documented subcommand, say which.

## Health list — check and report each item explicitly

1. **Engine** — `amirctl.py` present, `portfolio-*` subcommands available.
2. **Registry** — `projects.yaml` exists, parses, schema-valid; entry count; archived count.
3. **Portfolio store** — `%USERPROFILE%\.amir\portfolio\` exists with `graph\`, `reports\`,
   `locks\`.
4. **Global graph** — `graph\global-graph.json` exists, loads, namespace count; namespaces
   match registered ids (orphans/missing flagged, not repaired).
5. **Locks** — any lock files in `locks\`; age; a stale lock (older than a reasonable run) is
   flagged with the removal advice, but this command NEVER deletes a lock.
6. **Backups** — most recent global-graph backup: present, timestamp.
7. **Reports** — last `portfolio-report` generation time, if any.
8. **Per-project rollup** (from `portfolio-status` / registry, no directory scanning beyond
   registered roots): counts by lifecycle (active/paused/archived), and counts of
   missing-directory, invalid-manifest, graph-stale, status-stale, at-risk, needs-attention.
9. **Secret hygiene** — registry and portfolio store contain non-secret metadata only; if
   anything secret-like is spotted, warn without printing the value.

## Output

A short status block per item above (OK / WARN / FAIL with one-line evidence), then next
steps: `/amir:graph_projects_list needs-attention` for the project detail,
`/amir:graph_projects_update_all` for staleness, `/amir:graph_projects_validate` for a deep
integrity pass. Report **current / stale / missing / failed** as distinct states — never
blend them into a single health score.
