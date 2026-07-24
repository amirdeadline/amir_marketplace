---
description: Refresh the Amir component catalog and marketplace (git pull + regeneration + validation)
---

# /amir:update_catalog

## Engine

There is no single amirctl subcommand for this; the update is these explicit steps (each output
shown, each mutating step confirmed):
```powershell
# 1. locate the catalog (from ~/.amir/config.json "catalog_root")
# 2. pull the catalog repo
git -C <catalog_root> pull --ff-only
# 3. refresh the host marketplace registration
claude plugin marketplace update amir-marketplace
# 4. re-verify tooling + catalog integrity
python "$env:USERPROFILE\.amir\bin\amirctl.py" doctor
```
If `amirctl.py` is missing → report "amirctl engine not provisioned at
%USERPROFILE%\.amir\bin\amirctl.py" and stop after steps 2–3.

## What an update does (engine or supervised manual fallback)

1. `git pull` the marketplace repo (`E:\PC3_Shared\Plugins\amir_marketplace` on this machine —
   machine-local note) to get the latest catalog and plugin definitions. Show the actual pull
   output; a failed pull means the catalog was NOT updated — say so.
2. Validate/regenerate `catalog/catalog.json` (and regenerate `catalog/hosts.json` from it — the
   hosts file is derived, never hand-edited).
3. Refresh the Claude Code marketplace registration:
   `claude plugin marketplace update amir-marketplace` (or the currently documented equivalent —
   verify with `claude plugin --help` if it errors, and report the command actually used).
4. Report versions: catalog version/commit before → after, and any components added, removed,
   changed. If `catalog/catalog.json` still does not exist after the update, state that plainly —
   several commands (create/onboard/list_components) depend on it and stay degraded until it exists.

## Constraints

- Network access happens here (git pull) — announce it before running (security-secrets rule).
- Never modify any project's manifest during a catalog update; projects pick up changes on their
  next configure/validate.
- Honest reporting: no "catalog updated" claims unless the pull and regeneration actually
  succeeded.
