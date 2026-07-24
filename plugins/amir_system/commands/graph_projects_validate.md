---
description: Deep integrity validation of the portfolio system — registry, graph, namespaces, freshness, locks, secret leakage; findings only, repairs proposed not applied
---

# /amir:graph_projects_validate

Read-only by default: this command FINDS problems and proposes fixes; it applies nothing
without the user choosing a fix explicitly.

Engine:

```powershell
python "$env:USERPROFILE\.amir\bin\amirctl.py" portfolio-validate
```

Engine missing → report that as finding #1, then perform the checks below manually
(read-only) and label the run as manual. Subcommand rejected → `--help` once, closest
documented subcommand, say which.

## Validation list — check ALL, report each with OK / WARN / FAIL + evidence

1. **Registry integrity** — `projects.yaml` parses; required fields per entry; stable ids
   unique; no duplicate directories.
2. **Directory reachability** — each registered root exists and its `.amir\project.yaml`
   parses; the manifest `project.id` matches the registry id (mismatch = FAIL).
3. **Global graph integrity** — `global-graph.json` loads; internal structure sane.
4. **Namespace consistency** —
   - no **duplicate namespaces**;
   - no **orphaned namespaces** (namespace with no active registry entry);
   - no missing namespaces (graph-eligible registered project without one — metadata-only
     registrations are exempt and listed as such).
5. **Secret leakage scan** — search graph node/edge content and the registry for
   secret-shaped values (key/token/password patterns, `.env` content, credential paths).
   A hit is CRITICAL: warn WITHOUT printing the value, identify the namespace, and recommend
   fixing exclusions then `/amir:graph_projects_rebuild` (valid reason 4). Also verify no
   secret stores (`%USERPROFILE%\.amir\secrets\`) were ever indexed.
6. **Freshness bookkeeping** — every namespace has a build timestamp and source commit;
   timestamps are not in the future; stale namespaces listed (stale is a WARN, not a FAIL —
   but an UNLABELED stale state is a FAIL of honest bookkeeping).
7. **Missing `.ai\` files** — per reachable project: which of the 9 workspace files
   (project.md, status.md, tasks.md, decisions.md, risks.md, architecture.md,
   references.md, changelog.md, context_handoff.md) are absent; missing `.ai\status.md`
   is flagged prominently (it feeds every status view).
8. **Portfolio.yaml presence/validity** — `.amir\portfolio.yaml` exists per project, parses,
   and contains no fabricated-looking progress (progress with no evidence source = WARN).
9. **Locks** — stale lock files in `%USERPROFILE%\.amir\portfolio\locks\` (age, holder).
   Never delete a lock from this command.
10. **Backups** — a global-graph backup exists from the most recent mutating run.
11. **Report hygiene** — `%USERPROFILE%\.amir\portfolio\reports\` contains no secret values.

## Output

Findings grouped CRITICAL / WARN / INFO, each with: what, where (project id / file path /
namespace), evidence, and the proposed fix command (`graph_projects_update`, `_remove`,
`_rebuild`, `/amir:repair_project`, manual step). End with a one-line honest verdict:
"valid", "valid with warnings (N)", or "invalid (N critical)" — never soften a critical
finding into a warning.
