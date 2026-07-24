---
description: Validate the Langfuse integration end to end with a live test trace
---

# /amir:langfuse_validate

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.langfuse.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Validation matrix (run all applicable; pass/fail per line)

1. Manifest mode is one of hosted | self_hosted | disabled; `disabled` → report "intentionally disabled" and stop (that is a valid state, not a failure).
2. Secrets: env file exists outside the repo; defines LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY / LANGFUSE_HOST; no `sk-lf-` value appears anywhere in tracked project files (grep the repo; report file:line on a hit as CRITICAL).
3. Server reachable: self_hosted → `docker compose ps` healthy plus HTTP health endpoint answers; hosted → the region host answers.
4. Auth: `langfuse.auth_check()` returns true from a short Python run that loads the env file.
5. Round trip: send one test trace named `amir-validate-<timestamp>`, flush, then fetch it back via the API. Pass only if it is retrievable.
6. Privacy config: redaction/truncation of prompt content is configured per project policy; sampling rate is set; warn (not fail) if tracing captures full prompts with proprietary source and no recorded user opt-in.
7. State dir: `.amir/state/langfuse/` exists for local records.

Verdict "healthy" requires 2-5 passing (plus 7). Report failing checks precisely with remedies (`/amir:langfuse_setup`, `/amir:langfuse_start`).
