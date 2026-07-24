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

CRITICAL cache rule (learned 2026-07-24): `claude plugin update` refreshes the installed cache ONLY
when the plugin.json version CHANGED — same-version updates report "already at the latest version"
and silently keep stale files, while `claude plugin details` reads the source and masks the gap.
After any catalog content change: bump `version` in the plugin's plugin.json AND the three
marketplace manifests, then `claude plugin update amir_system@amir-marketplace`, then verify the new
`~/.claude/plugins/cache/amir-marketplace/amir_system/<version>/` contains the change. A restart of
Claude Code is required for the running session to pick it up.
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
