---
description: Produce a reproducibility-grade report for a Terminal-Bench run
argument-hint: <run-id>
---

# /amir:terminalbench_report

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.terminal_bench.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Gather everything for `<run-id>` from `.amir/state/terminalbench/runs/<run-id>/` (config, results, evaluation, cost actuals). List gaps as gaps.
2. Report sections (write to `.amir/state/terminalbench/runs/<run-id>/report.md`):
   - **Setup**: dataset + version, exact task list, harness (Harbor/tb) version, docker/platform, isolation posture (no host credentials, container-scoped tasks), limits in force, date.
   - **System under test**: agent adapter, model id and settings, prompts/config references.
   - **Results**: pass rate with numerator/denominator, per-task table (passed / failed / unmeasured with class), failure-class breakdown from the evaluation.
   - **Cost**: tokens/dollars total and per passed task; wall time.
   - **Threats to validity**: small slice, single run, task-version drift, agent-harness fit, and the standing caveat: benchmark performance is not production safety — a high score licenses nothing about running the same agent against real systems.
   - **Reproduction**: exact commands and config to rerun.
3. Honor `generated_artifacts.commit_benchmark_results` from the manifest for whether the report is staged for commit; say which way it went.
4. Chat summary: headline rate with scope qualifier, cost, biggest caveat — five lines max.
