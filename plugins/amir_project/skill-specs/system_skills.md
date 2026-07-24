# system_skills

## Command

`/system_skills {ai_app}`

`{ai_app}`: `claude` | `cursor` | `codex`

## Purpose

Enumerate and present a table of skills installed at the **system level** for the specified AI application host — read-only inventory for audit and troubleshooting.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `{ai_app}` | Yes | Host identifier: `claude`, `cursor`, or `codex` |
| Plugin root | Implicit | amir plugin install location |
| Host paths | Resolved | From `adapters/<ai_app>/capabilities.md` and `adapters/<ai_app>/install-paths.md` |

## Behavior

1. Validate `{ai_app}` is one of `claude`, `cursor`, `codex`; if invalid, ask human to choose (**Blocking**).
2. Read `adapters/<ai_app>/capabilities.md` for system skill root paths and naming conventions.
3. Resolve system-level directories (examples — verify on host):
   - **claude:** `~/.claude/skills/`, plugin-dropped skills under Claude Code config
   - **cursor:** `~/.cursor/skills-cursor/`, `~/.cursor/plugins/` skill bundles
   - **codex:** host-documented global skills path from adapter
4. Scan each resolved path: list skill files (`SKILL.md`, `*.md` commands, host-specific skill manifests).
5. Cross-reference amir plugin `skills/*.md` definitions with installed copies; mark `installed`, `missing`, or `stale` (version mismatch vs plugin `VERSION`).
6. Build **system skills table** columns: Skill name | Source (amir/bundled/third-party) | Install path | Host invocation (`/name` or equivalent) | Status.
7. Present table to human per `core/interaction-style.md`; note `/btw` is **not** in plugin `skills/` — lives only in cursor+codex adapters per README.
8. Append read-only `system_skills` activity with `{ai_app}` and counts (installed/missing/stale).
9. Emit short lead per `core/message-contract.md`; offer `/details` for full table export path if saved.

## Core modules referenced

- Follow `core/honesty-rules.md`
- Follow `core/message-contract.md`
- Follow `core/interaction-style.md`

## State files read/written

| File | Access |
|------|--------|
| `adapters/<ai_app>/capabilities.md` | Read |
| `adapters/<ai_app>/install-paths.md` | Read |
| `skills/*.md` (plugin) | Read (catalog) |
| `VERSION` | Read |
| Host system skill directories | Read only |
| `ai/state/activity.jsonl` | Append (when run inside project) |

## Outputs

- System-level skills table for `{ai_app}`
- Status summary: installed / missing / stale counts
- Optional saved artifact: `ai/agents/1-orchestrator/logs/system-skills-<ai_app>-<timestamp>.md`

## Failure/abort behavior

- Abort if `{ai_app}` missing or unrecognized.
- If adapter paths missing, emit **Not Supported** degrade per `core/honesty-rules.md` — list paths attempted.
- Do not claim skills installed without VERIFIED directory listing.
- Read-only — never modify system skill files in this skill.
- If host path inaccessible (permissions), report PROBLEM with path and stop.
