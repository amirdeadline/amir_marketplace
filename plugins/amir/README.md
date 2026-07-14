# amir (marketplace package)

Self-contained amir plugin built by `scripts/pack-amir.js` for Claude Code, Cursor, and Codex marketplace installs.

| Path | Role |
|------|------|
| `core/` | Process rules (single source) |
| `skill-specs/` | Host-agnostic skill definitions |
| `skills/` | Host wrappers (`SKILL.md`) |
| `tools/` | Node.js CLI (state, render, activity, cost, doctor, secrets_scan) |
| `commands/` | Cursor slash commands (includes `/btw`) |
| `agents/` | Claude Code agent defs |
| `rules/` | Cursor always-on rules |
| `schemas/`, `templates/` | State schemas + prompt templates |

**Source of truth for development:** `../Amir` (sibling repo). Re-run `node scripts/pack-amir.js` after changing the source.

Requires **Node.js >= 18**.

See `capabilities.md` for host degrade paths. Claude Code does **not** register `/btw`.
