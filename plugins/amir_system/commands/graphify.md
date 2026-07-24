---
description: Graphify hub — detect project, check manifest gate and graph health, then route to the right graphify operation
argument-hint: [question or operation]
---

# /amir:graphify

Interactive hub for the Graphify knowledge graph (system CLI `graphify`, pip package `graphifyy`,
verified v0.8.33 on this machine; installed under the Python 3.12 Scripts directory on PATH).

## Tool-scope gate (mandatory, run FIRST for this and every graphify_* command)

1. Find the project root: nearest ancestor of the current directory containing `.amir/project.yaml`.
2. If no `.amir/project.yaml` exists → STOP. Report: "Not an Amir project (no .amir/project.yaml).
   Graphify commands are project-scoped — run /amir:create_project or /amir:onboard_project first."
   Do not run any graphify CLI command.
3. Read `project_tools.graphify.enabled` from the manifest. If absent or `false` → STOP. Report
   that Graphify is disabled for this project and suggest enabling it via
   `/amir:configure_project` then `/amir:graphify_setup`. A globally installed CLI is NOT
   authorization to use it (tool-scope rule).

## Hub flow (after the gate passes)

1. Check the CLI: run `graphify --version`. If it fails, report the CLI is not installed
   (`pip install graphifyy`) — do not install anything without explicit approval.
2. Check graph health: does `graphify-out/graph.json` exist in the project? Compare its mtime
   against recent source changes to judge freshness (`graphify update` exists for incremental
   refresh). Report: built/missing, stale/fresh, last build time.
3. If `$ARGUMENTS` looks like a question about the codebase → treat as `/amir:graphify_query`.
   If it names an operation (setup/build/update/status/impact/architecture/clean/disable/explain)
   → route to that `/amir:graphify_{name}` command's procedure.
4. Otherwise present the operations menu with one-line descriptions and current applicability
   (e.g. "build — graph missing, recommended first step") and ask the user to pick one.

## Safety

- Never scan outside the project root without explicit approval.
- Never register the project in a global graph (`graphify global add`) without explicit approval.
- Never silently rebuild — building/updating is always announced first.
- Honest reporting: if a CLI call fails, show the actual error; never claim the graph is current
  after a failed update.
