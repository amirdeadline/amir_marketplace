---
description: Disable/remove a plugin or component from the current project (preserves data by default)
argument-hint: <component-or-plugin name>
---

# /amir:project_disable_plugin

Mutating. Requires an Amir project (nearest ancestor with `.amir/project.yaml`; if none → STOP).
If no argument was given, show the /amir:project_list_plugins table and ask which one to disable.

## Procedure

1. Confirm the target is currently enabled in this project (manifest — same three categories as
   /amir:project_add_plugin). If it is not enabled, say so and stop (nothing to do).
2. Show what disabling will change BEFORE doing it:
   - the manifest diff (component removed from `plugins.amir_project.components`, or
     `project_tools.<tool>.enabled: false`, or `system_capabilities.<name>.allowed: false`)
   - the rendered files that will be deleted (stale-cleanup list from
     `python "$env:USERPROFILE\.amir\bin\amirctl.py" generate --dry-run` after the edit)
   - what is PRESERVED by default: project data/state (`graphify-out/`, `.serena/`,
     `.amir/state/<tool>/`, worktrees, findings, traces). Deleting data is a separate, explicit
     opt-in per the destructive-action rule.
3. On confirmation, apply: edit manifest → `generate` (stale cleanup removes only amir-generated
   files) → `lock` → show real outputs.
4. Tool-specific teardown (only when the target is that tool and only with confirmation):
   graphify → follow /amir:graphify_disable; external-marketplace plugin installed at project scope
   → `claude plugin uninstall <p>@<m> --scope project`.
5. Report honestly: disabled (manifest), removed files (count), preserved data (paths), and how to
   re-enable (`/amir:project_add_plugin <name>` — sub-config was preserved in the manifest where the
   schema allows, e.g. the graphify block stays with `enabled: false`).

Never touch other projects, user scope, or the system CLI of any tool.
