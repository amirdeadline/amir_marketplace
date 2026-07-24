---
description: Remove a project from the portfolio graph — never touches source code; shows scope, confirms, preserves local config by default, archives registry history
argument-hint: project_directory | project_id
---

# /amir:graph_projects_remove

Mutating (registry + global graph). **This command NEVER deletes project source code, and
never deletes anything outside `%USERPROFILE%\.amir\portfolio\`, the registry entry, and —
only with the extra flag and extra confirmation — the project's local `graphify-out\`.**

Argument: a directory or a registered project id. If `$ARGUMENTS` is empty, show the
registered projects (`portfolio-list`) and ASK which one — one question, explicit answer;
never fuzzy-match.

Engine:

```powershell
python "$env:USERPROFILE\.amir\bin\amirctl.py" portfolio-remove <dir|id> [--keep-registry|--archive-registry] [--remove-local-graph]
```

Engine missing → report honestly; the only fallback is a supervised manual edit of
`projects.yaml` + namespace removal from `global-graph.json` with a shown diff and a manual
backup first. Subcommand rejected → run `--help` once, use the closest documented name, say so.

## Procedure

1. Resolve the target to a registry entry (by id, or by directory → id). Not registered →
   report and stop; nothing to do.
2. Show EXACTLY what will be removed and what will be kept, before asking anything:
   - **Removed (default)**: the project's namespace from
     `%USERPROFILE%\.amir\portfolio\graph\global-graph.json`; its active registry entry.
   - **Kept (default)**: the project directory and ALL source code; its local graphify config
     and local `graphify-out\` graph; its `.amir\` and `.ai\` files; registry HISTORY —
     the entry is archived (default `--archive-registry`), not erased.
   - **Optional flags**:
     - `--keep-registry` — remove only the graph namespace; leave the registry entry active.
     - `--archive-registry` — the default; entry moves to the archive section with a
       removal timestamp.
     - `--remove-local-graph` — ALSO delete the project's local `graphify-out\`. This is the
       only variant that touches the project directory; it requires its OWN second
       confirmation naming the exact path to be deleted (destructive-action rule).
3. Require explicit confirmation of the shown plan. Cancel = zero side effects.
4. Execute via the engine. It acquires the portfolio lock and backs up `global-graph.json`
   before writing; confirm the backup path from its output. Held lock → report and stop.
5. Verify after removal:
   - the namespace is gone from the global graph;
   - **all other namespaces are untouched** (list count and ids before/after);
   - registry state matches the chosen flag (archived / kept / removed).
6. Write `<project>\.amir\reports\global-graph-removal.md` (only if the project directory
   still exists and is reachable — otherwise note in chat why the report was skipped):
   timestamp, id, flags used, what was removed/kept, backup path, verification results.
7. Report honestly: **completed / failed / skipped / blocked** as separate categories. A
   failed namespace removal means the previous global graph (or its backup) is still
   authoritative — never claim removal that did not verify.
