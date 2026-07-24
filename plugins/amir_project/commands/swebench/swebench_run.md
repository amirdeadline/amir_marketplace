---
description: Execute a prepared SWE-bench run (generation + evaluation) with cost guards
argument-hint: <run-id>
---

# /amir:swebench_run

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.swe_bench.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Load the frozen config for `<run-id>` from `.amir/state/swebench/runs/<run-id>/config.yaml`; refuse to run without one (point to `/amir:swebench_prepare`). Refuse silent config edits — changes mean a NEW run id.
2. Cost guard: estimate model cost (instances × expected tokens × price) and evaluation time; show the estimate. Full-dataset or Verified-500 runs REQUIRE explicit user approval here even if prepare was approved. No expensive full runs on a nod.
3. Generation phase: run the project's model/agent pipeline over the instance list to produce `predictions.jsonl` (each: instance_id, model_name_or_path, model_patch). Record actual tokens/cost per instance as the pipeline reports them. If the project pipeline cannot produce patches, stop and say what is missing — do not fabricate predictions.
4. Evaluation phase (official harness, reproducible docker envs):

```
python -m swebench.harness.run_evaluation --dataset_name <dataset> --predictions_path <predictions.jsonl> --max_workers <N> --run_id <run-id> --instance_ids <ids...>
```

   Choose `max_workers` conservatively (harness guidance: well under CPU count, they recommend fewer than 28 and ~0.75 × cores). On Windows execute inside WSL 2.
5. Preserve EVERYTHING under `.amir/state/swebench/runs/<run-id>/`: predictions, the harness `evaluation_results`/logs output, per-instance test output, tokens/cost actuals. Patches and evaluator output are the evidence of record — never discard them.
6. Report: resolved / unresolved / error counts with instance ids, cost actual vs estimate, wall time. State the scope honestly: "N% resolved on <subset> of <dataset> with <model+scaffold>" — SWE-bench measures patch-level issue resolution on historical Python repos; it does not measure every capability, and a subset score is not the leaderboard score.
