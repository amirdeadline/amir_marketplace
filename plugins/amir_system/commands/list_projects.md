---
description: List, search, and inspect registered Amir projects from the user registry
argument-hint: [search-term | status | clean]
---

# /amir:list_projects

Operate on the project registry at `%USERPROFILE%\.amir\registry\projects.json`.

## Engine

The deterministic engine is `python "%USERPROFILE%\.amir\bin\amirctl.py"`. Prefer it:

```powershell
python "$env:USERPROFILE\.amir\bin\amirctl.py" registry-list
```

If `amirctl.py` does not exist, report honestly: "The amirctl engine is not installed at
`%USERPROFILE%\.amir\bin\amirctl.py` â€” the amir_system tools have not been provisioned on this
machine yet." Then fall back to reading `projects.json` directly (read-only) if it exists. If the
expected subcommand name is rejected, run the script with `--help` once, use the closest documented
subcommand, and say which one you used.

## Behavior

- No arguments: table of all registered projects â€” id, name, root, type, cursor_enabled,
  claude_enabled, last_validation, last_opened, enabled components (count or ids).
- `$ARGUMENTS` = search term: filter by name/root/type substring.
- `$ARGUMENTS` = `status`: additionally check each registered root â€” flag missing directories
  (root no longer exists) and moved projects (manifest found elsewhere is NOT assumed; only flag,
  never scan the whole computer). Offer per-entry: re-register, remove stale entry, open, or run
  `/amir:validate_project` against it.
- `$ARGUMENTS` = `clean`: propose removal of stale entries; require explicit confirmation before
  modifying the registry (destructive-action rule).

## Constraints

- Registry holds non-secret metadata only. If you see anything secret-like in it, warn the user â€”
  never print the value.
- NEVER scan the filesystem beyond the registered roots.
- Do not duplicate manifest contents into the registry; the manifest at `manifest_path` stays the
  source of truth.
- If the registry file is missing or empty, say so plainly â€” do not invent projects.
