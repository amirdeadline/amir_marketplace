# rollback

## Command

`/rollback`

## Purpose

Revert project codebase to a prior checkpoint safely. Prefer git revert; allow `git reset --hard` only with explicit typed human confirmation.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Project root | Implicit | Current amir project root |
| Target | Yes | Commit hash, checkpoint tag (`amir/T<id>-complete`), or ref |
| Scope | Optional | Whole repo vs paths |
| Confirmation | Conditional | Typed phrase required for `--hard` reset |

## Behavior

1. Verify git repo; if absent, offer `/git_setup` and stop.
2. Run `node tools/doctor.js <root>`; note tasks `in_progress`.
3. Identify target ref from argument or latest checkpoint tag in `tasks.json`.
4. **Prefer `git revert`** for shared branches — create revert commit preserving history.
5. If human requests hard reset, require typed confirmation phrase (e.g. `ROLLBACK HARD <ref>`) logged to `decisions.json` before `git reset --hard <ref>`.
6. Mark downstream tasks for re-verification: any task after rolled-back checkpoint with `complete` status → orchestrator sets note `needs_reverify` via `set-task-field` or human-approved bulk update.
7. Do not delete `ai/state/` or `ai/project-goal.md`; state may need manual reconciliation after rollback.
8. Append `rollback` event to activity with ref, method (revert|hard), and affected task ids.
9. Recommend `./verify.sh` and `/resume_build`.

## Core modules referenced

- Follow `core/security-rules.md`
- Follow `core/workspace-rules.md`
- Follow `core/message-contract.md`
- Follow `core/honesty-rules.md`
- Follow `core/qa-loop.md` (regression after rollback)

## State files read/written

| File | Access |
|------|--------|
| `ai/state/tasks.json` | Write (reverify flags, notes) |
| `ai/state/decisions.json` | Write (hard reset approval) |
| `ai/state/activity.jsonl` | Append |
| Git tree | Write (revert or reset) |

## Outputs

- Git rollback result (commit or reset)
- List of tasks marked for re-verification
- Activity audit entry

## Failure/abort behavior

- Abort hard reset without typed confirmation.
- Abort if target ref not found.
- Never run `git push --force` unless explicit separate human approval per `core/security-rules.md`.
- Emit **PROBLEM** if rollback would orphan QA evidence; archive evidence paths in decision note first.
- Do not rollback `ai/state/` JSON automatically — human must reconcile task status vs code state.
