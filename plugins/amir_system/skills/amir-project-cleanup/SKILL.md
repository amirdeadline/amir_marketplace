---
name: amir-project-cleanup
description: >-
  Comprehensive project audit and cleanup for long-running repos: scan code and
  docs, classify stale AI/project memory, reconstruct current truth, rebuild
  PROJECT.md and a clean .ai/ knowledge system, graph architecture, consolidate
  requirements/MVP/TODOs, safely delete superseded context, and write a cleanup
  report. Use when cleaning up a project, auditing the entire project, rebuilding
  project memory, cleaning AI context, removing outdated project docs, rebuilding
  PROJECT.md, cleaning stale TODOs, consolidating documentation, analyzing current
  project state, rebuilding .ai, updating project memory, performing project
  context cleanup, cleaning long-running project state, optimizing repository
  context for AI, or graphing project architecture. Invoked as /amir-project-cleanup
  or /amir:amir-project-cleanup.
---

# amir-project-cleanup

Perform a full project-memory and documentation rebuild in the **current repository**.
This is an execution skill: inspect, reconstruct, write files, validate, then safely
clean obsolete context. Do not stop at advice.

**Not the same as** `/amir:cleanup_context` (session handoff) or harness
`project_cleanup`. This skill rebuilds durable project knowledge from implementation.

Works in any repo (Amir project or not). Stay inside the project root.

## Operating principles

1. **Code > docs.** Prefer working implementation, tests, schemas, infra, and manifests
   over old plans/memories.
2. **One canonical fact, one place.** Reference; do not duplicate.
3. **Never invent requirements.** Mark uncertainty `NEEDS_CONFIRMATION` or put it in
   `.ai/open_questions.md`.
4. **Never blindly delete.** Migrate useful facts first; when unsure, retain and list.
5. **No secrets** in any written doc (values, tokens, keys, connection strings).
6. **Show a deletion plan and get explicit approval** before removing files (destructive-action).
7. Keep `PROJECT.md` and `.ai/memory.md` especially compact.

### Source-of-truth priority

1. Working implementation
2. Tests
3. Schemas / migrations
4. Infrastructure config
5. Deployment / runtime config
6. Package manifests
7. APIs / interfaces
8. Recent authoritative docs
9. Old documentation
10. Old plans / agent memories / scratch notes

---

## Phase 0 — Scope check

- Confirm the project root (git root or workspace root).
- Note host docs already present (`.ai/`, `PROJECT.md`, `AGENTS.md`, etc.).
- If the tree is huge, inventory systematically; use bounded subagents only with
  explicit path allowlists — never dump the whole repo into one context.

---

## Phase 1 — Repository discovery

Inventory:

- apps, services, modules, packages, libraries
- frontend / backend / workers / queues / APIs
- databases, schemas, migrations
- infra, CI/CD, deploy, scripts, config
- external integrations, tests

Search for project/AI context (non-exhaustive):

`PROJECT*`, `README*`, `AGENTS*`, `MEMORY*`, `TODO*`, `ROADMAP*`, `PLAN*`,
`STATUS*`, `ARCHITECTURE*`, `DESIGN*`, `DECISIONS*`, `NOTES*`, `CHANGELOG*`,
`docs/**`, `.ai/**`, `.cursor/**`, `.claude/**`, `.codex/**`, `.github/**`, `.amir/**`

Record a working **repository map** (paths + roles). Do not trust filenames alone.

---

## Phase 2 — Audit existing memory

Read relevant memory/status/plan/architecture/TODO docs. Classify each material fact:

| Label | Meaning |
|---|---|
| CURRENT | Matches implementation |
| PARTIALLY_CURRENT | Partially true |
| SUPERSEDED | Replaced by newer truth |
| HISTORICAL | Once true; useful only as history |
| DUPLICATE | Same fact elsewhere |
| COMPLETED | Done; should not stay as open work |
| ABANDONED | Stopped; not planned |
| INCORRECT | Contradicted by code/config |
| UNKNOWN | Cannot verify yet |

Never assume a document is correct because it exists.

---

## Phase 3 — Reconstruct current truth

From implementation evidence, determine:

- product purpose and user flows
- MVP definition and completion
- architecture, components, boundaries, data/runtime flow
- requirements (functional / non-functional / security / data / deploy / ops / integration)
- dependencies and integrations
- deployment model
- implementation status, known problems, debt

Label claims **VERIFIED** (seen in tree) vs **INFERRED**. Never present INFERRED as VERIFIED.

---

## Phase 4 — Validate historical TODOs and plans

Classify every historical task:

`DONE` | `STILL_REQUIRED` | `PARTIALLY_DONE` | `OBSOLETE` | `ABANDONED` | `UNKNOWN`

Only real remaining work enters the new TODO system. Do not copy old lists blindly.

---

## Phase 5 — Detect stale context

Flag material that is outdated, duplicated, contradicted, completed, abandoned,
superseded, irrelevant, temporary, verbose, or misleading (old architecture, finished
migrations, removed services, stale env vars, abandoned experiments, debug notes,
copied agent summaries, old status reports).

Goal: aggressive **context hygiene** without unsafe deletion.

---

## Phase 6 — Rebuild `.ai/` and `PROJECT.md`

