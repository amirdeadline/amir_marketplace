# user_skills

## Command

`/user_skills {ai_app}`

`{ai_app}`: `claude` | `cursor` | `codex`

## Purpose

Enumerate and present a table of skills installed at the **user level** for the specified AI application — project-scoped or user-home overrides, read-only inventory.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `{ai_app}` | Yes | Host identifier: `claude`, `cursor`, or `codex` |
| Project root | Implicit | Current workspace (for project-local skills) |
| User home | Implicit | Resolve `~` / `%USERPROFILE%` for user-level paths |

## Behavior

1. Validate `{ai_app}` is one of `claude`, `cursor`, `codex`; if invalid, ask human to choose (**Blocking**).
2. Read `adapters/<ai_app>/capabilities.md` for user-level skill paths (project `.cursor/skills`, `.claude/skills`, Codex user config, etc.).
3. Scan **user-level** locations in order:
   - Project-local: `.cursor/skills/`, `.claude/skills/`, `.codex/skills/` (per adapter — only those that exist for host)
   - User home overrides: `~/.cursor/skills/`, `~/.claude/skills/`, documented codex user paths
4. List each skill file with name, path, last modified (VERIFIED stat).
5. Distinguish **user** vs **system** skills: user table includes only paths under project or user home, excludes system dirs from `/system_skills`.
6. Cross-reference names against plugin `skills/*.md`; flag duplicates (user override shadows system).
7. Build **user skills table** columns: Skill name | Scope (project/user) | Path | Overrides system? | Invocation.
8. Present table per `core/interaction-style.md`.
9. Append `user_skills` activity when run inside amir project.
10. Emit short summary per `core/message-contract.md`.

## Core modules referenced

- Follow `core/honesty-rules.md`
- Follow `core/message-contract.md`
- Follow `core/interaction-style.md`
- Follow `core/workspace-rules.md`

## State files read/written

| File | Access |
|------|--------|
| `adapters/<ai_app>/capabilities.md` | Read |
| `skills/*.md` (plugin) | Read (catalog) |
| Project `.cursor/`, `.claude/`, `.codex/` skill dirs | Read only |
| User home skill dirs | Read only |
| `ai/state/activity.jsonl` | Append |

## Outputs

- User-level skills table for `{ai_app}`
- Override/duplicate warnings
- Optional saved artifact: `ai/agents/1-orchestrator/logs/user-skills-<ai_app>-<timestamp>.md`

## Failure/abort behavior

- Abort if `{ai_app}` missing or unrecognized.
- Read-only — never create, edit, or delete user skills.
- Do not invent skill names; VERIFIED filesystem listing only.
- If no user skills found, report empty table explicitly (not an error).
- If project root has no amir `ai/` tree, still scan user paths but note non-amir context.
