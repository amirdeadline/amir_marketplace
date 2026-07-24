---
description: Edit the current project's Amir manifest (.amir/project.yaml) safely — change selections, re-render, re-validate
argument-hint: [component or setting to change]
---

# /amir:configure_project

## Preconditions

1. Nearest ancestor with `.amir/project.yaml`; if none → STOP: "Not an Amir project — run
   /amir:create_project or /amir:onboard_project first."
2. Engine: the deterministic path is a pipeline of amirctl subcommands (there is no single
   `configure` subcommand): after editing the manifest, run
   `python "$env:USERPROFILE\.amir\bin\amirctl.py" catalog-resolve <selected ids...>` to check
   the new selection, then `validate`, then `generate --dry-run` (show the plan), then on
   confirmation `generate` and `lock`. If `amirctl.py` is missing at `%USERPROFILE%\.amir\bin\`,
   say so honestly ("amirctl engine not provisioned on this machine") and offer a careful manual
   edit with mandatory `/amir:validate_project` afterwards.

## Procedure

1. Read the current manifest and summarize the current configuration (enabled components, hosts,
   tools, permissions).
2. Determine the requested change from `$ARGUMENTS` or by asking. For component enable/disable,
   show the catalog entry (`catalog/catalog.json` — if missing, direct the user to
   `/amir:update_catalog`): description, dependencies, required credentials, network/secret
   access, security implications.
3. Resolve consequences BEFORE editing: new dependencies pulled in, conflicts, credentials that
   will be required, network/secret permissions that would change. Enabling network or secret
   access ALWAYS requires an explicit separate confirmation (security-secrets rule).
4. Show the change plan (manifest diff, files that will be re-rendered, installs/uninstalls) and
   confirm.
5. Apply via the engine: update manifest → update `.amir/components.lock.json` → re-render host
   files (Claude + Cursor) → run validation.
6. Report actual results per component: changed / rendered / validated / failed / needs-credential.
   Never report a component enabled unless its health check actually passed. Secrets are
   referenced by name only — never displayed, never written into the manifest.