Create or replace the canonical set. Only add extra files when they hold genuinely
distinct knowledge.

```text
.ai/
├── architecture.md
├── cleanup_report.md
├── components.md
├── context_rules.md
├── data_model.md
├── decisions.md
├── deployment.md
├── development.md
├── integrations.md
├── memory.md
├── mvp.md
├── open_questions.md
├── project_graph.md
├── project_graph.mmd
├── project_requirements.md
├── project_status.md
├── repository_map.md
├── risks.md
├── security.md
├── testing.md
└── todo.md
```

If an Amir project already uses `.ai/status.md`, `.ai/tasks.md`, etc., **migrate**
durable content into this canonical set (or clearly cross-link once). Prefer one
canonical location per fact; do not leave contradictory twin files.

### File contracts

**`.ai/memory.md`** — durable agent knowledge only: constraints, conventions, decision
rationales that still matter, pitfalls, compatibility/ops facts. Not a diary. Not debug history.

**`.ai/mvp.md`** — objective, users, flows, required features/integrations, explicit
exclusions, completion. Mark items: `COMPLETE` | `PARTIAL` | `MISSING`.

**`.ai/project_requirements.md`** — canonical requirements. Uncertain items:
`NEEDS_CONFIRMATION`. Never silently promote assumptions to requirements.

**`.ai/project_status.md`** — component status matrix using:
`COMPLETE` | `FUNCTIONAL` | `PARTIAL` | `STUB` | `EXPERIMENTAL` | `BROKEN` |
`DEPRECATED` | `PLANNED` | `UNKNOWN`.
Also: overall state, MVP completion, blockers, high-risk areas, debt, incomplete migrations.

**`.ai/todo.md`** — actionable work only. Priorities: `P0` | `P1` | `P2` | `P3` | `BACKLOG`.
Include components/paths/deps/acceptance criteria when useful. No completed work.

**`.ai/architecture.md`** — actual architecture (apps, boundaries, deps, data/runtime flow,
storage, workers/queues, integrations, deploy, authn/authz). Mermaid where useful.

**`.ai/project_graph.md` + `.ai/project_graph.mmd`** — component/system graph (not every
file): services, modules, apps, APIs, DBs, queues, workers, infra, external providers.

**`.ai/context_rules.md`** — how future agents should use this `.ai/` set (read order,
canonical files, what not to duplicate).

**`.ai/open_questions.md`** — unresolved items and anything retained pending human review.

**`.ai/cleanup_report.md`** — see Phase 8.

### Root `PROJECT.md`

Create or rebuild compact entry point:

```markdown
# Project

## Overview
## Current State
## MVP Status
## Architecture Summary
## Major Components
## Current Priorities
## Known Blockers
## Critical Constraints
## AI Working Rules
## Detailed Project Knowledge
```

`PROJECT.md` = compact global context + navigation.
`.ai/*.md` = canonical detail. Do not paste full `.ai/` contents into `PROJECT.md`.

---

## Phase 7 — Safe cleanup

Candidates: superseded AI/project-memory docs, duplicate status/TODO/architecture notes,
obsolete plans fully migrated.

**Before any delete:**

1. Read the file
2. Extract still-valuable facts
3. Verify against implementation
4. Migrate into canonical `.ai/` / `PROJECT.md`
5. Grep for tooling/doc references to the path
6. Present the deletion list with reasons
7. **Require explicit user approval**
8. Delete only approved, safe items

**Never delete** (unless the user explicitly expands scope with strong evidence):

- source code, production config, migrations, databases
- required generated files, test fixtures
- secrets-management infrastructure, deployment artifacts

If uncertain → retain + list in `.ai/open_questions.md` and the cleanup report.

Optional archive: move to `.ai/archive/` only if the user prefers archive over delete;
still requires approval.

---

## Phase 8 — Cleanup report

Write `.ai/cleanup_report.md` with:

- audit summary
- files created / replaced / deleted / archived (reason per deletion)
- contradictions resolved
- stale information found
- architecture problems and technical debt
- human-review items

---

## Phase 9 — Self-validation

Before claiming complete:

- [ ] Documented paths exist
- [ ] Commands checked where practical
- [ ] Component names match implementation
- [ ] TODOs match remaining code gaps
- [ ] API/architecture claims checked
- [ ] Internal Markdown links resolve
- [ ] No references to removed files left dangling
- [ ] No secrets copied into docs
- [ ] No duplicated canonical facts across `PROJECT.md` / `.ai/`

Fix issues found; do not mark validation passed without evidence.

---

## Completion summary (report to user)

1. Project health
2. Architecture discovered
3. MVP state
4. Major unfinished work
5. Important stale information removed
6. Contradictions resolved
7. Documentation created
8. Documentation removed
9. Human review required
10. Recommended next engineering priorities

Separate **completed / failed / skipped / blocked**. Partial success = partial.

---

## Scenario expectations

| Scenario | Behavior |
|---|---|
| Mature repo with contradictory docs | Reconstruct from code; migrate; replace stale; delete only after approval |
| New / sparse docs | Build canonical set from implementation; do not invent unsupported facts |
| Ambiguous legacy | Analyze; do not blind-delete; park unresolved items in `open_questions.md` |
