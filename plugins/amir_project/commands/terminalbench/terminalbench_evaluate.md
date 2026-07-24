---
description: Re-examine a Terminal-Bench run's results from preserved logs
argument-hint: <run-id> [task id]
---

# /amir:terminalbench_evaluate

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.terminal_bench.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Load the run's preserved artifacts from `.amir/state/terminalbench/runs/<run-id>/`. Terminal-Bench tasks are scored by their own in-container test scripts at run time, so evaluation here means verifying and analyzing preserved results, not re-scoring: missing logs → the run is unauditable; say so and stop.
2. Verify result integrity: the results file's per-task verdicts are consistent with the per-task logs (spot-check: a "passed" task's log shows its checks succeeding). Flag inconsistencies instead of trusting the summary.
3. Classify failures from logs (per task or for the task in `$ARGUMENTS`): agent error (wrong approach), environment/setup error (image or harness), limit hit (timeout/token cap — these are "unmeasured at this budget", not plain failures), flaky infrastructure. Quote the decisive log lines (redact anything credential-shaped).
4. If a task verdict is suspect, offer a targeted re-run of just that task (goes through `/amir:terminalbench_run` discipline with a new sub-run id) rather than editing results.
5. Write the analysis to `.amir/state/terminalbench/runs/<run-id>/evaluation.md`: verdict table with failure classes, notable transcripts, and corrected aggregate ("N passed, M failed, K unmeasured (limits/env)").
6. Chat summary keeps the honest denominator: exclude unmeasured tasks from the pass rate and say how many were excluded.
