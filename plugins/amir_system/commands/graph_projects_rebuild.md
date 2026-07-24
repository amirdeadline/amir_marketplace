---
description: Full rebuild of the global portfolio graph from all registered projects — destructive to the graph store, confirmation required, valid-reason gated
---

# /amir:graph_projects_rebuild

Mutating and expensive: discards the current `global-graph.json` and rebuilds every
namespace from the registered projects. Project source code is never touched.

Engine:

```powershell
python "$env:USERPROFILE\.amir\bin\amirctl.py" portfolio-rebuild --confirm
```

The `--confirm` flag is passed ONLY after the user's explicit confirmation in chat — never
preemptively. Engine missing → report honestly and stop (there is no safe manual full
rebuild). Subcommand rejected → `--help` once, closest documented subcommand, say which.

## Valid reasons — require one before proposing a rebuild

A full rebuild is justified ONLY by one of these 6 reasons (ask which applies; if none does,
recommend `/amir:graph_projects_update` or `update_all` instead — they are cheaper and safer):

1. The global graph file is corrupted or no longer loads.
2. The graph schema/format changed (e.g. after an engine or graphify upgrade).
3. Namespace pollution — orphaned or duplicated namespaces that
   `/amir:graph_projects_validate` reports as unrepairable incrementally.
4. Suspected secret leakage into the graph — rebuild AFTER the exclusion rules are fixed, so
   the leak is not re-indexed.
5. Registry and graph are irreconcilably out of sync (ids renamed/re-registered in bulk).
6. Migration — projects moved or ids changed across the portfolio and per-project updates
   would leave stale remnants.

## Procedure

1. Establish the valid reason (above). State it back.
2. Show the plan: number of registered projects; which will be skipped (missing directory,
   graphify disabled — those become metadata-only namespace entries or are skipped per the
   engine's rules); estimated scope; that the engine backs up the current
   `global-graph.json` before discarding it and holds the **portfolio lock** for the whole
   run. Held lock → report and stop, never force.
3. Require explicit confirmation quoting the consequence: "the current global graph will be
   replaced; the previous one remains only as the backup at <path>". Cancel = zero side
   effects.
4. Run the engine with `--confirm`; show real output; failures per project are collected,
   not fatal to the run.
5. Verify: namespaces == registered graph-eligible ids, no duplicates, graph loads.
   Then run `/amir:graph_projects_validate` and include its result.
6. Report per-project results (rebuilt / skipped-with-reason / failed-with-error) and totals.
   **Never report overall success when some namespaces failed** — a partial rebuild is
   reported as partial, with the failures listed first.
