# system_cleanup

## Command

`/system_cleanup {ai_app}`

`{ai_app}`: `claude` | `cursor` | `codex`

## Purpose

**DESTRUCTIVE.** Remove system-level amir and host skill installations for the specified AI application — only after timestamped backup, explicit deletion list, typed confirmation, and audit log. Refuse if any safeguard is missing.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `{ai_app}` | Yes | Host to clean: `claude`, `cursor`, or `codex` |
| Confirmation phrase | Required | Exact typed phrase: `DELETE SYSTEM <ai_app>` (e.g. `DELETE SYSTEM claude`) |
| Human approval | Required | Explicit approval after reviewing deletion list |

## Behavior

1. Validate `{ai_app}`; emit **DESTRUCTIVE** warning prominently per `core/interaction-style.md`.
2. Resolve system paths from `adapters/<ai_app>/install-paths.md` and `adapters/<ai_app>/capabilities.md` — all directories and files that amir install placed at system level (skills, commands, hooks, adapter copies).
3. **Safeguard 1 — Backup:** create timestamped archive of every path slated for deletion:
   - Archive to `<plugin-root>/backups/system-cleanup-<ai_app>-<YYYYMMDD-HHMMSS>.zip` (or `.tar.gz` on Unix)
   - Include manifest JSON listing archived relative paths and SHA hashes
   - **Show human the backup path** before any delete
4. **Safeguard 2 — Deletion list:** present numbered table of **exact** paths and files to delete (no globs without expanded listing); classify each as amir-managed vs shared host file.
5. **Safeguard 3 — Typed confirmation:** require human to type exactly `DELETE SYSTEM <ai_app>` in chat; no paraphrase accepted.
6. If any safeguard incomplete (no backup, no list, wrong phrase, no approval): **REFUSE** — emit **PROBLEM** and stop with zero deletions.
7. **Safeguard 4 — Log:** before delete, append `system_cleanup` to `ai/state/activity.jsonl` (or `ai/agents/1-orchestrator/logs/system-cleanup-<timestamp>.jsonl` if outside project) with: `{ai_app}`, backup path, deletion list checksum, confirmation timestamp.
8. Delete **only** listed paths; never expand scope during execution.
9. Verify post-delete: re-run `/system_skills {ai_app}` — expect amir entries missing or empty.
10. Present result per `core/message-contract.md`: backup path, deleted count, failures if any.

## Core modules referenced

- Follow `core/security-rules.md`
- Follow `core/honesty-rules.md`
- Follow `core/message-contract.md`
- Follow `core/interaction-style.md`
- Follow `core/question-format.md`

## State files read/written

| File | Access |
|------|--------|
| `adapters/<ai_app>/install-paths.md` | Read |
| `adapters/<ai_app>/capabilities.md` | Read |
| `<plugin-root>/backups/system-cleanup-*.zip` | Write (backup) |
| Host system install paths | Delete (listed only) |
| `ai/state/activity.jsonl` | Append |
| `ai/state/decisions.json` | Write (cleanup approval record) |

## Outputs

- Timestamped backup archive path (mandatory)
- Executed deletion report
- Post-cleanup inventory summary
- Audit log entry

## Failure/abort behavior

- **REFUSE without all three:** (1) backup shown, (2) exact deletion list approved, (3) typed `DELETE SYSTEM <ai_app>` — plus logging before delete.
- Abort on backup creation failure — zero deletions.
- Stop on first delete error; report partial completion and backup restore instructions.
- Never delete user project directories, `ai/state/`, or unrelated host config outside amir install list.
- Never delete backup archive in same operation.
- Wrong confirmation phrase → refuse and re-prompt.
