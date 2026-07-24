# Validation Protocol

Orchestrator validates every subagent result **independently**.

## Pass conditions (all required)

1. Expected deliverable exists.
2. Every acceptance criterion is observably satisfied.
3. Required validation commands/tests were executed (or explicitly NOT RUN with impact).
4. Result stays within `allowed_changes` / outside `prohibited_changes`.
5. Compatible with frozen dependency contracts.
6. No unresolved critical issue remains for this task.

## Reject phrases (insufficient alone)

- “This should work.”
- “Tests would likely pass.”
- “The implementation appears correct.”
- “Follows best practices.”

## Evidence types

| Type | Examples |
|------|----------|
| Executed tests | unit/integration output |
| Build / lint / typecheck | compiler or linter output |
| Diff | file list + focused review |
| Runtime | API response, query result |
| Manual | reproduction steps + inspection notes |

## High-risk gate

If `risk_level` is medium or high, require a separate review task (different agent) before treating the implementation task as fully accepted for integration.

## Integration validation

After implementation tasks complete:

- Combine outputs without silent large rewrites
- Confirm interfaces, migrations, config compatibility
- Run system-level / regression checks
- Track material integration edits as new tasks
