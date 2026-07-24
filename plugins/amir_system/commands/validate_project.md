---
description: Validate the current Amir project — manifest schema, lock checksums, naming, hosts, MCP, isolation, drift
---

# /amir:validate_project

## Preconditions

1. Nearest ancestor with `.amir/project.yaml`; if none → STOP: "Not an Amir project — nothing to
   validate here."
2. Engine: run the validator deterministically:
   ```powershell
   python "$env:USERPROFILE\.amir\bin\amirctl.py" validate
   ```
   If `amirctl.py` is missing → report "amirctl engine not provisioned at
   %USERPROFILE%\.amir\bin\amirctl.py — full deterministic validation unavailable", then perform
   the best-effort manual checks below and clearly label the report as MANUAL/PARTIAL. If the
   subcommand differs, check `--help` once and report the command actually used.

## Validation coverage (what the engine checks; mirror these manually if falling back)

- Manifest validates against `schemas/project-manifest.schema.json` (schema v2).
- `.amir/components.lock.json` checksums match rendered files (drift detection).
- Naming compliance: all commands `/amir:` + snake_case; no hyphen/underscore twins.
- No duplicate command names within or across rendered sets.
- Host compatibility of every enabled component (supported_hosts, OS, host version).
- MCP server definitions well-formed; referenced executables exist.
- Secret REFERENCES only — a validation failure if any secret VALUE appears in manifest, lock,
  or rendered files (report the location, never the value).
- Graphify health (if enabled): CLI present, output state, hook state.
- Project isolation: no Amir-generated file writes outside the project root.

## Reporting

Present the drift/validation report grouped by severity (errors / warnings / info), with exact
file paths. State clearly: PASSED / FAILED / PARTIAL(manual). Never claim a check ran if it
didn't. For fixable drift, point to `/amir:repair_project`; for selection changes, to
`/amir:configure_project`. Update `last_validation` in the registry only when validation truly ran.
