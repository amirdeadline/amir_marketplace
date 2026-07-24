---
name: onboard_project
description: Onboard an existing repository into the Amir system — deep discovery, evidence-based component classification, merge-not-overwrite migration with backups, interview-confirmed selection, honest onboarding report. Use for /amir:onboard_project.
---

# onboard_project — full workflow

You are adopting an EXISTING repository into the Amir system. Non-negotiables: **discovery
before recommendations**, **evidence for every classification**, **merge never overwrite**,
**backups before touching anything**, **honest final ledger**.

## Phase 0 — Preflight

1. Confirm the repo root with the user (argument or cwd). Verify it exists and is readable.
2. If `.amir/project.yaml` already exists → this project is already onboarded; offer
   `/amir:project_status`, `/amir:configure_project`, or `/amir:repair_project` instead and stop
   unless the user wants a re-onboarding (which follows the same merge rules).
3. Catalog check: `catalog/catalog.json`. If missing, warn: recommendations will lack
   dependency/credential metadata — user should run `/amir:update_catalog`; ask whether to
   continue degraded.
4. Everything in Phases 0–2 is READ-ONLY.

## Phase 1 — Discovery (systematic; collect evidence, cite files)

Inspect and record (with the file paths that prove each finding):

- repo root, git status, branches, existing worktrees
- languages (by extension census), frameworks (manifests: package.json, pyproject.toml,
  go.mod, Cargo.toml, *.csproj, …), dependencies
- build system(s) and test system(s); test locations and rough coverage signals
- CI/CD (`.github/workflows`, gitlab-ci, azure-pipelines, Jenkinsfile)
- containers (Dockerfile, compose), IaC (terraform/, bicep, k8s manifests)
- entry points (mains, servers, CLIs, exported APIs)
- existing AI config, BOTH hosts:
  - Cursor: `.cursor/` (rules, commands, mcp.json)
  - Claude: `.claude/` (settings, skills, agents, hooks), CLAUDE.md
- existing rules/skills/agents/MCP servers/connectors from any other system
- existing Graphify (`graphify-out/`, hooks), Serena, Context7, Semgrep configs
- observability (Langfuse or similar), benchmarks (SWE-bench/Terminal-Bench artifacts)
- AI docs (`.ai/`, docs/ with agent-oriented content)
- **legacy `ai/` workspace** (the pre-rename convention, no leading dot): record its file
  inventory — it is a migration candidate (see "Legacy ai/ → .ai/ migration" below)
