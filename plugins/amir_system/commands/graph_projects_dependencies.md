---
description: Cross-project dependency analysis — namespace-to-namespace edges from the global graph plus shared-technology overlap from the registry
argument-hint: [project_id]
---

# /amir:graph_projects_dependencies

Read-only. Optional `$ARGUMENTS` = one project id to focus on; empty = whole portfolio.
Sources: the global graph (`%USERPROFILE%\.amir\portfolio\graph\global-graph.json`) and the
registry (`projects.yaml` + each project's `.amir\portfolio.yaml` metadata). Registered
projects only — never scan the computer.

## Procedure

1. Load the global graph (via `graphify query` with the graph-path flag per
   `/amir:graph_projects_query`, or direct JSON traversal — say which). Check namespace
   freshness; stale namespaces are flagged in every finding that relies on them.
2. Extract **cross-namespace edges**: any edge whose endpoints live in different namespaces
   (imports, API calls, shared modules/packages, data contracts). Cite each as
   `namespaceA::node -> namespaceB::node`.
3. Extract **shared technology** from registry/manifest metadata: same languages, frameworks,
   package managers, infra components across projects (this is overlap, NOT a dependency —
   label it separately).

## Report — cover ALL of these

1. **Direct dependencies** per project: which registered projects it depends on, with the
   cited edges.
2. **Reverse dependencies**: which projects depend on it (impact direction).
3. **Shared libraries/APIs**: concrete shared code-level artifacts, with `namespace::node`
   citations.
4. **Shared technologies** (registry-derived overlap): languages/frameworks/infra in common —
   explicitly labeled "overlap, not a code dependency".
5. **Dependency clusters and cycles**: groups of mutually-connected projects; any circular
   cross-project dependency flagged prominently.
6. **Isolated projects**: registered projects with NO cross-namespace edges (also lists
   projects that are metadata-only registered and therefore invisible to graph analysis —
   named as such, never presented as "no dependencies").
7. **Coverage and freshness caveat**: which namespaces the analysis covered, which were
   stale/missing, and that findings from stale namespaces may be outdated.

Honesty: absence of an edge in the graph is evidence of "not indexed", not proof of "no
dependency" — state this caveat when the graph is stale or projects are metadata-only. Never
silently rebuild; recommend `/amir:graph_projects_update` where staleness hurt the analysis.
