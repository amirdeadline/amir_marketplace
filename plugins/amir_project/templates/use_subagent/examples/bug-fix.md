# Example: Bug fix

## Invocation

```text
/use_subagent Investigate and fix the failing CI pipeline.
```

## Expected flow

1. Stage 1: inspect CI config, recent commits, failing job logs (read-only).
2. Clarify only if environment/secrets/access blocks diagnosis.
3. Atomic tasks e.g. T001 reproduce failure, T002 isolate failing step, T003 minimal fix, T004 add/adjust regression test, T005 re-run focused CI check, T006 document root cause.
4. Do not “fix CI” in one task.
5. Validation requires actual CI or local equivalent evidence — not “should pass”.