- existing PM/portfolio docs anywhere in the repo (roadmaps, milestone lists, status docs,
  CHANGELOG, project boards exports) — candidates to IMPORT/map into `.ai\` and
  `.amir\portfolio.yaml`, never to overwrite
- secrets: detect PRESENCE ONLY (.env files, *credential* files, key-looking entries in
  configs). **NEVER read, print, or copy secret values. Report file names and variable NAMES
  only.**
- global config leaking into the project (user-scope paths hardcoded, absolute machine paths)

## Phase 2 — Classification and recommendations (evidence-based, advisory only)

Classify EVERY optional component from the catalog with exactly one label:
**Strongly recommended / Recommended / Optional / Not useful / Unsupported / Already
configured / Conflicting / Requires migration** — each with cited evidence ("Semgrep:
Strongly recommended — handles credentials in `src/auth/token.py`, external input in
`api/routes.py`").

Built-in heuristics (apply and cite):

| Component | Recommend when the repo shows |
|---|---|
| Playwright | web app with browser flows |
| Semgrep | external input handling or credential handling |
| Serena | supported language + medium/large repo |
| Context7 | heavy external libraries/APIs usage |
| Graphify | medium/large, modular, or multi-service codebase |
| Langfuse | LLM/agent workflows present |
| OpenHands | desire for sandboxed autonomous coding |
| SWE-bench | issue-resolution evaluation relevant |
| Terminal-Bench | terminal-agent evaluation relevant |
| Git worktrees | parallel agents will modify code concurrently |

Present the classification table, then run the same selection controls as create_project
(`recommended` / individual / `all` / `none` [default] / `search` / `details` / `back` /
`review` / `cancel`), showing per-option catalog details (deps, credentials, network/secret
access, security/performance implications). Ask remaining interview questions the discovery
could not answer (hosts to enable, testing/security requirements, per-tool choices, and the
portfolio questions from create_project Phase 1 items 25–36 — lifecycle, priority, deadline,
milestones, phase, owner, Asana link, **global-graph join [default: no]**, related projects,
progress source, staleness threshold, reporting) — ONE question at a time. Where discovery
found existing PM docs, propose a mapping ("your ROADMAP.md milestones → portfolio.yaml
milestones; your STATUS.md → seed for .ai\status.md") and let the user confirm or adjust
each mapping — import, never invent, and never delete the originals.

Also check the registry (`portfolio-list`) for already-registered projects this repo relates
to (shared org, imports, same product): present detected candidates as suggestions for the
related-projects answer — suggestions only, user-confirmed.

## Phase 3 — Migration plan and confirmation

Show the full plan before any write:

- what will be BACKED UP: every existing AI config file → `.amir/backups/<timestamp>/`
  (mirroring original paths)
- what is PRESERVED as-is (valid existing config)
- what is MIGRATED (existing config transformed into Amir-managed form) — with per-file mapping
- what is ADDED (newly selected components)
- what is DISABLED/SKIPPED and why
- detected COLLISIONS (same command/rule name from different sources) and the proposed
  resolution for each
- detected global-config leakage and the proposed fix
- legacy `ai/` found → the migration offer (procedure below) with its full file mapping
- the `.amir\portfolio.yaml` that will be created (imported values labeled with their source
  doc; everything unknown left blank — never fabricated)
- registration: the registry entry (`%USERPROFILE%\.amir\registry\projects.yaml`) and the
  global-graph decision (join / metadata-only / no) — **the project is NEVER registered in
  the registry or the global graph without the user's explicit approval of this plan**
- files created/modified; dependencies installed; credentials still required (names only)

### Legacy `ai/` → `.ai/` migration (offer when Phase 1 found `ai/`; safe, reversible)

Offer, never force. If declined, record the decision and leave `ai/` untouched. If accepted:

1. Back up BOTH directories (`ai/` and any existing `.ai/`) to
   `.amir\backups\<timestamp>\` and verify the backup before anything else.
2. Collision check: for every `ai/<file>` that also exists in `.ai/`, show both and ask
   which wins (or merge) — per file, no bulk overwrite.
3. Move with history: `git mv ai/<file> .ai/<file>` when the repo is git-tracked (preserves
   history); plain move otherwise. Say which was used.
4. Update every internal reference to `ai/` paths: links within the moved docs, CLAUDE.md,
   AGENTS.md, `.cursor\rules\*`, skills, manifests (`.amir\project.yaml`), scripts, and
   tests. Show the per-file reference diff.
5. Validate ZERO old references remain (search the repo for `ai/` path references, excluding
   backups and false positives like "main/", and show the empty result).
6. **Do not delete the old `ai/` directory until validation passes** (with `git mv` it is
   already gone; for the plain-move case, remove it only after step 5, with confirmation).
7. Write the migration report `.amir\migration\ai-to-dot-ai.md` containing: timestamp; who
   ran it (host/session); backup locations; the complete old→new file inventory; collisions
   found and how each was resolved; every reference updated (file + what changed);
   validation evidence (the search command and its empty output); old-directory removal
   status; and rollback instructions (restore from the named backup / git revert).

**MERGE, not overwrite**: existing `.cursor/mcp.json` entries, rules, commands, and Claude
config that Amir does not own are kept untouched; Amir entries are added alongside. Require
explicit confirmation. Cancel = zero side effects (backups may already exist; say so).

## Phase 4 — Execution (ordered)

1. Create `.amir/backups/<timestamp>/` and copy every file that will be modified. Verify the
   backup before proceeding.
2. Write `.amir/project.yaml` (schema v2) reflecting discovered facts + selections.
3. Resolve dependencies (engine/validator); surface problems; re-confirm if selection changes.
4. Write `.amir/components.lock.json`.
5. Install ONLY selected components (renderer subset or full amir_project fast path — see
   create_project Phase 4 step 5).
6. Render both hosts as selected (Cursor flat commands/rules/mcp merge; Claude files).
7. Run the legacy `ai/` → `.ai/` migration if it was accepted in the plan (procedure above,
   including the `.amir\migration\ai-to-dot-ai.md` report).
8. Create `.amir\portfolio.yaml` from this plugin's `templates\portfolio.yaml.tmpl`, filled
   only with confirmed interview answers and confirmed imports from existing PM docs —
   blanks stay blank. Seed missing `.ai\` files from `templates\dot-ai\` (imports win over
   empty templates; existing `.ai\` files are preserved, merge-not-overwrite).
9. Validate: startup checks per component (run catalog `health_check`s), isolation check (no
   Amir writes outside root).
10. Register in `%USERPROFILE%\.amir\registry\projects.yaml` (the ONE shared registry) — only
    because the approved plan included it; approval is per-plan, never assumed.
11. If the approved plan included joining the global graph: run the
    `/amir:graph_projects_add` procedure (graphify gate, scope display, namespace merge,
    `.amir\reports\global-graph-registration.md`). Metadata-only or declined → do exactly
    that and nothing more.

## Phase 5 — Onboarding report (mandatory file)

Write `.amir/onboarding/onboarding-report.md` with a per-item ledger; every touched or
considered item gets exactly one primary status:

`existed-before` / `preserved` / `migrated` / `added` / `disabled` / `skipped` / `failed` /
`manual-config-needed` / `missing-credentials`

plus per-host activation flags: `active-in-cursor: yes|no`, `active-in-claude: yes|no`.

Include in the ledger: the `ai/` → `.ai/` migration outcome (migrated / declined / n-a, with
a pointer to `.amir\migration\ai-to-dot-ai.md`), the portfolio.yaml creation, the registry
registration, and the global-graph decision + outcome.

Honesty rules for the report: a component is "added" and healthy ONLY if its health check ran
and passed (include evidence); failures include the real error; nothing is omitted. Summarize
the report in chat and end with next steps (credentials to place, `/amir:project_status`,
tool-specific setup commands, and `/amir:graph_projects_list` if the project was registered).
