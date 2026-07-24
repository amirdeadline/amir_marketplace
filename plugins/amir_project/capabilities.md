# amir — host capability matrix

Cross-host comparison for **Claude Code**, **Cursor**, and **OpenAI Codex CLI**. amir skills, `core/` rules, `tools/`, schemas, and project JSON truth are **identical** across hosts; only packaging, invocation, and native platform features differ.

## Shared (all hosts)

| Concern | Location | Notes |
|---------|----------|-------|
| Process rules | `core/*.md` | Single source; skills reference, never restate |
| Skill definitions | `skills/*.md` | Host-agnostic behavior spec |
| State & views | `tools/*.js` + `schemas/` | JSON is truth; markdown views regenerated |
| Workspace layout | `core/workspace-rules.md` | `.ai/state/`, `.ai/views/`, agent workspaces |
| Message contract | `core/message-contract.md` | Five-field routine status |
| Budgets | `core/budget-rules.md` | QA cycles, discovery batches, token caps |
| Approvals | `core/interaction-style.md` + `schemas/approvals.schema.json` | Human gates for material decisions |
| Secrets gate | `tools/secrets_scan.js` + `/git_commit` skill (when present) | Primary enforcement at commit time |

Install copies or links the full amir package so `skills/`, `tools/`, and `core/` resolve consistently regardless of adapter.

---

## Capability matrix

| Capability | Claude Code | Cursor | Codex |
|------------|-------------|--------|-------|
| **Subagent support** | **Native** — `Task` tool launches isolated subagents with typed roles | **Native when `Task` available** — Cursor Agent `Task` tool (parallel subagents); **Degrade** to Mode C isolated contexts if Task unavailable | **Degrade** — AGENTS.md + skill wrappers; sequential **simulated** / Mode C unless host adds native delegation |
| **Subagent degrade path** | Use `Task` with agent id from `core/naming-rules.md` | Prefer `Task` (Mode A) for `/amir:use_subagent`; if unavailable, label **isolated task execution context** (Mode C) — do not claim native spawn | Same Mode C pattern; document which logical agent is active |
| **`/amir:use_subagent`** | Skill wrapper → `skills/use_subagent.md` | Command + skill; aliases `/use_subagent`, trailing trigger | Skill wrapper; Mode C default |
| **Hooks** | **Yes** — `hooks/hooks.json` (`PreToolUse`, `SessionStart`, etc.) | **Limited** — `.cursor/hooks.json` where supported; rules compensate | **Limited** — rely on skill discipline + `AGENTS.md`; sample `.codex/config.toml` notes only |
| **Command registration** | Plugin `skills/<name>/SKILL.md` → `/amir:<name>` (namespaced) | `commands/<name>.md` → slash command | `.agents/skills/<name>/SKILL.md` (custom slash commands **deprecated** → use skills) |
| **Rules / always-on context** | Skills + optional `settings.json` agent | `rules/amir-core.mdc` (`alwaysApply: true`) | `AGENTS.md` at adapter root |
| **Context-size introspection** | Host `/context` + model window; amir `compact` skill | Cursor context meter; amir `compact` skill | Codex context limits; amir `compact` skill |
| **Token / cost telemetry** | **Estimate** — `node tools/cost.js` from `activity.jsonl`; no native billing API | **Estimate** — same `tools/cost.js` | **Estimate** — same `tools/cost.js` |
| **Ephemeral session (`/btw`)** | **Intentionally absent** — no true zero-pollution ephemeral session in Claude Code; not registered | **Closest primitive** — read-only Ask / ephemeral-style command (`commands/btw.md`); residual host history | **Closest primitive** — `.agents/skills/btw/SKILL.md` self-imposed read-only single turn; residual transcript retention |

---

## Claude Code

**Adapter:** `adapters/claude-code/`

| Feature | Detail |
|---------|--------|
| Packaging | `.claude-plugin/plugin.json`, `skills/`, `agents/`, `hooks/`, `bin/` |
| Skills | One directory per skill: `skills/<name>/SKILL.md` with YAML `name` + `description`; body is thin wrapper → `../../skills/<name>.md` |
| Subagents | Native **Task** subagents map to `1-orchestrator`, `2-architect`, `3-qa`, `4-security`, `dev-T*`, `qa-T*` per `agents/*.md` |
| Hooks | `PreToolUse` on `Bash` can run `secrets_scan.js` before shell; **primary secrets gate remains commit-time** via git commit skill flow |
| `/btw` | **Not registered.** Claude Code has no true zero-pollution ephemeral session; amir deliberately does not ship a `/btw` skill here |

---

## Cursor

**Adapter:** `adapters/cursor/`

| Feature | Detail |
|---------|--------|
| Packaging | `.cursor-plugin/plugin.json`, `commands/`, `rules/`, optional `skills/`, `hooks/` |
| Commands | One `commands/<skill>.md` per amir skill + `commands/btw.md` |
| Rules | `rules/amir-core.mdc` — `alwaysApply: true`, points to `core/` paths, message contract, JSON truth |
| Subagents | Prefer native **Task** when present (Mode A for `/amir:use_subagent`). If Task unavailable: Mode C sequential isolated contexts — label explicitly; do not claim parallel native subagents |
| `/btw` | `commands/btw.md` — temporary read-only, single turn, banner **BTW MODE — Temporary • Read-only • Not saved**, close with **Temporary session closed.** |
| Residual `/btw` limits | Cursor may retain the turn in chat history; tool write blocking depends on mode — agent must refuse writes even if tools appear available |

---

## Codex

**Adapter:** `adapters/codex/`

| Feature | Detail |
|---------|--------|
| Packaging | `AGENTS.md`, `.codex/config.toml` (sample), `.agents/skills/<name>/SKILL.md` |
| Slash commands | **Deprecated** in favor of skills — legacy slash files may exist in old installs; new installs use skill wrappers only |
| Subagents | Sequential **simulated** roles per `AGENTS.md`; no guaranteed parallel subagent runtime |
| `/btw` | `.agents/skills/btw/SKILL.md` — read-only single-turn approximation |
| Residual `/btw` limits | Codex may persist transcript; no cryptographic isolation — separate session for true air-gap |

---

## Degrade path summary

```
Native subagents available?
├── Claude Code: YES → Task with agent id (Mode A)
├── Cursor: Task available? YES → Mode A; NO → Mode C isolated contexts
└── Codex: usually Mode C (simulated / isolated) unless host adds delegation
         ├── Announce mode once; label [AGENT <id>] / isolated context
         ├── /use_subagent: one fresh context per atomic task
         └── amir project JSON optional — use_subagent is independent of .ai/state

/btw requested?
├── Claude Code: refuse / not registered — use fresh chat for side questions
├── Cursor: btw.md read-only command (honest residual limits)
└── Codex: btw skill (honest residual limits)
```

---

## Path resolution after install

| Host | amir root | Skill file | Tools |
|------|-----------|------------|-------|
| Claude Code | `${CLAUDE_PLUGIN_ROOT}/../..` | `skills/<name>.md` | `tools/*.js` |
| Cursor | parent of `adapters/` | `skills/<name>.md` | `tools/*.js` |
| Codex | directory containing `AGENTS.md` sibling `core/` | `skills/<name>.md` | `tools/*.js` |

See each adapter's `README.md` for host-specific install steps.
