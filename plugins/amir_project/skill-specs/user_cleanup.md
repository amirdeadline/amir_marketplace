# user_cleanup

## Command

`/user_cleanup {ai_app}`

`{ai_app}`: `claude` | `cursor` | `codex`

## Purpose

**DESTRUCTIVE.** Remove user-level and project-local amir installations for the specified AI application — only after timestamped backup, explicit deletion list, typed confirmation, and audit log. Refuse if any safeguard is missing.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `{ai_app}` | Yes | Host to clean: `claude`, `cursor`, or `codex` |
| Project root | Implicit | Current workspace (project-local targets) |
| Confirmation phrase | Required | Exact typed phrase: `DELETE USER <ai_app>` (e.g. `DELETE USER cursor`) |
| Human approval | Required | Explicit approval after reviewing deletion list |

## Behavior

1. Validate `{ai_app}`; emit **DESTRUCTIVE** warning — affects project and user-home overrides, not system install (use `/system_cleanup` for system scope).
2. Resolve user-level paths from `adapters/<ai_app>/capabilities.md`:
   - Project: `.cursor/`, `.claude/`, `.codex/` amir-related skills, rules, commands
   - User home: `~/.cursor/skills/`, `~/.claude/skills/`, etc. — **only** amir-copied artifacts (not entire host config unless amir-only subpaths)
3. **Safeguard 1 — Backup:** timestamped archive:
   - `.ai/agents/1-orchestrator/archive/user-cleanup-<ai_app>-<YYYYMMDD-HHMMSS>.zip` (project context)
   - Or `<project-root>/backups/user-cleanup-<ai_app>-<timestamp>.zip`
   - Manifest with paths and hashes
   - **Show human the backup path** before delete
4. **Safeguard 2 — Deletion list:** numbered table of exact files/dirs to delete; **exclude** `.ai/state/`, `.ai/project-goal.md`, and git history unless human explicitly adds via separate decision.
5. **Safeguard 3 — Typed confirmation:** require exactly `DELETE USER <ai_app>`; refuse paraphrase.
6. Without backup + list + correct phrase + approval: **REFUSE** — zero deletions.
7. **Safeguard 4 — Log:** append `user_cleanup` to `.ai/state/activity.jsonl` with backup path, list checksum, `{ai_app}`, confirmation timestamp; record approval in `.ai/state/decisions.json`.
8. Delete only listed paths; do not touch system-level install dirs.
9. Post-verify with `/user_skills {ai_app}` — expect amir user entries cleared.
10. Emit summary per `core/message-contract.md`: backup path, deleted count, protected paths preserved.

## Core modules referenced

- Follow `core/security-rules.md`
- Follow `core/honesty-rules.md`
- Follow `core/message-contract.md`
- Follow `core/interaction-style.md`
- Follow `core/question-format.md`
- Follow `core/workspace-rules.md`

## State files read/written

| File | Access |
|------|--------|
| `adapters/<ai_app>/capabilities.md` | Read |
| Project/user amir skill paths | Delete (listed only) |
| `.ai/agents/1-orchestrator/archive/user-cleanup-*.zip` | Write (backup) |
| `.ai/state/activity.jsonl` | Append |
| `.ai/state/decisions.json` | Write |
| `.ai/state/**` | Read — **never delete** unless explicitly listed with separate human gate |

## Outputs

- Timestamped backup archive path (mandatory)
- Executed deletion report
- Protected paths confirmation (`.ai/state/` preserved by default)
- Audit log entry

## Failure/abort behavior

- **REFUSE without all three:** (1) backup shown, (2) exact deletion list approved, (3) typed `DELETE USER <ai_app>` — plus logging before delete.
- Abort if backup fails — no deletions.
- Never delete `.ai/state/`, `.ai/project-goal.md`, or checkpoint evidence by default.
- Stop on delete error; report partial completion; backup remains for restore.
- Wrong phrase → refuse.
- Do not conflate with `/project_cleanup` — user_cleanup targets host user install artifacts, not general workspace hygiene.
