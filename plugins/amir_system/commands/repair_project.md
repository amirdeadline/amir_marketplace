---
description: Repair drift in the current Amir project — regenerate missing/modified generated files; never changes selections
---

# /amir:repair_project

## Preconditions

1. Nearest ancestor with `.amir/project.yaml`; if none → STOP: "Not an Amir project — nothing to
   repair."
2. Engine:
   ```powershell
   python "$env:USERPROFILE\.amir\bin\amirctl.py" repair
   ```
   If `amirctl.py` is missing → report honestly that the deterministic repair engine is not
   provisioned; offer only a diagnosis (via the manual checks in `/amir:validate_project`) —
   do NOT hand-regenerate renderer-owned files without the engine, as that creates worse drift.

## Scope (strict)

- Repair fixes DRIFT ONLY: missing generated files, generated files whose checksum no longer
  matches `.amir/components.lock.json`, stale generated-file headers, broken junctions/paths.
- Repair NEVER changes component selections, never enables/disables tools, never edits the
  manifest's choices. Selection changes belong to `/amir:configure_project`.
- User-owned files are sacred: if a drifted file lacks the Amir generated-file header, treat it
  as user-modified — show it and ask (overwrite / keep / back up and overwrite) instead of
  silently clobbering.

## Procedure

1. Run drift detection first (engine `validate` or its repair dry-run). Show the repair plan:
   each file to be recreated/rewritten and why.
2. Confirm before overwriting anything that currently exists (destructive-action rule; pure
   re-creation of missing files may proceed after plan approval).
3. Execute, then re-run validation to prove the repair worked.
4. Report per-file: repaired / skipped (user-modified, kept) / failed — with evidence. Never
   report the project healthy unless post-repair validation actually passed.
