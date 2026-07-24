# system_settings

## Command

`/system_settings {ai_app}`

`{ai_app}`: `claude` | `cursor` | `codex`

## Purpose

Produce a clean, human-readable artifact of **system-level** settings for the specified AI application, ordered by importance — for audit, backup review, and troubleshooting.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `{ai_app}` | Yes | Host identifier: `claude`, `cursor`, or `codex` |
| Output path | Optional | Save artifact; default show in chat summary + offer `/details` |

## Behavior

1. Validate `{ai_app}`; read `adapters/<ai_app>/capabilities.md` and `adapters/<ai_app>/install-paths.md` for system config file locations.
2. Discover settings files (VERIFIED paths only), typical examples:
   - **claude:** `~/.claude/settings.json`, Claude Code config manifests
   - **cursor:** `~/.cursor/settings.json`, MCP config, rules paths
   - **codex:** adapter-documented global config files
3. Read each file; **redact** secrets (API keys, tokens, passwords) — show `***REDACTED***` at path key per `core/security-rules.md`.
4. Classify settings by importance tier:
   - **Critical:** auth, API endpoints, model defaults, security toggles
   - **High:** MCP servers, hooks, agent permissions, paths
   - **Medium:** UI/UX preferences, telemetry
   - **Low:** cosmetic, experimental flags
5. Render **human-readable artifact** (markdown): grouped sections highest tier first; each entry = setting name, value (redacted), source file path, notes.
6. Save to `.ai/agents/1-orchestrator/logs/system-settings-<ai_app>-<timestamp>.md` when project context exists; otherwise present inline.
7. Present chat summary per `core/message-contract.md`: file count, critical/high counts, artifact path — not full dump.
8. Append read-only `system_settings` activity.

## Core modules referenced

- Follow `core/security-rules.md`
- Follow `core/honesty-rules.md`
- Follow `core/message-contract.md`
- Follow `core/interaction-style.md`

## State files read/written

| File | Access |
|------|--------|
| `adapters/<ai_app>/capabilities.md` | Read |
| `adapters/<ai_app>/install-paths.md` | Read |
| Host system config files | Read only |
| `.ai/agents/1-orchestrator/logs/system-settings-*.md` | Write |
| `.ai/state/activity.jsonl` | Append |

## Outputs

- Redacted system settings artifact ordered by importance
- Summary counts by tier
- Source path index

## Failure/abort behavior

- Abort if `{ai_app}` invalid.
- Never paste raw secrets into chat or artifact — redact always.
- If config file unreadable, list path with VERIFIED error; continue other files.
- Read-only — do not modify system settings in this skill.
- If adapter docs missing, **Not Supported** with paths attempted.
