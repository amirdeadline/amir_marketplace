# git_commit

## Command

`/git_commit`

## Purpose

Create a git commit with message metadata derived from activity and implementation notes, after a mandatory secrets scan gate. Hard-fail on any findings with file locations before staging or committing.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Project root | Implicit | Current amir project root |
| Commit scope | Optional | Default: all approved tracked changes; human may narrow paths |
| Checkpoint tag | Optional | e.g. `amir/T001-complete` when closing a task |
| Message override | Optional | Human may supply subject line; body still includes metadata |

## Behavior

1. Verify git repository (`git rev-parse --is-inside-work-tree`); if absent, offer `/git_setup` and stop.
2. Run `git status` and `git diff --stat`; if no changes, report clean tree and stop.
3. **Mandatory gate:** run `node tools/secrets_scan.js <root>` (or documented project scope). Archive raw JSON to `ai/agents/4-security/logs/secrets_scan-<timestamp>.json`.
4. If scan reports **any findings**: **hard FAIL** — do not stage, do not commit. Present table: `path:line`, finding type, masked snippet. Recommend removal/rotation per `core/security-rules.md`. Stop until clean re-scan passes.
5. If scan did not run (tool missing/error): **BLOCKED** — log Reason/Impact; do not commit.
6. Collect commit metadata:
   - Recent `ai/state/activity.jsonl` events for active task(s)
   - `ai/agents/dev-<task-id>/notes.md` and `implementation-notes` if present
   - Task id, phase, files changed summary from worker artifacts
7. Compose commit message: subject (`feat|fix|chore|docs: <task-id> <summary>`) + body bullets from metadata (VERIFIED actions only).
8. Present proposed message and file list to human per `core/interaction-style.md` (**Material** approval unless orchestrator checkpoint mode with pre-approval).
9. Stage only approved paths; never stage secrets-pattern files flagged by scan.
10. `git commit` with approved message; optionally `git tag <checkpoint-tag>` when provided and task at `qa_passed`/`complete`.
11. Append activity: `node tools/activity.js <root> append --agent 1-orchestrator --action git_commit --result "<hash>" --task <task-id>`.
12. Emit summary per `core/message-contract.md`: commit hash, tag if any, files count.

## Core modules referenced

- Follow `core/security-rules.md`
- Follow `core/workspace-rules.md`
- Follow `core/message-contract.md`
- Follow `core/interaction-style.md`
- Follow `core/honesty-rules.md`
- Follow `core/qa-loop.md`

## State files read/written

| File | Access |
|------|--------|
| `ai/state/activity.jsonl` | Read/Append |
| `ai/state/tasks.json` | Read (active task, checkpoint tag) |
| `ai/agents/dev-*/notes.md` | Read |
| `ai/agents/dev-*/implementation-notes.md` | Read |
| `ai/agents/4-security/logs/secrets_scan-*.json` | Write |
| Git index/commits/tags | Write |

## Outputs

- Git commit with metadata-rich message
- Optional checkpoint tag `amir/T<id>-complete`
- Secrets scan archive (clean run)
- Activity audit entry with commit hash

## Failure/abort behavior

- **Hard fail** on any `secrets_scan.js` finding — list every `path:line`; no commit.
- Abort if human rejects commit message or staged file list.
- Abort if staged paths include `.env`, private keys, or tokens — even if scan missed (manual check).
- Never use `--no-verify` unless human explicitly requests and logs decision.
- Do not copy secret values into commit message or chat — locations and types only.
- If commit hook fails, fix and create **new** commit (no amend unless hook auto-modified and conditions met).
