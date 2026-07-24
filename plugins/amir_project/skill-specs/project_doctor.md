# project_doctor

## Command

`/project_doctor`

## Purpose

Run structural and operational health checks; present findings as a severity table with suggested fixes.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Project root | Implicit | Current amir project root |

## Behavior

1. Run `node tools/doctor.js <root>`; capture JSON findings array.
2. Render findings table: Severity | Check | Message | Suggested fix.
3. Sort by severity: CRITICAL, HIGH, MEDIUM, LOW.
4. Report exit code implication (non-zero if CRITICAL or HIGH present).
5. Recommend concrete next commands per finding (e.g. `node tools/render.js <root> all`, `/resume_build`, `/security_scan`).
6. Read-only — doctor does not auto-repair.

## Core modules referenced

- Follow `core/workspace-rules.md`
- Follow `core/naming-rules.md`
- Follow `core/qa-loop.md`
- Follow `core/budget-rules.md`
- Follow `core/security-rules.md`
- Follow `core/honesty-rules.md`

## State files read/written

| File | Access |
|------|--------|
| `.ai/state/*.json` | Read |
| `.ai/state/activity.jsonl` | Read |
| `.ai/views/*.md` | Read |
| `.ai/agents/**` | Read (scan) |

## Outputs

- Findings JSON from doctor tool
- Formatted findings table in chat
- Pass/fail summary with counts by severity

## Failure/abort behavior

- If project root invalid, report usage error from tool.
- Do not suppress CRITICAL/HIGH findings.
- Doctor command failure is informational; present findings even when exit code is 1.
