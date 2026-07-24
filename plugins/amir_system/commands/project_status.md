---
description: Health report for the current Amir project — manifest, components, tools, docs, validation state
---

# /amir:project_status

## Preconditions

1. Nearest ancestor with `.amir/project.yaml`; if none → STOP: "Not an Amir project. Use
   /amir:list_projects to see registered projects, or /amir:create_project /
   /amir:onboard_project to set one up."
2. Engine (preferred):
   ```powershell
   python "$env:USERPROFILE\.amir\bin\amirctl.py" validate
   python "$env:USERPROFILE\.amir\bin\amirctl.py" drift
   ```
   If `amirctl.py` is missing, build the report manually from the files below and label it
   MANUAL (no deterministic checksums).

## Report sections (read-only)

1. **Identity**: project name, root, type, manifest schema version, registry entry present?
2. **Hosts**: cursor_enabled / claude_enabled; rendered files present for each.
3. **Components**: per enabled component — state distinctions made explicit:
   installed_at_system_scope vs available_to_project vs enabled_in_project vs authorized_write
   vs configured vs healthy. Health = its catalog health_check actually passing NOW (run it;
   if you don't run it, print "not checked", never "healthy").
4. **Tools**: Graphify (enabled? graph built? stale?), worktrees, Serena/Context7/Semgrep/etc.
   as the manifest declares.
5. **Credentials**: required credential NAMES per component and whether each is present
   (env/secrets file EXISTS — never read or print values).
6. **Docs**: `ai/` files present (status, tasks, decisions, risks, architecture,
   context_handoff) with last-modified dates.
7. **Validation**: last validation timestamp/result from lock/registry; current drift signal if
   the engine ran. Recommend `/amir:validate_project` if stale.
8. **Git**: branch, dirty/clean, worktrees list (if a git repo).

End with a short prioritized list of concrete issues found (or "no issues detected by the checks
that actually ran" — enumerate any checks skipped).
