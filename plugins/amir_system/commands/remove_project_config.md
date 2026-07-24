---
description: Remove Amir-managed configuration from the current project (backup first; preserves everything user-owned)
---

# /amir:remove_project_config

## Preconditions

1. Nearest ancestor with `.amir/project.yaml`; if none → STOP: "Not an Amir project — nothing to
   remove."
2. Engine:
   ```powershell
   python "$env:USERPROFILE\.amir\bin\amirctl.py" remove-project-config
   ```
   If `amirctl.py` is missing → report it honestly; a supervised manual removal is possible but
   riskier — proceed only with the full plan/confirm flow below and recommend re-provisioning
   the engine.

## Procedure (destructive-action rule — strict order)

1. **Backup first.** Copy the entire Amir-managed set (`.amir/`, generated Cursor/Claude files,
   rendered plugin subset) into `.amir-removal-backup-<timestamp>/` OUTSIDE `.amir/` (since
   `.amir/` itself is being removed) or a user-chosen location. Verify the backup exists before
   anything is deleted.
2. **Show the deletion plan**: every file/directory to be removed, identified as Amir-managed by
   the lock file and generated-file headers. Explicitly list what is PRESERVED:
   - unrelated Cursor config (user's own `.cursor/rules`, other commands, unrelated
     `.cursor/mcp.json` entries — merge-remove only Amir entries, never the whole file)
   - unrelated Claude config (user's own `.claude/` content)
   - project docs (`ai/` stays unless the user explicitly asks to remove it)
   - all source code, git history, everything not created by the Amir renderer
3. **Confirm explicitly.** No deletion before a clear yes.
4. Execute; deregister the project from `%USERPROFILE%\.amir\registry\projects.json`.
5. **Never uninstall Graphify globally**, never touch the graphify CLI, never remove
   user-scope plugins — this command's scope ends at the project boundary.
6. Report per-item: removed / preserved / failed, plus the backup location and how to restore.
