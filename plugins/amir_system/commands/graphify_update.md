---
description: Incremental Graphify graph update for the current Amir project
argument-hint: [--force]
---

# /amir:graphify_update

## Tool-scope gate (mandatory, run FIRST)

1. Nearest ancestor with `.amir/project.yaml`; if none → STOP: "Not an Amir project — no
   .amir/project.yaml." No graphify CLI calls.
2. `project_tools.graphify.enabled` absent/false → STOP: Graphify disabled in the manifest.

## Procedure

1. Precondition: `graphify-out/graph.json` must exist. If it doesn't, say the graph was never
   built and point to `/amir:graphify_build` — `update` cannot create a graph from nothing.
2. From the project root run:
   ```powershell
   graphify update
   ```
   Pass `--force` only if the user supplied it in `$ARGUMENTS` (forces refresh even when
   graphify considers the graph current).
3. Show the CLI's actual output. On success, record in the report (and in
   `ai/status.md` if the project keeps one): update timestamp and the current source commit
   (`git rev-parse HEAD` if a git repo).
4. HONESTY RULE: if `graphify update` exits non-zero or reports errors, the graph is NOT current.
   Report the failure verbatim, keep the previous timestamp, and never claim freshness. Suggest
   `--force` or a full `/amir:graphify_build` as recovery options — but do not run them
   unprompted.
