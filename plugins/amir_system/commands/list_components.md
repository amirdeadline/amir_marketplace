---
description: Browse the Amir component catalog (catalog/catalog.json) â€” details, dependencies, credentials, security notes
argument-hint: [group or component-id or search term]
---

# /amir:list_components

## Data source

The marketplace catalog at `catalog/catalog.json` (repo `E:\PC3_Shared\Plugins\amir_marketplace`
when working inside it, or the cached copy the installed plugin references). Prefer the engine:
```powershell
python "$env:USERPROFILE\.amir\bin\amirctl.py" catalog-list
```
If `amirctl.py` is missing, read the catalog file directly (read-only). If `catalog/catalog.json`
itself does not exist, STOP and say: "The component catalog is not present â€” run
/amir:update_catalog to fetch/generate it." Do not invent components from memory.

## Behavior

- No arguments: grouped listing (harness, aws, azure, docker, graphify, serena, context7,
  semgrep, langfuse, openhands, worktrees, swebench, terminalbench, security tools, etc. â€” as the
  catalog defines) with one-line descriptions and host support.
- `$ARGUMENTS` = group name: list that group's components in full.
- `$ARGUMENTS` = component id: full detail card â€”
  description, why useful, supported hosts, supported operating systems, dependencies
  (requires / optional_dependencies / conflicts_with), required executables, required
  credentials (NAMES only â€” never values), network_access, secret_access, security implications,
  performance implications, min/max host version, health check.
- `$ARGUMENTS` = other text: substring search across ids and descriptions.

## Constraints

- Read-only: this command never installs, enables, or modifies anything. To act on a component,
  point to `/amir:configure_project` (existing project) or `/amir:create_project`.
- If the current directory is an Amir project, annotate each listed component with its state in
  THIS project (enabled / available / not selected) from `.amir/project.yaml` â€” clearly
  distinguishing installed-at-system-scope vs enabled-in-project (they are not the same thing).
