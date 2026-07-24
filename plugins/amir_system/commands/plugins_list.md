---
description: List all plugins/components available to enable in a project (name, source, summary) as a table
---

# /amir:plugins_list

Read-only. Works anywhere (inside or outside a project).

## Procedure

1. Gather the Amir catalog components (the primary source of project-enableable units):
   ```powershell
   python "$env:USERPROFILE\.amir\bin\amirctl.py" catalog-list --json
   ```
   If `amirctl.py` is missing, read `catalog/catalog.json` directly from the catalog root recorded in
   `%USERPROFILE%\.amir\config.json` (`catalog_root`). If neither is available, say so honestly and stop.
2. Gather host marketplaces (secondary source — any non-Amir plugins the user may have registered later):
   ```powershell
   claude plugin marketplace list
   ```
   For each marketplace other than `amir-marketplace`, note its plugins as additional rows (source = that
   marketplace). Do not error if the CLI is unavailable; report the catalog table alone and say which
   source was skipped.
3. If inside an Amir project (nearest ancestor with `.amir/project.yaml`), read the manifest so the
   table can mark what is already enabled here.

## Output — one table, exactly these columns

| Plugin / Component | Source / Marketplace | Summary |
|---|---|---|

- One row per amir_project component group (harness, aws, azure, xdr, docker, elastic, litellm, nmap,
  paloalto, prisma, qradar, sentinel, splunk, ssh, terraform, wireshark, serena, context7, semgrep,
  langfuse, openhands, worktrees, swebench, terminalbench) — Source: `amir_project @ amir-marketplace`,
  Summary: the catalog `description` (one line).
- One row per amir_system-provided capability that projects can opt into (`graphify`, `playwright`,
  `asana`) — Source: `amir_system @ amir-marketplace (system capability — availability ≠ project
  authorization)`.
- Rows for plugins from any other registered marketplace, if present.
- When inside a project, append a status marker to the first column: `(enabled here)` or
  `(blocked: <reason>)` using `amirctl catalog-resolve <id>` for components the user asks about —
  do not run resolve for every row unless asked (it is slower).

After the table, one line: how to enable → `/amir:project_add_plugin <name>` (inside a project) or
`/amir:create_project` / `/amir:onboard_project` first. Never enable anything from this command.
