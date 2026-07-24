---
description: Report SWE-bench harness, image cache, and run history state
---

# /amir:swebench_status

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.swe_bench.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Checks (report each separately)

1. Harness installed: the tool dir exists (`%USERPROFILE%\.amir\tools\SWE-bench` or the path in `.amir/state/swebench/setup.md`); `python -m swebench.harness.run_evaluation --help` exits 0 in its environment; harness commit hash vs upstream (informational).
2. Docker: `docker info`; count and total size of SWE-bench evaluation images (`docker images` filtered on the sweb prefix); free disk vs the ~120 GB guidance.
3. Run history: list `.amir/state/swebench/runs/` — run ids, dates, dataset, subset size, resolved counts from stored evaluator output.
4. Pending artifacts: predictions files present without evaluation results (point to `/amir:swebench_evaluate`).
5. Reproducibility record intact: each run dir has benchmark version, task set, model + harness config, token/cost record. Flag runs missing metadata — they cannot be cited.

Read-only. Suggest `/amir:swebench_setup` or `/amir:swebench_cleanup` as needed.
