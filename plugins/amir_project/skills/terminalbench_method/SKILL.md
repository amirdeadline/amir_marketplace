---
name: terminalbench_method
description: >-
  Terminal-Bench methodology for amir projects: Harbor harness, isolation and
  limits, result records, honest benchmark-vs-production framing.
---

# terminalbench_method

Terminal-Bench (https://github.com/laude-institute/terminal-bench, docs at tbench.ai) evaluates agents on realistic terminal tasks, each scored by its own tests inside a docker container. Gated on `project_tools.terminal_bench.enabled`.

## Harness versions (verified July 2026)

- **Terminal-Bench 2.0**: run via **Harbor** (`uv tool install harbor` / `pip install harbor`), dataset `terminal-bench/terminal-bench-2`, e.g. `harbor run -d terminal-bench/terminal-bench-2 -a <agent> -l 5`. Default for new work.
- **1.x legacy**: `pip install terminal-bench`, `tb run --dataset-name terminal-bench-core --dataset-version 0.1.1 ...` — only for comparability with old runs. Do not mix versions in one comparison; task definitions differ.
- Docker required; docs assume Linux/macOS — run inside WSL 2 on this machine.

## Isolation constraints (hard)

Tasks run in isolated containers. Never expose host credentials to task containers: provider API keys go to the harness process env only; no host directory mounts beyond what the harness defines; the agent under test gets no host network privileges beyond the task's own definition. Oracle runs (`-a oracle`) validate the environment without any model key.

## Limits (enforced, recorded)

Every run config declares wall-time per task and per run, token/cost budget, disk expectation, network policy. Exceeding a limit stops the run; over-budget partials are labeled partial. Limit-hit tasks are "unmeasured at this budget", excluded from pass rates with disclosure — not counted as failures.

## Record per task, always

task id / environment (image, dataset version) / model / harness version / result, plus transcripts and logs, preserved under `.amir/state/terminalbench/runs/<run-id>/`. Logs are captured before containers are cleaned — task containers are ephemeral. Runs without this record cannot be cited or compared.

## Evaluation precedence and framing (SPEC §13)

Project acceptance tests → project benchmarks → SWE/Terminal-Bench → human review. And the standing sentence for every report: benchmark performance is not production safety — passing terminal tasks in a sandbox licenses nothing about pointing the same agent at real systems with real credentials.

## Fallback

Harness or docker unavailable → evaluate the agent on project-defined terminal tasks in a controlled container you build, clearly labeled "project tasks, not Terminal-Bench"; never report improvised results under the benchmark's name.
