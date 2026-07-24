---
description: Run a defined task in the OpenHands sandbox and capture the outcome
argument-hint: <task description or task file path>
---

# /amir:openhands_run

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.openhands.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Require a concrete task from `$ARGUMENTS` (inline text or a path to a task file in the project). Refuse vague tasks ("improve the code") — ask for acceptance criteria first; a run without criteria cannot be evaluated.
2. Start or reuse a policy-conformant sandbox via `/amir:openhands_sandbox` (same checks apply). One task per sandbox session — no task piggybacking, so results stay attributable.
3. Cost/resource guard: state the expected model usage and runtime resources; get confirmation before launch if the task looks long-running.
4. Launch the task (UI session, or headless/CLI mode if the project set it up per official docs). Record start time, task text, model, and image tags in `.amir/state/openhands/runs/<label>/`.
5. While running: do not interfere with the project working tree outside the sandbox. All agent edits happen on the mounted project per `project_mount` policy — if `read_write`, warn the user that the REAL project tree is being modified and recommend a dedicated worktree (`/amir:worktree_create`) as the mount when the worktrees group is enabled.
6. On completion: collect the agent's diff (`git status` / `git diff` in the mounted tree), test results if the task ran tests, and the event log. Store pointers under the run directory.
7. Report honestly: what the agent changed, whether acceptance criteria were verified (run the project's tests yourself — the agent claiming success is not evidence), cost if reported. "Task complete" only after your own verification passes.
