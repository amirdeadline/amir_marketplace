---
description: Set up Graphify for the current Amir project (platform installs, include/exclude config, hooks per manifest policy)
---

# /amir:graphify_setup

## Tool-scope gate (mandatory, run FIRST)

1. Find the nearest ancestor with `.amir/project.yaml`. If none → STOP: "Not an Amir project
   (no .amir/project.yaml) — run /amir:create_project or /amir:onboard_project first."
2. If `project_tools.graphify.enabled` is absent or false → STOP: Graphify is disabled in the
   manifest. Setup does not bypass the gate — the user must first enable it via
   `/amir:configure_project`. Global CLI availability is not authorization.

## Procedure

1. Verify the CLI: `graphify --version` (expected v0.8.33 line). If missing, report it and stop;
   suggest `pip install graphifyy` but do not run installs without approval.
2. Run the project-scoped platform installs from the project root, one per enabled host in the
   manifest:
   - `graphify install --project --platform claude`
   - `graphify install --project --platform cursor`
   Only for platforms the manifest enables. Show each command's real output.
3. Write/update the graphify include/exclude configuration so it honors the manifest's exclude
   list (plus `.gitignore`). Never configure paths outside the project root.
4. Ensure `graphify-out/` is in `.gitignore` UNLESS the manifest explicitly says the project
   commits its graph output.
5. Hook policy: `graphify install` may auto-register PreToolUse hooks. Read the manifest's
   `project_tools.graphify.update_policy`:
   - `auto` → keep hooks; verify with `graphify hook status`.
   - `manual` → remove them: `graphify hook uninstall`; verify with `graphify hook status`.
6. Report exactly what was installed/configured, with command outputs. If any step failed, list
   it under FAILED — do not summarize a partial setup as complete.

Never run `graphify global add` or otherwise register this project globally without explicit
user approval.
