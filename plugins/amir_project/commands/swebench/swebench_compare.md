---
description: Compare two SWE-bench runs instance by instance, not just headline rates
argument-hint: <run-id A> <run-id B>
---

# /amir:swebench_compare

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.swe_bench.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Load both runs' configs and evaluator outputs from `.amir/state/swebench/runs/`. Refuse runs lacking preserved evaluator output — "I remember it scored 40%" is not comparable evidence.
2. Comparability check first: same dataset version and same instance set? If the instance sets differ, restrict the comparison to the INTERSECTION and say so; different datasets → refuse a numeric comparison, offer qualitative notes only.
3. Config delta: list every difference (model, scaffold, harness commit, workers, dates). More than one changed variable → state that attribution is confounded.
4. Instance-level comparison on the shared set: resolved-by-both, resolved-only-A, resolved-only-B, by-neither, error-in-either (excluded, listed). The flip lists (only-A / only-B) matter more than the aggregate — include instance ids and, for a few representative flips, a one-line note from the logs on why.
5. Aggregates with honest framing: resolution rates on the shared set, cost per resolved instance, wall time. Small subsets get a caveat: on 10 instances a 10% delta is one task — do not claim significance.
6. Write the comparison to `.amir/state/swebench/comparisons/<A>-vs-<B>.md` and summarize in chat with a criteria table, not a single winner headline.
