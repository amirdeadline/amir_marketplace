---
description: Run or review evaluations (scores) on traced runs in Langfuse
argument-hint: [evaluator or score name] [trace/dataset scope]
---

# /amir:langfuse_evaluate

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.langfuse.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Confirm connectivity (`langfuse.auth_check()` true) — otherwise point to `/amir:langfuse_validate`.
2. Clarify what is being evaluated: a set of traces, a dataset run, or a single trace, from `$ARGUMENTS` or by asking. Do not evaluate "everything" implicitly.
3. Scoring paths, choose per project need and state the choice:
   - Programmatic scores via SDK (`langfuse.create_score(...)` / score APIs) computed locally from trace outputs — free, works in all modes.
   - LLM-as-judge evaluators configured in the Langfuse UI — note honestly: managed evaluators run on the Langfuse side and their availability depends on plan/self-hosted feature set (some evaluation features are gated on cloud plans or an enterprise license when self-hosting). Check the UI; report what is actually available rather than assuming.
4. If judging with an LLM locally, never send redacted-away proprietary content to the judge either; evaluate on the same redacted data that was traced.
5. Persist an evaluation summary (what was scored, scorer, aggregate results, run date) to `.amir/state/langfuse/evaluations.md` (append).
6. Report aggregate scores with counts, not vibes ("mean 0.82 over 40 traces"), and flag sample sizes too small to mean anything.
