---
description: Compare two OpenHands runs (configs, diffs, outcomes) side by side
argument-hint: <run label A> <run label B>
---

# /amir:openhands_compare

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.openhands.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Resolve both run labels from `$ARGUMENTS` against `.amir/state/openhands/runs/`. If either is missing its recorded config or outcome, say so — an unrecorded run cannot be compared, only recalled anecdotally.
2. Compare configurations first and list every difference: task text, model, image tags, sandbox policy snapshot, network state, mount mode. If more than one variable differs, warn that outcome differences cannot be attributed to a single cause.
3. Compare outcomes with evidence: acceptance criteria verified (per your own test runs at the time, from the run records), size and shape of the diffs (files touched, lines), test pass/fail counts, wall time, model cost if recorded, notable failure modes from the event logs.
4. Verdict format: a table of criteria × runs, then a short judgment naming which run did better ON WHICH criteria — avoid a single "winner" claim when results are mixed.
5. Append the comparison to `.amir/state/openhands/comparisons.md`. No re-running here; if the user wants a fair rematch with one variable changed, point to `/amir:openhands_run`.
