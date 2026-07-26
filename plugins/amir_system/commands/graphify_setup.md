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

## Output locations (mandatory)

- **Graphify output** defaults to `.amir/graphify-out/` (manifest
  `project_tools.graphify.output_directory`). Never write `graphify-out/` at the project root.
- **AI docs** (architecture, status, decisions, handoff, …) stay under `.ai/` — never at the
  project root and never inside `graphify-out/`.
- Before every `graphify` CLI call in this project, set the env var so the vendor CLI honors
  the Amir path:
  ```powershell
  $env:GRAPHIFY_OUT = (Select-String -Path .amir\project.yaml -Pattern 'output_directory:' |
    ForEach-Object { ($_ -split ':',2)[1].Trim().Trim('"') } | Select-Object -First 1)
  if (-not $env:GRAPHIFY_OUT) { $env:GRAPHIFY_OUT = ".amir/graphify-out" }
  ```

## Procedure

1. Ensure the manifest has `project_tools.graphify.output_directory: .amir/graphify-out` (set it
   if missing or still the legacy root `graphify-out`). If a legacy root `graphify-out/` exists,
   offer to move it into `.amir/graphify-out/` (show plan; require confirmation) — do not leave
   two live graphs.
2. Verify the CLI: `graphify --version` (expected v0.8.33 line). If missing, report it and stop;
   suggest `pip install graphifyy` but do not run installs without approval.
3. Run the project-scoped platform installs from the project root, one per enabled host in the
   manifest (with `GRAPHIFY_OUT` set as above):
   - `graphify install --project --platform claude`
   - `graphify install --project --platform cursor`
   Only for platforms the manifest enables. Show each command's real output.
4. After Cursor install, rewrite `.cursor/rules/graphify.mdc` so every `graphify-out/` path
   becomes `.amir/graphify-out/` (and mention `$env:GRAPHIFY_OUT`). The vendor installer still
   writes the root path — Amir owns the corrected rule.
5. Write/update the graphify include/exclude configuration so it honors the manifest's exclude
   list (plus `.gitignore`). Never configure paths outside the project root. Exclude `.amir/`
   and `.ai/` from indexing sources.
6. Ensure `.amir/graphify-out/` is in `.gitignore` UNLESS the manifest explicitly says the
   project commits its graph output (`commit_generated_graph: true` /
   `generated_artifacts.commit_graphify_output: true`). Also ignore any leftover root
   `graphify-out/` so a mistaken vendor default cannot be committed.
7. Hook policy: `graphify install` may auto-register PreToolUse hooks. Read the manifest's
   `project_tools.graphify.update_policy`:
   - `auto` / non-`manual` → keep hooks; verify with `graphify hook status`.
   - `manual` → remove them: `graphify hook uninstall`; verify with `graphify hook status`.
8. Report exactly what was installed/configured, with command outputs. If any step failed, list
   it under FAILED — do not summarize a partial setup as complete.

Never run `graphify global add` or otherwise register this project globally without explicit
user approval.
