---
description: Execute a prepared Terminal-Bench run in isolated containers with limits
argument-hint: <run-id>
---

# /amir:terminalbench_run

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.terminal_bench.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Load the frozen config for `<run-id>` from `.amir/state/terminalbench/runs/<run-id>/config.yaml`; refuse without it (point to `/amir:terminalbench_prepare`). Config changes = new run id.
2. Cost/scope guard: show estimated cost (tasks × expected agent tokens) and wall time; full-suite runs require explicit approval now.
3. Isolation preflight: tasks run in the harness's docker containers — verify no host credential material can reach them: provider keys go to the HARNESS process env only (the agent client runs harness-side); never mount host dirs into task containers beyond what the harness itself defines; never disable the harness's isolation flags.
4. Execute (Harbor, TB 2.0; inside WSL 2 on this machine):

```
harbor run -d terminal-bench/terminal-bench-2 -a <agent> -m <model> [task selection flags per config] 
```

   Legacy 1.x: `tb run --agent <agent> --model <model> --dataset-name terminal-bench-core --dataset-version 0.1.1 [--n-concurrent N]`. Keep concurrency within the config's limits.
5. Enforce limits during the run: stop the run if wall-time or cost budget from the config is exceeded (record the overrun and partial results as partial — clearly labeled).
6. Preserve everything under `.amir/state/terminalbench/runs/<run-id>/`: the harness's output/log directory (copy it in), per-task results, agent transcripts, token/cost actuals, plus the standard record task/env/model/harness/result per task.
7. Report: passed/failed/error task counts with ids, cost actual vs estimate, wall time. Frame honestly: "N/M tasks passed on <dataset vX> with <agent+model>" — a terminal benchmark score is not evidence of production safety or general capability.
