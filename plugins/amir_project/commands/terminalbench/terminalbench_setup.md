---
description: Install the Terminal-Bench harness (Harbor for TB 2.0; docker-isolated tasks)
---

# /amir:terminalbench_setup

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.terminal_bench.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Which harness (verified July 2026 against https://github.com/laude-institute/terminal-bench and https://www.tbench.ai/docs)

- **Terminal-Bench 2.0** runs on **Harbor**, the current official harness: `uv tool install harbor` or `pip install harbor`; dataset `terminal-bench/terminal-bench-2`. This is the default for new work.
- **Terminal-Bench 1.x (legacy)** uses the `terminal-bench` package and the `tb` CLI (`pip install terminal-bench`; dataset `terminal-bench-core` v0.1.1). Install only if the project explicitly needs 1.x comparability.

Both require Docker running. The docs do not document native Windows execution — plan to run inside WSL 2 with Docker Desktop integration and state this to the user.

## Install (after explicit user confirmation; network access)

This machine has no uv; either install uv first (official: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`) and then `uv tool install harbor`, or use pip in a dedicated venv outside the project tree (`%USERPROFILE%\.amir\tools\harbor-venv`):

```powershell
python -m venv "$env:USERPROFILE\.amir\tools\harbor-venv"
& "$env:USERPROFILE\.amir\tools\harbor-venv\Scripts\pip.exe" install harbor
```

Model API keys for agents under test are env vars set at run time by the user (e.g. provider keys) — never written into project files by this command.

## Health check (mandatory)

1. `harbor --help` exits 0 (from the venv or uv tool shim).
2. `docker info` succeeds in the execution context (WSL).
3. Oracle smoke on a tiny slice (downloads task images — confirm first): run the oracle solver on a few tasks, per official quick start:

```
harbor run -d terminal-bench/terminal-bench-2 -a oracle -l 5
```

   Pass = tasks execute in containers and the oracle resolves them (oracle failures indicate a broken environment, not a bad model).
4. Record harness version (`harbor --version` / pip show), dataset id, and docker version in `.amir/state/terminalbench/setup.md`.

Report per honest-execution; "ready" only after the oracle smoke passes. Writes outside the project: the harness install, docker images, and Harbor's own cache only.
