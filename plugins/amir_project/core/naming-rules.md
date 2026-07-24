# amir — naming rules

Canonical agent ids, task ids, and hierarchy for amir projects.

## Top-level agents

Fixed ids — use exactly these strings in messages, paths, and state:

| Id | Role |
|----|------|
| `1-orchestrator` | Single coordinator; owns JSON state writes and `complete` |
| `2-architect` | Design, architecture, task breakdown proposals |
| `3-qa` | QA org parent; hosts verifier sub-agents |
| `4-security` | Security review, secrets_scan interpretation, security gates |

Message contract example: `[AGENT 1-orchestrator] T001 — plan (cycle 1/10)`

## Task workers

Format: **`dev-<task-id>`**

| Example | Meaning |
|---------|---------|
| `dev-T001` | Worker for task T001 |
| `dev-D003` | Worker for documentation task D003 |

Workspace: `ai/agents/dev-T001/` (or equivalent per `core/workspace-rules.md`).

One primary worker per task id unless orchestrator splits subtasks with explicit ids.

## Verifiers

Format: **`qa-<task-id>`**

| Example | Meaning |
|---------|---------|
| `qa-T001` | Independent verifier for T001 |

Hierarchy: **`qa-<task-id>`** is under **`3-qa`** organizationally and in reporting. Paths may be `ai/agents/3-qa/qa-T001/` or `ai/agents/qa-T001/` — pick one convention per project at create time.

Verifier sets `qa_passed`; does **not** set `complete`.

## Sub-agents

Format: **`<parent-id>/sub-<name>`** or nested directory under parent workspace

| Example | Parent |
|---------|--------|
| `dev-T001/sub-migration` | `dev-T001` |
| `2-architect/sub-api-design` | `2-architect` |

Rules:

- Sub-agent inherits budget and task id from parent unless given own task id
- Sub-agent conclusions are **INFERRED** until parent or QA verifies
- Name `sub-<name>` in kebab-case, ≤32 chars

Native host Task/subagent: map to same logical id in activity log.

## document_max roles

Documentation sprint agents:

| Id | Role |
|----|------|
| `doc-lead` | Outline, section assignment, checkpoint every 15 sections |
| `doc-worker` | Writes assigned sections |
| `doc-verifier` | Reviews accuracy vs goal and decisions |

Doc tasks use **Doc IDs** (`D001`, `D002`, …) in `tasks.json`, parallel to `T001` for build tasks.

Workers may be `dev-D001` or `doc-worker` scoped to D001 — project template defines mapping; stay consistent.

## Task IDs

| Type | Pattern | Example |
|------|---------|---------|
| Build / feature tasks | `T` + three digits | `T001`, `T042` |
| Documentation tasks | `D` + three digits | `D001`, `D015` |

Rules:

- Assign sequentially in `tasks.json`; no reuse after abandon without orchestrator note in decisions
- Reference task id in all agent ids, messages, and activity events
- Subtasks either use new ids (`T001a` not allowed — use `T002` with dependency link) or `sub-*` under parent

## Host degradation

When host lacks native subagents:

- Log **simulated** role with same logical id (`qa-T001`, etc.)
- Do not invent alternate naming schemes per host

## Quick reference

```
1-orchestrator
2-architect
3-qa
  └── qa-T001, qa-T002, ...
4-security
dev-T001, dev-T002, ...
doc-lead | doc-worker | doc-verifier  (document_max)
dev-D001, qa-D001                     (doc tasks, if used)
```

## Cross-references

| Topic | File |
|-------|------|
| Workspace paths | `core/workspace-rules.md` |
| Message header | `core/message-contract.md` |
| QA verifier | `core/qa-loop.md` |
| Doc budget | `core/budget-rules.md` |

Skills and agents must say **"Follow `core/naming-rules.md`"** — do not restate these rules elsewhere.
