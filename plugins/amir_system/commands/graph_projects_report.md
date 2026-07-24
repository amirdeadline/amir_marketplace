---
description: Generate the portfolio report set into ~/.amir/portfolio/reports via the deterministic engine
---

# /amir:graph_projects_report

Writes files ONLY under `%USERPROFILE%\.amir\portfolio\reports\` — never into any project.

Engine:

```powershell
python "$env:USERPROFILE\.amir\bin\amirctl.py" portfolio-report
```

Engine missing → report honestly and STOP; do NOT hand-write substitute report files as if
the engine produced them (an offer to assemble a clearly-labeled ad-hoc summary in chat is
fine). Subcommand rejected → `--help` once, closest documented subcommand, say which.

## Procedure

1. Snapshot the contents of `%USERPROFILE%\.amir\portfolio\reports\` (names + timestamps)
   BEFORE running, so you can state exactly what the run produced.
2. Run `portfolio-report` and show its real output. The engine generates the report set —
   **5 files** covering: portfolio overview, per-project health, cross-project dependencies,
   progress (confirmed vs estimated, evidence-based), and risks/blockers. The engine defines
   the exact filenames — list the files it ACTUALLY wrote (diff against the snapshot); never
   assert a filename you did not observe.
3. If fewer than the expected files appear or any generation step failed, report that as a
   partial result with the real error — never claim the full set exists when it does not.
4. Summarize each generated file in 1–2 lines in chat, with its full path, and note the
   generation timestamp (this is what `/amir:graph_projects_status` shows as "last report").

## Constraints

- The reports are derived from the registry and the global graph; stale namespaces flow
  through as stale data — if `portfolio-status`/the engine flags staleness, surface that
  caveat with the report summary and recommend `/amir:graph_projects_update_all` first.
- Progress figures in reports follow the evidence rule: Confirmed / Estimated / Unknown,
  never invented. If the engine output contradicts this, flag it.
- Reports must contain no secret values; if one appears to, warn (without printing it) and
  recommend `/amir:graph_projects_validate`.
