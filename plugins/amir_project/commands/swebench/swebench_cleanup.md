---
description: Reclaim SWE-bench disk space - images and scratch, never the evidence
argument-hint: [--images] [--run <run-id>]
---

# /amir:swebench_cleanup

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.swe_bench.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Inventory and show BEFORE deleting anything: SWE-bench docker images with sizes (`docker images` filtered on the harness's image prefixes, e.g. `sweb.eval`/`sweb.base`/`sweb.env`), dangling build layers, harness scratch/log temp dirs, and per-run artifact sizes under `.amir/state/swebench/runs/`.
2. Default action (after one confirmation): remove evaluation docker images and dangling layers — they are re-buildable caches:

```powershell
docker images --format "{{.Repository}}:{{.Tag}}" | Select-String '^sweb' | ForEach-Object { docker rmi $_.ToString() }
docker image prune -f
```

3. PRESERVE by default, forever: run configs, predictions, evaluator outputs, reports (the reproducibility evidence). Deleting a run's artifacts requires naming the run (`--run <run-id>`) and an explicit per-run confirmation; even then, offer to zip it to an archive location first.
4. Never run `docker system prune -a` here — it would destroy images belonging to other tools (OpenHands, Terminal-Bench, the project's own images). Scope every removal to SWE-bench image names.
5. Report space reclaimed (before/after `docker system df` and disk free), what was preserved, and the remaining footprint.
