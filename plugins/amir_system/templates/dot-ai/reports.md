# Agent reports index

Last updated: <!-- YYYY-MM-DDTHH:MM:SSZ -->

Summary of all agent reports. Full detail lives under the creating host's
`agents/<agent>/report.md` (`.cursor/`, `.claude/`, or `.codex/`).

| Agent | Host | Score (1–100) | Datetime (UTC) | Summary | Detail |
|-------|------|---------------|----------------|---------|--------|
| <!-- orchestrator --> | <!-- cursor --> | <!-- 0–100 --> | <!-- ISO-8601 Z --> | <!-- one-line summary --> | <!-- [report](../.cursor/agents/orchestrator/report.md) --> |

## Scoring guide

- **1–20** — informational; no human action needed
- **21–50** — review when convenient
- **51–80** — should review before next major step
- **81–100** — needs human attention soon (risk, blocker, security, goal drift)

## Rules

1. Every new/updated agent `report.md` gets a row here (replace the prior row for that agent+host).
2. Score is "how much human attention is required", not quality of the work.
3. Links must be relative paths to the real report file.
4. Do not paste full report bodies into this file.
