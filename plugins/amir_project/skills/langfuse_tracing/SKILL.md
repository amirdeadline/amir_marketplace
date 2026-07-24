---
name: langfuse_tracing
description: >-
  Langfuse tracing methodology for amir projects: opt-in telemetry, standard
  trace hierarchy, redaction and sampling, hosted vs self-hosted trade-offs.
---

# langfuse_tracing

Langfuse (https://langfuse.com) records LLM/agent observability: traces, spans, tokens, cost, evaluations, datasets. Gated on `project_tools.langfuse.enabled` with `mode: hosted | self_hosted | disabled`.

## Consent and privacy — the governing rules

- Telemetry is NEVER auto-enabled. Explicit user approval precedes any tracing, with a plain statement of what gets recorded.
- Default capture: model, latency, tokens, cost, retries, tool calls, span structure. NOT captured by default: full proprietary prompts/completions — store redacted/truncated content or hashes. Full-content capture requires a recorded user opt-in.
- Redaction: strip credential patterns (api keys, tokens, connection strings), file paths outside the project, and user PII from any captured content before it leaves the process. Sampling is configurable; use it — 100% tracing of a chatty agent is cost without insight.
- Keys are env references only: `LANGFUSE_PUBLIC_KEY` (pk-lf-...), `LANGFUSE_SECRET_KEY` (sk-lf-...), `LANGFUSE_HOST` (SDK v3 also reads `LANGFUSE_BASE_URL`; set both). Stored in `%USERPROFILE%\.amir\secrets\langfuse.env`, never in tracked files. An `sk-lf-` value in the repo is a CRITICAL finding.

## Mode choice

- **hosted** (Langfuse Cloud): EU `https://cloud.langfuse.com`, US `https://us.cloud.langfuse.com`. Account required; free tier exists, volume is paid — label plan-dependent features. Trace content leaves the machine: acceptable only if the redaction defaults above are on or data is not proprietary.
- **self_hosted**: official docker compose (`git clone https://github.com/langfuse/langfuse.git; docker compose up`), UI on localhost:3000. Free, data stays local; the compose stack is dev-grade (no HA/backup). Some managed evaluation features are cloud/enterprise-gated — check the UI, report what actually exists.
- **disabled**: a valid, intentional state. Respect it; do not nag.

## Standard trace hierarchy (use these span names so runs are comparable)

Task → Planning → Context retrieval → Architecture agent → Development agent → Test execution → QA agent → Security scan → Final validation.

Per span record: model, latency, tokens in/out, cost, retries, tool calls. Verification of instrumentation = one real run whose trace arrives with this hierarchy (`langfuse.auth_check()` for connectivity, then fetch the trace back).

## Fallback behavior

Langfuse down (self-hosted stopped, cloud unreachable): the application must keep working — SDK failures are non-fatal by design; never let tracing break the pipeline. Buffered events may drop while the server is down; say so instead of pretending continuity. Local records (`.amir/state/langfuse/`) keep evaluation/experiment/cost summaries so the project retains history even if the instance is wiped.
