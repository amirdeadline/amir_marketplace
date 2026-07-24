# /use_subagent — skill package README

## Installation

### Project-scoped (recommended)

Enable the **amir** marketplace plugin for the workspace only (Cursor / Claude Code / Codex). Do not rely on user-global plugin junctions as the supported path.

From marketplace root after source edits:

```powershell
cd E:\PC3_Shared\Plugins\amir_marketplace
node scripts\pack-amir.js
python scripts\fix_amir_command_frontmatter.py
```

### Source layout

| Path | Role |
|------|------|
| `skills/use_subagent.md` | Host-agnostic behavior |
| `templates/use_subagent/` | Stage templates + prompts |
| `schemas/use_subagent-*.yaml` | Plan / task / result / validation schemas |
| `adapters/cursor/commands/use_subagent.md` | Cursor slash `/amir:use_subagent` |
| `adapters/*/skills/use_subagent/SKILL.md` | Thin host wrappers |
| `templates/use_subagent/adapters/` | Mode A–D notes per host |
| `examples/use_subagent/` | Worked examples |
| `tests/use_subagent/` | Acceptance / scenario tests |

## Invocation

```text
/amir:use_subagent Add role-based access control to the application.
/use_subagent Fix the flaky login test.
Investigate the CI failure /amir:use_subagent
```

## Compatibility

See `templates/use_subagent/adapters/compatibility-matrix.md`.
