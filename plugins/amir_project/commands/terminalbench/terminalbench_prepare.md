---
description: Prepare a Terminal-Bench run - dataset, task slice, agent config, limits frozen
argument-hint: [dataset, default terminal-bench-2] [task count or task ids]
---

# /amir:terminalbench_prepare

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.terminal_bench.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Dataset from `$ARGUMENTS`: default `terminal-bench/terminal-bench-2` (Harbor). Legacy: `terminal-bench-core` v0.1.1 via `tb`. Record dataset id AND version.
2. Task slice: start small (spec rule) — default first 5-10 tasks (`-l N`) or an explicit task-id list; record the exact selection deterministically. Full-suite runs need approval at run time.
3. Agent under test: which agent adapter (e.g. a built-in Harbor agent, `oracle` for environment checks, or the project's own agent) plus model id and settings. Freeze into `.amir/state/terminalbench/runs/<run-id>/config.yaml`: run id, dataset+version, task list, agent, model, harness version, limits, date.
4. Limits (mandatory in the config, enforced at run): wall-time per task and per run, token/cost budget, disk quota expectation, network policy for task containers (default: only what the benchmark's own task definitions require; the agent gets no extra host network privileges and NEVER host credentials).
5. Model keys: identify which provider env vars the chosen agent needs; verify they are available in the user's environment WITHOUT printing them; they will be passed only to the harness process at run time.
6. Optionally pre-pull images for the selected tasks (confirm the download). Report the frozen config and the estimated cost envelope. Prepare ≠ run.
