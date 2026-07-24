---
description: Impact analysis — what is affected by changing given files/symbols (graphify affected + graph traversal)
argument-hint: <changed files or symbols>
---

# /amir:graphify_impact

## Tool-scope gate (mandatory, run FIRST)

1. Nearest ancestor with `.amir/project.yaml`; if none → STOP: "Not an Amir project — no
   .amir/project.yaml."
2. `project_tools.graphify.enabled` absent/false → STOP: Graphify disabled in the manifest;
   offer a best-effort manual impact estimate via Grep only if the user asks, clearly labeled
   as non-graph inference.

## Procedure

1. Determine the change set: `$ARGUMENTS` (files/symbols), or if empty, propose using the
   current git diff (`git status --short` / `git diff --name-only`) and confirm.
2. From the project root run (CLI v0.8.33):
   ```powershell
   graphify affected <targets>
   ```
3. Deepen with graph traversal where useful: `graphify path` between changed nodes and critical
   entry points, `graphify tree` for containment context.
4. Present the impact report in tiers:
   - **Directly affected** (graph edges from changed nodes) — with `source_location` citations.
   - **Transitively affected** (traversal depth ≥ 2) — cited.
   - **Suspected** (your inference beyond graph evidence) — explicitly labeled INFERENCE.
   Never blend graph evidence with inference; the distinction is mandatory.
5. Recommend which tests/validation should run for the affected set. Recommendations are
   advisory — do not run them unprompted.
6. If the graph is stale relative to the change set, warn that impact results may be incomplete
   and recommend `/amir:graphify_update` first. Never update silently.
