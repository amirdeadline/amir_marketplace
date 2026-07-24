---
description: Report Graphify status for the current Amir project (never rebuilds anything)
---

# /amir:graphify_status

## Tool-scope gate (mandatory, run FIRST)

1. Nearest ancestor with `.amir/project.yaml`; if none → STOP: "Not an Amir project — no
   .amir/project.yaml." (Status of a non-project is meaningless; do not run the CLI.)
2. This command may run even when `project_tools.graphify.enabled` is false — but then the FIRST
   line of the report must be "Graphify: DISABLED in manifest" and no graph operations beyond
   read-only inspection may occur.

## Report contents (read-only — NEVER build, update, or modify anything)

1. Manifest: `project_tools.graphify.enabled` value; `update_policy` if present.
2. CLI: `graphify --version` output (or "CLI not installed").
3. Hooks: `graphify hook status` output.
4. Graph output: does `graphify-out/graph.json` exist; file size; last-modified time.
5. Last build/update metadata: timestamp and source commit if recorded (project `.ai/status.md`
   or graphify-out metadata); otherwise "not recorded".
6. Staleness: compare graph mtime against latest source change (`git log -1 --format=%ci` or
   newest source file mtime). State the comparison honestly — "stale" / "fresh" / "cannot
   determine".
7. Configured ignored/excluded dirs (from graphify config + manifest excludes).
8. Output size on disk (`graphify-out/` total).

Explicit prohibition: NEVER silently rebuild or update because the graph looks stale. Only
recommend `/amir:graphify_update` or `/amir:graphify_build` and let the user decide.
