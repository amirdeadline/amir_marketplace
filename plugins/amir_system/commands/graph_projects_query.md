---
description: Answer portfolio-level questions across all registered projects — right source per question type, namespace-cited answers, never invented progress
argument-hint: <question>
---

# /amir:graph_projects_query

Read-only. `$ARGUMENTS` is the question; if empty, ask for it.

## Source selection — pick per question type, and SAY which source you used

| Question is about | Authoritative source |
|---|---|
| Code, architecture, cross-project dependencies | global graph (`%USERPROFILE%\.amir\portfolio\graph\global-graph.json`) |
| Current project state / status | that project's `.ai\status.md` |
| Tasks | `.ai\tasks.md`, or Asana when `integrations.asana` is configured |
| Deadlines | `.amir\portfolio.yaml` / manifest, or Asana |
| Risks | `.ai\risks.md` |
| Decisions | `.ai\decisions.md` |
| References | `.ai\references.md` |
| Progress | explicit milestones / acceptance criteria ONLY — Confirmed vs Estimated vs Unknown; never inferred from graph size or commits |

Mixed questions use multiple sources; label which part of the answer came from which.

## Querying the global graph

1. Preferred: point `graphify query` at the global graph. The graph-path flag differs by
   version — check once:
   ```powershell
   graphify query --help
   ```
   and use the documented graph/path option (e.g. `--graph <path>`), passing
   `"$env:USERPROFILE\.amir\portfolio\graph\global-graph.json"`. Report which flag you used.
2. If no graph-path flag exists in the installed version, or the CLI is missing, fall back to
   reading `global-graph.json` directly and traversing nodes/edges yourself — and label the
   answer as coming from direct JSON traversal, not the CLI.
3. The graph may be stale: check the namespace timestamps of every project your answer relies
   on. Stale namespaces are flagged inline ("stale — last built <date>; run
   /amir:graph_projects_update <id>"). Never silently rebuild during a query.

## Answer rules

- Every graph-sourced claim cites its source as `namespace::node` (plus file path/line span
  when the node carries a source_location) so the user can verify.
- Every `.ai\`/portfolio-sourced claim cites the file (`<id> .ai\status.md`, etc.).
- Only registered projects are queried — never scan the computer for more.
- Unknown is a valid answer: if the sources do not contain it, say so; never fabricate
  progress, deadlines, or state (honest-execution rule).
- Never print secret values found anywhere; the graph must not contain any — if it appears
  to, warn and recommend `/amir:graph_projects_validate`.
