---
description: Evaluate existing predictions with the official harness (no generation)
argument-hint: <run-id> [predictions path override]
---

# /amir:swebench_evaluate

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.swe_bench.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Resolve `<run-id>` and its predictions file (default `.amir/state/swebench/runs/<run-id>/predictions.jsonl`, or the override in `$ARGUMENTS`). Validate the file: parseable, one record per instance, non-empty `model_patch` fields; report malformed records instead of letting the harness fail cryptically.
2. Confirm dataset + instance list from the run config so evaluation matches what the predictions were generated for — evaluating Lite predictions against Verified is meaningless; refuse mismatches.
3. Run the official evaluator (docker; WSL 2 on Windows):

```
python -m swebench.harness.run_evaluation --dataset_name <dataset> --predictions_path <predictions> --max_workers <N> --run_id <run-id>
```

   To sanity-check the harness itself first, `--predictions_path gold` on the same instances must resolve ~100%; offer this when results look implausible.
4. Preserve the evaluator's full output (report JSON, per-instance logs) under the run dir; append an `evaluated_at` record with harness commit hash.
5. Report resolved/unresolved/error per instance and the aggregate rate, always suffixed with the exact dataset/subset and config. Distinguish "patch failed tests" from "environment error" — error instances are unmeasured, not failed; rerun or exclude them explicitly and say which.
