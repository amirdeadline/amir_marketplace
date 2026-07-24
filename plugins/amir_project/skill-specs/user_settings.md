# user_settings

## Command

`/user_settings {ai_app}`

`{ai_app}`: `claude` | `cursor` | `codex`

## Purpose

Produce a clean, human-readable artifact of **user-level** settings for the specified AI application (project + user home overrides), ordered by importance — read-only audit.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `{ai_app}` | Yes | Host identifier: `claude`, `cursor`, or `codex` |
| Project root | Implicit | Current workspace for project-local settings |
| Output path | Optional | Save artifact path |

## Behavior

1. Validate `{ai_app}`; read `adapters/<ai_app>/capabilities.md` for user-level config locations.
2. Discover user settings files (VERIFIED), typical examples:
   - **cursor:** `.cursor/settings.json`, `.cursor/rules/`, project MCP overrides
   - **claude:** `.claude/settings.json`, project `CLAUDE.md` local config sections if present
   - **codex:** project/user config per adapter
3. Merge precedence: project-local overrides user-home defaults — document override chain in artifact header.
4. Read each file; **redact** secrets per `core/security-rules.md` (`***REDACTED***` at key).
5. Classify by importance (Critical → High → Medium → Low) same tiers as `/system_settings`.
6. Render markdown artifact grouped by tier; note which scope (project vs user home) each entry comes from.
7. Save to `ai/agents/1-orchestrator/logs/user-settings-<ai_app>-<timestamp>.md`.
8. Chat summary per `core/message-contract.md`: artifact path, tier counts, override notes — no full dump.
9. Append `user_settings` activity.

## Core modules referenced

- Follow `core/security-rules.md`
- Follow `core/honesty-rules.md`
- Follow `core/message-contract.md`
- Follow `core/interaction-style.md`
- Follow `core/workspace-rules.md`

## State files read/written

| File | Access |
|------|--------|
| `adapters/<ai_app>/capabilities.md` | Read |
| Project host config dirs (`.cursor/`, `.claude/`, etc.) | Read only |
| User home host config | Read only |
| `ai/agents/1-orchestrator/logs/user-settings-*.md` | Write |
| `ai/state/activity.jsonl` | Append |

## Outputs

- Redacted user settings artifact ordered by importance
- Override/precedence documentation
- Summary by tier and scope

## Failure/abort behavior

- Abort if `{ai_app}` invalid.
- Never output raw API keys or tokens.
- Read-only — no writes to user settings files.
- If no user settings files exist, report empty artifact explicitly.
- Continue on per-file read errors; mark section UNKNOWN with path.
