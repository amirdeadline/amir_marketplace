---
description: Instrument or inspect hierarchical traces for this project's agent runs
argument-hint: [trace id to inspect | "instrument" to add tracing]
---

# /amir:langfuse_trace

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.langfuse.enabled` is not `true`, stop and point to `/amir:configure_project`. If mode is `disabled`, stop — no telemetry.

## Inspect mode (`$ARGUMENTS` is a trace id or empty)

1. Load creds from `%USERPROFILE%\.amir\secrets\langfuse.env` (never print values). Use the SDK/API to fetch the trace (or the most recent project traces when no id given).
2. Present the hierarchy with per-span: name, duration, model, tokens in/out, cost, retries, tool calls, error states. Link to the UI (`<LANGFUSE_HOST>/project/.../traces/<id>`).

## Instrument mode (`$ARGUMENTS` starts with "instrument")

1. Add tracing to the project's agent/LLM code using the official SDK (`pip install langfuse`; `@observe` decorator or explicit spans). Follow the standard amir hierarchy so runs are comparable: Task → Planning → Context retrieval → Architecture agent → Development agent → Test execution → QA agent → Security scan → Final validation. Name spans exactly by stage.
2. Record per span: model, latency, token counts, cost, retries, tool calls.
3. Privacy defaults (non-negotiable without explicit user opt-out): do NOT capture full proprietary prompts/completions — store truncated/redacted versions or hashes; apply the redaction patterns from the `langfuse_tracing` skill; honor the configured sampling rate instead of tracing 100% by default.
4. Show the user the instrumentation diff before applying; run the project's tests after applying (instrumentation must not change behavior).
5. Verify: execute one instrumented run and confirm the trace arrives with the expected hierarchy before reporting success.
