---
description: Generate or update .ai/architecture.md from the Graphify graph (review-gated, never overwrites manual decisions)
---

# /amir:graphify_architecture

## Tool-scope gate (mandatory, run FIRST)

1. Nearest ancestor with `.amir/project.yaml`; if none → STOP: "Not an Amir project — no
   .amir/project.yaml."
2. `project_tools.graphify.enabled` absent/false → STOP: Graphify disabled in the manifest.

## Procedure

1. Gather graph evidence from the project root: `graphify tree` (module containment),
   `graphify cluster-only` (community structure), `graphify query`/`graphify explain` for entry
   points, data flows, and external-system touchpoints. If the graph is missing/stale, say so;
   offer `/amir:graphify_update` first (user decides).
2. Draft/refresh `.ai/architecture.md` with these sections:
   - **Module map** — top-level modules/packages and responsibilities
   - **Dependency map** — who depends on whom (major edges only, cited)
   - **Entry points** — executables, servers, CLIs, exported APIs
   - **Data flows** — how data moves between modules and to storage
   - **External systems** — APIs, databases, queues, third-party services
   Cite `source_location` for structural claims; label anything inferred as INFERENCE.
3. MERGE, don't clobber: if `.ai/architecture.md` already exists, diff your draft against it.
   Sections containing manual decisions/ADR-style content are preserved verbatim. Show the user
   the proposed diff and require approval before writing — never replace manual decisions
   without review.
4. Stamp the generated sections with a header comment: generation date, graph build timestamp,
   and source commit, so staleness is auditable.
5. Report honestly what was updated, preserved, and skipped.
