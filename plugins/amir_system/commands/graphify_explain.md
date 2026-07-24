---
description: Explain a file, module, or symbol using the Graphify graph (evidence-cited)
argument-hint: <file | module | symbol>
---

# /amir:graphify_explain

## Tool-scope gate (mandatory, run FIRST)

1. Nearest ancestor with `.amir/project.yaml`; if none → STOP: "Not an Amir project — no
   .amir/project.yaml."
2. `project_tools.graphify.enabled` absent/false → STOP: Graphify disabled in the manifest;
   offer plain repo inspection instead (clearly labeled).

## Procedure

1. `$ARGUMENTS` names the target (file path, module, or symbol). If empty, ask.
2. From the project root run (CLI v0.8.33):
   ```powershell
   graphify explain "<target>"
   ```
   Enrich with `graphify path`/`graphify tree` when the explanation needs
   dependency/containment context, and `graphify cluster-only` for community-level placement.
3. Present: what the target is, what depends on it, what it depends on, which community/cluster
   it belongs to, and notable god-node relationships — each point citing `source_location`.
4. Distinguish evidence classes explicitly: (a) graph evidence with citations, (b) live-file
   confirmation, (c) your inference. Never blur these.
5. If the graph is missing or the target isn't in it, say so and fall back to reading the actual
   file(s), labeled as live inspection. Recommend `/amir:graphify_update` if staleness is likely.
   Never rebuild silently.
