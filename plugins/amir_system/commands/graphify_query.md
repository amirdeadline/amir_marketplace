---
description: Answer a question about the codebase from the Graphify knowledge graph (cites source locations)
argument-hint: <question>
---

# /amir:graphify_query

## Tool-scope gate (mandatory, run FIRST)

1. Nearest ancestor with `.amir/project.yaml`; if none → STOP: "Not an Amir project — no
   .amir/project.yaml." Answer from ordinary repo inspection instead ONLY if the user asks.
2. `project_tools.graphify.enabled` absent/false → STOP: Graphify disabled in the manifest;
   offer to answer via plain repo inspection instead (clearly labeled as such).

## Procedure

1. Require a question: `$ARGUMENTS` is the query text. If empty, ask for it.
2. From the project root run the CLI (v0.8.33 verified subcommands):
   ```powershell
   graphify query "<question>"
   ```
   For relationship/path questions, `graphify path` and `graphify tree` are also available;
   use whichever fits the question shape.
3. Answer FROM THE GRAPH results. Every claim sourced from the graph must cite its
   `source_location` (file path and, when available, line span) so the user can verify.
4. Fallback: if the graph is missing, stale, or the query returns nothing useful, say so
   explicitly, then fall back to direct repo inspection (Grep/Read) — and label which parts of
   the answer came from the graph vs. live inspection. Never present inference as graph evidence.
5. Never silently rebuild or update the graph as part of a query; if staleness hurt the answer,
   recommend `/amir:graphify_update`.
