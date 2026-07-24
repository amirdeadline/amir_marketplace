---
description: List, search, and inspect registered Amir projects from the user registry (concise PM view)
argument-hint: [search-term | status | clean]
---

# /amir:list_projects

Operate on the project registry at `%USERPROFILE%\.amir\registry\projects.yaml` — the ONE
registry shared with the portfolio-graph commands (`/amir:graph_projects_*`). There is no
second project list anywhere; both views read the same file.

## Engine

The deterministic engine is `python "%USERPROFILE%\.amir\bin\amirctl.py"`. Prefer it:

```powershell
python "$env:USERPROFILE\.amir\bin\amirctl.py" registry-list
# or, equivalently for the same registry with portfolio filters:
python "$env:USERPROFILE\.amir\bin\amirctl.py" portfolio-list
```

If `amirctl.py` does not exist, report honestly: "The amirctl engine is not installed at
`%USERPROFILE%\.amir\bin\amirctl.py` — the amir_system tools have not been provisioned on this
machine yet." Then fall back to reading `projects.yaml` directly (read-only) if it exists. If the
expected subcommand name is rejected, run the script with `--help` once, use the closest documented
subcommand, and say which one you used.

## Behavior

This is the CONCISE project-management view. For the full graph-health view (graph freshness,
confirmed/estimated progress, git state, blockers, the 5 registration states), use
`/amir:graph_projects_list` — same registry, wider table.

- No arguments: table of all registered projects — id, name, root, type, lifecycle, priority,
  cursor_enabled, claude_enabled, last_validation, last_opened, enabled components (count or ids).
- `$ARGUMENTS` = search term: filter by name/root/type substring.
- `$ARGUMENTS` = `status`: additionally check each registered root — flag missing directories
  (root no longer exists) and moved projects (manifest found elsewhere is NOT assumed; only flag,
  never scan the whole computer). Offer per-entry: re-register, remove stale entry, open, or run
  `/amir:validate_project` against it. For graph staleness specifically, point to
  `/amir:graph_projects_list needs-attention`.
- `$ARGUMENTS` = `clean`: propose removal of stale entries; require explicit confirmation before
  modifying the registry (destructive-action rule). Removing a registry entry for a
  graph-registered project should go through `/amir:graph_projects_remove` so the global graph
  namespace and registry stay consistent.

## Constraints

- Registry holds non-secret metadata only. If you see anything secret-like in it, warn the user —
  never print the value.
- NEVER scan the filesystem beyond the registered roots.
- Do not duplicate manifest contents into the registry; the manifest at `manifest_path` stays the
  source of truth.
- If the registry file is missing or empty, say so plainly — do not invent projects.
