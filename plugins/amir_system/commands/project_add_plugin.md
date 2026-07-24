---
description: Add an available plugin/component to the current project (resolve, render, lock, validate)
argument-hint: <component-or-plugin name>
---

# /amir:project_add_plugin

Mutating. Requires an Amir project (nearest ancestor with `.amir/project.yaml`; if none → STOP and
point to /amir:onboard_project). If no argument was given, first show the /amir:plugins_list table
and ask which one to add — one question, then proceed.

## Procedure

1. Identify what the name refers to:
   - an **amir_project component group** (harness, aws, …, terminalbench) → manifest list
     `plugins.amir_project.components`
   - a **project tool** (graphify, serena, context7, semgrep, langfuse, openhands, git_worktrees,
     swe_bench, terminal_bench) → `project_tools.<tool>.enabled: true` (plus its sub-config defaults
     from the manifest schema)
   - a **system capability** (asana, playwright) → `system_capabilities.<name>.allowed: true`
   - a plugin from another registered marketplace → `claude plugin install <p>@<m> --scope project`
     (Claude Code only; tell the user Cursor has no per-project install for external plugins)
   Unknown name → show the closest matches from /amir:plugins_list and stop.
2. BEFORE editing anything, run the resolver and show the result:
   ```powershell
   python "$env:USERPROFILE\.amir\bin\amirctl.py" catalog-resolve <ids...>
   ```
   (pass the full prospective selection: current components + the addition). If it reports BLOCKED
   (missing executable/credential/permission/conflict), show the exact block chain and what would
   fix it (e.g. grant network permission in the manifest, install uv, set a credential env var).
   Ask whether to apply the fix where it is a manifest permission; STOP for anything requiring
   installs or credentials until the user confirms per the security rules.
3. Edit `.amir/project.yaml` (minimal diff — show it), then run in order, showing real output:
   ```powershell
   python "$env:USERPROFILE\.amir\bin\amirctl.py" validate
   python "$env:USERPROFILE\.amir\bin\amirctl.py" generate --dry-run
   # confirm plan with the user, then:
   python "$env:USERPROFILE\.amir\bin\amirctl.py" generate
   python "$env:USERPROFILE\.amir\bin\amirctl.py" lock
   ```
4. Post-checks: run the component's catalog `health_check` when its prerequisites are present;
   report per the honest-execution rule (a component is "added" when rendered+locked; "healthy"
   only when its health check passed — never conflate the two).
5. If amirctl is missing, refuse the deterministic path and offer only a supervised manual edit
   followed by /amir:validate_project.

Never add a dependency that expands security permissions silently — surface every transitive
addition the resolver reports.
