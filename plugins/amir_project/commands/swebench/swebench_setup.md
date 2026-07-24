---
description: Install the official SWE-bench evaluation harness (docker-based; heavy)
---

# /amir:swebench_setup

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.swe_bench.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Resource statement (give it BEFORE asking to proceed)

Official harness (https://github.com/SWE-bench/SWE-bench) requirements: Docker, ~120 GB free disk for evaluation images, 16 GB+ RAM, 8+ CPU cores recommended; built for x86_64 (ARM experimental). The harness targets Linux/macOS — on this Windows machine run it inside WSL 2 with Docker Desktop WSL integration and ensure Docker Desktop's virtual disk can grow to the required size. Confirm the user accepts the disk/network cost before anything is installed or pulled.

## Install (after explicit confirmation; network access)

Official install is from source into a Python 3.10+ environment. Keep it OUT of the project tree — use `%USERPROFILE%\.amir\tools\SWE-bench` (documented tool cache location):

```powershell
git clone https://github.com/SWE-bench/SWE-bench.git "$env:USERPROFILE\.amir\tools\SWE-bench"
wsl -e bash -lc "cd /mnt/c/Users/<user>/.amir/tools/SWE-bench && python3 -m venv .venv && .venv/bin/pip install -e ."
```

(Adjust the WSL path to wherever the clone landed; a Linux-side clone inside WSL is preferable for performance — offer that option.)

## Health check (mandatory; cheap smoke, not a full run)

1. `python -m swebench.harness.run_evaluation --help` exits 0 inside the environment.
2. `docker info` works from the same context.
3. Gold-patch smoke test on ONE instance (downloads one image set — confirm first):

```
python -m swebench.harness.run_evaluation --dataset_name princeton-nlp/SWE-bench_Lite --predictions_path gold --max_workers 1 --instance_ids sympy__sympy-20590 --run_id amir-setup-check
```

   Pass = the run completes and reports the gold patch resolving the instance.
4. Record harness commit hash, Python version, and docker version in `.amir/state/swebench/setup.md`.

Report honestly per check; never claim "ready for benchmarks" without the smoke test having passed. Nothing outside the project is modified except the tool clone, its venv, and docker images (documented caches).
