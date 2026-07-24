---
description: Report Terminal-Bench harness, image cache, and run history state
---

# /amir:terminalbench_status

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.terminal_bench.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Checks (report each separately)

1. Harness: `harbor --help` (and `tb --help` if legacy 1.x was installed) exits 0; installed versions; install location from `.amir/state/terminalbench/setup.md`.
2. Docker: `docker info`; count/size of Terminal-Bench task images; free disk.
3. Run history: list `.amir/state/terminalbench/runs/` — run ids, dates, dataset + version, agent + model, pass counts from stored results; flag runs missing the task/env/model/harness/result record (uncitable).
4. Isolation posture: confirm no host credentials are configured to leak into task containers (no provider keys baked into images or global docker env; keys are per-run env only).
5. Limits config: the project's declared time/token/disk/network limits for runs (from manifest notes or run configs) — present or missing.

Read-only. Suggest `/amir:terminalbench_setup` or `/amir:terminalbench_cleanup` as remedies.
