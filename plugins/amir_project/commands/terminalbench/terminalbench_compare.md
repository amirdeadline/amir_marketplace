---
description: Compare two Terminal-Bench runs task by task with confound checks
argument-hint: <run-id A> <run-id B>
---

# /amir:terminalbench_compare

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.terminal_bench.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Load both runs' configs and preserved results from `.amir/state/terminalbench/runs/`. Runs without preserved results are not comparable — refuse with the reason.
2. Comparability: same dataset AND dataset version AND task set? Compare only the intersection of tasks; different dataset versions → refuse numeric comparison (task definitions change between versions), offer qualitative notes.
3. Config delta: list every difference (agent, model, harness version, limits, concurrency, dates). Multiple changed variables → attribution is confounded; say so.
4. Task-level comparison on the shared set: passed-by-both, only-A, only-B, by-neither, unmeasured-in-either (limit/env — exclude from rates, list ids). For a few flips, pull the one-line cause from each run's evaluation/logs.
5. Aggregates: pass rate on the shared measured set, cost per passed task, mean task wall time. Small-slice caveat: with 5-10 tasks, one flip dominates the rate — do not claim significance.
6. Write to `.amir/state/terminalbench/comparisons/<A>-vs-<B>.md`; chat summary as a criteria table, no single-winner headline when results are mixed.
