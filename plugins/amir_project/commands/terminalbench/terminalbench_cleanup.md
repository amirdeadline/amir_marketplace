---
description: Reclaim Terminal-Bench disk space - task images and scratch, never the evidence
argument-hint: [--images] [--run <run-id>]
---

# /amir:terminalbench_cleanup

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.terminal_bench.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Inventory and show before deleting: Terminal-Bench/Harbor task images with sizes (filter `docker images` on the benchmark's image prefixes), stopped task containers (`docker ps -a` filtered likewise), harness cache dirs, and per-run artifact sizes under `.amir/state/terminalbench/runs/`.
2. Default action (one confirmation): remove stopped task containers and task images — re-pullable caches:

```powershell
docker ps -aq --filter status=exited | ForEach-Object { docker rm $_ }   # scope to TB containers from the inventory, not blindly
docker image prune -f
```

   Remove images by explicit name:tag from the inventory list; never `docker system prune -a` (would hit other tools' images).
3. PRESERVE by default: run configs, results, logs, transcripts, evaluations, reports — the record of task/env/model/harness/result is the point of the exercise. Deleting a run requires `--run <run-id>` plus explicit per-run confirmation; offer archiving to a zip first.
4. Check limits compliance in passing: if any run directory exceeds the project's disk expectations, report it rather than silently deleting.
5. Report space reclaimed (docker system df and disk free, before/after), what was preserved, remaining footprint.
