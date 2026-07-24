---
description: Disable Graphify for this project (uninstall per platform, update manifest+lock, preserve output)
---

# /amir:graphify_disable

## Tool-scope gate (mandatory, run FIRST)

1. Nearest ancestor with `.amir/project.yaml`; if none → STOP: "Not an Amir project — no
   .amir/project.yaml."
2. If `project_tools.graphify.enabled` is already false/absent, report that Graphify is already
   disabled and only offer the leftover-cleanup steps below (skip what's already done).

## Procedure (destructive-action rule: show plan, confirm, then act)

1. Present the disable plan: which platform integrations will be uninstalled, that the manifest
   and lock will be updated, and that `graphify-out/` will be PRESERVED (offer optional archive
   to `.amir/backups/<timestamp>/graphify-out/` or later `/amir:graphify_clean`). Confirm.
2. From the project root, per platform enabled in the manifest (CLI v0.8.33):
   ```powershell
   graphify uninstall --platform claude
   graphify uninstall --platform cursor
   ```
   Also remove project hooks: `graphify hook uninstall`, verify with `graphify hook status`.
   Show real outputs; if a subcommand rejects a flag, run `graphify uninstall --help` once and
   use the documented form, reporting what you actually ran.
3. Update `.amir/project.yaml`: set `project_tools.graphify.enabled: false` (preserve the rest
   of the graphify block for easy re-enable). Then refresh deterministically:
   `python "$env:USERPROFILE\.amir\bin\amirctl.py" generate` followed by `lock`; if amirctl is
   missing, edit carefully and recommend `/amir:validate_project` after.
4. Strict boundaries: NEVER uninstall or modify the graphify CLI itself, global graphify state,
   or any other project.
5. Report per-step results honestly (done / failed / skipped), including preserved artifacts and
   how to re-enable later (`/amir:configure_project` → `/amir:graphify_setup`).
