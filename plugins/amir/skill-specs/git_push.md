# git_push

## Command

`/git_push`

## Purpose

Confirm remote and branch, show what will push, execute push, and report result with evidence.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Project root | Implicit | Current amir project root |
| Remote | Optional | Default `origin` |
| Branch | Optional | Default current upstream or current branch |
| Force | Optional | Default forbidden |

## Behavior

1. Verify git repository; if absent, offer `/git_setup` and stop.
2. Resolve remote name (default `origin`) and branch (current checked-out branch).
3. Run `git remote -v` and `git branch -vv`; if no upstream configured, ask human for remote branch name per `core/question-format.md` (**Material**).
4. Run `git fetch <remote>` when network available; compare local branch to upstream with `git log --oneline <upstream>..HEAD` and `git diff --stat <upstream>...HEAD`.
5. Present **push preview** table: commits to push (hash, subject), files changed aggregate, tags included (if any `amir/T*-complete` not on remote).
6. Ask human to confirm push (**Material**); record approval in `ai/state/decisions.json` when pushing task checkpoints or first push.
7. Execute `git push -u <remote> <branch>` (set upstream on first push); push tags separately with `git push <remote> --tags` only if human approved tag publish.
8. Capture VERIFIED command output (exit code, summary line).
9. Append `git_push` to `ai/state/activity.jsonl` with remote, branch, commit range, result.
10. Emit summary per `core/message-contract.md`: remote, branch, commits pushed count, new upstream if set.

## Core modules referenced

- Follow `core/security-rules.md`
- Follow `core/message-contract.md`
- Follow `core/interaction-style.md`
- Follow `core/question-format.md`
- Follow `core/honesty-rules.md`

## State files read/written

| File | Access |
|------|--------|
| `ai/state/decisions.json` | Write (push approval) |
| `ai/state/activity.jsonl` | Append |
| Git remotes/branches | Read/Write (push) |

## Outputs

- Push preview (pre-execution)
- Push result with exit evidence
- Updated upstream tracking (if `-u` used)
- Activity audit entry

## Failure/abort behavior

- Abort without human confirmation of push preview.
- **Never** `git push --force` or `--force-with-lease` unless human provides separate explicit approval logged per `core/security-rules.md`.
- Abort if `git fetch` or `git push` fails; report VERIFIED stderr; do not claim success.
- Abort if secrets_scan would block (uncommitted secrets in pushed commits) — recommend `/git_commit` fix first.
- If no commits ahead of upstream, report already up to date; skip push.
