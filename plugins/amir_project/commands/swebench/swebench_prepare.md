---
description: Prepare a SWE-bench run - pick dataset and subset, pre-pull images, freeze config
argument-hint: [lite|verified|full] [subset size or instance ids]
---

# /amir:swebench_prepare

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.swe_bench.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Choose the dataset from `$ARGUMENTS`: `princeton-nlp/SWE-bench_Lite` (default, 300 instances), `princeton-nlp/SWE-bench_Verified` (500 human-verified), or full `princeton-nlp/SWE-bench`. Record the dataset name AND revision/version.
2. Subset policy (spec rule): start small. Default to a validation slice of 5-25 Lite instances (deterministic selection — sorted instance ids, take first N, record the exact list). Full runs are expensive and need explicit approval later at `/amir:swebench_run`.
3. Freeze the run config into `.amir/state/swebench/runs/<run-id>/config.yaml` BEFORE running: run id, dataset + version, instance id list, model under test and its config (temperature, context, scaffold/agent harness and its version), harness commit hash, date, planned max_workers, cost budget.
4. Environment: confirm disk headroom for the chosen subset's images; optionally pre-pull/build by running the gold smoke on 1-2 of the selected instances (confirm the download first).
5. Predictions format reminder: the harness consumes a JSON/JSONL of `{instance_id, model_name_or_path, model_patch}` — set up the path `.amir/state/swebench/runs/<run-id>/predictions.jsonl` where the generation step must write.
6. Report the frozen config and what remains manual (generating predictions with the model/agent under test is the project's pipeline; the harness only evaluates patches). Prepare ≠ run: make that explicit.
