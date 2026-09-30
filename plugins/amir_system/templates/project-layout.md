# Amir project layout (authoritative)

Every Amir-managed project MUST have these directories at the project root:

```text
.ai/       # host-independent project data (shared by all agents/hosts)
.cursor/   # Cursor-only: settings, skills, rules, commands, agents
.claude/   # Claude Code-only: settings, skills, commands, agents
.codex/    # Codex-only: settings, agents, AGENTS.md companions
.vscode/   # Editor workspace settings + project theme color
.amir/     # Amir manifest, lock, portfolio (unchanged)
```

## Separation rule

| Kind of data | Where it lives |
|---|---|
| Project facts, plans, TODOs, design, shared status, report index | `.ai/` |
| Cursor agent workspaces, Cursor skills/rules/commands/settings | `.cursor/` |
| Claude agent workspaces, Claude skills/commands/settings | `.claude/` |
| Codex agent workspaces and Codex settings | `.codex/` |
| VS Code / Cursor IDE chrome (theme, editor prefs) | `.vscode/` |

Never put Cursor-only config under `.claude/`, or Claude-only config under `.cursor/`.
Never put host-specific agent reports only under `.ai/` — index them from `.ai/reports.md`
and store the full report under the creating host's `agents/<agent>/report.md`.

## `.ai/` required files

Seed from `templates/dot-ai/`:

| File | Purpose |
|---|---|
| `settings.json` | Host-independent project AI settings |
| `TODO.md` | Open work / backlog (human + agents) |
| `project.md` | Goal, scope, constraints |
| `status.md` | Current honest status |
| `assumptions.md` | Explicit assumptions (challenge regularly) |
| `design.md` | Architecture / design decisions (living) |
| `tasks.md` | Task list |
| `reports.md` | Index table of all agent reports |
| `decisions.md` | Decision log (retained) |
| `risks.md` | Risks (retained) |
| `architecture.md` | Module map (retained; may sync from Graphify) |
| `references.md` | External refs (retained) |
| `changelog.md` | Session/project changelog (retained) |
| `context_handoff.md` | Fresh-session handoff (retained) |

Optional when amir_project harness is enabled: `.ai/state/`, `.ai/views/` (JSON truth +
generated views). Those are harness internals — not a substitute for the shared markdown
files above, and not host agent workspaces.

## `.ai/reports.md` table format

```markdown
| Agent | Host | Score (1–100) | Datetime (UTC) | Summary | Detail |
|-------|------|---------------|----------------|---------|--------|
| orchestrator | cursor | 12 | 2026-07-29T12:00:00Z | Initial plan drafted | [report](../.cursor/agents/orchestrator/report.md) |
```

Columns:

1. **Agent** — agent id / folder name
2. **Host** — `cursor` | `claude` | `codex`
3. **Score (1–100)** — how urgently a human should read this (100 = immediate attention)
4. **Datetime (UTC)** — when the report was written
5. **Summary** — one or two sentences
6. **Detail** — relative markdown link to `.<host>/agents/<agent>/report.md`

Update this table whenever an agent writes or replaces its `report.md`.

## Host directories (`.cursor/`, `.claude/`, `.codex/`)

Each host directory MUST contain:

```text
.<host>/
  settings.json
  agents/
    orchestrator/
      report.md
    qa/
      report.md
    <additional-agent>/
      report.md
```

Create additional agent folders only when that agent is actually used. Minimum when
subagent orchestration is enabled: `orchestrator` + `qa` under **every enabled host**.
When a host is not selected in the manifest, still create the directory skeleton
(`.cursor`, `.claude`, `.codex`) so the project layout is uniform; leave unused hosts
with empty agent stubs and a minimal `settings.json`.

Host-local extras (do not put these in `.ai/`):

- `.cursor/`: `commands/`, `rules/`, `skills/`, `mcp.json` (renderer + host tools)
- `.claude/`: Claude project settings, skills, hooks as applicable
- `.codex/`: Codex companions / config as applicable

## Agent `report.md`

Every agent folder has `report.md`. Agents append or replace their own report; they do not
edit another agent's `report.md`. After writing a report, update `.ai/reports.md`.

## `.vscode/settings.json`

Always create. Include useful workspace defaults and an active
`workbench.colorCustomizations` block using **one randomly chosen palette** from
`templates/vscode/theme-palettes.json` so each project is visually distinct. Base theme
stays `Default Dark Modern`.
