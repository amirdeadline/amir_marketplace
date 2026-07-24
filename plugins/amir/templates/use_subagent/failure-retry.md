# Failure and Retry Protocol

## Classify the failure

| Class | Typical action |
|-------|----------------|
| Requirement ambiguity | Clarification (A–E); freeze answer; update dependents |
| Missing dependency | Complete or create prerequisite task |
| Incorrect assumption | Document correction; supersede invalid tasks |
| Context deficiency | Narrow prompt; add only missing facts/files |
| Implementation error | New specialized agent; smaller task |
| Test failure | Capture failing evidence; fix or split |
| Tool / environment failure | Diagnose env; do not blame code without evidence |
| Merge / ownership conflict | Serialize; reassign ownership; revalidate |
| Scope violation | Reject result; redispatch with tighter bounds |
| Unsupported capability | Switch mode (A→C/D); tell user honestly |

## Retry rules

1. Do **not** resend the identical prompt unchanged.
2. Update context, narrow, or split first.
3. Retry only the failed or invalid portion.
4. Do not restart successful independent tasks without reason.
5. After repeated failure (suggest ≤2 meaningful retries unless user directs otherwise), report the blocker clearly — never fabricate success.
6. Revalidate affected downstream tasks when contracts change.
