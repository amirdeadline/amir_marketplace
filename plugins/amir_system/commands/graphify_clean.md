---
description: Remove this project's Graphify output (graphify-out/) after showing exactly what will be deleted
---

# /amir:graphify_clean

## Tool-scope gate (mandatory, run FIRST)

1. Nearest ancestor with `.amir/project.yaml`; if none → STOP: "Not an Amir project — no
   .amir/project.yaml." Never clean anything outside an Amir project via this command.
2. Manifest check: run even if `project_tools.graphify.enabled` is false (cleaning output of a
   disabled tool is legitimate) — but state the enabled/disabled status in the plan.

## Procedure (destructive-action rule applies)

1. Scope: ONLY this project's `graphify-out/` directory. Never touch the graphify CLI, global
   graphify state, or any other project's output.
2. Show the deletion plan BEFORE deleting: full path of `graphify-out/`, total size, file count,
   and a top-level listing. State what is PRESERVED: graphify config (include/exclude), hooks,
   manifest settings — unless the user explicitly asks to remove config too.
3. Require explicit confirmation. Cleaning is irreversible for the graph data (a rebuild
   recreates it, but at rebuild cost — say roughly what a rebuild involves).
4. Delete only after confirmation:
   ```powershell
   Remove-Item -Recurse -Force "<project-root>\graphify-out"
   ```
5. Verify the directory is gone and report the actual result. If deletion partially failed
   (locked files etc.), list exactly what remains — never report a partial clean as complete.
