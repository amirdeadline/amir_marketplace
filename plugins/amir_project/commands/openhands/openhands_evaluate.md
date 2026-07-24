---
description: Evaluate an OpenHands run against its acceptance criteria with fresh evidence
argument-hint: <run label>
---

# /amir:openhands_evaluate

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.openhands.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Load the run record from `.amir/state/openhands/runs/<label>/` (config, task, criteria, diff pointers). Missing criteria → the evaluation can only be descriptive; say so.
2. Re-verify NOW, independently of anything the agent or an earlier session claimed:
   - Apply/check out the run's diff in the relevant tree (prefer the worktree the run mounted).
   - Run the project's test suite and any task-specific checks; capture real output.
   - Check each acceptance criterion explicitly: met / not met / unverifiable, with the evidence line.
3. Also assess non-functional aspects: code quality of the diff (style rules of the project), scope creep (files touched beyond the task), and whether the sandbox policy held for the run (from the recorded inspect audit).
4. Write the evaluation to `.amir/state/openhands/runs/<label>/evaluation.md`: criteria table, test output summary, verdict.
5. Verdict wording: "criteria met (N/M) as of <date> on <commit>" — never a blanket "the agent solved it" without the criteria table. If evaluation could not run (environment broken), report exactly that instead of guessing.
